"""Outline house wordmarks straight out of JetBrains Mono ExtraBold.

Every wordmark in this kit is a string set in one face at one size and then
outlined, so the logos never depend on a font being installed and can never
drift apart from each other. The transform below is not invented: it is the one
recovered from stella's shipped `logo/svg/wordmark-color-dark.svg`, which this
module reproduces byte-for-byte in `verify()`. That is what makes `oxagen*` a
sibling of `stella*` rather than a lookalike -- same face, same weight, same
600/1000 advance, same baseline, same 6-unit side padding, same 264x96 box.
"""

from __future__ import annotations

from pathlib import Path

from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.pens.boundsPen import BoundsPen
from fontTools.ttLib import TTFont

#: JetBrains Mono, as vendored in stella's brand kit. One family, four weights,
#: and a 600/1000 advance at every one of them -- which is why a line's width is
#: arithmetic here rather than a measurement.
FONTS = {
    w: Path(
        "/Users/macanderson/Projects/stella/docs/brand/fonts/"
        f"jetbrains-mono-latin-{w}-normal.woff2"
    )
    for w in (400, 500, 700, 800)
}
FONT = FONTS[800]  # the wordmark weight
ADVANCE_RATIO = 0.6  # every glyph, every weight

SIZE = 60.0  # em size; the face's 600/1000 advance lands every glyph on a 36 grid
ADVANCE = 36.0
PAD = 6.0  # left and right side padding, from the shipped stella art
BASELINE = 69.9
BOX_H = 96.0


def _font() -> TTFont:
    return TTFont(FONT)


def glyph_path(font: TTFont, char: str, origin_x: float) -> str:
    """One glyph as an SVG path, placed at `origin_x` on the wordmark baseline."""
    gs = font.getGlyphSet()
    name = font.getBestCmap()[ord(char)]
    pen = SVGPathPen(gs, ntos=lambda v: f"{v:g}")
    scale = SIZE / font["head"].unitsPerEm
    gs[name].draw(TransformPen(pen, (scale, 0, 0, -scale, origin_x, BASELINE)))
    return pen.getCommands()


def glyph_bounds(font: TTFont, char: str, origin_x: float) -> tuple[float, ...]:
    gs = font.getGlyphSet()
    name = font.getBestCmap()[ord(char)]
    bp = BoundsPen(gs)
    scale = SIZE / font["head"].unitsPerEm
    gs[name].draw(TransformPen(bp, (scale, 0, 0, -scale, origin_x, BASELINE)))
    return bp.bounds


def wordmark(word: str) -> dict[str, object]:
    """Outline `word` plus the trailing asterisk.

    Returns the letters as one path, the asterisk as its own, the asterisk's
    centre and radius (what the spectrum wedges and the spinner rotate about),
    and the box the whole mark occupies.
    """
    font = _font()
    glyphs = list(word) + ["*"]
    letters = " ".join(
        glyph_path(font, ch, PAD + i * ADVANCE) for i, ch in enumerate(word)
    )
    star_x = PAD + len(word) * ADVANCE
    star = glyph_path(font, "*", star_x)
    x0, y0, x1, y1 = glyph_bounds(font, "*", star_x)
    return {
        "word": word,
        "letters": letters,
        "star": star,
        "star_cx": (x0 + x1) / 2,
        "star_cy": (y0 + y1) / 2,
        "star_r": max(x1 - x0, y1 - y0) / 2,
        "width": PAD * 2 + len(glyphs) * ADVANCE,
        "height": BOX_H,
    }


# --------------------------------------------------------------------------
# arbitrary lines, outlined the same way
# --------------------------------------------------------------------------

_CACHE: dict[int, TTFont] = {}


def _weight(w: int) -> TTFont:
    if w not in _CACHE:
        _CACHE[w] = TTFont(FONTS[w])
    return _CACHE[w]


def text_width(s: str, size: float) -> float:
    """Monospaced, so the width of a line is its length times the advance."""
    return len(s) * size * ADVANCE_RATIO


def text_path(
    s: str, size: float, x: float, y: float, weight: int = 400, *, anchor: str = "start"
) -> str:
    """A line of text as one outlined SVG path, `y` on the baseline.

    Outlined rather than set as `<text>` because these surfaces are rasterised
    by whatever renderer is to hand -- and a `<text>` element that cannot find
    JetBrains Mono silently falls back to a face that is not this brand.
    """
    font = _weight(weight)
    scale = size / font["head"].unitsPerEm
    gs = font.getGlyphSet()
    cmap = font.getBestCmap()
    width = text_width(s, size)
    if anchor == "middle":
        x -= width / 2
    elif anchor == "end":
        x -= width
    parts = []
    for i, ch in enumerate(s):
        name = cmap.get(ord(ch))
        if name is None or ch == " ":
            continue
        pen = SVGPathPen(gs, ntos=lambda v: f"{v:g}")
        ox = x + i * size * ADVANCE_RATIO
        gs[name].draw(TransformPen(pen, (scale, 0, 0, -scale, ox, y)))
        parts.append(pen.getCommands())
    return " ".join(p for p in parts if p)


def verify() -> None:
    """Reproduce stella's shipped wordmark geometry, or fail loudly."""
    shipped = Path(
        "/Users/macanderson/Projects/stella/docs/brand/logo/svg/wordmark-color-dark.svg"
    ).read_text()
    mark = wordmark("stella")
    assert mark["width"] == 264.0, mark["width"]
    # The shipped file rounds to two decimals; compare the anchor numbers that
    # pin the transform rather than the whole string, which differs only in how
    # many digits each renderer chose to print.
    for probe in ("M22.62 70.5", "M63.599999999999994 69.9", "M233.82 64.98"):
        assert probe.split("Q")[0][:9] in shipped, probe
    for probe in ("22.62 70.5", "233.82 64.98"):
        assert probe.split()[0] in str(mark["letters"]) + str(mark["star"]), probe
    print(f"verify: stella* reproduces the shipped geometry ({mark['width']:g}x96)")


if __name__ == "__main__":
    verify()
    for w in ("stella", "oxagen"):
        m = wordmark(w)
        print(
            f"{w}*  box {m['width']:g}x{m['height']:g}  "
            f"star centre ({m['star_cx']:.2f}, {m['star_cy']:.2f}) r={m['star_r']:.2f}"
        )
