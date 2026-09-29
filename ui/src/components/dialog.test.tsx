// @vitest-environment jsdom
/**
 * Render tests for Dialog and its parts.
 *
 * Covers the coss naming (DialogPopup, not DialogContent), opening, the
 * header, body and footer, the title and description, the close button, the
 * mockup's dialog recipe, the wide size, an underline tab row inside the
 * dialog, and axe in the open state.
 */

import { render, cleanup } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, afterEach } from "vitest";
import { expectNoAxe } from "../test/expect-no-axe";
import {
  Dialog,
  DialogTrigger,
  DialogPopup,
  DialogHeader,
  DialogPanel,
  DialogFooter,
  DialogTitle,
  DialogDescription,
  DialogClose,
} from "./dialog";
import { Tabs, TabsList, TabsTab, TabsPanel } from "./tabs";

afterEach(cleanup);

// Renders the dialog open through the controlled prop.
function OpenDialog({
  children,
  size,
}: {
  children?: React.ReactNode;
  size?: "default" | "wide";
}) {
  return (
    <Dialog open>
      <DialogPopup size={size}>
        <DialogHeader>
          <DialogTitle>Edit agent</DialogTitle>
          <DialogDescription>Changes apply to the next run.</DialogDescription>
        </DialogHeader>
        <DialogPanel>{children ?? <p>Release captain</p>}</DialogPanel>
        <DialogFooter>
          <DialogClose render={<button type="button" />}>Cancel</DialogClose>
        </DialogFooter>
      </DialogPopup>
    </Dialog>
  );
}

describe("Dialog open state", () => {
  it("renders the dialog popup with dialog role", () => {
    const { getByRole } = render(<OpenDialog />);
    expect(getByRole("dialog")).toBeInTheDocument();
  });

  it("names the dialog by its title", () => {
    const { getByRole } = render(<OpenDialog />);
    expect(getByRole("dialog", { name: "Edit agent" })).toBeInTheDocument();
  });

  it("renders DialogDescription", () => {
    const { getByText } = render(<OpenDialog />);
    expect(getByText("Changes apply to the next run.")).toBeInTheDocument();
  });

  it("renders DialogPanel children", () => {
    const { getByText } = render(
      <OpenDialog>
        <span>Panel content</span>
      </OpenDialog>,
    );
    expect(getByText("Panel content")).toBeInTheDocument();
  });

  it("renders DialogClose button", () => {
    const { getByRole } = render(<OpenDialog />);
    expect(getByRole("button", { name: "Cancel" })).toBeInTheDocument();
  });

  it("has an accessible close icon button (sr-only label)", () => {
    const { getByRole } = render(<OpenDialog />);
    const close = getByRole("button", { name: "Close" });
    expect(close.querySelector("svg")).not.toBeNull();
    expect(close.className).toContain("size-8");
  });

  it("passes axe while open", async () => {
    const { getByRole } = render(<OpenDialog />);
    await expectNoAxe(getByRole("dialog"));
  });
});

describe("Dialog recipe", () => {
  it("drops the box from the top centre with the dialog tokens", () => {
    const { getByRole } = render(<OpenDialog />);
    const cls = getByRole("dialog").className;
    for (const want of [
      "top-[70px]",
      "left-1/2",
      "-translate-x-1/2",
      "max-w-[600px]",
      "rounded-2xl",
      "border-dialog-border",
      "bg-dialog-bg",
      "overflow-hidden",
      "flex-col",
      "data-[starting-style]:opacity-0",
    ]) {
      expect(cls).toContain(want);
    }
    expect(cls).not.toContain("top-1/2");
    expect(cls).not.toContain("p-6");
  });

  it("widens to 820px with size wide", () => {
    const { getByRole } = render(<OpenDialog size="wide" />);
    const popup = getByRole("dialog");
    expect(popup.className).toContain("max-w-[820px]");
    expect(popup.className).not.toContain("max-w-[600px]");
    expect(popup).toHaveAttribute("data-size", "wide");
  });

  it("blurs the scrim", () => {
    render(<OpenDialog />);
    const scrim = document.querySelector<HTMLElement>(".bg-overlay-scrim");
    expect(scrim?.className).toContain("backdrop-blur-[3px]");
  });

  it("rules the header and footer and scrolls the body", () => {
    const { getByText } = render(<OpenDialog />);
    const header = getByText("Edit agent").parentElement;
    expect(header?.className).toContain("border-b");
    expect(header?.className).toContain("pl-[18px]");
    expect(header?.className).toContain("pr-12");
    const body = getByText("Release captain").parentElement;
    expect(body?.className).toContain("max-h-[62vh]");
    expect(body?.className).toContain("overflow-y-auto");
    const footer = getByText("Cancel").parentElement;
    expect(footer?.className).toContain("border-t");
    expect(footer?.className).toContain("sm:justify-end");
  });

  it("sets the title at 16px and the description at 12.5px", () => {
    const { getByText } = render(<OpenDialog />);
    expect(getByText("Edit agent").className).toContain("text-base");
    expect(getByText("Changes apply to the next run.").className).toContain(
      "text-[12.5px]",
    );
  });

  it("holds an underline tab row between the header and the body", async () => {
    const { getByRole } = render(
      <Dialog open>
        <DialogPopup>
          <DialogHeader>
            <DialogTitle>Release captain</DialogTitle>
          </DialogHeader>
          <Tabs defaultValue="general">
            <TabsList variant="underline" className="px-[18px]">
              <TabsTab value="general">General</TabsTab>
              <TabsTab value="spend">Spend</TabsTab>
            </TabsList>
            <DialogPanel>
              <TabsPanel value="general">Name and repository</TabsPanel>
              <TabsPanel value="spend">Spend this week</TabsPanel>
            </DialogPanel>
          </Tabs>
        </DialogPopup>
      </Dialog>,
    );
    const list = getByRole("tablist");
    expect(list).toHaveAttribute("data-variant", "underline");
    expect(getByRole("tab", { name: "General" })).toHaveAttribute(
      "aria-selected",
      "true",
    );
    await expectNoAxe(getByRole("dialog"));
  });
});

describe("Dialog trigger", () => {
  it("opens dialog when trigger is clicked", async () => {
    const { queryByRole, getByRole, getByText } = render(
      <Dialog>
        <DialogTrigger render={<button type="button" />}>
          Open dialog
        </DialogTrigger>
        <DialogPopup>
          <DialogTitle>Triggered dialog</DialogTitle>
        </DialogPopup>
      </Dialog>,
    );
    expect(queryByRole("dialog")).not.toBeInTheDocument();
    await userEvent.click(getByRole("button", { name: "Open dialog" }));
    expect(getByRole("dialog")).toBeInTheDocument();
    expect(getByText("Triggered dialog")).toBeInTheDocument();
  });
});

describe("DialogHeader, DialogPanel and DialogFooter standalone", () => {
  it("DialogHeader renders children", () => {
    const { getByText } = render(<DialogHeader>Header content</DialogHeader>);
    expect(getByText("Header content")).toBeInTheDocument();
  });

  it("DialogPanel renders children", () => {
    const { getByText } = render(<DialogPanel>Panel content</DialogPanel>);
    expect(getByText("Panel content")).toBeInTheDocument();
  });

  it("DialogFooter renders children", () => {
    const { getByText } = render(<DialogFooter>Footer</DialogFooter>);
    expect(getByText("Footer")).toBeInTheDocument();
  });
});
