import type { Meta, StoryObj } from "@storybook/react-vite";
import { TruncatedCell } from "./truncated-cell";

const meta = {
  title: "Primitives/TruncatedCell",
  component: TruncatedCell,
} satisfies Meta<typeof TruncatedCell>;
export default meta;
type Story = StoryObj<typeof meta>;

export const Clipped: Story = {
  render: () => (
    <div className="w-60 rounded-lg border border-border bg-card p-3 text-base text-foreground">
      <TruncatedCell>
        Watches the release branch and cuts a tag when every required check
        passes
      </TruncatedCell>
      <p className="mt-2 text-sm text-muted-foreground">
        Rest the pointer on the text, or press Tab to focus it.
      </p>
    </div>
  ),
};

export const ClippedWithValue: Story = {
  render: () => (
    <div className="w-60 rounded-lg border border-border bg-card p-3 font-mono text-sm text-foreground">
      <TruncatedCell value="run_01J9Z3K4Q2W8XYV5T6R7S8P9M0">
        run_01J9Z3K4Q2W8XYV5T6R7S8P9M0 in oxagen/runtime
      </TruncatedCell>
    </div>
  ),
};

export const NotClipped: Story = {
  render: () => (
    <div className="w-60 rounded-lg border border-border bg-card p-3 text-base text-foreground">
      <TruncatedCell>release-bot</TruncatedCell>
      <p className="mt-2 text-sm text-muted-foreground">
        The text fits, so no card opens.
      </p>
    </div>
  ),
};
