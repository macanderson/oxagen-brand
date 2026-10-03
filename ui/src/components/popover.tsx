"use client";
import * as React from "react";
import { Popover as PopoverPrimitive } from "@base-ui/react/popover";
import { cn } from "../lib/utils";
import { popoverSurface } from "./control-styles";

/**
 * coss ui Popover on Base UI Popover, drawn with the kit's one floating
 * surface (oxagen-roadmap #244): the popover fill at 70% over a blur, a faint
 * ring, the deep shadow and a 16px corner.
 *
 *   <Popover>
 *     <PopoverTrigger render={<Button variant="ghost" size="icon" />}>
 *       <HelpCircle />
 *     </PopoverTrigger>
 *     <PopoverPopup>
 *       <PopoverTitle>What is a registry?</PopoverTitle>
 *       <PopoverDescription>A registry holds the agents a workspace can run.</PopoverDescription>
 *     </PopoverPopup>
 *   </Popover>
 *
 * Uses Base UI's `render` prop, not `asChild`. The popup is portalled and
 * positioned, and `side`, `align` and `sideOffset` tune placement. Prose sits
 * 12px by 16px in from the edge: the menu surface's 4px inset plus the 8px by
 * 12px a menu row keeps, so a popover's text lines up with a menu's.
 */
const Popover = PopoverPrimitive.Root;
const PopoverTrigger = PopoverPrimitive.Trigger;
const PopoverClose = PopoverPrimitive.Close;

const PopoverTitle = React.forwardRef<
  React.ComponentRef<typeof PopoverPrimitive.Title>,
  React.ComponentPropsWithoutRef<typeof PopoverPrimitive.Title>
>(({ className, ...props }, ref) => (
  <PopoverPrimitive.Title
    ref={ref}
    className={cn("text-base font-semibold text-foreground", className)}
    {...props}
  />
));
PopoverTitle.displayName = "PopoverTitle";

const PopoverDescription = React.forwardRef<
  React.ComponentRef<typeof PopoverPrimitive.Description>,
  React.ComponentPropsWithoutRef<typeof PopoverPrimitive.Description>
>(({ className, ...props }, ref) => (
  <PopoverPrimitive.Description
    ref={ref}
    className={cn("mt-1 text-base text-muted-foreground", className)}
    {...props}
  />
));
PopoverDescription.displayName = "PopoverDescription";

interface PopoverPopupProps
  extends React.ComponentPropsWithoutRef<typeof PopoverPrimitive.Popup> {
  sideOffset?: number;
  align?: "start" | "center" | "end";
  side?: "top" | "bottom" | "left" | "right";
  /** Forwarded to Base UI `Popover.Portal`. */
  portalProps?: React.ComponentPropsWithoutRef<typeof PopoverPrimitive.Portal>;
}

const PopoverPopup = React.forwardRef<
  React.ComponentRef<typeof PopoverPrimitive.Popup>,
  PopoverPopupProps
>(
  (
    {
      className,
      sideOffset = 8,
      align = "start",
      side = "bottom",
      portalProps,
      ...props
    },
    ref,
  ) => (
    <PopoverPrimitive.Portal {...portalProps}>
      <PopoverPrimitive.Positioner
        sideOffset={sideOffset}
        align={align}
        side={side}
        className="z-50"
      >
        <PopoverPrimitive.Popup
          ref={ref}
          className={cn(
            popoverSurface,
            "z-50 max-w-sm px-4 py-3 text-base outline-none",
            "origin-(--transform-origin) transition-[opacity,transform,translate,scale] duration-[var(--motion-overlay)] ease-[var(--ease-entry)] data-[starting-style]:opacity-0 data-[starting-style]:scale-[0.97] data-[ending-style]:opacity-0 data-[ending-style]:scale-[0.97]",
            className,
          )}
          {...props}
        />
      </PopoverPrimitive.Positioner>
    </PopoverPrimitive.Portal>
  ),
);
PopoverPopup.displayName = "PopoverPopup";

export {
  Popover,
  PopoverTrigger,
  PopoverClose,
  PopoverPopup,
  PopoverTitle,
  PopoverDescription,
};
