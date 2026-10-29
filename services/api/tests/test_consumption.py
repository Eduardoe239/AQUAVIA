import uuid
from datetime import UTC, datetime, timedelta

from tests.conftest import login, make_event


def iso(dt):
    return dt.isoformat().replace("+00:00", "Z")


def ingest(client, tenant, events):
    r = client.post(
        "/api/v1/telemetry/batch",
        json={"batch_id": str(uuid.uuid4()), "events": events},
        headers={"X-Device-Id": f"dev-{tenant}", "X-Device-Key": f"key-{tenant}"},
    )
    assert all(x["status"] == "accepted" for x in r.json()["results"]), r.json()


def setup(client, world):
    login(client, "a")
    client.post(
        "/api/v1/devices/claim",
        headers={"X-Requested-With": "aquavia-web"},
        json={
            "device_id": "dev-a",
            "activation_code": "codigo-a",
            "property_id": world["a"]["prop"],
        },
    )
    return world["a"]["prop"]


def ev(seq, vol, ts, **kw):
    return make_event(seq=seq, volume=vol, device_id="dev-a", captured_at=iso(ts), **kw)


def test_timeseries_deltas_gaps_and_no_negative(client, world):
    prop = setup(client, world)
    d = datetime(2026, 10, 20, tzinfo=UTC)
    ingest(
        client,
        "a",
        [
            ev(1, 100, d + timedelta(hours=1)),  # base
            ev(2, 110, d + timedelta(hours=2)),  # +10 às 02h
            ev(3, 125, d + timedelta(hours=2, minutes=30)),  # +15 às 02h
            ev(4, 50, d + timedelta(hours=5)),  # regressão: ignorada
            ev(
                5,
                60,
                d + timedelta(hours=6),
                quality={"sensor_status": "ok", "measurement_kind": "estimated"},
            ),
        ],
    )
    r = client.get(
        "/api/v1/consumption/timeseries",
        params={
            "property_id": prop,
            "start": "2026-10-20",
            "end": "2026-10-20",
            "granularity": "hour",
            "tz": "UTC",
        },
    ).json()
    b = r["buckets"]
    assert len(b) == 24 and r["regressions_ignored"] == 1
    assert b[2]["volume_liters"] == 25.0 and b[2]["quality"] == "measured"
    assert b[6]["volume_liters"] == 10.0 and b[6]["quality"] == "estimated"
    assert b[3]["volume_liters"] is None and b[3]["quality"] is None  # lacuna ≠ zero
    assert b[1]["volume_liters"] is None  # primeiro evento é só base


def test_invalid_events_excluded_and_day_granularity_tz(client, world):
    prop = setup(client, world)
    d = datetime(2026, 10, 20, 12, tzinfo=UTC)
    bad = {"sensor_status": "fault", "measurement_kind": "invalid"}
    ingest(
        client,
        "a",
        [
            ev(1, 0, d),
            ev(2, 9999, d + timedelta(hours=1), quality=bad),
            ev(3, 40, d + timedelta(hours=2)),
        ],
    )
    r = client.get(
        "/api/v1/consumption/timeseries",
        params={"property_id": prop, "start": "2026-10-20", "end": "2026-10-21", "tz": "UTC"},
    ).json()
    assert [x["volume_liters"] for x in r["buckets"]] == [40.0, None]


def test_summary_today_and_simulated_flag(client, world):
    prop = setup(client, world)
    now = datetime.now(UTC)
    ingest(
        client,
        "a",
        [
            ev(1, 1000, now - timedelta(seconds=3), firmware_version="sim-0.1.0"),
            ev(2, 1012.5, now - timedelta(seconds=1), firmware_version="sim-0.1.0"),
        ],
    )
    s = client.get("/api/v1/consumption/summary", params={"property_id": prop, "tz": "UTC"}).json()
    assert s["today_liters"] == 12.5 and s["month_liters"] == 12.5
    assert s["simulated"] is True and s["devices"][0]["connection"] == "online"
    assert s["yesterday_liters"] is None and s["unit"] == "L"


def test_consumption_is_tenant_scoped_and_validates_input(client, world):
    setup(client, world)
    other = world["b"]["prop"]
    assert (
        client.get("/api/v1/consumption/summary", params={"property_id": other}).status_code == 404
    )
    mine = world["a"]["prop"]
    bad = {"property_id": mine, "start": "2026-10-01", "end": "2026-10-20", "granularity": "hour"}
    assert client.get("/api/v1/consumption/timeseries", params=bad).status_code == 422
    assert (
        client.get(
            "/api/v1/consumption/summary", params={"property_id": mine, "tz": "Mars/Base"}
        ).status_code
        == 422
    )
    assert [p["name"] for p in client.get("/api/v1/properties").json()["items"]] == ["Prop a"]
