"""The literal guard: every colour, corner, shadow, space, and font size the kit sets.

    python3 build/css_literals.py            # list each literal, exit 1 if any
    python3 build/css_literals.py --report   # count the literals by scope and group

A theme change reaches the kit's components through the `--ox-*` tokens that
`build/build.py` writes from `theme/theme.json`. A corner, a shadow, a font
size, or a heading's line height written as a literal does not follow that
change, and a second declaration of the same value is how the two drift
apart. `build/build.py --check` runs this guard. It lists each literal with
its line and the token to read instead.

It reads two scopes:

- **The kit's stylesheet**, `ui/src/styles/globals.css`: every corner,
  shadow, font size, and heading line height, and every colour and space a
  rule (not a custom property) writes. Its custom properties are the
  mapping layer, which turns the raw tokens into semantic ones, so a colour
  there passes. `semantic_problems` holds each semantic token to one
  definition per theme.
- **Every component and page** (Mac, 2026-10-02: "we can't hard code font
  sizes in classes, we need to let the tokens do their job", and 2026-10-03:
  "everything has to be semantic driven from tokens"): the CSS, the stories,
  and the components in `ui/src`, the Work and Run app copies included, the
  SDLC page in `sdlc/public`, the PWA install prompt, and the kit's own pages
  (`playbook.html`, `message-bank.html`, `always-on.html`,
  `brand-guide.html`). Each colour, corner, shadow, space (padding, margin,
  gap), and font size reads a token. In a page it reads each `<style>` block
  and `style` attribute. In a script it reads Tailwind classes (a palette
  colour such as `bg-zinc-800`, a raw house colour such as `bg-ox-gold`, and
  an arbitrary value such as `gap-[7px]` or `text-[13px]`), a style object's
  values, an SVG colour attribute, and CSS written in a string. A custom
  property in a stylesheet is that file's token layer, so its colour and its
  space pass. Tests are not read, because they name classes to assert them.
  `EXEMPT` names the few whole files a group skips, each with its reason.

It is a regex pass with no CSS parser, on the model of the literal guard in
oxageninc/product (`tools/scripts/lib/brand-literals.mjs`).

What passes without an entry in KEEP:

- a value that reads a token (`var(--...)`) and writes no length of its own,
  a fallback inside the `var()` included;
- a Tailwind size that reads a token, `text-(length:--ox-a-h2)` or
  `text-[length:var(--ox-a-h2)]`, and Tailwind's named sizes `text-xs` to
  `text-3xl`, which `tokens/house-text-scale.css` points at the app steps in
  order (`text-base` is the app base). The kit's stylesheet imports that
  file. Tailwind's larger sizes (`text-4xl` and up) read no step, so they
  fail, and so does a text field's size on a phone written as a literal:
  it reads `text-input-touch`;
- a corner of 0, a circle (50%), or a pill (999px or 9999px);
- a ring, which is a shadow with no offset and no blur, such as a focus or
  hover ring, and an inset bar;
- a font size of 1em or more, or 100% or more, which never sets text below
  its parent.

A font size under 1em or under 100% fails, because it sets a size no step
names: `.9em` of a 14px body is 12.6px. Text that should be smaller reads a
smaller step, such as `text-sm` (micro) or `text-xs` (2xs). No rule here sets
a smallest size.

Every other literal is in KEEP, with its file and its reason. An entry that
matches nothing fails too, so the allowlist cannot outlive the literal it
excused. `sdlc/public/sdlc.css` names the type steps once, as it names its
colours, because that site cannot import `tokens/`. The guard holds those
names to the theme's values.
"""

from __future__ import annotations

import re
import sys
from dataclasses import dataclass
from pathlib import Path

import pagecss as PC
import typeset as T
from theme import ROOT, THEME, rem_px

KIT_CSS = "ui/src/styles/globals.css"

#: Where the guard reads font sizes, by kind, as globs from the repository root.
FONT_SCOPE: dict[str, tuple[str, ...]] = {
    "css": ("ui/src/**/*.css", "sdlc/public/*.css"),
    "html": ("playbook.html", "message-bank.html", "always-on.html", "brand-guide.html", "sdlc/public/*.html"),
    "script": ("ui/src/**/*.ts", "ui/src/**/*.tsx", "pwa/*.js", "sdlc/public/*.js"),
}

#: A file the guard does not read: a test names a class to assert it. Every
#: page is read, the Work and Run app copies in `ui/src/pages/app/` included,
#: because they are where the theme editor previews the app.
SKIP = re.compile(r"\.test\.[jt]sx?$")

#: The SDLC page's own names for the type steps, which must equal the theme's.
SDLC_CSS = "sdlc/public/sdlc.css"


@dataclass(frozen=True)
class Keep:
    """A literal a file keeps on purpose: its group, its value, why, and the file."""

    group: str
    value: str
    why: str
    path: str = KIT_CSS


#: The literals the guard excuses, by file, group, and value. A text field on
#: a phone reads `--text-input-touch` (`text-input-touch`), which holds iOS
#: Safari's 16px in the token layer, so no file here keeps a size of its own.
KEEP: tuple[Keep, ...] = ()


@dataclass(frozen=True)
class Decl:
    """One declaration: the selector it sits under, its property and value, and its line."""

    selector: str
    prop: str
    value: str
    line: int


@dataclass(frozen=True)
class Hit:
    """A literal that should read a token."""

    line: int
    group: str
    prop: str
    value: str
    use: str
    path: str = KIT_CSS


