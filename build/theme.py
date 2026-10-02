"""Load `theme/theme.json`, the one editable source for the house design.

    python3 build/theme.py           # validate theme/theme.json against its schema

`theme/theme.json` holds every value a person may change: the colours, the
faces, the radius, the shadows, the spacing, and the two type scales.
`theme/theme.schema.json` says what each field holds. `color.py` and
`typeset.py` read the theme through this module, and every generator reads
those two, so a change to the theme reaches every token, mark, and image on
the next build.

The theme is validated before anything reads it. Each value is written into
CSS, TypeScript, JSON, SVG, and HTML, and in a later phase a workflow applies
a theme that arrives in a pull request, so the schema is strict: a colour is a
six-digit hex, a font file is a bare file name, and no string may carry the
characters that would end a CSS declaration or an HTML tag.

The validator covers the keywords the schema uses, with the standard library
alone, because `build/conformance.py` imports `color.py` and runs with no
packages installed. It rejects a schema keyword it does not know, so the
schema cannot ask for a rule that nothing checks.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
THEME_FILE = ROOT / "theme" / "theme.json"
SCHEMA_FILE = ROOT / "theme" / "theme.schema.json"

#: Keywords that describe a schema and constrain nothing.
ANNOTATIONS = {"$schema", "$id", "$comment", "$defs", "title", "description", "default", "examples"}

#: Keywords this validator checks.
CHECKED = {
    "type", "properties", "required", "additionalProperties", "items", "minItems", "maxItems",
    "enum", "pattern", "minLength", "maxLength", "minimum", "maximum", "exclusiveMinimum",
    "exclusiveMaximum", "$ref",
}

_TYPES = {
    "object": lambda v: isinstance(v, dict),
    "array": lambda v: isinstance(v, list),
    "string": lambda v: isinstance(v, str),
    "number": lambda v: isinstance(v, (int, float)) and not isinstance(v, bool),
    "integer": lambda v: isinstance(v, int) and not isinstance(v, bool),
    "boolean": lambda v: isinstance(v, bool),
}


def _resolve(ref: str, root: dict) -> dict:
    if not ref.startswith("#/"):
        raise ValueError(f"only local references are supported: {ref}")
    node: object = root
    for part in ref[2:].split("/"):
        node = node[part]  # type: ignore[index]
    return node  # type: ignore[return-value]


def validate(value: object, schema: dict, root: dict, where: str = "") -> list[str]:
    """Every way `value` breaks `schema`, as one line per problem."""
    here = where or "the theme"
    unknown = set(schema) - ANNOTATIONS - CHECKED
    if unknown:
        return [f"the schema at {here} uses {', '.join(sorted(unknown))}, which build/theme.py does not check"]
    if "$ref" in schema:
        return validate(value, _resolve(schema["$ref"], root), root, where)

    problems: list[str] = []
    kind = schema.get("type")
    if kind is not None:
        kinds = kind if isinstance(kind, list) else [kind]
        if not any(_TYPES[k](value) for k in kinds):
            return [f"{here} is {json.dumps(value)}, not a {' or '.join(kinds)}"]
    if "enum" in schema and value not in schema["enum"]:
        problems.append(f"{here} is {json.dumps(value)}, not one of {json.dumps(schema['enum'])}")

    if isinstance(value, str):
        if "pattern" in schema and not re.search(schema["pattern"], value):
            problems.append(f"{here} is {json.dumps(value)}, which does not match {schema['pattern']}")
        if "minLength" in schema and len(value) < schema["minLength"]:
            problems.append(f"{here} is shorter than {schema['minLength']} characters")
        if "maxLength" in schema and len(value) > schema["maxLength"]:
            problems.append(f"{here} is longer than {schema['maxLength']} characters")

    if _TYPES["number"](value):
        n = value  # type: ignore[assignment]
        if "minimum" in schema and n < schema["minimum"]:
            problems.append(f"{here} is {n}, below the minimum {schema['minimum']}")
        if "maximum" in schema and n > schema["maximum"]:
            problems.append(f"{here} is {n}, above the maximum {schema['maximum']}")
        if "exclusiveMinimum" in schema and n <= schema["exclusiveMinimum"]:
            problems.append(f"{here} is {n}, not above {schema['exclusiveMinimum']}")
        if "exclusiveMaximum" in schema and n >= schema["exclusiveMaximum"]:
            problems.append(f"{here} is {n}, not below {schema['exclusiveMaximum']}")

    if isinstance(value, list):
        if "minItems" in schema and len(value) < schema["minItems"]:
            problems.append(f"{here} holds {len(value)} items, fewer than {schema['minItems']}")
        if "maxItems" in schema and len(value) > schema["maxItems"]:
            problems.append(f"{here} holds {len(value)} items, more than {schema['maxItems']}")
        if "items" in schema:
            for i, item in enumerate(value):
                problems += validate(item, schema["items"], root, f"{where}[{i}]")

    if isinstance(value, dict):
        props = schema.get("properties", {})
        for key in schema.get("required", []):
            if key not in value:
                problems.append(f"{here} has no {key}")
        extra = schema.get("additionalProperties", True)
        for key, item in value.items():
            path = f"{where}.{key}" if where else key
            if key in props:
                problems += validate(item, props[key], root, path)
            elif extra is False:
                problems.append(f"{here} has {key}, which the schema does not name")
            elif isinstance(extra, dict):
                problems += validate(item, extra, root, path)
    return problems


#: The wordmark face, which never changes. Mac, 2026-10-02: "i would never
#: change the wordmark font - that is always going to be space grotesk for the
#: forseeable future". The build draws both wordmarks and Stella's asterisk
#: from this file at this weight, and `glyphs.verify()` holds the result to
#: the reference drawing in `build/reference/`.
WORDMARK_FAMILY = "Space Grotesk"
WORDMARK_OUTLINE = {"file": "SpaceGrotesk-VariableFont_wght.ttf", "weight": 600}
WORDMARK_FIXED = (
    "the wordmark face is fixed: Space Grotesk, drawn from fonts/SpaceGrotesk-VariableFont_wght.ttf at weight 600"
)


def wordmark_problems(theme: dict) -> list[str]:
    """How `theme`'s wordmark face differs from the fixed one. Expects a theme that validates."""
    face = theme["faces"]["wordmark"]
    found = []
    if face["family"] != WORDMARK_FAMILY:
        found.append(f"faces.wordmark.family is {json.dumps(face['family'])}, and {WORDMARK_FIXED}")
    outline = face.get("outline", {})
    if outline.get("file") != WORDMARK_OUTLINE["file"]:
        found.append(f"faces.wordmark.outline.file is {json.dumps(outline.get('file'))}, and {WORDMARK_FIXED}")
    if outline.get("weight") != WORDMARK_OUTLINE["weight"]:
        found.append(f"faces.wordmark.outline.weight is {json.dumps(outline.get('weight'))}, and {WORDMARK_FIXED}")
    return found


