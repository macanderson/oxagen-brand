"""Check every Oxagen surface against the house system, and report what differs.

    python3 build/conformance.py                      # every repo and surface in consumers.json
    python3 build/conformance.py --report out.md      # also write the report as Markdown
    python3 build/conformance.py --only oxagen-gtm    # one repo and its surfaces

`consumers.json` lists every repo that ships Oxagen or Stella and every live
surface it serves. For each repo this checks, on its default branch, that:

- `.claude/skills/oxagen-branding/SKILL.md` is the stub in `skills/stub/`,
  byte for byte, so its agents read the brand from main.
- `.github/workflows/brand-drift.yml` exists, so its CI fails when its copies
  of the kit fall behind.

It reads each repo through the GitHub contents API. The consumers are public,
so the check runs without a token. With `BRAND_SYNC_TOKEN` (or `GITHUB_TOKEN`)
set, it reads with that token, which raises the API rate limit and reads a
consumer that turns private. A repo the check cannot read is a defect that
names the token, so a missing token never reads as a missing stub.

For each live surface it fetches the listed pages and the stylesheets they
link, and checks that:

- each linked icon is a kit file (from `icons/` or `logo/svg/`, by sha256), or
  an SVG that carries a live kit mark (`data-mark="hive"`); a raster that is
  not a kit file is noted, not failed, because a render differs byte for byte;
- no gold, amber, or yellow is served that is not a house value: a token, or
  a value the kit's `ui/src/styles/globals.css` authors (its gold ramp);
- every declared font family is a house face or a system fallback;
- the visible text carries no retired registry line, no em dash, and no
  exclamation point (text inside `code` and `pre` is skipped).

It exits 1 when any check fails. A page rendered only in the browser shows
little text to a plain fetch, so the text checks see only what the server
sends. Standard library only, plus `build/color.py`.
"""

from __future__ import annotations

import argparse
import hashlib
import html
import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass, field
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import color as C  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
CONSUMERS = ROOT / "consumers.json"
STUB = ROOT / "skills" / "stub" / "oxagen-branding" / "SKILL.md"
TOKENS = ROOT / "tokens" / "house-tokens.json"
KIT_CSS = ROOT / "ui" / "src" / "styles" / "globals.css"
INDEX = ROOT / "messages" / "index.json"
ICONS = ROOT / "icons"
MARKS = ROOT / "logo" / "svg"
#: How the kit's live marks name themselves: the hive carries data-mark="hive",
#: and stella's asterisk is labelled "stella mark". A retired mark carries neither.
LIVE_MARKS = re.compile(rb'data-mark="hive"|aria-label="stella mark"')

UA = "oxagen-brand-conformance/1 (+https://github.com/macanderson/oxagen-brand)"
MAX_BYTES = 5 * 1024 * 1024
MAX_SHEETS = 12

#: Substrings that mark a house face, including the names next/font generates
#: from the loaders in tokens/next-fonts.ts (for example `__spaceGrotesk_1a2b3c`).
HOUSE_FACES = ("space grotesk", "grotesk", "geist", "monaspace")
#: Generic families and the system stacks Tailwind and the kit fall back to.
SYSTEM_FACES = {
    "serif", "sans-serif", "monospace", "cursive", "fantasy", "system-ui", "ui-sans-serif", "ui-serif",
    "ui-monospace", "ui-rounded", "emoji", "math", "fangsong", "-apple-system", "blinkmacsystemfont",
    "segoe ui", "roboto", "helvetica", "helvetica neue", "arial", "noto sans", "ubuntu", "cantarell",
    "oxygen", "fira sans", "droid sans", "apple color emoji", "segoe ui emoji", "segoe ui symbol",
    "noto color emoji", "sfmono-regular", "sf mono", "menlo", "monaco", "consolas", "liberation mono",
    "courier new", "courier", "inherit", "initial", "unset", "revert", "revert-layer",
}

HEX = re.compile(r"#([0-9a-fA-F]{6}|[0-9a-fA-F]{3})\b")
RGB = re.compile(r"rgba?\(\s*(\d{1,3})[\s,]+(\d{1,3})[\s,]+(\d{1,3})")
OKLCH = re.compile(r"oklch\(\s*([\d.]+)(%?)\s+([\d.]+)\s+([\d.]+)")
FONT_FAMILY = re.compile(r"font-family\s*:\s*([^;}{]+)", re.I)
LINK = re.compile(r"<link\b[^>]*>", re.I)
ATTR = re.compile(r'(\w[\w-]*)\s*=\s*("[^"]*"|\'[^\']*\'|[^\s>]+)')
STYLE_BLOCK = re.compile(r"<style\b[^>]*>(.*?)</style>", re.I | re.S)
SKIP_BLOCKS = re.compile(r"<(script|style|code|pre|noscript|svg|template)\b.*?</\1>", re.I | re.S)
TAG = re.compile(r"<[^>]+>")