def strip_comments(css: str) -> str:
    """`css` with each comment blanked, newlines and quoted strings kept.

    A string may hold `/*`, as in `@source "../dist/*.js"`, so the pass skips
    strings rather than reading that as the start of a comment.
    """

    def blank(m: re.Match[str]) -> str:
        return m.group(1) or re.sub(r"[^\n]", " ", m.group(0))

    return re.sub(r"(\"[^\"\n]*\"|'[^'\n]*')|/\*.*?\*/", blank, css, flags=re.S)


_DECL = re.compile(r"\s*(--[\w-]+|[a-z][a-z-]*)\s*:(.*)", re.S)


def declarations(css: str) -> list[Decl]:
    """Every declaration in `css`, with the innermost selector it sits under."""
    text = strip_comments(css)
    out: list[Decl] = []
    stack: list[str] = []
    start = 0

    def flush(end: int) -> None:
        m = _DECL.match(text, start, end)
        if not m:
            return
        selector = next((p for p in reversed(stack) if not p.startswith("@")), "")
        line = text.count("\n", 0, m.start(1)) + 1
        out.append(Decl(selector, m.group(1), " ".join(m.group(2).split()), line))

    for i, ch in enumerate(text):
        if ch == "{":
            stack.append(" ".join(text[start:i].split()))
            start = i + 1
        elif ch in ";}":
            flush(i)
            if ch == "}" and stack:
                stack.pop()
            start = i + 1
    flush(len(text))
    return out


_HEADING = re.compile(r"(?<![\w.#-])h[1-6](?![\w-])")


def group_of(decl: Decl) -> str | None:
    """The group a declaration belongs to, or None when the guard does not read it.

    A custom property joins a group by its name, so an alias such as
    `--ui-radius: 0.5rem` is read as the corner it is.
    """
    p = decl.prop
    if p.startswith("--"):
        if "radius" in p:
            return "border-radius"
        if "shadow" in p:
            return "box-shadow"
        if "leading" in p or "line-height" in p:
            return "line-height"
        if "font-size" in p or (p.startswith("--text-") and "--" not in p[2:]):
            return "font-size"
        return None
    if re.fullmatch(r"border(-[a-z]+)*-radius", p):
        return "border-radius"
    if p == "box-shadow":
        return "box-shadow"
    if p in ("font-size", "font"):
        return "font-size"
    if p == "line-height" and _HEADING.search(decl.selector):
        return "line-height"
    return None


def without_vars(value: str) -> str:
    """`value` with every `var(...)` removed, nested ones included."""
    out, i = [], 0
    while i < len(value):
        if value.startswith("var(", i):
            depth, j = 0, i + 3
            while j < len(value):
                if value[j] == "(":
                    depth += 1
                elif value[j] == ")":
                    depth -= 1
                    if depth == 0:
                        break
                j += 1
            out.append(" ")
            i = j + 1
        else:
            out.append(value[i])
            i += 1
    return "".join(out)


_LENGTH = re.compile(r"(?<![\w.-])(-?\d*\.?\d+)(px|rem|pt)\b")
KEPT_CORNERS = {"0", "0px", "50%", "999px", "9999px"}


def _layers(value: str) -> list[str]:
    """`value` split at its top-level commas, so `rgb(0, 0, 0)` stays whole."""
    out, depth, start = [], 0, 0
    for i, ch in enumerate(value):
        if ch == "(":
            depth += 1
        elif ch == ")":
            depth -= 1
        elif ch == "," and depth == 0:
            out.append(value[start:i].strip())
            start = i + 1
    out.append(value[start:].strip())
    return out


def _ring_or_inset(layer: str) -> bool:
    """Whether a shadow layer is an inset, or a ring with no offset and no blur (`0 0 0 2px`)."""
    if re.search(r"\binset\b", layer):
        return True
    bare = layer
    while re.search(r"\([^()]*\)", bare):
        bare = re.sub(r"\([^()]*\)", "", bare)
    numbers = [float(re.match(r"-?\d*\.?\d+", part).group()) for part in bare.split()
               if re.fullmatch(r"-?\d*\.?\d+(px|rem|em)?", part)]
    return len(numbers) >= 3 and all(n == 0 for n in numbers[:3])


def is_literal(group: str, value: str) -> bool:
    """Whether `value` writes a literal that its group should take from a token."""
    bare = without_vars(value)
    if group == "border-radius":
        parts = re.split(r"[\s/(),]+", bare)
        return any(re.fullmatch(r"\d*\.?\d+(px|rem|em|%)", p) and p not in KEPT_CORNERS for p in parts)
    if group == "box-shadow":
        return any(_LENGTH.search(without_vars(layer)) and not _ring_or_inset(layer) for layer in _layers(value))
    if group == "font-size":
        return small_or_fixed(value)
    if group == "line-height":
        return bool(re.search(r"\d", bare))
    return False


_RELATIVE = re.compile(r"(?<![\w.-])(\d*\.?\d+)(em|%)(?![\w-])")
_SMALLER = re.compile(r"^(smaller|x-small|xx-small)$")


def small_or_fixed(value: str) -> bool:
    """Whether a font size writes a fixed length, or a relative one that sets text below its parent.

    A length inside a `var()`, such as a fallback, passes: the token is what
    sets the size. `1em`, `1.2em`, and `100%` pass. `.9em`, `85%`, and
    `smaller` fail.
    """
    bare = without_vars(value)
    if _LENGTH.search(bare) or _SMALLER.match(bare.strip()):
        return True
    return any(float(n) < (1 if unit == "em" else 100) for n, unit in _RELATIVE.findall(bare))


def _nearest(target: float, options: dict[str, float], unit: str = "") -> str:
    name = min(options, key=lambda k: abs(options[k] - target))
    return f"var({name}) ({options[name]:g}{unit})"


