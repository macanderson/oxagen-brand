"""Write `playbook.html` -- the one document that explains the house system.

Every specimen on the page is emitted by the same functions that write the
files in this kit, so the playbook cannot describe a logo the kit does not
ship. Change a colour in `color.py` and the swatch, the contrast number, the
wallpaper and the downloadable PNG all move together on the next build.
"""

from __future__ import annotations

from pathlib import Path

import color as C
import surfaces as SF
from glyphs import wordmark
from marks import (
    INK_TEXT,
    OXAGEN_RAYS,
    PAPER_TEXT,
    STELLA_RAYS,
    spin_style,
    star_group,
    star_only_svg,
    wordmark_svg,
)

ROOT = Path(__file__).resolve().parent.parent
RAYS = {"stella": STELLA_RAYS, "oxagen": OXAGEN_RAYS}
TAG = {"stella": "verified done, not claimed done", "oxagen": "deterministic ai engineering"}

_n = [0]


def uid(p: str = "u") -> str:
    _n[0] += 1
    return f"{p}{_n[0]}"



# --------------------------------------------------------------------------
# specimens
# --------------------------------------------------------------------------


def construction_diagram(word: str) -> str:
    """The grid the wordmark is set on, drawn over the wordmark itself."""
    m = wordmark(word)
    g = ["#26262C", "#EFC53F"]
    guides = []
    for i in range(8):
        x = 6 + i * 36
        guides.append(
            f'<line x1="{x}" y1="8" x2="{x}" y2="88" stroke="{g[0]}" '
            f'stroke-width="0.5" stroke-dasharray="2 3"/>'
        )
    guides.append('<line x1="0" y1="69.9" x2="264" y2="69.9" stroke="#EFC53F" stroke-width="0.6" opacity="0.75"/>')
    guides.append('<line x1="0" y1="26.1" x2="264" y2="26.1" stroke="#26262C" stroke-width="0.5"/>')
    guides.append('<rect x="223.62" y="33.3" width="32.76" height="31.68" fill="none" stroke="#EFC53F" stroke-width="0.6" opacity="0.6"/>')
    d, star = star_group(m, RAYS[word], uid("cx"))
    return (
        f'<svg viewBox="0 0 264 96" role="img" aria-label="{word} wordmark construction grid">'
        f"<defs>{d}</defs>"
        f'<path d="{m["letters"]}" fill="none" stroke="#777782" stroke-width="0.6"/>'
        f'<g opacity="0.9">{star}</g>{"".join(guides)}'
        f'<text x="6" y="94" font-size="5.5" fill="#777782" font-family="monospace">6</text>'
        f'<text x="42" y="94" font-size="5.5" fill="#777782" font-family="monospace">42</text>'
        f'<text x="258" y="94" font-size="5.5" fill="#777782" font-family="monospace" text-anchor="end">264</text>'
        f"</svg>"
    )


def clearspace_diagram(word: str) -> str:
    m = wordmark(word)
    q = 32.76  # one star width
    w, h = m["width"] + q * 2, m["height"] + q * 2
    d, star = star_group(m, RAYS[word], uid("cs"))
    return (
        f'<svg viewBox="0 0 {w:g} {h:g}" role="img" aria-label="{word} clear space">'
        f"<defs>{d}</defs>"
        f'<rect x="0.5" y="0.5" width="{w - 1:g}" height="{h - 1:g}" fill="none" '
        f'stroke="#26262C" stroke-width="1" stroke-dasharray="4 4"/>'
        f'<rect x="{q:g}" y="{q:g}" width="{m["width"]:g}" height="{m["height"]:g}" '
        f'fill="#EFC53F" opacity="0.05"/>'
        f'<g transform="translate({q:g},{q:g})">'
        f'<path d="{m["letters"]}" fill="{PAPER_TEXT}"/>{star}</g>'
        f'<g transform="translate({q / 2 - 8:g},{h / 2 - 8:g}) scale(0.5)">'
        f'{star_body_only(RAYS[word])}</g>'
        f"</svg>"
    )


def star_body_only(rays: list[str]) -> str:
    m = wordmark("stella")
    d, star = star_group(m, rays, uid("sb"))
    return (
        f"<defs>{d}</defs><g transform=\"translate({-m['star_cx'] + 16:.2f},"
        f'{-m["star_cy"] + 16:.2f})">{star}</g>'
    )


def misuse_panel(kind: str, word: str = "stella") -> str:
    """The four ways the wordmark actually gets broken."""
    m = wordmark(word)
    d, star = star_group(m, RAYS[word], uid("mu"))
    body = f'<path d="{m["letters"]}" fill="{PAPER_TEXT}"/>{star}'
    if kind == "left-icon":
        d2, s2 = star_group(m, RAYS[word], uid("mu"))
        body = (
            f'{d2}<g transform="translate({22 - 1.15 * m["star_cx"]:.1f},'
            f'{48 - 1.15 * m["star_cy"]:.1f}) scale(1.15)">{s2}</g>'
            f'<g transform="translate(46,0) scale(0.84)">'
            f'<path d="{m["letters"]}" fill="{PAPER_TEXT}"/>{star}</g>'
        )
    elif kind == "recolour":
        body = f'<path d="{m["letters"]}" fill="#EFC53F"/>{star}'
    elif kind == "stretch":
        body = (
            f'<g transform="translate(0,10) scale(1,0.78)">'
            f'<path d="{m["letters"]}" fill="{PAPER_TEXT}"/>{star}</g>'
        )
    elif kind == "swap":
        d3, s3 = star_group(m, OXAGEN_RAYS if word == "stella" else STELLA_RAYS, uid("mu"))
        body = f'{d3}<path d="{m["letters"]}" fill="{PAPER_TEXT}"/>{s3}'
    return (
        f'<svg viewBox="0 0 300 96" role="img" aria-label="incorrect use">'
        f"<defs>{d}</defs>{body}</svg>"
    )


