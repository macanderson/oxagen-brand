"""Write `playbook.html`: the one document that explains the house system.

Every specimen on the page is emitted by the same functions that write the
files in this kit, so the playbook cannot describe a logo the kit does not
ship. Change the gold in `color.py` and the swatch, the contrast number, the
wallpaper and the downloadable PNG all move together on the next build.
"""

from __future__ import annotations

import html
from pathlib import Path

import color as C
import typeset as T
import glyphs as G
import surfaces as SF
from build import AD_COPY, CONTENT, TAGLINES, ad_svg
from marks import (
    BRANDS,
    HIVE,
    HIVE_CELLS,
    HIVE_HALF,
    SHIMMER_PERIOD,
    asterisk,
    favicon_svg,
    hive,
    hive_centre,
    icon_body,
    icon_svg,
    lockup_svg,
    sheen_defs,
    spinner_svg,
    spinner_wordmark_svg,
    wordmark_svg,
)

ROOT = Path(__file__).resolve().parent.parent

_n = [0]


def uid(p: str = "u") -> str:
    _n[0] += 1
    return f"{p}{_n[0]}"


def esc(s: str) -> str:
    return html.escape(s, quote=True)


# --------------------------------------------------------------------------
# specimens
# --------------------------------------------------------------------------


def construction_diagram(brand: str) -> str:
    """The wordmark with its ink box, baseline, x-height and em drawn over it."""
    spec = BRANDS[brand]
    m = G.wordmark(str(spec["text"]))
    plain, gold = G.glyph_paths(m, {str(spec["accent"])})
    w, h, base = float(m["width"]), float(m["height"]), float(m["baseline"])  # type: ignore[arg-type]
    f = G.font()
    upm = f["head"].unitsPerEm
    xh = base - f["OS/2"].sxHeight * G.EM / upm
    cap = base - f["OS/2"].sCapHeight * G.EM / upm
    pad = 24
    lines = [
        f'<rect x="0.5" y="0.5" width="{w - 1:.2f}" height="{h - 1:.2f}" fill="none" stroke="{C.GOLD}" stroke-width="0.8" stroke-dasharray="3 3" opacity="0.7"/>',
        f'<line x1="{-pad}" y1="{base:.2f}" x2="{w + pad:.2f}" y2="{base:.2f}" stroke="{C.GOLD}" stroke-width="0.8" opacity="0.9"/>',
        f'<line x1="{-pad}" y1="{xh:.2f}" x2="{w + pad:.2f}" y2="{xh:.2f}" stroke="currentColor" stroke-width="0.6" opacity="0.35" stroke-dasharray="2 3"/>',
        f'<line x1="{-pad}" y1="{cap:.2f}" x2="{w + pad:.2f}" y2="{cap:.2f}" stroke="currentColor" stroke-width="0.6" opacity="0.35" stroke-dasharray="2 3"/>',
    ]
    labels = [
        (w + pad - 2, base + 9, "baseline", C.GOLD),
        (w + pad - 2, xh + 9, "x-height", "currentColor"),
        (w + pad - 2, cap - 3, "cap height", "currentColor"),
        (2, h + 14, f"{w:.0f} x {h:.0f} box  ·  em {G.EM:.1f}  ·  Space Grotesk 600", "currentColor"),
    ]
    text = "".join(
        f'<text x="{x:.1f}" y="{y:.1f}" font-size="9" fill="{c}" text-anchor="{"end" if x > 100 else "start"}" '
        f'opacity="{0.9 if c == C.GOLD else 0.6}">{esc(t)}</text>'
        for x, y, t, c in labels
    )
    return (
        f'<svg viewBox="{-pad} -12 {w + pad * 2:.0f} {h + 34:.0f}" role="img" aria-label="{brand} wordmark construction" class="diagram">'
        f'<path d="{plain}" fill="none" stroke="currentColor" stroke-width="0.7" opacity="0.7"/>'
        f'<path d="{gold}" fill="{C.GOLD}" opacity="0.95"/>{"".join(lines)}{text}</svg>'
    )


def clearspace_diagram(brand: str) -> str:
    """Clear space is one accent glyph on every side."""
    spec = BRANDS[brand]
    m = G.wordmark(str(spec["text"]))
    plain, gold = G.glyph_paths(m, {str(spec["accent"])})
    acc = [g for g in m["glyphs"] if g["char"] == spec["accent"]][0]  # type: ignore[index]
    b = acc["bounds"]  # type: ignore[index]
    q = float(b[2]) - float(b[0])  # type: ignore[index]
    w, h = float(m["width"]) + q * 2, float(m["height"]) + q * 2  # type: ignore[arg-type]
    ghost = (
        f'<g transform="translate({q / 2 - (float(b[2]) + float(b[0])) / 2:.2f},{h / 2 - (float(b[3]) + float(b[1])) / 2:.2f})" opacity="0.35">'  # type: ignore[index]
        f'<path d="{acc["path"]}" fill="{C.GOLD}"/></g>'
    )
    return (
        f'<svg viewBox="0 0 {w:.0f} {h:.0f}" role="img" aria-label="{brand} clear space" class="diagram">'
        f'<rect x="0.5" y="0.5" width="{w - 1:.2f}" height="{h - 1:.2f}" fill="none" stroke="currentColor" stroke-width="0.8" stroke-dasharray="4 4" opacity="0.4"/>'
        f'<rect x="{q:.2f}" y="{q:.2f}" width="{m["width"]}" height="{m["height"]}" fill="{C.GOLD}" opacity="0.06"/>'
        f'<g transform="translate({q:.2f},{q:.2f})"><path d="{plain}" fill="currentColor"/><path d="{gold}" fill="{C.GOLD}"/></g>'
        f"{ghost}</svg>"
    )