def suggestion(group: str, value: str, prop: str = "") -> str:
    """The token to read instead of a literal, for the guard's message."""
    step = re.fullmatch(r"--radius-([\w]+)", prop)
    if group == "border-radius" and step and step.group(1) in THEME["radius"]["steps"]:
        return f"var(--ox-radius-{step.group(1)})"
    if group == "box-shadow":
        return ("var(--ui-shadow) under a control, var(--ui-shadow-pop) under floating chrome, "
                "or no shadow on a surface at rest")
    if group == "line-height":
        found = re.search(r"\d*\.?\d+", without_vars(value))
        steps = {f"--ox-a-{st.name}-leading": float(st.leading) for st in T.APP.steps}
        return _nearest(float(found.group()), steps) if found else "an --ox-a-*-leading step"
    found = _LENGTH.search(without_vars(value))
    px = float(found.group(1)) * (16 if found and found.group(2) == "rem" else 1) if found else None
    if group == "border-radius":
        if px is None:
            return "an --ox-radius-* token"
        base = rem_px(THEME["radius"]["base"])
        steps = {f"--ox-radius-{s}": round(base * k, 2) for s, k in THEME["radius"]["steps"].items()}
        return _nearest(px, steps, "px")
    return size_suggestion(px)


def _step_sizes(prefix: str = "--ox-") -> dict[str, float]:
    """Each step of both scales and its size at the theme's base, by token name."""
    return {f"{prefix}{s.key}-{st.name}": st.px for s in T.SCALES for st in s.steps}


def size_suggestion(px: float | None, prefix: str = "--ox-") -> str:
    """The step a font size takes instead: the nearest step, the small ones included, or the step for its role."""
    if px is None:
        return f"var({prefix}a-body), the app base, or the step for its role"
    return _nearest(px, _step_sizes(prefix), "px") + ", or the step for its role"


def tailwind_suggestion(px: float | None) -> str:
    """The Tailwind size a class takes instead: the named size whose app step is nearest."""
    named = {f"text-{name}": T.APP.step(step).px for name, step in T.TAILWIND_SIZES}
    if px is None:
        return "text-base (the app base), or the named size for its role"
    name = min(named, key=lambda k: abs(named[k] - px))
    return f"{name} ({named[name]:g}px at the base), a text-a-* or text-m-* step, or the named size for its role"


def literals(css: str, keep: tuple[Keep, ...] = KEEP, path: str = KIT_CSS) -> tuple[list[Hit], list[Keep]]:
    """Every literal in `css` that should read a token, and every KEEP entry for `path` that excuses nothing."""
    hits: list[Hit] = []
    used: set[Keep] = set()
    mine = tuple(k for k in keep if k.path == path)
    for decl in declarations(css):
        value = re.sub(r"\s*!important$", "", decl.value)
        groups = [g for g in (group_of(decl),) if g] + [g for g in style_groups(decl) if g in ("color", "spacing")]
        for group in groups:
            literal = {"color": color_literal, "spacing": spacing_literal}.get(group, lambda v, g=group: is_literal(g, v))
            if not literal(value):
                continue
            entry = next((k for k in mine if k.group == group and k.value == value), None)
            if entry:
                used.add(entry)
                continue
            use = _style_suggestion(group, value, decl.prop, "--ox-") if group in ("color", "spacing") else suggestion(group, value, decl.prop)
            hits.append(Hit(decl.line, group, decl.prop, value, use, path))
    return hits, [k for k in mine if k not in used]


# --------------------------------------------------------------------------
# font sizes, in every file the kit sets text in
# --------------------------------------------------------------------------


def _font_sizes(decls: list[Decl], path: str, offset: int = 0, prefix: str = "--ox-") -> list[Hit]:
    """Each declaration in `decls` that sets a font size from a literal."""
    out = []
    for d in decls:
        if group_of(d) != "font-size":
            continue
        value = re.sub(r"\s*!important$", "", d.value)
        if small_or_fixed(value):
            found = _LENGTH.search(without_vars(value))
            px = float(found.group(1)) * (16 if found.group(2) == "rem" else 1) if found else None
            out.append(Hit(d.line + offset, "font-size", d.prop, value, size_suggestion(px, prefix), path))
    return out


def _line(text: str, index: int) -> int:
    return text.count("\n", 0, index) + 1


_STYLE_BLOCK = re.compile(r"<style[^>]*>(.*?)</style>", re.S | re.I)
_STYLE_ATTR = re.compile(r"""\sstyle=(["'])(.*?)\1""", re.S | re.I)


def css_font_sizes(css: str, path: str) -> list[Hit]:
    """Each font size a stylesheet writes as a literal. A page outside ui/src names the steps without `ox-`."""
    return _font_sizes(declarations(css), path, prefix="--ox-" if path.startswith("ui/") else "--")


def html_font_sizes(html: str, path: str) -> list[Hit]:
    """Each font size a page writes as a literal, in a `<style>` block or a `style` attribute."""
    out = []
    for m in _STYLE_BLOCK.finditer(html):
        out += _font_sizes(declarations(m.group(1)), path, _line(html, m.start(1)) - 1, "--")
    for m in _STYLE_ATTR.finditer(html):
        out += _font_sizes(declarations(m.group(2)), path, _line(html, m.start(2)) - 1, "--")
    return out


def strip_script_comments(code: str) -> str:
    """`code` with `/* */` blocks and `//` comments blanked, newlines kept. A `//` after a colon is a URL."""

    def blank(m: re.Match[str]) -> str:
        return m.group(1) or re.sub(r"[^\n]", " ", m.group(0))

    return re.sub(r"(\"(?:[^\"\\\n]|\\.)*\"|'(?:[^'\\\n]|\\.)*')|/\*.*?\*/|(?<![:\\])//[^\n]*", blank, code, flags=re.S)


