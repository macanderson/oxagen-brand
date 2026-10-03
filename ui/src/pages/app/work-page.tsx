"use client";
// The product app's Work page, copied from oxageninc/product
// apps/app/src/features/work/ (work-page.tsx, work-table.tsx, words.tsx,
// new-item.tsx) at fad620bcef (2026-10-02). It keeps the app's markup and
// classes, so the theme editor shows the page as the app draws it. It reads
// the sample items in work-items.ts in place of the workspace's, and a tab
// switches the table on the page in place of changing the URL.
//
// The page will drift from the app. To refresh it, copy the same files from
// the app again and keep the data as props.
import * as React from "react";
import { PaperPlaneTiltIcon, PlusIcon } from "@phosphor-icons/react";
import { WORKSPACE } from "./fixtures";
import {
  Badge,
  Money,
  PageHeader,
  RouteTabPanel,
  RouteTabs,
  Table,
  type BadgeTone,
} from "./parts";
import { AppFrame } from "./shell";
import {
  buttonPrimary,
  buttonSecondary,
  buttonSmall,
  cell,
  linkText,
  mono,
  numericCell,
  panel,
  statNote,
  statStrip,
  statTerm,
  statTile,
  statValue,
} from "./styles";
import { WORK_ITEMS, type ChecksWord, type WorkItem, type WorkStatus, type WorkTab } from "./work-items";

const STATUS: Record<WorkStatus, { tone: BadgeTone; label: string }> = {
  triaging: { tone: "quiet", label: "Triaging" },
  triage_failed: { tone: "failed", label: "Triage failed" },
  needs_info: { tone: "approval", label: "Needs info" },
  brief_to_approve: { tone: "approval", label: "Brief to approve" },
  changed: { tone: "approval", label: "Changed" },
  ready: { tone: "allowed", label: "Ready" },
  waiting_for_claim: { tone: "quiet", label: "Waiting for claim" },
  running: { tone: "allowed", label: "Running" },
  stopping: { tone: "approval", label: "Stopping" },
  in_review: { tone: "approval", label: "In review" },
  accepted: { tone: "allowed", label: "Accepted" },
  done: { tone: "allowed", label: "Done" },
  closed: { tone: "quiet", label: "Closed" },
};

/** A status that is happening now breathes. */
const LIVE: ReadonlySet<WorkStatus> = new Set(["triaging", "running"]);

function WorkStatusBadge({ status }: { status: WorkStatus }) {
  const { tone, label } = STATUS[status];
  return (
    <Badge tone={tone} dot={LIVE.has(status) ? "pulse" : true}>
      {label}
    </Badge>
  );
}

const CHECKS: Record<ChecksWord, { tone: BadgeTone; label: string }> = {
  passing: { tone: "allowed", label: "Passing" },
  failing: { tone: "failed", label: "Failing" },
  running: { tone: "approval", label: "Running" },
};

function ChecksBadge({ word }: { word: ChecksWord }) {
  const { tone, label } = CHECKS[word];
  return <Badge tone={tone}>{label}</Badge>;
}

const PRIORITY_TONE: Record<"P0" | "P1" | "P2" | "P3", BadgeTone> = {
  P0: "critical",
  P1: "denied",
  P2: "approval",
  P3: "quiet",
};

/** The priority: the badge, then who set it, triage's reason, and the rules it cites. */
function PriorityCell({ priority }: { priority: WorkItem["priority"] }) {
  if (priority.label === null) return <span className="text-muted-foreground">none</span>;
  return (
    <span className="flex min-w-0 flex-col items-start gap-1">
      <Badge tone={PRIORITY_TONE[priority.label]} dot={false}>
        {priority.label}
      </Badge>
      <span className="text-[11.5px] text-muted-foreground" data-wrap="">
        {priority.setBy === undefined ? null : `Set by ${priority.setBy}. `}
        {priority.reason}
        {priority.cites.map((cite) => (
          <span key={cite} className={`${mono} ml-1 text-dim`}>
            {cite}
          </span>
        ))}
      </span>
    </span>
  );
}

/** What an item's runs cost: the known total and its coverage, or none yet. */
function CostText({ cost }: { cost: WorkItem["cost"] }) {
  if (cost.runs === 0) return <span className="text-muted-foreground">none yet</span>;
  return (
    <span className="inline-flex flex-col items-end gap-0.5">
      {cost.total === null ? <span className="text-muted-foreground">unknown</span> : <Money>{cost.total}</Money>}
      {cost.knownRuns < cost.runs ? (
        <span className="text-[11.5px] text-muted-foreground">
          {cost.knownRuns} of {cost.runs} runs known
        </span>
      ) : null}
    </span>
  );
}

