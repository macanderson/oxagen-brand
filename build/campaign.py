"""The always-on campaign page: Mac's draft of 2026-09-26, set as ads, banners, website sections, and calls to action.

`build/messages.py` renders this page beside the message bank, runs the same
page check over it, and writes it to `always-on.html`. Every line on the page
comes from `messages/always-on/`. `build/build.py` renders the approved
combinations into `ads/`. Every other entry is a candidate, and nothing here
renders it.

The art is plain SVG drawn in this file with the house ad geometry of
`build/surfaces.py`: the ghost or the orbit behind, then the kicker, the
headline, the rule, the subline, and the action stacked above the wordmark. It
does not import `surfaces.py`, so the page needs PyYAML and nothing else. The
builder on the page carries a JavaScript port of `ad()`; change both together.

The website previews set every heading (`.m-h1`, `.m-h2`, the wall, the
strip, the sign-offs) in Space Grotesk through `--font-display`, at a
marketing step of 20px or more. The page chrome is an app surface and sets its
headings in Aeonik. The ad art sets all of its text in Aeonik, as the files in `ads/` do,
and `WIDTHS` measures it. Only the wordmark is Space Grotesk, and it is a
drawn path.
"""

from __future__ import annotations

import json
import math
import re

import color as C
import messages as MS
import pwa

PAGE = MS.ROOT / "always-on.html"
TITLE = "Oxagen always-on campaign"
T, A = MS.T, MS.A
DISPLAY = "'Aeonik', system-ui, -apple-system, 'Segoe UI', sans-serif"

#: Aeonik 700 advances in em, read from fonts/aeonik-wght.woff2 instanced at
#: wght 700 (`glyphs.font(700, "text")`). Line breaks and fits measure with
#: these, so the art wraps where the font does. A change of text face needs a
#: new table, and the JavaScript port reads this one.
CHARS = " !\"#$%&'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\\]^_`abcdefghijklmnopqrstuvwxyz{|}~’·"
WIDTHS = (
    0.238, 0.253, 0.411, 0.645, 0.62, 0.919, 0.804, 0.217, 0.344, 0.344, 0.434, 0.515, 0.248, 0.43, 0.248, 0.383,
    0.647, 0.367, 0.567, 0.588, 0.615, 0.59, 0.612, 0.54, 0.6, 0.612, 0.248, 0.248, 0.515, 0.515, 0.515, 0.534,
    0.981, 0.703, 0.634, 0.699, 0.704, 0.564, 0.546, 0.739, 0.691, 0.263, 0.394, 0.68, 0.507, 0.886, 0.694, 0.753,
    0.619, 0.76, 0.635, 0.62, 0.6, 0.683, 0.657, 0.996, 0.656, 0.666, 0.628, 0.333, 0.442, 0.333, 0.526, 0.504,
    0.4, 0.561, 0.615, 0.569, 0.615, 0.581, 0.37, 0.615, 0.599, 0.244, 0.252, 0.559, 0.244, 0.904, 0.599, 0.6,
    0.615, 0.615, 0.379, 0.53, 0.377, 0.592, 0.548, 0.825, 0.54, 0.552, 0.507, 0.348, 0.254, 0.348, 0.515, 0.248,
    0.248,
)
assert len(CHARS) == len(WIDTHS), "one advance per character"
ADVANCE = dict(zip(CHARS, WIDTHS))
FALLBACK = 0.6  # a character the table lacks measures as a wide lowercase letter
FIT = 0.97  # a line fills at most this share of its measure, for rounding and the 500 weight

_PATHS = re.findall(r' d="([^"]+)"', MS.WORDMARK)
assert len(_PATHS) == 4, "the wordmark carries the hexes, the cells, the letters, and the x"
HEX, CELLS, LETTERS, X = _PATHS
WM_W, WM_H = 574.244, 106.313
MARK_SCALE = 2.842952  # the mark's scale inside the wordmark
LETTERS_AT = (120.376, 13.067)
ICON_W, ICON_H = 32.214, 33.76  # the mark in its own units

ORBIT_RADII = (0.78, 1.16, 1.6, 2.1, 2.7)
ORBIT_NODES = (6, 9, 13, 18, 24)

SHAPES = {"square": "Square", "portrait": "Portrait", "landscape": "Landscape", "mpu": "Medium rectangle"}
GROUND = {"dark": "ink", "light": "paper"}
NAV = (("ads", "Ads"), ("banners", "Banners"), ("sites", "Website sections"), ("ctas", "Calls to action"),
       ("builder", "Builder"), ("lines", "Lines"))


def n(v: float) -> str:
    s = f"{v:.2f}".rstrip("0").rstrip(".")
    return "0" if s in ("-0", "") else s


def width(s: str, size: float) -> float:
    return sum(ADVANCE.get(ch, FALLBACK) for ch in s) * size


def wrap(text: str, size: float, max_w: float) -> list[str]:
    lines, cur = [], ""
    for word in text.split():
        t = f"{cur} {word}" if cur else word
        if cur and width(t, size) > max_w * FIT:
            lines.append(cur)
            cur = word
        else:
            cur = t
    if cur:
        lines.append(cur)
    return lines


def balanced(text: str, size: float, max_w: float) -> list[str]:
    """The greedy wrap at the narrowest measure that keeps its line count, so the last line is not left short."""
    lines, target = wrap(text, size, max_w), max_w
    for _ in range(40):
        if len(lines) < 2:
            break
        trial = wrap(text, size, target * 0.97)
        if len(trial) != len(lines):
            break
        target, lines = target * 0.97, trial
    return lines


def fit(text: str, size: float, floor: float, max_w: float) -> float:
    while size > floor and width(text, size) > max_w * FIT:
        size *= 0.96
    return size


def action(cta: str, start: float, floor: float, max_w: float) -> tuple[str, float]:
    """The action line at the largest size that fits, or only its address when the whole line cannot."""
    c = fit(cta, start, floor, max_w)
    if width(cta, c) > max_w * FIT and " · " in cta:
        cta = cta.split(" · ")[-1]
        c = fit(cta, start, floor, max_w)
    return cta, c


def sublines(text: str | None, size: float, max_w: float) -> tuple[float, list[str]]:
    """The subline at 44 percent of the headline, in two lines at most."""
    if not text:
        return 0.0, []
    sub = size * 0.44
    lines = wrap(text, sub, max_w)
    while len(lines) > 2 and sub > size * 0.22:
        sub *= 0.96
        lines = wrap(text, sub, max_w)
    return sub, lines


#: The smallest size a qualifier is set at. build/surfaces.py holds the same
#: floor for the files in ads/, so the page and the files agree.
QUALIFIER_FLOOR_PX = 8.0


def qualifier_lines(text: str | None, size: float, max_w: float) -> tuple[float, list[str]]:
    """The qualifier under the answer line, as surfaces.qualifier_lines sets it: 34 percent of
    the headline, shrinking to 26 percent and never below the floor, on one line or split once
    at the sentence boundary. (0, []) when two lines at the floor still run past the measure."""
    if not text:
        return 0.0, []
    start = max(size * 0.34, QUALIFIER_FLOOR_PX)
    floor = max(size * 0.26, QUALIFIER_FLOOR_PX)
    head, sep, rest = text.partition(". ")
    for lines in [[text]] + ([[head + ".", rest]] if sep and rest else []):
        q = start
        while q > floor and max(width(x, q) for x in lines) > max_w * FIT:
            q = max(floor, q * 0.96)
        if max(width(x, q) for x in lines) <= max_w * FIT:
            return q, lines
    return 0.0, []


def first_sentence(text: str) -> tuple[str, str]:
    head, _, rest = text.partition(". ")
    return (head + ".", rest) if rest else (text, "")


# ---------------------------------------------------------------------------- art


