import * as React from "react";
import { Menu as MenuPrimitive } from "@base-ui/react/menu";
/**
 * Menu — coss ui menu built on Base UI `Menu` (replaces the shadcn/Radix-era
 * `DropdownMenu`).
 *
 *   <Menu>
 *     <MenuTrigger render={<Button variant="ghost" />}>Open</MenuTrigger>
 *     <MenuPopup>
 *       <MenuItem onClick={...}>Item</MenuItem>
 *     </MenuPopup>
 *   </Menu>
 *
 * Composition uses Base UI's `render` prop (not `asChild`); items use the
 * native `onClick` (not `onSelect`). Base UI closes the menu on click.
 */
declare const Menu: <Payload>(props: MenuPrimitive.Root.Props<Payload>) => import("react/jsx-runtime").JSX.Element;
declare const MenuGroup: React.ForwardRefExoticComponent<Omit<import("@base-ui/react").ContextMenuGroupProps, "ref"> & React.RefAttributes<HTMLDivElement>>;
declare const MenuPortal: React.ForwardRefExoticComponent<Omit<import("@base-ui/react").ContextMenuPortalProps, "ref"> & React.RefAttributes<HTMLDivElement>>;
declare const MenuRadioGroup: React.NamedExoticComponent<Omit<import("@base-ui/react").ContextMenuRadioGroupProps, "ref"> & React.RefAttributes<HTMLDivElement>>;
declare const MenuSub: typeof MenuPrimitive.SubmenuRoot;
declare const MenuTrigger: MenuPrimitive.Trigger;
interface MenuPopupProps extends React.ComponentPropsWithoutRef<typeof MenuPrimitive.Popup> {
    sideOffset?: number;
    align?: "start" | "center" | "end";
    side?: "top" | "bottom" | "left" | "right";
    /** Forwarded to Base UI `Menu.Portal` (e.g. `keepMounted`, custom `container`). */
    portalProps?: React.ComponentPropsWithoutRef<typeof MenuPrimitive.Portal>;
}
declare const MenuPopup: React.ForwardRefExoticComponent<MenuPopupProps & React.RefAttributes<HTMLDivElement>>;
interface MenuItemProps extends React.ComponentPropsWithoutRef<typeof MenuPrimitive.Item> {
    inset?: boolean;
    /** `destructive` inks the item with the error token (delete/remove actions). */
    variant?: "default" | "destructive";
}
declare const MenuItem: React.ForwardRefExoticComponent<MenuItemProps & React.RefAttributes<HTMLElement>>;
declare const MenuCheckboxItem: React.ForwardRefExoticComponent<Omit<Omit<import("@base-ui/react").ContextMenuCheckboxItemProps, "ref"> & React.RefAttributes<HTMLElement>, "ref"> & React.RefAttributes<HTMLElement>>;
declare const MenuRadioItem: React.ForwardRefExoticComponent<Omit<Omit<import("@base-ui/react").ContextMenuRadioItemProps, "ref"> & React.RefAttributes<HTMLElement>, "ref"> & React.RefAttributes<HTMLElement>>;
/**
 * MenuGroupLabel — standalone, non-interactive label inside a menu popup. This
 * is the coss equivalent of shadcn's `DropdownMenuLabel` (a plain styled `div`),
 * NOT Base UI's `Menu.GroupLabel` — the latter throws "MenuGroupContext is
 * missing" unless wrapped in a `<Menu.Group>`/`<Menu.RadioGroup>`. Use this for
 * headers and section titles that aren't bound to a specific group. If you need
 * a label that's ARIA-associated with a group, render it inside `<MenuGroup>`;
 * the styling still applies.
 */
declare const MenuGroupLabel: React.ForwardRefExoticComponent<React.HTMLAttributes<HTMLDivElement> & {
    inset?: boolean;
} & React.RefAttributes<HTMLDivElement>>;
declare const MenuSeparator: React.ForwardRefExoticComponent<Omit<Omit<import("@base-ui/react").SeparatorProps, "ref"> & React.RefAttributes<HTMLDivElement>, "ref"> & React.RefAttributes<HTMLDivElement>>;
declare function MenuShortcut({ className, ...props }: React.HTMLAttributes<HTMLSpanElement>): import("react/jsx-runtime").JSX.Element;
declare namespace MenuShortcut {
    var displayName: string;
}
declare const MenuSubTrigger: React.ForwardRefExoticComponent<Omit<Omit<import("@base-ui/react").ContextMenuSubmenuTriggerProps, "ref"> & React.RefAttributes<HTMLElement>, "ref"> & {
    inset?: boolean;
} & React.RefAttributes<HTMLElement>>;
declare const MenuSubPopup: React.ForwardRefExoticComponent<MenuPopupProps & React.RefAttributes<HTMLDivElement>>;
export { Menu, MenuTrigger, MenuPopup, MenuItem, MenuCheckboxItem, MenuRadioGroup, MenuRadioItem, MenuGroupLabel, MenuSeparator, MenuShortcut, MenuGroup, MenuPortal, MenuSub, MenuSubTrigger, MenuSubPopup, };
