"use client";
// Moved from oxagen apps/app/src/ui/pagination.tsx at ddb85803.
// shadcn's base-maia pagination (ADR-221), written from
// https://ui.shadcn.com/r/styles/base-maia/pagination.json, and the pager
// every list draws under its rows, laid out as shadcn's data-table pagination
// with the page numbers dropped (the mockup's `.pager`): a Rows per page
// select on the left, and Previous and Next on the right.
//
// Three changes from the registry. Previous and Next are buttons, because a
// list here pages in the browser and a link cannot be disabled. They are
// 32px outline icon buttons, 36px below md, named only by their `aria-label`.
// And every label arrives translated from the caller (INV-12). The fleet's
// pager pages by address and keeps its own links, and draws `RowsField` on
// its left.
import { CaretLeftIcon, CaretRightIcon } from "@phosphor-icons/react";
import {
  type ComponentProps,
  type ReactNode,
  useEffect,
  useId,
  useRef,
} from "react";
import { cn } from "../lib/utils";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "./select";

function Pagination({ className, ...props }: ComponentProps<"nav">) {
  return (
    <nav
      data-slot="pagination"
      className={cn("mx-auto flex w-full justify-center", className)}
      {...props}
    />
  );
}

function PaginationContent({ className, ...props }: ComponentProps<"ul">) {
  return (
    <ul
      data-slot="pagination-content"
      className={cn("flex items-center gap-2", className)}
      {...props}
    />
  );
}

function PaginationItem(props: ComponentProps<"li">) {
  return <li data-slot="pagination-item" {...props} />;
}

/** The mockup's `.iconbtn`: a square outline button that holds one glyph. */
const stepClass = cn(
  "inline-flex size-8 shrink-0 items-center justify-center rounded-lg border border-border bg-card text-[var(--muted)] max-md:size-9",
  "transition-[border-color,color] duration-150",
  "hover:border-rule hover:text-foreground",
  "focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-ring",
  "disabled:cursor-not-allowed disabled:opacity-50 disabled:hover:border-border disabled:hover:text-[var(--muted)]",
);

type StepProps = Omit<ComponentProps<"button">, "children"> & {
  /** The button's name. It shows no text, so this is all a reader hears. */
  text: string;
};

function PaginationPrevious({ className, text, ...props }: StepProps) {
  return (
    <button
      type="button"
      data-slot="pagination-previous"
      aria-label={text}
      className={cn(stepClass, className)}
      {...props}
    >
      <CaretLeftIcon aria-hidden className="size-4 rtl:-scale-x-100" />
    </button>
  );
}

function PaginationNext({ className, text, ...props }: StepProps) {
  return (
    <button
      type="button"
      data-slot="pagination-next"
      aria-label={text}
      className={cn(stepClass, className)}
      {...props}
    >
      <CaretRightIcon aria-hidden className="size-4 rtl:-scale-x-100" />
    </button>
  );
}

/** A press that turns the page, or null when there is no page that way. */
type PagerStep = (() => void) | null;

/**
 * Rows per page, the field on the left of every pager, as a horizontal
 * field: the label, then an 80px select of the sizes.
 */
export function RowsField({
  label,
  perPage,
  sizes,
  onPerPage,
  testId,
}: {
  /** "Rows per page". */
  label: string;
  perPage: number;
  sizes: readonly number[];
  onPerPage: (size: number) => void;
  /** A `data-testid` for the select's trigger. */
  testId?: string;
}) {
  const id = useId();
  const items = sizes.map((size) => ({ value: size, label: String(size) }));
  return (
    <div
      role="group"
      aria-labelledby={id}
      data-slot="field"
      data-orientation="horizontal"
      className="flex w-fit flex-row items-center gap-2"
    >
      <span
        id={id}
        data-slot="field-label"
        className="flex w-fit text-[13px] leading-snug font-medium whitespace-nowrap text-foreground max-sm:sr-only"
      >
        {label}
      </span>
      <Select
        items={items}
        value={perPage}
        onValueChange={(value) => {
          if (value !== null) onPerPage(value);
        }}
      >
        <SelectTrigger
          aria-labelledby={id}
          data-testid={testId}
          className="w-20 max-md:min-h-9"
        >
          <SelectValue />
        </SelectTrigger>
        <SelectContent>
          {items.map((item) => (
            <SelectItem key={item.value} value={item.value}>
              {item.label}
            </SelectItem>
          ))}
        </SelectContent>
      </Select>
    </div>
  );
}

/**
 * The pager under a list: Rows per page on the left, beside the range the
 * page shows ("1–10 of 75"), and Previous and Next on the right. A step that
 * the press itself disables hands focus to the other step, so the keyboard
 * never lands on the page body at the first or last page.
 */
export function RowsPager({
  label,
  rowsLabel,
  perPage,
  sizes,
  onPerPage,
  range,
  previousLabel,
  nextLabel,
  previous,
  next,
  className,
}: {
  /** The pager's name as a landmark: "Pages". */
  label: string;
  /** "Rows per page". */
  rowsLabel: string;
  perPage: number;
  sizes: readonly number[];
  onPerPage: (size: number) => void;
  range?: ReactNode;
  previousLabel: string;
  nextLabel: string;
  previous: PagerStep;
  next: PagerStep;
  className?: string;
}) {
  const previousRef = useRef<HTMLButtonElement>(null);
  const nextRef = useRef<HTMLButtonElement>(null);
  // The step pressed last, read once by the render the press causes.
  const pressedRef = useRef<"previous" | "next" | null>(null);

  useEffect(() => {
    const pressed = pressedRef.current;
    pressedRef.current = null;
    if (pressed === null) return;
    const from = pressed === "previous" ? previousRef.current : nextRef.current;
    const to = pressed === "previous" ? nextRef.current : previousRef.current;
    if (from?.disabled !== true || to === null || to.disabled) return;
    // A disabled button drops focus to the page body, or keeps it and stops
    // taking keys; either way the reader has lost their place.
    const active = document.activeElement;
    if (active === from || active === document.body) to.focus();
  });

  return (
    <div
      data-rows-pager=""
      className={cn(
        "flex items-center justify-between gap-3 border-t border-border px-3 py-2.5",
        className,
      )}
    >
      <div className="flex min-w-0 items-center gap-3">
        <RowsField
          label={rowsLabel}
          perPage={perPage}
          sizes={sizes}
          onPerPage={onPerPage}
        />
        {range === undefined ? null : (
          <span
            data-range=""
            className="font-mono text-xs whitespace-nowrap text-dim tabular-nums"
          >
            {range}
          </span>
        )}
      </div>
      <Pagination aria-label={label} className="mx-0 w-auto">
        <PaginationContent>
          <PaginationItem>
            <PaginationPrevious
              ref={previousRef}
              text={previousLabel}
              disabled={previous === null}
              onClick={
                previous === null
                  ? undefined
                  : () => {
                      pressedRef.current = "previous";
                      previous();
                    }
              }
            />
          </PaginationItem>
          <PaginationItem>
            <PaginationNext
              ref={nextRef}
              text={nextLabel}
              disabled={next === null}
              onClick={
                next === null
                  ? undefined
                  : () => {
                      pressedRef.current = "next";
                      next();
                    }
              }
            />
          </PaginationItem>
        </PaginationContent>
      </Pagination>
    </div>
  );
}
