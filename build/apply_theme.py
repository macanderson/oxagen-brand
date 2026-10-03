"""Apply a theme request to the kit. This is the step behind Update all sites.

    python3 build/apply_theme.py apply --state DIR theme/requests/<name>.json [...]
    python3 build/apply_theme.py report --state DIR > comment.md

The theme editor on the kit's example pages writes a request into
`theme/requests/` on a branch. `.github/workflows/apply-theme.yml` runs this
script on that branch's pull request, then runs the generators, commits the
result, and comments on the pull request with `report`.

`apply` does five things, in order, and writes nothing until every request
validates:

1. Validates each request against `theme/request.schema.json`
   (`build/request.py`). A request that names `faces.wordmark` fails here:
   the wordmark face is fixed, Space Grotesk drawn at weight 600.
2. Resolves each face the request names. A `google` face is fetched from
   Google Fonts: the latin WOFF2 files at the requested weights, a TTF to draw
   the art's text from for the text role, and the family's licence from the
   google/fonts repository. An `upload` face must already be in `fonts/` on
   the branch, and a TTF, OTF, or WOFF upload gets a WOFF2 copy for the web.
3. Merges the requests into `theme/theme.json`, in file-name order, and
   validates the result against `theme/theme.schema.json`.
4. Carries a new gold into the copies no generator writes: the three gold
   hexes in the files `CARRY_FILES` lists, and the gold ramp's hue in
   `ui/src/styles/globals.css`.
5. Deletes the request files, so the request's pull request carries the
   theme change and not the request.

It records what it did in `DIR/state.json`. `report` reads that file in a
fresh process, so the colour module loads the new theme, and writes the pull
request comment: what changed, the new gold and its neighbours, and every
contrast warning.

Every path the script writes is checked to sit inside `theme/` or `fonts/`
(or, for the gold carry, to be one of `CARRY_FILES`). Needs fontTools and
brotli, which CI's `check` job installs.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

import request as R
from theme import ROOT, THEME_FILE

#: A request file's name: the editor writes `<yyyy-mm-dd-hhmm>-<slug>.json`.
REQUEST_NAME = re.compile(r"^[a-z0-9][a-z0-9-]{0,80}\.json$")

#: A font file name, as `theme/theme.schema.json` allows it.
FONT_NAME = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,120}\.(woff2|woff|ttf|otf)$")

#: The files that carry a gold hex by hand. No generator writes them, so a
#: new gold reaches them here. CHANGING.md lists the same files.
CARRY_FILES = (
    "README.md",
    "pwa/install-prompt.js",
    "skills/oxagen-branding/references/system.md",
    "ui/src/components/brand-marks.generated.ts",
    "ui/src/components/global-error.tsx",
    "ui/src/components/stella-spinner.tsx",
    "ui/src/styles/globals.css",
    "sdlc/lib/pdf.js",
    "sdlc/og/og.html",
    "sdlc/public/google-docs.html",
    "sdlc/public/index.html",
    "sdlc/public/sdlc.css",
)

#: The gold ramp in `globals.css`: tints typed as `oklch()` on the gold's hue.
#: A new gold turns each one by the same number of degrees the gold moved.
RAMP = re.compile(
    r"(?P<head>--_amber-\d+:\s*oklch\(\s*)(?P<l>[\d.]+)(?P<s1>\s+)(?P<c>[\d.]+)(?P<s2>\s+)(?P<h>[\d.]+)(?P<tail>\s*\))"
)

GOOGLE_CSS = "https://fonts.googleapis.com/css2"
#: Google Fonts serves WOFF2 to a current browser, and TTF to a client it does not know.
WOFF2_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
)
TTF_AGENT = "curl/8.7.1"
GOOGLE_REPO = "https://api.github.com/repos/google/fonts/contents"
#: The licence directories of the google/fonts repository, and each one's licence file.
LICENCES = {"ofl": "OFL.txt", "apache": "LICENSE.txt", "ufl": "UFL.txt"}
#: Static file names in the google/fonts repository, by weight.
WEIGHT_NAMES = {
    100: "Thin", 200: "ExtraLight", 300: "Light", 400: "Regular", 500: "Medium",
    600: "SemiBold", 700: "Bold", 800: "ExtraBold", 900: "Black",
}


class ApplyError(Exception):
    """A request that cannot be applied. The message says what to do."""


# --------------------------------------------------------------------------
# paths
# --------------------------------------------------------------------------


def inside(path: Path, folder: Path) -> bool:
    try:
        path.resolve().relative_to(folder.resolve())
    except ValueError:
        return False
    return True


def request_path(arg: str, root: Path = ROOT) -> Path:
    """A request file the workflow may read: a plain JSON file directly in theme/requests/."""
    path = (root / arg) if not Path(arg).is_absolute() else Path(arg)
    folder = root / "theme" / "requests"
    if path.parent.resolve() != folder.resolve() or not REQUEST_NAME.match(path.name):
        raise ApplyError(f"{arg} is not a request. A request is theme/requests/<name>.json, in lowercase.")
    if path.is_symlink() or not path.is_file():
        raise ApplyError(f"{arg} is not a plain file in theme/requests/.")
    return path


def font_path(name: str, fonts_dir: Path) -> Path:
    """`fonts/<name>`, after checking the name cannot point anywhere else."""
    if not FONT_NAME.match(name):
        raise ApplyError(f"{name} is not a font file name: letters, digits, dots, dashes, and underscores, ending .woff2, .woff, .ttf, or .otf.")
    path = fonts_dir / name
    if not inside(path, fonts_dir) or path.is_symlink():
        raise ApplyError(f"fonts/{name} is a link or points outside fonts/.")
    return path


def slug(family: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", family.lower()).strip("-")


# --------------------------------------------------------------------------
# Google Fonts
# --------------------------------------------------------------------------


def http_get(url: str, agent: str = WOFF2_AGENT) -> bytes:
    headers = {"User-Agent": agent}
    token = os.environ.get("GITHUB_TOKEN")
    if token and url.startswith("https://api.github.com/"):
        headers["Authorization"] = f"Bearer {token}"
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=60) as resp:  # noqa: S310 - fixed https hosts
        return resp.read()


def parse_css(css: str) -> list[dict]:
    """Every @font-face in a Google Fonts stylesheet: subset, style, weight, and URL."""
    faces = []
    for subset, body in re.findall(r"(?:/\*\s*([a-z0-9-]+)\s*\*/\s*)?@font-face\s*\{([^}]*)\}", css):
        style = re.search(r"font-style:\s*(\w+)", body)
        weight = re.search(r"font-weight:\s*([0-9 ]+);", body)
        url = re.search(r"url\((https://fonts\.gstatic\.com/[^)\s]+)\)", body)
        if style and weight and url:
            faces.append(
                {"subset": subset or "all", "style": style.group(1), "weight": weight.group(1).strip(), "url": url.group(1)}
            )
    return faces


def google_stylesheet(family: str, weights: list[int], agent: str = WOFF2_AGENT) -> str:
    """The Google Fonts stylesheet for `family`: one variable range if the family has one, else each weight."""
    name = urllib.parse.quote_plus(family)
    lo, hi = min(weights), max(weights)
    tries = [f"wght@{lo}..{hi}"] if lo != hi else []
    tries.append("wght@" + ";".join(str(w) for w in sorted(set(weights))))
    last = ""
    for axis in tries:
        try:
            return http_get(f"{GOOGLE_CSS}?family={name}:{axis}&display=swap", agent).decode()
        except urllib.error.HTTPError as e:
            last = f"HTTP {e.code}"
    raise ApplyError(
        f"Google Fonts has no family named {family} at weights {', '.join(map(str, weights))} ({last}). "
        "Check the name on fonts.google.com, or choose weights the family has."
    )


def fetch_google_webfonts(family: str, weights: list[int], fonts_dir: Path) -> list[dict]:
    """Download the latin WOFF2 files and return the theme's `files` list."""
    faces = [f for f in parse_css(google_stylesheet(family, weights)) if f["subset"] == "latin" and f["style"] == "normal"]
    if not faces:
        raise ApplyError(f"Google Fonts serves no latin upright files for {family}.")
    urls = {f["url"] for f in faces}
    files: list[dict] = []
    if len(urls) == 1:
        # One file draws every weight: a variable font.
        lo = min(int(w) for f in faces for w in f["weight"].split())
        hi = max(int(w) for f in faces for w in f["weight"].split())
        name = f"{slug(family)}-latin-wght.woff2" if lo != hi else f"{slug(family)}-latin-{lo}.woff2"
        font_path(name, fonts_dir).write_bytes(http_get(faces[0]["url"]))
        files.append({"file": name, "weight": f"{lo} {hi}" if lo != hi else str(lo)})
    else:
        for f in sorted(faces, key=lambda f: int(f["weight"].split()[0])):
            name = f"{slug(family)}-latin-{f['weight'].split()[0]}.woff2"
            font_path(name, fonts_dir).write_bytes(http_get(f["url"]))
            files.append({"file": name, "weight": f["weight"]})
    return files


