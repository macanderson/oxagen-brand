import * as React from "react";
export interface StatProps extends React.HTMLAttributes<HTMLDivElement> {
    label: React.ReactNode;
    value: React.ReactNode;
    /** Formatted change, e.g. "+12.4%". Rendered beside the trend arrow. */
    delta?: React.ReactNode;
    /** Arrow direction. Defaults the color intent: up=positive, down=negative. */
    trend?: "up" | "down" | "flat";
    /** Override the delta color when direction ≠ sentiment (e.g. cost going up). */
    intent?: "positive" | "negative" | "neutral";
    /** Small helper line under the value (e.g. "vs last 30 days"). */
    hint?: React.ReactNode;
    /** Leading icon, muted, top-right aligned. */
    icon?: React.ReactNode;
    /** Skeleton placeholders while the metric loads. */
    loading?: boolean;
    /** Status tint applied to the value itself (posture/health dashboards). */
    tone?: "neutral" | "success" | "warning" | "error";
}
declare const Stat: React.ForwardRefExoticComponent<StatProps & React.RefAttributes<HTMLDivElement>>;
/**
 * StatGroup — hairline-divided frame for a row of Stats. The `gap-px` over the
 * border color yields 1px dividers that stay correct at every responsive wrap
 * (no divide-x edge cases). Defaults to 2-up on small screens, one column per
 * stat from `lg` up (capped at 4).
 */
export interface StatGroupProps extends React.HTMLAttributes<HTMLDivElement> {
    /** Column count at the `lg` breakpoint. Defaults to the number of children (max 4). */
    columns?: 1 | 2 | 3 | 4;
}
declare const StatGroup: React.ForwardRefExoticComponent<StatGroupProps & React.RefAttributes<HTMLDivElement>>;
export { Stat, StatGroup };
