// @vitest-environment jsdom
/**
 * Render tests for Sheet and its parts, including the mockup's drawer recipe
 * and axe in the open state.
 */

import { render, cleanup } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, afterEach } from "vitest";
import { expectNoAxe } from "../test/expect-no-axe";
import {
  Sheet,
  SheetTrigger,
  SheetPopup,
  SheetHeader,
  SheetPanel,
  SheetFooter,
  SheetTitle,
  SheetDescription,
  SheetClose,
} from "./sheet";

afterEach(cleanup);

function OpenSheet({ side }: { side?: "top" | "bottom" | "left" | "right" }) {
  return (
    <Sheet open>
      <SheetPopup side={side}>
        <SheetHeader>
          <SheetTitle>Sheet Title</SheetTitle>
          <SheetDescription>Sheet description.</SheetDescription>
        </SheetHeader>
        <SheetPanel>
          <p>Sheet body content</p>
        </SheetPanel>
        <SheetFooter>
          <SheetClose render={<button type="button" />}>Close Sheet</SheetClose>
        </SheetFooter>
      </SheetPopup>
    </Sheet>
  );
}

describe("Sheet open state", () => {
  it("renders with dialog role when open", () => {
    const { getByRole } = render(<OpenSheet />);
    expect(getByRole("dialog")).toBeInTheDocument();
  });

  it("renders SheetTitle", () => {
    const { getByText } = render(<OpenSheet />);
    expect(getByText("Sheet Title")).toBeInTheDocument();
  });

  it("renders SheetDescription", () => {
    const { getByText } = render(<OpenSheet />);
    expect(getByText("Sheet description.")).toBeInTheDocument();
  });

  it("renders SheetPanel children", () => {
    const { getByText } = render(<OpenSheet />);
    expect(getByText("Sheet body content")).toBeInTheDocument();
  });

  it("renders SheetClose button", () => {
    const { getByRole } = render(<OpenSheet />);
    expect(getByRole("button", { name: "Close Sheet" })).toBeInTheDocument();
  });

  it("has an accessible close icon button", () => {
    const { getByRole } = render(<OpenSheet />);
    const close = getByRole("button", { name: "Close" });
    expect(close.querySelector("svg")).not.toBeNull();
  });

  it("passes axe while open", async () => {
    const { getByRole } = render(<OpenSheet />);
    await expectNoAxe(getByRole("dialog"));
  });
});

describe("Sheet drawer recipe", () => {
  it("opens from the right, up to 580px wide, with a rule on its inner edge", () => {
    const { getByRole } = render(<OpenSheet />);
    const cls = getByRole("dialog").className;
    for (const want of [
      "right-0",
      "w-[min(580px,100%)]",
      "border-l",
      "border-dialog-border",
      "bg-dialog-bg",
      "flex-col",
    ]) {
      expect(cls).toContain(want);
    }
    expect(cls).not.toContain("p-6");
    expect(cls).not.toContain("sm:max-w-sm");
  });

  it("puts the rule on the right edge of a left drawer", () => {
    const { getByRole } = render(<OpenSheet side="left" />);
    const cls = getByRole("dialog").className;
    expect(cls).toContain("left-0");
    expect(cls).toContain("border-r");
  });

  it("rules the header, sets the title at 17px and pads the body", () => {
    const { getByText } = render(<OpenSheet />);
    const title = getByText("Sheet Title");
    expect(title.className).toContain("text-(length:--ox-a-h4)");
    const header = title.parentElement;
    expect(header?.className).toContain("border-b");
    expect(header?.className).toContain("py-3.5");
    expect(header?.className).toContain("pl-4.5");
    const body = getByText("Sheet body content").parentElement;
    for (const want of ["px-4.5", "pt-4", "pb-12", "gap-3", "overflow-y-auto"]) {
      expect(body?.className).toContain(want);
    }
  });
});

describe("Sheet trigger", () => {
  it("opens sheet when trigger is clicked", async () => {
    const { queryByRole, getByRole } = render(
      <Sheet>
        <SheetTrigger render={<button type="button" />}>
          Open Sheet
        </SheetTrigger>
        <SheetPopup>
          <SheetTitle>Triggered Sheet</SheetTitle>
        </SheetPopup>
      </Sheet>,
    );
    expect(queryByRole("dialog")).not.toBeInTheDocument();
    await userEvent.click(getByRole("button", { name: "Open Sheet" }));
    expect(getByRole("dialog")).toBeInTheDocument();
  });
});

describe("SheetHeader, SheetPanel and SheetFooter standalone", () => {
  it("SheetHeader renders children", () => {
    const { getByText } = render(<SheetHeader>Header</SheetHeader>);
    expect(getByText("Header")).toBeInTheDocument();
  });

  it("SheetPanel renders children", () => {
    const { getByText } = render(<SheetPanel>Content</SheetPanel>);
    expect(getByText("Content")).toBeInTheDocument();
  });

  it("SheetFooter renders children", () => {
    const { getByText } = render(<SheetFooter>Footer</SheetFooter>);
    expect(getByText("Footer")).toBeInTheDocument();
  });
});
