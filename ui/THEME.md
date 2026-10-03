# Oxagen theme

This file restates no token value. It says where each answer lives, because a
document that copies the palette becomes a second authority the moment the
palette moves.

The kit sits beside the tokens it reads. `src/styles/globals.css` imports
`../tokens/` and the fonts load from `../fonts/`, so the kit has no copy to
drift and no sync step.

## Where the truth lives

| Question | Read |
|---|---|
| What is every token worth? | `../tokens/house-tokens.css`, and `house-tokens.json` for the same values as data |
| Which corner, shadow, and spacing unit? | `--ox-radius-base` and its steps `--ox-radius-*`, `--ox-shadow-ui` and `--ox-shadow-pop` (each with an `-ink` twin for paper), and `--ox-space`, all in `../tokens/house-tokens.css` |
| What type scale and utilities exist? | `../tokens/house-tailwind.css`, with the `text-m-*` marketing and `text-a-*` app scales, and `../tokens/house-text-scale.css`, which points Tailwind's `text-xs` to `text-3xl` at the app steps |
| Which face and size does each surface take? | The Type section of `../skills/oxagen-branding/references/system.md` |
| Which font files load, and how? | `../tokens/house-fonts.css` and `../fonts/` |
| How do tokens map to semantic roles, per theme? | `src/styles/globals.css`: the `:root`, `.dark`, and `prefers-color-scheme` blocks, with one definition of each semantic token per theme |
| Where do the values come from? | `../theme/theme.json`, which `../build/color.py` and `../build/typeset.py` read |
| What may a surface say? | `../skills/oxagen-branding/`, whose `references/positioning.md` carries the live and retired lines |

The token files are generated. `build/build.py` writes them from
`theme/theme.json`, and `build/build.py --check` fails when a token drops below
AA on its ground or a generated file differs from the theme. Change a value in
`theme/theme.json`, run the build, and commit what it writes. Never edit a
generated file by hand.

`globals.css` is the one stylesheet the kit authors by hand, and it is the whole
reskin surface. It maps the house values onto the semantic roles components
use. A component never names a Tailwind palette colour or a hex. It names a
house token only to read a type step, as `text-(length:--ox-a-h4)` does.

The v3 design came from the oxagen app with the components in
`src/components/`. Its tokens, such as the gold primary button and the panel
and rule tokens, sit at the end of each theme block. Each semantic token has
one definition per theme: `:root` for light, `.dark` for dark, and the
`prefers-color-scheme` block, which repeats `.dark` for a dark OS with no
class. `build/css_literals.py` fails when a token is declared twice in one
block, or when a later `:root` declaration would override a `.dark` one. Table
truncation, the phone rules, and the shimmer and spinner motion sit after the
utilities.

Each corner, shadow, font size, and heading line height in `globals.css` is
declared once and reads an `--ox-*` token. The radius and shadow scales sit in
the mapping layer. The radius scale reads `--ox-radius-xs`
to `--ox-radius-4xl`, which multiply `--ox-radius-base`. The shadow scale reads
`--ox-shadow-ui` and `shadow-pop` reads `--ox-shadow-pop`, each with its `-ink`
twin on paper. `h1`, `h2`, and `h3` read `--ox-a-h1-leading`,
`--ox-a-h2-leading`, and `--ox-a-h3-leading`, as product's `packages/ui` does.
`h4` to `h6` read `--ox-a-h4-leading`.

`h1` to `h3` take `--font-heading`, which is Aeonik in the kit, as in the app.
A Pages/Website story points it at `--font-display`, Space Grotesk, as a
marketing or docs site does in its own stylesheet. `h4` to `h6` take
`--font-sans`, Aeonik, on every surface.

`globals.css` imports `../tokens/house-text-scale.css` after
`house-tailwind.css`, so Tailwind's named sizes read the app steps in order.
`text-base` is the app base, `text-sm` is micro, `text-xs` is 2xs, and
`text-lg` to `text-3xl` are h4 to h1. Running text, controls, inputs, buttons,
menu items, and table body cells take `text-base`. Labels, badges, timestamps,
and table headers take `text-sm` or `text-xs`.

