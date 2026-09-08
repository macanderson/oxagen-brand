"""Every finished surface: wallpapers, social art, ads, and content cards.

One composition rule holds all of them. A surface is a ground, one warm bloom
of the metal, the brand's own icon placed off-centre, and at most a few lines
of type. The icon is the only picture either brand owns, so a surface that
needs more than a mark builds one out of the icon itself: a constellation of
nodes wired to it, a mosaic of blocks in its shape, or rings of nodes in orbit
around it. Nothing here draws a shape the marks do not already contain. Every
one of them is placed by a seeded random, so the same file comes out of the
build every time.
"""

from __future__ import annotations

import math

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
from geom import Point, dist, nearest, rng, scatter
from glyphs import glyph_paths, text_path, text_width, wordmark
from marks import BRANDS, icon_body, icon_geometry, icon_hit, sheen_defs

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


def icon_ports(brand: str) -> list[Point]:
    """Where an edge may leave the icon, in its own units.

    Six points on the ellipse the mark's ink box inscribes, so a constellation
    hangs off the shape rather than off its corners. Both marks are outlines
    now, so neither needs a special case.
    """
    g = icon_geometry(brand)
    cx, cy = float(g["cx"]), float(g["cy"])  # type: ignore[arg-type]
    rx, ry = float(g["w"]) / 2 * 0.9, float(g["h"]) / 2 * 0.9  # type: ignore[arg-type]
    return [
        (cx + rx * math.cos(math.radians(a)), cy + ry * math.sin(math.radians(a)))
        for a in range(30, 360, 60)
    ]


