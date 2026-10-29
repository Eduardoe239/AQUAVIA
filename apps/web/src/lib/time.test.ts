import { describe, expect, it } from "vitest";
import { connectionText, formatAge, periodRange } from "./time";

describe("tempo", () => {
  it("formata idade", () => {
    expect(formatAge(20)).toBe("há instantes");
    expect(formatAge(5 * 60)).toBe("há 5 min");
    expect(formatAge(2 * 3600)).toBe("há 2 h");
  });
  it("texto de conexão é acionável", () => {
    expect(connectionText("offline", 7200)).toBe("Sem comunicação — última leitura há 2 h");
    expect(connectionText("never_reported", null)).toBe("Aguardando a primeira leitura");
  });
  it("períodos", () => {
    const now = new Date(2026, 9, 29);
    expect(periodRange("day", now)).toEqual({ start: "2026-10-29", end: "2026-10-29", granularity: "hour" });
    expect(periodRange("week", now).start).toBe("2026-10-23");
    expect(periodRange("month", now).start).toBe("2026-10-01");
  });
});
