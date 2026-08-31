"""Every finished surface: wallpapers, social art, ads, and content cards.

One composition rule holds all of them. A surface is a ground, one oversized
ghost of the star placed off-centre, and at most two lines of type. The star is
the only illustration this brand owns, so a surface that needs a picture uses a
bigger star rather than a new drawing -- and because the ghost is the same glyph
outline the logo uses, a poster and a favicon are provably the same shape.
"""

from __future__ import annotations

import math

from color import INK, PAPER, contrast
from glyphs import text_path, text_width, wordmark
from marks import (
    INK_TEXT,
    OXAGEN_RAYS,
    PAPER_TEXT,
    STELLA_RAYS,
    star_group,
    wedges,
)

_M = wordmark("stella")  # the star's home coordinates; identical in both marks
STAR_CX, STAR_CY, STAR_R = _M["star_cx"], _M["star_cy"], _M["star_r"]
STAR_SPAN = STAR_R * 2

#: Warm paper is a hair off white and the ink canvas a hair off black, so a
#: surface never reads as a browser default. Both are stella's shipped tokens.
GROUNDS = {"dark": INK, "light": PAPER}
TEXT_ON = {"dark": PAPER_TEXT, "light": INK_TEXT}
MUTED_ON = {"dark": "#777782", "light": "#605F5C"}

#: The ghost sits heavier on paper than on ink: a light ground swallows a tint
#: that a near-black one lets glow.
GHOST_ALPHA = {"dark": 0.085, "light": 0.115}


#: Process-global, not per-surface. Several of these compositions are inlined
#: into one HTML document by the playbook, and `id` is document-scoped: a
#: per-surface counter hands the second wallpaper the same clip-path id as the
#: first, and every star after it is clipped by the wrong outline.
_IDS = [0]


def _sid(_unused: object = None) -> str:
    _IDS[0] += 1
    return f"s{_IDS[0]}"