_TW_SIZE = re.compile(r"(?<![\w-])text-\[([^\]\s]+)\]")
#: Tailwind's own fixed sizes: the ones above 3xl. `text-xs` to `text-3xl` are
#: not here, because `tokens/house-text-scale.css` points each at an app step.
_TW_NAMED = re.compile(r"(?<![\w-])text-([4-9]xl)(?![\w-])")
_FONT_SIZE_PROP = re.compile(r"\bfontSize\s*[:=]\s*\{?\s*(?:([\"'`])([^\"'`]*)\1|(-?\d*\.?\d+))")
_CSS_IN_STRING = re.compile(r"(?<![\w-])(font-size|font)\s*:\s*([^;\"'`}\n]+)")


def script_font_sizes(code: str, path: str) -> list[Hit]:
    """Each font size a script writes as a literal: a Tailwind arbitrary size, a `fontSize`, or CSS in a string."""
    text = strip_script_comments(code)
    out = []
    for m in _TW_SIZE.finditer(text):
        value = m.group(1)
        body = value[len("length:"):] if value.startswith("length:") else value
        if body.startswith("var(") or not small_or_fixed(body.replace("_", " ")):
            continue
        found = _LENGTH.search(body)
        px = float(found.group(1)) * (16 if found.group(2) == "rem" else 1) if found else None
        out.append(Hit(_line(text, m.start()), "font-size", "class", f"text-[{value}]", tailwind_suggestion(px), path))
    for m in _TW_NAMED.finditer(text):
        out.append(Hit(_line(text, m.start()), "font-size", "class", m.group(0),
                       "text-3xl or a smaller named size, a text-a-* or text-m-* step, or text-(length:--ox-<step>), "
                       "in place of Tailwind's own size", path))
    for m in _FONT_SIZE_PROP.finditer(text):
        value = m.group(2) if m.group(2) is not None else m.group(3)
        if m.group(3) is not None or small_or_fixed(value):
            px = float(value) if m.group(3) is not None else None
            if px is None:
                found = _LENGTH.search(without_vars(value))
                px = float(found.group(1)) * (16 if found.group(2) == "rem" else 1) if found else None
            out.append(Hit(_line(text, m.start()), "font-size", "fontSize", value, size_suggestion(px), path))
    for m in _CSS_IN_STRING.finditer(text):
        prop, value = m.group(1), m.group(2).strip()
        if prop == "font" and value in ("inherit", "initial", "unset"):
            continue
        if small_or_fixed(value):
            found = _LENGTH.search(without_vars(value))
            px = float(found.group(1)) * (16 if found.group(2) == "rem" else 1) if found else None
            out.append(Hit(_line(text, m.start()), "font-size", prop, value, size_suggestion(px, "--"), path))
    return out


def scanned_files(root: Path = ROOT) -> list[tuple[str, Path]]:
    """Each file the font-size scope covers, as (kind, path), tests and the kit's stylesheet left out."""
    out = []
    for kind, globs in FONT_SCOPE.items():
        for g in globs:
            for f in sorted(root.glob(g)):
                rel = f.relative_to(root).as_posix()
                if f.is_file() and not SKIP.search(rel) and rel != KIT_CSS:
                    out.append((kind, f))
    return out


def font_size_hits(root: Path = ROOT, keep: tuple[Keep, ...] = KEEP) -> tuple[list[Hit], set[Keep]]:
    """Every literal font size in the scope, and the KEEP entries that excused one."""
    hits: list[Hit] = []
    used: set[Keep] = set()
    read = {"css": css_font_sizes, "html": html_font_sizes, "script": script_font_sizes}
    for kind, f in scanned_files(root):
        rel = f.relative_to(root).as_posix()
        for h in read[kind](f.read_text(), rel):
            entry = next((k for k in keep if k.path == rel and k.group == h.group and k.value == h.value), None)
            if entry:
                used.add(entry)
            else:
                hits.append(h)
    return hits, used


# --------------------------------------------------------------------------
# colours, corners, shadows, and spacing, in every file the kit styles
# --------------------------------------------------------------------------

#: Mac, 2026-10-03: "make sure you take the time to check buttons, border
#: radius, colors etc - everything has to be semantic driven from tokens".
#: A component or a page reads a semantic token for every colour, corner,
#: shadow, and space. These groups join the font size in the same scope.
STYLE_GROUPS = ("color", "border-radius", "box-shadow", "spacing", "font-size")

#: Each group as a guard message names it.
GROUP_WORDS = {
    "color": "colour",
    "border-radius": "corner",
    "box-shadow": "shadow",
    "spacing": "space",
    "font-size": "font size",
}

#: Whole files a group does not read, each with its reason. Keep this short.
EXEMPT: dict[tuple[str, str], str] = {
    ("ui/src/components/brand-marks.generated.ts", "color"): (
        "generated art: the drawn marks and the gold they paint, copied from the kit's own drawings"
    ),
}

_COLOR_PROPS = re.compile(
    r"^(color|background(-color|-image)?|border(-(top|right|bottom|left|block|inline)(-(start|end))?)?(-color)?"
    r"|outline(-color)?|fill|stroke|stop-color|flood-color|lighting-color|caret-color|accent-color"
    r"|text-decoration(-color)?|text-emphasis-color|column-rule(-color)?|scrollbar-color|text-shadow"
    r"|-webkit-text-fill-color|-webkit-text-stroke(-color)?|box-shadow)$"
)
_SPACING_PROPS = re.compile(
    r"^((padding|margin|scroll-padding|scroll-margin)(-(top|right|bottom|left|block|inline)(-(start|end))?)?"
    r"|gap|row-gap|column-gap)$"
)

