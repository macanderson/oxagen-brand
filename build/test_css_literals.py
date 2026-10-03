"""Tests for build/css_literals.py, the literal guard on the kit's globals.css.

    python3 -m unittest discover -s build -p "test_*.py"
"""

from __future__ import annotations

import unittest

import css_literals as L


def flagged(css: str) -> list[tuple[int, str, str]]:
    """Each literal the guard finds in `css`, as (line, property, value)."""
    hits, _stale = L.literals(css, keep=())
    return [(h.line, h.prop, h.value) for h in hits]


class TheKitStylesheet(unittest.TestCase):
    def test_globals_css_writes_no_literal_and_keeps_no_stale_entry(self) -> None:
        self.assertEqual(L.check(), [])

    def test_every_keep_entry_gives_a_reason(self) -> None:
        for entry in L.KEEP:
            self.assertTrue(entry.why.strip(), entry)


class Corners(unittest.TestCase):
    def test_a_literal_corner_fails(self) -> None:
        self.assertEqual(flagged(".a {\n  border-radius: 6px;\n}"), [(2, "border-radius", "6px")])

    def test_a_corner_alias_fails(self) -> None:
        self.assertEqual(flagged(":root { --ui-radius: 0.5rem; }"), [(1, "--ui-radius", "0.5rem")])

    def test_a_step_that_adds_pixels_to_a_token_fails(self) -> None:
        css = "@theme inline { --radius-xl: calc(var(--radius) + 4px); }"
        self.assertEqual(flagged(css), [(1, "--radius-xl", "calc(var(--radius) + 4px)")])

    def test_the_suggestion_names_the_same_step(self) -> None:
        hits, _ = L.literals("@theme inline { --radius-2xl: calc(var(--radius) + 8px); }", keep=())
        self.assertEqual(hits[0].use, "var(--ox-radius-2xl)")

    def test_pills_circles_and_square_corners_pass(self) -> None:
        css = ".p { border-radius: 9999px; } .q { border-radius: 999px; } .c { border-radius: 50%; } .z { border-radius: 0; }"
        self.assertEqual(flagged(css), [])

    def test_a_token_passes(self) -> None:
        self.assertEqual(flagged(".a { border-radius: var(--radius-lg); --radius-xs: var(--ox-radius-xs); }"), [])


class Shadows(unittest.TestCase):
    def test_a_drop_shadow_fails(self) -> None:
        self.assertEqual(flagged(".a { box-shadow: 0 4px 12px rgb(0 0 0 / 0.2); }"),
                         [(1, "box-shadow", "0 4px 12px rgb(0 0 0 / 0.2)")])

    def test_a_shadow_alias_fails(self) -> None:
        self.assertEqual(flagged(":root { --ui-shadow-pop: 0 25px 50px -12px #000; }"),
                         [(1, "--ui-shadow-pop", "0 25px 50px -12px #000")])

    def test_a_ring_and_an_inset_bar_pass(self) -> None:
        css = (".ring:hover { box-shadow: 0 0 0 2px color-mix(in oklch, var(--ring) 25%, transparent); }\n"
               ".bar { box-shadow: inset 0 -2px 0 var(--gold); }")
        self.assertEqual(flagged(css), [])

    def test_a_ring_beside_a_drop_shadow_fails(self) -> None:
        self.assertEqual(len(flagged(".a { box-shadow: 0 0 0 1px red, 0 2px 4px black; }")), 1)

    def test_a_token_passes(self) -> None:
        self.assertEqual(flagged(".a { box-shadow: var(--ui-shadow); } :root { --ui-shadow: var(--ox-shadow-ui-ink); }"), [])


class FontSizes(unittest.TestCase):
    def test_a_pixel_or_rem_size_fails(self) -> None:
        self.assertEqual(flagged(".a { font-size: 13px; }\n.b { font-size: 0.75rem; }"),
                         [(1, "font-size", "13px"), (2, "font-size", "0.75rem")])

    def test_the_font_shorthand_is_read(self) -> None:
        self.assertEqual(len(flagged(".a { font: 600 14px/1.2 var(--font-sans); }")), 1)

    def test_a_relative_size_of_one_or_more_and_a_token_pass(self) -> None:
        css = ".a { font-size: 1em; } .b { font-size: 120%; } .c { font-size: var(--ox-a-micro); } .d { font-size: var(--x, 13px); }"
        self.assertEqual(flagged(css), [])

    def test_a_relative_size_below_its_parent_fails(self) -> None:
        css = ".a { font-size: 0.9em; }\n.b { font-size: 85%; }\n.c { font-size: smaller; }"
        self.assertEqual([h[0] for h in flagged(css)], [1, 2, 3])


