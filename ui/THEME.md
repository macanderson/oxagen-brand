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
| What type scale and utilities exist? | `../tokens/house-tailwind.css`, with the `text-m-*` marketing and `text-a-*` app scales |
| Which font files load, and how? | `../tokens/house-fonts.css` and `../fonts/` |
| How do tokens map to semantic roles, per theme? | `src/styles/globals.css`: the `:root`, `.dark`, and `prefers-color-scheme` blocks, then the v3 layer at the end of the file |
| Where do the values come from? | `../theme/theme.json`, which `../build/color.py` and `../build/typeset.py` read |
| What may a surface say? | `../skills/oxagen-branding/`, whose `references/positioning.md` carries the live and retired lines |

The token files are generated. `build/build.py` writes them from
`theme/theme.json`, and `build/build.py --check` fails when a token drops below
AA on its ground or a generated file differs from the theme. Change a value in
`theme/theme.json`, run the build, and commit what it writes. Never edit a
generated file by hand.

`globals.css` is the one stylesheet the kit authors by hand, and it is the whole
reskin surface. It maps the house values onto the semantic roles components
use. A component never names a house token, a Tailwind palette colour, or a
hex.

The v3 layer at the end of `globals.css` came from the oxagen app with the
components in `src/components/`. It sets the gold primary, the panel and rule
tokens, table truncation, the phone rules, and the shimmer and spinner motion.
It comes last, so it wins on cascade order.

Corners, shadows, and type sizes are declared once, in the layers above it, and
each reads an `--ox-*` token. The radius scale reads `--ox-radius-xs` to
`--ox-radius-4xl`, which multiply `--ox-radius-base`. The shadow scale reads
`--ox-shadow-ui` and `shadow-pop` reads `--ox-shadow-pop`, each with its `-ink`
twin on paper. Heading line heights read the app scale's `--ox-a-*-leading`
steps. `build/build.py --check` fails on a literal corner, shadow, font size,
or heading line height in `globals.css` that its allowlist does not name.

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
