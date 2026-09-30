# Oxagen house system

One design system for everything a customer sees from **Oxagen** and **Stella**:
the colours, the type, the two logos, the icons, the spinner, the wallpapers,
the social art, the ads, and the content cards.

**Start with [`playbook.html`](playbook.html).** It shows every asset, adapts
to light and dark, and works offline.

**Writing copy? Start in [`messages/`](messages/).** The registry holds every
line with its status, scope, evidence, and owner. [`message-bank.html`](message-bank.html)
is generated from it and shows every line, the held ones marked with their gate.

## The decision

The Oxagen brand kit is the house kit. It already had the right bones: Space
Grotesk and a wordmark whose only colour is one gold letter. This system takes
that kit as the base and brings Stella onto it. Since September 2026 it sits
on obsidian `#09090B` and white, with neutral zinc greys between, so the gold
is the only warm value on a screen.

- **oxagen** is the kit's wordmark, reproduced from the font: the word in
  Space Grotesk 600, lowercase, its **x** in gold.
- **stella\*** is the same word treatment followed by the font's own asterisk,
  in the same gold. The asterisk is a character, not a drawing. It is never
  redrawn.

Both are set at one em (the size the kit froze `oxagen` at), so they are the
same letter size exactly and the same height to within a pixel.

The gold is `#D4AF37`. Its two neighbours are derived from it in OKLCH, not
picked: `#F1CE65` is the highlight the shimmer passes through, and `#8A7223`
is gold as text on white, where the metal itself is 2.1:1. Both names carry
the one value, so the two marks cannot drift apart.

