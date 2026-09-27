import * as React from "react";
import { ToggleGroup } from "@base-ui/react/toggle-group";
import { Toggle } from "@base-ui/react/toggle";
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
 */
interface SegmentedControlProps extends Omit<React.ComponentPropsWithoutRef<typeof ToggleGroup>, "value" | "defaultValue" | "onValueChange" | "multiple"> {
    /** The currently selected item value (controlled). */
    value?: string;
    /** The initially selected item value (uncontrolled). */
    defaultValue?: string;
    /** Called when the selected item changes. */
    onValueChange?: (value: string) => void;
}
declare const SegmentedControl: React.ForwardRefExoticComponent<SegmentedControlProps & React.RefAttributes<HTMLDivElement>>;
/**
 * Individual item within a `SegmentedControl`.
 * State attributes: `data-[pressed]` (selected), `data-[disabled]`.
 */
interface SegmentedControlItemProps extends React.ComponentPropsWithoutRef<typeof Toggle> {
    value: string;
}
declare const SegmentedControlItem: React.ForwardRefExoticComponent<SegmentedControlItemProps & React.RefAttributes<HTMLButtonElement>>;
export { SegmentedControl, SegmentedControlItem };
export type { SegmentedControlProps, SegmentedControlItemProps };
