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

Where a square is required, Stella uses its asterisk and Oxagen uses **the
hive**: six hexagonal cells on a honeycomb grid, four drawn as an outline and
two filled with the metal, one of them at half strength. It is the knowledge
graph as a picture -- a lattice, with the parts Oxagen has learned lit up --
and it is built from five numbers rather than drawn: a cell's height and
width, the pitch along a row, the pitch between rows, and the outline's
weight. The cells are a touch wider than a regular hexagon, which is what
makes the cluster stand square.

**The hive is two colours, and only two.** Its outlines take the colour of
whatever it sits on -- paper on ink, ink on paper, `currentColor` in the
adaptive files -- and its two lit cells take the metal: flat gold in the
plain files, the metal lit from above in the tiles. A mono file paints all
of it one colour. It is the app icon, the favicon and the avatar; the
wordmark is still what Oxagen prefers wherever there is room for a word.

The kit's continuous-loop monogram, the ox graph and the `Ox` lettermark are
all retired (September 2026); the kit's own file stays in `build/reference/`
as history.

Oxagen alone has a lockup: the hive, a gap, then the word. The hive stands a
quarter taller than the wordmark's box and centres on it. Stella has no
lockup; its asterisk is already in the word.

## Layout

```
playbook.html      the document. Read this first.
build/             color.py · glyphs.py · geom.py · marks.py · surfaces.py · build.py · playbook.py
build/reference/   the kit wordmark and logomark this system is checked against
fonts/             Space Grotesk, variable and static, with its licence
tokens/            house-tokens.css · house-tokens.json
logo/svg,png/      wordmarks, icons, the oxagen lockup: dark · light · adaptive · mono · sheen · tiles
icons/             favicons, app icons 16 to 512, maskable 192/512, .ico, .webmanifest
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

For a PWA, copy `icons/oxagen-*.png`, `icons/oxagen-favicon.ico` and
`icons/oxagen.webmanifest` into the app's public folder and point at them:

```html
<link rel="icon" href="/oxagen-favicon.ico" sizes="any">
<link rel="icon" href="/oxagen-favicon.svg" type="image/svg+xml">
<link rel="apple-touch-icon" href="/oxagen-icon-180.png">
<link rel="manifest" href="/oxagen.webmanifest">
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
- **The hive is two colours.** Outlines in the surface's ink, two cells in
  the metal. Never a third colour, never a filled outline, never rotated,
  never a cell moved.
- **The icon is the only picture we own.** No stock illustration, no gradient
  mesh, no 3D render. A surface that needs a picture builds one out of the
  icon -- its outline, its mosaic, a field around it (the `quiet`, `blocks`,
  `graph` and `orbit` wallpapers) -- or simply uses a bigger one.
- **Every ad opens on the reader's pain, and answers it in one line.** The
  bill, the re-explaining, the waste. Under the headline sits one sentence
  saying what Oxagen does about it: it teaches your agents your business,
  governs what they may do, explains every run, or learns from each one. One
  of the four to an ad, all four across the campaign.
- **Space Grotesk is not a code face.** Terminal output and code stay in the
  system monospace.
