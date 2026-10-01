# Changing the brand

Every change to a colour, a face, a mark, a line, or a component starts in this repo. A product never changes a brand value in its own source. It picks up the change from here.

Oxagen and Stella share one house system: the palette, the three faces, the components, the layout rules, and the voice. Each brand has its own name in the wordmark and its own app icon. Oxagen's icon is the hive, and Stella's is the asterisk.

[`brand-guide.html`](brand-guide.html), served at brand.oxagen.cloud/brand-guide, walks through these changes for a person and shows which repos receive them today. This file is the reference.

## Rules for every change

1. Edit the source file. Run its generator. Commit the source and everything the generator writes, in one PR.
2. Never edit a generated file by hand: `tokens/`, `logo/`, `icons/`, `spinners/`, `wallpapers/`, `splash/`, `social/`, `ads/`, `content/`, `github-badges/`, `messages/index.json`, `message-bank.html`, `always-on.html`, `playbook.html`, `skills/oxagen-branding/assets/`, and `skills/oxagen-branding/references/always-on-lines.md`.
3. Open a pull request. On every PR, CI runs `build/build.py --check`, `build/messages.py --check`, `build/fonts.py --check`, `build/skill.py --check`, and an install of the skill stub, and the kit's typecheck, tests, Storybook, and bundle beside them. The deploy to brand.oxagen.cloud waits for all of them.
4. The generators run on your machine. The checks run in CI. `build/build.py` checks its sources before it writes, and it prints a `problem:` line and writes nothing when one fails.

Set up the generators once:

```sh
python3 -m venv .venv && .venv/bin/pip install fonttools brotli pyyaml
brew install harfbuzz librsvg
```

## Change a colour token

1. Edit `build/color.py`. Every colour is one constant there, and `TOKENS` lists the ones the token files carry.
2. The gold's two neighbours are derived in OKLCH: `GOLD_BRIGHT_LCH` and `GOLD_DEEP_LCH` hold the coordinates, and `GOLD_BRIGHT` and `GOLD_DEEP` pin the hex they produce. To move the gold's hue, change `GOLD`, the hue in both triples, and the two pinned hex values. `.venv/bin/python build/build.py --check` prints the hex each triple produces when a pin is wrong.
3. Run `.venv/bin/python build/build.py`. It rewrites the token files, the skill's `assets/tokens.css`, the marks, the icons, and every raster that paints the colour. Add `--svg` to skip the rasters while you iterate.
4. Run `.venv/bin/python build/playbook.py` and `.venv/bin/python build/messages.py`. Both pages embed the tokens.
5. If the change moves a semantic role, edit `ui/src/styles/globals.css`. It maps the tokens onto roles, and it carries the dark theme in two pairs of blocks, each under `.dark` and under `prefers-color-scheme`: the base layer and the v3 layer. Change all four. A derived text pair keeps its measured contrast ratio in a comment beside it (see `ui/THEME.md`).
6. A gold or ground change also reaches these copies, which no generator writes. Change them in the same PR:
   - the gold ramp `--_amber-*` and `--ox-ember-soft` in `ui/src/styles/globals.css`, typed as `oklch()` values. `build/conformance.py` treats every colour in this file as on palette, so a stale value here hides an off-palette gold everywhere.
   - `BRAND_GOLD` in `ui/src/components/brand-marks.generated.ts`, and the literal gold that `ui/src/components/brand.test.tsx` asserts. The `test` job fails until both match `tokens/house-tokens.json`.
   - the hex values in `skills/oxagen-branding/references/system.md`.
   - `pwa/install-prompt.js`, and the `theme-color` grounds in `build/pwa.py`.
   - the copies under `sdlc/`.
7. Open the PR. The check fails if a text token drops below 4.5:1 on its ground, or if a pinned neighbour stops matching its derivation.

## Change a font family

