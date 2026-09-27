import * as React from "react";
import { Tabs as TabsPrimitive } from "@base-ui/react/tabs";
import { type VariantProps } from "class-variance-authority";
declare const Tabs: React.ForwardRefExoticComponent<Omit<import("@base-ui/react").TabsRootProps, "ref"> & React.RefAttributes<HTMLDivElement>>;
declare const tabsListVariants: (props?: ({
    variant?: "default" | "underline" | null | undefined;
} & import("class-variance-authority/types").ClassProp) | undefined) => string;
interface TabsListProps extends React.ComponentPropsWithoutRef<typeof TabsPrimitive.List>, VariantProps<typeof tabsListVariants> {
}
declare const TabsList: React.ForwardRefExoticComponent<TabsListProps & React.RefAttributes<HTMLDivElement>>;
/** coss ui tab control (replaces the shadcn `TabsTrigger` name). */
declare const TabsTab: React.ForwardRefExoticComponent<Omit<Omit<import("@base-ui/react").TabsTabProps, "ref"> & React.RefAttributes<HTMLElement>, "ref"> & React.RefAttributes<HTMLElement>>;
/** coss ui tab panel (replaces the shadcn `TabsContent` name). Fades in. */
declare const TabsPanel: React.ForwardRefExoticComponent<Omit<Omit<import("@base-ui/react").TabsPanelProps, "ref"> & React.RefAttributes<HTMLDivElement>, "ref"> & React.RefAttributes<HTMLDivElement>>;
/**
 * coss ui sliding tab indicator powered by Base UI's `Tabs.Indicator`. Base UI
 * writes `--active-tab-left`/`--active-tab-width` (etc.) CSS vars onto the
 * element so it self-positions. This slide is one of the two preserved motions.
 */
declare const TabsIndicator: React.ForwardRefExoticComponent<Omit<Omit<import("@base-ui/react").TabsIndicatorProps, "ref"> & React.RefAttributes<HTMLSpanElement>, "ref"> & React.RefAttributes<HTMLSpanElement>>;
export { Tabs, TabsList, TabsTab, TabsPanel, TabsIndicator };