@dataclass
class Result:
    name: str
    defects: list[str] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)


def fetch(url: str, headers: dict[str, str] | None = None) -> tuple[int, bytes]:
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "*/*", **(headers or {})})
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            return r.status, r.read(MAX_BYTES)
    except urllib.error.HTTPError as e:
        return e.code, b""
    except (urllib.error.URLError, TimeoutError, OSError) as e:
        return 0, str(e).encode()


#: The variables a token is read from, in order. The fan-out's BRAND_SYNC_TOKEN
#: reaches every consumer. GITHUB_TOKEN is for a run by hand.
TOKEN_VARS = ("BRAND_SYNC_TOKEN", "GITHUB_TOKEN")


def token() -> str:
    return next((os.environ[v] for v in TOKEN_VARS if os.environ.get(v)), "")


def github(repo: str, path: str = "") -> tuple[int, bytes]:
    """GET a repo, or one file's raw bytes on its default branch, from the GitHub API."""
    headers = {"Accept": "application/vnd.github.raw+json", "X-GitHub-Api-Version": "2022-11-28"}
    if tok := token():
        headers["Authorization"] = f"Bearer {tok}"
    url = f"https://api.github.com/repos/{repo}"
    if path:
        url += "/contents/" + urllib.parse.quote(path)
    return fetch(url, headers)


# --------------------------------------------------------------------------
# the kit
# --------------------------------------------------------------------------


def palette() -> set[str]:
    """Every hex value in the token file and the kit's stylesheet, upper case, six digits."""
    found: set[str] = set()

    def walk(v):
        if isinstance(v, dict):
            for x in v.values():
                walk(x)
        elif isinstance(v, list):
            for x in v:
                walk(x)
        elif isinstance(v, str):
            for m in HEX.finditer(v):
                found.add(norm_hex(m.group(1)))

    walk(json.loads(TOKENS.read_text()))
    # The kit's stylesheet derives a few pairs the token file does not list.
    if KIT_CSS.exists():
        walk(KIT_CSS.read_text())
    return found


def kit_oklch() -> list[tuple[float, float, float]]:
    """The OKLCH values the kit's stylesheet authors directly, such as its gold ramp."""
    if not KIT_CSS.exists():
        return []
    out = []
    for m in OKLCH.finditer(KIT_CSS.read_text()):
        L = float(m.group(1)) / (100 if m.group(2) else 1)
        out.append((L, float(m.group(3)), float(m.group(4))))
    return out


def icon_hashes() -> dict[str, str]:
    files = [p for d in (ICONS, MARKS) for p in d.iterdir() if p.is_file()]
    return {hashlib.sha256(p.read_bytes()).hexdigest(): p.name for p in files}


def retired_lines() -> list[tuple[str, str]]:
    out = []
    for e in json.loads(INDEX.read_text())["entries"]:
        if e.get("status") != "retired":
            continue
        for key in ("title", "long"):
            text = squash(e.get(key) or "")
            if len(text) >= 30:
                out.append((e["id"], text[:60]))
    return out


# --------------------------------------------------------------------------
# colour
# --------------------------------------------------------------------------


def norm_hex(h: str) -> str:
    h = h.lstrip("#").upper()
    return "#" + ("".join(c * 2 for c in h) if len(h) == 3 else h)


def goldish(L: float, Ch: float, H: float) -> bool:
    """A gold, amber, or yellow: warm hue, enough chroma to read as colour."""
    return 60 <= H <= 105 and Ch >= 0.08 and 0.45 <= L <= 0.93


def near(a: tuple[float, float, float], b: tuple[float, float, float]) -> bool:
    return abs(a[0] - b[0]) < 0.012 and abs(a[1] - b[1]) < 0.012 and abs(a[2] - b[2]) < 2.5


