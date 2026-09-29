"use client";
import * as React from "react";
import { useRender } from "@base-ui/react/use-render";
import { cva, type VariantProps } from "class-variance-authority";
import { cn } from "../lib/utils";

/*
 * The badge follows the mockup's `.b` (section 5): 11px at weight 600 with
 * .02em tracking, 2px by 7px, a 6px corner and a 1px border. A soft variant
 * puts its hue on the ink, 42% of it on the border and 11% behind; critical
 * takes 12%. `quiet` is `.b-q`, `chip` is `.chip` and `label` is the `.lab`
 * pill. The kind badge (`.kb`) is the app's, because its hues are.
 */
const badgeVariants = cva(
  "inline-flex items-center gap-[5px] whitespace-nowrap rounded-md border font-semibold leading-normal tracking-[0.02em] transition-colors focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-ring [&_svg]:size-3 [&_svg]:shrink-0",
  {
    variants: {
      variant: {
        // Default badge: an OUTLINED chip, never a filled/secondary surface.
        // `border-current` keys the outline to the ink (text) color so it
        // reads correctly on both light and dark layouts, and follows any
        // text-color override a caller applies. Never monospace.
        default: "border-current bg-transparent text-foreground",
        secondary:
          "border-transparent bg-secondary text-secondary-foreground hover:bg-secondary/80",
        destructive:
          "border-transparent bg-destructive text-destructive-foreground hover:bg-destructive/80",
        // Alias of default: the outlined ink chip is the default now.
        outline: "border-current bg-transparent text-foreground",
        muted: "border-transparent bg-muted text-muted-foreground",
        // Brand surface badges: paper-tan brand and neutral accent.
        brand: "border-transparent bg-brand text-brand-foreground",
        cyan: "border-transparent bg-secondary text-secondary-foreground",
        // Semantic status variants (--info/--success/--warning/--error tokens).
        info: "border-transparent bg-info text-info-foreground",
        success: "border-transparent bg-success text-success-foreground",
        warning: "border-transparent bg-warning text-warning-foreground",
        error: "border-transparent bg-error text-error-foreground",
        // Soft status variants: the mockup's `.b-<state>`, a status ink on a
        // 42% border and an 11% wash. ToneBadge draws the same pills by state.
        "info-soft": "border-info/42 bg-info/11 text-info",
        "success-soft": "border-success/42 bg-success/11 text-success",
        "warning-soft": "border-warning/42 bg-warning/11 text-warning",
        "error-soft": "border-error/42 bg-error/11 text-error-ink",
        "proven-soft": "border-proven/42 bg-proven/11 text-proven",
        "critical-soft": "border-critical/42 bg-critical/12 text-critical",
        // `.b-q`: the quiet neutral, muted ink on the wash.
        quiet: "border-border bg-hl text-muted-foreground",
        // `.chip`: a neutral tag, body ink at regular weight.
        chip: "border-border bg-hl font-normal tracking-normal text-[var(--body)]",
        // `.lab`: a neutral pill for a label such as a priority or an area.
        label:
          "rounded-full border-border bg-hl font-medium tracking-normal text-[var(--body)]",
      },
      // coss ui adds size variants for density control. `lg` matches the fixed
      // shadcn/ui badge size.
      size: {
        sm: "px-1.5 py-0 text-[10px]",
        default: "px-[7px] py-0.5 text-[11px]",
        lg: "px-2.5 py-0.5 text-xs",
      },
    },
    defaultVariants: { variant: "default", size: "default" },
  },
);

export interface BadgeProps
  extends React.HTMLAttributes<HTMLSpanElement>,
    VariantProps<typeof badgeVariants> {
  /** Render the badge styling onto another element (Base UI `render`). */
  render?: React.ReactElement;
  /** Leading status dot in the badge ink color (pairs with soft variants). */
  dot?: boolean;
}

function Badge({
  className,
  variant,
  size,
  render,
  dot,
  children,
  ...props
}: BadgeProps) {
  return useRender({
    render: render ?? <span />,
    props: {
      className: cn(badgeVariants({ variant, size }), className),
      ...props,
      // Forward children into the rendered element (default <span> or a
      // `render` element), so label content renders in both cases.
      children: dot ? (
        <>
          <span
            aria-hidden="true"
            className="size-[5px] shrink-0 rounded-full bg-current"
          />
          {children}
        </>
      ) : (
        children
      ),
    },
  });
}

export { Badge, badgeVariants };
