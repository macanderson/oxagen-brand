"""The short CSS variable set the kit's own pages and the branding skill use.

`tokens/house-tokens.css` names every value `--ox-*` for products. A page in
this repo (the playbook, the message bank) and the skill's `assets/tokens.css`
use a shorter set that flips with the theme: `--ink` is the page ground in
either theme, `--fg` its primary text. This module writes that set from
`theme/theme.json`, through `color.py` and `typeset.py`, so no page carries a
hex of its own.
"""

from __future__ import annotations

import re

import color as C
import typeset as T
from theme import THEME, rem_px


def _dark() -> dict[str, str]:
    v = {
        "ink": C.INK, "void": C.VOID, "panel": C.PANEL, "hl": C.HL, "border": C.BORDER, "rule": C.RULE,
        "fg": C.PAPER_TEXT, "body": C.TEXT, "muted": C.MUTED, "dim": C.DIM,
        "gold": C.GOLD, "gold-bright": C.GOLD_BRIGHT, "gold-deep": C.GOLD_DEEP,
        "accent-text": C.GOLD, "on-gold": C.INK, "destructive": C.DESTRUCTIVE["dark"],
    }
    v.update({f"state-{n}": d for n, d, _, _ in C.STATES})
    v.update({f"state-{n}-text": C.STATE_TEXT[n]["dark"] for n, _, _, _ in C.STATES})
    v.update({"destructive-text": C.STATE_TEXT["destructive"]["dark"], "muted-text": C.MUTED})
    return v


def _light() -> dict[str, str]:
    v = {
        "ink": C.PAPER, "void": C.PAPER_VOID, "panel": C.PAPER_PANEL, "hl": C.PAPER_HL,
        "border": C.PAPER_BORDER, "rule": C.PAPER_RULE,
        "fg": C.INK_TEXT, "body": C.TEXT_INK, "muted": C.MUTED_INK, "dim": C.DIM_INK,
        "accent-text": C.GOLD_DEEP, "destructive": C.DESTRUCTIVE["light"],
    }
    v.update({f"state-{n}": l for n, _, l, _ in C.STATES})
    v.update({f"state-{n}-text": C.STATE_TEXT[n]["light"] for n, _, _, _ in C.STATES})
    v.update({"destructive-text": C.STATE_TEXT["destructive"]["light"], "muted-text": C.MUTED_TEXT_INK})
    return v


def _block(values: dict[str, str], indent: str = "  ") -> str:
    return "\n".join(f"{indent}--{k}: {v};" for k, v in values.items())


def resolve(css: str) -> str:
    """`css` with each `var(--ox-<token>)` replaced by the token's hex, for a page that loads no token file."""
    tokens = {name: value for name, value, _ in C.TOKENS}
    return re.sub(r"var\(--ox-([a-z-]+)\)", lambda m: tokens[m.group(1)], css)


def _shape(theme: str) -> dict[str, str]:
    """The shadows for one theme, in the short names: `ink` is the dark theme and `paper` the light."""
    shadow = THEME["shadow"]
    return {"shadow-ui": resolve(shadow["ui"][theme]), "shadow-pop": resolve(shadow["pop"][theme])}


def _shape_fixed() -> dict[str, str]:
    """The corners and spacing, which do not flip with the theme."""
    radius = THEME["radius"]
    v = {"radius-base": radius["base"]}
    v.update({f"radius-{step}": f"calc(var(--radius-base) * {mult:g})" for step, mult in radius["steps"].items()})
    v["radius-card"] = f"var(--radius-{radius['card']})"
    v["space"] = THEME["spacing"]["unit"]
    return v


def type_sizes() -> dict[str, str]:
    """Each step of both scales and its leading, in the short names: `--m-body` is the marketing body."""
    v = {}
    for scale in T.SCALES:
        for st in scale.steps:
            v[f"{scale.key}-{st.name}"] = st.size
            v[f"{scale.key}-{st.name}-leading"] = st.leading
    return v


def page_vars(*, fonts: bool = True, shape: bool = False) -> str:
    """Dark first. Light by `data-theme="light"` or the OS preference.

    `fonts` adds the faces and the two type scales, so a page sets every size
    from a step (`font-size: var(--a-body)`) and writes none of its own.
    `shape` adds the corners, shadows, and spacing. The skill's tokens carry
    them. The kit's own pages set their own.
    """
    extra = ""
    if fonts:
        # --font-heading is the face this page's h1 to h3 take: the text face,
        # as in the app. A public page points it at --font-display, the
        # marketing heading face. --font-wordmark is the fixed wordmark face.
        extra = (
            f"\n  --font-display: {T.DISPLAY_FACE.css_stack};"
            f"\n  --font-heading: var(--font);"
            f"\n  --font-wordmark: {T.WORDMARK_FACE.css_stack};"
            f"\n  --font: {T.TEXT_FACE.css_stack};"
            f"\n  --mono: {T.MONASPACE_NEON.css_stack};"
            f"\n  --mono-features: {T.MONASPACE_NEON.features};"
            f"\n  --radius: {rem_px(THEME['radius']['site']):g}px; --wrap: {THEME['spacing']['wrap']};"
            "\n" + _block(type_sizes())
        )
    dark, light = _dark(), _light()
    if shape:
        extra += "\n" + _block({**_shape_fixed(), **_shape("ink")})
        light.update(_shape("paper"))
    return (
        ":root {\n" + _block(dark) + extra + "\n}\n"
        '@media (prefers-color-scheme: light) {\n  :root:not([data-theme="dark"]) {\n' + _block(light, "    ") + "\n  }\n}\n"
        ':root[data-theme="light"] {\n' + _block(light) + "\n}\n"
    )


def skill_tokens_css() -> str:
    return (
        "/* Oxagen design tokens for pages the branding skill guides.\n"
        " * GENERATED by build/build.py from theme/theme.json. Do not edit.\n"
        " * Products use tokens/house-tailwind.css instead; these are the same values. */\n"
        + page_vars(shape=True)
    )