def off_palette_golds(css: str, house: set[str], house_lch: list[tuple[float, float, float]]) -> set[str]:
    bad: set[str] = set()
    for m in HEX.finditer(css):
        h = norm_hex(m.group(1))
        lch = C.hex_to_oklch(h)
        if h not in house and goldish(*lch) and not any(near(lch, p) for p in house_lch):
            bad.add(h)
    for m in RGB.finditer(css):
        r, g, b = (min(255, int(x)) for x in m.groups())
        h = f"#{r:02X}{g:02X}{b:02X}"
        lch = C.hex_to_oklch(h)
        if h not in house and goldish(*lch) and not any(near(lch, p) for p in house_lch):
            bad.add(f"rgb({r}, {g}, {b})")
    for m in OKLCH.finditer(css):
        L = float(m.group(1)) / (100 if m.group(2) else 1)
        lch = (L, float(m.group(3)), float(m.group(4)))
        if goldish(*lch) and not any(near(lch, p) for p in house_lch):
            bad.add(f"oklch({m.group(1)}{m.group(2)} {m.group(3)} {m.group(4)})")
    return bad


# --------------------------------------------------------------------------
# type and text
# --------------------------------------------------------------------------


def foreign_faces(css: str, allow: set[str]) -> set[str]:
    bad = set()
    for m in FONT_FAMILY.finditer(css):
        # var(--x, fallback) leaves "var(--x" and "fallback)" once split on commas.
        for name in m.group(1).replace(")", "").split(","):
            face = name.strip().strip("\"'").strip()
            low = face.lower()
            if not re.search(r"[a-z]", low) or low.startswith("var(") or low in SYSTEM_FACES or low in allow:
                continue
            if any(h in low for h in HOUSE_FACES):
                continue
            bad.add(face)
    return bad


def squash(text: str) -> str:
    text = text.replace("’", "'").replace("‘", "'").replace("“", '"').replace("”", '"')
    return re.sub(r"\s+", " ", text).strip().lower()


def visible_text(page: str) -> str:
    return html.unescape(re.sub(r"\s+", " ", TAG.sub(" ", SKIP_BLOCKS.sub(" ", page))))


# --------------------------------------------------------------------------
# checks
# --------------------------------------------------------------------------


def links(page: str, base: str) -> tuple[list[str], list[str]]:
    """(stylesheet URLs, icon URLs) linked from a page, resolved against base."""
    sheets, icons = [], []
    for tag in LINK.findall(page):
        attrs = {k.lower(): v.strip("\"'") for k, v in ATTR.findall(tag)}
        rel, href = attrs.get("rel", "").lower(), attrs.get("href")
        if not href:
            continue
        url = urllib.parse.urljoin(base, html.unescape(href))
        if "stylesheet" in rel:
            sheets.append(url)
        elif "icon" in rel:
            icons.append(url)
    return sheets, icons


def check_repo(repo: str, stub: bytes) -> Result:
    r = Result(repo)
    # The contents API answers 404 both for a missing file and for a private repo
    # the caller cannot see. Asking for the repo first tells the two apart.
    status, _ = github(repo)
    if status == 404 and token():
        r.defects.append(f"the token cannot read {repo}; give BRAND_SYNC_TOKEN read access to it")
        return r
    if status == 404:
        r.defects.append(f"{repo} is private or missing, and no token is set; set BRAND_SYNC_TOKEN so the check can read it")
        return r
    if status == 401:
        r.defects.append("GitHub refused the token (HTTP 401); replace BRAND_SYNC_TOKEN")
        return r
    if status != 200:
        r.defects.append(f"the GitHub API returned {status or 'no response'} for {repo}")
        return r
    status, body = github(repo, ".claude/skills/oxagen-branding/SKILL.md")
    if status == 404:
        r.defects.append("no stub skill at .claude/skills/oxagen-branding/SKILL.md on the default branch")
    elif status != 200:
        r.defects.append(f"reading .claude/skills/oxagen-branding/SKILL.md returned {status or 'no response'}")
    elif body != stub:
        r.defects.append(".claude/skills/oxagen-branding/SKILL.md is not the current stub; run skills/install.sh --project")
    status, _ = github(repo, ".github/workflows/brand-drift.yml")
    if status == 404:
        r.defects.append("no .github/workflows/brand-drift.yml on the default branch")
    elif status != 200:
        r.defects.append(f"reading .github/workflows/brand-drift.yml returned {status or 'no response'}")
    return r


