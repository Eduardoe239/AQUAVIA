#!/usr/bin/env python3
"""Simulador de dispositivo AQUAVIA: gera telemetria v1, mantém fila offline e
envia lotes com retry exponencial + jitter. Só remove da fila eventos
accepted/duplicate (regra do ADR 0003). Dados 100% sintéticos."""
import argparse
import json
import random
import time
import urllib.error
import urllib.request
import uuid
from datetime import UTC, datetime, timedelta


def build_events(device_id: str, n: int, start_seq: int, rng: random.Random) -> list[dict]:
    t0, volume, out = datetime.now(UTC) - timedelta(minutes=5 * n), 1000.0, []
    for i in range(n):
        flow = max(0.0, rng.gauss(4.0, 1.5))
        volume += flow * 5  # intervalo de 5 min
        out.append({
            "schema_version": 1, "event_id": str(uuid.uuid4()), "device_id": device_id,
            "sequence": start_seq + i,
            "captured_at": (t0 + timedelta(minutes=5 * i)).isoformat().replace("+00:00", "Z"),
            "clock_synchronized": True, "firmware_version": "sim-0.1.0", "calibration_version": 1,
            "measurements": {"volume_total_liters": round(volume, 3),
                             "flow_liters_per_minute": round(flow, 3)},
            "quality": {"sensor_status": "ok", "measurement_kind": "measured"},
        })
    return out


def send(url: str, dev: str, key: str, events: list[dict]) -> list[dict]:
    body = json.dumps({"batch_id": str(uuid.uuid4()), "events": events}).encode()
    req = urllib.request.Request(f"{url}/api/v1/telemetry/batch", body, {
        "Content-Type": "application/json", "X-Device-Id": dev, "X-Device-Key": key})
    with urllib.request.urlopen(req, timeout=10) as r:  # noqa: S310
        return json.load(r)["results"]


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--url", default="http://localhost:8000")
    p.add_argument("--device-id", required=True)
    p.add_argument("--key", required=True)
    p.add_argument("--events", type=int, default=50)
    p.add_argument("--batch-size", type=int, default=20)
    p.add_argument("--drop-rate", type=float, default=0.0, help="prob. de falha de rede por envio")
    p.add_argument("--seed", type=int, default=1)
    a = p.parse_args()
    rng = random.Random(a.seed)
    queue = build_events(a.device_id, a.events, 1, rng)
    attempt = 0
    while queue:
        batch = queue[: a.batch_size]
        try:
            if rng.random() < a.drop_rate:
                raise urllib.error.URLError("simulated network loss")
            results = {r["event_id"]: r for r in send(a.url, a.device_id, a.key, batch)}
            done = {e for e, r in results.items() if r["status"] in ("accepted", "duplicate")}
            bad = [r for r in results.values() if r["status"] in ("invalid", "rejected")]
            queue = [e for e in queue if e["event_id"] not in done]
            print(f"acked={len(done)} pending={len(queue)} problems={len(bad)}")
            if bad and not done:  # evita loop infinito com evento permanentemente inválido
                raise SystemExit(f"eventos recusados: {bad[:3]}")
            attempt = 0
        except (urllib.error.URLError, TimeoutError) as exc:
            attempt += 1
            delay = min(30, 2 ** attempt) * rng.uniform(0.5, 1.0)  # backoff + jitter
            print(f"offline ({exc}); fila={len(queue)}; retry em {delay:.1f}s")
            time.sleep(min(delay, 1.0))  # limitado no simulador para ser rápido


if __name__ == "__main__":
    main()
