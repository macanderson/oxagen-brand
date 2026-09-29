# Changing the brand

Every change to a colour, a face, a mark, a line, or a component starts in this repo. A product never changes a brand value in its own source. It picks up the change from here.

## Rules for every change

1. Edit the source file. Run its generator. Commit the source and everything the generator writes, in one PR.
2. Never edit a generated file by hand: `tokens/`, `logo/`, `icons/`, `spinners/`, `wallpapers/`, `social/`, `ads/`, `content/`, `messages/index.json`, `message-bank.html`, `always-on.html`, `playbook.html`, `skills/oxagen-branding/assets/`, and `skills/oxagen-branding/references/always-on-lines.md`.
3. Open a pull request. CI runs `build/build.py --check`, `build/messages.py --check`, and `build/skill.py --check` on every PR, and the kit's typecheck, tests, Storybook, and bundle beside them. The deploy to brand.oxagen.cloud waits for all of them.
4. The generators run on your machine. The checks run in CI.

Set up the generators once:

```sh
python3 -m venv .venv && .venv/bin/pip install fonttools brotli pyyaml
brew install harfbuzz librsvg
```

## Change a colour token

1. Edit `build/color.py`. Every colour is one constant there, and `TOKENS` lists the ones the token files carry.
2. The gold's two neighbours are derived in OKLCH: `GOLD_BRIGHT_LCH` and `GOLD_DEEP_LCH` hold the coordinates, and `GOLD_BRIGHT` and `GOLD_DEEP` pin the hex they produce. To move the gold's hue, change `GOLD`, the hue in both triples, and the two pinned hex values. `.venv/bin/python build/build.py --check` prints the hex each triple produces when a pin is wrong.
3. Run `.venv/bin/python build/build.py`. It rewrites the token files, the skill's `assets/tokens.css`, the marks, the icons, and every raster that paints the colour. Add `--svg` to skip the rasters while you iterate.
4. Run `.venv/bin/python build/playbook.py` and `python3 build/messages.py`. Both pages embed the tokens.
5. If the change moves a semantic role, edit `ui/src/styles/globals.css`. It maps the tokens onto roles, and it carries the dark theme twice, under `.dark` and under `prefers-color-scheme`. Change both blocks. A derived text pair keeps its measured contrast ratio in a comment beside it (see `ui/THEME.md`).
6. Open the PR. The check fails if a text token drops below 4.5:1 on its ground, or if a pinned neighbour stops matching its derivation.

## Change a font family

1. **Check the licence first.** This repo is public, so a house face must allow redistribution in a public repository and embedding on the web. The three faces today are under the SIL Open Font License. A face licensed per seat or per domain, such as Aeonik, cannot be a house face: `.gitignore` keeps its files out of this repo, and a product that commits them publishes them.
2. Add the webfont files under `fonts/` with the licence beside them. For a variable text or code face, add a target to `build/fonts.py` so it subsets the release to the latin set and pins the axes the house does not use. `build/fonts.py --check` then guards the file.
3. Edit the `Face` in `build/typeset.py`: the family, the fallback stack, the CSS variable `next/font` sets, the files and their weights, and the feature settings. The same file routes each role to a face (h1 to h3, h4 to body, code) and holds both size scales.
4. Run `.venv/bin/python build/build.py`. It rewrites `tokens/house-fonts.css`, `tokens/house-tailwind.css`, `tokens/next-fonts.ts`, the skill's tokens, and every asset set in type.
5. **The display face also draws the wordmarks.** `build/build.py --check` reproduces the `oxagen` wordmark from Space Grotesk and fails when its geometry moves. A new display face is therefore a logo change. Update `build/reference/` and the check in the same PR, and say so in the PR body.
6. Update the face names in `skills/oxagen-branding/references/core.md` (the checklist) and `skills/oxagen-branding/references/system.md` (the type section).
7. Open the PR.

## Change a line

1. Edit or add the entry under `messages/`, one YAML file per line. `messages/README.md` describes every field. Retire a line by setting `status: retired` and `replaced_by`. Never delete it.
2. Run `python3 build/messages.py`. It writes `messages/index.json`, `message-bank.html`, `always-on.html`, and the skill's `always-on-lines.md`. If the line appears in an ad or a tagline, run `.venv/bin/python build/build.py --only ads social`.
3. Open the PR. The check fails on a missing field, a held line without a gate, a dash, an avoided word, an unscoped claim, or a retired line's text in an approved entry.

## Change a component

Edit `ui/src/components/`, and give each state it draws a story. Reskin through `ui/src/styles/globals.css` and the tokens, never with a colour in a class string. `ui/README.md` has the rules.

## How a change reaches each surface

**Agents** get it on their next run. The `oxagen-branding` skill, and the stub every other repo carries, read this repo from the current `main` commit each time.

**brand.oxagen.cloud** deploys from every push to `main`, after the checks pass.

**Frontends** copy the files they use from this repo through their own sync scripts, and each one's CI fails when its copy has drifted from `main`. After a merge here, run the frontend's sync, commit what it writes, and open a PR there:

| Surface | Repo | Sync | Deploy |
|---|---|---|---|
| oxagen.sh, oxagen.app, docs.oxagen.app | `oxagen` | `node tools/scripts/sync-brand-assets.mjs` | `pipeline.yml` on merge |
| stella website | `stella` | `node scripts/sync-brand-assets.mjs` | see the stella repo |
| roadmap.oxagen.cloud | `oxagen-roadmap` | see its README | `deploy-production.yml` on merge |
| gtm.oxagen.cloud | `oxagen-gtm` | `node scripts/build-data.mjs` | by hand, `vercel deploy --prod` |
| survey.oxagen.app | `oxagen-survey` | see its README | by hand, `vercel deploy --prod` |

Issue #28 replaces the manual step: the files publish to npm as `@oxagen/brand`, and a merge here opens an update PR in every frontend, which merges when its CI passes.
