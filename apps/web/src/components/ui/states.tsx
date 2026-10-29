import type { ReactNode } from "react";
import { ApiError } from "../../lib/api/client";

export function Skeleton({ height = 24 }: { height?: number }) {
  return <div className="skeleton" style={{ height }} aria-hidden="true" />;
}

export function ErrorState({ error, onRetry }: { error: unknown; onRetry?: () => void }) {
  const e = error instanceof ApiError ? error : null;
  const msg = e?.status === 0 ? "Sem conexão. Verifique sua internet e tente novamente." : e?.message ?? "Algo deu errado.";
  return (
    <div className="error" role="alert">
      <strong>{msg}</strong>
      {e?.requestId && <div className="num" style={{ fontSize: "0.875rem" }}>Código para o suporte: {e.requestId}</div>}
      {onRetry && <div style={{ marginTop: 8 }}><button className="btn ghost" onClick={onRetry}>Tentar novamente</button></div>}
    </div>
  );
}

export function EmptyState({ title, children }: { title: string; children?: ReactNode }) {
  return (
    <div className="card" style={{ textAlign: "center" }}>
      <h2>{title}</h2>
      <p style={{ color: "var(--muted)", margin: 0 }}>{children}</p>
    </div>
  );
}

export function StatusPill({ tone, children }: { tone: "ok" | "warn" | "err" | "muted"; children: ReactNode }) {
  const icon = tone === "ok" ? "●" : tone === "warn" ? "▲" : tone === "err" ? "■" : "○"; // formas distintas: não depende só de cor
  return <span className={`pill ${tone}`}><span aria-hidden="true">{icon}</span>{children}</span>;
}
