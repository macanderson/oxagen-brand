/**
 * The palette a theme produces, and the checks the build runs on it, ported
 * from `build/color.py`.
 *
 * `derivePalette` returns every colour token `build/build.py` writes into
 * `tokens/house-tokens.css`, by its CSS variable name. `verifyPalette`
 * returns the problems `color.verify()` reports, in the same words, so the
 * editor can warn before a request reaches the build.
 */
import {
  contrast,
  goldHue,
  hexToOklch,
  hueDistance,
  lchRounded,
  oklchHex,
  pyRoundTo,
  type Hex,
  type Lch,
} from "./color";

export const STATE_NAMES = [
  "allowed",
  "approval",
  "denied",
  "proven",
  "failed",
  "critical",
] as const;
export type StateName = (typeof STATE_NAMES)[number];

export interface Neighbour {
  lightness: number;
  chroma: number;
}

export interface InkGrounds {
  ink: Hex;
  void: Hex;
  panel: Hex;
  hl: Hex;
  border: Hex;
  rule: Hex;
}

export interface PaperGrounds {
  paper: Hex;
  void: Hex;
  panel: Hex;
  hl: Hex;
  border: Hex;
  rule: Hex;
}

/** The `color` section of `theme/theme.json`. */
export interface ThemeColor {
  gold: Hex;
  gold_bright: Neighbour;
  gold_deep: Neighbour;
  /** The gold as words on paper, `--ox-gold-text-ink`. */
  gold_text: Neighbour;
  ink: InkGrounds;
  paper: PaperGrounds;
  text_on_ink: { body: Hex; muted: Hex; dim: Hex };
  text_on_paper: { body: Hex; muted: Hex; dim: Hex; muted_text_lightness: number };
  states: Record<StateName, { ink: Hex; paper: Hex }>;
  state_text_lightness_on_ink: number;
  destructive_lift_on_ink: number;
}

type Mode = "dark" | "light";

export interface Palette {
  gold: Hex;
  goldBright: Hex;
  goldDeep: Hex;
  goldBrightLch: Lch;
  goldDeepLch: Lch;
  goldTextInk: Hex;
  goldTextInkLch: Lch;
  mutedTextInk: Hex;
  mutedTextInkLch: Lch;
  destructive: Record<Mode, Hex>;
  /** Every state's mark, and the destructive red, on ink (dark) and on paper (light). */
  marks: Record<StateName | "destructive", Record<Mode, Hex>>;
  stateTextLch: Record<StateName | "destructive", Record<Mode, Lch>>;
  stateText: Record<StateName | "destructive", Record<Mode, Hex>>;
  /** The colour tokens, as `--ox-<name>` CSS variables. */
  vars: Record<string, string>;
}

/** `color.py`'s `derive_destructive`: the failed mark on ink, lifted in OKLCH lightness. */
function deriveDestructive(color: ThemeColor): Hex {
  const [L, C, H] = hexToOklch(color.states.failed.ink);
  return oklchHex(L + color.destructive_lift_on_ink, C, H);
}

