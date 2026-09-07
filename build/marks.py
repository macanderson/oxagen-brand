"""Every logo, icon, lockup and spinner in the kit, emitted from one geometry.

Two wordmarks, one face, one metal.

- `oxagen`   the word in Space Grotesk 600, its `x` in gold. This is the
             Oxagen brand kit's wordmark, reproduced from the font.
- `stella*`  the word in the same face and weight, followed by the font's own
             asterisk, in the same gold. The asterisk is a character, not a
             drawing, and it is never redrawn.

Each brand has one icon for squares: Stella's is the asterisk; Oxagen's is the
kit's continuous `ox` monogram, an open loop whose right edge becomes an `x`,
gold only where the two shapes share an edge.

The house motion is the shimmer: a band of light passes over the metal. It is
declarative CSS inside the SVG, so it runs in an `<img>` with no script, and
`prefers-reduced-motion` lands it on a still mark.
"""

from __future__ import annotations

from color import GOLD, GOLD_BRIGHT, GOLD_DEEP, INK, INK_TEXT, PAPER, PAPER_TEXT
from glyphs import LOGO_WEIGHT, EM, glyph_paths, set_line, union_bounds, wordmark

#: What each brand is made of. `accent` is the one glyph painted in the metal.
BRANDS: dict[str, dict[str, object]] = {
    "oxagen": {"text": "oxagen", "accent": "x", "label": "oxagen"},
    "stella": {"text": "stella*", "accent": "*", "label": "stella"},
}


def _uid(*parts: object) -> str:
    return "-".join(str(p) for p in parts)


def _head(w: float, h: float, label: str) -> str:
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w:g}" height="{h:g}" '
        f'viewBox="0 0 {w:g} {h:g}" role="img" aria-label="{label}">'
    )


#: The adaptive files carry the kit's own convention: ink on a light page,
#: paper when the page prefers dark, through `currentColor`.
ADAPTIVE_STYLE = (
    f"<style>:root{{color:{INK_TEXT}}}"
    f"@media(prefers-color-scheme:dark){{:root{{color:{PAPER_TEXT}}}}}</style>"
)


# --------------------------------------------------------------------------
# the sheen and the shimmer
# --------------------------------------------------------------------------


def sheen_defs(uid: str) -> str:
    """A diagonal metallic gradient, bottom-left to top-right, in the glyph's own box.

    Deep at the edges, the metal in the body, the highlight just past the
    middle. Subtle by design: it is what makes a flat gold read as a metal at
    poster size. Wordmark files stay flat; this is for the `-sheen` variants,
    icons on tiles, and surfaces.
    """
    return (
        f'<linearGradient id="sheen-{uid}" x1="0" y1="1" x2="1" y2="0">'
        f'<stop offset="0" stop-color="{GOLD_DEEP}"/>'
        f'<stop offset="0.38" stop-color="{GOLD}"/>'
        f'<stop offset="0.56" stop-color="{GOLD_BRIGHT}"/>'
        f'<stop offset="0.74" stop-color="{GOLD}"/>'
        f'<stop offset="1" stop-color="{GOLD_DEEP}"/></linearGradient>'
    )


SHIMMER_PERIOD = 2.8  # seconds between one pass of light and the next


