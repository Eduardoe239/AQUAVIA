import uuid

from tests.conftest import HDR, login, make_event


def claim(client, tenant, world, code=None, device=None, prop=None):
    return client.post(
        "/api/v1/devices/claim",
        headers=HDR,
        json={
            "device_id": device or f"dev-{tenant}",
            "activation_code": code or f"codigo-{tenant}",
            "property_id": prop or world[tenant]["prop"],
        },
    )


def test_login_sets_httponly_strict_cookie_and_me_works(client, world):
    r = login(client, "a")
    sc = r.headers["set-cookie"].lower()
    assert "httponly" in sc and "samesite=strict" in sc
    assert client.get("/api/v1/me").json()["organizations"][0]["role"] == "owner"


def test_unauthenticated_and_bad_login(client, world):
    assert client.get("/api/v1/me").status_code == 401
    r = client.post("/api/v1/auth/login", json={"email": "a@example.invalid", "password": "x"})
    assert r.status_code == 401 and r.json()["error"]["code"] == "INVALID_CREDENTIALS"
    ghost = client.post("/api/v1/auth/login", json={"email": "no@example.invalid", "password": "x"})
    assert ghost.json()["error"] == {
        **r.json()["error"],
        "request_id": ghost.json()["error"]["request_id"],
    }


def test_login_rate_limited(client, world):
    for _ in range(5):
        client.post("/api/v1/auth/login", json={"email": "a@example.invalid", "password": "x"})
    r = client.post(
        "/api/v1/auth/login", json={"email": "a@example.invalid", "password": "senha-a"}
    )
    assert r.status_code == 429


def test_forged_or_tampered_cookie_rejected(client, world):
    client.cookies.set("aquavia_session", "e30.assinatura-falsa")
    assert client.get("/api/v1/me").status_code == 401


def test_claim_requires_csrf_header(client, world):
    login(client, "a")
    r = client.post(
        "/api/v1/devices/claim",
        json={
            "device_id": "dev-a",
            "activation_code": "codigo-a",
            "property_id": world["a"]["prop"],
        },
    )
    assert r.status_code == 403


def test_claim_success_is_single_use(client, world):
    login(client, "a")
    assert claim(client, "a", world).status_code == 200
    again = claim(client, "a", world)
    assert again.status_code == 404 and again.json()["error"]["code"] == "ACTIVATION_INVALID"


def test_claim_wrong_code_or_foreign_property_indistinguishable(client, world):
    login(client, "a")
    wrong = claim(client, "a", world, code="codigo-errado")
    foreign = claim(client, "a", world, device="dev-b", code="codigo-b", prop=world["b"]["prop"])
    assert wrong.status_code == 404 and foreign.status_code == 404
    assert foreign.json()["error"]["code"] == "NOT_FOUND"


def test_tenant_isolation_on_list_and_status(client, world):
    login(client, "a")
    claim(client, "a", world)
    assert [d["device_id"] for d in client.get("/api/v1/devices").json()["items"]] == ["dev-a"]
    login(client, "b")
    assert client.get("/api/v1/devices").json()["items"] == []
    assert client.get("/api/v1/devices/dev-a/status").status_code == 404  # IDOR
    assert client.get("/api/v1/devices/inexistente/status").status_code == 404


def test_status_never_reported_then_online_after_ingest(client, world):
    login(client, "a")
    claim(client, "a", world)
    st = client.get("/api/v1/devices/dev-a/status").json()
    assert st["connection"] == "never_reported" and st["last_reading_at"] is None
    ev = make_event(device_id="dev-a")
    r = client.post(
        "/api/v1/telemetry/batch",
        json={"batch_id": str(uuid.uuid4()), "events": [ev]},
        headers={"X-Device-Id": "dev-a", "X-Device-Key": "key-a"},
    )
    assert r.json()["results"][0]["status"] == "accepted"
    st = client.get("/api/v1/devices/dev-a/status").json()
    assert st["connection"] == "online" and st["volume_total_liters"] == 10.0
    assert st["measurement_kind"] == "measured" and st["age_seconds"] < 60


def test_logout_clears_session(client, world):
    login(client, "a")
    assert client.post("/api/v1/auth/logout", headers=HDR).status_code == 200
    client.cookies.clear()
    assert client.get("/api/v1/me").status_code == 401
