"""Make the text and code webfonts from their upstream releases, and check every webfont the kit ships.

    .venv/bin/python build/fonts.py geist path/to/Geist[wght].woff2
    .venv/bin/python build/fonts.py mono  "path/to/Monaspace Neon Var.woff2"
    .venv/bin/python build/fonts.py --check

Space Grotesk is outlined at build time from the variable TTF in `fonts/`, and
its four static webfonts were instanced from it (see the git history of
`fonts/`).

Aeonik ships as CoType Foundry delivered it: four variable WOFF2 files, each on
one weight axis from 100 to 900, copied into `fonts/` unchanged. It was the
house sans from 2026-10-02 to 2026-10-03, when Mac set Geist back. All four
load, and no role takes them. This script does not make them.

    fonts/aeonik-wght.woff2         Aeonik, upright: loads, and no role takes it
    fonts/aeonik-italic-wght.woff2  Aeonik, italic: the same family, font-style italic
    fonts/aeonik-mono-wght.woff2    Aeonik Mono: loads, and no role takes it yet
    fonts/aeonik-fono-wght.woff2    Aeonik Fono: loads, and no role takes it yet

Each file names itself with a " VF" suffix ("Aeonik VF"). The CSS asks for the
family the theme names ("Aeonik"), and the @font-face rule binds that name to
the file, so the suffix never reaches a page.

Geist and Monaspace Neon ship as one variable file each, subset to the latin
codepoints the Space Grotesk webfonts carry, with the weight axis kept:

    fonts/geist-latin-wght.woff2           Geist, wght 100 to 900: every heading
                                           and line of text
    fonts/monaspace-neon-latin-wght.woff2  Monaspace Neon, wght 200 to 800,
                                           width pinned at 100, upright

The width and slant axes are pinned because the house uses neither: one
variable file with three axes is 500 KB, and the same face on one axis is a
tenth of that. Texture healing (`calt`) and the code ligatures (`liga`) survive
the subset; the CSS turns them on.

The releases are not tracked. `--check` reads every file back and fails if one
has drifted: the family name it carries, its axes, upright or italic, the
codepoints it must cover, and the features the CSS relies on.
"""

from __future__ import annotations

import argparse
import sys
import unicodedata
from io import BytesIO
from pathlib import Path

from fontTools import subset
from fontTools.ttLib import TTFont
from fontTools.varLib import instancer

ROOT = Path(__file__).resolve().parent.parent
FONTS = ROOT / "fonts"

#: The codepoints every webfont in the kit covers: whatever the Space Grotesk
#: subset already carries, so the faces agree on what they can set.
REFERENCE_SUBSET = FONTS / "space-grotesk-latin-400.woff2"

#: The OpenType features the subset keeps. `calt` is Monaspace's texture
#: healing; `liga` the code ligatures; the rest are the ordinary text features
#: Geist ships with and the numerals the tables need.
FEATURES = ["calt", "liga", "kern", "ccmp", "locl", "case", "tnum", "pnum", "frac", "dnom", "numr", "sups", "subs", "ordn"]

#: The faces this script makes from an upstream release.
FACES: dict[str, dict] = {
    "geist": {
        "out": "geist-latin-wght.woff2",
        "family": "Geist",
        "axes": {"wght": (100, 900)},
        "pin": {},
    },
    "mono": {
        "out": "monaspace-neon-latin-wght.woff2",
        "family": "Monaspace Neon",
        "axes": {"wght": (200, 800)},
        "pin": {"wdth": 100, "slnt": 0},
    },
}


#: Codepoints in the Space Grotesk subset that Geist, Monaspace Neon, and Aeonik
#: do not draw: the division slash and the okina. Not required of them.
NOT_UPSTREAM = {0x2215, 0x02BB}

#: Codepoints in the Space Grotesk subset that Aeonik does not draw: the
#: modifier letter apostrophe, the prime, and the double prime. A browser takes
#: them from the fallback stack.
NOT_IN_AEONIK = {0x02BC, 0x2032, 0x2033}