def shimmer(
    uid: str, clip_d: str, bounds: tuple[float, float, float, float], *, period: float = SHIMMER_PERIOD
) -> tuple[str, str, str]:
    """A band of light crossing the gold glyph, as (defs, body, style).

    The glyph outline becomes a clip; a soft highlight band slides through it
    left to right, tilted the way a reflection tilts. The band starts off the
    glyph, so a renderer with no CSS animation (a PNG export) shows the still
    mark.
    """
    x0, y0, x1, y1 = bounds
    w, h = x1 - x0, y1 - y0
    band = w * 0.55
    defs = (
        f'<clipPath id="shim-{uid}"><path d="{clip_d}"/></clipPath>'
        f'<linearGradient id="shimg-{uid}" x1="0" y1="0" x2="1" y2="0">'
        f'<stop offset="0" stop-color="{GOLD_BRIGHT}" stop-opacity="0"/>'
        f'<stop offset="0.5" stop-color="{GOLD_BRIGHT}" stop-opacity="0.95"/>'
        f'<stop offset="1" stop-color="{GOLD_BRIGHT}" stop-opacity="0"/></linearGradient>'
    )
    body = (
        f'<g clip-path="url(#shim-{uid})"><rect class="sweep-{uid}" '
        f'x="{x0 - band - h * 0.4:.2f}" y="{y0 - h * 0.1:.2f}" width="{band:.2f}" '
        f'height="{h * 1.2:.2f}" fill="url(#shimg-{uid})" '
        f'transform="skewX(-18)"/></g>'
    )
    style = (
        f".sweep-{uid}{{animation:sweep-{uid} {period:g}s cubic-bezier(.45,0,.2,1) infinite}}"
        f"@keyframes sweep-{uid}{{0%{{transform:skewX(-18deg) translateX(0)}}"
        f"55%,100%{{transform:skewX(-18deg) translateX({w + band + h * 0.8:.2f}px)}}}}"
        f"@media(prefers-reduced-motion:reduce){{.sweep-{uid}{{animation:none;opacity:0}}}}"
    )
    return defs, body, style


# --------------------------------------------------------------------------
# wordmarks
# --------------------------------------------------------------------------


def wordmark_svg(
    brand: str,
    *,
    letters: str = PAPER_TEXT,
    accent: str = GOLD,
    background: str | None = None,
    adaptive: bool = False,
    mono: str | None = None,
    sheen: bool = False,
    shimmer_motion: bool = False,
    uid: str | None = None,
) -> str:
    """The wordmark in its ink-tight box.

    `mono` paints the whole mark one colour; pass `"currentColor"` for a mark
    that takes the colour of the surface it sits on. `adaptive` swaps only the
    letters between grounds; the gold stays gold on both, the rule the kit
    already ships. `sheen` fills the accent with the metallic gradient.
    """
    spec = BRANDS[brand]
    m = wordmark(str(spec["text"]))
    plain, gold = glyph_paths(m, {str(spec["accent"])})
    uid = uid or _uid(brand, "wm")
    w, h = float(m["width"]), float(m["height"])  # type: ignore[arg-type]
    bg = f'<rect width="{w:g}" height="{h:g}" fill="{background}"/>' if background else ""
    head = _head(w, h, f"{spec['label']} logo")
    if mono:
        return f"{head}{bg}<path d=\"{plain} {gold}\" fill=\"{mono}\"/></svg>"
    defs, style, extra = "", "", ""
    if adaptive:
        letters = "currentColor"
        style += ADAPTIVE_STYLE
    if sheen:
        defs += sheen_defs(uid)
        accent = f"url(#sheen-{uid})"
    if shimmer_motion:
        star = [g for g in m["glyphs"] if g["char"] == spec["accent"]][0]  # type: ignore[index]
        d, b, s = shimmer(uid, gold, star["bounds"])  # type: ignore[arg-type]
        defs, extra, style = defs + d, b, style + f"<style>{s}</style>"
    defs = f"<defs>{defs}</defs>" if defs else ""
    return (
        f"{head}{defs}{bg}"
        f'<path class="letters" d="{plain}" fill="{letters}"/>'
        f'<path class="accent" d="{gold}" fill="{accent}"/>{extra}{style}</svg>'
    )


# --------------------------------------------------------------------------
# the continuous ox
# --------------------------------------------------------------------------

#: The monogram's own drawing box, from the kit. Stroke geometry in these
#: units; the ink extends past the paths by half the stroke.
OX_BOX = (128.0, 96.0)
OX_STROKE = 12.0
OX_PATHS = {
    "o": "M66.213 26.787 A30 30 0 1 0 66.213 69.213",
    "xa": "M66.213 26.787 L108 72",
    "xb": "M108 24 L66.213 69.213",
    "ga": "M66.213 26.787 L78.2 39.760",
    "gb": "M66.213 69.213 L78.2 56.240",
}
#: The ink the strokes actually cover, measured with their caps.
OX_INK = (9.0, 15.51, 116.49, 80.49)


