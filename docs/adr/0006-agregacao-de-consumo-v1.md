# ADR 0006 — Agregação de consumo v1 (sob demanda)
- Data: 2026-10-29 · Status: aceito para MVP
## Decisão
Consumo = delta entre volumes acumulados consecutivos (por `sequence`) de eventos não inválidos, atribuído ao intervalo do evento mais recente; calculado sob demanda a partir de `telemetry_events` (algoritmo `v1`, devolvido na API). O primeiro evento é só linha de base.
Regressão de volume nunca vira consumo negativo: é ignorada, contada em `regressions_ignored` e vira nova base. Lacuna ≠ zero: balde sem delta retorna `volume_liters: null`. Qualidade do balde: `estimated` > `corrected` > `measured`. Fuso por parâmetro `tz` (padrão America/Sao_Paulo); baldes em UTC na resposta; sem arredondamento antes de somar.
Dados de firmware `sim-*` marcam `simulated: true` e a UI exibe aviso.
## Consequências
Simples e correto no MVP; custo cresce com o volume. Quando a medição indicar, materializar `consumption_buckets` (chave entidade/período/`aggregation_version`) via worker idempotente, mantendo este algoritmo como referência de teste.
