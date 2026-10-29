# AQUAVIA — Uma união para um gasto eficiente

Monorepo do MVP. Fonte de verdade de produto: *Documento Mestre* e *Documento de Desenvolvimento* v1.0.

## Método
Fatias verticais: dispositivo mede → fila local → lote → API valida → PostgreSQL → dashboard → alerta.
Monólito modular, eventos versionados, idempotência por `event_id`, UTC na API, unidades explícitas.

## Estado (Sprints 0, 1 e 2 concluídas)
| Item | Situação |
|---|---|
| ADRs 0001–0006 | feitos |
| `GET /properties`, `/consumption/summary`, `/consumption/timeseries` (agregação v1, lacuna ≠ zero) | feito, testado |
| Frontend `apps/web`: login, Home (hoje/mês, histórico dia/semana/mês, saúde do dispositivo), gráfico SVG acessível com tabela alternativa | feito; typecheck, build e 8 testes verdes |
| Login por cookie HttpOnly, `/me`, escopo por organização/propriedade | feito, testado (inclui IDOR) |
| `POST /devices/claim` (código de uso único), `GET /devices`, `GET /devices/{id}/status` | feito, testado |
| Contrato de telemetria v1 (JSON Schema + fixtures) | feito |
| API: `POST /api/v1/telemetry/batch` (auth de dispositivo, idempotência, resposta por evento) | feito, testado |
| Migração Alembic inicial | feita, testada |
| Simulador de dispositivo (fila offline, retry com backoff+jitter) | feito |
| Firmware: componente `metering` (C puro, testável no host) | feito, testado |
| Docker Compose + CI | feitos |

## Início rápido
```bash
cp .env.example .env
make up                      # db + api (aplica migrações)
docker compose -f infra/compose/docker-compose.yml exec api python -m app.cli seed-demo demo@example.invalid 'troque-esta-senha'
# imprime property_id, device_id, device_key e activation_code (uma única vez)
python tools/simulator/simulate.py --device-id <id> --key <key> --events 50 --drop-rate 0.3
```
Testes: `make api-test` e `make fw-test`.

## Frontend
```bash
cd apps/web && npm install && npm run dev   # http://localhost:5173, proxy /api -> :8000
npm test && npm run build
```
Dados do simulador aparecem com aviso "Dados simulados". Ainda sem dark mode (tokens prontos para isso).

## Próximo (Sprint 3 — Firmware de bancada)
Driver de sensor candidato (interface init/read_raw/get_health/self_test), `persistent_queue` com checksum e escrita atômica, `event_builder` (event_id/sequência), simulador de sensor, testes de brownout/flash cheia no host.
Pendências: reset explícito de volume (ADR 0003), RLS (ADR 0005), página de dispositivo e alertas (Sprint 5), cliente de API gerado do OpenAPI.
