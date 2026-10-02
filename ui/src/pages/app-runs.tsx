import * as React from "react";
import {
  ArrowSquareOutIcon,
  CopyIcon,
  DotsThreeIcon,
  ExportIcon,
  PauseIcon,
  PlayIcon,
  PlusIcon,
  StopIcon,
} from "@phosphor-icons/react";
import { Button } from "../components/button";
import { CommandMenu, CommandMenuTrigger } from "../components/command-menu";
import { panel } from "../components/control-styles";
import { cell, DataTable, numericCell } from "../components/data-table";
import {
  Menu,
  MenuItem,
  MenuPopup,
  MenuSeparator,
  MenuTrigger,
} from "../components/menu";
import { Tabs, TabsList, TabsTab } from "../components/tabs";
import type { ToastAddOptions } from "../components/toast";
import { ToggleGroup, ToggleGroupItem } from "../components/toggle-group";
import { TruncatedCell } from "../components/truncated-cell";
import { cn } from "../lib/utils";
import {
  AppHeader,
  AppShell,
  commandGroups,
  RunStatusBadge,
  WithToasts,
  type RunStatus,
} from "./page-chrome";

export type Run = {
  id: string;
  agent: string;
  operator: string;
  task: string;
  steps: number;
  cost: string;
  status: RunStatus;
  started: string;
};

const AGENTS = [
  {
    agent: "release-bot",
    task: "Cut the 3.2.0 tag once every required check on the release branch passes",
  },
  {
    agent: "schema-migrator",
    task: "Add the invoice currency column and backfill it from the account region",
  },
  {
    agent: "dependency-updater",
    task: "Bump the lockfile and open one pull request for each major version",
  },
  {
    agent: "docs-writer",
    task: "Write the changelog entry for the billing proration fix",
  },
  {
    agent: "triage-bot",
    task: "Label new issues in product and route each one to its area owner",
  },
  {
    agent: "invoice-reconciler",
    task: "Match last month's card charges to invoices and flag the ones that differ",
  },
  {
    agent: "flaky-test-hunter",
    task: "Find the tests that failed and passed on the same commit this week",
  },
  {
    agent: "night-shift-runner",
    task: "Rebuild the docs search index after the nightly import",
  },
] as const;

const OPERATORS = ["Dana", "Priya", "Omar", "Lena"] as const;

const STATUSES: readonly RunStatus[] = [
  "running",
  "waiting",
  "ended",
  "ended",
  "failed",
  "running",
  "ended",
  "stopped",
  "ended",
  "ended",
];

/** HH:MM, counting back from 14:20 in 11-minute steps. */
function startedAt(index: number): string {
  const minutes = 14 * 60 + 20 - index * 11;
  const hh = String(Math.floor(minutes / 60)).padStart(2, "0");
  const mm = String(minutes % 60).padStart(2, "0");
  return `${hh}:${mm}`;
}

/**
 * 28 sample runs, enough to scroll under the header. Row 2 is the run the
 * Run detail page shows, so its figures match that page.
 */
export const RUNS: readonly Run[] = Array.from({ length: 28 }, (_, index) => {
  const { agent, task } = AGENTS[index % AGENTS.length] ?? AGENTS[0];
  const run: Run = {
    id: `run_${String(148 - index).padStart(4, "0")}`,
    agent,
    operator: OPERATORS[index % OPERATORS.length] ?? "Dana",
    task,
    steps: ((index * 7) % 40) + 3,
    cost: `$${(((index * 37) % 190) / 100 + 0.08).toFixed(2)}`,
    status: STATUSES[index % STATUSES.length] ?? "ended",
    started: startedAt(index),
  };
  return index === 1
    ? { ...run, operator: "Dana", steps: 7, cost: "$1.04", started: "14:02" }
    : run;
});

const COLUMNS = [
  { label: "Run" },
  { label: "Agent" },
  { label: "Operator" },
  { label: "Task" },
  { label: "Steps", numeric: true },
  { label: "Cost", numeric: true },
  { label: "Status" },
  { label: "Started", numeric: true },
  { label: "Actions", hidden: true },
] as const;

const FILTERS: readonly { value: RunStatus; label: string }[] = [
  { value: "running", label: "Running" },
  { value: "waiting", label: "Waiting" },
  { value: "failed", label: "Failed" },
  { value: "ended", label: "Ended" },
];