#: Every CSS named colour. `transparent` and `currentColor` are not here: they
#: name no hue, so they pass.
NAMED_COLORS = frozenset("""
aliceblue antiquewhite aqua aquamarine azure beige bisque black blanchedalmond blue blueviolet brown
burlywood cadetblue chartreuse chocolate coral cornflowerblue cornsilk crimson cyan darkblue darkcyan
darkgoldenrod darkgray darkgreen darkgrey darkkhaki darkmagenta darkolivegreen darkorange darkorchid
darkred darksalmon darkseagreen darkslateblue darkslategray darkslategrey darkturquoise darkviolet
deeppink deepskyblue dimgray dimgrey dodgerblue firebrick floralwhite forestgreen fuchsia gainsboro
ghostwhite gold goldenrod gray green greenyellow grey honeydew hotpink indianred indigo ivory khaki
lavender lavenderblush lawngreen lemonchiffon lightblue lightcoral lightcyan lightgoldenrodyellow
lightgray lightgreen lightgrey lightpink lightsalmon lightseagreen lightskyblue lightslategray
lightslategrey lightsteelblue lightyellow lime limegreen linen magenta maroon mediumaquamarine
mediumblue mediumorchid mediumpurple mediumseagreen mediumslateblue mediumspringgreen mediumturquoise
mediumvioletred midnightblue mintcream mistyrose moccasin navajowhite navy oldlace olive olivedrab
orange orangered orchid palegoldenrod palegreen paleturquoise palevioletred papayawhip peachpuff peru
pink plum powderblue purple rebeccapurple red rosybrown royalblue saddlebrown salmon sandybrown
seagreen seashell sienna silver skyblue slateblue slategray slategrey snow springgreen steelblue tan
teal thistle tomato turquoise violet wheat white whitesmoke yellow yellowgreen
""".split())

_HEX = re.compile(r"(?<![\w&])#[0-9a-fA-F]{3,8}(?![\w-])")
_COLOR_FN = re.compile(r"(?<![\w-])(rgba?|hsla?|hwb|lab|lch|oklab|oklch|color)\(", re.I)
_WORD = re.compile(r"(?<![\w-])[a-zA-Z]+(?![\w-])")
#: A house token read straight from the raw layer. Components and pages read
#: the semantic layer, so a raw colour token outside a custom property fails.
_RAW_OX_COLOR = re.compile(
    r"var\(\s*--ox-(?!font|weight|tracking|radius|shadow|space|wrap|shimmer|m-|a-)[\w-]+"
)
_SPACE_LENGTH = re.compile(r"(?<![\w.-])-?(\d*\.?\d+)(px|rem|em|pt|vh|vw|ch)\b")


def color_literal(value: str) -> bool:
    """Whether a value writes a colour of its own or reads a raw `--ox-*` colour token.

    A hex, an `rgb()`, `oklch()`, or other colour function, or a named colour
    fails. `transparent`, `currentColor`, and a colour inside a `var()`
    fallback pass, and so does `color-mix()` over tokens.
    """
    if _RAW_OX_COLOR.search(value):
        return True
    bare = re.sub(r"url\([^)]*\)", " ", without_vars(value))
    if _HEX.search(bare) or _COLOR_FN.search(bare):
        return True
    return any(w.lower() in NAMED_COLORS for w in _WORD.findall(bare))


def spacing_literal(value: str) -> bool:
    """Whether a padding, margin, or gap writes a length other than 0 of its own. `auto` and `%` pass."""
    return any(float(n) != 0 for n, _unit in _SPACE_LENGTH.findall(without_vars(value)))


def style_groups(decl: Decl) -> list[str]:
    """The groups a declaration's value answers to in the style scope.

    A custom property is the page's own token layer, so its colour and its
    spacing pass. Its corner, shadow, and size follow `group_of`.
    """
    groups = []
    base = group_of(decl)
    if base in ("border-radius", "box-shadow", "font-size"):
        groups.append(base)
    if not decl.prop.startswith("--"):
        if _COLOR_PROPS.match(decl.prop):
            groups.append("color")
        if _SPACING_PROPS.match(decl.prop):
            groups.append("spacing")
    return groups


def _style_suggestion(group: str, value: str, prop: str, prefix: str) -> str:
    if group == "color":
        return "a semantic colour token, such as var(--foreground), var(--muted-foreground), or var(--border)"
    if group == "spacing":
        return "the spacing unit: calc(var(--ox-space) * n), or the page's --space"
    if group == "font-size":
        found = _LENGTH.search(without_vars(value))
        px = float(found.group(1)) * (16 if found.group(2) == "rem" else 1) if found else None
        return size_suggestion(px, prefix)
    return suggestion(group, value, prop)


def _style_decls(decls: list[Decl], path: str, offset: int = 0, prefix: str = "--ox-") -> list[Hit]:
    out = []
    for d in decls:
        value = re.sub(r"\s*!important$", "", d.value)
        for group in style_groups(d):
            literal = {
                "color": color_literal,
                "spacing": spacing_literal,
                "font-size": small_or_fixed,
            }.get(group, lambda v, g=group: is_literal(g, v))(value)
            if literal:
                out.append(Hit(d.line + offset, group, d.prop, value, _style_suggestion(group, value, d.prop, prefix), path))
    return out


def css_style_hits(css: str, path: str) -> list[Hit]:
    """Each colour, corner, shadow, space, and font size a stylesheet writes as a literal."""
    return _style_decls(declarations(css), path, prefix="--ox-" if path.startswith("ui/") else "--")


