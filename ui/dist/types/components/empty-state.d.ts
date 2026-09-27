import * as React from "react";
export interface EmptyStateProps extends Omit<React.HTMLAttributes<HTMLDivElement>, "title"> {
    /** Lucide icon element; auto-sized and muted. */
    icon?: React.ReactNode;
    title: React.ReactNode;
    description?: React.ReactNode;
    /** Primary (and optionally secondary) call to action. */
    action?: React.ReactNode;
    size?: "sm" | "default";
    /**
     * Container treatment: `plain` for inside an existing Panel/Card, `dashed`
     * for a standalone drop-target-style block, `muted` for a soft filled block.
     */
    variant?: "plain" | "dashed" | "muted";
}
declare const EmptyState: React.ForwardRefExoticComponent<EmptyStateProps & React.RefAttributes<HTMLDivElement>>;
export { EmptyState };