def swatch_row(name: str, hexv: str, note: str, on_ink: float, on_paper: float) -> str:
    return (
        f'<tr><td><span class="chip" style="background:{hexv}"></span></td>'
        f'<td class="mono">{name}</td><td class="mono num">{hexv}</td>'
        f'<td class="num">{on_ink:.1f}<span class="unit">:1</span></td>'
        f'<td class="num">{on_paper:.1f}<span class="unit">:1</span></td>'
        f"<td class=\"note\">{note}</td></tr>"
    )


def live_spinner(rays: list[str], size: int = 64) -> str:
    u = uid("sp")
    svg = star_only_svg(rays, box=96, fill=0.74, uid=u)
    m = wordmark("stella")
    svg = svg.replace("</svg>", spin_style(m["star_cx"], m["star_cy"]) + "</svg>")
    return svg.replace('width="96" height="96"', f'width="{size}" height="{size}"')


def type_scale_rows() -> str:
    steps = [
        ("display", 800, "2.986rem", "wordmark weight; one per screen"),
        ("h1", 800, "2.488rem", "page title"),
        ("h2", 700, "1.728rem", "section"),
        ("h3", 700, "1.2rem", "subsection"),
        ("body", 400, "1rem", "running text, measure 62ch"),
        ("ui", 500, "0.833rem", "labels, buttons, table headers"),
        ("caption", 400, "0.833rem", "captions, metadata, code"),
    ]
    out = []
    for name, w, size, note in steps:
        out.append(
            f'<div class="tsr"><div class="tsr-meta"><span class="mono">{name}</span>'
            f'<span class="mono dim">{w} / {size}</span></div>'
            f'<div class="tsr-spec" style="font-size:{size};font-weight:{w}">'
            f"the quick brown fox</div>"
            f'<div class="tsr-note">{note}</div></div>'
        )
    return "".join(out)


# --------------------------------------------------------------------------


