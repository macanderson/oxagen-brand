"""Write the whole kit. Nothing in this repository is drawn by hand.

    python3 build/build.py --check    # verify the face and the palette, write nothing
    python3 build/build.py            # write every asset
    python3 build/build.py --svg      # skip the PNG raster pass (fast)
    python3 build/build.py --only ads social   # rebuild only these steps

Ad copy and taglines come from the message registry in `messages/`, read by
`build/messages.py`, which needs PyYAML (`.venv/bin/pip install pyyaml`).

Rasterising needs `rsvg-convert` (`brew install librsvg`); shaping needs
`hb-shape` (`brew install harfbuzz`). Every PNG here is a render of the SVG
beside it, so a colour can only be changed in one place -- `theme/theme.json`
-- and everything downstream follows on the next run.

`--check` writes nothing. It fails when `theme/theme.json` does not match
`theme/theme.schema.json`, when the palette or the type breaks a rule, or when
a generated file differs from what the theme produces: every token file, mark,
icon, and image the build writes as text, and `playbook.html`. A PNG is checked
for presence, because a render differs byte for byte between versions of
librsvg.
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

import badges as BD
import color as C
import fonts as FT
import glyphs as G
import marks as MK
import messages as MS
import surfaces as SF
import pagecss as PG
import request as RQ
import typeset as T
from theme import THEME, rem_px
from marks import (
    BRANDS,
    favicon_svg,
    icon_svg,
    lockup_svg,
    spinner_svg,
    spinner_wordmark_svg,
    wordmark_svg,
)

ROOT = Path(__file__).resolve().parent.parent
BRAND_WORDS = ("oxagen", "stella")

#: Every build step and the directories it owns. A step deletes the generated
#: files in its own directories before it writes, so a renamed asset cannot
#: leave its old name behind, and `--only` never touches a directory another
#: step owns. Files with other suffixes, such as notes in Markdown, stay.
STEPS: dict[str, tuple[str, ...]] = {
    "tokens": ("tokens",),
    "logos": ("logo",),
    "icons": ("icons",),
    "spinners": ("spinners",),
    "wallpapers": ("wallpapers",),
    "splash": ("splash",),
    "social": ("social",),
    "ads": ("ads",),
    "content": ("content",),
    "badges": ("github-badges",),
}
GENERATED =tuple(d for dirs in STEPS.values() for d in dirs)
GENERATED_SUFFIXES = {".svg", ".png", ".ico", ".webmanifest", ".css", ".json", ".ts"}

#: The social and manifest taglines, from approved, launch-released registry
#: entries (`hero-headline` and `stella-tagline`), so the art cannot say
#: something the company has stopped saying.
TAGLINES = MS.taglines()
DOMAINS = {"stella": "stella.oxagen.sh", "oxagen": "oxagen.sh"}

#: The branding skill's copy of the tokens. The tokens step writes it, and
#: --check fails if it has drifted, so an agent reading the skill reads the
#: values the products compile.
SKILL_TOKENS = "skills/oxagen-branding/assets/tokens.css"
SKILL_LOGO = "skills/oxagen-branding/assets/logo.svg"

#: The corners, shadows, and spacing, straight from the theme.
RADIUS = THEME["radius"]
SHADOW = THEME["shadow"]


#: While `--check` runs, the build writes into this dict instead of the disk:
#: each generated path and its text, and each raster with no text (None).
CHECKING: dict[Path, str | None] | None = None


def write(rel: str, text: str) -> Path:
    p = ROOT / rel
    if CHECKING is not None:
        CHECKING[p] = text
        return p
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text)
    return p


def png(svg: Path, width: int | None = None, height: int | None = None, out: Path | None = None) -> None:
    """Rasterise beside the source. The SVG is always the original."""
    out = out or svg.with_suffix(".png")
    if CHECKING is not None:
        CHECKING[out] = None
        return
    cmd = ["rsvg-convert", str(svg), "-o", str(out)]
    if width:
        cmd += ["-w", str(width)]
    if height:
        cmd += ["-h", str(height)]
    subprocess.run(cmd, check=True)


# --------------------------------------------------------------------------


_NUMBERS = {1: "one", 2: "two", 3: "three", 4: "four"}


def _count(items: tuple) -> str:
    return _NUMBERS.get(len(items), str(len(items)))


def _and(words: list[str]) -> str:
    return words[0] if len(words) == 1 else ", ".join(words[:-1]) + " and " + words[-1]


def _wrap(text: str, width: int = 73) -> list[str]:
    """A comment paragraph as lines no wider than `width`."""
    lines, line = [], ""
    for word in text.split():
        if line and len(line) + 1 + len(word) > width:
            lines.append(line)
            line = word
        else:
            line = f"{line} {word}" if line else word
    return lines + [line]


def _headings_and_text() -> str:
    if T.HEADING_FACE is T.TEXT_FACE:
        return f"Every heading and all text take {T.TEXT_FACE.family}"
    return f"Every heading takes {T.HEADING_FACE.family}, all text takes {T.TEXT_FACE.family}"


def _faces_note() -> list[str]:
    """The header's sentence on which face sets what."""
    if T.HEADING_FACE is T.TEXT_FACE:
        lead = f"{T.TEXT_FACE.family} sets every heading and everything read."
    else:
        lead = f"{T.HEADING_FACE.family} sets every heading. {T.TEXT_FACE.family} sets everything read."
    return _wrap(
        f"{lead} {T.CODE_FACE.family} sets code, logs, digests, and the numbers in tables. "
        f"{T.WORDMARK_FACE.family} sets the wordmarks and line 1 of a marketing hero, and no other heading."
    )


def _header(what: str, *extra: str) -> list[str]:
    lines = ["/*", f" * {what}", " *", " * GENERATED by build/build.py from theme/theme.json. Do not edit."]
    if extra:
        lines.append(" *")
        lines += [f" * {e}" if e else " *" for e in extra]
    lines.append(" */")
    return lines


