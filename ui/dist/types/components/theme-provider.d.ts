/**
 * ThemeProvider / useTheme — self-hosted, class-based theming for all Oxagen
 * Next.js apps. Vendor-neutral replacement for `next-themes`.
 *
 * The preference lives in a cookie ({@link THEME_COOKIE_NAME}). `"system"`
 * renders no class and is resolved by CSS `@media (prefers-color-scheme)`
 * (see styles/globals.css). Two no-flash integration modes:
 *
 *   1. SSR-cookie mode (apps WITHOUT Cache Components): the root layout (a
 *      Server Component) reads the cookie via {@link parseTheme} and renders
 *      the resolved class onto `<html>` directly, then passes it as
 *      `initialTheme`. No inline `<script>` needed.
 *   2. Bootstrap-script mode (apps WITH `cacheComponents: true`, e.g.
 *      apps/app): the root layout is prerendered into a static shell and must
 *      not read cookies, so it renders no theme class and embeds a tiny
 *      SERVER-rendered inline script (see apps/app AppearanceBootstrap) that
 *      applies the cookie's class before first paint. Omit `initialTheme`;
 *      the provider adopts the cookie in a mount effect.
 *
 * Inline-script caveat: React 19.2 (Next 16) replaces CLIENT-rendered
 * executable `<script>` elements with a `<div>` and logs "Encountered a script
 * tag while rendering React component". A script emitted by a Server Component
 * into the initial HTML stream is executed by the browser's parser, not React,
 * so bootstrap-script mode is safe — but never render an executable `<script>`
 * from a client component.
 *
 * Split of responsibilities:
 *   - The root layout (server) establishes the pre-paint class via mode 1 or 2.
 *   - {@link ThemeProvider} (this file, "use client") owns React state, the
 *     `setTheme` setter, system-preference + cross-tab sync, cookie persistence,
 *     and reflecting the resolved class onto `<html>`. It renders NO `<script>`.
 *
 * Usage (SSR-cookie mode root layout — a Server Component):
 *   import { cookies } from "next/headers";
 *   import { ThemeProvider, THEME_COOKIE_NAME, parseTheme, themeClass } from "@oxagen/ui";
 *   export default async function RootLayout({ children }) {
 *     const theme = parseTheme((await cookies()).get(THEME_COOKIE_NAME)?.value);
 *     return (
 *       <html lang="en" className={themeClass(theme)} suppressHydrationWarning>
 *         <body>
 *           <ThemeProvider initialTheme={theme}>{children}</ThemeProvider>
 *         </body>
 *       </html>
 *     );
 *   }
 *
 * Keep `suppressHydrationWarning` on `<html>`: for "system" the provider adds an
 * explicit class on the client after resolving the OS preference, so the class
 * attribute legitimately differs from the (classless) server markup.
 */
import * as React from "react";
import { type Theme, type ResolvedTheme } from "./theme-config";
export interface ThemeContextValue {
    /** The user's selection, including "system". */
    theme: Theme;
    /** The concrete theme in effect — "system" resolved against the OS preference. */
    resolvedTheme: ResolvedTheme;
    /** Persist and apply a new selection. */
    setTheme: (theme: Theme) => void;
    /** All selectable values. */
    themes: readonly Theme[];
}
export interface ThemeProviderProps {
    children: React.ReactNode;
    /**
     * The cookie-resolved preference from the server, so client state matches the
     * SSR-rendered `<html>` class with no hydration mismatch or flash. Omit on
     * static pages that don't read the cookie — the provider falls back to
     * `defaultTheme` and adopts any existing cookie on mount.
     */
    initialTheme?: Theme;
    /** Cookie key for the persisted preference. Must match the layout's read. */
    cookieName?: string;
    /** Theme to assume when no preference is known (no `initialTheme`, no cookie). */
    defaultTheme?: Theme;
    /** Set `color-scheme` on `<html>` alongside the class. */
    enableColorScheme?: boolean;
    /** Suppress CSS transitions during the swap to avoid a color flash. */
    disableTransitionOnChange?: boolean;
}
export declare function ThemeProvider({ children, initialTheme, cookieName, defaultTheme, enableColorScheme, disableTransitionOnChange, }: ThemeProviderProps): import("react/jsx-runtime").JSX.Element;
/**
 * Read the active theme and setter. Intended to be used under a <ThemeProvider>
 * (every Oxagen app mounts one in its root layout). If the provider context is
 * missing it does NOT throw — it returns {@link FALLBACK_THEME} and, in
 * development only, logs a warning. This keeps a transient Fast Refresh context
 * mismatch (or any stray render outside the provider) from crashing the app,
 * while still surfacing a genuinely missing provider to developers.
 */
export declare function useTheme(): ThemeContextValue;
