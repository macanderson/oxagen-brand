import type { Meta, StoryObj } from "@storybook/react-vite";
import { RunPage } from "./run-page";

const meta = {
  title: "Pages/App/Run",
  component: RunPage,
  // A page fixture is not a component, so it gets no Docs page.
  tags: ["!autodocs"],
  parameters: { layout: "fullscreen", page: true },
} satisfies Meta<typeof RunPage>;
export default meta;
type Story = StoryObj<typeof meta>;

/** A live Claude Code run whose push to the release branch waits for a person, with the Transcript tab open. */
export const Live: Story = {};
