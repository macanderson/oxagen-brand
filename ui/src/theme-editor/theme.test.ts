/**
 * The preview variables against the files the build writes.
 *
 * For the shipped theme, every variable `themeVars` sets must equal the value
 * `tokens/house-tokens.css` declares, so a fresh editor changes nothing on
 * the page. The gold ramp table must match `globals.css`, where
 * `build/apply_theme.py` turns the same tints.
 */
import { readFileSync } from "node:fs";
import { describe, expect, it } from "vitest";
import { GOLD_RAMP, SHIPPED, fontStack, pxRem, rampVars, remPx, themeVars, type FaceChoice, type Role } from "./theme";

const read = (path: string) => readFileSync(new URL(path, import.meta.url), "utf8");
const tokensCss = read("../../../tokens/house-tokens.css");
const globalsCss = read("../styles/globals.css");

const shippedFaces: Record<Role, FaceChoice> = {
  wordmark: { kind: "shipped" },
  display: { kind: "shipped" },
  sans: { kind: "shipped" },
  mono: { kind: "shipped" },
};

function declared(css: string, name: string): string | undefined {
  const escaped = name.replace(/[-]/g, "\\-");
  return new RegExp(`^\\s*${escaped}: ([^;]+);`, "m").exec(css)?.[1];
}

describe("themeVars for the shipped theme", () => {
  const vars = themeVars(SHIPPED, shippedFaces);

  it("matches every --ox-* token in house-tokens.css", () => {
    for (const [name, value] of Object.entries(vars)) {
      if (!name.startsWith("--ox-") || name === "--ox-ember-soft") continue;
      expect(declared(tokensCss, name), name).toBe(value);
    }
  });

  it("sets every type step's size and leading", () => {
    expect(vars["--ox-m-h1"]).toBe("4.5rem");
    expect(vars["--ox-a-body-leading"]).toBe("1.5");
  });
});

describe("the gold ramp", () => {
  it("matches the oklch() tints in globals.css", () => {
    for (const tint of GOLD_RAMP) {
      expect(declared(globalsCss, tint.name), tint.name).toBe(`oklch(${tint.l} ${tint.c} ${tint.h})`);
    }
  });

  it("keeps its hues for the shipped gold", () => {
    const vars = rampVars(SHIPPED.color.gold);
    for (const tint of GOLD_RAMP) {
      expect(vars[tint.name]).toBe(`oklch(${tint.l} ${tint.c} ${tint.h})`);
    }
  });

  it("turns by the degrees the gold's hue moves, as apply_theme.py does", () => {
    // #C99B2E sits 7 degrees below the shipped gold (84 against 91).
    const vars = rampVars("#C99B2E");
    expect(vars["--ox-ember-soft"]).toBe("oklch(0.25 0.035 81)");
    expect(vars["--_amber-50"]).toBe("oklch(0.985 0.02 88)");
  });
});

describe("faces", () => {
  it("writes the shipped stacks as house-tokens.css does", () => {
    expect(fontStack("sans", { kind: "shipped" })).toBe(declared(tokensCss, "--ox-font"));
    expect(fontStack("mono", { kind: "shipped" })).toBe(declared(tokensCss, "--ox-font-mono"));
    expect(fontStack("wordmark", { kind: "shipped" })).toBe(declared(tokensCss, "--ox-font-display"));
  });

  it("gives a new family the role's default fallback", () => {
    expect(fontStack("display", { kind: "google", family: "Inter", weights: [400] })).toBe(
      '"Inter", system-ui, -apple-system, "Segoe UI", sans-serif',
    );
  });
});

describe("lengths", () => {
  it("converts between rem and pixels", () => {
    expect(remPx("0.45rem")).toBeCloseTo(7.2);
    expect(remPx("1120px")).toBe(1120);
    expect(pxRem(72)).toBe("4.5rem");
    expect(pxRem(13)).toBe("0.8125rem");
  });
});
