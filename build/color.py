"""OKLCH <-> sRGB, WCAG contrast, and the house spectrum.

The spectrum is the one colour decision this kit adds to stella's black-and-gold
system, so it is derived here rather than picked by eye. Five rays, one per arm
of the JetBrains Mono asterisk, at a single OKLCH lightness: equal perceived
lightness is what makes five hues read as one object instead of five stickers.
Stella's gold is one of the five, unchanged, which is what makes the two
wordmarks provably the same system rather than merely adjacent.
"""

from __future__ import annotations

import math

# --------------------------------------------------------------------------
# sRGB <-> linear <-> OKLab <-> OKLCH
# --------------------------------------------------------------------------


def _srgb_to_linear(c: float) -> float:
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def _linear_to_srgb(c: float) -> float:
    return 12.92 * c if c <= 0.0031308 else 1.055 * c ** (1 / 2.4) - 0.055


def hex_to_rgb(h: str) -> tuple[float, float, float]:
    h = h.lstrip("#")
    return tuple(int(h[i : i + 2], 16) / 255 for i in (0, 2, 4))  # type: ignore[return-value]


def rgb_to_hex(r: float, g: float, b: float) -> str:
    return "#%02X%02X%02X" % tuple(round(max(0.0, min(1.0, v)) * 255) for v in (r, g, b))


def rgb_to_oklab(r: float, g: float, b: float) -> tuple[float, float, float]:
    lr, lg, lb = (_srgb_to_linear(v) for v in (r, g, b))
    l = 0.4122214708 * lr + 0.5363325363 * lg + 0.0514459929 * lb
    m = 0.2119034982 * lr + 0.6806995451 * lg + 0.1073969566 * lb
    s = 0.0883024619 * lr + 0.2817188376 * lg + 0.6299787005 * lb
    l_, m_, s_ = (math.copysign(abs(v) ** (1 / 3), v) for v in (l, m, s))
    return (
        0.2104542553 * l_ + 0.7936177850 * m_ - 0.0040720468 * s_,
        1.9779984951 * l_ - 2.4285922050 * m_ + 0.4505937099 * s_,
        0.0259040371 * l_ + 0.7827717662 * m_ - 0.8086757660 * s_,
    )


def oklab_to_rgb(L: float, a: float, b: float) -> tuple[float, float, float]:
    l_ = L + 0.3963377774 * a + 0.2158037573 * b
    m_ = L - 0.1055613458 * a - 0.0638541728 * b
    s_ = L - 0.0894841775 * a - 1.2914855480 * b
    l, m, s = (v**3 for v in (l_, m_, s_))
    lr = +4.0767416621 * l - 3.3077115913 * m + 0.2309699292 * s
    lg = -1.2684380046 * l + 2.6097574011 * m - 0.3413193965 * s
    lb = -0.0041960863 * l - 0.7034186147 * m + 1.7076147010 * s
    return tuple(_linear_to_srgb(v) for v in (lr, lg, lb))  # type: ignore[return-value]


def oklch(L: float, C: float, H: float) -> tuple[float, float, float]:
    rad = math.radians(H)
    return oklab_to_rgb(L, C * math.cos(rad), C * math.sin(rad))


def hex_to_oklch(h: str) -> tuple[float, float, float]:
    L, a, b = rgb_to_oklab(*hex_to_rgb(h))
    return L, math.hypot(a, b), math.degrees(math.atan2(b, a)) % 360


def in_gamut(rgb: tuple[float, float, float], eps: float = 1e-4) -> bool:
    return all(-eps <= v <= 1 + eps for v in rgb)


def max_chroma(L: float, H: float, ceiling: float = 0.40) -> float:
    """Largest in-gamut chroma at this lightness and hue, to 1e-4."""
    lo, hi = 0.0, ceiling
    for _ in range(40):
        mid = (lo + hi) / 2
        if in_gamut(oklch(L, mid, H)):
            lo = mid
        else:
            hi = mid
    return lo


# --------------------------------------------------------------------------
# WCAG relative luminance and contrast
# --------------------------------------------------------------------------


