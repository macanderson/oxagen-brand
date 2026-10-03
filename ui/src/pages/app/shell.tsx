// The product app's shell, copied from oxageninc/product
// apps/app/src/features/shell/ (shell-frame.tsx, sidebar.tsx, switchers.tsx,
// assistant-launcher.tsx, topbar.tsx, user-menu.tsx) at fad620bcef
// (2026-10-02): the rail on the left, the sticky top bar, and the page's one
// <main>. It keeps the app's markup and classes. The dialogs, drawers, and
// menus the chrome opens are left out, so its buttons open nothing here.
import type * as React from "react";
import { Fragment } from "react";
import {
  BellIcon,
  BuildingsIcon,
  CaretRightIcon,
  CaretUpDownIcon,
  CoinsIcon,
  CompassIcon,
  CrosshairIcon,
  FolderSimpleIcon,
  ListChecksIcon,
  ListIcon,
  MagnifyingGlassIcon,
  ReceiptIcon,
  RobotIcon,
  ShieldCheckIcon,
  type Icon,
} from "@phosphor-icons/react";
import { OxagenWordmark, StellaIcon } from "../../components/brand";
import { cn } from "../../lib/utils";
import { Avatar, Badge } from "./parts";
import { ORG, VIEWER, WORKSPACE } from "./fixtures";

export type NavKey =
  | "work"
  | "fleet"
  | "agents"
  | "steering"
  | "repositories"
  | "spend"
  | "organization"
  | "billing"
  | "audit";

const NAV_ICONS: Record<NavKey, Icon> = {
  work: ListChecksIcon,
  fleet: CrosshairIcon,
  agents: RobotIcon,
  steering: CompassIcon,
  repositories: FolderSimpleIcon,
  spend: CoinsIcon,
  organization: BuildingsIcon,
  billing: ReceiptIcon,
  audit: ShieldCheckIcon,
};

const NAV_LABELS: Record<NavKey, string> = {
  work: "Work",
  fleet: "Fleet",
  agents: "Agents",
  steering: "Steering",
  repositories: "Repositories",
  spend: "Spend",
  organization: "Organization",
  billing: "Billing",
  audit: "Audit",
};

const SECTIONS: readonly { key: string; label: string; items: readonly NavKey[] }[] = [
  { key: "workspace", label: "Workspace", items: ["work", "fleet", "agents", "steering", "repositories", "spend"] },
  { key: "organization", label: "Organization", items: ["organization", "billing", "audit"] },
];

/** What waits on a person: Fleet's parked approvals (hot) and Steering's proposals. */
const COUNTS: Partial<Record<NavKey, { value: number; hot: boolean }>> = {
  fleet: { value: 2, hot: true },
  steering: { value: 3, hot: false },
};

const tileClass =
  "mb-[7px] flex w-full items-center gap-[9px] rounded-[10px] border border-border bg-card px-2.5 py-2 text-left text-card-foreground transition-colors hover:border-rule focus-visible:outline-2 focus-visible:outline-ring";

function Switcher({
  title,
  avatar,
  name,
  sub,
}: {
  title: string;
  avatar: React.ReactNode;
  name: string;
  sub: string;
}) {
  return (
    <button type="button" aria-haspopup="dialog" className={tileClass}>
      <span className="sr-only">{title}</span>
      {avatar}
      <span className="min-w-0 flex-1">
        <b className="block truncate text-[13px] font-semibold">{name}</b>
        <span className="block truncate font-mono text-[11px] text-muted-foreground">{sub}</span>
      </span>
      <CaretUpDownIcon aria-hidden="true" className="size-3.5 flex-none text-muted-foreground" />
    </button>
  );
}

