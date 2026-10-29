# ADR 0001 — Monólito modular
- Data: 2026-10-29 · Responsável: a designar · Status: aceito
## Contexto
MVP com equipe pequena; Documento de Desenvolvimento §Princípio veta microserviços/IA iniciais.
## Alternativas
Microserviços; monólito modular; serverless.
## Decisão
Um único serviço FastAPI organizado por domínio (`app/domains/*`), worker separado só quando houver jobs assíncronos (Sprint 5).
## Consequências
Deploy simples e transações locais; fronteiras de módulo exigem disciplina (sem importações circulares, sem regra de negócio em handlers).
