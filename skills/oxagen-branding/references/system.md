# Visual system

Source of truth: `theme/theme.json` in `oxageninc/brand`. `build/color.py` and `build/typeset.py` read it and generate every token file, mark, and asset. `assets/tokens.css` is generated from it, and the build fails if it drifts. Use it; do not retype a value. A Next.js product imports `tokens/house-tailwind.css` and `tokens/next-fonts.ts` from the kit instead, and `tokens/house-text-scale.css` when it opts in to Tailwind's named sizes on the app steps.

## Ground and surfaces

Dark first. Obsidian ground `#09090B`, panel `#18181B`, highlight and border `#27272A`, heavier rule `#3F3F46`. The light theme is white: `#FFFFFF` ground and panel, highlight `#F4F4F5`, border `#E4E4E7`. A card on white is a hairline, not a tint. Every asset ships both themes, toggled by `data-theme` or the OS preference. Never ship a dark-only page.

The greys are neutral zinc and carry no hue, so the gold is the only warm value on a screen.

## Glass

Glass belongs only on chrome that floats over content: menus, selects, comboboxes, popovers, hover cards, the command menu, toasts, a dialog's scrim, and sticky navigation and header bars. Cards, panels, tables, and text never take it.

- **A floating surface** is the popover ground at 70% over a 40px blur at 150% saturation, with a faint ring in place of a border and a deep shadow. In the kit it is `floatingSurface`.
- **A sticky bar** is the page ground at 72% over a 24px blur at 150% saturation, with a hairline under it. In the kit it is `glassBar`. Text set straight on the bar takes the primary text colour, which stays above 8:1 whatever scrolls under it. Secondary text sits on an opaque control, such as a tab track or a badge.
- **A dialog's scrim** dims the page and blurs it by 3px.
- **Fallbacks.** Where a browser has no `backdrop-filter`, each glass surface is opaque on its own ground. Under `prefers-reduced-transparency: reduce`, each glass surface turns opaque and drops its blur. A scrim keeps its dim either way, since an opaque scrim would hide the page behind the dialog.
- **The blur reads as frosted, never milky.** No white haze on obsidian, no rainbow, no gradient border, and no glow. Glass needs something behind it worth blurring: content scrolling under a bar, the hero's hex field, or a table under an open menu. Gold is never translucent.

`ui/README.md` in the kit carries the recipes, and its `Pages/` stories show the rule at page scale.

## Text

| Role | On obsidian | On white |
|---|---|---|
| primary | `#FFFFFF` (19.9:1) | `#09090B` (19.9:1) |
| body | `#E4E4E7` (15.7:1) | `#27272A` (14.9:1) |
| secondary | `#A1A1AA` (7.8:1) | `#71717A` (4.8:1) |
| quietest | `#71717A` (4.1:1) | `#A1A1AA` (2.6:1) |

Every text role that carries meaning clears 4.5:1 on its ground, and the build checks it. On a lifted row in the light theme (`#F4F4F5`), secondary text is `#6E6E77` (`muted-text-ink`, 4.6:1), because `#71717A` is 4.4:1 there. The quietest shade is for placeholders and decoration, never for a word the reader needs. On obsidian, secondary text may also be the primary colour at reduced opacity (`text-white/60`), so it takes the tone of the ground; never a flat mid grey below 4.5:1.

## Gold

`#D4AF37`, bright `#F1CE65`, deep `#8A7223`, and words `#866D1D`. The neighbours are derived from the gold in OKLCH, not picked. Deep is gold as a mark on white. Gold words on white, a link or an accent word, take the words shade (`--ox-gold-text-ink`, through `--gold-text`), which clears 4.5:1 on white and on a lifted row. Gold is the identity. It appears in the hive's two lit cells, the x of oxagen, and the asterisk of stella, and on at most one action per screen. The focus ring is gold too, because it marks where the one action is. Gold is never a state colour, never a surface fill, never a border on a card, never a highlight on a row, and never a paragraph or a full heading. If a second gold thing appears on a screen, one of them is wrong.

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

Three faces, each with its own job. Mac set this rule on 2026-10-02. It replaces every earlier face and size rule.

