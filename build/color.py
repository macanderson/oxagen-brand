"""The house colours: one gold, two grounds, and the neutral greys between.

Every value comes from `theme/theme.json`, through `build/theme.py`. This
module derives what the theme does not state: the gold's two neighbours, the
destructive red on ink, and every state's text stop. Other modules import the
names below, so they keep their old meaning whatever the theme holds.

Obsidian `#09090B` is the dark ground and white the light one, with neutral
zinc greys between (September 2026). The greys carry no hue, so the gold
`#D4AF37` is the only warm value on a screen. Its bright and deep neighbours
are derived from it in OKLCH, not typed.

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

from theme import THEME

_COLOR = THEME["color"]

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

GOLD = _COLOR["gold"]  # the gold: identity, one action per screen. flat, always

#: The two gold neighbours are the same metal moved in OKLCH, not typed.
#: bright is lighter, for the moment the shimmer passes. deep is darker, on
#: the gold's own OKLCH hue, for gold set as type on white, where the metal
#: itself is 2.1:1 and cannot be text. Keeping the hue is what lets Stella's
#: token gate (a shade within 4 degrees of its gold) accept the same value.
#: The theme holds each neighbour's lightness and chroma. The hue is the
#: gold's own, rounded to a whole degree, and the hex is derived from all three.
GOLD_HUE = float(round(hex_to_oklch(GOLD)[2]))
GOLD_BRIGHT_LCH = (_COLOR["gold_bright"]["lightness"], _COLOR["gold_bright"]["chroma"], GOLD_HUE)
GOLD_DEEP_LCH = (_COLOR["gold_deep"]["lightness"], _COLOR["gold_deep"]["chroma"], GOLD_HUE)
GOLD_BRIGHT = oklch_hex(*GOLD_BRIGHT_LCH)  # the highlight the shimmer passes through, in motion only
GOLD_DEEP = oklch_hex(*GOLD_DEEP_LCH)  # gold as text on paper, and small details there

# --------------------------------------------------------------------------
# the grounds and the greys
# --------------------------------------------------------------------------

#: Obsidian and white, with neutral greys between. The greys carry no hue, so
#: the one gold is the only warm thing on the screen and reads as metal
#: against either ground.

_INK, _PAPER = _COLOR["ink"], _COLOR["paper"]
INK = _INK["ink"]  # the dark canvas: obsidian
VOID = _INK["void"]  # below the canvas: full-bleed backdrops
PANEL = _INK["panel"]  # panels, cards, code blocks
HL = _INK["hl"]  # a row or line lifted off a panel; the hover surface
BORDER = _INK["border"]  # hairlines on ink
RULE = _INK["rule"]  # a heavier rule on ink

PAPER = _PAPER["paper"]  # the light canvas: white
PAPER_VOID = _PAPER["void"]  # below paper: full-bleed backdrops
PAPER_PANEL = _PAPER["panel"]  # light panel: a card on white is a hairline, not a tint
PAPER_HL = _PAPER["hl"]  # a row or line lifted off paper; the hover surface there
PAPER_BORDER = _PAPER["border"]  # hairlines on paper
PAPER_RULE = _PAPER["rule"]  # a heavier rule on paper

PAPER_TEXT = PAPER  # primary text on ink
TEXT = _COLOR["text_on_ink"]["body"]  # body text on ink
MUTED = _COLOR["text_on_ink"]["muted"]  # secondary text on ink
DIM = _COLOR["text_on_ink"]["dim"]  # the quietest text on ink

INK_TEXT = INK  # primary text on paper
TEXT_INK = _COLOR["text_on_paper"]["body"]  # body text on paper
MUTED_INK = _COLOR["text_on_paper"]["muted"]  # secondary text on paper
DIM_INK = _COLOR["text_on_paper"]["dim"]  # the quietest text on paper; never a word that carries meaning


def _lch(h: str) -> tuple[float, float, float]:
    """A colour's OKLCH coordinates at the precision the theme states them: L and C to 3 places, H to 1."""
    L, C, H = hex_to_oklch(h)
    return round(L, 3), round(C, 3), round(H, 1)