def _semantic(theme: str) -> list[tuple[str, str]]:
    """The shadcn and Base UI semantic tokens for one theme, each a reference
    into the house palette. The names are the ones shadcn components bind to;
    the values are the kit's, so nothing here writes a hex."""
    dark = theme == "dark"
    ox = lambda name: f"var(--ox-{name})"  # noqa: E731
    return [
        ("background", ox("ink" if dark else "paper")),
        ("foreground", ox("text" if dark else "text-ink")),
        ("card", ox("panel" if dark else "paper-panel")),
        ("card-foreground", ox("text" if dark else "text-ink")),
        ("popover", ox("panel" if dark else "paper-panel")),
        ("popover-foreground", ox("text" if dark else "text-ink")),
        ("primary", ox("text" if dark else "ink")),
        ("primary-foreground", ox("ink" if dark else "paper")),
        ("secondary", ox("hl" if dark else "paper-hl")),
        ("secondary-foreground", ox("text" if dark else "text-ink")),
        ("muted", ox("hl" if dark else "paper-hl")),
        # Secondary text sits on `muted` as often as on the canvas. muted-ink is
        # 4.40:1 on paper-hl, so the light theme takes muted-text-ink, which
        # clears both. On ink, muted clears 4.5:1 on the lifted row as it is.
        ("muted-foreground", ox("muted" if dark else "muted-text-ink")),
        # shadcn's `accent` is the hover surface under menu items and rows.
        # It is a surface, so it is never gold: gold never fills a surface.
        ("accent", ox("hl" if dark else "paper-hl")),
        ("accent-foreground", ox("text" if dark else "text-ink")),
        ("destructive", ox("destructive" if dark else "destructive-ink")),
        ("destructive-foreground", ox("ink" if dark else "paper")),
        ("border", ox("border" if dark else "paper-border")),
        ("input", ox("border" if dark else "paper-border")),
        # The focus ring is the one gold mark a component may carry.
        ("ring", ox("gold" if dark else "gold-deep")),
        # The house gold, as a mark and as text. On paper, gold text is the
        # deep shade; the metal itself is below AA there and stays a mark.
        ("gold", ox("gold")),
        ("gold-foreground", ox("ink")),
        ("gold-text", ox("gold" if dark else "gold-deep")),
        ("sidebar", ox("panel" if dark else "paper-panel")),
        ("sidebar-foreground", ox("text-body" if dark else "text-ink-body")),
        ("sidebar-primary", ox("text" if dark else "ink")),
        ("sidebar-primary-foreground", ox("ink" if dark else "paper")),
        ("sidebar-accent", ox("hl" if dark else "paper-hl")),
        ("sidebar-accent-foreground", ox("text" if dark else "text-ink")),
        ("sidebar-border", ox("border" if dark else "paper-border")),
        ("sidebar-ring", ox("gold" if dark else "gold-deep")),
    ]


SEMANTIC_NAMES = [name for name, _ in _semantic("dark")]


def _state_var(name: str) -> str:
    """The token stem for a state's stops: `st-failed`, or `destructive` for the red."""
    return name if name == "destructive" else f"st-{name}"


def house_tokens_css() -> str:
    lines = _header(
        f"The house colour and type system: one palette and {_count(T.FACES)} faces for oxagen and stella.",
        f"Obsidian ({C.INK}) and white, with neutral greys between, and one gold",
        f"({C.GOLD}). gold-bright is what the shimmer passes through and gold-deep",
        "is gold as text on white, both derived from the gold in OKLCH. Gold is",
        "identity and at most one action per screen. It never encodes a state.",
        "",
        "State is carried by border shape. The st-* colours are for the badge or",
        "dot inside a table where shape is too small to read, never the only",
        "signal. destructive is the failed red lifted until it clears AA on ink.",
        "A word in a state's colour takes its text stop, st-*-text on ink and",
        "st-*-text-ink on paper, which clears 4.5:1 on every surface of its theme.",
        "",
        *_faces_note(),
        "tokens/house-fonts.css carries the @font-face rules.",
    )
    lines += ["", ":root {"]
    for name, hexv, note in C.TOKENS:
        lines.append(f"  --ox-{name}: {hexv}; /* {note} */")
    lines.append("")
    for name, dark, light, note in C.STATES:
        lines.append(f"  --ox-st-{name}: {dark}; /* {note}, on ink */")
        lines.append(f"  --ox-st-{name}-ink: {light}; /* the same, on paper */")
    lines.append(f"  --ox-destructive: {C.DESTRUCTIVE['dark']}; /* a destructive action, on ink: text and fill */")
    lines.append(f"  --ox-destructive-ink: {C.DESTRUCTIVE['light']}; /* the same, on paper */")
    lines.append("")
    for name, text in C.STATE_TEXT.items():
        lines.append(f"  --ox-{_state_var(name)}-text: {text['dark']}; /* {name} as words, on ink, panel, and hl */")
        lines.append(f"  --ox-{_state_var(name)}-text-ink: {text['light']}; /* {name} as words, on paper and paper-hl */")
    lines += [
        "",
        f"  --ox-gold-sheen: linear-gradient(45deg, {C.GOLD_DEEP} 0%, {C.GOLD} 38%, "
        f"{C.GOLD_BRIGHT} 56%, {C.GOLD} 74%, {C.GOLD_DEEP} 100%);",
        "",
    ]
    for face in T.FACES:
        if face.key == "heading":
            continue  # written below, as every theme's heading face is
        var = "--ox-font" if face.key == "sans" else f"--ox-font-{face.key}"
        lines.append(f"  {var}: {face.css_stack}; /* {face.job} */")
    lines.append(f"  --ox-font-heading: {T.HEADING_FACE.css_stack}; /* every heading, h1 to h6 */")
    lines.append(f"  --ox-font-mono-features: {T.FACE['mono'].features}; /* texture healing and code ligatures */")
    lines.append("")
    for job, w in T.WEIGHTS.items():
        lines.append(f"  --ox-weight-{job}: {w};")
    lines.append("")
    for job, t in T.TRACKING.items():
        lines.append(f"  --ox-tracking-{job}: {t};")
    lines.append("")
    for scale in T.SCALES:
        for st in scale.steps:
            lines.append(f"  --ox-{scale.key}-{st.name}: {st.size}; /* {scale.name} {st.name}, {st.px}px, line-height {st.leading} */")
        lines.append("")
    for scale in T.SCALES:
        for st in scale.steps:
            lines.append(f"  --ox-{scale.key}-{st.name}-leading: {st.leading};")
        lines.append("")
    site = RADIUS["site"]
    lines += [
        f"  --ox-radius: {site}; /* {rem_px(site):g}px: cards, panels, inputs on the website */",
        f"  --ox-wrap: {THEME['spacing']['wrap']};",
        "  --ox-shimmer-period: 2.8s;",
        "",
        f"  --ox-radius-base: {RADIUS['base']}; /* {rem_px(RADIUS['base']):g}px: the corner every step multiplies */",
    ]
    for step, mult in RADIUS["steps"].items():
        lines.append(f"  --ox-radius-{step}: calc(var(--ox-radius-base) * {mult:g}); /* {rem_px(RADIUS['base']) * mult:.2f}px */")
    lines += [
        f"  --ox-radius-card: var(--ox-radius-{RADIUS['card']}); /* a card and a panel */",
        "",
        f"  --ox-shadow-ui: {SHADOW['ui']['ink']}; /* under a control, on ink */",
        f"  --ox-shadow-ui-ink: {SHADOW['ui']['paper']}; /* the same, on paper */",
        f"  --ox-shadow-pop: {SHADOW['pop']['ink']}; /* under a menu, popover, dialog, or toast, on ink */",
        f"  --ox-shadow-pop-ink: {SHADOW['pop']['paper']}; /* the same, on paper */",
        "",
        f"  --ox-space: {THEME['spacing']['unit']}; /* the spacing unit: p-4 is four of it */",
        "}",
    ]
    return "\n".join(lines) + "\n"


