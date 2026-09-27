import * as React from "react";
import { Slider as SliderPrimitive } from "@base-ui/react/slider";
/**
 * coss ui Slider — wraps Base UI `Slider.Root`, `Slider.Control`, `Slider.Track`,
 * `Slider.Indicator`, `Slider.Thumb`, and `Slider.Value`.
 *
 * Numeric/stepped preference control (e.g. font-size scale, volume).
 * State attributes: `data-[dragging]`, `data-[disabled]`, `data-[orientation]`.
 */
declare const Slider: React.ForwardRefExoticComponent<Omit<SliderPrimitive.Root.Props<number | readonly number[]> & {
    ref?: React.Ref<HTMLDivElement> | undefined;
}, "ref"> & React.RefAttributes<HTMLDivElement>>;
declare const SliderControl: React.ForwardRefExoticComponent<Omit<Omit<import("@base-ui/react").SliderControlProps, "ref"> & React.RefAttributes<HTMLDivElement>, "ref"> & React.RefAttributes<HTMLDivElement>>;
declare const SliderTrack: React.ForwardRefExoticComponent<Omit<Omit<import("@base-ui/react").SliderTrackProps, "ref"> & React.RefAttributes<HTMLDivElement>, "ref"> & React.RefAttributes<HTMLDivElement>>;
declare const SliderIndicator: React.ForwardRefExoticComponent<Omit<Omit<import("@base-ui/react").SliderIndicatorProps, "ref"> & React.RefAttributes<HTMLDivElement>, "ref"> & React.RefAttributes<HTMLDivElement>>;
declare const SliderThumb: React.ForwardRefExoticComponent<Omit<Omit<import("@base-ui/react").SliderThumbProps, "ref"> & React.RefAttributes<HTMLDivElement>, "ref"> & React.RefAttributes<HTMLDivElement>>;
declare const SliderValue: React.ForwardRefExoticComponent<Omit<Omit<import("@base-ui/react").SliderValueProps, "ref"> & React.RefAttributes<HTMLOutputElement>, "ref"> & React.RefAttributes<HTMLOutputElement>>;
export { Slider, SliderControl, SliderTrack, SliderIndicator, SliderThumb, SliderValue, };
