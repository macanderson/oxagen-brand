// The run the Run page draws: a live Claude Code run of the schema migrator
// whose push to the release branch is parked for a person. The words on each
// row follow the product app's English strings (apps/app/messages/run.json
// at fad620bcef). The app derives them from the run's frames. Here each one
// is written out.

export const RUN = {
  id: "arun_01JB7Q3K9M2XW4",
  name: "Backfill the invoice currency column from the account region",
  task: "WI-40",
  agentKey: "a-intel.platform.schema-migrator",
  agentName: "Schema migrator",
  harness: "Claude Code",
  harnessVersion: "2.1.4",
  model: "claude-opus-5-5",
  operator: "Dana Whitfield",
  operatorInitials: "DW",
  started: "Oct 2, 2026, 2:02:08 PM",
  repository: "a-intel/platform",
  branch: "wi-40-invoice-currency",
  path: "ci-runner-6:/srv/work/platform",
  summary:
    "Added a currency column to invoices and backfilled 412,908 rows on staging from each account's region. A push to main was denied by rule no-push-main, so the agent cut release/2026.10 and asked to push there. The push waits for a person under rule release-branch.",
  summaryModel: "claude-haiku-4-5",
  summaryAt: "Oct 2, 2026, 2:09 PM",
} as const;

export type Frame = { type: string; seq: number };

export type FeedRow =
  | { kind: "prompt"; at: string; text: string }
  | { kind: "thinking"; at: string; text: string }
  | { kind: "text"; at: string; text: string }
  | {
      kind: "tool";
      at: string;
      name: string;
      arg: string;
      state: "ok" | "err" | "ask";
      duration: string | null;
      output: string | null;
      diff: { added: number; removed: number } | null;
      gate: { decision: string; seq: number } | null;
      parked: number | null;
      frame: Frame;
    }
  | { kind: "usage"; at: string; line: string; effort: string; cost: string; spent: string; frame: Frame };

