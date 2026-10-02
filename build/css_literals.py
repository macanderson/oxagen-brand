"""The literal guard for the kit's own stylesheet, `ui/src/styles/globals.css`.

    python3 build/css_literals.py    # list each literal, exit 1 if any

A theme change reaches the kit's components through the `--ox-*` tokens that
`build/build.py` writes from `theme/theme.json`. A corner, a shadow, a font
size, or a heading's line height written as a literal in `globals.css` does
not follow that change, and a second declaration of the same value is how the
two drift apart. `build/build.py --check` runs this guard. It lists each
literal with its line and the token to read instead.

It is a regex pass over one file, with no CSS parser, on the model of the
literal guard in oxageninc/product (`tools/scripts/lib/brand-literals.mjs`).

What passes without an entry in KEEP:

- a value that reads a token (`var(--...)`) and writes no length of its own;
- a corner of 0, a circle (50%), or a pill (999px or 9999px);
- a ring, which is a shadow with no offset and no blur, such as a focus or
  hover ring, and an inset bar;
- a font size in em or percent, which follows its parent.

Every other literal the file keeps is in KEEP, with its reason. An entry that
matches nothing fails too, so the allowlist cannot outlive the literal it
excused.
"""

from __future__ import annotations

import re
import sys
from dataclasses import dataclass
from pathlib import Path

from theme import ROOT, THEME, rem_px

KIT_CSS = "ui/src/styles/globals.css"


@dataclass(frozen=True)
class Keep:
    """A literal the stylesheet keeps on purpose: its group, its value, and why."""

    group: str
    value: str
    why: str


#: The literals `globals.css` keeps, by group and value.
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
        return bool(_LENGTH.search(bare))
    if group == "line-height":
        return bool(re.search(r"\d", bare))
    return False


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
    if px is None:
        return "an --ox-* token"
    if group == "border-radius":
        base = rem_px(THEME["radius"]["base"])
        steps = {f"--ox-radius-{s}": round(base * k, 2) for s, k in THEME["radius"]["steps"].items()}
        return _nearest(px, steps, "px")
    sizes = {f"--ox-a-{s}": rem_px(app[s]["size"]) for s in app}
    return _nearest(px, sizes, "px")


def literals(css: str, keep: tuple[Keep, ...] = KEEP) -> tuple[list[Hit], list[Keep]]:
    """Every literal in `css` that should read a token, and every KEEP entry that excuses nothing."""
    hits: list[Hit] = []
    used: set[Keep] = set()
    for decl in declarations(css):
        group = group_of(decl)
        if group is None:
            continue
        value = re.sub(r"\s*!important$", "", decl.value)
        if not is_literal(group, value):
            continue
        entry = next((k for k in keep if k.group == group and k.value == value), None)
        if entry:
            used.add(entry)
            continue
        hits.append(Hit(decl.line, group, decl.prop, value, suggestion(group, value, decl.prop)))
    return hits, [k for k in keep if k not in used]


def check(path: Path = ROOT / KIT_CSS) -> list[str]:
    """The guard's problems, as `build/build.py --check` prints them."""
    hits, stale = literals(path.read_text())
    problems = [
        f"{KIT_CSS}:{h.line} writes {h.prop}: {h.value} as a literal. Read {h.use} instead, "
        "or add it to KEEP in build/css_literals.py with the reason it stays."
        for h in hits
    ]
    problems += [
        f"build/css_literals.py keeps {k.group}: {k.value}, but {KIT_CSS} no longer writes it. "
        "Remove the entry from KEEP."
        for k in stale
    ]
    return problems


if __name__ == "__main__":
    found = check()
    for p in found:
        print("problem:", p)
    if not found:
        print(f"check: {KIT_CSS} reads every corner, shadow, font size, and heading line height from a token, "
              f"apart from {len(KEEP)} kept literal{'s' if len(KEEP) != 1 else ''}")
    sys.exit(1 if found else 0)
