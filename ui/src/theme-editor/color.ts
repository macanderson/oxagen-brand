/**
 * The house colour maths, ported from `build/color.py` so the theme editor can
 * preview a change before any build runs.
 *
 * Every function here mirrors one in `color.py`, with the same constants and
 * the same rounding. `color.test.ts` holds the port to the values `color.py`
 * computes (`python-colors.fixture.json`, written by
 * `build/editor_fixture.py`), so a preview shows the hex the build will write.
 */

export type Hex = string;
export type Lch = readonly [l: number, c: number, h: number];

/** Python's `round()`: half to even, as `color.py` rounds a channel or a hue. */
export function pyRound(x: number): number {
  const floor = Math.floor(x);
  const diff = x - floor;
  if (diff > 0.5) return floor + 1;
  if (diff < 0.5) return floor;
  return floor % 2 === 0 ? floor : floor + 1;
}

/** Python's `round(x, digits)` for the few places `color.py` rounds a coordinate. */
export function pyRoundTo(x: number, digits: number): number {
  return Number(x.toFixed(digits));
}

function srgbToLinear(c: number): number {
  return c <= 0.04045 ? c / 12.92 : ((c + 0.055) / 1.055) ** 2.4;
}

function linearToSrgb(c: number): number {
  return c <= 0.0031308 ? 12.92 * c : 1.055 * c ** (1 / 2.4) - 0.055;
}

/** Whether `value` is a colour as the theme holds one: six uppercase hex digits. */
export function isHex(value: string): boolean {
  return /^#[0-9A-F]{6}$/.test(value);
}

/** A typed or picked colour as the theme holds it, or null when it is not one. */
export function normalizeHex(value: string): Hex | null {
  const v = value.trim().toUpperCase();
  const full = /^#?([0-9A-F]{6})$/.exec(v);
  if (full) return `#${full[1]}`;
  const short = /^#?([0-9A-F])([0-9A-F])([0-9A-F])$/.exec(v);
  if (short) return `#${short[1]}${short[1]}${short[2]}${short[2]}${short[3]}${short[3]}`;
  return null;
}

export function hexToRgb(hex: Hex): [number, number, number] {
  const h = hex.replace(/^#/, "");
  return [0, 2, 4].map((i) => parseInt(h.slice(i, i + 2), 16) / 255) as [number, number, number];
}

export function rgbToHex(r: number, g: number, b: number): Hex {
  const part = (v: number) =>
    pyRound(Math.max(0, Math.min(1, v)) * 255)
      .toString(16)
      .toUpperCase()
      .padStart(2, "0");
  return `#${part(r)}${part(g)}${part(b)}`;
}

export function rgbToOklab(r: number, g: number, b: number): [number, number, number] {
  const lr = srgbToLinear(r);
  const lg = srgbToLinear(g);
  const lb = srgbToLinear(b);
  const l = 0.4122214708 * lr + 0.5363325363 * lg + 0.0514459929 * lb;
  const m = 0.2119034982 * lr + 0.6806995451 * lg + 0.1073969566 * lb;
  const s = 0.0883024619 * lr + 0.2817188376 * lg + 0.6299787005 * lb;
  const l_ = Math.cbrt(l);
  const m_ = Math.cbrt(m);
  const s_ = Math.cbrt(s);
  return [
    0.2104542553 * l_ + 0.793617785 * m_ - 0.0040720468 * s_,
    1.9779984951 * l_ - 2.428592205 * m_ + 0.4505937099 * s_,
    0.0259040371 * l_ + 0.7827717662 * m_ - 0.808675766 * s_,
  ];
}

export function oklabToRgb(L: number, a: number, b: number): [number, number, number] {
  const l_ = L + 0.3963377774 * a + 0.2158037573 * b;
  const m_ = L - 0.1055613458 * a - 0.0638541728 * b;
  const s_ = L - 0.0894841775 * a - 1.291485548 * b;
  const l = l_ ** 3;
  const m = m_ ** 3;
  const s = s_ ** 3;
  return [
    linearToSrgb(4.0767416621 * l - 3.3077115913 * m + 0.2309699292 * s),
    linearToSrgb(-1.2684380046 * l + 2.6097574011 * m - 0.3413193965 * s),
    linearToSrgb(-0.0041960863 * l - 0.7034186147 * m + 1.707614701 * s),
  ];
}

/** `color.py`'s `oklch_hex`: an OKLCH coordinate as a hex, clamped into sRGB. */
export function oklchHex(L: number, C: number, H: number): Hex {
  const rad = (H * Math.PI) / 180;
  const [r, g, b] = oklabToRgb(L, C * Math.cos(rad), C * Math.sin(rad));
  return rgbToHex(r, g, b);
}

export function hexToOklch(hex: Hex): [number, number, number] {
  const [L, a, b] = rgbToOklab(...hexToRgb(hex));
  const h = (Math.atan2(b, a) * 180) / Math.PI;
  return [L, Math.hypot(a, b), ((h % 360) + 360) % 360];
}

export function luminance(hex: Hex): number {
  const [r, g, b] = hexToRgb(hex).map(srgbToLinear) as [number, number, number];
  return 0.2126 * r + 0.7152 * g + 0.0722 * b;
}

/** The WCAG contrast ratio between two colours, from 1 to 21. */
export function contrast(a: Hex, b: Hex): number {
  const la = luminance(a);
  const lb = luminance(b);
  return (Math.max(la, lb) + 0.05) / (Math.min(la, lb) + 0.05);
}

/** A colour's OKLCH at the precision the theme states it: L and C to 3 places, H to 1. */
export function lchRounded(hex: Hex): Lch {
  const [L, C, H] = hexToOklch(hex);
  return [pyRoundTo(L, 3), pyRoundTo(C, 3), pyRoundTo(H, 1)];
}

/** The gold's hue, rounded to a whole degree as `color.py` rounds it for the neighbours. */
export function goldHue(gold: Hex): number {
  return pyRound(hexToOklch(gold)[2]);
}

/** The smallest signed difference between two hues, in degrees. */
export function hueDistance(a: number, b: number): number {
  return Math.abs((((a - b + 180) % 360) + 360) % 360 - 180);
}
