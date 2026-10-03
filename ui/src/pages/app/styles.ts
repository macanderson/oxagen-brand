// The product app's class recipes, copied from oxageninc/product
// apps/app/src/ui/control-styles.ts, ui/table.tsx, and ui/route-tabs.tsx at
// fad620bcef (2026-10-02). Each colour, font size, space, and corner reads a
// kit token, so a theme change reaches them as it reaches the app. Where the
// app wrote a pixel value, the recipe takes the nearest step of the kit's scale.

/** A pill 36px tall, 12px across, 14px text, a 16px glyph. */
const buttonBase =
  "inline-flex min-h-9 max-md:min-h-11 items-center justify-center gap-1.5 rounded-4xl px-3 py-1.5 text-base font-medium whitespace-nowrap transition-colors [&_svg]:pointer-events-none [&_svg]:shrink-0 [&_svg:not([class*='size-'])]:size-4 " +
  "focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-ring " +
  "disabled:cursor-not-allowed disabled:opacity-45 aria-disabled:cursor-not-allowed";

/** The one gold action a screen carries. */
export const buttonPrimary = `${buttonBase} border border-button-primary-border bg-button-primary-bg font-semibold text-button-primary-fg hover:bg-button-primary-hover-bg hover:border-button-primary-hover-bg active:bg-button-primary-active-bg`;

/** A button at rest: panel fill, hairline border, the wash on hover. */
export const buttonSecondary = `${buttonBase} border border-button-default-border bg-button-default-bg text-button-default-fg hover:border-rule hover:bg-button-default-hover-bg active:bg-button-default-active-bg`;

/** An action that ends something, in the failed hue as ink. */
export const buttonDanger = `${buttonBase} border border-error/40 bg-button-default-bg text-error-ink hover:bg-error/10 active:bg-error/15`;

export const buttonSmall =
  "inline-flex min-h-8 flex-none items-center justify-center gap-1 rounded-4xl border border-button-default-border bg-button-default-bg px-3 text-base font-medium whitespace-nowrap text-button-default-fg hover:bg-button-default-hover-bg focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-ring disabled:cursor-not-allowed disabled:bg-button-disabled-bg disabled:text-muted-foreground [&_svg]:pointer-events-none [&_svg]:shrink-0 [&_svg:not([class*='size-'])]:size-4";

/** Gold as ink, underlined on hover. */
export const linkText =
  "font-medium text-link underline-offset-4 hover:text-link-hover hover:underline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-ring rounded-sm";

export const panel =
  "app-panel min-w-0 overflow-hidden rounded-2xl border border-border bg-card text-card-foreground";

/** The scope line over an h1, in gold as ink. */
export const eyebrow =
  "text-sm font-semibold uppercase tracking-[0.14em] text-accent-text";

/** The same caps line inside a panel, muted. */
export const eyebrowQuiet =
  "text-sm font-semibold uppercase tracking-[0.14em] text-muted-foreground";

export const mono = "font-mono";

/** The one sentence under a table or a chart that says how to read it. */
export const note =
  "border-l-2 border-gold py-0.5 pl-3 text-sm text-muted-foreground";

/** A record's fields, label left in the dim ink and value right. */
export const kvList =
  "grid grid-cols-[auto_1fr] items-baseline gap-x-4 gap-y-1.75 text-sm";
export const kvTerm = "whitespace-nowrap text-muted-foreground";
export const kvValue = "m-0 min-w-0 text-foreground [overflow-wrap:anywhere]";

/** A quiet pill that is a link or a copy button. */
export const linkChip =
  "inline-flex min-w-0 max-w-full items-center gap-1.25 whitespace-nowrap rounded-md border border-border bg-hl px-1.75 py-0.5 text-sm font-semibold leading-normal tracking-[0.02em] text-muted-foreground transition-colors hover:border-gold hover:bg-hl hover:no-underline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-ring";

export const panelHeader =
  "flex flex-wrap items-center justify-between gap-3 border-b border-border bg-panel-head px-4 py-3";
export const panelTitle = "text-base font-semibold text-foreground";
export const panelFooter =
  "flex flex-wrap items-center justify-between gap-3 border-t border-border px-4 py-3 text-sm text-muted-foreground";
export const panelBody = "px-4 py-3.5";

/** One tile of a figure strip. */
export const statTile =
  "flex min-w-0 flex-col rounded-2xl border border-border bg-card px-3.75 py-3.25 text-card-foreground max-md:px-3 max-md:py-2.75";
export const statTerm =
  "mb-1.25 text-xs font-semibold uppercase tracking-[0.1em] text-muted-foreground";
export const statValue =
  "text-2xl font-bold leading-[1.15] tracking-[-0.02em] tabular-nums max-md:text-lg";
export const statNote = "mt-0.75 text-sm text-muted-foreground";
export const statStrip =
  "grid grid-cols-2 gap-3.5 md:[grid-template-columns:repeat(auto-fit,minmax(175px,1fr))]";

/** The Run page's six figures: a tighter tile than the page strips. */
export const runStatStrip =
  "grid grid-cols-2 gap-2 sm:grid-cols-3 min-[86.25rem]:grid-cols-6";
export const runStatTile =
  "flex min-w-0 flex-col rounded-2xl border border-border bg-card px-2.75 py-2.25 text-card-foreground";
export const runStatTerm =
  "mb-1.25 text-xs font-semibold uppercase tracking-[0.1em] text-muted-foreground";
export const runStatValue =
  "text-lg font-bold leading-[1.15] tracking-[-0.02em] tabular-nums";
export const runStatNote = "mt-0.75 text-xs text-muted-foreground";

/** A table cell, and a numeric one in the mono face. */
export const cell = "px-3 py-2.25 align-middle";
export const numericCell = `${cell} whitespace-nowrap text-right font-mono tabular-nums`;
export const headCell =
  "whitespace-nowrap bg-card px-3 py-2.25 text-xs font-semibold uppercase tracking-[0.09em] text-muted-foreground";

/** A route tab: underlined in the gold when selected, a mono dim count after the label. */
export const tabLink =
  "-mb-px inline-flex min-h-10 max-md:min-h-11 shrink-0 items-center gap-1.5 whitespace-nowrap border-b-2 border-transparent px-3.25 py-2 text-base font-medium text-muted-foreground transition-colors hover:text-foreground focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-ring aria-selected:border-gold aria-selected:text-foreground";
export const tabCount = "font-mono text-xs font-normal text-muted-foreground";
