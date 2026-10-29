from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel, Field

from app.api.v1.deps import SessionDep, UserDep, csrf_guard
from app.core.config import get_settings
from app.core.errors import ApiError
from app.domains.devices import service
from app.domains.identity import service as identity

router = APIRouter(prefix="/devices", tags=["devices"])
NOT_FOUND = ApiError(404, "NOT_FOUND", "Recurso não encontrado.")


class DeviceOut(BaseModel):
    device_id: str
    property_id: str | None
    status: str
    claimed_at: datetime | None


class ClaimIn(BaseModel):
    device_id: Annotated[str, Field(min_length=1, max_length=64)]
    activation_code: Annotated[str, Field(min_length=8, max_length=128)]
    property_id: Annotated[str, Field(min_length=1, max_length=36)]


def _out(d) -> DeviceOut:
    return DeviceOut(
        device_id=d.device_id, property_id=d.property_id, status=d.status, claimed_at=d.claimed_at
    )


@router.get("")
def list_devices(
    user: UserDep,
    session: SessionDep,
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
    offset: Annotated[int, Query(ge=0)] = 0,
):
    rows = service.visible_devices(session, identity.org_ids(session, user.id), limit, offset)
    return {"items": [_out(d) for d in rows], "limit": limit, "offset": offset}


@router.post("/claim", dependencies=[Depends(csrf_guard)])
def claim(body: ClaimIn, user: UserDep, session: SessionDep):
    prop = identity.get_property(session, body.property_id)
    role = identity.role_in_org(session, user.id, prop.org_id) if prop else None
    if role not in ("owner", "admin"):  # inexistente e sem permissão são indistinguíveis
        raise ApiError(404, "NOT_FOUND", "Recurso não encontrado.")
    device = service.claim(
        session, f"user:{user.id}", body.device_id, body.activation_code, prop.id
    )
    if not device:
        raise ApiError(404, "ACTIVATION_INVALID", "Código inválido ou dispositivo indisponível.")
    return _out(device)


@router.get("/{device_id}/status")
def device_status(device_id: str, user: UserDep, session: SessionDep):
    s = get_settings()
    device = service.get_visible_device(session, identity.org_ids(session, user.id), device_id)
    if not device:
        raise ApiError(404, "NOT_FOUND", "Recurso não encontrado.")
    st = service.status_of(session, device, s.online_max_age_seconds, s.delayed_max_age_seconds)
    return {"device_id": device.device_id, **st.__dict__}