def css() -> str:
    r = C.RESTING
    return f"""
:root {{
  --ink:{C.INK}; --void:#050507; --panel:#0F0F12; --hl:#17171B;
  --border:#26262C; --rule:#2C2C33;
  --fg:{PAPER_TEXT}; --muted:#9A9AA6; --dim:#7A7A85;
  --gold:{C.GOLD}; --gold-bright:#F7D96B; --accent-text:{C.GOLD};
  --ray-ember:{r['ember']}; --ray-rose:{r['rose']};
  --ray-orchid:{r['orchid']}; --ray-azure:{r['azure']};
  --card:#0F0F12; --card-2:#131317;
  --shadow:0 1px 0 rgba(255,255,255,.03), 0 18px 44px rgba(0,0,0,.5);
}}
@media (prefers-color-scheme: light) {{
  :root:not([data-theme="dark"]) {{
    --ink:{C.PAPER}; --void:#F2EEE5; --panel:#F9F6EF; --hl:#F2EFE8;
    --border:#E6E3DD; --rule:#DCD8D0;
    --fg:{INK_TEXT}; --muted:#5D5B57; --dim:#75726C;
    --card:#FDFAF3; --card-2:#F7F4ED; --accent-text:{C.INKED['gold']};
    --shadow:0 1px 0 rgba(255,255,255,.7), 0 18px 44px rgba(20,20,19,.07);
  }}
}}
:root[data-theme="light"] {{
  --ink:{C.PAPER}; --void:#F2EEE5; --panel:#F9F6EF; --hl:#F2EFE8;
  --border:#E6E3DD; --rule:#DCD8D0;
  --fg:{INK_TEXT}; --muted:#5D5B57; --dim:#75726C;
  --card:#FDFAF3; --card-2:#F7F4ED; --accent-text:{C.INKED['gold']};
  --shadow:0 1px 0 rgba(255,255,255,.7), 0 18px 44px rgba(20,20,19,.07);
}}

*,*::before,*::after {{ box-sizing:border-box; }}
html {{ scroll-behavior:smooth; scroll-padding-top:78px; }}
@media (prefers-reduced-motion: reduce) {{ html {{ scroll-behavior:auto; }} }}
body {{
  margin:0; background:var(--ink); color:var(--fg);
  font-family:"JetBrains Mono", ui-monospace, "SF Mono", Menlo, monospace;
  font-size:15px; line-height:1.72; font-weight:400;
  -webkit-font-smoothing:antialiased;
}}

/* ---- shell ---- */
.bar {{
  position:sticky; top:0; z-index:50; background:color-mix(in srgb, var(--ink) 86%, transparent);
  backdrop-filter:blur(14px); border-bottom:1px solid var(--border);
}}
.bar-in {{
  max-width:1180px; margin:0 auto; padding:12px 28px;
  display:flex; align-items:center; gap:20px; color:var(--fg);
}}
.bar svg {{ height:20px; width:auto; display:block; }}
.bar nav {{ display:flex; gap:16px; margin-left:auto; flex-wrap:wrap; }}
.bar a {{
  color:var(--muted); text-decoration:none; font-size:12px; font-weight:500;
  letter-spacing:.04em; padding:4px 0; border-bottom:1px solid transparent;
}}
.bar a:hover {{ color:var(--fg); border-bottom-color:var(--accent-text); }}
.bar a:focus-visible {{ outline:2px solid var(--gold); outline-offset:3px; border-radius:2px; }}

.wrap {{ max-width:1180px; margin:0 auto; padding:0 28px; }}
section {{ padding:74px 0; border-top:1px solid var(--rule); }}
section:first-of-type {{ border-top:0; }}

.eyebrow {{
  display:flex; align-items:center; gap:10px;
  font-size:11px; letter-spacing:.16em; text-transform:uppercase;
  color:var(--accent-text); font-weight:700; margin:0 0 14px;
}}
.eyebrow::before {{ content:"*"; font-weight:800; font-size:15px; line-height:1; }}
figure.m0 {{ margin:0; }}
h1,h2,h3 {{ text-wrap:balance; margin:0; font-weight:800; letter-spacing:-.02em; }}
h1 {{ font-size:clamp(2rem,5vw,2.986rem); line-height:1.12; }}
h2 {{ font-size:clamp(1.5rem,3.2vw,2.074rem); line-height:1.18; }}
h3 {{ font-size:1.2rem; font-weight:700; letter-spacing:-.01em; }}
p {{ margin:14px 0; max-width:62ch; color:var(--muted); }}
p strong {{ color:var(--fg); font-weight:700; }}
p.lead {{ font-size:1.06rem; color:var(--fg); max-width:58ch; }}
a {{ color:var(--accent-text); }}
code {{
  font-size:.86em; background:var(--hl); border:1px solid var(--border);
  padding:1px 6px; border-radius:5px; color:var(--fg);
}}
.mono {{ font-variant-ligatures:none; }}
.num {{ font-variant-numeric:tabular-nums; }}
.dim {{ color:var(--dim); }}
.unit {{ color:var(--dim); font-size:.85em; }}

/* ---- hero ---- */
.hero {{ padding:86px 0 70px; }}
.hero-marks {{ display:flex; flex-direction:column; gap:26px; margin:0 0 34px; }}
.hero-marks svg {{ width:min(430px,72vw); height:auto; display:block; }}
.hero-rule {{ height:3px; width:96px; background:var(--accent-text); margin:26px 0; border-radius:2px; }}

/* ---- grids ---- */
.grid {{ display:grid; gap:20px; }}
.g2 {{ grid-template-columns:repeat(auto-fit,minmax(300px,1fr)); }}
.g3 {{ grid-template-columns:repeat(auto-fit,minmax(230px,1fr)); }}
.g4 {{ grid-template-columns:repeat(auto-fit,minmax(168px,1fr)); }}

.card {{
  background:var(--card); border:1px solid var(--border);
  border-radius:14px; padding:22px; box-shadow:var(--shadow);
}}
.card h3 {{ margin-bottom:6px; }}
.card p {{ margin:8px 0 0; font-size:13px; line-height:1.65; }}

/* fixed-ground specimens: these show the BRAND's grounds, not the page theme */
.on-ink {{ background:{C.INK}; color:{PAPER_TEXT}; }}
.on-paper {{ background:{C.PAPER}; color:{INK_TEXT}; }}
.plate {{
  border-radius:14px; border:1px solid var(--border); overflow:hidden;
  display:flex; align-items:center; justify-content:center; padding:34px 24px;
}}
.plate svg {{ width:100%; height:auto; max-width:340px; display:block; }}
.plate.tight {{ padding:0; }}
.plate.tight svg {{ max-width:none; }}
.cap {{
  font-size:11px; letter-spacing:.1em; text-transform:uppercase;
  color:var(--dim); margin:10px 0 0; font-weight:500;
}}

/* ---- colour table ---- */
.tbl-wrap {{ overflow-x:auto; border:1px solid var(--border); border-radius:14px; background:var(--card); }}
table {{ border-collapse:collapse; width:100%; min-width:620px; font-size:13px; }}
th, td {{ text-align:left; padding:11px 14px; border-bottom:1px solid var(--border); }}
th {{
  font-size:10px; letter-spacing:.12em; text-transform:uppercase;
  color:var(--dim); font-weight:700; white-space:nowrap;
}}
tbody tr:last-child td {{ border-bottom:0; }}
td.num, th.num {{ text-align:right; font-variant-numeric:tabular-nums; }}
td.note {{ color:var(--dim); font-size:12px; }}
.chip {{
  display:block; width:26px; height:26px; border-radius:7px;
  border:1px solid rgba(128,128,128,.28);
}}

/* ---- spectrum ---- */
.swatches {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(128px,1fr)); gap:12px; }}
.swatch-card {{ border-radius:12px; overflow:hidden; border:1px solid var(--border); background:var(--card); }}
.swatch-sw {{ height:76px; }}
.swatch-meta {{ padding:11px 13px; font-size:11.5px; line-height:1.55; }}
.swatch-meta b {{ display:block; font-weight:700; font-size:12.5px; color:var(--fg); }}
.swatch-meta span {{ color:var(--dim); font-variant-numeric:tabular-nums; }}

/* ---- type scale ---- */
.tsr {{
  display:grid; grid-template-columns:150px 1fr 190px; gap:20px;
  align-items:baseline; padding:15px 0; border-bottom:1px solid var(--border);
}}
.tsr:last-child {{ border-bottom:0; }}
.tsr-meta {{ display:flex; flex-direction:column; font-size:11px; }}
.tsr-meta .mono {{ color:var(--fg); font-weight:500; }}
.tsr-spec {{ line-height:1.25; letter-spacing:-.02em; overflow:hidden; text-overflow:ellipsis; white-space:nowrap; }}
.tsr-note {{ font-size:11.5px; color:var(--dim); line-height:1.5; }}
@media (max-width:760px) {{ .tsr {{ grid-template-columns:1fr; gap:6px; }} }}

/* ---- motion ---- */
.spin-row {{ display:flex; align-items:center; gap:34px; flex-wrap:wrap; }}
.spin-cell {{ display:flex; flex-direction:column; align-items:center; gap:10px; }}
.spin-cell svg {{ display:block; }}

/* ---- rules list ---- */
.rules {{ list-style:none; padding:0; margin:18px 0 0; display:grid; gap:11px; }}
.rules li {{
  display:grid; grid-template-columns:auto 1fr; gap:12px;
  font-size:13.5px; line-height:1.62; color:var(--muted);
}}
.rules b {{ color:var(--fg); font-weight:700; }}
.tick {{ color:var(--accent-text); font-weight:800; }}
.cross {{ color:{r['rose']}; font-weight:800; }}

/* ---- misuse ---- */
.mis {{ border:1px solid var(--border); border-radius:12px; overflow:hidden; background:{C.INK}; }}
.mis svg {{ display:block; width:100%; height:auto; padding:14px 16px; }}
.mis-lbl {{
  border-top:1px solid var(--border); padding:9px 13px; font-size:11.5px;
  color:#8A8A95; display:flex; gap:8px; align-items:flex-start; line-height:1.5;
}}

/* ---- file list ---- */
.files {{ font-size:12.5px; line-height:1.95; color:var(--muted); margin:0; white-space:pre; overflow-x:auto; }}
.files b {{ color:var(--fg); font-weight:700; }}

footer {{
  border-top:1px solid var(--rule); padding:38px 0 60px;
  font-size:12px; color:var(--dim);
}}
"""


