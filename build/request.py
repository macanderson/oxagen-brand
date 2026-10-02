"""A theme request: the fields of `theme/theme.json` a person wants to change.

    python3 build/request.py --write              # write theme/request.schema.json
    python3 build/request.py --check              # fail if the committed schema is stale
    python3 build/request.py theme/requests/x.json  # validate one request

The theme editor on the kit's example pages writes a request when you select
Update all sites. The request lands in `theme/requests/` on a branch, and the
`apply-theme` workflow merges it into `theme/theme.json` with
`build/apply_theme.py`.

A request holds only what changed. Its colour, radius, shadow, spacing, and
type sections have the same shape as the theme's, with every field optional,
so a request that moves the gold is `{"color": {"gold": "#C9A227"}}` and a
summary. A face is the exception. A request names the whole face of a role,
and where its files come from:

- `google`: a Google Fonts family and the weights to fetch. The workflow
  fetches the files into `fonts/`.
- `upload`: files someone uploaded to `fonts/` on the same branch.
- `kit`: files already in `fonts/`, such as a face the kit ships.

A request cannot change the wordmark face. It is always Space Grotesk, drawn
from `fonts/SpaceGrotesk-VariableFont_wght.ttf` at weight 600 (Mac,
2026-10-02), so the schema leaves `faces.wordmark` out and `problems()` says
why. A new gold still recolours the wordmarks' gold x and asterisk, because
the marks paint their accent from `color.gold`.

`theme/request.schema.json` is derived from `theme/theme.schema.json` by
`request_schema()`, so the two cannot drift: `--check` fails when the
committed file differs from what this module writes, and `build/build.py
--check` runs the same comparison.

Standard library only, like `build/theme.py`.
"""

from __future__ import annotations

import argparse
import copy
import json
import sys
from pathlib import Path

from theme import ROOT, SCHEMA_FILE, WORDMARK_FIXED, validate

REQUEST_SCHEMA_FILE = ROOT / "theme" / "request.schema.json"
REQUESTS_DIR = ROOT / "theme" / "requests"
FONTS_DIR = ROOT / "fonts"

#: The four type roles a theme names, in the order the theme lists them.
ROLES = ("wordmark", "display", "sans", "mono")

#: The roles a request may change. The wordmark face is fixed.
REQUEST_ROLES = ("display", "sans", "mono")

#: The role a request may give an outline file: the art's text is drawn from
#: it. The marks are drawn from the wordmark face, which is fixed.
OUTLINE_ROLES = ("sans",)

#: The sections a request may change field by field.
PARTIAL_SECTIONS = ("color", "radius", "shadow", "spacing", "type")

#: The fallback a new family takes when the request names none.
DEFAULT_FALLBACK = {
    "display": ["system-ui", "-apple-system", "Segoe UI", "sans-serif"],
    "sans": ["system-ui", "-apple-system", "Segoe UI", "sans-serif"],
    "mono": ["ui-monospace", "SF Mono", "Menlo", "Consolas", "monospace"],
}

# --------------------------------------------------------------------------
# the schema
# --------------------------------------------------------------------------


def _partial(node: object) -> object:
    """`node` with every object's fields made optional.

    Objects reached through `properties`, `$defs`, and `additionalProperties`
    lose `required`. Array items keep theirs, because a request replaces an
    array whole: a face's file list needs a file and a weight in every item.
    """
    if not isinstance(node, dict):
        return node
    out: dict = {}
    for key, value in node.items():
        if key == "required":
            continue
        if key in ("properties", "$defs"):
            out[key] = {name: _partial(sub) for name, sub in value.items()}
        elif key == "additionalProperties" and isinstance(value, dict):
            out[key] = _partial(value)
        else:
            out[key] = copy.deepcopy(value)
    return out


