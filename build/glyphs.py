"""Outline the house type straight out of Space Grotesk.

Every logo in this kit is a string set in one face, at one size, and then
outlined, so the logos never depend on a font being installed and can never
drift apart from each other. The face is the variable Space Grotesk vendored in
`fonts/`, instanced to a fixed weight at build time.

Two things are borrowed from the Oxagen brand kit this system is built to
match, and `verify()` checks both against the kit's own `wordmark-color-light`:

- the em. The kit set `oxagen` at Space Grotesk 600 and scaled the ink box to
  96 tall, which puts the em at 96 x 96/70. Both wordmarks use that em, so
  `stella*` and `oxagen` are the same size when they are the same height.
- the spacing. Words are shaped with HarfBuzz, the engine the kit used, so the
  kerning pairs in the font are honoured. Summing raw advances is not the same
  wordmark.
"""

from __future__ import annotations

import json
import shutil
import subprocess
from functools import lru_cache
from pathlib import Path

from fontTools.pens.boundsPen import BoundsPen
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import TTFont
from fontTools.varLib import instancer

ROOT = Path(__file__).resolve().parent.parent
FONT = ROOT / "fonts" / "SpaceGrotesk-VariableFont_wght.ttf"
REFERENCE = ROOT / "build" / "reference" / "oxagen-wordmark-color-light.svg"

WEIGHTS = (400, 500, 600, 700)
LOGO_WEIGHT = 600  # the wordmark weight, as the kit ships it

#: The kit rendered at 96 px and its ink box came out 70 tall; scaling that box
#: to 96 is a 96/70 lift. This is the em every wordmark is set at.
EM = 96.0 * 96.0 / 70.0

_FONTS: dict[int, TTFont] = {}


def font(weight: int = LOGO_WEIGHT) -> TTFont:
    """One static instance of the variable font per weight, cached."""
    if weight not in _FONTS:
        if weight not in WEIGHTS:
            raise ValueError(f"weight {weight} is not one of {WEIGHTS}")
        _FONTS[weight] = instancer.instantiateVariableFont(
            TTFont(FONT), {"wght": weight}, inplace=False
        )
    return _FONTS[weight]


def _upm(f: TTFont) -> float:
    return float(f["head"].unitsPerEm)


# --------------------------------------------------------------------------
# shaping
# --------------------------------------------------------------------------


@lru_cache(maxsize=None)
def shape(text: str, weight: int = LOGO_WEIGHT) -> tuple[tuple[str, float, float, float, int], ...]:
    """`text` through HarfBuzz: (glyph name, x advance, x offset, y offset, cluster).

    HarfBuzz is what the reference kit's outlines came from, so this is the
    only way to reproduce their spacing. `hb-shape` ships with harfbuzz
    (`brew install harfbuzz`). The cluster is the index of the character a
    glyph came from; the face has an `fi` ligature, so glyphs and characters
    do not line up one to one and must be matched through it.
    """
    if not shutil.which("hb-shape"):
        raise SystemExit("hb-shape not found: `brew install harfbuzz`")
    out = subprocess.run(
        [
            "hb-shape",
            str(FONT),
            f"--variations=wght={weight}",
            f"--text={text}",
            "--output-format=json",
        ],
        check=True,
        capture_output=True,
        text=True,
    ).stdout
    return tuple(
        (g["g"], float(g["ax"]), float(g["dx"]), float(g["dy"]), int(g["cl"])) for g in json.loads(out)
    )


# --------------------------------------------------------------------------
# outlines
# --------------------------------------------------------------------------


def _draw(f: TTFont, name: str, x: float, y: float, size: float) -> tuple[str, tuple | None]:
    gs = f.getGlyphSet()
    s = size / _upm(f)
    pen = SVGPathPen(gs, ntos=lambda v: f"{v:g}")
    gs[name].draw(TransformPen(pen, (s, 0, 0, -s, x, y)))
    bp = BoundsPen(gs)
    gs[name].draw(TransformPen(bp, (s, 0, 0, -s, x, y)))
    b = bp.bounds
    if b is None:
        return "", None
    return pen.getCommands(), (b[0], b[1], b[2], b[3])


def set_line(
    text: str, x: float = 0.0, y: float = 0.0, size: float = EM, weight: int = LOGO_WEIGHT
) -> list[dict[str, object]]:
    """Every glyph of `text` on one baseline at (`x`, `y`), left to right, kerned.

    One record per glyph: the character(s) it came from, its glyph name, path,
    origin, advance and ink bounds (None for anything with no contour, such as
    a space). A ligature is one record whose `char` is both letters.
    """
    f = font(weight)
    s = size / _upm(f)
    glyphs = shape(text, weight)
    out = []
    cx = x
    for i, (name, ax, dx, dy, cl) in enumerate(glyphs):
        end = glyphs[i + 1][4] if i + 1 < len(glyphs) else len(text)
        path, bounds = _draw(f, name, cx + dx * s, y - dy * s, size)
        out.append(
            {"char": text[cl:end], "glyph": name, "x": cx, "advance": ax * s, "path": path, "bounds": bounds}
        )
        cx += ax * s
    return out


