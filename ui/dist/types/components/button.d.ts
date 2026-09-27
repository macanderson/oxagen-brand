import * as React from "react";
import { type VariantProps } from "class-variance-authority";
declare const buttonVariants: (props?: ({
    variant?: "default" | "secondary" | "destructive" | "outline" | "link" | "primary" | "ghost" | "destructive-outline" | "gradient" | null | undefined;
    size?: "default" | "sm" | "lg" | "xs" | "xl" | "icon" | "icon-sm" | "icon-lg" | null | undefined;
} & import("class-variance-authority/types").ClassProp) | undefined) => string;
export interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement>, VariantProps<typeof buttonVariants> {
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
     * changes width. Use instead of hand-rolling `<Loader2 className="animate-spin" />`.
     */
    loading?: boolean;
}
declare const Button: React.ForwardRefExoticComponent<ButtonProps & React.RefAttributes<HTMLButtonElement>>;
export { Button, buttonVariants };