Three faces set the type, each with one job. Space Grotesk sets the wordmarks
and h1 to h3. Geist sets h4 to h6 and everything read. Monaspace Neon sets
code, logs, and data. Two size scales sit on top: marketing for pages read
once, app for dashboards read all day.

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
message-bank.html  generated from messages/: every line, pitch, card, ad, and rule, with its status.
finding-wasted-spend.html  the unproductive spend detectors and the 2026-09-27 spend decisions, copied from oxagen-roadmap. Written by hand.
messages/          the message registry: one YAML file per line, schema.json, findings.yaml, index.json (generated)
build/             color.py · typeset.py · fonts.py · pagecss.py · glyphs.py · geom.py · marks.py · surfaces.py · build.py · messages.py · playbook.py
build/reference/   the kit wordmark and logomark this system is checked against
fonts/             Space Grotesk, Geist and Monaspace Neon webfonts, each with its licence
tokens/            house-tokens.css · house-tokens.json · house-tailwind.css · house-fonts.css · next-fonts.ts
ui/                @oxagen/ui: the component kit, its Storybook, and the design-system bundle. Reads tokens/ and fonts/.
logo/svg,png/      wordmarks, icons, the oxagen lockup: dark · light · adaptive · mono · sheen · tiles
icons/             favicons, app icons 16 to 512, maskable 192/512, .ico, .webmanifest
spinners/          the house motion, animated SVG, no script
wallpapers/        desktop 4K/5K/6K · iphone ×3 · glow | quiet | graph | blocks | orbit | word | echo · dark | light
splash/            launch screens for an installed app, every iPhone and iPad size, dark | light, and splash-screens.json
pwa/               install-prompt.js: the card that offers to add a site to the home screen
social/            avatar · x · linkedin · youtube · open graph · dark | light
ads/               from messages/ads/ and messages/always-on/: workforce · authority · equipment · finance · keys · night shift · capacity · driver seat · stella proof · check · 1080×1080 · 1080×1350 · 1200×628 · 300×250
content/           changelog · essay · release · field note · fleet note · always-on cards, 1200×675
skills/            the oxagen-branding Claude Code skill and its installer
```

## Every pixel here is generated

No file in this kit is drawn by hand. Every PNG is a render of the SVG beside
it. Every SVG is emitted from `build/`. The colours live in one file,
`build/color.py`, and the type in another, `build/typeset.py`, so a change
there moves every asset, token file, and the branding skill's own tokens on
the next run.

```sh
python3 -m venv .venv && .venv/bin/pip install fonttools brotli pyyaml
brew install harfbuzz librsvg          # hb-shape and rsvg-convert
.venv/bin/python build/build.py --check   # verify the face, the palette, and the registry, write nothing
.venv/bin/python build/build.py           # every asset
.venv/bin/python build/build.py --svg     # skip the raster pass
.venv/bin/python build/build.py --only ads social   # only these steps
.venv/bin/python build/build.py --only splash       # the launch screens and their table
.venv/bin/python build/playbook.py        # rebuild the document
.venv/bin/python build/messages.py       # rebuild the message bank
.venv/bin/python github-badges/build.py  # rebuild the GitHub badges
```

## Use it in a product

This repo is the design system spec for every Oxagen frontend. A product does
not copy values out of it. It imports the generated files and re-syncs them
when the kit changes.

For a Next.js app on Tailwind CSS v4 with shadcn/ui or Base UI:

```css
/* app/globals.css */
@import "tailwindcss";
@import "./house-tailwind.css";   /* imports house-tokens.css beside it */
```

```tsx
// app/layout.tsx
import { fontVariables } from "@/styles/next-fonts";

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className={fontVariables}>
      <body className="bg-background text-foreground font-sans">{children}</body>
    </html>
  );
}
```

`house-tailwind.css` sets the semantic tokens shadcn components bind to
(`--background`, `--primary`, `--ring`, `--sidebar-*`) for light, `.dark`, and
the OS preference, adds the palette as `bg-ox-*` and `text-ox-*` utilities,
routes h1 to h3, h4 to h6, body, and code to their faces, and defines the two
scales as `text-m-h1` to `text-m-micro` and `text-a-h1` to `text-a-micro`.
`next-fonts.ts` loads its fonts from `../fonts/`, so vendor `tokens/` and
`fonts/` side by side.

The oxagen monorepo vendors these files with
`tools/scripts/sync-brand-assets.mjs`, and CI runs it with `--check`, so a
product that has fallen behind the kit fails its build.

## Components and Storybook

`ui/` is `@oxagen/ui`, the React component kit for Oxagen's frontends. It is
built on Base UI and Tailwind v4, and it reads `tokens/` and `fonts/` in place,
so a token change here reaches every component on the next build.

Storybook shows every component, one story per state. Its toolbar switches each
story between the light and dark themes. A push to main deploys it to
[brand.oxagen.cloud/storybook](https://brand.oxagen.cloud/storybook/).

```sh
cd ui && pnpm install
pnpm storybook              # Storybook on port 6008
pnpm build-storybook        # static Storybook in storybook-static/
pnpm build:design-system    # design-system/: components/bundle.js, bundle.css, index.d.ts
```

CI (`.github/workflows/ui.yml`) typechecks and tests the kit on every pull
request that touches `ui/`, `tokens/`, or `fonts/`. It uploads the static
Storybook as the artifact `storybook-static` and the bundle as
`design-system-bundle`. The bundle sets `window.OxagenUI` and feeds the Claude
Design project named in `ui/.design-sync/config.json`.
[`ui/README.md`](ui/README.md) lists the components and the rules for adding
one.

## Keep agents current

Agents steer from the `oxagen-branding` skill in `skills/`. Its
`assets/tokens.css` and `assets/logo.svg` are written by the build, and
`--check` fails if either drifts, so the numbers an agent reads are the
numbers the products compile. Install the skill as a symlink and `git pull`
here updates every session on the machine.

## Messages

Every line either brand publishes lives in [`messages/`](messages/), one YAML
file per entry: the headline or card itself, its short and long forms, who
reads it, where it is used, whether it is approved, whether it ships at launch
or waits for a capability, the scope sentence its short forms must keep, the
evidence it needs, its owner, and the date to review it. Retired lines stay in
the registry beside what replaced them. [`messages/README.md`](messages/README.md)
describes every field.

**A copy change starts in `messages/`.** `message-bank.html`,
`messages/index.json`, the ad copy, and the social taglines are generated from
it, so nothing downstream is edited by hand and nobody keeps a count of lines.

```sh
python3 build/messages.py --check          # validate the registry and confirm the generated files are current
python3 build/messages.py                  # write message-bank.html and messages/index.json
.venv/bin/python build/build.py --only ads social   # render the ads and taglines from the registry
```

The check fails on missing fields, a held entry without a gate, dashes or
exclamation points, words the voice guide avoids, unscoped claims, prospect
names, retired text in an approved entry, and any file in `ads/` that no
approved, launch-released ad entry produces.

## Install the branding skill

`skills/oxagen-branding/` is the Claude Code skill that carries the positioning,
the voice, the vocabulary, and worked examples, beside the marks it describes.
It is the source of truth for every word either brand publishes. The oxagen
monorepo vendors it through its own sync script; everything else installs it
from here.

```sh
skills/install.sh                          # link it into ~/.claude/skills, for every project on this machine
skills/install.sh --project ~/Projects/x   # copy it into one project's .claude/skills
skills/install.sh --check                  # does the installed skill match this checkout?
```

The per-user install is a symlink, so `git pull` here is the update. This skill
supersedes the older `brand-voice-guidelines` skill some machines still carry
under `~/.claude/skills`; the installer leaves that one alone.

For a PWA, copy `icons/oxagen-*.png`, `icons/oxagen-favicon.ico` and
`icons/oxagen.webmanifest` into the app's public folder and point at them:

```html
<link rel="icon" href="/oxagen-favicon.ico" sizes="any">
<link rel="icon" href="/oxagen-favicon.svg" type="image/svg+xml">
<link rel="apple-touch-icon" href="/oxagen-icon-180.png">
<link rel="manifest" href="/oxagen.webmanifest">
```

An installed app opens on a launch screen. iOS and iPadOS show one only when a
`<link rel="apple-touch-startup-image">` names an image the exact size of the
screen, so `splash/` holds the `word` phone wallpaper (the wordmark on the
glow) at every current iPhone and iPad size, upright and, for an iPad, on its
side, on ink and on paper. `splash/splash-screens.json` lists each screen with
the media query Safari matches it on. Write the links from that table:

```html
<link rel="apple-touch-startup-image"
      media="(device-width: 393px) and (device-height: 852px) and (-webkit-device-pixel-ratio: 3) and (orientation: portrait) and (prefers-color-scheme: dark)"
      href="/splash/oxagen-splash-1179x2556-dark.png">
