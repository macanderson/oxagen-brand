"""Every logo and spinner in the kit, emitted from one geometry.

There is exactly one shape in this brand: the JetBrains Mono ExtraBold asterisk
at the end of a lowercase wordmark. Stella paints all five of its arms in the
house metal; oxagen paints them in the five-hue spectrum. Nothing else differs,
which is the whole argument -- two products of one company, one letterform, one
star, and a colour that says which is which.

The asterisk is never redrawn to make the arms paintable. The real glyph outline
becomes a clip path and five 72-degree wedges are painted through it, so the
coloured star and the gold one are the same curve to the last control point.
"""

from __future__ import annotations

import math

from color import GOLD, INK, PAPER, RAY_NAMES, RESTING
from glyphs import wordmark

PAPER_TEXT = "#F4F1EA"  # stella's --st-paper-text: letters on the ink canvas
INK_TEXT = "#141413"  # stella's --st-ink: letters on warm paper

#: Clockwise from twelve o'clock. Warm at the top-right, cool at the top-left.
RAY_ORDER = RAY_NAMES

STELLA_RAYS = [GOLD] * 5
OXAGEN_RAYS = [RESTING[n] for n in RAY_ORDER]

BRANDS = {"stella": STELLA_RAYS, "oxagen": OXAGEN_RAYS}


def _uid(*parts: object) -> str:
    return "-".join(str(p) for p in parts)


def wedges(cx: float, cy: float, r: float, rays: list[str]) -> str:
    """Five 72-degree sectors about the star's centre, ray 0 pointing up."""
    out = []
    reach = r * 3  # past the glyph's outer edge at every angle, then clipped
    for k, fill in enumerate(rays):
        a0 = math.radians(-90 + 72 * k - 36)
        a1 = math.radians(-90 + 72 * k + 36)
        out.append(
            f'<path class="ray ray{k}" d="M{cx:.2f} {cy:.2f} '
            f"L{cx + reach * math.cos(a0):.2f} {cy + reach * math.sin(a0):.2f} "
            f'L{cx + reach * math.cos(a1):.2f} {cy + reach * math.sin(a1):.2f} Z" '
            f'fill="{fill}"/>'
        )
    return "".join(out)


def star_group(m: dict, rays: list[str], uid: str) -> tuple[str, str]:
    """The painted star as (defs, body). Body must sit in the wordmark's space."""
    defs = f'<clipPath id="clip-{uid}"><path d="{m["star"]}"/></clipPath>'
    body = (
        f'<g class="star" clip-path="url(#clip-{uid})">'
        f'{wedges(m["star_cx"], m["star_cy"], m["star_r"], rays)}</g>'
    )
    return defs, body


# --------------------------------------------------------------------------
# wordmarks
# --------------------------------------------------------------------------


def wordmark_svg(
    word: str,
    rays: list[str],
    *,
    letters: str = PAPER_TEXT,
    background: str | None = None,
    adaptive: bool = False,
    mono: str | None = None,
    uid: str | None = None,
) -> str:
    """`word` plus its star, in the shared 264x96 box.

    `mono` paints the whole mark one colour (pass `"currentColor"` for a mark
    that inherits from the surface it is placed on). `adaptive` swaps only the
    letters between grounds -- the star keeps its colour on both, which is the
    rule stella already ships for its gold.
    """
    m = wordmark(word)
    uid = uid or _uid(word, "wm")
    w, h = m["width"], m["height"]
    bg = f'<rect width="{w:g}" height="{h:g}" fill="{background}"/>' if background else ""

    if mono:
        return (
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{w:g}" height="{h:g}" '
            f'viewBox="0 0 {w:g} {h:g}" fill="none" role="img" '
            f'aria-label="{word} logo">{bg}'
            f'<path d="{m["letters"]}" fill="{mono}"/>'
            f'<path d="{m["star"]}" fill="{mono}"/></svg>'
        )

    defs, body = star_group(m, rays, uid)
    style = ""
    if adaptive:
        style = (
            "<style>@media (prefers-color-scheme: light)"
            f"{{.letters-{uid}{{fill:{INK_TEXT}}}}}</style>"
        )
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w:g}" height="{h:g}" '
        f'viewBox="0 0 {w:g} {h:g}" fill="none" role="img" aria-label="{word} logo">'
        f"<defs>{defs}</defs>{bg}"
        f'<path class="letters-{uid}" d="{m["letters"]}" fill="{letters}"/>'
        f"{body}{style}</svg>"
    )


