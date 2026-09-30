"""The <head> tags that make a page of this site installable.

Every page the site serves (the playbook, the message bank, the always-on
campaign) carries the same set: the hive favicon, the home-screen icons, the
kit's own web manifest, one launch screen per iOS screen size from `splash/`,
and the house install prompt from `pwa/install-prompt.js`. A product copies the
same assets; this is the kit wearing them itself.
"""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SPLASH_TABLE = ROOT / "splash/splash-screens.json"


def splash_links(brand: str = "oxagen", base: str = "/splash/") -> str:
    """One `apple-touch-startup-image` per screen and scheme, from the splash table."""
    screens = json.loads(SPLASH_TABLE.read_text())["screens"]
    out = []
    for scheme in ("dark", "light"):
        for s in screens:
            href = base + s["file"].format(brand=brand, scheme=scheme)
            media = f"{s['media']} and (prefers-color-scheme: {scheme})"
            out.append(f'<link rel="apple-touch-startup-image" media="{media}" href="{href}">')
    return "\n".join(out)


def head(title: str = "Oxagen") -> str:
    """Favicons, touch icons, manifest, launch screens and the install prompt."""
    return "\n".join([
        '<link rel="icon" href="/logo/svg/oxagen-favicon.svg" type="image/svg+xml" sizes="any">',
        '<link rel="icon" href="/icons/oxagen-icon-32.png" sizes="32x32" type="image/png">',
        '<link rel="icon" href="/icons/oxagen-icon-16.png" sizes="16x16" type="image/png">',
        '<link rel="icon" href="/icons/oxagen-favicon.ico" sizes="16x16 32x32 48x48">',
        '<link rel="apple-touch-icon" href="/icons/oxagen-icon-180.png" sizes="180x180">',
        '<link rel="manifest" href="/icons/oxagen.webmanifest">',
        '<meta name="theme-color" media="(prefers-color-scheme: light)" content="#FFFFFF">',
        '<meta name="theme-color" media="(prefers-color-scheme: dark)" content="#09090B">',
        '<meta name="mobile-web-app-capable" content="yes">',
        '<meta name="apple-mobile-web-app-capable" content="yes">',
        '<meta name="apple-mobile-web-app-status-bar-style" content="default">',
        f'<meta name="apple-mobile-web-app-title" content="{title}">',
        splash_links(),
        '<script src="/pwa/install-prompt.js" defer data-icon="/icons/oxagen-icon-192.png"></script>',
    ])
