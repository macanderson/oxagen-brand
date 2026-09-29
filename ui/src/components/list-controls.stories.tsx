import type { Meta, StoryObj } from "@storybook/react-vite";
import {
  ListBar,
  type ListFilter,
  ListPager,
  type ListSort,
  useList,
} from "./list-controls";

type Repository = { name: string; role: "main" | "linked"; runs: number };

const REPOSITORIES: Repository[] = Array.from({ length: 42 }, (_, i) => ({
  name: `oxagen/service-${String(i + 1).padStart(2, "0")}`,
  role: i % 7 === 0 ? "main" : "linked",
  runs: (i * 37) % 120,
}));

const SORTS: ListSort<Repository>[] = [
  { value: "shown", label: "Shown order", compare: null },
  {
    value: "runs",
    label: "Most runs",
    compare: (a, b) => b.runs - a.runs,
  },
];

const FILTERS: ListFilter<Repository>[] = [
  {
    key: "role",
    label: "Role",
    options: [
      { value: "main", label: "Main" },
      { value: "linked", label: "Linked" },
    ],
    get: (repository) => repository.role,
  },
];

function Repositories({ items }: { items: readonly Repository[] }) {
  const list = useList(items, {
    text: (repository) => repository.name,
    sorts: SORTS,
    filters: FILTERS,
  });
  return (
    <div className="w-[640px] max-w-full overflow-hidden rounded-lg border border-border bg-card">
      <ListBar
        list={list}
        searchLabel="Search repositories"
        sortLabel="Sort"
        sorts={SORTS}
        filters={FILTERS}
        allLabel={(column) => `All ${column.toLowerCase()}s`}
      />
      <ul className="divide-y divide-border text-[13px]">
        {list.shown.map((repository) => (
          <li
            key={repository.name}
            className="flex items-center justify-between px-3 py-2"
          >
            <span className="font-mono text-xs text-foreground">
              {repository.name}
            </span>
            <span className="text-xs text-muted-foreground tabular-nums">
              {repository.runs} runs
            </span>
          </li>
        ))}
        {list.total === 0 ? (
          <li className="px-3 py-6 text-center text-muted-foreground">
            No repositories match.
          </li>
        ) : null}
      </ul>
      <ListPager
        list={list}
        label="Pages"
        rowsLabel="Rows per page"
        range={(from, to, total) =>
          `${String(from)}–${String(to)} of ${String(total)}`
        }
        previousLabel="Previous page"
        nextLabel="Next page"
      />
    </div>
  );
}

const meta = {
  title: "Navigation/ListControls",
  component: Repositories,
} satisfies Meta<typeof Repositories>;
export default meta;
type Story = StoryObj<typeof meta>;

export const Default: Story = {
  args: { items: REPOSITORIES },
};

export const OnePage: Story = {
  args: { items: REPOSITORIES.slice(0, 8) },
};

export const Empty: Story = {
  args: { items: [] },
};

export const PhoneWidth: Story = {
  args: { items: REPOSITORIES },
  render: (props) => (
    <div className="w-[360px]">
      <Repositories {...props} />
    </div>
  ),
};
