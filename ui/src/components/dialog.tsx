"use client";
import * as React from "react";
import { Dialog as DialogPrimitive } from "@base-ui/react/dialog";
import { XIcon } from "@phosphor-icons/react";
import { cn } from "../lib/utils";

/**
 * Dialog, after the mockup's dialog recipe (oxagen-roadmap #244).
 *
 * The box drops from the top centre of the page over a blurred scrim. A ruled
 * header holds the title, the description and the close button; the body
 * scrolls on its own; a ruled footer puts the actions on the right. Compose
 * it from `DialogHeader`, `DialogPanel` and `DialogFooter`, which carry the
 * padding, so a row of `TabsList variant="underline"` can sit flush between
 * the header and the body.
 */
const Dialog = DialogPrimitive.Root;
const DialogTrigger = DialogPrimitive.Trigger;
const DialogClose = DialogPrimitive.Close;
const DialogPortal = DialogPrimitive.Portal;

const DialogOverlay = React.forwardRef<
  React.ComponentRef<typeof DialogPrimitive.Backdrop>,
  React.ComponentPropsWithoutRef<typeof DialogPrimitive.Backdrop>
>(({ className, ...props }, ref) => (
  <DialogPrimitive.Backdrop
    ref={ref}
    className={cn(
      // `glass-scrim` hooks the scrim to the glass fallbacks in globals.css:
      // under reduced transparency it keeps its dim and drops its blur.
      "glass-scrim fixed inset-0 z-50 bg-overlay-scrim backdrop-blur-[3px] transition-opacity duration-[var(--motion-overlay)] ease-[var(--ease-entry)] data-[starting-style]:opacity-0 data-[ending-style]:opacity-0",
      className,
    )}
    {...props}
  />
));
DialogOverlay.displayName = "DialogOverlay";

const dialogWidths = {
  default: "max-w-[600px]",
  wide: "max-w-[820px]",
} as const;

interface DialogPopupProps
  extends React.ComponentPropsWithoutRef<typeof DialogPrimitive.Popup> {
  /** `wide` fits a table or a two-column form. */
  size?: keyof typeof dialogWidths;
  /** Forwarded to Base UI `Dialog.Portal` (e.g. `keepMounted`, custom `container`). */
  portalProps?: React.ComponentPropsWithoutRef<typeof DialogPrimitive.Portal>;
}

const DialogPopup = React.forwardRef<
  React.ComponentRef<typeof DialogPrimitive.Popup>,
  DialogPopupProps
>(({ className, children, size = "default", portalProps, ...props }, ref) => (
  <DialogPortal {...portalProps}>
    <DialogOverlay />
    <DialogPrimitive.Popup
      ref={ref}
      data-size={size}
      className={cn(
        // The box sits 70px from the top and never runs past the bottom edge.
        // It clips its own corners; the body scrolls instead, so over-tall
        // content (the Stripe Payment Element, say) stays reachable.
        // w-[calc(100%-2rem)] keeps a floating card on a phone.
        "fixed left-1/2 top-[70px] z-50 flex max-h-[calc(100dvh-86px)] w-[calc(100%-2rem)] -translate-x-1/2 flex-col overflow-hidden rounded-2xl border border-dialog-border bg-dialog-bg text-dialog-fg outline-none",
        "shadow-pop",
        dialogWidths[size],
        "origin-top transition-[opacity,transform,translate,scale] duration-[var(--motion-overlay)] ease-[var(--ease-entry)] data-[starting-style]:opacity-0 data-[starting-style]:scale-[0.98] data-[ending-style]:opacity-0 data-[ending-style]:scale-[0.98]",
        className,
      )}
      {...props}
    >
      {children}
      <DialogPrimitive.Close className="absolute right-3 top-3 inline-flex size-8 cursor-pointer items-center justify-center rounded-lg text-muted-foreground transition-colors outline-none hover:bg-foreground/10 hover:text-foreground focus-visible:outline-2 focus-visible:outline-offset-0 focus-visible:outline-input-ring disabled:pointer-events-none">
        <XIcon className="size-4" aria-hidden />
        <span className="sr-only">Close</span>
      </DialogPrimitive.Close>
    </DialogPrimitive.Popup>
  </DialogPortal>
));
DialogPopup.displayName = "DialogPopup";

/** The ruled top row. It leaves room on the right for the close button. */
const DialogHeader = ({
  className,
  ...props
}: React.HTMLAttributes<HTMLDivElement>) => (
  <div
    className={cn(
      "flex shrink-0 flex-col gap-1 border-b border-dialog-border py-[15px] pr-12 pl-[18px] text-left",
      className,
    )}
    {...props}
  />
);
DialogHeader.displayName = "DialogHeader";

/** coss ui body wrapper. It sits between `DialogHeader` and `DialogFooter` and scrolls. */
const DialogPanel = ({
  className,
  ...props
}: React.HTMLAttributes<HTMLDivElement>) => (
  <div
    className={cn(
      "flex max-h-[62vh] min-h-0 flex-1 flex-col gap-3 overflow-y-auto px-[18px] py-[17px] text-sm",
      className,
    )}
    {...props}
  />
);
DialogPanel.displayName = "DialogPanel";

/** The ruled bottom row. Actions sit on the right, stacked on a phone. */
const DialogFooter = ({
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
DialogFooter.displayName = "DialogFooter";

const DialogTitle = React.forwardRef<
  React.ComponentRef<typeof DialogPrimitive.Title>,
  React.ComponentPropsWithoutRef<typeof DialogPrimitive.Title>
>(({ className, ...props }, ref) => (
  <DialogPrimitive.Title
    ref={ref}
    className={cn("text-base font-semibold leading-snug", className)}
    {...props}
  />
));
DialogTitle.displayName = "DialogTitle";

const DialogDescription = React.forwardRef<
  React.ComponentRef<typeof DialogPrimitive.Description>,
  React.ComponentPropsWithoutRef<typeof DialogPrimitive.Description>
>(({ className, ...props }, ref) => (
  <DialogPrimitive.Description
    ref={ref}
    className={cn("text-sm leading-normal text-muted-foreground", className)}
    {...props}
  />
));
DialogDescription.displayName = "DialogDescription";

export {
  Dialog,
  DialogPortal,
  DialogOverlay,
  DialogTrigger,
  DialogClose,
  DialogPopup,
  DialogHeader,
  DialogPanel,
  DialogFooter,
  DialogTitle,
  DialogDescription,
};