```

Android draws its own launch screen from the manifest's `background_color`
and icon, so it needs nothing more.

`pwa/install-prompt.js` is the card that offers to add the site to the home
screen. It shows once, on a phone or tablet, the first time a person visits.
On Android and Chromium its button opens the browser's install dialog; on
iPhone and iPad it says where the command is (Share, then Add to Home Screen).
Closing it, answering the dialog, or installing sets the `ox_install_prompt`
cookie for a year, and clearing cookies brings the card back. It has no
dependencies. Load it as a plain script, and pass translated strings as data
attributes when the product has a message catalogue:

```html
<script src="/install-prompt.js" defer data-icon="/oxagen-icon-192.png"></script>
```

The pages this site serves carry all of it themselves (`build/pwa.py`).

Every raster icon also comes on a white tile, named with `-light`
(`oxagen-icon-light-180.png`, `oxagen-favicon-light.ico`,
`oxagen-light.webmanifest`), for an app whose shell is light. Point at them
with `media="(prefers-color-scheme: light)"` or use them in place of the dark
set.

`--check` reproduces the kit's shipped `oxagen` wordmark from the font (same
weight, same em, HarfBuzz spacing including kerning) and fails if the geometry
has moved. It also fails if a gold neighbour stops matching its OKLCH
derivation, if any text token drops below AA on its ground, if a type step
sets Space Grotesk below 20 px, if a webfont loses a face or a feature, or if
the skill's tokens or logo drift from the build.

## Rules worth knowing before you use it

- **One glyph is gold.** The x in oxagen, the asterisk in stella. Never a
  second one, never the whole word.
- **Gold is identity and at most one action per screen.** It is never a
  surface and it never encodes a state.
- **Gold as text on white becomes `#8A7223`.** The mark keeps its metal.
  Words do not.
- **Gold is never a paragraph or a whole heading.** It is a mark, a metric
  callout, an indicator pill, the focus ring, or the one action.
- **Nothing sits to the left of stella.** The asterisk is the only mark.
- **Minimum 88 px** for a wordmark, **24 px** for an icon, **120 px** for the
  lockup. Below that, use the favicon.
- **The hive is two colours.** Outlines in the surface's ink, two cells in
  the metal. Never a third colour, never a filled outline, never rotated,
  never a cell moved.
- **The icon is the only picture we own.** No stock illustration, no gradient
  mesh, no 3D render. A surface that needs a picture builds one out of the
  icon -- its outline, its mosaic, a field around it (the `quiet`, `blocks`,
  `graph` and `orbit` wallpapers) -- or simply uses a bigger one. The
  wordmark is the one other thing a ground may carry: the `word` and `echo`
  wallpapers set it alone, with no icon beside it.
- **Every ad explains one operator decision, and keeps its scope.** The
  workforce ad states the job; authority, equipment, spend, and the keys each
  take one ad. The short forms keep the scope of the long ones:
  governed, recorded, mediated. Ad copy comes only from approved,
  launch-released entries in `messages/ads/`.
- **Space Grotesk is for display only.** Nothing below 20 px, and never code.
  Code, terminal output, and data are Monaspace Neon.
