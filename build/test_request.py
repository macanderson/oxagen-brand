"""Tests for build/request.py: the request schema, its rules, and the merge.

    python3 -m unittest discover -s build -p "test_*.py"

CI runs these in the `check` job of `.github/workflows/ui.yml`.
"""

from __future__ import annotations

import json
import unittest

import request as R
from theme import THEME_FILE


def theme() -> dict:
    return json.loads(THEME_FILE.read_text())


class SchemaTest(unittest.TestCase):
    def test_committed_schema_matches_the_theme_schema(self) -> None:
        self.assertEqual(R.check_schema(), [])

    def test_every_partial_field_is_optional(self) -> None:
        schema = R.request_schema()
        self.assertEqual(schema["required"], ["summary"])
        self.assertNotIn("required", schema["properties"]["color"])
        self.assertNotIn("required", schema["$defs"]["state"])
        self.assertNotIn("required", schema["$defs"]["step"])

    def test_array_items_stay_strict(self) -> None:
        items = R.request_schema()["$defs"]["files"]["items"]
        self.assertEqual(items["required"], ["file", "weight"])


class ProblemsTest(unittest.TestCase):
    def test_a_gold_change_is_valid(self) -> None:
        self.assertEqual(R.problems({"summary": "A warmer gold", "color": {"gold": "#C9A227"}}), [])

    def test_a_partial_ground_is_valid(self) -> None:
        req = {"summary": "Lift the panel", "color": {"ink": {"panel": "#1C1C1F"}, "states": {"allowed": {"paper": "#2F7D52"}}}}
        self.assertEqual(R.problems(req), [])

    def test_a_request_needs_a_summary(self) -> None:
        self.assertTrue(any("summary" in p for p in R.problems({"color": {"gold": "#C9A227"}})))

    def test_a_request_must_change_something(self) -> None:
        self.assertTrue(any("changes nothing" in p for p in R.problems({"summary": "Nothing"})))

    def test_unknown_fields_fail(self) -> None:
        found = R.problems({"summary": "Bad", "colour": {"gold": "#C9A227"}})
        self.assertTrue(any("colour" in p for p in found))

    def test_a_lowercase_hex_fails(self) -> None:
        self.assertTrue(R.problems({"summary": "Bad", "color": {"gold": "#c9a227"}}))

    def test_a_file_name_cannot_leave_fonts(self) -> None:
        for name in ("../build/x.woff2", "sub/x.woff2", ".hidden.woff2", "x.js"):
            req = {
                "summary": "Upload",
                "faces": {"sans": {"family": "Aeonik", "source": "upload", "files": [{"file": name, "weight": "400"}]}},
            }
            self.assertTrue(R.problems(req), name)

    def test_a_css_breaking_shadow_fails(self) -> None:
        req = {"summary": "Shadow", "shadow": {"ui": {"ink": "0 1px 2px red; } body { color: red"}}}
        self.assertTrue(R.problems(req))

    def test_a_google_face_needs_weights_and_no_files(self) -> None:
        found = R.problems({"summary": "Inter", "faces": {"display": {"family": "Inter", "source": "google"}}})
        self.assertTrue(any("needs weights" in p for p in found))
        req = {
            "summary": "Inter",
            "faces": {"display": {"family": "Inter", "source": "google", "weights": [400], "files": [{"file": "a.woff2", "weight": "400"}]}},
        }
        self.assertTrue(any("names none" in p for p in R.problems(req)))

    def test_an_upload_needs_files(self) -> None:
        found = R.problems({"summary": "Aeonik", "faces": {"sans": {"family": "Aeonik", "source": "upload"}}})
        self.assertTrue(any("needs files" in p for p in found))

    def test_only_outline_roles_take_an_outline(self) -> None:
        req = {
            "summary": "Mono",
            "faces": {
                "mono": {
                    "family": "JetBrains Mono",
                    "source": "google",
                    "weights": [400],
                    "outline": {"file": "x.ttf"},
                }
            },
        }
        self.assertTrue(any("only wordmark and sans" in p for p in R.problems(req)))

    def test_summary_rejects_markup(self) -> None:
        self.assertTrue(R.problems({"summary": "<script>", "color": {"gold": "#C9A227"}}))