- **Aeonik** sets the default text on every surface: body, labels, buttons, tooltips, tables, and navigation. It sets h1 to h3 in the web app (app.oxagen.sh) and the internal tools (roadmap.oxagen.cloud, gtm.oxagen.cloud). It sets every h4 to h6 on every surface. Small headings take weight 500 or 600 to stand apart from body. Its italic ships beside it, so `em` draws the real italic.
- **Space Grotesk** sets h1 to h3 on the marketing and customer sites: oxagen.sh, docs.oxagen.sh, stella.oxagen.sh and its docs, and survey.oxagen.cloud. It also sets the oxagen and stella wordmarks and Stella's asterisk icon, and that use is fixed. Nothing in Space Grotesk is set below 20px, because its wide letters lose their shape there.
- **Monaspace Neon** is the code face: code, commands, terminal output, logs, digests, paths, frame kinds, verdict values, ids, and the numbers in tables. Texture healing and code ligatures are on (`font-feature-settings: "calt", "liga"`).

The kit's own pages follow the same split. `playbook.html`, `brand-guide.html`, sdlc.oxagen.sh, and the Pages/Website stories are customer pages. `message-bank.html`, the theme editor, the Pages/App stories, and the page chrome of `always-on.html` are internal tools. The website sections that `always-on.html` previews are marketing.

No fourth role face. In CSS a rule names a role, never a face. Five roles carry the three faces:

- `--font-sans` is Aeonik, the default text.
- `--font-display` is Space Grotesk, for h1 to h3 on a marketing or customer site. `text-m-h1` to `text-m-h3` read it.
- `--font-heading` is the face h1 to h3 take on the surface. It reads `--font-sans`, so a bare h1 to h3 and `text-a-h1` to `text-a-h3` draw Aeonik. A marketing or docs site sets its h1 to h3 in Space Grotesk with one line in its own stylesheet: `:root { --font-heading: var(--font-display); }`.
- `--font-mono` is Monaspace Neon.
- `--font-wordmark` is Space Grotesk, for a wordmark set as text rather than drawn. It stays Space Grotesk whatever face `--font-display` takes.

The token files name the same roles `--ox-font`, `--ox-font-display`, `--ox-font-heading`, `--ox-font-mono`, and `--ox-font-wordmark`. A site that reads them sets its h1 to h3 in Space Grotesk with `h1, h2, h3 { font-family: var(--ox-font-display); }`. `assets/tokens.css` and the kit's pages call the text role `--font` and the code role `--mono`. Aeonik Mono and Aeonik Fono ship in the kit's `fonts/` too and load as their own families, and no role takes either one yet. Headings are sentence case.

Two scales. Each has one base, and every step is the base times its ratio. Each cell gives the size at the shipped base, the ratio, the line height, the weight, and the tracking.

| Step | Marketing face | Marketing (`text-m-*`) | App face | App (`text-a-*`) |
|---|---|---|---|---|
| base | | 16px, `--ox-m-base` | | 14px, `--ox-a-base` |
| h1 | Space Grotesk | 72px, ×4.5, 1.05, 700, -0.03em | Aeonik | 30px, ×2.142857, 1.15, 700, -0.02em |
| h2 | Space Grotesk | 40px, ×2.5, 1.2, 700, -0.01em | Aeonik | 24px, ×1.714286, 1.2, 600 |
| h3 | Space Grotesk | 28px, ×1.75, 1.3, 600 | Aeonik | 20px, ×1.428571, 1.25, 600 |
| h4 | Aeonik | 20px, ×1.25, 1.4, 500 | Aeonik | 16px, ×1.142857, 1.4, 600 |
| body | Aeonik | 16px, ×1, 1.625, 400 | Aeonik | 14px, ×1, 1.5, 400 |
| micro | Monaspace Neon | 14px, ×0.875, 1.5, 400 | Monaspace Neon | 12px, ×0.857143, 1.4, 400 |
| 2xs | none | none | Aeonik | 10px, ×0.714286, 1.4, 500 |

Marketing is for landing pages and posts: large and spaced. App is for the web app and the internal tools: dense, for dashboards, panels, tables, terminals, and logs. Docs sites are customer sites, so their h1 to h3 take Space Grotesk and their body is 16px. A docs site sets both in its own stylesheet: `--font-heading: var(--font-display)` for the headings, and `--ox-m-body` for the body.

