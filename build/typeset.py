"""The house type: three faces, each with one job, and two size scales.

**Geist** is the text face: every heading from h1 to h6, body, labels,
buttons, tables, navigation, everything read. **Space Grotesk** is the
wordmark face, and it sets three things only: the Oxagen wordmark, the stella
wordmark, and line 1 of the oxagen.sh hero. Mac narrowed it to those on
2026-09-29. Its wide geometric letters lose their shape below 20 px, so
nothing smaller is set in it. **Monaspace Neon** is the code face: code,
terminal output, logs, digests, paths, ids, and the numbers in a metric or a
table. Its texture healing (`calt`) and code ligatures (`liga`) are on
wherever it is used.

`display` names the heading role, not a face. `--font-display` and
`--ox-font-display` point at Geist, so a product can retune its headings in
one place. `--font-wordmark` and `--ox-font-wordmark` are the only tokens that
name Space Grotesk, and the marketing scale's `hero` step, `text-m-hero`, is
the one type step set in it.

Two scales, because a landing page and a dashboard do not breathe the same
way. The **marketing** scale is large and spaced for a page read once. The
**app** scale is dense for panels, tables, and logs read all day. A surface
picks one scale and uses it throughout. Both scales route the same way: the
heading role on h1 to h3, the text face on h4 and body, the code face on the
smallest step.

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
    key: str  # wordmark | sans | mono
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
    key="wordmark",
    family="Space Grotesk",
    job="the Oxagen and stella wordmarks, and line 1 of the oxagen.sh hero",
    stack='"Helvetica Neue", Arial, sans-serif',
    next_var="--font-space-grotesk",
    files=tuple((f"space-grotesk-latin-{w}.woff2", str(w)) for w in (400, 500, 600, 700)),
)

GEIST = Face(
    key="sans",
    family="Geist",
    job="every heading, body, labels, buttons, tables, navigation",
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

#: Roles that name a job rather than a face, and the face each one resolves
#: to. `display` is every heading, h1 to h6 in the element routing and h1 to
#: h3 in the scales, and it is Geist.
ROLES = {"display": "sans"}


def face_of(key: str) -> Face:
    """The face a step or a route draws in, through its role when it names one."""
    return FACE[ROLES.get(key, key)]

#: The weights the house uses, by job.
WEIGHTS = {
    "display": 700,  # the hero, h1 and h2 in the marketing scale, h1 in the app scale
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
    name: str  # hero | h1 | h2 | h3 | h4 | body | micro
    face: str  # a face key (wordmark | sans | mono) or a role (display)
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
        # Line 1 of the oxagen.sh hero, the one line of type set in the wordmark face.
        Step("hero", "wordmark", "4.5rem", 72, "1.05", 700, TRACKING["hero"]),
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

#: The wordmark face is set only at this size and up. Space Grotesk below this
#: is a defect.
WORDMARK_FLOOR_PX = 20


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
        "roles": {role: {"face": key, "family": FACE[key].family} for role, key in ROLES.items()},
        "weights": WEIGHTS,
        "tracking": TRACKING,
        "routing": [{"elements": e, "face": f, "family": face_of(f).family} for e, f in ROUTING],
        "wordmark_floor_px": WORDMARK_FLOOR_PX,
        "scales": {
            s.name: {
                "utility_prefix": f"text-{s.key}-",
                "use": s.use,
                "steps": [
                    {
                        "step": st.name,
                        "face": st.face,
                        "family": face_of(st.face).family,
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
            if face_of(st.face) is SPACE_GROTESK and st.px < WORDMARK_FLOOR_PX:
                problems.append(f"{s.name} {st.name}: Space Grotesk at {st.px}px, below the {WORDMARK_FLOOR_PX}px floor")
            if face_of(st.face) is SPACE_GROTESK and st.name != "hero":
                problems.append(f"{s.name} {st.name} is set in Space Grotesk, which sets only the wordmarks and the hero")
            if st.name == "hero" and st.face != "wordmark":
                problems.append(f"{s.name} hero is not in the wordmark face")
            if st.name in ("h1", "h2", "h3") and st.face != "display":
                problems.append(f"{s.name} {st.name} is not in the heading role")
            if st.name in ("h4", "body") and st.face != "sans":
                problems.append(f"{s.name} {st.name} is not in the text face")
            if st.name == "micro" and st.face != "mono":
                problems.append(f"{s.name} micro is not in the code face")
            if st.name == "h1" and not (1.05 <= float(st.leading) <= 1.25):
                problems.append(f"{s.name} h1 line-height {st.leading} is outside 1.05 to 1.25")
    if face_of("display") is not GEIST:
        problems.append("the heading role is not Geist")
    for elements, key in ROUTING:
        if face_of(key) is SPACE_GROTESK:
            problems.append(f"{elements} route to Space Grotesk, which sets only the wordmarks and the hero")
    return problems


if __name__ == "__main__":
    for s in SCALES:
        print(f"{s.name}: {s.use}")
        for st in s.steps:
            print(f"  {st.name:6} {face_of(st.face).family:15} {st.size:9} {st.px:3}px  lh {st.leading:5}  w{st.weight}  {st.tracking}")
    print("problems:", verify() or "none")
