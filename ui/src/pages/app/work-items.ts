// The work items the Work page lists. Each status, wait line, and check word
// uses the product app's English strings (apps/app/messages/work.json at
// fad620bcef). The app words a wait line from the item's record. Here each
// line is written out.

export type WorkTab = "inbox" | "running" | "review" | "done";

export type WorkStatus =
  | "triaging"
  | "triage_failed"
  | "needs_info"
  | "brief_to_approve"
  | "changed"
  | "ready"
  | "waiting_for_claim"
  | "running"
  | "stopping"
  | "in_review"
  | "accepted"
  | "done"
  | "closed";

export type ChecksWord = "passing" | "failing" | "running";

export type WorkItem = {
  number: string;
  title: string;
  tab: WorkTab;
  status: WorkStatus;
  wait: string;
  labels: readonly string[];
  priority: { label: "P0" | "P1" | "P2" | "P3" | null; reason: string; cites: readonly string[]; setBy?: string };
  send: {
    agent: string;
    runtime: string;
    sentOn: string;
    pullRequest: { number: number; head: string } | null;
    checks: ChecksWord;
  } | null;
  cost: { runs: number; knownRuns: number; total: string | null };
  finished: string | null;
};

const NO_COST = { runs: 0, knownRuns: 0, total: null } as const;
const NO_PRIORITY = { label: null, reason: "", cites: [] } as const;
const P1 = {
  label: "P1",
  reason: "A customer cannot finish a task and has no workaround.",
  cites: ["a-intel.work.priorities#2"],
} as const;
const P2 = { label: "P2", reason: "A defect with a workaround.", cites: ["a-intel.work.priorities#3"] } as const;
const P3 = { label: "P3", reason: "A change that no customer is waiting on.", cites: [] } as const;

