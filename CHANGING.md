# Changing the brand

Every change to a colour, a face, a mark, a line, or a component starts in this repo. A product never changes a brand value in its own source. It picks up the change from here.

Oxagen and Stella share one house system: the palette, the faces, the components, the layout rules, and the voice. Each brand has its own name in the wordmark and its own app icon. Oxagen's icon is the hive, and Stella's is the asterisk.

[`brand-guide.html`](brand-guide.html), served at brand.oxagen.cloud/brand-guide, walks through these changes for a person and shows which repos receive them today. This file is the reference.

## Rules for every change

1. Edit the source file. For a colour, a face, a corner, a shadow, the spacing, or a type size, that is `theme/theme.json`. Run its generator. Commit the source and everything the generator writes, in one PR.
2. Never edit a generated file by hand: `tokens/`, `logo/`, `icons/`, `spinners/`, `wallpapers/`, `splash/`, `social/`, `ads/`, `content/`, `github-badges/`, `messages/index.json`, `message-bank.html`, `always-on.html`, `playbook.html`, `skills/oxagen-branding/assets/`, `skills/oxagen-branding/references/always-on-lines.md`, and `ui/src/lib/house-type-utilities.json`.
3. Open a pull request. On every PR, CI runs `build/build.py --check`, the unit tests in `build/` (`python -m unittest discover -s build -p "test_*.py"`), `build/editor_fixture.py --check`, `build/messages.py --check`, `build/fonts.py --check`, `build/skill.py --check`, and an install of the skill stub, and the kit's typecheck, tests, Storybook, and bundle beside them. The deploy to brand.oxagen.cloud waits for all of them.
4. The generators run on your machine. The checks run in CI. `build/build.py` checks its sources before it writes, and it prints a `problem:` line and writes nothing when one fails.

Set up the generators once:

```sh
python3 -m venv .venv && .venv/bin/pip install fonttools brotli pyyaml
brew install harfbuzz librsvg
```

`build/theme.py` validates the theme with the standard library alone, so the schema needs no extra package.

## Change the theme

`theme/theme.json` holds every value of the house design a person may change. `theme/theme.schema.json` describes each field. The generators read the theme, so one edit there moves every token file, mark, icon, and image.

