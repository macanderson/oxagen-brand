"use client";
import * as React from "react";
import { Dialog as DialogPrimitive } from "@base-ui/react/dialog";
import { cva, type VariantProps } from "class-variance-authority";
import { XIcon } from "@phosphor-icons/react";
import { cn } from "../lib/utils";

/**
 * Sheet, after the mockup's drawer recipe (oxagen-roadmap #244).
 *
 * The drawer slides in from an edge, up to 580px wide, with a rule on its
 * inner edge. A ruled header holds the title and the close button, and the
 * body scrolls with room at the end so the last row clears the edge. The
 * ground, border and shadow match `DialogPopup`.
 */

const Sheet = DialogPrimitive.Root;
const SheetTrigger = DialogPrimitive.Trigger;
const SheetClose = DialogPrimitive.Close;
const SheetPortal = DialogPrimitive.Portal;

const SheetOverlay = React.forwardRef<
  React.ComponentRef<typeof DialogPrimitive.Backdrop>,
  React.ComponentPropsWithoutRef<typeof DialogPrimitive.Backdrop>
>(({ className, ...props }, ref) => (
  <DialogPrimitive.Backdrop
    ref={ref}
    className={cn(
      // The token scrim that DialogOverlay uses, never a raw palette colour.
      "fixed inset-0 z-50 bg-overlay-scrim transition-opacity duration-300 ease-[var(--ease-entry)] data-[starting-style]:opacity-0 data-[ending-style]:opacity-0",
      className,
    )}
    {...props}
  />
));
SheetOverlay.displayName = "SheetOverlay";

const sheetVariants = cva(
  "fixed z-50 flex flex-col border-dialog-border bg-dialog-bg text-dialog-fg outline-none shadow-pop transition ease-[var(--ease-entry)] duration-300 data-[ending-style]:duration-200",
  {
    variants: {
      side: {
        top: "inset-x-0 top-0 max-h-[85dvh] border-b data-[starting-style]:-translate-y-full data-[ending-style]:-translate-y-full",
        bottom:
          "inset-x-0 bottom-0 max-h-[85dvh] border-t data-[starting-style]:translate-y-full data-[ending-style]:translate-y-full",
        left: "inset-y-0 left-0 h-full w-[min(580px,100%)] border-r data-[starting-style]:-translate-x-full data-[ending-style]:-translate-x-full",
        right:
          "inset-y-0 right-0 h-full w-[min(580px,100%)] border-l data-[starting-style]:translate-x-full data-[ending-style]:translate-x-full",
      },
    },
    defaultVariants: { side: "right" },
  },
);

interface SheetPopupProps
  extends React.ComponentPropsWithoutRef<typeof DialogPrimitive.Popup>,
    VariantProps<typeof sheetVariants> {
  /** Forwarded to Base UI `Dialog.Portal` (e.g. `keepMounted`, custom `container`). */
  portalProps?: React.ComponentPropsWithoutRef<typeof DialogPrimitive.Portal>;
}

const SheetPopup = React.forwardRef<
  React.ComponentRef<typeof DialogPrimitive.Popup>,
  SheetPopupProps
>(({ side = "right", className, children, portalProps, ...props }, ref) => (
  <SheetPortal {...portalProps}>
    <SheetOverlay />
    <DialogPrimitive.Popup
      ref={ref}
      className={cn(sheetVariants({ side }), className)}
      {...props}
    >
      {children}
      <DialogPrimitive.Close className="absolute right-3 top-3 inline-flex size-8 cursor-pointer items-center justify-center rounded-lg text-muted-foreground transition-colors outline-none hover:bg-foreground/10 hover:text-foreground focus-visible:outline-2 focus-visible:outline-offset-0 focus-visible:outline-input-ring disabled:pointer-events-none">
        <XIcon className="size-4" aria-hidden />
        <span className="sr-only">Close</span>
      </DialogPrimitive.Close>
    </DialogPrimitive.Popup>
  </SheetPortal>
));
SheetPopup.displayName = "SheetPopup";

/** The ruled top row. It leaves room on the right for the close button. */
const SheetHeader = ({
  className,
  ...props
}: React.HTMLAttributes<HTMLDivElement>) => (
  <div
    className={cn(
      "flex shrink-0 flex-col gap-1 border-b border-dialog-border py-[14px] pr-12 pl-[18px] text-left",
      className,
    )}
    {...props}
  />
);
SheetHeader.displayName = "SheetHeader";

/**
 * coss ui body wrapper. It sits between `SheetHeader` and `SheetFooter`,
 * scrolls, and ends with 48px of room.
 */
const SheetPanel = ({
  className,
  ...props
}: React.HTMLAttributes<HTMLDivElement>) => (
  <div
    className={cn(
      "flex min-h-0 flex-1 flex-col gap-3 overflow-y-auto px-[18px] pt-4 pb-12 text-sm",
      className,
    )}
    {...props}
  />
);
SheetPanel.displayName = "SheetPanel";

/** The ruled bottom row, as in `DialogFooter`. */
const SheetFooter = ({
  className,
  ...props
}: React.HTMLAttributes<HTMLDivElement>) => (
  <div
    className={cn(
      "flex shrink-0 flex-col-reverse gap-[9px] border-t border-dialog-border px-[18px] py-[13px] sm:flex-row sm:items-center sm:justify-end",
      className,
    )}
    {...props}
  />
);
SheetFooter.displayName = "SheetFooter";

const SheetTitle = React.forwardRef<
  React.ComponentRef<typeof DialogPrimitive.Title>,
  React.ComponentPropsWithoutRef<typeof DialogPrimitive.Title>
>(({ className, ...props }, ref) => (
  <DialogPrimitive.Title
    ref={ref}
    className={cn("text-(length:--ox-a-h4) font-semibold leading-snug", className)}
    {...props}
  />
));
SheetTitle.displayName = "SheetTitle";

const SheetDescription = React.forwardRef<
  React.ComponentRef<typeof DialogPrimitive.Description>,
  React.ComponentPropsWithoutRef<typeof DialogPrimitive.Description>
>(({ className, ...props }, ref) => (
  <DialogPrimitive.Description
    ref={ref}
    className={cn("text-sm leading-normal text-muted-foreground", className)}
    {...props}
  />
));
SheetDescription.displayName = "SheetDescription";

export {
  Sheet,
  SheetPortal,
  SheetOverlay,
  SheetTrigger,
  SheetClose,
  SheetPopup,
  SheetHeader,
  SheetPanel,
  SheetFooter,
  SheetTitle,
  SheetDescription,
};
