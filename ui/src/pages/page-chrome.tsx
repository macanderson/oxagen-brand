"use client";
// The chrome the `Pages/Website/` stories share: the website's sticky nav,
// section, footer, and the request answer chip. These are story fixtures.
// Nothing in `src/index.ts` exports them, and
// `.design-sync/tsconfig.types.json` leaves this folder out of the bundle's
// types. The `Pages/App/` stories draw the product app's own chrome, copied
// into `app/`.
//
// Each page's body lives in its own module (`website-home.tsx` and the
// rest), and its `.stories.tsx` file only sets the story's args. Every
// colour, face, radius, and shadow here comes from a kit token or recipe, so
// a change to a token reaches the pages with no edit.
//
// Type follows the house rule. The website's h1 to h3 wear text-m-h1 to
// text-m-h3, which set Space Grotesk, and its body text is 16px. No text is
// below 14px.
//
// Glass appears only where the kit's rule allows it: the sticky nav takes
// `glassBar`, and the menus and popovers take `floatingSurface` through their
// own components. Cards and panels take `panel`, which is opaque.
import * as React from "react";
import {
  ArrowRightIcon,
  CaretDownIcon,
  CoinsIcon,
  KeyIcon,
  PlayIcon,
  ShieldCheckIcon,
  TerminalWindowIcon,
  UsersThreeIcon,
  type Icon,
} from "@phosphor-icons/react";
import { OxagenWordmark } from "../components/brand";
import { Button } from "../components/button";
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
  "inline-flex h-9 items-center gap-1 rounded-4xl px-3 text-sm font-medium text-foreground transition-colors hover:bg-foreground/10 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-ring aria-[current=page]:bg-foreground/10 data-[popup-open]:bg-foreground/10";

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
        <span className="block text-sm leading-snug text-muted-foreground">
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
    <p className={cn("text-sm text-muted-foreground", className)}>{children}</p>
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
        <p className="mt-1 text-sm text-muted-foreground">{meta}</p>
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
          className="mt-auto inline-flex w-fit items-center gap-1.5 rounded-sm pt-5 text-sm font-medium text-foreground underline-offset-4 hover:underline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-ring"
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
            className="flex size-8 flex-none items-center justify-center rounded-md border border-border bg-card font-mono text-sm text-foreground"
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
          <p className="mt-4 text-sm text-muted-foreground">
            Oxagen is workforce management for autonomous agents: give each
            agent an identity, set its authority and budget, equip it with
            tools and skills, and review what it did and what its operators
            spent, through a shared agent control plane.
          </p>
        </div>
        <nav aria-label="Footer" className="flex gap-6 text-sm">
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

/* ── State chips ──────────────────────────────────────────────────────────── */

/**
 * State is carried by shape as well as hue and word (system.md): allowed
 * takes a 3px double border, routed takes a dashed one, and denied a single
 * one. The double border drops the badge's padding so the chip keeps its
 * height.
 */
const SHAPE = {
  double: "border-[3px] border-double py-0",
  dashed: "border-dashed",
  single: "",
} as const;

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
