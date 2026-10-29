"""Agregação de consumo — algoritmo v1.

Consumo = diferença entre volumes acumulados consecutivos (por sequência) de eventos
não inválidos, atribuída ao intervalo do evento mais recente. Regras:
- o primeiro evento de um dispositivo é só linha de base (não gera consumo);
- volume que regride não vira consumo negativo: é contado em `regressions` e vira nova base;
- lacunas NUNCA viram zero: balde sem nenhum delta fica `None` ("sem dados");
- nenhum arredondamento antes de somar.
"""

from bisect import bisect_right
from dataclasses import dataclass
from datetime import UTC, date, datetime, time, timedelta
from zoneinfo import ZoneInfo

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import Device, TelemetryEvent

ALGORITHM_VERSION = "v1"


@dataclass(frozen=True)
class Delta:
    ts: datetime
    liters: float
    kind: str


def _aware(dt: datetime) -> datetime:
    return dt if dt.tzinfo else dt.replace(tzinfo=UTC)


def property_device_pks(session: Session, property_id: str) -> list[str]:
    return list(session.scalars(select(Device.id).where(Device.property_id == property_id)))


def deltas(
    session: Session, device_pks: list[str], start: datetime, end: datetime
) -> tuple[list[Delta], int]:
    out: list[Delta] = []
    regressions = 0
    for pk in device_pks:
        base = session.scalar(
            select(TelemetryEvent)
            .where(
                TelemetryEvent.device_pk == pk,
                TelemetryEvent.captured_at < start,
                TelemetryEvent.measurement_kind != "invalid",
            )
            .order_by(TelemetryEvent.sequence.desc())
            .limit(1)
        )
        events = session.scalars(
            select(TelemetryEvent)
            .where(
                TelemetryEvent.device_pk == pk,
                TelemetryEvent.captured_at >= start,
                TelemetryEvent.captured_at < end,
            )
            .order_by(TelemetryEvent.sequence)
        )
        prev = base
        for ev in events:
            if ev.measurement_kind == "invalid":
                continue
            if prev is not None:
                d = float(ev.volume_total_liters) - float(prev.volume_total_liters)
                if d >= 0:
                    out.append(Delta(_aware(ev.captured_at), d, ev.measurement_kind))
                else:
                    regressions += 1
            prev = ev
    return out, regressions


def _quality(kinds: set[str]) -> str:
    if "estimated" in kinds:
        return "estimated"
    return "corrected" if "corrected" in kinds else "measured"


def local_midnight(d: date, tz: ZoneInfo) -> datetime:
    return datetime.combine(d, time.min, tz).astimezone(UTC)


def edges(start: date, end: date, granularity: str, tz: ZoneInfo) -> list[datetime]:
    """Limites dos baldes em UTC; `end` é inclusivo (data local)."""
    first, stop = local_midnight(start, tz), local_midnight(end + timedelta(days=1), tz)
    if granularity == "hour":
        n = int((stop - first).total_seconds() // 3600)
        return [first + timedelta(hours=i) for i in range(n + 1)]
    days = (end - start).days + 1
    return [local_midnight(start + timedelta(days=i), tz) for i in range(days)] + [stop]


def bucketize(items: list[Delta], bucket_edges: list[datetime]) -> list[dict]:
    sums: list[float | None] = [None] * (len(bucket_edges) - 1)
    kinds: list[set[str]] = [set() for _ in sums]
    for d in items:
        i = bisect_right(bucket_edges, d.ts) - 1
        if 0 <= i < len(sums):
            sums[i] = (sums[i] or 0.0) + d.liters
            kinds[i].add(d.kind)
    return [
        {
            "start": bucket_edges[i].isoformat().replace("+00:00", "Z"),
            "volume_liters": None if v is None else round(v, 3),
            "quality": None if v is None else _quality(kinds[i]),
        }
        for i, v in enumerate(sums)
    ]


def total(items: list[Delta], start: datetime, end: datetime) -> float | None:
    sel = [d.liters for d in items if start <= d.ts < end]
    return round(sum(sel), 3) if sel else None


def first_of_month(d: date) -> date:
    return d.replace(day=1)
