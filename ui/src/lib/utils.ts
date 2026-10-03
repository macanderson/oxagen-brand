import { clsx, type ClassValue } from "clsx";
import { extendTailwindMerge } from "tailwind-merge";
import typeUtilities from "./house-type-utilities.json";

/**
 * tailwind-merge with the house type utilities in its `font-size` group.
 *
 * Its default config does not know `text-a-h3`, `text-m-body`, or
 * `text-input-touch`, so it reads them as a text colour. A colour class such
 * as `text-foreground` in the same list then wins, and the size is dropped
 * (oxageninc/brand#75). In the `font-size` group, a house size conflicts only
 * with another size, such as `text-base` or `text-a-h1`.
 *
 * `build/build.py` writes the step names into `house-type-utilities.json`
 * beside this file from `theme/theme.json`, so a new step reaches `cn()` with
 * no edit here. The fan-out copies the same file into product.
 */
const { scales, named } = typeUtilities;

const twMerge = extendTailwindMerge({
  extend: {
    classGroups: {
      "font-size": [{ text: [{ a: scales.a, m: scales.m }, ...named] }],
    },
  },
});

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}
