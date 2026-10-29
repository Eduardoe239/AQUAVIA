# ADR 0002 — Stack do MVP
- Data: 2026-10-29 · Status: aceito (revisável)
## Decisão
Firmware ESP32/ESP-IDF (candidato, não irreversível); backend Python 3.12 + FastAPI + Pydantic v2 + SQLAlchemy 2 + Alembic + PostgreSQL; frontend React + TypeScript + Vite + TanStack Query (Sprint 2); Docker Compose local; GitHub Actions.
## Consequências
Versões fixadas por lockfile antes do piloto; validar CVE/licença antes de fixar. MCU sujeito a validação de memória, segurança e ciclo de vida.
