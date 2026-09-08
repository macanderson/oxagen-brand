"""Every logo, icon, lockup and spinner in the kit, emitted from one geometry.

Two wordmarks, one face, one metal.

- `oxagen`   the word in Space Grotesk 600, its `x` in gold. This is the
             Oxagen brand kit's wordmark, reproduced from the font.
- `stella*`  the word in the same face and weight, followed by the font's own
             asterisk, in the same gold. The asterisk is a character, not a
             drawing, and it is never redrawn.

Each brand has one icon for squares. Stella's is the asterisk. Oxagen's is
the ox graph: a hollow node (the `o`) wired to four context blocks (the `x`),
one node connected to many and every edge running both ways. The blocks and
their edges are gold; the node takes the letter colour, exactly as the
wordmark paints `ox`.

The house motion is the shimmer: a band of light passes over the metal. It is
declarative CSS inside the SVG, so it runs in an `<img>` with no script, and
`prefers-reduced-motion` lands it on a still mark.
"""

from __future__ import annotations

import math

from color import GOLD, GOLD_BRIGHT, GOLD_DEEP, INK, INK_TEXT, PAPER, PAPER_TEXT
from geom import path_hit
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
# the ox graph
# --------------------------------------------------------------------------

#: The graph's drawing box and its parts, in its own units. The `o` is a
#: hollow node at the centre; the `x` is four context blocks, one on each
#: diagonal, each wired to the node by a short edge. One node, many blocks,
#: and every edge runs both ways.
OXG_BOX = 96.0
OXG = {
    "cx": 48.0,
    "cy": 48.0,
    "ring_r": 15.0,  # the node's centreline radius
    "ring_w": 6.5,  # and its stroke
    "leaf_d": 41.0,  # centre to each block's centre, along the diagonal
    "leaf": 14.0,  # block side
    "leaf_rx": 3.8,  # block corner
    "edge_w": 5.0,  # the wire
    "gap": 2.2,  # daylight between the wire and what it joins
}
OXG_ANGLES = (45.0, 135.0, 225.0, 315.0)
_SQ2 = 2**0.5


def oxg_parts(weight: float = 1.0) -> dict[str, object]:
    """The graph's primitives as numbers: the ring, the four edges, the four blocks.

    `weight` thickens strokes and blocks without moving their centres, which
    is what the favicon needs at 16 px.
    """
    g = OXG
    cx, cy = g["cx"], g["cy"]
    rr, rw = g["ring_r"], g["ring_w"] * weight
    leaf, lrx = g["leaf"] * (0.5 + weight / 2), g["leaf_rx"] * (0.5 + weight / 2)
    ew, gap = g["edge_w"] * weight, g["gap"]
    edges, leaves = [], []
    for a in OXG_ANGLES:
        ux, uy = math.cos(math.radians(a)), math.sin(math.radians(a))
        r0 = rr + rw / 2 + gap
        r1 = g["leaf_d"] - leaf / 2 * _SQ2 * 0.72 - gap * 0.4
        edges.append((cx + ux * r0, cy + uy * r0, cx + ux * r1, cy + uy * r1))
        leaves.append((cx + ux * g["leaf_d"], cy + uy * g["leaf_d"]))
    half = g["leaf_d"] / _SQ2 + leaf / 2
    return {
        "ring": (cx, cy, rr, rw),
        "edges": edges,
        "edge_w": ew,
        "leaves": leaves,
        "leaf": leaf,
        "leaf_rx": lrx,
        "ink": (cx - half, cy - half, cx + half, cy + half),
    }


def oxg_mark(
    ink: str = PAPER_TEXT,
    gold: str = GOLD,
    *,
    cls: bool = False,
    opacity: float = 1.0,
    weight: float = 1.0,
) -> str:
    """The graph in its 96 box. `cls` adds the classes the spinner animates."""
    p = oxg_parts(weight)
    op = f' opacity="{opacity:g}"' if opacity < 1 else ""
    c = (lambda k: f' class="{k}"') if cls else (lambda k: "")
    cx, cy, rr, rw = p["ring"]  # type: ignore[misc]
    out = [
        '<g data-mark="ox-graph">',
        f'<circle data-part="o"{c("o")} pathLength="1" cx="{cx:g}" cy="{cy:g}" r="{rr:g}" fill="none" '
        f'stroke="{ink}" stroke-width="{rw:g}"{op}/>',
    ]
    for i, (x0, y0, x1, y1) in enumerate(p["edges"]):  # type: ignore[arg-type]
        out.append(
            f'<line data-part="e{i}"{c("e")} pathLength="1" x1="{x0:.3f}" y1="{y0:.3f}" x2="{x1:.3f}" y2="{y1:.3f}" '
            f'stroke="{gold}" stroke-width="{p["edge_w"]:g}" stroke-linecap="round"{op}/>'
        )
    s, rx = float(p["leaf"]), float(p["leaf_rx"])  # type: ignore[arg-type]
    for i, (lx, ly) in enumerate(p["leaves"]):  # type: ignore[misc]
        out.append(
            f'<rect data-part="b{i}"{c("b")} x="{lx - s / 2:.3f}" y="{ly - s / 2:.3f}" width="{s:g}" height="{s:g}" '
            f'rx="{rx:g}" fill="{gold}"{op}/>'
        )
    out.append("</g>")
    return "".join(out)


