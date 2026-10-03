import type { Meta, StoryObj } from "@storybook/react-vite";
import {
  Table,
  TableBody,
  TableCell,
  TableEmpty,
  TableFooter,
  TableGroupRow,
  TableHead,
  TableHeader,
  TableRow,
} from "./table";
import { ToneBadge, type ToneBadgeTone } from "./tone-badge";
import { TruncatedCell } from "./truncated-cell";

const meta = {
  title: "Primitives/Table",
  component: Table,
} satisfies Meta<typeof Table>;
export default meta;
type Story = StoryObj<typeof meta>;

type Run = {
  id: string;
  agent: string;
  repository: string;
  task: string;
  day: string;
  minutes: string;
  cost: string;
  tone: ToneBadgeTone;
  status: string;
};

const RUNS: Run[] = [
  {
    id: "run_0142",
    agent: "release-bot",
    repository: "oxagen/runtime",
    task: "Cut the 3.2.0 tag once every required check on the release branch passes",
    day: "Today",
    minutes: "4.2",
    cost: "$0.38",
    tone: "allowed",
    status: "Allowed",
  },
  {
    id: "run_0141",
    agent: "schema-migrator",
    repository: "oxagen/billing",
    task: "Add the invoice currency column and backfill it from the account region",
    day: "Today",
    minutes: "11.7",
    cost: "$1.04",
    tone: "approval",
    status: "Needs approval",
  },
  {
    id: "run_0139",
    agent: "dependency-updater",
    repository: "oxagen/web",
    task: "Bump the lockfile",
    day: "Yesterday",
    minutes: "2.9",
    cost: "$0.21",
    tone: "denied",
    status: "Denied",
  },
  {
    id: "run_0137",
    agent: "audit-writer",
    repository: "oxagen/mandates",
    task: "Write the weekly mandate audit and attach the signed digest",
    day: "Yesterday",
    minutes: "6.5",
    cost: "$0.57",
    tone: "proven",
    status: "Proven",
  },
];

const frame = "rounded-xl border border-border bg-card";

export const Plain: Story = {
  render: () => (
    <Table containerClassName={frame}>
      <TableHeader>
        <TableRow>
          <TableHead>Run</TableHead>
          <TableHead>Agent</TableHead>
          <TableHead>Repository</TableHead>
          <TableHead numeric>Minutes</TableHead>
          <TableHead>Status</TableHead>
        </TableRow>
      </TableHeader>
      <TableBody>
        {RUNS.map((run) => (
          <TableRow key={run.id} interactive>
            <TableCell className="font-mono text-sm text-muted-foreground">
              {run.id}
            </TableCell>
            <TableCell className="font-medium text-foreground">
              {run.agent}
            </TableCell>
            <TableCell>{run.repository}</TableCell>
            <TableCell numeric>{run.minutes}</TableCell>
            <TableCell>
              <ToneBadge tone={run.tone}>{run.status}</ToneBadge>
            </TableCell>
          </TableRow>
        ))}
      </TableBody>
    </Table>
  ),
};

export const GroupedByDay: Story = {
  render: () => (
    <Table containerClassName={frame}>
      <TableHeader>
        <TableRow>
          <TableHead>Run</TableHead>
          <TableHead>Agent</TableHead>
          <TableHead numeric>Cost</TableHead>
        </TableRow>
      </TableHeader>
      <TableBody>
        {RUNS.map((run, index) => (
          <RunWithDay
            key={run.id}
            run={run}
            opensDay={RUNS[index - 1]?.day !== run.day}
          />
        ))}
      </TableBody>
      <TableFooter>
        <TableRow>
          <TableCell colSpan={2}>Total</TableCell>
          <TableCell numeric>$2.20</TableCell>
        </TableRow>
      </TableFooter>
    </Table>
  ),
};

function RunWithDay({ run, opensDay }: { run: Run; opensDay: boolean }) {
  return (
    <>
      {opensDay ? <TableGroupRow colSpan={3}>{run.day}</TableGroupRow> : null}
      <TableRow interactive>
        <TableCell className="font-mono text-sm text-muted-foreground">
          {run.id}
        </TableCell>
        <TableCell>{run.agent}</TableCell>
        <TableCell numeric>{run.cost}</TableCell>
      </TableRow>
    </>
  );
}

export const TruncatedCells: Story = {
  render: () => (
    <div className="w-[720px] max-w-full">
      <Table containerClassName={frame}>
        <TableHeader>
          <TableRow>
            <TableHead>Agent</TableHead>
            <TableHead>Task</TableHead>
            <TableHead numeric>Cost</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {RUNS.map((run) => (
            <TableRow key={run.id}>
              <TableCell className="font-medium text-foreground">
                {run.agent}
              </TableCell>
              <TruncatedCell
                as="td"
                className="px-[var(--table-pad-x)] py-[var(--table-pad-y)] align-middle [--cell-max:18rem]"
              >
                {run.task}
              </TruncatedCell>
              <TableCell numeric>{run.cost}</TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </div>
  ),
};

export const Compact: Story = {
  render: () => (
    <Table density="compact" containerClassName={frame}>
      <TableHeader>
        <TableRow>
          <TableHead>Agent</TableHead>
          <TableHead numeric>Minutes</TableHead>
        </TableRow>
      </TableHeader>
      <TableBody>
        {RUNS.map((run) => (
          <TableRow key={run.id}>
            <TableCell>{run.agent}</TableCell>
            <TableCell numeric>{run.minutes}</TableCell>
          </TableRow>
        ))}
      </TableBody>
    </Table>
  ),
};

export const Narrow: Story = {
  render: () => (
    <div className="w-[320px]">
      <Table narrow containerClassName={frame}>
        <TableBody>
          <TableRow>
            <TableCell className="text-muted-foreground">Agent</TableCell>
            <TableCell>release-bot</TableCell>
          </TableRow>
          <TableRow>
            <TableCell className="text-muted-foreground">Repository</TableCell>
            <TableCell>oxagen/runtime</TableCell>
          </TableRow>
          <TableRow>
            <TableCell className="text-muted-foreground">Mandate</TableCell>
            <TableCell>Release on green</TableCell>
          </TableRow>
        </TableBody>
      </Table>
    </div>
  ),
};

export const Empty: Story = {
  render: () => (
    <Table containerClassName={frame}>
      <TableHeader>
        <TableRow>
          <TableHead>Run</TableHead>
          <TableHead>Agent</TableHead>
          <TableHead numeric>Cost</TableHead>
        </TableRow>
      </TableHeader>
      <TableBody>
        <TableEmpty colSpan={3}>No runs yet</TableEmpty>
      </TableBody>
    </Table>
  ),
};

export const PhoneWidth: Story = {
  render: () => (
    <div className="w-[360px]">
      <Table containerClassName={frame}>
        <TableHeader>
          <TableRow>
            <TableHead>Run</TableHead>
            <TableHead>Agent</TableHead>
            <TableHead>Status</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {RUNS.map((run) => (
            <TableRow key={run.id} interactive>
              <TableCell className="font-mono text-sm text-muted-foreground">
                {run.id}
              </TableCell>
              <TableCell>{run.agent}</TableCell>
              <TableCell>
                <ToneBadge tone={run.tone}>{run.status}</ToneBadge>
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </div>
  ),
};
