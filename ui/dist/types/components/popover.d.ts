import * as React from "react";
import { Popover as PopoverPrimitive } from "@base-ui/react/popover";
/**
 * coss ui Popover — Base UI Popover, token-driven.
 *
 *   <Popover>
 *     <PopoverTrigger render={<Button variant="ghost" size="icon" />}>
 *       <HelpCircle />
 *     </PopoverTrigger>
 *     <PopoverPopup>
 *       <PopoverTitle>What is a registry?</PopoverTitle>
 *       <PopoverDescription>…</PopoverDescription>
 *     </PopoverPopup>
 *   </Popover>
 *
 * Uses Base UI's `render` prop (not `asChild`). The popup is portalled and
 * positioned. `side`/`align`/`sideOffset` tune placement.
 */
declare const Popover: typeof PopoverPrimitive.Root;
declare const PopoverTrigger: PopoverPrimitive.Trigger;
declare const PopoverClose: React.ForwardRefExoticComponent<Omit<import("@base-ui/react").PopoverCloseProps, "ref"> & React.RefAttributes<HTMLButtonElement>>;
declare const PopoverTitle: React.ForwardRefExoticComponent<Omit<import("@base-ui/react").PopoverTitleProps, "ref"> & React.RefAttributes<HTMLHeadingElement>>;
declare const PopoverDescription: React.ForwardRefExoticComponent<Omit<import("@base-ui/react").PopoverDescriptionProps, "ref"> & React.RefAttributes<HTMLParagraphElement>>;
interface PopoverPopupProps extends React.ComponentPropsWithoutRef<typeof PopoverPrimitive.Popup> {
    sideOffset?: number;
    align?: "start" | "center" | "end";
    side?: "top" | "bottom" | "left" | "right";
    /** Forwarded to Base UI `Popover.Portal`. */
    portalProps?: React.ComponentPropsWithoutRef<typeof PopoverPrimitive.Portal>;
}
declare const PopoverPopup: React.ForwardRefExoticComponent<PopoverPopupProps & React.RefAttributes<HTMLDivElement>>;
export { Popover, PopoverTrigger, PopoverClose, PopoverPopup, PopoverTitle, PopoverDescription, };
