// Moved from oxagen apps/app/src/ui/badge.tsx at ddb85803.
// The one state badge (mockup `.b`, engine.css, ADR-132): a dot and a word in
// a tinted pill, so the state survives greyscale and reads the same on every
// page. The hue is a state hue and never the gold: gold is identity.
//
// `.b { gap:5px; font-size:11px; font-weight:600; letter-spacing:.02em;
// padding:2px 7px; border-radius:6px; border:1px solid }`, and `.b-<state>`
// puts the state hue on the ink, 42% of it on the border and 11% behind;
// critical takes 12%. `.b-q` is the quiet pill: muted ink, the hairline, the
// wash. `.b-tier` is the mono, lowercase variant an enforcement tier takes.
// Badge's soft variants draw the same pills for a caller that has no state.
import type { ReactNode } from "react";
import { cn } from "../lib/utils";

/** The mockup's state vocabulary; `quiet` is `.b-q`. */
export type ToneBadgeTone =
  | "allowed"
  | "approval"
  | "denied"
  | "proven"
  | "failed"
  | "critical"
  | "quiet";

const TONE: Record<ToneBadgeTone, string> = {
  allowed: "border-success/42 bg-success/11 text-success-ink",
  approval: "border-info/42 bg-info/11 text-info-ink",
  denied: "border-warning/42 bg-warning/11 text-warning-ink",
  proven: "border-proven/42 bg-proven/11 text-proven-ink",
  failed: "border-error/42 bg-error/11 text-error-ink",
  critical: "border-critical/42 bg-critical/12 text-critical-ink",
  quiet: "border-border bg-hl text-muted-foreground",
};

/** Every tone, in the order a legend lists them. */
export const TONE_BADGE_TONES = Object.keys(TONE) as ToneBadgeTone[];

const badgeBase =
  "inline-flex items-center gap-[5px] whitespace-nowrap rounded-md border px-[7px] py-0.5 text-sm font-semibold leading-normal tracking-[0.02em]";

export function ToneBadge({
  tone,
  dot = true,
  mono = false,
  title,
  className,
  children,
  ...rest
}: {
  tone: ToneBadgeTone;
  /**
   * `.b .d`: the 5px dot in the state hue. Off for a kind or a tier;
   * `"pulse"` breathes, for a state that is happening right now.
   */
  dot?: boolean | "pulse";
  /** `.b-tier`: mono, lowercase, regular weight. */
  mono?: boolean;
  /** The longer reading, on hover and to assistive tech. */
  title?: string;
  /** Classes merged after the tone's, for spacing in a layout. */
  className?: string;
  children: ReactNode;
} & Record<`data-${string}`, string | undefined>) {
  return (
    <span
      {...rest}
      title={title}
      className={cn(
        badgeBase,
        TONE[tone],
        mono && "font-mono text-xs font-medium lowercase",
        className,
      )}
    >
      {dot ? (
        <span
          aria-hidden="true"
          data-pulse={dot === "pulse" ? "true" : undefined}
          className={cn(
            "size-[5px] flex-none rounded-full bg-current",
            dot === "pulse" && "animate-pulse motion-reduce:animate-none",
          )}
        />
      ) : null}
      {children}
    </span>
  );
}