class Art:
    """One SVG canvas: a ground, the defs it needs, and fragments in paint order.

    `themed` drops the ground and paints the ink in `currentColor`, so the art
    follows the page theme inside a website mock.
    """

    def __init__(self, uid: str, w: float, h: float, scheme: str, label: str, *, themed: bool = False):
        self.uid, self.w, self.h, self.label = uid, w, h, label
        self.dark = scheme == "dark" and not themed
        self.ink = "currentColor" if themed else C.TEXT_ON[scheme]
        self.muted = "currentColor" if themed else C.MUTED_ON[scheme]
        self.gold_text = C.GOLD_TEXT_ON[scheme]
        self.ground = None if themed else C.GROUNDS[scheme]
        self.defs: list[str] = []
        self.body: list[str] = []
        self._sheen = ""
        self._n = 0

    @property
    def short(self) -> float:
        return min(self.w, self.h)

    def sheen(self) -> str:
        if not self._sheen:
            sid = f"{self.uid}-sheen"
            self.defs.append(
                f'<linearGradient id="{sid}" x1="0" y1="1" x2="1" y2="0"><stop offset="0" stop-color="{C.GOLD_DEEP}"/>'
                f'<stop offset="0.38" stop-color="{C.GOLD}"/><stop offset="0.56" stop-color="{C.GOLD_BRIGHT}"/>'
                f'<stop offset="0.74" stop-color="{C.GOLD}"/><stop offset="1" stop-color="{C.GOLD_DEEP}"/></linearGradient>')
            self._sheen = f"url(#{sid})"
        return self._sheen

    def glow(self, cx: float, cy: float, r: float, alpha: float) -> None:
        """Dark grounds only: on white a bloom of gold reads as a cream wash."""
        if not self.dark:
            return
        self._n += 1
        gid = f"{self.uid}-glow{self._n}"
        self.defs.append(
            f'<radialGradient id="{gid}"><stop offset="0" stop-color="{C.GOLD}" stop-opacity="{n(alpha)}"/>'
            f'<stop offset="0.5" stop-color="{C.GOLD}" stop-opacity="{n(alpha * 0.35)}"/>'
            f'<stop offset="1" stop-color="{C.GOLD}" stop-opacity="0"/></radialGradient>')
        self.body.append(f'<circle cx="{n(cx)}" cy="{n(cy)}" r="{n(r)}" fill="url(#{gid})"/>')

    def text(self, x: float, y: float, s: str, size: float, weight: int, fill: str, anchor: str = "start") -> None:
        a = f' text-anchor="{anchor}"' if anchor != "start" else ""
        self.body.append(f'<text x="{n(x)}" y="{n(y)}" font-size="{n(size)}" font-weight="{weight}" fill="{fill}"{a}>{T(s)}</text>')

    def rule(self, x: float, y: float, w: float, h: float) -> None:
        self.body.append(f'<rect x="{n(x)}" y="{n(y)}" width="{n(w)}" height="{n(h)}" rx="{n(min(w, h) / 2)}" fill="{self.sheen()}"/>')

    def wordmark(self, x: float, y: float, w: float) -> None:
        self.body.append(
            f'<g transform="translate({n(x)},{n(y)}) scale({w / WM_W:.5f})"><g transform="scale({MARK_SCALE})">'
            f'<path d="{HEX}" fill="{self.ink}"/><path d="{CELLS}" fill="{C.GOLD}"/></g>'
            f'<g transform="translate({LETTERS_AT[0]},{LETTERS_AT[1]})"><path d="{LETTERS}" fill="{self.ink}"/>'
            f'<path d="{X}" fill="{C.GOLD}"/></g></g>')

    @staticmethod
    def icon(cx: float, cy: float, span: float, hexes: str, cells: str, hex_opacity: float | None = None) -> str:
        s = span / max(ICON_W, ICON_H)
        op = f' fill-opacity="{n(hex_opacity)}"' if hex_opacity is not None else ""
        return (f'<g transform="translate({n(cx)},{n(cy)}) scale({s:.5f}) translate({-ICON_W / 2:.3f},{-ICON_H / 2:.3f})">'
                f'<path d="{HEX}" fill="{hexes}"{op}/><path d="{CELLS}" fill="{cells}"/></g>')

    def block(self, x: float, y: float, side: float, alpha: float) -> str:
        return (f'<rect x="{n(x - side / 2)}" y="{n(y - side / 2)}" width="{n(side)}" height="{n(side)}" '
                f'rx="{n(side * 0.24)}" fill="{self.sheen()}" opacity="{n(alpha)}"/>')

    def ghost(self, cx: float, cy: float, span: float) -> None:
        """The mark, oversized, in the metal at a sixth strength over its bloom. On white, its own two colours, faint."""
        if self.dark:
            self.glow(cx, cy, span * 0.95, 0.42)
            fill = self.sheen()
            self.body.append(f'<g opacity="0.16">{self.icon(cx, cy, span, fill, fill)}</g>')
        else:
            self.body.append(f'<g opacity="0.55">{self.icon(cx, cy, span, self.ink, C.GOLD, 0.25)}</g>')

    def orbit(self, cx: float, cy: float, span: float, behind: float | None) -> None:
        """Five rings of nodes around the mark, each wired to the ring inside it and the first ring to the mark.

        The house draws the node phases from a seeded generator. These come from
        fixed formulas, so the page is the same bytes on every run and the
        builder's port draws the same picture.
        """
        start = len(self.body)
        short, hair = self.short, max(1.2, self.short * 0.0009)
        rings: list[tuple[float, list[tuple[float, float]]]] = []
        for k, (f, count) in enumerate(zip(ORBIT_RADII, ORBIT_NODES)):
            r, pts = span * f, []
            for i in range(count):
                a = k * 0.9 + 2 * math.pi * i / count + 0.18 * math.sin(i * 2.3 + k)
                rr = r * (1 + 0.04 * math.sin(i * 1.7 + k * 0.5))
                pts.append((cx + rr * math.cos(a), cy + rr * math.sin(a)))
            rings.append((r, pts))
        ring_op, wire_op, port_op = (0.11, 0.16, 0.6) if self.dark else (0.13, 0.18, 0.65)

        def line(p, q):
            return f'<line x1="{n(p[0])}" y1="{n(p[1])}" x2="{n(q[0])}" y2="{n(q[1])}"/>'

        def nearest(p, pts):
            return min(pts, key=lambda q: (q[0] - p[0]) ** 2 + (q[1] - p[1]) ** 2)

        circles = "".join(f'<circle cx="{n(cx)}" cy="{n(cy)}" r="{n(r)}"/>' for r, _ in rings)
        self.body.append(f'<g fill="none" stroke="{self.ink}" stroke-width="{n(hair)}" opacity="{ring_op}">{circles}</g>')
        wires = "".join(line(p, nearest(p, rings[k - 1][1])) for k in range(1, len(rings)) for p in rings[k][1])
        self.body.append(f'<g stroke="{self.ink}" stroke-width="{n(hair)}" opacity="{wire_op}">{wires}</g>')
        s = span / max(ICON_W, ICON_H)
        ports = [(cx + ICON_W / 2 * 0.9 * s * math.cos(math.radians(d)), cy + ICON_H / 2 * 0.9 * s * math.sin(math.radians(d)))
                 for d in range(30, 360, 60)]
        joins = "".join(line(p, nearest(p, ports)) for p in rings[0][1])
        self.body.append(f'<g stroke="{C.GOLD}" stroke-width="{n(hair * 1.6)}" stroke-linecap="round" opacity="{port_op}">{joins}</g>')
        nodes = []
        for k, (_, pts) in enumerate(rings):
            fade = 1 - k * 0.16
            for i, (x, y) in enumerate(pts):
                if k == 0:
                    nodes.append(self.block(x, y, short * 0.016, 0.95))
                elif (i * 5 + k * 3) % 9 in (1, 5):
                    nodes.append(self.block(x, y, short * 0.011, 0.95 * fade))
                else:
                    r = short * (0.0028 + 0.0025 * ((i * 7 + k) % 5) / 4)
                    nodes.append(f'<circle cx="{n(x)}" cy="{n(y)}" r="{n(r)}" fill="{self.ink}" opacity="{n(0.55 * fade)}"/>')
        self.body.append("".join(nodes))
        self.glow(cx, cy, span * 1.3, 0.36)
        self.body.append(self.icon(cx, cy, span, self.ink, self.sheen()))
        if behind is not None:
            painted = "".join(self.body[start:])
            del self.body[start:]
            self.body.append(f'<g opacity="{behind}">{painted}</g>')

    def svg(self) -> str:
        ground = f'<rect width="{n(self.w)}" height="{n(self.h)}" fill="{self.ground}"/>' if self.ground else ""
        defs = f"<defs>{''.join(self.defs)}</defs>" if self.defs else ""
        return (f'<svg xmlns="http://www.w3.org/2000/svg" class="art" viewBox="0 0 {n(self.w)} {n(self.h)}" '
                f'width="{n(self.w)}" height="{n(self.h)}" font-family="{DISPLAY}" role="img" aria-label="{A(self.label)}">'
                f'{defs}{ground}{"".join(self.body)}</svg>')


