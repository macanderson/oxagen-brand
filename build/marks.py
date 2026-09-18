"""Every logo, icon, lockup and spinner in the kit, emitted from one geometry.

Two wordmarks, one face, one metal.

- `oxagen`   the word in Space Grotesk 600, its `x` in gold. This is the
             Oxagen brand kit's wordmark, reproduced from the font.
- `stella*`  the word in the same face and weight, followed by the font's own
             asterisk, in the same gold. The asterisk is a character, not a
             drawing, and it is never redrawn.

Each brand has one icon for squares. Stella's is the asterisk. Oxagen's is
the hive: six hexagonal cells on a honeycomb grid, four drawn as an outline
in the surface's own ink and two filled with the metal, one of them at half
strength. The cells are the knowledge graph as a picture -- a lattice, with
the parts Oxagen has learned lit up in gold -- and they are primitives, so
the mark is a handful of numbers rather than a drawing.

The house motion is the shimmer: a band of light passes over the mark. On the
metal it is a gold highlight; on the hive's ink it is the same gesture in
value, the outline held low and the band bringing it up. It is declarative
CSS inside the SVG, so it runs in an `<img>` with no script, and
`prefers-reduced-motion` lands it on a still mark.
"""

from __future__ import annotations

import math
from functools import lru_cache

from color import GOLD, GOLD_BRIGHT, GOLD_DEEP, INK, INK_TEXT, PAPER, PAPER_TEXT
from geom import Point, path_hit
from glyphs import LOGO_WEIGHT, EM, font, glyph_paths, set_line, union_bounds, wordmark

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


