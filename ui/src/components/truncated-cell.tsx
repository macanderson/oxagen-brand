"use client";
// Text that ends in an ellipsis, with its whole value in a hover card. The card
// follows the mockup's `.hcard` (mockups/src/core.js): a mouse or pen that
// rests on clipped text opens it after OPEN_DELAY_MS, and keyboard focus opens
// it at once. Moving from one clipped value to the next, as down a column,
// opens the next card at once. Text that fits shows nothing, and a touch shows
// nothing, because a tap is a press there.
//
// The element carries `data-hover-card`, so the app's page-wide CellOverflow
// skips it and one value never shows two cards.
import * as React from "react";
import { composeRefs } from "../lib/compose-refs";
import { HoverCard, HoverCardContent } from "./hover-card";
import { cn } from "../lib/utils";

/** How long a mouse or pen rests on clipped text before the card opens. */
export const OPEN_DELAY_MS = 500;

/** A card that closed less than this long ago lets the next one open at once. */
export const REOPEN_WINDOW_MS = 300;

/** When the last card on the page closed. Shared, so a column reads quickly. */
let lastClosedAt = Number.NEGATIVE_INFINITY;

/** Anything inside the value that takes focus on its own. */
const FOCUSABLE =
  "a[href], button, input, select, textarea, summary, [tabindex]";

const useIsomorphicLayoutEffect =
  typeof window === "undefined" ? React.useEffect : React.useLayoutEffect;

type TruncatedCellElement = "span" | "div" | "td";

interface TruncatedCellProps extends React.HTMLAttributes<HTMLElement> {
  /** The element to render. A `td` caps its width at `--cell-max`. */
  as?: TruncatedCellElement;
  /**
   * The whole value for the card, for text the element shortens itself. By
   * default the card shows the element's own text.
   */
  value?: string;
}

/** The element's text, one line per block, as the browser lays it out. */
function wholeText(node: HTMLElement): string {
  const text =
    typeof node.innerText === "string" ? node.innerText : node.textContent;
  return (text ?? "")
    .split("\n")
    .map((line) => line.replace(/\s+/g, " ").trim())
    .filter((line) => line !== "")
    .join("\n");
}

/** Whether the node's text runs past its own box. */
function isClipped(node: HTMLElement): boolean {
  return (
    node.scrollWidth > node.clientWidth &&
    (node.textContent ?? "").trim() !== ""
  );
}

type Shown = { text: string; fontFamily: string; fontWeight: string };

