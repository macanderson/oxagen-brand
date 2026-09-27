import * as React from "react";
import { type VariantProps } from "class-variance-authority";
declare const badgeVariants: (props?: ({
    variant?: "default" | "secondary" | "destructive" | "outline" | "muted" | "brand" | "cyan" | "info" | "success" | "warning" | "error" | "info-soft" | "success-soft" | "warning-soft" | "error-soft" | null | undefined;
    size?: "default" | "sm" | "lg" | null | undefined;
} & import("class-variance-authority/types").ClassProp) | undefined) => string;
export interface BadgeProps extends React.HTMLAttributes<HTMLSpanElement>, VariantProps<typeof badgeVariants> {
    /** Render the badge styling onto another element (Base UI `render`). */
    render?: React.ReactElement;
    /** Leading status dot in the badge ink color (pairs with soft variants). */
    dot?: boolean;
}
declare function Badge({ className, variant, size, render, dot, children, ...props }: BadgeProps): React.ReactElement<unknown, string | React.JSXElementConstructor<any>>;
export { Badge, badgeVariants };
