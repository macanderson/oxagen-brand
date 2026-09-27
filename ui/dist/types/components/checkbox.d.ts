import * as React from "react";
/**
 * coss ui Checkbox — Base UI `Checkbox.Root` + `Checkbox.Indicator`. Flat (no
 * shadow). UNCHECKED: a transparent box with a `--foreground`-coloured outline
 * (so it reads dark in light mode, light in dark mode — never a filled white
 * chip). CHECKED / INDETERMINATE: fills with the primary track colour and the
 * outline disappears into the fill; the mark colour is --control-indicator.
 * (The checked track + indicator colours stay on the shared --control-* tokens
 * that Radio and Switch also consume.)
 *
 * State attributes: `data-[checked]`, `data-[unchecked]`,
 * `data-[indeterminate]`, `data-[disabled]`.
 *
 *   <Checkbox checked={v} onCheckedChange={setV} />
 *   <label className="flex items-center gap-2 text-sm">
 *     <Checkbox defaultChecked /> Remember me
 *   </label>
 */
declare const Checkbox: React.ForwardRefExoticComponent<Omit<Omit<import("@base-ui/react").CheckboxRootProps, "ref"> & React.RefAttributes<HTMLElement>, "ref"> & React.RefAttributes<HTMLElement>>;
export { Checkbox };