| Field | What it sets |
|---|---|
| `color.gold` | The primary brand colour, as six uppercase hex digits. It fills the gold glyph of each wordmark, the hive's lit cells, Stella's asterisk, the primary button, and the focus ring. |
| `color.gold_bright`, `color.gold_deep` | The OKLCH lightness and chroma of the gold's two neighbours. The build takes the hue from the gold and derives the hex. `gold_deep` is gold as a mark on paper, the hive's gradient, and words in the art. |
| `color.gold_text` | The OKLCH lightness and chroma of gold as words on paper, as `--ox-gold-text-ink`. `--gold-text`, `--link`, and `--accent-text` read it in the light theme. The build derives it like the neighbours, and fails if it drops below 4.5:1 on paper, a panel, or a lifted row. |
| `color.ink`, `color.paper` | The dark and the light surfaces: the canvas, `void`, `panel`, `hl`, `border`, and `rule`. |
| `color.text_on_ink`, `color.text_on_paper` | Body, muted, and dim text. Primary text is the other ground: paper on ink, and ink on paper. `muted_text_lightness` sets muted-text-ink, the secondary text that also clears 4.5:1 on a lifted row on paper. |
| `color.states` | Each governance state's mark on ink and on paper. |
| `color.state_text_lightness_on_ink` | The OKLCH lightness of every state's text stop on ink. The build derives each text stop from its mark. |
| `color.destructive_lift_on_ink` | How far the destructive red on ink sits above the failed mark in OKLCH lightness. |
| `faces.wordmark` | The face of both wordmarks and Stella's asterisk icon, as `--ox-font-wordmark` and `--font-wordmark`. It is fixed: Space Grotesk, drawn from `fonts/SpaceGrotesk-VariableFont_wght.ttf` at weight 600, as `outline` names. The build refuses any other family, outline file, or weight. |
| `faces.display` | The face of h1 to h3 on the marketing and customer sites, docs included, as `--ox-font-display` and `--font-display`. `text-m-h1` to `text-m-h3` read it. It is Space Grotesk today. When two roles name the same family, as `faces.display` and `faces.wordmark` do today, they must list the same files, fallback, and features. |
| `faces.sans` | The default text face on every surface, as `--ox-font` and `--font-sans`. It also sets h1 to h3 in the app and the internal tools, through `--font-heading`, and every h4 to h6. `outline` names the variable font file the art's lines of text are drawn from. |
| `faces.mono` | The face of code, logs, digests, paths, ids, and the numbers in tables. |
| `extra_faces` | Faces that load and take no role, such as Aeonik, Aeonik Mono, and Aeonik Fono. Each gets `@font-face` rules and a next/font loader, so a page can name its family. No `--font-*` or `--ox-font-*` token reads one. A theme request cannot change them. |
| `radius.base` | The corner every step multiplies, as `--ox-radius-base`. The kit's UI reads it as `--ui-radius`. |
| `radius.steps` | Each step's multiplier, as `--ox-radius-xs` to `--ox-radius-4xl`. The kit's `rounded-xs` to `rounded-4xl` read these. |
| `radius.card` | The step a card and a panel take, as `--ox-radius-card`. |
| `radius.site` | The website's corner for cards, panels, and inputs, as `--ox-radius`. It does not follow the base yet. |
| `shadow.ui`, `shadow.pop` | The quiet shadow under a control, and the shadow under a menu, popover, dialog, or toast, each on ink and on paper. The tokens are `--ox-shadow-ui`, `--ox-shadow-ui-ink`, `--ox-shadow-pop`, and `--ox-shadow-pop-ink`. The `-ink` twin is the value on paper, as for every other house token. |
| `spacing.unit` | The spacing unit, as `--ox-space`. Tailwind's `--spacing` reads it, so `p-4` is four units. |
| `spacing.wrap` | The widest a page's content runs, as `--ox-wrap`. |
| `type.weights` | The weight for each job, as `--ox-weight-*`. The wordmarks take `faces.wordmark.outline.weight`. |
| `type.tracking` | Letter spacing, as `--ox-tracking-*`. |
| `type.scales.marketing`, `type.scales.app` | Each scale's `base`, its body size, as `--ox-m-base` (16px) and `--ox-a-base` (14px). Each step in `steps` carries its `ratio`, leading, weight, and tracking. A step's size is the base times its ratio, written as `calc()` over the base, such as `calc(var(--ox-a-base) * 0.857143)` for the app micro step. Body's ratio is 1, so body is the base. A new base moves every step on its scale. The steps reach a page as `--ox-m-*` and `--ox-a-*`, their `-leading` twins, and the `text-m-*` and `text-a-*` utilities. Each utility reads its step's size and leading tokens, so a page that sets a token restyles that step. `tokens/house-text-scale.css` points Tailwind's `text-xs` to `text-3xl` at the app steps. It is opt-in: a product imports it after `house-tailwind.css` and renames its classes in the same change, as `README.md` says under "Use it in a product". Mac: "The base page font size should never be lower than 14px". The theme editor warns when a base goes under 14px, and no check refuses a smaller base or step. |

Each face lists its `family`, its `source`, its `files` with their weights, its `fallback` families in order, and its OpenType `features`. A file with `"style": "italic"` loads as the same family with `font-style: italic`, as Aeonik's italic does. `source` is `kit` for files already in `fonts/`, or `google` for a Google family. The `apply-theme` workflow fetches a `google` family into `fonts/` when a theme request names it (see "Theme editor" below). When you edit the theme by hand, add the files to `fonts/` yourself.

1. Edit `theme/theme.json`.
2. Run `.venv/bin/python build/build.py`, then `.venv/bin/python build/playbook.py` and `.venv/bin/python build/messages.py`. `--svg` skips the rasters while you iterate, and it deletes the PNGs in the steps it runs, so run the full build before you commit.
3. Run `.venv/bin/python build/build.py --check`. It fails when the theme does not match its schema, when the wordmark face is not Space Grotesk at weight 600, when a value breaks a rule (contrast, the gold between its neighbours, the drawn wordmark against the reference, the type scales), when a file the literal guard reads hard-codes a colour, corner, shadow, space, or font size, when a semantic token has a second definition in a theme, when a semantic text role drops below 4.5:1 on a ground, or when a generated file differs from what the theme produces.
4. Change the copies no generator writes. The colour and font sections below list them.
5. Open the PR.