def house_fonts_css() -> str:
    lines = _header(
        f"The {_count(T.FACES)} house faces as @font-face rules, for a page that loads them itself.",
        "Paths are relative to tokens/; a Next.js app uses tokens/next-fonts.ts instead.",
    )
    return "\n".join(lines) + "\n\n" + T.font_faces("../fonts/") + "\n"


def house_tailwind_css() -> str:
    lines = _header(
        "The house system for Tailwind CSS v4, shadcn/ui and Base UI.",
        "Import it after Tailwind, in the app's global stylesheet:",
        "",
        '    @import "tailwindcss";',
        '    @import "./house-tailwind.css";',
        "",
        "Every value is a reference into house-tokens.css, so the app writes no",
        "brand hex. Light is the default; `.dark` on <html> is the dark theme, and",
        "a system preference falls back to it when neither class is set.",
        "",
        *_wrap(
            f"Fonts: tokens/next-fonts.ts sets {_and([f.next_var for f in T.FACES])} on <html>."
            " Without next/font, import house-fonts.css and the family names below"
            " resolve to its @font-face."
        ),
        "",
        *_wrap(
            "Type: text-m-* is the marketing scale, text-a-* the app scale. A surface picks one. "
            + _headings_and_text()
            + f", and code takes {T.CODE_FACE.family} with texture healing on, whichever scale is in use."
        ),
        "",
        f"{T.WORDMARK_FACE.family} reaches a page two ways. --font-wordmark sets a wordmark",
        f"that is text rather than an SVG. The {T.HERO_CLASS} class sets line 1 of",
        "a marketing hero, inside a text-m-h1 heading:",
        "",
        f'    <h1 class="text-m-h1"><span class="{T.HERO_CLASS}">Line one</span><br>Line two</h1>',
        "",
        "text-m-h1 points --font-hero at the wordmark face for its own contents.",
        f"Everywhere else --font-hero is the heading face, so {T.HERO_CLASS} in the",
        "app, in a text-a-h1, or on any other heading draws in Geist.",
    )
    out = "\n".join(lines) + "\n\n"
    out += '@import "./house-tokens.css";\n\n'

    # 1. the brand palette as Tailwind utilities: text-ox-gold, bg-ox-panel ...
    out += "@theme {\n"
    for name, _, note in C.TOKENS:
        out += f"  --color-ox-{name}: var(--ox-{name}); /* {note} */\n"
    for name, _, _, _ in C.STATES:
        out += f"  --color-ox-st-{name}: var(--ox-st-{name});\n"
        out += f"  --color-ox-st-{name}-ink: var(--ox-st-{name}-ink);\n"
    out += "  --color-ox-destructive: var(--ox-destructive);\n"
    out += "  --color-ox-destructive-ink: var(--ox-destructive-ink);\n"
    for name in C.STATE_TEXT:
        var = _state_var(name)
        out += f"  --color-ox-{var}-text: var(--ox-{var}-text);\n"
        out += f"  --color-ox-{var}-text-ink: var(--ox-{var}-text-ink);\n"
    out += "\n"
    for role in T.ROLES:
        if role.key == "hero":
            continue  # set in the base layer below, so a hero step can redefine it
        face = T.FACE[role.face]
        out += f"  --font-{role.key}: var({face.next_var}, \"{face.family}\"), {face.stack}; /* {role.job} */\n"
    out += "\n"
    for job, t in T.TRACKING.items():
        out += f"  --tracking-{job}: {t};\n"
    out += "\n"
    out += "  --radius-card: var(--ox-radius);\n"
    out += "  --container-wrap: var(--ox-wrap);\n"
    out += "  --spacing: var(--ox-space);\n"
    out += "}\n\n"

    # 2. the semantic tokens shadcn and Base UI components bind to
    out += "@layer base {\n"
    for theme, selector in (("light", ":root"), ("dark", ".dark")):
        out += f"  {selector} {{\n    color-scheme: {theme};\n"
        for name, value in _semantic(theme):
            out += f"    --{name}: {value};\n"
        out += "    --radius: var(--ox-radius);\n  }\n"
        if theme == "light":
            out += "\n"
    out += "\n  @media (prefers-color-scheme: dark) {\n    :root:not(.light):not(.dark) {\n      color-scheme: dark;\n"
    for name, value in _semantic("dark"):
        out += f"      --{name}: {value};\n"
    out += "    }\n  }\n"

    # 3. element routing: which face each element takes, whatever the scale
    out += "\n"
    out += f"  /* {T.ROLE['hero'].job} */\n"
    out += f"  :root {{ --font-hero: var(--font-{T.HERO_ROLE_OUTSIDE}); }}\n"
    for route in T.ROUTING:
        decl = "; ".join((f"font-family: var(--font-{route.role})", *route.extra)) + ";"
        out += f"  {route.elements} {{ {decl} }}\n"
    out += "  body { -webkit-font-smoothing: antialiased; }\n"
    out += "  :focus-visible { outline: 2px solid var(--ring); outline-offset: 2px; }\n"
    out += "}\n\n"

    # 4. the semantic utilities: bg-background, text-muted-foreground, ring-ring ...
    out += "@theme inline {\n"
    for name in SEMANTIC_NAMES:
        out += f"  --color-{name}: var(--{name});\n"
    out += "  --radius-sm: calc(var(--radius) - 4px);\n"
    out += "  --radius-md: calc(var(--radius) - 2px);\n"
    out += "  --radius-lg: var(--radius);\n"
    out += "  --radius-xl: calc(var(--radius) + 4px);\n"
    out += "}\n\n"

    # 5. the two type scales
    for scale in T.SCALES:
        out += f"/* {scale.name} scale: {scale.use} */\n"
        for st in scale.steps:
            out += f"@utility text-{scale.key}-{st.name} {{ {T.step_css(st, scale.key)} }}\n"
        out += "\n"
    admitted = " and ".join(f"text-{s.key}-{st.name}" for s in T.SCALES for st in s.steps if st.hero)
    out += f"/* line 1 of a hero: Space Grotesk inside {admitted}, Geist everywhere else */\n"
    out += f"@utility {T.HERO_CLASS} {{ font-family: var(--font-hero); }}\n\n"
    out += "/* the code face with texture healing, for anything not already routed */\n"
    out += f"@utility font-code {{ font-family: var(--font-mono); font-feature-settings: {T.FACE['mono'].features}; }}\n"
    return out