class Surface:
    """A fixed-size canvas that stacks SVG fragments in order."""

    def __init__(self, w: int, h: int, scheme: str = "dark", ground: str | None = None):
        self.w, self.h, self.scheme = w, h, scheme
        self.ground = ground or GROUNDS[scheme]
        self.text = TEXT_ON[scheme]
        self.muted = MUTED_ON[scheme]
        self.body: list[str] = []
        self.defs: list[str] = []
        self._n = [0]

    # -- pieces ---------------------------------------------------------

    def ghost(
        self,
        rays: list[str],
        cx: float,
        cy: float,
        size: float,
        *,
        rot: float = -12.0,
        alpha: float | None = None,
    ) -> "Surface":
        """An oversized star with its own light under it -- the kit's one picture.

        Deliberately not a flat tint. See `AURORA_ALPHA`: a tinted star on a
        near-black ground reads as five dull blocks, so the bloom carries the
        colour and the glyph carries the shape.
        """
        scale = 1.0 if alpha is None else alpha / GHOST_ALPHA[self.scheme]
        return aurora(
            self,
            rays,
            cx,
            cy,
            size,
            rot=rot,
            alpha=0.26 * scale,
            star_alpha=0.16 * scale,
        )

    def star(
        self, rays: list[str], cx: float, cy: float, size: float, *, rot: float = 0.0
    ) -> "Surface":
        """The star at full strength."""
        uid = _sid(self._n)
        s = size / STAR_SPAN
        d, g = star_group(_M, rays, uid)
        self.defs.append(d)
        self.body.append(
            f'<g transform="translate({cx:.2f},{cy:.2f}) rotate({rot:g}) '
            f'scale({s:.5f}) translate({-STAR_CX:.2f},{-STAR_CY:.2f})">{g}</g>'
        )
        return self

    def wordmark(
        self,
        word: str,
        rays: list[str],
        cx: float,
        cy: float,
        size: float,
        *,
        anchor: str = "middle",
        letters: str | None = None,
    ) -> "Surface":
        """A logo placed by its own centre, `size` being the box's width."""
        uid = _sid(self._n)
        m = wordmark(word)
        s = size / m["width"]
        x = cx - size / 2 if anchor == "middle" else (cx if anchor == "start" else cx - size)
        y = cy - m["height"] * s / 2
        d, g = star_group(m, rays, uid)
        self.defs.append(d)
        self.body.append(
            f'<g transform="translate({x:.2f},{y:.2f}) scale({s:.5f})">'
            f'<path d="{m["letters"]}" fill="{letters or self.text}"/>{g}</g>'
        )
        return self

    def line(
        self,
        s: str,
        x: float,
        y: float,
        size: float,
        *,
        weight: int = 400,
        fill: str | None = None,
        anchor: str = "start",
        opacity: float = 1.0,
    ) -> "Surface":
        d = text_path(s, size, x, y, weight, anchor=anchor)
        if d:
            op = f' opacity="{opacity:g}"' if opacity < 1 else ""
            self.body.append(f'<path d="{d}" fill="{fill or self.text}"{op}/>')
        return self

    def rect(self, x, y, w, h, fill, *, rx: float = 0, opacity: float = 1.0) -> "Surface":
        r = f' rx="{rx:g}"' if rx else ""
        op = f' opacity="{opacity:g}"' if opacity < 1 else ""
        self.body.append(f'<rect x="{x:g}" y="{y:g}" width="{w:g}" height="{h:g}"{r} fill="{fill}"{op}/>')
        return self

    def glow(self, cx: float, cy: float, r: float, colour: str, alpha: float) -> "Surface":
        """A soft radial lift under the ghost, so the ground is not flat."""
        uid = _sid(self._n)
        self.defs.append(
            f'<radialGradient id="g-{uid}"><stop offset="0" stop-color="{colour}" '
            f'stop-opacity="{alpha:g}"/><stop offset="1" stop-color="{colour}" '
            f'stop-opacity="0"/></radialGradient>'
        )
        self.body.append(
            f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r:.1f}" fill="url(#g-{uid})"/>'
        )
        return self

    # -- output ---------------------------------------------------------

    def svg(self) -> str:
        defs = f"<defs>{''.join(self.defs)}</defs>" if self.defs else ""
        return (
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{self.w}" '
            f'height="{self.h}" viewBox="0 0 {self.w} {self.h}">{defs}'
            f'<rect width="{self.w}" height="{self.h}" fill="{self.ground}"/>'
            f"{''.join(self.body)}</svg>"
        )


# --------------------------------------------------------------------------
# the compositions
# --------------------------------------------------------------------------


#: A star tinted down onto a near-black ground goes muddy: every ray lands
#: within a few points of the canvas and the arms read as five dull blocks. So
#: the wallpapers put the light *under* the star instead -- one soft bloom per
#: ray, at that ray's own hue and angle -- and lay the glyph over the top at a
#: fifth strength, where it now has something to be legible against.
AURORA_ALPHA = {"dark": 0.46, "light": 0.42}
AURORA_STAR = {"dark": 0.20, "light": 0.26}


def aurora(
    s: Surface,
    rays: list[str],
    cx: float,
    cy: float,
    span: float,
    *,
    rot: float = -12.0,
    alpha: float | None = None,
    star_alpha: float | None = None,
) -> Surface:
    a = AURORA_ALPHA[s.scheme] if alpha is None else alpha
    for k, col in enumerate(rays):
        ang = math.radians(-90 + 72 * k + rot)
        px, py = cx + span * 0.34 * math.cos(ang), cy + span * 0.34 * math.sin(ang)
        uid = _sid(s._n)
        s.defs.append(
            f'<radialGradient id="au-{uid}">'
            f'<stop offset="0" stop-color="{col}" stop-opacity="{a:g}"/>'
            f'<stop offset="0.45" stop-color="{col}" stop-opacity="{a * 0.34:.3f}"/>'
            f'<stop offset="1" stop-color="{col}" stop-opacity="0"/></radialGradient>'
        )
        s.body.append(
            f'<circle cx="{px:.1f}" cy="{py:.1f}" r="{span * 0.62:.1f}" '
            f'fill="url(#au-{uid})"/>'
        )
    sa = AURORA_STAR[s.scheme] if star_alpha is None else star_alpha
    uid = _sid(s._n)
    sc = span / STAR_SPAN
    d, g = star_group(_M, rays, uid)
    s.defs.append(d)
    s.body.append(
        f'<g opacity="{sa:g}" transform="translate({cx:.1f},{cy:.1f}) rotate({rot:g}) '
        f'scale({sc:.5f}) translate({-STAR_CX:.2f},{-STAR_CY:.2f})">{g}</g>'
    )
    return s


