import * as React from "react";
import "./preview.css";
import type { Decorator, Preview } from "@storybook/react-vite";
import { useGlobals } from "storybook/preview-api";
import { ThemeEditor } from "../src/theme-editor/theme-editor";

/**
 * Theme toolbar — coss ui is fully token-driven: the `.dark` class on an
 * ancestor flips every surface, control, and state. The decorator below applies
 * that class to the story container so each component can be inspected in both
 * light and dark without a full ThemeProvider (which needs cookies/SSR wiring).
 */
const withTheme: Decorator = (Story, context) => {
  const theme = (context.globals.theme as string | undefined) ?? "light";
  // Base UI overlays (Select / Menu / Dialog / Combobox / Tooltip popups) portal
  // to document.body — OUTSIDE the wrapper div below — so the wrapper's `.dark`
  // class never reaches them. Mirror the class onto <html> so portalled content
  // inherits the same token theme it does in the real app, where the
  // ThemeProvider sets `.dark` on <html>.
  //
  // Light mode sets `.light` too. The tokens follow the OS preference on a root
  // that carries neither class, so without it a viewer on a dark OS saw dark
  // tokens under the Light toolbar item.
  React.useEffect(() => {
    const root = document.documentElement;
    root.classList.toggle("dark", theme === "dark");
    root.classList.toggle("light", theme !== "dark");
    return () => root.classList.remove("dark", "light");
  }, [theme]);
  // A page story (`parameters: { page: true }`, the `Pages/` stories) draws
  // its own edges, so its sticky bar meets the top of the frame. Every other
  // story sits 24px in.
  const page = context.parameters.page === true;
  // A docs page draws every story of a component one after another, so a
  // story there takes its own height. In the canvas it fills the frame.
  const docs = context.viewMode === "docs";
  return (
    <div
      className={[
        theme === "dark" ? "dark" : "light",
        "bg-background text-foreground",
        docs ? "" : "min-h-screen",
        page ? "" : "p-6",
      ]
        .filter(Boolean)
        .join(" ")}
    >
      <Story />
    </div>
  );
};

/**
 * The theme editor (#63): a Theme button on every page story (`page: true`,
 * the `Pages/` stories) opens a panel that previews a theme change on the
 * page and sends it to every site. Its Light and Dark switch sets the same
 * theme global as the toolbar, so either one turns the page, and the panel
 * edits the colours of the theme the page shows. Add `theme-editor=open` to
 * the iframe's query string to open the panel on load.
 */
const withThemeEditor: Decorator = (Story, context) => {
  const [globals, updateGlobals] = useGlobals();
  if (context.parameters.page !== true) return <Story />;
  const mode = globals.theme === "dark" ? "dark" : "light";
  return (
    <>
      <Story />
      <ThemeEditor mode={mode} onModeChange={(theme) => updateGlobals({ theme })} />
    </>
  );
};

const preview: Preview = {
  // Every component gets a Docs page built from its stories: the description,
  // the first story with its controls, the props table, then the rest of the
  // stories. The `Pages/` stories opt out with `!autodocs`.
  tags: ["autodocs"],
  // The last decorator wraps the others, so the editor sits inside the theme.
  decorators: [withThemeEditor, withTheme],
  globalTypes: {
    theme: {
      description: "Light / dark token theme",
      defaultValue: "light",
      toolbar: {
        title: "Theme",
        icon: "circlehollow",
        items: [
          { value: "light", title: "Light", icon: "sun" },
          { value: "dark", title: "Dark", icon: "moon" },
        ],
        dynamicTitle: true,
      },
    },
  },
  parameters: {
    layout: "fullscreen",
    controls: { expanded: true },
    // The Overview page first, then the groups in the order the README lists
    // them. Storybook reads this object as source, so it must stay a literal.
    options: {
      storySort: {
        order: [
          "Overview",
          "Foundations",
          "Primitives",
          "Forms",
          "Surfaces",
          "Navigation",
          "Overlays",
          "Brand",
          "Pages",
        ],
      },
    },
  },
};

export default preview;