def google_listing(family: str) -> tuple[str, list[dict]]:
    """The family's directory in the google/fonts repository, and its licence directory."""
    folder = re.sub(r"[^a-z0-9]", "", family.lower())
    for kind in LICENCES:
        try:
            return kind, json.loads(http_get(f"{GOOGLE_REPO}/{kind}/{folder}"))
        except urllib.error.HTTPError as e:
            if e.code != 404:
                raise ApplyError(f"The google/fonts repository answered HTTP {e.code} for {family}. Run the workflow again.") from e
    raise ApplyError(f"The google/fonts repository has no folder for {family}, so its licence cannot be fetched.")


def fetch_google_licence(family: str, fonts_dir: Path, listing: tuple[str, list[dict]]) -> str:
    kind, entries = listing
    want = LICENCES[kind]
    entry = next((e for e in entries if e["name"] == want), None)
    if entry is None:
        raise ApplyError(f"google/fonts {kind}/{family} has no {want}.")
    name = f"LICENSE-{kind.upper()}-{slug(family)}.txt"
    path = fonts_dir / name
    if not inside(path, fonts_dir):
        raise ApplyError(f"{name} points outside fonts/.")
    path.write_bytes(http_get(entry["download_url"]))
    return name


def fetch_google_outline(family: str, weight: int, fonts_dir: Path, listing: tuple[str, list[dict]]) -> str:
    """A TTF to draw from: the family's variable TTF, else the static TTF at `weight`."""
    _, entries = listing
    ttfs = [e for e in entries if e["name"].endswith(".ttf") and "italic" not in e["name"].lower()]
    variable = [e for e in ttfs if "[" in e["name"] and "wght" in e["name"]]
    if variable:
        entry = min(variable, key=lambda e: len(e["name"]))
        axes = re.search(r"\[([^\]]+)\]", entry["name"]).group(1).replace(",", "-")  # type: ignore[union-attr]
        name = f"{family.replace(' ', '')}-VariableFont_{axes}.ttf"
        font_path(name, fonts_dir).write_bytes(http_get(entry["download_url"]))
        return name
    static = f"{family.replace(' ', '')}-{WEIGHT_NAMES[weight]}.ttf"
    entry = next((e for e in ttfs if e["name"].lower() == static.lower()), None)
    if entry is not None:
        font_path(static, fonts_dir).write_bytes(http_get(entry["download_url"]))
        return static
    faces = parse_css(google_stylesheet(family, [weight], TTF_AGENT))
    if not faces:
        raise ApplyError(f"Google Fonts serves no TTF for {family} at {weight}.")
    name = f"{slug(family)}-{weight}.ttf"
    font_path(name, fonts_dir).write_bytes(http_get(faces[0]["url"], TTF_AGENT))
    return name


