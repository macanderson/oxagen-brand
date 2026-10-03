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

    def test_only_tests_are_skipped(self) -> None:
        self.assertTrue(L.SKIP.search("ui/src/components/button.test.tsx"))
        self.assertFalse(L.SKIP.search("ui/src/pages/app/work-page.tsx"))
        self.assertFalse(L.SKIP.search("ui/src/pages/app/app.css"))
        scanned = {p.relative_to(L.ROOT).as_posix() for _kind, p in L.scanned_files()}
        self.assertIn("ui/src/pages/app/work-page.tsx", scanned)
        self.assertIn("ui/src/pages/app/app.css", scanned)
        self.assertIn("ui/src/pages/website-home.tsx", scanned)

    def test_a_tailwind_arbitrary_size_fails(self) -> None:
        hits = L.script_font_sizes('const a = "px-2 text-[13px] font-medium";\nconst b = "text-[0.75rem]";', "x.tsx")
        self.assertEqual([(h.line, h.value) for h in hits], [(1, "text-[13px]"), (2, "text-[0.75rem]")])

    def test_a_tailwind_size_with_no_step_fails(self) -> None:
        hits = L.script_font_sizes('const a = "text-4xl max-md:text-base text-6xl";', "x.tsx")
        self.assertEqual([h.value for h in hits], ["text-4xl", "text-6xl"])

    def test_a_tailwind_size_that_reads_a_token_passes(self) -> None:
        code = (
            'const a = "text-(length:--ox-a-h2) text-[length:var(--ox-m-h2)] text-[var(--body)] text-a-body text-a-2xs";\n'
            'const b = "text-xs text-sm text-base text-lg text-xl text-2xl text-3xl";'
        )
        self.assertEqual(L.script_font_sizes(code, "x.tsx"), [])

    def test_a_small_literal_reads_the_nearest_small_step(self) -> None:
        hits = L.script_font_sizes('const a = "text-[10.5px]";\nconst b = "text-[12px]";', "x.tsx")
        self.assertTrue(hits[0].use.startswith("text-xs (10px"))
        self.assertTrue(hits[1].use.startswith("text-sm (12px"))
        self.assertIn("var(--ox-a-micro) (12px)", L.size_suggestion(11.5))

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



class SemanticTokens(unittest.TestCase):
    def test_the_kit_stylesheet_gives_each_token_one_definition_per_theme(self) -> None:
        self.assertEqual(L.semantic_problems((L.ROOT / L.KIT_CSS).read_text()), [])

    def test_a_second_declaration_in_one_block_fails(self) -> None:
        css = ":root {\n  --muted: #eee;\n}\n:root {\n  --muted: #666;\n}"
        found = L.semantic_problems(css, "x.css")
        self.assertEqual(len(found), 1)
        self.assertIn("x.css:5 declares --muted a second time in :root (first at line 2)", found[0])

    def test_a_root_declaration_after_dark_fails(self) -> None:
        css = (".dark { --x: white; }\n"
               "@media (prefers-color-scheme: dark) { :root:not(.light):not(.dark) { --x: white; } }\n"
               ":root { --x: black; }")
        found = L.semantic_problems(css, "x.css")
        self.assertEqual(len(found), 2)
        self.assertTrue(any("declares --x on :root after .dark does" in p for p in found))

    def test_the_os_dark_block_must_repeat_dark(self) -> None:
        css = (":root { --x: black; }\n.dark { --x: white; }\n"
               "@media (prefers-color-scheme: dark) { :root:not(.light):not(.dark) { --x: grey; } }")
        found = L.semantic_problems(css, "x.css")
        self.assertEqual(len(found), 1)
        self.assertIn("sets --x to 'white' in .dark and 'grey'", found[0])

    def test_one_definition_per_theme_passes(self) -> None:
        css = (":root { --x: black; }\n.dark { --x: white; }\n"
               "@media (prefers-color-scheme: dark) { :root:not(.light):not(.dark) { --x: white; } }")
        self.assertEqual(L.semantic_problems(css, "x.css"), [])


class StyleLiterals(unittest.TestCase):
    def test_the_scope_reads_every_colour_corner_shadow_and_space_from_a_token(self) -> None:
        self.assertEqual([(h.path, h.line, h.group, h.value) for h in L.style_hits()], [])

    def test_a_colour_literal_fails_and_a_token_passes(self) -> None:
        for value in ("#fff", "rgb(0 0 0 / 0.5)", "oklch(0.5 0.1 80)", "white", "1px solid #27272A", "var(--ox-gold)"):
            self.assertTrue(L.color_literal(value), value)
        for value in ("var(--border)", "transparent", "currentColor", "var(--x, #fff)",
                      "color-mix(in oklch, var(--gold) 40%, transparent)", "1px solid var(--border)"):
            self.assertFalse(L.color_literal(value), value)

    def test_a_spacing_literal_fails_and_the_unit_passes(self) -> None:
        for value in ("9px 12px", "0.5rem", "1em", "calc(100% - 16px)"):
            self.assertTrue(L.spacing_literal(value), value)
        for value in ("0", "0 auto", "calc(var(--ox-space) * 3)", "50%", "var(--pad)"):
            self.assertFalse(L.spacing_literal(value), value)

    def test_a_stylesheet_custom_property_is_its_token_layer(self) -> None:
        css = ":root { --x: #fff; --pad: 12px; }\n.a { color: #fff; padding: 9px; border-radius: 6px; }"
        hits = L.css_style_hits(css, "sdlc/public/x.css")
        self.assertEqual(sorted(h.group for h in hits), ["border-radius", "color", "spacing"])

    def test_a_script_literal_fails(self) -> None:
        code = (
            'const a = "gap-[7px] rounded-[10px] shadow-[0_1px_2px_black] bg-[#fff] bg-zinc-800 text-white bg-ox-gold";\n'
            'const b = <div style={{ padding: 24, color: "#27272A", borderRadius: "8px" }} />;\n'
            'const c = <path fill="#D4AF37" />;\n'
            'const d = ".t{padding:9px 12px;background:#000}";'
        )
        groups = sorted(h.group for h in L.script_style_hits(code, "x.tsx"))
        self.assertEqual(groups, ["border-radius", "border-radius", "box-shadow", "color", "color", "color", "color",
                                  "color", "color", "color", "spacing", "spacing", "spacing"])

    def test_a_script_token_passes(self) -> None:
        code = (
            'const a = "gap-1.75 rounded-xl shadow-pop bg-card text-muted-foreground p-(--pad) gap-[var(--x)]";\n'
            'const b = <div style={{ padding: 0, color: "var(--foreground)" }} />;\n'
            'const c = <path fill="currentColor" stroke="none" />;'
        )
        self.assertEqual(L.script_style_hits(code, "x.tsx"), [])

    def test_the_exempt_list_gives_a_reason(self) -> None:
        for (path, group), why in L.EXEMPT.items():
            self.assertTrue((L.ROOT / path).is_file(), path)
            self.assertIn(group, L.STYLE_GROUPS)
            self.assertTrue(why.strip())


if __name__ == "__main__":
    unittest.main()
