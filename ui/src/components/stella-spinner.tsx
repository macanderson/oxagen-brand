// Moved from oxagen apps/app/src/ui/stella-mark.tsx at ddb85803. The wordmark
// and icon stayed behind, because `brand.tsx` already draws both from the
// generated geometry. The spinner takes its asterisk and gold from that same
// geometry, and `stella-spinner.test.tsx` checks its placement and shimmer
// against `spinners/stella-spinner.svg` in this repository.
import { type SVGProps, useId } from "react";
import { BRAND_GOLD, STELLA } from "./brand-marks.generated";

const STELLA_MARK = STELLA.icon.parts[0]?.d ?? "";

/**
 * The light that sweeps across the spinner's asterisk.
 *
 * @internal Exported for its unit test; nothing outside this module imports it.
 */
export const STELLA_SHIMMER = "#F1CE65";

/**
 * The placement `spinners/stella-spinner.svg` gives the asterisk, a little
 * larger than the icon's so the turning points stay inside the square.
 *
 * @internal Exported for its unit test; nothing outside this module imports it.
 */
export const STELLA_SPINNER_TRANSFORM =
  "translate(8.813,117.886) scale(1.11248)";

type SpinnerProps = Omit<SVGProps<SVGSVGElement>, "viewBox" | "children"> & {
  /**
   * The accessible name. Omit it where the spinner sits beside its own label,
   * or inside a control that has one, and the spinner is hidden from assistive
   * technology.
   */
  title?: string;
};

/**
 * The stella spinner: the asterisk turns and a light sweeps across it. Drawn
 * inline so it follows the page's theme, and because the sweep needs gradient
 * and clip ids that stay unique when two spinners share a page. The motion is
 * `.ox-stella-turn` and `.ox-stella-sweep` in `styles/globals.css`, which hold
 * still under reduced motion.
 */
export function StellaSpinner({ title, ...props }: SpinnerProps) {
  const id = useId().replace(/[^\w-]/g, "");
  const clip = `stella-spin-clip-${id}`;
  const sweep = `stella-spin-sweep-${id}`;
  const a11y =
    title === undefined
      ? { "aria-hidden": true as const }
      : { role: "img" as const, "aria-label": title };
  return (
    <svg
      xmlns="http://www.w3.org/2000/svg"
      viewBox={STELLA.icon.viewBox}
      focusable="false"
      data-mark="stella-spinner"
      {...a11y}
      {...props}
    >
      <defs>
        <clipPath id={clip}>
          <path d={STELLA_MARK} />
        </clipPath>
        <linearGradient id={sweep} x1="0" y1="0" x2="1" y2="0">
          <stop offset="0" stopColor={STELLA_SHIMMER} stopOpacity="0" />
          <stop offset="0.5" stopColor={STELLA_SHIMMER} stopOpacity="0.95" />
          <stop offset="1" stopColor={STELLA_SHIMMER} stopOpacity="0" />
        </linearGradient>
      </defs>
      <g transform={STELLA_SPINNER_TRANSFORM}>
        <g className="ox-stella-turn">
          <path d={STELLA_MARK} fill={BRAND_GOLD} />
          <g clipPath={`url(#${clip})`}>
            <rect
              className="ox-stella-sweep"
              x="-49.86"
              y="-98.03"
              width="32.27"
              height="70.42"
              fill={`url(#${sweep})`}
              transform="skewX(-18)"
            />
          </g>
        </g>
      </g>
    </svg>
  );
}