# --------------------------------------------------------------------------
# uploaded and kit files
# --------------------------------------------------------------------------


def webfont(name: str, fonts_dir: Path) -> str:
    """The WOFF2 the web loads for `fonts/<name>`, written beside it when the file is another format."""
    from fontTools.ttLib import TTFont

    src = font_path(name, fonts_dir)
    try:
        font = TTFont(src)
    except Exception as e:  # noqa: BLE001 - fontTools raises many kinds for a bad file
        raise ApplyError(f"fonts/{name} is not a font file fontTools can read: {e}") from e
    if src.suffix.lower() == ".woff2":
        return name
    out = font_path(src.stem + ".woff2", fonts_dir)
    font.flavor = "woff2"
    font.save(out)
    return out.name


def local_files(role: str, face: dict, fonts_dir: Path) -> tuple[list[dict], list[str], list[str]]:
    """The theme's `files` for an upload or kit face, the files it read, and the files it wrote."""
    read, wrote, files = [], [], []
    missing = [f["file"] for f in face["files"] if not font_path(f["file"], fonts_dir).is_file()]
    if missing:
        where = "Upload them to fonts/ on this branch" if face["source"] == "upload" else "Add them to fonts/"
        raise ApplyError(
            f"faces.{role} names {', '.join('fonts/' + m for m in missing)}, which this branch does not have. "
            f"{where}, and the workflow runs again on the push."
        )
    for f in face["files"]:
        read.append(f["file"])
        web = webfont(f["file"], fonts_dir)
        if web != f["file"]:
            wrote.append(web)
        # An italic file keeps its style, so it loads as the italic of the family.
        files.append({"file": web, "weight": f["weight"], **({"style": f["style"]} if "style" in f else {})})
    return files, read, wrote


