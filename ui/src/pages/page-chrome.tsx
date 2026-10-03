"use client";
// The chrome the `Pages/` stories share: the website's sticky nav, section,
// and footer, and the app's shell, sticky header, status chips, and command
// list. These are story fixtures. Nothing in `src/index.ts` exports them, and
// `.design-sync/tsconfig.types.json` leaves this folder out of the bundle's
// types.
//
// Each page's body lives in its own module (`website-home.tsx` and the
// rest), and its `.stories.tsx` file only sets the story's args. A tool that
// wraps the pages, such as a theme editor (#63), imports a page component and
// renders it. Every colour, face, radius, and shadow here comes from a kit
// token or recipe, so a change to a token reaches the pages with no edit.
//
// Type follows the house rule. The website's h1 to h3 wear text-m-h1 to
// text-m-h3, which set Space Grotesk, and its body text is 16px. The app's
// headings wear text-a-*, which read --font-heading (Aeonik), and its body
// text is 14px, the app base. Labels, badges, and table headers take the
// smaller steps.
//
// Glass appears only where the kit's rule allows it: the sticky nav and
// header take `glassBar`, and the menus, popovers, the command menu, and the
// toast take `floatingSurface` through their own components. Cards and
// panels take `panel`, which is opaque.
import * as React from "react";
import {
  ArrowRightIcon,
  CaretDownIcon,
  CaretUpDownIcon,
  CoinsIcon,
  CurrencyDollarIcon,
  EnvelopeSimpleIcon,
  ExportIcon,
  GearIcon,
  KeyIcon,
  LightningIcon,
  ListChecksIcon,
  PauseIcon,
  PlayIcon,
  PlugsConnectedIcon,
  PlusIcon,
  RobotIcon,
  ShieldCheckIcon,
  SteeringWheelIcon,
  TerminalWindowIcon,
  UsersThreeIcon,
  WrenchIcon,
  type Icon,
} from "@phosphor-icons/react";
import { OxagenWordmark } from "../components/brand";
import { Button } from "../components/button";
import type { CommandMenuCommandGroup } from "../components/command-menu";
import {
  eyebrowQuiet,
  glassBar,
  panel,
} from "../components/control-styles";
import {
  Menu,
  MenuGroup,
  MenuGroupLabel,
  MenuItem,
  MenuPopup,
  MenuSeparator,
  MenuTrigger,
} from "../components/menu";
import { TabsCount } from "../components/tabs";
import {
  ToastProvider,
  ToastViewport,
  useToast,
  type ToastAddOptions,
} from "../components/toast";
import { ToneBadge, type ToneBadgeTone } from "../components/tone-badge";
import { cn } from "../lib/utils";

/* ── Website ──────────────────────────────────────────────────────────────── */

/** The website's measure: the theme's wrap (`--ox-wrap`) with 24px at each side. */
export const siteWrap = "mx-auto w-full max-w-[var(--ox-wrap)] px-6";

/**
 * A link set straight on the glass bar. It takes the foreground ink, which
 * holds its contrast whatever scrolls under the bar, and the row wash for the
 * current page.
 */
const barLink =
  "inline-flex h-9 items-center gap-1 rounded-4xl px-3 text-base font-medium text-foreground transition-colors hover:bg-foreground/10 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-ring aria-[current=page]:bg-foreground/10 data-[popup-open]:bg-foreground/10";

type ProductPage = { label: string; line: string; icon: Icon };

/** Each line is the approved title of the page's card in `messages/workforce/`. */
const PRODUCT_PAGES: readonly ProductPage[] = [
  {
    label: "Fleet",
    line: "Your agents. Their work. One place to act.",
    icon: UsersThreeIcon,
  },
  {
    label: "Access",
    line: "Answer each request when the agent makes it.",
    icon: KeyIcon,
  },
  {
    label: "Mandates",
    line: "Set the terms your agents work under.",
    icon: ShieldCheckIcon,
  },
  {
    label: "Spend",
    line: "Read your AI bill down to the work.",
    icon: CoinsIcon,
  },
  { label: "Run playback", line: "See what the agent saw.", icon: PlayIcon },
];

function ProductMenuRow({ label, line, icon: RowIcon }: ProductPage) {
  return (
    <MenuItem className="items-start gap-3 py-2.5" onClick={() => {}}>
      <RowIcon className="mt-0.5 text-muted-foreground" aria-hidden />
      <span className="min-w-0">
        <span className="block font-medium text-foreground">{label}</span>
        <span className="block text-base leading-snug text-muted-foreground">
          {line}
        </span>
      </span>
    </MenuItem>
  );
}

