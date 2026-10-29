# ADR 0004 — Credencial de dispositivo
- Data: 2026-10-29 · Status: aceito para MVP
## Decisão
Credencial separada da sessão de usuário: cabeçalhos `X-Device-Id` + `X-Device-Key`. Servidor guarda apenas SHA-256 do segredo (256 bits aleatórios) e compara em tempo constante. `device_id` do evento deve igualar o autenticado.
## Consequências
Revogação por `status != active`. Evolução prevista: certificados por dispositivo (mTLS/MQTT) conforme ADR de transporte.
