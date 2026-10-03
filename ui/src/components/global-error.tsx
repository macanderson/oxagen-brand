"use client";
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
 * Styling is self-contained (no theme `class` dependency), so the fallback
 * renders with zero app context. Every colour reads its semantic token and
 * every space reads the spacing unit, each with a light-mode fallback inside
 * the var(), so the page still draws when the kit's stylesheet is missing.
 * Flat: no radius, no shadow, matching the product skin. When the palette
 * changes, update the fallbacks against the light-mode values in
 * ui/src/styles/globals.css.
 */
export function GlobalErrorPage({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  return (
    <html lang="en">
      <body
        style={{
          margin: 0,
          minHeight: "100vh",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          padding: "calc(var(--ox-space, 0.25rem) * 6)",
          background: "var(--background, #FFFFFF)",
          color: "var(--foreground, #09090B)",
          fontFamily:
            '"Aeonik", ui-sans-serif, system-ui, -apple-system, Segoe UI, Roboto, sans-serif',
        }}
      >
        <section
          style={{
            width: "100%",
            maxWidth: "28rem",
            borderRadius: "0",
            border: "1px solid var(--border, #E4E4E7)",
            background: "var(--card, #FFFFFF)",
            padding: "calc(var(--ox-space, 0.25rem) * 10)",
            textAlign: "center",
          }}
        >
          <h1 style={{ fontSize: "var(--ox-a-h3, 1.25rem)", fontWeight: 600, margin: 0 }}>
            Something went wrong
          </h1>
          <p
            style={{
              marginTop: "calc(var(--ox-space, 0.25rem) * 2)",
              fontSize: "var(--ox-a-body, 0.875rem)",
              color: "var(--body, #27272A)",
            }}
          >
            An unexpected error occurred. You can try again, and if it keeps
            happening we’re already on it.
          </p>
          {error?.digest ? (
            <p
              style={{
                marginTop: "calc(var(--ox-space, 0.25rem) * 3)",
                fontSize: "var(--ox-a-micro, 0.75rem)",
                color: "var(--muted-foreground, #71717A)",
                fontFamily:
                  '"Monaspace Neon", ui-monospace, SFMono-Regular, monospace',
              }}
            >
              {error.digest}
            </p>
          ) : null}
          <button
            type="button"
            onClick={() => reset()}
            style={{
              marginTop: "calc(var(--ox-space, 0.25rem) * 8)",
              height: "2.25rem",
              padding: "0 calc(var(--ox-space, 0.25rem) * 5)",
              borderRadius: "0",
              border: "none",
              background: "var(--button-primary-bg, #D4AF37)",
              color: "var(--button-primary-fg, #09090B)",
              fontSize: "var(--ox-a-body, 0.875rem)",
              fontWeight: 500,
              cursor: "pointer",
            }}
          >
            Try again
          </button>
        </section>
      </body>
    </html>
  );
}
