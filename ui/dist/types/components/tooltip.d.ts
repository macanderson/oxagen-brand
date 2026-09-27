import * as React from "react";
import { Tooltip as TooltipPrimitive } from "@base-ui/react/tooltip";
/**
 * coss ui Tooltip — Base UI Tooltip, token-driven via the --tooltip-* tokens.
 * Mount <TooltipProvider> once near the app root so hover open/close delays are
 * shared across the app (Base UI's grouping behaviour); an individual <Tooltip>
 * still works standalone without it.
 *
 *   <Tooltip>
 *     <TooltipTrigger render={<Button variant="ghost" size="icon" />}>
 *       <Bell />
 *     </TooltipTrigger>
 *     <TooltipPopup>Notifications</TooltipPopup>
 *   </Tooltip>
 *
 * Composition uses Base UI's `render` prop (not `asChild`). The popup is
 * portalled and positioned; `side`/`align`/`sideOffset` tune placement. Follows
 * the same Portal → Positioner → Popup shape and motion tokens as Menu/Select.
 */
declare const TooltipProvider: React.FC<import("@base-ui/react").TooltipProviderProps>;
declare const Tooltip: <Payload>(props: TooltipPrimitive.Root.Props<Payload>) => import("react/jsx-runtime").JSX.Element;
declare const TooltipTrigger: TooltipPrimitive.Trigger;
interface TooltipPopupProps extends React.ComponentPropsWithoutRef<typeof TooltipPrimitive.Popup> {
    sideOffset?: number;
    align?: "start" | "center" | "end";
    side?: "top" | "bottom" | "left" | "right";
    /** Forwarded to Base UI `Tooltip.Portal` (e.g. `keepMounted`, custom `container`). */
    portalProps?: React.ComponentPropsWithoutRef<typeof TooltipPrimitive.Portal>;
}
declare const TooltipPopup: React.ForwardRefExoticComponent<TooltipPopupProps & React.RefAttributes<HTMLDivElement>>;
export { Tooltip, TooltipTrigger, TooltipPopup, TooltipProvider };
