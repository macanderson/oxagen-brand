"""Every logo, icon, lockup and spinner in the kit, emitted from one geometry.

Two wordmarks, one face, one metal.

- `oxagen`   the word in Space Grotesk 600, its `x` in gold. This is the
             Oxagen brand kit's wordmark, reproduced from the font.
- `stella*`  the word in the same face and weight, followed by the font's own
             asterisk, in the same gold. The asterisk is a character, not a
             drawing, and it is never redrawn.

Each brand has one icon for squares. Stella's is the asterisk. Oxagen's is
the `Ox` lettermark: the word's own first two letters, capitalised the way a
name is, set in the house face and fitted tighter than the font would set
them. It carries no metal. The mark is one colour, whatever colour the
surface it sits on gives it, and it says the company's name at 16 px.

The house motion is the shimmer: a band of light passes over the mark. On the
metal it is a gold highlight; on the one-colour lettermark it is the same
gesture in value, the mark held low and the band bringing it up. It is
declarative CSS inside the SVG, so it runs in an `<img>` with no script, and
`prefers-reduced-motion` lands it on a still mark.
"""

from __future__ import annotations

from functools import lru_cache

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
# the Ox lettermark
# --------------------------------------------------------------------------

#: The mark is the word's own first two letters, capitalised the way a name
#: is: `Ox`. It is set in the house face at the display weight, and fitted
#: tighter than the font would set them, because two letters standing alone
#: are a drawing and not a word. Nothing about it is redrawn: like the
#: wordmark and like Stella's asterisk, it is outlines straight out of the
#: font, so the mark and the word can never drift apart.
#:
#: The mark carries no metal. It is one colour, always, and that colour is
#: whatever the surface gives it -- paper on ink, ink on paper,
#: `currentColor` in the adaptive files. The gold stays where the kit put it:
#: on the `x` of the wordmark.
OX_TEXT = "Ox"
OX_WEIGHT = 700  # the display weight: an icon needs more mass than a word
OX_TRACKING = -0.06  # ems, fitted by eye at 16 px and again at 256 px


@lru_cache(maxsize=None)
def ox_lettermark() -> dict[str, object]:
    """`Ox` at the logo em, one path, with its ink box and its type metrics.

    The metrics come back with it because the playbook draws them: the mark
    is letters, so its construction drawing is a baseline, an x-height and a
    cap-height, not a set of radii.
    """
    recs = set_line(OX_TEXT, 0.0, 0.0, EM, OX_WEIGHT, OX_TRACKING * EM)
    x0, y0, x1, y1 = union_bounds(recs)
    f = font(OX_WEIGHT)
    upm = float(f["head"].unitsPerEm)
    return {
        "path": " ".join(str(r["path"]) for r in recs if r["path"]),
        "glyphs": recs,
        "bounds": (x0, y0, x1, y1),
        "cx": (x0 + x1) / 2,
        "cy": (y0 + y1) / 2,
        "w": x1 - x0,
        "h": y1 - y0,
        "baseline": 0.0,
        "x_height": f["OS/2"].sxHeight * EM / upm,
        "cap_height": f["OS/2"].sCapHeight * EM / upm,
        "em": EM,
        "weight": OX_WEIGHT,
        "tracking": OX_TRACKING,
    }


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
    """The icon's ink box in its own drawing units, and how to paint it."""
    if brand == "stella":
        a = asterisk()
        return {"kind": "asterisk", "bounds": a["bounds"], "cx": a["cx"], "cy": a["cy"],
                "w": a["w"], "h": a["h"], "path": a["path"]}
    m = ox_lettermark()
    return {"kind": "letters", "bounds": m["bounds"], "cx": m["cx"], "cy": m["cy"],
            "w": m["w"], "h": m["h"], "path": m["path"]}


def icon_hit(brand: str):
    """A point test in the icon's own units, for mosaics and fields.

    Both icons are font outlines now, so both are tested the same way: the
    non-zero winding rule against the flattened contour.
    """
    return path_hit(str(icon_geometry(brand)["path"]))


