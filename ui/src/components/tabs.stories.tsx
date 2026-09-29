import type { Meta, StoryObj } from "@storybook/react-vite";
import { RobotIcon } from "@phosphor-icons/react";
import {
  Tabs,
  TabsList,
  TabsTab,
  TabsCount,
  TabsPanel,
  TabsIndicator,
} from "./tabs";

const meta = {
  title: "Navigation/Tabs",
  component: Tabs,
} satisfies Meta<typeof Tabs>;
export default meta;
type Story = StoryObj<typeof meta>;

export const Default: Story = {
  render: () => (
    <Tabs defaultValue="account" className="w-80">
      <TabsList>
        <TabsTab value="account">Account</TabsTab>
        <TabsTab value="password">Password</TabsTab>
        <TabsTab value="team">Team</TabsTab>
      </TabsList>
      <TabsPanel value="account">Manage your account settings.</TabsPanel>
      <TabsPanel value="password">Change your password here.</TabsPanel>
      <TabsPanel value="team">Invite and manage team members.</TabsPanel>
    </Tabs>
  ),
};

export const WithCounts: Story = {
  render: () => (
    <Tabs defaultValue="runs">
      <TabsList>
        <TabsTab value="runs" count={24}>
          Runs
        </TabsTab>
        <TabsTab value="agents" count={6}>
          Agents
        </TabsTab>
        <TabsTab value="mandates" count={3}>
          Mandates
        </TabsTab>
      </TabsList>
      <TabsPanel value="runs">Runs from the last seven days.</TabsPanel>
      <TabsPanel value="agents">Agents in this workspace.</TabsPanel>
      <TabsPanel value="mandates">Mandates that apply to these agents.</TabsPanel>
    </Tabs>
  ),
};

export const ZeroCount: Story = {
  render: () => (
    <Tabs defaultValue="open">
      <TabsList>
        <TabsTab value="open" count={5}>
          Open
        </TabsTab>
        <TabsTab value="waiting" count={0}>
          Waiting on you
        </TabsTab>
        <TabsTab value="closed" count={41}>
          Closed
        </TabsTab>
      </TabsList>
      <TabsPanel value="open">Five runs are open.</TabsPanel>
      <TabsPanel value="waiting">No run is waiting on you.</TabsPanel>
      <TabsPanel value="closed">Closed runs from this month.</TabsPanel>
    </Tabs>
  ),
};

export const CountPart: Story = {
  render: () => (
    <Tabs defaultValue="agents">
      <TabsList>
        <TabsTab value="agents">
          <RobotIcon aria-hidden className="size-4" />
          Agents
          <TabsCount>6</TabsCount>
        </TabsTab>
        <TabsTab value="repositories" count={12}>
          Repositories
        </TabsTab>
      </TabsList>
      <TabsPanel value="agents">Agents in this workspace.</TabsPanel>
      <TabsPanel value="repositories">Repositories the agents can read.</TabsPanel>
    </Tabs>
  ),
};

export const PhoneWidth: Story = {
  render: () => (
    <div className="w-[360px]">
      <Tabs defaultValue="runs">
        <TabsList>
          <TabsTab value="runs" count={24}>
            Runs
          </TabsTab>
          <TabsTab value="agents" count={6}>
            Agents
          </TabsTab>
          <TabsTab value="mandates" count={3}>
            Mandates
          </TabsTab>
          <TabsTab value="repositories" count={12}>
            Repositories
          </TabsTab>
        </TabsList>
        <TabsPanel value="runs">The row scrolls sideways when the tabs do not fit.</TabsPanel>
      </Tabs>
    </div>
  ),
};

export const Underline: Story = {
  render: () => (
    <Tabs defaultValue="overview" className="w-80">
      <TabsList variant="underline">
        <TabsTab value="overview">Overview</TabsTab>
        <TabsTab value="activity">Activity</TabsTab>
        <TabsTab value="settings">Settings</TabsTab>
        <TabsIndicator />
      </TabsList>
      <TabsPanel value="overview">Overview panel.</TabsPanel>
      <TabsPanel value="activity">Activity panel.</TabsPanel>
      <TabsPanel value="settings">Settings panel.</TabsPanel>
    </Tabs>
  ),
};
