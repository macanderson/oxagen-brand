// @vitest-environment jsdom
/**
 * Render tests for CommandMenu and its parts.
 *
 * Covers the trigger and its shortcut, opening with focus in the search
 * field, the groups, filtering by name, group and keyword, the empty line,
 * running a command by Enter and by a press, the Cmd+K and Ctrl+K toggle,
 * the controlled state, a disabled row, the phone bar's close button, the
 * mockup's recipe, a menu built from the parts, and axe while open.
 */

import { cleanup, fireEvent, render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { createRef } from "react";
import { afterEach, describe, expect, it, vi } from "vitest";
import { expectNoAxe } from "../test/expect-no-axe";
import {
  CommandMenu,
  CommandMenuClose,
  CommandMenuEmpty,
  CommandMenuInput,
  CommandMenuItem,
  CommandMenuList,
  CommandMenuPopup,
  CommandMenuRoot,
  CommandMenuSearch,
  CommandMenuTrigger,
  type CommandMenuCommandGroup,
} from "./command-menu";

afterEach(cleanup);

// Base UI marks a popup `pointer-events: none` during its entry animation,
// which never resolves in jsdom. Turn user-event's guard off.
const user = userEvent.setup({ pointerEventsCheck: 0 });

const GROUPS: CommandMenuCommandGroup[] = [
  {
    label: "Go to",
    items: [
      { value: "runs", label: "Runs", icon: <svg data-testid="runs-icon" /> },
      { value: "agents", label: "Agents" },
      { value: "spend", label: "Spend", keywords: ["billing"] },
    ],
  },
  {
    label: "Create",
    items: [
      { value: "new-work", label: "New work item" },
      {
        value: "connect",
        label: "Connect an agent",
        detail: "Claude Code, Codex or Stella",
      },
    ],
  },
  {
    label: "Actions",
    items: [{ value: "pause", label: "Pause every live run", disabled: true }],
  },
];

const INPUT = { name: "Search pages and actions" };

function optionNames() {
  return screen.queryAllByRole("option").map((o) => o.textContent);
}

describe("CommandMenuTrigger", () => {
  it("reads as a search button with the shortcut as a key cap", () => {
    const { container } = render(
      <CommandMenu groups={GROUPS}>
        <CommandMenuTrigger />
      </CommandMenu>,
    );
    const trigger = screen.getByRole("button", { name: "Search" });
    expect(trigger).toHaveAttribute("aria-keyshortcuts", "Meta+K Control+K");
    expect(container.querySelector("kbd")).toHaveTextContent("⌘K");
    expect(screen.queryByRole("dialog")).not.toBeInTheDocument();
  });

  it("takes its own words and key cap", () => {
    const { container } = render(
      <CommandMenu groups={GROUPS}>
        <CommandMenuTrigger shortcutLabel="Ctrl K">Find a page</CommandMenuTrigger>
      </CommandMenu>,
    );
    expect(screen.getByRole("button", { name: "Find a page" })).toBeInTheDocument();
    expect(container.querySelector("kbd")).toHaveTextContent("Ctrl K");
  });

  it("opens the menu with focus in the search field", async () => {
    render(
      <CommandMenu groups={GROUPS}>
        <CommandMenuTrigger />
      </CommandMenu>,
    );
    await user.click(screen.getByRole("button", { name: "Search" }));
    expect(screen.getByRole("dialog", { name: "Search" })).toBeInTheDocument();
    await waitFor(() => expect(screen.getByRole("combobox", INPUT)).toHaveFocus());
  });
});

describe("CommandMenu results", () => {
  it("lists every group and its rows", () => {
    render(<CommandMenu groups={GROUPS} defaultOpen />);
    expect(screen.getByRole("group", { name: "Go to" })).toBeInTheDocument();
    expect(screen.getByRole("group", { name: "Create" })).toBeInTheDocument();
    expect(screen.getByRole("group", { name: "Actions" })).toBeInTheDocument();
    expect(screen.getAllByRole("option")).toHaveLength(6);
    expect(screen.getByTestId("runs-icon")).toBeInTheDocument();
  });

  it("filters by a command's name", async () => {
    render(<CommandMenu groups={GROUPS} defaultOpen />);
    await user.type(screen.getByRole("combobox", INPUT), "spend");
    expect(optionNames()).toEqual(["Spend"]);
    expect(screen.queryByRole("group", { name: "Create" })).not.toBeInTheDocument();
  });

  it("lists a whole group when the query names it", async () => {
    render(<CommandMenu groups={GROUPS} defaultOpen />);
    await user.type(screen.getByRole("combobox", INPUT), "create");
    expect(optionNames()).toEqual([
      "New work item",
      "Connect an agentClaude Code, Codex or Stella",
    ]);
  });

  it("matches a keyword and a detail", async () => {
    render(<CommandMenu groups={GROUPS} defaultOpen />);
    const input = screen.getByRole("combobox", INPUT);
    await user.type(input, "billing");
    expect(optionNames()).toEqual(["Spend"]);
    await user.clear(input);
    await user.type(input, "codex");
    expect(optionNames()).toEqual(["Connect an agentClaude Code, Codex or Stella"]);
  });

  it("says so when nothing matches", async () => {
    render(<CommandMenu groups={GROUPS} defaultOpen />);
    expect(screen.getByRole("status")).toBeEmptyDOMElement();
    await user.type(screen.getByRole("combobox", INPUT), "zzz");
    expect(screen.queryAllByRole("option")).toHaveLength(0);
    expect(screen.getByRole("status")).toHaveTextContent("Nothing matches.");
  });

  it("opens filtered by defaultQuery", () => {
    render(<CommandMenu groups={GROUPS} defaultOpen defaultQuery="agent" />);
    expect(screen.getByRole("combobox", INPUT)).toHaveValue("agent");
    expect(optionNames()).toEqual([
      "Agents",
      "Connect an agentClaude Code, Codex or Stella",
    ]);
  });

  it("takes its own placeholder, label, title and empty line", () => {
    render(
      <CommandMenu
        groups={GROUPS}
        defaultOpen
        defaultQuery="zzz"
        title="Jump"
        inputLabel="Jump to a page"
        placeholder="Type a page"
        emptyMessage="No page by that name."
      />,
    );
    expect(screen.getByRole("dialog", { name: "Jump" })).toBeInTheDocument();
    expect(screen.getByRole("combobox", { name: "Jump to a page" })).toHaveAttribute(
      "placeholder",
      "Type a page",
    );
    expect(screen.getByRole("status")).toHaveTextContent("No page by that name.");
  });
});

describe("Running a command", () => {
  it("runs the first match on Enter and closes", async () => {
    const onSelect = vi.fn();
    render(<CommandMenu groups={GROUPS} defaultOpen onSelect={onSelect} />);
    await user.type(screen.getByRole("combobox", INPUT), "spend{Enter}");
    expect(onSelect).toHaveBeenCalledOnce();
    expect(onSelect.mock.calls[0]?.[0]).toMatchObject({ value: "spend" });
    await waitFor(() => expect(screen.queryByRole("dialog")).not.toBeInTheDocument());
  });

  it("calls the menu's and the command's handlers on a press", async () => {
    const onSelect = vi.fn();
    const onRun = vi.fn();
    const groups: CommandMenuCommandGroup[] = [
      { label: "Go to", items: [{ value: "runs", label: "Runs", onSelect: onRun }] },
    ];
    render(<CommandMenu groups={groups} defaultOpen onSelect={onSelect} />);
    await user.click(screen.getByRole("option", { name: "Runs" }));
    expect(onSelect).toHaveBeenCalledWith(groups[0]?.items[0]);
    expect(onRun).toHaveBeenCalledOnce();
    await waitFor(() => expect(screen.queryByRole("dialog")).not.toBeInTheDocument());
  });

  it("only closes when nothing handles the command", async () => {
    render(<CommandMenu groups={GROUPS} defaultOpen />);
    await user.click(screen.getByRole("option", { name: "Agents" }));
    await waitFor(() => expect(screen.queryByRole("dialog")).not.toBeInTheDocument());
  });

  it("does not run a disabled command", async () => {
    const onSelect = vi.fn();
    render(<CommandMenu groups={GROUPS} defaultOpen onSelect={onSelect} />);
    const row = screen.getByRole("option", { name: "Pause every live run" });
    expect(row).toHaveAttribute("data-disabled");
    await user.click(row);
    expect(onSelect).not.toHaveBeenCalled();
    expect(screen.getByRole("dialog")).toBeInTheDocument();
  });
});

describe("Opening and closing", () => {
  it("toggles on Cmd+K and Ctrl+K", async () => {
    const onOpenChange = vi.fn();
    render(<CommandMenu groups={GROUPS} onOpenChange={onOpenChange} />);
    fireEvent.keyDown(document, { key: "k", metaKey: true });
    expect(await screen.findByRole("dialog")).toBeInTheDocument();
    expect(onOpenChange).toHaveBeenLastCalledWith(true);
    fireEvent.keyDown(document, { key: "K", ctrlKey: true });
    await waitFor(() => expect(screen.queryByRole("dialog")).not.toBeInTheDocument());
    expect(onOpenChange).toHaveBeenLastCalledWith(false);
  });

  it("ignores another key with the modifier, and Cmd+K when the shortcut is off", () => {
    const { unmount } = render(<CommandMenu groups={GROUPS} />);
    fireEvent.keyDown(document, { key: "j", metaKey: true });
    fireEvent.keyDown(document, { key: "k" });
    expect(screen.queryByRole("dialog")).not.toBeInTheDocument();
    unmount();
    render(<CommandMenu groups={GROUPS} shortcut={false} />);
    fireEvent.keyDown(document, { key: "k", metaKey: true });
    expect(screen.queryByRole("dialog")).not.toBeInTheDocument();
  });

  it("asks the owner to close on Escape when controlled", async () => {
    const onOpenChange = vi.fn();
    render(<CommandMenu groups={GROUPS} open onOpenChange={onOpenChange} />);
    await user.click(screen.getByRole("combobox", INPUT));
    await user.keyboard("{Escape}");
    expect(onOpenChange).toHaveBeenCalledWith(false);
    expect(screen.getByRole("dialog")).toBeInTheDocument();
  });

  it("closes from the phone bar's close button", async () => {
    render(<CommandMenu groups={GROUPS} defaultOpen />);
    const close = screen.getByRole("button", { name: "Close" });
    expect(close.parentElement).toHaveClass("md:hidden");
    await user.click(close);
    await waitFor(() => expect(screen.queryByRole("dialog")).not.toBeInTheDocument());
  });
});

describe("CommandMenu recipe", () => {
  it("draws the translucent floating surface 70px from the top", () => {
    render(<CommandMenu groups={GROUPS} defaultOpen />);
    expect(screen.getByRole("dialog")).toHaveClass(
      "rounded-3xl",
      "bg-menu-popup-bg/70",
      "backdrop-blur-2xl",
      "backdrop-saturate-150",
      "p-1",
      "top-[70px]",
      "max-w-[600px]",
      "data-[starting-style]:opacity-0",
    );
  });

  it("dims the page with an unblurred scrim", () => {
    render(<CommandMenu groups={GROUPS} defaultOpen />);
    const scrim = Array.from(document.body.querySelectorAll("div")).find((el) =>
      el.classList.contains("bg-overlay-scrim/50"),
    );
    expect(scrim).toBeDefined();
    expect(scrim?.className).not.toContain("backdrop-blur");
  });

  it("rounds the field and rows one step in and caps the group names", () => {
    render(<CommandMenu groups={GROUPS} defaultOpen />);
    expect(screen.getByRole("combobox", INPUT)).toHaveClass("rounded-2xl", "text-sm");
    expect(screen.getByRole("option", { name: "Runs" })).toHaveClass(
      "rounded-2xl",
      "px-3",
      "py-2",
      "gap-2.5",
    );
    expect(screen.getByText("Go to")).toHaveClass(
      "uppercase",
      "text-menu-group-label-fg",
    );
    expect(screen.getByText("Claude Code, Codex or Stella")).toHaveClass(
      "font-mono",
      "text-[11px]",
    );
  });

  it("passes axe open with results", async () => {
    render(<CommandMenu groups={GROUPS} defaultOpen />);
    await expectNoAxe(screen.getByRole("dialog"));
  });

  it("passes axe open with no result", async () => {
    render(<CommandMenu groups={GROUPS} defaultOpen defaultQuery="zzz" />);
    await expectNoAxe(screen.getByRole("dialog"));
  });
});

describe("A menu built from the parts", () => {
  const PAGES = ["Runs", "Agents", "Steering"];

  function PartsMenu({ initialFocus }: { initialFocus?: boolean }) {
    return (
      <CommandMenuRoot defaultOpen>
        <CommandMenuPopup title="Jump to" initialFocus={initialFocus}>
          <CommandMenuSearch open inline items={PAGES}>
            <CommandMenuInput aria-label="Jump to a page" />
            <CommandMenuList aria-label="Pages">
              {(page: string) => (
                <CommandMenuItem key={page} value={page}>
                  {page}
                </CommandMenuItem>
              )}
            </CommandMenuList>
            <CommandMenuEmpty>No page</CommandMenuEmpty>
          </CommandMenuSearch>
          <CommandMenuClose>Done</CommandMenuClose>
        </CommandMenuPopup>
      </CommandMenuRoot>
    );
  }

  it("composes a dialog named by its title with the search field focused", async () => {
    render(<PartsMenu />);
    expect(screen.getByRole("dialog", { name: "Jump to" })).toBeInTheDocument();
    expect(screen.getAllByRole("option")).toHaveLength(3);
    await waitFor(() =>
      expect(screen.getByRole("combobox", { name: "Jump to a page" })).toHaveFocus(),
    );
  });

  it("keeps the caller's initialFocus", async () => {
    render(<PartsMenu initialFocus={false} />);
    const input = screen.getByRole("combobox", { name: "Jump to a page" });
    await new Promise((resolve) => setTimeout(resolve, 20));
    expect(input).not.toHaveFocus();
  });

  it("falls back to the first control when it holds no search field", async () => {
    render(
      <CommandMenuRoot defaultOpen>
        <CommandMenuPopup>
          <p>Loading commands</p>
        </CommandMenuPopup>
      </CommandMenuRoot>,
    );
    const dialog = screen.getByRole("dialog", { name: "Search" });
    await waitFor(() =>
      expect(dialog).toContainElement(document.activeElement as HTMLElement),
    );
  });

  it("forwards its ref to the popup", () => {
    const ref = createRef<HTMLDivElement>();
    render(
      <CommandMenuRoot defaultOpen>
        <CommandMenuPopup ref={ref}>
          <p>Loading commands</p>
        </CommandMenuPopup>
      </CommandMenuRoot>,
    );
    expect(ref.current).toBe(screen.getByRole("dialog"));
  });
});