## Theme editor

The kit's Storybook has a theme editor on every example page, the `Pages/` stories. Use it to try a change on real pages, then send it to every site. The editor lives in `ui/src/theme-editor/`, and `ui/.storybook/preview.tsx` mounts it. It is not part of the kit's exports or its bundle.

1. **Open the editor.** Open Storybook at brand.oxagen.cloud/storybook, or a pull request's Storybook, and pick any story under Pages. Select Theme in the bottom-right corner. A glass panel opens over the page. Add `theme-editor=open` to the story iframe's query string to open it on load.
2. **Preview a change.** Each control writes `--ox-*` variables on the page's `<html>`. The kit's semantic roles in `globals.css` read those tokens, so the page restyles as you change it. The colour fields edit the theme the page shows. Select Light or Dark at the top of the panel to switch the page and the theme the fields edit. The Storybook toolbar does the same. The Pages/App stories are copies of the product app's Work and Run pages, so they show how a change lands on the app.
   - **Primary colour.** The gold. The editor derives gold-bright and gold-deep as `build/color.py` does, and the marks, the primary button, the focus ring, and the gold tints follow. The marks read `var(--ox-gold)`.
   - **Surfaces, Text, and States.** The grounds, the text colours, and the six state marks. Each shows its measured contrast and flags any value below the bar the build holds it to: 4.5:1 for text, 3:1 for a mark.
   - **Fonts.** The wordmark is always Space Grotesk, so its row shows the face, a line set in it, and the drawn marks, with no picker. The marks' gold x and asterisk follow the primary colour. Marketing headings (the display role: h1 to h3 on a marketing or customer site), text, and code each take the shipped face, another face the kit ships, a Google family by name with its weights, or uploaded `.woff2`, `.woff`, `.ttf`, or `.otf` files. A Google family loads from fonts.googleapis.com. Uploaded files load with the FontFace API and stay in this browser.
   - **Corners, Shadows, Spacing, and Type sizes.** The radius base, the card step, and the website corner. The shadow under a control and under a floating surface, from a preset or as CSS. The spacing unit. A base for each type scale, and the ratio of each step. Every step is `calc()` over its base, so a new base moves every step on the page as you change it. The editor warns, without blocking, when a base goes under 14px, in Mac's words: "The base page font size should never be lower than 14px". It also warns when a heading that can take Space Grotesk falls under 20px.
   - **Checks and Changes.** The checks the build runs, in its words, and every field the draft changes.
   - The draft stays in this browser's localStorage, so it survives a reload and a move to another story. Reset returns to the shipped theme. Copy JSON and Download JSON export the request.
3. **Select Update all sites.** The editor builds a request that holds only the changed fields, in the shape `theme/request.schema.json` gives (`build/request.py` derives it from `theme/theme.schema.json`). It opens GitHub's new-file page with `theme/requests/<yyyy-mm-dd-hhmm>-<slug>.json` filled in. You commit it with your own GitHub login, so the page holds no secret.
   - Main requires checks to pass, so choose Create a new branch for this commit and start a pull request. Then select Propose changes and Create pull request.
   - A request that names uploaded fonts starts with the files. Upload them to `fonts/` on a new branch with the name the editor shows, then commit the request to the same branch.
   - GitHub refuses a new-file link longer than about 6,900 characters, so the editor stops at 6,000. For a longer request, it downloads the file and links the upload page for `theme/requests/`.
