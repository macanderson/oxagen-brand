// @vitest-environment jsdom
/**
 * table.test.tsx: render tests for the shared Table primitive set.
 *
 * Covers the scroll container, the 560px floor and `narrow`, density vars, the
 * mockup's header caps, numeric columns, the row wash, the sticky header, the
 * totals rule, the group row, the empty row colSpan, and axe.
 */

import { cleanup, render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it } from "vitest";
import { expectNoAxe } from "../test/expect-no-axe";
import {
  Table,
  TableBody,
  TableCaption,
  TableCell,
  TableEmpty,
  TableFooter,
  TableGroupRow,
  TableHead,
  TableHeader,
  TableRow,
} from "./table";

afterEach(cleanup);

function renderTable(tableProps: React.ComponentProps<typeof Table> = {}) {
  return render(
    <Table {...tableProps}>
      <TableCaption>Monthly usage</TableCaption>
      <TableHeader data-testid="thead">
        <TableRow>
          <TableHead>Name</TableHead>
          <TableHead numeric>Cost</TableHead>
        </TableRow>
      </TableHeader>
      <TableBody>
        <TableGroupRow colSpan={2}>Today</TableGroupRow>
        <TableRow data-testid="row">
          <TableCell>ontology.query</TableCell>
          <TableCell numeric>$1.20</TableCell>
        </TableRow>
      </TableBody>
      <TableFooter data-testid="tfoot">
        <TableRow>
          <TableCell>Total</TableCell>
          <TableCell numeric>$1.20</TableCell>
        </TableRow>
      </TableFooter>
    </Table>,
  );
}

describe("Table", () => {
  it("wraps the table in an overflow-x-auto container for mobile scroll", () => {
    renderTable();
    const table = screen.getByRole("table");
    expect(table.parentElement?.className).toContain("overflow-x-auto");
  });

  it("marks the table for the kit's cell rules and sets 14px rows", () => {
    renderTable();
    const table = screen.getByRole("table");
    expect(table).toHaveAttribute("data-slot", "table");
    expect(table.className).toContain("text-base");
    expect(table.className).toContain("border-collapse");
  });

  it("holds a 560px floor from md up, and narrow drops it", () => {
    renderTable();
    expect(screen.getByRole("table").className).toContain("md:min-w-[560px]");
    cleanup();
    renderTable({ narrow: true });
    expect(screen.getByRole("table").className).not.toContain("min-w-");
  });

  it("applies the default density padding vars", () => {
    renderTable();
    const table = screen.getByRole("table");
    expect(table.className).toContain("[--table-pad-x:0.75rem]");
    expect(table.className).toContain("[--table-pad-y:9px]");
  });

  it("compact density tightens the vertical padding var", () => {
    renderTable({ density: "compact" });
    expect(screen.getByRole("table").className).toContain(
      "[--table-pad-y:0.375rem]",
    );
  });

  it("merges containerClassName onto the scroll wrapper", () => {
    renderTable({ containerClassName: "rounded-xl" });
    const table = screen.getByRole("table");
    expect(table.parentElement?.className).toContain("rounded-xl");
  });

  it("head cells read in the dim caps on the card surface", () => {
    renderTable();
    const th = screen.getByText("Name");
    expect(th.tagName).toBe("TH");
    for (const token of [
      "uppercase",
      "text-xs",
      "tracking-[0.09em]",
      "font-semibold",
      "text-dim",
      "bg-card",
      "whitespace-nowrap",
    ]) {
      expect(th.className).toContain(token);
    }
  });

  it("header rows draw the border rule", () => {
    renderTable();
    expect(screen.getByTestId("thead").className).toContain(
      "[&_tr]:border-border",
    );
  });

  it("cells read the density padding vars", () => {
    renderTable();
    const td = screen.getByText("ontology.query");
    expect(td.className).toContain("px-[var(--table-pad-x)]");
    expect(td.className).toContain("py-[var(--table-pad-y)]");
  });

  it("numeric head and cells align right in tabular numerals", () => {
    renderTable();
    const head = screen.getByText("Cost");
    expect(head.className).toContain("text-right");
    expect(head.className).not.toContain("text-left");
    const [figure] = screen.getAllByText("$1.20");
    expect(figure?.className).toContain("text-right");
    expect(figure?.className).toContain("tabular-nums");
  });

  it("rows wash to the highlight on hover and can opt into pointer affordance", () => {
    render(
      <Table>
        <TableBody>
          <TableRow data-testid="interactive-row" interactive>
            <TableCell>Row</TableCell>
          </TableRow>
          <TableRow data-testid="plain-row">
            <TableCell>Row</TableCell>
          </TableRow>
        </TableBody>
      </Table>,
    );
    const row = screen.getByTestId("interactive-row");
    expect(row.className).toContain("hover:bg-hl");
    expect(row.className).toContain("duration-[120ms]");
    expect(row.className).toContain("border-border");
    expect(row.className).toContain("cursor-pointer");
    expect(screen.getByTestId("plain-row").className).not.toContain(
      "cursor-pointer",
    );
  });

  it("sticky header opts into sticky positioning", () => {
    render(
      <Table>
        <TableHeader sticky data-testid="sticky-head">
          <TableRow>
            <TableHead>Name</TableHead>
          </TableRow>
        </TableHeader>
      </Table>,
    );
    expect(screen.getByTestId("sticky-head").className).toContain("sticky");
  });

  it("footer renders inside tfoot under the rule line", () => {
    renderTable();
    const tfoot = screen.getByTestId("tfoot");
    expect(tfoot.tagName).toBe("TFOOT");
    expect(tfoot.className).toContain("border-rule");
  });

  it("TableGroupRow spans the columns in the header's caps", () => {
    renderTable();
    const cell = screen.getByText("Today");
    expect(cell.tagName).toBe("TD");
    expect(cell.getAttribute("colspan")).toBe("2");
    expect(cell.className).toContain("bg-hl");
    expect(cell.className).toContain("uppercase");
    expect(cell.closest("tr")).toHaveAttribute(
      "data-slot",
      "table-group-row",
    );
  });

  it("TableEmpty spans the given columns with a default message", () => {
    render(
      <Table>
        <TableBody>
          <TableEmpty colSpan={3} />
        </TableBody>
      </Table>,
    );
    const cell = screen.getByText("No results.");
    expect(cell.getAttribute("colspan")).toBe("3");
  });

  it("TableEmpty renders custom children", () => {
    render(
      <Table>
        <TableBody>
          <TableEmpty colSpan={2}>No usage yet</TableEmpty>
        </TableBody>
      </Table>,
    );
    expect(screen.getByText("No usage yet")).toBeInTheDocument();
  });

  it("caption renders as muted helper text", () => {
    renderTable();
    expect(screen.getByText("Monthly usage").tagName).toBe("CAPTION");
  });

  it("has no axe violations with a group row, a footer and an empty table", async () => {
    const { container } = renderTable();
    await expectNoAxe(container);
    cleanup();
    const empty = render(
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>Run</TableHead>
            <TableHead>Agent</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          <TableEmpty colSpan={2}>No runs yet</TableEmpty>
        </TableBody>
      </Table>,
    );
    await expectNoAxe(empty.container);
  });
});