class FontSizesEverywhere(unittest.TestCase):
    def test_the_scope_sets_every_font_size_from_a_token(self) -> None:
        hits, _used = L.font_size_hits()
        self.assertEqual([f"{h.path}:{h.line} {h.value}" for h in hits], [])

    def test_the_app_copy_is_skipped_and_nothing_else_is(self) -> None:
        self.assertTrue(L.SKIP.search("ui/src/pages/app/work-page.tsx"))
        self.assertTrue(L.SKIP.search("ui/src/pages/app/app.css"))
        self.assertFalse(L.SKIP.search("ui/src/pages/website-home.tsx"))
        self.assertFalse(L.SKIP.search("ui/src/components/app/button.tsx"))
        scanned = {p.relative_to(L.ROOT).as_posix() for _kind, p in L.scanned_files()}
        self.assertFalse(any(p.startswith("ui/src/pages/app/") for p in scanned))
        self.assertIn("ui/src/pages/website-home.tsx", scanned)

    def test_a_tailwind_arbitrary_size_fails(self) -> None:
        hits = L.script_font_sizes('const a = "px-2 text-[13px] font-medium";\nconst b = "text-[0.75rem]";', "x.tsx")
        self.assertEqual([(h.line, h.value) for h in hits], [(1, "text-[13px]"), (2, "text-[0.75rem]")])

    def test_a_tailwind_fixed_size_fails(self) -> None:
        hits = L.script_font_sizes('const a = "text-lg max-md:text-base text-2xl";', "x.tsx")
        self.assertEqual([h.value for h in hits], ["text-lg", "text-base", "text-2xl"])

    def test_a_tailwind_size_that_reads_a_token_passes(self) -> None:
        code = 'const a = "text-(length:--ox-a-h2) text-[length:var(--ox-m-h2)] text-[var(--body)] text-sm text-a-body";'
        self.assertEqual(L.script_font_sizes(code, "x.tsx"), [])

    def test_a_font_size_prop_and_css_in_a_string_fail(self) -> None:
        code = 'h({ fontSize: "0.75rem" });\nconst css = ".t{font:14px/1.45 Aeonik}.b{font-size:13px}";'
        hits = L.script_font_sizes(code, "x.js")
        self.assertEqual([(h.line, h.prop) for h in hits], [(1, "fontSize"), (2, "font"), (2, "font-size")])

    def test_a_comment_in_a_script_is_not_read(self) -> None:
        code = "/** `.th { font-size:10.5px }` */\n// text-[11px]\nconst url = \"https://x.test/a\";"
        self.assertEqual(L.script_font_sizes(code, "x.ts"), [])

    def test_a_page_style_block_and_attribute_are_read(self) -> None:
        html = '<style>\n.a{font-size:12px}\n.b{font-size:var(--a-body)}\n</style>\n<p style="font-size:13.5px">x</p>'
        self.assertEqual([(h.line, h.value) for h in L.html_font_sizes(html, "x.html")], [(2, "12px"), (5, "13.5px")])


class HeadingLineHeights(unittest.TestCase):
    def test_a_literal_on_a_heading_fails(self) -> None:
        css = "h1,\nh2 {\n  line-height: 1.12;\n}\n.prose h3 { line-height: 1.3; }"
        self.assertEqual(flagged(css), [(3, "line-height", "1.12"), (5, "line-height", "1.3")])

    def test_a_heading_in_a_layer_or_a_media_query_is_read(self) -> None:
        css = "@layer base { @media (width >= 48rem) { h4 { line-height: 1.4; } } }"
        self.assertEqual(flagged(css), [(1, "line-height", "1.4")])

    def test_a_leading_alias_fails(self) -> None:
        self.assertEqual(flagged(":root { --heading-leading: 1.12; }"), [(1, "--heading-leading", "1.12")])

    def test_a_token_on_a_heading_passes(self) -> None:
        self.assertEqual(flagged("h1 { line-height: var(--ox-a-h1-leading); }"), [])

    def test_a_line_height_off_a_heading_passes(self) -> None:
        css = ".ox-wordmark { line-height: 1; } .h1-like { line-height: 1.2; } th { line-height: 1.5; }"
        self.assertEqual(flagged(css), [])


class Reading(unittest.TestCase):
    def test_a_literal_in_a_comment_passes(self) -> None:
        self.assertEqual(flagged("/* .a { border-radius: 6px; } */\n.b { color: red; }"), [])

    def test_a_glob_in_a_string_does_not_open_a_comment(self) -> None:
        # `/*` inside the @source path is not a comment, so the rule after it is still read.
        css = '@source "../node_modules/x/dist/*.js";\n.a { border-radius: 6px; }\n/* end */'
        self.assertEqual(flagged(css), [(2, "border-radius", "6px")])

    def test_important_is_ignored_when_matching_keep(self) -> None:
        keep = (L.Keep("font-size", "16px", "the iOS zoom floor"),)
        hits, stale = L.literals("input { font-size: 16px !important; }", keep=keep)
        self.assertEqual((hits, stale), ([], []))


class Keep(unittest.TestCase):
    def test_a_kept_literal_passes(self) -> None:
        keep = (L.Keep("font-size", "16px", "the iOS zoom floor"),)
        self.assertEqual(L.literals("@media (width < 48rem) { input { font-size: 16px; } }", keep=keep), ([], []))

    def test_an_entry_that_excuses_nothing_is_stale(self) -> None:
        keep = (L.Keep("font-size", "16px", "the iOS zoom floor"),)
        self.assertEqual(L.literals(".a { color: red; }", keep=keep), ([], list(keep)))


if __name__ == "__main__":
    unittest.main()