/** Inbox in the app's order: the failed triage, then P0 to P3, then no priority, then triage. */
export const WORK_ITEMS: readonly WorkItem[] = [
  {
    number: "WI-48",
    title: "Retry webhook deliveries that time out after 30 seconds",
    tab: "inbox",
    status: "triage_failed",
    wait: "Triage failed. The model call timed out after three tries.",
    labels: ["bug", "webhooks"],
    priority: NO_PRIORITY,
    send: null,
    cost: NO_COST,
    finished: null,
  },
  {
    number: "WI-47",
    title: "Customers on annual plans see the wrong renewal date",
    tab: "inbox",
    status: "ready",
    wait: "The brief is approved. It waits to be sent to an agent.",
    labels: ["billing", "customer"],
    priority: { ...P1, setBy: "Priya Natarajan" },
    send: null,
    cost: NO_COST,
    finished: null,
  },
  {
    number: "WI-45",
    title: "Show the renewal date on the billing page",
    tab: "inbox",
    status: "brief_to_approve",
    wait: "Triage drafted a brief. It waits for a person to approve it.",
    labels: ["billing"],
    priority: P2,
    send: null,
    cost: NO_COST,
    finished: null,
  },
  {
    number: "WI-44",
    title: "Export the audit log as CSV",
    tab: "inbox",
    status: "ready",
    wait: "Returned: The export stopped at 10,000 rows. It waits to be sent again.",
    labels: ["audit"],
    priority: P2,
    send: null,
    cost: { runs: 1, knownRuns: 1, total: "$0.86" },
    finished: null,
  },
  {
    number: "WI-43",
    title: "Rename workspace to project in the CLI help",
    tab: "inbox",
    status: "needs_info",
    wait: "Triage asks: Should the --workspace flag keep working as an alias?",
    labels: ["cli"],
    priority: P3,
    send: null,
    cost: NO_COST,
    finished: null,
  },
  {
    number: "WI-42",
    title: "Billing proration test rounds the last cent",
    tab: "inbox",
    status: "changed",
    wait: "The source changed on Oct 1, 04:40 PM after brief revision 2 was approved. Approve it again to send.",
    labels: ["tests"],
    priority: P3,
    send: null,
    cost: NO_COST,
    finished: null,
  },
  {
    number: "WI-49",
    title: "Add the workspace logo to the invoice PDF",
    tab: "inbox",
    status: "triaging",
    wait: "Triage is reading it.",
    labels: [],
    priority: NO_PRIORITY,
    send: null,
    cost: NO_COST,
    finished: null,
  },
  {
    number: "WI-40",
    title: "Backfill the invoice currency column from the account region",
    tab: "running",
    status: "running",
    wait: "Running on brief revision 1.",
    labels: [],
    priority: P1,
    send: { agent: "Schema migrator", runtime: "CI runner 6", sentOn: "Oct 2, 02:02 PM", pullRequest: null, checks: "running" },
    cost: { runs: 1, knownRuns: 1, total: "$1.04" },
    finished: null,
  },
  {
    number: "WI-39",
    title: "Bump the lockfile and open one pull request for each major version",
    tab: "running",
    status: "waiting_for_claim",
    wait: "Waiting for Release host to claim it. Sent on Oct 2, 01:55 PM. Last poll on Oct 2, 01:54 PM.",
    labels: [],
    priority: P3,
    send: { agent: "Dependency updater", runtime: "Release host", sentOn: "Oct 2, 01:55 PM", pullRequest: null, checks: "running" },
    cost: NO_COST,
    finished: null,
  },
  {
    number: "WI-38",
    title: "Cut the 3.2.0 tag once every required check passes",
    tab: "running",
    status: "stopping",
    wait: "Stop requested. Waiting for CI runner 2 to confirm.",
    labels: [],
    priority: P2,
    send: { agent: "Release manager", runtime: "CI runner 2", sentOn: "Oct 2, 12:41 PM", pullRequest: null, checks: "running" },
    cost: { runs: 1, knownRuns: 1, total: "$0.37" },
    finished: null,
  },
  {
    number: "WI-36",
    title: "Write the changelog entry for the billing proration fix",
    tab: "review",
    status: "in_review",
    wait: "Ready for review on 9e41b07.",
    labels: [],
    priority: P3,
    send: {
      agent: "Docs writer",
      runtime: "CI runner 6",
      sentOn: "Oct 2, 10:12 AM",
      pullRequest: { number: 812, head: "9e41b07" },
      checks: "passing",
    },
    cost: { runs: 1, knownRuns: 1, total: "$0.58" },
    finished: null,
  },
  {
    number: "WI-35",
    title: "Label new issues and route each one to its area owner",
    tab: "review",
    status: "in_review",
    wait: "Required check unit-tests failed on 3c1d2aa.",
    labels: [],
    priority: P2,
    send: {
      agent: "Triage bot",
      runtime: "CI runner 2",
      sentOn: "Oct 2, 09:31 AM",
      pullRequest: { number: 809, head: "3c1d2aa" },
      checks: "failing",
    },
    cost: { runs: 2, knownRuns: 1, total: "$2.11" },
    finished: null,
  },
  {
    number: "WI-33",
    title: "Match last month's card charges to invoices",
    tab: "review",
    status: "accepted",
    wait: "Accepted by Priya Natarajan on 71b0e4c. Waiting for the merge.",
    labels: [],
    priority: P1,
    send: {
      agent: "Invoice reconciler",
      runtime: "CI runner 6",
      sentOn: "Oct 1, 03:20 PM",
      pullRequest: { number: 806, head: "71b0e4c" },
      checks: "passing",
    },
    cost: { runs: 1, knownRuns: 1, total: "$3.42" },
    finished: null,
  },
  {
    number: "WI-31",
    title: "Find the tests that failed and passed on the same commit this week",
    tab: "done",
    status: "done",
    wait: "Dana Whitfield accepted 5af93c0 on Oct 2, 11:05 AM. Merged on Oct 2, 11:18 AM.",
    labels: [],
    priority: P2,
    send: {
      agent: "Flaky test hunter",
      runtime: "CI runner 6",
      sentOn: "Oct 2, 08:40 AM",
      pullRequest: { number: 801, head: "5af93c0" },
      checks: "passing",
    },
    cost: { runs: 2, knownRuns: 2, total: "$1.76" },
    finished: "Oct 2, 11:18 AM",
  },
  {
    number: "WI-30",
    title: "Rebuild the docs search index after the nightly import",
    tab: "done",
    status: "done",
    wait: "Omar Haddad accepted 0d2e7f1 on Oct 1, 05:12 PM. Merged on Oct 1, 05:30 PM.",
    labels: [],
    priority: P3,
    send: {
      agent: "Night shift runner",
      runtime: "Release host",
      sentOn: "Oct 1, 02:00 AM",
      pullRequest: { number: 798, head: "0d2e7f1" },
      checks: "passing",
    },
    cost: { runs: 1, knownRuns: 1, total: "$0.21" },
    finished: "Oct 1, 05:30 PM",
  },
  {
    number: "WI-28",
    title: "Move the status page to the new domain",
    tab: "done",
    status: "closed",
    wait: "Declined by Lena Fischer on Oct 1, 10:02 AM. The status page stays on the vendor's domain.",
    labels: [],
    priority: P3,
    send: null,
    cost: NO_COST,
    finished: "Oct 1, 10:02 AM",
  },
  {
    number: "WI-27",
    title: "Cache the pricing table for the checkout page",
    tab: "done",
    status: "done",
    wait: "Priya Natarajan accepted e44a1b9 on Sep 30, 04:48 PM. Merged on Sep 30, 05:01 PM.",
    labels: [],
    priority: P2,
    send: {
      agent: "Release manager",
      runtime: "CI runner 2",
      sentOn: "Sep 30, 01:15 PM",
      pullRequest: { number: 793, head: "e44a1b9" },
      checks: "passing",
    },
    cost: { runs: 3, knownRuns: 3, total: "$4.90" },
    finished: "Sep 30, 05:01 PM",
  },
];
