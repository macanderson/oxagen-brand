import * as React from "react";
import { Dialog as DialogPrimitive } from "@base-ui/react/dialog";
declare const Dialog: typeof DialogPrimitive.Root;
declare const DialogTrigger: DialogPrimitive.Trigger;
declare const DialogClose: React.ForwardRefExoticComponent<Omit<import("@base-ui/react").AlertDialogCloseProps, "ref"> & React.RefAttributes<HTMLButtonElement>>;
declare const DialogPortal: React.ForwardRefExoticComponent<Omit<import("@base-ui/react").AlertDialogPortalProps, "ref"> & React.RefAttributes<HTMLDivElement>>;
declare const DialogOverlay: React.ForwardRefExoticComponent<Omit<Omit<import("@base-ui/react").AlertDialogBackdropProps, "ref"> & React.RefAttributes<HTMLDivElement>, "ref"> & React.RefAttributes<HTMLDivElement>>;
interface DialogPopupProps extends React.ComponentPropsWithoutRef<typeof DialogPrimitive.Popup> {
    /** Forwarded to Base UI `Dialog.Portal` (e.g. `keepMounted`, custom `container`). */
    portalProps?: React.ComponentPropsWithoutRef<typeof DialogPrimitive.Portal>;
}
declare const DialogPopup: React.ForwardRefExoticComponent<DialogPopupProps & React.RefAttributes<HTMLDivElement>>;
declare const DialogHeader: {
    ({ className, ...props }: React.HTMLAttributes<HTMLDivElement>): import("react/jsx-runtime").JSX.Element;
    displayName: string;
};
/** coss ui body wrapper — sits between `DialogHeader` and `DialogFooter`. */
declare const DialogPanel: {
    ({ className, ...props }: React.HTMLAttributes<HTMLDivElement>): import("react/jsx-runtime").JSX.Element;
    displayName: string;
};
declare const DialogFooter: {
    ({ className, ...props }: React.HTMLAttributes<HTMLDivElement>): import("react/jsx-runtime").JSX.Element;
    displayName: string;
};
declare const DialogTitle: React.ForwardRefExoticComponent<Omit<Omit<import("@base-ui/react").AlertDialogTitleProps, "ref"> & React.RefAttributes<HTMLHeadingElement>, "ref"> & React.RefAttributes<HTMLHeadingElement>>;
declare const DialogDescription: React.ForwardRefExoticComponent<Omit<Omit<import("@base-ui/react").AlertDialogDescriptionProps, "ref"> & React.RefAttributes<HTMLParagraphElement>, "ref"> & React.RefAttributes<HTMLParagraphElement>>;
export { Dialog, DialogPortal, DialogOverlay, DialogTrigger, DialogClose, DialogPopup, DialogHeader, DialogPanel, DialogFooter, DialogTitle, DialogDescription, };
