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
Navigation, Overlays, Feedback, and Brand.

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
| Button | `button.tsx` | `Button` with `render`. Variants `primary`, `default`, `secondary`, `outline`, `ghost`, `destructive`, `destructive-outline`, `link`, and `gradient`. |
| Badge | `badge.tsx` | `Badge` with `render`. Semantic variants `info`, `success`, `warning`, and `error`. |
| ToneBadge | `tone-badge.tsx` | `ToneBadge` for a record's state, drawn by shape as well as colour. |
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
| ToggleGroup | `toggle-group.tsx` | The outline toggle group for filters that show or hide rows by state. |
| Slider | `slider.tsx` | `Slider` and its parts. |
| Select | `select.tsx` | `Select`, `SelectTrigger`, `SelectValue`, `SelectPopup`, `SelectGroup`, `SelectLabel`, and `SelectItem`. Use it for 20 options or fewer. |
| Combobox | `combobox.tsx` | `Combobox` and its parts, for more than 20 options. |
| SearchInput | `search-input.tsx` | `SearchInput`: an input with a leading glyph and a clear button. |
| FormAlert, SubmitButton, OutcomePanel | `form-feedback.tsx` | A form's error, its pending submit, and the result it lands on. |
| Control styles | `control-styles.ts` | The shared class strings for buttons, fields, and menu surfaces. |

### Surfaces

| Component | File | Parts and API |
|---|---|---|
| Card | `card.tsx` | `Card`, `CardHeader`, `CardTitle`, `CardDescription`, `CardPanel`, and `CardFooter`. |
| Panel | `panel.tsx` | `Panel` with `eyebrow`, `title`, `actions`, `footer`, and `inset`. |
| PageHeader | `page-header.tsx` | `PageHeader`: the page's one h1, with an eyebrow, a description, metadata, and actions. |
| Table | `table.tsx` | `Table` and its parts, with `density`. It scrolls inside its own container. |
| DataTable | `data-table.tsx` | `DataTable` with the `cell`, `numericCell`, and `headCell` class strings. |
| TruncatedCell | `truncated-cell.tsx` | A cell that clips its text and opens a hover card with the full value, only when the text is clipped. |
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
| Tabs | `tabs.tsx` | `Tabs`, `TabsList`, `TabsTab`, and `TabsPanel`. The default list is a muted track with count badges. `variant="underline"` is for tabs inside a dialog. |
| Pagination | `pagination.tsx` | `RowsPager` and `RowsField`: rows per page on the left, Previous and Next on the right. |
| List controls | `list-controls.tsx` | `useList`, `ListBar`, and `ListPager` for a sorted, filtered, paged list. |
| pageList | `page-list.tsx` | The page-number sequence with gaps. |

### Overlays

| Component | File | Parts and API |
|---|---|---|
| Dialog | `dialog.tsx` | `Dialog`, `DialogTrigger`, `DialogPopup`, `DialogHeader`, `DialogPanel`, `DialogFooter`, `DialogTitle`, `DialogDescription`, and `DialogClose`. |
| Sheet | `sheet.tsx` | `Sheet` and its parts, with `side` on `SheetPopup`. |
| Menu | `menu.tsx` | `Menu` and its parts. Items take `onClick`. |
| Popover | `popover.tsx` | `Popover` and its parts. |
| HoverCard | `hover-card.tsx` | `HoverCard` for text a surface cuts off. |
| Tooltip | `tooltip.tsx` | `Tooltip` and its parts, under `TooltipProvider`. |
| CommandMenu | `command-menu.tsx` | The command menu: a search field over grouped commands. |

Menus, selects, popovers, hover cards, and the command menu share one
translucent surface: a blurred popover ground, a faint ring, a 16px radius,
and 12px items.

### Feedback

| Component | File | Parts and API |
|---|---|---|
| Toast | `toast.tsx` | `ToastProvider`, `ToastViewport`, and `useToast`. Four tones: success, warning, info, and error. A toast lasts 4200 ms. |
| Attachment | `attachment.tsx` | `Attachment` and its parts: a media tile, a name, a kind and size, and a remove action. It shimmers while it uploads. |
| Composer | `composer.tsx` | The assistant composer with an attach button and its attachment cards. |

### Brand

| Component | File | Parts and API |
|---|---|---|
| Logo | `brand.tsx` | `OxagenLogo`, `OxagenLogomark`, `OxagenWordmark`, `OxagenLockup`, and `BrandMark`. |
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
