// @vitest-environment jsdom
// Moved from oxagen apps/app/src/ui/stella-mark.test.tsx at ddb85803. The
// wordmark and icon tests stayed behind with those marks.
import { readFileSync } from "node:fs";
import { cleanup, render } from "@testing-library/react";
import { afterEach, describe, expect, it } from "vitest";
import { expectNoAxe } from "../test/expect-no-axe";
import { BRAND_GOLD, STELLA } from "./brand-marks.generated";
import {
  STELLA_SHIMMER,
  STELLA_SPINNER_TRANSFORM,
  StellaSpinner,
} from "./stella-spinner";

afterEach(cleanup);

const MARK = STELLA.icon.parts[0]?.d ?? "";

/** The house spinner this component redraws inline. */
const kitSpinner = readFileSync(
  new URL("../../../spinners/stella-spinner.svg", import.meta.url),
  "utf8",
);

function attr(svg: string, pattern: RegExp): string {
  const found = pattern.exec(svg)?.[1];
  if (found === undefined) throw new Error(`no match for ${pattern.source}`);
  return found;
}

describe("the spinner matches the house spinner", () => {
  it("places the asterisk where the kit's file does", () => {
    expect(STELLA_SPINNER_TRANSFORM).toBe(
      attr(kitSpinner, /<g transform="([^"]+)"><g class="turn">/),
    );
    expect(STELLA.icon.viewBox).toBe(attr(kitSpinner, /viewBox="([^"]+)"/));
  });

  it("turns the kit's asterisk in the kit's gold, under the kit's shimmer", () => {
    expect(MARK).toBe(attr(kitSpinner, /<g class="turn"><path d="([^"]+)"/));
    expect(BRAND_GOLD).toBe(
      attr(kitSpinner, /<g class="turn"><path d="[^"]+" fill="([^"]+)"/),
    );
    expect(STELLA_SHIMMER).toBe(attr(kitSpinner, /stop-color="([^"]+)"/));
  });
});

describe("StellaSpinner", () => {
  it("draws the gold asterisk turning, a light sweeping across it", () => {
    const { container } = render(<StellaSpinner />);
    const svg = container.querySelector("svg");
    expect(svg?.getAttribute("data-mark")).toBe("stella-spinner");
    expect(svg?.getAttribute("viewBox")).toBe(STELLA.icon.viewBox);
    expect(
      container.querySelector(`g[transform="${STELLA_SPINNER_TRANSFORM}"]`),
    ).not.toBeNull();

    const turn = container.querySelector(".ox-stella-turn");
    expect(turn).not.toBeNull();
    const mark = turn?.querySelector(":scope > path");
    expect(mark?.getAttribute("d")).toBe(MARK);
    expect(mark?.getAttribute("fill")).toBe(BRAND_GOLD);
    // The sweep is clipped to the same asterisk, so the light stays on it.
    expect(container.querySelector("clipPath path")?.getAttribute("d")).toBe(
      MARK,
    );
    const stops = Array.from(container.querySelectorAll("stop"));
    expect(stops.map((s) => s.getAttribute("stop-color"))).toEqual([
      STELLA_SHIMMER,
      STELLA_SHIMMER,
      STELLA_SHIMMER,
    ]);
    expect(container.querySelector("rect.ox-stella-sweep")).not.toBeNull();
  });

  it("gives each spinner its own clip and gradient ids, so two on a page do not share one", () => {
    const { container } = render(
      <>
        <StellaSpinner />
        <StellaSpinner />
      </>,
    );
    const clips = Array.from(container.querySelectorAll("clipPath")).map(
      (c) => c.id,
    );
    const gradients = Array.from(
      container.querySelectorAll("linearGradient"),
    ).map((g) => g.id);
    expect(new Set(clips).size).toBe(2);
    expect(new Set(gradients).size).toBe(2);
    const svgs = container.querySelectorAll("svg");
    svgs.forEach((svg) => {
      const gradient = svg.querySelector("linearGradient")?.id ?? "";
      const clip = svg.querySelector("clipPath")?.id ?? "";
      expect(gradient).toMatch(/^stella-spin-sweep-[\w-]+$/);
      expect(svg.querySelector("rect")?.getAttribute("fill")).toBe(
        `url(#${gradient})`,
      );
      expect(svg.querySelector("g[clip-path]")?.getAttribute("clip-path")).toBe(
        `url(#${clip})`,
      );
    });
  });

  it("is hidden from assistive technology without a title, and named by one", async () => {
    const hidden = render(<StellaSpinner />);
    expect(
      hidden.container.querySelector("svg")?.getAttribute("aria-hidden"),
    ).toBe("true");
    await expectNoAxe(hidden.container);
    cleanup();

    const { getByRole, container } = render(
      <StellaSpinner title="stella is thinking" />,
    );
    expect(getByRole("img", { name: "stella is thinking" })).toBeTruthy();
    await expectNoAxe(container);
  });
});
