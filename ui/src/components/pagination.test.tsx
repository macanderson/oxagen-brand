// @vitest-environment jsdom
// Moved from oxagen apps/app/src/ui/pagination.test.tsx at ddb85803.
// The pager under a list: a missing step is disabled, a present one turns the
// page, choosing a size from Rows per page reports it, and a step the press
// disables hands focus to the other step.
import { cleanup, render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { useState } from "react";
import { afterEach, describe, expect, it, vi } from "vitest";
import { expectNoAxe } from "../test/expect-no-axe";
import { RowsField, RowsPager } from "./pagination";

afterEach(cleanup);

function renderPager(
  steps: { previous: (() => void) | null; next: (() => void) | null },
  onPerPage = vi.fn(),
) {
  return render(
    <RowsPager
      label="Pages"
      rowsLabel="Rows per page"
      perPage={25}
      sizes={[10, 25, 50, 100]}
      onPerPage={onPerPage}
      range="1–25 of 60"
      previousLabel="Previous"
      nextLabel="Next"
      {...steps}
    />,
  );
}

/** A pager over `pages` pages that keeps its own page. */
function Paged({ pages }: { pages: number }) {
  const [page, setPage] = useState(1);
  return (
    <RowsPager
      label="Pages"
      rowsLabel="Rows per page"
      perPage={25}
      sizes={[10, 25, 50, 100]}
      onPerPage={vi.fn()}
      range={`Page ${String(page)} of ${String(pages)}`}
      previousLabel="Previous page"
      nextLabel="Next page"
      previous={
        page <= 1
          ? null
          : () => {
              setPage(page - 1);
            }
      }
      next={
        page >= pages
          ? null
          : () => {
              setPage(page + 1);
            }
      }
    />
  );
}

describe("RowsPager", () => {
  it("disables a step with no page that way and turns the other", async () => {
    const next = vi.fn();
    const { container } = renderPager({ previous: null, next });
    expect(screen.getByRole("button", { name: "Previous" })).toBeDisabled();
    await userEvent.click(screen.getByRole("button", { name: "Next" }));
    expect(next).toHaveBeenCalledOnce();
    expect(screen.getByRole("navigation", { name: "Pages" })).toBeTruthy();
    expect(screen.getByText("1–25 of 60")).toBeTruthy();
    await expectNoAxe(container);
  });

  it("names each step by its label alone and shows no text", () => {
    renderPager({ previous: vi.fn(), next: vi.fn() });
    const previous = screen.getByRole("button", { name: "Previous" });
    const next = screen.getByRole("button", { name: "Next" });
    expect(previous).toHaveAttribute("type", "button");
    expect(previous.textContent).toBe("");
    expect(next.textContent).toBe("");
    expect(previous.querySelector("svg")).not.toBeNull();
    expect(screen.queryAllByRole("link")).toHaveLength(0);
  });

  it("reports the size chosen from Rows per page", async () => {
    const onPerPage = vi.fn();
    renderPager({ previous: vi.fn(), next: null }, onPerPage);
    const rows = screen.getByRole("combobox", { name: "Rows per page" });
    expect(rows).toHaveTextContent("25");
    await userEvent.click(rows);
    await userEvent.click(await screen.findByRole("option", { name: "50" }));
    await waitFor(() => {
      expect(onPerPage).toHaveBeenCalledWith(50);
    });
  });

  it("leaves the range out when none is given", () => {
    const { container } = render(
      <RowsPager
        label="Pages"
        rowsLabel="Rows per page"
        perPage={10}
        sizes={[10, 25]}
        onPerPage={vi.fn()}
        previousLabel="Previous page"
        nextLabel="Next page"
        previous={null}
        next={null}
      />,
    );
    expect(container.querySelector("[data-range]")).toBeNull();
  });

  it("hands focus to Previous when Next reaches the last page", async () => {
    const user = userEvent.setup();
    render(<Paged pages={2} />);
    const next = screen.getByRole("button", { name: "Next page" });
    await user.click(next);
    expect(screen.getByText("Page 2 of 2")).toBeTruthy();
    expect(next).toBeDisabled();
    expect(
      screen.getByRole("button", { name: "Previous page" }),
    ).toHaveFocus();
  });

  it("hands focus to Next when Previous reaches the first page", async () => {
    const user = userEvent.setup();
    render(<Paged pages={2} />);
    await user.click(screen.getByRole("button", { name: "Next page" }));
    const previous = screen.getByRole("button", { name: "Previous page" });
    await user.click(previous);
    expect(screen.getByText("Page 1 of 2")).toBeTruthy();
    expect(previous).toBeDisabled();
    expect(screen.getByRole("button", { name: "Next page" })).toHaveFocus();
  });

  it("keeps focus on a step that stays enabled", async () => {
    const user = userEvent.setup();
    render(<Paged pages={3} />);
    const next = screen.getByRole("button", { name: "Next page" });
    await user.click(next);
    expect(screen.getByText("Page 2 of 3")).toBeTruthy();
    expect(next).toHaveFocus();
  });

  it("disables both steps when there is one page", async () => {
    const { container } = render(<Paged pages={1} />);
    expect(
      screen.getByRole("button", { name: "Previous page" }),
    ).toBeDisabled();
    expect(screen.getByRole("button", { name: "Next page" })).toBeDisabled();
    await expectNoAxe(container);
  });
});

describe("RowsField", () => {
  it("labels its select and tags the trigger", () => {
    render(
      <RowsField
        label="Rows per page"
        perPage={10}
        sizes={[10, 25]}
        onPerPage={vi.fn()}
        testId="rows"
      />,
    );
    expect(screen.getByRole("group", { name: "Rows per page" })).toBeTruthy();
    expect(screen.getByTestId("rows")).toHaveTextContent("10");
  });
});
