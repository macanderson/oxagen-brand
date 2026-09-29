// @vitest-environment jsdom
/**
 * Render tests for Combobox and its parts.
 *
 * Covers the coss naming (ComboboxPopup, not ComboboxContent), the trigger
 * sizes, the placeholder, opening with a search row and items, filtering, the
 * shared floating surface and row recipe, and the empty message, which shows
 * only when nothing matches.
 */

import { render, cleanup } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, afterEach } from "vitest";
import { expectNoAxe } from "../test/expect-no-axe";
import {
  Combobox,
  ComboboxTrigger,
  ComboboxValue,
  ComboboxPopup,
  ComboboxItem,
} from "./combobox";

afterEach(cleanup);

// Base UI portals the popup and marks it `pointer-events: none` during its
// entry animation. In jsdom that animation never resolves, so user-event's
// pointer-events guard blocks typing into the search input, which is
// interactive in a real browser. Turn the guard off.
const user = userEvent.setup({ pointerEventsCheck: 0 });

const REPOS = ["oxagen", "stella", "oxagen-roadmap", "context-graph"];
const EMPTY = "No results found.";

function TestCombobox({
  size,
  defaultOpen,
  defaultValue,
  defaultSearchValue,
}: {
  size?: "sm" | "default" | "lg";
  defaultOpen?: boolean;
  defaultValue?: string;
  defaultSearchValue?: string;
}) {
  return (
    <Combobox defaultOpen={defaultOpen} defaultValue={defaultValue}>
      <ComboboxTrigger size={size}>
        <ComboboxValue placeholder="Pick a repository" />
      </ComboboxTrigger>
      <ComboboxPopup
        searchPlaceholder="Search repositories…"
        defaultSearchValue={defaultSearchValue}
      >
        {REPOS.map((r) => (
          <ComboboxItem key={r} value={r}>
            {r}
          </ComboboxItem>
        ))}
      </ComboboxPopup>
    </Combobox>
  );
}

describe("Combobox trigger", () => {
  it("renders a combobox trigger button", () => {
    const { getByRole } = render(<TestCombobox />);
    expect(getByRole("combobox")).toBeInTheDocument();
  });

  it("shows placeholder text", () => {
    const { getByRole } = render(<TestCombobox />);
    expect(getByRole("combobox")).toHaveTextContent("Pick a repository");
  });

  it("sm size trigger includes h-7 class", () => {
    const { getByRole } = render(<TestCombobox size="sm" />);
    expect(getByRole("combobox").className).toContain("h-7");
  });

  it("default size trigger includes h-8 class", () => {
    const { getByRole } = render(<TestCombobox size="default" />);
    expect(getByRole("combobox").className).toContain("h-8");
  });

  it("lg size trigger includes h-9 class", () => {
    const { getByRole } = render(<TestCombobox size="lg" />);
    expect(getByRole("combobox").className).toContain("h-9");
  });

  it("draws the pill field and a caret", () => {
    const { getByRole } = render(<TestCombobox />);
    const trigger = getByRole("combobox");
    expect(trigger.className).toContain("rounded-4xl");
    expect(trigger.className).toContain("bg-input-bg");
    expect(trigger.querySelector("svg")).not.toBeNull();
  });
});

describe("Combobox popup opens and shows items", () => {
  it("opens popup on trigger click", async () => {
    const { getByRole, getByText } = render(<TestCombobox />);
    await user.click(getByRole("combobox"));
    expect(getByText("oxagen")).toBeInTheDocument();
    expect(getByText("stella")).toBeInTheDocument();
  });

  it("shows search input inside popup", async () => {
    const { getByRole, getByPlaceholderText } = render(<TestCombobox />);
    await user.click(getByRole("combobox"));
    expect(getByPlaceholderText("Search repositories…")).toBeInTheDocument();
  });

  it("renders all items in popup", async () => {
    const { getByRole, getByText } = render(<TestCombobox />);
    await user.click(getByRole("combobox"));
    for (const repo of REPOS) {
      expect(getByText(repo)).toBeInTheDocument();
    }
  });

  it("opens on mount with defaultOpen", async () => {
    const { findByRole } = render(<TestCombobox defaultOpen />);
    expect(await findByRole("listbox")).toBeInTheDocument();
  });
});

