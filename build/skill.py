"""Check the branding skill and its stub, write nothing.

    python3 build/skill.py --check

The skill in `skills/oxagen-branding/` holds the method, and the brand it
describes lives in `tokens/`, `messages/`, and the skill's references. Agents
fetch all of it from `main` at a pinned commit, so a copy of the skill never
goes stale. That holds only while four things stay true, and this check fails
when one of them breaks:

- The stub in `skills/stub/oxagen-branding/` carries the same frontmatter as
  the skill, byte for byte. The frontmatter is what makes an agent load the
  skill, so a stub with a different description triggers on different work.
- `SKILL.md` and the stub carry no colour value and no line from the message
  registry. A value typed into the method is a second authority that drifts.
- Every repo path `SKILL.md` names exists, so the fetch it describes never
  returns a 404.
- The skill folder holds only `SKILL.md`, `references/*.md`, and the two
  generated assets. An archive or a stray copy would ride along into every
  project that installs from the folder.

Needs Python 3.10 and nothing else.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKILL_DIR = ROOT / "skills" / "oxagen-branding"
SKILL = SKILL_DIR / "SKILL.md"
STUB = ROOT / "skills" / "stub" / "oxagen-branding" / "SKILL.md"
INDEX = ROOT / "messages" / "index.json"

#: The files the skill folder may hold. `assets/` is written by build/build.py.
ALLOWED = {"SKILL.md", "assets/tokens.css", "assets/logo.svg"}
ALLOWED_DIRS = {"references": ".md"}
IGNORED = {".DS_Store"}

HEX = re.compile(r"(?<![\w&/])#(?:[0-9A-Fa-f]{8}|[0-9A-Fa-f]{6}|[0-9A-Fa-f]{3})\b")
CODE_SPAN = re.compile(r"`([^`\s]+)`")
#: A registry line shorter than this is too generic to count as a copy.
MIN_LINE = 30


def frontmatter(text: str) -> str:
    """The text between the opening and closing `---`, or "" when there is none."""
    if not text.startswith("---\n"):
        return ""
    end = text.find("\n---\n", 4)
    return text[4:end] if end != -1 else ""


def registry_lines() -> list[tuple[str, str]]:
    """(entry id, text) for every title and long form in the registry."""
    entries = json.loads(INDEX.read_text())["entries"]
    out = []
    for e in entries:
        for field in ("title", "long"):
            text = (e.get(field) or "").strip()
            if len(text) >= MIN_LINE:
                out.append((e["id"], text))
    return out


def named_paths(text: str) -> list[str]:
    """Repo paths a file names in code spans: `dir/...` under a root entry, or a root `NAME.md`."""
    roots = {p.name for p in ROOT.iterdir()}
    paths = []
    for token in CODE_SPAN.findall(text):
        if "/" in token and token.split("/", 1)[0] in roots:
            paths.append(token.rstrip("/"))
        elif re.fullmatch(r"[A-Z][A-Z_]*\.md", token):
            paths.append(token)
    return list(dict.fromkeys(paths))


def stray_files() -> list[str]:
    out = []
    for path in sorted(SKILL_DIR.rglob("*")):
        if path.is_dir() or path.name in IGNORED:
            continue
        rel = path.relative_to(SKILL_DIR).as_posix()
        top, _, rest = rel.partition("/")
        if rel in ALLOWED:
            continue
        if top in ALLOWED_DIRS and rest and "/" not in rest and rest.endswith(ALLOWED_DIRS[top]):
            continue
        out.append(rel)
    return out


def check() -> list[str]:
    problems = []
    skill, stub = SKILL.read_text(), STUB.read_text() if STUB.exists() else ""

    if not stub:
        problems.append(f"{STUB.relative_to(ROOT)} is missing")
    elif frontmatter(stub) != frontmatter(skill):
        problems.append(f"{STUB.relative_to(ROOT)} frontmatter differs from {SKILL.relative_to(ROOT)}; copy it byte for byte")
    if not frontmatter(skill):
        problems.append(f"{SKILL.relative_to(ROOT)} has no frontmatter")

    lines = registry_lines()
    for path, text in ((SKILL, skill), (STUB, stub)):
        name = path.relative_to(ROOT)
        for value in sorted(set(HEX.findall(text))):
            problems.append(f"{name} carries the colour {value}; name the token file instead")
        for entry, line in lines:
            if line in text:
                problems.append(f"{name} carries the registry line {entry}; point at messages/index.json instead")

    for rel in named_paths(skill):
        if not (ROOT / rel).exists():
            problems.append(f"{SKILL.relative_to(ROOT)} names {rel}, which does not exist")

    for rel in stray_files():
        problems.append(f"skills/oxagen-branding/{rel} does not belong in the skill folder")
    return problems


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--check", action="store_true", help="check, write nothing (the only mode)")
    ap.parse_args()
    problems = check()
    for p in problems:
        print("problem:", p)
    if problems:
        sys.exit(f"\n{len(problems)} problems in the branding skill")
    print("check: the skill, its stub, and the paths it names are consistent")


if __name__ == "__main__":
    main()