def metal_defs(uid: str) -> str:
    """The metal lit from above: bright at the top-left, deep at the bottom-right.

    The sheen's three colours in one pass rather than a streak. It is what
    the hive's cells take when they are asked for the metal, because a
    cell is a face, and a face under one light is bright on the side the
    light comes from and deep on the other. Applied in the cell's own box,
    so every cell is lit the same way.
    """
    return (
        f'<linearGradient id="metal-{uid}" x1="0" y1="0" x2="1" y2="1">'
        f'<stop offset="0" stop-color="{GOLD_BRIGHT}"/>'
        f'<stop offset="0.5" stop-color="{GOLD}"/>'
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
# the hive
# --------------------------------------------------------------------------

#: The hive's geometry, measured from the drawing it was approved as
#: (September 2026) and nothing else. A cell is a pointy-top hexagon,
#: `r` from centre to top, `w` from centre to side -- a touch wider than a
#: regular hexagon would be, which is what keeps the cluster reading as a
#: square. Rows sit `py` apart and cells `px` apart along a row, with the
#: middle row shifted half a pitch, the way a honeycomb is. `stroke` is the
#: outline at this scale; the favicon thickens it, and nothing else does.
HIVE = {
    "r": 6.08,
    "w": 5.80,
    "px": 13.08,
    "py": 10.24,
    "stroke": 1.0,
}

#: Which cells there are, and what each is. `(col, row)` on the grid; the
#: middle row is the offset one. `ink` is an outline in the surface colour,
#: `gold` is filled with the metal, `gold-half` the same at half strength.
HIVE_CELLS: tuple[tuple[int, int, str], ...] = (
    (0, 0, "ink"),
    (1, 0, "ink"),
    (0, 1, "ink"),
    (1, 1, "gold"),
    (0, 2, "gold-half"),
    (1, 2, "ink"),
)
HIVE_HALF = 0.55  # the half-strength cell's opacity


def hive_centre(col: int, row: int) -> Point:
    """Where a cell sits, in the hive's own units. Cell (0, 0) is the origin."""
    return (col * HIVE["px"] + (HIVE["px"] / 2 if row == 1 else 0.0), row * HIVE["py"])


def hive_scale(kind: str, weight: float = 1.0) -> float:
    """How far a cell is grown from the outline's centreline.

    A filled cell is drawn out to the outline's outer edge, so the two kinds
    stand the same size on the page; an outlined cell stays on its
    centreline and lets the stroke reach out to meet it.
    """
    if kind == "ink":
        return 1.0
    return (HIVE["r"] + HIVE["stroke"] * weight / 2) / HIVE["r"]


def hive_polygon(cx: float, cy: float, scale: float = 1.0) -> list[Point]:
    """The six corners of one cell, clockwise from the top."""
    r, w = HIVE["r"] * scale, HIVE["w"] * scale
    return [(cx, cy - r), (cx + w, cy - r / 2), (cx + w, cy + r / 2), (cx, cy + r), (cx - w, cy + r / 2), (cx - w, cy - r / 2)]


def _poly_d(pts: list[Point]) -> str:
    return "M" + "L".join(f"{x:.3f} {y:.3f}" for x, y in pts) + "Z"


@lru_cache(maxsize=None)
def hive() -> dict[str, object]:
    """Every cell placed, and the ink box round all of them.

    The box is measured to the outside of the outline, the same edge the
    filled cells are drawn to, so the mark centres on what is actually
    painted.
    """
    cells = []
    for col, row, kind in HIVE_CELLS:
        cx, cy = hive_centre(col, row)
        cells.append({"cx": cx, "cy": cy, "kind": kind, "outer": hive_polygon(cx, cy, hive_scale("gold"))})
    xs = [x for c in cells for x, _ in c["outer"]]  # type: ignore[union-attr]
    ys = [y for c in cells for _, y in c["outer"]]  # type: ignore[union-attr]
    x0, y0, x1, y1 = min(xs), min(ys), max(xs), max(ys)
    return {
        "cells": cells,
        "path": " ".join(_poly_d(c["outer"]) for c in cells),  # type: ignore[arg-type]
        "bounds": (x0, y0, x1, y1),
        "cx": (x0 + x1) / 2,
        "cy": (y0 + y1) / 2,
        "w": x1 - x0,
        "h": y1 - y0,
    }


def hive_mark(
    ink: str = PAPER_TEXT,
    gold: str = GOLD,
    *,
    weight: float = 1.0,
    ink_opacity: float = 1.0,
    cls: bool = False,
) -> str:
    """The hive in its own units: four outlines in `ink`, two cells in `gold`.

    `weight` thickens the outline without moving the cells, which is what
    the favicon needs at 16 px. `ink_opacity` is for the spinner, which
    holds the outline low while the light is elsewhere. `cls` tags each
    cell with its kind so a stylesheet can reach it.
    """
    sw = HIVE["stroke"] * weight
    out = ['<g data-mark="hive">']
    for c in hive()["cells"]:  # type: ignore[union-attr]
        kind = str(c["kind"])
        k = f' class="{kind}"' if cls else ""
        if kind == "ink":
            pts = hive_polygon(float(c["cx"]), float(c["cy"]))
            op = f' stroke-opacity="{ink_opacity:g}"' if ink_opacity < 1 else ""
            out.append(
                f'<path{k} d="{_poly_d(pts)}" fill="none" stroke="{ink}" '
                f'stroke-width="{sw:g}" stroke-linejoin="miter"{op}/>'
            )
        else:
            pts = hive_polygon(float(c["cx"]), float(c["cy"]), hive_scale(kind, weight))
            op = f' opacity="{HIVE_HALF:g}"' if kind == "gold-half" else ""
            out.append(f'<path{k} d="{_poly_d(pts)}" fill="{gold}"{op}/>')
    out.append("</g>")
    return "".join(out)


def _in_hex(px: float, py: float, cx: float, cy: float, scale: float) -> bool:
    """Whether a point lies inside one cell grown by `scale`."""
    r, w = HIVE["r"] * scale, HIVE["w"] * scale
    ax, ay = abs(px - cx), abs(py - cy)
    return ax <= w and ay <= r - (r / 2) * (ax / w)


def hive_hit(px: float, py: float, *, weight: float = 1.6) -> bool:
    """Whether (px, py), in the hive's own units, lands on its ink.

    A filled cell counts everywhere inside it; an outlined cell counts only
    on its outline, taken a little heavier than drawn so a mosaic built
    from it stays joined up.
    """
    sw = HIVE["stroke"] * weight
    for c in hive()["cells"]:  # type: ignore[union-attr]
        cx, cy, kind = float(c["cx"]), float(c["cy"]), str(c["kind"])
        if kind != "ink":
            if _in_hex(px, py, cx, cy, hive_scale(kind)):
                return True
        else:
            grow = sw / 2 / HIVE["r"]
            if _in_hex(px, py, cx, cy, 1 + grow) and not _in_hex(px, py, cx, cy, 1 - grow):
                return True
    return False


def hive_lit(px: float, py: float) -> bool:
    """Whether (px, py), in the hive's own units, lands on one of its two lit cells."""
    for c in hive()["cells"]:  # type: ignore[union-attr]
        kind = str(c["kind"])
        if kind != "ink" and _in_hex(px, py, float(c["cx"]), float(c["cy"]), hive_scale(kind)):
            return True
    return False


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
ICON_FILL = {"stella": 0.60, "oxagen": 0.72}  # the icon's long edge over the box


def icon_geometry(brand: str) -> dict[str, object]:
    """The icon's ink box in its own drawing units, and how to paint it.

    `path` is the icon as closed outlines -- the glyph contour for the
    asterisk, the six cells for the hive -- for the surfaces that trace the
    mark rather than paint it.
    """
    if brand == "stella":
        a = asterisk()
        return {"kind": "asterisk", "bounds": a["bounds"], "cx": a["cx"], "cy": a["cy"],
                "w": a["w"], "h": a["h"], "path": a["path"]}
    h = hive()
    return {"kind": "hive", "bounds": h["bounds"], "cx": h["cx"], "cy": h["cy"],
            "w": h["w"], "h": h["h"], "path": h["path"]}


def icon_hit(brand: str):
    """A point test in the icon's own units, for mosaics and fields.

    The asterisk is a font outline, so it is flattened and tested by the
    non-zero winding rule. The hive is primitives and tests itself.
    """
    if brand == "stella":
        return path_hit(str(icon_geometry(brand)["path"]))
    return hive_hit


def icon_body(
    brand: str,
    *,
    letters: str = PAPER_TEXT,
    accent: str = GOLD,
    mono: str | None = None,
    cls: bool = False,
    weight: float = 1.0,
    ink_opacity: float = 1.0,
) -> str:
    """The icon's drawing in its own units.

    Stella's asterisk is the wordmark's gold glyph, one path in `accent`.
    Oxagen's hive is two colours: its outlines take `letters`, the colour
    of the surface's own text, and its filled cells take `accent`. `mono`
    paints all of it one colour.
    """
    g = icon_geometry(brand)
    if g["kind"] == "asterisk":
        return f'<path class="mark" d="{g["path"]}" fill="{mono or accent}"/>'
    return hive_mark(mono or letters, mono or accent, weight=weight, ink_opacity=ink_opacity, cls=cls)


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
    weight: float = 1.0,
    uid: str | None = None,
) -> str:
    """The brand's icon centred in a square.

    `sheen` fills whatever is gold with the metal: the asterisk takes the
    sheen, the hive's two lit cells take the metal lit from above. The
    hive's outlines never take either.
    """
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
        if brand == "stella":
            defs, accent = f"<defs>{sheen_defs(uid)}</defs>", f"url(#sheen-{uid})"
        else:
            defs, accent = f"<defs>{metal_defs(uid)}</defs>", f"url(#metal-{uid})"
    t, _ = icon_transform(brand, box, fill)
    return (
        f"{_head(box, box, BRANDS[brand]['label'] + ' mark')}{defs}{bg}"
        f'<g transform="{t}">{icon_body(brand, letters=letters, accent=accent, mono=mono, weight=weight)}</g>'
        f"{style}</svg>"
    )


