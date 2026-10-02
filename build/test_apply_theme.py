"""Tests for build/apply_theme.py: paths, Google Fonts parsing, uploads, the gold carry, and the report.

    python3 -m unittest discover -s build -p "test_*.py"

Nothing here reaches the network. The apply-theme workflow's proof run
covers the fetches. The wordmark test shapes with `hb-shape`, which the
`check` job installs.
"""

from __future__ import annotations

import json
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
import uuid
from pathlib import Path

import apply_theme as A
import color as C
import request as R
from theme import ROOT, THEME_FILE, WORDMARK_FIXED

CSS = """/* latin-ext */
@font-face {
  font-family: 'Inter';
  font-style: normal;
  font-weight: 400 700;
  font-display: swap;
  src: url(https://fonts.gstatic.com/s/inter/v20/ext.woff2) format('woff2');
}
/* latin */
@font-face {
  font-family: 'Inter';
  font-style: normal;
  font-weight: 400 700;
  font-display: swap;
  src: url(https://fonts.gstatic.com/s/inter/v20/latin.woff2) format('woff2');
}
/* latin */
@font-face {
  font-family: 'Inter';
  font-style: italic;
  font-weight: 400;
  src: url(https://fonts.gstatic.com/s/inter/v20/italic.woff2) format('woff2');
}
"""

TTF_CSS = """@font-face {
  font-family: 'Inter';
  font-style: normal;
  font-weight: 600;
  src: url(https://fonts.gstatic.com/s/inter/v20/static.ttf) format('truetype');
}
"""


def theme() -> dict:
    return json.loads(THEME_FILE.read_text())


def other(value: str, *choices: str) -> str:
    """The first of `choices` that differs from `value`, so a test changes the theme whatever it holds."""
    return next(c for c in choices if c != value)


class Scratch(unittest.TestCase):
    def setUp(self) -> None:
        self.root = Path(tempfile.mkdtemp())
        self.fonts = self.root / "fonts"
        self.fonts.mkdir()
        (self.root / "theme" / "requests").mkdir(parents=True)

    def tearDown(self) -> None:
        shutil.rmtree(self.root)


class PathTest(Scratch):
    def test_a_request_is_a_plain_json_file_in_theme_requests(self) -> None:
        good = self.root / "theme" / "requests" / "2026-10-01-1405-warm-gold.json"
        good.write_text("{}")
        self.assertEqual(A.request_path("theme/requests/2026-10-01-1405-warm-gold.json", self.root), good)
        for bad in ("theme/theme.json", "theme/requests/Upper.json", "theme/requests/../theme.json", "fonts/x.json"):
            with self.assertRaises(A.ApplyError, msg=bad):
                A.request_path(bad, self.root)

    def test_a_linked_request_is_refused(self) -> None:
        target = self.root / "secret.json"
        target.write_text("{}")
        (self.root / "theme" / "requests" / "link.json").symlink_to(target)
        with self.assertRaises(A.ApplyError):
            A.request_path("theme/requests/link.json", self.root)

    def test_a_font_name_stays_in_fonts(self) -> None:
        self.assertEqual(A.font_path("Aeonik-Regular.otf", self.fonts), self.fonts / "Aeonik-Regular.otf")
        for bad in ("../x.woff2", "a/b.woff2", ".x.woff2", "x.svg"):
            with self.assertRaises(A.ApplyError, msg=bad):
                A.font_path(bad, self.fonts)

    def test_slug(self) -> None:
        self.assertEqual(A.slug("IBM Plex Sans"), "ibm-plex-sans")


class GoogleCssTest(unittest.TestCase):
    def test_parse_keeps_subset_style_weight_and_url(self) -> None:
        faces = A.parse_css(CSS)
        latin = [f for f in faces if f["subset"] == "latin" and f["style"] == "normal"]
        self.assertEqual(latin, [{"subset": "latin", "style": "normal", "weight": "400 700", "url": "https://fonts.gstatic.com/s/inter/v20/latin.woff2"}])
        self.assertEqual(len(faces), 3)

    def test_parse_reads_a_stylesheet_with_no_subset_comments(self) -> None:
        faces = A.parse_css(TTF_CSS)
        self.assertEqual(faces[0]["subset"], "all")
        self.assertTrue(faces[0]["url"].endswith(".ttf"))

    def test_parse_ignores_a_url_on_another_host(self) -> None:
        self.assertEqual(A.parse_css(CSS.replace("fonts.gstatic.com", "example.com")), [])


