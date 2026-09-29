// @vitest-environment jsdom
/**
 * Tooltip renders the Base UI tooltip and styles the popup through the
 * --tooltip-* token utilities. The tooltip is forced open, so the portalled
 * popup is asserted without waiting on hover delays.
 */
import { render, cleanup } from "@testing-library/react";
import { describe, expect, it, afterEach } from "vitest";
import { expectNoAxe } from "../test/expect-no-axe";
import {
  Tooltip,
  TooltipTrigger,
  TooltipPopup,
  TooltipProvider,
} from "./tooltip";

afterEach(cleanup);

describe("Tooltip", () => {
  it("renders the trigger", () => {
    const { getByText } = render(
      <TooltipProvider>
        <Tooltip>
          <TooltipTrigger>Hover me</TooltipTrigger>
          <TooltipPopup>Tip body</TooltipPopup>
        </Tooltip>
      </TooltipProvider>,
    );
    expect(getByText("Hover me")).toBeInTheDocument();
  });

  it("renders the popup content with --tooltip-* token classes when open", () => {
    const { getByText } = render(
      <TooltipProvider>
        <Tooltip open>
          <TooltipTrigger>Trigger</TooltipTrigger>
          <TooltipPopup>Notifications</TooltipPopup>
        </Tooltip>
      </TooltipProvider>,
    );
    const popup = getByText("Notifications");
    expect(popup).toBeInTheDocument();
    expect(popup.className).toContain("bg-tooltip-bg");
    expect(popup.className).toContain("text-tooltip-fg");
    expect(popup.className).toContain("border-tooltip-border");
  });

  it("merges a custom className onto the popup", () => {
    const { getByText } = render(
      <TooltipProvider>
        <Tooltip open>
          <TooltipTrigger>T</TooltipTrigger>
          <TooltipPopup className="max-w-sm">Body</TooltipPopup>
        </Tooltip>
      </TooltipProvider>,
    );
    expect(getByText("Body").className).toContain("max-w-sm");
    expect(getByText("Body").className).toContain("bg-tooltip-bg");
  });

  it("stays an opaque, small bubble with the overlay radius step and motion", () => {
    const { getByText } = render(
      <TooltipProvider>
        <Tooltip open>
          <TooltipTrigger>Pause</TooltipTrigger>
          <TooltipPopup>Pause the run</TooltipPopup>
        </Tooltip>
      </TooltipProvider>,
    );
    const cls = getByText("Pause the run").className;
    for (const want of [
      "rounded-lg",
      "text-xs",
      "px-2",
      "py-1",
      "origin-(--transform-origin)",
      "data-[starting-style]:opacity-0",
      "data-[instant]:transition-none",
    ]) {
      expect(cls).toContain(want);
    }
    for (const unwanted of ["rounded-md", "backdrop-blur", "bg-tooltip-bg/", "origin-[var"]) {
      expect(cls).not.toContain(unwanted);
    }
  });

  it("passes axe while open", async () => {
    const { getByText } = render(
      <TooltipProvider>
        <Tooltip open>
          <TooltipTrigger>Pause</TooltipTrigger>
          <TooltipPopup>Pause the run</TooltipPopup>
        </Tooltip>
      </TooltipProvider>,
    );
    await expectNoAxe(getByText("Pause the run"));
  });
});
