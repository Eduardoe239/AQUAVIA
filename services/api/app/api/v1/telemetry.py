from typing import Annotated

from fastapi import APIRouter, Depends, Header
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.errors import ApiError
from app.db.models import Device
from app.db.session import get_session
from app.domains.telemetry import service
from app.schemas.telemetry import BatchRequest, BatchResponse

router = APIRouter(prefix="/telemetry", tags=["telemetry"])
SessionDep = Annotated[Session, Depends(get_session)]


def device_auth(
    session: SessionDep,
    x_device_id: Annotated[str | None, Header()] = None,
    x_device_key: Annotated[str | None, Header()] = None,
) -> Device:
    device = service.authenticate(session, x_device_id or "", x_device_key or "")
    if not device:
        raise ApiError(401, "DEVICE_UNAUTHORIZED", "Credencial de dispositivo inválida.")
    return device


@router.post("/batch", response_model=BatchResponse)
def post_batch(
    body: BatchRequest, session: SessionDep, device: Annotated[Device, Depends(device_auth)]
):
    s = get_settings()
    if len(body.events) > s.max_batch_events:
        raise ApiError(422, "BATCH_TOO_LARGE", "Lote acima do limite.")
    results = service.ingest(session, device, body.events, s.max_clock_skew_seconds)
    return BatchResponse(batch_id=body.batch_id, results=results)
