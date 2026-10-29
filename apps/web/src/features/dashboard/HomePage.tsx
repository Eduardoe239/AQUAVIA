import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { ErrorState, EmptyState, Skeleton } from "../../components/ui/states";
import { api } from "../../lib/api/client";
import { type Period, periodRange } from "../../lib/time";
import { formatDeltaPct, formatVolume } from "../../lib/units";
import { ConsumptionChart } from "./ConsumptionChart";
import { DeviceHealthCard } from "./DeviceHealthCard";
import { MetricCard } from "./MetricCard";

const tz = Intl.DateTimeFormat().resolvedOptions().timeZone;
const periods: { id: Period; label: string }[] = [
  { id: "day", label: "Dia" }, { id: "week", label: "Semana" }, { id: "month", label: "Mês" },
];

export function HomePage() {
  const nav = useNavigate();
  const qc = useQueryClient();
  const [period, setPeriod] = useState<Period>("day");
  const props = useQuery({ queryKey: ["properties"], queryFn: api.properties });
  const propertyId = props.data?.items[0]?.id;
  const summary = useQuery({
    queryKey: ["summary", propertyId], enabled: !!propertyId, refetchInterval: 60_000,
    queryFn: () => api.summary(propertyId!, tz),
  });
  const range = periodRange(period, new Date());
  const series = useQuery({
    queryKey: ["series", propertyId, period], enabled: !!propertyId, refetchInterval: 60_000,
    queryFn: () => api.timeseries({ property_id: propertyId!, ...range, tz }),
  });
  const logout = useMutation({
    mutationFn: api.logout,
    onSuccess: () => { qc.clear(); nav("/login"); },
  });

  const s = summary.data;
  const vsYesterday = s ? formatDeltaPct(s.today_liters, s.yesterday_liters) : null;
  const periodLabel = periods.find((p) => p.id === period)!.label.toLowerCase();

  return (
    <>
      <header className="header">
        <div className="inner">
          <img src="/brand/aquavia-logo-horizontal-dark.svg" alt="AQUAVIA" height={36} style={{ display: "block" }} />
          <button className="btn ghost" style={{ color: "#fff", borderColor: "#fff" }} onClick={() => logout.mutate()}>Sair</button>
        </div>
      </header>
      <main className="page">
        <h1>Consumo de água</h1>
        {props.isError && <ErrorState error={props.error} onRetry={() => props.refetch()} />}
        {props.isSuccess && !propertyId && <EmptyState title="Nenhuma propriedade ainda">Quando o técnico concluir a instalação, o seu consumo aparece aqui.</EmptyState>}
        {s?.simulated && <div className="banner" role="status"><strong>Dados simulados.</strong> Estes valores vêm de um dispositivo de teste, não de uma medição real.</div>}
        {summary.isError && <ErrorState error={summary.error} onRetry={() => summary.refetch()} />}
        {summary.isLoading && <div className="grid three"><Skeleton height={96} /><Skeleton height={96} /><Skeleton height={96} /></div>}
        {s && (
          <div className="grid three">
            <MetricCard label="Hoje" value={formatVolume(s.today_liters)} hint={s.today_liters == null ? "Sem leituras hoje" : vsYesterday ? `${vsYesterday} em relação a ontem (dia completo)` : undefined} />
            <MetricCard label="Mês atual" value={formatVolume(s.month_liters)} hint={s.previous_month_liters != null ? `Mês anterior: ${formatVolume(s.previous_month_liters)}` : undefined} />
            <MetricCard label="Meta" value="—" hint="Defina uma meta em breve" />
          </div>
        )}
        {propertyId && (
          <section className="card" aria-labelledby="hist-h">
            <h2 id="hist-h">Histórico</h2>
            <div className="seg" role="group" aria-label="Período">
              {periods.map((p) => <button key={p.id} className="btn" aria-pressed={period === p.id} onClick={() => setPeriod(p.id)}>{p.label}</button>)}
            </div>
            <div style={{ marginTop: 16 }} aria-live="polite">
              {series.isLoading && <Skeleton height={220} />}
              {series.isError && <ErrorState error={series.error} onRetry={() => series.refetch()} />}
              {series.data && <ConsumptionChart data={series.data} periodLabel={periodLabel} />}
            </div>
          </section>
        )}
        {s && <DeviceHealthCard devices={s.devices} />}
        {s && s.regressions_ignored > 0 && <p style={{ color: "var(--muted)", fontSize: "0.875rem" }}>{s.regressions_ignored} leitura(s) com volume menor que a anterior foram ignoradas no cálculo.</p>}
      </main>
    </>
  );
}