def request_schema() -> dict:
    """The request schema, derived from the theme schema."""
    theme = json.loads(SCHEMA_FILE.read_text())
    defs = {name: _partial(d) for name, d in theme["$defs"].items() if name != "face"}
    defs["face_request"] = {
        "description": (
            "The whole face of one role. google fetches the family from Google Fonts at the weights given. "
            "upload reads files someone uploaded to fonts/ on the same branch. kit reads files already in fonts/."
        ),
        "type": "object",
        "required": ["family", "source"],
        "additionalProperties": False,
        "properties": {
            "family": {"$ref": "#/$defs/family"},
            "source": {
                "description": "Where the files come from.",
                "type": "string",
                "enum": ["google", "upload", "kit"],
            },
            "weights": {
                "description": "For google: the weights to fetch. The workflow fetches one variable file when the family has one.",
                "type": "array",
                "minItems": 1,
                "maxItems": 9,
                "items": {"$ref": "#/$defs/weight"},
            },
            "files": {
                "description": "For upload and kit: the files in fonts/, by name, with the weight each one draws. A .ttf, .otf, or .woff upload is converted to .woff2 for the web.",
                "$ref": "#/$defs/files",
            },
            "fallback": {"$ref": "#/$defs/fallback"},
            "features": {"$ref": "#/$defs/features"},
            "outline": {
                "description": (
                    "For sans: the file the art's text is drawn from. "
                    "When it is left out, the workflow picks the file closest to weight 400."
                ),
                "type": "object",
                "additionalProperties": False,
                "properties": {
                    "file": {"$ref": "#/$defs/file"},
                },
            },
        },
    }
    props = theme["properties"]
    return {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "$id": "https://brand.oxagen.cloud/theme/request.schema.json",
        "title": "Oxagen theme request",
        "description": (
            "The fields of theme/theme.json one change asks for. The theme editor writes a request into "
            "theme/requests/, and the apply-theme workflow merges it into theme/theme.json, fetches any Google face, "
            "and runs the generators. Every field is optional except summary. A face names the whole face of a role. "
            "The wordmark face is fixed, so faces has no wordmark."
        ),
        "type": "object",
        "required": ["summary"],
        "additionalProperties": False,
        "properties": {
            "$schema": {"type": "string", "pattern": "^[./a-z.-]{1,40}$"},
            "summary": {
                "description": "One line that says what the change is. It becomes the commit message.",
                "type": "string",
                "pattern": "^[A-Za-z0-9][A-Za-z0-9 .,:;()'/+&#%-]{0,119}$",
            },
            "requested_at": {
                "description": "When the editor wrote the request, in UTC.",
                "type": "string",
                "pattern": "^20[0-9]{2}-[01][0-9]-[0-3][0-9]T[0-2][0-9]:[0-5][0-9](:[0-5][0-9])?Z$",
            },
            **{name: _partial(props[name]) for name in PARTIAL_SECTIONS},
            "faces": {
                "description": (
                    "The roles whose face changes. Each names the whole face. "
                    "The wordmark face is fixed: Space Grotesk, drawn at weight 600."
                ),
                "type": "object",
                "additionalProperties": False,
                "properties": {role: {"$ref": "#/$defs/face_request"} for role in REQUEST_ROLES},
            },
        },
        "$defs": defs,
    }


def schema_text() -> str:
    return json.dumps(request_schema(), indent=2) + "\n"


# --------------------------------------------------------------------------
# validation
# --------------------------------------------------------------------------


#: What `problems()` says about a request that names the wordmark face.
WORDMARK_REFUSED = (
    f"faces.wordmark cannot change, because {WORDMARK_FIXED}. "
    "Remove faces.wordmark from the request. A new color.gold still recolours the wordmarks' gold x and asterisk."
)


def problems(request: object) -> list[str]:
    """Every way `request` breaks the request schema or the rules beside it."""
    schema = request_schema()
    found = validate(request, schema, schema, "")
    faces = request.get("faces") if isinstance(request, dict) else None
    if isinstance(faces, dict) and "wordmark" in faces:
        # The schema's own line names the field without saying why.
        found = [WORDMARK_REFUSED] + [p for p in found if p != "faces has wordmark, which the schema does not name"]
    if found or not isinstance(request, dict):
        return [p.replace("the theme", "the request", 1) for p in found]
    if not any(key in request for key in (*PARTIAL_SECTIONS, "faces")):
        found.append("the request changes nothing: it names no colour, face, radius, shadow, spacing, or type")
    for role, face in request.get("faces", {}).items():
        src = face["source"]
        if src == "google" and "weights" not in face:
            found.append(f"faces.{role} is a google face, so it needs weights")
        if src == "google" and "files" in face:
            found.append(f"faces.{role} is a google face, so the workflow fetches its files and the request names none")
        if src in ("upload", "kit") and "files" not in face:
            found.append(f"faces.{role} is a {src} face, so it needs files")
        if src in ("upload", "kit") and "weights" in face:
            found.append(f"faces.{role} is a {src} face, so its files carry the weights and weights is not used")
        if "outline" in face and role not in OUTLINE_ROLES:
            found.append(f"faces.{role} has an outline, and only sans is drawn from one")
    return found


# --------------------------------------------------------------------------
# merging
# --------------------------------------------------------------------------


def _deep_merge(base: dict, change: dict) -> dict:
    out = copy.deepcopy(base)
    for key, value in change.items():
        if isinstance(value, dict) and isinstance(out.get(key), dict):
            out[key] = _deep_merge(out[key], value)
        else:
            out[key] = copy.deepcopy(value)
    return out


def merge(theme: dict, request: dict, faces: dict[str, dict] | None = None) -> dict:
    """The theme with the request's changes in it.

    `faces` maps a role to the face the theme takes, already resolved: a
    google face's files fetched and an upload's files converted. The request's
    own face entries name sources the theme does not hold, so they never reach
    the theme as written.
    """
    out = copy.deepcopy(theme)
    for name in PARTIAL_SECTIONS:
        if name in request:
            out[name] = _deep_merge(out[name], request[name])
    for role, face in (faces or {}).items():
        out["faces"][role] = copy.deepcopy(face)
    return out


