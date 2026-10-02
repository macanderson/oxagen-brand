"""The literal guard: the kit's stylesheet, and every font size the kit sets.

    python3 build/css_literals.py    # list each literal, exit 1 if any

A theme change reaches the kit's components through the `--ox-*` tokens that
`build/build.py` writes from `theme/theme.json`. A corner, a shadow, a font
size, or a heading's line height written as a literal does not follow that
change, and a second declaration of the same value is how the two drift
apart. `build/build.py --check` runs this guard. It lists each literal with
its line and the token to read instead.

It reads two scopes:

- **The kit's stylesheet**, `ui/src/styles/globals.css`: every corner,
  shadow, font size, and heading line height.
- **Every font size the kit sets** (Mac, 2026-10-02: "we can't hard code font
  sizes in classes, we need to let the tokens do their job"): the CSS, the
  stories, and the components in `ui/src`, the SDLC page in `sdlc/public`,
  the PWA install prompt, and the kit's own pages (`playbook.html`,
  `message-bank.html`, `always-on.html`, `brand-guide.html`). In a page it
  reads each `<style>` block and `style` attribute. In a script it reads
  Tailwind's arbitrary sizes (`text-[13px]`), a `fontSize` value, and CSS
  written in a string. Tests are not read, because they name classes to
  assert them.

It is a regex pass with no CSS parser, on the model of the literal guard in
oxageninc/product (`tools/scripts/lib/brand-literals.mjs`).

What passes without an entry in KEEP:

- a value that reads a token (`var(--...)`) and writes no length of its own,
  a fallback inside the `var()` included;
- a Tailwind size that reads a token, `text-(length:--ox-a-h2)` or
  `text-[length:var(--ox-a-h2)]`, and Tailwind's named sizes, since
  `tokens/house-tailwind.css` points `text-xs` and `text-sm` at a step;
- a corner of 0, a circle (50%), or a pill (999px or 9999px);
- a ring, which is a shadow with no offset and no blur, such as a focus or
  hover ring, and an inset bar;
- a font size of 1em or more, or 100% or more, which never sets text below
  its parent.

A font size under 1em or under 100% fails, because it sets text below a
step: `.9em` of a 14px body is 12.6px.

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

from theme import ROOT, THEME, TYPE_FLOOR_PX, rem_px

KIT_CSS = "ui/src/styles/globals.css"

#: Where the guard reads font sizes, by kind, as globs from the repository root.
FONT_SCOPE: dict[str, tuple[str, ...]] = {
    "css": ("ui/src/**/*.css", "sdlc/public/*.css"),
    "html": ("playbook.html", "message-bank.html", "always-on.html", "brand-guide.html", "sdlc/public/*.html"),
    "script": ("ui/src/**/*.ts", "ui/src/**/*.tsx", "pwa/*.js", "sdlc/public/*.js"),
}

#: A file the guard does not read for font sizes: a test names a class to assert it.
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


#: The literals the guard excuses, by file, group, and value.
KEEP: tuple[Keep, ...] = (
    Keep("font-size", "16px", "Safari's floor for a text field on a phone, below which iOS zooms the page on focus"),
)


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
    app = THEME["type"]["scales"]["app"]
    step = re.fullmatch(r"--radius-([\w]+)", prop)
    if group == "border-radius" and step and step.group(1) in THEME["radius"]["steps"]:
        return f"var(--ox-radius-{step.group(1)})"
    if group == "box-shadow":
        return ("var(--ui-shadow) under a control, var(--ui-shadow-pop) under floating chrome, "
                "or no shadow on a surface at rest")
    if group == "line-height":
        found = re.search(r"\d*\.?\d+", without_vars(value))
        steps = {f"--ox-a-{s}-leading": float(app[s]["leading"]) for s in app}
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


def size_suggestion(px: float | None, prefix: str = "--ox-") -> str:
    """The step a font size takes instead: the body step under the floor, else the nearest step."""
    app, marketing = THEME["type"]["scales"]["app"], THEME["type"]["scales"]["marketing"]
    if px is None or px < TYPE_FLOOR_PX:
        return f"var({prefix}a-body), the {rem_px(app['body']['size']):g}px floor, or the step for its role"
    sizes = {f"{prefix}a-{s}": rem_px(app[s]["size"]) for s in app}
    sizes.update({f"{prefix}m-{s}": rem_px(marketing[s]["size"]) for s in marketing})
    return _nearest(px, sizes, "px")


def literals(css: str, keep: tuple[Keep, ...] = KEEP, path: str = KIT_CSS) -> tuple[list[Hit], list[Keep]]:
    """Every literal in `css` that should read a token, and every KEEP entry for `path` that excuses nothing."""
    hits: list[Hit] = []
    used: set[Keep] = set()
    mine = tuple(k for k in keep if k.path == path)
    for decl in declarations(css):
        group = group_of(decl)
        if group is None:
            continue
        value = re.sub(r"\s*!important$", "", decl.value)
        if not is_literal(group, value):
            continue
        entry = next((k for k in mine if k.group == group and k.value == value), None)
        if entry:
            used.add(entry)
            continue
        hits.append(Hit(decl.line, group, decl.prop, value, suggestion(group, value, decl.prop), path))
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
        use = (
            f"text-sm ({TYPE_FLOOR_PX}px, the app body step)"
            if px is None or px < TYPE_FLOOR_PX
            else f"a text-a-* or text-m-* step, or text-(length:{size_suggestion(px).split(' ')[0][4:-1]})"
        )
        out.append(Hit(_line(text, m.start()), "font-size", "class", f"text-[{value}]", use, path))
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


def sdlc_step_problems(root: Path = ROOT) -> list[str]:
    """Each type step `sdlc/public/sdlc.css` names with a value other than the theme's."""
    path = root / SDLC_CSS
    if not path.is_file():
        return []
    want = {}
    for scale, key in (("marketing", "m"), ("app", "a")):
        for step, spec in THEME["type"]["scales"][scale].items():
            want[f"--{key}-{step}"] = spec["size"]
            want[f"--{key}-{step}-leading"] = f"{spec['leading']:g}"
    found = []
    for d in declarations(path.read_text()):
        if d.prop in want and d.value != want[d.prop]:
            found.append(
                f"{SDLC_CSS}:{d.line} names {d.prop}: {d.value}, and theme/theme.json makes it {want[d.prop]}. "
                "Copy the theme's value."
            )
    return found


