// @vitest-environment jsdom
/**
 * stat.test.tsx: render tests for Stat and StatGroup.
 *
 * Covers the label, value and hint slots, the trend arrow and derived intent,
 * the intent override, tone, the loading skeleton, the empty figure, the
 * mockup's tile recipe, and StatGroup's strip and fixed columns.
 */

import { cleanup, render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it } from "vitest";
import { expectNoAxe } from "../test/expect-no-axe";
import { Stat, StatGroup } from "./stat";
import { statStrip, statTile } from "./control-styles";

afterEach(cleanup);

describe("Stat render", () => {
  it("renders label, value, and hint", () => {
    render(<Stat label="Tool calls" value="48,391" hint="last 30 days" />);
    expect(screen.getByText("Tool calls")).toBeInTheDocument();
    expect(screen.getByText("48,391")).toBeInTheDocument();
    expect(screen.getByText("last 30 days")).toBeInTheDocument();
  });

  it("draws the tile from the shared stat recipe", () => {
    const { container } = render(<Stat label="Runs" value="120" />);
    const tile = container.firstChild as HTMLElement;
    expect(tile).toHaveAttribute("data-slot", "stat");
    for (const token of statTile.split(" ")) {
      expect(tile.className).toContain(token);
    }
    expect(screen.getByText("Runs").className).toContain("uppercase");
    expect(screen.getByText("Runs").className).toContain("text-muted-foreground");
  });

  it("value uses tabular numerals at the tile's figure size", () => {
    render(<Stat label="Spend" value="$12.40" />);
    const value = screen.getByText("$12.40");
    expect(value.className).toContain("tabular-nums");
    expect(value.className).toContain("text-(length:--ox-a-h2)");
  });

  it("up trend derives a positive (success) delta with an arrow", () => {
    render(<Stat label="Runs" value="120" delta="+12%" trend="up" />);
    const delta = screen.getByText("+12%").closest("span");
    expect(delta?.className).toContain("text-success-ink");
    expect(delta?.querySelector("svg")).not.toBeNull();
  });

  it("down trend derives a negative (error) delta", () => {
    render(<Stat label="Runs" value="90" delta="-8%" trend="down" />);
    expect(screen.getByText("-8%").closest("span")?.className).toContain(
      "text-error-ink",
    );
  });

  it("flat trend reads neutral", () => {
    render(<Stat label="Agents" value="12" delta="0%" trend="flat" />);
    expect(screen.getByText("0%").closest("span")?.className).toContain(
      "text-muted-foreground",
    );
  });

  it("intent override wins over trend direction (cost going up is bad)", () => {
    render(
      <Stat
        label="Spend"
        value="$99"
        delta="+40%"
        trend="up"
        intent="negative"
      />,
    );
    expect(screen.getByText("+40%").closest("span")?.className).toContain(
      "text-error-ink",
    );
  });

  it("tone tints the value itself", () => {
    render(<Stat label="Open findings" value="3" tone="warning" />);
    expect(screen.getByText("3").className).toContain("text-warning-ink");
  });

  it("hides the icon from assistive tech", () => {
    const { container } = render(
      <Stat label="Runs" value="120" icon={<svg data-testid="icon" />} />,
    );
    expect(
      container.querySelector('[aria-hidden="true"] [data-testid="icon"]'),
    ).not.toBeNull();
  });

  it("loading renders a skeleton instead of the value", () => {
    const { container } = render(<Stat label="Spend" value="$1" loading />);
    expect(screen.queryByText("$1")).toBeNull();
    expect(container.querySelector('[data-slot="stat-skeleton"]')).not.toBeNull();
    expect(container.firstChild).toHaveAttribute("aria-busy", "true");
  });

  it("an empty figure reads the empty text and drops the delta", () => {
    const { container } = render(
      <Stat
        label="Last run"
        value={null}
        empty="None yet"
        delta="+2"
        trend="up"
      />,
    );
    const empty = screen.getByText("None yet");
    expect(empty.className).toContain("text-muted-foreground");
    expect(screen.queryByText("+2")).toBeNull();
    expect(container.firstChild).toHaveAttribute("data-empty");
  });

  it("an empty string counts as no figure", () => {
    render(<Stat label="Last run" value="" empty="None yet" />);
    expect(screen.getByText("None yet")).toBeInTheDocument();
  });

  it("has no axe violations with a trend, a hint and an icon", async () => {
    const { container } = render(
      <Stat
        label="Spend this month"
        value="$1,204.55"
        delta="+12.4%"
        trend="up"
        intent="negative"
        hint="vs last 30 days"
        icon={<svg />}
      />,
    );
    await expectNoAxe(container);
  });
});

describe("StatGroup render", () => {
  it("lays tiles in the shared strip by default", () => {
    const { container } = render(
      <StatGroup>
        <Stat label="A" value="1" />
        <Stat label="B" value="2" />
      </StatGroup>,
    );
    const group = container.firstChild as HTMLElement;
    expect(group).toHaveAttribute("data-slot", "stat-group");
    for (const token of statStrip.split(" ")) {
      expect(group.className).toContain(token);
    }
  });

  it("accepts an explicit column count from md up", () => {
    const { container } = render(
      <StatGroup columns={3}>
        <Stat label="A" value="1" />
        <Stat label="B" value="2" />
        <Stat label="C" value="3" />
      </StatGroup>,
    );
    const group = container.firstChild as HTMLElement;
    expect(group.className).toContain("md:grid-cols-3");
    expect(group.className).toContain("grid-cols-2");
    expect(group.className).not.toContain("auto-fit");
  });

  it("keeps one column when asked for one", () => {
    const { container } = render(
      <StatGroup columns={1}>
        <Stat label="A" value="1" />
      </StatGroup>,
    );
    expect((container.firstChild as HTMLElement).className).toContain(
      "grid-cols-1",
    );
  });

  it("has no axe violations as a strip of four", async () => {
    const { container } = render(
      <StatGroup>
        <Stat label="Runs" value="1,284" />
        <Stat label="Agents" value="12" />
        <Stat label="Mandates" value="7" />
        <Stat label="Last run" value={null} empty="None yet" />
      </StatGroup>,
    );
    await expectNoAxe(container);
  });
});