def misuse_panel(kind: str, brand: str) -> str:
    """The ways the wordmark actually gets broken."""
    spec = BRANDS[brand]
    m = G.wordmark(str(spec["text"]))
    plain, gold = G.glyph_paths(m, {str(spec["accent"])})
    w, h = float(m["width"]), float(m["height"])  # type: ignore[arg-type]
    body = f'<path d="{plain}" fill="currentColor"/><path d="{gold}" fill="{C.GOLD}"/>'
    vb = f"-20 -20 {w + 40:.0f} {h + 40:.0f}"
    if kind == "all-gold":
        body = f'<path d="{plain} {gold}" fill="{C.GOLD}"/>'
    elif kind == "stretch":
        body = f'<g transform="translate(0,{h * 0.11:.1f}) scale(1,0.78)">{body}</g>'
    elif kind == "drawn-star":
        # a five-point star drawn by hand where the asterisk should be
        acc = [g for g in m["glyphs"] if g["char"] == spec["accent"]][0]  # type: ignore[index]
        b = acc["bounds"]  # type: ignore[index]
        cx, cy, r = (b[0] + b[2]) / 2, (b[1] + b[3]) / 2, (b[2] - b[0]) / 2  # type: ignore[index]
        import math

        pts = []
        for i in range(10):
            rr = r if i % 2 == 0 else r * 0.45
            a = math.radians(-90 + i * 36)
            pts.append(f"{cx + rr * math.cos(a):.1f},{cy + rr * math.sin(a):.1f}")
        body = f'<path d="{plain}" fill="currentColor"/><polygon points="{" ".join(pts)}" fill="{C.GOLD}"/>'
    elif kind == "icon-left":
        s = 0.9
        body = (
            f'<g transform="translate(0,{h * (1 - s) / 2:.1f}) scale({s})">'
            f'<path d="{plain}" fill="currentColor"/><path d="{gold}" fill="{C.GOLD}"/></g>'
        )
        ic = icon_svg("stella", box=h * 0.8, uid=uid("mu")).split(">", 1)[1].rsplit("</svg>", 1)[0]
        body = f'<g transform="translate({-h * 0.85:.1f},{h * 0.1:.1f})">{ic}</g>{body}'
        vb = f"-{h * 0.95:.0f} -20 {w + h + 20:.0f} {h + 40:.0f}"
    elif kind == "wrong-gold":
        body = f'<path d="{plain}" fill="currentColor"/><path d="{gold}" fill="#EFC53F"/>'
    elif kind == "outline":
        body = f'<path d="{plain} {gold}" fill="none" stroke="currentColor" stroke-width="1.5"/>'
    return (
        f'<svg viewBox="{vb}" role="img" aria-label="incorrect use" class="diagram">'
        f"{body}<line x1=\"-20\" y1=\"-20\" x2=\"{w + 20:.0f}\" y2=\"{h + 20:.0f}\" stroke=\"#C0392B\" stroke-width=\"1.2\" opacity=\"0.55\"/></svg>"
    )


def icon_construction() -> str:
    """The hive on its grid: the cell centres, the two pitches, the ink box.

    The mark is cells on a honeycomb, so what there is to show is the grid
    they sit on -- a centre for each cell, the pitch along a row and the
    pitch between rows -- and the box the outline reaches. Every number is
    one of the five in `HIVE`.
    """
    h = hive()
    x0, y0, x1, y1 = h["bounds"]  # type: ignore[misc]
    w, ht = float(x1) - float(x0), float(y1) - float(y0)
    pad = w * 0.10
    guides = [
        f'<rect x="{float(x0):.2f}" y="{float(y0):.2f}" width="{w:.2f}" height="{ht:.2f}" fill="none" '
        f'stroke="{C.GOLD}" stroke-width="0.25" stroke-dasharray="1.2 1.2" opacity="0.7"/>',
    ]
    dots = []
    for col, row, kind in HIVE_CELLS:
        cx, cy = hive_centre(col, row)
        dots.append(f'<circle cx="{cx:.2f}" cy="{cy:.2f}" r="0.45" fill="{C.GOLD}"/>')
    # the row pitch, measured between the first two rows on the left
    ax, ay = hive_centre(0, 0)
    bx, by = hive_centre(0, 1)
    cx2, cy2 = hive_centre(1, 0)
    guides.append(
        f'<path d="M{float(x0) - pad * 0.45:.2f} {ay:.2f}H{ax:.2f}M{float(x0) - pad * 0.45:.2f} {by:.2f}H{bx:.2f}" '
        f'stroke="currentColor" stroke-width="0.25" stroke-dasharray="0.8 0.8" opacity="0.4"/>'
        f'<path d="M{ax:.2f} {float(y0) - pad * 0.45:.2f}V{ay:.2f}M{cx2:.2f} {float(y0) - pad * 0.45:.2f}V{cy2:.2f}" '
        f'stroke="currentColor" stroke-width="0.25" stroke-dasharray="0.8 0.8" opacity="0.4"/>'
    )
    labels = [
        (float(x0), float(y0) - pad * 0.6, f"cell r {HIVE['r']:g} · w {HIVE['w']:g} · stroke {HIVE['stroke']:g}"),
        (float(x0), float(y1) + pad * 0.9, f"pitch {HIVE['px']:g} along a row · {HIVE['py']:g} between rows"),
        (float(x0), float(y1) + pad * 1.5, f"the half cell at {HIVE_HALF:g} · filled cells reach the outline's outer edge"),
    ]
    text = "".join(
        f'<text x="{x:.2f}" y="{y:.2f}" font-size="1.6" fill="currentColor" opacity="0.7">{esc(t)}</text>'
        for x, y, t in labels
    )
    vx, vy = float(x0) - pad, float(y0) - pad * 1.4
    vw, vh = w + pad * 2, ht + pad * 3.6
    return (
        f'<svg viewBox="{vx:.2f} {vy:.2f} {vw:.2f} {vh:.2f}" role="img" '
        f'aria-label="hive construction" class="diagram">'
        f'<g opacity="0.55">{icon_body("oxagen", letters="currentColor")}</g>'
        f'{"".join(guides)}{"".join(dots)}{text}</svg>'
    )


def icon_family() -> str:
    """Both icons at the same optical size on one line, the way they meet in the product."""
    st = icon_svg("stella", uid=uid("fam")).split(">", 1)[1].rsplit("</svg>", 1)[0]
    ox = icon_svg("oxagen", letters="currentColor", uid=uid("fam")).split(">", 1)[1].rsplit("</svg>", 1)[0]
    return (
        '<svg viewBox="0 0 220 96" role="img" aria-label="the two icons" class="diagram">'
        f'<g transform="translate(8,0)">{st}</g><g transform="translate(116,0)">{ox}</g>'
        '<path d="M110 20V76" stroke="currentColor" stroke-width="0.5" opacity="0.3"/></svg>'
    )