export function derivePalette(color: ThemeColor): Palette {
  const hue = goldHue(color.gold);
  const goldBrightLch: Lch = [color.gold_bright.lightness, color.gold_bright.chroma, hue];
  const goldDeepLch: Lch = [color.gold_deep.lightness, color.gold_deep.chroma, hue];
  const goldBright = oklchHex(...goldBrightLch);
  const goldDeep = oklchHex(...goldDeepLch);
  const goldTextInkLch: Lch = [color.gold_text.lightness, color.gold_text.chroma, hue];
  const goldTextInk = oklchHex(...goldTextInkLch);

  const [, mC, mH] = lchRounded(color.text_on_paper.muted);
  const mutedTextInkLch: Lch = [color.text_on_paper.muted_text_lightness, mC, mH];
  const mutedTextInk = oklchHex(...mutedTextInkLch);

  const destructive: Record<Mode, Hex> = {
    dark: deriveDestructive(color),
    light: color.states.failed.paper,
  };
  const marks = {} as Palette["marks"];
  for (const name of STATE_NAMES) {
    marks[name] = { dark: color.states[name].ink, light: color.states[name].paper };
  }
  marks.destructive = destructive;

  const stateTextLch = {} as Palette["stateTextLch"];
  const stateText = {} as Palette["stateText"];
  for (const [name, byMode] of Object.entries(marks) as [StateName | "destructive", Record<Mode, Hex>][]) {
    const [dL, dC, dH] = lchRounded(byMode.dark);
    const [lL, lC, lH] = lchRounded(byMode.light);
    const dark: Lch = [color.state_text_lightness_on_ink, dC, dH];
    const light: Lch = [lL, lC, lH];
    stateTextLch[name] = { dark, light };
    stateText[name] = { dark: oklchHex(...dark), light: oklchHex(...light) };
  }

  const { ink, paper } = color;
  const vars: Record<string, string> = {
    "--ox-gold": color.gold,
    "--ox-gold-bright": goldBright,
    "--ox-gold-deep": goldDeep,
    "--ox-gold-text-ink": goldTextInk,
    "--ox-ink": ink.ink,
    "--ox-void": ink.void,
    "--ox-panel": ink.panel,
    "--ox-hl": ink.hl,
    "--ox-border": ink.border,
    "--ox-rule": ink.rule,
    "--ox-paper": paper.paper,
    "--ox-paper-void": paper.void,
    "--ox-paper-panel": paper.panel,
    "--ox-paper-hl": paper.hl,
    "--ox-paper-border": paper.border,
    "--ox-paper-rule": paper.rule,
    "--ox-text": paper.paper,
    "--ox-text-body": color.text_on_ink.body,
    "--ox-muted": color.text_on_ink.muted,
    "--ox-dim": color.text_on_ink.dim,
    "--ox-text-ink": ink.ink,
    "--ox-text-ink-body": color.text_on_paper.body,
    "--ox-muted-ink": color.text_on_paper.muted,
    "--ox-muted-text-ink": mutedTextInk,
    "--ox-dim-ink": color.text_on_paper.dim,
  };
  for (const name of STATE_NAMES) {
    vars[`--ox-st-${name}`] = color.states[name].ink;
    vars[`--ox-st-${name}-ink`] = color.states[name].paper;
  }
  vars["--ox-destructive"] = destructive.dark;
  vars["--ox-destructive-ink"] = destructive.light;
  for (const [name, text] of Object.entries(stateText)) {
    const stem = name === "destructive" ? "destructive" : `st-${name}`;
    vars[`--ox-${stem}-text`] = text.dark;
    vars[`--ox-${stem}-text-ink`] = text.light;
  }
  vars["--ox-gold-sheen"] =
    `linear-gradient(45deg, ${goldDeep} 0%, ${color.gold} 38%, ${goldBright} 56%, ${color.gold} 74%, ${goldDeep} 100%)`;

  return {
    gold: color.gold,
    goldBright,
    goldDeep,
    goldBrightLch,
    goldDeepLch,
    goldTextInk,
    goldTextInkLch,
    mutedTextInk,
    mutedTextInkLch,
    destructive,
    marks,
    stateTextLch,
    stateText,
    vars,
  };
}

/** Python's `f"{x:.2f}"` and `f"{x:.3f}"`. */
const fixed = (x: number, digits: number) => x.toFixed(digits);

/** Python's `str()` of a number in the theme, such as 0.86 or 0.1. */
const py = (x: number) => String(x);

/**
 * Every problem `color.verify()` reports for this palette, in its words.
 * An empty list means the build accepts the colours.
 */