def ox_mark(
    ink: str = PAPER_TEXT,
    gold: str = GOLD,
    *,
    cls: bool = False,
    opacity: float = 1.0,
    stroke: float = OX_STROKE,
) -> str:
    """The monogram in its 128x96 box. `cls` adds classes the spinner animates.

    The `o` is an open loop; its right edge is absorbed into an asymmetric `x`.
    Gold appears only on the two short segments the loop and the `x` share, so
    the symbol stays one gesture and not a circle with a cross on it.
    """
    op = f' opacity="{opacity:g}"' if opacity < 1 else ""
    c = (lambda k: f' class="{k}"') if cls else (lambda k: "")

    def seg(key: str, colour: str, cap: str) -> str:
        return (
            f'<path data-part="{key}"{c(key)} pathLength="1" d="{OX_PATHS[key]}" fill="none" '
            f'stroke="{colour}" stroke-width="{stroke:g}" stroke-linecap="{cap}"{op}/>'
        )

    return (
        '<g data-mark="continuous-ox">'
        + seg("o", ink, "round")
        + seg("xa", ink, "square")
        + seg("xb", ink, "square")
        + seg("ga", gold, "butt")
        + seg("gb", gold, "butt")
        + "</g>"
    )


def ox_outline(ink: str, width: float, opacity: float = 1.0) -> str:
    """The monogram as a hairline: one colour, thin stroke, the gold segments left out."""
    return ox_mark(ink, ink, opacity=opacity, stroke=width).replace(
        'stroke-linecap="butt"', 'stroke-linecap="butt" visibility="hidden"'
    )


# --------------------------------------------------------------------------
# the asterisk
# --------------------------------------------------------------------------


def asterisk() -> dict[str, object]:
    """The font's asterisk at the logo em, on its own, with its ink box."""
    recs = set_line("*", 0.0, 0.0, EM, LOGO_WEIGHT)
    x0, y0, x1, y1 = union_bounds(recs)
    return {
        "path": recs[0]["path"],
        "bounds": (x0, y0, x1, y1),
        "cx": (x0 + x1) / 2,
        "cy": (y0 + y1) / 2,
        "w": x1 - x0,
        "h": y1 - y0,
    }


# --------------------------------------------------------------------------
# icons: squares
# --------------------------------------------------------------------------

ICON_BOX = 96.0
ICON_FILL = {"stella": 0.60, "oxagen": 0.74}  # the icon's long edge over the box


def icon_geometry(brand: str) -> dict[str, object]:
    """The icon's ink box in its own drawing units, and how to paint it."""
    if brand == "stella":
        a = asterisk()
        return {"kind": "asterisk", "bounds": a["bounds"], "cx": a["cx"], "cy": a["cy"],
                "w": a["w"], "h": a["h"], "path": a["path"]}
    x0, y0, x1, y1 = OX_INK
    return {"kind": "ox", "bounds": OX_INK, "cx": (x0 + x1) / 2, "cy": (y0 + y1) / 2,
            "w": x1 - x0, "h": y1 - y0, "path": ""}


def icon_body(
    brand: str,
    *,
    letters: str = PAPER_TEXT,
    accent: str = GOLD,
    mono: str | None = None,
    cls: bool = False,
) -> str:
    """The icon's drawing in its own units (asterisk: the em; ox: the 128x96 box)."""
    g = icon_geometry(brand)
    if g["kind"] == "asterisk":
        fill = mono or accent
        return f'<path class="accent" d="{g["path"]}" fill="{fill}"/>'
    return ox_mark(mono or letters, mono or accent, cls=cls)


def icon_transform(brand: str, box: float, fill: float | None = None) -> tuple[str, float]:
    """The transform that centres the icon in a `box` square at `fill` of its edge."""
    g = icon_geometry(brand)
    f = ICON_FILL[brand] if fill is None else fill
    s = box * f / max(float(g["w"]), float(g["h"]))  # type: ignore[arg-type]
    tx = box / 2 - float(g["cx"]) * s  # type: ignore[arg-type]
    ty = box / 2 - float(g["cy"]) * s  # type: ignore[arg-type]
    return f"translate({tx:.3f},{ty:.3f}) scale({s:.5f})", s


