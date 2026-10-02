// @vitest-environment jsdom
/**
 * The theme editor as Mac uses it: open the panel, change the gold, and see
 * the page's tokens move; then reach the Update all sites steps.
 */
import { act, cleanup, fireEvent, render, screen } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it } from "vitest";
import { STORAGE_KEY } from "./draft";
import { SHIPPED } from "./theme";
import { ThemeEditor } from "./theme-editor";

const NEW_GOLD = SHIPPED.color.gold === "#C99B2E" ? "#D9B13B" : "#C99B2E";

beforeEach(() => {
  window.localStorage.clear();
});

afterEach(() => {
  cleanup();
  document.documentElement.removeAttribute("style");
});

describe("ThemeEditor", () => {
  it("shows a Theme button that opens the panel", () => {
    render(<ThemeEditor mode="light" />);
    fireEvent.click(screen.getByRole("button", { name: /Theme/ }));
    expect(screen.getByRole("heading", { name: "Primary colour" })).toBeInTheDocument();
    expect(screen.getByRole("heading", { name: "Fonts" })).toBeInTheDocument();
  });

  it("writes a new gold and its neighbours on <html>, and keeps the draft", () => {
    render(<ThemeEditor mode="light" defaultOpen />);
    const gold = screen.getByRole("textbox", { name: "Gold" });
    act(() => {
      fireEvent.change(gold, { target: { value: NEW_GOLD } });
    });
    const root = document.documentElement.style;
    expect(root.getPropertyValue("--ox-gold")).toBe(NEW_GOLD);
    expect(root.getPropertyValue("--ox-gold-deep")).not.toBe("");
    expect(window.localStorage.getItem(STORAGE_KEY)).toContain(NEW_GOLD);
  });

  it("edits the surfaces of the theme the page shows", () => {
    render(<ThemeEditor mode="dark" defaultOpen />);
    const canvas = screen.getByRole("textbox", { name: "Canvas" });
    expect(canvas).toHaveValue(SHIPPED.color.ink.ink);
  });

  it("restores the shipped theme on Reset and on unmount", () => {
    const { unmount } = render(<ThemeEditor mode="light" defaultOpen />);
    act(() => {
      fireEvent.change(screen.getByRole("textbox", { name: "Gold" }), { target: { value: NEW_GOLD } });
    });
    fireEvent.click(screen.getByRole("button", { name: "Reset" }));
    expect(document.documentElement.style.getPropertyValue("--ox-gold")).toBe("");
    act(() => {
      fireEvent.change(screen.getByRole("textbox", { name: "Gold" }), { target: { value: NEW_GOLD } });
    });
    unmount();
    expect(document.documentElement.style.getPropertyValue("--ox-gold")).toBe("");
  });

  it("leads to the steps that send the request to GitHub", () => {
    render(<ThemeEditor mode="light" defaultOpen />);
    expect(screen.getByRole("button", { name: "Update all sites" })).toBeDisabled();
    act(() => {
      fireEvent.change(screen.getByRole("textbox", { name: "Gold" }), { target: { value: NEW_GOLD } });
    });
    fireEvent.click(screen.getByRole("button", { name: "Update all sites" }));
    expect(screen.getByRole("heading", { name: "Steps" })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Open GitHub" })).toBeEnabled();
    expect(screen.getByRole("textbox", { name: "Summary" })).toHaveValue(`Gold ${NEW_GOLD}`);
  });
});
