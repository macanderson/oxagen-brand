import * as React from "react";
type TableDensity = "default" | "compact";
export interface TableProps extends React.HTMLAttributes<HTMLTableElement> {
    /** Row padding scale. `compact` tightens vertical rhythm for dense data. */
    density?: TableDensity;
    /** Class applied to the scroll container wrapping the `<table>`. */
    containerClassName?: string;
}
declare const Table: React.ForwardRefExoticComponent<TableProps & React.RefAttributes<HTMLTableElement>>;
export interface TableHeaderProps extends React.HTMLAttributes<HTMLTableSectionElement> {
    /** Keep the header visible while the table body scrolls under it. */
    sticky?: boolean;
}
declare const TableHeader: React.ForwardRefExoticComponent<TableHeaderProps & React.RefAttributes<HTMLTableSectionElement>>;
declare const TableBody: React.ForwardRefExoticComponent<React.HTMLAttributes<HTMLTableSectionElement> & React.RefAttributes<HTMLTableSectionElement>>;
declare const TableFooter: React.ForwardRefExoticComponent<React.HTMLAttributes<HTMLTableSectionElement> & React.RefAttributes<HTMLTableSectionElement>>;
export interface TableRowProps extends React.HTMLAttributes<HTMLTableRowElement> {
    /** Pointer affordance for clickable rows (row-level navigation/selection). */
    interactive?: boolean;
}
declare const TableRow: React.ForwardRefExoticComponent<TableRowProps & React.RefAttributes<HTMLTableRowElement>>;
declare const TableHead: React.ForwardRefExoticComponent<React.ThHTMLAttributes<HTMLTableCellElement> & React.RefAttributes<HTMLTableCellElement>>;
declare const TableCell: React.ForwardRefExoticComponent<React.TdHTMLAttributes<HTMLTableCellElement> & React.RefAttributes<HTMLTableCellElement>>;
declare const TableCaption: React.ForwardRefExoticComponent<React.HTMLAttributes<HTMLTableCaptionElement> & React.RefAttributes<HTMLTableCaptionElement>>;
export interface TableEmptyProps extends React.HTMLAttributes<HTMLTableRowElement> {
    /** Number of columns the empty message spans (match your header). */
    colSpan: number;
}
/** Full-width empty-state row — render inside `<TableBody>` when there are no rows. */
declare const TableEmpty: React.ForwardRefExoticComponent<TableEmptyProps & React.RefAttributes<HTMLTableRowElement>>;
export { Table, TableHeader, TableBody, TableFooter, TableRow, TableHead, TableCell, TableCaption, TableEmpty, };