def icon_svg(
    brand: str,
    *,
    background: str | None = None,
    box: float = ICON_BOX,
    fill: float | None = None,
    radius: float | None = None,
    letters: str = PAPER_TEXT,
    accent: str = GOLD,
    mono: str | None = None,
    adaptive: bool = False,
    sheen: bool = False,
    uid: str | None = None,
) -> str:
    """The brand's icon centred in a square."""
    uid = uid or _uid(brand, "ic")
    bg = ""
    if background:
        rx = f' rx="{radius:g}"' if radius else ""
        bg = f'<rect width="{box:g}" height="{box:g}"{rx} fill="{background}"/>'
    defs, style = "", ""
    if adaptive:
        letters = "currentColor"
        style = ADAPTIVE_STYLE
    if sheen and not mono:
        defs = f"<defs>{sheen_defs(uid)}</defs>"
        accent = f"url(#sheen-{uid})"
    t, _ = icon_transform(brand, box, fill)
    return (
        f"{_head(box, box, BRANDS[brand]['label'] + ' mark')}{defs}{bg}"
        f'<g transform="{t}">{icon_body(brand, letters=letters, accent=accent, mono=mono)}</g>'
        f"{style}</svg>"
    )


def favicon_svg(brand: str, *, box: float = 96.0, background: str | None = None) -> str:
    """The 16 to 48 px mark: what survives at that size.

    Stella's asterisk survives as itself. The `ox` monogram does not, so
    Oxagen's favicon is the kit's simplified gold `x` alone.
    """
    if brand == "stella":
        return icon_svg(brand, box=box, background=background, fill=0.78, uid="fav")
    bg = f'<rect width="{box:g}" height="{box:g}" fill="{background}"/>' if background else ""
    cx = cy = box / 2
    half, stroke = box * 0.28, box * 0.19
    return (
        f"{_head(box, box, 'oxagen mark')}{bg}"
        f'<path d="M{cx - half:.3f} {cy - half:.3f} L{cx + half:.3f} {cy + half:.3f} '
        f'M{cx + half:.3f} {cy - half:.3f} L{cx - half:.3f} {cy + half:.3f}" fill="none" '
        f'stroke="{GOLD}" stroke-width="{stroke:.3f}" stroke-linecap="square"/></svg>'
    )


# --------------------------------------------------------------------------
# the oxagen lockup: monogram, gap, wordmark
# --------------------------------------------------------------------------


def lockup_svg(
    *,
    letters: str = PAPER_TEXT,
    accent: str = GOLD,
    background: str | None = None,
    adaptive: bool = False,
    mono: str | None = None,
    uid: str | None = None,
) -> str:
    """The kit's primary lockup: the monogram at 4:3 of the height, then the word."""
    m = wordmark("oxagen")
    h = float(m["height"])  # type: ignore[arg-type]
    mark_w, gap = h * 1.333333, h * 0.22
    w = mark_w + gap + float(m["width"])  # type: ignore[arg-type]
    plain, gold = glyph_paths(m, {"x"})
    s = mark_w / OX_BOX[0]
    ty = (h - OX_BOX[1] * s) / 2
    bg = f'<rect width="{w:g}" height="{h:g}" fill="{background}"/>' if background else ""
    style = ""
    if adaptive:
        letters, style = "currentColor", ADAPTIVE_STYLE
    ink, gold_c = (mono, mono) if mono else (letters, accent)
    return (
        f"{_head(w, h, 'oxagen')}{bg}"
        f'<g transform="translate(0,{ty:.3f}) scale({s:.6f})">{ox_mark(ink, gold_c)}</g>'
        f'<g transform="translate({mark_w + gap:.3f},0)">'
        f'<path class="letters" d="{plain}" fill="{ink}"/>'
        f'<path class="accent" d="{gold}" fill="{gold_c}"/></g>{style}</svg>'
    )


# --------------------------------------------------------------------------
# the house motion
# --------------------------------------------------------------------------