class MergeTest(unittest.TestCase):
    def test_a_partial_change_keeps_every_other_value(self) -> None:
        before = theme()
        after = R.merge(before, {"summary": "x", "color": {"gold": "#C9A227", "ink": {"panel": "#1C1C1F"}}})
        self.assertEqual(after["color"]["gold"], "#C9A227")
        self.assertEqual(after["color"]["ink"]["panel"], "#1C1C1F")
        self.assertEqual(after["color"]["ink"]["ink"], before["color"]["ink"]["ink"])
        self.assertEqual(after["faces"], before["faces"])
        self.assertEqual(before["color"]["gold"], "#D4AF37", "merge must not change its input")

    def test_a_type_step_changes_one_field(self) -> None:
        after = R.merge(theme(), {"summary": "x", "type": {"scales": {"app": {"body": {"size": "0.9375rem"}}}}})
        body = after["type"]["scales"]["app"]["body"]
        self.assertEqual(body["size"], "0.9375rem")
        self.assertEqual(body["leading"], 1.5)

    def test_the_merged_theme_validates(self) -> None:
        import theme as TH

        after = R.merge(theme(), {"summary": "x", "radius": {"base": "0.5rem", "card": "xl"}, "spacing": {"unit": "0.25rem"}})
        self.assertEqual(TH.problems(after), [])

    def test_resolved_faces_replace_the_role(self) -> None:
        before = theme()
        face = R.face_entry(
            "display",
            before["faces"]["display"],
            {"family": "Inter", "source": "google", "weights": [400, 700]},
            [{"file": "inter-latin-wght.woff2", "weight": "400 700"}],
            None,
        )
        after = R.merge(before, {"summary": "x"}, {"display": face})
        self.assertEqual(after["faces"]["display"]["family"], "Inter")
        self.assertEqual(after["faces"]["display"]["source"], "google")
        self.assertEqual(after["faces"]["display"]["fallback"], R.DEFAULT_FALLBACK["display"])
        self.assertEqual(after["faces"]["sans"], before["faces"]["sans"])


class FaceEntryTest(unittest.TestCase):
    def test_the_same_family_keeps_its_fallback_and_features(self) -> None:
        mono = theme()["faces"]["mono"]
        face = R.face_entry("mono", mono, {"family": mono["family"], "source": "kit", "files": mono["files"]}, mono["files"], None)
        self.assertEqual(face["features"], ["calt", "liga"])
        self.assertEqual(face["fallback"], mono["fallback"])

    def test_an_upload_becomes_a_kit_face(self) -> None:
        sans = theme()["faces"]["sans"]
        files = [{"file": "Aeonik-Regular.woff2", "weight": "400"}]
        face = R.face_entry("sans", sans, {"family": "Aeonik", "source": "upload", "files": files}, files, {"file": "Aeonik-Regular.ttf"})
        self.assertEqual(face["source"], "kit")
        self.assertEqual(face["outline"], {"file": "Aeonik-Regular.ttf"})

    def test_an_outline_role_needs_an_outline(self) -> None:
        with self.assertRaises(ValueError):
            R.face_entry("wordmark", theme()["faces"]["wordmark"], {"family": "Inter", "source": "google"}, [], None)

    def test_nearest_prefers_a_variable_file_that_covers_the_weight(self) -> None:
        files = [
            {"file": "a-400.woff2", "weight": "400"},
            {"file": "a-wght.woff2", "weight": "100 900"},
            {"file": "a-700.woff2", "weight": "700"},
        ]
        self.assertEqual(R.nearest(files, 600)["file"], "a-wght.woff2")
        self.assertEqual(R.nearest(files[:1] + files[2:], 600)["file"], "a-700.woff2")


class LayoutTest(unittest.TestCase):
    def test_dump_reproduces_the_theme_file(self) -> None:
        self.assertEqual(R.dump_theme(theme()), THEME_FILE.read_text())


if __name__ == "__main__":
    unittest.main()
