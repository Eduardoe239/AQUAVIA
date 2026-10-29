import { describe, expect, it } from "vitest";
import { formatDeltaPct, formatVolume } from "./units";

describe("formatVolume", () => {
  it("usa L abaixo de 1000 e m³ acima", () => {
    expect(formatVolume(850)).toBe("850 L");
    expect(formatVolume(12.5)).toBe("12,5 L");
    expect(formatVolume(12548.72)).toBe("12,55 m³");
  });
  it("mostra traço quando não há dado (nunca zero)", () => expect(formatVolume(null)).toBe("—"));
});

describe("formatDeltaPct", () => {
  it("compara e omite quando não há base", () => {
    expect(formatDeltaPct(150, 100)).toBe("+50%");
    expect(formatDeltaPct(50, 100)).toBe("−50%");
    expect(formatDeltaPct(10, null)).toBeNull();
    expect(formatDeltaPct(10, 0)).toBeNull();
  });
});