def problems(theme: object | None = None) -> list[str]:
    """What is wrong with the theme on disk, or with `theme` when given."""
    try:
        schema = json.loads(SCHEMA_FILE.read_text())
    except (OSError, ValueError) as e:
        return [f"{SCHEMA_FILE.relative_to(ROOT)} cannot be read: {e}"]
    if theme is None:
        try:
            theme = json.loads(THEME_FILE.read_text())
        except (OSError, ValueError) as e:
            return [f"{THEME_FILE.relative_to(ROOT)} cannot be read: {e}"]
    found = validate(theme, schema, schema)
    if found or not isinstance(theme, dict):
        return found
    return wordmark_problems(theme)


def load() -> dict:
    """The theme, validated. Exits with every problem when it does not validate."""
    found = problems()
    if found:
        lines = [f"problem: {THEME_FILE.relative_to(ROOT)}: {p}" for p in found]
        raise SystemExit("\n".join(lines) + "\nthe theme does not validate; nothing was read")
    return json.loads(THEME_FILE.read_text())


THEME: dict = load()


def rem_px(length: str) -> float:
    """A `rem` or `px` length from the theme, in CSS pixels at a 16px root."""
    if length.endswith("rem"):
        return float(length[:-3]) * 16
    if length.endswith("px"):
        return float(length[:-2])
    raise ValueError(f"{length} is not a rem or px length")


if __name__ == "__main__":
    print(f"theme: {THEME_FILE.relative_to(ROOT)} validates against {SCHEMA_FILE.relative_to(ROOT)}")
    sys.exit(0)
