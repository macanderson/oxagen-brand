import type { Meta, StoryObj } from "@storybook/react-vite";
import { WorkPage } from "./work-page";

const meta = {
  title: "Pages/App/Work",
  component: WorkPage,
  // A page fixture is not a component, so it gets no Docs page.
  tags: ["!autodocs"],
  parameters: { layout: "fullscreen", page: true },
  args: { tab: "inbox", collectorFailing: false },
  argTypes: {
    tab: { control: "inline-radio", options: ["inbox", "running", "review", "done"] },
  },
} satisfies Meta<typeof WorkPage>;
export default meta;
type Story = StoryObj<typeof meta>;

/** The Inbox: a failed triage first, then the items by priority, then the one triage is reading. */
export const Inbox: Story = {};

/** The items an agent is working on, and what each one costs so far. */
export const Running: Story = {
  args: { tab: "running" },
};

/** The pull requests waiting for a person, with their required checks. */
export const Review: Story = {
  args: { tab: "review" },
};

/** The Inbox under the banner a failing collector raises. */
export const CollectorFailing: Story = {
  name: "Collector failing",
  args: { collectorFailing: true },
};
