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


def other(value: str, *choices: str) -> str:
    """The first of `choices` that differs from `value`, so a test changes the theme whatever it holds."""
    return next(c for c in choices if c != value)


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
        self.assertTrue(any("only sans is drawn from one" in p for p in R.problems(req)))

    def test_summary_rejects_markup(self) -> None:
        self.assertTrue(R.problems({"summary": "<script>", "color": {"gold": "#C9A227"}}))


class MergeTest(unittest.TestCase):
    def test_a_partial_change_keeps_every_other_value(self) -> None:
        before = theme()
        gold = other(before["color"]["gold"], "#C9A227", "#D9B13B")
        panel = other(before["color"]["ink"]["panel"], "#1C1C1F", "#1A1A1D")
        after = R.merge(before, {"summary": "x", "color": {"gold": gold, "ink": {"panel": panel}}})
        self.assertEqual(after["color"]["gold"], gold)
        self.assertEqual(after["color"]["ink"]["panel"], panel)
        self.assertEqual(after["color"]["ink"]["ink"], before["color"]["ink"]["ink"])
        self.assertEqual(after["faces"], before["faces"])
        self.assertEqual(before, theme(), "merge must not change its input")

    def test_a_type_base_changes_one_field(self) -> None:
        before = theme()
        base = other(before["type"]["scales"]["app"]["base"], "0.9375rem", "0.875rem")
        after = R.merge(before, {"summary": "x", "type": {"scales": {"app": {"base": base}}}})
        app = after["type"]["scales"]["app"]
        self.assertEqual(app["base"], base)
        self.assertEqual(app["steps"], before["type"]["scales"]["app"]["steps"])

    def test_a_type_ratio_changes_one_field(self) -> None:
        before = theme()
        after = R.merge(before, {"summary": "x", "type": {"scales": {"app": {"steps": {"micro": {"ratio": 0.8}}}}}})
        micro = after["type"]["scales"]["app"]["steps"]["micro"]
        self.assertEqual(micro["ratio"], 0.8)
        self.assertEqual(micro["leading"], before["type"]["scales"]["app"]["steps"]["micro"]["leading"])

    def test_the_merged_theme_validates(self) -> None:
        import theme as TH

        after = R.merge(theme(), {"summary": "x", "radius": {"base": "0.5rem", "card": "xl"}, "spacing": {"unit": "0.25rem"}})
        self.assertEqual(TH.problems(after), [])

    def test_a_small_base_and_a_small_step_pass(self) -> None:
        import theme as TH

        change = {"scales": {"app": {"base": "0.75rem", "steps": {"2xs": {"ratio": 0.6}}}, "marketing": {"base": "0.8125rem"}}}
        after = R.merge(theme(), {"summary": "x", "type": change})
        self.assertEqual(TH.problems(after), [])

    def test_a_body_ratio_other_than_one_fails(self) -> None:
        import theme as TH

        after = R.merge(theme(), {"summary": "x", "type": {"scales": {"app": {"steps": {"body": {"ratio": 1.1}}}}}})
        found = TH.problems(after)
        self.assertEqual(len(found), 1)
        self.assertIn("type.scales.app.steps.body.ratio is 1.1", found[0])

    def test_the_theme_round_trips_through_its_layout(self) -> None:
        import theme as TH

        self.assertEqual(R.dump_theme(theme()), TH.THEME_FILE.read_text())

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
        self.assertEqual(face["features"], mono["features"])
        self.assertEqual(face["fallback"], mono["fallback"])

    def test_an_upload_becomes_a_kit_face(self) -> None:
        sans = theme()["faces"]["sans"]
        files = [{"file": "Aeonik-Regular.woff2", "weight": "400"}]
        face = R.face_entry("sans", sans, {"family": "Aeonik", "source": "upload", "files": files}, files, {"file": "Aeonik-Regular.ttf"})
        self.assertEqual(face["source"], "kit")
        self.assertEqual(face["outline"], {"file": "Aeonik-Regular.ttf"})

    def test_an_outline_role_needs_an_outline(self) -> None:
        with self.assertRaises(ValueError):
            R.face_entry("sans", theme()["faces"]["sans"], {"family": "Inter", "source": "google"}, [], None)

    def test_nearest_prefers_a_variable_file_that_covers_the_weight(self) -> None:
        files = [
            {"file": "a-400.woff2", "weight": "400"},
            {"file": "a-wght.woff2", "weight": "100 900"},
            {"file": "a-700.woff2", "weight": "700"},
        ]
        self.assertEqual(R.nearest(files, 600)["file"], "a-wght.woff2")
        self.assertEqual(R.nearest(files[:1] + files[2:], 600)["file"], "a-700.woff2")

    def test_nearest_prefers_an_upright_file(self) -> None:
        files = [
            {"file": "a-italic-wght.woff2", "weight": "100 900", "style": "italic"},
            {"file": "a-700.woff2", "weight": "700"},
        ]
        self.assertEqual(R.nearest(files, 400)["file"], "a-700.woff2")


