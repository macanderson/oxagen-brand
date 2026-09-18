"""Generate the GitHub badges in the house system.

Every badge is Space Grotesk outlined to paths, so nothing depends on a font
being installed where GitHub renders it. Colours are the house tokens from
`../tokens/house-tokens.json`. Gold appears once, as the brand glyph in
the `oxagen` label; it never encodes a state. State is carried by shape: a
filled square is verified, a hollow square is proving, a struck square is
refuted.

    python3 -m venv .venv && .venv/bin/pip install fonttools brotli
    brew install harfbuzz                     # hb-shape
    .venv/bin/python build.py                 # writes every badge beside this file
"""

from __future__ import annotations

import json
import shutil
import subprocess
import tempfile
from pathlib import Path

from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import TTFont

HERE = Path(__file__).resolve().parent
BRAND = HERE.parent  # the kit root: fonts/ and tokens/ sit beside github-badges/
TOKENS = json.loads((BRAND / "tokens" / "house-tokens.json").read_text())["tokens"]

INK, PAPER = TOKENS["ink"], TOKENS["paper"]
PANEL, PAPER_PANEL = TOKENS["panel"], TOKENS["paper-panel"]
BORDER, PAPER_BORDER = TOKENS["border"], TOKENS["paper-border"]
TEXT, TEXT_INK = TOKENS["text"], TOKENS["text-ink"]
MUTED, MUTED_INK = TOKENS["muted"], TOKENS["muted-ink"]
GOLD = TOKENS["gold"]

_FONTS: dict[int, TTFont] = {}
_TTF: dict[int, Path] = {}
_TMP = Path(tempfile.mkdtemp(prefix="ox-badges-"))


def font(weight: int) -> TTFont:
    """The static woff2 the skill ships, decoded once per weight."""
    if weight not in _FONTS:
        f = TTFont(BRAND / "fonts" / f"space-grotesk-latin-{weight}.woff2")
        f.flavor = None
        p = _TMP / f"sg-{weight}.ttf"
        f.save(p)
        _FONTS[weight], _TTF[weight] = TTFont(p), p
    return _FONTS[weight]


def shape(text: str, weight: int) -> list[tuple[str, float, float, float]]:
    """(glyph name, x advance, x offset, y offset) per glyph, kerned by HarfBuzz."""
    if not shutil.which("hb-shape"):
        raise SystemExit("hb-shape not found: `brew install harfbuzz`")
    font(weight)
    out = subprocess.run(
        ["hb-shape", "--font-file", str(_TTF[weight]), "--output-format=json", "--no-clusters", "--no-glyph-names", text],
        capture_output=True, text=True, check=True,
    ).stdout
    order = font(weight).getGlyphOrder()  # the subset webfonts carry no glyph names; map ids
    return [(order[g["g"]], g["ax"], g.get("dx", 0), g.get("dy", 0)) for g in json.loads(out)]


def text_path(text: str, size: float, x: float, y: float, weight: int, *, gold: str = "") -> tuple[str, str, float]:
    """`text` on the baseline at (x, y) as two path strings: plain and gold.

    `gold` names the one character that takes the metal. Returns the advance
    width too, so the caller can size the badge around the words.
    """
    f = font(weight)
    s = size / f["head"].unitsPerEm
    gs = f.getGlyphSet()
    cmap = f.getBestCmap()
    gold_glyph = cmap[ord(gold)] if gold else None
    plain, metal, cx = [], [], x
    for name, ax, dx, dy in shape(text, weight):
        pen = SVGPathPen(gs, ntos=lambda v: f"{v:.2f}")
        gs[name].draw(TransformPen(pen, (s, 0, 0, -s, cx + dx * s, y - dy * s)))
        (metal if name == gold_glyph else plain).append(pen.getCommands())
        cx += ax * s
    return " ".join(plain), " ".join(metal), cx - x


def svg(w: float, h: float, body: str, label: str) -> str:
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w:g} {h:g}" width="{w:g}" height="{h:g}" '
        f'role="img" aria-label="{label}">{body}</svg>\n'
    )


# --------------------------------------------------------------------------
# status pills: 22 px, a square that says the state, a word beside it
# --------------------------------------------------------------------------

