"""The house type: three faces, five roles, and two size scales.

**Aeonik** sets every heading and every line of text in the app and on the
docs site: h1 to h6, body, labels, buttons, tables, and navigation. Its
italic ships beside the upright as the same family. **Monaspace Neon** sets
code, terminal output, logs, digests, paths, ids, and the numbers in a metric
or a table. Its texture healing (`calt`) and code ligatures (`liga`) are on
wherever it is used. **Space Grotesk** sets the oxagen and stella wordmarks,
Stella's asterisk icon, and line 1 of a marketing hero. On the website
(oxagen.sh) it also sets every h1, h2, and h3. Mac set that rule on
2026-10-02, when Aeonik became the house sans. The website applies it in its own
stylesheet: the marketing scale here still reads the heading role, and only
the marketing h1 points `--font-hero` at Space Grotesk. Its wide geometric
letters lose their shape below 20 px, so nothing smaller is set in it.

**Aeonik Mono** and **Aeonik Fono** ship too, from `extra_faces` in the
theme. Each gets @font-face rules and a next/font loader, so a page can name
its family. No role reads them yet.

A product's CSS names a role, `--font-<role>`, and each role resolves to one
face:

- `sans` is Aeonik, for everything read.
- `display` is Aeonik too. It is the heading token, so every heading can be
  retuned in one place. The name predates the 2026-09-29 rule and stays so
  that no consumer breaks.
- `mono` is Monaspace Neon.
- `wordmark` is Space Grotesk, for a wordmark set as text rather than drawn.
- `hero` is Aeonik, except inside a heading set on a step that admits a hero.
  Only the marketing h1 admits one. It points `--font-hero` at the wordmark
  face for its own contents, so the `hero-line-1` class reaches Space Grotesk
  inside a marketing h1 and resolves to Aeonik everywhere else. An app heading
  cannot reach Space Grotesk by accident.

Two scales, because a landing page and a dashboard do not breathe the same
way. The **marketing** scale is large and spaced for a landing page or a post read
once. The **app** scale is dense for docs, panels, tables, and logs. A surface
picks one scale and uses it throughout. Both scales route the same way:
headings to `display`, body to `sans`, and the smallest step to `mono`.

Every value here comes from `theme/theme.json`, through `build/theme.py`, and
`build/build.py` emits it into `tokens/`. Nothing downstream retypes a size.
The names above describe the theme the kit ships. A theme that names other
families changes what each role resolves to, and `verify()` checks the rules
that hold for any family.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from theme import ROOT, THEME, rem_px

FONTS = ROOT / "fonts"

_FACES = THEME["faces"]
_TYPE = THEME["type"]

# --------------------------------------------------------------------------
# faces
# --------------------------------------------------------------------------


@dataclass(frozen=True)
class Face:
    key: str  # display | sans | mono | heading, or extra-<family> for a face no role takes
    family: str
    job: str
    stack: str  # the fallbacks after the family, as CSS
    next_var: str  # the CSS variable next/font/local sets on <html>
    files: tuple[tuple[str, str, str], ...]  # (file, weight or weight range, normal or italic)
    features: str = "normal"  # font-feature-settings

    @property
    def css_stack(self) -> str:
        return f'"{self.family}", {self.stack}'


def _family_stack(names: list[str]) -> str:
    """A fallback list as CSS: a name with a space is quoted, a single word is not."""
    return ", ".join(f'"{n}"' if " " in n else n for n in names)


def _features(tags: list[str]) -> str:
    return ", ".join(f'"{t}"' for t in tags) if tags else "normal"


def _next_var(family: str) -> str:
    """The CSS variable next/font/local sets for a family: `--font-space-grotesk`."""
    return "--font-" + re.sub(r"[^a-z0-9]+", "-", family.lower()).strip("-")


def _from_spec(key: str, spec: dict, job: str) -> Face:
    return Face(
        key=key,
        family=spec["family"],
        job=job,
        stack=_family_stack(spec["fallback"]),
        next_var=_next_var(spec["family"]),
        files=tuple((f["file"], f["weight"], f.get("style", "normal")) for f in spec["files"]),
        features=_features(spec["features"]),
    )


def _face(key: str, role: str, job: str) -> Face:
    return _from_spec(key, _FACES[role], job)


#: The face of each role in the theme. The face key of the wordmark stays
#: `display` so that `--ox-font-display` and `--font-space-grotesk` keep their
#: names in every repository that vendors the tokens. The module-level names
#: below name the role's face whatever family the theme holds, because other
#: modules import them. SPACE_GROTESK and MONASPACE_NEON keep the names of the
#: faces the kit ships.
SPACE_GROTESK = _face("display", "wordmark", "the wordmarks, Stella's icon, and line 1 of a marketing hero")
TEXT_FACE = _face("sans", "sans", "every heading, body, labels, buttons, tables, navigation")
MONASPACE_NEON = _face("mono", "mono", "code, terminal output, logs, digests, paths, ids, and numbers in tables")
WORDMARK_FACE, CODE_FACE = SPACE_GROTESK, MONASPACE_NEON

#: Headings share a face with another role when the theme gives the display
#: role that role's family, as it gives it the text face today. A theme that
#: names a family no other role uses adds a fourth face.
_HEADING = _face("heading", "display", "every heading, h1 to h6")
HEADING_FACE: Face = next(
    (f for f in (TEXT_FACE, SPACE_GROTESK, MONASPACE_NEON) if f.family == _HEADING.family), _HEADING
)

FACES: tuple[Face, ...] = tuple(
    dict.fromkeys((SPACE_GROTESK, TEXT_FACE, HEADING_FACE, MONASPACE_NEON))
)
FACE = {f.key: f for f in FACES}

#: Faces the kit ships and loads that no role takes, from `extra_faces` in the
#: theme: Aeonik Mono and Aeonik Fono today. They get @font-face rules and a
#: next/font loader, so a page can name the family, and no `--font-*` or
#: `--ox-font-*` token. Their keys stay out of FACE, so no role can resolve to one.
EXTRA_FACES: tuple[Face, ...] = tuple(
    _from_spec(
        "extra-" + re.sub(r"[^a-z0-9]+", "-", spec["family"].lower()).strip("-"),
        spec,
        "loads for a page that names it. No role reads it yet",
    )
    for spec in THEME.get("extra_faces", [])
)

#: Every face the kit loads: the role faces, then the extra faces.
LOADED_FACES: tuple[Face, ...] = FACES + EXTRA_FACES


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
    Role("display", HEADING_FACE.key, "every heading, h1 to h6"),
    Role("mono", "mono", "code, logs, ids, and numbers in tables"),
    Role("wordmark", "display", "a wordmark set as text rather than drawn"),
    Role("hero", HEADING_FACE.key, f"line 1 of a hero, in {WORDMARK_FACE.family} only inside a step that admits a hero"),
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


#: The weights the house uses, by job. The wordmarks take the weight their
#: outlines are set at.
WEIGHTS = {
    "display": _TYPE["weights"]["display"],  # h1, h2 in the marketing scale; h1 in the app scale
    "logo": _FACES["wordmark"]["outline"]["weight"],  # the wordmarks
    "heading": _TYPE["weights"]["heading"],  # h3, and h2 in the app scale
    "subheading": _TYPE["weights"]["subheading"],  # h4 to h6
    "ui": _TYPE["weights"]["ui"],  # buttons, labels, navigation
    "body": _TYPE["weights"]["body"],
}

#: Headings track tighter as they grow. The wordmark is not tracked.
TRACKING = dict(_TYPE["tracking"])


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


#: The role each step reads. Headings read the heading role, body the text
#: face, and the smallest step the code face, on both scales.
STEP_ROLES = {"h1": "display", "h2": "display", "h3": "display", "h4": "display", "body": "sans", "micro": "mono"}


def _scale(key: str, name: str, use: str) -> Scale:
    steps = []
    for step, role in STEP_ROLES.items():
        spec = _TYPE["scales"][name][step]
        steps.append(
            Step(
                step,
                role,
                spec["size"],
                round(rem_px(spec["size"])),
                f"{spec['leading']:g}",
                spec["weight"],
                TRACKING[spec["tracking"]],
                # Only line 1 of a marketing hero may take the wordmark face.
                hero=(name == "marketing" and step == "h1"),
            )
        )
    return Scale(key=key, name=name, use=use, steps=tuple(steps))


MARKETING = _scale("m", "marketing", "landing pages and posts read once: large and spaced")
APP = _scale("a", "app", "dashboards, docs, panels, tables, terminals, logs: dense")

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


#: The `format()` hint each font file type takes in an @font-face rule.
FONT_FORMATS = {".woff2": "woff2", ".woff": "woff", ".ttf": "truetype", ".otf": "opentype"}


def font_faces(prefix: str = "../fonts/") -> str:
    """The @font-face rules for every face the kit loads, one per file.

    An italic file is the same family with `font-style: italic`, so a browser
    picks it for `em` and `font-style: italic` instead of slanting the upright.
    """
    out = []
    for face in LOADED_FACES:
        for file, weight, style in face.files:
            kind = FONT_FORMATS[file[file.rindex(".") :].lower()]
            out.append(
                f'@font-face{{font-family:"{face.family}";font-style:{style};font-weight:{weight};'
                f'font-display:swap;src:url({prefix}{file}) format("{kind}")}}'
            )
    return "\n".join(out)


def step_css(step: Step, scale_key: str) -> str:
    """The declarations for one step, reading the `--font-<role>` variables.

    The size and the leading read the step's tokens, `--ox-m-h1` and
    `--ox-m-h1-leading`, so a page that sets a token restyles every heading
    on that step. The theme editor on the example pages does that.
    """
    decl = [
        f"font-size: var(--ox-{scale_key}-{step.name})",
        f"line-height: var(--ox-{scale_key}-{step.name}-leading)",
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


def _face_json(f: Face) -> dict:
    return {
        "family": f.family,
        "job": f.job,
        "stack": f.css_stack,
        "next_var": f.next_var,
        "files": [{"file": file, "weight": w, "style": style} for file, w, style in f.files],
        "features": f.features,
    }


def as_json() -> dict:
    return {
        "faces": {f.key: _face_json(f) for f in FACES},
        "extra_faces": [_face_json(f) for f in EXTRA_FACES],
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
    if family("sans") != TEXT_FACE.family or family("display") != HEADING_FACE.family:
        problems.append("the sans and display roles do not resolve to the theme's faces")
    if family("hero") != family("display") or family(HERO_ROLE_OUTSIDE) != family("display"):
        problems.append("the hero role does not take the heading face outside a hero step")
    if family("wordmark") != WORDMARK_FACE.family or family(HERO_ROLE_INSIDE) != WORDMARK_FACE.family:
        problems.append(f"the wordmark role is not {WORDMARK_FACE.family}")
    if HEADING_FACE is not _HEADING and (_HEADING.files, _HEADING.stack, _HEADING.features) != (
        HEADING_FACE.files, HEADING_FACE.stack, HEADING_FACE.features
    ):
        problems.append(
            f"faces.display names {_HEADING.family}, as another role does, so it needs that role's files, fallback, and features"
        )
    families = {}
    for face in FACES:
        if families.setdefault(face.family, face) is not face:
            problems.append(f"two roles name {face.family} with different files, fallback, or features")
    for role, spec in _FACES.items():
        files = [f["file"] for f in spec["files"]] + ([spec["outline"]["file"]] if "outline" in spec else [])
        for file in files:
            if not (FONTS / file).is_file():
                problems.append(f"faces.{role} names fonts/{file}, which does not exist")
    for face in EXTRA_FACES:
        if face.family in families:
            problems.append(f"extra_faces names {face.family}, which a role already takes")
        families.setdefault(face.family, face)
        for file, _, _ in face.files:
            if not (FONTS / file).is_file():
                problems.append(f"extra_faces names fonts/{file} for {face.family}, which does not exist")
    for face in LOADED_FACES:
        upright = {w for _, w, style in face.files if style == "normal"}
        if not upright:
            problems.append(f"{face.family} has no upright file, so a browser has nothing to set upright text in")
    for r in ROUTING:
        if r.role not in ("display", "sans", "mono"):
            problems.append(f"{r.elements} route to the {r.role} role, which only a wordmark or a hero line takes")
    for s in SCALES:
        sizes = [st.px for st in s.steps]
        if sizes != sorted(sizes, reverse=True):
            problems.append(f"{s.name} scale does not descend: {sizes}")
        for st in s.steps:
            if abs(rem_px(st.size) - st.px) > 1e-6:
                problems.append(f"{s.name} {st.name}: {st.size} is {rem_px(st.size):g}px, not a whole number of pixels")
            if st.name in ("h1", "h2", "h3", "h4") and st.role != "display":
                problems.append(f"{s.name} {st.name} does not read the heading role")
            if st.name == "body" and st.role != "sans":
                problems.append(f"{s.name} body is not in the text face")
            if st.name == "micro" and st.role != "mono":
                problems.append(f"{s.name} micro is not in the code face")
            if st.hero and (s is not MARKETING or st.name != "h1"):
                problems.append(f"{s.name} {st.name} admits a hero, and only the marketing h1 may")
            if st.hero and st.px < DISPLAY_FLOOR_PX:
                problems.append(f"{s.name} {st.name}: a {WORDMARK_FACE.family} hero at {st.px}px, below the {DISPLAY_FLOOR_PX}px floor")
            if st.name == "h1" and not (1.05 <= float(st.leading) <= 1.25):
                problems.append(f"{s.name} h1 line-height {st.leading} is outside 1.05 to 1.25")
    if HEADING_FACE is WORDMARK_FACE:
        for s in SCALES:
            for st in s.steps:
                if st.role == "display" and st.px < DISPLAY_FLOOR_PX:
                    problems.append(
                        f"{s.name} {st.name} sets a heading in {WORDMARK_FACE.family} at {st.px}px, below the {DISPLAY_FLOOR_PX}px floor"
                    )
    if not any(st.hero for st in MARKETING.steps):
        problems.append(f"no marketing step admits a hero, so line 1 of a hero cannot take {WORDMARK_FACE.family}")
    return problems


if __name__ == "__main__":
    for s in SCALES:
        print(f"{s.name}: {s.use}")
        for st in s.steps:
            hero = "  hero" if st.hero else ""
            print(f"  {st.name:6} {family(st.role):15} {st.size:9} {st.px:3}px  lh {st.leading:5}  w{st.weight}  {st.tracking}{hero}")
    print("problems:", verify() or "none")