def outline(
    s: Surface, rays: list[str], cx: float, cy: float, span: float, *, rot: float = -12.0
) -> Surface:
    """The star as a hairline -- the quiet wallpaper, and the section rule."""
    sc = span / STAR_SPAN
    s.body.append(
        f'<g transform="translate({cx:.1f},{cy:.1f}) rotate({rot:g}) scale({sc:.5f}) '
        f'translate({-STAR_CX:.2f},{-STAR_CY:.2f})">'
        f'<path d="{_M["star"]}" fill="none" stroke="{rays[0]}" '
        f'stroke-width="{0.9 / sc:.4f}" opacity="0.85"/></g>'
    )
    return s


def wallpaper_desktop(w: int, h: int, rays: list[str], scheme: str, style: str = "aurora") -> str:
    """The bloom sits right of centre, leaving the icon corner clear."""
    s = Surface(w, h, scheme)
    cx, cy, span = w * 0.80, h * 0.42, h * 0.95
    return (aurora(s, rays, cx, cy, span) if style == "aurora"
            else outline(s, rays, cx, cy, span)).svg()


def wallpaper_phone(w: int, h: int, rays: list[str], scheme: str, style: str = "aurora") -> str:
    """Portrait: the star sits below the clock and above the dock."""
    s = Surface(w, h, scheme)
    cx, cy, span = w * 0.5, h * 0.52, w * 1.15
    return (aurora(s, rays, cx, cy, span) if style == "aurora"
            else outline(s, rays, cx, cy, span)).svg()


def avatar(rays: list[str], size: int, scheme: str) -> str:
    s = Surface(size, size, scheme)
    s.glow(size * 0.5, size * 0.5, size * 0.62, rays[0], 0.10 if scheme == "dark" else 0.06)
    s.star(rays, size * 0.5, size * 0.5, size * 0.56)
    return s.svg()


def banner(
    w: int,
    h: int,
    word: str,
    rays: list[str],
    scheme: str,
    *,
    tagline: str = "",
    safe_h: float | None = None,
) -> str:
    """Wordmark centred inside the platform's safe area, ghost off the right."""
    s = Surface(w, h, scheme)
    box = safe_h if safe_h is not None else h
    cy = h / 2
    # One star, mostly off-canvas. Two of them fought the wordmark for the
    # middle of the banner and the type stopped being the first thing read.
    s.ghost(rays, w * 0.97, cy, box * 1.9, rot=-12, alpha=GHOST_ALPHA[scheme] * 0.8)
    mark_w = min(w * 0.40, box * 2.4)
    s.wordmark(word, rays, w / 2, cy - (box * 0.07 if tagline else 0), mark_w)
    if tagline:
        size = box * 0.085
        s.line(tagline, w / 2, cy + box * 0.24, size, fill=s.muted, anchor="middle")
    return s.svg()


def og_card(
    w: int, h: int, word: str, rays: list[str], scheme: str, *, tagline: str
) -> str:
    s = Surface(w, h, scheme)
    s.glow(w * 0.82, h * 0.3, h * 0.9, rays[0], 0.08 if scheme == "dark" else 0.05)
    s.ghost(rays, w * 0.85, h * 0.32, h * 1.05, rot=-12)
    pad = w * 0.075
    s.wordmark(word, rays, pad, h * 0.42, w * 0.34, anchor="start")
    s.line(tagline, pad, h * 0.66, h * 0.062, weight=500, fill=s.muted)
    s.rect(pad, h * 0.78, w * 0.10, h * 0.012, rays[0], rx=h * 0.006)
    return s.svg()