class UploadTest(Scratch):
    def test_an_upload_gets_a_woff2_copy_and_keeps_its_original_for_the_outline(self) -> None:
        shutil.copy(ROOT / "fonts" / "SpaceGrotesk-VariableFont_wght.ttf", self.fonts / "Brand-Variable.ttf")
        req = {
            "summary": "Upload",
            "faces": {"sans": {"family": "Brand", "source": "upload", "files": [{"file": "Brand-Variable.ttf", "weight": "300 700"}]}},
        }
        self.assertEqual(R.problems(req), [])
        log: dict = {"fonts": []}
        faces = A.resolve_faces(theme(), req, self.fonts, log)
        face = faces["sans"]
        self.assertEqual(face["source"], "kit")
        self.assertEqual(face["files"], [{"file": "Brand-Variable.woff2", "weight": "300 700"}])
        self.assertEqual(face["outline"], {"file": "Brand-Variable.ttf"})
        self.assertEqual(face["fallback"], R.DEFAULT_FALLBACK["sans"])
        self.assertTrue((self.fonts / "Brand-Variable.woff2").is_file())
        self.assertEqual(log["fonts"][0]["converted"], ["Brand-Variable.woff2"])

    def test_an_italic_file_keeps_its_style_and_is_never_the_outline(self) -> None:
        for name in ("aeonik-wght.woff2", "aeonik-italic-wght.woff2"):
            shutil.copy(ROOT / "fonts" / name, self.fonts / name)
        files = [
            {"file": "aeonik-italic-wght.woff2", "weight": "100 900", "style": "italic"},
            {"file": "aeonik-wght.woff2", "weight": "100 900"},
        ]
        req = {"summary": "Kit face", "faces": {"sans": {"family": "Brand Sans", "source": "kit", "files": files}}}
        self.assertEqual(R.problems(req), [])
        face = A.resolve_faces(theme(), req, self.fonts, {"fonts": []})["sans"]
        self.assertEqual(face["files"], files)
        self.assertEqual(face["outline"], {"file": "aeonik-wght.woff2"})

    def test_resolving_a_wordmark_face_is_refused(self) -> None:
        shutil.copy(ROOT / "fonts" / "SpaceGrotesk-VariableFont_wght.ttf", self.fonts / "Brand-Variable.ttf")
        req = {
            "summary": "Upload",
            "faces": {"wordmark": {"family": "Brand", "source": "upload", "files": [{"file": "Brand-Variable.ttf", "weight": "300 700"}]}},
        }
        with self.assertRaises(A.ApplyError) as e:
            A.resolve_faces(theme(), req, self.fonts, {"fonts": []})
        self.assertIn(WORDMARK_FIXED, str(e.exception))
        self.assertFalse((self.fonts / "Brand-Variable.woff2").exists(), "nothing is written for a refused face")

    def test_a_missing_upload_says_where_to_put_it(self) -> None:
        req = {"summary": "Upload", "faces": {"sans": {"family": "Aeonik", "source": "upload", "files": [{"file": "Aeonik-Regular.woff2", "weight": "400"}]}}}
        with self.assertRaises(A.ApplyError) as e:
            A.resolve_faces(theme(), req, self.fonts, {"fonts": []})
        self.assertIn("Upload them to fonts/ on this branch", str(e.exception))

    def test_a_file_that_is_not_a_font_fails(self) -> None:
        (self.fonts / "Fake-Regular.woff2").write_text("not a font")
        req = {"summary": "Upload", "faces": {"mono": {"family": "Fake", "source": "upload", "files": [{"file": "Fake-Regular.woff2", "weight": "400"}]}}}
        with self.assertRaises(A.ApplyError):
            A.resolve_faces(theme(), req, self.fonts, {"fonts": []})