/**
 * The website's sticky nav on the glass bar: the wordmark, the Product menu,
 * two links, and the page's one gold action. `productMenuOpen` renders the
 * menu open. It is not modal, so the page still scrolls under the bar.
 */
export function SiteNav({
  current,
  productMenuOpen = false,
}: {
  current?: "security";
  productMenuOpen?: boolean;
}) {
  return (
    <header className={glassBar}>
      <div className={cn(siteWrap, "flex h-16 items-center gap-6")}>
        <a
          href="#top"
          className="rounded-md focus-visible:outline-2 focus-visible:outline-offset-4 focus-visible:outline-ring"
        >
          <OxagenWordmark />
        </a>
        <nav aria-label="Main" className="hidden items-center gap-1 md:flex">
          <Menu defaultOpen={productMenuOpen} modal={false}>
            <MenuTrigger className={barLink}>
              Product
              <CaretDownIcon className="size-3.5" aria-hidden />
            </MenuTrigger>
            <MenuPopup sideOffset={12} className="w-[22rem]">
              <MenuGroup>
                <MenuGroupLabel>Pages</MenuGroupLabel>
                {PRODUCT_PAGES.map((page) => (
                  <ProductMenuRow key={page.label} {...page} />
                ))}
              </MenuGroup>
              <MenuSeparator />
              <ProductMenuRow
                label="Wrappers"
                line="Claude Code, the Agent SDK, or a custom loop."
                icon={TerminalWindowIcon}
              />
            </MenuPopup>
          </Menu>
          <a
            href="#security"
            className={barLink}
            aria-current={current === "security" ? "page" : undefined}
          >
            Security
          </a>
          <a href="#docs" className={barLink}>
            Docs
          </a>
        </nav>
        <div className="ml-auto flex items-center gap-1">
          <a href="#sign-in" className={cn(barLink, "max-sm:hidden")}>
            Sign in
          </a>
          <Button variant="primary" render={<a href="#explore" />}>
            Explore Oxagen
          </Button>
        </div>
      </div>
    </header>
  );
}

/** A claim's scope, set small and muted beside the claim. */
export function Qualifier({
  className,
  children,
}: {
  className?: string;
  children: React.ReactNode;
}) {
  return (
    <p className={cn("text-base text-muted-foreground", className)}>{children}</p>
  );
}

/**
 * One website section: the house rhythm of a hairline on top and 44px above
 * and below, a muted eyebrow, an h2, a lead, and the claim's scope.
 */
export function SiteSection({
  id,
  eyebrow,
  title,
  lead,
  qualifier,
  aside,
  children,
}: {
  id?: string;
  eyebrow: string;
  title: string;
  lead?: React.ReactNode;
  qualifier?: React.ReactNode;
  /** Sits to the right of the heading from md up, such as a scope button. */
  aside?: React.ReactNode;
  children?: React.ReactNode;
}) {
  return (
    <section id={id} className="border-t border-border">
      <div className={cn(siteWrap, "py-11")}>
        <div className="flex flex-col gap-6 md:flex-row md:items-end md:justify-between">
          <div className="max-w-[44rem]">
            <p className={eyebrowQuiet}>{eyebrow}</p>
            <h2 className="mt-3 text-m-h2 text-foreground max-md:text-(length:--ox-m-h3)">
              {title}
            </h2>
            {lead ? (
              <p className="mt-4 text-m-body text-muted-foreground">{lead}</p>
            ) : null}
            {qualifier ? (
              <Qualifier className="mt-3">{qualifier}</Qualifier>
            ) : null}
          </div>
          {aside ? <div className="shrink-0">{aside}</div> : null}
        </div>
        {children ? <div className="mt-8">{children}</div> : null}
      </div>
    </section>
  );
}

/**
 * A website card on the `panel` recipe: opaque, a hairline, the card corner,
 * no shadow. The title is a plain noun. The approved line, when there is one,
 * opens the body.
 */
