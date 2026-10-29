import hmac
from dataclasses import dataclass
from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import AuditEvent, Device, Property, TelemetryEvent
from app.domains.telemetry.service import hash_key


def visible_devices(session: Session, org_ids: list[str], limit: int, offset: int) -> list[Device]:
    q = (
        select(Device)
        .join(Property, Device.property_id == Property.id)
        .where(Property.org_id.in_(org_ids))
        .order_by(Device.created_at, Device.id)
        .limit(limit)
        .offset(offset)
    )
    return list(session.scalars(q))


def get_visible_device(session: Session, org_ids: list[str], device_id: str) -> Device | None:
    """None tanto para inexistente quanto para outro tenant: o chamador responde 404."""
    return session.scalar(
        select(Device)
        .join(Property, Device.property_id == Property.id)
        .where(Property.org_id.in_(org_ids), Device.device_id == device_id)
    )


def claim(
    session: Session, actor: str, device_id: str, code: str, property_id: str
) -> Device | None:
    device = session.scalar(select(Device).where(Device.device_id == device_id))
    stored = device.activation_code_hash if device else None
    ok = hmac.compare_digest(stored or "0" * 64, hash_key(code))
    if not (device and stored and ok and device.property_id is None and device.status == "active"):
        session.add(
            AuditEvent(
                actor=actor, action="device.claim", resource=f"device:{device_id}", result="denied"
            )
        )
        session.commit()
        return None
    device.property_id = property_id
    device.activation_code_hash = None  # uso único
    device.claimed_at = datetime.now(UTC)
    session.add(
        AuditEvent(actor=actor, action="device.claim", resource=f"device:{device_id}", result="ok")
    )
    session.commit()
    return device


@dataclass
class DeviceStatus:
    connection: str  # never_reported | online | delayed | offline
    age_seconds: int | None
    last_reading_at: datetime | None
    last_sync_at: datetime | None
    volume_total_liters: float | None
    flow_liters_per_minute: float | None
    sensor_status: str | None
    measurement_kind: str | None
    firmware_version: str | None
    calibration_version: int | None
    clock_synchronized: bool | None


def _aware(dt: datetime) -> datetime:
    return dt if dt.tzinfo else dt.replace(tzinfo=UTC)


def status_of(session: Session, device: Device, online_s: int, delayed_s: int) -> DeviceStatus:
    last = session.scalar(
        select(TelemetryEvent)
        .where(TelemetryEvent.device_pk == device.id)
        .order_by(TelemetryEvent.sequence.desc())
        .limit(1)
    )
    if last is None:
        return DeviceStatus(
            "never_reported", None, None, None, None, None, None, None, None, None, None
        )
    sync = session.scalar(
        select(TelemetryEvent.received_at)
        .where(TelemetryEvent.device_pk == device.id)
        .order_by(TelemetryEvent.received_at.desc())
        .limit(1)
    )
    age = int((datetime.now(UTC) - _aware(sync)).total_seconds())
    conn = "online" if age <= online_s else "delayed" if age <= delayed_s else "offline"
    return DeviceStatus(
        conn,
        age,
        _aware(last.captured_at),
        _aware(sync),
        float(last.volume_total_liters),
        float(last.flow_liters_per_minute),
        last.sensor_status,
        last.measurement_kind,
        last.firmware_version,
        last.calibration_version,
        last.clock_synchronized,
    )
