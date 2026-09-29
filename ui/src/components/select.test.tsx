// @vitest-environment jsdom
/**
 * Render tests for Select and its parts.
 *
 * Covers the trigger sizes and aria, and, with the popup open through
 * `defaultOpen`, the shared floating surface, the row recipe, the group
 * label and the trailing checked mark.
 */

import { render, cleanup } from "@testing-library/react";
import { describe, expect, it, afterEach } from "vitest";
import { expectNoAxe } from "../test/expect-no-axe";
import {
  Select,
  SelectTrigger,
  SelectValue,
  SelectPopup,
  SelectGroup,
  SelectLabel,
  SelectItem,
} from "./select";

afterEach(cleanup);

function TestSelect({
  size,
  defaultOpen,
}: {
  size?: "sm" | "default" | "lg";
  defaultOpen?: boolean;
}) {
  return (
    <Select defaultOpen={defaultOpen} defaultValue={defaultOpen ? "opus" : undefined}>
      <SelectTrigger size={size} aria-label="Model">
        <SelectValue placeholder="Pick a model" />
      </SelectTrigger>
      <SelectPopup>
        <SelectGroup>
          <SelectLabel>Anthropic</SelectLabel>
          <SelectItem value="opus">Claude Opus</SelectItem>
          <SelectItem value="sonnet">Claude Sonnet</SelectItem>
        </SelectGroup>
      </SelectPopup>
    </Select>
  );
}

describe("Select trigger", () => {
  it("renders a combobox trigger", () => {
    const { getByRole } = render(<TestSelect />);
    expect(getByRole("combobox")).toBeInTheDocument();
  });

  it("shows placeholder text", () => {
    const { getByRole } = render(<TestSelect />);
    expect(getByRole("combobox")).toHaveTextContent("Pick a model");
  });

  it("sm size trigger includes h-8 class", () => {
    const { getByRole } = render(<TestSelect size="sm" />);
    expect(getByRole("combobox").className).toContain("h-8");
  });

  it("default size trigger includes h-9 class", () => {
    const { getByRole } = render(<TestSelect size="default" />);
    expect(getByRole("combobox").className).toContain("h-9");
  });

  it("lg size trigger includes h-10 class", () => {
    const { getByRole } = render(<TestSelect size="lg" />);
    expect(getByRole("combobox").className).toContain("h-10");
  });

  it("trigger has aria-haspopup=listbox", () => {
    const { getByRole } = render(<TestSelect />);
    expect(getByRole("combobox")).toHaveAttribute("aria-haspopup", "listbox");
  });

  it("trigger starts with aria-expanded=false", () => {
    const { getByRole } = render(<TestSelect />);
    expect(getByRole("combobox")).toHaveAttribute("aria-expanded", "false");
  });
});

describe("Select popup", () => {
  it("draws the shared translucent surface", async () => {
    const { findByRole } = render(<TestSelect defaultOpen />);
    const listbox = await findByRole("listbox");
    const popup = listbox.closest("[data-slot=select-content]") ?? listbox;
    for (const cls of [
      "rounded-3xl",
      "bg-menu-popup-bg/70",
      "backdrop-blur-2xl",
      "backdrop-saturate-150",
      "p-1",
    ]) {
      expect(popup.className).toContain(cls);
    }
    expect(popup.className).not.toContain("before:backdrop-blur-2xl");
  });

  it("gives options the menu row recipe and a trailing gold check", async () => {
    const { findByRole } = render(<TestSelect defaultOpen />);
    const option = await findByRole("option", { name: "Claude Opus" });
    for (const cls of ["rounded-2xl", "px-3", "py-2", "pr-9", "gap-2.5"]) {
      expect(option.className).toContain(cls);
    }
    const mark = option.querySelector("span.absolute");
    expect(mark?.className).toContain("right-3");
    expect(mark?.className).toContain("text-accent-text");
  });

  it("names a group in the menu label style", async () => {
    const { findByText } = render(<TestSelect defaultOpen />);
    const label = await findByText("Anthropic");
    expect(label.className).toContain("uppercase");
    expect(label.className).toContain("text-menu-group-label-fg");
  });

  it("passes axe while open", async () => {
    const { findByRole } = render(<TestSelect defaultOpen />);
    await expectNoAxe(await findByRole("listbox"));
  });
});
