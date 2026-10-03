// Moved from oxagen apps/app/src/ui/control-styles.ts at ddb85803.
// The Run page's `runStat*` recipes stayed in the app.
// Class recipes for plain controls (buttons, links, inputs, panels, tiles,
// eyebrows) that are not their own component. Each recipe is one rule of the
// design of record, `mockups/src/engine.css` in the roadmap repository, named
// in the comment above it (ADR-132); the values are house tokens, so a reskin
// in the kit reaches every screen and the shape stays the mockup's.
//
// `design-record.test.ts` holds these recipes to the rules they cite. Change a
// recipe with the rule, never around it.
//
// Shape, type size and spacing follow the shadcn preset Mac chose on
// 2026-09-28 (`--preset b6FlQHSba`, style base-maia): pill buttons and
// inputs, 14px control text, rounder cards, and translucent menus and
// popovers. Colour stays the house's. Where a comment below quotes an
// engine.css rule and a recipe now differs from it, the recipe names the maia
// value it took, and engine.css follows.

/**
 * `.btn { border:1px solid var(--border); background:var(--panel);
 * font-weight:500 }`, in the maia button's shape: a pill 36px tall, 12px
 * across, 14px text, a 16px glyph. A phone keeps the 44px touch target the
 * mockup's sheet buttons have.
 */
const buttonBase =
  "inline-flex min-h-9 max-md:min-h-11 items-center justify-center gap-1.5 rounded-4xl px-3 py-1.5 text-base font-medium whitespace-nowrap transition-colors [&_svg]:pointer-events-none [&_svg]:shrink-0 [&_svg:not([class*='size-'])]:size-4 " +
  "focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-ring " +
  "disabled:cursor-not-allowed disabled:opacity-45 aria-disabled:cursor-not-allowed";

/**
 * `.btn.primary { background:var(--gold); border-color:var(--gold);
 * color:var(--on-gold); font-weight:600 }` — the one gold action a screen
 * carries (creation-spec §6: gold is identity, never state). The tokens
 * resolve to the gold in both themes (globals.css). Ink on gold is 9.5:1.
 */
export const buttonPrimary = `${buttonBase} border border-button-primary-border bg-button-primary-bg font-semibold text-button-primary-fg hover:bg-button-primary-hover-bg hover:border-button-primary-hover-bg active:bg-button-primary-active-bg`;

/**
 * `.btn` at rest: panel fill, hairline border, the wash on hover. The tokens
 * are the kit's default-button set, which globals.css points at the panel and
 * the wash so the recipe and the kit's own buttons agree.
 */
export const buttonSecondary = `${buttonBase} border border-button-default-border bg-button-default-bg text-button-default-fg hover:border-rule hover:bg-button-default-hover-bg active:bg-button-default-active-bg`;

/**
 * `.btn.danger { color:var(--st-failed); border-color:<st-failed 40%> }` and
 * `.btn.danger:hover { background:<st-failed 12%> }`: an action that ends
 * something, such as Deregister. It carries the failed hue as ink, never a fill.
 */
export const buttonDanger = `${buttonBase} border border-error/40 bg-button-default-bg text-error-ink hover:bg-error/10 active:bg-error/15`;

/** `a { color:var(--accent-text) }` — gold as ink, underlined on hover. */
export const linkText =
  "font-medium text-link underline-offset-4 hover:text-link-hover hover:underline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-ring rounded-sm";

/**
 * The Account and Avatar dialogs' field label and the hint under a field
 * (`.field label`, `.field .hint`), and the small button beside a field.
 * The label and hint take the maia field's type: a 14px medium label in the
 * foreground, 8px above its control, and a 14px muted hint.
 */
export const fieldLabel = "mb-2 block text-base font-medium text-foreground";
export const fieldHint = "mt-2 text-base leading-normal text-muted-foreground";
export const buttonSmall =
  "inline-flex min-h-8 flex-none items-center justify-center gap-1 rounded-4xl border border-button-default-border bg-button-default-bg px-3 text-base font-medium whitespace-nowrap text-button-default-fg hover:bg-button-default-hover-bg focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-ring disabled:cursor-not-allowed disabled:bg-button-disabled-bg disabled:text-muted-foreground [&_svg]:pointer-events-none [&_svg]:shrink-0 [&_svg:not([class*='size-'])]:size-4";

/** The one skin every field wears; `inputBase` and `textareaBase` add the shape. */
const fieldSkin =
  // 16px below md as well as by phone.css, so the class list alone says an
  // input never makes iOS zoom the page on focus.
  "block w-full min-w-0 border border-input-border bg-input-bg px-3 text-base max-md:text-input-touch text-input-fg placeholder:text-input-placeholder " +
  "hover:border-input-border-hover focus-visible:border-input-border-focus focus-visible:outline-2 focus-visible:outline-offset-0 focus-visible:outline-input-ring " +
  "disabled:bg-input-disabled-bg disabled:text-input-disabled-fg aria-invalid:border-input-invalid-border aria-invalid:outline-input-invalid-ring";

