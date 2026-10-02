# fonts

Three faces take a role. Aeonik sets the default text on every surface, h1 to
h3 in the web app and the internal tools, and every h4 to h6. Space Grotesk
sets h1 to h3 on the marketing and customer sites, docs included, and the two
wordmarks. Monaspace Neon sets code, logs, digests, and data. Mac set this
rule on 2026-10-02.

Aeonik Mono and Aeonik Fono ship here too. Each loads as its own family, so a
page can name it. No role takes either one yet.

Aeonik, Aeonik Mono, and Aeonik Fono are by CoType Foundry. Space Grotesk and
Monaspace Neon are under the SIL Open Font License, and each has its licence
beside it.

The wordmark face is fixed: Space Grotesk, drawn from
`SpaceGrotesk-VariableFont_wght.ttf` at weight 600. `build/theme.py` refuses
any other wordmark family, outline file, or weight, and a theme request cannot
name the wordmark.

| File | Face | Licence |
|---|---|---|
| `SpaceGrotesk-VariableFont_wght.ttf` | Space Grotesk, the fixed source the wordmarks are outlined from at weight 600 at build time | `LICENSE-OFL.txt` |
| `space-grotesk-latin-{400,500,600,700}.woff2` | Space Grotesk, four static weights for the web | `LICENSE-OFL.txt` |
| `aeonik-wght.woff2` | Aeonik, variable weight 100 to 900, upright, and the source the art's lines of text are outlined from at build time | |
| `aeonik-italic-wght.woff2` | Aeonik, variable weight 100 to 900, italic | |
| `aeonik-mono-wght.woff2` | Aeonik Mono, variable weight 100 to 900 | |
| `aeonik-fono-wght.woff2` | Aeonik Fono, variable weight 100 to 900 | |
| `monaspace-neon-latin-wght.woff2` | Monaspace Neon, variable weight 200 to 800, upright, normal width | `LICENSE-OFL-monaspace.txt` |

The four Aeonik files ship as CoType Foundry delivered them, with no subset.
Each covers the latin set the Space Grotesk webfonts carry, except the modifier
letter apostrophe, the prime, and the double prime. A browser takes those from
the fallback stack.

`build/fonts.py` makes the Monaspace Neon file from its upstream release
(Monaspace v1.400), keeping texture healing (`calt`) and the code ligatures
(`liga`), and checks every file here:

```sh
.venv/bin/python build/fonts.py mono "Monaspace Neon Var.woff2"
.venv/bin/python build/fonts.py --check
```

`build/build.py --check` runs the same check.

To load the faces, a Next.js app uses `tokens/next-fonts.ts`, and any other
page imports `tokens/house-fonts.css`.

The `apply-theme` workflow adds files here when a theme request names a new
face: a Google face's latin WOFF2 files, the TTF the art's text is drawn
from, and the family's licence as `LICENSE-<KIND>-<family>.txt`,
and a WOFF2 copy of an uploaded TTF, OTF, or WOFF. It never deletes a file.
It does not edit the table above, so add the new face's row in the request's
pull request. See `CHANGING.md`, "Theme editor".