#: How much heavier the hive's outline is drawn at favicon size. At 16 px
#: the outline as drawn is under half a pixel and vanishes; at this weight
#: it holds a pixel and a half at 32 px, the size a tab actually shows.
FAVICON_WEIGHT = 2.4


def favicon_svg(
    brand: str,
    *,
    box: float = 96.0,
    background: str | None = None,
    radius: float | None = None,
    adaptive: bool = False,
    letters: str = PAPER_TEXT,
) -> str:
    """The 16 to 48 px mark: the icon, filling more of the square.

    Neither mark is redrawn for small sizes. Stella's asterisk survives as
    itself. The hive survives because it is six cells on a grid, which is
    what a 16 px grid can hold; only its outline is thickened, so the ink
    cells do not fall between pixels. The fill fraction goes up too: the
    mark takes almost the whole square, because at 16 px the padding a
    256 px tile wants is four pixels it cannot spare.
    """
    if brand == "stella":
        return icon_svg(brand, box=box, background=background, radius=radius, fill=0.78, adaptive=adaptive, letters=letters, uid="fav")
    return icon_svg(
        brand, box=box, background=background, radius=radius, fill=0.88, adaptive=adaptive, letters=letters,
        weight=FAVICON_WEIGHT, uid="fav",
    )


# --------------------------------------------------------------------------
# the oxagen lockup: the hive, a gap, the word
# --------------------------------------------------------------------------