class GoldTest(Scratch):
    def test_golds_match_the_colour_module(self) -> None:
        self.assertEqual(A.golds(theme()), {"gold": C.GOLD, "gold-bright": C.GOLD_BRIGHT, "gold-deep": C.GOLD_DEEP})

    def test_replace_hexes_swaps_in_one_pass(self) -> None:
        text = "a #D4AF37 b #f1ce65 c #8A7223"
        out = A.replace_hexes(text, {"#D4AF37": "#F1CE65", "#F1CE65": "#8A7223", "#8A7223": "#8A7223"})
        self.assertEqual(out, "a #F1CE65 b #8A7223 c #8A7223")

    def test_turn_ramp_moves_only_the_ramp(self) -> None:
        text = (
            "--_amber-50: oklch(0.985 0.02 95);\n"
            "--ox-ember-soft: oklch(0.25 0.035 88);\n"
            "--_stone-700: oklch(0.442 0.015 285.8);\n"
            "--_amber-900: oklch(0.3 0.05 2);\n"
        )
        out = A.turn_ramp(text, -7)
        self.assertIn("--_amber-50: oklch(0.985 0.02 88);", out)
        self.assertIn("--ox-ember-soft: oklch(0.25 0.035 81);", out)
        self.assertIn("--_stone-700: oklch(0.442 0.015 285.8);", out)
        self.assertIn("--_amber-900: oklch(0.3 0.05 355);", out)

    def test_the_ramp_is_in_globals_css(self) -> None:
        css = (ROOT / "ui" / "src" / "styles" / "globals.css").read_text()
        self.assertEqual(len(A.RAMP.findall(css)), 8, "seven --_amber-* tints and --ox-ember-soft")

    def test_carry_gold_rewrites_the_copies(self) -> None:
        before = theme()
        after = json.loads(json.dumps(before))
        after["color"]["gold"] = other(before["color"]["gold"], "#C99B2E", "#D9B13B")
        old = A.golds(before)
        (self.root / "pwa").mkdir()
        (self.root / "pwa" / "install-prompt.js").write_text(
            f"--gold:{old['gold']};--hi:{old['gold-bright']};--deep:{old['gold-deep']};"
        )
        css = self.root / "ui" / "src" / "styles"
        css.mkdir(parents=True)
        (css / "globals.css").write_text(f"--ox-ember-soft: oklch(0.25 0.035 88);\n--x: {old['gold']};\n")
        changed = A.carry_gold(before, after, self.root)
        new = A.golds(after)
        self.assertEqual(sorted(changed), ["pwa/install-prompt.js", "ui/src/styles/globals.css"])
        self.assertEqual(
            (self.root / "pwa" / "install-prompt.js").read_text(),
            f"--gold:{new['gold']};--hi:{new['gold-bright']};--deep:{new['gold-deep']};",
        )
        degrees = A.gold_hue(after) - A.gold_hue(before)
        self.assertIn(f"oklch(0.25 0.035 {88 + degrees})", (css / "globals.css").read_text())

    def test_every_carry_file_exists(self) -> None:
        for rel in A.CARRY_FILES:
            self.assertTrue((ROOT / rel).is_file(), rel)


class WordmarkRequestTest(unittest.TestCase):
    """`apply` refuses a request that names the wordmark face, before it writes anything."""

    def test_apply_refuses_a_wordmark_face_and_leaves_the_theme(self) -> None:
        folder = ROOT / "theme" / "requests"
        made = not folder.exists()
        folder.mkdir(parents=True, exist_ok=True)
        path = folder / f"test-wordmark-{uuid.uuid4().hex[:12]}.json"
        before = THEME_FILE.read_bytes()
        try:
            path.write_text(
                json.dumps({"summary": "Inter for the wordmark", "faces": {"wordmark": {"family": "Inter", "source": "google", "weights": [600]}}})
            )
            state: dict = {}
            with self.assertRaises(A.ApplyError) as e:
                A.apply([path.relative_to(ROOT).as_posix()], state)
            self.assertIn("the wordmark face is fixed", str(e.exception))
            self.assertIn("Remove faces.wordmark", str(e.exception))
            self.assertEqual(THEME_FILE.read_bytes(), before)
            self.assertTrue(path.is_file(), "a refused request stays on the branch")
        finally:
            path.unlink(missing_ok=True)
            if made:
                shutil.rmtree(folder, ignore_errors=True)