/** The item's number and title (the row's link), what it waits for, and on Inbox its labels. */
function ItemCell({ item, labels }: { item: WorkItem; labels: boolean }) {
  return (
    <div className="flex min-w-0 flex-col gap-0.5">
      <a
        href={`#${item.number}`}
        className="inline-flex max-w-full items-baseline gap-2 rounded-sm font-medium text-foreground after:absolute after:inset-0 after:content-[''] focus-visible:outline-2 focus-visible:outline-ring"
      >
        <span className={`${mono} flex-none text-muted-foreground`}>{item.number}</span>{" "}
        <span className="min-w-0 [overflow-wrap:anywhere]">{item.title}</span>
      </a>
      <span className="text-[12.5px] text-muted-foreground" data-wrap="">
        {item.wait}
      </span>
      {labels && item.labels.length > 0 ? (
        <span className="flex flex-wrap gap-1 pt-0.5">
          {item.labels.map((label) => (
            <Badge key={label} tone="quiet" dot={false}>
              {label}
            </Badge>
          ))}
        </span>
      ) : null}
    </div>
  );
}

function Muted({ children }: { children: string }) {
  return <span className="text-muted-foreground">{children}</span>;
}

/** A row that opens its item: the title link is stretched over it. */
const ROW = "relative cursor-pointer";

function InboxTable({ items }: { items: readonly WorkItem[] }) {
  return (
    <Table
      label="Inbox"
      columns={[{ label: "Work item" }, { label: "Priority" }, { label: "State" }, { label: "Send", hidden: true }]}
    >
      {items.map((item) => (
        <tr key={item.number} className={ROW}>
          <td className={cell}>
            <ItemCell item={item} labels />
          </td>
          <td className={cell}>
            <PriorityCell priority={item.priority} />
          </td>
          <td className={cell}>
            <WorkStatusBadge status={item.status} />
          </td>
          <td className={`${cell} text-right`}>
            {item.status === "ready" ? (
              <a
                href={`#${item.number}-send`}
                aria-label={`Send ${item.number} to an agent`}
                className={`${buttonSmall} relative z-10`}
              >
                Send
              </a>
            ) : null}
          </td>
        </tr>
      ))}
    </Table>
  );
}

function RunningTable({ items }: { items: readonly WorkItem[] }) {
  return (
    <Table
      label="Running"
      columns={[{ label: "Work item" }, { label: "Target" }, { label: "Status" }, { label: "Cost", numeric: true }]}
    >
      {items.map((item) => (
        <tr key={item.number} className={ROW}>
          <td className={cell}>
            <ItemCell item={item} labels={false} />
          </td>
          <td className={cell}>
            {item.send === null ? (
              <Muted>none</Muted>
            ) : (
              <span className="flex flex-col">
                <span>{item.send.agent}</span>
                <span className="text-[12px] text-muted-foreground">{item.send.runtime}</span>
              </span>
            )}
          </td>
          <td className={cell}>
            <span className="flex flex-col items-start gap-1">
              <WorkStatusBadge status={item.status} />
              {item.send === null ? null : (
                <span className="text-[12px] text-muted-foreground">Sent on {item.send.sentOn}</span>
              )}
            </span>
          </td>
          <td className={numericCell}>
            <CostText cost={item.cost} />
          </td>
        </tr>
      ))}
    </Table>
  );
}

function ReviewTable({ items }: { items: readonly WorkItem[] }) {
  return (
    <Table
      label="Review"
      columns={[
        { label: "Work item" },
        { label: "Pull request" },
        { label: "Required checks" },
        { label: "Cost", numeric: true },
      ]}
    >
      {items.map((item) => {
        const pr = item.send?.pullRequest ?? null;
        return (
          <tr key={item.number} className={ROW}>
            <td className={cell}>
              <ItemCell item={item} labels={false} />
            </td>
            <td className={cell}>
              {pr === null ? (
                <Muted>none</Muted>
              ) : (
                <span className="flex flex-col">
                  <span className={mono}>#{pr.number}</span>
                  <span className={`${mono} text-[12px] text-muted-foreground`}>{pr.head}</span>
                </span>
              )}
            </td>
            <td className={cell}>{item.send === null ? <Muted>none</Muted> : <ChecksBadge word={item.send.checks} />}</td>
            <td className={numericCell}>
              <CostText cost={item.cost} />
            </td>
          </tr>
        );
      })}
    </Table>
  );
}

function DoneTable({ items }: { items: readonly WorkItem[] }) {
  return (
    <Table
      label="Done"
      columns={[
        { label: "Work item" },
        { label: "Result" },
        { label: "Agent" },
        { label: "Cost", numeric: true },
        { label: "Finished" },
      ]}
    >
      {items.map((item) => (
        <tr key={item.number} className={ROW}>
          <td className={cell}>
            <ItemCell item={item} labels={false} />
          </td>
          <td className={cell}>
            <WorkStatusBadge status={item.status} />
          </td>
          <td className={cell}>{item.send === null ? <Muted>none</Muted> : item.send.agent}</td>
          <td className={numericCell}>
            <CostText cost={item.cost} />
          </td>
          <td className={`${cell} whitespace-nowrap`}>{item.finished === null ? <Muted>none</Muted> : item.finished}</td>
        </tr>
      ))}
    </Table>
  );
}