def html_style_hits(html: str, path: str) -> list[Hit]:
    """The same, in a page's `<style>` blocks and `style` attributes."""
    out = []
    for m in _STYLE_BLOCK.finditer(html):
        out += _style_decls(declarations(m.group(1)), path, _line(html, m.start(1)) - 1, "--")
    for m in _STYLE_ATTR.finditer(html):
        out += _style_decls(declarations(m.group(2)), path, _line(html, m.start(2)) - 1, "--")
    return out


_TW_PALETTE = re.compile(
    r"(?<![\w-])(?:bg|text|border(?:-[trblxyse])?|ring|ring-offset|outline|fill|stroke|from|via|to|divide"
    r"|placeholder|caret|accent|decoration|shadow)-(?:(?:slate|gray|zinc|neutral|stone|red|orange|amber|yellow"
    r"|lime|green|emerald|teal|cyan|sky|blue|indigo|violet|purple|fuchsia|pink|rose)-\d{2,3}|white|black)"
    r"(?:/\d+)?(?![\w-])"
)
_TW_RAW_OX = re.compile(
    r"(?<![\w-])(?:bg|text|border(?:-[trblxyse])?|ring|outline|fill|stroke|from|via|to|decoration|divide|caret"
    r"|accent|placeholder)-ox-[\w-]+"
)
_TW_ARB = re.compile(r"(?<![\w-])(-?[a-z][a-z0-9-]*)-\[([^\]\s]+)\]")
_TW_ARB_PROP = re.compile(r"\[([a-z-]+):([^\]\s]+)\]")
_TW_COLOR_UTIL = {"bg", "text", "border", "border-t", "border-r", "border-b", "border-l", "border-x", "border-y",
                  "ring", "ring-offset", "outline", "fill", "stroke", "from", "via", "to", "decoration", "divide",
                  "caret", "accent", "placeholder", "shadow"}
_TW_RADIUS_UTIL = re.compile(r"^rounded(-(t|r|b|l|tl|tr|br|bl|s|e|ss|se|es|ee))?$")
_TW_SPACING_UTIL = re.compile(r"^-?(p|px|py|pt|pr|pb|pl|ps|pe|m|mx|my|mt|mr|mb|ml|ms|me|gap|gap-x|gap-y|space-x|space-y)$")
_STYLE_PROP = re.compile(
    r"\b(color|background|backgroundColor|backgroundImage|border(?:Top|Right|Bottom|Left)?(?:Color)?|outline(?:Color)?"
    r"|fill|stroke|stopColor|borderRadius|boxShadow|(?:padding|margin)(?:Top|Right|Bottom|Left|Block|Inline"
    r"|BlockStart|BlockEnd|InlineStart|InlineEnd)?|gap|rowGap|columnGap)\s*:\s*(?:([\"'`])([^\"'`]*)\2|(-?\d*\.?\d+)(?![\w.%]))"
)
_SVG_ATTR = re.compile(r"(?<![\w-])(fill|stroke|stop-color|stopColor|color)=([\"'])([^\"']+)\2")
_CSS_IN_STRING_ANY = re.compile(r"(?<![\w-])([a-z][a-z-]*)\s*:\s*([^;\"'`}\n]+)")


def _style_prop_group(name: str) -> str:
    if name in ("borderRadius",):
        return "border-radius"
    if name == "boxShadow":
        return "box-shadow"
    if re.match(r"^(padding|margin|gap|rowGap|columnGap)", name):
        return "spacing"
    return "color"


def script_style_hits(code: str, path: str) -> list[Hit]:
    """Each colour, corner, shadow, and space a script writes as a literal.

    It reads Tailwind classes (a palette colour such as `bg-zinc-800`, a raw
    house colour utility such as `bg-ox-gold`, and an arbitrary value such as
    `gap-[7px]`, `rounded-[10px]`, `shadow-[...]`, or `bg-[#fff]`), a style
    object's values, an SVG colour attribute, and CSS written in a string.
    Font sizes stay with `script_font_sizes`.
    """
    text = strip_script_comments(code)
    out: list[Hit] = []

    def hit(index: int, group: str, prop: str, value: str, use: str) -> None:
        out.append(Hit(_line(text, index), group, prop, value, use, path))

    for m in _TW_PALETTE.finditer(text):
        hit(m.start(), "color", "class", m.group(0), "a semantic colour utility, such as bg-card or text-muted-foreground")
    for m in _TW_RAW_OX.finditer(text):
        hit(m.start(), "color", "class", m.group(0), "the semantic utility for the role, such as bg-primary or text-gold-text")
    for m in _TW_ARB.finditer(text):
        util, value = m.group(1), m.group(2)
        body = value.replace("_", " ")
        if body.startswith("var(") or body.startswith("length:var(") or body.startswith("color:var("):
            if util.lstrip("-") in _TW_COLOR_UTIL and _RAW_OX_COLOR.search(body):
                hit(m.start(), "color", "class", m.group(0), "the semantic token for the role, not a raw --ox-* colour")
            continue
        name = util.lstrip("-")
        if name == "shadow":
            if _LENGTH.search(without_vars(body)) and body != "none":
                hit(m.start(), "box-shadow", "class", m.group(0), "shadow-pop under floating chrome, or a --shadow-* step")
            elif color_literal(body):
                hit(m.start(), "color", "class", m.group(0), "a semantic colour utility")
        elif name in _TW_COLOR_UTIL and color_literal(body):
            hit(m.start(), "color", "class", m.group(0), "a semantic colour utility")
        elif _TW_RADIUS_UTIL.match(name) and is_literal("border-radius", body):
            hit(m.start(), "border-radius", "class", m.group(0), "a rounded-* step, which reads --ox-radius-*")
        elif _TW_SPACING_UTIL.match(name) and spacing_literal(body):
            hit(m.start(), "spacing", "class", m.group(0), "a spacing step: Tailwind takes quarter steps, such as gap-1.75 for 7px")
    for m in _TW_ARB_PROP.finditer(text):
        prop, value = m.group(1), m.group(2).replace("_", " ")
        d = Decl("", prop, value, 0)
        for group in style_groups(d):
            if group != "font-size" and {"color": color_literal, "spacing": spacing_literal}.get(
                group, lambda v, g=group: is_literal(g, v)
            )(value):
                hit(m.start(), group, "class", m.group(0), _style_suggestion(group, value, prop, "--ox-"))
    for m in _STYLE_PROP.finditer(text):
        name = m.group(1)
        value = m.group(3) if m.group(3) is not None else m.group(4)
        group = _style_prop_group(name)
        if m.group(4) is not None:
            if group in ("spacing", "border-radius") and float(value) != 0:
                hit(m.start(), group, name, value, _style_suggestion(group, value, name, "--ox-"))
            continue
        check_fn = {"color": color_literal, "spacing": spacing_literal}.get(group, lambda v, g=group: is_literal(g, v))
        if check_fn(value):
            hit(m.start(), group, name, value, _style_suggestion(group, value, name, "--ox-"))
    for m in _SVG_ATTR.finditer(text):
        value = m.group(3)
        if value.startswith("{") or value in ("none", "currentColor", "transparent") or value.startswith("url("):
            continue
        if color_literal(value):
            hit(m.start(), "color", m.group(1), value, "currentColor, or a semantic colour token")
    for m in _CSS_IN_STRING_ANY.finditer(text):
        prop, value = m.group(1), m.group(2).strip()
        d = Decl("", prop, value, 0)
        for group in style_groups(d):
            if group == "font-size":
                continue
            literal = {"color": color_literal, "spacing": spacing_literal}.get(group, lambda v, g=group: is_literal(g, v))
            if literal(value):
                hit(m.start(), group, prop, value, _style_suggestion(group, value, prop, "--"))
    return out


