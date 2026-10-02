"use client";
import * as React from "react";
import { useRender } from "@base-ui/react/use-render";
import { cva, type VariantProps } from "class-variance-authority";
import { cn } from "../lib/utils";
import { Spinner } from "./spinner";
import { Tooltip, TooltipTrigger, TooltipPopup } from "./tooltip";

/*
 * Button is the maia pill: every size is fully rounded (rounded-4xl) and the
 * default height is 36px (h-9). Colour, border, ring and disabled states all
 * resolve through the --button-* tokens (see THEME.md section 5), so the v3
 * layer makes the primary gold without this file naming a palette colour.
 * Hover feedback is the token colour shift. The transform reads
 * --button-hover-scale, which the current skin pins at 1.
 *
 * The variant map is public API. `default`, `primary` and `gradient` are the
 * solid primary. `secondary`, `outline` and `ghost` are neutral. The two
 * `destructive` variants use the error token, and `link` is text only.
 *
 * Sizes carry no radius of their own, so the pill in the base class holds at
 * every size.
 */
const buttonVariants = cva(
  "inline-flex items-center justify-center gap-2 whitespace-nowrap rounded-4xl text-sm font-medium transition-[color,background-color,border-color,transform] duration-[var(--motion-micro)] ease-[var(--ease-hover)] hover:scale-[var(--button-hover-scale)] active:scale-100 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-offset-0 disabled:pointer-events-none disabled:hover:scale-100 [&_svg]:pointer-events-none [&_svg]:size-4 [&_svg]:shrink-0",
  {
    variants: {
      variant: {
        // Solid primary. The v3 layer points these tokens at --gold.
        primary:
          "border border-button-primary-border bg-button-primary-bg text-button-primary-fg hover:bg-button-primary-hover-bg active:bg-button-primary-active-bg focus-visible:ring-button-primary-ring disabled:border-transparent disabled:bg-button-disabled-bg disabled:text-button-disabled-fg",
        default:
          "border border-button-primary-border bg-button-primary-bg text-button-primary-fg hover:bg-button-primary-hover-bg active:bg-button-primary-active-bg focus-visible:ring-button-primary-ring disabled:border-transparent disabled:bg-button-disabled-bg disabled:text-button-disabled-fg",
        // Neutral filled: the secondary surface with the default border, hover and ring.
        secondary:
          "border border-button-default-border bg-secondary text-secondary-foreground hover:bg-button-default-hover-bg active:bg-button-default-active-bg focus-visible:ring-button-default-ring disabled:bg-button-disabled-bg disabled:text-button-disabled-fg",
        // Neutral outline on the --button-default-bg panel.
        outline:
          "border border-button-default-border bg-button-default-bg text-button-default-fg hover:bg-button-default-hover-bg active:bg-button-default-active-bg focus-visible:ring-button-default-ring disabled:text-button-disabled-fg",
        ghost:
          "text-button-default-fg hover:bg-button-default-hover-bg active:bg-button-default-active-bg focus-visible:ring-button-default-ring disabled:text-button-disabled-fg",
        destructive:
          "bg-error text-error-foreground hover:bg-error/90 active:bg-error/80 focus-visible:ring-error disabled:bg-button-disabled-bg disabled:text-button-disabled-fg",
        // The error colour on an outline, for a destructive action that should not shout.
        "destructive-outline":
          "border border-error/50 bg-background text-error-ink hover:bg-error/10 focus-visible:ring-error disabled:text-button-disabled-fg",
        link: "text-foreground underline-offset-4 hover:underline hover:scale-100 focus-visible:ring-button-default-ring disabled:text-button-disabled-fg",
        // An alias of `primary`. It renders the same flat fill with no gradient.
        gradient:
          "border border-button-primary-border bg-button-primary-bg text-button-primary-fg hover:bg-button-primary-hover-bg active:bg-button-primary-active-bg focus-visible:ring-button-primary-ring disabled:border-transparent disabled:bg-button-disabled-bg disabled:text-button-disabled-fg",
      },
      // The maia scale: default is 36px, and each step moves 4px.
      size: {
        xs: "h-7 px-2.5 text-xs",
        sm: "h-8 px-3 text-xs",
        default: "h-9 px-4",
        lg: "h-10 px-5",
        xl: "h-11 px-6 text-(length:--ox-a-h4)",
        icon: "size-9",
        "icon-sm": "size-8",
        "icon-lg": "size-10",
      },
    },
    defaultVariants: { variant: "default", size: "default" },
  },
);

export interface ButtonProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement>,
    VariantProps<typeof buttonVariants> {
  /**
   * Render the button styling/behaviour onto another element (Base UI `render`).
   * Replaces the shadcn/Radix `asChild` pattern: pass a `ReactElement`.
   *
   *   <Button render={<Link href="/login" />}>Login</Button>
   */
  render?: React.ReactElement;
  /** Leading icon rendered before the label. Auto-sized to 1rem. */
  startIcon?: React.ReactNode;
  /** Trailing icon rendered after the label. */
  endIcon?: React.ReactNode;
  /**
   * When the button is `disabled`, show this content in a tooltip on hover/focus
   * (typically the reason it is disabled). The button is rendered inside a
   * focusable wrapper so the tooltip stays reachable even though a disabled
   * `<button>` emits no pointer events.
   */
  disabledTooltip?: React.ReactNode;
  /**
   * Pending state: swaps the leading icon for a spinner, disables the button
   * and sets `aria-busy`, while keeping the label visible so the button never
   * changes width. Use it in place of a hand-rolled spinning icon.
   */
  loading?: boolean;
}

const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  (
    {
      className,
      variant,
      size,
      render,
      children,
      startIcon,
      endIcon,
      type,
      disabled,
      disabledTooltip,
      loading,
      ...props
    },
    ref,
  ) => {
    // While loading the spinner takes the leading-icon slot (replacing any
    // startIcon) so the label keeps its position and the button keeps its width.
    const lead = loading ? <Spinner size="sm" label="Loading" /> : startIcon;
    const isDisabled = disabled || loading;
    const element = useRender({
      render: render ?? <button type={type ?? "button"} />,
      ref,
      props: {
        className: cn(buttonVariants({ variant, size }), className),
        disabled: isDisabled,
        "aria-busy": loading || undefined,
        ...props,
        children:
          lead || endIcon ? (
            <>
              {lead}
              {children}
              {endIcon}
            </>
          ) : (
            children
          ),
      },
    });

    // A disabled button emits no pointer events (`disabled:pointer-events-none`),
    // so a tooltip attached directly to it would never open. Wrap it in a
    // focusable span that acts as the tooltip anchor: hover/focus lands on the
    // span and the tooltip explains why the action is unavailable.
    if (disabled && disabledTooltip != null) {
      return (
        <Tooltip>
          <TooltipTrigger
            render={<span tabIndex={0} className="inline-flex" />}
          >
            {element}
          </TooltipTrigger>
          <TooltipPopup>{disabledTooltip}</TooltipPopup>
        </Tooltip>
      );
    }

    return element;
  },
);
Button.displayName = "Button";

export { Button, buttonVariants };
