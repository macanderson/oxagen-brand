// @vitest-environment jsdom
// Moved from oxagen apps/app/src/ui/table.test.tsx at ddb85803.
// Table (table.tsx): one header row, a numeric column aligned right, and a
// hidden column that names itself to assistive tech through aria-label and
// draws no text, so the phone card features/shell/card-tables.ts builds from
// the header leaves that cell unlabelled. With no rows, the `empty` text fills
// one row across every column. Every test ends in an axe check.
import { cleanup, render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it } from "vitest";
import { expectNoAxe } from "../test/expect-no-axe";
import { DataTable as Table } from "./data-table";

function renderTable() {
  render(
    <Table
      label="Invoices"
      columns={[
        { label: "Invoice" },
        { label: "Amount", numeric: true },
        { label: "Open in Stripe", hidden: true },
      ]}
    >
      <tr>
        <td>OXA-0042</td>
        <td>$32.10</td>
        <td>
          <a href="https://invoice.stripe.com/i/x">Open ↗</a>
        </td>
      </tr>
    </Table>,
  );
}

afterEach(async () => {
  try {
    await expectNoAxe(document.body);
  } finally {
    cleanup();
  }
});

describe("Table", () => {
  it("names the table and prints each visible column's label, the numeric one on the right", () => {
    renderTable();
    expect(screen.getByRole("table", { name: "Invoices" })).toBeInTheDocument();
    const invoice = screen.getByRole("columnheader", { name: "Invoice" });
    expect(invoice).toHaveTextContent("Invoice");
    expect(invoice).not.toHaveAttribute("aria-label");
    expect(invoice.className).toContain("text-left");
    expect(
      screen.getByRole("columnheader", { name: "Amount" }).className,
    ).toContain("text-right");
  });

  it("names a hidden column through aria-label and draws no text in its header", () => {
    renderTable();
    const link = screen.getByRole("columnheader", { name: "Open in Stripe" });
    expect(link).toHaveAttribute("aria-label", "Open in Stripe");
    expect(link).toHaveTextContent("");
  });

  it("keeps the kit's table slot, 14px rows and the 560px floor", () => {
    renderTable();
    const table = screen.getByRole("table", { name: "Invoices" });
    expect(table).toHaveAttribute("data-slot", "table");
    expect(table.className).toContain("text-sm");
    expect(table.className).toContain("min-w-[560px]");
  });

  it("washes a hovered row to the highlight over 120ms", () => {
    renderTable();
    const body = screen.getByRole("table").querySelector("tbody");
    expect(body?.className).toContain("[&>tr:hover]:bg-hl");
    expect(body?.className).toContain("[&>tr]:duration-[120ms]");
  });

  it("reads the empty text across every column when there are no rows", () => {
    render(
      <Table
        label="Invoices"
        columns={[
          { label: "Invoice" },
          { label: "Amount", numeric: true },
          { label: "Open in Stripe", hidden: true },
        ]}
        empty="No invoices yet"
      >
        {[]}
      </Table>,
    );
    const cell = screen.getByText("No invoices yet");
    expect(cell.tagName).toBe("TD");
    expect(cell).toHaveAttribute("colspan", "3");
    expect(cell.closest("tbody")?.className).not.toContain("bg-hl");
  });

  it("shows the rows and not the empty text when there are rows", () => {
    render(
      <Table
        label="Invoices"
        columns={[{ label: "Invoice" }]}
        empty="No invoices yet"
      >
        <tr>
          <td>OXA-0042</td>
        </tr>
      </Table>,
    );
    expect(screen.getByText("OXA-0042")).toBeInTheDocument();
    expect(screen.queryByText("No invoices yet")).toBeNull();
  });
});
