import * as React from "react";
import type { Meta, StoryObj } from "@storybook/react-vite";
import { ToggleGroup, ToggleGroupItem } from "./toggle-group";

const meta = {
  title: "Forms/ToggleGroup",
  component: ToggleGroup,
} satisfies Meta<typeof ToggleGroup>;
export default meta;
type Story = StoryObj<typeof meta>;

const STATUSES = [
  { value: "running", label: "Running", count: 4 },
  { value: "waiting", label: "Waiting", count: 2 },
  { value: "failed", label: "Failed", count: 0 },
  { value: "done", label: "Done", count: 38 },
];

export const NoneSelected: Story = {
  render: () => {
    const [value, setValue] = React.useState<string[]>([]);
    return (
      <ToggleGroup
        aria-label="Run status"
        multiple
        value={value}
        onValueChange={setValue}
      >
        {STATUSES.map((status) => (
          <ToggleGroupItem key={status.value} value={status.value}>
            {status.label}
          </ToggleGroupItem>
        ))}
      </ToggleGroup>
    );
  },
};

export const OneSelected: Story = {
  render: () => {
    const [value, setValue] = React.useState<string[]>(["week"]);
    return (
      <ToggleGroup aria-label="Time range" value={value} onValueChange={setValue}>
        <ToggleGroupItem value="day">Day</ToggleGroupItem>
        <ToggleGroupItem value="week">Week</ToggleGroupItem>
        <ToggleGroupItem value="month">Month</ToggleGroupItem>
      </ToggleGroup>
    );
  },
};

export const SeveralSelected: Story = {
  render: () => {
    const [value, setValue] = React.useState<string[]>(["running", "waiting"]);
    return (
      <ToggleGroup
        aria-label="Run status"
        multiple
        value={value}
        onValueChange={setValue}
      >
        {STATUSES.map((status) => (
          <ToggleGroupItem key={status.value} value={status.value}>
            {status.label}
          </ToggleGroupItem>
        ))}
      </ToggleGroup>
    );
  },
};

export const WithCounts: Story = {
  render: () => {
    const [value, setValue] = React.useState<string[]>(["running"]);
    return (
      <ToggleGroup
        aria-label="Run status"
        multiple
        value={value}
        onValueChange={setValue}
      >
        {STATUSES.map((status) => (
          <ToggleGroupItem
            key={status.value}
            value={status.value}
            count={status.count}
          >
            {status.label}
          </ToggleGroupItem>
        ))}
      </ToggleGroup>
    );
  },
};

export const Disabled: Story = {
  render: () => (
    <div className="flex flex-col items-start gap-3">
      <ToggleGroup aria-label="Agent scope" defaultValue={["mine"]} disabled>
        <ToggleGroupItem value="mine">My agents</ToggleGroupItem>
        <ToggleGroupItem value="team">Team agents</ToggleGroupItem>
      </ToggleGroup>
      <ToggleGroup aria-label="Repository visibility" defaultValue={["all"]}>
        <ToggleGroupItem value="all">All</ToggleGroupItem>
        <ToggleGroupItem value="public">Public</ToggleGroupItem>
        <ToggleGroupItem value="archived" disabled>
          Archived
        </ToggleGroupItem>
      </ToggleGroup>
    </div>
  ),
};

export const Wide: Story = {
  render: () => (
    <div className="w-[360px]">
      <ToggleGroup aria-label="Mandate state" wide defaultValue={["active"]}>
        <ToggleGroupItem value="active" count={12}>
          Active
        </ToggleGroupItem>
        <ToggleGroupItem value="paused" count={3}>
          Paused
        </ToggleGroupItem>
        <ToggleGroupItem value="retired" count={0}>
          Retired
        </ToggleGroupItem>
      </ToggleGroup>
    </div>
  ),
};