function WorkTable({ tab, items }: { tab: WorkTab; items: readonly WorkItem[] }) {
  switch (tab) {
    case "inbox":
      return <InboxTable items={items} />;
    case "running":
      return <RunningTable items={items} />;
    case "review":
      return <ReviewTable items={items} />;
    case "done":
      return <DoneTable items={items} />;
  }
}

function Tile({ term, value, sub }: { term: string; value: string; sub: string }) {
  return (
    <div className={statTile}>
      <dt className={statTerm}>{term}</dt>
      <dd className={statValue}>{value}</dd>
      <dd className={statNote}>{sub}</dd>
    </div>
  );
}

function plural(count: number, one: string, other: string): string {
  return `${count} ${count === 1 ? one : other}`;
}

/** The banner a failing collector raises: what it reads and its last good read. */
function CollectorBanner() {
  return (
    <div className="flex flex-wrap items-start gap-x-3 gap-y-2 rounded-[10px] border border-error/40 bg-error/10 px-3.5 py-[11px] text-base text-foreground">
      <div className="flex min-w-0 grow flex-col gap-1">
        <p>
          <b className="font-semibold">Collector github is failing</b> It reads a-intel/platform and
          a-intel/billing-service. Last good read on Oct 2, 11:39 AM.
        </p>
      </div>
      <a href="#collectors" className={buttonSmall}>
        Open collectors
      </a>
    </div>
  );
}

const TABS: readonly { name: WorkTab; label: string }[] = [
  { name: "inbox", label: "Inbox" },
  { name: "running", label: "Running" },
  { name: "review", label: "Review" },
  { name: "done", label: "Done" },
];

export interface WorkPageProps {
  /** The tab open on load. */
  tab: WorkTab;
  /** Shows the banner a failing collector raises. */
  collectorFailing: boolean;
}

/** The Work page: the tiles, the tab row, and the open tab's table, in the app's shell. */
export function WorkPage({ tab: initial, collectorFailing }: WorkPageProps) {
  const [tab, setTab] = React.useState<WorkTab>(initial);
  React.useEffect(() => setTab(initial), [initial]);
  const on = (name: WorkTab) => WORK_ITEMS.filter((item) => item.tab === name);
  const groups: Record<WorkTab, readonly WorkItem[]> = {
    inbox: on("inbox"),
    running: on("running"),
    review: on("review"),
    done: on("done"),
  };
  const ready = groups.inbox.filter((item) => item.status === "ready").length;
  const waitingForRuntime = groups.running.filter((item) => item.status === "waiting_for_claim").length;
  const waitingForMerge = groups.review.filter((item) => item.status === "accepted").length;
  return (
    <AppFrame
      current="work"
      crumbs={[
        { text: "A-Intel", href: "#organization" },
        { text: WORKSPACE.name, href: "#workspace" },
        { text: "Work", href: null },
      ]}
    >
      <div className="flex flex-col gap-4">
        <PageHeader
          eyebrow={WORKSPACE.name}
          title="Work"
          description={
            <>
              Triage suggests priorities with{" "}
              <a href="#priorities" className={linkText}>
                a-intel.work.priorities v7
              </a>
              .
            </>
          }
          actions={
            <>
              <a href="#setup" className={buttonSecondary}>
                Setup
              </a>
              <a href="#outcomes" className={buttonSecondary}>
                Outcomes
              </a>
              <button type="button" className={buttonSecondary}>
                <PlusIcon aria-hidden="true" />
                New work item
              </button>
              <a href="#send" className={buttonPrimary}>
                <PaperPlaneTiltIcon aria-hidden="true" />
                Send to an agent
              </a>
            </>
          }
        />
        {collectorFailing ? <CollectorBanner /> : null}
        <dl aria-label="Work totals" className={statStrip}>
          <Tile
            term="Ready to send"
            value={String(ready)}
            sub={`${plural(groups.inbox.length - ready, "item", "items")} still in triage or approval`}
          />
          <Tile
            term="Running"
            value={String(groups.running.length)}
            sub={`${plural(waitingForRuntime, "send", "sends")} waiting for a runtime`}
          />
          <Tile
            term="Waiting for review"
            value={String(groups.review.length - waitingForMerge)}
            sub={`${plural(waitingForMerge, "accepted item", "accepted items")} waiting for the merge`}
          />
        </dl>
        <RouteTabs
          label="Work tabs"
          panel="work-panel"
          selected={tab}
          onSelect={(name) => setTab(name as WorkTab)}
          tabs={TABS.map(({ name, label }) => ({ name, label, count: String(groups[name].length) }))}
        />
        <RouteTabPanel panel="work-panel" className={panel}>
          <WorkTable tab={tab} items={groups[tab]} />
        </RouteTabPanel>
      </div>
    </AppFrame>
  );
}
