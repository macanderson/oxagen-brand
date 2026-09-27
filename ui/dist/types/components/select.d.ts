import * as React from "react";
import { Select as SelectPrimitive } from "@base-ui/react/select";
import { type VariantProps } from "class-variance-authority";
declare const Select: typeof SelectPrimitive.Root;
declare const SelectGroup: React.ForwardRefExoticComponent<Omit<import("@base-ui/react").SelectGroupProps, "ref"> & React.RefAttributes<HTMLDivElement>>;
declare const SelectValue: React.ForwardRefExoticComponent<Omit<import("@base-ui/react").SelectValueProps, "ref"> & React.RefAttributes<HTMLSpanElement>>;
declare const selectTriggerVariants: (props?: ({
    size?: "default" | "sm" | "lg" | null | undefined;
} & import("class-variance-authority/types").ClassProp) | undefined) => string;
interface SelectTriggerProps extends Omit<React.ComponentPropsWithoutRef<typeof SelectPrimitive.Trigger>, "size">, VariantProps<typeof selectTriggerVariants> {
}
declare const SelectTrigger: React.ForwardRefExoticComponent<SelectTriggerProps & React.RefAttributes<HTMLButtonElement>>;
interface SelectPopupProps extends React.ComponentPropsWithoutRef<typeof SelectPrimitive.Popup> {
    sideOffset?: number;
    /**
     * When `true`, the popup aligns the selected item with the trigger text
     * (Base UI default). Defaults to `false` for a conventional dropdown.
     */
    alignItemWithTrigger?: boolean;
    /** Forwarded to Base UI `Select.Portal` (e.g. `keepMounted`, custom `container`). */
    portalProps?: React.ComponentPropsWithoutRef<typeof SelectPrimitive.Portal>;
}
declare const SelectPopup: React.ForwardRefExoticComponent<SelectPopupProps & React.RefAttributes<HTMLDivElement>>;
declare const SelectLabel: React.ForwardRefExoticComponent<Omit<Omit<import("@base-ui/react").SelectGroupLabelProps, "ref"> & React.RefAttributes<HTMLDivElement>, "ref"> & React.RefAttributes<HTMLDivElement>>;
declare const SelectItem: React.ForwardRefExoticComponent<Omit<Omit<import("@base-ui/react").SelectItemProps, "ref"> & React.RefAttributes<HTMLElement>, "ref"> & React.RefAttributes<HTMLElement>>;
export { Select, SelectGroup, SelectValue, SelectTrigger, SelectPopup, SelectLabel, SelectItem, };