Every type step is `calc()` over its scale's base, `--ox-m-base` or
`--ox-a-base`. A new base in `theme/theme.json` moves every step on the next
build. The theme editor writes only the values that differ from the shipped
theme on `<html>`. A new base writes `--ox-a-base` or `--ox-m-base` alone, and
every step on the page follows it as you change it. Set the base on `:root`.
Each step is computed where `:root` declares it, so a base set on a
descendant element does not move the steps inside it.

## Literal guard

`build/css_literals.py` is the literal guard, and `build/build.py --check` runs
it. Mac, 2026-10-03: "everything has to be semantic driven from tokens". It
reads two scopes, and `--report` counts what it finds by scope and kind.

- **`globals.css`.** It fails on a literal colour, corner, shadow, space, font
  size, or heading line height in a rule. Its custom properties are the
  mapping layer, which turns raw tokens into semantic ones, so a colour there
  passes. Each semantic token has one definition per theme. A phone's text
  fields read `--text-input-touch`, 16px or the app base, whichever is larger,
  so iOS does not zoom on focus. `KEEP` in `build/css_literals.py` is empty.
- **Every component and page.** It fails on any colour, corner, shadow,
  space, or font size written as a literal in `ui/src` (the Work and Run app
  copies included), `sdlc/public`, `pwa/`, and the kit's pages
  (`playbook.html`, `message-bank.html`, `always-on.html`, and
  `brand-guide.html`). That covers a Tailwind class (a palette colour such as
  `bg-zinc-800`, a raw house colour such as `bg-ox-gold`, Tailwind's fixed
  bare `rounded`, and an arbitrary value such as `gap-[7px]`, `rounded-[10px]`,
  `shadow-[…]`, `bg-[#fff]`, or `text-[13px]`), a style object's value, an
  SVG colour attribute, and CSS in a style block, a `style` attribute, or a
  string. A custom property in a stylesheet is that file's token layer, so it
  passes. Tests are not read, because they name classes to assert them.
  `EXEMPT` names the one file a kind skips: the generated brand marks.
- **Contrast.** Every semantic text role clears 4.5:1 on the page, a card, a
  popover, a lifted row, and a panel header, in both themes. No word is set in
  dim, which is below 4.5:1. Gold words are checked on the page, a card, and a
  popover until #93 decides the gold for words on a lifted row.

A size passes when it reads a token: `var(--ox-a-body)`,
`text-(length:--ox-a-h2)`, a house utility (`text-m-*`, `text-a-*`), or
Tailwind's `text-xs` to `text-3xl`, which read the app steps. A size of 1em or
100% or more passes too, since it never sets text below its parent.
`sdlc/public/sdlc.css` names the type steps once, because that site cannot
import `tokens/`, and the guard holds those names to the theme's values.

## Three rules a value cannot state

**Gold is identity and action, never state.** A screen has at most one gold
action. A gold border, dot, or label that means "running", "passed", or "held"
is a defect. State has its own ramp, `--ox-st-*`.

**Marks use the bare stops, and words use the text stops.** Each state has
four. `--ox-st-failed` is the mark on ink and `--ox-st-failed-ink` the mark on
paper: a badge, a dot, a border, or a fill, which needs 3:1.
`--ox-st-failed-text` is the word on ink and `--ox-st-failed-text-ink` the word
on paper, and each clears 4.5:1 on every surface of its theme: ink, panel, and
the lifted row, or paper and paper-hl. The destructive red follows the same
pattern. On paper a text stop equals its mark today. Use it anyway, because the
split is what keeps a word legible when a mark moves. `globals.css` maps the
text stops onto `--error-ink`, `--success-ink`, `--warning-ink`, `--info-ink`,
`--proven-ink`, and `--critical-ink`, and `build.py --check` measures every
one, so no text stop is derived by hand here. Secondary text on paper is
`--ox-muted-text-ink`, which clears 4.5:1 on paper-hl, where `--ox-muted-ink`
does not.

**Every theme block states every pair.** `globals.css` carries the dark theme
twice, under `.dark` and under `prefers-color-scheme`. A value set in one block
and not the other makes a surface change colour depending on whether the reader
chose the theme or the operating system did. Keep both blocks in step.

## For the design-sync bundle

`.design-sync/config.json` reads this file as its guidelines document. It stays
short on purpose: a generator handed a stale palette produces stale designs.
The tokens reach the bundle as `bundle.css`, and a designer or a generator
reads them there.
