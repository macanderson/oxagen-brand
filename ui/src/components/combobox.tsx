"use client";
/**
 * Combobox is a searchable typeahead select built on Base UI's Combobox
 * primitive.
 *
 * Use this instead of Select whenever the option list has more than 20 items
 * (country: 249, US state: 51, industry: 24). The UX rule:
 *   > 20 options → Combobox with typeahead search
 *   ≤ 20 options → plain Select
 *
 * Parts exported, with shadcn names and the coss popup name:
 *   Combobox            the root: value, onValueChange, defaultValue, disabled
 *   ComboboxTrigger     the button that opens it and shows the selected label
 *   ComboboxValue       the selected label, or the placeholder
 *   ComboboxPopup       the floating surface with the search row and the list
 *   ComboboxItem        one option row
 *
 * The popup is the kit's one floating surface (oxagen-roadmap #244), and its
 * rows and checked mark match a menu's and a select's.
 *
 * Usage:
 * ```tsx
 * <Combobox value={country} onValueChange={setCountry}>
 *   <ComboboxTrigger id="country" size="lg" className="w-full">
 *     <ComboboxValue placeholder="Select country" />
 *   </ComboboxTrigger>
 *   <ComboboxPopup searchPlaceholder="Search countries…">
 *     {COUNTRY_OPTIONS.map((o) => (
 *       <ComboboxItem key={o.value} value={o.value}>{o.label}</ComboboxItem>
 *     ))}
 *   </ComboboxPopup>
 * </Combobox>
 * ```
 */
import * as React from "react";
import { Combobox as ComboboxPrimitive } from "@base-ui/react/combobox";
import { cva, type VariantProps } from "class-variance-authority";
import {
  CaretDownIcon,
  CheckIcon,
  MagnifyingGlassIcon,
} from "@phosphor-icons/react";
import { cn } from "../lib/utils";
import { menuItem, menuSeparator, menuSurface } from "./control-styles";

// ── Root ─────────────────────────────────────────────────────────────────────

/**
 * Root combobox context provider.
 * Accepts `value`, `onValueChange`, `defaultValue`, `disabled`, `name`.
 */
function Combobox<V = string>({
  children,
  value,
  onValueChange,
  defaultValue,
  disabled,
  name,
  defaultOpen,
}: {
  children: React.ReactNode;
  value?: V | null;
  onValueChange?: (value: V | null) => void;
  defaultValue?: V | null;
  disabled?: boolean;
  name?: string;
  /** Opens the popup on mount, for a story or a first-run screen. */
  defaultOpen?: boolean;
}) {
  return (
    <ComboboxPrimitive.Root
      value={value}
      onValueChange={onValueChange}
      defaultValue={defaultValue}
      disabled={disabled}
      name={name}
      defaultOpen={defaultOpen}
    >
      {children}
    </ComboboxPrimitive.Root>
  );
}
Combobox.displayName = "Combobox";

// ── Trigger ──────────────────────────────────────────────────────────────────

// Mirrors the Select trigger: a pill on the --input-* tokens, so the field
// reads as a solid field rather than a cut-out that shows the page through.
const comboboxTriggerVariants = cva(
  "flex w-full cursor-pointer items-center justify-between gap-1.5 whitespace-nowrap rounded-4xl border border-input-border bg-input-bg px-3 py-2 text-sm text-input-fg transition-colors outline-none hover:border-input-border-hover focus-visible:border-input-border-focus focus-visible:outline-2 focus-visible:outline-offset-0 focus-visible:outline-input-ring data-[popup-open]:border-input-border-focus disabled:cursor-not-allowed disabled:bg-input-disabled-bg disabled:text-input-disabled-fg [&>span]:line-clamp-1",
  {
    variants: {
      size: {
        sm: "h-7",
        default: "h-8",
        lg: "h-9",
      },
    },
    defaultVariants: { size: "default" },
  },
);

interface ComboboxTriggerProps
  extends Omit<
      React.ComponentPropsWithoutRef<typeof ComboboxPrimitive.Trigger>,
      "size"
    >,
    VariantProps<typeof comboboxTriggerVariants> {}

const ComboboxTrigger = React.forwardRef<
  React.ComponentRef<typeof ComboboxPrimitive.Trigger>,
  ComboboxTriggerProps
>(({ className, size, children, ...props }, ref) => (
  <ComboboxPrimitive.Trigger
    ref={ref}
    className={cn(comboboxTriggerVariants({ size }), className)}
    {...props}
  >
    {children}
    <CaretDownIcon className="pointer-events-none size-4 shrink-0 text-muted-foreground" />
  </ComboboxPrimitive.Trigger>
));
ComboboxTrigger.displayName = "ComboboxTrigger";

// ── Value (selected label display) ───────────────────────────────────────────
// ComboboxValue renders text into the trigger and has no element or ref of
// its own. It takes only `placeholder` from Base UI's API.

function ComboboxValue({ placeholder }: { placeholder?: string }) {
  return <ComboboxPrimitive.Value placeholder={placeholder} />;
}
ComboboxValue.displayName = "ComboboxValue";

// ── Popup ─────────────────────────────────────────────────────────────────────

interface ComboboxPopupProps {
  children: React.ReactNode;
  className?: string;
  searchPlaceholder?: string;
  /** The query the search row starts with, for a story or a deep link. */
  defaultSearchValue?: string;
  sideOffset?: number;
  portalProps?: React.ComponentPropsWithoutRef<typeof ComboboxPrimitive.Portal>;
}

