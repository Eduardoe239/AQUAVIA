# Contribuindo
- PRs pequenos: problema, abordagem, testes, risco, rollback. Screenshot para UI.
- Definition of Done: requisito ligado a teste; lint/typecheck/testes verdes; segurança considerada; docs e migração seguras.
- Decisão de arquitetura relevante ⇒ ADR em `docs/adr/`. Não trocar stack sem ADR.
- Nunca versionar segredos, dados reais ou certificados. Fixtures são sintéticas.
- Nunca editar migração já aplicada em ambiente compartilhado; crie nova.
