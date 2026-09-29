"use client";
import * as React from "react";
import { ToggleGroup } from "@base-ui/react/toggle-group";
import { Toggle } from "@base-ui/react/toggle";
import { cn } from "../lib/utils";
import { toggleGroupClass, toggleGroupItemClass } from "./toggle-group";

/**
 * coss ui SegmentedControl — wraps Base UI `ToggleGroup` + `Toggle`.
 *
 * Single-select pill control for discrete preference choices such as:
 * - Font size: Small / Medium / Large
 * - Density: Compact / Comfortable / Spacious
 * - Prompt behavior: Queue / Interrupt
 *
 * Controlled via `value` / `onValueChange` (single string, not array).
 * Base UI `ToggleGroup` is array-based; this wrapper enforces single-select
 * by accepting a single string value and converting to/from the Base UI
 * array-based API. `multiple` is always false.
 *
 * State attributes on items: `data-[pressed]` (selected), `data-[disabled]`.
 *
 * It is the single-select form of ToggleGroup and shares its outline look
 * (`toggleGroupClass` and `toggleGroupItemClass`), so the two never drift.
 * Reach for ToggleGroup when a choice needs several values or counts.
 */
interface SegmentedControlProps
  extends Omit<
    React.ComponentPropsWithoutRef<typeof ToggleGroup>,
    "value" | "defaultValue" | "onValueChange" | "multiple"
  > {
  /** The currently selected item value (controlled). */
  value?: string;
  /** The initially selected item value (uncontrolled). */
  defaultValue?: string;
  /** Called when the selected item changes. */
  onValueChange?: (value: string) => void;
}

const SegmentedControl = React.forwardRef<
  HTMLDivElement,
  SegmentedControlProps
>(({ className, value, defaultValue, onValueChange, ...props }, ref) => {
  const groupValue = value !== undefined ? [value] : undefined;
  const groupDefault = defaultValue !== undefined ? [defaultValue] : undefined;

  const handleValueChange = React.useCallback(
    (groupValues: string[]) => {
      // Single-select: take the last pressed value; ignore empty (deselect not allowed)
      const next = groupValues[groupValues.length - 1];
      if (next !== undefined) {
        onValueChange?.(next);
      }
    },
    [onValueChange],
  );

  return (
    <ToggleGroup
      ref={ref}
      multiple={false}
      value={groupValue}
      defaultValue={groupDefault}
      onValueChange={handleValueChange}
      data-slot="segmented-control"
      className={cn(toggleGroupClass, className)}
      {...props}
    />
  );
});
SegmentedControl.displayName = "SegmentedControl";

/**
 * Individual item within a `SegmentedControl`.
 * State attributes: `data-[pressed]` (selected), `data-[disabled]`.
 */
interface SegmentedControlItemProps
  extends React.ComponentPropsWithoutRef<typeof Toggle> {
  value: string;
}

const SegmentedControlItem = React.forwardRef<
  HTMLButtonElement,
  SegmentedControlItemProps
>(({ className, ...props }, ref) => (
  <Toggle
    ref={ref}
    data-slot="segmented-control-item"
    className={cn(toggleGroupItemClass, className)}
    {...props}
  />
));
SegmentedControlItem.displayName = "SegmentedControlItem";

export { SegmentedControl, SegmentedControlItem };
export type { SegmentedControlProps, SegmentedControlItemProps };
