import uuid

from tests.conftest import make_event


def post(client, headers, events):
    return client.post(
        "/api/v1/telemetry/batch",
        json={"batch_id": str(uuid.uuid4()), "events": events},
        headers=headers,
    )


def statuses(resp):
    return [r["status"] for r in resp.json()["results"]]


def test_valid_event_accepted(client, device):
    r = post(client, device, [make_event()])
    assert r.status_code == 200 and statuses(r) == ["accepted"]


def test_resend_same_event_is_idempotent_duplicate(client, device):
    ev = make_event()
    post(client, device, [ev])
    assert statuses(post(client, device, [ev])) == ["duplicate"]


def test_same_event_id_with_different_payload_is_conflict(client, device):
    ev = make_event(seq=1, volume=10)
    post(client, device, [ev])
    altered = {**ev, "measurements": {**ev["measurements"], "volume_total_liters": 99}}
    res = post(client, device, [altered]).json()["results"][0]
    assert res["status"] == "rejected" and res["code"] == "EVENT_ID_CONFLICT"


def test_same_sequence_other_event_id_is_rejected(client, device):
    post(client, device, [make_event(seq=5)])
    res = post(client, device, [make_event(seq=5)]).json()["results"][0]
    assert res["code"] == "SEQUENCE_CONFLICT"


def test_partial_batch_reports_each_event(client, device):
    good, bad = (
        make_event(seq=1),
        make_event(seq=2, measurements={"volume_total_liters": -1, "flow_liters_per_minute": 0}),
    )
    r = post(client, device, [good, bad, good])
    assert statuses(r) == ["accepted", "invalid", "duplicate"]
    assert r.json()["results"][1]["code"] == "INVALID_SCHEMA"


def test_naive_timestamp_and_extra_field_are_invalid(client, device):
    e1 = make_event(seq=1, captured_at="2026-10-24T11:30:00")
    e2 = {**make_event(seq=2), "surprise": 1}
    assert statuses(post(client, device, [e1, e2])) == ["invalid", "invalid"]


def test_future_timestamp_with_synced_clock_is_invalid(client, device):
    r = post(client, device, [make_event(captured_at="2999-01-01T00:00:00Z")])
    assert r.json()["results"][0]["code"] == "CAPTURED_AT_IN_FUTURE"


def test_event_for_other_device_is_rejected(client, device):
    r = post(client, device, [make_event(device_id="dev-other")])
    assert r.json()["results"][0]["code"] == "DEVICE_MISMATCH"


def test_missing_or_wrong_credentials_401_standard_error(client, device):
    r = post(client, {"X-Device-Id": "dev-test-1", "X-Device-Key": "nope"}, [make_event()])
    assert r.status_code == 401
    err = r.json()["error"]
    assert err["code"] == "DEVICE_UNAUTHORIZED" and err["request_id"]
    assert post(client, {}, [make_event()]).status_code == 401


def test_revoked_device_is_blocked(client, device, engine):
    from sqlalchemy.orm import Session

    from app.db.models import Device

    with Session(engine) as s:
        s.query(Device).update({"status": "revoked"})
        s.commit()
    assert post(client, device, [make_event()]).status_code == 401


def test_malformed_request_uses_standard_error_format(client, device):
    r = client.post("/api/v1/telemetry/batch", json={"events": []}, headers=device)
    assert r.status_code == 422 and r.json()["error"]["code"] == "REQUEST_INVALID"


def test_health(client):
    assert client.get("/health").json() == {"status": "ok"}