def build_html() -> str:
    sty = css()
    stella_ink = wordmark_svg("stella", STELLA_RAYS, uid=uid("w"))
    stella_pap = wordmark_svg("stella", STELLA_RAYS, letters=INK_TEXT, uid=uid("w"))
    oxagen_ink = wordmark_svg("oxagen", OXAGEN_RAYS, uid=uid("w"))
    oxagen_pap = wordmark_svg("oxagen", OXAGEN_RAYS, letters=INK_TEXT, uid=uid("w"))
    bar_mark = wordmark_svg("oxagen", OXAGEN_RAYS, letters="currentColor", uid=uid("bar"))

    # colour tables
    neutrals = [
        ("--ox-ink", C.INK, "the canvas"),
        ("--ox-void", "#050507", "below the canvas"),
        ("--ox-panel", "#0F0F12", "panels, cards, code"),
        ("--ox-border", "#26262C", "hairlines"),
        ("--ox-text", PAPER_TEXT, "primary text on ink"),
        ("--ox-muted", "#777782", "secondary text on ink"),
    ]
    papers = [
        ("--ox-paper", C.PAPER, "the warm light canvas"),
        ("--ox-paper-panel", "#F9F6EF", "light panel"),
        ("--ox-paper-border", "#E6E3DD", "light hairline"),
        ("--ox-text-ink", INK_TEXT, "primary text on paper"),
        ("--ox-muted-ink", "#605F5C", "secondary text on paper"),
    ]
    n_rows = "".join(
        swatch_row(n, h, note, C.contrast(h, C.INK), C.contrast(h, C.PAPER))
        for n, h, note in neutrals + papers
    )

    ray_cards = []
    for i, name in enumerate(C.RAY_NAMES):
        rest, ink = C.RESTING[name], C.INKED[name]
        pos = ["12 o'clock", "upper right", "lower right", "lower left", "upper left"][i]
        ray_cards.append(
            f'<div class="swatch-card"><div class="swatch-sw" style="background:{rest}"></div>'
            f'<div class="swatch-meta"><b>{name}</b>'
            f'<span>{rest}<br>{pos}<br>{C.contrast(rest, C.INK):.1f}:1 on ink<br>'
            f'ink text {ink}</span></div></div>'
        )

    # surfaces, inlined as vectors rather than screenshots
    wall_specimens = []
    for word in ("oxagen", "stella"):
        for scheme in ("dark", "light"):
            wall_specimens.append(
                f'<figure class="m0"><div class="plate tight">'
                f'{SF.wallpaper_desktop(1600, 900, RAYS[word], scheme)}</div>'
                f'<figcaption class="cap">{word} desktop &middot; {scheme} &middot; aurora</figcaption></figure>'
            )
    phone_specimens = []
    for word in ("oxagen", "stella"):
        for scheme, style in (("dark", "aurora"), ("dark", "quiet")):
            phone_specimens.append(
                f'<figure class="m0"><div class="plate tight">'
                f'{SF.wallpaper_phone(430, 932, RAYS[word], scheme, style)}</div>'
                f'<figcaption class="cap">{word} iphone &middot; {style}</figcaption></figure>'
            )

    social = []
    for word in ("oxagen", "stella"):
        social.append(
            f'<figure class="m0"><div class="plate tight">'
            f'{SF.avatar(RAYS[word], 400, "dark")}</div>'
            f'<figcaption class="cap">{word} avatar &middot; 1024&times;1024</figcaption></figure>'
        )
    banners = []
    for word in ("oxagen", "stella"):
        banners.append(
            f'<figure class="m0"><div class="plate tight">'
            f'{SF.banner(1500, 500, word, RAYS[word], "dark", tagline=TAG[word])}</div>'
            f'<figcaption class="cap">{word} &middot; x header 1500&times;500</figcaption></figure>'
        )
    banners.append(
        f'<figure class="m0"><div class="plate tight">'
        f'{SF.og_card(1200, 630, "stella", STELLA_RAYS, "dark", tagline=TAG["stella"])}</div>'
        f'<figcaption class="cap">stella &middot; open graph 1200&times;630</figcaption></figure>'
    )
    banners.append(
        f'<figure class="m0"><div class="plate tight">'
        f'{SF.og_card(1200, 630, "oxagen", OXAGEN_RAYS, "light", tagline=TAG["oxagen"])}</div>'
        f'<figcaption class="cap">oxagen &middot; open graph, paper</figcaption></figure>'
    )

    ads = []
    from build import AD_COPY, CONTENT

    for word, w, h, scheme in (
        ("oxagen", 1080, 1350, "dark"),
        ("stella", 1080, 1080, "dark"),
        ("oxagen", 1200, 628, "light"),
    ):
        cp = AD_COPY[word]
        ads.append(
            f'<figure class="m0"><div class="plate tight">'
            f'{SF.ad(w, h, word, RAYS[word], scheme, kicker=cp["kicker"], headline=cp["headline"], cta=cp["cta"])}'
            f'</div><figcaption class="cap">{word} &middot; {w}&times;{h} &middot; {scheme}</figcaption></figure>'
        )

    cards = []
    for word, scheme in (("stella", "dark"), ("oxagen", "light"), ("stella", "light")):
        kind, title, meta, body = CONTENT[word][0 if word == "stella" else 1]
        cards.append(
            f'<figure class="m0"><div class="plate tight">'
            f'{SF.content_card(1200, 675, word, RAYS[word], scheme, kind=kind, title=title, meta=meta, body=body)}'
            f'</div><figcaption class="cap">{word} &middot; {kind} card 1200&times;675</figcaption></figure>'
        )

    icons = []
    for word in ("oxagen", "stella"):
        for label, bg, rad in (("app tile", C.INK, 20), ("on paper", C.PAPER, 20)):
            icons.append(
                f'<figure class="m0"><div class="plate tight">'
                f'{star_only_svg(RAYS[word], background=bg, radius=rad, uid=uid("ic"))}</div>'
                f'<figcaption class="cap">{word} &middot; {label}</figcaption></figure>'
            )

    misuses = [
        ("left-icon", "A mark to the left of the word. The star is the only mark, and it goes last."),
        ("recolour", "Letters in the metal. Gold belongs to the star and to one action; never to the word."),
        ("stretch", "Scaled on one axis. The mark is one locked box &mdash; scale it whole."),
        ("swap", "The wrong star. Five golds is stella; five hues is oxagen. They never trade."),
    ]
    mis_html = "".join(
        f'<div class="mis">{misuse_panel(k)}'
        f'<div class="mis-lbl"><span class="cross">&#10007;</span><span>{t}</span></div></div>'
        for k, t in misuses
    )

    files = """<b>logo/svg/</b>      stella-wordmark-{dark,light,adaptive,mono,mono-white,mono-black}.svg
                oxagen-wordmark-{...}.svg  &middot;  {brand}-mark{,-tile-dark,-tile-light}.svg
<b>logo/png/</b>      every wordmark at 512 / 1024 / 2048w, every mark at 256 / 512 / 1024
<b>icons/</b>         {brand}-icon-{16,32,48,180,192,512}.png
<b>spinners/</b>      {brand}-spinner.svg  &middot;  {brand}-spinner-wordmark.svg
<b>wallpapers/</b>    desktop 4K / 5K / 6K  &middot;  phone iphone / pro / pro-max
                &times; aurora | quiet  &times; dark | light  &middot; svg + png
<b>social/</b>        avatar 1024  &middot;  x 1500&times;500  &middot;  linkedin 1584&times;396
                youtube 2560&times;1440  &middot;  og 1200&times;630  &middot; dark + light
<b>ads/</b>           1080&times;1080  &middot;  1080&times;1350  &middot;  1200&times;628  &middot;  300&times;250
<b>content/</b>       changelog / essay / release / field note cards, 1200&times;675
<b>tokens/</b>        house-tokens.css  &middot;  house-tokens.json"""

    return f"""<title>Oxagen House System</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;700;800&display=swap">
<style>{sty}</style>

<header class="bar">
  <div class="bar-in">
    {bar_mark}
    <nav>
      <a href="#decision">decision</a>
      <a href="#marks">marks</a>
      <a href="#colour">colour</a>
      <a href="#type">type</a>
      <a href="#motion">motion</a>
      <a href="#surfaces">surfaces</a>
      <a href="#publishing">publishing</a>
      <a href="#kit">kit</a>
    </nav>
  </div>
</header>

<main class="wrap">

<section class="hero">
  <p class="eyebrow">one system, two wordmarks</p>
  <div class="hero-marks">{oxagen_ink.replace('fill="' + PAPER_TEXT + '"', 'fill="currentColor"')}
  {stella_ink.replace('fill="' + PAPER_TEXT + '"', 'fill="currentColor"')}</div>
  <h1>The same six letters, the same star,<br>and one colour that says which is which.</h1>
  <div class="hero-rule"></div>
  <p class="lead">Everything a customer sees from Oxagen or Stella is drawn from this page:
  the palette, the type, the two logos, the spinner, the wallpapers, the social art,
  the ads, and the templates we publish content in.</p>
</section>

<section id="decision">
  <p class="eyebrow">the decision</p>
  <h2>Stella&rsquo;s black and gold wins. Oxagen moves to it.</h2>
  <p>Two identities existed. Stella shipped <strong>black and gold on warm paper</strong> &mdash;
  a measured system with a hue clamp on the metal, a contrast ratchet, and a generator that
  keeps every surface honest. Oxagen shipped a <strong>terminal prompt with a vermilion block
  cursor</strong> &mdash; a good joke, but a monochrome one, and the cursor idea does not scale
  past a logo.</p>
  <p>So the house adopts Stella&rsquo;s system whole, and Oxagen gets the wordmark treatment
  Stella already had right: <strong>lowercase name, no mark to the left, one asterisk at the
  end.</strong> The asterisk is where the two brands separate. Stella&rsquo;s five arms are all
  the house metal. Oxagen&rsquo;s five arms are five hues &mdash; and one of those five
  <em>is</em> Stella&rsquo;s gold, at the exact shipped value.</p>
  <div class="grid g3" style="margin-top:28px">
    <div class="card"><h3>The parent holds the spectrum</h3>
      <p>Oxagen is the company; Stella is one of the things it makes. Five hues for the house,
      one of them for the product. The brand architecture is legible in the mark itself.</p></div>
    <div class="card"><h3>Gold is read, not retyped</h3>
      <p>The gold ray is pulled from Stella&rsquo;s own token file at build time. Recolour the
      metal and Oxagen&rsquo;s star follows. The two marks cannot drift apart.</p></div>
    <div class="card"><h3>The cursor is retired</h3>
      <p>No <span class="mono">&#8250;oxagen.sh&#9646;</span>, no block cursor, no glyph before
      the name. The wordmark is the logo; the star alone is the avatar.</p></div>
  </div>
</section>

<section id="marks">
  <p class="eyebrow">the two marks</p>
  <h2>One letterform, two stars</h2>
  <p>Both wordmarks are the string set in <strong>JetBrains Mono ExtraBold</strong> at 60&thinsp;units
  and outlined, so they never depend on a font being installed. The face is monospaced, both names
  are six letters, and the asterisk is the seventh glyph &mdash; which is why the two logos occupy
  the <strong>identical 264&times;96 box</strong> and can be swapped in a layout with nothing else moving.</p>
  <div class="grid g2" style="margin-top:26px">
    <figure class="m0"><div class="plate on-ink">{oxagen_ink}</div>
      <figcaption class="cap">oxagen &middot; on ink</figcaption></figure>
    <figure class="m0"><div class="plate on-paper">{oxagen_pap}</div>
      <figcaption class="cap">oxagen &middot; on warm paper</figcaption></figure>
    <figure class="m0"><div class="plate on-ink">{stella_ink}</div>
      <figcaption class="cap">stella &middot; on ink</figcaption></figure>
    <figure class="m0"><div class="plate on-paper">{stella_pap}</div>
      <figcaption class="cap">stella &middot; on warm paper</figcaption></figure>
  </div>

  <h3 style="margin-top:52px">How it is drawn</h3>
  <p>The asterisk is never redrawn to make its arms paintable. The real glyph outline becomes a
  clipping path and five 72&deg; wedges are painted through it, so the coloured star and the gold
  one are the same curve to the last control point.</p>
  <div class="grid g2" style="margin-top:18px">
    <figure class="m0"><div class="plate on-ink">{construction_diagram("oxagen")}</div>
      <figcaption class="cap">36-unit advance grid &middot; baseline 69.9 &middot; star box 32.76&times;31.68</figcaption></figure>
    <figure class="m0"><div class="plate on-ink">{clearspace_diagram("stella")}</div>
      <figcaption class="cap">clear space &middot; one star width on every side</figcaption></figure>
  </div>

  <h3 style="margin-top:52px">Rules</h3>
  <ul class="rules">
    <li><span class="tick">&#10003;</span><span><b>Nothing sits to the left of the word.</b>
      The star is the only mark and it is always last.</span></li>
    <li><span class="tick">&#10003;</span><span><b>Minimum width 96&thinsp;px</b> for the wordmark,
      <b>24&thinsp;px</b> for the star alone. Below that the five arms merge.</span></li>
    <li><span class="tick">&#10003;</span><span><b>Clear space is one star width</b> &mdash;
      32.76 units, or an eighth of the mark&rsquo;s width &mdash; on all four sides.</span></li>
    <li><span class="tick">&#10003;</span><span><b>On a photo or a busy field, use the mono cut</b>
      in warm paper or ink. Never drop a coloured star onto an image.</span></li>
    <li><span class="tick">&#10003;</span><span><b>The star keeps its colour on both grounds.</b>
      The letters swap; the star does not.</span></li>
  </ul>
  <div class="grid g2" style="margin-top:22px">{mis_html}</div>
</section>

<section id="colour">
  <p class="eyebrow">colour</p>
  <h2>Two grounds, one metal, five rays</h2>
  <p>The neutrals and the metal are Stella&rsquo;s shipped tokens, unchanged. Contrast is measured
  against both canvases, so a value that only works on one of them says so here rather than in review.</p>
  <div class="tbl-wrap" style="margin-top:22px">
    <table>
      <thead><tr><th></th><th>token</th><th class="num">value</th>
        <th class="num">on ink</th><th class="num">on paper</th><th>use</th></tr></thead>
      <tbody>
        {swatch_row("--ox-ray-gold", C.GOLD, "the house metal: identity, one action, money",
                    C.contrast(C.GOLD, C.INK), C.contrast(C.GOLD, C.PAPER))}
        {n_rows}
      </tbody>
    </table>
  </div>
  <p style="margin-top:20px"><strong>Gold never encodes a state.</strong> It is identity and at most
  one primary action per screen. A gold &ldquo;active&rdquo; sits 1.3:1 from a warning amber &mdash;
  indistinguishable. Status colour is separate and lives outside this page&rsquo;s accent.</p>

  <h3 style="margin-top:52px">The spectrum</h3>
  <p>Five rays, clockwise from twelve o&rsquo;clock. All four non-gold rays share one OKLCH lightness
  (<span class="mono num">L&nbsp;{C.RAY_L}</span>) at 98% of the chroma their hue can reach there &mdash;
  equal perceived lightness is what makes five hues read as <em>one object</em> rather than five
  stickers. Every adjacent pair is at least 50&deg; apart in hue, well clear of the 30&deg; floor,
  so no two arms can be confused at avatar size.</p>
  <div class="swatches" style="margin-top:20px">{"".join(ray_cards)}</div>
  <p style="margin-top:20px">The resting values above are for <em>the mark</em>, and they stay the same
  on ink and on paper. When a ray has to work as <strong>text</strong> on warm paper it drops to the
  ink cut listed on each card, which clears 4.5:1 &mdash; the same reason Stella ships a gold-ink
  beside its metal.</p>
</section>

<section id="type">
  <p class="eyebrow">type</p>
  <h2>One family, four weights</h2>
  <p><strong>JetBrains Mono</strong> sets everything: the logo, the headlines, the running text,
  the code. It is the face the product is used in, so the marketing that leads people there is set
  in it too. Scale is a 1.2 ratio; body copy holds a 62-character measure.</p>
  <div style="margin-top:24px">{type_scale_rows()}</div>
  <ul class="rules" style="margin-top:26px">
    <li><span class="tick">&#10003;</span><span><b>Lowercase in the wordmark, sentence case everywhere else.</b>
      Uppercase is for eyebrows and chips only, at .16em tracking.</span></li>
    <li><span class="tick">&#10003;</span><span><b>Tighten display, loosen small.</b>
      &minus;.02em above 1.7rem; 0 at body; +.02em under 12px.</span></li>
    <li><span class="tick">&#10003;</span><span><b>Tabular figures wherever numbers stack</b> &mdash;
      tables, prices, benchmark results.</span></li>
  </ul>
</section>

<section id="motion">
  <p class="eyebrow">motion</p>
  <h2>One spinner for both brands</h2>
  <p>The arms light in turn, clockwise, and the star steps a fifth of a turn each cycle so the lit
  arm keeps travelling instead of pulsing in place. One period, <span class="mono">1.25s</span>,
  five steps. It is declarative CSS inside the SVG, so it runs in an
  <code>&lt;img&gt;</code> with no script, and <code>prefers-reduced-motion</code> lands it on a
  whole, still star.</p>
  <div class="plate on-ink" style="margin-top:24px;justify-content:flex-start;gap:44px;flex-wrap:wrap">
    <div class="spin-row">
      <div class="spin-cell">{live_spinner(OXAGEN_RAYS, 72)}<span class="cap">oxagen 72</span></div>
      <div class="spin-cell">{live_spinner(STELLA_RAYS, 72)}<span class="cap">stella 72</span></div>
      <div class="spin-cell">{live_spinner(OXAGEN_RAYS, 36)}<span class="cap">36</span></div>
      <div class="spin-cell">{live_spinner(STELLA_RAYS, 24)}<span class="cap">24</span></div>
    </div>
  </div>
  <p style="margin-top:18px">Use it for anything the agent is doing: a running turn, a build, a
  deploy. Do not use it as a decorative element on a static page &mdash; a spinning star that is not
  waiting for anything teaches people to ignore the one that is.</p>
</section>

<section id="surfaces">
  <p class="eyebrow">surfaces</p>
  <h2>The star is the only picture we own</h2>
  <p>Every surface is a ground, one oversized star placed off-centre, and at most two lines of type.
  A tinted star on a near-black ground goes muddy &mdash; every ray lands within a few points of the
  canvas &mdash; so the light goes <em>under</em> the star instead: one soft bloom per ray, at that
  ray&rsquo;s own hue and angle, with the glyph laid over at a fifth strength.</p>

  <h3 style="margin-top:44px">Desktop wallpapers</h3>
  <p>4K, 5K and 6K. The bloom sits right of centre so the icon corner stays clear.</p>
  <div class="grid g2" style="margin-top:18px">{"".join(wall_specimens)}</div>

  <h3 style="margin-top:52px">iPhone wallpapers</h3>
  <p>Three device widths. <strong>Aurora</strong> for a lock screen, <strong>quiet</strong> &mdash; the
  star as a hairline &mdash; for a home screen full of app icons.</p>
  <div class="grid g4" style="margin-top:18px">{"".join(phone_specimens)}</div>

  <h3 style="margin-top:52px">Avatars and app icons</h3>
  <p>The star alone, at 62% of the tile. Platforms round the corners themselves, so the square cut
  is the one to upload.</p>
  <div class="grid g4" style="margin-top:18px">{"".join(icons)}</div>

  <h3 style="margin-top:52px">Social headers</h3>
  <div class="grid g2" style="margin-top:18px">{"".join(banners)}</div>

  <h3 style="margin-top:52px">Advertising</h3>
  <p>A kicker in the accent, three short lines set tight in ExtraBold, a rule, the call to action,
  and the wordmark at the foot. The star bleeds off the top-right corner and never sits behind type.</p>
  <div class="grid g3" style="margin-top:18px">{"".join(ads)}</div>
</section>

<section id="publishing">
  <p class="eyebrow">publishing</p>
  <h2>How we put content out</h2>
  <p>Every post, release note and essay ships with a card built from one template: a
  <strong>kind chip</strong> in the accent, a title of one to three lines, an optional monospace
  panel for the thing being shown, the date and desk at the foot, and the wordmark opposite it.
  The chip is the only place the kind is written &mdash; it is not repeated in the title.</p>
  <div class="grid g2" style="margin-top:22px">{"".join(cards)}</div>
  <ul class="rules" style="margin-top:26px">
    <li><span class="tick">&#10003;</span><span><b>Show the artefact, not a stock photo.</b>
      A terminal transcript, a diff, a measured number. The panel exists for exactly this.</span></li>
    <li><span class="tick">&#10003;</span><span><b>Titles are lowercase and specific.</b>
      &ldquo;parallel tool calls, now measured&rdquo; &mdash; not &ldquo;Improving Performance&rdquo;.</span></li>
    <li><span class="tick">&#10003;</span><span><b>One claim per card,</b> and the claim carries its
      evidence. If the number is not on the card, the card is an ad, so use the ad template.</span></li>
    <li><span class="tick">&#10003;</span><span><b>Dark for engineering, paper for company writing.</b>
      Both grounds are ours; pick by voice, then stay consistent across the series.</span></li>
    <li><span class="cross">&#10007;</span><span><b>No stock illustration, no gradient mesh, no
      3D render.</b> The star is the only picture we own.</span></li>
  </ul>
</section>

<section id="kit">
  <p class="eyebrow">the kit</p>
  <h2>Nothing here is drawn by hand</h2>
  <p>Every PNG is a render of the SVG beside it, and every SVG is emitted from
  <code>build/color.py</code> and <code>build/glyphs.py</code>. A colour changes in one place and
  everything downstream follows on the next run.</p>
  <div class="card" style="margin-top:22px"><p class="files">{files}</p></div>
  <div class="card" style="margin-top:16px">
    <h3>Rebuild</h3>
    <p class="mono" style="color:var(--fg)">python3 build/build.py<br>
    python3 build/playbook.py</p>
    <p>Needs <code>fonttools</code>, <code>brotli</code> and <code>rsvg-convert</code>.
    Pass <code>--svg</code> to skip the raster pass.</p>
  </div>
</section>

</main>

<footer class="wrap">
  oxagen house system v1.0 &middot; built on stella black and gold v5.1.0 &middot;
  gold {C.GOLD} on {C.INK}
</footer>
"""


if __name__ == "__main__":
    out = ROOT / "playbook.html"
    out.write_text(build_html())
    print(f"{out}  ({out.stat().st_size / 1024:.0f} kB)")