export function SiteCard({
  title,
  line,
  body,
  qualifier,
  meta,
  action,
}: {
  title: string;
  line?: string;
  body: React.ReactNode;
  qualifier?: string;
  /** A short fact under the title, such as who sets a clause. */
  meta?: string;
  /** A link at the foot of the card. */
  action?: string;
}) {
  return (
    <article className={cn(panel, "flex flex-col p-6")}>
      <h3 className="text-m-h3 text-foreground">{title}</h3>
      {meta ? (
        <p className="mt-1 text-base text-muted-foreground">{meta}</p>
      ) : null}
      <p className="mt-3 text-m-body text-[var(--body)]">
        {line ? (
          <>
            <span className="font-semibold text-foreground">{line}</span>{" "}
          </>
        ) : null}
        {body}
      </p>
      {qualifier ? <Qualifier className="mt-3">{qualifier}</Qualifier> : null}
      {action ? (
        <a
          href="#more"
          className="mt-auto inline-flex w-fit items-center gap-1.5 rounded-sm pt-5 text-base font-medium text-foreground underline-offset-4 hover:underline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-ring"
        >
          {action}
          <ArrowRightIcon className="size-3.5" aria-hidden />
        </a>
      ) : null}
    </article>
  );
}

/**
 * The three steps of an access request, from `access-keys` and the
 * `keys-*` entries, as the house's numbered list with square mono markers.
 */
const REQUEST_STEPS = [
  {
    title: "The agent asks.",
    body: "When a task needs a system, a scope, or an action the mandate does not already cover, the agent asks for it at the moment of use.",
  },
  {
    title: "The rule decides.",
    body: "A rule allows the request, denies it, or routes it to a person.",
  },
  {
    title: "The record keeps the answer.",
    body: "Each request routed through Oxagen is a row with the rule that answered it and, when routed, the name of the person who did.",
  },
] as const;

export function RequestSteps({ className }: { className?: string }) {
  return (
    <ol className={cn("grid gap-6", className)}>
      {REQUEST_STEPS.map((step, index) => (
        <li key={step.title} className="flex gap-4">
          <span
            aria-hidden
            className="flex size-8 flex-none items-center justify-center rounded-md border border-border bg-card font-mono text-base text-foreground"
          >
            {index + 1}
          </span>
          <div className="min-w-0">
            <p className="text-m-h4 font-semibold text-foreground">
              {step.title}
            </p>
            <p className="mt-1 text-m-body text-muted-foreground">
              {step.body}
            </p>
          </div>
        </li>
      ))}
    </ol>
  );
}

export function SiteFooter() {
  return (
    <footer className="border-t border-border">
      <div
        className={cn(
          siteWrap,
          "flex flex-col gap-6 py-11 md:flex-row md:items-start md:justify-between",
        )}
      >
        <div className="max-w-[34rem]">
          <OxagenWordmark className="h-6" />
          <p className="mt-4 text-base text-muted-foreground">
            Oxagen is workforce management for autonomous agents: give each
            agent an identity, set its authority and budget, equip it with
            tools and skills, and review what it did and what its operators
            spent, through a shared agent control plane.
          </p>
        </div>
        <nav aria-label="Footer" className="flex gap-6 text-base">
          {["Product", "Security", "Docs"].map((label) => (
            <a
              key={label}
              href={`#${label.toLowerCase()}`}
              className="rounded-sm text-foreground underline-offset-4 hover:underline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-ring"
            >
              {label}
            </a>
          ))}
        </nav>
      </div>
    </footer>
  );
}

/* ── App ──────────────────────────────────────────────────────────────────── */

type ShellPage = {
  key: string;
  label: string;
  icon: Icon;
  count?: number;
};

/** The app's pages, as the command menu story names them. */
const SHELL_PAGES: readonly ShellPage[] = [
  { key: "work", label: "Work", icon: ListChecksIcon },
  { key: "runs", label: "Runs", icon: LightningIcon },
  { key: "access", label: "Access", icon: KeyIcon, count: 3 },
  { key: "agents", label: "Agents", icon: RobotIcon },
  { key: "steering", label: "Steering", icon: SteeringWheelIcon },
  { key: "tools", label: "Tools", icon: WrenchIcon },
  { key: "spend", label: "Spend", icon: CurrencyDollarIcon },
];

const shellLink =
  "flex h-9 items-center gap-2.5 rounded-xl px-3 text-base font-medium text-sidebar-nav-link-fg transition-colors hover:bg-sidebar-nav-link-hover-bg hover:text-sidebar-nav-link-hover-fg focus-visible:outline-2 focus-visible:-outline-offset-2 focus-visible:outline-ring aria-[current=page]:bg-sidebar-nav-link-active-bg aria-[current=page]:text-sidebar-nav-link-active-fg [&_svg]:size-4 [&_svg]:shrink-0 [&_svg]:text-muted-foreground";

