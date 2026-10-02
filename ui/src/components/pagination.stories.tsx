import type { Meta, StoryObj } from "@storybook/react-vite";
import { useState } from "react";
import { RowsPager } from "./pagination";

/** A pager over `total` runs that keeps its own page and page size. */
function RunsPager({ total, start = 1 }: { total: number; start?: number }) {
  const [perPage, setPerPage] = useState(25);
  const [page, setPage] = useState(start);
  const pages = Math.max(1, Math.ceil(total / perPage));
  const current = Math.min(page, pages);
  const from = total === 0 ? 0 : (current - 1) * perPage + 1;
  const to = Math.min(total, current * perPage);
  return (
    <div className="w-[640px] max-w-full rounded-lg border border-border bg-card">
      <p className="px-3 py-6 text-center text-[13px] text-muted-foreground">
        Runs {from} to {to}
      </p>
      <RowsPager
        label="Pages"
        rowsLabel="Rows per page"
        perPage={perPage}
        sizes={[10, 25, 50, 100]}
        onPerPage={(size) => {
          // Keep the first visible run on screen.
          setPage(Math.floor((from - 1) / size) + 1);
          setPerPage(size);
        }}
        range={`${String(from)}–${String(to)} of ${String(total)}`}
        previousLabel="Previous page"
        nextLabel="Next page"
        previous={
          current <= 1
            ? null
            : () => {
                setPage(current - 1);
              }
        }
        next={
          current >= pages
            ? null
            : () => {
                setPage(current + 1);
              }
        }
      />
    </div>
  );
}

/**
 * Page controls for a table: rows per page on the left, and Previous and Next
 * on the right.
 */
const meta = {
  title: "Navigation/Pagination",
  component: RowsPager,
} satisfies Meta<typeof RowsPager>;
export default meta;
type Story = StoryObj<typeof meta>;

// Each story draws its own pager, so the args below only satisfy the type.
const args = {
  label: "Pages",
  rowsLabel: "Rows per page",
  perPage: 25,
  sizes: [10, 25, 50, 100],
  onPerPage: () => undefined,
  previousLabel: "Previous page",
  nextLabel: "Next page",
  previous: null,
  next: null,
};

export const FirstPage: Story = {
  args,
  render: () => <RunsPager total={120} />,
};

export const MiddlePage: Story = {
  args,
  render: () => <RunsPager total={120} start={3} />,
};

export const LastPage: Story = {
  args,
  render: () => <RunsPager total={120} start={5} />,
};

export const OnePageOnly: Story = {
  args,
  render: () => <RunsPager total={18} />,
};

export const PhoneWidth: Story = {
  args,
  render: () => (
    <div className="w-[360px]">
      <RunsPager total={120} start={2} />
    </div>
  ),
};
