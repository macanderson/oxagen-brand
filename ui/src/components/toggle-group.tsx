"use client";
import * as React from "react";
import { ToggleGroup as ToggleGroupPrimitive } from "@base-ui/react/toggle-group";
import { Toggle } from "@base-ui/react/toggle";
import { cn } from "../lib/utils";

/*
 * ToggleGroup is the outline segmented control from the mockup (`.seg`): one
 * bordered track whose buttons sit edge to edge with a 1px rule between them.
 * The rule is the track's own background showing through a 1px gap, so a
 * wrapped row keeps its dividers without per-item borders.
 *
 * Base UI owns the state. Items carry `aria-pressed`, `data-pressed` and
 * `data-disabled`; the group is `role="group"` and needs an `aria-label`.
 * Pass `multiple` for a multi-select group. SegmentedControl reuses these
 * class strings, so the two controls always look the same.
 */

/** The track: a bordered row whose 1px gaps draw the dividers. */
const toggleGroupClass =
  "inline-flex max-w-full flex-wrap gap-px overflow-hidden rounded-lg border border-border bg-border shadow-xs";

/** One button in the track. Pressed reads as the highlight ground and a heavier weight. */
const toggleGroupItemClass = cn(
  "inline-flex flex-[1_1_auto] items-center justify-center gap-1.5 whitespace-nowrap bg-card px-[11px] py-[5px] text-base font-medium text-[var(--body)]",
  "transition-colors duration-[120ms]",
  "hover:bg-[color-mix(in_srgb,var(--hl)_60%,var(--card))] hover:text-foreground",
  "focus-visible:outline-2 focus-visible:-outline-offset-2 focus-visible:outline-ring",
  "data-[pressed]:bg-hl data-[pressed]:font-semibold data-[pressed]:text-foreground",
  "data-[disabled]:cursor-not-allowed data-[disabled]:opacity-45 data-[disabled]:hover:bg-card",
);

/** The count beside an item's label. It darkens with the pressed item. */
const toggleGroupCountClass =
  "font-mono text-xs font-medium tabular-nums text-muted-foreground group-data-[pressed]/toggle:text-muted-foreground";

interface ToggleGroupProps
  extends React.ComponentPropsWithoutRef<typeof ToggleGroupPrimitive> {
  /** Stretch the group to its container and share the width equally. */
  wide?: boolean;
}

const ToggleGroup = React.forwardRef<HTMLDivElement, ToggleGroupProps>(
  ({ className, wide = false, ...props }, ref) => (
    <ToggleGroupPrimitive
      ref={ref}
      data-slot="toggle-group"
      className={cn(
        toggleGroupClass,
        wide && "flex w-full [&>*]:flex-[1_1_0]",
        className,
      )}
      {...props}
    />
  ),
);
ToggleGroup.displayName = "ToggleGroup";

interface ToggleGroupItemProps
  extends React.ComponentPropsWithoutRef<typeof Toggle> {
  value: string;
  /**
   * A count shown after the label, such as the rows the filter matches. Zero
   * renders; leave the prop out to show no count.
   */
  count?: React.ReactNode;
}

const ToggleGroupItem = React.forwardRef<
  HTMLButtonElement,
  ToggleGroupItemProps
>(({ className, count, children, ...props }, ref) => (
  <Toggle
    ref={ref}
    data-slot="toggle-group-item"
    className={cn("group/toggle", toggleGroupItemClass, className)}
    {...props}
  >
    {children}
    {count !== undefined && count !== null ? (
      <span data-slot="toggle-group-count" className={toggleGroupCountClass}>
        {count}
      </span>
    ) : null}
  </Toggle>
));
ToggleGroupItem.displayName = "ToggleGroupItem";

export {
  ToggleGroup,
  ToggleGroupItem,
  toggleGroupClass,
  toggleGroupItemClass,
  toggleGroupCountClass,
};
export type { ToggleGroupProps, ToggleGroupItemProps };