#: The hive stands a little taller than the wordmark's box and centres on
#: it. A gap of a little over half an x-height keeps the two apart without
#: letting them drift.
LOCKUP_MARK = 1.24  # the hive's long edge, over the wordmark's height
LOCKUP_GAP = 0.62  # the gap, over the x-height


def lockup_metrics() -> dict[str, float]:
    """The mark, the gap, and the word: every number derived, none typed twice."""
    m = wordmark("oxagen")
    f = font()
    xh = f["OS/2"].sxHeight * EM / float(f["head"].unitsPerEm)
    return {
        "w": float(m["width"]),  # type: ignore[arg-type]
        "h": float(m["height"]),  # type: ignore[arg-type]
        "xh": xh,
        "mark": float(m["height"]) * LOCKUP_MARK,  # type: ignore[arg-type]
        "gap": xh * LOCKUP_GAP,
    }


def lockup_svg(
    *,
    letters: str = PAPER_TEXT,
    accent: str = GOLD,
    background: str | None = None,
    adaptive: bool = False,
    mono: str | None = None,
    sheen: bool = False,
    uid: str | None = None,
) -> str:
    """The primary lockup: the hive, a gap, then the word, centred on each other.

    The hive's outlines take the letter colour and its lit cells take the
    metal, exactly as the icon does. `sheen` reaches every gold in it: the
    wordmark's `x` takes the sheen, the hive's cells the metal lit from
    above, each as it does on its own.
    """
    lm = lockup_metrics()
    m = wordmark("oxagen")
    plain, gold = glyph_paths(m, {"x"})
    g = icon_geometry("oxagen")
    s = lm["mark"] / max(float(g["w"]), float(g["h"]))  # type: ignore[arg-type]
    mw, mh = float(g["w"]) * s, float(g["h"]) * s  # type: ignore[arg-type]
    h = max(lm["h"], mh)
    w = mw + lm["gap"] + lm["w"]
    uid = uid or "lk"
    bg = f'<rect width="{w:.3f}" height="{h:.3f}" fill="{background}"/>' if background else ""
    style, defs = "", ""
    if adaptive:
        letters, style = "currentColor", ADAPTIVE_STYLE
    ink, gold_c = (mono, mono) if mono else (letters, accent)
    cell_c = gold_c
    if sheen and not mono:
        defs = f"<defs>{sheen_defs(uid)}{metal_defs(uid)}</defs>"
        gold_c, cell_c = f"url(#sheen-{uid})", f"url(#metal-{uid})"
    tx = mw / 2 - float(g["cx"]) * s  # type: ignore[arg-type]
    ty = h / 2 - float(g["cy"]) * s  # type: ignore[arg-type]
    return (
        f"{_head(w, h, 'oxagen')}{defs}{bg}"
        f'<g transform="translate({tx:.3f},{ty:.3f}) scale({s:.6f})">'
        f'{icon_body("oxagen", letters=ink, accent=cell_c, mono=mono)}</g>'
        f'<g transform="translate({mw + lm["gap"]:.3f},{(h - lm["h"]) / 2:.3f})">'
        f'<path class="letters" d="{plain}" fill="{ink}"/>'
        f'<path class="accent" d="{gold}" fill="{gold_c}"/></g>{style}</svg>'
    )


