from datetime import datetime
from enum import StrEnum
from typing import Annotated, Literal
from uuid import UUID

from pydantic import AfterValidator, BaseModel, ConfigDict, Field


def _utc(v: datetime) -> datetime:
    if v.tzinfo is None or v.utcoffset() is None:
        raise ValueError("timezone_required")
    return v


class SensorStatus(StrEnum):
    ok = "ok"
    degraded = "degraded"
    fault = "fault"
    disconnected = "disconnected"


class MeasurementKind(StrEnum):
    measured = "measured"
    estimated = "estimated"
    corrected = "corrected"
    invalid = "invalid"


class _Strict(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)


class Measurements(_Strict):
    volume_total_liters: Annotated[float, Field(ge=0, allow_inf_nan=False)]
    flow_liters_per_minute: Annotated[float, Field(ge=0, allow_inf_nan=False)]


class Quality(_Strict):
    sensor_status: SensorStatus
    measurement_kind: MeasurementKind


class TelemetryEventV1(_Strict):
    schema_version: Literal[1]
    event_id: UUID
    device_id: Annotated[str, Field(min_length=1, max_length=64)]
    sequence: Annotated[int, Field(ge=0)]
    captured_at: Annotated[datetime, AfterValidator(_utc)]
    clock_synchronized: bool
    firmware_version: Annotated[str, Field(max_length=32)]
    calibration_version: Annotated[int, Field(ge=1)]
    measurements: Measurements
    quality: Quality


class BatchRequest(BaseModel):
    """Eventos chegam como dicts crus: cada um é validado individualmente,
    para que um evento ruim não derrube o lote inteiro."""

    model_config = ConfigDict(extra="forbid")
    batch_id: UUID
    events: Annotated[list[dict], Field(min_length=1)]


class EventStatus(StrEnum):
    accepted = "accepted"
    duplicate = "duplicate"
    invalid = "invalid"
    rejected = "rejected"


class EventResult(BaseModel):
    event_id: str | None
    status: EventStatus
    code: str | None = None
    details: list[dict] | None = None


class BatchResponse(BaseModel):
    batch_id: UUID
    results: list[EventResult]
