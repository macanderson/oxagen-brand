/**
 * @oxagen/ui — shared motion primitives.
 *
 * The single source of truth for framer-motion (the `motion` package) easing
 * curves, durations, and reusable variants across every Oxagen surface. These
 * mirror the CSS motion tokens in `styles/globals.css` — keep the two in sync so
 * the CSS-transition components (Base UI popups, hover-lift) and the
 * framer-motion components animate identically.
 *
 * Design intent: motion is restrained — a gentle *rise + settle* on entry, a soft
 * ease-out on hover, no scale-heavy or bouncy springs. "Alive, not over done."
 *
 * Pure module: no React, no "use client". Importable from server components,
 * client components, and the framer-motion layer alike. The reduced-motion
 * provider lives separately in `components/motion-provider.tsx`.
 */
/**
 * Easing curves as cubic-bezier control-point tuples, the shape framer-motion's
 * `ease` / `transition.ease` expects. Identical curves to the `--ease-*` CSS
 * custom properties.
 */
export declare const easing: {
    /** Elements entering — decelerate into rest. */
    readonly entry: readonly [0.16, 1, 0.3, 1];
    /** Hover / focus micro-interactions — gentle ease-out. */
    readonly hover: readonly [0.22, 1, 0.36, 1];
    /** Elements leaving — accelerate out. */
    readonly exit: readonly [0.4, 0, 1, 1];
};
/** Durations in seconds (framer-motion's unit). Mirror `--motion-*` (ms). */
export declare const duration: {
    readonly micro: 0.16;
    readonly base: 0.22;
    readonly overlay: 0.2;
    readonly entry: 0.32;
};
/**
 * Default transitions composed from the tokens above. Reuse these instead of
 * re-specifying `{ duration, ease }` inline so timing stays consistent.
 */
export declare const transition: {
    readonly entry: {
        readonly duration: 0.32;
        readonly ease: readonly [0.16, 1, 0.3, 1];
    };
    readonly base: {
        readonly duration: 0.22;
        readonly ease: readonly [0.22, 1, 0.36, 1];
    };
    readonly exit: {
        readonly duration: 0.16;
        readonly ease: readonly [0.4, 0, 1, 1];
    };
};
/**
 * Fade + rise on enter, fade + slight lift on exit. The workhorse variant for
 * chat messages, tool cards, and any element that mounts/unmounts. Pair with
 * framer-motion's `<AnimatePresence>` to get the exit animation.
 */
export declare const fadeInUp: {
    readonly hidden: {
        readonly opacity: 0;
        readonly y: 6;
    };
    readonly visible: {
        readonly opacity: 1;
        readonly y: 0;
        readonly transition: {
            readonly duration: 0.32;
            readonly ease: readonly [0.16, 1, 0.3, 1];
        };
    };
    readonly exit: {
        readonly opacity: 0;
        readonly y: -4;
        readonly transition: {
            readonly duration: 0.16;
            readonly ease: readonly [0.4, 0, 1, 1];
        };
    };
};
/** Plain fade, no translate — for overlays/backdrops that shouldn't drift. */
export declare const fade: {
    readonly hidden: {
        readonly opacity: 0;
    };
    readonly visible: {
        readonly opacity: 1;
        readonly transition: {
            readonly duration: 0.2;
            readonly ease: readonly [0.16, 1, 0.3, 1];
        };
    };
    readonly exit: {
        readonly opacity: 0;
        readonly transition: {
            readonly duration: 0.16;
            readonly ease: readonly [0.4, 0, 1, 1];
        };
    };
};
/**
 * Stagger container — children animate in sequence. Use on a list wrapper with
 * `variants={staggerContainer}` and `fadeInUp` on each child.
 */
export declare const staggerContainer: {
    readonly hidden: {};
    readonly visible: {
        readonly transition: {
            readonly staggerChildren: 0.04;
        };
    };
};
