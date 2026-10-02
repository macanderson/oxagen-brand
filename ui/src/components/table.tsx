import * as React from "react";
import { cn } from "../lib/utils";

/*
 * Table is the shared set of `<table>` parts for every data surface: billing
 * usage, registries, evals, skills, environments and runs. It follows the
 * mockup's `table`, `th` and `td` rules (mockups/src/v3.css 258-270): 13px
 * rows with 9px by 12px padding and a `--border` rule under each, a header in
 * 10.5px caps and the dim ink on the card surface, and the `--hl` wash on a
 * hovered row. The last row has no rule. Density is one CSS variable per axis,
 * so every cell follows it.
 *
 *   <Table density="compact">
 *     <TableHeader>
 *       <TableRow><TableHead>Name</TableHead><TableHead numeric>Cost</TableHead></TableRow>
 *     </TableHeader>
 *     <TableBody>
 *       <TableGroupRow colSpan={2}>Today</TableGroupRow>
 *       <TableRow interactive onClick={...}>
 *         <TableCell>...</TableCell>
 *       </TableRow>
 *       <TableEmpty colSpan={2}>No usage yet</TableEmpty>
 *     </TableBody>
 *   </Table>
 *
 * The table renders inside an `overflow-x-auto` box. From the md breakpoint it
 * is at least 560px wide, so a narrow panel scrolls instead of squeezing the
 * columns. `narrow` drops that floor for a small table such as a key and value
 * list. Pair it with `<Panel inset>` for a flush, titled surface.
 */

type TableDensity = "default" | "compact";

export interface TableProps extends React.HTMLAttributes<HTMLTableElement> {
  /** Row padding scale. `compact` tightens vertical rhythm for dense data. */
  density?: TableDensity;
  /** Class applied to the scroll container wrapping the `<table>`. */
  containerClassName?: string;
  /** Drop the 560px floor, for a small table that fits a narrow panel. */
  narrow?: boolean;
}

const densityVars: Record<TableDensity, string> = {
  // One knob per axis. Every cell and header reads these vars.
  default: "[--table-pad-x:0.75rem] [--table-pad-y:9px]",
  compact: "[--table-pad-x:0.625rem] [--table-pad-y:0.375rem]",
};

const Table = React.forwardRef<HTMLTableElement, TableProps>(
  (
    { className, density = "default", containerClassName, narrow, ...props },
    ref,
  ) => (
    <div className={cn("relative w-full overflow-x-auto", containerClassName)}>
      <table
        ref={ref}
        data-slot="table"
        className={cn(
          "w-full caption-bottom border-collapse text-sm",
          !narrow && "md:min-w-[560px]",
          densityVars[density],
          className,
        )}
        {...props}
      />
    </div>
  ),
);
Table.displayName = "Table";

export interface TableHeaderProps
  extends React.HTMLAttributes<HTMLTableSectionElement> {
  /** Keep the header visible while the table body scrolls under it. */
  sticky?: boolean;
}

const TableHeader = React.forwardRef<HTMLTableSectionElement, TableHeaderProps>(
  ({ className, sticky, ...props }, ref) => (
    <thead
      ref={ref}
      className={cn(
        "[&_tr]:border-b [&_tr]:border-border [&_tr]:hover:bg-transparent",
        sticky && "sticky top-0 z-10",
        className,
      )}
      {...props}
    />
  ),
);
TableHeader.displayName = "TableHeader";

const TableBody = React.forwardRef<
  HTMLTableSectionElement,
  React.HTMLAttributes<HTMLTableSectionElement>
>(({ className, ...props }, ref) => (
  <tbody
    ref={ref}
    className={cn("[&_tr:last-child]:border-0", className)}
    {...props}
  />
));
TableBody.displayName = "TableBody";

/** The totals row sits under a `--rule` line, the mockup's `tr.tot`. */
const TableFooter = React.forwardRef<
  HTMLTableSectionElement,
  React.HTMLAttributes<HTMLTableSectionElement>
>(({ className, ...props }, ref) => (
  <tfoot
    ref={ref}
    className={cn(
      "border-t border-rule font-medium [&>tr]:last:border-b-0",
      className,
    )}
    {...props}
  />
));
TableFooter.displayName = "TableFooter";

