# Oxagen house system

One design system for everything a customer sees from **Oxagen** and **Stella**:
the colours, the type, the two logos, the icons, the spinner, the wallpapers,
the social art, the ads, and the content cards.

**Start with [`playbook.html`](playbook.html).** It shows every asset, adapts
to light and dark, and works offline.

## The decision

The Oxagen brand kit is the house kit. It already had the right bones: Space
Grotesk, a warm near-black and a warm off-white, and a wordmark whose only
colour is one gold letter. This system takes that kit as the base and brings
Stella onto it.

- **oxagen** is the kit's wordmark, reproduced from the font: the word in
  Space Grotesk 600, lowercase, its **x** in gold.
- **stella\*** is the same word treatment followed by the font's own asterisk,
  in the same gold. The asterisk is a character, not a drawing. It is never
  redrawn.

Both are set at one em (the size the kit froze `oxagen` at), so they are the
same letter size exactly and the same height to within a pixel.

The gold is the kit's Bronze Gold `#C58A32` lifted one step in OKLCH: a little
lighter, a little richer, a few degrees toward yellow, so it reads as gold
rather than copper. That is `#D6962C`. `#F1C364` is the highlight the shimmer
passes through; `#8B5E1A` is gold as text on paper. Both names carry the one
value, so the two marks cannot drift apart.

Where a square is required, Stella uses its asterisk and Oxagen uses the **ox
graph**: a hollow node (the o) wired to four context blocks on the diagonals
(the x). One node connected to many, every edge running both ways. The blocks
and their edges are gold; the node takes the letter colour, exactly as the
wordmark paints `ox`. It is nine primitives, a ring, four lines and four
rounded squares, so it survives a 16 px favicon and a 6K wallpaper alike.
The kit's continuous-loop monogram is retired (September 2026); its file
stays in `build/reference/` as history.

Oxagen alone has a lockup: the graph centred on the x-height band, a third
taller than it, a gap of four tenths of the x-height, then the word. Stella
has none; its asterisk is already in the word.

## Layout

```
playbook.html      the document. Read this first.
build/             color.py · glyphs.py · geom.py · marks.py · surfaces.py · build.py · playbook.py
build/reference/   the kit wordmark and logomark this system is checked against
fonts/             Space Grotesk, variable and static, with its licence
tokens/            house-tokens.css · house-tokens.json
logo/svg,png/      wordmarks, icons, the oxagen lockup: dark · light · adaptive · mono · sheen · tiles
icons/             favicons and app icons, 16 to 512
spinners/          the house motion, animated SVG, no script
wallpapers/        desktop 4K/5K/6K · iphone ×3 · glow | quiet | graph | blocks | orbit · dark | light
social/            avatar · x · linkedin · youtube · open graph · dark | light
ads/               bill · memory · waste · proof · 1080×1080 · 1080×1350 · 1200×628 · 300×250
content/           changelog · essay · release · field note cards, 1200×675
```

## Every pixel here is generated

No file in this kit is drawn by hand. Every PNG is a render of the SVG beside
it. Every SVG is emitted from `build/`. The colours live in one file,
`build/color.py`, so a change there moves every asset on the next run.

```sh
python3 -m venv .venv && .venv/bin/pip install fonttools brotli
brew install harfbuzz librsvg          # hb-shape and rsvg-convert
.venv/bin/python build/build.py --check   # verify the face and the palette, write nothing
.venv/bin/python build/build.py           # every asset
.venv/bin/python build/build.py --svg     # skip the raster pass
.venv/bin/python build/playbook.py        # rebuild the document
```

`--check` reproduces the kit's shipped `oxagen` wordmark from the font (same
weight, same em, HarfBuzz spacing including kerning) and fails if the geometry
has moved. It also fails if the pinned gold stops matching its derivation from
the kit's Bronze Gold, or if any text token drops below AA on its ground.

## Rules worth knowing before you use it

- **One glyph is gold.** The x in oxagen, the asterisk in stella. Never a
  second one, never the whole word.
- **Gold is identity and at most one action per screen.** It is never a
  surface and it never encodes a state.
- **Gold as text on warm paper becomes `#8B5E1A`.** The mark keeps its metal;
  words do not.
- **Nothing sits to the left of stella.** The asterisk is the only mark.
- **Minimum 88 px** for a wordmark, **24 px** for an icon, **120 px** for the
  lockup. Below that, use the favicon.
- **The icon and its parts are the only pictures we own.** A node, an edge, a
  context block. No stock illustration, no gradient mesh, no 3D render. A
  surface that needs a picture builds one from those parts (the `graph`,
  `blocks` and `orbit` wallpapers) or uses a bigger icon.
- **Every ad opens on the reader's pain.** The bill, the re-explaining, the
  waste. The mark answers; it never leads.
- **Space Grotesk is not a code face.** Terminal output and code stay in the
  system monospace.