def _export_name(family: str) -> str:
    """A face's export in next-fonts.ts: `Space Grotesk` is `spaceGrotesk`."""
    words = re.findall(r"[A-Za-z0-9]+", family)
    return words[0].lower() + "".join(w[:1].upper() + w[1:] for w in words[1:])


def next_fonts_ts() -> str:
    fb = lambda face: ", ".join(f'"{s.strip().strip(chr(34))}"' for s in face.stack.split(",") if "monospace" not in s and "sans-serif" not in s)  # noqa: E731
    reads = (
        f"reads {T.TEXT_FACE.family} into --font-sans and --font-display, "
        if T.HEADING_FACE is T.TEXT_FACE
        else f"reads {T.TEXT_FACE.family} into --font-sans, {T.HEADING_FACE.family} into --font-display, "
    )
    tail = _wrap(
        "Each loader sets one CSS variable on <html>. tokens/house-tailwind.css "
        + reads
        + f"{T.CODE_FACE.family} into --font-mono, and {T.WORDMARK_FACE.family} into --font-wordmark and a marketing hero."
    )
    out = (
        "// GENERATED by build/build.py from theme/theme.json. Do not edit.\n"
        "//\n"
        f"// The {_count(T.FACES)} house faces for next/font/local. The paths are relative to\n"
        "// this file: tokens/ beside fonts/, as in the kit. Keep that layout where\n"
        "// the two are vendored, or rewrite the paths there. In the root layout:\n"
        "//\n"
        '//   import { fontVariables } from "@/styles/next-fonts";\n'
        '//   <html lang="en" className={fontVariables}>\n'
        "//\n"
        + "".join(f"// {line}\n" for line in tail)
        + "\n"
        'import localFont from "next/font/local";\n\n'
    )
    for face in T.FACES:
        out += f"/** {face.family}: {face.job}. */\n"
        out += f"export const {_export_name(face.family)} = localFont({{\n"
        if len(face.files) == 1:
            file, w = face.files[0]
            out += f'  src: "../fonts/{file}",\n  weight: "{w}",\n'
        else:
            out += "  src: [\n"
            for file, w in face.files:
                out += f'    {{ path: "../fonts/{file}", weight: "{w}", style: "normal" }},\n'
            out += "  ],\n"
        out += f'  variable: "{face.next_var}",\n  display: "swap",\n'
        out += f"  fallback: [{fb(face)}],\n"
        if face.key == "mono":
            out += "  adjustFontFallback: false,\n"
        out += "});\n\n"
    out += "/** Every variable, for the <html> className. */\n"
    joined = ", ".join(f"{_export_name(f.family)}.variable" for f in T.FACES)
    out += f"export const fontVariables = [{joined}].join(\" \");\n"
    return out


def build_tokens() -> None:
    write("tokens/house-tokens.css", house_tokens_css())
    write("tokens/house-fonts.css", house_fonts_css())
    write("tokens/house-tailwind.css", house_tailwind_css())
    write("tokens/next-fonts.ts", next_fonts_ts())
    write(SKILL_TOKENS, PG.skill_tokens_css())

    gL, gC, gH = C.hex_to_oklch(C.GOLD)
    marks = {}
    for b in BRAND_WORDS:
        m = G.wordmark(str(BRANDS[b]["text"]))
        marks[b] = {
            "text": m["text"],
            "accent": BRANDS[b]["accent"],
            "box": [m["width"], m["height"]],
            "baseline": m["baseline"],
        }
    payload = {
        "version": "2.6.0",
        "name": "oxagen house system",
        "built_on": "oxagen brand kit (Space Grotesk), on obsidian and white with one gold",
        "icons": {
            "oxagen": {
                "kind": "hive",
                "cells": [{"col": c, "row": r, "kind": k} for c, r, k in MK.HIVE_CELLS],
                "cell": {k: v for k, v in MK.HIVE.items()},
                "half": MK.HIVE_HALF,
                "colours": 2,
                "note": "outlines take the surface's ink; the two lit cells take the metal",
            },
            "stella": {"kind": "glyph", "text": "*", "family": T.WORDMARK_FACE.family,
                       "weight": G.LOGO_WEIGHT, "colours": 1, "note": "the metal"},
        },
        "gold": {
            "hex": C.GOLD,
            "oklch": {"L": round(gL, 4), "C": round(gC, 4), "H": round(gH, 2)},
            "bright_oklch": dict(zip("LCH", C.GOLD_BRIGHT_LCH)),
            "deep_oklch": dict(zip("LCH", C.GOLD_DEEP_LCH)),
            "bright": C.GOLD_BRIGHT,
            "deep": C.GOLD_DEEP,
            "on_ink": round(C.contrast(C.GOLD, C.INK), 2),
            "deep_on_paper": round(C.contrast(C.GOLD_DEEP, C.PAPER), 2),
        },
        "tokens": {name: value for name, value, _ in C.TOKENS},
        "states": {
            name: {
                "ink": d, "paper": l, "use": u,
                "text_ink": C.STATE_TEXT[name]["dark"], "text_paper": C.STATE_TEXT[name]["light"],
            }
            for name, d, l, u in C.STATES
        },
        "destructive": {
            "ink": C.DESTRUCTIVE["dark"], "paper": C.DESTRUCTIVE["light"], "lift": C.DESTRUCTIVE_LIFT,
            "text_ink": C.STATE_TEXT["destructive"]["dark"], "text_paper": C.STATE_TEXT["destructive"]["light"],
        },
        "state_text": {
            "rule": "a word in a state's colour takes its text stop; a badge or a dot takes the bare stop",
            "l_on_ink": C.TEXT_L_ON_INK,
            "oklch": {name: {t: dict(zip("LCH", v)) for t, v in th.items()} for name, th in C.STATE_TEXT_LCH.items()},
            "surfaces": C.TEXT_SURFACES,
        },
        "semantic": {theme: dict(_semantic(theme)) for theme in ("light", "dark")},
        "type": {
            "family": T.GEIST.family,
            "display_family": T.SPACE_GROTESK.family,
            "mono_family": T.MONASPACE_NEON.family,
            "weights": list(G.WEIGHTS),
            "logo_weight": G.LOGO_WEIGHT,
            "logo_em": round(G.EM, 3),
            **T.as_json(),
        },
        "radius": {
            "base": RADIUS["base"],
            "steps": RADIUS["steps"],
            "card": RADIUS["card"],
            "site": RADIUS["site"],
        },
        "shadow": SHADOW,
        "spacing": THEME["spacing"],
        "wordmarks": marks,
    }
    write("tokens/house-tokens.json", json.dumps(payload, indent=2) + "\n")