def oxg_outline(ink: str, width: float, opacity: float = 1.0) -> str:
    """The graph as a hairline: one colour, thin stroke, nothing filled."""
    p = oxg_parts()
    cx, cy, rr, rw = p["ring"]  # type: ignore[misc]
    op = f' opacity="{opacity:g}"' if opacity < 1 else ""
    st = f'fill="none" stroke="{ink}" stroke-width="{width:.4f}"{op}'
    out = [f'<g data-mark="ox-graph-outline" {st}>']
    out.append(f'<circle cx="{cx:g}" cy="{cy:g}" r="{rr + rw / 2:g}"/>')
    out.append(f'<circle cx="{cx:g}" cy="{cy:g}" r="{rr - rw / 2:g}"/>')
    ew = float(p["edge_w"])  # type: ignore[arg-type]
    for x0, y0, x1, y1 in p["edges"]:  # type: ignore[misc]
        ux, uy = x1 - x0, y1 - y0
        n = math.hypot(ux, uy)
        vx, vy = -uy / n * ew / 2, ux / n * ew / 2
        out.append(
            f'<path d="M{x0 + vx:.3f} {y0 + vy:.3f} L{x1 + vx:.3f} {y1 + vy:.3f} '
            f'M{x0 - vx:.3f} {y0 - vy:.3f} L{x1 - vx:.3f} {y1 - vy:.3f}"/>'
        )
    s, rx = float(p["leaf"]), float(p["leaf_rx"])  # type: ignore[arg-type]
    for lx, ly in p["leaves"]:  # type: ignore[misc]
        out.append(f'<rect x="{lx - s / 2:.3f}" y="{ly - s / 2:.3f}" width="{s:g}" height="{s:g}" rx="{rx:g}"/>')
    out.append("</g>")
    return "".join(out)


def oxg_hit(px: float, py: float) -> bool:
    """Whether (px, py), in the graph's own units, lands on its ink."""
    p = oxg_parts()
    cx, cy, rr, rw = p["ring"]  # type: ignore[misc]
    d = math.hypot(px - cx, py - cy)
    if abs(d - rr) <= rw / 2:
        return True
    hw = float(p["edge_w"]) / 2  # type: ignore[arg-type]
    for x0, y0, x1, y1 in p["edges"]:  # type: ignore[misc]
        dx, dy = x1 - x0, y1 - y0
        t = max(0.0, min(1.0, ((px - x0) * dx + (py - y0) * dy) / (dx * dx + dy * dy)))
        if math.hypot(px - (x0 + t * dx), py - (y0 + t * dy)) <= hw:
            return True
    half = float(p["leaf"]) / 2  # type: ignore[arg-type]
    rx = float(p["leaf_rx"])  # type: ignore[arg-type]
    for lx, ly in p["leaves"]:  # type: ignore[misc]
        ax, ay = abs(px - lx), abs(py - ly)
        if ax <= half and ay <= half:
            qx, qy = max(ax - (half - rx), 0.0), max(ay - (half - rx), 0.0)
            if qx * qx + qy * qy <= rx * rx:
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
ICON_FILL = {"stella": 0.60, "oxagen": 0.76}  # the icon's long edge over the box


def icon_geometry(brand: str) -> dict[str, object]:
    """The icon's ink box in its own drawing units, and how to paint it."""
    if brand == "stella":
        a = asterisk()
        return {"kind": "asterisk", "bounds": a["bounds"], "cx": a["cx"], "cy": a["cy"],
                "w": a["w"], "h": a["h"], "path": a["path"]}
    x0, y0, x1, y1 = oxg_parts()["ink"]  # type: ignore[misc]
    return {"kind": "graph", "bounds": (x0, y0, x1, y1), "cx": (x0 + x1) / 2, "cy": (y0 + y1) / 2,
            "w": x1 - x0, "h": y1 - y0, "path": ""}


def icon_hit(brand: str):
    """A point test in the icon's own units, for mosaics and fields."""
    if brand == "stella":
        return path_hit(str(asterisk()["path"]))
    return oxg_hit


def icon_body(
    brand: str,
    *,
    letters: str = PAPER_TEXT,
    accent: str = GOLD,
    mono: str | None = None,
    cls: bool = False,
    weight: float = 1.0,
) -> str:
    """The icon's drawing in its own units (asterisk: the em; graph: the 96 box)."""
    g = icon_geometry(brand)
    if g["kind"] == "asterisk":
        fill = mono or accent
        return f'<path class="accent" d="{g["path"]}" fill="{fill}"/>'
    return oxg_mark(mono or letters, mono or accent, cls=cls, weight=weight)


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
        f'<g transform="{t}">{icon_body(brand, letters=letters, accent=accent, mono=mono, weight=weight)}</g>'
        f"{style}</svg>"
    )