/** A one-line input or select: the maia input's 36px pill. */
export const inputBase = `${fieldSkin} min-h-9 rounded-4xl py-1.5`;

/**
 * A textarea: the maia textarea keeps the field's skin with a card corner
 * and 12px of air above and below, since a pill cannot hold several lines.
 */
export const textareaBase = `${fieldSkin} rounded-xl py-3`;

/**
 * `.menu { background:var(--pop-bg); backdrop-filter:blur(40px)
 * saturate(1.5); border-radius:16px; box-shadow:0 0 0 1px var(--pop-ring),
 * var(--shadow-pop) }` in `shared.css` (oxagen-roadmap #244): the one floating
 * surface a menu, a listbox, a popover, a hover card and the command menu
 * share. The popover fill at 70%, a blurred and saturated copy of the page
 * behind it, a 3xl corner (16px at the preset's radius), a faint ring in
 * place of a border, and the mockup's deep shadow.
 *
 * The blur sits on the element itself. A `::before` layer inside a scrolling
 * menu scrolls away with the rows, so the surface does not clip or layer.
 * The ring and the shadow read `--pop-ring` and `--ui-shadow-pop`, which
 * every theme block in `globals.css` sets. It sets no position, since its
 * callers sit inside a positioner or add `absolute` themselves.
 *
 * `glass-pop` is the hook for the glass fallbacks in `globals.css`. Where a
 * browser has no `backdrop-filter`, or the reader asks for reduced
 * transparency, the surface turns opaque on the popover ground.
 */
const floatingSurface =
  "glass-pop rounded-3xl bg-menu-popup-bg/70 text-menu-popup-fg ring-1 ring-pop-ring shadow-pop backdrop-blur-2xl backdrop-saturate-150";

/**
 * A sticky bar over scrolling content: the website's nav and the app's
 * header. It is the page ground at 72% over a 24px blur, with the same 150%
 * saturation as the floating surface, and a hairline under it at 60%. Content
 * that scrolls under the bar shows through as soft colour.
 *
 * Text set straight on the bar takes the foreground ink. At 72% the ink stays
 * above 8:1 in both themes even when pure black or pure white scrolls under
 * it. The muted ink does not hold 4.5:1 over a blurred dark headline, so
 * secondary text sits on an opaque control instead: a tab track, a badge, or
 * the command menu's trigger.
 *
 * `glass-bar` is the hook for the glass fallbacks in `globals.css`, which
 * turn the bar opaque on the page ground. The recipe sets `sticky top-0` and
 * a z-index under the floating surfaces (z-50), so an open menu covers it.
 */
export const glassBar =
  "glass-bar sticky top-0 z-30 border-b border-border/60 bg-background/72 text-foreground backdrop-blur-xl backdrop-saturate-150";

/**
 * A menu, listbox or picker surface. `menuPopup` adds the 4px inset a menu's
 * rows sit in.
 */
export const menuSurface = `${floatingSurface} outline-none`;
export const menuPopup = `${menuSurface} p-1`;

/**
 * `.menu-i { gap:10px; padding:8px 12px; border-radius:12px; font-size:14px;
 * min-height:36px }`: one row of a menu, a 2xl corner (13px at the preset's
 * radius), a 16px glyph, 44px tall on a phone, and the preset's subtle
 * highlight (`menuItemActive`, the foreground at 10%) under the pointer or
 * the keyboard. A listbox that tracks its own active row adds
 * `menuItemActive` to that row.
 */
export const menuItemActive = "bg-foreground/10";
export const menuItem =
  "flex min-h-9 w-full cursor-pointer select-none items-center gap-2.5 rounded-2xl px-3 py-2 text-left text-base text-menu-item-fg outline-none max-md:min-h-11 " +
  "data-[highlighted]:bg-foreground/10 data-[disabled]:pointer-events-none data-[disabled]:text-menu-item-disabled-fg " +
  "[&_svg]:pointer-events-none [&_svg]:shrink-0 [&_svg:not([class*='size-'])]:size-4";

/** `.menu-sep { height:1px; background:var(--border); margin:4px -4px }`: edge to edge. */
export const menuSeparator = "-mx-1 my-1 h-px bg-menu-separator";

/**
 * `.menu-h { font-size:10.5px; letter-spacing:.12em; text-transform:uppercase;
 * font-weight:600; padding:8px 12px 4px }`: a group's name over its rows. It
 * reads in the muted ink, since the dim ink fails contrast on the ground.
 */
export const menuLabel =
  "px-3 pt-2 pb-1 text-xs font-semibold uppercase tracking-[0.12em] text-menu-group-label-fg";

/**
 * A popover or hint that floats over the page, on the same surface as a menu.
 * It sets no position. The caller adds `absolute` or `fixed`; Tailwind emits
 * `relative` after both, so a `relative` here would pull the popover back
 * into the flow.
 */
export const popoverSurface = floatingSurface;

