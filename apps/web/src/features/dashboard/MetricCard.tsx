export function MetricCard({ label, value, hint }: { label: string; value: string; hint?: string }) {
  return (
    <section className="card metric" aria-label={label}>
      <p className="label">{label}</p>
      <p className="value num">{value}</p>
      {hint && <p className="hint">{hint}</p>}
    </section>
  );
}