def ad(
    w: int,
    h: int,
    word: str,
    rays: list[str],
    scheme: str,
    *,
    headline: list[str],
    kicker: str = "",
    cta: str = "",
) -> str:
    """Kicker, a short headline set tight, a rule in the accent, then the mark.

    Laid out from the bottom edge upward. Anchoring the headline to the top and
    hoping the call to action cleared the wordmark put the two on the same line
    at 1080x1080 and again at 1200x628 -- the square is the format where the
    headline is tallest relative to the canvas, so it is the one that collides.
    """
    s = Surface(w, h, scheme)
    short = min(w, h)
    s.glow(w * 0.9, h * 0.12, short * 1.0, rays[0], 0.09 if scheme == "dark" else 0.05)
    s.ghost(rays, w * 0.92, h * 0.10, short * 0.95, rot=-12)

    pad = w * 0.085
    mark_w = short * 0.36
    mark_h = mark_w * 96 / 264
    mark_cy = h - pad - mark_h / 2

    # Type is sized against both edges, so a wide banner is not set at a
    # square's scale with two thirds of the canvas empty -- and then shrunk
    # until the block actually fits, because a 1200x628 with three lines and a
    # kicker overruns the top edge and silently loses the kicker.
    size = min(w * 0.075, h * 0.105)
    ceiling = pad + (size * 0.035 / 0.075 * 2.2 if kicker else 0)
    for _ in range(24):
        block = (len(headline) - 1) * size * 1.32 + size * 1.9 + (size * 0.85 if cta else 0)
        if mark_cy - mark_h / 2 - size * 0.9 - block >= ceiling:
            break
        size *= 0.94
    lead = size * 1.32

    s.wordmark(word, rays, pad, mark_cy, mark_w, anchor="start")
    y = mark_cy - mark_h / 2 - size * 0.9
    if cta:
        s.line(cta, pad, y, size * 0.46, weight=500, fill=s.muted)
        y -= size * 0.85
    rule_h = max(3.0, short * 0.011)
    s.rect(pad, y - rule_h, short * 0.13, rule_h, rays[0], rx=rule_h / 2)
    y -= rule_h + size * 0.95

    for i, ln in enumerate(reversed(headline)):
        s.line(ln, pad, y - i * lead, size, weight=800)
    top = y - (len(headline) - 1) * lead
    if kicker:
        s.line(kicker.upper(), pad, top - lead * 0.95, short * 0.035, weight=700,
               fill=rays[0])
    return s.svg()


def content_card(
    w: int,
    h: int,
    word: str,
    rays: list[str],
    scheme: str,
    *,
    kind: str,
    title: list[str],
    meta: str = "",
    body: list[str] | None = None,
) -> str:
    """The publishing template: one kind chip, one title, optional monospace body."""
    s = Surface(w, h, scheme)
    short = min(w, h)
    s.ghost(rays, w * 0.95, h * 0.08, short * 0.85, rot=-12)
    pad = w * 0.062
    chip_h = short * 0.062
    chip_w = text_width(kind.upper(), short * 0.030) + chip_h * 1.1
    s.rect(pad, pad, chip_w, chip_h, rays[0], rx=chip_h / 2)
    s.line(
        kind.upper(),
        pad + chip_w / 2,
        pad + chip_h * 0.66,
        short * 0.030,
        weight=700,
        fill=INK,
        anchor="middle",
    )
    size = short * 0.078
    lead = size * 1.32
    top = pad + chip_h + short * 0.14
    for i, ln in enumerate(title):
        s.line(ln, pad, top + i * lead, size, weight=800)
    y = top + len(title) * lead + short * 0.03
    if body:
        panel_h = short * 0.055 * len(body) + short * 0.06
        s.rect(pad, y, w - pad * 2, panel_h, s.text, rx=short * 0.02, opacity=0.05)
        for i, ln in enumerate(body):
            s.line(
                ln,
                pad + short * 0.05,
                y + short * 0.075 + i * short * 0.055,
                short * 0.036,
                fill=s.muted,
            )
        y += panel_h
    if meta:
        s.line(meta, pad, h - pad, short * 0.034, weight=500, fill=s.muted)
    s.wordmark(word, rays, w - pad, h - pad - short * 0.022, short * 0.30, anchor="end")
    return s.svg()


BRAND_RAYS = {"stella": STELLA_RAYS, "oxagen": OXAGEN_RAYS}