# --------------------------------------------------------------------------
# faces
# --------------------------------------------------------------------------


#: The weight the text role's outline is picked at when the request names no file.
TEXT_OUTLINE_WEIGHT = 400


def resolve_faces(theme: dict, request: dict, fonts_dir: Path, log: dict) -> dict[str, dict]:
    """The theme's face for each role the request names. Fetches and converts files as it goes."""
    out: dict[str, dict] = {}
    fetched: dict[str, dict] = {}
    google_weights: dict[str, set[int]] = {}
    for face in request.get("faces", {}).values():
        if face["source"] == "google":
            google_weights.setdefault(face["family"], set()).update(face["weights"])
    for role, face in request.get("faces", {}).items():
        if role not in R.REQUEST_ROLES:
            raise ApplyError(R.WORDMARK_REFUSED)
        current = theme["faces"][role]
        outline: dict | None = None
        if face["source"] == "google":
            family = face["family"]
            if family not in fetched:
                listing = google_listing(family)
                files = fetch_google_webfonts(family, sorted(google_weights[family]), fonts_dir)
                licence = fetch_google_licence(family, fonts_dir, listing)
                fetched[family] = {"files": files, "licence": licence, "listing": listing}
                log["fonts"].append({"family": family, "source": "Google Fonts", "files": [f["file"] for f in files], "licence": licence})
            files = fetched[family]["files"]
            if role in R.OUTLINE_ROLES:
                if "outline" not in fetched[family]:
                    fetched[family]["outline"] = fetch_google_outline(family, TEXT_OUTLINE_WEIGHT, fonts_dir, fetched[family]["listing"])
                    log["fonts"].append({"family": family, "source": "google/fonts", "files": [fetched[family]["outline"]], "licence": ""})
                outline = {"file": fetched[family]["outline"]}
        else:
            files, read, wrote = local_files(role, face, fonts_dir)
            log["fonts"].append({"family": face["family"], "source": face["source"], "files": read, "converted": wrote, "licence": ""})
            if role in R.OUTLINE_ROLES:
                if "file" in face.get("outline", {}):
                    name = face["outline"]["file"]
                    if not font_path(name, fonts_dir).is_file():
                        raise ApplyError(f"faces.{role}.outline names fonts/{name}, which this branch does not have.")
                elif face["family"] == current["family"] and "outline" in current:
                    name = current["outline"]["file"]
                else:
                    name = R.nearest(face["files"], TEXT_OUTLINE_WEIGHT)["file"]
                outline = {"file": name}
        out[role] = R.face_entry(role, current, face, files, outline)
    return out


# --------------------------------------------------------------------------
# the gold carry
# --------------------------------------------------------------------------


def golds(theme: dict) -> dict[str, str]:
    """The gold and its two neighbours for `theme`, derived as `build/color.py` derives them."""
    from color import hex_to_oklch, oklch_hex

    gold = theme["color"]["gold"]
    hue = float(round(hex_to_oklch(gold)[2]))
    b, d = theme["color"]["gold_bright"], theme["color"]["gold_deep"]
    return {
        "gold": gold,
        "gold-bright": oklch_hex(b["lightness"], b["chroma"], hue),
        "gold-deep": oklch_hex(d["lightness"], d["chroma"], hue),
    }


def gold_hue(theme: dict) -> int:
    from color import hex_to_oklch

    return round(hex_to_oklch(theme["color"]["gold"])[2])


def replace_hexes(text: str, mapping: dict[str, str]) -> str:
    """`text` with each old hex in `mapping` replaced by its new hex, in one pass."""
    mapping = {k.upper(): v for k, v in mapping.items() if k.upper() != v.upper()}
    if not mapping:
        return text
    pattern = re.compile("|".join(re.escape(k) for k in mapping), re.IGNORECASE)
    return pattern.sub(lambda m: mapping[m.group(0).upper()], text)


