/**
 * NotFoundPage — shared 404 surface for every Oxagen Next.js app.
 *
 * Rendered by each app's `app/not-found.tsx`. Intentionally a plain Server
 * Component: NO hooks, NO next-themes, NO client context. Next.js statically
 * exports `/_not-found` at build time, so anything that reads React context
 * here (e.g. a theme provider) crashes the export worker. Keep it inert.
 *
 * Styling uses the @oxagen/ui theme tokens (plain CSS variables — no React
 * context), so it reads correctly in both light and dark.
 *
 * Uses a plain anchor (not `next/link`) to avoid coupling `@oxagen/ui` to a
 * `next` dependency — a 404 → home full navigation is fine.
 */
export declare function NotFoundPage({ homeHref }: {
    homeHref?: string;
}): import("react/jsx-runtime").JSX.Element;
