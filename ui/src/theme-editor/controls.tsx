"use client";
/**
 * The small controls the theme editor is built from: a section, a colour
 * field with its measured contrast, a slider, and a select. They use the
 * kit's tokens and field recipes, so the panel restyles with the draft like
 * the page behind it.
 */
import * as React from "react";
import { inputBase } from "../components/control-styles";
import { cn } from "../lib/utils";
import { contrast, normalizeHex, type Hex } from "./color";

export function Section({
  title,
  note,
  children,
}: {
  title: string;
  note?: React.ReactNode;
  children: React.ReactNode;
}) {
  const id = React.useId();
  return (
    <section aria-labelledby={id} className="flex flex-col gap-3 border-b border-border/70 pb-5 last:border-b-0">
      <h3 id={id} className="text-sm font-semibold text-foreground">
        {title}
      </h3>
      {note ? <p className="-mt-1.5 text-xs leading-normal text-muted-foreground">{note}</p> : null}
      {children}
    </section>
  );
}

/** A contrast ratio, flagged when it is below the bar the build holds it to. */
export function Ratio({
  fg,
  bg,
  min,
  label,
}: {
  fg: Hex;
  bg: Hex;
  /** The bar: 4.5 for text, 3 for a mark. Leave it out for a ratio the build does not check. */
  min?: number;
  label?: string;
}) {
  const value = contrast(fg, bg);
  const low = min !== undefined && value < min;
  return (
    <span
      className={cn(
        "inline-flex items-center gap-1 rounded-full px-1.5 py-0.5 font-mono text-sm tabular-nums",
        low ? "bg-error/10 text-error-ink" : "bg-muted text-muted-foreground",
      )}
      title={min === undefined ? "The build does not check this ratio." : `The build needs ${min}:1 or more.`}
    >
      {label ? <span className="font-sans">{label}</span> : null}
      {value.toFixed(2)}:1
      {low ? <span className="font-sans">below {min}:1</span> : null}
    </span>
  );
}

export function Swatch({ color, className }: { color: string; className?: string }) {
  return (
    <span
      aria-hidden
      className={cn("inline-block size-5 shrink-0 rounded-md border border-border", className)}
      style={{ background: color }}
    />
  );
}

/** A colour field: a picker, the hex typed out, and any ratios to show beside it. */
export function ColorField({
  label,
  value,
  onChange,
  children,
}: {
  label: string;
  value: Hex;
  onChange: (hex: Hex) => void;
  children?: React.ReactNode;
}) {
  const id = React.useId();
  const [text, setText] = React.useState(value);
  React.useEffect(() => setText(value), [value]);
  const valid = normalizeHex(text) !== null;
  return (
    <div className="flex flex-col gap-1.5">
      <div className="flex items-center gap-2">
        <input
          type="color"
          aria-label={`${label} picker`}
          value={value.toLowerCase()}
          onChange={(e) => {
            const hex = normalizeHex(e.target.value);
            if (hex) onChange(hex);
          }}
          className="size-8 shrink-0 cursor-pointer rounded-lg border border-border bg-transparent p-0.5"
        />
        <label htmlFor={id} className="min-w-0 flex-1 text-sm text-foreground">
          {label}
        </label>
        <input
          id={id}
          value={text}
          spellCheck={false}
          aria-invalid={!valid}
          onChange={(e) => {
            setText(e.target.value);
            const hex = normalizeHex(e.target.value);
            if (hex) onChange(hex);
          }}
          onBlur={() => setText(value)}
          className={cn(inputBase, "min-h-8 w-[6.5rem] py-1 font-mono text-xs uppercase")}
        />
      </div>
      {children ? <div className="flex flex-wrap gap-1.5 pl-10">{children}</div> : null}
    </div>
  );
}

export function RangeField({
  label,
  value,
  min,
  max,
  step,
  shown,
  onChange,
}: {
  label: string;
  value: number;
  min: number;
  max: number;
  step: number;
  /** The value as the reader sees it, such as "7.2px". */
  shown: string;
  onChange: (value: number) => void;
}) {
  const id = React.useId();
  return (
    <div className="flex flex-col gap-1">
      <div className="flex items-baseline justify-between gap-2">
        <label htmlFor={id} className="text-sm text-foreground">
          {label}
        </label>
        <span className="font-mono text-xs tabular-nums text-muted-foreground">{shown}</span>
      </div>
      <input
        id={id}
        type="range"
        min={min}
        max={max}
        step={step}
        value={value}
        onChange={(e) => onChange(Number(e.target.value))}
        className="w-full accent-[var(--ox-gold)]"
      />
    </div>
  );
}

export function SelectField<T extends string>({
  label,
  value,
  options,
  onChange,
  className,
}: {
  label: string;
  value: T;
  options: readonly { value: T; label: string }[];
  onChange: (value: T) => void;
  className?: string;
}) {
  const id = React.useId();
  return (
    <div className={cn("flex items-center gap-2", className)}>
      <label htmlFor={id} className="min-w-0 flex-1 text-sm text-foreground">
        {label}
      </label>
      <select
        id={id}
        value={value}
        onChange={(e) => onChange(e.target.value as T)}
        className={cn(inputBase, "min-h-8 w-auto max-w-[13rem] py-1 pr-8 text-xs")}
      >
        {options.map((o) => (
          <option key={o.value} value={o.value}>
            {o.label}
          </option>
        ))}
      </select>
    </div>
  );
}

/** A plain text field with a label above it. */
export function TextField({
  label,
  value,
  onChange,
  placeholder,
  invalid,
  hint,
  list,
}: {
  label: string;
  value: string;
  onChange: (value: string) => void;
  placeholder?: string;
  invalid?: boolean;
  hint?: React.ReactNode;
  list?: string;
}) {
  const id = React.useId();
  return (
    <div className="flex flex-col gap-1.5">
      <label htmlFor={id} className="text-sm text-foreground">
        {label}
      </label>
      <input
        id={id}
        value={value}
        list={list}
        placeholder={placeholder}
        spellCheck={false}
        aria-invalid={invalid || undefined}
        onChange={(e) => onChange(e.target.value)}
        className={cn(inputBase, "min-h-8 py-1 text-xs")}
      />
      {hint ? <p className={cn("text-xs leading-normal", invalid ? "text-error-ink" : "text-muted-foreground")}>{hint}</p> : null}
    </div>
  );
}
