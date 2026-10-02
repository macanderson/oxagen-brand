import * as React from "react";
import type { Meta, StoryObj } from "@storybook/react-vite";
import { HoverCard, HoverCardContent } from "./hover-card";

/**
 * A card that shows the full text when the pointer rests on text a surface cuts
 * off. `TruncatedCell` uses it.
 */
const meta = {
  title: "Overlays/HoverCard",
  component: HoverCard,
  // Some stories here open a portalled popup on load. On the docs page each
  // story draws in its own frame, so the popups do not cover the page.
  parameters: {
    layout: "centered",
    docs: { story: { inline: false, height: "320px" } },
  },
} satisfies Meta<typeof HoverCard>;
export default meta;
type Story = StoryObj<typeof meta>;

/**
 * Open and anchored to a clipped table cell, the way the app shows a cell's
 * full text. The card takes an `anchor`, so it needs no trigger of its own.
 */
function AnchoredCard() {
  const cell = React.useRef<HTMLSpanElement>(null);
  return (
    <div className="min-h-56 w-72">
      <span
        ref={cell}
        className="block w-48 truncate rounded-md border border-border px-3 py-2 text-sm"
      >
        Retry the billing webhook after the Stripe signature check fails
      </span>
      <HoverCard open>
        <HoverCardContent anchor={cell} align="start" alignOffset={0}>
          <p className="font-semibold text-foreground">Release captain</p>
          <p className="mt-1 text-muted-foreground">
            Retry the billing webhook after the Stripe signature check fails,
            then open a pull request with the fix.
          </p>
          <p className="mt-2 text-xs text-muted-foreground">
            142 runs this week, $18.40 spent
          </p>
        </HoverCardContent>
      </HoverCard>
    </div>
  );
}

export const Open: Story = {
  render: () => <AnchoredCard />,
};
