import { clsx, type ClassValue } from "clsx";
import { extendTailwindMerge } from "tailwind-merge";

/**
 * The steps of the two house type scales. `tokens/house-tailwind.css` turns
 * each one into a `text-m-<step>` or a `text-a-<step>` utility, and
 * `theme/theme.json` lists the same steps under `type.scales`. The app scale
 * has a 2xs step below micro. The test beside this file fails when the lists
 * differ.
 */
const MARKETING_STEPS = ["h1", "h2", "h3", "h4", "body", "micro"] as const;
const APP_STEPS = [...MARKETING_STEPS, "2xs"] as const;

/**
 * tailwind-merge with the house type utilities in its `font-size` group.
 *
 * Its default config does not know `text-a-h3` or `text-m-body`, so it reads
 * them as a text colour. A colour class such as `text-foreground` in the same
 * list then wins, and the size is dropped (oxageninc/brand#75). In the
 * `font-size` group, a house size conflicts only with another size, such as
 * `text-base` or `text-a-h1`. `text-input-touch`, a text field's size on a
 * phone, joins the group for the same reason.
 */
const twMerge = extendTailwindMerge({
  extend: {
    classGroups: {
      "font-size": [{ text: [{ a: APP_STEPS, m: MARKETING_STEPS }, "input-touch"] }],
    },
  },
});

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}