function Sidebar({ current }: { current: NavKey }) {
  return (
    <aside
      aria-label="Sidebar"
      className="sticky top-0 z-40 hidden h-dvh flex-col overflow-y-auto border-r border-sidebar-border bg-sidebar-bg text-sidebar-fg md:col-start-1 md:row-span-2 md:row-start-1 md:flex"
    >
      <div className="border-b border-sidebar-border px-3.5 pb-3 pt-4">
        <a
          href="#organization"
          className="mb-3 inline-flex rounded-sm px-1 focus-visible:outline-2 focus-visible:outline-ring"
          aria-label="Oxagen"
        >
          <OxagenWordmark className="h-6" />
        </a>
        <Switcher
          title="Switch organization"
          avatar={<Avatar initials={ORG.name.slice(0, 1).toUpperCase()} size={24} shape="agent" tone="gold" />}
          name={ORG.name}
          sub={ORG.slug}
        />
        <Switcher
          title="Switch workspace"
          avatar={<Avatar initials={WORKSPACE.slug.slice(0, 2)} size={24} shape="agent" font="mono" />}
          name={WORKSPACE.name}
          sub={`${ORG.slug}/${WORKSPACE.slug}`}
        />
      </div>
      <nav aria-label="Main" className="flex-1 px-2.5 py-3">
        {SECTIONS.map((section) => (
          <div key={section.key} className="mb-3">
            <p
              id={`app-nav-${section.key}`}
              className="px-2 pb-1.5 pt-3 text-[10.5px] font-semibold uppercase tracking-[0.13em] text-sidebar-nav-label-fg"
            >
              {section.label}
            </p>
            <ul aria-labelledby={`app-nav-${section.key}`}>
              {section.items.map((key) => {
                const NavIcon = NAV_ICONS[key];
                const on = key === current;
                const waiting = COUNTS[key];
                return (
                  <li key={key}>
                    <a
                      href={`#${key}`}
                      aria-current={on ? "page" : undefined}
                      data-nav={key}
                      className={`mb-px flex items-center gap-2.5 rounded-lg px-[9px] py-[7px] text-[13.5px] font-medium transition-colors focus-visible:outline-2 focus-visible:outline-ring ${
                        on
                          ? "bg-sidebar-nav-link-active-bg text-sidebar-nav-link-active-fg shadow-[inset_2px_0_0_var(--gold)]"
                          : "text-sidebar-nav-link-fg hover:bg-sidebar-nav-link-hover-bg hover:text-sidebar-nav-link-hover-fg"
                      }`}
                    >
                      <NavIcon aria-hidden="true" className="size-4 flex-none opacity-85" />
                      <span className="flex-1">{NAV_LABELS[key]}</span>
                      {waiting === undefined ? null : (
                        <span
                          data-count={key}
                          className={`rounded-[5px] border bg-card px-[5px] font-mono text-[10.5px] ${
                            waiting.hot ? "border-info/40 text-info" : "border-border text-sidebar-nav-label-fg"
                          }`}
                        >
                          <span aria-hidden="true">{waiting.value}</span>
                          <span className="sr-only">, {waiting.value} waiting</span>
                        </span>
                      )}
                    </a>
                  </li>
                );
              })}
            </ul>
          </div>
        ))}
      </nav>
      <div className="mt-auto border-t border-sidebar-border px-2.5 pb-3 pt-2.5">
        <button
          type="button"
          aria-haspopup="dialog"
          aria-expanded={false}
          className="mb-2 flex w-full items-center gap-2.5 rounded-[10px] border border-border bg-card px-2.5 py-2 text-left text-card-foreground transition-colors hover:border-rule focus-visible:outline-2 focus-visible:outline-ring"
        >
          <StellaIcon className="size-7 flex-none" />
          <span className="min-w-0 flex-1">
            <span className="block text-sm font-semibold">
              Ask{" "}
              <span className="ox-wordmark">
                stella
                <span aria-hidden="true" className="ox-wordmark-accent">
                  *
                </span>
              </span>
            </span>
          </span>
          <CaretRightIcon aria-hidden="true" className="size-3.5 flex-none text-sidebar-nav-label-fg" />
        </button>
        <div className="flex items-center justify-end gap-2 px-1">
          <span title="The control plane answered when this page loaded, and the browser is online.">
            <Badge tone="allowed">connected</Badge>
          </span>
        </div>
      </div>
    </aside>
  );
}

export type Crumb = { text: string; href: string | null; mono?: boolean };

const iconButton =
  "relative grid size-8 place-items-center rounded-lg border bg-card transition-colors focus-visible:outline-2 focus-visible:outline-ring border-border text-muted-foreground hover:border-rule hover:text-foreground";

