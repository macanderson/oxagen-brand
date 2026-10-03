"""The GitHub badges: status pills, shields, and the commit tombstone.

Every word is outlined to paths, so GitHub needs no font to draw a badge. A
wordmark label (`oxagen`, `stella*`) is the wordmark: the wordmark face at the
logo weight, with its accent glyph in gold. Every other word is in the text
face, Geist, because the text face sets every line of text and Space Grotesk
sets the wordmarks (Mac, 2026-09-29, 2026-10-02, and 2026-10-03). Colours come
from `color.py`, so a change to `theme/theme.json` moves every badge on the
next build.

Gold appears only as the accent glyph of a wordmark label. It never encodes a
state. The state is the shape: a filled square is verified, a hollow square is
proving, and a struck square is refuted.

`build/build.py` writes these files into `github-badges/` as its `badges` step.
`build/build.py --check` fails when a file there differs from what this module
draws. brand.oxagen.cloud serves them at `/github-badges/<file>`, which is the
public URL a pull request description links.
"""

from __future__ import annotations

import color as C
import glyphs as G
from marks import BRANDS

#: The status pills: the shape of the square, and the word beside it.
STATES = {
    "verified": ("filled", "Verified"),
    "proving": ("hollow", "Proving"),
    "refuted": ("struck", "Refuted"),
}

#: The shields, by file name: the label on ink, and the value on paper.
#: `oxagen` and `stella*` are wordmarks, so they keep their gold accent.
SHIELDS = {
    "shield-oxagen-verified.svg": ("oxagen", "verified"),
    # A pull request that a wrapped agent opened during a run Oxagen recorded.
    # The steering repo spec's Pull request badges section names it.
    "shield-oxagen-agent-run.svg": ("oxagen", "agent run"),
    "shield-stella-proven.svg": ("stella*", "proven"),
    "shield-receipt-proven.svg": ("receipt", "proven"),
}

#: The wordmark each shield label may be, and the glyph that takes the gold.
_WORDMARKS = {str(b["text"]): str(b["accent"]) for b in BRANDS.values()}


def svg(w: float, h: float, body: str, label: str) -> str:
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w:g} {h:g}" width="{w:g}" height="{h:g}" '
        f'role="img" aria-label="{label}">{body}</svg>\n'
    )


def words(text: str, size: float, x: float, y: float, weight: int, *, face: str = "text",
          accent: str = "") -> tuple[str, str, float]:
    """`text` on the baseline at (x, y) as two paths, plain and accent, and its advance.

    `accent` names the one character that takes the gold. The advance lets the
    caller size the badge around the words.
    """
    glyphs = G.set_line(text, x, y, size, weight, face=face)
    plain = " ".join(str(g["path"]) for g in glyphs if g["path"] and not (accent and g["char"] == accent))
    metal = " ".join(str(g["path"]) for g in glyphs if g["path"] and accent and g["char"] == accent)
    return plain, metal, G.text_width(text, size, weight, face)


# --------------------------------------------------------------------------
# status pills: 22 px, a square that says the state, a word beside it
# --------------------------------------------------------------------------


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
    ground, border = (C.PANEL, C.BORDER) if dark else (C.PAPER_PANEL, C.PAPER_BORDER)
    strong, quiet = (C.PAPER_TEXT, C.MUTED) if dark else (C.INK_TEXT, C.MUTED_INK)
    color = strong if kind == "filled" else quiet
    h, size, pad, gap = 22.0, 9.0, 8.0, 6.0
    text, _, adv = words(word, 11.5, pad + size + gap, 15.2, 500)
    w = round(pad + size + gap + adv + pad)
    body = (
        f'<rect x="0.5" y="0.5" width="{w - 1:g}" height="{h - 1:g}" rx="{(h - 1) / 2:g}" '
        f'fill="{ground}" stroke="{border}"/>'
        + square(kind, pad, (h - size) / 2, size, color)
        + f'<path fill="{color}" d="{text}"/>'
    )
    return svg(w, h, body, word)


# --------------------------------------------------------------------------
# shields: 20 px, the label on ink at the left, the value on paper at the right
# --------------------------------------------------------------------------


def shield(label: str, value: str) -> str:
    h, pad, size, baseline = 20.0, 7.0, 11.0, 14.2
    accent = _WORDMARKS.get(label)
    if accent is None:
        lp, lg, la = words(label, size, pad, baseline, 600)
    else:
        lp, lg, la = words(label, size, pad, baseline, G.LOGO_WEIGHT, face="wordmark", accent=accent)
    lw = round(pad + la + pad)
    vp, _, va = words(value, size, lw + pad, baseline, 500)
    w = round(lw + pad + va + pad)
    body = (
        f'<clipPath id="r"><rect width="{w:g}" height="{h:g}" rx="3"/></clipPath>'
        f'<g clip-path="url(#r)"><rect width="{lw:g}" height="{h:g}" fill="{C.INK}"/>'
        f'<rect x="{lw:g}" width="{w - lw:g}" height="{h:g}" fill="{C.PAPER}"/></g>'
        f'<path fill="{C.PAPER_TEXT}" d="{lp}"/>'
        + (f'<path fill="{C.GOLD}" d="{lg}"/>' if lg else "")
        + f'<path fill="{C.INK_TEXT}" d="{vp}"/>'
    )
    return svg(w, h, body, f"{label}: {value}")


# --------------------------------------------------------------------------
# the commit tombstone: 16 px, one filled square, the colour of the surface
# --------------------------------------------------------------------------


def tombstone(scheme: str) -> str:
    color = C.PAPER_TEXT if scheme == "dark" else C.INK_TEXT
    return svg(16, 16, square("filled", 3.5, 3.5, 9, color), "verified")


def files() -> dict[str, str]:
    """Every badge, by its file name under `github-badges/`."""
    out: dict[str, str] = {}
    for state in STATES:
        for scheme in ("dark", "light"):
            out[f"badge-{state}-{scheme}.svg"] = pill(state, scheme)
    for name, (label, value) in SHIELDS.items():
        out[name] = shield(label, value)
    for scheme in ("dark", "light"):
        out[f"commit-tombstone-{scheme}.svg"] = tombstone(scheme)
    return out
