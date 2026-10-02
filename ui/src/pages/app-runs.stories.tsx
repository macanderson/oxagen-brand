import type { Meta, StoryObj } from "@storybook/react-vite";
import { RunsPage } from "./app-runs";

const meta = {
  title: "Pages/App/Runs",
  component: RunsPage,
  parameters: { layout: "fullscreen", page: true },
  // A page story fills the screen, so a docs page would stack whole pages.
  // Each story stays in the sidebar.
  tags: ["!autodocs"],
  args: { rowMenuOpen: true, toast: true },
} satisfies Meta<typeof RunsPage>;
export default meta;
type Story = StoryObj<typeof meta>;

/** A row's action menu open over the table, and a toast in the corner. */
export const Open: Story = {
  name: "Menu and toast open",
};

/** The same page with every overlay closed. */
export const Closed: Story = {
  name: "Overlays closed",
  args: { rowMenuOpen: false, toast: false },
};
