"use client";
import * as React from "react";
import { Select as SelectPrimitive } from "@base-ui/react/select";
import { CaretDownIcon, CaretUpIcon, CheckIcon } from "@phosphor-icons/react";
import { cva, type VariantProps } from "class-variance-authority";
import { cn } from "../lib/utils";

/*
 * Select in shadcn's base-maia look, merged from oxagen apps/app/src/ui/select.tsx
 * at ddb85803. The trigger wears the input tokens in a pill. The popup fills
 * with the menu colour at 70% over a blur, as every floating surface does, and
 * a highlighted option tints with the foreground, as a menu item does. The kit
 * keeps its own API: refs, the `lg` size, `SelectGroup`, `SelectLabel`, and
 * `portalProps`. `SelectContent` is the shadcn name for `SelectPopup`.
 *
 * The app's popup animated with tw-animate classes (`animate-in`, `fade-in-0`,
 * `zoom-in-95`) that nothing defines, so it never animated. This popup uses
 * the Base UI starting and ending styles every other kit overlay uses.
 */
// `control-styles.ts` exports a `menuSurface` that clips its overflow. This
// popup scrolls, so it keeps its own copy without the clip.
const menuSurface =
  "relative isolate rounded-2xl bg-menu-popup-bg/70 text-menu-popup-fg shadow-2xl ring-1 ring-foreground/5 outline-none dark:ring-foreground/10 before:pointer-events-none before:absolute before:inset-0 before:-z-1 before:rounded-[inherit] before:backdrop-blur-2xl before:backdrop-saturate-150";

const Select = SelectPrimitive.Root;
const SelectGroup = SelectPrimitive.Group;

const SelectValue = React.forwardRef<
  React.ComponentRef<typeof SelectPrimitive.Value>,
  React.ComponentPropsWithoutRef<typeof SelectPrimitive.Value>
>(({ className, ...props }, ref) => (
  <SelectPrimitive.Value
    ref={ref}
    data-slot="select-value"
    className={cn("flex flex-1 text-left", className)}
    {...props}
  />
));
SelectValue.displayName = "SelectValue";

const selectTriggerVariants = cva(
  "flex w-fit cursor-pointer items-center justify-between gap-1.5 rounded-4xl border border-input-border bg-input-bg px-3 py-2 text-sm whitespace-nowrap text-input-fg transition-colors outline-none hover:border-input-border-hover focus-visible:border-input-border-focus focus-visible:outline-2 focus-visible:outline-offset-0 focus-visible:outline-input-ring data-[popup-open]:border-input-border-focus disabled:cursor-not-allowed disabled:opacity-50 aria-invalid:border-input-invalid-border data-placeholder:text-input-placeholder *:data-[slot=select-value]:line-clamp-1 *:data-[slot=select-value]:flex *:data-[slot=select-value]:items-center *:data-[slot=select-value]:gap-1.5 [&_svg]:pointer-events-none [&_svg]:shrink-0 [&_svg:not([class*='size-'])]:size-4",
  {
    variants: {
      size: {
        sm: "h-8",
        default: "h-9",
        lg: "h-10",
      },
    },
    defaultVariants: { size: "default" },
  },
);

interface SelectTriggerProps
  extends Omit<
      React.ComponentPropsWithoutRef<typeof SelectPrimitive.Trigger>,
      "size"
    >,
    VariantProps<typeof selectTriggerVariants> {}

const SelectTrigger = React.forwardRef<
  React.ComponentRef<typeof SelectPrimitive.Trigger>,
  SelectTriggerProps
>(({ className, size, children, ...props }, ref) => (
  <SelectPrimitive.Trigger
    ref={ref}
    data-slot="select-trigger"
    data-size={size ?? "default"}
    className={cn(selectTriggerVariants({ size }), className)}
    {...props}
  >
    {children}
    <SelectPrimitive.Icon
      render={
        <CaretDownIcon className="pointer-events-none size-4 text-muted-foreground" />
      }
    />
  </SelectPrimitive.Trigger>
));
SelectTrigger.displayName = "SelectTrigger";

interface SelectPopupProps
  extends React.ComponentPropsWithoutRef<typeof SelectPrimitive.Popup>,
    Pick<
      React.ComponentPropsWithoutRef<typeof SelectPrimitive.Positioner>,
      "align" | "alignOffset" | "side" | "sideOffset" | "alignItemWithTrigger"
    > {
  /** Forwarded to Base UI `Select.Portal` (e.g. `keepMounted`, custom `container`). */
  portalProps?: React.ComponentPropsWithoutRef<typeof SelectPrimitive.Portal>;
}