def build_logos(raster: bool) -> list[Path]:
    made = []
    for b in BRAND_WORDS:
        wm = {
            "dark": wordmark_svg(b, uid=f"{b}-d"),
            "light": wordmark_svg(b, letters=C.INK_TEXT, uid=f"{b}-l"),
            "adaptive": wordmark_svg(b, adaptive=True, uid=f"{b}-a"),
            "mono": wordmark_svg(b, mono="currentColor"),
            "mono-white": wordmark_svg(b, mono=C.PAPER_TEXT),
            "mono-black": wordmark_svg(b, mono=C.INK_TEXT),
            "sheen-dark": wordmark_svg(b, sheen=True, uid=f"{b}-sd"),
            "sheen-light": wordmark_svg(b, letters=C.INK_TEXT, sheen=True, uid=f"{b}-sl"),
            "dark-onground": wordmark_svg(b, background=C.INK, uid=f"{b}-dg"),
            "light-onground": wordmark_svg(b, letters=C.INK_TEXT, background=C.PAPER, uid=f"{b}-lg"),
        }
        for name, svg in wm.items():
            made.append(write(f"logo/svg/{b}-wordmark-{name}.svg", svg))
        ic = {
            "dark": icon_svg(b, uid=f"{b}-id"),
            "light": icon_svg(b, letters=C.INK_TEXT, uid=f"{b}-il"),
            "adaptive": icon_svg(b, adaptive=True, uid=f"{b}-ia"),
            "mono-white": icon_svg(b, mono=C.PAPER_TEXT),
            "mono-black": icon_svg(b, mono=C.INK_TEXT),
            "tile-dark": icon_svg(b, background=C.INK, radius=20, sheen=True, uid=f"{b}-td"),
            "tile-light": icon_svg(b, background=C.PAPER, letters=C.INK_TEXT, radius=20, sheen=True, uid=f"{b}-tl"),
        }
        for name, svg in ic.items():
            made.append(write(f"logo/svg/{b}-icon-{name}.svg", svg))
    lk = {
        "dark": lockup_svg(),
        "light": lockup_svg(letters=C.INK_TEXT),
        "adaptive": lockup_svg(adaptive=True),
        "mono-white": lockup_svg(mono=C.PAPER_TEXT),
        "mono-black": lockup_svg(mono=C.INK_TEXT),
        "sheen-dark": lockup_svg(sheen=True, uid="lk-sd"),
        "sheen-light": lockup_svg(letters=C.INK_TEXT, sheen=True, uid="lk-sl"),
        "dark-onground": lockup_svg(background=C.INK),
        "light-onground": lockup_svg(letters=C.INK_TEXT, background=C.PAPER),
    }
    for name, svg in lk.items():
        made.append(write(f"logo/svg/oxagen-lockup-{name}.svg", svg))
    # The branding skill carries the adaptive lockup as its logo; --check
    # fails if the two ever differ.
    write(SKILL_LOGO, lk["adaptive"])

    if raster:
        for p in made:
            if "mono.svg" in p.name or "adaptive" in p.name:
                continue  # currentColor has no colour in a PNG
            if "-icon-" in p.name:
                for w in (256, 512, 1024):
                    png(p, width=w, out=ROOT / "logo/png" / f"{p.stem}-{w}.png")
            else:
                for w in (512, 1024, 2048):
                    png(p, width=w, out=ROOT / "logo/png" / f"{p.stem}-{w}w.png")
    return made


def build_spinners() -> None:
    for b in BRAND_WORDS:
        write(f"spinners/{b}-spinner.svg", spinner_svg(b, uid=f"{b}-sp"))
        write(f"spinners/{b}-spinner-tile-dark.svg", spinner_svg(b, background=C.INK, uid=f"{b}-spd"))
        write(f"spinners/{b}-spinner-wordmark.svg", spinner_wordmark_svg(b, uid=f"{b}-spw"))


def build_badges() -> None:
    """The GitHub badges: status pills, shields, and the commit tombstone (`badges.py`)."""
    for name, text in BD.files().items():
        write(f"github-badges/{name}", text)


DESKTOP = [(3840, 2160, "4k"), (5120, 2880, "5k"), (6016, 3384, "6k")]
PHONE = [(1290, 2796, "iphone-pro"), (1179, 2556, "iphone"), (1320, 2868, "iphone-pro-max")]


def build_wallpapers(raster: bool) -> None:
    for b in BRAND_WORDS:
        for scheme in ("dark", "light"):
            for style in SF.WALLPAPER_STYLES:
                for w, h, tag in DESKTOP:
                    p = write(
                        f"wallpapers/desktop/{b}-desktop-{tag}-{style}-{scheme}.svg",
                        SF.wallpaper_desktop(w, h, b, scheme, style),
                    )
                    if raster:
                        png(p, width=w)
                for w, h, tag in PHONE:
                    p = write(
                        f"wallpapers/phone/{b}-{tag}-{style}-{scheme}.svg",
                        SF.wallpaper_phone(w, h, b, scheme, style),
                    )
                    if raster:
                        png(p, width=w)


#: Every launch screen iOS and iPadOS ask a home-screen web app for, as the
#: device's CSS size and pixel ratio. Safari shows an `apple-touch-startup-image`
#: only when its media query matches the screen exactly, so a size missing here
#: launches on a flat colour. Phones launch upright; an iPad launches in the
#: orientation it is held, so each iPad size also has its landscape screen.
SPLASH_PHONES = [
    (440, 956, 3),   # iPhone 16 Pro Max
    (402, 874, 3),   # iPhone 16 Pro
    (430, 932, 3),   # iPhone 16 Plus, 15 Plus, 15 Pro Max, 14 Pro Max
    (393, 852, 3),   # iPhone 16, 15, 15 Pro, 14 Pro
    (428, 926, 3),   # iPhone 14 Plus, 13 Pro Max, 12 Pro Max
    (390, 844, 3),   # iPhone 14, 13, 13 Pro, 12, 12 Pro
    (375, 812, 3),   # iPhone 13 mini, 12 mini, 11 Pro, XS, X
    (414, 896, 3),   # iPhone 11 Pro Max, XS Max
    (414, 896, 2),   # iPhone 11, XR
    (414, 736, 3),   # iPhone 8 Plus
    (375, 667, 2),   # iPhone SE 2nd and 3rd generation, 8
    (320, 568, 2),   # iPhone SE 1st generation
]
SPLASH_TABLETS = [
    (1032, 1376, 2),  # iPad Pro 13-inch (M4)
    (1024, 1366, 2),  # iPad Pro 12.9-inch
    (834, 1210, 2),   # iPad Pro 11-inch (M4)
    (834, 1194, 2),   # iPad Pro 11-inch
    (820, 1180, 2),   # iPad Air 10.9-inch, iPad 10th generation
    (834, 1112, 2),   # iPad Air 10.5-inch
    (810, 1080, 2),   # iPad 10.2-inch
    (744, 1133, 2),   # iPad mini 6th generation
    (768, 1024, 2),   # iPad mini 5th generation, iPad 9.7-inch
]