/**
 * Flatten a node tree to its searchable text. Walks nested elements and
 * fragments so an item whose label is wrapped (an icon plus text, a `<span>`,
 * an interpolated number) still matches the query. Reading only the top level
 * would yield "" for those and silently drop them from every non-empty search.
 */
function nodeText(node: React.ReactNode): string {
  if (node == null || typeof node === "boolean") return "";
  if (typeof node === "string") return node;
  if (typeof node === "number") return String(node);
  if (Array.isArray(node)) return node.map(nodeText).join("");
  if (React.isValidElement(node)) {
    const { children } = node.props as { children?: React.ReactNode };
    return nodeText(children);
  }
  return "";
}

function ComboboxPopup({
  children,
  className,
  searchPlaceholder = "Search…",
  defaultSearchValue = "",
  sideOffset = 4,
  portalProps,
}: ComboboxPopupProps) {
  const [searchValue, setSearchValue] = React.useState(defaultSearchValue);
  const inputRef = React.useRef<HTMLInputElement>(null);

  // Filter children on the search value: a case-insensitive substring match
  // against each ComboboxItem's flattened label text. Non-element children
  // (raw strings, separators) are always kept.
  const filteredChildren = React.useMemo(() => {
    if (!searchValue.trim()) return children;

    const query = searchValue.toLowerCase();
    return React.Children.toArray(children).filter((child) => {
      if (!React.isValidElement(child)) return true;
      // React 19 types child.props as unknown, so narrow it first.
      const childProps = child.props as { children?: React.ReactNode };
      return nodeText(childProps.children).toLowerCase().includes(query);
    });
  }, [children, searchValue]);

  // Base UI's `Combobox.Empty` decides emptiness from the root's `items` prop,
  // which this combobox does not pass, so it always thinks the list is empty.
  // Hand it the message only when no option survives the filter.
  const hasOptions = React.Children.toArray(filteredChildren).some((child) =>
    React.isValidElement(child),
  );

  return (
    <ComboboxPrimitive.Portal {...portalProps}>
      <ComboboxPrimitive.Positioner sideOffset={sideOffset} className="z-50">
        <ComboboxPrimitive.Popup
          className={cn(
            menuSurface,
            "z-50 w-(--anchor-width) min-w-[8rem] p-1",
            "origin-(--transform-origin) transition-[opacity,transform,translate,scale] duration-[var(--motion-overlay)] ease-[var(--ease-entry)]",
            "data-[starting-style]:opacity-0 data-[starting-style]:scale-[0.98] data-[starting-style]:-translate-y-1",
            "data-[ending-style]:opacity-0 data-[ending-style]:scale-[0.98] data-[ending-style]:-translate-y-1",
            className,
          )}
        >
          {/* The search row stays put above the list, which scrolls. */}
          <div className="flex items-center gap-2.5 px-3 py-2">
            <MagnifyingGlassIcon className="size-4 shrink-0 text-muted-foreground" />
            <ComboboxPrimitive.Input
              ref={inputRef}
              className="min-w-0 flex-1 bg-transparent text-sm text-foreground outline-none placeholder:text-input-placeholder disabled:cursor-not-allowed disabled:opacity-50"
              placeholder={searchPlaceholder}
              value={searchValue}
              onChange={(e) => setSearchValue(e.currentTarget.value)}
            />
          </div>

          <div role="presentation" className={menuSeparator} />

          {/* The option list scrolls past about 280px. */}
          <ComboboxPrimitive.List className="max-h-[280px] overflow-x-hidden overflow-y-auto">
            {filteredChildren}
          </ComboboxPrimitive.List>
          {/* The live region stays mounted so a screen reader hears the
              message arrive; it takes room only while it holds text. */}
          <ComboboxPrimitive.Empty className="px-3 text-center text-sm text-muted-foreground [&:not(:empty)]:py-6">
            {hasOptions ? null : "No results found."}
          </ComboboxPrimitive.Empty>
        </ComboboxPrimitive.Popup>
      </ComboboxPrimitive.Positioner>
    </ComboboxPrimitive.Portal>
  );
}
ComboboxPopup.displayName = "ComboboxPopup";

// ── Item ──────────────────────────────────────────────────────────────────────

const ComboboxItem = React.forwardRef<
  React.ComponentRef<typeof ComboboxPrimitive.Item>,
  React.ComponentPropsWithoutRef<typeof ComboboxPrimitive.Item>
>(({ className, children, ...props }, ref) => (
  <ComboboxPrimitive.Item
    ref={ref}
    // The menu row, highlighted with the foreground at 10% like every other
    // list in the kit. The checked mark sits at the trailing edge in gold.
    className={cn(menuItem, "relative pr-9", className)}
    {...props}
  >
    {/* Base UI Combobox has no ItemText, so the children are the label. */}
    {children}
    <span className="pointer-events-none absolute right-3 flex size-4 items-center justify-center text-accent-text">
      <ComboboxPrimitive.ItemIndicator>
        <CheckIcon className="size-4" />
      </ComboboxPrimitive.ItemIndicator>
    </span>
  </ComboboxPrimitive.Item>
));
ComboboxItem.displayName = "ComboboxItem";

export {
  Combobox,
  ComboboxTrigger,
  ComboboxValue,
  ComboboxPopup,
  ComboboxItem,
};
