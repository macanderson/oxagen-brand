// The product app's small shared parts, copied from oxageninc/product
// apps/app/src/ui/ (badge.tsx, avatar.tsx, table.tsx, page-header.tsx,
// route-tabs.tsx) at fad620bcef (2026-10-02). Each keeps the app's markup and
// classes, except that each font size, space, and corner reads the nearest kit
// token. What the app reads from its data layer or its router is a prop here:
// a tab is a link that calls `onSelect` in place of changing the URL.
import type * as React from "react";
import { cn } from "../../lib/utils";
import { cell, eyebrow as eyebrowStyle, headCell, tabCount, tabLink } from "./styles";

/* ── Badge ──────────────────────────────────────────────────────────────── */

/** The app's state vocabulary; `quiet` is the muted pill. */
export type BadgeTone = "allowed" | "approval" | "denied" | "proven" | "failed" | "critical" | "quiet";

const TONE: Record<BadgeTone, string> = {
  allowed: "border-success/40 bg-success/10 text-success",
  approval: "border-info/40 bg-info/10 text-info",
  denied: "border-warning/40 bg-warning/10 text-warning",
  proven: "border-proven/40 bg-proven/10 text-proven",
  failed: "border-error/40 bg-error/10 text-error-ink",
  critical: "border-critical/40 bg-critical/10 text-critical",
  quiet: "border-border bg-hl text-muted-foreground",
};

const badgeBase =
  "inline-flex items-center gap-1.25 whitespace-nowrap rounded-md border px-1.75 py-0.5 text-sm font-semibold leading-normal tracking-[0.02em]";

/** A dot and a word in a tinted pill, so the state survives greyscale. */
export function Badge({
  tone,
  dot = true,
  mono = false,
  title,
  children,
}: {
  tone: BadgeTone;
  /** The 5px dot in the state hue. `"pulse"` breathes, for a state happening now. */
  dot?: boolean | "pulse";
  /** Mono, lowercase, regular weight, as an enforcement tier reads. */
  mono?: boolean;
  title?: string;
  children: React.ReactNode;
}) {
  return (
    <span
      title={title}
      className={cn(badgeBase, TONE[tone], mono && "font-mono text-xs font-medium lowercase")}
    >
      {dot ? (
        <span
          aria-hidden="true"
          className={cn("size-[5px] flex-none rounded-full bg-current", dot === "pulse" && "animate-pulse")}
        />
      ) : null}
      {children}
    </span>
  );
}

/* ── Avatar ─────────────────────────────────────────────────────────────── */

export type AvatarTone = "solid" | "soft" | "line" | "gold" | "gold-deep";

const AVATAR_TONE: Record<AvatarTone, string> = {
  solid: "bg-foreground text-background border-foreground",
  soft: "bg-secondary text-foreground border-border",
  line: "bg-transparent text-foreground border-input-border",
  gold: "bg-gold text-on-gold border-gold",
  "gold-deep": "bg-gold-deep text-on-gold-deep border-gold-deep",
};

/**
 * A length that follows the app base: `px` at the shipped 14px base, and the
 * same share of the base when the theme editor or a site moves it.
 */
function baseLength(px: number): string {
  return `calc(var(--ox-a-base) * ${Number((px / 14).toFixed(4))})`;
}

/** One letter fills half the tile, two letters a little less. */
function initialsScale(letters: number): number {
  if (letters <= 1) return 0.5;
  if (letters === 2) return 0.42;
  return 0.36;
}

/** An initials tile, the avatar a person or an agent shows when none is set. */
export function Avatar({
  initials,
  size = 28,
  shape = "person",
  tone = "soft",
  font = "sans",
  glyph,
}: {
  initials: string;
  size?: number;
  shape?: "person" | "agent";
  tone?: AvatarTone;
  font?: "sans" | "mono";
  /** A designed avatar's glyph, in place of the initials. */
  glyph?: React.ReactNode;
}) {
  const radius = shape === "person" ? "rounded-full" : "rounded-lg";
  return (
    <span
      aria-hidden="true"
      style={{
        width: baseLength(size),
        height: baseLength(size),
        fontSize: baseLength(Math.round(size * initialsScale(initials.length))),
        letterSpacing: "0.02em",
      }}
      className={cn(
        "box-border inline-grid flex-none place-items-center overflow-hidden border align-middle leading-none [&_svg]:size-[56%]",
        radius,
        AVATAR_TONE[tone],
        font === "mono" ? "font-mono font-semibold" : "font-sans font-semibold",
      )}
    >
      {glyph ?? initials}
    </span>
  );
}

