import type { Meta, StoryObj } from "@storybook/react-vite";
import { SecurityPage } from "./website-security";

const meta = {
  title: "Pages/Website/Security",
  component: SecurityPage,
  parameters: { layout: "fullscreen", page: true },
  // A page story fills the screen, so a docs page would stack whole pages.
  // Each story stays in the sidebar.
  tags: ["!autodocs"],
  args: { scopeOpen: true },
} satisfies Meta<typeof SecurityPage>;
export default meta;
type Story = StoryObj<typeof meta>;

/** The Scope popover open over the capability cards. */
export const Open: Story = {
  name: "Popover open",
};

/** The same page with every overlay closed. */
export const Closed: Story = {
  name: "Popover closed",
  args: { scopeOpen: false },
};
