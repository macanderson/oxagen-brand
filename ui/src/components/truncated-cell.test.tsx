// @vitest-environment jsdom
// TruncatedCell: clipped text shows its whole value in a hover card after a
// pointer rests on it, or at once on keyboard focus, and text that fits shows
// nothing. jsdom has no layout, so each case stubs the widths a browser would
// measure. Timers stay real, because Base UI's transitions wait on them.
import {
  act,
  cleanup,
  fireEvent,
  render,
  screen,
  waitFor,
} from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it } from "vitest";
import {
  OPEN_DELAY_MS,
  REOPEN_WINDOW_MS,
  TruncatedCell,
} from "./truncated-cell";
import { expectNoAxe } from "../test/expect-no-axe";

const LONG =
  "Watches the release branch and cuts a tag when every required check passes";

/** The widths every truncated cell reports. Other elements keep jsdom's zero. */
const widths = { scroll: 0, client: 0 };

/** Makes each truncated cell measure as `scroll` wide inside a `client` box. */
function measure(scroll: number, client: number) {
  widths.scroll = scroll;
  widths.client = client;
}

function pause(ms: number) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

function cellOf(slot = "truncated-cell"): HTMLElement {
  const node = document.querySelector<HTMLElement>(`[data-slot="${slot}"]`);
  if (node === null) throw new Error(`no ${slot}`);
  return node;
}

beforeEach(async () => {
  for (const key of ["scrollWidth", "clientWidth"] as const) {
    Object.defineProperty(HTMLElement.prototype, key, {
      configurable: true,
      get(this: HTMLElement) {
        if (this.dataset.slot !== "truncated-cell") return 0;
        return key === "scrollWidth" ? widths.scroll : widths.client;
      },
    });
  }
  // A card the last test closed would let the next one open at once.
  await pause(REOPEN_WINDOW_MS + 20);
});

afterEach(async () => {
  await expectNoAxe(document.body);
  cleanup();
  Reflect.deleteProperty(HTMLElement.prototype, "scrollWidth");
  Reflect.deleteProperty(HTMLElement.prototype, "clientWidth");
});

