"""The house colours: one metal, two grounds, and the warm greys between.

The grounds and the greys are the Oxagen brand kit's Ink and Paper as shipped.
The metal is that kit's Bronze Gold lifted a step in OKLCH: a little lighter, a
little more saturated, and a few degrees toward yellow, so it reads as gold
rather than bronze. The lift is derived here, not typed, and `verify()` fails
if the pinned hex ever stops matching its derivation.

Gold is identity and at most one action per screen. It is never a surface and
it never encodes a state. Both wordmarks paint exactly one glyph in it.
"""

from __future__ import annotations

import math

# --------------------------------------------------------------------------
# sRGB <-> OKLCH, and WCAG contrast
# --------------------------------------------------------------------------


def _srgb_to_linear(c: float) -> float:
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def _linear_to_srgb(c: float) -> float:
    return 12.92 * c if c <= 0.0031308 else 1.055 * c ** (1 / 2.4) - 0.055


def hex_to_rgb(h: str) -> tuple[float, float, float]:
    h = h.lstrip("#")
    return tuple(int(h[i : i + 2], 16) / 255 for i in (0, 2, 4))  # type: ignore[return-value]


def rgb_to_hex(r: float, g: float, b: float) -> str:
    return "#%02X%02X%02X" % tuple(round(max(0.0, min(1.0, v)) * 255) for v in (r, g, b))


def rgb_to_oklab(r: float, g: float, b: float) -> tuple[float, float, float]:
    lr, lg, lb = (_srgb_to_linear(v) for v in (r, g, b))
    l = 0.4122214708 * lr + 0.5363325363 * lg + 0.0514459929 * lb
    m = 0.2119034982 * lr + 0.6806995451 * lg + 0.1073969566 * lb
    s = 0.0883024619 * lr + 0.2817188376 * lg + 0.6299787005 * lb
    l_, m_, s_ = (math.copysign(abs(v) ** (1 / 3), v) for v in (l, m, s))
    return (
        0.2104542553 * l_ + 0.7936177850 * m_ - 0.0040720468 * s_,
        1.9779984951 * l_ - 2.4285922050 * m_ + 0.4505937099 * s_,
        0.0259040371 * l_ + 0.7827717662 * m_ - 0.8086757660 * s_,
    )


def oklab_to_rgb(L: float, a: float, b: float) -> tuple[float, float, float]:
    l_ = L + 0.3963377774 * a + 0.2158037573 * b
    m_ = L - 0.1055613458 * a - 0.0638541728 * b
    s_ = L - 0.0894841775 * a - 1.2914855480 * b
    l, m, s = (v**3 for v in (l_, m_, s_))
    lr = +4.0767416621 * l - 3.3077115913 * m + 0.2309699292 * s
    lg = -1.2684380046 * l + 2.6097574011 * m - 0.3413193965 * s
    lb = -0.0041960863 * l - 0.7034186147 * m + 1.7076147010 * s
    return tuple(_linear_to_srgb(v) for v in (lr, lg, lb))  # type: ignore[return-value]


def oklch(L: float, C: float, H: float) -> tuple[float, float, float]:
    rad = math.radians(H)
    return oklab_to_rgb(L, C * math.cos(rad), C * math.sin(rad))


def oklch_hex(L: float, C: float, H: float) -> str:
    return rgb_to_hex(*oklch(L, C, H))


def hex_to_oklch(h: str) -> tuple[float, float, float]:
    L, a, b = rgb_to_oklab(*hex_to_rgb(h))
    return L, math.hypot(a, b), math.degrees(math.atan2(b, a)) % 360


def luminance(h: str) -> float:
    r, g, b = (_srgb_to_linear(v) for v in hex_to_rgb(h))
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast(a: str, b: str) -> float:
    la, lb = luminance(a), luminance(b)
    hi, lo = max(la, lb), min(la, lb)
    return (hi + 0.05) / (lo + 0.05)


# --------------------------------------------------------------------------
# the metal
# --------------------------------------------------------------------------

#: Bronze Gold as shipped in the Oxagen brand kit (`wordmark-color-light.svg`,
#: the fill of the `x`). Kept only as the anchor the house gold is derived from.
REFERENCE_GOLD = "#C58A32"

#: The lift, in OKLCH: lightness, chroma, hue degrees. "A tad brighter and more
#: shimmery" -- lighter so it lifts off ink, more chroma so it does not go
#: sandy when lighter, and a nudge toward yellow so it reads gold, not copper.
GOLD_LIFT = (0.043, 0.014, 1.8)

GOLD = "#D6962C"  # the metal: identity, one action per screen
GOLD_BRIGHT = "#F1C364"  # the highlight the shimmer passes through
GOLD_DEEP = "#8B5E1A"  # gold as text on paper, and small details there

#: What the two gold neighbours are: the same hue, moved in lightness only.
#: (L, C, H) for the highlight; the deep value is the reference kit's Bronze
#: Deep, unchanged, because it already clears AA on paper.
GOLD_BRIGHT_LCH = (0.840, 0.125, 84.0)

# --------------------------------------------------------------------------
# the grounds and the greys
# --------------------------------------------------------------------------

INK = "#10100F"  # the dark canvas
VOID = "#0A0A09"  # below the canvas: full-bleed backdrops
PANEL = "#181715"  # panels, cards, code blocks
HL = "#201F1C"  # a row or line lifted off a panel
BORDER = "#292722"  # hairlines on ink (the kit's Hairline Dark)
RULE = "#34322D"  # a heavier rule on ink