def check_surface(surface: dict, house: set[str], house_lch, icons: dict[str, str], retired) -> Result:
    base = surface["url"].rstrip("/")
    r = Result(base)
    allow = {f.lower() for f in surface.get("allow_fonts", [])}
    css_all, text_all, sheets_seen, icon_urls = [], [], set(), []
    for path in surface.get("pages", ["/"]):
        url = base + path
        status, body = fetch(url)
        if status != 200:
            r.defects.append(f"{url} returned {status or 'no response'}")
            continue
        page = body.decode("utf-8", "replace")
        css_all.append("\n".join(STYLE_BLOCK.findall(page)))
        css_all.append(" ".join(re.findall(r'style="([^"]*)"', page)))
        text = visible_text(page)
        text_all.append((url, text))
        sheets, found_icons = links(page, url)
        icon_urls += found_icons
        for sheet in sheets[:MAX_SHEETS]:
            if sheet in sheets_seen:
                continue
            sheets_seen.add(sheet)
            s_status, s_body = fetch(sheet)
            if s_status == 200:
                css_all.append(s_body.decode("utf-8", "replace"))
            else:
                r.notes.append(f"stylesheet {sheet} returned {s_status or 'no response'}")

    css = "\n".join(css_all)
    for value in sorted(off_palette_golds(css, house, house_lch)):
        r.defects.append(f"serves the off-palette gold {value}")
    for face in sorted(foreign_faces(css, allow)):
        r.defects.append(f"declares the font family {face!r}, which is not a house face")

    if not icon_urls:
        icon_urls = [base + "/favicon.ico"]
    for url in dict.fromkeys(icon_urls):
        status, body = fetch(url)
        if status != 200:
            r.defects.append(f"icon {url} returned {status or 'no response'}")
        elif hashlib.sha256(body).hexdigest() in icons:
            continue
        elif body.lstrip().startswith((b"<svg", b"<?xml")):
            if not LIVE_MARKS.search(body):
                r.defects.append(f"icon {url} is an SVG that carries no live kit mark")
        else:
            # A raster rendered from a kit SVG differs byte for byte from the kit's
            # own render, so a hash cannot settle it. The repo's drift check does.
            r.notes.append(f"icon {url} is a raster that is not a kit file byte for byte")

    for url, text in text_all:
        low = squash(text)
        if len(low) < 200:
            r.notes.append(f"{url} sends little text to a plain fetch; the text checks saw {len(low)} characters")
        for entry, line in retired:
            if line in low:
                r.defects.append(f"{url} shows the retired line {entry}")
        dashes, bangs = text.count("—"), len(re.findall(r"\w!(?=\s|$)", text))
        if dashes:
            r.defects.append(f"{url} shows {dashes} em dashes")
        if bangs:
            r.defects.append(f"{url} shows {bangs} exclamation points")
    return r


def report(results: list[Result]) -> str:
    failed = [r for r in results if r.defects]
    out = ["# Brand conformance", ""]
    out.append(f"{len(results) - len(failed)} of {len(results)} repos and surfaces conform to the kit at this commit.")
    out.append("")
    out.append("| Repo or surface | Result | Defects |")
    out.append("|---|---|---|")
    for r in results:
        out.append(f"| {r.name} | {'conforms' if not r.defects else 'differs'} | {len(r.defects)} |")
    for r in results:
        if not r.defects and not r.notes:
            continue
        out += ["", f"## {r.name}", ""]
        out += [f"- {d}" for d in r.defects]
        out += [f"- note: {n}" for n in r.notes]
    return "\n".join(out) + "\n"


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--report", type=Path, help="also write the report as Markdown to this path")
    ap.add_argument("--only", help="check one repo (its name or owner/name) and its surfaces")
    args = ap.parse_args()

    listing = json.loads(CONSUMERS.read_text())
    house = palette()
    house_lch = [C.hex_to_oklch(h) for h in house] + kit_oklch()
    icons, retired, stub = icon_hashes(), retired_lines(), STUB.read_bytes()

    results: list[Result] = []
    for consumer in listing["consumers"]:
        repo = consumer["repo"]
        if args.only and args.only not in (repo, repo.split("/")[-1]):
            continue
        results.append(check_repo(repo, stub))
        for surface in consumer.get("surfaces", []):
            results.append(check_surface(surface, house, house_lch, icons, retired))
    if not args.only:
        for surface in listing.get("kit", {}).get("surfaces", []):
            results.append(check_surface(surface, house, house_lch, icons, retired))

    text = report(results)
    print(text)
    if args.report:
        args.report.write_text(text)
    if any(r.defects for r in results):
        sys.exit(1)


if __name__ == "__main__":
    main()
