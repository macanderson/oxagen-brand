/**
 * Combobox — searchable typeahead select built on Base UI's Combobox primitive.
 *
 * Use this instead of Select whenever the option list has more than 20 items
 * (country: 249, US state: 51, industry: 24). The UX rule:
 *   > 20 options → Combobox with typeahead search
 *   ≤ 20 options → plain Select
 *
 * Parts exported (shadcn-style naming conventions, coss popup naming):
 *   Combobox            — root (value/onValueChange/defaultValue/disabled)
 *   ComboboxTrigger     — the clickable trigger button (shows selected label)
 *   ComboboxValue       — renders the selected label (or placeholder)
 *   ComboboxPopup       — the animated overlay containing search + list
 *   ComboboxItem        — a single option row
 *
 * Usage:
 * ```tsx
 * <Combobox value={country} onValueChange={setCountry}>
 *   <ComboboxTrigger id="country" size="lg" className="w-full">
 *     <ComboboxValue placeholder="Select country" />
 *   </ComboboxTrigger>
 *   <ComboboxPopup searchPlaceholder="Search countries…">
 *     {COUNTRY_OPTIONS.map((o) => (
 *       <ComboboxItem key={o.value} value={o.value}>{o.label}</ComboboxItem>
 *     ))}
 *   </ComboboxPopup>
 * </Combobox>
 * ```
 */
import * as React from "react";
import { Combobox as ComboboxPrimitive } from "@base-ui/react/combobox";
import { type VariantProps } from "class-variance-authority";
/**
 * Root combobox context provider.
 * Accepts `value`, `onValueChange`, `defaultValue`, `disabled`, `name`.
 */
declare function Combobox<V = string>({ children, value, onValueChange, defaultValue, disabled, name, }: {
    children: React.ReactNode;
    value?: V | null;
    onValueChange?: (value: V | null) => void;
    defaultValue?: V | null;
    disabled?: boolean;
    name?: string;
}): import("react/jsx-runtime").JSX.Element;
declare namespace Combobox {
    var displayName: string;
}
declare const comboboxTriggerVariants: (props?: ({
    size?: "default" | "sm" | "lg" | null | undefined;
} & import("class-variance-authority/types").ClassProp) | undefined) => string;
interface ComboboxTriggerProps extends Omit<React.ComponentPropsWithoutRef<typeof ComboboxPrimitive.Trigger>, "size">, VariantProps<typeof comboboxTriggerVariants> {
}
declare const ComboboxTrigger: React.ForwardRefExoticComponent<ComboboxTriggerProps & React.RefAttributes<HTMLButtonElement>>;
declare function ComboboxValue({ placeholder }: {
    placeholder?: string;
}): import("react/jsx-runtime").JSX.Element;
declare namespace ComboboxValue {
    var displayName: string;
}
interface ComboboxPopupProps {
    children: React.ReactNode;
    className?: string;
    searchPlaceholder?: string;
    sideOffset?: number;
    portalProps?: React.ComponentPropsWithoutRef<typeof ComboboxPrimitive.Portal>;
}
declare function ComboboxPopup({ children, className, searchPlaceholder, sideOffset, portalProps, }: ComboboxPopupProps): import("react/jsx-runtime").JSX.Element;
declare namespace ComboboxPopup {
    var displayName: string;
}
declare const ComboboxItem: React.ForwardRefExoticComponent<Omit<Omit<import("@base-ui/react").ComboboxItemProps, "ref"> & React.RefAttributes<HTMLDivElement>, "ref"> & React.RefAttributes<HTMLDivElement>>;
export { Combobox, ComboboxTrigger, ComboboxValue, ComboboxPopup, ComboboxItem, };