def favicon_row(brand: str) -> str:
    """The favicon at 16, 32 and 48, at true pixel size, from the PNGs the kit ships."""
    cells = "".join(
        f'<div><img src="icons/{brand}-icon-{s}.png" width="{s}" height="{s}" alt="{brand} favicon {s}"><span>{s}</span></div>'
        for s in (16, 32, 48)
    )
    return f'<div class="fav-row">{cells}<div><img src="icons/{brand}-icon-180.png" width="64" height="64" alt="{brand} app icon"><span>180 · app</span></div></div>'


def swatch_row(name: str, hexv: str, note: str) -> str:
    return (
        f'<tr><td><span class="chip" style="background:{hexv}"></span></td>'
        f'<td class="mono">--ox-{name}</td><td class="mono num">{hexv}</td>'
        f'<td class="num">{C.contrast(hexv, C.INK):.1f}<span class="unit">:1</span></td>'
        f'<td class="num">{C.contrast(hexv, C.PAPER):.1f}<span class="unit">:1</span></td>'
        f'<td class="note">{esc(note)}</td></tr>'
    )


def gold_card(label: str, hexv: str, note: str, *, sheen: bool = False) -> str:
    L, Cc, H = C.hex_to_oklch(hexv)
    bg = f"background:{hexv}"
    if sheen:
        bg = (
            f"background:linear-gradient(45deg,{C.GOLD_DEEP} 0%,{C.GOLD} 38%,"
            f"{C.GOLD_BRIGHT} 56%,{C.GOLD} 74%,{C.GOLD_DEEP} 100%)"
        )
    val = "sheen" if sheen else hexv
    lch = "" if sheen else f"<br>L {L:.2f} · C {Cc:.3f} · H {H:.0f}°"
    return (
        f'<div class="gold-card"><div class="gold-sw" style="{bg}"></div>'
        f'<div class="gold-meta"><b>{esc(label)}</b><span class="mono">{val}</span>'
        f'<span>{esc(note)}{lch}</span></div></div>'
    )


def plate(svg: str, cap: str, *, cls: str = "") -> str:
    return f'<figure class="m0"><div class="plate {cls}">{svg}</div><figcaption class="cap">{cap}</figcaption></figure>'


def inline(svg: str) -> str:
    """An SVG file body made safe to inline: no width/height, so CSS sizes it."""
    head, rest = svg.split(">", 1)
    head = head.replace('width="', 'data-w="').replace('height="', 'data-h="')
    return head + ">" + rest


# --------------------------------------------------------------------------
# the page
# --------------------------------------------------------------------------


FONT_FACES = T.font_faces("fonts/")