def style_hits(root: Path = ROOT) -> list[Hit]:
    """Every colour, corner, shadow, and space literal in the style scope, exempt files left out.

    Font sizes are not here: `font_size_hits` reads them, with their own
    suggestions.
    """
    read = {"css": css_style_hits, "html": html_style_hits, "script": script_style_hits}
    hits = []
    for kind, f in scanned_files(root):
        rel = f.relative_to(root).as_posix()
        for h in read[kind](f.read_text(), rel):
            if h.group == "font-size" or (rel, h.group) in EXEMPT:
                continue
            hits.append(h)
    return hits


#: The scopes `--report` counts, by path prefix, most specific first.
REPORT_SCOPES = (
    ("ui/src/pages/app/", "the Work and Run app copies"),
    ("ui/src/pages/", "the example pages"),
    ("ui/src/components/", "the components"),
    ("ui/src/theme-editor/", "the theme editor"),
    ("ui/src/", "the rest of ui/src"),
    ("sdlc/public/", "the SDLC site"),
    ("pwa/", "the PWA prompt"),
    ("", "the kit's pages"),
)


def report(root: Path = ROOT) -> dict[str, dict[str, int]]:
    """Literal counts by scope and group, for the guard's `--report`."""
    counts: dict[str, dict[str, int]] = {}
    all_hits = style_hits(root) + font_size_hits(root)[0]
    kit_hits, _ = literals((root / KIT_CSS).read_text())
    for h in all_hits + kit_hits:
        scope = next(label for prefix, label in REPORT_SCOPES if h.path.startswith(prefix))
        if h.path == KIT_CSS:
            scope = "the kit's stylesheet"
        counts.setdefault(scope, {g: 0 for g in STYLE_GROUPS})
        counts[scope][h.group] = counts[scope].get(h.group, 0) + 1
    return counts


def sdlc_step_problems(root: Path = ROOT) -> list[str]:
    """Each base, step, and leading `sdlc/public/sdlc.css` leaves out or names with a value other than the theme's.

    Each step reads its scale's base, `calc(var(--a-base) * 0.857143)`, so
    the page needs both bases and every step for its sizes to resolve.
    """
    path = root / SDLC_CSS
    if not path.is_file():
        return []
    want = {f"--{name}": value for name, value in PC.type_sizes().items()}
    found, seen = [], set()
    for d in declarations(path.read_text()):
        if d.prop not in want:
            continue
        seen.add(d.prop)
        if d.value != want[d.prop]:
            found.append(
                f"{SDLC_CSS}:{d.line} names {d.prop}: {d.value}, and theme/theme.json makes it {want[d.prop]}. "
                "Copy the theme's value."
            )
    found += [
        f"{SDLC_CSS} does not name {name}. Add `{name}: {value};` beside the other type steps."
        for name, value in want.items()
        if name not in seen
    ]
    return found


# --------------------------------------------------------------------------
# semantic tokens: one definition per theme
# --------------------------------------------------------------------------

#: The theme blocks of the kit's stylesheet: light, dark by class, and dark by
#: the OS setting, which repeats the dark block for a page with no class.
LIGHT, DARK, DARK_OS = ":root", ".dark", ":root:not(.light):not(.dark)"
DARK_MEDIA = "@media (prefers-color-scheme: dark)"


@dataclass(frozen=True)
class Token:
    """One custom-property declaration: the blocks it sits in, its name and value, its order, and its line."""

    scope: tuple[str, ...]
    name: str
    value: str
    order: int
    line: int