describe("TruncatedCell when clipped", () => {
  it("marks clipped text and gives it a keyboard stop", () => {
    measure(640, 200);
    render(<TruncatedCell>{LONG}</TruncatedCell>);
    const cell = cellOf();
    expect(cell).toHaveAttribute("data-clipped");
    expect(cell).toHaveAttribute("data-hover-card");
    expect(cell).toHaveAttribute("tabindex", "0");
  });

  it("opens the card after the pointer rests, not before", async () => {
    measure(640, 200);
    render(<TruncatedCell>{LONG}</TruncatedCell>);
    fireEvent.pointerEnter(cellOf(), { pointerType: "mouse" });
    expect(screen.queryByRole("tooltip")).toBeNull();
    const card = await screen.findByRole("tooltip");
    expect(card).toHaveTextContent(LONG);
  });

  it("shows the value prop in place of the element's text", async () => {
    measure(640, 200);
    render(
      <TruncatedCell value="run_01J9Z3K4Q2W8XYV5T6R7S8P9M0">
        run_01J9…P9M0
      </TruncatedCell>,
    );
    fireEvent.pointerEnter(cellOf(), { pointerType: "mouse" });
    expect(await screen.findByRole("tooltip")).toHaveTextContent(
      "run_01J9Z3K4Q2W8XYV5T6R7S8P9M0",
    );
  });

  it("closes when the pointer leaves", async () => {
    measure(640, 200);
    render(<TruncatedCell>{LONG}</TruncatedCell>);
    fireEvent.pointerEnter(cellOf(), { pointerType: "mouse" });
    await screen.findByRole("tooltip");
    fireEvent.pointerLeave(cellOf(), { pointerType: "mouse" });
    await waitFor(() => {
      expect(screen.queryByRole("tooltip")).toBeNull();
    });
  });

  it("opens the next card at once after one closes", async () => {
    measure(640, 200);
    render(
      <>
        <TruncatedCell data-testid="first">{LONG}</TruncatedCell>
        <TruncatedCell data-testid="second">{`${LONG} again`}</TruncatedCell>
      </>,
    );
    fireEvent.pointerEnter(screen.getByTestId("first"), {
      pointerType: "mouse",
    });
    await screen.findByRole("tooltip");
    fireEvent.pointerLeave(screen.getByTestId("first"), {
      pointerType: "mouse",
    });
    fireEvent.pointerEnter(screen.getByTestId("second"), {
      pointerType: "mouse",
    });
    // It opens well inside the rest delay, because a card closed a moment ago.
    // The first card may still be leaving, so look for the second among all.
    await waitFor(
      () => {
        const cards = screen.queryAllByRole("tooltip");
        expect(cards.map((card) => card.textContent)).toContain(
          `${LONG} again`,
        );
      },
      { timeout: OPEN_DELAY_MS - 200 },
    );
  });

  it("never opens for a touch", async () => {
    measure(640, 200);
    render(<TruncatedCell>{LONG}</TruncatedCell>);
    fireEvent.pointerEnter(cellOf(), { pointerType: "touch" });
    await pause(OPEN_DELAY_MS + 100);
    expect(screen.queryByRole("tooltip")).toBeNull();
  });

  it("opens at once on keyboard focus and closes on Escape", async () => {
    measure(640, 200);
    render(<TruncatedCell>{LONG}</TruncatedCell>);
    act(() => {
      cellOf().focus();
    });
    expect(await screen.findByRole("tooltip")).toHaveTextContent(LONG);
    fireEvent.keyDown(document, { key: "Escape" });
    await waitFor(() => {
      expect(screen.queryByRole("tooltip")).toBeNull();
    });
  });

  it("does not open on the focus a press causes", async () => {
    measure(640, 200);
    render(<TruncatedCell>{LONG}</TruncatedCell>);
    fireEvent.pointerDown(cellOf(), { pointerType: "mouse" });
    act(() => {
      cellOf().focus();
    });
    await pause(50);
    expect(screen.queryByRole("tooltip")).toBeNull();
  });

  it("leaves the keyboard stop to a link inside the value", () => {
    measure(640, 200);
    render(
      <TruncatedCell>
        <a href="#release-bot">{LONG}</a>
      </TruncatedCell>,
    );
    expect(cellOf()).not.toHaveAttribute("tabindex");
  });

  it("renders a table cell", () => {
    measure(640, 200);
    render(
      <table>
        <tbody>
          <tr>
            <TruncatedCell as="td">{LONG}</TruncatedCell>
          </tr>
        </tbody>
      </table>,
    );
    expect(cellOf().tagName).toBe("TD");
    expect(screen.getByRole("cell")).toHaveTextContent(LONG);
  });
});

describe("TruncatedCell when not clipped", () => {
  it("takes no keyboard stop and no clipped mark", () => {
    measure(120, 200);
    render(<TruncatedCell>Short</TruncatedCell>);
    const cell = cellOf();
    expect(cell).not.toHaveAttribute("data-clipped");
    expect(cell).not.toHaveAttribute("tabindex");
  });

  it("shows no card to a resting pointer", async () => {
    measure(120, 200);
    render(<TruncatedCell>Short</TruncatedCell>);
    fireEvent.pointerEnter(cellOf(), { pointerType: "mouse" });
    await pause(OPEN_DELAY_MS + 100);
    expect(screen.queryByRole("tooltip")).toBeNull();
  });

  it("shows no card on focus", async () => {
    measure(120, 200);
    render(<TruncatedCell tabIndex={0}>Short</TruncatedCell>);
    act(() => {
      cellOf().focus();
    });
    await pause(50);
    expect(screen.queryByRole("tooltip")).toBeNull();
  });
});
