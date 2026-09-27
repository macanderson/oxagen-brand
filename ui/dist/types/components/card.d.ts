import * as React from "react";
/**
 * coss ui Card — neutral surface container.
 *
 * Optional treatments (all default off):
 * - `glow`         — accepted but has no visual effect; this flat design has no glow treatment.
 * - `gradientRing` — accepted but has no visual effect; the border always stays neutral.
 * - `interactive`  — adds hover lift + pointer affordance (`hover-lift cursor-pointer`).
 */
export interface CardProps extends React.HTMLAttributes<HTMLDivElement> {
    /** Accepted for API parity with `Panel`; has no visual effect here. */
    glow?: boolean;
    /** Accepted for API parity with `Panel`; has no visual effect here. */
    gradientRing?: boolean;
    /** Add hover lift + pointer affordance for clickable cards. */
    interactive?: boolean;
}
declare const Card: React.ForwardRefExoticComponent<CardProps & React.RefAttributes<HTMLDivElement>>;
/**
 * CardHeader — a FLAT header that blends with the card surface: no shaded
 * band, just a hairline `border-b` separating it from the body (the ink still
 * flips per-theme via `--card-header-fg`). `rounded-t-xl` matches the Card
 * radius so it sits flush; the descendant `[&_p]` rule dims CardDescription to
 * 70% of the header ink so it stays legible.
 */
declare const CardHeader: React.ForwardRefExoticComponent<React.HTMLAttributes<HTMLDivElement> & React.RefAttributes<HTMLDivElement>>;
declare const CardTitle: React.ForwardRefExoticComponent<React.HTMLAttributes<HTMLHeadingElement> & React.RefAttributes<HTMLHeadingElement>>;
declare const CardDescription: React.ForwardRefExoticComponent<React.HTMLAttributes<HTMLParagraphElement> & React.RefAttributes<HTMLParagraphElement>>;
/** coss ui body wrapper. Replaces the shadcn `CardContent` name. */
declare const CardPanel: React.ForwardRefExoticComponent<React.HTMLAttributes<HTMLDivElement> & React.RefAttributes<HTMLDivElement>>;
declare const CardFooter: React.ForwardRefExoticComponent<React.HTMLAttributes<HTMLDivElement> & React.RefAttributes<HTMLDivElement>>;
export { Card, CardHeader, CardTitle, CardDescription, CardPanel, CardFooter };
