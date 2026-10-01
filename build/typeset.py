"""The house type: three faces, five roles, and two size scales.

**Geist** sets every heading and every line of text: h1 to h6, body, labels,
buttons, tables, and navigation, in the app and on the website alike.
**Monaspace Neon** sets code, terminal output, logs, digests, paths, ids, and
the numbers in a metric or a table. Its texture healing (`calt`) and code
ligatures (`liga`) are on wherever it is used. **Space Grotesk** sets the
oxagen and stella wordmarks, Stella's asterisk icon, and line 1 of a
marketing hero, and nothing else. Mac set that rule on 2026-09-29. Its wide
geometric letters lose their shape below 20 px, so nothing smaller is set in
it.

A product's CSS names a role, `--font-<role>`, and each role resolves to one
face:

- `sans` is Geist, for everything read.
- `display` is Geist too. It is the heading token, so every heading can be
  retuned in one place. The name predates the 2026-09-29 rule and stays so
  that no consumer breaks.
- `mono` is Monaspace Neon.
- `wordmark` is Space Grotesk, for a wordmark set as text rather than drawn.
- `hero` is Geist, except inside a heading set on a step that admits a hero.
  Only the marketing h1 admits one. It points `--font-hero` at the wordmark
  face for its own contents, so the `hero-line-1` class reaches Space Grotesk
  inside a marketing h1 and resolves to Geist everywhere else. An app heading
  cannot reach Space Grotesk by accident.

Two scales, because a landing page and a dashboard do not breathe the same
way. The **marketing** scale is large and spaced for a page read once. The
**app** scale is dense for panels, tables, and logs read all day. A surface
picks one scale and uses it throughout. Both scales route the same way:
headings to `display`, body to `sans`, and the smallest step to `mono`.

Every value here is emitted into `tokens/` by `build/build.py`. Nothing
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


# The key stays `display` so that `--ox-font-display` and `--font-space-grotesk`
# keep their names in every repository that vendors the tokens.
SPACE_GROTESK = Face(
    key="display",
    family="Space Grotesk",
    job="the wordmarks, Stella's icon, and line 1 of a marketing hero",
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


# --------------------------------------------------------------------------
# roles
# --------------------------------------------------------------------------


@dataclass(frozen=True)
class Role:
    key: str  # the CSS variable a product reads: --font-<key>
    face: str  # the face key the role resolves to
    job: str


ROLES: tuple[Role, ...] = (
    Role("sans", "sans", "body, labels, buttons, tables, navigation"),
    Role("display", "sans", "every heading, h1 to h6"),
    Role("mono", "mono", "code, logs, ids, and numbers in tables"),
    Role("wordmark", "display", "a wordmark set as text rather than drawn"),
    Role("hero", "sans", "line 1 of a hero, in Space Grotesk only inside a step that admits a hero"),
)
ROLE = {r.key: r for r in ROLES}

#: The class that marks line 1 of a hero. It reads `--font-hero`, which is
#: the heading face unless an enclosing step admits a hero.
HERO_CLASS = "hero-line-1"

#: The role a hero line takes inside a step that admits one, and everywhere else.
HERO_ROLE_INSIDE = "wordmark"
HERO_ROLE_OUTSIDE = "display"


def family(role: str) -> str:
    """The family a role resolves to outside a hero."""
    return FACE[ROLE[role].face].family


#: The weights the house uses, by job.
WEIGHTS = {
    "display": 700,  # h1, h2 in the marketing scale; h1 in the app scale
    "logo": 600,  # the wordmarks
    "heading": 600,  # h3, and h2 in the app scale
    "subheading": 500,  # h4 to h6
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
    role: str  # display | sans | mono
    size: str  # rem
    px: int  # the same size, for the reader
    leading: str  # unitless line-height
    weight: int
    tracking: str = "0"
    hero: bool = False  # line 1 of a heading on this step may take Space Grotesk


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
        Step("h1", "display", "4.5rem", 72, "1.05", 700, TRACKING["hero"], hero=True),
        Step("h2", "display", "2.5rem", 40, "1.2", 700, TRACKING["heading"]),
        Step("h3", "display", "1.75rem", 28, "1.3", 600),
        Step("h4", "display", "1.25rem", 20, "1.4", 500),
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
        Step("h4", "display", "1rem", 16, "1.4", 600),
        Step("body", "sans", "0.875rem", 14, "1.5", 400),
        Step("micro", "mono", "0.75rem", 12, "1.4", 400),
    ),
)

SCALES: tuple[Scale, ...] = (MARKETING, APP)


@dataclass(frozen=True)
class Route:
    elements: str
    role: str
    extra: tuple[str, ...] = ()  # declarations beyond the face


#: Which role each element takes, whatever the scale. This is the routing.
ROUTING: tuple[Route, ...] = (
    Route("h1, h2, h3", "display", ("letter-spacing: var(--tracking-display)",)),
    Route("h4, h5, h6", "display", (f"font-weight: {WEIGHTS['subheading']}",)),
    Route("body, button, input, select, textarea, label, nav", "sans"),
    Route("pre, code, kbd, samp, [data-mono]", "mono", (f"font-feature-settings: {MONASPACE_NEON.features}",)),
)

#: Space Grotesk is set only at these sizes and up. Below this it is a defect.
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


def step_css(step: Step) -> str:
    """The declarations for one step, reading the `--font-<role>` variables."""
    decl = [
        f"font-size: {step.size}",
        f"line-height: {step.leading}",
        f"font-family: var(--font-{step.role})",
        f"font-weight: {step.weight}",
    ]
    if step.tracking != "0":
        decl.append(f"letter-spacing: {step.tracking}")
    if step.role == "mono":
        decl.append(f"font-feature-settings: {MONASPACE_NEON.features}")
    if step.hero:
        decl.append(f"--font-hero: var(--font-{HERO_ROLE_INSIDE})")
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
        "roles": {
            r.key: {"css_var": f"--font-{r.key}", "face": r.face, "family": FACE[r.face].family, "job": r.job}
            for r in ROLES
        },
        "hero": {
            "class": HERO_CLASS,
            "family_inside": family(HERO_ROLE_INSIDE),
            "family_outside": family("hero"),
            "admitted_by": [f"text-{s.key}-{st.name}" for s in SCALES for st in s.steps if st.hero],
        },
        "weights": WEIGHTS,
        "tracking": TRACKING,
        "routing": [{"elements": r.elements, "role": r.role, "family": family(r.role)} for r in ROUTING],
        "display_floor_px": DISPLAY_FLOOR_PX,
        "scales": {
            s.name: {
                "utility_prefix": f"text-{s.key}-",
                "use": s.use,
                "steps": [
                    {
                        "step": st.name,
                        "role": st.role,
                        "family": family(st.role),
                        "size": st.size,
                        "px": st.px,
                        "line_height": float(st.leading),
                        "weight": st.weight,
                        "tracking": st.tracking,
                        "hero": st.hero,
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
    if family("display") != GEIST.family or family("sans") != GEIST.family:
        problems.append("headings and text are not both Geist")
    if family("hero") != GEIST.family or family(HERO_ROLE_OUTSIDE) != GEIST.family:
        problems.append("the hero role is not Geist outside a hero step")
    if family("wordmark") != SPACE_GROTESK.family or family(HERO_ROLE_INSIDE) != SPACE_GROTESK.family:
        problems.append("the wordmark role is not Space Grotesk")
    for r in ROUTING:
        if r.role not in ("display", "sans", "mono"):
            problems.append(f"{r.elements} route to the {r.role} role, which only a wordmark or a hero line takes")
    for s in SCALES:
        sizes = [st.px for st in s.steps]
        if sizes != sorted(sizes, reverse=True):
            problems.append(f"{s.name} scale does not descend: {sizes}")
        for st in s.steps:
            if round(float(st.size.rstrip("rem")) * 16) != st.px:
                problems.append(f"{s.name} {st.name}: {st.size} is not {st.px}px")
            if st.name in ("h1", "h2", "h3", "h4") and st.role != "display":
                problems.append(f"{s.name} {st.name} does not read the heading role")
            if st.name == "body" and st.role != "sans":
                problems.append(f"{s.name} body is not in the text face")
            if st.name == "micro" and st.role != "mono":
                problems.append(f"{s.name} micro is not in the code face")
            if st.hero and (s is not MARKETING or st.name != "h1"):
                problems.append(f"{s.name} {st.name} admits a hero, and only the marketing h1 may")
            if st.hero and st.px < DISPLAY_FLOOR_PX:
                problems.append(f"{s.name} {st.name}: a Space Grotesk hero at {st.px}px, below the {DISPLAY_FLOOR_PX}px floor")
            if st.name == "h1" and not (1.05 <= float(st.leading) <= 1.25):
                problems.append(f"{s.name} h1 line-height {st.leading} is outside 1.05 to 1.25")
    if not any(st.hero for st in MARKETING.steps):
        problems.append("no marketing step admits a hero, so line 1 of a hero cannot take Space Grotesk")
    return problems


if __name__ == "__main__":
    for s in SCALES:
        print(f"{s.name}: {s.use}")
        for st in s.steps:
            hero = "  hero" if st.hero else ""
            print(f"  {st.name:6} {family(st.role):15} {st.size:9} {st.px:3}px  lh {st.leading:5}  w{st.weight}  {st.tracking}{hero}")
    print("problems:", verify() or "none")
