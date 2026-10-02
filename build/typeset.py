"""The house type: three faces, five roles, and two size scales.

Mac set this rule on 2026-10-02. It replaces every earlier face and size rule.

**Aeonik** sets the default text on every surface: body, labels, buttons,
tables, and navigation. It sets h1 to h3 in the web app and the internal
tools, and every h4 to h6 everywhere. Its italic ships beside the upright as
the same family. **Space Grotesk** sets h1 to h3 on the marketing and customer
sites, and the docs sites count as customer sites. It also sets the oxagen and
stella wordmarks and Stella's asterisk, and that use is fixed. Its wide
geometric letters lose their shape below 20 px, so no heading step that can
take it is smaller. **Monaspace Neon** sets code, terminal output, logs,
digests, paths, ids, and the numbers in a metric or a table. Its texture
healing (`calt`) and code ligatures (`liga`) are on wherever it is used.

**Aeonik Mono** and **Aeonik Fono** ship too, from `extra_faces` in the
theme. Each gets @font-face rules and a next/font loader, so a page can name
its family. No role reads them yet.

A product's CSS names a role, `--font-<role>`, and each role resolves to one
face:

- `sans` is Aeonik, for everything read, every app heading, and every h4 to h6.
- `display` is Space Grotesk, for h1 to h3 on a marketing or customer site.
  It is the theme's `display` face, which the theme editor offers as the
  heading role.
- `heading` is the face h1 to h3 take on the surface. It reads `sans`, so an
  app heading is Aeonik. A marketing or docs site points it at `display` with
  one line, `--font-heading: var(--font-display)`.
- `mono` is Monaspace Neon.
- `wordmark` is Space Grotesk, for a wordmark set as text rather than drawn.
  It is fixed, whatever face `display` takes.

Two scales, because a landing page and a dashboard do not breathe the same
way. The **marketing** scale is large and spaced for a landing page or a post
read once. Its h1 to h3 read `display`. The **app** scale is dense for panels,
tables, and logs. Its h1 to h3 read `heading`. On both scales h4 and body read
`sans`, and micro reads `mono`. A surface picks one scale and uses it
throughout. No step on either scale is below 14px (`theme.TYPE_FLOOR_PX`).

Every value here comes from `theme/theme.json`, through `build/theme.py`, and
`build/build.py` emits it into `tokens/`. Nothing downstream retypes a size.
The names above describe the theme the kit ships. A theme that names other
families changes what each role resolves to, and `verify()` checks the rules
that hold for any family.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from theme import ROOT, THEME, TYPE_FLOOR_PX, rem_px

FONTS = ROOT / "fonts"

_FACES = THEME["faces"]
_TYPE = THEME["type"]

# --------------------------------------------------------------------------
# faces
# --------------------------------------------------------------------------


@dataclass(frozen=True)
class Face:
    key: str  # the role whose face this is: wordmark | display | sans | mono, or extra-<family> for a face no role takes
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


def _face(role: str, job: str) -> Face:
    return _from_spec(role, _FACES[role], job)


#: The face of each role in the theme. The module-level names name the role's
#: face whatever family the theme holds, because other modules import them.
#: SPACE_GROTESK and MONASPACE_NEON keep the names of the faces the kit ships.
WORDMARK_FACE = _face("wordmark", "the oxagen and stella wordmarks and Stella's asterisk, set as text. It is fixed")
DISPLAY_FACE = _face("display", "h1 to h3 on a marketing or customer site")
TEXT_FACE = _face("sans", "body, labels, buttons, tables, navigation, every app heading, and every h4 to h6")
CODE_FACE = _face("mono", "code, terminal output, logs, digests, paths, ids, and numbers in tables")
SPACE_GROTESK, MONASPACE_NEON = WORDMARK_FACE, CODE_FACE

#: The face each role in the theme names, by role.
FACE: dict[str, Face] = {f.key: f for f in (WORDMARK_FACE, DISPLAY_FACE, TEXT_FACE, CODE_FACE)}


def _one_per_family(faces: tuple[Face, ...]) -> tuple[Face, ...]:
    """`faces` with each family once, the first face that names it kept."""
    seen: dict[str, Face] = {}
    for f in faces:
        seen.setdefault(f.family, f)
    return tuple(seen.values())


#: The faces the roles load, one per family. The shipped theme gives the
#: display role the wordmark's family, so Space Grotesk loads once and the kit
#: loads three role faces.
FACES: tuple[Face, ...] = _one_per_family(tuple(FACE.values()))

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
    face: str  # the role whose face this one resolves to
    job: str
    reads: str = ""  # another role this one points at, so a surface can repoint it


ROLES: tuple[Role, ...] = (
    Role("sans", "sans", "body, labels, buttons, tables, navigation, every app heading, and every h4 to h6"),
    Role("display", "display", "h1 to h3 on a marketing or customer site"),
    Role(
        "heading",
        "sans",
        "h1 to h3 on this surface. A marketing or docs site points it at --font-display",
        reads="sans",
    ),
    Role("mono", "mono", "code, logs, ids, and numbers in tables"),
    Role("wordmark", "wordmark", "a wordmark set as text rather than drawn. It is fixed"),
)
ROLE = {r.key: r for r in ROLES}

#: The line a marketing or docs site writes to set its h1 to h3 in the display face.
MARKETING_HEADINGS = "--font-heading: var(--font-display)"


def family(role: str) -> str:
    """The family a role resolves to on an app surface."""
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


@dataclass(frozen=True)
class Scale:
    key: str  # the utility prefix: text-<key>-<step>
    name: str
    use: str
    steps: tuple[Step, ...]

    def step(self, name: str) -> Step:
        """The step named `name`: h1, h2, h3, h4, body, or micro."""
        return next(st for st in self.steps if st.name == name)


#: The role each step reads. A marketing h1 to h3 reads the display face. An
#: app h1 to h3 reads the surface's heading role, which is the text face
#: unless the surface points it at display. Every h4 and body read the text
#: face, and micro the code face.
STEP_ROLES = {
    "marketing": {"h1": "display", "h2": "display", "h3": "display", "h4": "sans", "body": "sans", "micro": "mono"},
    "app": {"h1": "heading", "h2": "heading", "h3": "heading", "h4": "sans", "body": "sans", "micro": "mono"},
}


def _scale(key: str, name: str, use: str) -> Scale:
    steps = []
    for step, role in STEP_ROLES[name].items():
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
            )
        )
    return Scale(key=key, name=name, use=use, steps=tuple(steps))


MARKETING = _scale("m", "marketing", "landing pages and posts read once: large and spaced")
APP = _scale("a", "app", "dashboards, panels, tables, terminals, logs: dense")

SCALES: tuple[Scale, ...] = (MARKETING, APP)


@dataclass(frozen=True)
class Route:
    elements: str
    role: str
    extra: tuple[str, ...] = ()  # declarations beyond the face


#: Which role each element takes, whatever the scale. This is the routing.
#: h1 to h3 read the surface's heading role, so an app gets Aeonik and a
#: marketing site that repoints `--font-heading` gets Space Grotesk. No
#: element reaches the display or wordmark face on its own.
ROUTING: tuple[Route, ...] = (
    Route("h1, h2, h3", "heading", ("letter-spacing: var(--tracking-display)",)),
    Route("h4, h5, h6", "sans", (f"font-weight: {WEIGHTS['subheading']}",)),
    Route("body, button, input, select, textarea, label, nav", "sans"),
    Route("pre, code, kbd, samp, [data-mono]", "mono", (f"font-feature-settings: {MONASPACE_NEON.features}",)),
)

#: A heading step that can take the display face is set at this size or up.
#: Space Grotesk's wide letters lose their shape below it.
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
        "faces": {role: _face_json(f) for role, f in FACE.items()},
        "extra_faces": [_face_json(f) for f in EXTRA_FACES],
        "roles": {
            r.key: {
                "css_var": f"--font-{r.key}",
                "face": r.face,
                "family": FACE[r.face].family,
                "job": r.job,
                **({"reads": f"--font-{r.reads}"} if r.reads else {}),
            }
            for r in ROLES
        },
        "marketing_headings": MARKETING_HEADINGS,
        "weights": WEIGHTS,
        "tracking": TRACKING,
        "routing": [{"elements": r.elements, "role": r.role, "family": family(r.role)} for r in ROUTING],
        "display_floor_px": DISPLAY_FLOOR_PX,
        "type_floor_px": TYPE_FLOOR_PX,
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
    if family("sans") != TEXT_FACE.family or family("display") != DISPLAY_FACE.family:
        problems.append("the sans and display roles do not resolve to the theme's faces")
    if ROLE["heading"].reads != "sans" or family("heading") != TEXT_FACE.family:
        problems.append("the heading role does not read the text face, so an app heading would not take it")
    if family("wordmark") != WORDMARK_FACE.family:
        problems.append(f"the wordmark role is not {WORDMARK_FACE.family}")
    families: dict[str, Face] = {}
    for face in FACE.values():
        first = families.setdefault(face.family, face)
        if (first.files, first.stack, first.features) != (face.files, face.stack, face.features):
            problems.append(
                f"faces.{face.key} names {face.family}, as faces.{first.key} does, "
                f"so it needs that face's files, fallback, and features"
            )
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
    routed = {r.elements: r.role for r in ROUTING}
    if routed.get("h1, h2, h3") != "heading":
        problems.append("h1 to h3 do not route to the heading role, so a surface cannot choose their face")
    if routed.get("h4, h5, h6") != "sans":
        problems.append("h4 to h6 do not route to the text face")
    for r in ROUTING:
        if r.role in ("display", "wordmark"):
            problems.append(f"{r.elements} route to the {r.role} role, which an app surface must not reach on its own")
    for s in SCALES:
        sizes = [st.px for st in s.steps]
        if sizes != sorted(sizes, reverse=True):
            problems.append(f"{s.name} scale does not descend: {sizes}")
        for st in s.steps:
            if abs(rem_px(st.size) - st.px) > 1e-6:
                problems.append(f"{s.name} {st.name}: {st.size} is {rem_px(st.size):g}px, not a whole number of pixels")
            if st.role != STEP_ROLES[s.name][st.name]:
                problems.append(f"{s.name} {st.name} reads the {st.role} role, not the {STEP_ROLES[s.name][st.name]} role")
            if st.px < TYPE_FLOOR_PX:
                problems.append(f"{s.name} {st.name} is {st.px}px, below the {TYPE_FLOOR_PX}px floor for every step")
            if st.role in ("display", "heading") and st.px < DISPLAY_FLOOR_PX:
                problems.append(
                    f"{s.name} {st.name} is {st.px}px and can take {DISPLAY_FACE.family}, "
                    f"below the {DISPLAY_FLOOR_PX}px floor for a display heading"
                )
            if st.name == "h1" and not (1.05 <= float(st.leading) <= 1.25):
                problems.append(f"{s.name} h1 line-height {st.leading} is outside 1.05 to 1.25")
    for scale, steps in STEP_ROLES.items():
        if [steps[h] for h in ("h1", "h2", "h3")] != (["display"] * 3 if scale == "marketing" else ["heading"] * 3):
            problems.append(f"the {scale} h1 to h3 do not read the {'display' if scale == 'marketing' else 'heading'} role")
        if (steps["h4"], steps["body"], steps["micro"]) != ("sans", "sans", "mono"):
            problems.append(f"the {scale} h4, body, and micro do not read the text, text, and code faces")
    return problems


if __name__ == "__main__":
    for s in SCALES:
        print(f"{s.name}: {s.use}")
        for st in s.steps:
            print(f"  {st.name:6} {st.role:8} {family(st.role):15} {st.size:9} {st.px:3}px  lh {st.leading:5}  w{st.weight}  {st.tracking}")
    print("problems:", verify() or "none")