def css() -> str:
    return f"""
{FONT_FACES}
:root{{
  --ink:{C.INK};--void:{C.VOID};--panel:{C.PANEL};--hl:{C.HL};--border:{C.BORDER};--rule:{C.RULE};
  --fg:{C.PAPER_TEXT};--body:{C.TEXT};--muted:{C.MUTED};--dim:{C.DIM};
  --gold:{C.GOLD};--gold-bright:{C.GOLD_BRIGHT};--gold-deep:{C.GOLD_DEEP};--accent-text:{C.GOLD};
  --paper:{C.PAPER};--card:{C.PANEL};
  --shadow:0 1px 0 rgba(255,255,255,.03),0 18px 44px rgba(0,0,0,.5);
  --ox-font:{T.GEIST.css_stack};
  --ox-font-display:{T.SPACE_GROTESK.css_stack};
  --ox-font-mono:{T.MONASPACE_NEON.css_stack};
}}
@media(prefers-color-scheme:light){{:root:not([data-theme="dark"]){{
  --ink:{C.PAPER};--void:{C.PAPER_VOID};--panel:{C.PAPER_PANEL};--hl:{C.PAPER_HL};--border:{C.PAPER_BORDER};--rule:{C.PAPER_RULE};
  --fg:{C.INK_TEXT};--body:{C.TEXT_INK};--muted:{C.MUTED_INK};--dim:{C.DIM_INK};--accent-text:{C.GOLD_DEEP};
  --card:{C.PAPER_PANEL};--shadow:0 1px 0 rgba(255,255,255,.7),0 18px 44px rgba(9,9,11,.08);}}}}
:root[data-theme="light"]{{
  --ink:{C.PAPER};--void:{C.PAPER_VOID};--panel:{C.PAPER_PANEL};--hl:{C.PAPER_HL};--border:{C.PAPER_BORDER};--rule:{C.PAPER_RULE};
  --fg:{C.INK_TEXT};--body:{C.TEXT_INK};--muted:{C.MUTED_INK};--dim:{C.DIM_INK};--accent-text:{C.GOLD_DEEP};
  --card:{C.PAPER_PANEL};--shadow:0 1px 0 rgba(255,255,255,.7),0 18px 44px rgba(9,9,11,.08);}}
*,*::before,*::after{{box-sizing:border-box}}
html{{scroll-behavior:smooth;scroll-padding-top:78px}}
@media(prefers-reduced-motion:reduce){{html{{scroll-behavior:auto}}}}
body{{margin:0;background:var(--ink);color:var(--fg);font-family:var(--ox-font);font-size:16px;line-height:1.65;-webkit-font-smoothing:antialiased}}
.bar{{position:sticky;top:0;z-index:50;background:color-mix(in srgb,var(--ink) 88%,transparent);backdrop-filter:blur(14px);border-bottom:1px solid var(--border)}}
.bar-in{{max-width:1180px;margin:0 auto;padding:12px 28px;display:flex;align-items:center;gap:20px}}
.bar svg{{height:20px;width:auto;display:block}}
.bar nav{{display:flex;gap:16px;margin-left:auto;flex-wrap:wrap;align-items:center}}
.bar a,.bar button{{color:var(--muted);text-decoration:none;font-size:13px;font-weight:500;letter-spacing:.02em;padding:4px 0;border:0;background:none;font-family:inherit;cursor:pointer;border-bottom:1px solid transparent}}
.bar a:hover,.bar button:hover{{color:var(--fg);border-bottom-color:var(--accent-text)}}
.wrap{{max-width:1180px;margin:0 auto;padding:0 28px}}
section{{padding:72px 0;border-top:1px solid var(--rule)}}
section:first-of-type{{border-top:0}}
.eyebrow{{font-size:12px;letter-spacing:.14em;text-transform:uppercase;color:var(--accent-text);font-weight:600;margin:0 0 12px}}
h1,h2,h3{{font-family:var(--ox-font-display)}}
h1{{font-size:clamp(40px,6vw,64px);line-height:1.02;letter-spacing:-.02em;font-weight:700;margin:0 0 20px}}
h2{{font-size:32px;line-height:1.1;letter-spacing:-.015em;font-weight:700;margin:0 0 14px}}
h3{{font-size:19px;font-weight:600;margin:32px 0 10px}}
p{{max-width:66ch;color:var(--body);margin:0 0 14px}}
p.lead{{font-size:20px;line-height:1.5;color:var(--fg);max-width:56ch}}
.mono{{font-family:var(--ox-font-mono);font-feature-settings:{T.MONASPACE_NEON.features};font-size:.92em}}
.muted{{color:var(--muted)}}
a{{color:var(--accent-text)}}
code{{font-family:var(--ox-font-mono);font-feature-settings:{T.MONASPACE_NEON.features};font-size:.9em;background:var(--hl);padding:.1em .35em;border-radius:4px}}
pre{{background:var(--panel);border:1px solid var(--border);border-radius:10px;padding:16px 18px;overflow-x:auto;font-size:13.5px;line-height:1.55;color:var(--body)}}
pre code{{background:none;padding:0}}
.grid{{display:grid;gap:18px}}
.g2{{grid-template-columns:repeat(auto-fit,minmax(340px,1fr))}}
.g3{{grid-template-columns:repeat(auto-fit,minmax(260px,1fr))}}
.g4{{grid-template-columns:repeat(auto-fit,minmax(200px,1fr))}}
.plate{{background:var(--panel);border:1px solid var(--border);border-radius:14px;padding:34px 28px;display:flex;align-items:center;justify-content:center;min-height:150px;overflow:hidden;color:var(--fg)}}
.plate.ink{{background:{C.INK};color:{C.PAPER_TEXT};border-color:{C.BORDER}}}
.plate.paper{{background:{C.PAPER};color:{C.INK_TEXT};border-color:{C.PAPER_BORDER}}}
.plate.tight{{padding:0;min-height:0;display:block}}
.plate.tight svg{{display:block;width:100%;height:auto}}
.plate>svg{{max-width:100%;height:auto}}
.plate.wm>svg{{width:min(100%,420px)}}
.plate.big>svg{{width:min(100%,560px)}}
.plate.icon>svg{{width:120px;height:120px}}
.plate.sp>svg{{width:88px;height:88px}}
.m0{{margin:0}}
.cap{{font-size:12.5px;color:var(--muted);margin-top:8px;letter-spacing:.01em}}
.diagram{{width:100%;height:auto;color:var(--fg);font-family:var(--ox-font-mono)}}
.hero{{padding:90px 0 60px}}
.hero .plates{{margin-top:36px}}
table{{border-collapse:collapse;width:100%;font-size:14px}}
th,td{{text-align:left;padding:10px 12px;border-bottom:1px solid var(--border);vertical-align:middle}}
th{{font-size:12px;letter-spacing:.08em;text-transform:uppercase;color:var(--muted);font-weight:600}}
td.num{{font-variant-numeric:tabular-nums}}
.unit{{color:var(--dim);font-size:.85em}}
.chip{{display:inline-block;width:28px;height:28px;border-radius:7px;border:1px solid var(--border)}}
.note{{color:var(--muted)}}
.gold-card{{background:var(--card);border:1px solid var(--border);border-radius:14px;overflow:hidden}}
.gold-sw{{height:110px}}
.gold-meta{{padding:14px 16px;display:grid;gap:4px;font-size:13.5px;color:var(--muted)}}
.gold-meta b{{color:var(--fg);font-size:15px}}
.rules{{list-style:none;padding:0;margin:0;display:grid;gap:12px;max-width:70ch}}
.rules li{{padding-left:26px;position:relative;color:var(--body)}}
.rules li::before{{content:"*";position:absolute;left:0;top:-2px;color:var(--gold);font-weight:700;font-size:22px;line-height:1}}
.rules b{{color:var(--fg)}}
.type-row{{display:grid;grid-template-columns:120px 1fr;gap:16px;align-items:baseline;padding:12px 0;border-bottom:1px solid var(--border)}}
.type-row .mono{{color:var(--muted);font-size:12.5px}}
.bad .cap::before{{content:"✕  ";color:#C0392B}}
.files{{display:grid;grid-template-columns:200px 1fr;gap:8px 20px;font-size:14px}}
.files .mono{{color:var(--fg)}}
.files span{{color:var(--muted)}}
footer{{padding:48px 0 80px;border-top:1px solid var(--rule);color:var(--muted);font-size:13.5px}}
.shimmer-demo svg{{width:min(100%,420px);height:auto}}
.favs{{display:flex;gap:28px;flex-wrap:wrap;margin-top:14px}}
.fav-row{{display:flex;align-items:flex-end;gap:14px;background:var(--panel);border:1px solid var(--border);border-radius:14px;padding:18px 20px}}
.fav-row img{{display:block;image-rendering:auto}}
.fav-row span{{font-size:11.5px;color:var(--muted);display:block;text-align:center;margin-top:6px}}
"""


