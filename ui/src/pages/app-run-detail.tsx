import {
  ArrowsSplitIcon,
  ChatTextIcon,
  CoinsIcon,
  CpuIcon,
  FootprintsIcon,
  HandIcon,
  PauseIcon,
  TimerIcon,
  WrenchIcon,
  type Icon,
} from "@phosphor-icons/react";
import { Button } from "../components/button";
import { CommandMenu, CommandMenuTrigger } from "../components/command-menu";
import { KeyValueList } from "../components/key-value-list";
import { Panel } from "../components/panel";
import { Stat, StatGroup } from "../components/stat";
import { Tabs, TabsList, TabsTab } from "../components/tabs";
import { ToneBadge } from "../components/tone-badge";
import { cn } from "../lib/utils";
import {
  AnswerBadge,
  AppHeader,
  AppShell,
  commandGroups,
  RUN_COMMANDS,
  RunStatusBadge,
  type RequestAnswer,
} from "./page-chrome";

type RecordEvent = {
  time: string;
  kind: "Turn" | "Model call" | "Tool call" | "Request";
  text: string;
  detail?: string;
  cost?: string;
  answer?: RequestAnswer;
  decidedBy?: string;
};

const KIND_ICON: Record<RecordEvent["kind"], Icon> = {
  Turn: ChatTextIcon,
  "Model call": CpuIcon,
  "Tool call": WrenchIcon,
  Request: HandIcon,
};

/**
 * The run's record in order: one turn, seven steps (a step is one model call
 * or one tool call), and three requests, one of which waits on a person.
 * The costs add up to the run's $1.04.
 */
const EVENTS: readonly RecordEvent[] = [
  {
    time: "14:02:08",
    kind: "Turn",
    text: "Turn 1 started by Dana",
    detail:
      "Add the invoice currency column and backfill it from the account region",
  },
  {
    time: "14:02:11",
    kind: "Model call",
    text: "Plan the migration",
    detail: "1,840 tokens in, 312 out",
    cost: "$0.38",
  },
  {
    time: "14:02:19",
    kind: "Tool call",
    text: "Read db/schema/invoices.sql",
    cost: "$0.00",
  },
  {
    time: "14:02:40",
    kind: "Tool call",
    text: "Write migrations/0147_invoice_currency.sql",
    cost: "$0.00",
  },
  {
    time: "14:03:05",
    kind: "Request",
    text: "Run the migration on staging",
    answer: "allowed",
    decidedBy: "Rule staging-migrate",
  },
  {
    time: "14:03:06",
    kind: "Tool call",
    text: "Run the migration on staging",
    detail: "412,908 rows backfilled",
    cost: "$0.00",
  },
  {
    time: "14:05:12",
    kind: "Model call",
    text: "Check the backfill",
    detail: "3,906 tokens in, 240 out",
    cost: "$0.41",
  },
  {
    time: "14:05:30",
    kind: "Request",
    text: "Push to main",
    answer: "denied",
    decidedBy: "Rule no-push-main",
  },
  {
    time: "14:06:02",
    kind: "Model call",
    text: "Open a branch for the release",
    detail: "2,214 tokens in, 188 out",
    cost: "$0.25",
  },
  {
    time: "14:06:09",
    kind: "Tool call",
    text: "Create branch release/2026.10",
    cost: "$0.00",
  },
  {
    time: "14:08:14",
    kind: "Request",
    text: "Push to release/2026.10",
    answer: "routed",
    decidedBy: "Waiting on Priya, rule release-branch",
  },
];

/** The record as a timeline: time, kind, what happened, and its cost or answer. */
function Timeline() {
  return (
    <ol className="divide-y divide-border">
      {EVENTS.map((event) => {
        const KindIcon = KIND_ICON[event.kind];
        return (
          <li
            key={`${event.time}-${event.text}`}
            className="grid grid-cols-[4.5rem_1.5rem_minmax(0,1fr)_auto] items-start gap-x-3 px-[18px] py-3"
          >
            <span className="pt-0.5 font-mono text-xs text-muted-foreground tabular-nums">
              {event.time}
            </span>
            <span
              aria-hidden
              className="flex size-6 items-center justify-center rounded-md border border-border bg-hl text-muted-foreground [&_svg]:size-3.5"
            >
              <KindIcon />
            </span>
            <div className="min-w-0">
              <p className="text-[13px] text-foreground">
                <span className="text-muted-foreground">{event.kind}</span>{" "}
                <span
                  className={cn(
                    "font-medium",
                    event.kind === "Tool call" && "font-mono text-xs",
                  )}
                >
                  {event.text}
                </span>
              </p>
              {event.detail ? (
                <p className="mt-0.5 truncate text-xs text-muted-foreground">
                  {event.detail}
                </p>
              ) : null}
              {event.decidedBy ? (
                <p className="mt-0.5 text-xs text-muted-foreground">
                  {event.decidedBy}
                </p>
              ) : null}
            </div>
            <span className="pt-0.5 text-right">
              {event.answer ? (
                <AnswerBadge answer={event.answer} />
              ) : event.cost ? (
                <span className="font-mono text-xs tabular-nums text-foreground">
                  {event.cost}
                </span>
              ) : null}
            </span>
          </li>
        );
      })}
    </ol>
  );
}