def turn_ramp(text: str, degrees: int) -> str:
    """`text` with every gold ramp tint turned by `degrees` of OKLCH hue."""
    if degrees % 360 == 0:
        return text

    def turn(m: re.Match) -> str:
        hue = (float(m.group("h")) + degrees) % 360
        shown = f"{hue:g}" if hue == int(hue) else f"{hue:.1f}"
        return f"{m.group('head')}{m.group('l')}{m.group('s1')}{m.group('c')}{m.group('s2')}{shown}{m.group('tail')}"

    return RAMP.sub(turn, text)


def carry_gold(before: dict, after: dict, root: Path = ROOT) -> list[str]:
    """Move the gold's hand copies from the old theme to the new. Returns the files changed."""
    mapping = {golds(before)[k]: v for k, v in golds(after).items()}
    degrees = gold_hue(after) - gold_hue(before)
    changed = []
    for rel in CARRY_FILES:
        path = root / rel
        if not path.is_file() or path.is_symlink():
            continue
        text = path.read_text()
        new = replace_hexes(text, mapping)
        if rel == "ui/src/styles/globals.css":
            new = turn_ramp(new, degrees)
        if new != text:
            path.write_text(new)
            changed.append(rel)
    return changed


# --------------------------------------------------------------------------
# the report
# --------------------------------------------------------------------------


def flatten(value: object, prefix: str = "") -> dict[str, object]:
    if isinstance(value, dict):
        out: dict[str, object] = {}
        for key, sub in value.items():
            if key == "$schema":
                continue
            out.update(flatten(sub, f"{prefix}.{key}" if prefix else key))
        return out
    return {prefix: value}


def changes(before: dict, after: dict) -> list[tuple[str, object, object]]:
    """Every field whose value differs, as (field, before, after)."""
    a, b = flatten(before), flatten(after)
    keys = list(b) + [k for k in a if k not in b]
    return [(k, a.get(k), b.get(k)) for k in keys if a.get(k) != b.get(k)]


def _cell(value: object) -> str:
    if value is None:
        return "none"
    text = value if isinstance(value, str) else json.dumps(value)
    return "`" + text.replace("|", "\\|").replace("`", "'") + "`"


def report(state: dict, pushed: bool = True, run_url: str = "") -> str:
    """The pull request comment, from the state `apply` wrote and the theme on disk.

    `pushed` says whether the workflow committed the result. When it did not,
    the generators or the check failed, and the comment says so.
    """
    lines = ["<!-- apply-theme -->", "## Theme request", ""]
    for req in state.get("requests", []):
        lines.append(f"- `{req['path']}`: {req['summary']}")
    lines.append("")
    if state.get("problems"):
        lines += ["The workflow did not apply the request, and the branch is unchanged.", ""]
        lines += [f"- {p}" for p in state["problems"]]
        lines += ["", "Fix the request or the files, and push to this branch. The workflow runs again."]
        return "\n".join(lines) + "\n"

    before = state["before"]
    after = json.loads(THEME_FILE.read_text())
    lines += ["### Changes", "", "| Field | Before | After |", "|---|---|---|"]
    rows = changes(before, after)
    lines += [f"| `{k}` | {_cell(old)} | {_cell(new)} |" for k, old, new in rows] or ["| none | | |"]

    import color as C

    old, new = golds(before), golds(after)
    lines += ["", "### Gold", "", "| Token | Before | After |", "|---|---|---|"]
    lines += [f"| {name} | `{old[name]}` | `{new[name]}` |" for name in new]

    problems = C.verify()
    lines += ["", "### Contrast", ""]
    if problems:
        lines += ["The build checks these and fails until each one clears:", ""]
        lines += [f"- {p}" for p in problems]
    else:
        lines.append("Every text token clears 4.5:1 on its ground, and every state mark clears 3:1.")
    quiet = [
        ("dim on ink", C.contrast(C.DIM, C.INK)),
        ("dim-ink on paper", C.contrast(C.DIM_INK, C.PAPER)),
    ]
    low = [f"{name} is {ratio:.2f}:1" for name, ratio in quiet if ratio < 4.5]
    if low:
        lines += ["", f"The quietest text sits below 4.5:1, which the build allows because it never carries meaning: {', '.join(low)}."]

    if state.get("fonts"):
        lines += ["", "### Fonts", "", "`fonts/README.md` lists the faces and their licences by hand. Add a row for a new face in this PR.", ""]
        for f in state["fonts"]:
            files = ", ".join(f"`fonts/{n}`" for n in f["files"])
            extra = f" Converted for the web: {', '.join('`fonts/' + n + '`' for n in f.get('converted', []))}." if f.get("converted") else ""
            licence = f" Licence: `fonts/{f['licence']}`." if f.get("licence") else ""
            lines.append(f"- {f['family']} from {f['source']}: {files}.{licence}{extra}")
    if state.get("carried"):
        lines += ["", "### Gold copies", "", "The new gold also reached the files no generator writes:", ""]
        lines += [f"- `{rel}`" for rel in state["carried"]]

    lines += ["", "### Next", ""]
    if pushed:
        lines.append(
            "The kit's checks run on the commit this workflow pushed. Review the change and its checks. "
            "Merging this PR deploys brand.oxagen.cloud and runs the fan-out, which opens a sync PR in every repo `consumers.json` lists."
        )
    else:
        log = f" Read the log: {run_url}" if run_url else ""
        lines.append(
            "The generators or `build/build.py --check` failed, so the workflow pushed nothing and the branch still holds the request. "
            f"Fix the request or the files, and push to this branch. The workflow runs again.{log}"
        )
    return "\n".join(lines) + "\n"