def ad(uid: str, w: float, h: float, scheme: str, *, lines: list[str] | None = None, text: str | None = None,
       kicker: str | None = None, subline: str | None = None, qualifier: str | None = None,
       cta: str | None = None, picture: str = "ghost",
       boost: float = 1.0, ghost_at: tuple[float, float, float] = (0.90, 0.12, 0.8)) -> str:
    """The house ad: the picture top right, the words stacked up from the wordmark at the bottom left.

    `lines` sets the headline as given. `text` wraps it at each trial size. `ghost_at` places the ghost as
    shares of the width, the height, and the short side; a skyscraper moves it down to fill its middle.
    `qualifier` goes under the answer line, muted, wherever `qualifier_lines` finds room for it.
    """
    label = " ".join(x for x in (kicker, " ".join(lines) if lines else text, subline, qualifier, cta) if x)
    a = Art(uid, w, h, scheme, label)
    short, pad = a.short, w * 0.085
    max_w = w - 2 * pad
    if picture == "orbit":
        a.orbit(w * 0.88, h * 0.13, short * 0.15, 0.52 if a.dark else 0.58)
    else:
        gx, gy, gs = ghost_at
        a.ghost(w * gx, h * gy, short * gs)
    mark_w = short * 0.40
    mark_h = mark_w * WM_H / WM_W
    mark_cy = h - pad - mark_h / 2
    size = min(w * 0.075, h * 0.105) * boost
    ceiling = pad + (size * 0.035 / 0.075 * 2.2 if kicker else 0)
    head: list[str] = []
    sub, subs = 0.0, []
    q, quals = 0.0, []
    for _ in range(24):
        head = list(lines) if lines else balanced(text or "", size, max_w)
        sub, subs = sublines(subline, size, max_w)
        q, quals = qualifier_lines(qualifier, size, max_w)
        block = ((len(head) - 1) * size * 1.22 + size * 1.9 + (size * 0.85 if cta else 0)
                 + (size * 1.05 + (len(subs) - 1) * sub * 1.3 if subs else 0)
                 + len(quals) * q * 1.3)
        widest = max(width(x, size) for x in head)
        if mark_cy - mark_h / 2 - size * 0.9 - block >= ceiling and widest <= max_w * FIT:
            break
        size *= 0.94
    lead = size * 1.22
    a.wordmark(pad, mark_cy - mark_h / 2, mark_w)
    y = mark_cy - mark_h / 2 - size * 0.9
    if cta:
        words, c = action(cta, size * 0.46, size * 0.24, max_w)
        a.text(pad, y, words, c, 500, a.muted)
        y -= size * 0.85
    rule_h = max(3, short * 0.011)
    a.rule(pad, y - rule_h, short * 0.13, rule_h)
    y -= rule_h + size * 0.95
    for j, s in enumerate(reversed(quals)):
        a.text(pad, y - j * q * 1.3, s, q, 500, a.muted)
    y -= len(quals) * q * 1.3
    if subs:
        for j, s in enumerate(reversed(subs)):
            a.text(pad, y - j * sub * 1.3, s, sub, 500, a.ink)
        y -= (len(subs) - 1) * sub * 1.3 + size * 1.05
    for i, s in enumerate(reversed(head)):
        a.text(pad, y - i * lead, s, size, 700, a.ink)
    top = y - (len(head) - 1) * lead
    if kicker:
        a.text(pad, top - lead * 0.95, kicker, short * 0.036, 600, a.gold_text)
    return a.svg()


def strip(uid: str, w: float, h: float, scheme: str, *, text: str, cta: str) -> str:
    """The leaderboard: the wordmark, a gold rule, one headline line, and the address at the right."""
    tail = cta.split(" · ")[-1]
    a = Art(uid, w, h, scheme, f"{text} {tail}")
    pad = h * 0.24
    mark_w = w * 0.13
    mark_h = mark_w * WM_H / WM_W
    a.wordmark(pad, (h - mark_h) / 2, mark_w)
    rule_w = max(2, h * 0.03)
    rx = pad + mark_w + pad * 0.8
    a.rule(rx, h * 0.28, rule_w, h * 0.44)
    tx = rx + rule_w + pad * 0.8
    c = h * 0.17
    a.text(w - pad, h / 2 + c * 0.35, tail, c, 500, a.muted, anchor="end")
    size = fit(text, h * 0.3, h * 0.14, w - pad - width(tail, c) - pad * 0.9 - tx)
    a.text(tx, h / 2 + size * 0.35, text, size, 700, a.ink)
    return a.svg()


def header(uid: str, w: float, h: float, scheme: str, *, text: str, kicker: str | None = None,
           subline: str | None = None, cta: str | None = None, x0: float | None = None, max_lines: int = 2) -> str:
    """A wide banner or a profile header: the words centred on the left, the orbit and the wordmark at the right.

    `x0` moves the words right of the profile photo a social header lays over its bottom left.
    """
    label = " ".join(x for x in (kicker, text, subline, cta) if x)
    a = Art(uid, w, h, scheme, label)
    pad = h * 0.14
    x0 = pad if x0 is None else x0
    a.orbit(w - h * 0.42, h * 0.3, h * 0.2, 0.52 if a.dark else 0.58)
    mark_w = min(h * 0.5, w * 0.14)
    mark_h = mark_w * WM_H / WM_W
    a.wordmark(w - pad - mark_w, h - pad - mark_h, mark_w)
    max_w = min(w - x0 - pad - mark_w - pad, w * 0.62)
    rule_h = max(3, h * 0.012)
    size = h * 0.2
    items: list[tuple] = []
    total = 0.0
    for _ in range(24):
        head = balanced(text, size, max_w)
        items, y = [], 0.0
        if kicker:
            ks = size * 0.36
            y += ks * 0.8
            items.append(("kicker", y, kicker, ks))
            y += size * 0.5
        for i, s in enumerate(head):
            y += size * 0.78 if i == 0 else size * 1.1
            items.append(("head", y, s, size))
        y += size * 0.42
        items.append(("rule", y, "", 0))
        y += rule_h
        if subline:
            ss = fit(subline, size * 0.46, size * 0.3, max_w)
            y += size * 0.45 + ss * 0.78
            items.append(("sub", y, subline, ss))
        if cta:
            words, c = action(cta, max(size * 0.34, h * 0.04), size * 0.24, max_w)
            y += c * 1.9
            items.append(("cta", y, words, c))
        total = y + size * 0.2
        widest = max(width(s, size) for s in head)
        if len(head) <= max_lines and widest <= max_w * FIT and total <= h - 2 * pad:
            break
        size *= 0.94
    off = (h - total) / 2
    for kind, y, s, z in items:
        if kind == "rule":
            a.rule(x0, off + y, h * 0.13, rule_h)
        elif kind == "kicker":
            a.text(x0, off + y, s, z, 600, a.gold_text)
        elif kind == "head":
            a.text(x0, off + y, s, z, 700, a.ink)
        elif kind == "sub":
            a.text(x0, off + y, s, z, 500, a.ink)
        else:
            a.text(x0, off + y, s, z, 500, a.muted)
    return a.svg()


# ---------------------------------------------------------------------------- page


def members(entries: list[dict]) -> list[dict]:
    rank = {key: i for i, (key, _h, _w) in enumerate(MS.SETS)}
    mem = [e for e in entries if e["_group"] == "always-on"]
    return sorted(mem, key=lambda e: (rank.get(e.get("set"), 99), e.get("order", 0), e["id"]))