#: Oxagen's monogram draws itself on, the way the kit animates it, and the gold
#: segments arrive last. Then the shimmer crosses the gold. One cycle.
_OX_DRAW_CSS = """
.o,.xa,.xb,.ga,.gb{stroke-dasharray:1;stroke-dashoffset:1}
.o{animation:ox-o {p}s cubic-bezier(.65,0,.35,1) infinite}
.xa{animation:ox-xa {p}s cubic-bezier(.65,0,.35,1) infinite}
.xb{animation:ox-xb {p}s cubic-bezier(.65,0,.35,1) infinite}
.ga,.gb{animation:ox-g {p}s cubic-bezier(.65,0,.35,1) infinite}
@keyframes ox-o{0%,4%{stroke-dashoffset:1}30%,86%{stroke-dashoffset:0}100%{stroke-dashoffset:1}}
@keyframes ox-xa{0%,22%{stroke-dashoffset:1}48%,86%{stroke-dashoffset:0}100%{stroke-dashoffset:1}}
@keyframes ox-xb{0%,32%{stroke-dashoffset:1}58%,86%{stroke-dashoffset:0}100%{stroke-dashoffset:1}}
@keyframes ox-g{0%,40%{stroke-dashoffset:1}62%,86%{stroke-dashoffset:0}100%{stroke-dashoffset:1}}
@media(prefers-reduced-motion:reduce){.o,.xa,.xb,.ga,.gb{animation:none;stroke-dashoffset:0}}
"""

#: Stella's asterisk turns a sixth of a turn, its own symmetry, while the light
#: crosses it, so the shimmer reads as a glint on something that moved.
_STAR_TURN_CSS = """
.turn{transform-origin:{cx:.3f}px {cy:.3f}px;animation:turn {p}s cubic-bezier(.6,0,.2,1) infinite}
@keyframes turn{0%,20%{transform:rotate(0deg)}70%,100%{transform:rotate(60deg)}}
@media(prefers-reduced-motion:reduce){.turn{animation:none}}
"""

SPIN_PERIOD = 3.2


def spinner_svg(
    brand: str, *, box: float = 96.0, background: str | None = None, uid: str | None = None
) -> str:
    """The icon, in motion. Drop it in an `<img>`; it needs no script."""
    uid = uid or _uid(brand, "sp")
    t, s = icon_transform(brand, box, 0.68)
    bg = f'<rect width="{box:g}" height="{box:g}" fill="{background}"/>' if background else ""
    g = icon_geometry(brand)
    if brand == "stella":
        d, b, st = shimmer(uid, str(g["path"]), g["bounds"], period=SPIN_PERIOD)  # type: ignore[arg-type]
        turn = _STAR_TURN_CSS.replace("{cx:.3f}", f"{float(g['cx']):.3f}").replace(  # type: ignore[arg-type]
            "{cy:.3f}", f"{float(g['cy']):.3f}"  # type: ignore[arg-type]
        ).replace("{p}", f"{SPIN_PERIOD:g}")
        # The rotating group carries no `transform` attribute of its own: a CSS
        # transform animation replaces the attribute rather than composing
        # with it, and the star would spin about the wrong point, off-canvas.
        return (
            f"{_head(box, box, 'stella loading')}<defs>{d}</defs>{bg}"
            f'<g transform="{t}"><g class="turn">'
            f'<path d="{g["path"]}" fill="{GOLD}"/>{b}</g></g>'
            f"<style>{turn}{st}</style></svg>"
        )
    return (
        f"{_head(box, box, 'oxagen loading')}{bg}"
        f'<g transform="{t}">{ox_mark(PAPER_TEXT, GOLD, cls=True)}</g>'
        f"<style>{_OX_DRAW_CSS.replace('{p}', f'{SPIN_PERIOD:g}')}</style></svg>"
    )


def spinner_wordmark_svg(brand: str, *, uid: str | None = None) -> str:
    """The full wordmark with light crossing its gold: a loading masthead."""
    return wordmark_svg(brand, shimmer_motion=True, uid=uid or _uid(brand, "spw"))


if __name__ == "__main__":
    for b in BRANDS:
        m = wordmark(str(BRANDS[b]["text"]))
        print(f"{b:7} wordmark {m['width']:g} x {m['height']:g}")
        g = icon_geometry(b)
        print(f"{b:7} icon {g['kind']} ink {g['w']:.1f} x {g['h']:.1f}")
