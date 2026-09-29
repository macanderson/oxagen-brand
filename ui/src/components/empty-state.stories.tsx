import type { Meta, StoryObj } from "@storybook/react-vite";
import { DatabaseIcon, SparkleIcon } from "@phosphor-icons/react";
import { Button } from "./button";
import { EmptyState } from "./empty-state";

const meta = {
  title: "Primitives/EmptyState",
  component: EmptyState,
} satisfies Meta<typeof EmptyState>;
export default meta;
type Story = StoryObj<typeof meta>;

export const Default: Story = {
  args: {
    icon: <DatabaseIcon aria-hidden="true" />,
    title: "No connections yet",
    description:
      "Connect a data source to start grounding agent answers in your knowledge graph.",
    action: <Button size="sm">Add connection</Button>,
    variant: "dashed",
  },
};

export const SmallMuted: Story = {
  args: {
    icon: <SparkleIcon aria-hidden="true" />,
    title: "No suggestions",
    description: "Inferred edges will appear here.",
    size: "sm",
    variant: "muted",
  },
};
