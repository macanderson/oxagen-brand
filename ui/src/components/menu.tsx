"use client";
import * as React from "react";
import { Menu as MenuPrimitive } from "@base-ui/react/menu";
import { CaretRightIcon, CheckIcon } from "@phosphor-icons/react";
import { cn } from "../lib/utils";
import {
  menuItem,
  menuLabel,
  menuPopup,
  menuSeparator,
} from "./control-styles";

/**
 * Menu is the coss ui menu built on Base UI `Menu`. It replaces the
 * shadcn and Radix `DropdownMenu`.
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
 *
 * The popup and its rows are the shared recipes in `control-styles.ts`
 * (`menuPopup`, `menuItem`, `menuLabel`, `menuSeparator`), so a menu, a
 * select and the command menu draw one translucent surface. A checked row
 * shows its mark at the trailing edge in gold as ink, as the mockup's
 * current row does.
 */
const Menu = MenuPrimitive.Root;
const MenuGroup = MenuPrimitive.Group;
const MenuPortal = MenuPrimitive.Portal;
const MenuRadioGroup = MenuPrimitive.RadioGroup;
const MenuSub = MenuPrimitive.SubmenuRoot;
const MenuTrigger = MenuPrimitive.Trigger;

/** Base UI starting and ending styles: a short fade and lift from the anchor. */
const popupMotion =
  "origin-(--transform-origin) transition-[opacity,transform,translate,scale] duration-[var(--motion-overlay)] ease-[var(--ease-entry)] data-[starting-style]:opacity-0 data-[starting-style]:scale-[0.98] data-[starting-style]:-translate-y-1 data-[ending-style]:opacity-0 data-[ending-style]:scale-[0.98] data-[ending-style]:-translate-y-1";

/** Lines a label up with rows that lead with a 16px glyph: 12px, the glyph, and the 10px gap. */
const insetPad = "pl-9.5";

/** Room at the trailing edge for a checked row's mark. */
const checkRow = "relative pr-9";
const checkSlot =
  "pointer-events-none absolute right-3 flex size-4 items-center justify-center text-accent-text";

interface MenuPopupProps
  extends React.ComponentPropsWithoutRef<typeof MenuPrimitive.Popup> {
  sideOffset?: number;
  align?: "start" | "center" | "end";
  side?: "top" | "bottom" | "left" | "right";
  /** Forwarded to Base UI `Menu.Portal` (e.g. `keepMounted`, custom `container`). */
  portalProps?: React.ComponentPropsWithoutRef<typeof MenuPrimitive.Portal>;
}

const MenuPopup = React.forwardRef<
  React.ComponentRef<typeof MenuPrimitive.Popup>,
  MenuPopupProps
>(
  (
    { className, sideOffset = 4, align = "start", side, portalProps, ...props },
    ref,
  ) => (
    <MenuPrimitive.Portal {...portalProps}>
      <MenuPrimitive.Positioner
        sideOffset={sideOffset}
        align={align}
        side={side}
        className="z-50"
      >
        <MenuPrimitive.Popup
          ref={ref}
          className={cn(
            menuPopup,
            "z-50 max-h-(--available-height) min-w-[8rem] overflow-y-auto",
            popupMotion,
            className,
          )}
          {...props}
        />
      </MenuPrimitive.Positioner>
    </MenuPrimitive.Portal>
  ),
);
MenuPopup.displayName = "MenuPopup";

interface MenuItemProps
  extends React.ComponentPropsWithoutRef<typeof MenuPrimitive.Item> {
  inset?: boolean;
  /** `destructive` inks the item with the error token (delete/remove actions). */
  variant?: "default" | "destructive";
}

const MenuItem = React.forwardRef<
  React.ComponentRef<typeof MenuPrimitive.Item>,
  MenuItemProps
>(({ className, inset, variant = "default", ...props }, ref) => (
  <MenuPrimitive.Item
    ref={ref}
    className={cn(
      menuItem,
      "relative transition-colors",
      variant === "destructive" &&
        "text-error data-[highlighted]:bg-error/10 data-[highlighted]:text-error [&_svg]:text-error",
      inset && insetPad,
      className,
    )}
    {...props}
  />
));
MenuItem.displayName = "MenuItem";

const MenuCheckboxItem = React.forwardRef<
  React.ComponentRef<typeof MenuPrimitive.CheckboxItem>,
  React.ComponentPropsWithoutRef<typeof MenuPrimitive.CheckboxItem>
>(({ className, children, ...props }, ref) => (
  <MenuPrimitive.CheckboxItem
    ref={ref}
    className={cn(menuItem, checkRow, "transition-colors", className)}
    {...props}
  >
    {children}
    <span className={checkSlot}>
      <MenuPrimitive.CheckboxItemIndicator>
        <CheckIcon className="size-4" />
      </MenuPrimitive.CheckboxItemIndicator>
    </span>
  </MenuPrimitive.CheckboxItem>
));
MenuCheckboxItem.displayName = "MenuCheckboxItem";