def tokens(css: str) -> list[Token]:
    """Every custom property `css` declares, with the full stack of blocks around it (`@layer` left out)."""
    text = strip_comments(css)
    out: list[Token] = []
    stack: list[str] = []
    start = depth = 0
    for i, ch in enumerate(text):
        if ch == "(":
            depth += 1
        elif ch == ")":
            depth -= 1
        elif ch == "{" and depth == 0:
            stack.append(" ".join(text[start:i].split()))
            start = i + 1
        elif ch in ";}" and depth == 0:
            m = re.match(r"\s*(--[\w-]+)\s*:", text[start:i])
            if m:
                scope = tuple(b for b in stack if not b.startswith("@layer"))
                line = text.count("\n", 0, start + m.start(1)) + 1
                out.append(Token(scope, m.group(1), " ".join(text[start + m.end():i].split()), len(out), line))
            if ch == "}" and stack:
                stack.pop()
            start = i + 1
    return out


def semantic_problems(css: str, path: str = KIT_CSS) -> list[str]:
    """Each way the stylesheet gives a semantic token more than one definition in a theme.

    - A token declared twice in the same block: the later one wins, and the
      earlier one reads as live while it is dead.
    - A `:root` declaration after a `.dark` one of the same token: on a page
      whose `<html>` carries `.dark`, both match at the same specificity, so
      the later `:root` value wins and the dark value is dead there, though it
      still applies to a `.dark` element further down.
    - A dark-by-OS block that differs from `.dark`: a dark OS with no class
      draws a different theme from a page that sets `.dark`.
    """
    toks = tokens(css)
    found = []
    seen: dict[tuple[tuple[str, ...], str], Token] = {}
    for t in toks:
        first = seen.setdefault((t.scope, t.name), t)
        if first is not t:
            found.append(
                f"{path}:{t.line} declares {t.name} a second time in {' '.join(t.scope) or 'the top level'} "
                f"(first at line {first.line}). Keep one declaration per theme block."
            )
    last = {}
    for t in toks:
        if t.scope in ((LIGHT,), (DARK,)):
            last[(t.scope[0], t.name)] = t
    for (block, name), t in last.items():
        light = last.get((LIGHT, name))
        if block == DARK and light and light.order > t.order:
            found.append(
                f"{path}:{light.line} declares {name} on :root after .dark does (line {t.line}), so the "
                "dark value never reaches a page whose <html> is .dark. Declare the light value before the "
                ".dark block."
            )
    dark = {t.name: t.value for t in toks if t.scope == (DARK,)}
    dark_os = {t.name: t.value for t in toks if t.scope == (DARK_MEDIA, DARK_OS)}
    for name in sorted(set(dark) | set(dark_os)):
        if dark.get(name) != dark_os.get(name):
            found.append(
                f"{path} sets {name} to {dark.get(name)!r} in .dark and {dark_os.get(name)!r} in the "
                f"{DARK_MEDIA} block. The OS block repeats .dark, so make them equal."
            )
    return found


def check(path: Path = ROOT / KIT_CSS, root: Path = ROOT) -> list[str]:
    """The guard's problems, as `build/build.py --check` prints them."""
    hits, stale = literals(path.read_text())
    problems_semantic = semantic_problems(path.read_text())
    problems = [
        f"{KIT_CSS}:{h.line} writes {h.prop}: {h.value} as a literal. Read {h.use} instead, "
        "or add it to KEEP in build/css_literals.py with the reason it stays."
        for h in hits
    ]
    sizes, used = font_size_hits(root)
    problems += [
        f"{h.path}:{h.line} sets {h.prop} {h.value}, a font size the tokens do not set. "
        f"Use {h.use} instead."
        for h in sizes
    ]
    problems += [
        f"{h.path}:{h.line} sets {h.prop} {h.value}, a {GROUP_WORDS[h.group]} the tokens do not set. "
        f"Use {h.use} instead."
        for h in style_hits(root)
    ]
    problems += [
        f"build/css_literals.py keeps {k.group}: {k.value} for {k.path}, but that file no longer writes it. "
        "Remove the entry from KEEP."
        for k in stale + [k for k in KEEP if k.path != KIT_CSS and k not in used]
    ]
    return problems + problems_semantic + sdlc_step_problems(root)


def summary() -> list[str]:
    """What a clean pass of the guard holds, one line per scope."""
    kit = sum(1 for k in KEEP if k.path == KIT_CSS)
    other = len(KEEP) - kit
    def kept(n: int, what: str) -> str:
        return f", apart from {n} kept {what}{'s' if n != 1 else ''}" if n else ""

    return [
        f"{KIT_CSS} reads every colour, corner, shadow, space, font size, and heading line height from a token"
        + kept(kit, "literal"),
        f"{KIT_CSS} gives each semantic token one definition per theme",
        f"{len(scanned_files())} files in ui/src, sdlc/public, pwa/, and the kit's pages set every colour, corner, "
        f"shadow, space, and font size from a token" + kept(other, "size")
        + (f", apart from {len(EXEMPT)} exempt file{'s' if len(EXEMPT) != 1 else ''}" if EXEMPT else ""),
    ]


if __name__ == "__main__":
    if "--report" in sys.argv[1:]:
        counts = report()
        print(f"{'scope':32} " + " ".join(f"{g:>13}" for g in STYLE_GROUPS) + "  total")
        for scope, row in counts.items():
            print(f"{scope:32} " + " ".join(f"{row.get(g, 0):>13}" for g in STYLE_GROUPS) + f"  {sum(row.values()):>5}")
        print(f"{'total':32} " + " ".join(f"{sum(r.get(g, 0) for r in counts.values()):>13}" for g in STYLE_GROUPS)
              + f"  {sum(sum(r.values()) for r in counts.values()):>5}")
        sys.exit(0)
    found = check()
    for p in found:
        print("problem:", p)
    if not found:
        for line in summary():
            print(f"check: {line}")
    sys.exit(1 if found else 0)
