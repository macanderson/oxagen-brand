/**
 * The Oxagen and Stella marks.
 *
 * Geometry comes from `./brand-marks.generated.ts`, extracted by
 * `tools/scripts/sync-brand-assets.mjs` from the house brand kit
 * (oxagenai/oxagen-brand). Nothing here is drawn: both wordmarks are
 * Space Grotesk's own outlines at weight 600, and both icons are the same face
 * at display weight, so the marks and the product's running text cannot drift
 * apart. To change a mark, change the kit and re-run the sync.
 *
 *   <OxagenWordmark className="h-7" />   // "oxagen", the x in gold — THE logo
 *   <OxagenIcon className="size-7" />    // the one-colour "Ox" lettermark
 *   <StellaWordmark className="h-7" />   // "stella*", the asterisk in gold
 *   <StellaIcon className="size-7" />    // the asterisk alone, in gold
 *   <BrandMark />                        // OxagenIcon at the app-chrome size
 *   <NodeChip kind="document" id="…" />  // typed knowledge-graph node
 *   <ConfidenceBar score={0.82} />       // edge-inference confidence
 *
 * ── THE RULES THESE COMPONENTS ENCODE ────────────────────────────────────────
 *
 * OXAGEN'S LOGO IS THE WORDMARK. There is deliberately no Oxagen lockup export
 * and no horizontal/vertical composition helper. The kit does emit a lockup —
 * the Ox mark in a plate, a gap, then the word — and it is not used in the
 * product: set plainly, `Ox oxagen` stutters, because the mark is the word's
 * own first two letters at the word's own size. Use the wordmark; use the icon
 * only where the slot is square and small (a favicon, an avatar, collapsed
 * chrome), and then use it ALONE, never beside the word.
 *
 * STELLA'S MARK IS INSIDE ITS WORD. `stella*` already carries the asterisk, so
 * the wordmark IS the Stella lockup and nothing is ever placed to its left.
 *
 * ONE GLYPH IS GOLD. The `x` of oxagen, the asterisk of stella — never a second
 * one, never the whole word. The gold stays #D6962C in BOTH themes: the kit's
 * "gold becomes its deep shade on paper" rule governs gold WORDS, not the mark,
 * and the kit's own light and dark files both fill the accent with the metal.
 *
 * THE ICON IS ONE COLOUR. It takes the colour of whatever it sits on, so it can
 * be placed and forgotten — and handed to an operating system that will tint it
 * however it likes. It never carries the metal. StellaIcon is the exception the
 * kit itself makes: the asterisk IS the metal, so it ships gold.
 *
 * MINIMUM SIZES. 88px for a wordmark, 24px for an icon. Below that, use the
 * favicon asset instead of shrinking a mark past legibility.
 *
 * All marks are pure presentational (no hooks) so they render in Server
 * Components.
 */
import type { CSSProperties } from "react";
/**
 * How a mark is coloured.
 *
 * `adaptive`  letters inherit currentColor and flip with the theme; the accent
 *             glyph keeps the metal. This is the default and what almost every
 *             surface wants.
 * `mono`      the whole mark, accent included, collapses to currentColor. For
 *             single-colour contexts: a print sheet, an embossed favicon, a
 *             partner's one-colour lockup slot, a disabled state.
 */
export type LogoTone = "adaptive" | "mono";
/**
 * THE Oxagen logo — "oxagen", lowercase, its `x` in gold. Use this everywhere a
 * surface identifies itself as Oxagen. There is no lockup alternative.
 */
export declare function OxagenWordmark({ className, tone, style, }: {
    className?: string;
    tone?: LogoTone;
    style?: CSSProperties;
}): import("react/jsx-runtime").JSX.Element;
/**
 * The Oxagen icon — `Ox`, the word's own first two letters, one colour, taken
 * from whatever it sits on. Square slots only, and always alone: putting it
 * beside the wordmark rebuilds the lockup the product does not use.
 */
export declare function OxagenIcon({ className, style, }: {
    className?: string;
    style?: CSSProperties;
}): import("react/jsx-runtime").JSX.Element;
/**
 * The Stella logo — `stella*`. The asterisk is the mark, and it is already in
 * the word, so nothing is ever placed to its left. This is Stella's lockup.
 */
export declare function StellaWordmark({ className, tone, style, }: {
    className?: string;
    tone?: LogoTone;
    style?: CSSProperties;
}): import("react/jsx-runtime").JSX.Element;
/**
 * The Stella icon — the asterisk alone. Unlike the Ox lettermark this one IS
 * the metal: the kit ships it gold, because a lone asterisk in ink reads as
 * punctuation rather than a mark. `tone="mono"` flattens it for one-colour
 * contexts.
 */
export declare function StellaIcon({ className, tone, style, }: {
    className?: string;
    tone?: LogoTone;
    style?: CSSProperties;
}): import("react/jsx-runtime").JSX.Element;
/**
 * The Oxagen icon at the app-chrome size — collapsed sidebars, tab strips,
 * anywhere a square slot names the product. Alone: see OxagenIcon.
 */
export declare function BrandMark({ className }: {
    className?: string;
}): import("react/jsx-runtime").JSX.Element;
export type NodeKind = "user" | "document" | "service" | "policy" | "resource" | "default";
/**
 * NodeChip — a typed knowledge-graph node reference: a colour-coded dot + mono
 * entity id, the way the product renders entities in edge diagrams and tool
 * output. `kind` colours the dot by entity class.
 */
export declare function NodeChip({ kind, id, label, className, }: {
    kind?: NodeKind;
    id?: string;
    label?: string;
    className?: string;
}): import("react/jsx-runtime").JSX.Element;
/**
 * ConfidenceBar — inference-confidence meter for semantic edges. Colour follows
 * the product thresholds: ≥0.8 success, ≥0.6 warning, else danger.
 */
export declare function ConfidenceBar({ score, showValue, width, className, }: {
    score?: number;
    showValue?: boolean;
    width?: number;
    className?: string;
}): import("react/jsx-runtime").JSX.Element;
