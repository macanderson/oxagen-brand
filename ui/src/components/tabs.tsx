"use client";
import * as React from "react";
import { Tabs as TabsPrimitive } from "@base-ui/react/tabs";
import { motion } from "motion/react";
import { cva, type VariantProps } from "class-variance-authority";
import { cn } from "../lib/utils";
import { fadeInUp } from "../lib/motion";

/*
 * Tabs — token-driven via the --tab-* tokens. Motion is retained: the sliding
 * active-indicator (TabsIndicator) and the per-panel fade-in both animate.
 *
 * The default variant is shadcn's Tabs, after the mockup's `.tabs`: a muted
 * `--hl` track as wide as its tabs, muted tabs, and one raised tab for the
 * selected view. The raised ground reads `--tab-on` and falls back to the card
 * surface. The underline variant is the dialog row and is unchanged.
 *
 * State is wired through Base UI's data-attributes (data-[active]); the rest
 * border stays a constant width so the active underline never shifts layout.
 */
const Tabs = TabsPrimitive.Root;

const tabsListVariants = cva(
  // `relative` is load-bearing: TabsIndicator is absolutely positioned with
  // `[left:var(--active-tab-left)]`, so the list MUST establish its containing
  // block. Without it the bar resolves against whatever ancestor happens to be
  // positioned (or the initial containing block) and lands somewhere arbitrary
  // — a different place per host page.
  "group/list relative inline-flex items-center text-tab-fg",
  {
    variants: {
      variant: {
        // Fits its tabs and scrolls sideways when they overflow the row.
        default:
          "w-max max-w-full gap-0.5 overflow-x-auto rounded-[10px] bg-hl p-[3px] [scrollbar-width:thin]",
        underline: "justify-start gap-4 border-b border-border",
      },
    },
    defaultVariants: { variant: "default" },
  },
);

interface TabsListProps
  extends React.ComponentPropsWithoutRef<typeof TabsPrimitive.List>,
    VariantProps<typeof tabsListVariants> {}

const TabsList = React.forwardRef<
  React.ComponentRef<typeof TabsPrimitive.List>,
  TabsListProps
>(({ className, variant = "default", ...props }, ref) => (
  <TabsPrimitive.List
    ref={ref}
    data-variant={variant}
    className={cn(tabsListVariants({ variant }), className)}
    {...props}
  />
));
TabsList.displayName = "TabsList";

/**
 * The round count after a tab's label, such as the rows the view holds.
 *
 * Counts come two ways. The `count` prop on TabsTab covers the common case
 * and places the badge after the label. TabsCount is the same badge as a part,
 * for a tab that lays out its own children, such as an icon, a label and a
 * count in a set order. Both render the same span, so they look the same.
 */
const TabsCount = React.forwardRef<
  HTMLSpanElement,
  React.ComponentPropsWithoutRef<"span">
>(({ className, ...props }, ref) => (
  <span
    ref={ref}
    data-slot="tabs-count"
    className={cn(
      // The ground is the foreground at 10%, so the badge reads on the track
      // and on the raised tab in both themes.
      "inline-flex h-5 min-w-5 items-center justify-center rounded-full bg-foreground/10 px-1.5 text-sm font-medium leading-none tabular-nums text-[var(--body)]",
      className,
    )}
    {...props}
  />
));
TabsCount.displayName = "TabsCount";

interface TabsTabProps
  extends React.ComponentPropsWithoutRef<typeof TabsPrimitive.Tab> {
  /**
   * A count shown in a round badge after the label. Zero renders; leave the
   * prop out to show no badge.
   */
  count?: React.ReactNode;
}

/** coss ui tab control (replaces the shadcn `TabsTrigger` name). */
const TabsTab = React.forwardRef<
  React.ComponentRef<typeof TabsPrimitive.Tab>,
  TabsTabProps
