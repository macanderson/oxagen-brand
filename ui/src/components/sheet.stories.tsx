import type { Meta, StoryObj } from "@storybook/react-vite";
import {
  Sheet,
  SheetTrigger,
  SheetPopup,
  SheetHeader,
  SheetPanel,
  SheetFooter,
  SheetTitle,
  SheetDescription,
  SheetClose,
} from "./sheet";
import { Button } from "./button";

const meta = {
  title: "Overlays/Sheet",
  component: Sheet,
} satisfies Meta<typeof Sheet>;
export default meta;
type Story = StoryObj<typeof meta>;

const STEPS = [
  ["Read the failing webhook test", "12s"],
  ["Patch the Stripe signature check", "48s"],
  ["Run the billing suite", "2m 04s"],
  ["Open pull request #4812", "9s"],
] as const;

function RunDrawer({ defaultOpen }: { defaultOpen?: boolean }) {
  return (
    <Sheet defaultOpen={defaultOpen}>
      <SheetTrigger render={<Button variant="outline">Open run</Button>} />
      <SheetPopup side="right">
        <SheetHeader>
          <SheetTitle>Run 4812</SheetTitle>
          <SheetDescription>
            Release captain on oxagen, finished 4 minutes ago for $0.62.
          </SheetDescription>
        </SheetHeader>
        <SheetPanel>
          {STEPS.map(([step, time]) => (
            <div
              key={step}
              className="flex items-center justify-between gap-3 border-b border-border pb-3"
            >
              <span>{step}</span>
              <span className="text-muted-foreground tabular-nums">{time}</span>
            </div>
          ))}
        </SheetPanel>
        <SheetFooter>
          <SheetClose render={<Button variant="ghost">Done</Button>} />
          <Button>Open pull request</Button>
        </SheetFooter>
      </SheetPopup>
    </Sheet>
  );
}

export const Right: Story = {
  render: () => <RunDrawer />,
};

/**
 * Open by default, so the sheet popup, header, body and footer are visible in
 * the catalog and verifiable by design-sync's oracle.
 */
export const RightOpen: Story = {
  render: () => <RunDrawer defaultOpen />,
};
