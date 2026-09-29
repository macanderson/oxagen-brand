// @vitest-environment jsdom
// Moved from oxagen apps/app/src/ui/badge.test.tsx at ddb85803.
// The one state badge: a tone is a state hue on the ink, the border and the
// wash; the dot is on by default and off for a fact; a data attribute the
// caller passes reaches the element, because every page reads the state off it.
import { cleanup, render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it } from "vitest";
import { expectNoAxe } from "../test/expect-no-axe";
import { TONE_BADGE_TONES, ToneBadge as Badge } from "./tone-badge";

afterEach(cleanup);

describe("Badge", () => {
  it("draws the tone on the ink, the border and the wash, with a dot", () => {
    render(
      <Badge tone="allowed" data-status="live">
        live
      </Badge>,
    );
    const pill = screen.getByText("live");
    expect(pill).toHaveAttribute("data-status", "live");
    expect(pill.className).toContain("text-success");
    expect(pill.className).toContain("border-success/42");
    expect(pill.className).toContain("bg-success/11");
    expect(pill.querySelector("[aria-hidden]")).not.toBeNull();
  });

  it("a quiet, mono badge is a fact: no dot, lowercase, the muted ink", () => {
    render(
      <Badge tone="quiet" dot={false} mono data-tier="harness">
        harness
      </Badge>,
    );
    const pill = screen.getByText("harness");
    expect(pill).toHaveAttribute("data-tier", "harness");
    expect(pill.className).toContain("text-muted-foreground");
    expect(pill.className).toContain("font-mono");
    expect(pill.querySelector("[aria-hidden]")).toBeNull();
  });

  it("gives critical the heavier 12% wash", () => {
    render(<Badge tone="critical">critical</Badge>);
    expect(screen.getByText("critical").className).toContain(
      "bg-critical/12",
    );
  });

  it("pulses the dot for a state happening now", () => {
    render(
      <Badge tone="approval" dot="pulse">
        waiting
      </Badge>,
    );
    const dot = screen.getByText("waiting").querySelector("[data-pulse]");
    expect(dot).toHaveAttribute("data-pulse", "true");
    expect(dot?.className).toContain("motion-reduce:animate-none");
  });

  it("merges a caller's className", () => {
    render(
      <Badge tone="proven" className="ml-2">
        proven
      </Badge>,
    );
    expect(screen.getByText("proven").className).toContain("ml-2");
  });

  it("has no axe violations in any tone", async () => {
    const { container } = render(
      <div>
        {TONE_BADGE_TONES.map((tone) => (
          <Badge key={tone} tone={tone} title={`Run ${tone}`}>
            {tone}
          </Badge>
        ))}
      </div>,
    );
    await expectNoAxe(container);
  });

  it("never paints a state with the gold", () => {
    for (const tone of TONE_BADGE_TONES) {
      const { unmount } = render(<Badge tone={tone}>{tone}</Badge>);
      expect(screen.getByText(tone).className).not.toMatch(/gold|brand|ember/);
      unmount();
    }
  });
});
