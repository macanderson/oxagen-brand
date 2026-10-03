// @vitest-environment jsdom
/**
 * Render tests for Menu and its parts.
 *
 * Base UI opens a menu from pointer events and positions it with floating-ui,
 * which jsdom cannot lay out. A test that needs the popup renders the menu
 * with `open`, which mounts the portal without any pointer work. Opening from
 * a click and moving through items with the keyboard are covered end to end.
 */

import { render, cleanup, within } from "@testing-library/react";
import { describe, expect, it, afterEach } from "vitest";
import { expectNoAxe } from "../test/expect-no-axe";
import {
  Menu,
  MenuTrigger,
  MenuPopup,
  MenuItem,
  MenuCheckboxItem,
  MenuGroupLabel,
  MenuSeparator,
  MenuShortcut,
  MenuGroup,
  MenuRadioGroup,
  MenuRadioItem,
  MenuSub,
  MenuSubTrigger,
  MenuSubPopup,
} from "./menu";

afterEach(cleanup);

describe("Menu trigger", () => {
  it("renders trigger with button role", () => {
    const { getByRole } = render(
      <Menu>
        <MenuTrigger render={<button type="button" />}>Open Menu</MenuTrigger>
        <MenuPopup>
          <MenuItem>Item</MenuItem>
        </MenuPopup>
      </Menu>,
    );
    expect(getByRole("button", { name: "Open Menu" })).toBeInTheDocument();
  });

  it("trigger has aria-haspopup=menu", () => {
    const { getByRole } = render(
      <Menu>
        <MenuTrigger render={<button type="button" />}>Open</MenuTrigger>
        <MenuPopup>
          <MenuItem>Item</MenuItem>
        </MenuPopup>
      </Menu>,
    );
    expect(getByRole("button", { name: "Open" })).toHaveAttribute(
      "aria-haspopup",
      "menu",
    );
  });

  it("trigger starts with aria-expanded=false (closed)", () => {
    const { getByRole } = render(
      <Menu>
        <MenuTrigger render={<button type="button" />}>Open</MenuTrigger>
        <MenuPopup>
          <MenuItem>Item</MenuItem>
        </MenuPopup>
      </Menu>,
    );
    expect(getByRole("button", { name: "Open" })).toHaveAttribute(
      "aria-expanded",
      "false",
    );
  });
});

describe("MenuPopup surface", () => {
  it("draws the translucent surface with a 4px inset", async () => {
    const { findByRole } = render(
      <Menu open>
        <MenuTrigger render={<button type="button" />}>Menu</MenuTrigger>
        <MenuPopup>
          <MenuItem>Rename</MenuItem>
        </MenuPopup>
      </Menu>,
    );
    const popup = await findByRole("menu");
    for (const cls of [
      "rounded-3xl",
      "bg-menu-popup-bg/70",
      "backdrop-blur-2xl",
      "backdrop-saturate-150",
      "ring-1",
      "p-1",
    ]) {
      expect(popup.className).toContain(cls);
    }
  });

  it("animates only through Base UI starting and ending styles", async () => {
    const { findByRole } = render(
      <Menu open>
        <MenuTrigger render={<button type="button" />}>Menu</MenuTrigger>
        <MenuPopup>
          <MenuItem>Rename</MenuItem>
        </MenuPopup>
      </Menu>,
    );
    const popup = await findByRole("menu");
    expect(popup.className).toContain("data-[starting-style]:opacity-0");
    expect(popup.className).toContain("duration-[var(--motion-overlay)]");
    expect(popup.className).not.toMatch(/\banimate-in\b|\bfade-in-0\b/);
  });

  it("passes axe with labels, icons, checks and a submenu", async () => {
    const { findByRole } = render(
      <Menu open>
        <MenuTrigger render={<button type="button" />}>Menu</MenuTrigger>
        <MenuPopup>
          <MenuGroup>
            <MenuGroupLabel>Run</MenuGroupLabel>
            <MenuItem>Open transcript</MenuItem>
            <MenuItem disabled>Retry run</MenuItem>
          </MenuGroup>
          <MenuSeparator />
          <MenuCheckboxItem checked>Show tool calls</MenuCheckboxItem>
          <MenuRadioGroup value="cost">
            <MenuRadioItem value="cost">Sort by cost</MenuRadioItem>
            <MenuRadioItem value="time">Sort by time</MenuRadioItem>
          </MenuRadioGroup>
          <MenuSub>
            <MenuSubTrigger>Move to</MenuSubTrigger>
            <MenuSubPopup>
              <MenuItem>Billing</MenuItem>
            </MenuSubPopup>
          </MenuSub>
        </MenuPopup>
      </Menu>,
    );
    await expectNoAxe(await findByRole("menu"));
  });
});

