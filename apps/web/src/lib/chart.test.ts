import { describe, expect, it } from "vitest";
import { hasAnyData, niceMax } from "./chart";

describe("chart", () => {
  it("niceMax arredonda o eixo para cima", () => {
    expect(niceMax(0)).toBe(1);
    expect(niceMax(73)).toBe(100);
    expect(niceMax(12)).toBe(20);
    expect(niceMax(430)).toBe(500);
  });
  it("detecta ausência de dados", () => {
    expect(hasAnyData([{ start: "x", volume_liters: null, quality: null }])).toBe(false);
    expect(hasAnyData([{ start: "x", volume_liters: 0, quality: "measured" }])).toBe(true);
  });
});
