const nf = (digits: number) =>
  new Intl.NumberFormat("pt-BR", { minimumFractionDigits: digits, maximumFractionDigits: digits });

/** Apenas apresentação: a API é sempre em litros e nada é arredondado antes de agregar. */
export function formatVolume(liters: number | null | undefined): string {
  if (liters == null) return "—";
  return Math.abs(liters) >= 1000
    ? `${nf(2).format(liters / 1000)} m³`
    : `${nf(liters % 1 === 0 ? 0 : 1).format(liters)} L`;
}

export function formatDeltaPct(current: number | null, previous: number | null): string | null {
  if (current == null || previous == null || previous === 0) return null;
  const pct = ((current - previous) / previous) * 100;
  const sign = pct > 0 ? "+" : pct < 0 ? "−" : "";
  return `${sign}${nf(0).format(Math.abs(pct))}%`;
}
