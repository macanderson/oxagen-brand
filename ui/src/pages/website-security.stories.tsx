import type { Meta, StoryObj } from "@storybook/react-vite";
import { SecurityPage } from "./website-security";

const meta = {
  title: "Pages/Website/Security",
  component: SecurityPage,
  // A page fixture is not a component, so it gets no Docs page.
  tags: ["!autodocs"],
  parameters: { layout: "fullscreen", page: true },
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