# --------------------------------------------------------------------------
# the house motion
# --------------------------------------------------------------------------

#: What the shimmer becomes on the hive's ink, which has no metal to catch the light.
MONO_REST = 0.30  # how far down the outline is held between passes


def mark_sweep(
    uid: str,
    body_rest: str,
    body_lit: str,
    bounds: tuple[float, float, float, float],
    *,
    period: float = SHIMMER_PERIOD,
) -> tuple[str, str, str]:
    """The shimmer over a drawing that is not one path: (defs, body, style).

    `shimmer` clips a band of brighter gold to a glyph outline. A mark made
    of strokes and fills has no single outline to clip to, so the band is a
    mask instead: `body_rest` is drawn as the mark stands between passes,
    and `body_lit` -- the same mark at full strength, its gold at the
    highlight -- is revealed through a soft band that crosses it. Same
    band, same tilt, same easing as `shimmer`.

    `prefers-reduced-motion` does not simply hide the band -- that would
    leave the mark at rest -- it stops the animation and shows the lit
    mark whole.
    """
    x0, y0, x1, y1 = bounds
    w, h = x1 - x0, y1 - y0
    band = w * 0.55
    defs = (
        f'<linearGradient id="shimg-{uid}" x1="0" y1="0" x2="1" y2="0">'
        f'<stop offset="0" stop-color="#fff" stop-opacity="0"/>'
        f'<stop offset="0.5" stop-color="#fff" stop-opacity="1"/>'
        f'<stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient>'
        f'<mask id="shim-{uid}" maskUnits="userSpaceOnUse" '
        f'x="{x0 - band * 2 - h:.2f}" y="{y0 - h * 0.1:.2f}" width="{w + band * 4 + h * 2:.2f}" height="{h * 1.2:.2f}">'
        f'<rect class="sweep-{uid}" x="{x0 - band - h * 0.4:.2f}" y="{y0 - h * 0.1:.2f}" width="{band:.2f}" '
        f'height="{h * 1.2:.2f}" fill="url(#shimg-{uid})" transform="skewX(-18)"/></mask>'
    )
    body = (
        f'<g class="rest-{uid}">{body_rest}</g>'
        f'<g class="lit-{uid}" mask="url(#shim-{uid})">{body_lit}</g>'
    )
    style = (
        f".sweep-{uid}{{animation:sweep-{uid} {period:g}s cubic-bezier(.45,0,.2,1) infinite}}"
        f"@keyframes sweep-{uid}{{0%{{transform:skewX(-18deg) translateX(0)}}"
        f"55%,100%{{transform:skewX(-18deg) translateX({w + band + h * 0.8:.2f}px)}}}}"
        f"@media(prefers-reduced-motion:reduce)"
        f"{{.rest-{uid}{{display:none}}.lit-{uid}{{mask:none}}.sweep-{uid}{{animation:none}}}}"
    )
    return defs, body, style

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
    # On a tile the outline takes the tile's opposite; standing on nothing it
    # takes the page, the same rule the icon files follow. The gold is gold.
    if background is None:
        colour, adapt = "currentColor", ADAPTIVE_STYLE
    else:
        colour, adapt = (INK_TEXT if background == PAPER else PAPER_TEXT), ""
    rest = icon_body(brand, letters=colour, accent=GOLD, ink_opacity=MONO_REST)
    lit = icon_body(brand, letters=colour, accent=GOLD_BRIGHT)
    d, b, st = mark_sweep(uid, rest, lit, g["bounds"], period=SPIN_PERIOD)  # type: ignore[arg-type]
    return (
        f"{_head(box, box, 'oxagen loading')}<defs>{d}</defs>{bg}"
        f'<g transform="{t}">{b}</g><style>{st}</style>{adapt}</svg>'
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
    hv = hive()
    print(f"hive    {len(HIVE_CELLS)} cells, ink {hv['w']:.1f} x {hv['h']:.1f} "
          f"(ratio {float(hv['w']) / float(hv['h']):.2f})")  # type: ignore[arg-type]
    lm = lockup_metrics()
    print("lockup", {k: round(v, 2) for k, v in lm.items()})
