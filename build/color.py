"""The house colours: one gold, two grounds, and the neutral greys between.

Obsidian `#09090B` is the dark ground and white the light one, with neutral
zinc greys between (September 2026). The greys carry no hue, so the gold
`#D4AF37` is the only warm value on a screen. Its bright and deep neighbours
are derived from it in OKLCH, not typed, and `verify()` fails if a pinned hex
ever stops matching its derivation.

**The gold is flat.** One value, one fill, everywhere it appears: the wordmark's
`x`, the asterisk, the hive's lit cells, a rule, a chip, a node. There is no
sheen, no metallic ramp, no lit-from-above version of it, and the build fails if
one reappears. A gradient is a texture, and a texture dates; a flat colour is a
fact. `gold-bright` and `gold-deep` are not shades of a gradient either: the
first is a moment of motion, the second is gold set as type on paper.

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
# the gold
# --------------------------------------------------------------------------

#: Bronze Gold as shipped in the original Oxagen brand kit, the fill of the
#: wordmark's `x`. The house gold below replaced it in September 2026; this
#: stays only so the reference wordmark check in glyphs.py can name it.
REFERENCE_GOLD = "#C58A32"

GOLD = "#D4AF37"  # the gold: identity, one action per screen. flat, always

#: The two gold neighbours are the same metal moved in OKLCH, not typed.
#: bright is lighter, for the moment the shimmer passes. deep is darker and a
#: few degrees warmer, for gold set as type on white, where the metal itself
#: is 2.1:1 and cannot be text. `verify()` fails if either pinned hex stops
#: matching its (L, C, H).
GOLD_BRIGHT_LCH = (0.860, 0.130, 91.0)
GOLD_DEEP_LCH = (0.570, 0.110, 82.0)
GOLD_BRIGHT = "#F1CE65"  # the highlight the shimmer passes through, in motion only
GOLD_DEEP = "#977017"  # gold as text on paper, and small details there

# --------------------------------------------------------------------------
# the grounds and the greys
# --------------------------------------------------------------------------

#: Obsidian and white, with neutral greys between. The greys carry no hue, so
#: the one gold is the only warm thing on the screen and reads as metal
#: against either ground.

INK = "#09090B"  # the dark canvas: obsidian
VOID = "#000000"  # below the canvas: full-bleed backdrops
PANEL = "#18181B"  # panels, cards, code blocks
HL = "#27272A"  # a row or line lifted off a panel; the hover surface
BORDER = "#27272A"  # hairlines on ink
RULE = "#3F3F46"  # a heavier rule on ink

PAPER = "#FFFFFF"  # the light canvas: white
PAPER_VOID = "#F4F4F5"  # below paper: full-bleed backdrops
PAPER_PANEL = "#FFFFFF"  # light panel: a card on white is a hairline, not a tint
PAPER_HL = "#F4F4F5"  # a row or line lifted off paper; the hover surface there
PAPER_BORDER = "#E4E4E7"  # hairlines on paper
PAPER_RULE = "#D4D4D8"  # a heavier rule on paper

PAPER_TEXT = PAPER  # primary text on ink
TEXT = "#E4E4E7"  # body text on ink
MUTED = "#A1A1AA"  # secondary text on ink
DIM = "#71717A"  # the quietest text on ink

INK_TEXT = INK  # primary text on paper
TEXT_INK = "#27272A"  # body text on paper
MUTED_INK = "#71717A"  # secondary text on paper
DIM_INK = "#A1A1AA"  # the quietest text on paper; never a word that carries meaning

#: (token, value, use). This list is the palette. Nothing else is.
TOKENS: list[tuple[str, str, str]] = [
    ("gold", GOLD, "the gold: identity, one action per screen. flat, always"),
    ("gold-bright", GOLD_BRIGHT, "the shimmer highlight; hover on ink"),
    ("gold-deep", GOLD_DEEP, "gold as text on paper; small gold details there"),
    ("ink", INK, "the dark canvas"),
    ("void", VOID, "below the canvas"),
    ("panel", PANEL, "panels, cards, code blocks"),
    ("hl", HL, "a lifted row or line"),
    ("border", BORDER, "hairlines on ink"),
    ("rule", RULE, "a heavier rule on ink"),
    ("paper", PAPER, "the light canvas"),
    ("paper-void", PAPER_VOID, "below paper"),
    ("paper-panel", PAPER_PANEL, "light panel"),
    ("paper-hl", PAPER_HL, "a lifted row or line on paper"),
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
# state, for badges and dots
# --------------------------------------------------------------------------

#: State is carried by border shape (double, dashed, single). These colours
#: exist for the badge or dot inside a table where shape alone is too small
#: to read, and are never the only signal. (name, on ink, on paper, use).
#: The values are the approved September 2026 system's.
STATES: list[tuple[str, str, str, str]] = [
    ("allowed", "#57A97C", "#2F7D52", "a request a rule allowed"),
    ("approval", "#5B93D6", "#2E6BA8", "a request routed to a person"),
    ("denied", "#C66A4A", "#9B4526", "a request a rule denied"),
    ("proven", "#3FA2A2", "#1F7676", "the witness's word, beside a witness flip"),
    ("failed", "#C0453C", "#992F28", "a check that did not hold"),
    ("critical", "#D6455E", "#AE2540", "a run that needs a person now"),
]
STATE = {name: {"dark": d, "light": l} for name, d, l, _ in STATES}

#: The one state colour that is also text and a fill: a destructive action.
#: On paper it is the failed badge as is. On ink the failed badge is 3.8:1,
#: so the destructive red is that badge lifted in OKLCH lightness until it
#: clears AA both as text on ink and as a fill under ink text. The lift is
#: derived, not typed; `verify()` fails if the pinned hex stops matching.
DESTRUCTIVE_LIFT = 0.06
DESTRUCTIVE = {"dark": "#D5584D", "light": STATE["failed"]["light"]}
DESTRUCTIVE_TEXT_ON = {"dark": INK, "light": PAPER}  # text on a destructive fill


# --------------------------------------------------------------------------
# checks
# --------------------------------------------------------------------------


def derive_destructive() -> str:
    L, C, H = hex_to_oklch(STATE["failed"]["dark"])
    return oklch_hex(L + DESTRUCTIVE_LIFT, C, H)


def verify() -> list[str]:
    """Every fact the palette claims, checked. Returns the problems found."""
    problems = []
    if oklch_hex(*GOLD_BRIGHT_LCH) != GOLD_BRIGHT:
        problems.append(f"gold-bright {GOLD_BRIGHT} != {oklch_hex(*GOLD_BRIGHT_LCH)}")
    if oklch_hex(*GOLD_DEEP_LCH) != GOLD_DEEP:
        problems.append(f"gold-deep {GOLD_DEEP} != {oklch_hex(*GOLD_DEEP_LCH)}")
    gL, _, _ = hex_to_oklch(GOLD)
    if not (GOLD_DEEP_LCH[0] < gL < GOLD_BRIGHT_LCH[0]):
        problems.append("gold does not sit between its deep and bright neighbours")
    if derive_destructive() != DESTRUCTIVE["dark"]:
        problems.append(f"destructive {DESTRUCTIVE['dark']} is not failed lifted by {DESTRUCTIVE_LIFT}: {derive_destructive()}")
    for theme, ground in GROUNDS.items():
        red = DESTRUCTIVE[theme]
        if contrast(red, ground) < 4.5:
            problems.append(f"destructive on {theme} is {contrast(red, ground):.2f}:1 as text, below AA")
        if contrast(DESTRUCTIVE_TEXT_ON[theme], red) < 4.5:
            problems.append(f"text on a destructive fill ({theme}) is {contrast(DESTRUCTIVE_TEXT_ON[theme], red):.2f}:1, below AA")
    for name, dark, light, _ in STATES:
        # A badge is a fill or a dot at least 3:1 against its ground (WCAG
        # 1.4.11, non-text), and never the only signal.
        if contrast(dark, INK) < 3 or contrast(light, PAPER) < 3:
            problems.append(f"state {name} is below 3:1 on a ground")
    if contrast(GOLD, INK) < 4.5:
        problems.append(f"gold on ink is {contrast(GOLD, INK):.2f}:1, below AA")
    if contrast(GOLD_DEEP, PAPER) < 4.5:
        problems.append(f"gold-deep on paper is {contrast(GOLD_DEEP, PAPER):.2f}:1, below AA")
    if contrast(INK, GOLD) < 4.5:
        problems.append(f"ink on a gold fill is {contrast(INK, GOLD):.2f}:1, below AA")
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
    L, C, H = hex_to_oklch(GOLD)
    print(f"gold        {GOLD}  L={L:.3f} C={C:.3f} H={H:.1f}")
    print()
    hdr = f"{'token':14} {'value':8} {'on ink':>7} {'on paper':>9}"
    print(hdr)
    print("-" * len(hdr))
    for name, value, _ in TOKENS:
        print(f"{name:14} {value:8} {contrast(value, INK):7.2f} {contrast(value, PAPER):9.2f}")
    print()
    print("problems:", verify() or "none")
