import * as React from "react";
/**
 * coss ui Panel — a titled surface container.
 *
 * The workhorse layout block for settings, detail views and dashboards: an
 * optional header (eyebrow + title + actions slot), a padded body, and an
 * optional footer. Distinct from `CardPanel` (a body wrapper *inside* a Card) —
 * `Panel` is the whole surface.
 *
 *   <Panel
 *     eyebrow="Workspace"
 *     title="General settings"
 *     actions={<Button size="sm" variant="outline">Edit</Button>}
 *     footer={<Button>Save</Button>}
 *   >
 *     …body…
 *   </Panel>
 *
 * Optional treatments (default off, mirroring `Card`):
 * - `inset`        — removes body padding for flush content (tables).
 * - `glow`         — accepted and ignored; this flat design has no glow treatment.
 * - `gradientRing` — accepted and ignored; the border always stays neutral.
 */
export interface PanelProps extends Omit<React.HTMLAttributes<HTMLElement>, "title"> {
    /** Main heading rendered in the header. */
    title?: React.ReactNode;
    /** Small mono/uppercase label above the title. */
    eyebrow?: React.ReactNode;
    /** Right-aligned header slot (buttons, menus, badges). */
    actions?: React.ReactNode;
    /** Footer slot rendered below the body on a tinted bar. */
    footer?: React.ReactNode;
    /** Remove body padding for flush content like tables. */
    inset?: boolean;
    /** Accepted for API parity with `Card`; ignored — no glow in this design. */
    glow?: boolean;
    /** Accepted for API parity with `Card`; ignored — the border stays neutral. */
    gradientRing?: boolean;
}
declare const Panel: React.ForwardRefExoticComponent<PanelProps & React.RefAttributes<HTMLElement>>;
export { Panel };
