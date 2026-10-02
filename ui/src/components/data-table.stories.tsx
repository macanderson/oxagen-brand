import type { Meta, StoryObj } from "@storybook/react-vite";
import { cell, DataTable, numericCell } from "./data-table";
import { ToneBadge, type ToneBadgeTone } from "./tone-badge";
import { TruncatedCell } from "./truncated-cell";

type Run = {
  id: string;
  agent: string;
  task: string;
  cost: string;
  tone: ToneBadgeTone;
  status: string;
};

const RUNS: Run[] = [
  {
    id: "run_0142",
    agent: "release-bot",
    task: "Cut the 3.2.0 tag once every required check on the release branch passes",
    cost: "$0.38",
    tone: "allowed",
    status: "Allowed",
  },
  {
    id: "run_0141",
    agent: "schema-migrator",
    task: "Add the invoice currency column and backfill it from the account region",
    cost: "$1.04",
    tone: "approval",
    status: "Needs approval",
  },
  {
    id: "run_0139",
    agent: "dependency-updater",
    task: "Bump the lockfile",
    cost: "$0.21",
    tone: "denied",
    status: "Denied",
  },
];

const COLUMNS = [
  { label: "Run" },
  { label: "Agent" },
  { label: "Task" },
  { label: "Cost", numeric: true },
  { label: "Status" },
] as const;

function Runs({
  runs,
  clipTask = false,
}: {
  runs: readonly Run[];
  clipTask?: boolean;
}) {
  return (
    <div className="w-[760px] max-w-full overflow-hidden rounded-xl border border-border bg-card">
      <DataTable label="Runs" columns={COLUMNS} empty="No runs yet">
        {runs.map((run) => (
          <tr key={run.id}>
            <td className={`${cell} font-mono text-xs text-muted-foreground`}>
              {run.id}
            </td>
            <td className={`${cell} font-medium text-foreground`}>
              {run.agent}
            </td>
            {clipTask ? (
              <TruncatedCell as="td" className={`${cell} [--cell-max:16rem]`}>
                {run.task}
              </TruncatedCell>
            ) : (
              <td className={cell}>{run.task}</td>
            )}
            <td className={numericCell}>{run.cost}</td>
            <td className={cell}>
              <ToneBadge tone={run.tone}>{run.status}</ToneBadge>
            </td>
          </tr>
        ))}
      </DataTable>
    </div>
  );
}

/**
 * A table drawn with the shared `cell`, `numericCell`, and `headCell` class
 * strings.
 */
const meta = {
  title: "Primitives/DataTable",
  component: Runs,
  args: { runs: RUNS },
} satisfies Meta<typeof Runs>;
export default meta;
type Story = StoryObj<typeof meta>;

export const Plain: Story = {};

export const TruncatedCells: Story = {
  args: { clipTask: true },
};

export const Empty: Story = {
  args: { runs: [] },
};
