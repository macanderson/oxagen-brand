import * as React from "react";
/**
 * coss ui Switch — Base UI `Switch.Root` + `Switch.Thumb`, fully token-driven
 * via the --control-* tokens. Flat (no shadow) but the track color and thumb
 * slide both animate.
 * State attributes: `data-[checked]` (on), `data-[disabled]` (disabled).
 */
declare const Switch: React.ForwardRefExoticComponent<Omit<Omit<import("@base-ui/react").SwitchRootProps, "ref"> & React.RefAttributes<HTMLElement>, "ref"> & React.RefAttributes<HTMLElement>>;
export { Switch };