def build_html() -> str:
    ox_d = inline(wordmark_svg("oxagen", uid=uid("w")))
    ox_l = inline(wordmark_svg("oxagen", letters=C.INK_TEXT, uid=uid("w")))
    st_d = inline(wordmark_svg("stella", uid=uid("w")))
    st_l = inline(wordmark_svg("stella", letters=C.INK_TEXT, uid=uid("w")))
    bar = inline(wordmark_svg("oxagen", letters="currentColor", uid=uid("bar")))

    st_m = G.wordmark("stella*")
    ox_m = G.wordmark("oxagen")
    a = asterisk()

    tokens_rows = "".join(swatch_row(n, v, note) for n, v, note in C.TOKENS)
    face_name = {"display": "Space Grotesk", "sans": "Geist", "mono": "Monaspace Neon"}
    scale_rows = "".join(
        f"<tr><td class=\"mono\">{m.name}</td><td>{face_name[m.face]}</td>"
        f"<td class=\"mono\">{m.px} · {m.leading} · {m.weight}</td><td class=\"mono\">{a.px} · {a.leading} · {a.weight}</td></tr>"
        for m, a in zip(T.MARKETING.steps, T.APP.steps)
    )
    gold_cards = "".join(
        [
            gold_card("gold", C.GOLD, "the metal. identity and one action per screen"),
            gold_card("gold-bright", C.GOLD_BRIGHT, "what the shimmer passes through; hover on ink"),
            gold_card("gold-deep", C.GOLD_DEEP, "gold as text on paper; small gold details there"),
            gold_card("gold-sheen", C.GOLD, "the metallic gradient for tiles and hero use", sheen=True),
        ]
    )

    walls = "".join(
        plate(SF.wallpaper_desktop(1600, 900, b, s, st), f"{b} desktop · {st} · {s}", cls="tight")
        for b, s, st in (
            ("oxagen", "dark", "graph"),
            ("oxagen", "light", "blocks"),
            ("stella", "dark", "orbit"),
            ("stella", "light", "graph"),
            ("oxagen", "dark", "glow"),
            ("stella", "light", "quiet"),
        )
    )
    phones = "".join(
        plate(SF.wallpaper_phone(430, 932, b, s, st), f"{b} iphone · {st} · {s}", cls="tight")
        for b, s, st in (("oxagen", "dark", "blocks"), ("stella", "dark", "graph"), ("oxagen", "light", "orbit"), ("stella", "light", "glow"))
    )
    social = "".join(
        [
            plate(SF.avatar("stella", 400, "dark"), "stella avatar · 1024", cls="tight"),
            plate(SF.avatar("oxagen", 400, "dark"), "oxagen avatar · 1024", cls="tight"),
            plate(SF.avatar("stella", 400, "light"), "stella avatar · paper", cls="tight"),
            plate(SF.avatar("oxagen", 400, "light"), "oxagen avatar · paper", cls="tight"),
        ]
    )
    banners = "".join(
        [
            plate(SF.banner(1500, 500, "oxagen", "dark", tagline=TAGLINES["oxagen"]), "oxagen · x header 1500×500", cls="tight"),
            plate(SF.banner(1500, 500, "stella", "light", tagline=TAGLINES["stella"]), "stella · x header, paper", cls="tight"),
            plate(SF.og_card(1200, 630, "stella", "dark", tagline=TAGLINES["stella"]), "stella · open graph 1200×630", cls="tight"),
            plate(SF.og_card(1200, 630, "oxagen", "light", tagline=TAGLINES["oxagen"]), "oxagen · open graph, paper", cls="tight"),
        ]
    )
    ads = []
    for b, slug, w, h, tag, s in (
        ("oxagen", "mission-control", 1080, 1350, "portrait", "dark"),
        ("oxagen", "authority", 1080, 1080, "square", "light"),
        ("oxagen", "equipment", 1200, 628, "landscape", "dark"),
        ("oxagen", "finance", 300, 250, "mpu", "light"),
        ("oxagen", "finance", 1080, 1080, "square", "dark"),
        ("oxagen", "keys", 1200, 628, "landscape", "light"),
        ("stella", "proof", 1080, 1080, "square", "dark"),
        ("stella", "check", 1200, 628, "landscape", "light"),
    ):
        cp = next(c for c in AD_COPY[b] if c["slug"] == slug)
        ads.append(plate(ad_svg(b, cp, w, h, tag, s), f"{b} · {slug} · {w}×{h} · {s}", cls="tight"))
    cards = []
    for b, want, s in (
        ("stella", "Changelog", "dark"),
        ("oxagen", "Field note", "light"),
        ("oxagen", "Fleet note", "dark"),
    ):
        kind, title, meta, body = next(c for c in CONTENT[b] if c[0] == want)
        cards.append(plate(SF.content_card(1200, 675, b, s, kind=kind, title=title, meta=meta, body=body), f"{b} · {kind.lower()} card · {s}", cls="tight"))

    files = [
        ("playbook.html", "this document"),
        ("message-bank.html", "every line, generated from messages/"),
        ("messages/", "the message registry: one YAML file per line, with its status, scope, evidence, and owner"),
        ("build/", "color.py · glyphs.py · geom.py · marks.py · surfaces.py · build.py · messages.py · playbook.py"),
        ("build/reference/", "the kit wordmark and logomark this system is checked against"),
        ("fonts/", "Space Grotesk, variable and static, with its licence"),
        ("tokens/", "house-tokens.css · house-tokens.json"),
        ("logo/svg, logo/png", "wordmarks, icons, the oxagen lockup: dark · light · adaptive · mono · sheen · tiles"),
        ("icons/", "favicons and app icons, 16 to 512"),
        ("spinners/", "the house motion, animated SVG, no script"),
        ("wallpapers/", "desktop 4K/5K/6K · iphone ×3 · glow | quiet | graph | blocks | orbit · dark | light"),
        ("social/", "avatar · x · linkedin · youtube · open graph · dark | light"),
        ("ads/", "mission-control · authority · equipment · finance · keys · stella proof · check · 1080×1080 · 1080×1350 · 1200×628 · 300×250"),
        ("content/", "changelog · essay · release · field note · fleet note cards, 1200×675"),
    ]
    files_html = "".join(f'<div class="mono">{esc(k)}</div><span>{esc(v)}</span>' for k, v in files)

    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Oxagen house system</title>
<meta name="color-scheme" content="dark light">
<style>{css()}</style>
</head>
<body>
<div class="bar"><div class="bar-in">{bar}
<nav><a href="#logos">Logos</a><a href="#icons">Icons</a><a href="#colour">Colour</a><a href="#type">Type</a><a href="#motion">Motion</a><a href="#surfaces">Surfaces</a><a href="#files">Files</a>
<button type="button" id="theme" aria-label="toggle theme">◐</button></nav></div></div>

