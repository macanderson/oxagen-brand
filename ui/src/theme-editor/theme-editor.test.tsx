// @vitest-environment jsdom
/**
 * The theme editor as Mac uses it: open the panel, change the gold, and see
 * the page's tokens move; then reach the Update all sites steps.
 */
import { act, cleanup, fireEvent, render, screen, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, beforeEach, describe, expect, it } from "vitest";
import { BRAND_GOLD } from "../components/brand-marks.generated";
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
  document.documentElement.classList.remove("dark", "light");
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

  it("asks its caller to switch the theme when Dark or Light is selected", async () => {
    const asked: string[] = [];
    render(<ThemeEditor mode="light" defaultOpen onModeChange={(mode) => asked.push(mode)} />);
    expect(screen.getByRole("button", { name: "Light" })).toHaveAttribute("aria-pressed", "true");
    await userEvent.click(screen.getByRole("button", { name: "Dark" }));
    expect(asked).toEqual(["dark"]);
  });

  it("switches <html> and the colour fields itself when no caller owns the theme", async () => {
    render(<ThemeEditor mode="light" defaultOpen />);
    expect(screen.getByRole("textbox", { name: "Canvas" })).toHaveValue(SHIPPED.color.paper.paper);
    await userEvent.click(screen.getByRole("button", { name: "Dark" }));
    expect(document.documentElement.classList.contains("dark")).toBe(true);
    expect(screen.getByRole("textbox", { name: "Canvas" })).toHaveValue(SHIPPED.color.ink.ink);
    await userEvent.click(screen.getByRole("button", { name: "Light" }));
    expect(document.documentElement.classList.contains("dark")).toBe(false);
    expect(screen.getByRole("textbox", { name: "Canvas" })).toHaveValue(SHIPPED.color.paper.paper);
  });

  it("shows the wordmark face read-only, and every other role with its picker", () => {
    render(<ThemeEditor mode="light" defaultOpen />);
    const row = screen.getByRole("group", { name: "Wordmark" });
    expect(within(row).getByText(SHIPPED.faces.wordmark.family)).toBeInTheDocument();
    expect(within(row).getByText("oxagen stella")).toBeInTheDocument();
    expect(within(row).getByText(/The wordmark face is fixed/)).toBeInTheDocument();
    expect(within(row).queryByRole("combobox")).toBeNull();
    expect(within(row).queryByRole("textbox")).toBeNull();
    expect(row.querySelector("input")).toBeNull();
    expect(screen.queryByRole("combobox", { name: "Wordmark" })).toBeNull();
    for (const name of ["Marketing headings", "Text", "Code"]) {
      expect(screen.getByRole("combobox", { name })).toBeInTheDocument();
    }
  });

  it("recolours the gold x and the gold asterisk when the gold changes", () => {
    render(<ThemeEditor mode="light" defaultOpen />);
    const row = screen.getByRole("group", { name: "Wordmark" });
    const accents = ["oxagen", "stella"].map((name) =>
      within(row).getByRole("img", { name }).querySelector(`path[fill="${BRAND_GOLD}"]`),
    );
    act(() => {
      fireEvent.change(screen.getByRole("textbox", { name: "Gold" }), { target: { value: NEW_GOLD } });
    });
    // jsdom resolves no var(), so check both halves: each accent paints from
    // --ox-gold, and the editor set --ox-gold to the new gold.
    expect(document.documentElement.style.getPropertyValue("--ox-gold")).toBe(NEW_GOLD);
    for (const accent of accents) {
      expect(accent).not.toBeNull();
      expect((accent as SVGPathElement).style.fill).toBe(`var(--ox-gold, ${BRAND_GOLD})`);
    }
  });

  it("moves the app base on <html> alone, and warns without blocking below 14px", () => {
    render(<ThemeEditor mode="light" defaultOpen />);
    const base = screen.getByRole("slider", { name: "App base" });
    act(() => {
      fireEvent.change(base, { target: { value: "12" } });
    });
    const root = document.documentElement.style;
    // Every app step is calc() over --ox-a-base in house-tokens.css, so the
    // editor writes the base and nothing else for the steps to follow it.
    expect(root.getPropertyValue("--ox-a-base")).toBe("0.75rem");
    expect(root.getPropertyValue("--ox-a-h1")).toBe("");
    expect(root.getPropertyValue("--ox-a-micro")).toBe("");
    expect(screen.getByText(/This base is under 14px/)).toBeInTheDocument();
    const warnings = screen.getByRole("list", { name: "Warnings" });
    expect(within(warnings).getByText(/The app base is 12px/)).toBeInTheDocument();
    expect(screen.queryByText(/The build will refuse/)).toBeNull();
    expect(screen.getByRole("button", { name: "Update all sites" })).toBeEnabled();
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
