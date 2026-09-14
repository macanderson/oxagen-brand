"""Small geometry the surfaces need: point-in-path, and a repeatable random.

The block mosaics and the constellations ask, thousands of times per canvas,
whether a point lies inside a brand mark. Stella's asterisk is a font outline
(cubics and quadratics), so it is flattened once into polygons and tested with
the non-zero winding rule, the same rule the renderer fills it with. Oxagen's
hive is built from primitives and tests itself analytically in `marks`.

The random here is `random.Random` seeded from a string. Python guarantees
`random()` reproduces the same sequence for the same seed across versions,
so a wallpaper built next year matches the one built today, pixel for pixel.
"""

from __future__ import annotations

import math
import random
import re
import zlib
from typing import Callable

Point = tuple[float, float]
Polygon = list[Point]

_TOKEN = re.compile(r"[MLHVQCZmlhvqcz]|-?\d*\.?\d+(?:e-?\d+)?")


def _bezier_points(pts: list[Point], steps: int) -> list[Point]:
    """`steps` points along a quadratic (3 pts) or cubic (4 pts) Bezier, the end included."""
    out = []
    n = len(pts)
    for i in range(1, steps + 1):
        t = i / steps
        if n == 3:
            (x0, y0), (x1, y1), (x2, y2) = pts
            u = 1 - t
            out.append((u * u * x0 + 2 * u * t * x1 + t * t * x2, u * u * y0 + 2 * u * t * y1 + t * t * y2))
        else:
            (x0, y0), (x1, y1), (x2, y2), (x3, y3) = pts
            u = 1 - t
            out.append(
                (
                    u**3 * x0 + 3 * u * u * t * x1 + 3 * u * t * t * x2 + t**3 * x3,
                    u**3 * y0 + 3 * u * u * t * y1 + 3 * u * t * t * y2 + t**3 * y3,
                )
            )
    return out


def flatten(d: str, steps: int = 8) -> list[Polygon]:
    """An SVG path (M L H V Q C Z, absolute or relative) as closed polygons."""
    toks = _TOKEN.findall(d)
    polys: list[Polygon] = []
    cur: Polygon = []
    x = y = 0.0
    sx = sy = 0.0
    i = 0
    cmd = ""

    def num() -> float:
        nonlocal i
        v = float(toks[i])
        i += 1
        return v

    while i < len(toks):
        t = toks[i]
        if t.isalpha():
            cmd = t
            i += 1
            if cmd in "Zz":
                if cur:
                    polys.append(cur)
                cur = []
                x, y = sx, sy
                continue
        rel = cmd.islower()
        c = cmd.upper()
        if c == "M":
            nx, ny = num(), num()
            if rel:
                nx, ny = x + nx, y + ny
            if cur:
                polys.append(cur)
            cur = [(nx, ny)]
            x, y, sx, sy = nx, ny, nx, ny
            cmd = "l" if rel else "L"
        elif c == "L":
            nx, ny = num(), num()
            if rel:
                nx, ny = x + nx, y + ny
            cur.append((nx, ny))
            x, y = nx, ny
        elif c == "H":
            nx = num()
            x = x + nx if rel else nx
            cur.append((x, y))
        elif c == "V":
            ny = num()
            y = y + ny if rel else ny
            cur.append((x, y))
        elif c == "Q":
            x1, y1, x2, y2 = num(), num(), num(), num()
            if rel:
                x1, y1, x2, y2 = x + x1, y + y1, x + x2, y + y2
            cur += _bezier_points([(x, y), (x1, y1), (x2, y2)], steps)
            x, y = x2, y2
        elif c == "C":
            x1, y1, x2, y2, x3, y3 = num(), num(), num(), num(), num(), num()
            if rel:
                x1, y1, x2, y2, x3, y3 = x + x1, y + y1, x + x2, y + y2, x + x3, y + y3
            cur += _bezier_points([(x, y), (x1, y1), (x2, y2), (x3, y3)], steps)
            x, y = x3, y3
        else:  # pragma: no cover - the pens here never emit S, T or A
            raise ValueError(f"unsupported path command {cmd!r}")
    if cur:
        polys.append(cur)
    return polys


def winding(polys: list[Polygon], px: float, py: float) -> int:
    """The non-zero winding number of (px, py) against a set of polygons."""
    wn = 0
    for poly in polys:
        n = len(poly)
        for j in range(n):
            x0, y0 = poly[j]
            x1, y1 = poly[(j + 1) % n]
            if y0 <= py:
                if y1 > py and (x1 - x0) * (py - y0) - (px - x0) * (y1 - y0) > 0:
                    wn += 1
            elif y1 <= py and (x1 - x0) * (py - y0) - (px - x0) * (y1 - y0) < 0:
                wn -= 1
    return wn


def path_hit(d: str) -> Callable[[float, float], bool]:
    """A test for `d`, with a bounding-box reject so the common case is cheap."""
    polys = flatten(d)
    xs = [p[0] for poly in polys for p in poly]
    ys = [p[1] for poly in polys for p in poly]
    x0, x1, y0, y1 = min(xs), max(xs), min(ys), max(ys)

    def hit(px: float, py: float) -> bool:
        if px < x0 or px > x1 or py < y0 or py > y1:
            return False
        return winding(polys, px, py) != 0

    return hit


# --------------------------------------------------------------------------


def rng(*seed: object) -> random.Random:
    """A generator whose sequence is fixed by its seed, wherever it is built."""
    key = zlib.crc32("|".join(str(s) for s in seed).encode()) & 0xFFFFFFFF
    return random.Random(key)


def scatter(
    r: random.Random,
    w: float,
    h: float,
    n: int,
    min_d: float,
    *,
    accept: Callable[[float, float], float] | None = None,
    tries: int = 40,
) -> list[Point]:
    """`n` points in a `w` x `h` box, none closer than `min_d`, by dart throwing.

    `accept(x, y)` returns the probability a candidate there is kept, which
    is how a composition leaves one corner quiet. A cell grid keeps the
    distance check linear, so a few thousand points cost nothing.
    """
    cell = min_d / math.sqrt(2)
    grid: dict[tuple[int, int], Point] = {}
    pts: list[Point] = []

    def ok(x: float, y: float) -> bool:
        gx, gy = int(x / cell), int(y / cell)
        for i in range(gx - 2, gx + 3):
            for j in range(gy - 2, gy + 3):
                p = grid.get((i, j))
                if p and (p[0] - x) ** 2 + (p[1] - y) ** 2 < min_d * min_d:
                    return False
        return True

    budget = n * tries
    while len(pts) < n and budget > 0:
        budget -= 1
        x, y = r.random() * w, r.random() * h
        if accept and r.random() > accept(x, y):
            continue
        if ok(x, y):
            grid[(int(x / cell), int(y / cell))] = (x, y)
            pts.append((x, y))
    return pts


def nearest(pts: list[Point], i: int, k: int) -> list[int]:
    """Indices of the `k` points nearest to `pts[i]`."""
    x, y = pts[i]
    order = sorted(
        (j for j in range(len(pts)) if j != i), key=lambda j: (pts[j][0] - x) ** 2 + (pts[j][1] - y) ** 2
    )
    return order[:k]


def dist(a: Point, b: Point) -> float:
    return math.hypot(a[0] - b[0], a[1] - b[1])


__all__ = ["Point", "dist", "flatten", "nearest", "path_hit", "rng", "scatter", "winding"]
