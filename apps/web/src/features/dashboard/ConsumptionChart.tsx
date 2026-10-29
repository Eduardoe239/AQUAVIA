import { useId } from "react";
import { bucketLabel, hasAnyData, niceMax } from "../../lib/chart";
import type { Timeseries } from "../../lib/api/client";
import { formatVolume } from "../../lib/units";

const W = 640, H = 260, M = { t: 12, r: 12, b: 32, l: 56 };
const qualityText = { measured: "medido", estimated: "estimado", corrected: "corrigido" } as const;

export function ConsumptionChart({ data, periodLabel }: { data: Timeseries; periodLabel: string }) {
  const id = useId();
  const { buckets, granularity, timezone } = data;
  if (!hasAnyData(buckets)) {
    return <p style={{ color: "var(--muted)" }}>Sem dados neste período. Os dados aparecem após a primeira sincronização do dispositivo.</p>;
  }
  const max = niceMax(Math.max(...buckets.map((b) => b.volume_liters ?? 0)));
  const iw = W - M.l - M.r, ih = H - M.t - M.b, bw = iw / buckets.length;
  const y = (v: number) => M.t + ih - (v / max) * ih;
  const ticks = [0, 0.25, 0.5, 0.75, 1].map((f) => f * max);
  const step = Math.ceil(buckets.length / 8);
  const summary = `Gráfico de barras do consumo em litros, ${periodLabel}. ` +
    `Total ${formatVolume(buckets.reduce((s, b) => s + (b.volume_liters ?? 0), 0))}. A tabela abaixo traz os mesmos valores.`;
  return (
    <div>
      <div className="chart-wrap">
        <svg viewBox={`0 0 ${W} ${H}`} role="img" aria-label={summary} style={{ width: "100%", minWidth: 480, height: "auto" }}>
          <defs>
            <pattern id={`${id}-est`} width="6" height="6" patternUnits="userSpaceOnUse" patternTransform="rotate(45)">
              <rect width="6" height="6" fill="#fff" /><rect width="3" height="6" fill="var(--blue)" />
            </pattern>
          </defs>
          {ticks.map((t) => (
            <g key={t}>
              <line x1={M.l} x2={W - M.r} y1={y(t)} y2={y(t)} stroke="var(--border)" />
              <text x={M.l - 6} y={y(t) + 4} textAnchor="end" fontSize="11" fill="var(--muted)">{formatVolume(t)}</text>
            </g>
          ))}
          {buckets.map((b, i) => {
            const x = M.l + i * bw + bw * 0.15, w = bw * 0.7;
            const label = bucketLabel(b.start, granularity, timezone);
            return (
              <g key={b.start}>
                {b.volume_liters == null ? (
                  <line x1={x} x2={x + w} y1={y(0) - 2} y2={y(0) - 2} stroke="var(--muted)" strokeDasharray="2 2"><title>{`${label}: sem dados`}</title></line>
                ) : (
                  <rect x={x} y={y(b.volume_liters)} width={w} height={Math.max(0, y(0) - y(b.volume_liters))} rx="2"
                    fill={b.quality === "estimated" ? `url(#${id}-est)` : "var(--blue)"}
                    stroke={b.quality === "estimated" ? "var(--blue)" : "none"} tabIndex={0}
                    aria-label={`${label}: ${formatVolume(b.volume_liters)}, ${qualityText[b.quality ?? "measured"]}`}>
                    <title>{`${label}: ${formatVolume(b.volume_liters)} (${qualityText[b.quality ?? "measured"]})`}</title>
                  </rect>
                )}
                {i % step === 0 && <text x={x + w / 2} y={H - 10} textAnchor="middle" fontSize="11" fill="var(--muted)">{label}</text>}
              </g>
            );
          })}
        </svg>
      </div>
      <p style={{ fontSize: "0.875rem", color: "var(--muted)" }}>
        <span aria-hidden="true" style={{ color: "var(--blue)" }}>■</span> medido &nbsp;
        <span aria-hidden="true" style={{ color: "var(--blue)" }}>▨</span> estimado &nbsp; ┄ sem dados (não é consumo zero)
      </p>
      <details>
        <summary>Ver dados em tabela</summary>
        <table>
          <caption className="sr-only">Consumo por período</caption>
          <thead><tr><th scope="col">Período</th><th scope="col">Volume</th><th scope="col">Qualidade</th></tr></thead>
          <tbody>
            {buckets.map((b) => (
              <tr key={b.start}>
                <th scope="row">{bucketLabel(b.start, granularity, timezone)}</th>
                <td className="num">{formatVolume(b.volume_liters)}</td>
                <td>{b.quality ? qualityText[b.quality] : "sem dados"}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </details>
    </div>
  );
}