<main class="wrap">

<section class="hero">
<p class="eyebrow">Oxagen house system · v2.3</p>
<h1>One house.<br>Two names. One gold.</h1>
<p class="lead">Everything a customer sees from Oxagen and Stella comes from one system: obsidian and white, three faces, and a single gold that each name carries in exactly one glyph.</p>
<div class="grid g2 plates">
{plate(ox_d, "oxagen · on ink", cls="ink wm")}
{plate(st_d, "stella* · on ink", cls="ink wm")}
{plate(ox_l, "oxagen · on paper", cls="paper wm")}
{plate(st_l, "stella* · on paper", cls="paper wm")}
</div>
</section>

<section id="decision">
<p class="eyebrow">The decision</p>
<h2>Oxagen's kit is the house kit</h2>
<p>The Oxagen brand kit already had the right bones: Space Grotesk and a wordmark whose only colour is one gold letter. This system takes that kit as the base and brings Stella onto it. Since September 2026 it sits on obsidian <span class="mono">{C.INK}</span> and white, with neutral greys between, so the gold is the only warm value on a screen.</p>
<p><b>oxagen</b> is the kit's wordmark, reproduced from the font: the word in Space Grotesk 600, lowercase, its <b>x</b> in gold. <b>stella*</b> is the same word treatment followed by the font's own asterisk, in the same gold. The asterisk is a character, not a drawing; it was never redrawn, and it must not be.</p>
<p>The gold is <span class="mono">{C.GOLD}</span>. Both names use it at the same value, so the two marks cannot drift apart.</p>
<ul class="rules">
<li><b>One glyph is gold.</b> The x in oxagen, the asterisk in stella. Never a second one.</li>
<li><b>Gold is identity, and one action per screen.</b> It is never a surface, and it never means a state.</li>
<li><b>Gold as text on paper becomes gold-deep.</b> The mark keeps its metal; words do not.</li>
<li><b>Nothing sits to the left of stella.</b> The asterisk is the only mark. Oxagen's lockup is the one exception, and only for Oxagen.</li>
<li><b>The hive is two colours, and only two.</b> Its outlines take the colour of whatever it sits on -- paper on ink, ink on paper, <code>currentColor</code> in the adaptive files -- and its two lit cells take the metal. Nothing else in it is ever coloured, and a mono file paints all of it one colour.</li>
<li><b>The icon is the only picture we own.</b> No stock illustration, no gradient mesh, no 3D render. A surface that needs a picture builds one out of the icon -- its outline, its mosaic, a field around it -- or simply uses a bigger one.</li>
</ul>
</section>

<section id="logos">
<p class="eyebrow">Logos</p>
<h2>Two wordmarks, one em</h2>
<p>Both are set at the same size, {G.EM:.1f} px per em, the size the kit's <code>oxagen</code> outline was frozen at. Each sits in an ink-tight box, so <code>oxagen</code> ({ox_m['width']:.0f}×{ox_m['height']:.0f}) and <code>stella*</code> ({st_m['width']:.0f}×{st_m['height']:.0f}) are the same height to within a pixel and the same letter size exactly.</p>
<div class="grid g2">
{plate(construction_diagram("oxagen"), "oxagen · construction")}
{plate(construction_diagram("stella"), "stella* · construction")}
</div>
<h3>The asterisk</h3>
<p>Space Grotesk's asterisk is a six-armed, cap-height glyph, {a['w']:.0f} units square at the logo em. It sits where the font puts it after an <code>a</code>, with no added space and no kerning. It is the same glyph in the wordmark, the icon, the favicon and the wallpaper.</p>
<div class="grid g2">
{plate(clearspace_diagram("oxagen"), "clear space: one x on every side")}
{plate(clearspace_diagram("stella"), "clear space: one asterisk on every side")}
</div>
<h3>Variants that ship</h3>
<div class="grid g3">
{plate(inline(wordmark_svg("stella", adaptive=True, uid=uid("v"))), "adaptive: letters follow the page, gold stays", cls="wm")}
{plate(inline(wordmark_svg("oxagen", mono="currentColor")), "mono: currentColor, for one-colour print", cls="wm")}
{plate(inline(wordmark_svg("stella", sheen=True, uid=uid("v"))), "sheen: the metallic gradient, for hero sizes", cls="ink wm")}
</div>
<h3>The oxagen lockup</h3>
<p>Oxagen alone has a lockup: the hive, a gap, then the word. The hive stands a quarter taller than the wordmark's box and centres on it; the gap is a little over half an x-height. The wordmark on its own is still the preferred mark -- the lockup is for the places that want a picture beside the name, a masthead or an app's title bar. Stella has no lockup; its asterisk is already in the word.</p>
<div class="grid g2">
{plate(inline(lockup_svg(uid=uid("lk"))), "oxagen lockup · on ink", cls="ink big")}
{plate(inline(lockup_svg(letters=C.INK_TEXT, uid=uid("lk"))), "oxagen lockup · on paper", cls="paper big")}
{plate(inline(lockup_svg(sheen=True, uid=uid("lk"))), "oxagen lockup · sheen, for hero sizes", cls="ink big")}
{plate(inline(lockup_svg(mono="currentColor", uid=uid("lk"))), "oxagen lockup · mono", cls="big")}
</div>
<h3>Minimum sizes</h3>
<p>Wordmark 88 px wide on screen, 24 mm in print. Icon 24 px, 8 mm. Lockup 120 px, 32 mm. Below that, use the favicon.</p>
<h3>Do not</h3>
<div class="grid g3">
<div class="bad">{plate(misuse_panel("all-gold", "stella"), "paint the whole word gold")}</div>
<div class="bad">{plate(misuse_panel("drawn-star", "stella"), "draw a star where the asterisk goes")}</div>
<div class="bad">{plate(misuse_panel("icon-left", "stella"), "put an icon to the left of stella")}</div>
<div class="bad">{plate(misuse_panel("wrong-gold", "oxagen"), "use another gold")}</div>
<div class="bad">{plate(misuse_panel("stretch", "oxagen"), "stretch or condense")}</div>
<div class="bad">{plate(misuse_panel("outline", "oxagen"), "outline it")}</div>
</div>
</section>