describe("Combobox search and filter", () => {
  it("typing in search narrows the visible items (case-insensitive)", async () => {
    const { getByRole, getByText, queryByText, getByPlaceholderText } = render(
      <TestCombobox />,
    );
    await user.click(getByRole("combobox"));
    await user.type(getByPlaceholderText("Search repositories…"), "stel");
    expect(getByText("stella")).toBeInTheDocument();
    expect(queryByText("oxagen")).not.toBeInTheDocument();
    expect(queryByText("context-graph")).not.toBeInTheDocument();
  });

  it("clearing the search restores all items", async () => {
    const { getByRole, getByText, getByPlaceholderText } = render(
      <TestCombobox />,
    );
    await user.click(getByRole("combobox"));
    const searchInput = getByPlaceholderText("Search repositories…");
    await user.type(searchInput, "graph");
    expect(getByText("context-graph")).toBeInTheDocument();
    await user.clear(searchInput);
    for (const repo of REPOS) {
      expect(getByText(repo)).toBeInTheDocument();
    }
  });

  it("search is case-insensitive (uppercase query)", async () => {
    const { getByRole, getByText, queryByText, getByPlaceholderText } = render(
      <TestCombobox />,
    );
    await user.click(getByRole("combobox"));
    await user.type(getByPlaceholderText("Search repositories…"), "STELLA");
    expect(getByText("stella")).toBeInTheDocument();
    expect(queryByText("context-graph")).not.toBeInTheDocument();
  });

  it("no-match search shows no items and the empty message", async () => {
    const { getByRole, queryByText, findByText, getByPlaceholderText } = render(
      <TestCombobox />,
    );
    await user.click(getByRole("combobox"));
    await user.type(getByPlaceholderText("Search repositories…"), "zzz");
    for (const repo of REPOS) {
      expect(queryByText(repo)).not.toBeInTheDocument();
    }
    expect(await findByText(EMPTY)).toBeInTheDocument();
  });

  it("starts filtered with defaultSearchValue", async () => {
    const { findByPlaceholderText, queryByText } = render(
      <TestCombobox defaultOpen defaultSearchValue="road" />,
    );
    const input = await findByPlaceholderText("Search repositories…");
    expect(input).toHaveValue("road");
    expect(queryByText("oxagen-roadmap")).toBeInTheDocument();
    expect(queryByText("stella")).not.toBeInTheDocument();
  });
});

describe("Combobox empty message", () => {
  it("stays silent while options match", async () => {
    const { findByRole, queryByText } = render(<TestCombobox defaultOpen />);
    await findByRole("listbox");
    expect(queryByText(EMPTY)).not.toBeInTheDocument();
  });

  it("speaks through a mounted live region when nothing matches", async () => {
    const { findByText } = render(
      <TestCombobox defaultOpen defaultSearchValue="zzz" />,
    );
    const message = await findByText(EMPTY);
    expect(message).toHaveAttribute("role", "status");
    expect(message.className).toContain("[&:not(:empty)]:py-6");
  });
});

describe("Combobox popup surface", () => {
  it("draws the shared translucent surface", async () => {
    const { findByRole } = render(<TestCombobox defaultOpen />);
    const listbox = await findByRole("listbox");
    const popup = listbox.closest<HTMLElement>(".rounded-3xl");
    expect(popup).not.toBeNull();
    for (const cls of [
      "bg-menu-popup-bg/70",
      "backdrop-blur-2xl",
      "backdrop-saturate-150",
      "ring-1",
      "p-1",
      "w-(--anchor-width)",
      "data-[starting-style]:opacity-0",
    ]) {
      expect(popup?.className).toContain(cls);
    }
    expect(popup?.className).not.toContain("overflow-hidden");
    expect(popup?.className).not.toContain("border-border");
  });

  it("gives options the menu row recipe and a trailing gold check", async () => {
    const { findByRole } = render(
      <TestCombobox defaultOpen defaultValue="stella" />,
    );
    const option = await findByRole("option", { name: "stella" });
    for (const cls of ["rounded-2xl", "px-3", "py-2", "pr-9", "gap-2.5"]) {
      expect(option.className).toContain(cls);
    }
    expect(option.className).toContain("data-[highlighted]:bg-foreground/10");
    expect(option.className).not.toContain("bg-primary");
    const mark = option.querySelector("span.absolute");
    expect(mark?.className).toContain("right-3");
    expect(mark?.className).toContain("text-accent-text");
  });

  it("passes axe while open with results", async () => {
    const { findByRole } = render(<TestCombobox defaultOpen />);
    const listbox = await findByRole("listbox");
    await expectNoAxe(listbox.closest(".rounded-3xl") ?? listbox);
  });

  it("passes axe while open with no result", async () => {
    const { findByText } = render(
      <TestCombobox defaultOpen defaultSearchValue="zzz" />,
    );
    const message = await findByText(EMPTY);
    await expectNoAxe(message.closest(".rounded-3xl") ?? message);
  });
});
