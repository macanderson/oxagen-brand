/**
 * The editor's colour maths against `build/color.py`.
 *
 * `python-colors.fixture.json` holds what `color.py` derives for the shipped
 * colours and for six changed ones (`build/editor_fixture.py` writes it, and
 * CI fails when it is stale). Every token the port derives, and every problem
 * its checks report, must match the Python value exactly, so the preview
 * shows the hex the build will write.
 */
import { readFileSync } from "node:fs";
import { describe, expect, it } from "vitest";
import houseTokens from "../../../tokens/house-tokens.json";
import fixture from "./python-colors.fixture.json";
import { contrast, goldHue, hexToOklch, normalizeHex, oklchHex, pyRound } from "./color";
import { derivePalette, verifyPalette, type ThemeColor } from "./palette";
import { SHIPPED } from "./theme";

const cases = fixture.cases as unknown as {
  name: string;
  color: ThemeColor;
  vars: Record<string, string>;
  problems: string[];
}[];

describe("the port of color.py", () => {
  it.each(cases.map((c) => [c.name, c] as const))("derives every colour token for %s", (_, c) => {
    expect(derivePalette(c.color).vars).toEqual(c.vars);
  });

  it.each(cases.map((c) => [c.name, c] as const))("reports the build's problems for %s", (_, c) => {
    expect(verifyPalette(c.color)).toEqual(c.problems);
  });

  it("covers a case with problems and one without", () => {
    expect(cases.some((c) => c.problems.length > 0)).toBe(true);
    expect(cases.some((c) => c.problems.length === 0)).toBe(true);
  });
});

describe("the shipped palette", () => {
  it("matches tokens/house-tokens.json", () => {
    const p = derivePalette(SHIPPED.color);
    expect(p.gold).toBe(houseTokens.gold.hex);
    expect(p.goldBright).toBe(houseTokens.gold.bright);
    expect(p.goldDeep).toBe(houseTokens.gold.deep);
    for (const [name, value] of Object.entries(houseTokens.tokens)) {
      expect(p.vars[`--ox-${name}`], name).toBe(value);
    }
  });

  it("matches every colour in tokens/house-tokens.css", () => {
    const css = readFileSync(new URL("../../../tokens/house-tokens.css", import.meta.url), "utf8");
    const p = derivePalette(SHIPPED.color);
    for (const [name, value] of Object.entries(p.vars)) {
      const line = new RegExp(`^\\s*${name}: ([^;]+);`, "m").exec(css);
      expect(line?.[1], name).toBe(value);
    }
  });

  it("passes the build's checks", () => {
    expect(verifyPalette(SHIPPED.color)).toEqual([]);
  });
});

describe("helpers", () => {
  it("rounds half to even, as Python does", () => {
    expect(pyRound(0.5)).toBe(0);
    expect(pyRound(1.5)).toBe(2);
    expect(pyRound(2.5)).toBe(2);
    expect(pyRound(2.6)).toBe(3);
  });

  it("round-trips a hex through OKLCH", () => {
    for (const hex of ["#D4AF37", "#09090B", "#FFFFFF", "#5B93D6"]) {
      expect(oklchHex(...hexToOklch(hex))).toBe(hex);
    }
  });

  it("takes the gold's hue to a whole degree", () => {
    expect(goldHue("#D4AF37")).toBe(91);
  });

  it("measures contrast as WCAG does", () => {
    expect(contrast("#FFFFFF", "#000000")).toBeCloseTo(21, 5);
    expect(contrast("#D4AF37", "#09090B")).toBeGreaterThan(4.5);
  });

  it("normalizes a typed colour", () => {
    expect(normalizeHex("d4af37")).toBe("#D4AF37");
    expect(normalizeHex("#fff")).toBe("#FFFFFF");
    expect(normalizeHex("gold")).toBeNull();
  });
});
