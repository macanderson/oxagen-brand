import type { StorybookConfig } from "@storybook/react-vite";

/**
 * Storybook for @oxagen/ui — the coss ui (Base UI) component system.
 *
 * Runs the components straight from `src` (this package has no build step;
 * apps consume the raw TS via `transpilePackages`). Tailwind v4 + the design
 * tokens are processed through `postcss.config.mjs` (the `@tailwindcss/postcss`
 * plugin), and the token-driven `globals.css` is imported once in `preview.tsx`.
 */
const config: StorybookConfig = {
  // The .mdx entry is the Overview page. Every other docs page is generated
  // from a component's stories by the `autodocs` tag in `preview.tsx`.
  stories: ["../src/**/*.mdx", "../src/**/*.stories.@(ts|tsx)"],
  framework: { name: "@storybook/react-vite", options: {} },
  addons: ["@storybook/addon-docs"],
  core: { disableTelemetry: true },
  // tokens/house-fonts.css names each face as `url(../fonts/<file>)`, which the
  // CSS keeps as written. In the built Storybook that resolves from assets/ to
  // fonts/ beside it, so the kit's fonts/ folder ships there. Without it every
  // story fell back to system fonts and the browser logged a 404 per face.
  staticDirs: [{ from: "../../fonts", to: "/fonts" }],
};

export default config;