4. **The `apply-theme` workflow runs.** `.github/workflows/apply-theme.yml` runs on a pull request from a branch in this repo that adds or changes `theme/requests/`. It never runs on a fork. Every commit on the branch that it did not write may change only `theme/requests/` and `fonts/`. It runs `build/apply_theme.py`, which:
   - validates the request, and refuses one that names `faces.wordmark`, because the wordmark face is fixed,
   - fetches each Google face into `fonts/`: the latin WOFF2 files at the requested weights, a TTF to draw the art's text from for the text role, and the family's licence from the google/fonts repository,
   - checks that each uploaded file is on the branch, and writes a WOFF2 copy of a TTF, OTF, or WOFF upload,
   - merges the request into `theme/theme.json`,
   - carries a new gold into the hand copies (see "Change a colour token", step 6),
   - and deletes the request.
   Then the workflow runs `build/build.py`, `build/playbook.py`, `build/messages.py`, `build/editor_fixture.py`, and `build/build.py --check`. It commits the result to the branch with `BRAND_SYNC_TOKEN`, because a push made with `GITHUB_TOKEN` starts no workflow, and the kit's checks must run on the result. It comments on the pull request with the changed fields, the new gold and its neighbours, and any contrast warning. When a step fails, it pushes nothing and comments with the problem.
5. **Review the pull request.** Read the comment and the checks. A request that adds a face also needs a row in `fonts/README.md`, which lists the faces and their licences by hand. Two quick pushes, such as the request and then its fonts, can start two runs: the first pushes the result, and the second fails at its push and comments so. The branch holds the first run's result, and its checks decide.
6. **Merge it.** `ui.yml` deploys brand.oxagen.cloud, and the `fan-out` workflow opens a sync pull request in every repo `consumers.json` lists. See "How a change reaches each surface".

The editor's colour maths is a port of `build/color.py`. `build/editor_fixture.py` writes what `color.py` derives for the shipped colours and six changed ones, the editor's tests hold the port to it, and CI fails when the fixture is stale.

## Change a colour token

1. Edit `color` in `theme/theme.json`. Every colour the token files carry is a field there, or is derived from one.
2. The gold's neighbours are derived in OKLCH. `gold_bright`, `gold_deep`, and `gold_text` hold each neighbour's lightness and chroma, the hue is the gold's own, rounded to a whole degree, and `build/color.py` derives the hex. A new gold moves both neighbours with it.
   - Each state, and the destructive red, also has a text stop for words, derived from its mark. A text stop keeps the mark's hue and chroma. On ink it sits at `state_text_lightness_on_ink`, and on paper it keeps the mark's own lightness. When a state's mark moves, its text stop moves with it. `muted_text_lightness` does the same for secondary text on paper-hl.
3. Run `.venv/bin/python build/build.py`. It rewrites the token files, the skill's `assets/tokens.css`, the marks, the icons, and every raster that paints the colour. Add `--svg` to skip the rasters while you iterate.
4. Run `.venv/bin/python build/playbook.py` and `.venv/bin/python build/messages.py`. Both pages embed the tokens.
5. If the change moves a semantic role, edit `ui/src/styles/globals.css`. It maps the tokens onto roles with one definition per theme: `:root` for light, `.dark` for dark, and the `prefers-color-scheme` block, which repeats `.dark` for a dark OS with no class. Change `.dark` and the `prefers-color-scheme` block together. `build/css_literals.py` fails when a token is declared twice in one block, when a later `:root` declaration would override a `.dark` one, or when the two dark blocks differ. Status words (`--error-ink`, `--success-ink`, and the rest) map to the kit's text stops, never to a mark, and each keeps its worst measured ratio in a comment beside it (see `ui/THEME.md`).
6. A gold or ground change also reaches these copies, which no generator writes. For a theme request, the `apply-theme` workflow carries a new gold into them: it replaces the gold and its two neighbours in each file `CARRY_FILES` lists in `build/apply_theme.py`, and turns the gold ramp's hue. A ground change, or a gold changed by hand, needs them changed in the same PR:
   - the gold ramp `--_amber-*` in `ui/src/styles/globals.css`, typed as `oklch()` values. Each tint sits a fixed number of degrees from the gold's hue, and the theme editor previews them the same way. `build/conformance.py` treats every colour in this file as on palette, so a stale value here hides an off-palette gold everywhere.
   - `BRAND_GOLD` in `ui/src/components/brand-marks.generated.ts`. `ui/src/components/brand.test.tsx` compares it with `tokens/house-tokens.json`, so the `test` job fails until the two match.
   - the hex values in `skills/oxagen-branding/references/system.md`.
   - `pwa/install-prompt.js`.
   - the copies under `sdlc/`.
