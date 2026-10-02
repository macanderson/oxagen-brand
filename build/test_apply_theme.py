"""Tests for build/apply_theme.py: paths, Google Fonts parsing, uploads, the gold carry, and the report.

    python3 -m unittest discover -s build -p "test_*.py"

Nothing here reaches the network. The apply-theme workflow's proof run
covers the fetches.
"""

from __future__ import annotations

import json
import shutil
import tempfile
import unittest
from pathlib import Path

import apply_theme as A
import color as C
from theme import ROOT, THEME_FILE

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
            "faces": {"wordmark": {"family": "Brand", "source": "upload", "files": [{"file": "Brand-Variable.ttf", "weight": "300 700"}]}},
        }
        log: dict = {"fonts": []}
        faces = A.resolve_faces(theme(), req, self.fonts, log)
        face = faces["wordmark"]
        self.assertEqual(face["source"], "kit")
        self.assertEqual(face["files"], [{"file": "Brand-Variable.woff2", "weight": "300 700"}])
        self.assertEqual(face["outline"], {"file": "Brand-Variable.ttf", "weight": 600})
        self.assertTrue((self.fonts / "Brand-Variable.woff2").is_file())
        self.assertEqual(log["fonts"][0]["converted"], ["Brand-Variable.woff2"])

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
        after["color"]["gold"] = "#C99B2E"
        (self.root / "pwa").mkdir()
        (self.root / "pwa" / "install-prompt.js").write_text("--gold:#D4AF37;--hi:#F1CE65;--deep:#8A7223;")
        css = self.root / "ui" / "src" / "styles"
        css.mkdir(parents=True)
        (css / "globals.css").write_text("--ox-ember-soft: oklch(0.25 0.035 88);\n--x: #D4AF37;\n")
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


class ReportTest(unittest.TestCase):
    def test_changes_lists_each_changed_field(self) -> None:
        before = theme()
        after = json.loads(json.dumps(before))
        after["color"]["gold"] = "#C99B2E"
        after["radius"]["base"] = "0.5rem"
        self.assertEqual(
            A.changes(before, after),
            [("color.gold", "#D4AF37", "#C99B2E"), ("radius.base", "0.45rem", "0.5rem")],
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