class Campaign:
    def __init__(self, entries: list[dict], standalone: bool):
        self.members = members(entries)
        self.ids = {e["id"]: e for e in self.members}
        self.standalone = standalone
        self.rendered: set[str] = set()
        self._n = 0
        combos = [e for e in self.members if e.get("set") == "combos"]
        self.cta = combos[0]["cta"] if combos else "Explore Oxagen · oxagen.sh"
        self.button, _, self.address = self.cta.partition(" · ")

    def uid(self) -> str:
        self._n += 1
        return f"ad{self._n}"

    def t(self, eid: str) -> str:
        return self.ids[eid]["title"]

    def of(self, key: str, kind: str | None = None) -> list[dict]:
        return [e for e in self.members if e.get("set") == key and (kind is None or e["kind"] == kind)]

    @staticmethod
    def ref(eid: str) -> str:
        return f'<a href="#line-{A(eid)}">{T(eid)}</a>'

    def uses(self, eids: list[str]) -> str:
        return f'<p class="uses"><span>Lines</span>{"".join(self.ref(i) for i in eids)}</p>'

    def fig(self, svg: str, caption: str, eid: str, max_w: float | None = None) -> str:
        style = f' style="max-width:{n(max_w)}px"' if max_w else ""
        return f'<figure{style}>{svg}<figcaption><span>{T(caption)}</span>{self.ref(eid)}</figcaption></figure>'

    def combo(self, e: dict, shape: str, scheme: str) -> str:
        w, h = {s: (sw, sh) for sw, sh, s in MS.AD_SIZES}[shape]
        pic = e.get("picture", "ghost")
        q = e.get("qualifier")
        if shape == "mpu":
            # The 300x250 drops the kicker and the action, as ads/ does, and keeps the answer line short.
            art = ad(self.uid(), w, h, scheme, lines=e["short_lines"], subline=e.get("subshort"), qualifier=q,
                     picture=pic)
        elif shape == "landscape":
            art = ad(self.uid(), w, h, scheme, lines=e.get("wide"), text=None if e.get("wide") else e["title"],
                     kicker=e.get("kicker"), subline=e.get("subline"), qualifier=q, cta=e["cta"], picture=pic)
        else:
            art = ad(self.uid(), w, h, scheme, lines=e["headline"], kicker=e.get("kicker"), subline=e.get("subline"),
                     qualifier=q, cta=e["cta"], picture=pic)
        return self.fig(art, f"{SHAPES[shape]} {w} by {h} on {GROUND[scheme]}", e["id"], w if w < 600 else None)

    # ------------------------------------------------------------------ sections

    def intro(self) -> str:
        bank = ('<a href="message-bank.html#always-on">The message bank</a>' if self.standalone
                else 'The message bank (<span class="mono">message-bank.html</span>)')
        return (f'<div class="hero"><p class="eyebrow q">Always-on</p><h1>Always-on campaign</h1>'
                f'<p class="lead">Mac\'s draft of 2026-09-26, set as ads, banners, website sections, and calls to action.</p>'
                f'<p>Every line here comes from <span class="mono">messages/always-on/</span>, one entry per line. '
                f'An approved combination renders into <span class="mono">ads/</span>. Every other entry is a candidate until Mac approves it. '
                f'{bank} lists each entry with its readers, its owner, and its review date.</p></div>')

    def ads(self) -> str:
        rows = []
        for e in self.of("combos"):
            rows.append(f'<div class="figs">{self.combo(e, "square", "dark")}{self.combo(e, "square", "light")}</div>')
        sizes = [("portrait", "ad-oxagen-night-shift"), ("landscape", "ad-oxagen-progress-report"), ("mpu", "ad-oxagen-driver-seat")]
        more = "".join(f'<div class="figs">{self.combo(self.ids[eid], shape, "dark")}{self.combo(self.ids[eid], shape, "light")}</div>'
                       for shape, eid in sizes if eid in self.ids)
        return (f'<section id="ads"><p class="eyebrow q">Ads</p><h2>Ads</h2>'
                f'<p>Each ad pairs an intro line with a tagline, as the draft suggests. The kicker names the set the pair comes from.</p>'
                f'{"".join(rows)}<h3 class="group">Sizes</h3>'
                f'<p>The house sizes beside the square. The medium rectangle carries the headline alone.</p>{more}</section>')

    def banners(self) -> str:
        out = []
        if "night-progress-not-problems" in self.ids:
            out.append(self.fig(strip(self.uid(), 728, 90, "dark", text=self.t("night-progress-not-problems"), cta=self.cta),
                                "Leaderboard 728 by 90 on ink", "night-progress-not-problems", 728))
        if "workday-lead" in self.ids:
            head, rest = first_sentence(self.t("workday-lead"))
            out.append(self.fig(header(self.uid(), 970, 250, "light", text=head, subline=rest or None, cta=self.cta),
                                "Billboard 970 by 250 on paper", "workday-lead", 970))
        tall = []
        if "night-shift" in self.ids:
            tall.append(self.fig(ad(self.uid(), 300, 600, "dark", text=self.t("night-shift"), kicker="Always-on workforce",
                                    cta=self.cta, picture="orbit", boost=2.1), "Half page 300 by 600 on ink", "night-shift", 300))
        if "night-never-sleep" in self.ids:
            tall.append(self.fig(ad(self.uid(), 160, 600, "light", text=self.t("night-never-sleep"), cta=self.cta, boost=2.6,
                                    ghost_at=(0.62, 0.3, 1.25)),
                                 "Skyscraper 160 by 600 on paper", "night-never-sleep", 160))
        if tall:
            out.append(f'<div class="tall">{"".join(tall)}</div>')
        if "always-on-eyebrow" in self.ids and "control-plane-category" in self.ids:
            out.append(self.fig(header(self.uid(), 1584, 396, "dark", text=self.t("always-on-eyebrow"),
                                       subline=self.t("control-plane-category"), x0=1584 * 0.30),
                                "LinkedIn header 1584 by 396 on ink", "always-on-eyebrow"))
        if "night-around-the-clock" in self.ids:
            out.append(self.fig(header(self.uid(), 1500, 500, "light", text=self.t("night-around-the-clock"), cta=self.address or self.cta,
                                       x0=1500 * 0.30, max_lines=3), "X header 1500 by 500 on paper", "night-around-the-clock"))
        return (f'<section id="banners"><p class="eyebrow q">Banners</p><h2>Banners</h2>'
                f'<p>Display and social sizes, each set from one line. The social headers leave the bottom left clear for the profile photo.</p>'
                f'<div class="stack">{"".join(out)}</div></section>')

    @staticmethod
    def frame(body: str, cls: str = "") -> str:
        return (f'<div class="site"><div class="chrome"><i></i><i></i><i></i><span class="url">oxagen.sh</span></div>'
                f'<div class="m-body{" " + cls if cls else ""}">{body}</div></div>')

    def cards(self, eids: list[str]) -> str:
        return f'<div class="m-grid">{"".join(f"<p class=m-card>{T(self.t(i))}</p>" for i in eids)}</div>'

    def band(self, heading: str, title_id: str, lead_id: str, card_ids: list[str]) -> str:
        eids = [title_id, lead_id, *card_ids]
        if any(i not in self.ids for i in eids):
            return ""
        body = f'<p class="m-h2">{T(self.t(title_id))}</p><p class="m-lead">{T(self.t(lead_id))}</p>{self.cards(card_ids)}'
        return f'<h3 class="group">{T(heading)}</h3>{self.frame(body)}{self.uses(eids)}'

    def sites(self) -> str:
        out = []
        hero_ids = ["always-on-eyebrow", "workday-lead", "dispatch-experience", "control-plane-category"]
        if all(i in self.ids for i in hero_ids):
            head, rest = first_sentence(self.t("workday-lead"))
            art = Art(self.uid(), 480, 480, "light", "oxagen", themed=True)
            art.orbit(240, 240, 480 * 0.17, None)
            body = (f'<div><p class="m-eyebrow">{T(self.t("always-on-eyebrow"))}</p><p class="m-h1">{T(head)}</p>'
                    + (f'<p class="m-h1 m-quiet">{T(rest)}</p>' if rest else "")
                    + f'<p class="m-lead">{T(self.t("dispatch-experience"))}</p>'
                    f'<div class="m-actions"><span class="m-btn">{T(self.button)}</span><span class="m-url">{T(self.address)}</span></div>'
                    f'<p class="m-cat">{T(self.t("control-plane-category"))}</p></div><div class="m-art">{art.svg()}</div>')
            out.append(f'<h3 class="group">Hero</h3>{self.frame(body, "m-hero")}{self.uses(hero_ids)}')
        values = [e["id"] for e in self.of("value") if e["id"] != "value-not-human"]
        out.append(self.band("Value propositions", "night-progress-not-problems", "value-not-human", values))
        out.append(self.band("Workforce management", "momentum-drive", "reframe-capacity",
                             ["reframe-job-scope-rules", "reframe-report-not-timesheet", "reframe-like-tools"]))
        out.append(self.band("Operators and agents", "split-driver-seat", "split-prioritize-steer",
                             ["split-check-in", "split-step-back", "split-give-them-a-job"]))
        out.append(self.band("Steering", "steer-on-course", "steer-marching-orders",
                             ["steer-rules-once", "steer-context-per-job", "steer-new-direction"]))
        out.append(self.band("Coaching operators", "coach-keep-rolling", "coach-guide-strategy",
                             ["coach-where-agents-excelled", "coach-live-your-life"]))
        vision = [e["id"] for e in self.of("vision")]
        if vision:
            wall = "".join(f"<p>{T(self.t(i))}</p>" for i in vision[1:])
            body = f'<p class="m-h2">{T(self.t(vision[0]))}</p><div class="m-wall">{wall}</div>'
            out.append(f'<h3 class="group">Vision wall</h3>{self.frame(body)}{self.uses(vision)}')
        if "signoff-vision-momentum" in self.ids:
            body = (f'<p class="m-h2">{T(self.t("signoff-vision-momentum"))}</p>'
                    f'<div class="m-actions"><span class="m-btn">{T(self.button)}</span><span class="m-url">{T(self.address)}</span></div>')
            out.append(f'<h3 class="group">Closing call to action</h3>{self.frame(body, "m-center")}{self.uses(["signoff-vision-momentum"])}')
        return (f'<section id="sites"><p class="eyebrow q">Website sections</p><h2>Website sections</h2>'
                f'<p>Page bands for a campaign page on oxagen.sh. Each band takes a heading line, an intro line, and supporting lines from one set. '
                f'The mocks follow the page theme.</p>{"".join(out)}</section>')

    def ctas(self) -> str:
        signs = self.of("signoff")
        if not signs:
            return ""
        first = next((e for e in signs if e["id"] == "signoff-moving"), signs[0])
        strip_html = (f'<div class="cta-strip"><p>{T(first["title"])}</p><div class="m-actions">'
                      f'<span class="m-btn">{T(self.button)}</span><span class="m-url">{T(self.address)}</span></div></div>')
        cards = "".join(f'<div class="panel so"><p>{T(e["title"])}</p><span class="m-quietbtn">{T(self.button)}</span>'
                        f'<p class="uses">{self.ref(e["id"])}</p></div>' for e in signs)
        return (f'<section id="ctas"><p class="eyebrow q">Calls to action</p><h2>Calls to action</h2>'
                f'<p>The sign-offs close an ad, a page, or an email. The action is the house action, {T(self.cta)}. '
                f'A screen carries one gold action, so the cards use the quiet button.</p>'
                f'<h3 class="group">Strip</h3>{strip_html}{self.uses([first["id"]])}'
                f'<h3 class="group">Sign-off cards</h3><div class="grid g3 signoffs">{cards}</div></section>')

    def builder(self) -> str:
        def options(key_kinds, selected):
            groups = []
            for key, heading, _how in MS.SETS:
                opts = [e for e in self.of(key) if e["kind"] in key_kinds]
                if not opts:
                    continue
                body = "".join(f'<option value="{A(e["id"])}"{" selected" if e["id"] == selected else ""}>{T(e["title"])}</option>'
                               for e in opts)
                groups.append(f'<optgroup label="{A(heading)}">{body}</optgroup>')
            return "".join(groups)

        taglines = [e for e in self.members if e["kind"] == "headline" and e.get("set") != "signoff"]
        intros = [e for e in self.members if e["kind"] == "pitch"]
        signs = self.of("signoff")
        kickers = list(dict.fromkeys(e["kicker"] for e in self.of("combos") if e.get("kicker")))
        if not taglines:
            return ""
        tag_default = "night-sleep-tight" if "night-sleep-tight" in self.ids else taglines[0]["id"]
        intro_default = "value-overnight" if "value-overnight" in self.ids else ""
        close = f'<option value="cta" selected>{T(self.cta)}</option>' + "".join(
            f'<option value="{A(e["id"])}">{T(e["title"])}</option>' for e in signs)
        kick = '<option value="">None</option>' + "".join(
            f'<option value="{A(k)}"{" selected" if i == 0 else ""}>{T(k)}</option>' for i, k in enumerate(kickers))
        size_opts = "".join(f'<option value="{s}"{" selected" if s == "square" else ""}>{T(SHAPES[s])} {w} by {h}</option>'
                            for w, h, s in MS.AD_SIZES)
        data = {
            "advance": ADVANCE, "fallback": FALLBACK, "fit": FIT,
            "paths": {"hex": HEX, "cells": CELLS, "letters": LETTERS, "x": X},
            "wm": [WM_W, WM_H, MARK_SCALE, *LETTERS_AT], "icon": [ICON_W, ICON_H],
            "gold": [C.GOLD_DEEP, C.GOLD, C.GOLD_BRIGHT],
            "colors": {s: {"text": C.TEXT_ON[s], "muted": C.MUTED_ON[s], "goldText": C.GOLD_TEXT_ON[s], "ground": C.GROUNDS[s]}
                       for s in MS.SCHEMES},
            "sizes": {s: [w, h] for w, h, s in MS.AD_SIZES},
            "orbit": [ORBIT_RADII, ORBIT_NODES], "display": DISPLAY, "cta": self.cta,
            "lines": {e["id"]: e["title"] for e in [*taglines, *intros, *signs]},
        }
        blob = json.dumps(data, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
        return (f'<section id="builder"><p class="eyebrow q">Builder</p><h2>Ad builder</h2>'
                f'<p>Pick a tagline, an intro, and a closing line from the draft. The builder sets them in the house ad layout at any house size.</p>'
                f'<div class="builder"><div class="controls">'
                f'<label for="b-tagline">Tagline</label><select id="b-tagline">{options(("headline",), tag_default)}</select>'
                f'<label for="b-intro">Intro</label><select id="b-intro"><option value="">None</option>{options(("pitch",), intro_default)}</select>'
                f'<label for="b-close">Closing line</label><select id="b-close">{close}</select>'
                f'<label for="b-kicker">Kicker</label><select id="b-kicker">{kick}</select>'
                f'<label for="b-size">Size</label><select id="b-size">{size_opts}</select>'
                f'<label for="b-ground">Ground</label><select id="b-ground"><option value="dark" selected>Ink</option><option value="light">Paper</option></select>'
                f'<label for="b-picture">Picture</label><select id="b-picture"><option value="orbit" selected>Orbit</option><option value="ghost">Ghost</option></select>'
                f'<div class="acts"><button class="btn" id="b-copy-text" type="button">Copy text</button>'
                f'<button class="btn" id="b-copy-svg" type="button">Copy SVG</button></div>'
                f'<p id="b-status" class="dim" role="status" aria-live="polite"></p>'
                f'<textarea id="b-fallback" rows="6" readonly hidden aria-label="Text to copy"></textarea>'
                f'</div><div class="out" id="b-out"></div></div>'
                f'<script type="application/json" id="b-data">{blob}</script><script>{BUILDER_JS}</script></section>')

    def lines(self) -> str:
        blocks = []
        for key, heading, how in MS.SETS:
            rows = []
            for e in self.of(key):
                self.rendered.add(e["id"])
                extra = f'<div class="dim">{T(e["subline"])}</div>' if e.get("subline") else ""
                notes = f'<details><summary>Notes</summary><p>{T(e["notes"])}</p></details>' if e.get("notes") else ""
                rows.append(f'<tr id="line-{A(e["id"])}"><td><b>{T(e["title"])}</b>{extra}{notes}</td>'
                            f'<td>{T(MS.ROLES.get(e["kind"], e["kind"]))}</td><td class="mono">{T(e["id"])}</td></tr>')
            if rows:
                blocks.append(f'<h3 class="group" id="set-{A(key)}">{T(heading)}</h3><p>{T(how)}</p>'
                              f'<div class="tw"><table><thead><tr><th>Line</th><th>Role</th><th>Id</th></tr></thead>'
                              f'<tbody>{"".join(rows)}</tbody></table></div>')
        return (f'<section id="lines"><p class="eyebrow q">Lines</p><h2>Lines</h2>'
                f'<p>Every line in the draft, by set. Each row is one entry in <span class="mono">messages/always-on/</span>.</p>'
                f'{"".join(blocks)}</section>')

    def render(self) -> str:
        body = "\n".join([self.intro(), self.ads(), self.banners(), self.sites(), self.ctas(), self.builder(), self.lines()])
        nav = "".join(f'<a href="#{a}">{T(label)}</a>' for a, label in NAV)
        if self.standalone:
            nav += '<a href="message-bank.html">Message bank</a>'
        page = (f'<header class="top"><div class="wrap"><div class="bar">{MS.WORDMARK}<span class="tag">always-on campaign</span>'
                f'<button class="btn" id="theme" type="button">Light theme</button></div>'
                f'<nav class="sub">{nav}</nav></div></header>\n<main class="wrap">\n{body}\n</main>\n'
                f'<footer><div class="wrap"><p style="margin:0">Oxagen always-on campaign. Generated by <span class="mono">build/campaign.py</span> '
                f'from <span class="mono">messages/always-on/</span>.</p></div></footer>\n<script>{THEME_JS}</script>\n')
        styles = f"<style>{MS.FONT_FACES}</style>\n<style>\n{MS.BANK_CSS}{MS.EXTRA_CSS}{CSS}</style>\n<script>{THEME_INIT}</script>\n"
        if not self.standalone:
            return f"<title>{TITLE}</title>\n{styles}{page}"
        return (f'<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n'
                f'<meta name="viewport" content="width=device-width, initial-scale=1">\n<meta name="color-scheme" content="dark light">\n'
                f'<title>{TITLE}</title>\n{pwa.head()}\n{styles}</head>\n<body>\n'
                f'<!-- GENERATED by build/campaign.py from messages/always-on/. Do not edit. -->\n{page}</body>\n</html>\n')


def render(entries: list[dict], *, standalone: bool = True) -> tuple[str, set[str]]:
    """The page, and the ids of the entries it anchors. `standalone=False` returns the body for an artifact."""
    c = Campaign(entries, standalone)
    return c.render(), c.rendered


CSS = r"""
:root{color-scheme:dark;--site-pad:clamp(calc(var(--space) * 5.5),5vw,calc(var(--space) * 14))}
@media (prefers-color-scheme: light){:root:not([data-theme="dark"]){color-scheme:light}}
:root[data-theme="light"]{color-scheme:light}
header.top{top:env(safe-area-inset-top,0px)}
header.top .tag{margin-left:auto}
@media(max-width:640px){.wrap{padding-inline:calc(var(--space) * 4)}}
.figs{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:calc(var(--space) * 4.5);margin:calc(var(--space) * 4.5) 0 calc(var(--space) * 7.5);align-items:start}
.stack{display:grid;gap:calc(var(--space) * 6.5);margin-top:calc(var(--space) * 4.5)}
.tall{display:flex;gap:calc(var(--space) * 4.5);flex-wrap:wrap;align-items:flex-start}
.tall figure{flex:1 1 160px}
figure{margin:0;min-width:0}
svg.art{display:block;width:100%;height:auto;max-width:100%}
figure svg.art{border:1px solid var(--border);border-radius:var(--radius-lg)}
figcaption{display:flex;justify-content:space-between;gap:calc(var(--space) * 1.5) calc(var(--space) * 3);flex-wrap:wrap;font-size:var(--a-micro);color:var(--muted);margin-top:calc(var(--space) * 2)}
figcaption a,.uses a{font-family:var(--mono);font-size:var(--a-micro)}
.uses{display:flex;flex-wrap:wrap;gap:calc(var(--space) * 1) calc(var(--space) * 3);font-size:var(--a-micro);color:var(--muted);margin:0 0 calc(var(--space) * 2)}
.site{border:1px solid var(--border);border-radius:var(--radius);overflow:hidden;background:var(--ink);margin:calc(var(--space) * 3.5) 0 calc(var(--space) * 2)}
.site .chrome{display:flex;align-items:center;gap:calc(var(--space) * 1.75);padding:calc(var(--space) * 2.25) calc(var(--space) * 3.5);border-bottom:1px solid var(--border);background:var(--panel)}
.site .chrome i{width:9px;height:9px;border-radius:50%;border:1px solid var(--rule);display:block}
.site .chrome .url{margin-left:calc(var(--space) * 2);font-family:var(--mono);font-size:var(--a-micro);color:var(--muted)}
.m-body{padding:var(--site-pad)}
.m-eyebrow{font-size:var(--a-micro);letter-spacing:.14em;text-transform:uppercase;color:var(--muted);font-weight:600;margin:0 0 calc(var(--space) * 4)}
.m-h1{font-family:var(--font-display);font-weight:700;font-size:clamp(var(--m-h3),4.6vw,var(--m-h2));line-height:1.04;letter-spacing:-.025em;color:var(--fg);margin:0;max-width:20ch;text-wrap:balance}
.m-h1.m-quiet{font-family:var(--font-display);color:var(--muted);margin-top:calc(var(--space) * 1.5)}
.m-h2{font-family:var(--font-display);font-weight:700;font-size:clamp(var(--m-h4),3.4vw,var(--m-h3));line-height:1.1;letter-spacing:-.02em;color:var(--fg);margin:0 0 calc(var(--space) * 3.5);max-width:26ch;text-wrap:balance}
.m-lead{font-size:var(--m-body);line-height:1.55;color:var(--body);max-width:58ch;margin:calc(var(--space) * 4) 0 0}
.m-actions{display:flex;align-items:center;gap:calc(var(--space) * 3.5);flex-wrap:wrap;margin-top:calc(var(--space) * 6.5)}
.m-btn{display:inline-block;background:var(--gold);color:var(--on-gold);border:1px solid var(--gold-deep);border-radius:var(--radius-lg);padding:calc(var(--space) * 2.5) calc(var(--space) * 4);font-weight:600;font-size:var(--m-micro)}
.m-quietbtn{display:inline-block;border:1px solid var(--border);border-radius:var(--radius-lg);padding:calc(var(--space) * 1.75) calc(var(--space) * 3);font-weight:600;font-size:var(--m-micro);color:var(--fg);margin-bottom:calc(var(--space) * 3)}
.m-url{font-family:var(--mono);font-size:var(--a-micro);color:var(--muted)}
.m-cat{font-size:var(--m-micro);color:var(--muted);margin:calc(var(--space) * 5.5) 0 0}
.m-hero{display:grid;grid-template-columns:minmax(0,1.35fr) minmax(0,1fr);gap:calc(var(--space) * 7);align-items:center}
.m-art svg{color:var(--fg)}
.m-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(210px,1fr));gap:calc(var(--space) * 3.5);margin-top:calc(var(--space) * 6.5)}
.m-card{border:1px solid var(--border);border-radius:var(--radius);padding:calc(var(--space) * 4) calc(var(--space) * 4.5);background:var(--panel);color:var(--fg);font-size:var(--m-body);line-height:1.5;margin:0;max-width:none}
.m-wall{columns:3 220px;column-gap:calc(var(--space) * 5.5);margin-top:calc(var(--space) * 6)}
.m-wall p{break-inside:avoid;font-family:var(--font-display);font-size:var(--m-h4);font-weight:600;line-height:1.25;letter-spacing:-.01em;color:var(--fg);margin:0 0 calc(var(--space) * 4)}
.m-center{text-align:center}
.m-center .m-h2{margin-inline:auto}
.m-center .m-actions{justify-content:center}
.cta-strip{display:flex;align-items:center;justify-content:space-between;gap:calc(var(--space) * 4.5);flex-wrap:wrap;border:1px solid var(--border);border-radius:var(--radius);background:var(--panel);padding:calc(var(--space) * 5.5) calc(var(--space) * 6);margin:calc(var(--space) * 3.5) 0 calc(var(--space) * 2)}
.cta-strip p{margin:0;font-family:var(--font-display);font-weight:700;font-size:clamp(var(--m-h4),2.6vw,var(--m-h3));line-height:1.15;letter-spacing:-.02em;color:var(--fg)}
.cta-strip .m-actions{margin-top:0}
.signoffs .so>p:first-child{font-family:var(--font-display);font-weight:600;font-size:var(--m-h4);line-height:1.3;color:var(--fg)}
.builder{display:grid;grid-template-columns:minmax(0,340px) minmax(0,1fr);gap:calc(var(--space) * 6);margin-top:calc(var(--space) * 5);align-items:start}
.builder label{display:block;font-size:var(--a-body);color:var(--muted);margin:calc(var(--space) * 3) 0 calc(var(--space) * 1)}
.builder label:first-child{margin-top:0}
.builder select{width:100%;font:inherit;font-size:var(--a-body);background:var(--panel);color:var(--fg);border:1px solid var(--border);border-radius:var(--radius-lg);padding:calc(var(--space) * 2) calc(var(--space) * 2.5)}
.builder .acts{display:flex;gap:calc(var(--space) * 2.5);flex-wrap:wrap;margin-top:calc(var(--space) * 4.5)}
.builder #b-status{min-height:1.6em;margin:calc(var(--space) * 2.5) 0 0;font-size:var(--a-body)}
.builder textarea{width:100%;margin-top:calc(var(--space) * 2);font-family:var(--mono);font-size:var(--a-micro);background:var(--void);color:var(--body);border:1px solid var(--border);border-radius:var(--radius-lg);padding:calc(var(--space) * 2.5)}
.builder .out svg{border:1px solid var(--border);border-radius:var(--radius-lg);margin-inline:auto}
.lead+p{max-width:70ch}
@media(max-width:860px){.builder{grid-template-columns:1fr}}
@media(max-width:760px){.m-hero{grid-template-columns:1fr}.m-art{max-width:320px}}
@media(max-width:640px){.builder select{font-size:var(--a-h4)}}
"""

THEME_INIT = r"""try{var t=localStorage.getItem("oxagen-theme");if(t==="light"||t==="dark")document.documentElement.dataset.theme=t}catch(e){}"""

THEME_JS = r"""(() => {
  const root = document.documentElement, btn = document.getElementById("theme");
  const now = () => root.dataset.theme || (matchMedia("(prefers-color-scheme: light)").matches ? "light" : "dark");
  const label = () => { btn.textContent = now() === "dark" ? "Light theme" : "Dark theme"; };
  btn.addEventListener("click", () => {
    const next = now() === "dark" ? "light" : "dark";
    root.dataset.theme = next;
    try { localStorage.setItem("oxagen-theme", next); } catch (e) { /* the theme holds for this visit */ }
    label();
  });
  label();
})();"""

#: A port of `ad()` above. The builder draws the same layout from the same widths.
BUILDER_JS = r"""(() => {
  const D = JSON.parse(document.getElementById("b-data").textContent);
  const $ = (id) => document.getElementById(id);
  const esc = (s) => String(s).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;");
  const n = (v) => String(Math.round(v * 100) / 100);
  const width = (s, z) => { let t = 0; for (const ch of s) t += D.advance[ch] ?? D.fallback; return t * z; };
  function wrap(text, z, maxW) {
    const lines = []; let cur = "";
    for (const w of text.split(/\s+/).filter(Boolean)) {
      const t = cur ? cur + " " + w : w;
      if (cur && width(t, z) > maxW * D.fit) { lines.push(cur); cur = w; } else cur = t;
    }
    if (cur) lines.push(cur);
    return lines;
  }
  function balanced(text, z, maxW) {
    let lines = wrap(text, z, maxW), target = maxW;
    for (let k = 0; k < 40 && lines.length > 1; k++) {
      const trial = wrap(text, z, target * 0.97);
      if (trial.length !== lines.length) break;
      target *= 0.97; lines = trial;
    }
    return lines;
  }
  function fit(text, z, floor, maxW) { while (z > floor && width(text, z) > maxW * D.fit) z *= 0.96; return z; }
  function action(cta, start, floor, maxW) {
    let c = fit(cta, start, floor, maxW);
    if (width(cta, c) > maxW * D.fit && cta.includes(" · ")) { cta = cta.split(" · ").pop(); c = fit(cta, start, floor, maxW); }
    return [cta, c];
  }
  function sublines(text, z, maxW) {
    if (!text) return [0, []];
    let sub = z * 0.44, lines = wrap(text, sub, maxW);
    while (lines.length > 2 && sub > z * 0.22) { sub *= 0.96; lines = wrap(text, sub, maxW); }
    return [sub, lines];
  }
  class Art {
    constructor(w, h, scheme, label) {
      const c = D.colors[scheme];
      Object.assign(this, { w, h, label, dark: scheme === "dark", ink: c.text, muted: c.muted, goldText: c.goldText,
        ground: c.ground, defs: [], body: [], k: 0, sh: "", short: Math.min(w, h) });
    }
    sheen() {
      if (!this.sh) {
        const [deep, gold, bright] = D.gold;
        this.defs.push(`<linearGradient id="b-sheen" x1="0" y1="1" x2="1" y2="0"><stop offset="0" stop-color="${deep}"/><stop offset="0.38" stop-color="${gold}"/><stop offset="0.56" stop-color="${bright}"/><stop offset="0.74" stop-color="${gold}"/><stop offset="1" stop-color="${deep}"/></linearGradient>`);
        this.sh = "url(#b-sheen)";
      }
      return this.sh;
    }
    glow(cx, cy, r, a) {
      if (!this.dark) return;
      const id = `b-glow${++this.k}`, g = D.gold[1];
      this.defs.push(`<radialGradient id="${id}"><stop offset="0" stop-color="${g}" stop-opacity="${n(a)}"/><stop offset="0.5" stop-color="${g}" stop-opacity="${n(a * 0.35)}"/><stop offset="1" stop-color="${g}" stop-opacity="0"/></radialGradient>`);
      this.body.push(`<circle cx="${n(cx)}" cy="${n(cy)}" r="${n(r)}" fill="url(#${id})"/>`);
    }
    text(x, y, s, z, weight, fill) {
      this.body.push(`<text x="${n(x)}" y="${n(y)}" font-size="${n(z)}" font-weight="${weight}" fill="${fill}">${esc(s)}</text>`);
    }
    rule(x, y, w, h) {
      this.body.push(`<rect x="${n(x)}" y="${n(y)}" width="${n(w)}" height="${n(h)}" rx="${n(Math.min(w, h) / 2)}" fill="${this.sheen()}"/>`);
    }
    wordmark(x, y, w) {
      const [ww, , ms, lx, ly] = D.wm, P = D.paths, g = D.gold[1];
      this.body.push(`<g transform="translate(${n(x)},${n(y)}) scale(${(w / ww).toFixed(5)})"><g transform="scale(${ms})"><path d="${P.hex}" fill="${this.ink}"/><path d="${P.cells}" fill="${g}"/></g><g transform="translate(${lx},${ly})"><path d="${P.letters}" fill="${this.ink}"/><path d="${P.x}" fill="${g}"/></g></g>`);
    }
    icon(cx, cy, span, hexes, cells, op) {
      const [iw, ih] = D.icon, s = span / Math.max(iw, ih), o = op == null ? "" : ` fill-opacity="${n(op)}"`;
      return `<g transform="translate(${n(cx)},${n(cy)}) scale(${s.toFixed(5)}) translate(${(-iw / 2).toFixed(3)},${(-ih / 2).toFixed(3)})"><path d="${D.paths.hex}" fill="${hexes}"${o}/><path d="${D.paths.cells}" fill="${cells}"/></g>`;
    }
    block(x, y, side, a) {
      return `<rect x="${n(x - side / 2)}" y="${n(y - side / 2)}" width="${n(side)}" height="${n(side)}" rx="${n(side * 0.24)}" fill="${this.sheen()}" opacity="${n(a)}"/>`;
    }
    ghost(cx, cy, span) {
      if (this.dark) {
        this.glow(cx, cy, span * 0.95, 0.42);
        const f = this.sheen();
        this.body.push(`<g opacity="0.16">${this.icon(cx, cy, span, f, f)}</g>`);
      } else {
        this.body.push(`<g opacity="0.55">${this.icon(cx, cy, span, this.ink, D.gold[1], 0.25)}</g>`);
      }
    }
    orbit(cx, cy, span, behind) {
      const start = this.body.length, short = this.short, hair = Math.max(1.2, short * 0.0009);
      const [radii, counts] = D.orbit, rings = [];
      radii.forEach((f, k) => {
        const r = span * f, pts = [];
        for (let i = 0; i < counts[k]; i++) {
          const a = k * 0.9 + 2 * Math.PI * i / counts[k] + 0.18 * Math.sin(i * 2.3 + k);
          const rr = r * (1 + 0.04 * Math.sin(i * 1.7 + k * 0.5));
          pts.push([cx + rr * Math.cos(a), cy + rr * Math.sin(a)]);
        }
        rings.push([r, pts]);
      });
      const [ringOp, wireOp, portOp] = this.dark ? [0.11, 0.16, 0.6] : [0.13, 0.18, 0.65];
      const line = (p, q) => `<line x1="${n(p[0])}" y1="${n(p[1])}" x2="${n(q[0])}" y2="${n(q[1])}"/>`;
      const nearest = (p, pts) => pts.reduce((b, q) => ((q[0] - p[0]) ** 2 + (q[1] - p[1]) ** 2 < (b[0] - p[0]) ** 2 + (b[1] - p[1]) ** 2 ? q : b));
      this.body.push(`<g fill="none" stroke="${this.ink}" stroke-width="${n(hair)}" opacity="${ringOp}">${rings.map(([r]) => `<circle cx="${n(cx)}" cy="${n(cy)}" r="${n(r)}"/>`).join("")}</g>`);
      let wires = "";
      for (let k = 1; k < rings.length; k++) for (const p of rings[k][1]) wires += line(p, nearest(p, rings[k - 1][1]));
      this.body.push(`<g stroke="${this.ink}" stroke-width="${n(hair)}" opacity="${wireOp}">${wires}</g>`);
      const [iw, ih] = D.icon, s = span / Math.max(iw, ih), ports = [];
      for (let d = 30; d < 360; d += 60) ports.push([cx + iw / 2 * 0.9 * s * Math.cos(d * Math.PI / 180), cy + ih / 2 * 0.9 * s * Math.sin(d * Math.PI / 180)]);
      this.body.push(`<g stroke="${D.gold[1]}" stroke-width="${n(hair * 1.6)}" stroke-linecap="round" opacity="${portOp}">${rings[0][1].map((p) => line(p, nearest(p, ports))).join("")}</g>`);
      let nodes = "";
      rings.forEach(([, pts], k) => {
        const fade = 1 - k * 0.16;
        pts.forEach(([x, y], i) => {
          if (k === 0) nodes += this.block(x, y, short * 0.016, 0.95);
          else if ([1, 5].includes((i * 5 + k * 3) % 9)) nodes += this.block(x, y, short * 0.011, 0.95 * fade);
          else nodes += `<circle cx="${n(x)}" cy="${n(y)}" r="${n(short * (0.0028 + 0.0025 * ((i * 7 + k) % 5) / 4))}" fill="${this.ink}" opacity="${n(0.55 * fade)}"/>`;
        });
      });
      this.body.push(nodes);
      this.glow(cx, cy, span * 1.3, 0.36);
      this.body.push(this.icon(cx, cy, span, this.ink, this.sheen()));
      if (behind != null) { const painted = this.body.splice(start).join(""); this.body.push(`<g opacity="${behind}">${painted}</g>`); }
    }
    svg() {
      const defs = this.defs.length ? `<defs>${this.defs.join("")}</defs>` : "";
      return `<svg xmlns="http://www.w3.org/2000/svg" class="art" viewBox="0 0 ${n(this.w)} ${n(this.h)}" width="${n(this.w)}" height="${n(this.h)}" font-family="${D.display}" role="img" aria-label="${esc(this.label)}">${defs}<rect width="${n(this.w)}" height="${n(this.h)}" fill="${this.ground}"/>${this.body.join("")}</svg>`;
    }
  }
  function ad(w, h, scheme, o) {
    const a = new Art(w, h, scheme, [o.kicker, o.text, o.subline, o.cta].filter(Boolean).join(" "));
    const short = a.short, pad = w * 0.085, maxW = w - 2 * pad;
    if (o.picture === "orbit") a.orbit(w * 0.88, h * 0.13, short * 0.15, a.dark ? 0.52 : 0.58);
    else a.ghost(w * 0.9, h * 0.12, short * 0.8);
    const markW = short * 0.4, markH = markW * D.wm[1] / D.wm[0], markCy = h - pad - markH / 2;
    let size = Math.min(w * 0.075, h * 0.105);
    const ceiling = pad + (o.kicker ? size * 0.035 / 0.075 * 2.2 : 0);
    let head = [], sub = 0, subs = [];
    for (let k = 0; k < 24; k++) {
      head = balanced(o.text, size, maxW);
      [sub, subs] = sublines(o.subline, size, maxW);
      const block = (head.length - 1) * size * 1.22 + size * 1.9 + (o.cta ? size * 0.85 : 0) + (subs.length ? size * 1.05 + (subs.length - 1) * sub * 1.3 : 0);
      const widest = Math.max(...head.map((l) => width(l, size)));
      if (markCy - markH / 2 - size * 0.9 - block >= ceiling && widest <= maxW * D.fit) break;
      size *= 0.94;
    }
    const lead = size * 1.22;
    a.wordmark(pad, markCy - markH / 2, markW);
    let y = markCy - markH / 2 - size * 0.9;
    if (o.cta) { const [words, c] = action(o.cta, size * 0.46, size * 0.24, maxW); a.text(pad, y, words, c, 500, a.muted); y -= size * 0.85; }
    const ruleH = Math.max(3, short * 0.011);
    a.rule(pad, y - ruleH, short * 0.13, ruleH);
    y -= ruleH + size * 0.95;
    if (subs.length) {
      subs.slice().reverse().forEach((s, j) => a.text(pad, y - j * sub * 1.3, s, sub, 500, a.ink));
      y -= (subs.length - 1) * sub * 1.3 + size * 1.05;
    }
    head.slice().reverse().forEach((s, i) => a.text(pad, y - i * lead, s, size, 700, a.ink));
    if (o.kicker) a.text(pad, y - (head.length - 1) * lead - lead * 0.95, o.kicker, short * 0.036, 600, a.goldText);
    return a.svg();
  }
  const ids = ["b-tagline", "b-intro", "b-close", "b-kicker", "b-size", "b-ground", "b-picture"];
  const status = $("b-status"), fallback = $("b-fallback"), out = $("b-out");
  function state() {
    const v = Object.fromEntries(ids.map((id) => [id.slice(2), $(id).value]));
    const mpu = v.size === "mpu";
    return {
      size: v.size, ground: v.ground, picture: v.picture, kicker: v.kicker || "",
      text: D.lines[v.tagline] || "",
      subline: mpu ? "" : (D.lines[v.intro] || ""),
      cta: mpu ? "" : (v.close === "cta" ? D.cta : (D.lines[v.close] || "")),
    };
  }
  function draw() {
    const s = state(), [w, h] = D.sizes[s.size];
    out.innerHTML = ad(w, h, s.ground, s);
    status.textContent = "";
    fallback.hidden = true;
  }
  function copy(text, what) {
    const done = () => { status.textContent = `${what} copied.`; fallback.hidden = true; };
    const manual = () => {
      fallback.value = text; fallback.hidden = false; fallback.focus(); fallback.select();
      status.textContent = "The browser blocked the clipboard. The text is selected below. Copy it from there.";
    };
    try { navigator.clipboard.writeText(text).then(done, manual); } catch (e) { manual(); }
  }
  ids.forEach((id) => $(id).addEventListener("change", draw));
  $("b-copy-text").addEventListener("click", () => {
    const s = state();
    copy([s.kicker, s.text, s.subline, s.cta].filter(Boolean).join("\n"), "Text");
  });
  $("b-copy-svg").addEventListener("click", () => { const svg = out.querySelector("svg"); if (svg) copy(svg.outerHTML, "SVG"); });
  draw();
})();"""