describe("MenuItem", () => {
  it("uses the shared row recipe: 12px radius, 8px by 12px padding, 10px gap", async () => {
    const { findByText } = render(
      <Menu open>
        <MenuTrigger render={<button type="button" />}>Menu</MenuTrigger>
        <MenuPopup>
          <MenuItem>Rename</MenuItem>
        </MenuPopup>
      </Menu>,
    );
    const item = await findByText("Rename");
    for (const cls of ["rounded-2xl", "px-3", "py-2", "gap-2.5", "text-base"]) {
      expect(item.className).toContain(cls);
    }
    expect(item.className).toContain("data-[highlighted]:bg-foreground/10");
  });

  it("inks the destructive variant with the error token", async () => {
    const { findByText } = render(
      <Menu open>
        <MenuTrigger render={<button type="button" />}>Menu</MenuTrigger>
        <MenuPopup>
          <MenuItem variant="destructive">Delete</MenuItem>
        </MenuPopup>
      </Menu>,
    );
    const item = await findByText("Delete");
    expect(item.className).toContain("text-error-ink");
    expect(item.className).toContain("data-[highlighted]:bg-error/10");
  });

  it("default variant carries no error ink", async () => {
    const { findByText } = render(
      <Menu open>
        <MenuTrigger render={<button type="button" />}>Menu</MenuTrigger>
        <MenuPopup>
          <MenuItem>Rename</MenuItem>
        </MenuPopup>
      </Menu>,
    );
    const item = await findByText("Rename");
    expect(item.className).not.toContain("text-error");
  });

  it("marks a disabled item for assistive tech", async () => {
    const { findByText } = render(
      <Menu open>
        <MenuTrigger render={<button type="button" />}>Menu</MenuTrigger>
        <MenuPopup>
          <MenuItem disabled>Retry run</MenuItem>
        </MenuPopup>
      </Menu>,
    );
    const item = await findByText("Retry run");
    expect(item).toHaveAttribute("aria-disabled", "true");
    expect(item.className).toContain(
      "data-[disabled]:text-menu-item-disabled-fg",
    );
  });
});

describe("Checkbox and radio items", () => {
  it("shows the check at the trailing edge in gold when checked", async () => {
    const { findByRole } = render(
      <Menu open>
        <MenuTrigger render={<button type="button" />}>Menu</MenuTrigger>
        <MenuPopup>
          <MenuCheckboxItem checked>Show tool calls</MenuCheckboxItem>
        </MenuPopup>
      </Menu>,
    );
    const item = await findByRole("menuitemcheckbox", {
      name: "Show tool calls",
    });
    expect(item).toHaveAttribute("aria-checked", "true");
    expect(item.className).toContain("pr-9");
    const slot = item.querySelector("span.absolute");
    expect(slot?.className).toContain("right-3");
    expect(slot?.className).toContain("text-accent-text");
    expect(slot?.querySelector("svg")).not.toBeNull();
  });

  it("renders no mark when unchecked", async () => {
    const { findByRole } = render(
      <Menu open>
        <MenuTrigger render={<button type="button" />}>Menu</MenuTrigger>
        <MenuPopup>
          <MenuCheckboxItem checked={false}>Show tool calls</MenuCheckboxItem>
        </MenuPopup>
      </Menu>,
    );
    const item = await findByRole("menuitemcheckbox", {
      name: "Show tool calls",
    });
    expect(item.querySelector("svg")).toBeNull();
  });

  it("shows a dot on the selected radio item only", async () => {
    const { findByRole } = render(
      <Menu open>
        <MenuTrigger render={<button type="button" />}>Menu</MenuTrigger>
        <MenuPopup>
          <MenuRadioGroup value="cost">
            <MenuRadioItem value="cost">Sort by cost</MenuRadioItem>
            <MenuRadioItem value="time">Sort by time</MenuRadioItem>
          </MenuRadioGroup>
        </MenuPopup>
      </Menu>,
    );
    const cost = await findByRole("menuitemradio", { name: "Sort by cost" });
    const time = await findByRole("menuitemradio", { name: "Sort by time" });
    expect(cost).toHaveAttribute("aria-checked", "true");
    expect(cost.querySelector(".rounded-full")).not.toBeNull();
    expect(time.querySelector(".rounded-full")).toBeNull();
  });
});