/**
 * The app's frame: an opaque sidebar that stays put, and a column whose
 * sticky header is the glass bar. The page scrolls the document, so the
 * column's content passes under the header.
 */
export function AppShell({
  current,
  children,
}: {
  current: string;
  children: React.ReactNode;
}) {
  return (
    <div className="flex min-h-screen">
      <aside className="sticky top-0 z-20 hidden h-screen w-60 shrink-0 flex-col border-r border-sidebar-border bg-sidebar-bg md:flex">
        <div className="flex h-16 items-center px-5">
          <OxagenWordmark className="h-6" />
        </div>
        <div className="px-3">
          <button
            type="button"
            className="flex h-10 w-full items-center gap-2.5 rounded-xl border border-border bg-card px-3 text-left text-base text-foreground transition-colors hover:bg-hl focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-ring"
          >
            <span className="min-w-0 flex-1">
              <span className="block text-sm text-muted-foreground">
                Workspace
              </span>
              <span className="block truncate font-medium leading-tight">
                platform
              </span>
            </span>
            <CaretUpDownIcon className="size-4 text-muted-foreground" aria-hidden />
          </button>
        </div>
        <nav aria-label="Workspace" className="mt-4 flex-1 px-3">
          <ul className="grid gap-0.5">
            {SHELL_PAGES.map(({ key, label, icon: PageIcon, count }) => (
              <li key={key}>
                <a
                  href={`#${key}`}
                  className={shellLink}
                  aria-current={current === key ? "page" : undefined}
                >
                  <PageIcon aria-hidden />
                  <span className="flex-1">{label}</span>
                  {count !== undefined ? (
                    <TabsCount>
                      {count}
                      <span className="sr-only"> waiting</span>
                    </TabsCount>
                  ) : null}
                </a>
              </li>
            ))}
          </ul>
        </nav>
        <div className="grid gap-0.5 border-t border-sidebar-border p-3">
          <a href="#settings" className={shellLink}>
            <GearIcon aria-hidden />
            Settings
          </a>
          <div className="flex items-center gap-2.5 px-3 py-2">
            <span
              aria-hidden
              className="flex size-7 items-center justify-center rounded-full bg-hl text-sm font-semibold text-foreground"
            >
              D
            </span>
            <span className="min-w-0 text-base">
              <span className="block truncate font-medium text-foreground">
                Dana
              </span>
              <span className="block truncate text-sm text-muted-foreground">
                Operator
              </span>
            </span>
          </div>
        </div>
      </aside>
      <div className="flex min-w-0 flex-1 flex-col">{children}</div>
    </div>
  );
}

/**
 * The app's sticky header on the glass bar: the page's one h1 with its
 * actions, then a row for route tabs and filters. Words set straight on the
 * bar take the foreground ink. Counts and filters sit on the opaque tab track
 * and toggle group.
 */
export function AppHeader({
  eyebrow,
  title,
  mono = false,
  actions,
  children,
}: {
  eyebrow?: React.ReactNode;
  title: string;
  /** Sets the title in the mono face, for a record whose title is its id. */
  mono?: boolean;
  actions?: React.ReactNode;
  /** The second row: route tabs on the left, filters on the right. */
  children?: React.ReactNode;
}) {
  return (
    <header className={glassBar}>
      <div className="flex min-h-16 flex-wrap items-center gap-x-4 gap-y-2 px-6 py-3">
        <div className="min-w-0 flex-1">
          {eyebrow ? (
            <p className="text-sm font-semibold uppercase tracking-[0.14em] text-foreground">
              {eyebrow}
            </p>
          ) : null}
          <h1
            className={cn(
              "truncate text-a-h3 text-foreground",
              mono && "font-mono tracking-normal",
            )}
          >
            {title}
          </h1>
        </div>
        {actions ? (
          <div className="flex flex-wrap items-center gap-2">{actions}</div>
        ) : null}
      </div>
      {children ? (
        <div className="flex flex-wrap items-center justify-between gap-3 px-6 pb-3">
          {children}
        </div>
      ) : null}
    </header>
  );
}

