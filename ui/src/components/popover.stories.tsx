import type { Meta, StoryObj } from "@storybook/react-vite";
import {
  Popover,
  PopoverTrigger,
  PopoverPopup,
  PopoverTitle,
  PopoverDescription,
} from "./popover";
import { Button } from "./button";
import { Input } from "./input";
import { Label } from "./label";

const meta = {
  title: "Overlays/Popover",
  component: Popover,
  parameters: { layout: "centered" },
} satisfies Meta<typeof Popover>;
export default meta;
type Story = StoryObj<typeof meta>;

function SpendCap({ defaultOpen }: { defaultOpen?: boolean }) {
  return (
    <Popover defaultOpen={defaultOpen}>
      <PopoverTrigger render={<Button variant="outline">Spend cap</Button>} />
      <PopoverPopup className="w-72">
        <PopoverTitle>Daily spend cap</PopoverTitle>
        <PopoverDescription>
          Runs pause when the workspace spends this much in a day.
        </PopoverDescription>
        <div className="mt-3 flex items-center gap-2">
          <Label htmlFor={defaultOpen ? "cap-open" : "cap"} className="w-16">
            USD
          </Label>
          <Input
            id={defaultOpen ? "cap-open" : "cap"}
            defaultValue="40.00"
            size="sm"
          />
        </div>
      </PopoverPopup>
    </Popover>
  );
}

export const Default: Story = {
  render: () => <SpendCap />,
};

/** Open by default, so the surface, title, description and field show. */
export const Open: Story = {
  render: () => (
    <div className="min-h-56">
      <SpendCap defaultOpen />
    </div>
  ),
};
