# fonts

Three faces, each with one job. Space Grotesk sets the wordmarks and h1 to
h3. Geist sets h4 to h6 and everything read. Monaspace Neon sets code, logs,
and data. All three are under the SIL Open Font License, so all three live in
this repo, each with its licence beside it.

| File | Face | Licence |
|---|---|---|
| `SpaceGrotesk-VariableFont_wght.ttf` | Space Grotesk, the source the wordmarks are outlined from at build time | `LICENSE-OFL.txt` |
| `space-grotesk-latin-{400,500,600,700}.woff2` | Space Grotesk, four static weights for the web | `LICENSE-OFL.txt` |
| `geist-latin-wght.woff2` | Geist, variable weight 100 to 900 | `LICENSE-OFL-geist.txt` |
| `monaspace-neon-latin-wght.woff2` | Monaspace Neon, variable weight 200 to 800, upright, normal width | `LICENSE-OFL-monaspace.txt` |

Every webfont covers the same latin subset. `build/fonts.py` makes the Geist
and Monaspace Neon files from their upstream releases (Geist v1.7.2, Monaspace
v1.400), keeping texture healing (`calt`) and the code ligatures (`liga`):

```sh
.venv/bin/python build/fonts.py geist "Geist[wght].woff2"
.venv/bin/python build/fonts.py mono  "Monaspace Neon Var.woff2"
.venv/bin/python build/fonts.py --check
```

`build/build.py --check` runs the same check.

To load the faces, a Next.js app uses `tokens/next-fonts.ts`, and any other
page imports `tokens/house-fonts.css`.
