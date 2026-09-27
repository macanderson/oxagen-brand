import * as React from "react";
import { RadioGroup as RadioGroupPrimitive } from "@base-ui/react/radio-group";
import { Radio as RadioPrimitive } from "@base-ui/react/radio";
/**
 * coss ui RadioGroup — Base UI `RadioGroup` + `Radio.Root` + `Radio.Indicator`,
 * token-driven via the --control-* tokens. Flat (no shadow); the ring color
 * transitions on select.
 * State attributes on Radio: `data-[checked]` (selected), `data-[disabled]`.
 */
declare const RadioGroup: React.ForwardRefExoticComponent<Omit<RadioGroupPrimitive.Props<unknown>, "ref"> & React.RefAttributes<HTMLDivElement>>;
/** Individual radio button — outer ring + inner fill indicator. */
declare const Radio: React.ForwardRefExoticComponent<Omit<RadioPrimitive.Root.Props<unknown>, "ref"> & React.RefAttributes<HTMLSpanElement>>;
export { RadioGroup, Radio };