#: Every webfont `--check` guards, by file: the family name the file carries,
#: its axes, whether it is italic (None leaves the flag unchecked), the GSUB
#: features the CSS relies on, the required codepoints it may lack, and how to
#: put it back when it is missing.
CHECKS: dict[str, dict] = {
    FACES["geist"]["out"]: {
        "family": FACES["geist"]["family"], "axes": FACES["geist"]["axes"], "italic": None,
        "features": ("liga",), "lacks": set(), "restore": "run build/fonts.py geist <release file>",
    },
    "aeonik-wght.woff2": {
        "family": "Aeonik VF", "axes": {"wght": (100, 900)}, "italic": False,
        "features": ("liga",), "lacks": NOT_IN_AEONIK, "restore": "copy aeonikvf.woff2 from the CoType release",
    },
    "aeonik-italic-wght.woff2": {
        "family": "Aeonik VF", "axes": {"wght": (100, 900)}, "italic": True,
        "features": ("liga",), "lacks": NOT_IN_AEONIK, "restore": "copy aeonikvf-italic.woff2 from the CoType release",
    },
    "aeonik-mono-wght.woff2": {
        "family": "Aeonik Mono VF", "axes": {"wght": (100, 900)}, "italic": False,
        "features": (), "lacks": NOT_IN_AEONIK, "restore": "copy aeonikmonovf.woff2 from the CoType release",
    },
    "aeonik-fono-wght.woff2": {
        "family": "Aeonik Fono VF", "axes": {"wght": (100, 900)}, "italic": False,
        "features": (), "lacks": NOT_IN_AEONIK, "restore": "copy aeonikfonovf.woff2 from the CoType release",
    },
    FACES["mono"]["out"]: {
        "family": FACES["mono"]["family"], "axes": FACES["mono"]["axes"], "italic": None,
        "features": ("calt", "liga"), "lacks": set(), "restore": "run build/fonts.py mono <release file>",
    },
}


def reference_codepoints() -> set[int]:
    return set(TTFont(REFERENCE_SUBSET).getBestCmap())


def required_codepoints() -> set[int]:
    """The reference set less format characters and the two glyphs above."""
    return {
        c
        for c in reference_codepoints()
        if (c == 0x20 or unicodedata.category(chr(c))[0] in "LNPS") and c not in NOT_UPSTREAM
    }


def make(face: str, src: Path) -> Path:
    spec = FACES[face]
    font = TTFont(src)
    axes = {tag: a for tag, a in spec["axes"].items()}
    axes.update(spec["pin"])
    if axes:
        font = instancer.instantiateVariableFont(font, axes, inplace=False, updateFontNames=False)
        # Round-trip through bytes: the instancer leaves gvar as a lazy table
        # with no entry for a glyph that never varied, and the subsetter walks
        # every glyph.
        buf = BytesIO()
        font.save(buf)
        buf.seek(0)
        font = TTFont(buf, lazy=False)

    opts = subset.Options()
    opts.flavor = "woff2"
    opts.layout_features = FEATURES
    opts.name_IDs = ["*"]
    opts.name_legacy = True
    opts.notdef_outline = True
    opts.glyph_names = False
    sub = subset.Subsetter(options=opts)
    sub.populate(unicodes=reference_codepoints())
    sub.subset(font)

    # One family name, so the CSS asks for what the file says it is.
    for rec in font["name"].names:
        if rec.nameID in (1, 4, 16):
            rec.string = spec["family"]
        if rec.nameID == 6:
            rec.string = spec["family"].replace(" ", "") + "-Variable"

    out = FONTS / spec["out"]
    font.save(out)
    return out


def check() -> list[str]:
    """Every fact the webfonts must hold. Returns the problems found."""
    problems = []
    want = required_codepoints()
    for name, spec in CHECKS.items():
        p = FONTS / name
        if not p.exists():
            problems.append(f"{p.relative_to(ROOT)} is missing; {spec['restore']}")
            continue
        f = TTFont(p)
        family = f["name"].getDebugName(1)
        if family != spec["family"]:
            problems.append(f"{name}: family is {family!r}, not {spec['family']!r}")
        axes = {a.axisTag: (a.minValue, a.maxValue) for a in f["fvar"].axes} if "fvar" in f else {}
        if axes != {k: tuple(map(float, v)) for k, v in spec["axes"].items()}:
            problems.append(f"{name}: axes are {axes}, not {spec['axes']}")
        if spec["italic"] is not None and bool(f["OS/2"].fsSelection & 1) != spec["italic"]:
            problems.append(f"{name}: the file is {'not ' if spec['italic'] else ''}italic, and the theme loads it as {'italic' if spec['italic'] else 'upright'}")
        missing = want - spec["lacks"] - set(f.getBestCmap())
        if missing:
            shown = ", ".join(f"U+{c:04X}" for c in sorted(missing)[:8])
            problems.append(f"{name}: {len(missing)} codepoints missing from the latin subset ({shown})")
        feats = {fr.FeatureTag for fr in f["GSUB"].table.FeatureList.FeatureRecord} if "GSUB" in f else set()
        for tag in spec["features"]:
            if tag not in feats:
                problems.append(f"{name}: {tag} is not in the file")
    return problems


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("face", nargs="?", choices=sorted(FACES))
    ap.add_argument("src", nargs="?", type=Path)
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args()
    if a.check:
        problems = check()
        for p in problems:
            print("fonts:", p, file=sys.stderr)
        print("fonts: ok" if not problems else f"fonts: {len(problems)} problem(s)")
        return 1 if problems else 0
    if not (a.face and a.src):
        ap.error("give a face and its release file, or --check")
    out = make(a.face, a.src)
    print(f"wrote {out.relative_to(ROOT)} ({out.stat().st_size // 1024} KB)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