const TruncatedCell = React.forwardRef<HTMLElement, TruncatedCellProps>(
  (
    {
      as = "span",
      value,
      className,
      children,
      tabIndex,
      title,
      onPointerEnter,
      onPointerLeave,
      onPointerDown,
      onFocus,
      onBlur,
      ...props
    },
    forwardedRef,
  ) => {
    const nodeRef = React.useRef<HTMLElement | null>(null);
    const timerRef = React.useRef<ReturnType<typeof setTimeout> | undefined>(
      undefined,
    );
    // Set by a press, so the focus the press causes does not open the card.
    const pressedRef = React.useRef(false);
    const shownRef = React.useRef(false);
    const [shown, setShown] = React.useState<Shown | null>(null);
    // A clipped value with nothing focusable inside takes a keyboard stop.
    const [stop, setStop] = React.useState(false);
    const [clipped, setClipped] = React.useState(false);

    const setRefs = React.useMemo(
      () => composeRefs(nodeRef, forwardedRef),
      [forwardedRef],
    );

    const measure = React.useCallback((): boolean => {
      const node = nodeRef.current;
      if (node === null) return false;
      const cut = isClipped(node);
      setClipped(cut);
      setStop(cut && node.querySelector(FOCUSABLE) === null);
      return cut;
    }, []);

    const close = React.useCallback(() => {
      clearTimeout(timerRef.current);
      timerRef.current = undefined;
      if (shownRef.current) lastClosedAt = Date.now();
      shownRef.current = false;
      setShown(null);
    }, []);

    const open = React.useCallback(() => {
      const node = nodeRef.current;
      if (node === null || !node.isConnected) return;
      const style = getComputedStyle(node);
      shownRef.current = true;
      setShown({
        text: value ?? wholeText(node),
        fontFamily: style.fontFamily,
        fontWeight: style.fontWeight,
      });
    }, [value]);

    // Measure after layout, and again whenever the box or its text resizes.
    useIsomorphicLayoutEffect(() => {
      measure();
    }, [measure, children, value]);

    React.useEffect(() => {
      const node = nodeRef.current;
      if (node === null || typeof ResizeObserver === "undefined") return;
      const observer = new ResizeObserver(() => {
        measure();
      });
      observer.observe(node);
      return () => {
        observer.disconnect();
      };
    }, [measure]);

    // While a card is open, the page closes it: Escape, any press, any scroll,
    // and the window losing focus.
    const isOpen = shown !== null;
    React.useEffect(() => {
      if (!isOpen) return;
      const onKeyDown = (event: KeyboardEvent) => {
        if (event.key === "Escape") close();
      };
      document.addEventListener("keydown", onKeyDown, true);
      document.addEventListener("pointerdown", close, true);
      document.addEventListener("scroll", close, true);
      window.addEventListener("blur", close);
      return () => {
        document.removeEventListener("keydown", onKeyDown, true);
        document.removeEventListener("pointerdown", close, true);
        document.removeEventListener("scroll", close, true);
        window.removeEventListener("blur", close);
      };
    }, [isOpen, close]);

    React.useEffect(
      () => () => {
        clearTimeout(timerRef.current);
      },
      [],
    );

    const Comp = as as React.ElementType;

    return (
      <Comp
        ref={setRefs}
        data-slot="truncated-cell"
        data-hover-card=""
        data-clipped={clipped ? "" : undefined}
        title={title}
        tabIndex={tabIndex ?? (stop ? 0 : undefined)}
        className={cn(
          as === "td"
            ? "max-w-[var(--cell-max,20rem)] truncate"
            : "block min-w-0 max-w-full truncate",
          "focus-visible:outline-2 focus-visible:-outline-offset-2 focus-visible:outline-ring",
          className,
        )}
        onPointerEnter={(event: React.PointerEvent<HTMLElement>) => {
          onPointerEnter?.(event);
          // A title already shows the text to a pointer.
          if (event.pointerType === "touch" || title !== undefined) return;
          if (!measure()) return;
          clearTimeout(timerRef.current);
          const soon = Date.now() - lastClosedAt < REOPEN_WINDOW_MS;
          timerRef.current = setTimeout(open, soon ? 0 : OPEN_DELAY_MS);
        }}
        onPointerLeave={(event: React.PointerEvent<HTMLElement>) => {
          onPointerLeave?.(event);
          close();
        }}
        onPointerDown={(event: React.PointerEvent<HTMLElement>) => {
          onPointerDown?.(event);
          pressedRef.current = true;
          // The focus a press causes lands in the same task, before this runs.
          setTimeout(() => {
            pressedRef.current = false;
          }, 0);
          close();
        }}
        onFocus={(event: React.FocusEvent<HTMLElement>) => {
          onFocus?.(event);
          if (pressedRef.current) return;
          if (measure()) {
            clearTimeout(timerRef.current);
            open();
          }
        }}
        onBlur={(event: React.FocusEvent<HTMLElement>) => {
          onBlur?.(event);
          // Focus moving to a link inside the value keeps the card.
          const next = event.relatedTarget;
          if (next instanceof Node && event.currentTarget.contains(next)) return;
          close();
        }}
        {...props}
      >
        {children}
        <HoverCard
          open={isOpen}
          onOpenChange={(next) => {
            if (!next) close();
          }}
        >
          <HoverCardContent
            anchor={nodeRef}
            side="bottom"
            align="start"
            sideOffset={6}
            alignOffset={-16}
            collisionPadding={8}
            role="tooltip"
            data-slot="truncated-cell-card"
            className="pointer-events-none w-auto max-w-[min(420px,calc(100vw-16px))] p-1 text-base leading-[1.45] [overflow-wrap:anywhere]"
          >
            <div
              className="px-3 py-2 whitespace-pre-line"
              style={
                shown
                  ? { fontFamily: shown.fontFamily, fontWeight: shown.fontWeight }
                  : undefined
              }
            >
              {shown?.text}
            </div>
          </HoverCardContent>
        </HoverCard>
      </Comp>
    );
  },
);
TruncatedCell.displayName = "TruncatedCell";

export { TruncatedCell };
export type { TruncatedCellProps, TruncatedCellElement };
