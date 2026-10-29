from datetime import UTC, date, datetime, timedelta
from typing import Annotated
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from fastapi import APIRouter, Query
from sqlalchemy import select

from app.api.v1.deps import SessionDep, UserDep
from app.core.config import get_settings
from app.core.errors import ApiError
from app.db.models import Device, Property
from app.domains.consumption import service as cons
from app.domains.devices import service as devices
from app.domains.identity import service as identity

router = APIRouter(tags=["consumption"])
DEFAULT_TZ = "America/Sao_Paulo"


def _tz(name: str) -> ZoneInfo:
    try:
        return ZoneInfo(name)
    except (ZoneInfoNotFoundError, ValueError, OSError) as exc:
        raise ApiError(422, "TIMEZONE_INVALID", "Fuso horário inválido.") from exc


def _property(session, user, property_id: str) -> Property:
    prop = identity.get_property(session, property_id)
    if not prop or prop.org_id not in identity.org_ids(session, user.id):
        raise ApiError(404, "NOT_FOUND", "Recurso não encontrado.")
    return prop


@router.get("/properties")
def list_properties(user: UserDep, session: SessionDep):
    ids = identity.org_ids(session, user.id)
    rows = session.scalars(select(Property).where(Property.org_id.in_(ids)).order_by(Property.name))
    return {"items": [{"id": p.id, "org_id": p.org_id, "name": p.name} for p in rows]}


@router.get("/consumption/summary")
def summary(
    user: UserDep,
    session: SessionDep,
    property_id: str,
    tz: Annotated[str, Query(max_length=64)] = DEFAULT_TZ,
):
    s = get_settings()
    prop = _property(session, user, property_id)
    zone = _tz(tz)
    today = datetime.now(UTC).astimezone(zone).date()
    d0, d1 = cons.local_midnight(today, zone), cons.local_midnight(today + timedelta(days=1), zone)
    dy = cons.local_midnight(today - timedelta(days=1), zone)
    m0 = cons.local_midnight(cons.first_of_month(today), zone)
    prev_month_first = cons.first_of_month(cons.first_of_month(today) - timedelta(days=1))
    pm0 = cons.local_midnight(prev_month_first, zone)
    pks = cons.property_device_pks(session, prop.id)
    items, regressions = cons.deltas(session, pks, pm0, d1)
    devs = list(session.scalars(select(Device).where(Device.property_id == prop.id)))
    statuses = []
    simulated = False
    for d in devs:
        st = devices.status_of(session, d, s.online_max_age_seconds, s.delayed_max_age_seconds)
        simulated = simulated or bool(
            st.firmware_version and st.firmware_version.startswith("sim-")
        )
        statuses.append(
            {
                "device_id": d.device_id,
                "connection": st.connection,
                "age_seconds": st.age_seconds,
                "last_reading_at": st.last_reading_at,
                "last_sync_at": st.last_sync_at,
                "sensor_status": st.sensor_status,
            }
        )
    return {
        "property_id": prop.id,
        "unit": "L",
        "timezone": tz,
        "algorithm_version": cons.ALGORITHM_VERSION,
        "today_liters": cons.total(items, d0, d1),
        "yesterday_liters": cons.total(items, dy, d0),
        "month_liters": cons.total(items, m0, d1),
        "previous_month_liters": cons.total(items, pm0, m0),
        "regressions_ignored": regressions,
        "simulated": simulated,
        "devices": statuses,
    }


@router.get("/consumption/timeseries")
def timeseries(
    user: UserDep,
    session: SessionDep,
    property_id: str,
    start: date,
    end: date,
    granularity: Annotated[str, Query(pattern="^(hour|day)$")] = "day",
    tz: Annotated[str, Query(max_length=64)] = DEFAULT_TZ,
):
    prop = _property(session, user, property_id)
    zone = _tz(tz)
    span = (end - start).days + 1
    if span < 1 or span > (7 if granularity == "hour" else 366):
        raise ApiError(422, "RANGE_INVALID", "Intervalo fora do limite permitido.")
    bucket_edges = cons.edges(start, end, granularity, zone)
    items, regressions = cons.deltas(
        session, cons.property_device_pks(session, prop.id), bucket_edges[0], bucket_edges[-1]
    )
    return {
        "property_id": prop.id,
        "unit": "L",
        "timezone": tz,
        "granularity": granularity,
        "algorithm_version": cons.ALGORITHM_VERSION,
        "regressions_ignored": regressions,
        "buckets": cons.bucketize(items, bucket_edges),
    }