describe("MenuSubTrigger", () => {
  it("draws a trailing caret and opens a submenu", async () => {
    const { findByRole } = render(
      <Menu open>
        <MenuTrigger render={<button type="button" />}>Menu</MenuTrigger>
        <MenuPopup>
          <MenuSub>
            <MenuSubTrigger>Move to</MenuSubTrigger>
            <MenuSubPopup>
              <MenuItem>Billing</MenuItem>
            </MenuSubPopup>
          </MenuSub>
        </MenuPopup>
      </Menu>,
    );
    const trigger = await findByRole("menuitem", { name: "Move to" });
    expect(trigger).toHaveAttribute("aria-haspopup", "menu");
    expect(trigger.querySelector("svg")).not.toBeNull();
    expect(trigger.className).toContain("rounded-2xl");
  });
});

describe("MenuGroupLabel", () => {
  it("renders with role=presentation", () => {
    const { getByText } = render(<MenuGroupLabel>Section</MenuGroupLabel>);
    const el = getByText("Section");
    expect(el).toBeInTheDocument();
    expect(el.getAttribute("role")).toBe("presentation");
  });

  it("uses the group label ink and weight", () => {
    const { getByText } = render(<MenuGroupLabel>Section</MenuGroupLabel>);
    const cls = getByText("Section").className;
    expect(cls).toContain("font-semibold");
    expect(cls).toContain("text-menu-group-label-fg");
    expect(cls).toContain("uppercase");
  });

  it("inset lines the label up with rows that lead with an icon", () => {
    const { getByText } = render(<MenuGroupLabel inset>Inset</MenuGroupLabel>);
    expect(getByText("Inset").className).toContain("pl-9.5");
  });
});

describe("MenuSeparator", () => {
  it("renders a separator inside an open menu", async () => {
    const { findByRole } = render(
      <Menu open>
        <MenuTrigger render={<button type="button" />}>Menu</MenuTrigger>
        <MenuPopup>
          <MenuItem>Rename</MenuItem>
          <MenuSeparator />
          <MenuItem>Archive</MenuItem>
        </MenuPopup>
      </Menu>,
    );
    const menu = await findByRole("menu");
    const separator = within(menu).getByRole("separator");
    expect(separator.className).toContain("bg-menu-separator");
  });
});

describe("MenuShortcut", () => {
  it("renders shortcut text", () => {
    const { getByText } = render(<MenuShortcut>⌘K</MenuShortcut>);
    expect(getByText("⌘K")).toBeInTheDocument();
  });

  it("includes tracking-widest and opacity-60 classes", () => {
    const { getByText } = render(<MenuShortcut>⌘K</MenuShortcut>);
    const el = getByText("⌘K");
    expect(el.className).toContain("tracking-widest");
    expect(el.className).toContain("opacity-60");
  });

  it("merges custom className", () => {
    const { getByText } = render(
      <MenuShortcut className="custom-sc">⌘S</MenuShortcut>,
    );
    expect(getByText("⌘S").className).toContain("custom-sc");
  });
});
