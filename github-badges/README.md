# GitHub badges

These files are the status pills, the shields, and the commit tombstone. Every
word is outlined to paths, so GitHub needs no font to draw one. A wordmark label
(`oxagen`, `stella*`) is set in the wordmark face. Every other word is Aeonik.
The colours are the house colours.

Gold never encodes a state. The state is the shape: a filled square is
verified, a hollow square is proving, and a struck square is refuted. The only
gold is the accent glyph in the `oxagen` and `stella*` shield labels.

| File                                                | Size  | Use                                                                    |
| --------------------------------------------------- | ----- | ---------------------------------------------------------------------- |
| `badge-{verified,proving,refuted}-{dark,light}.svg` | 22 px | status pills in a README or PR description; dark on GitHub dark themes |
| `shield-oxagen-verified.svg`                        | 20 px | shields.io-style badge, works on either theme                          |
| `shield-oxagen-agent-run.svg`                       | 20 px | same, for a pull request a wrapped agent opened during a recorded run  |
| `shield-receipt-proven.svg`                         | 20 px | same, for a receipt                                                    |
| `shield-stella-proven.svg`                          | 20 px | same, for Stella; the asterisk takes the gold                          |
| `commit-tombstone-{dark,light}.svg`                 | 16 px | the lone square for commit rows                                        |

## Hosting

GitHub draws an image in a description through its image proxy, so a badge
needs a public URL. brand.oxagen.cloud serves every file here at
`https://brand.oxagen.cloud/github-badges/<file>`. A push to `main` deploys the
site once every check passes, so a badge there always matches `main`.

```md
[![oxagen: agent run](https://brand.oxagen.cloud/github-badges/shield-oxagen-agent-run.svg)](https://app.oxagen.sh/<org>/<workspace>/runs/<run>)

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="https://brand.oxagen.cloud/github-badges/badge-verified-dark.svg">
  <img alt="Verified" src="https://brand.oxagen.cloud/github-badges/badge-verified-light.svg" height="22">
</picture>
```

## Regenerate

`build/badges.py` draws every file here, and `build/build.py` writes them as
its `badges` step. Never edit an SVG here by hand.

```sh
.venv/bin/python build/build.py --only badges --svg   # rewrite github-badges/
.venv/bin/python build/build.py --check               # fails if a file here has drifted
```