def splash_screens() -> list[dict[str, object]]:
    """One row per launch screen: its CSS size, pixel ratio, orientation and pixels."""
    rows: list[dict[str, object]] = []
    for devices, turns in ((SPLASH_PHONES, ("portrait",)), (SPLASH_TABLETS, ("portrait", "landscape"))):
        for cw, ch, ratio in devices:
            for turn in turns:
                w, h = (cw * ratio, ch * ratio) if turn == "portrait" else (ch * ratio, cw * ratio)
                rows.append({"deviceWidth": cw, "deviceHeight": ch, "pixelRatio": ratio,
                             "orientation": turn, "width": w, "height": h})
    return rows


def build_splash(raster: bool) -> None:
    """The launch screens of an installed app, and the table that places them.

    `splash/splash-screens.json` lists every screen with the media query Safari
    matches it on, so a product writes its `apple-touch-startup-image` links from
    the table rather than from a hand-kept list of device sizes.
    """
    rows = splash_screens()
    for b in BRAND_WORDS:
        for scheme in ("dark", "light"):
            for r in rows:
                w, h = int(r["width"]), int(r["height"])
                p = write(f"splash/{b}-splash-{w}x{h}-{scheme}.svg", SF.splash(w, h, b, scheme))
                if raster:
                    png(p, width=w)
    table = [
        {
            **r,
            "file": "{brand}-splash-%dx%d-{scheme}.png" % (r["width"], r["height"]),
            "media": (
                f"(device-width: {r['deviceWidth']}px) and (device-height: {r['deviceHeight']}px)"
                f" and (-webkit-device-pixel-ratio: {r['pixelRatio']}) and (orientation: {r['orientation']})"
            ),
        }
        for r in rows
    ]
    write("splash/splash-screens.json", json.dumps({"screens": table}, indent=2) + "\n")


def build_social(raster: bool) -> None:
    for b in BRAND_WORDS:
        tag = TAGLINES[b]
        for scheme in ("dark", "light"):
            jobs = [
                (f"social/{b}-avatar-{scheme}.svg", SF.avatar(b, 1024, scheme), 1024),
                (f"social/{b}-x-header-{scheme}.svg", SF.banner(1500, 500, b, scheme, tagline=tag), 1500),
                (
                    f"social/{b}-linkedin-banner-{scheme}.svg",
                    SF.banner(1584, 396, b, scheme, tagline=tag),
                    1584,
                ),
                (
                    f"social/{b}-youtube-banner-{scheme}.svg",
                    SF.banner(2560, 1440, b, scheme, tagline=tag, safe_h=423),
                    2560,
                ),
                (f"social/{b}-og-1200x630-{scheme}.svg", SF.og_card(1200, 630, b, scheme, tagline=tag), 1200),
            ]
            for rel, svg, w in jobs:
                p = write(rel, svg)
                if raster:
                    png(p, width=w)


#: Every campaign is an approved, launch-released `kind: ad` entry in
#: `messages/ads/` or `messages/always-on/`. Held and retired entries are not rendered, and
#: `build/messages.py --check` fails on any file in `ads/` that no entry
#: produces. The Oxagen campaign follows the operator's job: the workforce ad
#: states the job, and each of the others explains one decision an operator
#: makes, with its scope kept in the short form.
#:
#: Each campaign carries `headline`, the tall stack for the square and the
#: portrait; `wide`, the same words in long lines for the landscape, where a
#: four-line stack would shrink to fit; and `short`, what the 300x250 carries,
#: because a banner is not a poster with its middle line deleted. `picture`
#: names the composition in the top right and defaults to the ghost.
#:
#: No benchmark numbers and no competitor is named in public art: a number in
#: an ad is a claim the ad has to keep being true.
AD_COPY: dict[str, list[dict[str, object]]] = MS.ad_campaigns()
AD_SIZES = MS.AD_SIZES


def ad_svg(brand: str, campaign: dict[str, object], w: int, h: int, tag: str, scheme: str) -> str:
    """One campaign at one size. The small formats carry their own, shorter copy.

    A banner is not a poster with the middle line deleted. The 300x250 drops
    the kicker and the call to action -- there is no room for either at a
    legible size -- but it keeps the answer line, in its short form, because
    that line is the reason the ad exists. The qualifier, the scope sentence
    the registry keeps beside the line, goes under the answer line at every
    size where it fits, because a short form keeps the qualifier of its
    longer version.
    """
    small = tag == "mpu"
    key = "short" if small else ("wide" if tag == "landscape" and "wide" in campaign else "headline")
    sub = campaign.get("subshort" if small else "subline", "")
    return SF.ad(
        w, h, brand, scheme,
        kicker="" if small else str(campaign["kicker"]),
        headline=list(campaign[key]),  # type: ignore[call-overload]
        subline=str(sub),
        qualifier=str(campaign.get("qualifier", "")),
        cta="" if small else str(campaign["cta"]),
        picture=str(campaign.get("picture", "ghost")),
    )


def build_ads(raster: bool) -> None:
    for b in BRAND_WORDS:
        for campaign in AD_COPY[b]:
            for scheme in ("dark", "light"):
                for w, h, tag in AD_SIZES:
                    p = write(
                        f"ads/{b}-{campaign['slug']}-{tag}-{w}x{h}-{scheme}.svg",
                        ad_svg(b, campaign, w, h, tag, scheme),
                    )
                    if raster:
                        png(p, width=w)


CONTENT = {
    "oxagen": [
        ("Field note", ["The meter runs.", "The knowledge", "leaves."], "The field manual", None),
        ("Essay", ["Own the model that", "learns your business"], "Engineering notes", None),
        ("Release", ["Oxagen platform"], "oxagen.sh/changelog",
         ["+ agent identity, roles, and budgets on governed calls",
          "+ every run saved as a trace beside its data"]),
        # The card an operator's weekly fleet report goes out on. Its panel is
        # the fleet's week in three rows, not a terminal: the card's text face
        # is Geist, not a code face, so nothing here is set as command output.
        ("Fleet note", ["What the fleet", "asked for this week"], "The weekly fleet report",
         ["9 agents ran under mandate",
          "4 requests routed to a person",
          "1 agent held at its budget"]),
        # The always-on campaign, from Mac's draft of 2026-09-26. The title is
        # the approved night-shift ad.
        ("Always-on", ["Sleep tight.", "Your agents are", "on the job."], "The always-on campaign", None),
    ],
    "stella": [
        ("Changelog", ["Parallel tool calls,", "now measured"], "30 Aug 2026 · Engineering",
         ["$ stella run --pipeline vera", "  witness authored    fail -> pass",
          "  verdict CONFIRMED   12.4s"]),
        ("Essay", ["A green check is not", "an answer"], "Engineering notes", None),
        ("Release", ["stella 0.9.305"], "brew upgrade stella",
         ["+ skills mined from proven runs", "+ settings picked by measured A/B"]),
    ],
}


