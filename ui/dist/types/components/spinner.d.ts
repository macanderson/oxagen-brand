import * as React from "react";
import { type VariantProps } from "class-variance-authority";
declare const spinnerVariants: (props?: ({
    size?: "default" | "sm" | "lg" | "xs" | "xl" | null | undefined;
} & import("class-variance-authority/types").ClassProp) | undefined) => string;
export interface SpinnerProps extends React.HTMLAttributes<HTMLSpanElement>, VariantProps<typeof spinnerVariants> {
    /**
     * Accessible loading announcement. Rendered visually hidden; the wrapper is
     * `role="status"` so screen readers announce the state change.
     */
    label?: string;
}
declare function Spinner({ className, size, label, ...props }: SpinnerProps): import("react/jsx-runtime").JSX.Element;
export { Spinner, spinnerVariants };