/* ── State chips ──────────────────────────────────────────────────────────── */

/**
 * State is carried by shape as well as hue and word (system.md): allowed
 * takes a 3px double border, waiting and routed take a dashed one, and the
 * rest a single one. The double border drops the badge's padding so the chip
 * keeps its height.
 */
const SHAPE = {
  double: "border-[3px] border-double py-0",
  dashed: "border-dashed",
  single: "",
} as const;

export type RunStatus = "running" | "waiting" | "ended" | "failed" | "stopped";

const RUN_STATUS: Record<
  RunStatus,
  { tone: ToneBadgeTone; label: string; shape: keyof typeof SHAPE; dot?: "pulse" }
> = {
  running: { tone: "allowed", label: "Running", shape: "single", dot: "pulse" },
  waiting: { tone: "approval", label: "Waiting on approval", shape: "dashed" },
  ended: { tone: "quiet", label: "Ended", shape: "single" },
  failed: { tone: "failed", label: "Failed", shape: "single" },
  stopped: { tone: "denied", label: "Stopped", shape: "single" },
};

export function RunStatusBadge({ status }: { status: RunStatus }) {
  const { tone, label, shape, dot } = RUN_STATUS[status];
  return (
    <ToneBadge tone={tone} dot={dot ?? true} className={SHAPE[shape]}>
      {label}
    </ToneBadge>
  );
}

export type RequestAnswer = "allowed" | "denied" | "routed";

const ANSWER: Record<
  RequestAnswer,
  { tone: ToneBadgeTone; label: string; shape: keyof typeof SHAPE }
> = {
  allowed: { tone: "allowed", label: "Allowed", shape: "double" },
  denied: { tone: "denied", label: "Denied", shape: "single" },
  routed: { tone: "approval", label: "Routed", shape: "dashed" },
};

export function AnswerBadge({ answer }: { answer: RequestAnswer }) {
  const { tone, label, shape } = ANSWER[answer];
  return (
    <ToneBadge tone={tone} className={SHAPE[shape]}>
      {label}
    </ToneBadge>
  );
}

/* ── Command menu and toasts ──────────────────────────────────────────────── */

/** The command menu story's groups, with the run page's own actions first. */
export function commandGroups(
  extra: readonly CommandMenuCommandGroup[] = [],
): CommandMenuCommandGroup[] {
  return [
    ...extra,
    {
      label: "Go to",
      items: SHELL_PAGES.map(({ key, label, icon: PageIcon }) => ({
        value: key,
        label,
        icon: <PageIcon />,
        ...(key === "spend" ? { keywords: ["billing", "cost"] } : {}),
      })),
    },
    {
      label: "Create",
      items: [
        { value: "new-work", label: "New work item", icon: <PlusIcon /> },
        {
          value: "wrap",
          label: "Wrap an agent",
          icon: <PlugsConnectedIcon />,
          detail: "Claude Code, Codex CLI, or Stella",
        },
        {
          value: "invite",
          label: "Invite a person",
          icon: <EnvelopeSimpleIcon />,
        },
      ],
    },
  ];
}

/** The run page's own commands, for the command menu's first group. */
export const RUN_COMMANDS: CommandMenuCommandGroup = {
  label: "This run",
  items: [
    { value: "pause", label: "Pause run", icon: <PauseIcon /> },
    { value: "playback", label: "Play back run", icon: <PlayIcon /> },
    { value: "export", label: "Export record", icon: <ExportIcon /> },
  ],
};

/**
 * Adds toasts once on mount with `timeout: 0`, as `toast.stories.tsx` does,
 * so the story holds still and a screenshot taken at any moment matches.
 */
function PresetToasts({ toasts }: { toasts: readonly ToastAddOptions[] }) {
  const toast = useToast();
  const fired = React.useRef(false);
  React.useEffect(() => {
    if (fired.current) return;
    fired.current = true;
    for (const options of toasts) toast.add({ ...options, timeout: 0 });
  }, [toast, toasts]);
  return null;
}

/** The toast provider and viewport, with `toasts` up from the first frame. */
export function WithToasts({
  toasts = [],
  children,
}: {
  toasts?: readonly ToastAddOptions[];
  children: React.ReactNode;
}) {
  return (
    <ToastProvider>
      {children}
      {toasts.length > 0 ? <PresetToasts toasts={toasts} /> : null}
      <ToastViewport />
    </ToastProvider>
  );
}