# --------------------------------------------------------------------------
# the star on its own -- avatars, favicons, app icons
# --------------------------------------------------------------------------

ICON_BOX = 96.0
ICON_FILL = 0.62  # the star's long edge as a fraction of the box


def star_only_svg(
    rays: list[str],
    *,
    background: str | None = None,
    box: float = ICON_BOX,
    fill: float = ICON_FILL,
    radius: float | None = None,
    mono: str | None = None,
    uid: str = "star",
) -> str:
    """The asterisk centred in a square, at `fill` of the box's long edge."""
    m = wordmark("stella")  # the star is the same glyph in either wordmark
    x0, y0 = m["star_cx"] - m["star_r"], m["star_cy"] - m["star_r"]
    side = m["star_r"] * 2
    s = box * fill / side
    tx = box / 2 - (m["star_cx"]) * s
    ty = box / 2 - (m["star_cy"]) * s
    bg = ""
    if background:
        rx = f' rx="{radius:g}"' if radius else ""
        bg = f'<rect width="{box:g}" height="{box:g}"{rx} fill="{background}"/>'
    if mono:
        inner = f'<path d="{m["star"]}" fill="{mono}"/>'
        defs = ""
    else:
        defs, inner = star_group(m, rays, uid)
        defs = f"<defs>{defs}</defs>"
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{box:g}" height="{box:g}" '
        f'viewBox="0 0 {box:g} {box:g}" fill="none" role="img" aria-label="mark">'
        f"{defs}{bg}<g transform=\"translate({tx:.3f},{ty:.3f}) scale({s:.5f})\">"
        f"{inner}</g></svg>"
    )


# --------------------------------------------------------------------------
# the house motion
# --------------------------------------------------------------------------

SPIN_PERIOD = 1.25  # seconds for one trip around the five arms

#: One motion for both brands: the arms light in turn, clockwise, and the star
#: steps a fifth of a turn each cycle so the lit arm keeps travelling instead of
#: pulsing in place. Declarative CSS only, so it runs inside `<img>` with no
#: script, and `prefers-reduced-motion` lands it on a whole, still star.
_SPIN_CSS = """
.star{{transform-origin:{cx:.2f}px {cy:.2f}px;animation:step {step:.3f}s steps(1,end) infinite}}
.ray{{animation:lift {period:.3f}s linear infinite}}
{delays}
@keyframes step{{from{{transform:rotate(0deg)}}to{{transform:rotate(72deg)}}}}
@keyframes lift{{0%{{opacity:1}}18%{{opacity:1}}36%{{opacity:.24}}100%{{opacity:.24}}}}
@media (prefers-reduced-motion:reduce){{
.star{{animation:none}}.ray{{animation:none;opacity:1}}}}
"""


def spin_style(cx: float, cy: float, period: float = SPIN_PERIOD) -> str:
    delays = "\n".join(
        f".ray{k}{{animation-delay:{-k * period / 5:.3f}s}}" for k in range(5)
    )
    return (
        "<style>"
        + _SPIN_CSS.format(cx=cx, cy=cy, step=period, period=period, delays=delays)
        + "</style>"
    )


def spinner_svg(
    rays: list[str], *, box: float = 96.0, background: str | None = None, uid: str = "spin"
) -> str:
    """The star alone, animating. Drop it in an `<img>`; it needs no script."""
    svg = star_only_svg(rays, background=background, box=box, fill=0.72, uid=uid)
    m = wordmark("stella")
    return svg.replace("</svg>", spin_style(m["star_cx"], m["star_cy"]) + "</svg>")


def spinner_wordmark_svg(word: str, rays: list[str], *, uid: str | None = None) -> str:
    """The full lockup with only its star in motion -- a loading masthead."""
    uid = uid or _uid(word, "spin")
    svg = wordmark_svg(word, rays, uid=uid)
    m = wordmark(word)
    return svg.replace("</svg>", spin_style(m["star_cx"], m["star_cy"]) + "</svg>")