export const FEED: readonly FeedRow[] = [
  {
    kind: "prompt",
    at: "14:02:08.1",
    text: "Add the invoice currency column and backfill it from the account region. Follow the migration rules in db/README.md, run it on staging first, and push the change for review.",
  },
  {
    kind: "thinking",
    at: "14:02:10.4",
    text: "The invoices table has no currency today, so amounts are read as USD.\nThe account table already holds a region, and the region maps to a currency.\nA nullable column first, then a backfill in batches, then NOT NULL.\nThe README asks for a reversible migration and a staging run before any push.\nI should read the schema and the README before I write anything.\nThe backfill touches about 400,000 rows, so batches of 10,000.",
  },
  {
    kind: "text",
    at: "14:02:11.9",
    text: "I'll read the invoices schema and the migration rules first, then write the migration.",
  },
  {
    kind: "tool",
    at: "14:02:19.0",
    name: "Read",
    arg: "db/schema/invoices.sql",
    state: "ok",
    duration: "0.1s",
    output: "create table invoices (\n  id uuid primary key,\n  account_id uuid not null references accounts(id),\n  amount_cents bigint not null,\n  issued_at timestamptz not null\n);",
    diff: null,
    gate: null,
    parked: null,
    frame: { type: "tool_call", seq: 5 },
  },
  {
    kind: "tool",
    at: "14:02:21.6",
    name: "Read",
    arg: "db/README.md",
    state: "ok",
    duration: "0.1s",
    output: "Every migration is reversible.\nRun it on staging before you push.\nBackfill in batches of 10,000 rows or fewer.",
    diff: null,
    gate: null,
    parked: null,
    frame: { type: "tool_call", seq: 6 },
  },
  {
    kind: "usage",
    at: "14:02:24.3",
    line: "usage · claude-opus-5-5 · in 1,840 · cache 12,288 · out 312",
    effort: "effort high",
    cost: "$0.38",
    spent: "$0.38",
    frame: { type: "model_call", seq: 7 },
  },
  {
    kind: "tool",
    at: "14:02:40.2",
    name: "Write",
    arg: "migrations/0147_invoice_currency.sql",
    state: "ok",
    duration: "0.2s",
    output: null,
    diff: { added: 38, removed: 0 },
    gate: { decision: "allowed", seq: 11 },
    parked: null,
    frame: { type: "tool_call", seq: 11 },
  },
  {
    kind: "tool",
    at: "14:03:06.5",
    name: "Bash",
    arg: "pnpm db:migrate --env staging",
    state: "ok",
    duration: "2m 04s",
    output: "Applying 0147_invoice_currency\nAdded column invoices.currency\nBackfilled 412,908 rows in 42 batches\nSet invoices.currency NOT NULL\nDone in 124.2s",
    diff: null,
    gate: { decision: "allowed", seq: 14 },
    parked: null,
    frame: { type: "tool_call", seq: 14 },
  },
  {
    kind: "text",
    at: "14:05:12.8",
    text: "The backfill wrote 412,908 rows. I'll check a sample against the account regions before I push.",
  },
  {
    kind: "tool",
    at: "14:05:14.0",
    name: "Bash",
    arg: "psql staging -c \"select currency, count(*) from invoices group by 1\"",
    state: "ok",
    duration: "0.8s",
    output: " currency |  count\n----------+--------\n USD      | 301,442\n EUR      |  88,105\n GBP      |  23,361\n(3 rows)",
    diff: null,
    gate: null,
    parked: null,
    frame: { type: "tool_call", seq: 16 },
  },
  {
    kind: "usage",
    at: "14:05:22.7",
    line: "usage · claude-opus-5-5 · in 3,906 · cache 14,102 · out 240",
    effort: "effort high",
    cost: "$0.41",
    spent: "$0.79",
    frame: { type: "model_call", seq: 17 },
  },
  {
    kind: "tool",
    at: "14:05:30.1",
    name: "Bash",
    arg: "git push origin main",
    state: "err",
    duration: "0.0s",
    output: "Denied by rule no-push-main: an agent never pushes to main.",
    diff: null,
    gate: { decision: "denied", seq: 19 },
    parked: null,
    frame: { type: "tool_call", seq: 19 },
  },
  {
    kind: "text",
    at: "14:06:02.4",
    text: "Pushing to main is not allowed here. I'll cut a release branch and push there instead.",
  },
  {
    kind: "tool",
    at: "14:06:09.3",
    name: "Bash",
    arg: "git checkout -b release/2026.10",
    state: "ok",
    duration: "0.1s",
    output: "Switched to a new branch 'release/2026.10'",
    diff: null,
    gate: null,
    parked: null,
    frame: { type: "tool_call", seq: 22 },
  },
  {
    kind: "usage",
    at: "14:06:11.0",
    line: "usage · claude-opus-5-5 · in 2,214 · cache 15,330 · out 188",
    effort: "effort high",
    cost: "$0.25",
    spent: "$1.04",
    frame: { type: "model_call", seq: 23 },
  },
  {
    kind: "tool",
    at: "14:08:14.6",
    name: "Bash",
    arg: "git push origin release/2026.10",
    state: "ask",
    duration: null,
    output: null,
    diff: null,
    gate: null,
    parked: 26,
    frame: { type: "tool_call", seq: 26 },
  },
];

/** The kind chips over the feed, with the server's count of each over the whole run. */
export const KINDS: readonly { group: string; label: string; count: number }[] = [
  { group: "prompt", label: "prompt", count: 1 },
  { group: "responses", label: "responses", count: 3 },
  { group: "thinking", label: "thinking", count: 1 },
  { group: "tools", label: "tools", count: 8 },
  { group: "usage", label: "usage", count: 3 },
  { group: "recall", label: "recall", count: 0 },
  { group: "seal", label: "seal", count: 0 },
];
