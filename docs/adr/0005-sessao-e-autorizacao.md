# ADR 0005 — Sessão de usuário, CSRF e isolamento de tenant
- Data: 2026-10-29 · Status: aceito para MVP
## Decisão
Sessão em cookie `HttpOnly; SameSite=Strict` (`Secure` em produção), token HMAC-SHA256 com expiração (sem localStorage). Mutações exigem `X-Requested-With: aquavia-web` (defesa em profundidade). Senhas com scrypt; verificação em tempo constante mesmo sem usuário; limite de tentativas por e-mail+IP (em memória no MVP; mover para store compartilhado antes de múltiplas réplicas).
Autorização por objeto: toda consulta de dispositivo é escopada por `memberships → properties`. Recurso de outro tenant responde 404 idêntico ao inexistente. Ativação (`/devices/claim`) exige papel owner/admin, código de uso único (hash) e não distingue código errado de dispositivo indisponível; tudo auditado.
## Pendente
Refresh/revogação de sessão, reset de senha, MFA para admin, RLS no PostgreSQL como camada adicional.