>(({ className, count, children, ...props }, ref) => (
  <TabsPrimitive.Tab
    ref={ref}
    className={cn(
      "inline-flex items-center justify-center gap-1.5 whitespace-nowrap text-sm font-medium text-tab-fg transition-all hover:text-tab-fg-hover focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring disabled:pointer-events-none disabled:opacity-50",
      // Default list treatment: muted tabs on the track, and the active tab
      // raised on its own ground with a border and a small shadow.
      "group-data-[variant=default]/list:min-h-[30px] group-data-[variant=default]/list:flex-none group-data-[variant=default]/list:rounded-[7px] group-data-[variant=default]/list:border group-data-[variant=default]/list:border-transparent group-data-[variant=default]/list:px-[11px] group-data-[variant=default]/list:py-1 group-data-[variant=default]/list:text-sm",
      "group-data-[variant=default]/list:data-[active]:border-border group-data-[variant=default]/list:data-[active]:bg-[var(--tab-on,var(--card))] group-data-[variant=default]/list:data-[active]:text-tab-fg-active group-data-[variant=default]/list:data-[active]:shadow-sm",
      // Underline list treatment — constant-width border at rest, color flips on state.
      "group-data-[variant=underline]/list:-mb-px group-data-[variant=underline]/list:border-b-[length:var(--tab-border-width)] group-data-[variant=underline]/list:border-tab-border group-data-[variant=underline]/list:hover:border-tab-border-hover group-data-[variant=underline]/list:px-1 group-data-[variant=underline]/list:py-2 group-data-[variant=underline]/list:data-[active]:border-tab-border-active group-data-[variant=underline]/list:data-[active]:text-tab-fg-active",
      className,
    )}
    {...props}
  >
    {children}
    {count !== undefined && count !== null ? (
      <TabsCount>{count}</TabsCount>
    ) : null}
  </TabsPrimitive.Tab>
));
TabsTab.displayName = "TabsTab";

/** coss ui tab panel (replaces the shadcn `TabsContent` name). Fades in. */
const TabsPanel = React.forwardRef<
  React.ComponentRef<typeof TabsPrimitive.Panel>,
  React.ComponentPropsWithoutRef<typeof TabsPrimitive.Panel>
>(({ className, children, ...props }, ref) => (
  <TabsPrimitive.Panel
    ref={ref}
    className={cn(
      "mt-2 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring",
      className,
    )}
    {...props}
  >
    <motion.div
      // `h-full` lets a height-constrained panel (e.g. a `flex-1 min-h-0` panel
      // inside a fixed-height dialog) pass its bounded height down to the content
      // so an inner `overflow-auto` region can actually scroll. For the common
      // auto-height panel this resolves to `auto` and is a no-op.
      className="h-full"
      key={props.value as string | undefined}
      initial="hidden"
      animate="visible"
      variants={fadeInUp}
    >
      {children}
    </motion.div>
  </TabsPrimitive.Panel>
));
TabsPanel.displayName = "TabsPanel";

/**
 * coss ui sliding tab indicator powered by Base UI's `Tabs.Indicator`. Base UI
 * writes `--active-tab-left`/`--active-tab-width` (etc.) CSS vars onto the
 * element so it self-positions. This slide is one of the two preserved motions.
 */
const TabsIndicator = React.forwardRef<
  React.ComponentRef<typeof TabsPrimitive.Indicator>,
  React.ComponentPropsWithoutRef<typeof TabsPrimitive.Indicator>
>(({ className, ...props }, ref) => (
  <TabsPrimitive.Indicator
    ref={ref}
    className={cn(
      // Active indicator is a solid bar in the active tab-border color.
      // NOTE: do NOT add a `left-0` here — it conflicts with the
      // `[left:var(--active-tab-left)]` arbitrary value below and pins the
      // bar under the first tab (width still tracks, so it "grows" wrongly).
      "absolute bottom-0 h-0.5 rounded-full bg-tab-border-active",
      // PRESERVED MOTION: the indicator slides between tabs.
      "transition-all duration-[var(--motion-base)] ease-[var(--ease-hover)]",
      "[left:var(--active-tab-left)] [width:var(--active-tab-width)]",
      className,
    )}
    {...props}
  />
));
TabsIndicator.displayName = "TabsIndicator";

export { Tabs, TabsList, TabsTab, TabsCount, TabsPanel, TabsIndicator };
export type { TabsListProps, TabsTabProps };
