import * as React from "react";
import { MinusIcon, TrendDownIcon, TrendUpIcon } from "@phosphor-icons/react";
import { cn } from "../lib/utils";
import {
  statNote,
  statStrip,
  statTerm,
  statTile,
  statValue,
} from "./control-styles";
import { Skeleton } from "./skeleton";

/*
 * Stat is the shared figure tile, the mockup's `.stat`: a panel card with a
 * dim caps label, a 24px tabular figure and a muted note under it. It carries
 * usage meters, billing totals and run counts. The value uses tabular
 * numerals so a live figure does not jitter. `StatGroup` is the strip a page
 * lays tiles in (`.grid.g4`): tiles at least 175px wide with a 14px gap, and
 * two to a row on a phone.
 *
 *   <StatGroup>
 *     <Stat label="Spend this month" value="$1,204.55" delta="+12.4%" trend="up" intent="negative" />
 *     <Stat label="Tool calls" value="48,391" delta="+3.1%" trend="up" />
 *   </StatGroup>
 *
 * The recipes live in control-styles (`statTile`, `statTerm`, `statValue`,
 * `statNote`, `statStrip`), so a page that draws its own tile matches this one.
 */
export interface StatProps extends React.HTMLAttributes<HTMLDivElement> {
  label: React.ReactNode;
  /** The figure. Null, undefined or an empty string shows `empty` instead. */
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
  /**
   * What the tile reads when there is no figure yet, such as "None yet". It
   * takes the figure's place in the muted ink, and the delta is left out.
   */
  empty?: React.ReactNode;
}

const trendIcon = {
  up: TrendUpIcon,
  down: TrendDownIcon,
  flat: MinusIcon,
} as const;
// Words and figures take the state's text stop (the `-ink` roles), which clears
// 4.5:1 on every surface of its theme. The bare roles are marks.
const intentClass = {
  positive: "text-success-ink",
  negative: "text-error-ink",
  neutral: "text-muted-foreground",
} as const;

const toneClass = {
  neutral: "text-foreground",
  success: "text-success-ink",
  warning: "text-warning-ink",
  error: "text-error-ink",
} as const;

function isBlank(value: React.ReactNode): boolean {
  return value === null || value === undefined || value === "";
}

const Stat = React.forwardRef<HTMLDivElement, StatProps>(
  (
    {
      className,
      label,
      value,
      delta,
      trend,
      intent,
      hint,
      icon,
      loading,
      tone = "neutral",
      empty,
      ...props
    },
    ref,
  ) => {
    const resolvedIntent =
      intent ??
      (trend === "up" ? "positive" : trend === "down" ? "negative" : "neutral");
    const TrendIcon = trend ? trendIcon[trend] : null;
    const blank = isBlank(value);
    return (
      <div
        ref={ref}
        data-slot="stat"
        data-empty={blank && !loading ? "" : undefined}
        aria-busy={loading ? true : undefined}
        className={cn(statTile, "relative", className)}
        {...props}
      >
        <div className="flex items-start justify-between gap-2">
          <div className={cn(statTerm, "min-w-0 truncate")}>{label}</div>
          {icon && (
            <div
              aria-hidden="true"
              className="-mt-px shrink-0 text-muted-foreground [&_svg]:size-4"
            >
              {icon}
            </div>
          )}
        </div>
        {loading ? (
          <Skeleton data-slot="stat-skeleton" className="h-[26px] w-24" />
        ) : blank ? (
          <span className={cn(statValue, "text-muted-foreground")}>
            {empty}
          </span>
        ) : (
          <div className="flex flex-wrap items-baseline gap-x-2 gap-y-0.5">
            <span className={cn(statValue, toneClass[tone])}>{value}</span>
            {(delta != null || TrendIcon) && (
              <span
                className={cn(
                  "inline-flex items-center gap-0.5 text-sm font-medium tabular-nums",
                  intentClass[resolvedIntent],
                )}
              >
                {TrendIcon && (
                  <TrendIcon aria-hidden="true" className="size-3" />
                )}
                {delta}
              </span>
            )}
          </div>
        )}
        {hint && <div className={statNote}>{hint}</div>}
      </div>
    );
  },
);
Stat.displayName = "Stat";

/**
 * StatGroup is the strip a row of Stats sits in. By default tiles are at
 * least 175px wide and fill the row, two to a row on a phone. `columns` fixes
 * the count from md up instead.
 */
export interface StatGroupProps extends React.HTMLAttributes<HTMLDivElement> {
  /** Column count from the `md` breakpoint. By default tiles fill the row at 175px or wider. */
  columns?: 1 | 2 | 3 | 4;
}

const fixedCols: Record<1 | 2 | 3 | 4, string> = {
  1: "grid grid-cols-1 gap-3.5",
  2: "grid grid-cols-2 gap-3.5",
  3: "grid grid-cols-2 gap-3.5 md:grid-cols-3",
  4: "grid grid-cols-2 gap-3.5 md:grid-cols-4",
};

const StatGroup = React.forwardRef<HTMLDivElement, StatGroupProps>(
  ({ className, columns, children, ...props }, ref) => (
    <div
      ref={ref}
      data-slot="stat-group"
      className={cn(
        columns === undefined ? statStrip : fixedCols[columns],
        className,
      )}
      {...props}
    >
      {children}
    </div>
  ),
);
StatGroup.displayName = "StatGroup";

export { Stat, StatGroup };