<section id="icons">
<p class="eyebrow">Icons</p>
<h2>The asterisk and the hive</h2>
<p>Where a square is required, Stella uses its asterisk and Oxagen uses the hive: six hexagonal cells on a honeycomb grid, four drawn as an outline and two filled with the metal, one of them at half strength. It is the knowledge graph as a picture -- a lattice, with the parts Oxagen has learned lit up -- and it is built from five numbers, not drawn: a cell's height and width, the pitch along a row, the pitch between rows, and the outline's weight. The cells are a touch wider than a regular hexagon, which is what makes the cluster stand square.</p>
<p>The hive is two colours. Its outlines take the colour of the surface it sits on, and its two lit cells take the metal -- flat gold in the plain files, and the metal lit from above in the tiles. Do not add a third colour, do not fill the outlined cells, do not rotate it, and do not move a cell.</p>
<div class="grid g2">
{plate(icon_construction(), "construction: the grid the cells sit on")}
{plate(icon_family(), "the family: asterisk and hive, side by side")}
</div>
<div class="grid g4">
{plate(inline(icon_svg("stella", uid=uid("i"))), "stella icon · on ink", cls="ink icon")}
{plate(inline(icon_svg("oxagen", uid=uid("i"))), "oxagen icon · on ink", cls="ink icon")}
{plate(inline(icon_svg("stella", letters=C.INK_TEXT, uid=uid("i"))), "stella icon · on paper", cls="paper icon")}
{plate(inline(icon_svg("oxagen", letters=C.INK_TEXT, uid=uid("i"))), "oxagen icon · on paper", cls="paper icon")}
{plate(inline(icon_svg("stella", background=C.INK, radius=20, sheen=True, uid=uid("i"))), "stella tile · sheen", cls="icon")}
{plate(inline(icon_svg("oxagen", background=C.INK, radius=20, sheen=True, uid=uid("i"))), "oxagen tile · sheen", cls="icon")}
{plate(inline(icon_svg("stella", background=C.PAPER, letters=C.INK_TEXT, radius=20, sheen=True, uid=uid("i"))), "stella tile · paper", cls="icon")}
{plate(inline(icon_svg("oxagen", background=C.PAPER, letters=C.INK_TEXT, radius=20, sheen=True, uid=uid("i"))), "oxagen tile · paper", cls="icon")}
</div>
<p style="margin-top:18px">At 16 to 48 px both icons survive as themselves, and neither is redrawn to get there. The hive is six cells on a grid, which is what a 16 px grid can hold; only its outline is thickened, so the ink cells do not fall between pixels. The fill fraction goes up too -- at 16 px the mark takes almost the whole square, because the padding a 256 px tile wants is four pixels a favicon cannot spare. The small PNGs come from a favicon tile on ink, because an outline on nothing is no favicon on a tab that happens to be its colour.</p>
<div class="favs">{favicon_row("oxagen")}{favicon_row("stella")}</div>
</section>

<section id="colour">
<p class="eyebrow">Colour</p>
<h2>One metal, two grounds</h2>
<p>The gold is <span class="mono">{C.GOLD}</span>, and its two neighbours are derived from it in OKLCH, not picked: gold-bright is lighter, for the moment the shimmer passes, and gold-deep is darker and a few degrees warmer, for gold set as text on white. The build fails if a pinned value stops matching its derivation. gold clears {C.contrast(C.GOLD, C.INK):.1f}:1 on obsidian; on white it is {C.contrast(C.GOLD, C.PAPER):.1f}:1, which is why gold as <em>text</em> on white becomes gold-deep at {C.contrast(C.GOLD_DEEP, C.PAPER):.1f}:1.</p>
<div class="grid g4" style="margin:22px 0 34px">{gold_cards}</div>
<h3>Every token</h3>
<div style="overflow-x:auto"><table>
<thead><tr><th></th><th>token</th><th>value</th><th>on ink</th><th>on paper</th><th>use</th></tr></thead>
<tbody>{tokens_rows}</tbody></table></div>
<p class="muted" style="margin-top:14px;font-size:13.5px">Contrast is WCAG 2.x. Text tokens clear 4.5:1 on their own ground; the build checks it.</p>
</section>

<section id="type">
<p class="eyebrow">Type</p>
<h2>Three faces, each with one job</h2>
<p><b>Space Grotesk</b> sets the wordmarks and h1 to h3, and nothing smaller than 20 px: its wide geometric letters lose their shape below that. <b>Geist</b> sets h4 to h6 and everything read: body, labels, buttons, tables, navigation. <b>Monaspace Neon</b> sets code, logs, digests, paths, ids, and the numbers in tables, with texture healing and code ligatures on.</p>
<div class="type-row"><span class="mono">display · 700</span><span style="font-family:var(--ox-font-display);font-weight:700;font-size:40px;line-height:1.05;letter-spacing:-.03em">Mission Control for your autonomous agents.</span></div>
<div class="type-row"><span class="mono">display · 600</span><span style="font-family:var(--ox-font-display);font-weight:600;font-size:26px;line-height:1.2">See which agent spent what.</span></div>
<div class="type-row"><span class="mono">text · 600</span><span style="font-weight:600;font-size:16px">Runs waiting for approval</span></div>
<div class="type-row"><span class="mono">text · 400</span><span style="font-weight:400;font-size:16px;color:var(--body)">A rule the owning team wrote answers each request: allowed, denied, or routed to a person.</span></div>
<div class="type-row"><span class="mono">code · 400</span><span style="font-family:var(--ox-font-mono);font-feature-settings:{T.MONASPACE_NEON.features};font-size:14px">oxagen dod verify --run 4f2c  =&gt;  held</span></div>
<h3>Two scales</h3>
<p>A surface picks one scale and keeps it. <b>marketing</b> (<span class="mono">text-m-*</span>) is large and spaced, for a page read once. <b>app</b> (<span class="mono">text-a-*</span>) is dense, for panels, tables, and logs read all day.</p>
<div style="overflow-x:auto"><table>
<thead><tr><th>step</th><th>face</th><th>marketing</th><th>app</th></tr></thead>
<tbody>{scale_rows}</tbody></table></div>
<p class="muted" style="margin-top:14px;font-size:13.5px">Sizes in px, then line height and weight. <span class="mono">tokens/house-tailwind.css</span> carries both scales as Tailwind v4 utilities; <span class="mono">tokens/next-fonts.ts</span> loads the three faces with next/font.</p>
</section>