/* ── Money ──────────────────────────────────────────────────────────────── */

/** An amount, already formatted, in the mono face. */
export function Money({ children }: { children: string }) {
  return <span className="font-mono tabular-nums">{children}</span>;
}

/* ── Table ──────────────────────────────────────────────────────────────── */

export type TableColumn = { label: string; numeric?: boolean; hidden?: boolean };

export { cell };

export function Table({
  label,
  columns,
  children,
}: {
  label: string;
  columns: readonly TableColumn[];
  children: React.ReactNode;
}) {
  return (
    <div className="min-w-0 overflow-x-auto">
      <table aria-label={label} className="w-full min-w-[560px] border-collapse text-base">
        <thead>
          <tr className="border-b border-border">
            {columns.map((column) => (
              <th
                key={column.label}
                scope="col"
                aria-label={column.hidden === true ? column.label : undefined}
                className={cn(headCell, column.numeric === true ? "text-right" : "text-left")}
              >
                {column.hidden === true ? null : column.label}
              </th>
            ))}
          </tr>
        </thead>
        <tbody className="divide-y divide-border [&>tr]:transition-colors [&>tr:hover]:bg-hl">{children}</tbody>
      </table>
    </div>
  );
}

/* ── Page header ────────────────────────────────────────────────────────── */

/** The page's one h1, with its eyebrow, description, facts, and actions. */
export function PageHeader({
  title,
  mono = false,
  eyebrow,
  description,
  meta,
  actions,
  figure,
}: {
  title: string;
  mono?: boolean;
  eyebrow?: React.ReactNode;
  description?: React.ReactNode;
  meta?: React.ReactNode;
  actions?: React.ReactNode;
  figure?: React.ReactNode;
}) {
  return (
    <header className="flex flex-col gap-3 pb-4.5 sm:flex-row sm:items-start sm:justify-between">
      <div className="flex min-w-0 flex-col gap-1">
        {eyebrow ? <p className={`${eyebrowStyle} mb-1`}>{eyebrow}</p> : null}
        <div className="flex flex-wrap items-center gap-x-4 gap-y-2">
          <h1
            className={`min-w-0 text-2xl font-bold leading-tight text-foreground ${mono ? "break-all font-mono tracking-normal" : "tracking-[-0.015em]"}`}
          >
            {title}
          </h1>
          {figure}
        </div>
        {description ? <p className="max-w-[70ch] text-base text-muted-foreground">{description}</p> : null}
        {meta ? <div className="flex flex-wrap items-center gap-2 pt-1">{meta}</div> : null}
      </div>
      {actions ? <div className="flex shrink-0 flex-wrap items-center gap-2">{actions}</div> : null}
    </header>
  );
}

/* ── Route tabs ─────────────────────────────────────────────────────────── */

export type RouteTab = {
  name: string;
  label: string;
  count?: React.ReactNode;
  /** A mark after the count, such as the dot for a call parked on a run. */
  mark?: React.ReactNode;
};

/** A row of tabs the app draws as links. The selected tab carries the gold underline. */
export function RouteTabs({
  label,
  panel,
  tabs,
  selected,
  onSelect,
}: {
  label: string;
  panel: string;
  tabs: readonly RouteTab[];
  selected: string;
  onSelect: (name: string) => void;
}) {
  return (
    <div data-tab-row="" className="min-w-0 overflow-x-auto border-b border-border">
      <div role="tablist" aria-label={label} className="flex w-max min-w-full gap-0.5">
        {tabs.map((tab) => {
          const open = tab.name === selected;
          return (
            <a
              key={tab.name}
              href={`#${tab.name}`}
              role="tab"
              id={open ? `${panel}-tab` : undefined}
              aria-selected={open}
              aria-controls={open ? panel : undefined}
              tabIndex={open ? 0 : -1}
              data-tab={tab.name}
              className={tabLink}
              onClick={(event) => {
                event.preventDefault();
                onSelect(tab.name);
              }}
            >
              {tab.label}
              {tab.count === undefined ? null : <span className={tabCount}>{tab.count}</span>}
              {tab.mark ?? null}
            </a>
          );
        })}
      </div>
    </div>
  );
}

/** The body under a row of route tabs. */
export function RouteTabPanel({
  panel,
  ...props
}: Omit<React.ComponentProps<"div">, "id" | "role" | "aria-labelledby"> & { panel: string }) {
  return <div {...props} role="tabpanel" id={panel} aria-labelledby={`${panel}-tab`} />;
}
