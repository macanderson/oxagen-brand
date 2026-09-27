/**
 * GlobalErrorPage — shared top-level error boundary for every Oxagen Next.js
 * app, rendered by each app's `app/global-error.tsx`.
 *
 * Next.js renders `global-error` ENTIRELY OUTSIDE the root layout, so it must
 * supply its own `<html>`/`<body>`. Critically, that also means it runs with no
 * ThemeProvider / next-themes context — which is exactly why it is safe: it
 * cannot trip the `useContext` null crash that breaks `/_global-error` static
 * export when the default (provider-wrapped) error tree is used instead.
 *
 * Styling is fully self-contained (hardcoded light-mode hexes, no theme `class`
 * dependency) so the fallback renders correctly with zero app context. Flat: no
 * radius, no shadow — matching the product skin. Because no tokens are loaded
 * here these hexes cannot follow a reskin: when the palette changes, update
 * them by hand against the light-mode values in
 * packages/ui/src/styles/globals.css.
 */
export declare function GlobalErrorPage({ error, reset, }: {
    error: Error & {
        digest?: string;
    };
    reset: () => void;
}): import("react/jsx-runtime").JSX.Element;
