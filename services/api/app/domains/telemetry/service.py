"""Ingestão: valida -> autoriza -> deduplica -> persiste. Sem I/O de transporte aqui."""

import hashlib
import hmac
import logging
from datetime import UTC, datetime, timedelta

from pydantic import ValidationError
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.db.models import AuditEvent, Device, TelemetryEvent
from app.schemas.telemetry import EventResult, EventStatus, TelemetryEventV1

log = logging.getLogger("aquavia.telemetry")


def hash_key(secret: str) -> str:
    return hashlib.sha256(secret.encode()).hexdigest()


def authenticate(session: Session, device_id: str, key: str) -> Device | None:
    device = session.scalar(select(Device).where(Device.device_id == device_id))
    expected = device.api_key_hash if device else "0" * 64  # compara sempre (tempo constante)
    ok = hmac.compare_digest(expected, hash_key(key))
    return device if (device and ok and device.status == "active") else None


def _res(event_id, status, code=None, details=None) -> EventResult:
    return EventResult(event_id=event_id, status=status, code=code, details=details)


def ingest(
    session: Session, device: Device, raw_events: list[dict], max_skew_s: int = 300
) -> list[EventResult]:
    results: list[EventResult] = []
    now = datetime.now(UTC)
    for raw in raw_events:
        raw_id = raw.get("event_id") if isinstance(raw.get("event_id"), str) else None
        try:
            ev = TelemetryEventV1.model_validate(raw)
        except ValidationError as exc:
            details = [
                {"field": ".".join(map(str, e["loc"])), "reason": e["type"]} for e in exc.errors()
            ]
            results.append(_res(raw_id, EventStatus.invalid, "INVALID_SCHEMA", details))
            continue

        eid = str(ev.event_id)
        if ev.device_id != device.device_id:
            results.append(_res(eid, EventStatus.rejected, "DEVICE_MISMATCH"))
            continue
        if ev.clock_synchronized and ev.captured_at > now + timedelta(seconds=max_skew_s):
            results.append(_res(eid, EventStatus.invalid, "CAPTURED_AT_IN_FUTURE"))
            continue

        payload = ev.model_dump(mode="json")
        existing = session.scalar(select(TelemetryEvent).where(TelemetryEvent.event_id == eid))
        if existing:
            if existing.device_pk == device.id and existing.payload == payload:
                results.append(_res(eid, EventStatus.duplicate))
            else:
                session.add(
                    AuditEvent(
                        actor=f"device:{device.device_id}",
                        action="telemetry.conflict",
                        resource=f"event:{eid}",
                        result="rejected",
                    )
                )
                results.append(_res(eid, EventStatus.rejected, "EVENT_ID_CONFLICT"))
            continue
        seq_taken = session.scalar(
            select(TelemetryEvent.id).where(
                TelemetryEvent.device_pk == device.id, TelemetryEvent.sequence == ev.sequence
            )
        )
        if seq_taken:
            results.append(_res(eid, EventStatus.rejected, "SEQUENCE_CONFLICT"))
            continue

        row = TelemetryEvent(
            event_id=eid,
            device_pk=device.id,
            sequence=ev.sequence,
            captured_at=ev.captured_at,
            schema_version=ev.schema_version,
            firmware_version=ev.firmware_version,
            calibration_version=ev.calibration_version,
            clock_synchronized=ev.clock_synchronized,
            volume_total_liters=ev.measurements.volume_total_liters,
            flow_liters_per_minute=ev.measurements.flow_liters_per_minute,
            sensor_status=ev.quality.sensor_status.value,
            measurement_kind=ev.quality.measurement_kind.value,
            payload=payload,
        )
        try:
            with session.begin_nested():  # corrida entre requisições: a unicidade decide
                session.add(row)
            results.append(_res(eid, EventStatus.accepted))
        except IntegrityError:
            results.append(_res(eid, EventStatus.duplicate))
    session.commit()
    log.info("batch ingested device=%s n=%d", device.device_id, len(results))
    return results