1. **Check the licence first.** This repo is public, so a house face must allow redistribution in a public repository and embedding on the web. The three faces today are under the SIL Open Font License. A face licensed per seat or per domain, such as Aeonik, cannot be a house face: `.gitignore` keeps its files out of this repo, and a product that commits them publishes them.
2. Add the webfont files under `fonts/` with the licence beside them. For a variable text or code face, add a target to `build/fonts.py` so it subsets the release to the latin set and pins the axes the house does not use. `build/fonts.py --check` then guards the file.
3. Edit the `Face` in `build/typeset.py`: the family, the fallback stack, the CSS variable `next/font` sets, the files and their weights, and the feature settings. The same file maps each role (`--font-sans`, `--font-display`, `--font-mono`, `--font-wordmark`, `--font-hero`) to a face in `ROLES`, routes each element to a role in `ROUTING`, and holds both size scales. On 2026-09-29 Mac narrowed the type rule: Geist sets every heading and every line of text, and Space Grotesk sets only the two wordmarks and line 1 of a marketing hero. A `Step` with `hero=True` admits that line, and `verify()` fails unless the marketing h1 is the only one.
4. Run `.venv/bin/python build/build.py`. It rewrites `tokens/house-fonts.css`, `tokens/house-tailwind.css`, `tokens/next-fonts.ts`, the skill's tokens, and every asset set in type.
5. **The wordmarks and the Stella icon come from a font file, not from `Face`.** `build/glyphs.py` outlines both wordmarks and Stella's asterisk from `FONT` (`fonts/SpaceGrotesk-VariableFont_wght.ttf`) at `LOGO_WEIGHT`, and `glyphs.verify()` compares the result with `build/reference/oxagen-wordmark-color-light.svg`. Editing `Face` moves the CSS and leaves the marks alone. To change the face the marks are set in, change `FONT` and `LOGO_WEIGHT`, update `build/reference/`, the `family` of the Stella icon in `build/build.py`, the width table in `build/campaign.py`, and the pasted `WORDMARK` in `build/messages.py`, all in one PR. That is a logo change, so say so in the PR body.
6. Update the face names in `skills/oxagen-branding/references/core.md` (the checklist), `skills/oxagen-branding/references/system.md` (the type section), and `HOUSE_FACES` in `build/conformance.py`, which flags any other face it finds on a live page.
7. Open the PR.

## Change an app icon

Both icons are drawn by code in `build/`. A new icon is a change to that code, not a file dropped into `icons/`. One run of the generator then redraws every size, tile, favicon, splash screen, wallpaper, social card, ad, and spinner that carries it.

1. **Oxagen's hive.** Edit `build/marks.py`: `HIVE` holds the cell's radius, width, pitch, and stroke, `HIVE_CELLS` lists each cell and whether it is outlined or gold, and `HIVE_HALF` is the opacity of the half-strength cell. A shape that is not a hive also replaces `hive()`, `hive_mark()`, `hive_hit()`, `hive_lit()`, `icon_geometry()`, `icon_hit()`, `icon_body()`, and `mark_sweep()`, and the `icons` entry that `build/build.py` writes into `tokens/house-tokens.json`.
2. **Stella's asterisk.** It is the `*` of the wordmark face, outlined by `asterisk()` in `build/marks.py` through `glyphs.set_line("*")`. A change to `glyphs.FONT` changes it too.
3. **Size on the tile.** `ICON_FILL` in `build/marks.py` and `MASKABLE_FILL` in `build/build.py` set how much of each tile the icon fills, per brand. `FAVICON_WEIGHT` in `build/marks.py` thickens the hive's outline at favicon sizes.
4. Run the whole build, `.venv/bin/python build/build.py`, with no `--only`. Then run `.venv/bin/python build/playbook.py` and `.venv/bin/python build/messages.py`.
5. Change the copies no generator writes, in the same PR:
   - `WORDMARK` in `build/messages.py`, a pasted Oxagen lockup.
   - `ui/src/components/brand-marks.generated.ts`, and the hive assertions in `ui/src/components/brand.test.tsx` (four outlines, two gold cells, one at `0.55`).
   - `sdlc/public/favicon.svg`, `favicon-32.png`, and `apple-touch-icon.png`.
6. Keep `data-mark="hive"` on Oxagen's SVG marks, or change `LIVE_MARKS` in `build/conformance.py` in the same PR. Conformance finds the live icon on each surface by that attribute.
7. Check the result by eye. No check pins the icon's geometry: `build/reference/oxagen-logomark-color.svg` is a reference no code reads.
8. **Native app icons.** The kit draws web icons only: PNG, ICO, SVG, and web manifests. It makes no `.icns`, Windows app icon set, iOS asset catalogue, or Android adaptive icon. The Oxagen desktop app cuts its Tauri icons from the synced `oxagen-avatar-light.svg` with `pnpm --filter @oxagen/desktop icons` in `oxageninc/product`. The cut writes `apps/desktop/src-tauri/icons/source.sha256`: the sha256 of the avatar it cut from, and of every icon it wrote.
   - The product repo's brand check, `node tools/scripts/sync-brand-assets.mjs --check`, runs in its `brand-drift.yml` and in its required `checks` job. It fails while the stamp does not match the synced avatar or the committed icons.
   - A kit icon change therefore keeps the fan-out's sync PR in `oxageninc/product` red until someone runs the cut on that PR's branch and commits `apps/desktop/src-tauri/icons/`. The fan-out cannot run the cut, because it needs `rsvg-convert` and the Tauri CLI.
   - The stamp and the check arrive with oxageninc/product#4906 (oxageninc/product#4892).

