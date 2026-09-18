# GitHub badges

Status pills, shields, and the commit tombstone, set in Space Grotesk and
outlined to paths, so GitHub needs no font. Colors are the house tokens.

Gold never encodes a state. The state is the shape: a filled square is
verified, a hollow square is proving, a struck square is refuted. The only
gold is the brand glyph in the `oxagen` and `stella*` shield labels.

| File                                                | Size  | Use                                                                    |
| --------------------------------------------------- | ----- | ---------------------------------------------------------------------- |
| `badge-{verified,proving,refuted}-{dark,light}.svg` | 22 px | status pills in a README or PR description; dark on GitHub dark themes |
| `shield-oxagen-verified.svg`                        | 20 px | shields.io-style badge, works on either theme                          |
| `shield-receipt-proven.svg`                         | 20 px | same, for a receipt                                                    |
| `shield-stella-proven.svg`                          | 20 px | same, for Stella; the asterisk takes the gold                          |
| `commit-tombstone-{dark,light}.svg`                 | 16 px | the lone square for commit rows                                        |

```md
![verified](assets/github-badges/shield-oxagen-verified.svg)
<picture>

  <source media="(prefers-color-scheme: dark)" srcset="assets/github-badges/badge-verified-dark.svg">
  <img alt="Verified" src="assets/github-badges/badge-verified-light.svg" height="22">
</picture>
```

Regenerate with `build.py` (see its docstring). It reads the fonts and tokens
from the kit root, so a token change there moves every badge on the next run.