#: Secondary text on paper that also clears 4.5:1 on a lifted row there.
#: muted-ink is 4.40:1 on paper-hl, so this is muted-ink moved darker in OKLCH
#: lightness, on its own hue and chroma, until it clears both. The theme holds
#: the lightness, and `verify()` fails if the result drops below 4.5:1.
MUTED_TEXT_INK_LCH = (_COLOR["text_on_paper"]["muted_text_lightness"], *_lch(MUTED_INK)[1:])
MUTED_TEXT_INK = oklch_hex(*MUTED_TEXT_INK_LCH)

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
    ("muted-text-ink", MUTED_TEXT_INK, "secondary text on paper and on a lifted row there"),
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
#: The theme holds the marks, and the uses live here.
_STATE_USE = {
    "allowed": "a request a rule allowed",
    "approval": "a request routed to a person",
    "denied": "a request a rule denied",
    "proven": "the witness's word, beside a witness flip",
    "failed": "a check that did not hold",
    "critical": "a run that needs a person now",
}
STATES: list[tuple[str, str, str, str]] = [
    (name, marks["ink"], marks["paper"], _STATE_USE[name]) for name, marks in _COLOR["states"].items()
]
STATE = {name: {"dark": d, "light": l} for name, d, l, _ in STATES}

#: The one state colour that is also text and a fill: a destructive action.
#: On paper it is the failed badge as is. On ink the failed badge is 3.8:1,
#: so the destructive red is that badge lifted in OKLCH lightness until it
#: clears AA both as text on ink and as a fill under ink text. The theme holds
#: the lift, and the hex is derived from it.
DESTRUCTIVE_LIFT = _COLOR["destructive_lift_on_ink"]


def derive_destructive() -> str:
    L, C, H = hex_to_oklch(STATE["failed"]["dark"])
    return oklch_hex(L + DESTRUCTIVE_LIFT, C, H)


DESTRUCTIVE = {"dark": derive_destructive(), "light": STATE["failed"]["light"]}
DESTRUCTIVE_TEXT_ON = {"dark": INK, "light": PAPER}  # text on a destructive fill

# --------------------------------------------------------------------------
# state as words
# --------------------------------------------------------------------------

#: The surfaces a word sits on in each theme: the canvas, a panel, and a
#: lifted row.
TEXT_SURFACES = {
    "dark": {"ink": INK, "panel": PANEL, "hl": HL},
    "light": {"paper": PAPER, "paper-hl": PAPER_HL},
}

#: A state stop is a mark: a badge or a dot, which needs 3:1. A word needs
#: 4.5:1 on every surface it sits on, so each state, and the destructive red,
#: has a text stop as well. A text stop keeps its mark's OKLCH hue and chroma
#: and moves only in lightness, away from the ground.
#:
#: On ink every text stop sits at L 0.67. That is as far as the reds have to
#: move to clear 4.5:1 on the lifted row, and one lightness sets every status
#: word at the same weight. Allowed's mark already sits there, so its text stop
#: is the mark. The destructive red is the failed red lifted, on the same hue
#: and chroma, so the two share one text stop on ink.
#:
#: On paper every mark already clears 4.5:1 on paper and on paper-hl, so each
#: text stop keeps its mark's lightness and equals the mark. The token still
#: exists: words read the text stop and marks read the bare stop, and that
#: split is what survives a mark that moves.
#:
#: The theme holds the lightness on ink, and every text stop's hex is derived.
#: `verify()` fails if a stop leaves its mark's hue, or if one drops below
#: 4.5:1 on a surface of its theme.
TEXT_L_ON_INK = _COLOR["state_text_lightness_on_ink"]


def state_marks() -> dict[str, dict[str, str]]:
    """Every mark a text stop is derived from: the six states and the destructive red."""
    return {**STATE, "destructive": DESTRUCTIVE}


