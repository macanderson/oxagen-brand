import * as React from "react";
import { Dialog as DialogPrimitive } from "@base-ui/react/dialog";
import { type VariantProps } from "class-variance-authority";
declare const Sheet: typeof DialogPrimitive.Root;
declare const SheetTrigger: DialogPrimitive.Trigger;
declare const SheetClose: React.ForwardRefExoticComponent<Omit<import("@base-ui/react").AlertDialogCloseProps, "ref"> & React.RefAttributes<HTMLButtonElement>>;
declare const SheetPortal: React.ForwardRefExoticComponent<Omit<import("@base-ui/react").AlertDialogPortalProps, "ref"> & React.RefAttributes<HTMLDivElement>>;
declare const SheetOverlay: React.ForwardRefExoticComponent<Omit<Omit<import("@base-ui/react").AlertDialogBackdropProps, "ref"> & React.RefAttributes<HTMLDivElement>, "ref"> & React.RefAttributes<HTMLDivElement>>;
declare const sheetVariants: (props?: ({
    side?: "bottom" | "left" | "right" | "top" | null | undefined;
} & import("class-variance-authority/types").ClassProp) | undefined) => string;
interface SheetPopupProps extends React.ComponentPropsWithoutRef<typeof DialogPrimitive.Popup>, VariantProps<typeof sheetVariants> {
    /** Forwarded to Base UI `Dialog.Portal` (e.g. `keepMounted`, custom `container`). */
    portalProps?: React.ComponentPropsWithoutRef<typeof DialogPrimitive.Portal>;
}
declare const SheetPopup: React.ForwardRefExoticComponent<SheetPopupProps & React.RefAttributes<HTMLDivElement>>;
declare const SheetHeader: {
    ({ className, ...props }: React.HTMLAttributes<HTMLDivElement>): import("react/jsx-runtime").JSX.Element;
    displayName: string;
};
/** coss ui body wrapper — sits between `SheetHeader` and `SheetFooter`. */
declare const SheetPanel: {
    ({ className, ...props }: React.HTMLAttributes<HTMLDivElement>): import("react/jsx-runtime").JSX.Element;
    displayName: string;
};
declare const SheetFooter: {
    ({ className, ...props }: React.HTMLAttributes<HTMLDivElement>): import("react/jsx-runtime").JSX.Element;
    displayName: string;
};
declare const SheetTitle: React.ForwardRefExoticComponent<Omit<Omit<import("@base-ui/react").AlertDialogTitleProps, "ref"> & React.RefAttributes<HTMLHeadingElement>, "ref"> & React.RefAttributes<HTMLHeadingElement>>;
declare const SheetDescription: React.ForwardRefExoticComponent<Omit<Omit<import("@base-ui/react").AlertDialogDescriptionProps, "ref"> & React.RefAttributes<HTMLParagraphElement>, "ref"> & React.RefAttributes<HTMLParagraphElement>>;
export { Sheet, SheetPortal, SheetOverlay, SheetTrigger, SheetClose, SheetPopup, SheetHeader, SheetPanel, SheetFooter, SheetTitle, SheetDescription, };
