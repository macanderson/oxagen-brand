// Render og/og.html to public/og.png at 1200 x 630 with headless Chromium.
// No server: Playwright answers every request from the files in this folder.
// Run: npm run og   (uses the Playwright install on the machine)

import { execSync } from "node:child_process";
import { readFileSync } from "node:fs";
import { createRequire } from "node:module";
import { dirname, extname, join } from "node:path";
import { fileURLToPath } from "node:url";

const root = join(dirname(fileURLToPath(import.meta.url)), "..");
const require = createRequire(import.meta.url);
let pw;
try {
  pw = require("playwright");
} catch {
  pw = require(require.resolve("playwright", { paths: [execSync("npm root -g").toString().trim()] }));
}
const TYPES = { ".html": "text/html", ".woff2": "font/woff2", ".svg": "image/svg+xml", ".png": "image/png" };

const browser = await pw.chromium.launch();
const page = await browser.newPage({ viewport: { width: 1200, height: 630 }, deviceScaleFactor: 1 });
await page.route("https://og.local/**", (route) => {
  const path = decodeURIComponent(new URL(route.request().url()).pathname);
  route.fulfill({ body: readFileSync(join(root, path)), contentType: TYPES[extname(path)] ?? "application/octet-stream" });
});
await page.goto("https://og.local/og/og.html");
await page.evaluate(() => document.fonts.ready);
await page.screenshot({ path: join(root, "public/og.png"), clip: { x: 0, y: 0, width: 1200, height: 630 } });
await browser.close();
console.log("wrote public/og.png");