#: Draws both wordmarks for the theme on disk with a request merged in, as the
#: build does after `apply`. Runs in its own process, because the colour and
#: glyph modules read the theme once, when they are imported.
DRAW = """
import json, sys
import request as R
import theme
req = json.loads(sys.argv[1])
merged = R.merge(theme.THEME, req)
found = theme.problems(merged)
if found:
    raise SystemExit("; ".join(found))
theme.THEME.clear()
theme.THEME.update(merged)
import marks
print(json.dumps({
    brand: {
        "plain": marks.wordmark_svg(brand, uid=brand + "-t"),
        "light": marks.wordmark_svg(brand, letters=marks.INK_TEXT, uid=brand + "-l"),
        "sheen": marks.wordmark_svg(brand, sheen=True, uid=brand + "-s"),
    }
    for brand in ("oxagen", "stella")
}))
"""


def draw(request: dict) -> dict:
    out = subprocess.run(
        [sys.executable, "-c", DRAW, json.dumps(request)], cwd=ROOT / "build", check=True, capture_output=True, text=True
    )
    return json.loads(out.stdout)


class GoldWordmarkTest(unittest.TestCase):
    """A new gold recolours the gold x and the gold asterisk, and leaves every outline as it was."""

    def test_a_gold_request_recolours_only_the_accent(self) -> None:
        before = theme()
        gold = other(before["color"]["gold"], "#C99B2E", "#D9B13B")
        req = {"summary": "A new gold", "color": {"gold": gold}}
        self.assertEqual(R.problems(req), [])
        after = R.merge(before, req)
        old, new = A.golds(before), A.golds(after)
        shipped, changed = draw({"summary": "Nothing"}), draw(req)
        accent = re.compile(r'<path class="accent" d="[^"]*" fill="([^"]+)"/>')
        for brand in ("oxagen", "stella"):
            for variant in ("plain", "light", "sheen"):
                a, b = shipped[brand][variant], changed[brand][variant]
                where = f"{brand} {variant}"
                self.assertNotEqual(a, b, where)
                self.assertEqual(re.findall(r' d="([^"]*)"', a), re.findall(r' d="([^"]*)"', b), f"{where}: the outlines moved")
                self.assertEqual(A.replace_hexes(b, {new[k]: old[k] for k in new}), a, f"{where}: more than the gold changed")
            self.assertEqual(accent.search(shipped[brand]["plain"]).group(1), old["gold"], brand)  # type: ignore[union-attr]
            self.assertEqual(accent.search(changed[brand]["plain"]).group(1), gold, brand)  # type: ignore[union-attr]
            self.assertIn(new["gold-bright"], changed[brand]["sheen"], brand)


class ReportTest(unittest.TestCase):
    def test_changes_lists_each_changed_field(self) -> None:
        before = theme()
        after = json.loads(json.dumps(before))
        after["color"]["gold"] = other(before["color"]["gold"], "#C99B2E", "#D9B13B")
        after["radius"]["base"] = other(before["radius"]["base"], "0.5rem", "0.45rem")
        self.assertEqual(
            A.changes(before, after),
            [
                ("color.gold", before["color"]["gold"], after["color"]["gold"]),
                ("radius.base", before["radius"]["base"], after["radius"]["base"]),
            ],
        )

    def test_a_failed_request_reports_its_problems(self) -> None:
        state = {"requests": [{"path": "theme/requests/x.json", "summary": "x"}], "problems": ["faces.sans needs files"]}
        out = A.report(state)
        self.assertIn("did not apply the request", out)
        self.assertIn("- faces.sans needs files", out)
        self.assertTrue(out.startswith("<!-- apply-theme -->"))

    def test_a_clean_report_names_the_gold_and_the_next_step(self) -> None:
        state = {"before": theme(), "requests": [{"path": "theme/requests/x.json", "summary": "x"}], "fonts": [], "carried": [], "problems": []}
        out = A.report(state)
        self.assertIn(f"| gold | `{C.GOLD}` | `{C.GOLD}` |", out)
        self.assertIn("runs the fan-out", out)
        self.assertIn("pushed nothing", A.report(state, pushed=False, run_url="https://example.test/run"))


if __name__ == "__main__":
    unittest.main()
