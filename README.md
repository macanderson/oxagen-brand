# oxagen house system

One design system for everything a customer sees from **Oxagen** and **Stella** —
the palette, the type, the two logos, the spinner, the wallpapers, the social
art, the ads, and the templates we publish content in.

**Start with [`playbook.html`](playbook.html).** It explains everything below,
adapts to light and dark, and works offline.

## The decision

Stella's **black and gold on warm paper** is the house system. Oxagen moves onto
it and drops the `›oxagen.sh▮` prompt-and-cursor mark.

Both logos are now the same thing: a lowercase name set in **JetBrains Mono
ExtraBold**, outlined, with **one asterisk at the end and nothing to the left**.
The asterisk is where the two brands separate:

- **stella\*** — all five arms in the house metal, gold `#EFC53F`.
- **oxagen\*** — five arms, five hues, and one of those five *is* Stella's gold
  at the exact shipped value.

Oxagen is the company and Stella is one of the things it makes, so the parent
holds the whole spectrum and the product holds one ray of it. Both names are six
letters and the face is monospaced, so the two wordmarks occupy the **identical
264×96 box** and swap in a layout with nothing else moving.

## Layout

```
playbook.html      the document — read this first
build/             color.py · glyphs.py · marks.py · surfaces.py · build.py · playbook.py
tokens/            house-tokens.css · house-tokens.json
logo/svg,png/      wordmarks and marks — dark, light, adaptive, mono, mono-white, mono-black
icons/             favicons and app icons, 16 → 512
spinners/          the house motion, animated SVG, no script
wallpapers/        desktop 4K/5K/6K · iphone ×3 · aurora | quiet · dark | light
social/            avatar · x · linkedin · youtube · open graph · dark | light
ads/               1080×1080 · 1080×1350 · 1200×628 · 300×250
content/           changelog / essay / release / field-note cards, 1200×675
```

## Every pixel here is generated

No file in this kit is drawn by hand. Every PNG is a render of the SVG beside
it, every SVG is emitted from `build/`, and the gold is **read out of Stella's
own token file** rather than retyped — so recolouring the metal recolours
Oxagen's star, and the two marks cannot drift apart.

```sh
python3 build/build.py          # every asset
python3 build/build.py --svg    # skip the raster pass
python3 build/playbook.py       # rebuild the document
```

Needs `fonttools`, `brotli` and `rsvg-convert` (`brew install librsvg`).
`build/glyphs.py` has a `verify()` that reproduces Stella's shipped wordmark
geometry from the font; if that fails, the transform has moved and every logo
in the kit is wrong.

## Rules worth knowing before you use it

- **Nothing sits to the left of the word.** The star is the only mark.
- **Gold never encodes a state.** It is identity and at most one primary action
  per screen. A gold "active" sits 1.3:1 from a warning amber.
- **Gold as *text* on warm paper becomes `#806607`.** The mark keeps its metal;
  words do not.
- **Minimum 96 px** for the wordmark, **24 px** for the star alone.
- **The star is the only picture we own.** No stock illustration, no gradient
  mesh, no 3D render.