<section id="motion">
<p class="eyebrow">Motion</p>
<h2>Light passes over the metal</h2>
<p>The house motion is the shimmer: a band of light crosses the mark every {SHIMMER_PERIOD:g} seconds. Stella's asterisk turns a sixth of a turn, its own symmetry, as the light passes over its gold. The hive takes the same band over all of it: its outline is held at a third strength and the band brings it up to full, and its two cells catch the highlight as the band crosses them. Same band, same tilt, same easing -- one gesture, made in hue on the metal and in brightness on the ink. All of it is CSS inside the SVG; it runs in an <code>&lt;img&gt;</code> with no script, and <code>prefers-reduced-motion</code> lands it on a still mark at full strength.</p>
<div class="grid g4">
{plate(inline(spinner_svg("stella", uid=uid("sp"))), "stella spinner", cls="ink sp")}
{plate(inline(spinner_svg("oxagen", uid=uid("sp"))), "oxagen spinner", cls="ink sp")}
{plate(inline(spinner_svg("stella", background=C.INK, uid=uid("sp"))), "stella spinner · tile", cls="sp")}
{plate(inline(spinner_svg("oxagen", background=C.INK, uid=uid("sp"))), "oxagen spinner · tile", cls="sp")}
</div>
<div class="grid g2 shimmer-demo" style="margin-top:18px">
{plate(inline(spinner_wordmark_svg("stella", uid=uid("sw"))), "stella · loading masthead", cls="ink wm")}
{plate(inline(spinner_wordmark_svg("oxagen", uid=uid("sw"))), "oxagen · loading masthead", cls="ink wm")}
</div>
</section>

<section id="surfaces">
<p class="eyebrow">Surfaces</p>
<h2>One composition rule</h2>
<p>A surface is a ground, one bloom of the metal, the brand's own icon placed off-centre, and at most a few lines of type. When a surface needs more than a mark, it builds the picture out of the mark. Every surface below is the vector the kit ships, not a screenshot.</p>
<h3>Wallpapers, five ways</h3>
<p><b>graph</b> scatters nodes across the ground, wires each to its two nearest neighbours, and runs gold edges from the mark out to the nodes nearest it: the one-to-many, drawn. <b>blocks</b> rebuilds the mark from blocks on a grid, each tile a shade brighter or deeper than the next, with a bloom of fainter blocks around it. <b>orbit</b> hangs five rings of nodes off the mark, each node wired inward to the ring inside it. <b>glow</b> and <b>quiet</b> are the mark alone, as a bloom and as a hairline -- and both are pulled back inside the canvas rather than cropped, because a mark clipped by a few per cent of its width reads as a mistake and not as a crop. Every node is placed by a seeded random, so the same file comes out of every build.</p>
<div class="grid g2">{walls}</div>
<div class="grid g4" style="margin-top:18px">{phones}</div>
<h3>Social</h3>
<div class="grid g4">{social}</div>
<div class="grid g2" style="margin-top:18px">{banners}</div>
<h3>Ads</h3>
<p>Every ad takes its copy from an approved, launch-released entry in <code>messages/ads/</code>, and <code>build/messages.py --check</code> fails on any file in <code>ads/</code> that no entry produces. The Oxagen campaign follows the operator's job. <b>Mission Control</b> introduces the control plane, and each of the others explains one decision an operator makes: which agent has the <b>authority</b> to do what, how each agent is <b>equipped</b>, which agent <b>spent</b> what, and why the agent does not hold the <b>keys</b>. A short form keeps the scope of its long form, so the banner still says governed, recorded, or mediated where the poster does. The 300&times;250 drops the kicker and the call to action, because neither fits at a legible size, but it keeps the answer line in a shorter form. A held campaign, such as completion checks for bounded tasks, is written and not rendered until its capability ships. Stella runs two lines: the proof rule, and the green check. Each ships in the four sizes, on ink and on paper.</p>
<p>Four of the five Oxagen campaigns take the ghost in the top right. The <b>Mission Control</b> ad takes the orbit instead, laid back behind the type: rings of nodes wired inward to one mark is the only composition the kit already owns that reads as many agents under one control plane. It is not a new shape; it is the wallpaper's, at ad scale and at ad strength.</p>
<div class="grid g2">{"".join(ads)}</div>
<h3>Content cards</h3>
<div class="grid g2">{"".join(cards)}</div>
</section>

<section id="files">
<p class="eyebrow">Files</p>
<h2>Every pixel is generated</h2>
<p>No file in this kit is drawn by hand. Every PNG is a render of the SVG beside it; every SVG is emitted from <code>build/</code>. The colours live in one file, <code>build/color.py</code>, so a change there moves every asset on the next run.</p>
<div class="files">{files_html}</div>
<pre><code>python3 -m venv .venv &amp;&amp; .venv/bin/pip install fonttools brotli pyyaml
brew install harfbuzz librsvg
.venv/bin/python build/build.py --check   # verify the face and the palette, write nothing
.venv/bin/python build/build.py           # every asset
.venv/bin/python build/build.py --svg     # skip the raster pass
.venv/bin/python build/playbook.py        # rebuild this document</code></pre>
</section>

</main>
<footer><div class="wrap">Oxagen house system · built from the Oxagen brand kit · Space Grotesk, Geist and Monaspace Neon under the SIL Open Font License</div></footer>
<script>
(function(){{var b=document.getElementById('theme'),r=document.documentElement;
b.addEventListener('click',function(){{var dark=r.getAttribute('data-theme')==='dark'||(!r.getAttribute('data-theme')&&matchMedia('(prefers-color-scheme: dark)').matches);r.setAttribute('data-theme',dark?'light':'dark');}});}})();
</script>
</body>
</html>
"""


def main() -> None:
    out = ROOT / "playbook.html"
    out.write_text(build_html())
    print(f"playbook      ok  ({out.stat().st_size // 1024} KB)")


if __name__ == "__main__":
    main()