STATES = {
    "verified": ("filled", "Verified"),
    "proving": ("hollow", "Proving"),
    "refuted": ("struck", "Refuted"),
}


def square(kind: str, x: float, y: float, size: float, color: str) -> str:
    r = size * 0.16
    if kind == "filled":
        return f'<rect x="{x:g}" y="{y:g}" width="{size:g}" height="{size:g}" rx="{r:.2f}" fill="{color}"/>'
    box = (
        f'<rect x="{x + 0.6:.2f}" y="{y + 0.6:.2f}" width="{size - 1.2:.2f}" height="{size - 1.2:.2f}" '
        f'rx="{r:.2f}" fill="none" stroke="{color}" stroke-width="1.2"/>'
    )
    if kind == "hollow":
        return box
    return box + (
        f'<path d="M{x + 1.6:.2f} {y + size - 1.6:.2f}L{x + size - 1.6:.2f} {y + 1.6:.2f}" '
        f'stroke="{color}" stroke-width="1.2" stroke-linecap="round"/>'
    )


def pill(state: str, scheme: str) -> str:
    kind, word = STATES[state]
    dark = scheme == "dark"
    ground, border = (PANEL, BORDER) if dark else (PAPER_PANEL, PAPER_BORDER)
    strong, quiet = (TEXT, MUTED) if dark else (TEXT_INK, MUTED_INK)
    color = strong if kind == "filled" else quiet
    h, size, pad, gap = 22.0, 9.0, 8.0, 6.0
    text, _, adv = text_path(word, 11.5, pad + size + gap, 15.2, 500)
    w = round(pad + size + gap + adv + pad)
    body = (
        f'<rect x="0.5" y="0.5" width="{w - 1:g}" height="{h - 1:g}" rx="{(h - 1) / 2:g}" '
        f'fill="{ground}" stroke="{border}"/>'
        + square(kind, pad, (h - size) / 2, size, color)
        + f'<path fill="{color}" d="{text}"/>'
    )
    return svg(w, h, body, f"{word}")


# --------------------------------------------------------------------------
# shields: 20 px, ink label on the left, paper value on the right
# --------------------------------------------------------------------------


def shield(label: str, value: str, *, gold: str = "") -> str:
    h, pad = 20.0, 7.0
    lp, lg, la = text_path(label, 11.0, pad, 14.2, 600, gold=gold)
    lw = round(pad + la + pad)
    vp, _, va = text_path(value, 11.0, lw + pad, 14.2, 500)
    w = round(lw + pad + va + pad)
    body = (
        f'<clipPath id="r"><rect width="{w:g}" height="{h:g}" rx="3"/></clipPath>'
        f'<g clip-path="url(#r)"><rect width="{lw:g}" height="{h:g}" fill="{INK}"/>'
        f'<rect x="{lw:g}" width="{w - lw:g}" height="{h:g}" fill="{PAPER}"/></g>'
        f'<path fill="{TEXT}" d="{lp}"/>'
        + (f'<path fill="{GOLD}" d="{lg}"/>' if lg else "")
        + f'<path fill="{TEXT_INK}" d="{vp}"/>'
    )
    return svg(w, h, body, f"{label}: {value}")


# --------------------------------------------------------------------------
# the commit tombstone: 16 px, one filled square, the colour of the surface
# --------------------------------------------------------------------------


def tombstone(scheme: str) -> str:
    color = TEXT if scheme == "dark" else TEXT_INK
    return svg(16, 16, square("filled", 3.5, 3.5, 9, color), "verified")


def main() -> None:
    files = {}
    for state in STATES:
        for scheme in ("dark", "light"):
            files[f"badge-{state}-{scheme}.svg"] = pill(state, scheme)
    files["shield-oxagen-verified.svg"] = shield("oxagen", "verified", gold="x")
    files["shield-stella-proven.svg"] = shield("stella*", "proven", gold="*")
    files["shield-receipt-proven.svg"] = shield("receipt", "proven")
    for scheme in ("dark", "light"):
        files[f"commit-tombstone-{scheme}.svg"] = tombstone(scheme)
    for name, body in files.items():
        (HERE / name).write_text(body)
        print(name)


if __name__ == "__main__":
    main()
