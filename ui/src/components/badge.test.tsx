// @vitest-environment jsdom
/**
 * badge.test.tsx — render tests for the Badge component.
 *
 * Covers: variant → class, size → class, children forwarding, render-prop.
 */

import { cleanup, render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it } from "vitest";
import { expectNoAxe } from "../test/expect-no-axe";
import { Badge, badgeVariants } from "./badge";

afterEach(cleanup);

// ── Variant map ─────────────────────────────────────────────────────────────

describe("badgeVariants — class map", () => {
  it("default variant is the outlined ink chip (border-current, transparent bg)", () => {
    const cls = badgeVariants({});
    expect(cls).toContain("border-current");
    expect(cls).toContain("bg-transparent");
    expect(cls).toContain("text-foreground");
    // Never a filled primary/secondary surface, never monospace.
    expect(cls).not.toContain("bg-primary");
    expect(cls).not.toContain("bg-secondary");
    expect(cls).not.toContain("font-mono");
  });
  it("secondary variant includes bg-secondary", () => {
    expect(badgeVariants({ variant: "secondary" })).toContain("bg-secondary");
  });
  it("destructive variant includes bg-destructive", () => {
    expect(badgeVariants({ variant: "destructive" })).toContain(
      "bg-destructive",
    );
  });
  it("outline variant aliases the default outlined ink chip", () => {
    const cls = badgeVariants({ variant: "outline" });
    expect(cls).toContain("border-current");
    expect(cls).toContain("bg-transparent");
    expect(cls).toContain("text-foreground");
  });
  it("muted variant includes bg-muted", () => {
    expect(badgeVariants({ variant: "muted" })).toContain("bg-muted");
  });
  it("info variant includes bg-info", () => {
    expect(badgeVariants({ variant: "info" })).toContain("bg-info");
  });
  it("success variant includes bg-success", () => {
    expect(badgeVariants({ variant: "success" })).toContain("bg-success");
  });
  it("warning variant includes bg-warning", () => {
    expect(badgeVariants({ variant: "warning" })).toContain("bg-warning");
  });
  it("error variant maps to the bg-error status token", () => {
    expect(badgeVariants({ variant: "error" })).toContain("bg-error");
  });
  it("soft status variants mix the ink at 42% on the border and 11% behind", () => {
    const cls = badgeVariants({ variant: "success-soft" });
    expect(cls).toContain("border-success/42");
    expect(cls).toContain("bg-success/11");
    expect(cls).toContain("text-success-ink");
    expect(badgeVariants({ variant: "warning-soft" })).toContain(
      "text-warning-ink",
    );
    expect(badgeVariants({ variant: "error-soft" })).toContain(
      "text-error-ink",
    );
    expect(badgeVariants({ variant: "info-soft" })).toContain("text-info-ink");
    expect(badgeVariants({ variant: "proven-soft" })).toContain(
      "bg-proven/11",
    );
  });
  it("critical-soft takes the heavier 12% wash", () => {
    const cls = badgeVariants({ variant: "critical-soft" });
    expect(cls).toContain("border-critical/42");
    expect(cls).toContain("bg-critical/12");
    expect(cls).toContain("text-critical-ink");
  });
  it("the neutral variants sit on the wash with the hairline", () => {
    expect(badgeVariants({ variant: "quiet" })).toContain("bg-hl");
    expect(badgeVariants({ variant: "quiet" })).toContain(
      "text-muted-foreground",
    );
    expect(badgeVariants({ variant: "chip" })).toContain("border-border");
    expect(badgeVariants({ variant: "chip" })).toContain("font-normal");
    expect(badgeVariants({ variant: "label" })).toContain("rounded-full");
  });
  it("base classes follow the mockup's .b and size embedded icons", () => {
    const cls = badgeVariants({});
    expect(cls).toContain("font-semibold");
    expect(cls).toContain("tracking-[0.02em]");
    expect(cls).toContain("whitespace-nowrap");
    expect(cls).toContain("[&_svg]:size-3");
  });

  it("sm size includes text-[10px]", () => {
    expect(badgeVariants({ size: "sm" })).toContain("text-[10px]");
  });
  it("default size is 11px with 7px sides", () => {
    const cls = badgeVariants({ size: "default" });
    expect(cls).toContain("text-[11px]");
    expect(cls).toContain("px-[7px]");
  });
  it("lg size includes text-xs with px-2.5", () => {
    const cls = badgeVariants({ size: "lg" });
    expect(cls).toContain("px-2.5");
    expect(cls).toContain("text-xs");
  });
});

// ── Render tests ─────────────────────────────────────────────────────────────

describe("Badge — render", () => {
  it("renders children inside a span by default", () => {
    render(<Badge>New</Badge>);
    expect(screen.getByText("New")).toBeInTheDocument();
  });

  it("applies variant class", () => {
    render(<Badge variant="secondary">Beta</Badge>);
    const el = screen.getByText("Beta");
    expect(el.className).toContain("bg-secondary");
  });

  it("applies size class", () => {
    render(<Badge size="sm">Sm</Badge>);
    const el = screen.getByText("Sm");
    expect(el.className).toContain("text-[10px]");
  });

  it("merges custom className", () => {
    render(<Badge className="my-badge">Tag</Badge>);
    const el = screen.getByText("Tag");
    expect(el.className).toContain("my-badge");
  });

  it("dot renders a leading currentColor dot", () => {
    render(
      <Badge variant="success-soft" dot>
        Active
      </Badge>,
    );
    const badge = screen.getByText("Active").closest("span");
    const dot = badge?.querySelector(".rounded-full.bg-current");
    expect(dot).not.toBeNull();
    expect(dot).toHaveAttribute("aria-hidden", "true");
    expect(dot?.className).toContain("size-[5px]");
  });

  it("a label pill wins the rounded corner over the base", () => {
    render(<Badge variant="label">Security</Badge>);
    const el = screen.getByText("Security");
    expect(el.className).toContain("rounded-full");
    expect(el.className).not.toContain("rounded-md");
  });

  it("no dot by default", () => {
    render(<Badge>Plain</Badge>);
    const badge = screen.getByText("Plain");
    expect(badge.querySelector(".bg-current")).toBeNull();
  });

  it("render-prop forwards children through a custom element", () => {
    render(<Badge render={<button type="button" />}>Action</Badge>);
    const btn = screen.getByRole("button", { name: "Action" });
    expect(btn).toBeInTheDocument();
    // Variant classes forwarded to the rendered element
    expect(btn.className).toContain("border-current");
  });

  it("has no axe violations across the variants", async () => {
    const { container } = render(
      <div>
        <Badge>Draft</Badge>
        <Badge variant="success-soft" dot>
          Allowed
        </Badge>
        <Badge variant="critical-soft" dot>
          Critical
        </Badge>
        <Badge variant="quiet">Queued</Badge>
        <Badge variant="chip">oxagen/runtime</Badge>
        <Badge variant="label">Priority 1</Badge>
      </div>,
    );
    await expectNoAxe(container);
  });
});