const MenuRadioItem = React.forwardRef<
  React.ComponentRef<typeof MenuPrimitive.RadioItem>,
  React.ComponentPropsWithoutRef<typeof MenuPrimitive.RadioItem>
>(({ className, children, ...props }, ref) => (
  <MenuPrimitive.RadioItem
    ref={ref}
    className={cn(menuItem, checkRow, "transition-colors", className)}
    {...props}
  >
    {children}
    <span className={checkSlot}>
      <MenuPrimitive.RadioItemIndicator>
        <span className="block size-2 rounded-full bg-current" />
      </MenuPrimitive.RadioItemIndicator>
    </span>
  </MenuPrimitive.RadioItem>
));
MenuRadioItem.displayName = "MenuRadioItem";

/**
 * MenuGroupLabel is a standalone label inside a menu popup that takes no
 * input. It matches shadcn's `DropdownMenuLabel`, a plain styled `div`. It is
 * not Base UI's `Menu.GroupLabel`, which throws "MenuGroupContext is missing"
 * outside a `<Menu.Group>` or `<Menu.RadioGroup>`. Use it for headers and
 * section titles that belong to no group. To tie a label to a group for
 * assistive tech, render it inside `<MenuGroup>`; the styling still applies.
 */
const MenuGroupLabel = React.forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement> & { inset?: boolean }
>(({ className, inset, ...props }, ref) => (
  <div
    ref={ref}
    role="presentation"
    className={cn(menuLabel, inset && insetPad, className)}
    {...props}
  />
));
MenuGroupLabel.displayName = "MenuGroupLabel";

const MenuSeparator = React.forwardRef<
  React.ComponentRef<typeof MenuPrimitive.Separator>,
  React.ComponentPropsWithoutRef<typeof MenuPrimitive.Separator>
>(({ className, ...props }, ref) => (
  <MenuPrimitive.Separator
    ref={ref}
    className={cn(menuSeparator, className)}
    {...props}
  />
));
MenuSeparator.displayName = "MenuSeparator";

function MenuShortcut({
  className,
  ...props
}: React.HTMLAttributes<HTMLSpanElement>) {
  return (
    <span
      className={cn("ml-auto text-xs tracking-widest opacity-60", className)}
      {...props}
    />
  );
}
MenuShortcut.displayName = "MenuShortcut";

const MenuSubTrigger = React.forwardRef<
  React.ComponentRef<typeof MenuPrimitive.SubmenuTrigger>,
  React.ComponentPropsWithoutRef<typeof MenuPrimitive.SubmenuTrigger> & {
    inset?: boolean;
  }
>(({ className, inset, children, ...props }, ref) => (
  <MenuPrimitive.SubmenuTrigger
    ref={ref}
    className={cn(
      menuItem,
      "data-[popup-open]:bg-foreground/10",
      inset && insetPad,
      className,
    )}
    {...props}
  >
    {children}
    <CaretRightIcon className="ml-auto size-3.5 text-muted-foreground" />
  </MenuPrimitive.SubmenuTrigger>
));
MenuSubTrigger.displayName = "MenuSubTrigger";

const MenuSubPopup = React.forwardRef<
  React.ComponentRef<typeof MenuPrimitive.Popup>,
  MenuPopupProps
>(
  (
    { className, sideOffset = 0, align = "start", side, portalProps, ...props },
    ref,
  ) => (
    <MenuPrimitive.Portal {...portalProps}>
      <MenuPrimitive.Positioner
        sideOffset={sideOffset}
        align={align}
        // Lift the submenu by the popup's 4px inset so its first row sits
        // level with the row that opened it.
        alignOffset={-4}
        side={side}
        className="z-50"
      >
        <MenuPrimitive.Popup
          ref={ref}
          className={cn(
            menuPopup,
            "z-50 max-h-(--available-height) min-w-[8rem] overflow-y-auto",
            popupMotion,
            className,
          )}
          {...props}
        />
      </MenuPrimitive.Positioner>
    </MenuPrimitive.Portal>
  ),
);
MenuSubPopup.displayName = "MenuSubPopup";

export {
  Menu,
  MenuTrigger,
  MenuPopup,
  MenuItem,
  MenuCheckboxItem,
  MenuRadioGroup,
  MenuRadioItem,
  MenuGroupLabel,
  MenuSeparator,
  MenuShortcut,
  MenuGroup,
  MenuPortal,
  MenuSub,
  MenuSubTrigger,
  MenuSubPopup,
};