def check(path: Path = ROOT / KIT_CSS, root: Path = ROOT) -> list[str]:
    """The guard's problems, as `build/build.py --check` prints them."""
    hits, stale = literals(path.read_text())
    problems = [
        f"{KIT_CSS}:{h.line} writes {h.prop}: {h.value} as a literal. Read {h.use} instead, "
        "or add it to KEEP in build/css_literals.py with the reason it stays."
        for h in hits
    ]
    sizes, used = font_size_hits(root)
    problems += [
        f"{h.path}:{h.line} sets {h.prop} {h.value}, a font size the tokens do not set. "
        f"Use {h.use} instead. No text is set below {TYPE_FLOOR_PX}px."
        for h in sizes
    ]
    problems += [
        f"build/css_literals.py keeps {k.group}: {k.value} for {k.path}, but that file no longer writes it. "
        "Remove the entry from KEEP."
        for k in stale + [k for k in KEEP if k.path != KIT_CSS and k not in used]
    ]
    return problems + sdlc_step_problems(root)


if __name__ == "__main__":
    found = check()
    for p in found:
        print("problem:", p)
    if not found:
        print(f"check: {KIT_CSS} reads every corner, shadow, font size, and heading line height from a token, "
              f"apart from {len(KEEP)} kept literal{'s' if len(KEEP) != 1 else ''}")
        print(f"check: {len(scanned_files())} files in ui/src, sdlc/public, pwa/, and the kit's pages set every font size from a token")
    sys.exit(1 if found else 0)
