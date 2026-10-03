// Moved from oxagen apps/app/src/ui/table.tsx at ddb85803.
// A list table: one header row and a body the caller fills with rows. On a
// phone the shell turns it into labelled cards (features/shell/card-tables.ts),
// so a table must keep a single header row with no grouped header.
//
// The shape is the mockup's `table`, `th` and `td` rules (engine.css, ADR-132):
// 13px rows on the panel, a header in 10.5px caps and the dim ink with no band
// behind it, and the wash on a hovered row. globals.css carries the same rule
// for every table under the shell, so a caller that draws its own <table>
// cannot fall off it.
//
// A value too wide for its column ends in an ellipsis. Render that cell as
// `<TruncatedCell as="td">` so a hover or focus shows the whole value.
import { Children, type ReactNode } from "react";
import { cn } from "../lib/utils";

type TableColumn = {
  label: string;
  numeric?: boolean;
  /**
   * The header names the column to assistive tech through aria-label and draws
   * nothing (a link column). It carries no text, so the phone card that
   * features/shell/card-tables.ts builds leaves the cell unlabelled.
   */
  hidden?: boolean;
};

/** `th,td { padding:9px 12px; vertical-align:middle }` */
export const cell = "px-3 py-[9px] align-middle";
/*
 * A numeric cell takes the mono face: the kit assigns code, logs, digests and
 * the numbers in tables to Monaspace Neon, so a column of figures reads as one
 * column rather than as prose that happens to be digits.
 */
export const numericCell = `${cell} whitespace-nowrap text-right font-mono tabular-nums`;

/**
 * `th { font-size:10.5px; letter-spacing:.09em; text-transform:uppercase; color:var(--dim) }`.
 * A header carries meaning, so the kit sets it in --muted-foreground, which
 * clears 4.5:1 on every ground, in place of the mockup's dim (#88).
 */
export const headCell =
  "whitespace-nowrap bg-card px-3 py-[9px] text-xs font-semibold uppercase tracking-[0.09em] text-muted-foreground";

export function DataTable({
  label,
  columns,
  empty,
  children,
}: {
  /** The table's accessible name, already translated. */
  label: string;
  columns: readonly TableColumn[];
  /**
   * What the body reads when it has no rows, already translated. It fills one
   * row across every column. Without it an empty table shows its header only.
   */
  empty?: ReactNode;
  children?: ReactNode;
}) {
  const blank = empty !== undefined && Children.toArray(children).length === 0;
  return (
    <div className="min-w-0 overflow-x-auto">
      <table
        data-slot="table"
        aria-label={label}
        className="w-full min-w-[560px] border-collapse text-base"
      >
        <thead>
          <tr className="border-b border-border">
            {columns.map((column) => (
              <th
                key={column.label}
                scope="col"
                aria-label={column.hidden === true ? column.label : undefined}
                className={`${headCell} ${column.numeric === true ? "text-right" : "text-left"}`}
              >
                {column.hidden === true ? null : column.label}
              </th>
            ))}
          </tr>
        </thead>
        <tbody
          className={cn(
            "divide-y divide-border",
            !blank &&
              "[&>tr]:transition-colors [&>tr]:duration-[120ms] [&>tr:hover]:bg-hl",
          )}
        >
          {blank ? (
            <tr data-slot="table-empty">
              <td
                colSpan={columns.length}
                className="px-3 py-8 text-center text-base text-muted-foreground"
              >
                {empty}
              </td>
            </tr>
          ) : (
            children
          )}
        </tbody>
      </table>
    </div>
  );
}
