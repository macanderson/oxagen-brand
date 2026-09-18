# fonts

Two faces. Space Grotesk sets the wordmarks and the headings; Aeonik sets
everything that is read rather than seen.

## Space Grotesk — tracked here

`SpaceGrotesk-VariableFont_wght.ttf` is the source the wordmarks are outlined
from at build time, and `space-grotesk-latin-{400,500,600,700}.woff2` are the
subset webfonts the HTML surfaces load. It ships under the SIL Open Font
License (`LICENSE-OFL.txt`), so it lives in the repo.

## Aeonik — licensed, not tracked

Aeonik is licensed from [CoType Foundry](https://www.cotypefoundry.com/aeonik)
and is not on Google Fonts or any public CDN. This repo is public, so the files
are gitignored and never committed.

Drop the licensed webfonts in here, named to match what the CSS asks for:

    fonts/aeonik-latin-400.woff2
    fonts/aeonik-latin-500.woff2
    fonts/aeonik-latin-600.woff2
    fonts/aeonik-latin-700.woff2

Use **Aeonik**, the sans — not Aeonik Fono and not Aeonik Mono.

Until those files are in place, body text falls back to Helvetica Neue and then
Arial. Nothing breaks; the pages just set their body copy in the fallback.
Headings and wordmarks are unaffected either way.