def _text_stop(mark: str, theme: str) -> tuple[float, float, float]:
    L, C, H = _lch(mark)
    return (TEXT_L_ON_INK if theme == "dark" else L, C, H)


STATE_TEXT_LCH: dict[str, dict[str, tuple[float, float, float]]] = {
    name: {theme: _text_stop(mark, theme) for theme, mark in marks.items()} for name, marks in state_marks().items()
}
STATE_TEXT: dict[str, dict[str, str]] = {
    name: {theme: oklch_hex(*lch) for theme, lch in stops.items()} for name, stops in STATE_TEXT_LCH.items()
}


# --------------------------------------------------------------------------
# checks
# --------------------------------------------------------------------------


def verify() -> list[str]:
    """Every fact the palette claims, checked. Returns the problems found."""
    problems = []
    for name, lch, value in (("gold-bright", GOLD_BRIGHT_LCH, GOLD_BRIGHT), ("gold-deep", GOLD_DEEP_LCH, GOLD_DEEP)):
        # rgb_to_hex clamps a colour outside sRGB, which moves its hue, so the
        # derived hex is measured, not only its coordinates.
        _, _, h = hex_to_oklch(value)
        if abs((h - lch[2] + 180) % 360 - 180) > 2:
            problems.append(f"{name} {value} leaves the gold's hue: lightness {lch[0]} and chroma {lch[1]} fall outside sRGB there")
    gL, _, _ = hex_to_oklch(GOLD)
    if not (GOLD_DEEP_LCH[0] < gL < GOLD_BRIGHT_LCH[0]):
        problems.append("gold does not sit between its deep and bright neighbours")
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
    if set(STATE_TEXT) != set(state_marks()) or set(STATE_TEXT_LCH) != set(state_marks()):
        problems.append("every state and the destructive red need a text stop on ink and on paper")
    for name, marks in state_marks().items():
        for theme, mark in marks.items():
            lch, stop = STATE_TEXT_LCH.get(name, {}).get(theme), STATE_TEXT.get(name, {}).get(theme)
            if lch is None or stop is None:
                continue
            where = f"{name} text stop on {'ink' if theme == 'dark' else 'paper'}"
            mL, mC, mH = hex_to_oklch(mark)
            pL, pC, pH = hex_to_oklch(stop)
            # rgb_to_hex clamps out-of-gamut channels, which moves the hue, so
            # the derived hex is measured, not only its coordinates.
            if abs((pH - mH + 180) % 360 - 180) > 1 or abs(lch[1] - mC) > 0.001:
                problems.append(f"{where} leaves its mark's hue or chroma: {stop} vs {mark}")
            if theme == "dark" and pL < mL - 0.002:
                problems.append(f"{where} is darker than its mark {mark}: raise state_text_lightness_on_ink above {mL:.3f}")
            if theme == "light" and pL > mL + 0.002:
                problems.append(f"{where} is lighter than its mark {mark}")
            for surface, ground in TEXT_SURFACES[theme].items():
                if contrast(stop, ground) < 4.5:
                    problems.append(f"{where} is {contrast(stop, ground):.2f}:1 on {surface}, below AA")
    _, mC, mH = hex_to_oklch(MUTED_INK)
    _, _, pH = hex_to_oklch(MUTED_TEXT_INK)
    if abs((pH - mH + 180) % 360 - 180) > 1 or abs(MUTED_TEXT_INK_LCH[1] - mC) > 0.001:
        problems.append("muted-text-ink leaves muted-ink's hue or chroma")
    for surface, ground in TEXT_SURFACES["light"].items():
        if contrast(MUTED_TEXT_INK, ground) < 4.5:
            problems.append(f"muted-text-ink is {contrast(MUTED_TEXT_INK, ground):.2f}:1 on {surface}, below AA")
    if contrast(MUTED, HL) < 4.5:
        problems.append(f"muted is {contrast(MUTED, HL):.2f}:1 on hl, below AA")
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
