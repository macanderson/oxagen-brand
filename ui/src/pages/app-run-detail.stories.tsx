import type { Meta, StoryObj } from "@storybook/react-vite";
import { RunDetailPage } from "./app-run-detail";

const meta = {
  title: "Pages/App/Run detail",
  component: RunDetailPage,
  parameters: { layout: "fullscreen", page: true },
  // A page story fills the screen, so a docs page would stack whole pages.
  // Each story stays in the sidebar.
  tags: ["!autodocs"],
  args: { commandMenuOpen: true },
} satisfies Meta<typeof RunDetailPage>;
export default meta;
type Story = StoryObj<typeof meta>;

/** The command menu open over the page, with the run's own commands first. */
export const Open: Story = {
  name: "Command menu open",
};

/** The same page with every overlay closed. Scroll to pass it under the header. */
export const Closed: Story = {
  name: "Command menu closed",
  args: { commandMenuOpen: false },
};
