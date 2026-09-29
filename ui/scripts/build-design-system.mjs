// Builds the design-system bundle for the Claude Design project named in
// .design-sync/config.json. It writes three things under design-system/:
//
//   components/bundle.js  an IIFE that sets window.OxagenUI to the kit's exports
//   bundle.css            compiled Tailwind with the house tokens and fonts
//   index.d.ts            the export surface, re-exported from types/
//
// Run it from ui/ as `pnpm build:design-system`. That script emits the
// declarations into dist/types first (`pnpm build:types`), and this file copies
// them.
import { build } from "esbuild";
import postcss from "postcss";
import tailwind from "@tailwindcss/postcss";
import { cp, mkdir, readFile, rm, stat, writeFile, copyFile } from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const out = path.join(root, "design-system");
const cssEntry = path.join(root, "src/styles/globals.css");

// The design page loads React and ReactDOM 18 as UMD globals. The bundle reads
// them from window, because a second React would break every hook.
const jsxRuntime = `
const R = window.React;
function jsx(type, props, key) {
  return R.createElement(type, key === undefined ? props : { ...props, key });
}
module.exports = { Fragment: R.Fragment, jsx, jsxs: jsx, jsxDEV: jsx };
`;
const reactGlobals = {
  react: "module.exports = window.React;",
  "react-dom": "module.exports = window.ReactDOM;",
  "react-dom/client": "module.exports = window.ReactDOM;",
  "react/jsx-runtime": jsxRuntime,
  "react/jsx-dev-runtime": jsxRuntime,
};

const reactFromWindow = {
  name: "react-from-window",
  setup(b) {
    b.onResolve({ filter: /^react(-dom)?(\/.*)?$/ }, (args) => ({
      path: args.path,
      namespace: "react-from-window",
    }));
    b.onLoad({ filter: /.*/, namespace: "react-from-window" }, (args) => {
      const contents = reactGlobals[args.path];
      if (contents === undefined) {
        throw new Error(`No window global maps to "${args.path}". Add it to reactGlobals.`);
      }
      return { contents, loader: "js" };
    });
  },
};

async function exists(file) {
  try {
    await stat(file);
    return true;
  } catch {
    return false;
  }
}

async function buildJs() {
  await build({
    entryPoints: [path.join(root, "src/index.ts")],
    outfile: path.join(out, "components/bundle.js"),
    bundle: true,
    format: "iife",
    globalName: "OxagenUI",
    platform: "browser",
    target: "es2020",
    jsx: "automatic",
    minify: true,
    define: { "process.env.NODE_ENV": '"production"' },
    loader: { ".css": "empty" },
    plugins: [reactFromWindow],
    logLevel: "info",
  });
}

// Tailwind inlines tokens/house-fonts.css, whose url()s point at fonts/ at the
// repository root. The bundle ships beside no repository, so each font is
// copied to design-system/fonts/ and its url() rewritten to match. A url() that
// resolves to no file fails the build, so a moved font cannot ship as a 404.
async function bundleFonts(css) {
  const fontsOut = path.join(out, "fonts");
  await mkdir(fontsOut, { recursive: true });
  const bases = [path.dirname(cssEntry), root];
  const seen = new Map();
  const pattern = /url\((["']?)([^"')]+\.(?:woff2?|ttf|otf))\1\)/g;
  for (const match of css.matchAll(pattern)) {
    const ref = match[2];
    if (seen.has(ref) || /^(data:|https?:)/.test(ref)) continue;
    let source;
    for (const base of bases) {
      const candidate = path.resolve(base, ref);
      if (await exists(candidate)) {
        source = candidate;
        break;
      }
    }
    if (!source) throw new Error(`bundle.css references ${ref}, which resolves to no file.`);
    const name = path.basename(source);
    await copyFile(source, path.join(fontsOut, name));
    seen.set(ref, `./fonts/${name}`);
  }
  return css.replace(pattern, (whole, quote, ref) =>
    seen.has(ref) ? `url(${quote}${seen.get(ref)}${quote})` : whole,
  );
}

async function buildCss() {
  const source = await readFile(cssEntry, "utf8");
  const result = await postcss([tailwind({ base: root, optimize: { minify: true } })]).process(
    source,
    { from: cssEntry },
  );
  const css = await bundleFonts(result.css);
  await writeFile(path.join(out, "bundle.css"), css);
}

async function copyTypes() {
  const types = path.join(root, "dist/types");
  if (!(await exists(path.join(types, "index.d.ts")))) {
    throw new Error("dist/types/index.d.ts is missing. Run `pnpm build:types` first.");
  }
  await cp(types, path.join(out, "types"), { recursive: true });
  await writeFile(path.join(out, "index.d.ts"), 'export * from "./types/index";\n');
}

await rm(out, { recursive: true, force: true });
await mkdir(path.join(out, "components"), { recursive: true });
await Promise.all([buildJs(), buildCss(), copyTypes()]);
console.log(`design-system bundle written to ${path.relative(process.cwd(), out) || "."}`);