export interface TableRowProps
  extends React.HTMLAttributes<HTMLTableRowElement> {
  /** Pointer affordance for clickable rows (row-level navigation/selection). */
  interactive?: boolean;
}

const TableRow = React.forwardRef<HTMLTableRowElement, TableRowProps>(
  ({ className, interactive, ...props }, ref) => (
    <tr
      ref={ref}
      className={cn(
        "border-b border-border transition-colors duration-[120ms] hover:bg-hl data-[state=selected]:bg-muted",
        interactive && "cursor-pointer",
        className,
      )}
      {...props}
    />
  ),
);
TableRow.displayName = "TableRow";

export interface TableHeadProps
  extends React.ThHTMLAttributes<HTMLTableCellElement> {
  /** A column of figures: aligned right, in tabular numerals. */
  numeric?: boolean;
}

const TableHead = React.forwardRef<HTMLTableCellElement, TableHeadProps>(
  ({ className, numeric, ...props }, ref) => (
    <th
      ref={ref}
      className={cn(
        "whitespace-nowrap bg-card px-[var(--table-pad-x)] py-[var(--table-pad-y)] text-left align-middle text-sm font-semibold uppercase tracking-[0.09em] text-dim",
        numeric && "text-right tabular-nums",
        className,
      )}
      {...props}
    />
  ),
);
TableHead.displayName = "TableHead";

export interface TableCellProps
  extends React.TdHTMLAttributes<HTMLTableCellElement> {
  /** A figure: aligned right, in tabular numerals. */
  numeric?: boolean;
}

const TableCell = React.forwardRef<HTMLTableCellElement, TableCellProps>(
  ({ className, numeric, ...props }, ref) => (
    <td
      ref={ref}
      className={cn(
        "px-[var(--table-pad-x)] py-[var(--table-pad-y)] align-middle",
        numeric && "text-right tabular-nums",
        className,
      )}
      {...props}
    />
  ),
);
TableCell.displayName = "TableCell";

const TableCaption = React.forwardRef<
  HTMLTableCaptionElement,
  React.HTMLAttributes<HTMLTableCaptionElement>
>(({ className, ...props }, ref) => (
  <caption
    ref={ref}
    className={cn("mt-3 text-xs text-muted-foreground", className)}
    {...props}
  />
));
TableCaption.displayName = "TableCaption";

export interface TableGroupRowProps
  extends React.HTMLAttributes<HTMLTableRowElement> {
  /** Number of columns the row spans (match your header). */
  colSpan: number;
}

/**
 * A full-width row that opens a group, such as the runs of one day. It reads
 * in the header's caps on the `--hl` ground, the mockup's `tr.dayrow`.
 */
const TableGroupRow = React.forwardRef<HTMLTableRowElement, TableGroupRowProps>(
  ({ className, colSpan, children, ...props }, ref) => (
    <tr
      ref={ref}
      data-slot="table-group-row"
      className={cn("border-b border-border", className)}
      {...props}
    >
      <td
        colSpan={colSpan}
        className="whitespace-nowrap bg-hl px-[var(--table-pad-x)] py-1.5 text-sm font-semibold uppercase tracking-[0.1em] text-dim"
      >
        {children}
      </td>
    </tr>
  ),
);
TableGroupRow.displayName = "TableGroupRow";

export interface TableEmptyProps
  extends React.HTMLAttributes<HTMLTableRowElement> {
  /** Number of columns the empty message spans (match your header). */
  colSpan: number;
}

/** A full-width empty row. Render it inside `<TableBody>` when there are no rows. */
const TableEmpty = React.forwardRef<HTMLTableRowElement, TableEmptyProps>(
  ({ className, colSpan, children, ...props }, ref) => (
    <tr ref={ref} className={cn("hover:bg-transparent", className)} {...props}>
      <td
        colSpan={colSpan}
        className="px-[var(--table-pad-x)] py-8 text-center text-sm text-muted-foreground"
      >
        {children ?? "No results."}
      </td>
    </tr>
  ),
);
TableEmpty.displayName = "TableEmpty";

export {
  Table,
  TableHeader,
  TableBody,
  TableFooter,
  TableRow,
  TableHead,
  TableCell,
  TableCaption,
  TableGroupRow,
  TableEmpty,
};
