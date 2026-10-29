export interface Bucket { start: string; volume_liters: number | null; quality: string | null }

export function niceMax(max: number): number {
  if (max <= 0) return 1;
  const exp = Math.pow(10, Math.floor(Math.log10(max)));
  for (const m of [1, 2, 5, 10]) if (max <= m * exp) return m * exp;
  return 10 * exp;
}

export function bucketLabel(iso: string, granularity: "hour" | "day", tz: string): string {
  const d = new Date(iso);
  return granularity === "hour"
    ? new Intl.DateTimeFormat("pt-BR", { hour: "2-digit", minute: "2-digit", timeZone: tz }).format(d)
    : new Intl.DateTimeFormat("pt-BR", { day: "2-digit", month: "2-digit", timeZone: tz }).format(d);
}

export function hasAnyData(buckets: Bucket[]): boolean {
  return buckets.some((b) => b.volume_liters != null);
}
