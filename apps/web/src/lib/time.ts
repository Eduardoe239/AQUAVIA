export type Connection = "never_reported" | "online" | "delayed" | "offline";

export function formatAge(seconds: number): string {
  if (seconds < 60) return "há instantes";
  const m = Math.floor(seconds / 60);
  if (m < 60) return `há ${m} min`;
  const h = Math.floor(m / 60);
  if (h < 48) return `há ${h} h`;
  return `há ${Math.floor(h / 24)} dias`;
}

/** Texto acionável em vez de "Offline" isolado. */
export function connectionText(c: Connection, ageSeconds: number | null): string {
  if (c === "never_reported" || ageSeconds == null) return "Aguardando a primeira leitura";
  if (c === "online") return `Sincronizado ${formatAge(ageSeconds)}`;
  if (c === "delayed") return `Sincronização atrasada — última leitura ${formatAge(ageSeconds)}`;
  return `Sem comunicação — última leitura ${formatAge(ageSeconds)}`;
}

export function localDate(d: Date): string {
  const p = (n: number) => String(n).padStart(2, "0");
  return `${d.getFullYear()}-${p(d.getMonth() + 1)}-${p(d.getDate())}`;
}

export type Period = "day" | "week" | "month";

export function periodRange(period: Period, now: Date): { start: string; end: string; granularity: "hour" | "day" } {
  const end = localDate(now);
  if (period === "day") return { start: end, end, granularity: "hour" };
  if (period === "week") {
    const s = new Date(now); s.setDate(s.getDate() - 6);
    return { start: localDate(s), end, granularity: "day" };
  }
  const s = new Date(now.getFullYear(), now.getMonth(), 1);
  return { start: localDate(s), end, granularity: "day" };
}
