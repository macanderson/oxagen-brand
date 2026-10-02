import { clsx, type ClassValue } from "clsx";
import { extendTailwindMerge } from "tailwind-merge";

/**
 * The steps of the two house type scales. `tokens/house-tailwind.css` turns
 * each one into a `text-m-<step>` and a `text-a-<step>` utility, and
 * `theme/theme.json` lists the same steps under `type.scales`. The test beside
 * this file fails when the two lists differ.
 */
const TYPE_STEPS = ["h1", "h2", "h3", "h4", "body", "micro"] as const;

/**
 * tailwind-merge with the house type utilities in its `font-size` group.
 *
 * Its default config does not know `text-a-h3` or `text-m-body`, so it reads
 * them as a text colour. A colour class such as `text-foreground` in the same
 * list then wins, and the size is dropped (oxageninc/brand#75). In the
 * `font-size` group, a house size conflicts only with another size, such as
 * `text-sm` or `text-a-h1`.
 */
const twMerge = extendTailwindMerge({
  extend: {
    classGroups: {
      "font-size": [{ text: [{ a: TYPE_STEPS, m: TYPE_STEPS }] }],
    },
  },
});

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}
