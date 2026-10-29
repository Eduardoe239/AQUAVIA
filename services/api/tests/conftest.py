import os

os.environ["DATABASE_URL"] = "sqlite://"
os.environ["APP_ENV"] = "test"
os.environ["SECRET_KEY"] = "test-secret-not-for-prod"

import uuid  # noqa: E402
from datetime import UTC, datetime  # noqa: E402

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402
from sqlalchemy.orm import Session  # noqa: E402
from sqlalchemy.pool import StaticPool  # noqa: E402

from app.db import models  # noqa: E402,F401
from app.db.session import Base, get_engine, get_session  # noqa: E402
from app.main import create_app  # noqa: E402


@pytest.fixture
def engine():
    from sqlalchemy import create_engine

    eng = create_engine(
        "sqlite://", poolclass=StaticPool, connect_args={"check_same_thread": False}
    )
    Base.metadata.create_all(eng)
    return eng


@pytest.fixture
def client(engine):
    app = create_app()

    def _sess():
        with Session(engine, expire_on_commit=False) as s:
            yield s

    app.dependency_overrides[get_session] = _sess
    get_engine.cache_clear()
    return TestClient(app, raise_server_exceptions=False)


@pytest.fixture
def device(engine):
    from app.domains.telemetry.service import hash_key

    with Session(engine) as s:
        s.add(models.Device(device_id="dev-test-1", api_key_hash=hash_key("secret-1")))
        s.commit()
    return {"X-Device-Id": "dev-test-1", "X-Device-Key": "secret-1"}


def make_event(seq: int = 1, volume: float = 10.0, **over) -> dict:
    ev = {
        "schema_version": 1,
        "event_id": str(uuid.uuid4()),
        "device_id": "dev-test-1",
        "sequence": seq,
        "captured_at": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
        "clock_synchronized": True,
        "firmware_version": "0.1.0",
        "calibration_version": 1,
        "measurements": {"volume_total_liters": volume, "flow_liters_per_minute": 1.5},
        "quality": {"sensor_status": "ok", "measurement_kind": "measured"},
    }
    ev.update(over)
    return ev


HDR = {"X-Requested-With": "aquavia-web"}


@pytest.fixture(autouse=True)
def _reset_limiter():
    from app.domains.identity.service import reset_limiter

    reset_limiter()


@pytest.fixture
def world(engine):
    """Dois tenants (A e B), cada um com usuário, propriedade e um dispositivo reivindicável."""
    from app.core.security import hash_password
    from app.domains.telemetry.service import hash_key

    out = {}
    with Session(engine) as s:
        for t in ("a", "b"):
            u = models.User(email=f"{t}@example.invalid", password_hash=hash_password("senha-" + t))
            o = models.Organization(name=f"Org {t}")
            s.add_all([u, o])
            s.flush()
            p = models.Property(org_id=o.id, name=f"Prop {t}")
            s.add_all([p, models.Membership(user_id=u.id, org_id=o.id, role="owner")])
            d = models.Device(
                device_id=f"dev-{t}",
                api_key_hash=hash_key("key-" + t),
                activation_code_hash=hash_key("codigo-" + t),
            )
            s.add(d)
            s.flush()
            out[t] = {"prop": p.id}
        s.commit()
    return out


def login(client, tenant: str):
    r = client.post(
        "/api/v1/auth/login",
        json={"email": f"{tenant}@example.invalid", "password": "senha-" + tenant},
    )
    assert r.status_code == 200
    return r