def luminance(h: str) -> float:
    r, g, b = (_srgb_to_linear(v) for v in hex_to_rgb(h))
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast(a: str, b: str) -> float:
    la, lb = luminance(a), luminance(b)
    hi, lo = max(la, lb), min(la, lb)
    return (hi + 0.05) / (lo + 0.05)


# --------------------------------------------------------------------------
# the house spectrum
# --------------------------------------------------------------------------

GOLD = "#EFC53F"  # stella's brand metal, unchanged; ray 1 of 5
INK = "#0A0A0C"  # the canvas
PAPER = "#FFFCF5"  # the warm light canvas

#: Ray hues in OKLCH degrees, clockwise from twelve o'clock. Gold is measured
#: from the shipped token rather than typed, so recolouring gold moves the star.
GOLD_L, GOLD_C, GOLD_H = hex_to_oklch(GOLD)

#: The other four are a warm-to-cool sweep away from gold. Every adjacent gap
#: clears the 30-degree OKLCH separation floor stella's `hue-separation` gate
#: holds its web tokens to, so no two rays can be confused at avatar size.
RAY_NAMES = ("gold", "ember", "rose", "orchid", "azure")
RAY_HUES = (GOLD_H, 40.0, 350.0, 300.0, 220.0)

#: Chroma is capped just below the gamut edge so no ray clips to a flat primary
#: on a cheap panel, and every ray is capped at the same fraction of its own
#: maximum so none of them shouts over the others.
CHROMA_FRACTION = 0.98

#: The four non-gold rays share one lightness, chosen by rendering the mark at
#: 0.68, 0.72 and 0.76 against both grounds and looking at it. Above 0.72 the
#: rays go pastel and the star reads as confectionery; 0.68 keeps them jewelled
#: and still clears 6:1 on the ink canvas at every hue. Gold is left at its
#: shipped lightness (0.838) rather than dragged down to join them, because gold
#: is the house metal and is supposed to lead.
RAY_L = 0.68


def spectrum(L: float, *, anchor_gold: str | None = None) -> dict[str, str]:
    """Five rays at one perceived lightness, gold optionally pinned to a token."""
    out: dict[str, str] = {}
    for name, H in zip(RAY_NAMES, RAY_HUES):
        if name == "gold" and anchor_gold is not None:
            out[name] = anchor_gold
            continue
        out[name] = rgb_to_hex(*oklch(L, max_chroma(L, H) * CHROMA_FRACTION, H))
    return out


#: The star as it is drawn on every surface, light or dark. The gold ray is the
#: shipped stella token byte-for-byte, not a re-derivation of it, so recolouring
#: stella's metal recolours oxagen's star and the two cannot drift apart.
RESTING = spectrum(RAY_L, anchor_gold=GOLD)

#: The same five hues as *text* on warm paper, where a resting ray cannot clear
#: AA -- the reason stella ships `--st-gold-ink` beside its metal. Never used for
#: the mark itself, which keeps its resting colour on both grounds.
INK_L = 0.52
INKED = spectrum(INK_L)


if __name__ == "__main__":
    print(f"gold measured: L={GOLD_L:.4f} C={GOLD_C:.4f} H={GOLD_H:.2f}")
    print()
    hdr = f"{'ray':8} {'resting':9} {'on ink':>7} {'on paper':>9}   {'inked':9} {'on paper':>9}"
    print(hdr)
    print("-" * len(hdr))
    for name in RAY_NAMES:
        r, i = RESTING[name], INKED[name]
        print(
            f"{name:8} {r:9} {contrast(r, INK):7.2f} {contrast(r, PAPER):9.2f}   "
            f"{i:9} {contrast(i, PAPER):9.2f}"
        )
    print()
    hs = sorted(RAY_HUES)
    gaps = [min((b - a) % 360, (a - b) % 360) for a, b in zip(hs, hs[1:] + hs[:1])]
    print("adjacent OKLCH hue gaps:", ", ".join(f"{g:.0f}" for g in sorted(gaps)))
