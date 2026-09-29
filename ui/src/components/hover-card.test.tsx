// @vitest-environment jsdom
/**
 * Render tests for HoverCard. The card is forced open, so the portalled
 * content renders without waiting on hover delays.
 */
import { render, cleanup } from "@testing-library/react";
import { describe, expect, it, afterEach } from "vitest";
import { expectNoAxe } from "../test/expect-no-axe";
import { HoverCard, HoverCardContent } from "./hover-card";

afterEach(cleanup);

function OpenCard({ className }: { className?: string }) {
  return (
    <HoverCard open>
      <HoverCardContent className={className}>
        <p>Release captain</p>
        <p>Cuts releases and watches the deploy.</p>
      </HoverCardContent>
    </HoverCard>
  );
}

function contentOf(text: string): HTMLElement {
  const node = document.querySelector<HTMLElement>(
    "[data-slot=hover-card-content]",
  );
  if (!node || !node.textContent?.includes(text)) {
    throw new Error("hover card content did not render");
  }
  return node;
}

describe("HoverCard", () => {
  it("renders its content when open", () => {
    const { getByText } = render(<OpenCard />);
    expect(getByText("Release captain")).toBeInTheDocument();
    expect(contentOf("Release captain")).toBeInTheDocument();
  });

  it("draws the shared translucent surface with prose padding", () => {
    render(<OpenCard />);
    const content = contentOf("Release captain");
    for (const cls of [
      "rounded-3xl",
      "bg-menu-popup-bg/70",
      "backdrop-blur-2xl",
      "backdrop-saturate-150",
      "ring-1",
      "w-72",
      "px-4",
      "py-3",
    ]) {
      expect(content.className).toContain(cls);
    }
  });

  it("animates through Base UI styles, not tw-animate classes", () => {
    render(<OpenCard />);
    const cls = contentOf("Release captain").className;
    expect(cls).toContain("data-[starting-style]:opacity-0");
    expect(cls).toContain("duration-[var(--motion-overlay)]");
    for (const unused of ["animate-in", "fade-in-0", "zoom-in-95", "slide-in-from"]) {
      expect(cls).not.toContain(unused);
    }
  });

  it("merges a custom className", () => {
    render(<OpenCard className="w-96" />);
    const cls = contentOf("Release captain").className;
    expect(cls).toContain("w-96");
    expect(cls).not.toContain("w-72");
  });

  it("passes axe while open", async () => {
    render(<OpenCard />);
    await expectNoAxe(contentOf("Release captain"));
  });
});