def build_content(raster: bool) -> None:
    for b in BRAND_WORDS:
        for scheme in ("dark", "light"):
            for kind, title, meta, body in CONTENT[b]:
                slug = kind.lower().replace(" ", "-")
                p = write(
                    f"content/{b}-{slug}-{scheme}.svg",
                    SF.content_card(1200, 675, b, scheme, kind=kind, title=title, meta=meta, body=body),
                )
                if raster:
                    png(p, width=1200)


def ico(pngs: list[Path], out: Path) -> None:
    """Pack PNGs into one `.ico`, the file a browser still asks for first.

    An ICO is a directory of images; since Vista the images may be PNGs
    whole, and every browser that runs today reads them that way. Written
    by hand, because it is forty lines of header and not worth a dependency.
    """
    import struct

    if CHECKING is not None:
        CHECKING[out] = None
        return
    blobs = [q.read_bytes() for q in pngs]
    head = struct.pack("<HHH", 0, 1, len(blobs))
    offset = 6 + 16 * len(blobs)
    entries = b""
    for q, blob in zip(pngs, blobs):
        w, h = struct.unpack(">II", blob[16:24])
        entries += struct.pack("<BBBBHHII", w % 256, h % 256, 0, 0, 1, 32, len(blob), offset)
        offset += len(blob)
    out.write_bytes(head + entries + b"".join(blobs))


#: What a home screen wants, by name. `maskable` is drawn to the platform's
#: safe zone: full-bleed ink, the mark inside the centre four-fifths, so a
#: launcher that crops to a circle or a squircle does not clip a cell.
MASKABLE_FILL = {"stella": 0.50, "oxagen": 0.56}


def build_favicons(raster: bool) -> None:
    """The favicon, the app icons, and the files a PWA points at.

    The SVG favicon is adaptive: a browser that takes an SVG favicon gets a
    mark whose ink follows the tab's own colour scheme.

    A PNG cannot adapt, and that is what decides where each brand's small
    sizes come from. Stella's asterisk is gold, and gold is legible on a
    light tab and a dark one alike, so it rasterises on nothing. The hive's
    outline is one colour: on nothing it would be paper on a paper-coloured
    tab, which is no favicon at all. So Oxagen's small PNGs come from a
    favicon tile -- the favicon's heavier outline on an ink ground, shipped
    beside the SVG it is a render of. Both brands take 180 and up from the
    icon tile, because a home-screen icon is a tile and at that size the
    outline as drawn holds.

    Beside the PNGs: a `.ico` packing 16, 32 and 48; a maskable 192 and 512
    for Android and the desktop installers; and a `.webmanifest` that names
    all of them, ready to copy into an app's public folder.

    Every raster comes twice: on the obsidian tile (the unsuffixed names,
    unchanged for existing consumers) and on a white tile (`-light`), with
    its own `.ico` and `.webmanifest`.
    """
    for b in BRAND_WORDS:
        fav = write(f"logo/svg/{b}-favicon.svg", favicon_svg(b, adaptive=True))
        small = write(f"logo/svg/{b}-favicon-tile.svg", favicon_svg(b, background=C.INK, radius=14)) if b == "oxagen" else fav
        mask = write(f"logo/svg/{b}-icon-maskable.svg", icon_svg(b, background=C.INK, fill=MASKABLE_FILL[b], sheen=True, uid=f"{b}-mk"))
        # The light set: the same marks on a white tile, ink outlines, gold
        # only where the mark is gold. For a light app shell or a light tab.
        small_l = write(
            f"logo/svg/{b}-favicon-tile-light.svg",
            favicon_svg(b, background=C.PAPER, radius=14, letters=C.INK_TEXT),
        )
        mask_l = write(
            f"logo/svg/{b}-icon-maskable-light.svg",
            icon_svg(b, background=C.PAPER, fill=MASKABLE_FILL[b], letters=C.INK_TEXT, uid=f"{b}-mkl"),
        )
        write(f"icons/{b}.webmanifest", manifest(b))
        write(f"icons/{b}-light.webmanifest", manifest(b, light=True))
        if not raster:
            continue
        for theme, tile, fav_small, maskable in (
            ("", ROOT / f"logo/svg/{b}-icon-tile-dark.svg", small, mask),
            ("-light", ROOT / f"logo/svg/{b}-icon-tile-light.svg", small_l, mask_l),
        ):
            for size in (16, 32, 48, 180, 192, 512):
                png(tile if size > 48 else fav_small, width=size, height=size, out=ROOT / "icons" / f"{b}-icon{theme}-{size}.png")
            for size in (192, 512):
                png(maskable, width=size, height=size, out=ROOT / "icons" / f"{b}-icon-maskable{theme}-{size}.png")
            ico([ROOT / "icons" / f"{b}-icon{theme}-{n}.png" for n in (16, 32, 48)], ROOT / "icons" / f"{b}-favicon{theme}.ico")


def manifest(brand: str, *, light: bool = False) -> str:
    """A web app manifest for the brand, pointing at the icons this build writes.

    `light` names the white-tile icons and a white splash, for an app whose
    shell is light.
    """
    name = str(BRANDS[brand]["label"])
    t = "-light" if light else ""
    ground = C.PAPER if light else C.INK
    payload = {
        "name": name.capitalize() if brand == "oxagen" else "Stella",
        "short_name": name.capitalize() if brand == "oxagen" else "Stella",
        "description": TAGLINES[brand],
        "start_url": "/",
        "display": "standalone",
        "background_color": ground,
        "theme_color": ground,
        "icons": [
            {"src": f"{brand}-icon{t}-192.png", "sizes": "192x192", "type": "image/png"},
            {"src": f"{brand}-icon{t}-512.png", "sizes": "512x512", "type": "image/png"},
            {"src": f"{brand}-icon-maskable{t}-192.png", "sizes": "192x192", "type": "image/png", "purpose": "maskable"},
            {"src": f"{brand}-icon-maskable{t}-512.png", "sizes": "512x512", "type": "image/png", "purpose": "maskable"},
        ],
    }
    return json.dumps(payload, indent=2) + "\n"


_SVG_ID = re.compile(r'\bid="([^"]+)"')


