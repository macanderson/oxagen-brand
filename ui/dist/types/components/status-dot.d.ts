import * as React from "react";
import { type VariantProps } from "class-variance-authority";
declare const statusDotVariants: (props?: ({
    status?: "info" | "success" | "warning" | "error" | "primary" | "neutral" | null | undefined;
    size?: "default" | "sm" | "lg" | null | undefined;
} & import("class-variance-authority/types").ClassProp) | undefined) => string;
export interface StatusDotProps extends React.HTMLAttributes<HTMLSpanElement>, VariantProps<typeof statusDotVariants> {
    /** Soft expanding ring for live states (running, streaming, online). */
    pulse?: boolean;
    /** Visible text rendered beside the dot. Also used as the accessible name. */
    label?: React.ReactNode;
    /** Screen-reader-only status name when no visible `label` is given. */
    srLabel?: string;
}
declare function StatusDot({ className, status, size, pulse, label, srLabel, ...props }: StatusDotProps): import("react/jsx-runtime").JSX.Element;
export { StatusDot, statusDotVariants };