def favicon_svg(brand: str, *, box: float = 96.0, background: str | None = None) -> str:
    """The 16 to 48 px mark: the icon, set heavier and filling the square.

    Stella's asterisk survives as itself. The ox graph survives because it is
    four blocks and a ring, which is what a 16 px grid can hold; its strokes
    are thickened by a third so the wire does not fall between pixels.
    """
    if brand == "stella":
        return icon_svg(brand, box=box, background=background, fill=0.78, uid="fav")
    return icon_svg(brand, box=box, background=background, fill=0.92, weight=1.35, uid="fav")


# --------------------------------------------------------------------------
# the oxagen lockup: graph, gap, wordmark
# --------------------------------------------------------------------------


def lockup_metrics() -> dict[str, float]:
    """Where the graph sits beside the word.

    The graph is centred on the x-height band, the band the letters `o x a e n`
    live in, and stands a third taller than it, so the blocks reach a little
    above the x-height and a little below the baseline. The gap is four tenths
    of the x-height. Everything here is measured from the font, not typed.
    """
    m = wordmark("oxagen")
    f = font()
    upm = f["head"].unitsPerEm
    xh = f["OS/2"].sxHeight * EM / upm
    base = float(m["baseline"])  # type: ignore[arg-type]
    mark_h = xh * 1.34
    return {
        "w": float(m["width"]),  # type: ignore[arg-type]
        "h": float(m["height"]),  # type: ignore[arg-type]
        "xh": xh,
        "baseline": base,
        "mark_h": mark_h,
        "mark_cy": base - xh / 2,
        "gap": xh * 0.42,
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
    """The primary lockup: the graph on the x-height band, a gap, then the word."""
    lm = lockup_metrics()
    m = wordmark("oxagen")
    plain, gold = glyph_paths(m, {"x"})
    g = icon_geometry("oxagen")
    s = lm["mark_h"] / float(g["h"])  # type: ignore[arg-type]
    mark_w = float(g["w"]) * s  # type: ignore[arg-type]
    top = lm["mark_cy"] - lm["mark_h"] / 2
    y_off = min(0.0, top)  # the blocks may rise above the word's box
    h = max(lm["h"], top + lm["mark_h"]) - y_off
    w = mark_w + lm["gap"] + lm["w"]
    tx = -float(g["bounds"][0]) * s  # type: ignore[index]
    ty = top - y_off - float(g["bounds"][1]) * s  # type: ignore[index]
    uid = uid or "lk"
    bg = f'<rect width="{w:.3f}" height="{h:.3f}" fill="{background}"/>' if background else ""
    style, defs = "", ""
    if adaptive:
        letters, style = "currentColor", ADAPTIVE_STYLE
    ink, gold_c = (mono, mono) if mono else (letters, accent)
    if sheen and not mono:
        defs = f"<defs>{sheen_defs(uid)}</defs>"
        gold_c = f"url(#sheen-{uid})"
    return (
        f"{_head(w, h, 'oxagen')}{defs}{bg}"
        f'<g transform="translate({tx:.3f},{ty:.3f}) scale({s:.6f})">{icon_body("oxagen", letters=ink, accent=gold_c, mono=mono)}</g>'
        f'<g transform="translate({mark_w + lm["gap"]:.3f},{-y_off:.3f})">'
        f'<path class="letters" d="{plain}" fill="{ink}"/>'
        f'<path class="accent" d="{gold}" fill="{gold_c}"/></g>{style}</svg>'
    )


# --------------------------------------------------------------------------
# the house motion
# --------------------------------------------------------------------------

#: Oxagen's graph assembles: the node draws on, the four edges run out from it,
#: and the blocks land at their ends. Then it holds, and starts again.
_OXG_DRAW_CSS = """
.o,.e{stroke-dasharray:1;stroke-dashoffset:1}
.b{transform-box:fill-box;transform-origin:center;transform:scale(0)}
.o{animation:oxg-o {p}s cubic-bezier(.65,0,.35,1) infinite}
.e{animation:oxg-e {p}s cubic-bezier(.65,0,.35,1) infinite}
.b{animation:oxg-b {p}s cubic-bezier(.2,1.4,.4,1) infinite}
@keyframes oxg-o{0%,4%{stroke-dashoffset:1}30%,86%{stroke-dashoffset:0}100%{stroke-dashoffset:1}}
@keyframes oxg-e{0%,26%{stroke-dashoffset:1}48%,86%{stroke-dashoffset:0}100%{stroke-dashoffset:1}}
@keyframes oxg-b{0%,44%{transform:scale(0)}62%,86%{transform:scale(1)}100%{transform:scale(0)}}
@media(prefers-reduced-motion:reduce){.o,.e{animation:none;stroke-dashoffset:0}.b{animation:none;transform:none}}
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
        f'<g transform="{t}">{oxg_mark(PAPER_TEXT, GOLD, cls=True)}</g>'
        f"<style>{_OXG_DRAW_CSS.replace('{p}', f'{SPIN_PERIOD:g}')}</style></svg>"
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
    lm = lockup_metrics()
    print("lockup", {k: round(v, 2) for k, v in lm.items()})
