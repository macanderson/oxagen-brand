import * as React from "react";
export interface KeyValueItem {
    label: React.ReactNode;
    value: React.ReactNode;
    /** Optional stable key when labels can repeat. */
    key?: string;
}
export interface KeyValueListProps extends Omit<React.HTMLAttributes<HTMLDListElement>, "children"> {
    items: KeyValueItem[];
    /** Tighter row rhythm for sidebars and popovers. */
    dense?: boolean;
    /** Stack label above value instead of the two-column grid. */
    stacked?: boolean;
}
declare const KeyValueList: React.ForwardRefExoticComponent<KeyValueListProps & React.RefAttributes<HTMLDListElement>>;
export { KeyValueList };
