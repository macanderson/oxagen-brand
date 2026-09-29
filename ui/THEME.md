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
| What type scale and utilities exist? | `../tokens/house-tailwind.css`, with the `text-m-*` marketing and `text-a-*` app scales |
| Which font files load, and how? | `../tokens/house-fonts.css` and `../fonts/` |
| How do tokens map to semantic roles, per theme? | `src/styles/globals.css`: the `:root`, `.dark`, and `prefers-color-scheme` blocks, then the v3 layer at the end of the file |
| Where do the values come from? | `../build/color.py` for colour and `../build/typeset.py` for type |
| What may a surface say? | `../skills/oxagen-branding/`, whose `references/positioning.md` carries the live and retired lines |

The first three are generated. `build/build.py` writes them from `color.py` and
`typeset.py`, and `build/build.py --check` fails when a token drops below AA on
its ground. Change a value in `build/`, run the build, and commit what it
writes. Never edit a generated file by hand.

`globals.css` is the one stylesheet the kit authors by hand, and it is the whole
reskin surface. It maps the house values onto the semantic roles components
use. A component never names a house token, a Tailwind palette colour, or a
hex.

The v3 layer at the end of `globals.css` came from the oxagen app with the
components in `src/components/`. It sets the gold primary, the radius scale on
`--ui-radius`, the panel and rule tokens, table truncation, the phone rules, and
the shimmer and spinner motion. It comes last, so it wins on cascade order.

## Three rules a value cannot state

**Gold is identity and action, never state.** A screen has at most one gold
action. A gold border, dot, or label that means "running", "passed", or "held"
is a defect. State has its own ramp, `--ox-st-*`.

**Each state has two stops, and both are marks.** The bare name is the mark on
ink, and the `-ink` suffix is the mark on paper. A mark clears 3:1, which is
too low for words. A token that renders text needs a derived stop, with its
measured ratio in a comment beside it. `--error-ink` is the one that exists.
`build.py --check` measures the house tokens but not the pairs `globals.css`
derives, so that comment is the only record of the ratio.

**Every theme block states every pair.** `globals.css` carries the dark theme
twice, under `.dark` and under `prefers-color-scheme`. A value set in one block
and not the other makes a surface change colour depending on whether the reader
chose the theme or the operating system did. Keep both blocks in step.

## For the design-sync bundle

`.design-sync/config.json` reads this file as its guidelines document. It stays
short on purpose: a generator handed a stale palette produces stale designs.
The tokens reach the bundle as `bundle.css`, and a designer or a generator
reads them there.