7. Open the PR. The check fails if a text token drops below 4.5:1 on its ground, if a state text stop drops below 4.5:1 on any surface of its theme or leaves its mark's hue, if the gold's lightness leaves the space between its neighbours, or if a generated file differs from what the theme produces.

## Change a font family

The wordmark face is fixed. Space Grotesk sets both wordmarks and Stella's asterisk, drawn from `fonts/SpaceGrotesk-VariableFont_wght.ttf` at weight 600. Mac decided this on 2026-10-02. `build/theme.py` refuses a theme with any other wordmark family, outline file, or weight, so these steps change the marketing headings, the text, or the code.

1. **Check the licence first.** On 2026-10-01 Mac decided that a licensed face may be committed to this public repo like the open faces. The face's licence must still allow web embedding on Oxagen's sites, which are every surface `consumers.json` lists and brand.oxagen.cloud. Read the licence before you add the files, and stop if it does not allow that.
2. Add the webfont files under `fonts/`, and add their rows to `fonts/README.md`. For a variable text or code face from an upstream release, add a target to `build/fonts.py` so it subsets the release to the latin set and pins the axes the house does not use. For a face that ships as delivered, as Aeonik does, add its files to `CHECKS` in `build/fonts.py`. Either way, `build/fonts.py --check` then guards the file.
3. Edit the role's entry in `faces` in `theme/theme.json`: the family, the source, the files with their weights and styles, the fallback families, and the feature settings. A face that should load and take no role goes in `extra_faces` instead. The build derives the CSS variable `next/font` sets from the family, such as `--font-space-grotesk`. `build/typeset.py` maps each role (`--font-sans`, `--font-display`, `--font-heading`, `--font-mono`, `--font-wordmark`) to a face in `ROLES` and routes each element to a role in `ROUTING`. On 2026-10-02 Mac set the type rule, and on 2026-10-03 Mac set Geist back as the house sans in place of Aeonik. Geist (`faces.sans`) sets the default text on every surface, h1 to h3 in the app and the internal tools, and every h4 to h6. Space Grotesk (`faces.display`) sets h1 to h3 on the marketing and customer sites, docs included. Monaspace Neon (`faces.mono`) sets code. `--font-heading` reads `--font-sans`, and a marketing or docs site points it at `--font-display` in its own stylesheet. `verify()` fails if h1 to h3 stop reading `--font-heading`. It sets no smallest size.
4. Run `.venv/bin/python build/build.py`. It rewrites `tokens/house-fonts.css`, `tokens/house-tailwind.css`, `tokens/next-fonts.ts`, the skill's tokens, and every asset set in type. `next-fonts.ts` names each export after its family, so a new family renames the export a product imports.
5. **The wordmarks and the Stella icon come from a font file.** `build/glyphs.py` outlines both wordmarks and Stella's asterisk from `faces.wordmark.outline`, which is always `fonts/SpaceGrotesk-VariableFont_wght.ttf` at weight 600. On every check, `glyphs.verify()` compares the drawn `oxagen` with `build/reference/oxagen-wordmark-color-light.svg`. The wordmark face is fixed, so the marks' outlines never change. A new gold still recolours the gold x and asterisk, because the build paints them from `color.gold`.
   - **The art's lines of text come from `faces.sans.outline`** (today `fonts/geist-latin-wght.woff2`): every headline, answer line, qualifier, kicker, call to action, and tagline in `ads/`, `social/`, and `content/`. `text_path` and `text_width` in `build/glyphs.py` outline and measure in it. A WOFF or WOFF2 outline is unpacked for HarfBuzz, and a static outline file draws every weight as it is. `WIDTHS` in `build/campaign.py` holds the same face's 700 advances for the always-on page, and its JavaScript port reads them. To change the text face, change `faces.sans.outline`, regenerate `WIDTHS` from `glyphs.font(700, "text")`, set `DISPLAY` in `build/campaign.py` to the new stack, and run `build/build.py`.
