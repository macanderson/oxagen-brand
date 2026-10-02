"""Write the colour values the theme editor's tests compare against.

    python3 build/editor_fixture.py            # write the fixture
    python3 build/editor_fixture.py --check    # fail if the fixture is stale

The theme editor on the kit's example pages derives the gold's neighbours,
every state's text stop, the destructive red, and muted-text-ink in
TypeScript (`ui/src/theme-editor/color.ts`), so it previews a change before
any build runs. Its tests compare that port with the values `build/color.py`
computes for each theme in `CASES`, written to
`ui/src/theme-editor/python-colors.fixture.json`, and with the problems
`color.verify()` reports. CI's check job runs `--check`, so a change to the
colour maths here fails until the fixture, and then the port, follow it.
"""

from __future__ import annotations

import argparse
import copy
import importlib
import json
import sys

import theme as TH

FIXTURE = TH.ROOT / "ui" / "src" / "theme-editor" / "python-colors.fixture.json"

#: Each case changes the shipped colour section by these fields.
CASES: list[tuple[str, dict]] = [
    ("shipped", {}),
    ("deeper gold", {"gold": "#C99B2E"}),
    ("blue primary", {"gold": "#4F7CD9"}),
    ("dark gold", {"gold": "#7A5A10"}),
    ("neighbours moved", {"gold_bright": {"lightness": 0.9, "chroma": 0.15}, "gold_deep": {"lightness": 0.5, "chroma": 0.12}}),
    (
        "states moved",
        {
            "states": {"failed": {"ink": "#D04A40"}, "approval": {"paper": "#2A64A0"}},
            "destructive_lift_on_ink": 0.08,
            "state_text_lightness_on_ink": 0.7,
        },
    ),
    (
        "text moved",
        {
            "ink": {"hl": "#2E2E33"},
            "text_on_ink": {"muted": "#9A9AA3"},
            "text_on_paper": {"muted": "#737380", "muted_text_lightness": 0.5},
        },
    ),
]


def _merge(base: dict, change: dict) -> dict:
    out = copy.deepcopy(base)
    for key, value in change.items():
        out[key] = _merge(out[key], value) if isinstance(value, dict) else value
    return out


def _vars() -> dict[str, str]:
    """The colour tokens as `build/build.py` writes them into house-tokens.css."""
    import color as C

    out = {f"--ox-{name}": value for name, value, _ in C.TOKENS}
    for name, dark, light, _ in C.STATES:
        out[f"--ox-st-{name}"] = dark
        out[f"--ox-st-{name}-ink"] = light
    out["--ox-destructive"] = C.DESTRUCTIVE["dark"]
    out["--ox-destructive-ink"] = C.DESTRUCTIVE["light"]
    for name, text in C.STATE_TEXT.items():
        stem = name if name == "destructive" else f"st-{name}"
        out[f"--ox-{stem}-text"] = text["dark"]
        out[f"--ox-{stem}-text-ink"] = text["light"]
    out["--ox-gold-sheen"] = (
        f"linear-gradient(45deg, {C.GOLD_DEEP} 0%, {C.GOLD} 38%, {C.GOLD_BRIGHT} 56%, {C.GOLD} 74%, {C.GOLD_DEEP} 100%)"
    )
    return out


def fixture() -> dict:
    shipped = copy.deepcopy(TH.THEME["color"])
    cases = []
    try:
        for name, change in CASES:
            TH.THEME["color"] = _merge(shipped, change)
            import color as C

            importlib.reload(C)
            cases.append({"name": name, "color": TH.THEME["color"], "vars": _vars(), "problems": C.verify()})
    finally:
        TH.THEME["color"] = shipped
        import color as C

        importlib.reload(C)
    return {
        "_about": "Written by build/editor_fixture.py from build/color.py. Do not edit.",
        "cases": cases,
    }


def text() -> str:
    return json.dumps(fixture(), indent=2) + "\n"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args()
    if a.check:
        if not FIXTURE.is_file() or FIXTURE.read_text() != text():
            print(f"problem: {FIXTURE.relative_to(TH.ROOT)} is stale; run build/editor_fixture.py")
            return 1
        print(f"check: {FIXTURE.relative_to(TH.ROOT)} matches build/color.py")
        return 0
    FIXTURE.parent.mkdir(parents=True, exist_ok=True)
    FIXTURE.write_text(text())
    print(f"wrote {FIXTURE.relative_to(TH.ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
