import type { DeviceHealth } from "../../lib/api/client";
import { connectionText } from "../../lib/time";
import { StatusPill } from "../../components/ui/states";

const tone = { online: "ok", delayed: "warn", offline: "err", never_reported: "muted" } as const;
const label = { online: "Online", delayed: "Atrasado", offline: "Sem comunicação", never_reported: "Aguardando" } as const;

export function DeviceHealthCard({ devices }: { devices: DeviceHealth[] }) {
  return (
    <section className="card" aria-labelledby="dev-h">
      <h2 id="dev-h">Dispositivos</h2>
      {devices.length === 0 && <p style={{ color: "var(--muted)" }}>Nenhum dispositivo ativado nesta propriedade. Peça ao técnico para concluir a instalação.</p>}
      <ul style={{ listStyle: "none", padding: 0, margin: 0, display: "grid", gap: 12 }}>
        {devices.map((d) => (
          <li key={d.device_id} aria-live="polite">
            <StatusPill tone={tone[d.connection]}>{label[d.connection]}</StatusPill>{" "}
            <span className="num">{d.device_id}</span>
            <div style={{ color: "var(--muted)", fontSize: "0.875rem" }}>{connectionText(d.connection, d.age_seconds)}</div>
            {d.sensor_status && d.sensor_status !== "ok" && <div role="status" style={{ color: "var(--warn)" }}>Sensor: {d.sensor_status}</div>}
          </li>
        ))}
      </ul>
    </section>
  );
}
