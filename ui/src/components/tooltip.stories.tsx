import type { Meta, StoryObj } from "@storybook/react-vite";
import {
  Tooltip,
  TooltipTrigger,
  TooltipPopup,
  TooltipProvider,
} from "./tooltip";
import { Button } from "./button";

const meta = {
  title: "Overlays/Tooltip",
  component: Tooltip,
  // An open overlay portals to <body>, outside its story. On the Docs page
  // each story draws in its own frame, so the overlay stays with its story.
  parameters: { docs: { story: { inline: false, height: "200px" } } },
} satisfies Meta<typeof Tooltip>;
export default meta;
type Story = StoryObj<typeof meta>;

export const Default: Story = {
  render: () => (
    <TooltipProvider>
      <Tooltip>
        <TooltipTrigger render={<Button variant="outline">Pause</Button>} />
        <TooltipPopup>Pause the run after this step</TooltipPopup>
      </Tooltip>
    </TooltipProvider>
  ),
};

/**
 * Open by default, so the tooltip bubble itself is visible in the catalog and
 * verifiable by design-sync's oracle. The hover-driven `Default` story only
 * ever proves the trigger renders.
 */
export const Open: Story = {
  render: () => (
    <div className="pt-12">
      <TooltipProvider>
        <Tooltip defaultOpen>
          <TooltipTrigger render={<Button variant="outline">Pause</Button>} />
          <TooltipPopup>Pause the run after this step</TooltipPopup>
        </Tooltip>
      </TooltipProvider>
    </div>
  ),
};