class Surface:
    """A fixed-size canvas that stacks SVG fragments in order."""

    def __init__(self, w: int, h: int, scheme: str = "dark", ground: str | None = None):
        self.w, self.h, self.scheme = w, h, scheme
        self.dark = scheme == "dark"
        self.ground = ground or GROUNDS[scheme]
        self.text = TEXT_ON[scheme]
        self.muted = MUTED_ON[scheme]
        self.gold_text = GOLD_TEXT_ON[scheme]
        self.border = BORDER_ON[scheme]
        self.body: list[str] = []
        self.defs: list[str] = []
        self._sheen: str | None = None

    @property
    def short(self) -> float:
        return min(self.w, self.h)

    def sheen(self) -> str:
        """One metallic gradient per surface, shared by every block that wants it."""
        if not self._sheen:
            uid = _sid()
            self.defs.append(sheen_defs(uid))
            self._sheen = f"url(#sheen-{uid})"
        return self._sheen

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

    def _placement(self, brand: str, cx: float, cy: float, span: float, rot: float) -> tuple[float, float, float]:
        """(scale, icon cx, icon cy): the icon's own centre maps to (cx, cy) at `span`."""
        g = icon_geometry(brand)
        s = span / max(float(g["w"]), float(g["h"]))  # type: ignore[arg-type]
        return s, float(g["cx"]), float(g["cy"])  # type: ignore[arg-type]

    def _placed(self, brand: str, cx: float, cy: float, span: float, rot: float) -> tuple[str, float]:
        s, gcx, gcy = self._placement(brand, cx, cy, span, rot)
        return (
            f'transform="translate({cx:.2f},{cy:.2f}) rotate({rot:g}) scale({s:.5f}) '
            f'translate({-gcx:.3f},{-gcy:.3f})"',
            s,
        )

    def _to_canvas(self, brand: str, cx: float, cy: float, span: float, rot: float, p: Point) -> Point:
        """A point in icon units, on the canvas, under the same placement."""
        s, gcx, gcy = self._placement(brand, cx, cy, span, rot)
        x, y = (p[0] - gcx) * s, (p[1] - gcy) * s
        a = math.radians(rot)
        return (cx + x * math.cos(a) - y * math.sin(a), cy + x * math.sin(a) + y * math.cos(a))

    def inside(self, brand: str, cx: float, cy: float, span: float, *, margin: float = 0.05) -> tuple[float, float]:
        """`cx, cy` pulled back until a mark of `span` fits the canvas whole.

        A surface that wants the mark bleeding off an edge (the ads, the open
        graph card) places it directly and does not call this. A wallpaper
        does call it, because a mark clipped by a few per cent of its width
        reads as a mistake rather than as a crop -- and because the two marks
        are different shapes, the placement that fits one does not fit the
        other. `span` is the mark's long edge, so it bounds both directions.
        """
        half, m = span / 2, min(self.w, self.h) * margin
        if half * 2 + m * 2 <= self.w:
            cx = min(max(cx, half + m), self.w - half - m)
        if half * 2 + m * 2 <= self.h:
            cy = min(max(cy, half + m), self.h - half - m)
        return cx, cy

    def ghost(
        self, brand: str, cx: float, cy: float, span: float, *, rot: float = 0.0, alpha: float | None = None
    ) -> "Surface":
        """The icon, oversized, in the metal, at a fifth strength over its own bloom."""
        a = (0.16 if self.dark else 0.20) if alpha is None else alpha
        self.glow(cx, cy, span * 0.95, 0.42 if self.dark else 0.34)
        t, _ = self._placed(brand, cx, cy, span, rot)
        fill = self.sheen()
        self.body.append(f'<g opacity="{a:g}" {t}>{icon_body(brand, letters=fill, accent=fill)}</g>')
        return self

    def outline(self, brand: str, cx: float, cy: float, span: float, *, rot: float = 0.0) -> "Surface":
        """The icon as a hairline in the metal: the quiet wallpaper."""
        t, s = self._placed(brand, cx, cy, span, rot)
        g = icon_geometry(brand)
        hair = max(1.6, self.short * 0.0012)  # a hairline, but one that survives a thumbnail
        inner = (
            f'<path d="{g["path"]}" fill="none" stroke="{GOLD}" '
            f'stroke-width="{hair / s:.4f}" stroke-linejoin="round"/>'
        )
        self.body.append(f'<g opacity="0.85" {t}>{inner}</g>')
        return self

    def icon(self, brand: str, cx: float, cy: float, span: float, *, sheen: bool = True) -> "Surface":
        """The icon at full strength."""
        t, _ = self._placed(brand, cx, cy, span, 0.0)
        accent = self.sheen() if sheen else GOLD
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
        return self.rect(x, y, w, h, self.sheen(), rx=h / 2)

    # -- the icon's vocabulary, at scale ----------------------------------

    def _block(self, x: float, y: float, side: float, fill: str, alpha: float) -> str:
        return (
            f'<rect x="{x - side / 2:.1f}" y="{y - side / 2:.1f}" width="{side:.1f}" height="{side:.1f}" '
            f'rx="{side * 0.24:.1f}" fill="{fill}" opacity="{alpha:.2f}"/>'
        )

    def constellation(
        self,
        brand: str,
        hx: float,
        hy: float,
        span: float,
        *,
        seed: str = "",
        quiet: tuple[float, float, float, float] = (0.0, 0.0, 0.0, 0.0),
    ) -> "Surface":
        """A field of nodes, each wired to its neighbours, with the icon as the hub.

        Nodes scatter over the canvas but keep clear of the icon and thin out
        toward the quiet edges (`quiet` is how much of each of left, top, right,
        bottom to leave calm). Each node joins its two nearest neighbours in a
        hairline. The icon reaches out in gold to the nodes nearest it, and
        those nodes are lit as blocks: the one-to-many, drawn.
        """
        w, h, short = self.w, self.h, self.short
        r = rng("constellation", brand, w, h, seed)
        n = int(w * h / (short * short) * 150)
        min_d = short * 0.052
        clear = span * 0.66
        ql, qt, qr, qb = quiet

        def accept(x: float, y: float) -> float:
            if dist((x, y), (hx, hy)) < clear:
                return 0.0
            a = 1.0
            if ql and x < w * ql:
                a *= 0.25 + 0.75 * x / (w * ql)
            if qr and x > w * (1 - qr):
                a *= 0.25 + 0.75 * (w - x) / (w * qr)
            if qt and y < h * qt:
                a *= 0.25 + 0.75 * y / (h * qt)
            if qb and y > h * (1 - qb):
                a *= 0.25 + 0.75 * (h - y) / (h * qb)
            return a

        pts = scatter(r, w, h, n, min_d, accept=accept)
        if not pts:
            return self
        line_a = 0.13 if self.dark else 0.15
        edges: set[tuple[int, int]] = set()
        for i in range(len(pts)):
            for j in nearest(pts, i, 2):
                if dist(pts[i], pts[j]) < min_d * 2.8:
                    edges.add((min(i, j), max(i, j)))
        hair = max(1.2, short * 0.0009)
        seg = "".join(
            f'<path d="M{pts[i][0]:.1f} {pts[i][1]:.1f}L{pts[j][0]:.1f} {pts[j][1]:.1f}"/>' for i, j in sorted(edges)
        )
        self.body.append(f'<g fill="none" stroke="{self.text}" stroke-width="{hair:.2f}" opacity="{line_a}">{seg}</g>')

        # the hub reaches out: each port to the three nodes nearest it
        ports = [self._to_canvas(brand, hx, hy, span, 0.0, p) for p in icon_ports(brand)]
        gold_nodes: set[int] = set()
        gold_seg = []
        for px, py in ports:
            order = sorted(range(len(pts)), key=lambda k: dist(pts[k], (px, py)))
            for k in order[:3]:
                if dist(pts[k], (px, py)) < span * 1.15:
                    gold_nodes.add(k)
                    gold_seg.append(f'<path d="M{px:.1f} {py:.1f}L{pts[k][0]:.1f} {pts[k][1]:.1f}"/>')
        self.body.append(
            f'<g fill="none" stroke="{GOLD}" stroke-width="{hair * 1.6:.2f}" stroke-linecap="round" '
            f'opacity="{0.55 if self.dark else 0.6}">{"".join(gold_seg)}</g>'
        )

        # the nodes: dots that brighten toward the hub, and a few blocks
        dots, blocks = [], []
        reach = max(w, h) * 0.75
        for i, (x, y) in enumerate(pts):
            near = max(0.0, 1 - dist((x, y), (hx, hy)) / reach)
            if i in gold_nodes:
                blocks.append(self._block(x, y, short * 0.014, self.sheen(), 0.95))
            elif r.random() < 0.09:
                blocks.append(self._block(x, y, short * 0.010, GOLD, 0.35 + 0.45 * near))
            else:
                rad = short * (0.0022 + 0.0032 * r.random())
                a = 0.22 + 0.5 * near
                dots.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{rad:.1f}" opacity="{a:.2f}"/>')
        self.body.append(f'<g fill="{self.text}">{"".join(dots)}</g>')
        self.body.append("".join(blocks))

        self.glow(hx, hy, span * 1.4, 0.34 if self.dark else 0.26)
        self.icon(brand, hx, hy, span)
        return self

    def mosaic(self, brand: str, cx: float, cy: float, span: float, *, cell: float, seed: str = "") -> "Surface":
        """The icon rebuilt from blocks on a grid, with a bloom of blocks around it.

        A faint grid of blocks covers the whole ground. Every cell whose centre
        lands on the icon's ink is painted in the metal, each a shade brighter
        or deeper than its neighbour so the surface reads as tiles, not a
        stencil. Cells just outside the ink catch a little gold that fades with
        distance, the bloom drawn in the same blocks.
        """
        r = rng("mosaic", brand, self.w, self.h, seed)
        gap = cell * 0.26
        side = cell - gap
        rx = side * 0.24
        ox, oy = (cx % cell) - cell / 2, (cy % cell) - cell / 2  # the icon's centre on a cell centre
        uid = _sid()
        base_a = 0.055 if self.dark else 0.07
        self.defs.append(
            f'<pattern id="p-{uid}" x="{ox:.2f}" y="{oy:.2f}" width="{cell:.3f}" height="{cell:.3f}" patternUnits="userSpaceOnUse">'
            f'<rect x="{gap / 2:.2f}" y="{gap / 2:.2f}" width="{side:.2f}" height="{side:.2f}" rx="{rx:.2f}" '
            f'fill="{self.text}" opacity="{base_a}"/></pattern>'
        )
        self.body.append(f'<rect width="{self.w}" height="{self.h}" fill="url(#p-{uid})"/>')
        self.glow(cx, cy, span * 0.9, 0.30 if self.dark else 0.22)

        hit = icon_hit(brand)
        s, gcx, gcy = self._placement(brand, cx, cy, span, 0.0)
        halo = span * 0.8
        lit, warm = [], []
        nx, ny = int(self.w / cell) + 2, int(self.h / cell) + 2
        for j in range(ny):
            y = oy + j * cell + cell / 2
            for i in range(nx):
                x = ox + i * cell + cell / 2
                d = dist((x, y), (cx, cy))
                if d > halo:
                    continue
                if hit((x - cx) / s + gcx, (y - cy) / s + gcy):
                    lit.append(self._block(x, y, side, self.sheen(), 0.74 + 0.26 * r.random()))
                else:
                    a = (1 - d / halo) ** 2 * (0.20 if self.dark else 0.16) * (0.7 + 0.3 * r.random())
                    if a > 0.015:
                        warm.append(self._block(x, y, side, GOLD, a))
        self.body.append("".join(warm))
        self.body.append("".join(lit))
        return self

    def orbit(self, brand: str, cx: float, cy: float, span: float, *, seed: str = "") -> "Surface":
        """Rings of nodes around the icon, each wired inward: the graph, radially.

        Five hairline rings, more nodes on each ring out. Every node joins the
        nearest node on the ring inside it, and the innermost ring joins the
        icon's own ports in gold, so the whole field hangs off the mark.
        """
        r = rng("orbit", brand, self.w, self.h, seed)
        short = self.short
        radii = [span * k for k in (0.78, 1.16, 1.6, 2.1, 2.7)]
        counts = (6, 9, 13, 18, 24)
        hair = max(1.2, short * 0.0009)
        ring_a = 0.11 if self.dark else 0.13
        self.body.append(
            f'<g fill="none" stroke="{self.text}" stroke-width="{hair:.2f}" opacity="{ring_a}">'
            + "".join(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{rad:.1f}"/>' for rad in radii)
            + "</g>"
        )
        rings: list[list[Point]] = []
        for rad, n in zip(radii, counts):
            phase = r.random() * 360
            pts = []
            for k in range(n):
                a = math.radians(phase + k * 360 / n + (r.random() - 0.5) * 360 / n * 0.5)
                pts.append((cx + rad * math.cos(a), cy + rad * math.sin(a)))
            rings.append(pts)

        ports = [self._to_canvas(brand, cx, cy, span, 0.0, p) for p in icon_ports(brand)]
        gold_seg, seg = [], []
        for p in rings[0]:
            q = min(ports, key=lambda t: dist(t, p))
            gold_seg.append(f'<path d="M{q[0]:.1f} {q[1]:.1f}L{p[0]:.1f} {p[1]:.1f}"/>')
        for inner, outer in zip(rings, rings[1:]):
            for p in outer:
                q = min(inner, key=lambda t: dist(t, p))
                seg.append(f'<path d="M{q[0]:.1f} {q[1]:.1f}L{p[0]:.1f} {p[1]:.1f}"/>')
        self.body.append(
            f'<g fill="none" stroke="{self.text}" stroke-width="{hair:.2f}" opacity="{0.16 if self.dark else 0.18}">{"".join(seg)}</g>'
        )
        self.body.append(
            f'<g fill="none" stroke="{GOLD}" stroke-width="{hair * 1.6:.2f}" stroke-linecap="round" '
            f'opacity="{0.6 if self.dark else 0.65}">{"".join(gold_seg)}</g>'
        )
        nodes = []
        for depth, pts in enumerate(rings):
            fade = 1 - depth * 0.16
            for x, y in pts:
                if depth == 0:
                    nodes.append(self._block(x, y, short * 0.016, self.sheen(), 0.95))
                elif r.random() < 0.22:
                    nodes.append(self._block(x, y, short * 0.011, GOLD, 0.5 * fade))
                else:
                    nodes.append(
                        f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{short * (0.0028 + 0.0025 * r.random()):.1f}" '
                        f'fill="{self.text}" opacity="{0.55 * fade:.2f}"/>'
                    )
        self.body.append("".join(nodes))
        self.glow(cx, cy, span * 1.3, 0.36 if self.dark else 0.28)
        self.icon(brand, cx, cy, span)
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


def mark_aspect(brand: str) -> float:
    m = _mark(brand)
    return float(m["height"]) / float(m["width"])  # type: ignore[arg-type]


# --------------------------------------------------------------------------
# the compositions
# --------------------------------------------------------------------------

GHOST_ROT = {"stella": -15.0, "oxagen": 0.0}

#: The wallpaper styles. `glow` and `quiet` are the mark alone; the other
#: three build a picture from the mark's own parts.
WALLPAPER_STYLES = ("glow", "quiet", "graph", "blocks", "orbit")


def wallpaper_desktop(w: int, h: int, brand: str, scheme: str, style: str = "glow") -> str:
    """The picture sits right of centre, leaving the icon corner and the dock clear."""
    s = Surface(w, h, scheme)
    span = h * 0.82
    cx, cy = s.inside(brand, w * 0.78, h * 0.46, span)
    if style == "glow":
        s.ghost(brand, cx, cy, span, rot=GHOST_ROT[brand])
    elif style == "quiet":
        s.outline(brand, cx, cy, span, rot=GHOST_ROT[brand])
    elif style == "graph":
        s.constellation(brand, w * 0.66, h * 0.5, h * 0.30, quiet=(0.30, 0.06, 0.0, 0.08))
    elif style == "blocks":
        s.mosaic(brand, w * 0.66, h * 0.5, h * 0.66, cell=h / 44)
    elif style == "orbit":
        s.orbit(brand, w * 0.66, h * 0.5, h * 0.24)
    else:
        raise ValueError(style)
    return s.svg()


def wallpaper_phone(w: int, h: int, brand: str, scheme: str, style: str = "glow") -> str:
    """Portrait: the picture sits below the clock and above the dock."""
    s = Surface(w, h, scheme)
    cx, cy = w * 0.5, h * 0.47
    gx, gy = s.inside(brand, cx, h * 0.5, w * 0.92)
    if style == "glow":
        s.ghost(brand, gx, gy, w * 0.92, rot=GHOST_ROT[brand])
    elif style == "quiet":
        s.outline(brand, gx, gy, w * 0.92, rot=GHOST_ROT[brand])
    elif style == "graph":
        s.constellation(brand, cx, cy, w * 0.40, quiet=(0.0, 0.16, 0.0, 0.14))
    elif style == "blocks":
        s.mosaic(brand, cx, cy, w * 0.78, cell=w / 24)
    elif style == "orbit":
        s.orbit(brand, cx, cy, w * 0.30)
    else:
        raise ValueError(style)
    return s.svg()


def avatar(brand: str, size: int, scheme: str) -> str:
    s = Surface(size, size, scheme)
    s.glow(size * 0.5, size * 0.5, size * 0.6, 0.14 if scheme == "dark" else 0.08)
    s.icon(brand, size * 0.5, size * 0.5, size * (0.58 if brand == "stella" else 0.66))
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
    w: int,
    h: int,
    brand: str,
    scheme: str,
    *,
    headline: list[str],
    kicker: str = "",
    subline: str = "",
    cta: str = "",
) -> str:
    """Kicker, a short headline set tight, the answer line, a rule, then the mark.

    Laid out from the bottom edge upward so the call to action can never land
    on the wordmark, and the type is shrunk until the block fits under the
    kicker -- the square is where the headline is tallest against the canvas.

    The headline names the reader's problem; `subline` is the one line that
    says what Oxagen does about it. It is set at a little under half the
    headline and in the full text colour rather than the muted one, because
    it is the substance of the ad and not a caption to it.
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
        block = (
            (len(headline) - 1) * size * 1.22
            + size * 1.9
            + (size * 0.85 if cta else 0)
            + (size * 1.05 if subline else 0)
        )
        wide = max(text_width(ln, size, 700) for ln in headline)
        if mark_cy - mark_h / 2 - size * 0.9 - block >= ceiling and wide <= w - pad * 2:
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
    if subline:
        # The answer line never wraps and never runs into the margin: it is
        # one sentence, so if it will not fit the measure it is set smaller.
        sub = size * 0.44
        while sub > size * 0.22 and text_width(subline, sub, 500) > w - pad * 2:
            sub *= 0.96
        s.line(subline, pad, y, sub, weight=500)
        y -= size * 1.05

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
    "WALLPAPER_STYLES",
    "ad",
    "avatar",
    "banner",
    "content_card",
    "mark_aspect",
    "og_card",
    "wallpaper_desktop",
    "wallpaper_phone",
]
