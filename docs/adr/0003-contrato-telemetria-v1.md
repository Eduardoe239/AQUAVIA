# ADR 0003 — Contrato de telemetria v1 e idempotência
- Data: 2026-10-29 · Status: aceito
## Decisão
Envelope versionado (`packages/contracts`). `event_id` único e imutável; `sequence` monotônica por dispositivo; `captured_at` em UTC; qualidade explícita (`measured|estimated|corrected|invalid`).
Lote: resposta por evento (`accepted|duplicate|invalid|rejected`) com código estável; HTTP 200 mesmo em sucesso parcial. O firmware só apaga da fila eventos `accepted` ou `duplicate`.
Mesmo `event_id` com payload divergente ⇒ `rejected/EVENT_ID_CONFLICT` e log de auditoria. Mesma `sequence` com outro `event_id` ⇒ `rejected/SEQUENCE_CONFLICT`.
## Pendente
Regressão de volume exige evento de reset explícito (campo a definir na v1.1, aditivo).
