"""Every finished surface: wallpapers, social art, ads, and content cards.

One composition rule holds all of them. A surface is a ground, one warm bloom
of the metal, one oversized ghost of the brand's own icon placed off-centre,
and at most a few lines of type. The icon is the only picture either brand
owns, so a surface that needs an image uses a bigger icon rather than a new
drawing -- and because the ghost is the same geometry the logo uses, a poster
and a favicon are provably the same shape.
"""

from __future__ import annotations

from color import (
    BORDER_ON,
    GOLD,
    GOLD_BRIGHT,
    GOLD_TEXT_ON,
    GROUNDS,
    INK,
    MUTED_ON,
    TEXT_ON,
)
from glyphs import glyph_paths, text_path, text_width, wordmark
from marks import BRANDS, icon_body, icon_geometry, ox_outline, sheen_defs

#: Process-global, not per-surface. Several of these compositions are inlined
#: into one HTML document by the playbook, and `id` is document-scoped: a
#: per-surface counter would hand the second wallpaper the same gradient id as
#: the first, and every bloom after it would take the wrong colour.
_IDS = [0]


def _sid() -> str:
    _IDS[0] += 1
    return f"s{_IDS[0]}"


def _mark(brand: str) -> dict[str, object]:
    return wordmark(str(BRANDS[brand]["text"]))