The base is the body size: 16px on the marketing and customer sites, docs included, and 14px in the app and the internal tools. Mac, 2026-10-03: "The base page font size should never be lower than 14px". Every step derives from its scale's base (`--ox-m-base`, `--ox-a-base`) as the base times its ratio, such as `calc(var(--ox-a-base) * 0.857143)` for the app micro step, so a change to the base in `theme/theme.json` or the theme editor moves every step. The theme editor warns when a base goes under 14px. Set the base on `:root`. Each step is computed where `:root` declares it, so a base set on a descendant element does not move the steps inside it.

The smaller steps are for labels, badges, timestamps, and table headers, and dense metadata such as a chart axis: micro (12px) and 2xs (10px) in the app, and micro (14px) on marketing. Running text, control labels, inputs, buttons, menu items, and table body cells take the base, never a smaller step. An eyebrow takes the micro step's size in Aeonik, uppercase, at 0.14em tracking: 14px on a marketing or customer site and 12px in the app, at the shipped bases.

No class or stylesheet writes a font size of its own. Mac, 2026-10-02: "we can't hard code font sizes in classes, we need to let the tokens do their job." Every size reads a step token (`--ox-m-*`, `--ox-a-*`) or a house utility (`text-m-*`, `text-a-*`). A hard-coded small size becomes the nearest smaller step, never a literal. In this kit, `build/css_literals.py` fails on a hard-coded size.

In a Tailwind product, `tokens/house-tailwind.css` keeps `text-xs` and `text-sm` on the app base, so a product that syncs it keeps its sizes. A product opts in to the app steps by importing `tokens/house-text-scale.css` after it. Tailwind's named sizes then read the steps in order:

| Tailwind | App step | Size at the base |
|---|---|---|
| `text-xs` | 2xs | 10px |
| `text-sm` | micro | 12px |
| `text-base` | body, the base | 14px |
| `text-lg` | h4 | 16px |
| `text-xl` | h3 | 20px |
| `text-2xl` | h2 | 24px |
| `text-3xl` | h1 | 30px |

Rename the product's classes in the same change that adds the import: body text in `text-sm` becomes `text-base`, and a label in `text-xs` becomes `text-sm`. A text field on a phone takes `text-input-touch`, which is 16px or the app base, whichever is larger, so iOS Safari never zooms on focus and the field still follows a larger base.

## Layout

Wrap 1180px (`--ox-wrap`), 24px side padding. Every site uses the same wrap (Mac, 2026-10-02). Card radius 12px on the website. The app's card is `rounded-2xl` on the shadcn preset scale: 1.8 times a 0.45rem base, about 13px (oxagen ADR-221). Section rhythm: 44px vertical, 1px border on top. Grid gaps 16px. Tables sit inside a rounded, bordered, horizontally scrolling container with a highlight header row.

The eyebrow above an h2 is muted, except the first one on a page, which is gold and counts as the identity, not as the action.

## Marks

`assets/logo.svg` is the oxagen lockup: the hive, a gap, then the wordmark. The hive's two lit cells and the x are gold and stay gold on every background; everything else is `currentColor`. Minimum 120px wide for the lockup, 88px for a wordmark alone, 24px for an icon. Below that, use the favicon. Clear space equal to the height of one cell. Never recolour, outline, or shadow it.

Stella uses the same system with its own mark, `stella*`, whose asterisk is the gold glyph. The mark is the only difference.

## Components that exist

Header with mark and a mono tag. Sticky sub-nav. Eyebrow plus heading. Lead paragraph. Stat card (label, value, sub). Panel. Table container. Numbered method list with square mono markers. Note with a left rule. Verdict card by shape. Phase block with a gate line. Prompt box with a copy action. Toast.

Do not invent a component when one of these fits.

## Ads

Fixed canvases, same tokens, same rules. One gold action. The mark bottom left at 18 to 22px. Copy comes from the message registry at `messages/`, which generates the ad copy. `references/examples.md` shows the current directions. See `ads/` for the approved layouts.
