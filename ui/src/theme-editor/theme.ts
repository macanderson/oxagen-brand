/**
 * The theme the editor edits, and the CSS variables it writes for a preview.
 *
 * `SHIPPED` is `theme/theme.json` as the kit ships it. A draft is a copy of
 * it with the editor's changes, plus a face choice for each role.
 * `themeVars` turns a draft into the `--ox-*` variables `build/build.py`
 * would write for it, so setting them on `<html>` previews the change on the
 * page: the semantic roles in `globals.css` read the tokens, so the buttons,
 * the marks, the surfaces, and the type follow.
 */
import shippedJson from "../../../theme/theme.json";
import { goldHue, type Hex } from "./color";
import { derivePalette, type ThemeColor } from "./palette";

export const ROLES = ["wordmark", "display", "sans", "mono"] as const;
export type Role = (typeof ROLES)[number];

export interface FontFile {
  file: string;
  weight: string;
}

export interface ThemeFace {
  family: string;
  source: "kit" | "google";
  files: FontFile[];
  fallback: string[];
  features: string[];
  outline?: { file: string; weight?: number };
}

export interface TypeStep {
  size: string;
  leading: number;
  weight: number;
  tracking: string;
}

export const STEPS = ["h1", "h2", "h3", "h4", "body", "micro"] as const;
export type StepName = (typeof STEPS)[number];
export type ScaleName = "marketing" | "app";

export const RADIUS_STEPS = ["xs", "sm", "md", "lg", "xl", "2xl", "3xl", "4xl"] as const;

/** `theme/theme.json`. */
export interface Theme {
  color: ThemeColor;
  faces: Record<Role, ThemeFace>;
  radius: { base: string; steps: Record<string, number>; card: string; site: string };
  shadow: Record<"ui" | "pop", { ink: string; paper: string }>;
  spacing: { unit: string; wrap: string };
  type: {
    weights: Record<string, number>;
    tracking: Record<string, string>;
    scales: Record<ScaleName, Record<StepName, TypeStep>>;
  };
}

/** The theme the kit ships, without its `$schema` key. */
export const SHIPPED: Theme = (() => {
  const { $schema: _schema, ...rest } = shippedJson as Record<string, unknown>;
  return rest as unknown as Theme;
})();

/** How a role's face is chosen in the editor. */
export type FaceChoice =
  | { kind: "shipped" }
  | { kind: "kit"; family: string }
  | { kind: "google"; family: string; weights: number[] }
  | { kind: "upload"; family: string; files: UploadedFile[] };

export interface UploadedFile {
  /** The name the file takes in fonts/: letters, digits, dots, dashes, and underscores. */
  name: string;
  /** The name it had on disk, when that differs. */
  original: string;
  /** One weight such as "400", or the range a variable file covers such as "100 900". */
  weight: string;
}

/** The fallback a new family takes, as `build/request.py` gives it. */
export const DEFAULT_FALLBACK: Record<Role, string[]> = {
  wordmark: ["Helvetica Neue", "Arial", "sans-serif"],
  display: ["system-ui", "-apple-system", "Segoe UI", "sans-serif"],
  sans: ["system-ui", "-apple-system", "Segoe UI", "sans-serif"],
  mono: ["ui-monospace", "SF Mono", "Menlo", "Consolas", "monospace"],
};

/** The family a choice names, or the shipped family. */
export function choiceFamily(role: Role, choice: FaceChoice): string {
  return choice.kind === "shipped" ? SHIPPED.faces[role].family : choice.family;
}

/** A fallback list as CSS: a name with a space is quoted, a single word is not. */
function familyStack(names: string[]): string {
  return names.map((n) => (n.includes(" ") ? `"${n}"` : n)).join(", ");
}