def canonical_svg(text: str) -> str:
    """An SVG with its ids renumbered in the order they appear.

    `surfaces.py` numbers gradient ids from one counter per process, so the
    same drawing takes other ids when the build runs its steps in another
    order or alone. Two files that differ only in those numbers draw the same
    thing, and the drift check compares them in this form.
    """
    ids = list(dict.fromkeys(_SVG_ID.findall(text)))
    if not ids:
        return text
    names = {old: f"id{i}" for i, old in enumerate(ids)}
    pattern = re.compile(r"(?<![\w-])(" + "|".join(re.escape(i) for i in sorted(ids, key=len, reverse=True)) + r")(?![\w-])")
    return pattern.sub(lambda m: names[m.group(1)], text)


def drift() -> list[str]:
    """Every generated file that differs from what the theme produces, is missing, or is left over.

    The build runs once more with every write sent to memory. Each text file
    must match the file on disk, an SVG up to its id numbers. Each PNG and
    ICO must exist. A file in a generated directory that the build does not
    write is left over from an older build. `playbook.html` must match
    `build/playbook.py`.
    """
    global CHECKING
    CHECKING = {}
    try:
        run_steps(set(STEPS), raster=True)
        made = CHECKING
    finally:
        CHECKING = None

    differs, missing = [], []
    for path, text in made.items():
        rel = path.relative_to(ROOT).as_posix()
        if not path.is_file():
            missing.append(rel)
        elif text is not None:
            disk = path.read_text()
            if disk != text and (path.suffix != ".svg" or canonical_svg(disk) != canonical_svg(text)):
                differs.append(rel)
    stale = sorted(
        f.relative_to(ROOT).as_posix()
        for d in GENERATED
        for f in (ROOT / d).rglob("*")
        if f.is_file() and f.suffix in GENERATED_SUFFIXES and f not in made
    )

    import playbook

    SF._IDS[0] = 0  # as when build/playbook.py runs on its own
    page = ROOT / "playbook.html"
    if not page.is_file() or page.read_text() != playbook.build_html():
        differs.append("playbook.html")

    problems = []
    for one, many, paths, fix in (
        ("differs", "differ", differs, "run build/build.py and build/playbook.py"),
        ("is missing", "are missing", missing, "run build/build.py"),
        ("is left over", "are left over", stale, "run build/build.py, or delete the files"),
    ):
        if paths:
            verb = f"generated file {one}" if len(paths) == 1 else f"generated files {many}"
            where = " from what theme/theme.json produces" if one == "differs" else (
                " from an older build" if one == "is left over" else "")
            shown = ", ".join(paths[:8]) + (f", and {len(paths) - 8} more" if len(paths) > 8 else "")
            problems.append(f"{len(paths)} {verb}{where}: {shown}. To fix it, {fix}.")
    return problems


def check(drift_check: bool = True) -> int:
    problems = C.verify() + G.verify() + T.verify() + [f"fonts: {p}" for p in FT.check()] + RQ.check_schema()
    logo, lockup = ROOT / SKILL_LOGO, ROOT / "logo/svg/oxagen-lockup-adaptive.svg"
    if drift_check and (not logo.exists() or not lockup.exists() or logo.read_bytes() != lockup.read_bytes()):
        problems.append(f"{SKILL_LOGO} is not the adaptive lockup; run build/build.py --only logos")
    errors, _warnings, _context = MS.validate(MS.load(), MS.load_findings())
    problems += [f"messages: {e}" for e in errors]
    if drift_check and not problems:
        problems += drift()
    for p in problems:
        print("problem:", p)
    if not problems:
        ads = sum(len(v) for v in AD_COPY.values())
        print("check: theme/theme.json matches theme/theme.schema.json")
        print(f"check: {ads} ads and {len(TAGLINES)} taglines come from approved, launch-released registry entries")
        m = G.wordmark("oxagen")
        if G.reference_applies():
            print(f"check: oxagen reproduces the kit wordmark ({m['width']:g} x {m['height']:g}, em {G.EM:.2f})")
        else:
            print(f"check: the marks are drawn from fonts/{G.FONT.name} at {G.LOGO_WEIGHT}, so the reference "
                  f"wordmark check is skipped: this theme changes the logo ({m['width']:g} x {m['height']:g})")
        print(f"check: gold {C.GOLD}, with bright {C.GOLD_BRIGHT} and deep {C.GOLD_DEEP} derived from it in OKLCH")
        print("check: every text token clears AA on its ground")
        print(f"check: {len(T.FACES)} faces in fonts/, {len(T.SCALES)} type scales, every heading in {T.HEADING_FACE.family}, "
              f"{T.WORDMARK_FACE.family} on the wordmarks and a marketing hero only")
        if drift_check:
            print("check: every generated file, the skill's tokens, and playbook.html match theme/theme.json")
    return 1 if problems else 0


def run_steps(steps: set[str], raster: bool) -> None:
    """Run each build step in `steps`, in the order STEPS lists them."""
    run = {
        "tokens": build_tokens,
        "logos": lambda: build_logos(raster),
        "icons": lambda: build_favicons(raster),
        "spinners": build_spinners,
        "wallpapers": lambda: build_wallpapers(raster),
        "splash": lambda: build_splash(raster),
        "social": lambda: build_social(raster),
        "ads": lambda: build_ads(raster),
        "content": lambda: build_content(raster),
        "badges": build_badges,
    }
    for step in STEPS:
        if step in steps:
            run[step]()
            if CHECKING is None:
                print(f"{step:<13} ok")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--svg", action="store_true", help="skip the raster pass")
    ap.add_argument("--check", action="store_true", help="verify, write nothing")
    ap.add_argument("--only", nargs="+", choices=list(STEPS), metavar="STEP",
                    help=f"build only these steps ({', '.join(STEPS)}); empties only their directories")
    args = ap.parse_args()
    if args.check:
        sys.exit(check())
    raster = not args.svg
    if raster and not shutil.which("rsvg-convert"):
        sys.exit("rsvg-convert not found -- `brew install librsvg`, or pass --svg")
    if check(drift_check=False):
        sys.exit("the kit does not verify; not writing")

    steps = set(args.only or STEPS)
    if "logos" in steps:
        steps.add("icons")  # the favicons are written into logo/svg beside the marks
    for step in STEPS:
        if step in steps:
            for d in STEPS[step]:
                # Only what a build writes. Hand-written notes that live beside
                # the art (content/*.md) survive a rebuild.
                for f in (ROOT / d).rglob("*"):
                    if f.is_file() and f.suffix in GENERATED_SUFFIXES:
                        f.unlink()
    (ROOT / "logo/png").mkdir(parents=True, exist_ok=True)
    (ROOT / "icons").mkdir(parents=True, exist_ok=True)

    run_steps(steps, raster)

    n = sum(1 for _ in ROOT.rglob("*") if _.is_file() and _.suffix in {".svg", ".png"} and ".venv" not in _.parts)
    print(f"\n{n} files under {ROOT}")


if __name__ == "__main__":
    main()