def icon_body(
    brand: str,
    *,
    letters: str = PAPER_TEXT,
    accent: str = GOLD,
    mono: str | None = None,
    cls: bool = False,
) -> str:
    """The icon's drawing in its own units. Both icons are one path, one fill.

    Stella's asterisk is the wordmark's gold glyph, so it takes `accent`.
    Oxagen's lettermark carries no metal, so it takes `letters` and ignores
    `accent` entirely -- the one place in this file where the two brands
    differ in which colour a mark is handed.
    """
    g = icon_geometry(brand)
    fill = mono or (accent if g["kind"] == "asterisk" else letters)
    return f'<path class="mark" d="{g["path"]}" fill="{fill}"/>'


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
    """The brand's icon centred in a square.

    `sheen` only ever reaches Stella's asterisk: the metal is the accent, and
    Oxagen's lettermark has no accent to fill.
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
    if sheen and not mono and icon_geometry(brand)["kind"] == "asterisk":
        defs = f"<defs>{sheen_defs(uid)}</defs>"
        accent = f"url(#sheen-{uid})"
    t, _ = icon_transform(brand, box, fill)
    return (
        f"{_head(box, box, BRANDS[brand]['label'] + ' mark')}{defs}{bg}"
        f'<g transform="{t}">{icon_body(brand, letters=letters, accent=accent, mono=mono)}</g>'
        f"{style}</svg>"
    )


def favicon_svg(brand: str, *, box: float = 96.0, background: str | None = None, adaptive: bool = False) -> str:
    """The 16 to 48 px mark: the icon, filling more of the square.

    Neither mark is redrawn for small sizes. Stella's asterisk survives as
    itself, and `Ox` survives because it was fitted at 16 px in the first
    place -- the display weight keeps the stems on the pixel grid and the
    tight fit keeps the O's counter open. Only the fill fraction changes:
    the mark takes almost the whole square, because at 16 px the padding a
    256 px tile wants is four pixels it cannot spare.
    """
    fill = 0.78 if brand == "stella" else 0.90
    return icon_svg(brand, box=box, background=background, fill=fill, adaptive=adaptive, uid="fav")


# --------------------------------------------------------------------------
# the oxagen lockup: the mark in a plate, a gap, the word
# --------------------------------------------------------------------------

#: The plate: a rounded square the mark is reversed out of.
#:
#: Set plainly, `Ox oxagen` stutters -- the mark is the word's own first two
#: letters at the word's own size, so the eye reads one misspelt word rather
#: than a mark and a name. Reversing the mark out of a plate fixes it at the
#: root: the plate is an object, the word is text, and nothing about the
#: letterforms had to be compromised to tell them apart. It also costs
#: nothing in colour -- a plate with letters punched through it is one path
#: and one fill, so the lockup obeys the same one-colour rule as the icon.
LOCKUP_PLATE = 1.30  # the plate's side, over the wordmark's height
LOCKUP_INSET = 0.72  # the mark's width, over the plate's side
LOCKUP_RADIUS = 0.24  # the plate's corner, over its side


def _rounded_rect(x: float, y: float, w: float, h: float, r: float) -> str:
    return (
        f"M{x + r:.3f} {y:.3f}H{x + w - r:.3f}A{r:.3f} {r:.3f} 0 0 1 {x + w:.3f} {y + r:.3f}"
        f"V{y + h - r:.3f}A{r:.3f} {r:.3f} 0 0 1 {x + w - r:.3f} {y + h:.3f}H{x + r:.3f}"
        f"A{r:.3f} {r:.3f} 0 0 1 {x:.3f} {y + h - r:.3f}V{y + r:.3f}"
        f"A{r:.3f} {r:.3f} 0 0 1 {x + r:.3f} {y:.3f}Z"
    )


def lockup_metrics() -> dict[str, float]:
    """The plate, the gap, and the word: every number derived, none typed twice."""
    m = wordmark("oxagen")
    f = font()
    xh = f["OS/2"].sxHeight * EM / float(f["head"].unitsPerEm)
    om = ox_lettermark()
    side = float(m["height"]) * LOCKUP_PLATE  # type: ignore[arg-type]
    return {
        "w": float(m["width"]),  # type: ignore[arg-type]
        "h": float(m["height"]),  # type: ignore[arg-type]
        "xh": xh,
        "plate": side,
        "radius": side * LOCKUP_RADIUS,
        "mark_w": side * LOCKUP_INSET,
        "gap": xh * 0.62,
    }


def lockup_plate(colour: str, side: float, uid: str, *, x: float = 0.0, y: float = 0.0) -> str:
    """The plate with `Ox` punched out of it: one path, one fill, one colour.

    A mask rather than a shared `fill-rule`: the `O` brings its own counter as
    a reverse-wound contour, and an even-odd union of plate and letters would
    fill that counter back in as a solid dot.
    """
    om = ox_lettermark()
    x0, y0 = float(om["bounds"][0]), float(om["bounds"][1])  # type: ignore[index]
    s = side * LOCKUP_INSET / float(om["w"])  # type: ignore[arg-type]
    tx = x + (side - float(om["w"]) * s) / 2 - x0 * s  # type: ignore[arg-type]
    ty = y + (side - float(om["h"]) * s) / 2 - y0 * s  # type: ignore[arg-type]
    return (
        f'<mask id="plate-{uid}" maskUnits="userSpaceOnUse" x="{x:.3f}" y="{y:.3f}" '
        f'width="{side:.3f}" height="{side:.3f}">'
        f'<rect x="{x:.3f}" y="{y:.3f}" width="{side:.3f}" height="{side:.3f}" fill="#fff"/>'
        f'<path transform="translate({tx:.3f},{ty:.3f}) scale({s:.6f})" d="{om["path"]}" fill="#000"/>'
        f"</mask>"
        f'<path class="mark" mask="url(#plate-{uid})" fill="{colour}" '
        f'd="{_rounded_rect(x, y, side, side, side * LOCKUP_RADIUS)}"/>'
    )


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
    """The primary lockup: the plate, a gap, then the word, centred on each other.

    The plate takes the letter colour and never the metal. `sheen` reaches
    only the wordmark's own gold `x`, the one gold glyph the lockup has.
    """
    lm = lockup_metrics()
    m = wordmark("oxagen")
    plain, gold = glyph_paths(m, {"x"})
    side = lm["plate"]
    h = max(lm["h"], side)
    w = side + lm["gap"] + lm["w"]
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
        f'{lockup_plate(ink, side, uid, y=(h - side) / 2)}'
        f'<g transform="translate({side + lm["gap"]:.3f},{(h - lm["h"]) / 2:.3f})">'
        f'<path class="letters" d="{plain}" fill="{ink}"/>'
        f'<path class="accent" d="{gold}" fill="{gold_c}"/></g>{style}</svg>'
    )


# --------------------------------------------------------------------------
# the house motion
# --------------------------------------------------------------------------

#: What the shimmer becomes on a mark that has no metal to catch the light.
MONO_REST = 0.30  # how far down the mark is held between passes


def mono_sweep(
    uid: str,
    clip_d: str,
    bounds: tuple[float, float, float, float],
    colour: str,
    *,
    period: float = SHIMMER_PERIOD,
    rest: float = MONO_REST,
) -> tuple[str, str, str]:
    """The shimmer in value: the mark held low, a band bringing it up to full.

    The gold shimmer works by laying a brighter gold over gold. A one-colour
    mark has no brighter colour to lay over it, so the same gesture is made
    in opacity instead: the whole mark is drawn through its own outline as a
    clip, held at `rest`, and a soft band at full strength crosses it. It is
    the same band, the same tilt and the same easing as `shimmer`.

    `prefers-reduced-motion` does not simply hide the band -- that would leave
    a mark at a third strength -- it stops the animation and returns the mark
    to full.
    """
    x0, y0, x1, y1 = bounds
    w, h = x1 - x0, y1 - y0
    band = w * 0.55
    defs = (
        f'<clipPath id="shim-{uid}"><path d="{clip_d}"/></clipPath>'
        f'<linearGradient id="shimg-{uid}" x1="0" y1="0" x2="1" y2="0">'
        f'<stop offset="0" stop-color="{colour}" stop-opacity="0"/>'
        f'<stop offset="0.5" stop-color="{colour}" stop-opacity="1"/>'
        f'<stop offset="1" stop-color="{colour}" stop-opacity="0"/></linearGradient>'
    )
    body = (
        f'<g clip-path="url(#shim-{uid})">'
        f'<rect class="base-{uid}" x="{x0:.2f}" y="{y0:.2f}" width="{w:.2f}" height="{h:.2f}" '
        f'fill="{colour}"/>'
        f'<rect class="sweep-{uid}" x="{x0 - band - h * 0.4:.2f}" y="{y0 - h * 0.1:.2f}" '
        f'width="{band:.2f}" height="{h * 1.2:.2f}" fill="url(#shimg-{uid})" '
        f'transform="skewX(-18)"/></g>'
    )
    style = (
        f".base-{uid}{{opacity:{rest:g}}}"
        f".sweep-{uid}{{animation:sweep-{uid} {period:g}s cubic-bezier(.45,0,.2,1) infinite}}"
        f"@keyframes sweep-{uid}{{0%{{transform:skewX(-18deg) translateX(0)}}"
        f"55%,100%{{transform:skewX(-18deg) translateX({w + band + h * 0.8:.2f}px)}}}}"
        f"@media(prefers-reduced-motion:reduce)"
        f"{{.base-{uid}{{opacity:1}}.sweep-{uid}{{animation:none;opacity:0}}}}"
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
    # On a tile the mark takes the tile's opposite; standing on nothing it takes
    # the page, the same one-colour rule the icon files follow.
    if background is None:
        colour, adapt = "currentColor", ADAPTIVE_STYLE
    else:
        colour, adapt = (INK_TEXT if background == PAPER else PAPER_TEXT), ""
    d, b, st = mono_sweep(uid, str(g["path"]), g["bounds"], colour, period=SPIN_PERIOD)  # type: ignore[arg-type]
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
    om = ox_lettermark()
    print(f"ox      {OX_TEXT!r} wght {OX_WEIGHT} track {OX_TRACKING:+.2f}em "
          f"ink {om['w']:.1f} x {om['h']:.1f} (ratio {float(om['w']) / float(om['h']):.2f})")
    lm = lockup_metrics()
    print("lockup", {k: round(v, 2) for k, v in lm.items()})
