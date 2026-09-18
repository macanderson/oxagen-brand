"""The house type: three faces, each with one job, and two size scales.

**Space Grotesk** is the display face: the wordmarks and h1, h2, h3. Its wide
geometric letters are the brand at 28 px and up and lose their shape below
that, so nothing smaller is set in it. **Geist** is the text face: h4 to h6,
body, labels, buttons, tables, navigation, everything read rather than seen.
**Monaspace Neon** is the code face: code, terminal output, logs, digests,
paths, ids, and the numbers in a metric or a table. Its texture healing
(`calt`) and code ligatures (`liga`) are on wherever it is used.

Two scales, because a landing page and a dashboard do not breathe the same
way. The **marketing** scale is large and spaced for a page read once. The
**app** scale is dense for panels, tables, and logs read all day. A surface
picks one scale and uses it throughout. Both scales route the same way: the
display face on h1 to h3, the text face on h4 and body, the code face on
the smallest step.

Every value here is emitted into `tokens/` by `build/build.py`; nothing
downstream retypes a size.
"""

from __future__ import annotations

from dataclasses import dataclass

# --------------------------------------------------------------------------
# faces
# --------------------------------------------------------------------------


@dataclass(frozen=True)
class Face:
    key: str  # display | sans | mono
    family: str
    job: str
    stack: str  # the fallbacks after the family, as CSS
    next_var: str  # the CSS variable next/font/local sets on <html>
    files: tuple[tuple[str, str], ...]  # (file, weight or weight range)
    features: str = "normal"  # font-feature-settings

    @property
    def css_stack(self) -> str:
        return f'"{self.family}", {self.stack}'


SPACE_GROTESK = Face(
    key="display",
    family="Space Grotesk",
    job="wordmarks, h1, h2, h3",
    stack='"Helvetica Neue", Arial, sans-serif',
    next_var="--font-space-grotesk",
    files=tuple((f"space-grotesk-latin-{w}.woff2", str(w)) for w in (400, 500, 600, 700)),
)

GEIST = Face(
    key="sans",
    family="Geist",
    job="h4 to h6, body, labels, buttons, tables, navigation",
    stack='system-ui, -apple-system, "Segoe UI", sans-serif',
    next_var="--font-geist",
    files=(("geist-latin-wght.woff2", "100 900"),),
)

MONASPACE_NEON = Face(
    key="mono",
    family="Monaspace Neon",
    job="code, terminal output, logs, digests, paths, ids, and numbers in tables",
    stack='ui-monospace, "SF Mono", Menlo, Consolas, monospace',
    next_var="--font-monaspace-neon",
    files=(("monaspace-neon-latin-wght.woff2", "200 800"),),
    features='"calt", "liga"',
)

FACES: tuple[Face, ...] = (SPACE_GROTESK, GEIST, MONASPACE_NEON)
FACE = {f.key: f for f in FACES}

#: The weights the house uses, by job.
WEIGHTS = {
    "display": 700,  # h1, h2 in the marketing scale; h1 in the app scale
    "logo": 600,  # the wordmarks
    "heading": 600,  # h3, and h2 in the app scale
    "subheading": 500,  # h4 to h6 in the text face
    "ui": 500,  # buttons, labels, navigation
    "body": 400,
}

#: Headings track tighter as they grow. The wordmark is not tracked.
TRACKING = {"hero": "-0.03em", "display": "-0.02em", "heading": "-0.01em", "none": "0"}


# --------------------------------------------------------------------------
# scales
# --------------------------------------------------------------------------


@dataclass(frozen=True)
class Step:
    name: str  # h1 | h2 | h3 | h4 | body | micro
    face: str  # display | sans | mono
    size: str  # rem
    px: int  # the same size, for the reader
    leading: str  # unitless line-height
    weight: int
    tracking: str = "0"


@dataclass(frozen=True)
class Scale:
    key: str  # the utility prefix: text-<key>-<step>
    name: str
    use: str
    steps: tuple[Step, ...]


MARKETING = Scale(
    key="m",
    name="marketing",
    use="landing pages, posts, docs read once: large and spaced",
    steps=(
        Step("h1", "display", "4.5rem", 72, "1.05", 700, TRACKING["hero"]),
        Step("h2", "display", "2.5rem", 40, "1.2", 700, TRACKING["heading"]),
        Step("h3", "display", "1.75rem", 28, "1.3", 600),
        Step("h4", "sans", "1.25rem", 20, "1.4", 500),
        Step("body", "sans", "1.125rem", 18, "1.65", 400),
        Step("micro", "mono", "0.875rem", 14, "1.5", 400),
    ),
)