const mono = "font-mono text-[13px]";

/**
 * The app's Run detail page, for the run the Runs page lists second. The
 * header is the sticky glass bar with the run's id as its h1, its route tabs,
 * and its status. The command menu opens over the page on the translucent
 * floating surface, with the run's own commands first.
 */
export function RunDetailPage({
  commandMenuOpen,
}: {
  commandMenuOpen: boolean;
}) {
  return (
    <AppShell current="runs">
      <AppHeader
        eyebrow="Run"
        title="run_0147"
        mono
        actions={
          <>
            <CommandMenu
              groups={commandGroups([RUN_COMMANDS])}
              defaultOpen={commandMenuOpen}
            >
              <CommandMenuTrigger />
            </CommandMenu>
            <Button variant="outline" startIcon={<PauseIcon aria-hidden />}>
              Pause run
            </Button>
            <Button variant="primary">Review request</Button>
          </>
        }
      >
        <Tabs defaultValue="overview">
          <TabsList aria-label="Run views">
            <TabsTab value="overview">Overview</TabsTab>
            <TabsTab value="steps" count={7}>
              Steps
            </TabsTab>
            <TabsTab value="requests" count={3}>
              Requests
            </TabsTab>
            <TabsTab value="spend">Spend</TabsTab>
          </TabsList>
        </Tabs>
        <div className="flex flex-wrap items-center gap-2">
          <RunStatusBadge status="waiting" />
          <ToneBadge tone="quiet" dot={false} mono>
            claude-code
          </ToneBadge>
        </div>
      </AppHeader>

      <main className="grid gap-6 px-6 py-6">
        <StatGroup role="group" aria-label="Run summary">
          <Stat
            label="Cost"
            value="$1.04"
            icon={<CoinsIcon />}
            hint="Recorded on 7 steps"
          />
          <Stat
            label="Steps"
            value="7"
            icon={<FootprintsIcon />}
            hint="In 1 turn"
          />
          <Stat
            label="Requests"
            value="3"
            icon={<ArrowsSplitIcon />}
            hint="1 waiting on Priya"
          />
          <Stat
            label="Duration"
            value="6m 06s"
            icon={<TimerIcon />}
            hint="Waiting since 14:08"
          />
        </StatGroup>

        <div className="grid items-start gap-6 lg:grid-cols-[minmax(0,2fr)_minmax(0,1fr)]">
          <Panel title="Record" inset>
            <Timeline />
          </Panel>

          <div className="grid gap-6">
            <Panel title="Details">
              <KeyValueList
                items={[
                  { label: "Agent", value: "schema-migrator" },
                  { label: "Operator", value: "Dana" },
                  { label: "Workspace", value: "platform" },
                  {
                    label: "Mandate",
                    value: <span className={mono}>schema-migrator v7</span>,
                  },
                  { label: "Wrapper", value: "Claude Code" },
                  { label: "Mode", value: "Enforced" },
                  {
                    label: "Started",
                    value: <span className={mono}>2026-10-01 14:02 UTC</span>,
                  },
                ]}
              />
            </Panel>
            <Panel title="Budget">
              <KeyValueList
                items={[
                  { label: "Spent", value: <span className={mono}>$1.04</span> },
                  {
                    label: "Run budget",
                    value: <span className={mono}>$5.00</span>,
                  },
                  {
                    label: "Rule",
                    value: <span className={mono}>spend-cap</span>,
                  },
                ]}
              />
              <div
                role="meter"
                aria-label="Run budget spent"
                aria-valuemin={0}
                aria-valuemax={5}
                aria-valuenow={1.04}
                aria-valuetext="$1.04 of $5.00"
                className="mt-4 h-1.5 overflow-hidden rounded-full bg-hl"
              >
                <div className="h-full w-[21%] rounded-full bg-foreground/60" />
              </div>
            </Panel>
          </div>
        </div>
      </main>
    </AppShell>
  );
}