PAPER = "#F2EEE5"  # the warm light canvas
PAPER_PANEL = "#F8F5EE"  # light panel
PAPER_BORDER = "#D8CDBD"  # hairlines on paper (the kit's Hairline Light)
PAPER_RULE = "#C9BFAE"  # a heavier rule on paper

PAPER_TEXT = PAPER  # primary text on ink: the kit sets type in Paper
TEXT = "#DDD8CD"  # body text on ink
MUTED = "#9B958A"  # secondary text on ink
DIM = "#6E6A62"  # the quietest text on ink

INK_TEXT = INK  # primary text on paper
TEXT_INK = "#2A2823"  # body text on paper
MUTED_INK = "#6B665C"  # secondary text on paper
DIM_INK = "#8C877C"  # the quietest text on paper

#: (token, value, use). This list is the palette. Nothing else is.
TOKENS: list[tuple[str, str, str]] = [
    ("gold", GOLD, "the metal: identity, one action per screen"),
    ("gold-bright", GOLD_BRIGHT, "the shimmer highlight; hover on ink"),
    ("gold-deep", GOLD_DEEP, "gold as text on paper; small gold details there"),
    ("ink", INK, "the dark canvas"),
    ("void", VOID, "below the canvas"),
    ("panel", PANEL, "panels, cards, code blocks"),
    ("hl", HL, "a lifted row or line"),
    ("border", BORDER, "hairlines on ink"),
    ("rule", RULE, "a heavier rule on ink"),
    ("paper", PAPER, "the warm light canvas"),
    ("paper-panel", PAPER_PANEL, "light panel"),
    ("paper-border", PAPER_BORDER, "hairlines on paper"),
    ("paper-rule", PAPER_RULE, "a heavier rule on paper"),
    ("text", PAPER_TEXT, "primary text on ink"),
    ("text-body", TEXT, "body text on ink"),
    ("muted", MUTED, "secondary text on ink"),
    ("dim", DIM, "the quietest text on ink"),
    ("text-ink", INK_TEXT, "primary text on paper"),
    ("text-ink-body", TEXT_INK, "body text on paper"),
    ("muted-ink", MUTED_INK, "secondary text on paper"),
    ("dim-ink", DIM_INK, "the quietest text on paper"),
]

GROUNDS = {"dark": INK, "light": PAPER}
TEXT_ON = {"dark": PAPER_TEXT, "light": INK_TEXT}
MUTED_ON = {"dark": MUTED, "light": MUTED_INK}
GOLD_TEXT_ON = {"dark": GOLD, "light": GOLD_DEEP}
BORDER_ON = {"dark": BORDER, "light": PAPER_BORDER}


# --------------------------------------------------------------------------
# checks
# --------------------------------------------------------------------------


def derive_gold() -> str:
    L, C, H = hex_to_oklch(REFERENCE_GOLD)
    dL, dC, dH = GOLD_LIFT
    return oklch_hex(L + dL, C + dC, H + dH)


def verify() -> list[str]:
    """Every fact the palette claims, checked. Returns the problems found."""
    problems = []
    if derive_gold() != GOLD:
        problems.append(f"gold {GOLD} is not the reference gold lifted by {GOLD_LIFT}: {derive_gold()}")
    if oklch_hex(*GOLD_BRIGHT_LCH) != GOLD_BRIGHT:
        problems.append(f"gold-bright {GOLD_BRIGHT} != {oklch_hex(*GOLD_BRIGHT_LCH)}")
    gL, gC, gH = hex_to_oklch(GOLD)
    rL, rC, rH = hex_to_oklch(REFERENCE_GOLD)
    if not (gL > rL and gC > rC):
        problems.append("gold is not brighter and richer than the reference")
    if contrast(GOLD, INK) < 4.5:
        problems.append(f"gold on ink is {contrast(GOLD, INK):.2f}:1, below AA")
    if contrast(GOLD_DEEP, PAPER) < 4.5:
        problems.append(f"gold-deep on paper is {contrast(GOLD_DEEP, PAPER):.2f}:1, below AA")
    for name, value, ground in (
        ("text", PAPER_TEXT, INK),
        ("text-body", TEXT, INK),
        ("muted", MUTED, INK),
        ("text-ink", INK_TEXT, PAPER),
        ("text-ink-body", TEXT_INK, PAPER),
        ("muted-ink", MUTED_INK, PAPER),
    ):
        if contrast(value, ground) < 4.5:
            problems.append(f"{name} on its ground is {contrast(value, ground):.2f}:1, below AA")
    return problems


if __name__ == "__main__":
    L, C, H = hex_to_oklch(REFERENCE_GOLD)
    print(f"reference gold {REFERENCE_GOLD}  L={L:.3f} C={C:.3f} H={H:.1f}")
    L, C, H = hex_to_oklch(GOLD)
    print(f"house gold     {GOLD}  L={L:.3f} C={C:.3f} H={H:.1f}")
    print()
    hdr = f"{'token':14} {'value':8} {'on ink':>7} {'on paper':>9}"
    print(hdr)
    print("-" * len(hdr))
    for name, value, _ in TOKENS:
        print(f"{name:14} {value:8} {contrast(value, INK):7.2f} {contrast(value, PAPER):9.2f}")
    print()
    print("problems:", verify() or "none")