6. Update the face names in `skills/oxagen-branding/references/core.md` (the checklist), `skills/oxagen-branding/references/system.md` (the type section), `README.md`, `fonts/README.md`, `ui/THEME.md`, `ui/README.md`, `ui/.design-sync/conventions.md`, and the prose of `build/playbook.py` and `build/typeset.py`. `build/conformance.py` reads the house families from the theme, and it flags any other face it finds on a live page.
7. Open the PR.

## Change an app icon

Both icons are drawn by code in `build/`. A new icon is a change to that code, not a file dropped into `icons/`. One run of the generator then redraws every size, tile, favicon, splash screen, wallpaper, social card, ad, and spinner that carries it.

1. **Oxagen's hive.** Edit `build/marks.py`: `HIVE` holds the cell's radius, width, pitch, and stroke, `HIVE_CELLS` lists each cell and whether it is outlined or gold, and `HIVE_HALF` is the opacity of the half-strength cell. A shape that is not a hive also replaces `hive()`, `hive_mark()`, `hive_hit()`, `hive_lit()`, `icon_geometry()`, `icon_hit()`, `icon_body()`, and `mark_sweep()`, and the `icons` entry that `build/build.py` writes into `tokens/house-tokens.json`.
2. **Stella's asterisk.** It is the `*` of Space Grotesk, the fixed wordmark face, outlined by `asterisk()` in `build/marks.py` through `glyphs.set_line("*")`. Its gold follows `color.gold`.
3. **Size on the tile.** `ICON_FILL` in `build/marks.py` and `MASKABLE_FILL` in `build/build.py` set how much of each tile the icon fills, per brand. `FAVICON_WEIGHT` in `build/marks.py` thickens the hive's outline at favicon sizes.
4. Run the whole build, `.venv/bin/python build/build.py`, with no `--only`. Then run `.venv/bin/python build/playbook.py` and `.venv/bin/python build/messages.py`.
5. Change the copies no generator writes, in the same PR:
   - `WORDMARK` in `build/messages.py`, a pasted Oxagen lockup.
   - `ui/src/components/brand-marks.generated.ts`, and the hive assertions in `ui/src/components/brand.test.tsx` (four outlines, two gold cells, one at `0.55`).
   - `sdlc/public/favicon.svg`, `favicon-32.png`, and `apple-touch-icon.png`.
6. Keep `data-mark="hive"` on Oxagen's SVG marks, or change `LIVE_MARKS` in `build/conformance.py` in the same PR. Conformance finds the live icon on each surface by that attribute.
7. Check the result by eye. No check pins the icon's geometry: `build/reference/oxagen-logomark-color.svg` is a reference no code reads.
8. **Native app icons.** The kit draws web icons only: PNG, ICO, SVG, and web manifests. It makes no `.icns`, Windows app icon set, iOS asset catalogue, or Android adaptive icon. The Oxagen desktop app cuts its Tauri icons from the synced `oxagen-avatar-light.svg` with `pnpm --filter @oxagen/desktop icons` in the oxagen repo. The cut writes `apps/desktop/src-tauri/icons/source.sha256`: the sha256 of the avatar it cut from, and of every icon it wrote.
   - The oxagen repo's brand check, `node tools/scripts/sync-brand-assets.mjs --check`, runs in its `brand-drift.yml` and in its required `checks` job. It fails while the stamp does not match the synced avatar or the committed icons.
   - A kit icon change therefore keeps the fan-out's sync PR in the oxagen repo red until someone runs the cut on that PR's branch and commits `apps/desktop/src-tauri/icons/`. The fan-out cannot run the cut, because it needs `rsvg-convert` and the Tauri CLI.
   - The stamp and the check arrive with oxagen#4906 (oxagen#4892).

## Change a line

1. Edit or add the entry under `messages/`, one YAML file per line. `messages/README.md` describes every field. Retire a line by setting `status: retired` and `replaced_by`. Never delete it.
2. Run `.venv/bin/python build/messages.py`. It writes `messages/index.json`, `message-bank.html`, `always-on.html`, and the skill's `always-on-lines.md`. If the line appears in an ad or a tagline, run `.venv/bin/python build/build.py --only ads social`.
3. An ad's art carries its `subline`, its `subshort` on the 300×250, and its `qualifier` as a small muted line under either one. The qualifier shrinks to fit the measure on one line, splits once at a sentence boundary if it must, and is left off a size where two lines at 8 px still do not fit (`qualifier_lines` in `build/surfaces.py`, and its twin in `build/campaign.py` for `always-on.html`). A short form keeps the qualifier of its longer version, so write the qualifier as the scope sentence, not as copy.
4. Open the PR. The check fails on a missing field, a held line without a gate, a dash, an avoided word, an unscoped claim, a retired line's text in an approved entry, or an approved launch ad that has a `subline` and no `subshort`.