/**
 * `.panel { background:var(--panel); border:1px solid var(--border);
 * overflow:hidden }`, with the maia card's 2xl corner (13px at the preset's
 * radius, where the mockup drew 12px).
 */
export const panel =
  "app-panel min-w-0 overflow-hidden rounded-2xl border border-border bg-card text-card-foreground";

/**
 * `.eyebrow { font-size:12px; letter-spacing:.14em; text-transform:uppercase;
 * color:var(--accent-text); font-weight:600 }` — the scope line over an h1,
 * in gold-as-ink.
 */
export const eyebrow =
  "text-sm font-semibold uppercase tracking-[0.14em] text-accent-text";

/**
 * `.eyebrow.q { color:var(--muted) }`: the same caps line inside a panel,
 * where it names a section rather than the page's scope, so it is muted
 * rather than gold.
 */
export const eyebrowQuiet =
  "text-sm font-semibold uppercase tracking-[0.14em] text-muted-foreground";

export const mono = "font-mono";

/**
 * `.note { border-left:2px solid var(--gold); padding:2px 0 2px 12px;
 * font-size:12.5px; color:var(--muted) }`: the one sentence under a table or
 * a chart that says how to read it. The gold rule is identity, not state.
 */
export const note =
  "border-l-2 border-gold py-0.5 pl-3 text-base text-muted-foreground";

/**
 * `.kv { display:grid; grid-template-columns:auto 1fr; gap:7px 16px;
 * font-size:12.5px }`, `.kv dt { color:var(--dim) }` and `.kv dd
 * { color:var(--body); overflow-wrap:anywhere }`: a record's fields, label
 * left in the dim ink and value right.
 */
export const kvList =
  "grid grid-cols-[auto_1fr] items-baseline gap-x-4 gap-y-[7px] text-base";
export const kvTerm = "whitespace-nowrap text-dim";
export const kvValue = "m-0 min-w-0 text-foreground [overflow-wrap:anywhere]";

/**
 * `.b.b-q.lk` (the Run header's checkout strip): a quiet pill that is a link
 * or a copy button, so it carries the gold border and the wash on hover that
 * the badges around it do not.
 */
export const linkChip =
  "inline-flex min-w-0 max-w-full items-center gap-[5px] whitespace-nowrap rounded-md border border-border bg-hl px-[7px] py-0.5 text-sm font-semibold leading-normal tracking-[0.02em] text-muted-foreground transition-colors hover:border-gold hover:bg-hl hover:no-underline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-ring";

/**
 * `.panel-h { padding:12px 16px; border-bottom:1px solid var(--border) }` and
 * the maia card title's 14px, on the `--panel-head` band: light grey
 * on paper, a step lighter than the panel on ink (ADR-170). The footer keeps
 * the hairline and stays flat on the panel.
 */
export const panelHeader =
  "flex flex-wrap items-center justify-between gap-3 border-b border-border bg-panel-head px-4 py-3";
export const panelTitle = "text-base font-semibold text-foreground";
export const panelFooter =
  "flex flex-wrap items-center justify-between gap-3 border-t border-border px-4 py-3 text-sm text-muted-foreground";
/** `.panel-b { padding:14px 16px }` */
export const panelBody = "px-4 py-3.5";

/**
 * `.stat { background:var(--panel); border:1px solid var(--border);
 * padding:13px 15px }` with the panel's 2xl corner, `.stat .k` (10.5px caps, dim),
 * `.stat .v` (23px, 700, tabular) and `.stat .s` (11.5px, muted). One tile of
 * a figure strip; every strip on every page draws these four. On a phone the
 * tile tightens to `#viewport.phone .stat { padding:11px 12px }` and its
 * figure to `.stat .v { font-size:17px }`, so two tiles fit a row. The kit sets
 * the label at the 2xs step (`text-xs`, 10px), the note at the micro step
 * (`text-sm`, 12px), and the figure at the h2 step (24px, 16px on a phone).
 */
export const statTile =
  "flex min-w-0 flex-col rounded-2xl border border-border bg-card px-[15px] py-[13px] text-card-foreground max-md:px-3 max-md:py-[11px]";
export const statTerm =
  "mb-[5px] text-xs font-semibold uppercase tracking-[0.1em] text-dim";
export const statValue =
  "text-(length:--ox-a-h2) font-bold leading-[1.15] tracking-[-0.02em] tabular-nums max-md:text-(length:--ox-a-h4)";
export const statNote = "mt-[3px] text-sm text-muted-foreground";
/**
 * `.grid.g4 { grid-template-columns:repeat(auto-fit,minmax(175px,1fr)); gap:14px }`,
 * and `#viewport.phone .g4 { grid-template-columns:1fr 1fr }`: a phone draws
 * the strip two by two rather than one tile to a row.
 */
export const statStrip =
  "grid grid-cols-2 gap-3.5 md:[grid-template-columns:repeat(auto-fit,minmax(175px,1fr))]";
