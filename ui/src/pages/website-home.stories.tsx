import type { Meta, StoryObj } from "@storybook/react-vite";
import { HomePage } from "./website-home";

const meta = {
  title: "Pages/Website/Home",
  component: HomePage,
  parameters: { layout: "fullscreen", page: true },
  args: { productMenuOpen: true },
} satisfies Meta<typeof HomePage>;
export default meta;
type Story = StoryObj<typeof meta>;

/** The Product menu open over the hero. Scroll to pass the page under the nav. */
export const Open: Story = {
  name: "Menu open",
};

/** The same page with every overlay closed. */
export const Closed: Story = {
  name: "Menu closed",
  args: { productMenuOpen: false },
};