const SelectPopup = React.forwardRef<
  React.ComponentRef<typeof SelectPrimitive.Popup>,
  SelectPopupProps
>(
  (
    {
      className,
      children,
      side = "bottom",
      sideOffset = 4,
      align = "center",
      alignOffset = 0,
      alignItemWithTrigger = true,
      portalProps,
      ...props
    },
    ref,
  ) => (
    <SelectPrimitive.Portal {...portalProps}>
      <SelectPrimitive.Positioner
        side={side}
        sideOffset={sideOffset}
        align={align}
        alignOffset={alignOffset}
        alignItemWithTrigger={alignItemWithTrigger}
        className="isolate z-50"
      >
        <SelectPrimitive.Popup
          ref={ref}
          data-slot="select-content"
          data-align-trigger={alignItemWithTrigger}
          className={cn(
            menuSurface,
            "z-50 max-h-(--available-height) w-(--anchor-width) min-w-36 origin-(--transform-origin) overflow-x-hidden overflow-y-auto p-1",
            // Fade in place when the popup sits over the trigger, and grow
            // from the trigger when it drops below it.
            "transition-[opacity,scale,translate] duration-[var(--motion-overlay)] ease-[var(--ease-entry)] data-[starting-style]:opacity-0 data-[ending-style]:opacity-0 data-[align-trigger=false]:data-[starting-style]:scale-[0.98] data-[align-trigger=false]:data-[starting-style]:-translate-y-1 data-[align-trigger=false]:data-[ending-style]:scale-[0.98]",
            className,
          )}
          {...props}
        >
          <SelectPrimitive.ScrollUpArrow className="top-0 z-10 flex w-full cursor-default items-center justify-center py-1">
            <CaretUpIcon className="size-4" />
          </SelectPrimitive.ScrollUpArrow>
          <SelectPrimitive.List>{children}</SelectPrimitive.List>
          <SelectPrimitive.ScrollDownArrow className="bottom-0 z-10 flex w-full cursor-default items-center justify-center py-1">
            <CaretDownIcon className="size-4" />
          </SelectPrimitive.ScrollDownArrow>
        </SelectPrimitive.Popup>
      </SelectPrimitive.Positioner>
    </SelectPrimitive.Portal>
  ),
);
SelectPopup.displayName = "SelectPopup";

/** The shadcn name for `SelectPopup`. */
const SelectContent = SelectPopup;

const SelectLabel = React.forwardRef<
  React.ComponentRef<typeof SelectPrimitive.GroupLabel>,
  React.ComponentPropsWithoutRef<typeof SelectPrimitive.GroupLabel>
>(({ className, ...props }, ref) => (
  <SelectPrimitive.GroupLabel
    ref={ref}
    data-slot="select-label"
    className={cn(
      "px-3 py-1.5 text-xs font-medium text-menu-group-label-fg",
      className,
    )}
    {...props}
  />
));
SelectLabel.displayName = "SelectLabel";

const SelectItem = React.forwardRef<
  React.ComponentRef<typeof SelectPrimitive.Item>,
  React.ComponentPropsWithoutRef<typeof SelectPrimitive.Item>
>(({ className, children, ...props }, ref) => (
  <SelectPrimitive.Item
    ref={ref}
    data-slot="select-item"
    className={cn(
      "relative flex w-full cursor-pointer items-center gap-2.5 rounded-xl py-2 pr-8 pl-3 text-sm text-menu-item-fg outline-hidden select-none data-[highlighted]:bg-foreground/10 data-[disabled]:pointer-events-none data-[disabled]:opacity-50 [&_svg]:pointer-events-none [&_svg]:shrink-0 [&_svg:not([class*='size-'])]:size-4",
      className,
    )}
    {...props}
  >
    <SelectPrimitive.ItemText className="flex flex-1 shrink-0 gap-2 whitespace-nowrap">
      {children}
    </SelectPrimitive.ItemText>
    <SelectPrimitive.ItemIndicator
      render={
        <span className="pointer-events-none absolute right-2 flex size-4 items-center justify-center" />
      }
    >
      <CheckIcon className="pointer-events-none" />
    </SelectPrimitive.ItemIndicator>
  </SelectPrimitive.Item>
));
SelectItem.displayName = "SelectItem";

export {
  Select,
  SelectContent,
  SelectGroup,
  SelectItem,
  SelectLabel,
  SelectPopup,
  SelectTrigger,
  SelectValue,
};
