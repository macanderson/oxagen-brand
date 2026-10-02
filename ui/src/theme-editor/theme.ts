/**
 * The theme the editor edits, and the CSS variables it writes for a preview.
 *
 * `SHIPPED` is `theme/theme.json` as the kit ships it. A draft is a copy of
 * it with the editor's changes, plus a face choice for each role the editor
 * may change. The wordmark face is fixed, so a draft holds no choice for it.
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

/**
 * The roles the editor may change. The wordmark face is fixed: Space Grotesk,
 * drawn at weight 600 (Mac, 2026-10-02). `build/theme.py` refuses any other,
 * and a theme request cannot name it. A new gold still recolours the
 * wordmarks' gold x and asterisk, which paint from `--ox-gold`.
 */
export const FACE_ROLES = ["display", "sans", "mono"] as const;
export type FaceRole = (typeof FACE_ROLES)[number];

export interface FontFile {
  file: string;
  weight: string;
  /** Left out for an upright file. An italic file loads as the same family with `font-style: italic`. */
  style?: "normal" | "italic";
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
  /** Faces the kit loads that no role takes, such as Aeonik Mono. The editor does not change them. */
  extra_faces?: ThemeFace[];
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
export const DEFAULT_FALLBACK: Record<FaceRole, string[]> = {
  display: ["system-ui", "-apple-system", "Segoe UI", "sans-serif"],
  sans: ["system-ui", "-apple-system", "Segoe UI", "sans-serif"],
  mono: ["ui-monospace", "SF Mono", "Menlo", "Consolas", "monospace"],
};

/** The family a choice names, or the shipped family. */
export function choiceFamily(role: FaceRole, choice: FaceChoice): string {
  return choice.kind === "shipped" ? SHIPPED.faces[role].family : choice.family;
}

/** A fallback list as CSS: a name with a space is quoted, a single word is not. */
function familyStack(names: string[]): string {
  return names.map((n) => (n.includes(" ") ? `"${n}"` : n)).join(", ");
}

/**
 * The CSS font stack a role takes under a choice, as `typeset.py` writes it.
 * The fallback is the one the applied theme will hold: the role's own for its
 * shipped family, the kit face's own for another kit face (the request names
 * that face's fallback), and the role's default for a new family.
 */
export function fontStack(role: FaceRole, choice: FaceChoice): string {
  const family = choiceFamily(role, choice);
  const shipped = SHIPPED.faces[role];
  const kitFace = ROLES.map((r) => SHIPPED.faces[r]).find((f) => f.family === family);
  const fallback =
    family === shipped.family
      ? shipped.fallback
      : choice.kind === "kit" && kitFace
        ? kitFace.fallback
        : DEFAULT_FALLBACK[role];
  return `"${family}", ${familyStack(fallback)}`;
}

/** The wordmark's CSS font stack, as `typeset.py` writes `--ox-font-wordmark`. The wordmark face is fixed. */
export const WORDMARK_STACK = `"${SHIPPED.faces.wordmark.family}", ${familyStack(SHIPPED.faces.wordmark.fallback)}`;

/**
 * The gold ramp in `ui/src/styles/globals.css`: tints typed as `oklch()` on the
 * gold's hue. Each tint keeps its lightness and chroma and sits `offset`
 * degrees from the gold's whole-degree hue. `build/apply_theme.py` turns the
 * tints in the file by the degrees a new gold's hue moves, so the offsets
 * hold for any gold, and `theme.test.ts` checks them against the file.
 */
export const GOLD_RAMP: readonly { name: string; l: number; c: number; offset: number }[] = [
  { name: "--ox-ember-soft", l: 0.25, c: 0.035, offset: -3 },
  { name: "--_amber-50", l: 0.985, c: 0.02, offset: 4 },
  { name: "--_amber-100", l: 0.965, c: 0.04, offset: 4 },
  { name: "--_amber-200", l: 0.925, c: 0.08, offset: 2 },
  { name: "--_amber-500", l: 0.66, c: 0.125, offset: -3 },
  { name: "--_amber-700", l: 0.47, c: 0.09, offset: -11 },
  { name: "--_amber-800", l: 0.38, c: 0.07, offset: -11 },
  { name: "--_amber-900", l: 0.3, c: 0.05, offset: -11 },
];

export function rampVars(gold: Hex): Record<string, string> {
  const hue = goldHue(gold);
  const out: Record<string, string> = {};
  for (const tint of GOLD_RAMP) {
    const h = (((hue + tint.offset) % 360) + 360) % 360;
    out[tint.name] = `oklch(${tint.l} ${tint.c} ${h})`;
  }
  return out;
}

/** The `--ox-*` variables a theme and its face choices produce. */
export function themeVars(theme: Theme, faces: Record<FaceRole, FaceChoice>): Record<string, string> {
  const vars: Record<string, string> = { ...derivePalette(theme.color).vars, ...rampVars(theme.color.gold) };

  // The display face sets h1 to h3 on a marketing or customer site. An app
  // heading reads --ox-font-heading, which is the text face.
  vars["--ox-font-display"] = fontStack("display", faces.display);
  vars["--ox-font"] = fontStack("sans", faces.sans);
  vars["--ox-font-mono"] = fontStack("mono", faces.mono);
  vars["--ox-font-heading"] = fontStack("sans", faces.sans);
  vars["--ox-font-wordmark"] = WORDMARK_STACK;

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

/**
 * The smallest size a type step may take, on either scale, as `build/theme.py`
 * holds it. Mac, 2026-10-02: "The minimum font size in the app has to be 14px
 * at least! Not 13px!" No step is exempt, the micro steps included.
 */
export const TYPE_FLOOR_PX = 14;

/** A heading step that can take the display face is set at this size or up, as `build/typeset.py` holds it. */
export const DISPLAY_FLOOR_PX = 20;

/**
 * The type rules `build/theme.py` and `build/typeset.py` check that a size
 * change can break, in their words: every step is 14px or more, each scale
 * descends, h1 to h3 stay 20px or more, and each h1's leading sits between
 * 1.05 and 1.25.
 */
export function typeProblems(theme: Theme): string[] {
  const out: string[] = [];
  for (const scale of ["marketing", "app"] as const) {
    for (const step of STEPS) {
      const px = remPx(theme.type.scales[scale][step].size);
      if (px < TYPE_FLOOR_PX) {
        out.push(
          `The ${scale} ${step} is ${Math.round(px)}px. Every step on both scales is ${TYPE_FLOOR_PX}px or more, so set it to ${TYPE_FLOOR_PX} or larger.`,
        );
      }
    }
    for (const step of ["h1", "h2", "h3"] as const) {
      const px = remPx(theme.type.scales[scale][step].size);
      if (px >= TYPE_FLOOR_PX && px < DISPLAY_FLOOR_PX) {
        out.push(`The ${scale} ${step} is ${Math.round(px)}px. A heading that can take the display face is ${DISPLAY_FLOOR_PX}px or more.`);
      }
    }
    const sizes = STEPS.map((s) => Math.round(remPx(theme.type.scales[scale][s].size)));
    const sorted = [...sizes].sort((a, b) => b - a);
    if (sizes.some((s, i) => s !== sorted[i])) {
      out.push(`${scale} scale does not descend: [${sizes.join(", ")}]`);
    }
    const lead = theme.type.scales[scale].h1.leading;
    if (!(lead >= 1.05 && lead <= 1.25)) out.push(`${scale} h1 line-height ${lead} is outside 1.05 to 1.25`);
  }
  return out;
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
