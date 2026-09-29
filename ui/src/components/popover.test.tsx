// @vitest-environment jsdom
/**
 * Render tests for Popover and its parts: the popup inside an open popover,
 * the title, description, trigger and close, and the shared floating
 * surface. The kit uses the coss and Base UI name `PopoverPopup`, not
 * `PopoverContent`.
 */

import { render, cleanup } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import type { ReactNode } from "react";
import { describe, expect, it, afterEach } from "vitest";
import { expectNoAxe } from "../test/expect-no-axe";
import {
  Popover,
  PopoverTrigger,
  PopoverClose,
  PopoverPopup,
  PopoverTitle,
  PopoverDescription,
} from "./popover";

afterEach(cleanup);

// Helper: a pre-opened popover to avoid needing pointer interactions with the portal.
function OpenPopover({ children }: { children?: ReactNode }) {
  return (
    <Popover open>
      <PopoverPopup>
        {children ?? (
          <>
            <PopoverTitle>Popover title</PopoverTitle>
            <PopoverDescription>Popover description text.</PopoverDescription>
          </>
        )}
      </PopoverPopup>
    </Popover>
  );
}

describe("Popover open state", () => {
  it("renders PopoverPopup content when open", () => {
    const { getByText } = render(<OpenPopover />);
    expect(getByText("Popover title")).toBeInTheDocument();
    expect(getByText("Popover description text.")).toBeInTheDocument();
  });

  it("renders custom children inside PopoverPopup", () => {
    const { getByText } = render(
      <OpenPopover>
        <p>Custom content</p>
      </OpenPopover>,
    );
    expect(getByText("Custom content")).toBeInTheDocument();
  });

  it("PopoverTitle is rendered in the document", () => {
    const { getByText } = render(
      <Popover open>
        <PopoverPopup>
          <PopoverTitle>My Title</PopoverTitle>
        </PopoverPopup>
      </Popover>,
    );
    expect(getByText("My Title")).toBeInTheDocument();
  });

  it("PopoverDescription is rendered in the document", () => {
    const { getByText } = render(
      <Popover open>
        <PopoverPopup>
          <PopoverDescription>Some helpful text.</PopoverDescription>
        </PopoverPopup>
      </Popover>,
    );
    expect(getByText("Some helpful text.")).toBeInTheDocument();
  });
});

describe("Popover trigger", () => {
  it("opens when trigger is clicked", async () => {
    const { getByRole, getByText, queryByText } = render(
      <Popover>
        <PopoverTrigger render={<button type="button" />}>
          Open Popover
        </PopoverTrigger>
        <PopoverPopup>
          <PopoverTitle>Triggered Title</PopoverTitle>
        </PopoverPopup>
      </Popover>,
    );
    expect(queryByText("Triggered Title")).not.toBeInTheDocument();
    await userEvent.click(getByRole("button", { name: "Open Popover" }));
    expect(getByText("Triggered Title")).toBeInTheDocument();
  });
});

describe("PopoverClose", () => {
  it("renders a PopoverClose button in the open popover", () => {
    const { getByRole } = render(
      <Popover open>
        <PopoverPopup>
          <PopoverTitle>Closeable</PopoverTitle>
          <PopoverClose render={<button type="button" />}>Dismiss</PopoverClose>
        </PopoverPopup>
      </Popover>,
    );
    expect(getByRole("button", { name: "Dismiss" })).toBeInTheDocument();
  });
});

describe("PopoverPopup className", () => {
  it("merges custom className onto the popup element", () => {
    const { getByText } = render(
      <Popover open>
        <PopoverPopup className="custom-class">
          <PopoverTitle>Styled</PopoverTitle>
        </PopoverPopup>
      </Popover>,
    );
    const title = getByText("Styled");
    // The popup element is an ancestor; check it carries the custom class.
    const popup = title.closest("[class*='custom-class']");
    expect(popup).toBeInTheDocument();
  });
});

describe("PopoverPopup surface", () => {
  it("draws the shared translucent surface with prose padding", () => {
    const { getByRole } = render(
      <Popover open>
        <PopoverPopup>
          <PopoverTitle>Daily spend cap</PopoverTitle>
          <PopoverDescription>Runs pause at the cap.</PopoverDescription>
        </PopoverPopup>
      </Popover>,
    );
    const popup = getByRole("dialog");
    for (const cls of [
      "rounded-3xl",
      "bg-menu-popup-bg/70",
      "backdrop-blur-2xl",
      "backdrop-saturate-150",
      "ring-1",
      "px-4",
      "py-3",
    ]) {
      expect(popup.className).toContain(cls);
    }
    expect(popup.className).not.toContain("border-border");
  });

  it("names the dialog from its title and passes axe", async () => {
    const { getByRole } = render(
      <Popover open>
        <PopoverPopup>
          <PopoverTitle>Daily spend cap</PopoverTitle>
          <PopoverDescription>Runs pause at the cap.</PopoverDescription>
        </PopoverPopup>
      </Popover>,
    );
    const popup = getByRole("dialog", { name: "Daily spend cap" });
    await expectNoAxe(popup);
  });
});