function Topbar({ crumbs }: { crumbs: readonly Crumb[] }) {
  return (
    <header
      aria-label="Top bar"
      className="sticky top-0 z-30 flex items-center gap-3 border-b border-app-topbar-border bg-app-topbar-bg/90 px-4 pb-2.5 pt-[calc(0.625rem+env(safe-area-inset-top))] text-app-topbar-fg backdrop-blur md:col-start-2 md:row-start-1 md:px-5"
    >
      <button type="button" className={cn(iconButton, "md:hidden")} aria-label="Open navigation">
        <ListIcon aria-hidden="true" className="size-4" />
      </button>
      <nav aria-label="Breadcrumb" className="min-w-0 flex-1">
        <ol className="flex min-w-0 items-center gap-1.5 text-sm">
          {crumbs.map((crumb, i) => (
            <Fragment key={crumb.text}>
              {i > 0 ? (
                <li aria-hidden="true" className="hidden text-muted-foreground md:block">
                  /
                </li>
              ) : null}
              <li
                className={cn(
                  "truncate",
                  i < crumbs.length - 1 && "hidden md:block",
                  crumb.mono && "font-mono text-[13px]",
                )}
              >
                {crumb.href === null ? (
                  <span aria-current="page" className="font-semibold text-app-topbar-fg">
                    {crumb.text}
                  </span>
                ) : (
                  <a href={crumb.href} className="text-app-link-fg hover:text-app-link-hover-fg">
                    {crumb.text}
                  </a>
                )}
              </li>
            </Fragment>
          ))}
        </ol>
      </nav>
      <button
        type="button"
        aria-keyshortcuts="Meta+K Control+K"
        aria-label="Search or run an action"
        className="flex items-center gap-2 rounded-[9px] border border-border bg-card px-2.5 py-1.5 text-[12.5px] text-muted-foreground transition-colors hover:border-rule hover:text-foreground focus-visible:outline-2 focus-visible:outline-ring lg:min-w-[190px]"
      >
        <MagnifyingGlassIcon aria-hidden="true" className="size-3.5" />
        <span className="hidden lg:inline">Search or run an action</span>
        <kbd
          aria-hidden="true"
          className="ml-auto hidden rounded border border-border bg-hl px-[5px] font-mono text-[10.5px] text-muted-foreground sm:inline"
        >
          ⌘K
        </kbd>
      </button>
      <button type="button" aria-haspopup="dialog" aria-label="Notifications, 4 unread" className={iconButton}>
        <BellIcon aria-hidden="true" className="size-4" />
        <span
          aria-hidden="true"
          className="absolute right-1.5 top-1.5 size-[7px] rounded-full border border-app-topbar-bg bg-info"
        />
      </button>
      <button type="button" aria-pressed={false} aria-label="Approvals, 2 waiting" className={iconButton}>
        <ShieldCheckIcon aria-hidden="true" className="size-4" />
        <span
          aria-hidden="true"
          className="absolute -right-1.5 -top-1.5 min-w-[18px] rounded-full border border-app-topbar-bg bg-info px-1 text-center font-mono text-[10px] font-semibold leading-4 text-info-foreground"
        >
          2
        </span>
      </button>
      <button
        type="button"
        aria-label={`User menu for ${VIEWER.name}`}
        className="flex rounded-full focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-ring"
      >
        <Avatar initials={VIEWER.initials} size={30} />
      </button>
    </header>
  );
}

/**
 * The app's frame: the rail, the top bar over the page, and the page's one
 * <main>. Each copied page wears `app-snapshot`, which scopes the app's own
 * style layer (app.css) to it.
 */
export function AppFrame({
  current,
  crumbs,
  children,
}: {
  current: NavKey;
  crumbs: readonly Crumb[];
  children: React.ReactNode;
}) {
  return (
    <div className="app-snapshot">
      <div className="min-h-dvh bg-app-panel-bg text-app-panel-fg md:grid md:grid-cols-[var(--sidebar-width)_minmax(0,1fr)] md:grid-rows-[auto_1fr]">
        <Sidebar current={current} />
        <Topbar crumbs={crumbs} />
        <div
          data-shell-page=""
          className="min-w-0 pb-[calc(6rem+env(safe-area-inset-bottom))] md:col-start-2 md:row-start-2 md:pb-0"
        >
          <main id="main" className="mx-auto flex w-full flex-col gap-4">
            {children}
          </main>
        </div>
      </div>
    </div>
  );
}
