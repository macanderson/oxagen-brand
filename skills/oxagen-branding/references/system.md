# Visual system

Source of truth: `build/color.py` and `build/typeset.py` in `macanderson/oxagen-brand`, which generate every token file, mark, and asset. `assets/tokens.css` is generated from them, and the build fails if it drifts. Use it; do not retype a value. A Next.js product imports `tokens/house-tailwind.css` and `tokens/next-fonts.ts` from the kit instead.

## Ground and surfaces

Dark first. Obsidian ground `#09090B`, panel `#18181B`, highlight and border `#27272A`, heavier rule `#3F3F46`. The light theme is white: `#FFFFFF` ground and panel, highlight `#F4F4F5`, border `#E4E4E7`. A card on white is a hairline, not a tint. Every asset ships both themes, toggled by `data-theme` or the OS preference. Never ship a dark-only page.

The greys are neutral zinc and carry no hue, so the gold is the only warm value on a screen.

## Text

| Role | On obsidian | On white |
|---|---|---|
| primary | `#FFFFFF` (19.9:1) | `#09090B` (19.9:1) |
| body | `#E4E4E7` (15.7:1) | `#27272A` (14.9:1) |
| secondary | `#A1A1AA` (7.8:1) | `#71717A` (4.8:1) |
| quietest | `#71717A` (4.1:1) | `#A1A1AA` (2.6:1) |

Every text role that carries meaning clears 4.5:1 on its ground, and the build checks it. On a lifted row in the light theme (`#F4F4F5`), secondary text is `#6E6E77` (`muted-text-ink`, 4.6:1), because `#71717A` is 4.4:1 there. The quietest shade is for placeholders and decoration, never for a word the reader needs. On obsidian, secondary text may also be the primary colour at reduced opacity (`text-white/60`), so it takes the tone of the ground; never a flat mid grey below 4.5:1.

## Gold

`#D4AF37`, bright `#F1CE65`, deep `#8A7223`. The bright and deep shades are derived from the gold in OKLCH, not picked. Gold is the identity. It appears in the hive's two lit cells, the x of oxagen, and the asterisk of stella, and on at most one action per screen. The focus ring is gold too, because it marks where the one action is. Gold is never a state colour, never a surface fill, never a border on a card, never a highlight on a row, and never a paragraph or a full heading. If a second gold thing appears on a screen, one of them is wrong.

Gold on obsidian is 9.5:1. Gold on white is 2.1:1, so gold as text on white is always the deep shade (4.7:1). The mark keeps its metal; words do not.

## State by shape

Verdicts and statuses are carried by border shape, not colour, so they survive grayscale, print, and the light theme unchanged.

| State | Shape |
|---|---|
| held, allowed, proven | double border, 3px |
| pending, approval | dashed border |
| broken, denied, failed | single border |

The semantic colours (`--state-allowed`, `--state-approval`, `--state-denied`, `--state-proven`, `--state-failed`, `--state-critical`) exist for badges and dots inside tables where shape alone is too small to read. They are never the only signal. The destructive red (`#D5584D` on obsidian, `#992F28` on white) is the one state colour that is also a button fill, and it clears 4.5:1 on its ground both ways.

A state colour is a mark, and a mark needs only 3:1. A word in a state's colour takes the state's text stop: `--state-failed-text` in `assets/tokens.css`, or `--ox-st-failed-text` on obsidian and `--ox-st-failed-text-ink` on white in the token files. Each text stop clears 4.5:1 on every surface of its theme: the ground, a panel, and a lifted row. On obsidian the text stops sit at one OKLCH lightness, so `#E7685C` is failed as words where `#C0453C` is failed as a dot. On white each text stop equals its mark today. Use the text stop anyway, so a word stays legible when a mark moves.

## Type

Three faces, each with one job. Mac set the current rule on 2026-09-29.

- **Geist** is the text face: every heading from h1 to h6, body, labels, buttons, tooltips, tables, navigation. Everything read. Small headings take weight 500 or 600 to separate from body.
- **Space Grotesk** is the wordmark face. It sets three things only: the Oxagen wordmark, the stella wordmark, and line 1 of the oxagen.sh hero. Nothing in it is set below 20px, because its wide geometric letters lose their shape at small sizes.
- **Monaspace Neon** is the code face: code, commands, terminal output, logs, digests, paths, frame kinds, verdict values, ids, and the numbers in tables. Texture healing and code ligatures are on (`font-feature-settings: "calt", "liga"`).

No fourth typeface, ever. In CSS the faces are `--font-sans` (the kit's pages call it `--font`), `--font-wordmark`, and `--font-mono`. `--font-display` is the heading role, and it points at Geist. `text-m-hero` sets line 1 of the oxagen.sh hero in Space Grotesk. All three ship in the kit's `fonts/` under the SIL Open Font License. Headings are sentence case.

Two scales. A surface picks one and keeps it.

| Step | Face | Marketing (`text-m-*`) | App (`text-a-*`) |
|---|---|---|---|
| hero | Space Grotesk | 72px, 1.05, 700, -0.03em | none |
| h1 | Geist | 72px, 1.05, 700, -0.03em | 30px, 1.15, 700, -0.02em |
| h2 | Geist | 40px, 1.2, 700, -0.01em | 24px, 1.2, 600 |
| h3 | Geist | 28px, 1.3, 600 | 20px, 1.25, 600 |
| h4 | Geist | 20px, 1.4, 500 | 16px, 1.4, 600 |
| body | Geist | 18px, 1.65, 400 | 14px, 1.5, 400 |
| micro | Monaspace Neon | 14px, 1.5, 400 | 12px, 1.4, 400 |

The hero step is for line 1 of the oxagen.sh hero and nothing else. Marketing is for landing pages, posts, and anything read once: large and spaced. App is for dashboards, panels, tables, terminals, and logs read all day: dense. An eyebrow is 12px Geist, uppercase, at 0.14em tracking.

## Layout

Wrap 1120px, 24px side padding. Card radius 12px on the website. The app's card is `rounded-2xl` on the shadcn preset scale: 1.8 times a 0.45rem base, about 13px (oxagen ADR-221). Section rhythm: 44px vertical, 1px border on top. Grid gaps 16px. Tables sit inside a rounded, bordered, horizontally scrolling container with a highlight header row.

The eyebrow above an h2 is muted, except the first one on a page, which is gold and counts as the identity, not as the action.

## Marks

`assets/logo.svg` is the oxagen lockup: the hive, a gap, then the wordmark. The hive's two lit cells and the x are gold and stay gold on every background; everything else is `currentColor`. Minimum 120px wide for the lockup, 88px for a wordmark alone, 24px for an icon. Below that, use the favicon. Clear space equal to the height of one cell. Never recolour, outline, or shadow it.

Stella uses the same system with its own mark, `stella*`, whose asterisk is the gold glyph. The mark is the only difference.

## Components that exist

Header with mark and a mono tag. Sticky sub-nav. Eyebrow plus heading. Lead paragraph. Stat card (label, value, sub). Panel. Table container. Numbered method list with square mono markers. Note with a left rule. Verdict card by shape. Phase block with a gate line. Prompt box with a copy action. Toast.

Do not invent a component when one of these fits.

## Ads

Fixed canvases, same tokens, same rules. One gold action. The mark bottom left at 18 to 22px. Copy comes from the message registry at `messages/`, which generates the ad copy. `references/examples.md` shows the current directions. See `ads/` for the approved layouts.