class StyleTest(unittest.TestCase):
    def test_a_file_may_be_italic(self) -> None:
        files = [
            {"file": "aeonik-wght.woff2", "weight": "100 900"},
            {"file": "aeonik-italic-wght.woff2", "weight": "100 900", "style": "italic"},
        ]
        req = {"summary": "Aeonik", "faces": {"display": {"family": "Aeonik", "source": "kit", "files": files}}}
        self.assertEqual(R.problems(req), [])

    def test_a_style_other_than_normal_or_italic_fails(self) -> None:
        files = [{"file": "aeonik-wght.woff2", "weight": "100 900", "style": "oblique"}]
        req = {"summary": "Aeonik", "faces": {"display": {"family": "Aeonik", "source": "kit", "files": files}}}
        self.assertTrue(any("oblique" in p for p in R.problems(req)))

    def test_the_shipped_theme_loads_an_italic_and_two_extra_faces(self) -> None:
        import theme as TH

        shipped = theme()
        self.assertEqual(TH.problems(), [])
        styles = [f.get("style", "normal") for f in shipped["faces"]["sans"]["files"]]
        self.assertEqual(sorted(styles), ["italic", "normal"])
        self.assertEqual([f["family"] for f in shipped["extra_faces"]], ["Aeonik Mono", "Aeonik Fono"])
        self.assertNotIn("extra_faces", R.request_schema()["properties"], "a request cannot change the extra faces")


class WordmarkTest(unittest.TestCase):
    """The wordmark face is fixed: Space Grotesk, drawn at 600 (Mac, 2026-10-02)."""

    FACES = (
        {"family": "Inter", "source": "google", "weights": [600]},
        {"family": "Aeonik", "source": "upload", "files": [{"file": "Aeonik-Bold.otf", "weight": "600"}]},
        {"family": "Aeonik", "source": "kit", "files": [{"file": "aeonik-wght.woff2", "weight": "100 900"}]},
    )

    def test_the_schema_has_no_wordmark_face(self) -> None:
        schema = R.request_schema()
        self.assertNotIn("wordmark", schema["properties"]["faces"]["properties"])
        self.assertEqual(sorted(schema["properties"]["faces"]["properties"]), sorted(R.REQUEST_ROLES))
        self.assertNotIn("weight", schema["$defs"]["face_request"]["properties"]["outline"]["properties"])

    def test_a_request_cannot_change_the_wordmark_face(self) -> None:
        for face in self.FACES:
            found = R.problems({"summary": "New wordmark", "faces": {"wordmark": face}})
            self.assertEqual(found, [R.WORDMARK_REFUSED], face["source"])
        self.assertIn("the wordmark face is fixed", R.WORDMARK_REFUSED)
        self.assertIn("Space Grotesk", R.WORDMARK_REFUSED)

    def test_a_wordmark_face_fails_beside_a_valid_change(self) -> None:
        req = {"summary": "Gold and wordmark", "color": {"gold": "#C9A227"}, "faces": {"wordmark": self.FACES[0]}}
        self.assertEqual(R.problems(req), [R.WORDMARK_REFUSED])

    def test_face_entry_refuses_the_wordmark(self) -> None:
        current = theme()["faces"]["wordmark"]
        with self.assertRaises(ValueError):
            R.face_entry("wordmark", current, self.FACES[0], [], {"file": current["outline"]["file"]})

    def test_the_shipped_theme_draws_the_fixed_wordmark(self) -> None:
        import theme as TH

        face = theme()["faces"]["wordmark"]
        self.assertEqual(face["family"], TH.WORDMARK_FAMILY)
        self.assertEqual(face["outline"], TH.WORDMARK_OUTLINE)
        self.assertEqual(TH.problems(), [])

    def test_the_theme_refuses_another_wordmark_face(self) -> None:
        import theme as TH

        for field, value in (("family", "Inter"), ("file", "aeonik-wght.woff2"), ("weight", 700)):
            t = theme()
            if field == "family":
                t["faces"]["wordmark"]["family"] = value
            else:
                t["faces"]["wordmark"]["outline"][field] = value
            found = TH.problems(t)
            self.assertEqual(len(found), 1, field)
            self.assertIn(TH.WORDMARK_FIXED, found[0])

    def test_a_gold_request_leaves_the_wordmark_face_alone(self) -> None:
        import theme as TH

        before = theme()
        gold = other(before["color"]["gold"], "#C99B2E", "#D9B13B")
        req = {"summary": "A new gold", "color": {"gold": gold}}
        self.assertEqual(R.problems(req), [])
        after = R.merge(before, req)
        self.assertEqual(after["faces"]["wordmark"], before["faces"]["wordmark"])
        self.assertEqual(TH.problems(after), [])


class LayoutTest(unittest.TestCase):
    def test_dump_reproduces_the_theme_file(self) -> None:
        self.assertEqual(R.dump_theme(theme()), THEME_FILE.read_text())


if __name__ == "__main__":
    unittest.main()
