// @vitest-environment jsdom
/**
 * toggle-group.test.tsx: render, selection, counts and accessibility for
 * ToggleGroup and ToggleGroupItem.
 */

import { render, cleanup } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, afterEach, vi } from "vitest";
import { ToggleGroup, ToggleGroupItem } from "./toggle-group";
import { expectNoAxe } from "../test/expect-no-axe";

afterEach(cleanup);

describe("ToggleGroup", () => {
  it("renders a labelled group of toggle buttons", () => {
    const { getByRole } = render(
      <ToggleGroup aria-label="Run status">
        <ToggleGroupItem value="running">Running</ToggleGroupItem>
        <ToggleGroupItem value="failed">Failed</ToggleGroupItem>
      </ToggleGroup>,
    );
    expect(getByRole("group", { name: "Run status" })).toBeInTheDocument();
    expect(getByRole("button", { name: "Running" })).toHaveAttribute(
      "aria-pressed",
      "false",
    );
  });

  it("presses one item at a time by default", async () => {
    const onChange = vi.fn();
    const { getByRole } = render(
      <ToggleGroup aria-label="Time range" defaultValue={["day"]} onValueChange={onChange}>
        <ToggleGroupItem value="day">Day</ToggleGroupItem>
        <ToggleGroupItem value="week">Week</ToggleGroupItem>
      </ToggleGroup>,
    );
    await userEvent.click(getByRole("button", { name: "Week" }));
    expect(onChange).toHaveBeenLastCalledWith(["week"], expect.anything());
    expect(getByRole("button", { name: "Week" })).toHaveAttribute(
      "aria-pressed",
      "true",
    );
    expect(getByRole("button", { name: "Day" })).toHaveAttribute(
      "aria-pressed",
      "false",
    );
  });

  it("presses several items when multiple is set", async () => {
    const { getByRole } = render(
      <ToggleGroup aria-label="Run status" multiple>
        <ToggleGroupItem value="running">Running</ToggleGroupItem>
        <ToggleGroupItem value="waiting">Waiting</ToggleGroupItem>
      </ToggleGroup>,
    );
    await userEvent.click(getByRole("button", { name: "Running" }));
    await userEvent.click(getByRole("button", { name: "Waiting" }));
    expect(getByRole("button", { name: "Running" })).toHaveAttribute(
      "aria-pressed",
      "true",
    );
    expect(getByRole("button", { name: "Waiting" })).toHaveAttribute(
      "aria-pressed",
      "true",
    );
  });

  it("shows a count after the label, including zero", () => {
    const { getByRole, container } = render(
      <ToggleGroup aria-label="Run status">
        <ToggleGroupItem value="running" count={4}>
          Running
        </ToggleGroupItem>
        <ToggleGroupItem value="failed" count={0}>
          Failed
        </ToggleGroupItem>
        <ToggleGroupItem value="done">Done</ToggleGroupItem>
      </ToggleGroup>,
    );
    const counts = container.querySelectorAll('[data-slot="toggle-group-count"]');
    expect(Array.from(counts, (node) => node.textContent)).toEqual(["4", "0"]);
    expect(getByRole("button", { name: /Failed/ })).toHaveTextContent("Failed0");
  });

  it("does not press a disabled item", async () => {
    const onChange = vi.fn();
    const { getByRole } = render(
      <ToggleGroup aria-label="Scope" onValueChange={onChange}>
        <ToggleGroupItem value="mine">Mine</ToggleGroupItem>
        <ToggleGroupItem value="team" disabled>
          Team
        </ToggleGroupItem>
      </ToggleGroup>,
    );
    await userEvent.click(getByRole("button", { name: "Team" }));
    expect(onChange).not.toHaveBeenCalled();
    expect(getByRole("button", { name: "Team" })).toHaveAttribute(
      "data-disabled",
    );
  });

  it("merges a className on the group", () => {
    const { getByRole } = render(
      <ToggleGroup aria-label="Scope" className="custom-group">
        <ToggleGroupItem value="mine">Mine</ToggleGroupItem>
      </ToggleGroup>,
    );
    expect(getByRole("group").className).toContain("custom-group");
  });

  it("has no axe violations with a pressed item and counts", async () => {
    const { container } = render(
      <ToggleGroup aria-label="Run status" defaultValue={["running"]}>
        <ToggleGroupItem value="running" count={4}>
          Running
        </ToggleGroupItem>
        <ToggleGroupItem value="failed" count={0}>
          Failed
        </ToggleGroupItem>
      </ToggleGroup>,
    );
    await expectNoAxe(container);
  });
});
