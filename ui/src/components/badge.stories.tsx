import type { Meta, StoryObj } from "@storybook/react-vite";
import { GitBranchIcon } from "@phosphor-icons/react";
import { Badge } from "./badge";

/**
 * A small label for a count, a filter, a field name, or a state. Use
 * `ToneBadge` for a record's state.
 */
const meta = {
  title: "Primitives/Badge",
  component: Badge,
  argTypes: {
    variant: {
      control: "select",
      options: [
        "default",
        "secondary",
        "destructive",
        "outline",
        "muted",
        "brand",
        "cyan",
        "info",
        "success",
        "warning",
        "error",
        "info-soft",
        "success-soft",
        "warning-soft",
        "error-soft",
        "proven-soft",
        "critical-soft",
        "quiet",
        "chip",
        "label",
      ],
    },
    size: { control: "select", options: ["sm", "default", "lg"] },
  },
  args: { children: "Badge", variant: "default", size: "default" },
} satisfies Meta<typeof Badge>;
export default meta;
type Story = StoryObj<typeof meta>;

export const Playground: Story = {};

export const Solid: Story = {
  render: () => (
    <div className="flex flex-wrap items-center gap-2">
      <Badge variant="default">Default</Badge>
      <Badge variant="outline">Outline</Badge>
      <Badge variant="secondary">Secondary</Badge>
      <Badge variant="muted">Muted</Badge>
      <Badge variant="brand">Brand</Badge>
      <Badge variant="info">Info</Badge>
      <Badge variant="success">Success</Badge>
      <Badge variant="warning">Warning</Badge>
      <Badge variant="error">Error</Badge>
      <Badge variant="destructive">Destructive</Badge>
    </div>
  ),
};

export const Soft: Story = {
  render: () => (
    <div className="flex flex-wrap items-center gap-2">
      <Badge variant="info-soft">Needs approval</Badge>
      <Badge variant="success-soft">Allowed</Badge>
      <Badge variant="warning-soft">Denied</Badge>
      <Badge variant="error-soft">Failed</Badge>
      <Badge variant="proven-soft">Proven</Badge>
      <Badge variant="critical-soft">Critical</Badge>
    </div>
  ),
};

export const SoftWithDot: Story = {
  render: () => (
    <div className="flex flex-wrap items-center gap-2">
      <Badge variant="info-soft" dot>
        Needs approval
      </Badge>
      <Badge variant="success-soft" dot>
        Allowed
      </Badge>
      <Badge variant="warning-soft" dot>
        Denied
      </Badge>
      <Badge variant="error-soft" dot>
        Failed
      </Badge>
      <Badge variant="proven-soft" dot>
        Proven
      </Badge>
      <Badge variant="critical-soft" dot>
        Critical
      </Badge>
    </div>
  ),
};

export const Neutral: Story = {
  render: () => (
    <div className="flex flex-wrap items-center gap-2">
      <Badge variant="quiet">Queued</Badge>
      <Badge variant="chip">
        <GitBranchIcon aria-hidden />
        oxagen/runtime
      </Badge>
      <Badge variant="label">Priority 1</Badge>
      <Badge variant="label">Security</Badge>
    </div>
  ),
};

export const Sizes: Story = {
  render: () => (
    <div className="flex items-center gap-2">
      <Badge size="sm" variant="success-soft">
        Small
      </Badge>
      <Badge size="default" variant="success-soft">
        Default
      </Badge>
      <Badge size="lg" variant="success-soft">
        Large
      </Badge>
    </div>
  ),
};
