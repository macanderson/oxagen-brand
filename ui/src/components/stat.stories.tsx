import type { Meta, StoryObj } from "@storybook/react-vite";
import {
  CoinsIcon,
  PlayIcon,
  RobotIcon,
  ShieldCheckIcon,
} from "@phosphor-icons/react";
import { Stat, StatGroup } from "./stat";

const meta = {
  title: "Primitives/Stat",
  component: Stat,
  args: { label: "Runs this week", value: "1,284" },
  render: (args) => (
    <div className="w-[220px]">
      <Stat {...args} />
    </div>
  ),
} satisfies Meta<typeof Stat>;
export default meta;
type Story = StoryObj<typeof meta>;

export const Default: Story = {
  args: { icon: <PlayIcon />, hint: "Across 6 repositories" },
};

export const Rising: Story = {
  args: {
    icon: <PlayIcon />,
    delta: "+12.4%",
    trend: "up",
    hint: "Against last week",
  },
};

export const Falling: Story = {
  args: {
    label: "Spend this month",
    value: "$842.10",
    icon: <CoinsIcon />,
    delta: "-8.2%",
    trend: "down",
    intent: "positive",
    hint: "Against last month",
  },
};

export const Loading: Story = {
  args: { icon: <PlayIcon />, loading: true },
};

export const Empty: Story = {
  args: {
    label: "Last run",
    value: null,
    empty: "None yet",
    hint: "Runs appear once an agent starts",
  },
};

function StripOfFourTiles() {
  return (
    <StatGroup>
      <Stat
        label="Runs this week"
        value="1,284"
        delta="+12.4%"
        trend="up"
        icon={<PlayIcon />}
        hint="Against last week"
      />
      <Stat
        label="Spend this month"
        value="$842.10"
        delta="+3.1%"
        trend="up"
        intent="negative"
        icon={<CoinsIcon />}
        hint="Against last month"
      />
      <Stat
        label="Active agents"
        value="12"
        delta="0"
        trend="flat"
        icon={<RobotIcon />}
      />
      <Stat
        label="Open mandates"
        value="3"
        tone="warning"
        icon={<ShieldCheckIcon />}
        hint="Waiting on approval"
      />
    </StatGroup>
  );
}

export const StripOfFour: Story = {
  render: () => (
    <div className="w-[880px] max-w-full">
      <StripOfFourTiles />
    </div>
  ),
};

export const PhoneWidth: Story = {
  render: () => (
    <div className="w-[360px]">
      <StripOfFourTiles />
    </div>
  ),
};