def face_entry(role: str, current: dict, request_face: dict, files: list[dict], outline: dict | None) -> dict:
    """The theme's face for `role`, from the request and the resolved files.

    A field the request leaves out keeps the current face's value when the
    family stays the same. A new family starts from the role's default
    fallback and no features. The wordmark face is fixed, so `role` is never
    the wordmark.
    """
    if role not in REQUEST_ROLES:
        raise ValueError(WORDMARK_REFUSED)
    same = request_face["family"] == current["family"]
    face = {
        "family": request_face["family"],
        "source": "google" if request_face["source"] == "google" else "kit",
        "files": files,
        "fallback": request_face.get("fallback", current["fallback"] if same else DEFAULT_FALLBACK[role]),
        "features": request_face.get("features", current["features"] if same else []),
    }
    if role in OUTLINE_ROLES:
        if outline is None:
            raise ValueError(f"faces.{role} needs an outline file")
        face["outline"] = outline
    return face


def nearest(files: list[dict], weight: int) -> dict:
    """The file that draws closest to `weight`: a variable file that covers it, else the nearest static one."""

    def distance(f: dict) -> float:
        parts = [int(w) for w in f["weight"].split()]
        lo, hi = parts[0], parts[-1]
        return 0 if lo <= weight <= hi else min(abs(weight - lo), abs(weight - hi))

    return min(files, key=lambda f: (distance(f), len(f["weight"].split()) == 1))


# --------------------------------------------------------------------------
# writing theme.json in its own layout
# --------------------------------------------------------------------------


def _scalar(value: object) -> str:
    return json.dumps(value)


def _inline(value: object, depth: int) -> bool:
    """Whether the theme file sets `value` on one line.

    The layout follows the shipped file: a list of plain values, a list of one
    flat object, an object of plain values three levels down or deeper, and the
    gold's two neighbours.
    """
    flat = lambda v: not isinstance(v, (dict, list))  # noqa: E731
    if isinstance(value, list):
        return all(flat(v) for v in value) or (
            len(value) == 1 and isinstance(value[0], dict) and all(flat(v) for v in value[0].values())
        )
    if isinstance(value, dict):
        if not all(flat(v) for v in value.values()):
            return False
        if depth >= 3:
            return True
        return depth == 2 and len(value) <= 2 and all(isinstance(v, (int, float)) for v in value.values())
    return True


def _one_line(value: object) -> str:
    if isinstance(value, dict):
        if not value:
            return "{}"
        return "{ " + ", ".join(f"{_scalar(k)}: {_one_line(v)}" for k, v in value.items()) + " }"
    if isinstance(value, list):
        return "[" + ", ".join(_one_line(v) for v in value) + "]"
    return _scalar(value)


def _dump(value: object, depth: int, indent: str) -> str:
    if _inline(value, depth):
        return _one_line(value)
    inner = indent + "  "
    if isinstance(value, dict):
        rows = [f"{inner}{_scalar(k)}: {_dump(v, depth + 1, inner)}" for k, v in value.items()]
        return "{\n" + ",\n".join(rows) + "\n" + indent + "}"
    rows = [f"{inner}{_dump(v, depth + 1, inner)}" for v in value]  # type: ignore[union-attr]
    return "[\n" + ",\n".join(rows) + "\n" + indent + "]"


def dump_theme(theme: dict) -> str:
    """`theme` as `theme/theme.json` lays it out, so a change shows as the lines it changes."""
    return _dump(theme, 0, "") + "\n"


# --------------------------------------------------------------------------
# command line
# --------------------------------------------------------------------------


def check_schema() -> list[str]:
    if not REQUEST_SCHEMA_FILE.is_file():
        return [f"{REQUEST_SCHEMA_FILE.relative_to(ROOT)} is missing; run build/request.py --write"]
    if REQUEST_SCHEMA_FILE.read_text() != schema_text():
        return [
            f"{REQUEST_SCHEMA_FILE.relative_to(ROOT)} differs from what theme/theme.schema.json produces; "
            "run build/request.py --write"
        ]
    return []


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("request", nargs="?", type=Path)
    ap.add_argument("--write", action="store_true", help="write theme/request.schema.json")
    ap.add_argument("--check", action="store_true", help="fail if theme/request.schema.json is stale")
    a = ap.parse_args()
    if a.write:
        REQUEST_SCHEMA_FILE.write_text(schema_text())
        print(f"wrote {REQUEST_SCHEMA_FILE.relative_to(ROOT)}")
        return 0
    if a.check:
        found = check_schema()
        for p in found:
            print("problem:", p)
        return 1 if found else 0
    if a.request is None:
        ap.error("give a request file, --write, or --check")
    try:
        request = json.loads(a.request.read_text())
    except (OSError, ValueError) as e:
        print(f"problem: {a.request} cannot be read: {e}")
        return 1
    found = problems(request)
    for p in found:
        print(f"problem: {a.request}: {p}")
    if not found:
        print(f"{a.request} is a valid theme request")
    return 1 if found else 0


if __name__ == "__main__":
    sys.exit(main())