class Surface:
    """A fixed-size canvas that stacks SVG fragments in order."""

    def __init__(self, w: int, h: int, scheme: str = "dark", ground: str | None = None):
        self.w, self.h, self.scheme = w, h, scheme
        self.ground = ground or GROUNDS[scheme]
        self.text = TEXT_ON[scheme]
        self.muted = MUTED_ON[scheme]
        self.gold_text = GOLD_TEXT_ON[scheme]
        self.border = BORDER_ON[scheme]
        self.body: list[str] = []
        self.defs: list[str] = []

    # -- pieces ---------------------------------------------------------

    def glow(self, cx: float, cy: float, r: float, alpha: float, colour: str = GOLD) -> "Surface":
        """A soft radial lift of the metal under the ghost, so the ground is not flat."""
        uid = _sid()
        self.defs.append(
            f'<radialGradient id="g-{uid}"><stop offset="0" stop-color="{colour}" '
            f'stop-opacity="{alpha:g}"/><stop offset="0.5" stop-color="{colour}" '
            f'stop-opacity="{alpha * 0.35:.3f}"/><stop offset="1" stop-color="{colour}" '
            f'stop-opacity="0"/></radialGradient>'
        )
        self.body.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r:.1f}" fill="url(#g-{uid})"/>')
        return self

    def _placed(self, brand: str, cx: float, cy: float, span: float, rot: float) -> tuple[str, float]:
        g = icon_geometry(brand)
        s = span / max(float(g["w"]), float(g["h"]))  # type: ignore[arg-type]
        return (
            f'transform="translate({cx:.2f},{cy:.2f}) rotate({rot:g}) scale({s:.5f}) '
            f'translate({-float(g["cx"]):.3f},{-float(g["cy"]):.3f})"',  # type: ignore[arg-type]
            s,
        )

    def ghost(
        self, brand: str, cx: float, cy: float, span: float, *, rot: float = 0.0, alpha: float | None = None
    ) -> "Surface":
        """The icon, oversized, in the metal, at a fifth strength over its own bloom."""
        a = (0.16 if self.scheme == "dark" else 0.20) if alpha is None else alpha
        self.glow(cx, cy, span * 0.95, 0.42 if self.scheme == "dark" else 0.34)
        t, _ = self._placed(brand, cx, cy, span, rot)
        uid = _sid()
        self.defs.append(sheen_defs(uid))
        fill = f"url(#sheen-{uid})"
        self.body.append(
            f'<g opacity="{a:g}" {t}>{icon_body(brand, letters=fill, accent=fill)}</g>'
        )
        return self

    def outline(self, brand: str, cx: float, cy: float, span: float, *, rot: float = 0.0) -> "Surface":
        """The icon as a hairline in the metal: the quiet wallpaper."""
        t, s = self._placed(brand, cx, cy, span, rot)
        g = icon_geometry(brand)
        hair = max(1.6, min(self.w, self.h) * 0.0012)  # a hairline, but one that survives a thumbnail
        if g["kind"] == "asterisk":
            inner = f'<path d="{g["path"]}" fill="none" stroke="{GOLD}" stroke-width="{hair / s:.4f}"/>'
        else:
            inner = ox_outline(GOLD, hair / s)
        self.body.append(f'<g opacity="0.85" {t}>{inner}</g>')
        return self

    def icon(self, brand: str, cx: float, cy: float, span: float, *, sheen: bool = True) -> "Surface":
        """The icon at full strength."""
        t, _ = self._placed(brand, cx, cy, span, 0.0)
        accent = GOLD
        if sheen:
            uid = _sid()
            self.defs.append(sheen_defs(uid))
            accent = f"url(#sheen-{uid})"
        self.body.append(f"<g {t}>{icon_body(brand, letters=self.text, accent=accent)}</g>")
        return self

    def wordmark(
        self,
        brand: str,
        cx: float,
        cy: float,
        width: float,
        *,
        anchor: str = "middle",
        letters: str | None = None,
    ) -> "Surface":
        """A logo placed by its own centre, `width` being the box's width."""
        m = _mark(brand)
        plain, gold = glyph_paths(m, {str(BRANDS[brand]["accent"])})
        s = width / float(m["width"])  # type: ignore[arg-type]
        x = cx - width / 2 if anchor == "middle" else (cx if anchor == "start" else cx - width)
        y = cy - float(m["height"]) * s / 2  # type: ignore[arg-type]
        self.body.append(
            f'<g transform="translate({x:.2f},{y:.2f}) scale({s:.5f})">'
            f'<path d="{plain}" fill="{letters or self.text}"/><path d="{gold}" fill="{GOLD}"/></g>'
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
        self.body.append(
            f'<rect x="{x:.2f}" y="{y:.2f}" width="{w:.2f}" height="{h:.2f}"{r} fill="{fill}"{op}/>'
        )
        return self

    def rule(self, x: float, y: float, w: float, h: float) -> "Surface":
        """A short bar of the metal: the one accent a surface gets besides the mark."""
        uid = _sid()
        self.defs.append(sheen_defs(uid))
        return self.rect(x, y, w, h, f"url(#sheen-{uid})", rx=h / 2)

    # -- output ---------------------------------------------------------

    def svg(self) -> str:
        defs = f"<defs>{''.join(self.defs)}</defs>" if self.defs else ""
        return (
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{self.w}" '
            f'height="{self.h}" viewBox="0 0 {self.w} {self.h}">{defs}'
            f'<rect width="{self.w}" height="{self.h}" fill="{self.ground}"/>'
            f"{''.join(self.body)}</svg>"
        )


def mark_aspect(brand: str) -> float:
    m = _mark(brand)
    return float(m["height"]) / float(m["width"])  # type: ignore[arg-type]


# --------------------------------------------------------------------------
# the compositions
# --------------------------------------------------------------------------

GHOST_ROT = {"stella": -15.0, "oxagen": 0.0}


def wallpaper_desktop(w: int, h: int, brand: str, scheme: str, style: str = "glow") -> str:
    """The bloom sits right of centre, leaving the icon corner clear."""
    s = Surface(w, h, scheme)
    cx, cy, span = w * 0.78, h * 0.46, h * 0.82
    if style == "glow":
        s.ghost(brand, cx, cy, span, rot=GHOST_ROT[brand])
    else:
        s.outline(brand, cx, cy, span, rot=GHOST_ROT[brand])
    return s.svg()


def wallpaper_phone(w: int, h: int, brand: str, scheme: str, style: str = "glow") -> str:
    """Portrait: the icon sits below the clock and above the dock."""
    s = Surface(w, h, scheme)
    cx, cy, span = w * 0.5, h * 0.50, w * 0.92
    if style == "glow":
        s.ghost(brand, cx, cy, span, rot=GHOST_ROT[brand])
    else:
        s.outline(brand, cx, cy, span, rot=GHOST_ROT[brand])
    return s.svg()


def avatar(brand: str, size: int, scheme: str) -> str:
    s = Surface(size, size, scheme)
    s.glow(size * 0.5, size * 0.5, size * 0.6, 0.14 if scheme == "dark" else 0.08)
    s.icon(brand, size * 0.5, size * 0.5, size * (0.58 if brand == "stella" else 0.68))
    return s.svg()


def banner(
    w: int, h: int, brand: str, scheme: str, *, tagline: str = "", safe_h: float | None = None
) -> str:
    """Wordmark centred inside the platform's safe area, the ghost off the right."""
    s = Surface(w, h, scheme)
    box = safe_h if safe_h is not None else h
    cy = h / 2
    s.ghost(brand, w * 0.94, cy, box * 1.5, rot=GHOST_ROT[brand], alpha=0.12 if scheme == "dark" else 0.16)
    mark_w = min(w * 0.36, box * 2.2)
    s.wordmark(brand, w / 2, cy - (box * 0.08 if tagline else 0), mark_w)
    if tagline:
        s.line(tagline, w / 2, cy + box * 0.26, box * 0.08, weight=500, fill=s.muted, anchor="middle")
    return s.svg()


def og_card(w: int, h: int, brand: str, scheme: str, *, tagline: str) -> str:
    s = Surface(w, h, scheme)
    s.ghost(brand, w * 0.84, h * 0.36, h * 0.95, rot=GHOST_ROT[brand])
    pad = w * 0.075
    s.wordmark(brand, pad, h * 0.42, w * 0.36, anchor="start")
    s.line(tagline, pad, h * 0.66, h * 0.062, weight=500, fill=s.muted)
    s.rule(pad, h * 0.78, w * 0.10, h * 0.012)
    return s.svg()


def ad(
    w: int, h: int, brand: str, scheme: str, *, headline: list[str], kicker: str = "", cta: str = ""
) -> str:
    """Kicker, a short headline set tight, a rule in the metal, then the mark.

    Laid out from the bottom edge upward so the call to action can never land
    on the wordmark, and the type is shrunk until the block fits under the
    kicker -- the square is where the headline is tallest against the canvas.
    """
    s = Surface(w, h, scheme)
    short = min(w, h)
    s.ghost(brand, w * 0.90, h * 0.12, short * 0.8, rot=GHOST_ROT[brand])

    pad = w * 0.085
    mark_w = short * 0.40
    mark_h = mark_w * mark_aspect(brand)
    mark_cy = h - pad - mark_h / 2

    size = min(w * 0.075, h * 0.105)
    ceiling = pad + (size * 0.035 / 0.075 * 2.2 if kicker else 0)
    for _ in range(24):
        block = (len(headline) - 1) * size * 1.22 + size * 1.9 + (size * 0.85 if cta else 0)
        if mark_cy - mark_h / 2 - size * 0.9 - block >= ceiling:
            break
        size *= 0.94
    lead = size * 1.22

    s.wordmark(brand, pad, mark_cy, mark_w, anchor="start")
    y = mark_cy - mark_h / 2 - size * 0.9
    if cta:
        s.line(cta, pad, y, size * 0.46, weight=500, fill=s.muted)
        y -= size * 0.85
    rule_h = max(3.0, short * 0.011)
    s.rule(pad, y - rule_h, short * 0.13, rule_h)
    y -= rule_h + size * 0.95

    for i, ln in enumerate(reversed(headline)):
        s.line(ln, pad, y - i * lead, size, weight=700)
    top = y - (len(headline) - 1) * lead
    if kicker:
        s.line(kicker, pad, top - lead * 0.95, short * 0.036, weight=600, fill=s.gold_text)
    return s.svg()


def content_card(
    w: int,
    h: int,
    brand: str,
    scheme: str,
    *,
    kind: str,
    title: list[str],
    meta: str = "",
    body: list[str] | None = None,
) -> str:
    """The publishing template: one kind chip, one title, an optional code panel."""
    s = Surface(w, h, scheme)
    short = min(w, h)
    s.ghost(brand, w * 0.93, h * 0.10, short * 0.75, rot=GHOST_ROT[brand])
    pad = w * 0.062
    chip_h = short * 0.062
    chip_w = text_width(kind, short * 0.030, 600) + chip_h * 1.1
    s.rect(pad, pad, chip_w, chip_h, GOLD, rx=chip_h / 2)
    s.line(kind, pad + chip_w / 2, pad + chip_h * 0.66, short * 0.030, weight=600, fill=INK, anchor="middle")
    size = short * 0.082
    lead = size * 1.2
    top = pad + chip_h + short * 0.14
    for i, ln in enumerate(title):
        s.line(ln, pad, top + i * lead, size, weight=700)
    y = top + len(title) * lead + short * 0.03
    if body:
        panel_h = short * 0.055 * len(body) + short * 0.06
        s.rect(pad, y, w - pad * 2, panel_h, s.text, rx=short * 0.02, opacity=0.06)
        for i, ln in enumerate(body):
            s.line(ln, pad + short * 0.05, y + short * 0.075 + i * short * 0.055, short * 0.034, weight=500, fill=s.muted)
        y += panel_h
    if meta:
        s.line(meta, pad, h - pad, short * 0.034, weight=500, fill=s.muted)
    s.wordmark(brand, w - pad, h - pad - short * 0.022, short * 0.30, anchor="end")
    return s.svg()


__all__ = [
    "GOLD_BRIGHT",
    "Surface",
    "ad",
    "avatar",
    "banner",
    "content_card",
    "mark_aspect",
    "og_card",
    "wallpaper_desktop",
    "wallpaper_phone",
]