export function verifyPalette(color: ThemeColor): string[] {
  const p = derivePalette(color);
  const problems: string[] = [];
  const INK = color.ink.ink;
  const PAPER = color.paper.paper;
  const grounds: Record<Mode, Hex> = { dark: INK, light: PAPER };
  const textOnFill: Record<Mode, Hex> = { dark: INK, light: PAPER };
  const surfaces: Record<Mode, Record<string, Hex>> = {
    dark: { ink: INK, panel: color.ink.panel, hl: color.ink.hl },
    light: { paper: PAPER, "paper-hl": color.paper.hl },
  };

  for (const [name, lch, value] of [
    ["gold-bright", p.goldBrightLch, p.goldBright],
    ["gold-deep", p.goldDeepLch, p.goldDeep],
    ["gold-text-ink", p.goldTextInkLch, p.goldTextInk],
  ] as const) {
    const [, , h] = hexToOklch(value);
    if (hueDistance(h, lch[2]) > 2) {
      problems.push(
        `${name} ${value} leaves the gold's hue: lightness ${py(lch[0])} and chroma ${py(lch[1])} fall outside sRGB there`,
      );
    }
  }
  const [gL] = hexToOklch(color.gold);
  if (!(p.goldDeepLch[0] < gL && gL < p.goldBrightLch[0])) {
    problems.push("gold does not sit between its deep and bright neighbours");
  }
  for (const mode of ["dark", "light"] as const) {
    const red = p.destructive[mode];
    if (contrast(red, grounds[mode]) < 4.5) {
      problems.push(`destructive on ${mode} is ${fixed(contrast(red, grounds[mode]), 2)}:1 as text, below AA`);
    }
    if (contrast(textOnFill[mode], red) < 4.5) {
      problems.push(
        `text on a destructive fill (${mode}) is ${fixed(contrast(textOnFill[mode], red), 2)}:1, below AA`,
      );
    }
  }
  for (const name of STATE_NAMES) {
    const { ink, paper } = color.states[name];
    if (contrast(ink, INK) < 3 || contrast(paper, PAPER) < 3) {
      problems.push(`state ${name} is below 3:1 on a ground`);
    }
  }
  for (const [name, byMode] of Object.entries(p.marks) as [StateName | "destructive", Record<Mode, Hex>][]) {
    for (const mode of ["dark", "light"] as const) {
      const mark = byMode[mode];
      const lch = p.stateTextLch[name][mode];
      const stop = p.stateText[name][mode];
      const where = `${name} text stop on ${mode === "dark" ? "ink" : "paper"}`;
      const [mL, mC, mH] = hexToOklch(mark);
      const [pL, , pH] = hexToOklch(stop);
      if (hueDistance(pH, mH) > 1 || Math.abs(lch[1] - mC) > 0.001) {
        problems.push(`${where} leaves its mark's hue or chroma: ${stop} vs ${mark}`);
      }
      if (mode === "dark" && pL < mL - 0.002) {
        problems.push(
          `${where} is darker than its mark ${mark}: raise state_text_lightness_on_ink above ${fixed(mL, 3)}`,
        );
      }
      if (mode === "light" && pL > mL + 0.002) {
        problems.push(`${where} is lighter than its mark ${mark}`);
      }
      for (const [surface, ground] of Object.entries(surfaces[mode])) {
        if (contrast(stop, ground) < 4.5) {
          problems.push(`${where} is ${fixed(contrast(stop, ground), 2)}:1 on ${surface}, below AA`);
        }
      }
    }
  }
  const [, mutedC, mutedH] = hexToOklch(color.text_on_paper.muted);
  const [, , mtH] = hexToOklch(p.mutedTextInk);
  if (hueDistance(mtH, mutedH) > 1 || Math.abs(p.mutedTextInkLch[1] - mutedC) > 0.001) {
    problems.push("muted-text-ink leaves muted-ink's hue or chroma");
  }
  for (const [surface, ground] of Object.entries(surfaces.light)) {
    if (contrast(p.mutedTextInk, ground) < 4.5) {
      problems.push(`muted-text-ink is ${fixed(contrast(p.mutedTextInk, ground), 2)}:1 on ${surface}, below AA`);
    }
  }
  if (contrast(color.text_on_ink.muted, color.ink.hl) < 4.5) {
    problems.push(`muted is ${fixed(contrast(color.text_on_ink.muted, color.ink.hl), 2)}:1 on hl, below AA`);
  }
  if (contrast(color.gold, INK) < 4.5) {
    problems.push(`gold on ink is ${fixed(contrast(color.gold, INK), 2)}:1, below AA`);
  }
  if (contrast(p.goldDeep, PAPER) < 4.5) {
    problems.push(`gold-deep on paper is ${fixed(contrast(p.goldDeep, PAPER), 2)}:1, below AA`);
  }
  // Gold words in the light theme sit on paper, a panel, and a lifted row.
  for (const [surface, ground] of [
    ["paper", PAPER],
    ["paper-panel", color.paper.panel],
    ["paper-hl", color.paper.hl],
  ] as const) {
    if (contrast(p.goldTextInk, ground) < 4.5) {
      problems.push(`gold-text-ink is ${fixed(contrast(p.goldTextInk, ground), 2)}:1 on ${surface}, below AA`);
    }
  }
  if (contrast(INK, color.gold) < 4.5) {
    problems.push(`ink on a gold fill is ${fixed(contrast(INK, color.gold), 2)}:1, below AA`);
  }
  for (const [name, value, ground] of [
    ["text", PAPER, INK],
    ["text-body", color.text_on_ink.body, INK],
    ["muted", color.text_on_ink.muted, INK],
    ["text-ink", INK, PAPER],
    ["text-ink-body", color.text_on_paper.body, PAPER],
    ["muted-ink", color.text_on_paper.muted, PAPER],
  ] as const) {
    if (contrast(value, ground) < 4.5) {
      problems.push(`${name} on its ground is ${fixed(contrast(value, ground), 2)}:1, below AA`);
    }
  }
  return problems;
}

/** Round a contrast ratio for display, as the build prints it. */
export function ratio(a: Hex, b: Hex): string {
  return `${pyRoundTo(contrast(a, b), 2).toFixed(2)}:1`;
}
