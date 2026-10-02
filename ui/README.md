# @oxagen/ui

The component kit for Oxagen's frontends. It is built on
[Base UI](https://base-ui.com/) and Tailwind v4, and every colour, radius, and
face comes from the house tokens one directory up.

The kit moved here from oxagen `packages/ui` at `ddb85803`, with the generic
half of oxagen `apps/app/src/ui`. The oxagen monorepo still carries its own
`packages/ui` until it consumes this one.

The package ships TypeScript source with no build step. A consumer compiles it
with its own bundler. The design-system bundle below is the one compiled form.

## Boundary

- **Owns:** the components, `src/styles/globals.css`, the theme provider and
  cookie, the motion helpers, `cn`, the Storybook, the design-system bundle
  script, and `.design-sync/`.
- **Reads in place:** `../tokens/` for every value and `../fonts/` for every
  face. The kit keeps no copy of either.
- **Depends on:** no `@oxagen/*` package. `react`, `react-dom`, and
  `tailwindcss` are peer dependencies.

## Entry points

- `.` is `src/index.ts`: the component barrel, the providers, and `cn`.
- `./components/*` is one component file.
- `./styles/globals.css` is the stylesheet. It imports the house tokens and
  fonts from `../tokens/`.
- `./lib/motion` is the motion helpers.

## Rules

1. Composition uses the `render` prop. Radix `asChild` does not exist here.
2. Overlay parts are named `*Popup` or `*Panel`.
3. Reskin by editing tokens. A component class string never names a hex, a
   Tailwind palette colour, or a house token.
4. Icons come from `@phosphor-icons/react`, regular weight, with the `Icon`
   suffix: `import { XIcon } from "@phosphor-icons/react"`.
5. Overlays animate on Base UI's `data-[starting-style]` and
   `data-[ending-style]`.
6. Every component has a story for each state it draws.

```tsx
<Button render={<Link href="/login" />}>Log in</Button>
<DialogPopup>…</DialogPopup>
```

## Storybook

Storybook runs the components from `src` with Tailwind v4 and the tokens
processed through `postcss.config.mjs`. The toolbar flips every story between
light and dark. It sets the theme class on `<html>` as well as the story
wrapper, so portalled menus and dialogs follow it.

```bash
pnpm install
pnpm storybook         # http://localhost:6008
pnpm build-storybook   # static build in storybook-static/
```

Stories sit beside their component as `src/components/<name>.stories.tsx`. The
sidebar groups them by `title`: Foundations, Primitives, Forms, Surfaces,
Navigation, Overlays, Brand, and Pages. `src/docs/overview.mdx` is the first
page in the sidebar. It explains the groups, the docs pages, and the rules.

Each stories file gets a docs page, because `.storybook/preview.tsx` sets the
`autodocs` tag on every story. The page's description is the `/** ... */`
comment above the file's `meta`, and each story's description is the comment
above that story. A file whose stories open a popup on load sets
`parameters.docs.story` to `{ inline: false, height }`, so each story draws in
its own frame. The `Pages/` stories opt out with `tags: ["!autodocs"]`.

The `Pages/` stories show the kit at page scale: two website pages (Home and
Security) and two app pages (Runs and Run detail), each in light and dark, with
its menus, popover, command menu, or toast open over real content. They live in
`src/pages/`. Each page's body is `<page>.tsx`, its stories are
`<page>.stories.tsx`, and the website's nav and the app's shell and header are
in `page-chrome.tsx`. They are fixtures, so the barrel, the bundle, and the
bundle's types leave them out. A story that sets `parameters: { page: true }`
renders without the 24px frame, so its sticky bar meets the top of the frame.

A push to `main` deploys the static build to
[brand.oxagen.cloud/storybook](https://brand.oxagen.cloud/storybook/).

## Design-system bundle

```bash
pnpm build:design-system
```

It writes `components/bundle.js`, which sets `window.OxagenUI`, with
`components/bundle.css` and `components/index.d.ts`. The bundle feeds the
Claude Design project named in `.design-sync/config.json`.
`.design-sync/conventions.md` and `NOTES.md` tell a generator how to compose
the kit.

## CI

`.github/workflows/ui.yml` runs on a pull request that touches `ui/`,
`tokens/`, `fonts/`, or the Vercel config, and on every push to `main`. Each
job installs with `--frozen-lockfile`. The four jobs are `typecheck`, `test`,
`storybook`, and `bundle`, and the last two upload `storybook-static` and
`design-system-bundle` as artifacts. On `main`, a fifth job deploys the whole
site to Vercel.

## Tests

Each component's test sits beside it as `src/components/<name>.test.tsx`.
Vitest runs in node by default. A file that renders starts with
`// @vitest-environment jsdom`. `src/test/expect-no-axe.ts` runs axe on a
render. CI runs the suite. Do not run it on a laptop.

## Component inventory

Import from `@oxagen/ui`.

### Foundations

| Story | Shows |
|---|---|
| Typography | the app type scale, the three house faces, and their roles |
| Icons | the Phosphor icons the kit uses, by the name it uses them under |

### Primitives

| Component | File | Parts and API |
|---|---|---|
| Button | `button.tsx` | `Button` with `render`. Variants `primary`, `default`, `secondary`, `outline`, `ghost`, `destructive`, `destructive-outline`, `link`, and `gradient`. Sizes run from `xs` at 28px to `xl` at 44px, and `default` is 36px. |
| Badge | `badge.tsx` | `Badge` with `render`. Semantic variants `info`, `success`, `warning`, and `error`, each with a `-soft` form, plus `proven-soft` and `critical-soft`. `quiet`, `chip`, and `label` are for counts, filters, and field names. |
| ToneBadge | `tone-badge.tsx` | `ToneBadge` for a record's state, drawn by shape as well as colour. `TONE_BADGE_TONES` lists the tones. |
| Alert | `alert.tsx` | `Alert`, `AlertTitle`, and `AlertDescription`. |
| Separator | `separator.tsx` | `Separator` with `orientation`. |
| Skeleton | `skeleton.tsx` | `Skeleton`. |
| Spinner | `spinner.tsx` | `Spinner` with `size` and an `sr-only` label. |
| StellaSpinner | `stella-spinner.tsx` | The Stella asterisk turning under the house shimmer. |
| StatusDot | `status-dot.tsx` | `StatusDot` with `status`, `pulse`, and `label`. |
| Label | `label.tsx` | `Label`. |

### Forms

| Component | File | Parts and API |
|---|---|---|
| Input | `input.tsx` | `Input` with `size`. |
| Textarea | `textarea.tsx` | `Textarea` with `size`. |
| Field | `field.tsx` | `Field` and `PasswordField`: a label, a control, a hint, and an error. |
| Checkbox | `checkbox.tsx` | `Checkbox`, with indeterminate. |
| Switch | `switch.tsx` | `Switch`. |
| RadioGroup | `radio-group.tsx` | `RadioGroup` and `Radio`. |
| ChoiceGroup | `choice-group.tsx` | `ChoiceGroup`: one choice drawn as a row of option cards. A taken option stays focusable and says why. |
| SegmentedControl | `segmented-control.tsx` | `SegmentedControl` and `SegmentedControlItem`, single select, string value. |
| ToggleGroup | `toggle-group.tsx` | `ToggleGroup` and `ToggleGroupItem`: the outline toggle group for filters that show or hide rows by state. An item can carry a count. |
| Slider | `slider.tsx` | `Slider` and its parts. |
| Select | `select.tsx` | `Select`, `SelectTrigger`, `SelectValue`, `SelectPopup`, `SelectGroup`, `SelectLabel`, and `SelectItem`. Use it for 20 options or fewer. |
| Combobox | `combobox.tsx` | `Combobox` and its parts, for more than 20 options. The empty message shows only when nothing matches. |
| SearchInput | `search-input.tsx` | `SearchInput`: an input with a leading glyph and a clear button. |
| FormAlert, SubmitButton, OutcomePanel | `form-feedback.tsx` | A form's error, its pending submit, and the result it lands on. |
| Control styles | `control-styles.ts` | The shared class strings for buttons, fields, menu surfaces, and the sticky glass bar (`glassBar`). |

### Surfaces

| Component | File | Parts and API |
|---|---|---|
| Card | `card.tsx` | `Card`, `CardHeader`, `CardTitle`, `CardDescription`, `CardPanel`, and `CardFooter`. |
| Panel | `panel.tsx` | `Panel` with `eyebrow`, `title`, `actions`, `footer`, and `inset`. |
| PageHeader | `page-header.tsx` | `PageHeader`: the page's one h1, with an eyebrow, a description, metadata, and actions. |
| Table | `table.tsx` | `Table` and its parts, with `density`, plus `TableGroupRow` and `TableEmpty`. `TableHead` and `TableCell` take `numeric`. From 768px up the table is at least 560px wide and scrolls inside its own container. `narrow` drops that floor. |
| DataTable | `data-table.tsx` | `DataTable` with the `cell`, `numericCell`, and `headCell` class strings. |
| TruncatedCell | `truncated-cell.tsx` | `TruncatedCell`: a cell that clips its text and opens a hover card with the full value, only when the text is clipped. The card opens after 500 ms. |
| Stat | `stat.tsx` | `Stat` and `StatGroup`: a figure tile and its row. |
| EmptyState | `empty-state.tsx` | `EmptyState` with `variant`. |
| StateWrap | `state-wrap.tsx` | A full-width failed, denied, or neutral state with its facts. |
| KeyValueList | `key-value-list.tsx` | `KeyValueList` for dense metadata. |
| CopyButton | `copy-button.tsx` | `CopyButton` and `useCopyToClipboard`. |
| ProseMarkdown | `prose-markdown.tsx` | Markdown in the house type, through streamdown. |
| MessageScroller | `message-scroller.tsx` | shadcn's maia message scroller, with a button back to the newest message. |

### Navigation

| Component | File | Parts and API |
|---|---|---|
| Tabs | `tabs.tsx` | `Tabs`, `TabsList`, `TabsTab`, `TabsCount`, `TabsPanel`, and `TabsIndicator`. The default list is a muted track, and `TabsTab` takes a `count` for its badge. `variant="underline"` is for tabs inside a dialog. |
| Pagination | `pagination.tsx` | `RowsPager` and `RowsField`: rows per page on the left, Previous and Next on the right. |
| List controls | `list-controls.tsx` | `useList`, `ListBar`, and `ListPager` for a sorted, filtered, paged list. |
| pageList | `page-list.tsx` | The page-number sequence with gaps. |

### Overlays

| Component | File | Parts and API |
|---|---|---|
| Dialog | `dialog.tsx` | `Dialog`, `DialogTrigger`, `DialogPopup`, `DialogHeader`, `DialogPanel`, `DialogFooter`, `DialogTitle`, `DialogDescription`, and `DialogClose`. The box sits 70px from the top. `size="wide"` makes it 820px in place of 600px. The box has no padding, so content goes in the header, the panel, and the footer. |
| Sheet | `sheet.tsx` | `Sheet` and its parts, with `side` on `SheetPopup`. Like the dialog, its box has no padding. |
| Menu | `menu.tsx` | `Menu` and its parts. Items take `onClick`. |
| Popover | `popover.tsx` | `Popover` and its parts. |
| HoverCard | `hover-card.tsx` | `HoverCard` and `HoverCardContent`, for text a surface cuts off. `TruncatedCell` uses it. |
| Tooltip | `tooltip.tsx` | `Tooltip` and its parts, under `TooltipProvider`. |
| CommandMenu | `command-menu.tsx` | `CommandMenu` takes `groups` of commands and opens on Cmd+K or Ctrl+K: a search field over the grouped commands, with an empty line when nothing matches. `CommandMenuRoot`, `CommandMenuPopup`, `CommandMenuInput`, `CommandMenuList`, `CommandMenuItem`, and the other parts build a custom one. |

Menus, selects, comboboxes, popovers, hover cards, the command menu, and
toasts share one translucent surface. [Glass](#glass) below sets the rule.

### Feedback

| Component | File | Parts and API |
|---|---|---|
| Toast | `toast.tsx` | `ToastProvider`, `ToastViewport`, and `useToast`. Four tones: `success`, `info`, `warn`, and `error`, with `warning` as another name for `warn`. A toast lasts 4200 ms and pauses while the pointer is over it. |
| Attachment | `attachment.tsx` | `Attachment` and its parts: a media tile, a name, a kind and size, and a remove action. It shimmers while it uploads. `AttachmentCard` draws one `AttachmentFile` in the composer, and `ATTACHMENT_ACCEPT` lists the file types the attach button takes. |
| Composer | `composer.tsx` | `Composer`, the assistant composer with an attach button and its attachment cards, and `ComposerSentTurn`, the turn it leaves in the thread. The root is a `<form>`, so do not nest it in another form. |

### Brand

| Component | File | Parts and API |
|---|---|---|
| Logo | `brand.tsx` | `OxagenWordmark`, `OxagenIcon`, `StellaWordmark`, `StellaIcon`, and `BrandMark`, with the graph's `NodeChip` and `ConfidenceBar`. There is no lockup export: the wordmark is Oxagen's logo. |
| Brand marks | `brand-marks.generated.ts` | The mark paths and gold, generated from the house marks. |
| HexField | `hex-field.tsx` | The hexagon backdrop. It is not in the barrel. |

### Providers and hooks

| Export | File | Notes |
|---|---|---|
| `ThemeProvider`, `useTheme`, `THEME_COOKIE_NAME` | `theme-provider.tsx`, `theme-config.ts` | Cookie-based theming with no flash. |
| `MotionProvider` | `motion-provider.tsx` | The motion config. |
| `useExitGuard` | `exit-guard.ts` | Holds the window while a value exists only on this screen. |
| `useExpiryClock` | `expiry-clock.ts` | The clock a row judges its own expiry against, so a stale row stops saying active. |
| `FocusedHeading` | `focused-heading.tsx` | The heading of a result that replaced a form. It takes focus once, on mount. |
| `GlobalErrorPage`, `NotFoundPage` | `global-error.tsx`, `not-found.tsx` | Full-page templates. |
| `cn` | `lib/utils.ts` | `clsx` with `tailwind-merge`. |

## Glass

Glass belongs only on chrome that floats over content: menus, selects,
comboboxes, popovers, hover cards, the command menu, toasts, a dialog's scrim,
and sticky navigation and header bars. Cards, panels, tables, and text never
take it.

- **Floating surface.** `floatingSurface` in `control-styles.ts` draws every
  menu, select, combobox, popover, and hover card, the command menu, and the
  toast. It is the popover ground at 70% over a 40px blur at 150% saturation,
  with a faint ring in place of a border, a deep shadow, and a 16px corner.
  Its rows are 8px by 12px with 14px text. The ring and the shadow are the
  `--pop-ring` and `--ui-shadow-pop` tokens in `globals.css`. The tooltip
  stays opaque.
- **Sticky bar.** `glassBar` draws the website's nav and the app's header. It
  is the page ground at 72% over a 24px blur at 150% saturation, with a
  hairline under it. Text set straight on the bar takes the foreground ink,
  which stays above 8:1 in both themes whatever scrolls under it. Secondary
  text sits on an opaque control, such as a tab track or a badge.
- **Scrim.** A dialog's scrim dims the page and blurs it by 3px. The command
  menu's scrim dims without a blur, so the menu's own blur has the page to
  work on.
- **Fallbacks.** Each recipe carries a hook class: `glass-pop`, `glass-bar`,
  and `glass-scrim` on the dialog's scrim. The GLASS section of `globals.css`
  reads only those hooks, so no component changes when a fallback applies. A
  browser with no `backdrop-filter` draws each glass surface opaque on its own
  ground. Under `prefers-reduced-transparency: reduce`, which only Chromium
  supports today, each glass surface turns opaque and drops its blur. A scrim
  keeps its dim either way, since an opaque scrim would hide the page behind
  the dialog.

The `Pages/` stories show the rule at page scale.

## Styling

`src/styles/globals.css` maps the house tokens onto semantic roles and exposes
them to Tailwind through `@theme inline`. [`THEME.md`](./THEME.md) says which
file answers which question and states the rules a value cannot.

## Scripts

```bash
pnpm typecheck             # tsc --noEmit
pnpm test:unit             # vitest, in CI
pnpm test:coverage         # vitest with coverage thresholds
pnpm storybook             # Storybook on :6008
pnpm build-storybook       # static Storybook
pnpm build:types           # index.d.ts for the bundle
pnpm build:design-system   # bundle.js, bundle.css, and index.d.ts
```