## Change a line

1. Edit or add the entry under `messages/`, one YAML file per line. `messages/README.md` describes every field. Retire a line by setting `status: retired` and `replaced_by`. Never delete it.
2. Run `.venv/bin/python build/messages.py`. It writes `messages/index.json`, `message-bank.html`, `always-on.html`, and the skill's `always-on-lines.md`. If the line appears in an ad or a tagline, run `.venv/bin/python build/build.py --only ads social`.
3. Open the PR. The check fails on a missing field, a held line without a gate, a dash, an avoided word, an unscoped claim, or a retired line's text in an approved entry.

## Change a component

Edit `ui/src/components/`, and give each state it draws a story. Reskin through `ui/src/styles/globals.css` and the tokens, never with a colour in a class string. `ui/README.md` has the rules.

## How a change reaches each surface

**Agents** get it on their next run. The `oxagen-branding` skill, and the stub every other repo carries, read this repo from the current `main` commit each time.

**brand.oxagen.cloud** deploys from every push to `main`, after the checks pass.

**Frontends** each copy the files they use through their own sync script. `consumers.json` lists every repo, its sync command, and its live surfaces. After a push to `main` passes every check, the `fan-out` workflow runs each repo's sync against that commit, installs the current skill stub, and opens a PR in the repo when anything changed. The PR carries the `agent-monitored-pr` label and merges on its own once the repo's required checks pass, where the repo allows auto-merge. Each repo's `brand-drift.yml` also fails its CI whenever its copy has fallen behind `main`, so a missed sync cannot pass unnoticed.

The `fan-out` workflow needs the `BRAND_SYNC_TOKEN` secret in `oxageninc/brand`: a classic token with the `repo` and `workflow` scopes. The consumers sit under two owners, `oxageninc` and `macanderson` (for `stella`), and a fine-grained token has one resource owner, so it cannot cover both. Moving `stella` into `oxageninc` would let a fine-grained token do the job. The `conformance` workflow reads the private consumers with the same secret. Until it exists, every fan-out run fails at its first step and no frontend receives a change. `brand-guide.html` lists which repos have a working sync script and drift check today.

| Surface | Repo | Deploy |
|---|---|---|
| oxagen.sh, app.oxagen.sh, docs.oxagen.sh | `oxageninc/product` | `pipeline.yml` |
| stella.oxagen.sh | `macanderson/stella` | `docs.yml` |
| roadmap.oxagen.cloud | `oxageninc/roadmap` | `deploy-production.yml` |
| gtm.oxagen.cloud | `oxageninc/gtm` | Vercel's Git integration, on every push to `main` |
| survey.oxagen.cloud | `oxageninc/survey` | Vercel's Git integration, on every push to `main` |
| brand.oxagen.cloud | this repo | `ui.yml` on every push to `main` |
| sdlc.oxagen.sh | this repo, `sdlc/` | Vercel project `oxagen-sdlc`, on a push to `main` that changes `sdlc/` |

A merged sync PR ships through the deploy in this table. In `oxageninc/gtm` and `oxageninc/survey`, Vercel builds production from each push to `main`, with no `vercel deploy` step, so a merge in either repo puts it live. Review a sync PR there as a release.

To add a frontend, give its repo a sync script that takes `--brand <path>` and `--check`, commit the stub with `skills/install.sh --project <repo>`, add `.github/workflows/brand-drift.yml` (it checks out this repo's `main` and runs the sync with `--check`), and add the repo and its surfaces to `consumers.json`.

**Conformance.** The `conformance` workflow runs `build/conformance.py` every day and on demand. It checks each repo's stub and drift workflow, and each live surface's icons, golds, faces, retired lines, dashes, and exclamation points. When anything differs, it keeps one open issue labelled `brand-conformance` with the report, and it closes that issue when everything conforms again. It reads the private consumers through the GitHub API with `BRAND_SYNC_TOKEN`, and reports a repo it cannot read as a missing token. Run it by hand with a token that can read them: `GITHUB_TOKEN=$(gh auth token) python3 build/conformance.py`.