APP = Scale(
    key="a",
    name="app",
    use="dashboards, panels, tables, terminals, logs read all day: dense",
    steps=(
        Step("h1", "display", "1.875rem", 30, "1.15", 700, TRACKING["display"]),
        Step("h2", "display", "1.5rem", 24, "1.2", 600),
        Step("h3", "display", "1.25rem", 20, "1.25", 600),
        Step("h4", "sans", "1rem", 16, "1.4", 600),
        Step("body", "sans", "0.875rem", 14, "1.5", 400),
        Step("micro", "mono", "0.75rem", 12, "1.4", 400),
    ),
)

SCALES: tuple[Scale, ...] = (MARKETING, APP)

#: Which face each element takes, whatever the scale. This is the routing.
ROUTING: tuple[tuple[str, str], ...] = (
    ("h1, h2, h3", "display"),
    ("h4, h5, h6", "sans"),
    ("body, button, input, select, textarea, label, nav", "sans"),
    ("pre, code, kbd, samp, [data-mono]", "mono"),
)

#: Display type is set only at these sizes and up. Space Grotesk below this
#: is a defect.
DISPLAY_FLOOR_PX = 20


# --------------------------------------------------------------------------
# emitters
# --------------------------------------------------------------------------


def font_faces(prefix: str = "../fonts/") -> str:
    """The @font-face rules for the three faces, one per file."""
    out = []
    for face in FACES:
        for file, weight in face.files:
            out.append(
                f'@font-face{{font-family:"{face.family}";font-style:normal;font-weight:{weight};'
                f"font-display:swap;src:url({prefix}{file}) format(\"woff2\")}}"
            )
    return "\n".join(out)


def step_css(step: Step, *, family_var: str) -> str:
    """The declarations for one step. `family_var` is the CSS variable
    carrying the face, e.g. `--font-display` or `--ox-font-display`."""
    decl = [
        f"font-size: {step.size}",
        f"line-height: {step.leading}",
        f"font-family: var({family_var})",
        f"font-weight: {step.weight}",
    ]
    if step.tracking != "0":
        decl.append(f"letter-spacing: {step.tracking}")
    if step.face == "mono":
        decl.append(f"font-feature-settings: {FACE['mono'].features}")
    return "; ".join(decl) + ";"


def as_json() -> dict:
    return {
        "faces": {
            f.key: {
                "family": f.family,
                "job": f.job,
                "stack": f.css_stack,
                "next_var": f.next_var,
                "files": [{"file": file, "weight": w} for file, w in f.files],
                "features": f.features,
            }
            for f in FACES
        },
        "weights": WEIGHTS,
        "tracking": TRACKING,
        "routing": [{"elements": e, "face": f} for e, f in ROUTING],
        "display_floor_px": DISPLAY_FLOOR_PX,
        "scales": {
            s.name: {
                "utility_prefix": f"text-{s.key}-",
                "use": s.use,
                "steps": [
                    {
                        "step": st.name,
                        "face": st.face,
                        "size": st.size,
                        "px": st.px,
                        "line_height": float(st.leading),
                        "weight": st.weight,
                        "tracking": st.tracking,
                    }
                    for st in s.steps
                ],
            }
            for s in SCALES
        },
    }


# --------------------------------------------------------------------------
# checks
# --------------------------------------------------------------------------


def verify() -> list[str]:
    """Every fact the type claims, checked. Returns the problems found."""
    problems = []
    for s in SCALES:
        sizes = [st.px for st in s.steps]
        if sizes != sorted(sizes, reverse=True):
            problems.append(f"{s.name} scale does not descend: {sizes}")
        for st in s.steps:
            if round(float(st.size.rstrip("rem")) * 16) != st.px:
                problems.append(f"{s.name} {st.name}: {st.size} is not {st.px}px")
            if st.face == "display" and st.px < DISPLAY_FLOOR_PX:
                problems.append(f"{s.name} {st.name}: Space Grotesk at {st.px}px, below the {DISPLAY_FLOOR_PX}px floor")
            if st.name in ("h1", "h2", "h3") and st.face != "display":
                problems.append(f"{s.name} {st.name} is not in the display face")
            if st.name in ("h4", "body") and st.face != "sans":
                problems.append(f"{s.name} {st.name} is not in the text face")
            if st.name == "micro" and st.face != "mono":
                problems.append(f"{s.name} micro is not in the code face")
            if st.name == "h1" and not (1.05 <= float(st.leading) <= 1.25):
                problems.append(f"{s.name} h1 line-height {st.leading} is outside 1.05 to 1.25")
    return problems


if __name__ == "__main__":
    for s in SCALES:
        print(f"{s.name}: {s.use}")
        for st in s.steps:
            print(f"  {st.name:6} {st.face:8} {st.size:9} {st.px:3}px  lh {st.leading:5}  w{st.weight}  {st.tracking}")
    print("problems:", verify() or "none")
