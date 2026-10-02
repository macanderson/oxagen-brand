import type { Meta, StoryObj } from "@storybook/react-vite";
import {
  Dialog,
  DialogTrigger,
  DialogPopup,
  DialogHeader,
  DialogPanel,
  DialogFooter,
  DialogTitle,
  DialogDescription,
  DialogClose,
} from "./dialog";
import { Tabs, TabsList, TabsTab, TabsPanel } from "./tabs";
import { Button } from "./button";
import { Input } from "./input";
import { Label } from "./label";

/**
 * A box over the page that asks for input or a decision. The box has no
 * padding, so content goes in `DialogHeader`, `DialogPanel`, and
 * `DialogFooter`. `size="wide"` makes it 820px wide in place of 600px.
 */
const meta = {
  title: "Overlays/Dialog",
  component: Dialog,
  // Some stories here open a portalled popup on load. On the docs page each
  // story draws in its own frame, so the popups do not cover the page.
  parameters: { docs: { story: { inline: false, height: "520px" } } },
} satisfies Meta<typeof Dialog>;
export default meta;
type Story = StoryObj<typeof meta>;

function EditAgent({ defaultOpen, idPrefix }: { defaultOpen?: boolean; idPrefix: string }) {
  return (
    <Dialog defaultOpen={defaultOpen}>
      <DialogTrigger render={<Button>Edit agent</Button>} />
      <DialogPopup>
        <DialogHeader>
          <DialogTitle>Edit agent</DialogTitle>
          <DialogDescription>
            Changes apply to the next run this agent starts.
          </DialogDescription>
        </DialogHeader>
        <DialogPanel>
          <div className="flex flex-col gap-1.5">
            <Label htmlFor={`${idPrefix}-name`}>Name</Label>
            <Input id={`${idPrefix}-name`} defaultValue="Release captain" />
          </div>
          <div className="flex flex-col gap-1.5">
            <Label htmlFor={`${idPrefix}-cap`}>Daily spend cap in USD</Label>
            <Input id={`${idPrefix}-cap`} defaultValue="40.00" />
          </div>
        </DialogPanel>
        <DialogFooter>
          <DialogClose render={<Button variant="ghost">Cancel</Button>} />
          <DialogClose render={<Button>Save agent</Button>} />
        </DialogFooter>
      </DialogPopup>
    </Dialog>
  );
}

export const Default: Story = {
  render: () => <EditAgent idPrefix="agent" />,
};

/**
 * Open by default, so the popup surface itself is visible in the catalog and
 * verifiable by design-sync's screenshot oracle. The closed `Default` story
 * only ever proves the trigger renders.
 */
export const Open: Story = {
  render: () => <EditAgent defaultOpen idPrefix="agent-open" />,
};

/** An underline tab row sits flush between the header and the body. */
export const WithUnderlineTabs: Story = {
  render: () => (
    <Dialog defaultOpen>
      <DialogTrigger render={<Button>Agent settings</Button>} />
      <DialogPopup size="wide">
        <DialogHeader>
          <DialogTitle>Release captain</DialogTitle>
          <DialogDescription>
            Cuts releases on the oxagen repository and watches the deploy.
          </DialogDescription>
        </DialogHeader>
        <Tabs defaultValue="general" className="flex min-h-0 flex-1 flex-col">
          <TabsList variant="underline" className="shrink-0 px-[18px]">
            <TabsTab value="general">General</TabsTab>
            <TabsTab value="steering">Steering</TabsTab>
            <TabsTab value="spend">Spend</TabsTab>
          </TabsList>
          <DialogPanel>
            <TabsPanel value="general" className="mt-0">
              <div className="flex flex-col gap-3">
                <div className="flex flex-col gap-1.5">
                  <Label htmlFor="tabs-name">Name</Label>
                  <Input id="tabs-name" defaultValue="Release captain" />
                </div>
                <div className="flex flex-col gap-1.5">
                  <Label htmlFor="tabs-repo">Repository</Label>
                  <Input id="tabs-repo" defaultValue="macanderson/oxagen" />
                </div>
              </div>
            </TabsPanel>
            <TabsPanel value="steering" className="mt-0">
              <p className="text-muted-foreground">
                Four rules from .oxagen/rules apply to this agent.
              </p>
            </TabsPanel>
            <TabsPanel value="spend" className="mt-0">
              <p className="text-muted-foreground">
                $18.40 spent across 142 runs this week.
              </p>
            </TabsPanel>
          </DialogPanel>
        </Tabs>
        <DialogFooter>
          <DialogClose render={<Button variant="ghost">Cancel</Button>} />
          <DialogClose render={<Button>Save agent</Button>} />
        </DialogFooter>
      </DialogPopup>
    </Dialog>
  ),
};

/** A confirm for an action that cannot be undone. */
export const DestructiveConfirm: Story = {
  render: () => (
    <Dialog defaultOpen>
      <DialogTrigger render={<Button variant="destructive">Delete agent</Button>} />
      <DialogPopup>
        <DialogHeader>
          <DialogTitle>Delete Release captain?</DialogTitle>
          <DialogDescription>
            Its 142 runs stay in the record. Scheduled runs stop.
          </DialogDescription>
        </DialogHeader>
        <DialogPanel>
          <p>
            Work items assigned to this agent go back to the queue. You cannot
            undo this.
          </p>
        </DialogPanel>
        <DialogFooter>
          <DialogClose render={<Button variant="ghost">Keep agent</Button>} />
          <DialogClose render={<Button variant="destructive">Delete agent</Button>} />
        </DialogFooter>
      </DialogPopup>
    </Dialog>
  ),
};