def union_bounds(recs: list[dict[str, object]]) -> tuple[float, float, float, float]:
    bs = [r["bounds"] for r in recs if r["bounds"]]
    return (
        min(b[0] for b in bs),  # type: ignore[index]
        min(b[1] for b in bs),  # type: ignore[index]
        max(b[2] for b in bs),  # type: ignore[index]
        max(b[3] for b in bs),  # type: ignore[index]
    )


def text_width(s: str, size: float, weight: int = 400) -> float:
    f = font(weight)
    return sum(g[1] for g in shape(s, weight)) * size / _upm(f)


def text_path(
    s: str, size: float, x: float, y: float, weight: int = 400, *, anchor: str = "start"
) -> str:
    """A line of text as one outlined SVG path, `y` on the baseline.

    Outlined rather than set as `<text>`, because these surfaces are rasterised
    by whatever renderer is to hand, and a `<text>` element that cannot find
    Space Grotesk silently falls back to a face that is not this brand.
    """
    width = text_width(s, size, weight)
    if anchor == "middle":
        x -= width / 2
    elif anchor == "end":
        x -= width
    return " ".join(str(r["path"]) for r in set_line(s, x, y, size, weight) if r["path"])


# --------------------------------------------------------------------------
# the wordmark box
# --------------------------------------------------------------------------


def wordmark(text: str) -> dict[str, object]:
    """`text` at the logo em in an ink-tight box, the way the kit boxes `oxagen`.

    The box hugs the ink: its top is the tallest glyph's top, its bottom the
    lowest overshoot or descender, its sides the first and last glyph's ink.
    So `oxagen` (x-height letters and one descender) comes out 96 tall, and
    `stella*` (ascenders, no descender) a hair under -- at the same em.
    """
    x0, y0, x1, y1 = union_bounds(set_line(text))
    dx, dy = -x0, -y0
    shifted = set_line(text, dx, dy)  # re-drawn with the shift, so paths are absolute
    return {
        "text": text,
        "glyphs": shifted,
        "width": round(x1 - x0, 3),
        "height": round(y1 - y0, 3),
        "baseline": round(dy, 3),
        "em": EM,
    }


def glyph_paths(m: dict[str, object], accent: set[str]) -> tuple[str, str]:
    """The wordmark as two paths: the plain letters, and the accent glyph(s)."""
    plain = " ".join(str(g["path"]) for g in m["glyphs"] if g["path"] and g["char"] not in accent)  # type: ignore[index]
    gold = " ".join(str(g["path"]) for g in m["glyphs"] if g["path"] and g["char"] in accent)  # type: ignore[index]
    return plain, gold


# --------------------------------------------------------------------------
# verification against the reference kit
# --------------------------------------------------------------------------


def verify() -> list[str]:
    """Reproduce the kit's `oxagen` wordmark, or say exactly how it differs.

    Compares the box, the glyph-to-glyph spacing and the ink height against
    the kit's shipped `wordmark-color-light.svg`. The kit's box has a little
    slack from how its renderer rounded glyph extents, so the box is held to a
    small tolerance and the spacing to a tight one.
    """
    import re

    problems: list[str] = []
    if not REFERENCE.exists():
        return [f"reference wordmark missing: {REFERENCE}"]
    src = REFERENCE.read_text()
    ref_w = float(re.search(r'width="([\d.]+)"', src).group(1))  # type: ignore[union-attr]
    ref_h = float(re.search(r'height="([\d.]+)"', src).group(1))  # type: ignore[union-attr]
    scale = float(re.search(r"scale\(([\d.]+)\)", src).group(1))  # type: ignore[union-attr]
    origins = [
        float(x) * scale
        for x in re.findall(r'data-letter="\w" data-glyph="\d" transform="translate\((-?[\d.]+) ', src)
    ]
    m = wordmark("oxagen")
    ours = [float(g["x"]) for g in m["glyphs"]]  # type: ignore[arg-type]
    if abs(m["height"] - ref_h) > 3.0:  # type: ignore[operator]
        problems.append(f"oxagen box height {m['height']} vs reference {ref_h}")
    if abs(m["width"] - ref_w) > 6.0:  # type: ignore[operator]
        problems.append(f"oxagen box width {m['width']} vs reference {ref_w}")
    ref_gaps = [b - a for a, b in zip(origins, origins[1:])]
    our_gaps = [b - a for a, b in zip(ours, ours[1:])]
    for i, (rg, og) in enumerate(zip(ref_gaps, our_gaps)):
        if abs(rg - og) > 0.05:
            problems.append(f"advance {'oxagen'[i]}->{'oxagen'[i + 1]}: {og:.3f} vs reference {rg:.3f}")
    if not re.search(r'<path data-letter="x"[^>]*fill="#C58A32"', src):
        problems.append("reference no longer paints the x in gold; the rule this kit follows has moved")
    return problems


if __name__ == "__main__":
    for word in ("oxagen", "stella*"):
        m = wordmark(word)
        print(f"{word:8} box {m['width']:g} x {m['height']:g}  baseline {m['baseline']:g}  em {EM:.3f}")
    print("problems:", verify() or "none")