/** A row's actions. Oxagen does not run agents, so it offers no Run. */
function RowActions({ run, open }: { run: Run; open: boolean }) {
  return (
    <Menu defaultOpen={open} modal={false}>
      <MenuTrigger
        render={
          <Button
            variant="ghost"
            size="icon-sm"
            aria-label={`Actions for ${run.id}`}
          />
        }
      >
        <DotsThreeIcon aria-hidden />
      </MenuTrigger>
      <MenuPopup align="end" className="w-56">
        <MenuItem onClick={() => {}}>
          <ArrowSquareOutIcon aria-hidden />
          Open run
        </MenuItem>
        <MenuItem onClick={() => {}}>
          <PlayIcon aria-hidden />
          Play back run
        </MenuItem>
        <MenuItem onClick={() => {}}>
          <CopyIcon aria-hidden />
          Copy run link
        </MenuItem>
        <MenuItem onClick={() => {}}>
          <ExportIcon aria-hidden />
          Export record
        </MenuItem>
        <MenuSeparator />
        <MenuItem onClick={() => {}}>
          <PauseIcon aria-hidden />
          Pause run
        </MenuItem>
        <MenuItem variant="destructive" onClick={() => {}}>
          <StopIcon aria-hidden />
          Stop run
        </MenuItem>
      </MenuPopup>
    </Menu>
  );
}

/** The toast the page shows when a request routes to a person. */
export const ROUTED_TOAST: ToastAddOptions = {
  title: "Waiting on Priya",
  description:
    "schema-migrator requested a push to release/2026.10. Rule release-branch routes it to a person.",
  tone: "info",
};

/** The row whose action menu the open story shows. */
const MENU_ROW = 3;

/**
 * The app's Runs page. The header is the sticky glass bar with the page's
 * title, its route tabs and their counts, and the status filters. The table
 * scrolls under it. One row's action menu opens over the table, and a toast
 * sits in the corner, both on the translucent floating surface.
 */
export function RunsPage({
  rowMenuOpen,
  toast,
}: {
  rowMenuOpen: boolean;
  toast: boolean;
}) {
  const [shown, setShown] = React.useState<string[]>([]);
  const rows =
    shown.length === 0 ? RUNS : RUNS.filter((run) => shown.includes(run.status));
  const count = (status: RunStatus) =>
    RUNS.filter((run) => run.status === status).length;
  const mine = RUNS.filter((run) => run.operator === "Dana").length;

  return (
    <WithToasts toasts={toast ? [ROUTED_TOAST] : []}>
      <AppShell current="runs">
        <AppHeader
          title="Runs"
          actions={
            <>
              <CommandMenu groups={commandGroups()}>
                <CommandMenuTrigger />
              </CommandMenu>
              <Button variant="primary" startIcon={<PlusIcon aria-hidden />}>
                New work item
              </Button>
            </>
          }
        >
          <Tabs defaultValue="all">
            <TabsList aria-label="Run views">
              <TabsTab value="all" count={RUNS.length}>
                All runs
              </TabsTab>
              <TabsTab value="mine" count={mine}>
                Mine
              </TabsTab>
              <TabsTab value="archived" count={216}>
                Archived
              </TabsTab>
            </TabsList>
          </Tabs>
          <ToggleGroup
            aria-label="Run status"
            multiple
            value={shown}
            onValueChange={setShown}
          >
            {FILTERS.map((filter) => (
              <ToggleGroupItem
                key={filter.value}
                value={filter.value}
                count={count(filter.value)}
              >
                {filter.label}
              </ToggleGroupItem>
            ))}
          </ToggleGroup>
        </AppHeader>

        <main className="px-6 py-6">
          <div className={panel}>
            <DataTable
              label="Runs"
              columns={COLUMNS}
              empty="No runs match these filters."
            >
              {rows.map((run, index) => (
                <tr key={run.id}>
                  <td
                    className={cn(cell, "font-mono text-xs text-muted-foreground")}
                  >
                    {run.id}
                  </td>
                  <td className={cn(cell, "font-medium text-foreground")}>
                    {run.agent}
                  </td>
                  <td className={cell}>{run.operator}</td>
                  <TruncatedCell as="td" className={cn(cell, "[--cell-max:18rem]")}>
                    {run.task}
                  </TruncatedCell>
                  <td className={numericCell}>{run.steps}</td>
                  <td className={numericCell}>{run.cost}</td>
                  <td className={cell}>
                    <RunStatusBadge status={run.status} />
                  </td>
                  <td className={cn(numericCell, "text-muted-foreground")}>
                    {run.started}
                  </td>
                  <td className={cn(cell, "w-12 py-1 text-right")}>
                    <RowActions
                      run={run}
                      open={rowMenuOpen && index === MENU_ROW}
                    />
                  </td>
                </tr>
              ))}
            </DataTable>
          </div>
          <p className="mt-3 text-xs text-muted-foreground">
            Showing {rows.length} of {RUNS.length} runs from today.
          </p>
        </main>
      </AppShell>
    </WithToasts>
  );
}