## Change a component

Edit `ui/src/components/`, and give each state it draws a story. Reskin through `ui/src/styles/globals.css` and the tokens, never with a colour in a class string. `ui/README.md` has the rules.

## How a change reaches each surface

**Agents** get it on their next run. The `oxagen-branding` skill, and the stub every other repo carries, read this repo from the current `main` commit each time.

**brand.oxagen.cloud** deploys from every push to `main`, after the checks pass.

**Frontends** each copy the files they use through their own sync script. `consumers.json` lists every repo, its sync command, and its live surfaces. After a push to `main` passes every check, the `fan-out` workflow runs each repo's sync against that commit, installs the current skill stub, and opens a PR in the repo when anything changed. The PR carries the `agent-monitored-pr` label and merges on its own once the repo's required checks pass, where the repo allows auto-merge. Each repo's `brand-drift.yml` compares its copy with the kit's `main`. It fails a push to `main`, the daily run, and any pull request that touches a brand file, so a missed sync cannot pass unnoticed. On a pull request that touches no brand file it warns and passes, because a kit change is not that pull request's fault and the fan-out's sync PR fixes it.

The `fan-out` workflow needs the `BRAND_SYNC_TOKEN` secret: a token with contents and pull-requests write on every repo in `consumers.json`. The consumers sit under two owners, `oxageninc` and `macanderson` (stella), and a fine-grained token covers one owner only. On 2026-10-01 Mac chose the gh CLI's own token. If `gh auth login` runs again, set it again with `gh auth token | gh secret set BRAND_SYNC_TOKEN -R oxageninc/brand`. The `conformance` workflow reads the private consumer repos with the same secret.

| Surface | Repo | Deploy |
|---|---|---|
| oxagen.sh, app.oxagen.sh, docs.oxagen.sh | `oxageninc/product` | `pipeline.yml` |
| stella.oxagen.sh | `macanderson/stella` | `docs.yml` |
| roadmap.oxagen.cloud | `oxageninc/roadmap` | `deploy-production.yml` |
| gtm.oxagen.cloud | `oxageninc/gtm` | Vercel's Git integration, on every push to `main` |
| survey.oxagen.cloud | `oxageninc/oxagen-survey` | Vercel's Git integration, on every push to `main` |
| brand.oxagen.cloud | this repo | `ui.yml` on every push to `main` |
| sdlc.oxagen.sh | this repo, `sdlc/` | Vercel project `oxagen-sdlc`, on a push to `main` that changes `sdlc/` |

A merged sync PR ships through the deploy in this table. In `oxageninc/gtm` and `oxageninc/oxagen-survey`, Vercel builds production from each push to `main`, with no `vercel deploy` step, so a merge in either repo puts it live. Review a sync PR there as a release.

To add a frontend, give its repo a sync script that takes `--brand <path>` and `--check`, commit the stub with `skills/install.sh --project <repo>`, add `.github/workflows/brand-drift.yml` (it checks out the kit's `main` and runs the sync with `--check`, failing a push to `main` and any pull request that touches a brand file, and warning on other pull requests), and add the repo and its surfaces to `consumers.json`.

**Conformance.** The `conformance` workflow runs `build/conformance.py` every day and on demand. It checks each repo's stub and drift workflow, and each live surface's icons, golds, faces, retired lines, dashes, and exclamation points. When anything differs, it keeps one open issue labelled `brand-conformance` with the report, and it closes that issue when everything conforms again. It reads each consumer through the GitHub API, with `BRAND_SYNC_TOKEN` when it is set, and reports a repo it cannot read as a missing token rather than a missing stub. Run it by hand with `python3 build/conformance.py`.
