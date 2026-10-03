## Building with the Oxagen house system

This is the real `@oxagen/ui` library (Base UI + Tailwind v4, token-driven). It is
the house system for both **oxagen** and **stella** — one palette, one type scale;
the logo is the only difference.

### The rule that will bite you

**`styles.css` is a COMPILED, CLOSED stylesheet — there is no Tailwind runtime here.**
Only the ~597 utility classes the library itself already uses exist. A class you
invent (`bg-sidebar-bg`, `p-12`, `gap-8`) silently does nothing — no error, just
unstyled output.

So: **use library components for UI, and CSS variables for your own layout glue.**

```jsx
<div style={{ background: "var(--card)", color: "var(--card-foreground)",
              border: "1px solid var(--border)", borderRadius: "var(--ui-radius)",
              padding: 24, display: "flex", gap: 16 }}>
```

260 semantic tokens are declared at root scope in `_ds_bundle.css` and **always**
resolve (85 of them are redefined under `.dark`). Each one carries a
`/* @kind color|spacing|radius|shadow|font|other */` marker right after its
declaration — if a custom property has no marker it is Tailwind engine plumbing
(`--tw-*`, utility-scoped), not a token to design with. Families (each `--x` plus often
`--x-foreground`):

- Surfaces: `--background` `--foreground` `--card` `--popover` `--muted` `--surface` `--border` `--ring` `--radius` `--ui-radius`
- Brand/state: `--primary` `--brand` `--destructive` `--success` `--warning` `--error` `--info`
- Per-part: `--button-primary-bg` `--input-border-focus` `--menu-item-highlighted-bg`
  `--dialog-bg` `--tab-fg-active` `--tooltip-bg` `--sidebar-nav-link-active-bg`
  `--card-header-bg` `--control-thumb` `--app-topbar-bg` `--badge-bg` `--link`
- Raw house palette (rarely needed directly): `--ox-gold` `--ox-ink` `--ox-paper` `--ox-panel`

Utility classes that DO exist, if you prefer them: `bg-background` `bg-card`
`bg-muted` `bg-primary` `bg-destructive` `text-foreground` `text-muted-foreground`
`text-primary` `border-border` `border-input` `rounded-sm|md|lg|xl|full`
`shadow-sm|md|lg` `font-sans|display|heading|mono|medium|semibold`
`text-xs|sm|base|lg|xl|2xl|3xl` (the app steps 2xs, micro, base, h4, h3, h2, h1)
`text-a-h1|h2|h3|h4|body|micro|2xs` `text-m-h1|h2|h3|h4|body|micro`
`gap-1|2|3|4|6`. Anything outside that list: use `var(--token)` instead.

### Theme

`:root` is light; `.dark` on an ancestor flips all 85 themed tokens. Set it with
`<ThemeProvider>` (exported) or put `className="dark"` on a wrapper. Components read
tokens through CSS, so nothing else is needed — never hand-pick a hex.

### Type and the gold rule

Three families, each with its own job. **Aeonik** (`--ox-font`, read through
`--font-sans`) sets the default text on every surface: body, labels, buttons, tables,
navigation. It also sets h1 to h3 in the app and the internal tools, through
`--font-heading`, and every h4 to h6 everywhere. **Space Grotesk** (`--ox-font-display`,
read through `--font-display`) sets h1 to h3 on the marketing and customer sites, docs
included. `--font-wordmark` sets a wordmark in it as text. **Monaspace Neon**
(`--ox-font-mono`, read through `--font-mono`) sets code, terminal output, logs,
digests, paths, ids, and numbers in tables, with `calt` and `liga` on for texture
healing. A figure in a table is mono so columns of digits align.

Mac set this rule on 2026-10-02. A component's h1 to h3 read `--font-heading`, which is
Aeonik. A marketing or docs design sets `--font-heading: var(--font-display)` on its
root, so its h1 to h3 draw Space Grotesk. Each scale has one base: 14px in the app
(`--ox-a-base`) and 16px on marketing (`--ox-m-base`), never below 14px. Every step is the
base times a ratio, so it follows the base. No style writes a font size of its own: read
a step token, such as `var(--ox-a-body)` (the app base) or `var(--ox-a-micro)` (12px).
Running text, controls, inputs, buttons, menu items, and table body cells take the base
(`text-base`). Labels, badges, timestamps, and table headers take a smaller step:
`text-sm` (micro, 12px) or `text-xs` (2xs, 10px). Aeonik Mono and Aeonik Fono load as
their own families, and no role takes either one yet.

**Glass belongs only on chrome that floats over content:** menus, selects, comboboxes,
popovers, hover cards, the command menu, toasts, a dialog's scrim, and sticky navigation
and header bars. Cards, panels, tables, and text never take it. Use the kit's
components for floating chrome, and its `glassBar` class string for a sticky bar.

**Gold (`--ox-gold` / `--primary`) is identity, not state: at most one gold action per
screen, and it never encodes success/failure.** State colors are `--success`
`--warning` `--error` `--info` `--destructive`.

### Where the truth lives

- `_ds_bundle.css` — every token, in the `:root` and `.dark` blocks. Read it before styling.
- `guidelines/THEME.md` — where each kind of answer lives, plus the three rules a token value cannot state (gold is not state; a state's two stops are both marks, so text needs a derived one; both dark blocks state every pair).
- `components/<group>/<Name>/<Name>.prompt.md` and `<Name>.d.ts` — per-component API and examples.

### Idiomatic example

```jsx
const { Panel, Button, Badge } = window.OxagenUI;

<Panel style={{ display: "flex", flexDirection: "column", gap: 16, padding: 24 }}>
  <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
    <h2 style={{ font: "600 var(--ox-a-h2)/var(--ox-a-h2-leading) var(--font-heading)", margin: 0 }}>Fleet</h2>
    <Badge variant="secondary">12 agents</Badge>
  </div>
  <p style={{ color: "var(--muted-foreground)", margin: 0 }}>
    Every run is governed and evidenced.
  </p>
  <Button variant="primary">Register agent</Button>
</Panel>
```