# --------------------------------------------------------------------------
# command line
# --------------------------------------------------------------------------


def apply(paths: list[str], state: dict, fonts_dir: Path = R.FONTS_DIR) -> None:
    """Apply the requests at `paths`, recording what happened in `state` for `report`."""
    import theme as TH

    before = json.loads(THEME_FILE.read_text())
    state.update({"before": before, "requests": [], "fonts": [], "carried": [], "problems": []})
    files = sorted((request_path(p) for p in paths), key=lambda p: p.name)
    requests = []
    for path in files:
        try:
            req = json.loads(path.read_text())
        except ValueError as e:
            raise ApplyError(f"{path.relative_to(ROOT)} is not valid JSON: {e}") from e
        found = R.problems(req)
        if found:
            raise ApplyError("; ".join(f"{path.relative_to(ROOT)}: {p}" for p in found))
        requests.append((path, req))
        state["requests"].append({"path": path.relative_to(ROOT).as_posix(), "summary": req["summary"]})

    theme = before
    for path, req in requests:
        faces = resolve_faces(theme, req, fonts_dir, state)
        theme = R.merge(theme, req, faces)
        found = TH.problems(theme)
        if found:
            raise ApplyError("; ".join(f"after {path.name}, theme/theme.json: {p}" for p in found))

    THEME_FILE.write_text(R.dump_theme(theme))
    state["carried"] = carry_gold(before, theme)
    for path, _ in requests:
        path.unlink()


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="command", required=True)
    a_apply = sub.add_parser("apply", help="apply theme requests to the kit")
    a_apply.add_argument("--state", type=Path, required=True)
    a_apply.add_argument("requests", nargs="+")
    a_report = sub.add_parser("report", help="write the pull request comment")
    a_report.add_argument("--state", type=Path, required=True)
    a_report.add_argument("--failed", action="store_true", help="the generators or the check failed")
    a_report.add_argument("--run-url", default="")
    a = ap.parse_args()

    state_file = a.state / "state.json"
    if a.command == "report":
        print(report(json.loads(state_file.read_text()), pushed=not a.failed, run_url=a.run_url))
        return 0
    a.state.mkdir(parents=True, exist_ok=True)
    state: dict = {"requests": [{"path": p, "summary": "not read"} for p in a.requests]}
    try:
        apply(a.requests, state)
    except (ApplyError, urllib.error.URLError, TimeoutError) as e:
        # A network failure is worth a comment too: running the workflow
        # again usually clears it.
        state["problems"] = [str(e) if isinstance(e, ApplyError) else f"A download failed ({e}). Run the workflow again."]
        state_file.write_text(json.dumps(state, indent=2))
        print(f"problem: {e}", file=sys.stderr)
        return 1
    state_file.write_text(json.dumps(state, indent=2))
    print(f"applied {len(state['requests'])} request(s) to theme/theme.json")
    return 0


if __name__ == "__main__":
    sys.exit(main())
