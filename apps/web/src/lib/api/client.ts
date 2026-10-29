export class ApiError extends Error {
  constructor(public status: number, public code: string, message: string, public requestId?: string) {
    super(message);
  }
}

export interface Me { id: string; email: string; organizations: { id: string; name: string; role: string }[] }
export interface Property { id: string; org_id: string; name: string }
export interface DeviceHealth {
  device_id: string; connection: "never_reported" | "online" | "delayed" | "offline";
  age_seconds: number | null; last_reading_at: string | null; last_sync_at: string | null; sensor_status: string | null;
}
export interface Summary {
  property_id: string; unit: "L"; timezone: string; today_liters: number | null; yesterday_liters: number | null;
  month_liters: number | null; previous_month_liters: number | null; regressions_ignored: number;
  simulated: boolean; devices: DeviceHealth[];
}
export interface Timeseries {
  granularity: "hour" | "day"; timezone: string; unit: "L";
  buckets: { start: string; volume_liters: number | null; quality: "measured" | "estimated" | "corrected" | null }[];
}

async function request<T>(path: string, init: RequestInit = {}): Promise<T> {
  let res: Response;
  try {
    res = await fetch(`/api/v1${path}`, {
      credentials: "include",
      ...init,
      headers: { "Content-Type": "application/json", "X-Requested-With": "aquavia-web", ...init.headers },
    });
  } catch {
    throw new ApiError(0, "NETWORK", "Sem conexão com o servidor.");
  }
  if (!res.ok) {
    const body = await res.json().catch(() => null);
    const e = body?.error;
    throw new ApiError(res.status, e?.code ?? `HTTP_${res.status}`, e?.message ?? "Erro inesperado.", e?.request_id);
  }
  return res.json() as Promise<T>;
}

const q = (o: Record<string, string>) => "?" + new URLSearchParams(o).toString();

export const api = {
  login: (email: string, password: string) => request<{ user: { id: string } }>("/auth/login", { method: "POST", body: JSON.stringify({ email, password }) }),
  logout: () => request<{ ok: boolean }>("/auth/logout", { method: "POST" }),
  me: () => request<Me>("/me"),
  properties: () => request<{ items: Property[] }>("/properties"),
  summary: (property_id: string, tz: string) => request<Summary>("/consumption/summary" + q({ property_id, tz })),
  timeseries: (p: Record<string, string>) => request<Timeseries>("/consumption/timeseries" + q(p)),
};