/** The CSS font stack a role takes under a choice, as `typeset.py` writes it. */
export function fontStack(role: Role, choice: FaceChoice): string {
  const family = choiceFamily(role, choice);
  const shipped = SHIPPED.faces[role];
  const fallback = family === shipped.family ? shipped.fallback : DEFAULT_FALLBACK[role];
  return `"${family}", ${familyStack(fallback)}`;
}

/**
 * The gold ramp in `ui/src/styles/globals.css`: tints typed as `oklch()` on the
 * gold's hue. `build/apply_theme.py` turns them by the degrees the gold's hue
 * moves, and so does the preview. `theme.test.ts` checks this table against
 * the file.
 */
export const GOLD_RAMP: readonly { name: string; l: number; c: number; h: number }[] = [
  { name: "--ox-ember-soft", l: 0.25, c: 0.035, h: 88 },
  { name: "--_amber-50", l: 0.985, c: 0.02, h: 95 },
  { name: "--_amber-100", l: 0.965, c: 0.04, h: 95 },
  { name: "--_amber-200", l: 0.925, c: 0.08, h: 93 },
  { name: "--_amber-500", l: 0.66, c: 0.125, h: 88 },
  { name: "--_amber-700", l: 0.47, c: 0.09, h: 80 },
  { name: "--_amber-800", l: 0.38, c: 0.07, h: 80 },
  { name: "--_amber-900", l: 0.3, c: 0.05, h: 80 },
];

export function rampVars(gold: Hex): Record<string, string> {
  const degrees = goldHue(gold) - goldHue(SHIPPED.color.gold);
  const out: Record<string, string> = {};
  for (const tint of GOLD_RAMP) {
    const h = (((tint.h + degrees) % 360) + 360) % 360;
    out[tint.name] = `oklch(${tint.l} ${tint.c} ${h})`;
  }
  return out;
}

/** The `--ox-*` variables a theme and its face choices produce. */
export function themeVars(theme: Theme, faces: Record<Role, FaceChoice>): Record<string, string> {
  const vars: Record<string, string> = { ...derivePalette(theme.color).vars, ...rampVars(theme.color.gold) };

  vars["--ox-font-display"] = fontStack("wordmark", faces.wordmark);
  vars["--ox-font"] = fontStack("sans", faces.sans);
  vars["--ox-font-mono"] = fontStack("mono", faces.mono);
  vars["--ox-font-heading"] = fontStack("display", faces.display);

  vars["--ox-radius-base"] = theme.radius.base;
  vars["--ox-radius-card"] = `var(--ox-radius-${theme.radius.card})`;
  vars["--ox-radius"] = theme.radius.site;

  vars["--ox-shadow-ui"] = theme.shadow.ui.ink;
  vars["--ox-shadow-ui-ink"] = theme.shadow.ui.paper;
  vars["--ox-shadow-pop"] = theme.shadow.pop.ink;
  vars["--ox-shadow-pop-ink"] = theme.shadow.pop.paper;

  vars["--ox-space"] = theme.spacing.unit;

  for (const [scale, key] of [
    ["marketing", "m"],
    ["app", "a"],
  ] as const) {
    for (const step of STEPS) {
      const s = theme.type.scales[scale][step];
      vars[`--ox-${key}-${step}`] = s.size;
      vars[`--ox-${key}-${step}-leading`] = String(s.leading);
    }
  }
  return vars;
}

/** A rem or px length in CSS pixels at a 16px root, as `build/theme.py` reads one. */
export function remPx(length: string): number {
  if (length.endsWith("rem")) return Number(length.slice(0, -3)) * 16;
  if (length.endsWith("px")) return Number(length.slice(0, -2));
  return Number.NaN;
}

/** Pixels as the theme writes a length: rem, without trailing zeros. */
export function pxRem(px: number): string {
  return `${Number((px / 16).toFixed(4))}rem`;
}

/** A deep copy of a JSON value. */
export function clone<T>(value: T): T {
  return JSON.parse(JSON.stringify(value)) as T;
}
