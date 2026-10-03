/**
 * Faces for the preview: Google Fonts by name, and font files Mac uploads.
 *
 * A Google family loads through a stylesheet link from fonts.googleapis.com.
 * An uploaded file loads with the FontFace API, and its bytes are kept in
 * IndexedDB so the preview survives a reload. None of this reaches the kit:
 * the apply-theme workflow fetches a Google family into `fonts/` itself, and
 * an uploaded file reaches `fonts/` when Mac uploads it to the request's
 * branch.
 */

/** Google families that suit each role, offered as suggestions. Any family on fonts.google.com works. */
export const GOOGLE_SUGGESTIONS: Record<"text" | "mono", string[]> = {
  text: [
    "Inter",
    "Geist",
    "Space Grotesk",
    "Manrope",
    "DM Sans",
    "IBM Plex Sans",
    "Plus Jakarta Sans",
    "Work Sans",
    "Outfit",
    "Sora",
    "Figtree",
    "Public Sans",
    "Source Sans 3",
    "Instrument Sans",
    "Schibsted Grotesk",
    "Bricolage Grotesque",
  ],
  mono: [
    "JetBrains Mono",
    "IBM Plex Mono",
    "Geist Mono",
    "Fira Code",
    "Source Code Pro",
    "DM Mono",
    "Space Mono",
    "Roboto Mono",
  ],
};

/** The weights the editor offers for a Google family. */
export const WEIGHTS = [100, 200, 300, 400, 500, 600, 700, 800, 900] as const;

/** A family name the theme accepts: letters, digits, spaces, and dashes. */
export function isFamilyName(name: string): boolean {
  return /^[A-Za-z0-9][A-Za-z0-9 -]{0,62}$/.test(name);
}

/** The stylesheet URL for a Google family at some weights. */
export function googleCssUrl(family: string, weights: readonly number[]): string {
  const list = [...new Set(weights)].sort((a, b) => a - b).join(";");
  return `https://fonts.googleapis.com/css2?family=${encodeURIComponent(family).replace(/%20/g, "+")}:wght@${list}&display=swap`;
}

const LINK_ATTR = "data-theme-editor-font";

/**
 * Load a Google family into the page. Resolves once the stylesheet loads, and
 * rejects when Google Fonts has no such family at those weights.
 */
export function loadGoogleFont(family: string, weights: readonly number[]): Promise<void> {
  const href = googleCssUrl(family, weights);
  const existing = [...document.head.querySelectorAll<HTMLLinkElement>(`link[${LINK_ATTR}]`)].some(
    (link) => link.getAttribute(LINK_ATTR) === href,
  );
  if (existing) return Promise.resolve();
  return new Promise((resolve, reject) => {
    const link = document.createElement("link");
    link.rel = "stylesheet";
    link.href = href;
    link.setAttribute(LINK_ATTR, href);
    link.onload = () => resolve();
    link.onerror = () => {
      link.remove();
      reject(new Error(`Google Fonts has no family named ${family} at these weights.`));
    };
    document.head.appendChild(link);
  });
}

/** The weight a file's name suggests: Bold is 700, Medium 500, and Regular or no word 400. */
export function weightFromName(name: string): string {
  const n = name.toLowerCase().replace(/[^a-z]/g, "");
  if (/variable|vf|wght/.test(n)) return "100 900";
  const words: [RegExp, string][] = [
    [/hairline|thin/, "100"],
    [/extralight|ultralight/, "200"],
    [/light/, "300"],
    [/semibold|demibold/, "600"],
    [/extrabold|ultrabold/, "800"],
    [/black|heavy/, "900"],
    [/bold/, "700"],
    [/medium/, "500"],
  ];
  for (const [pattern, weight] of words) if (pattern.test(n)) return weight;
  return "400";
}

/** A file name the theme accepts, made from an uploaded file's name. */
export function fontFileName(original: string): string {
  const dot = original.lastIndexOf(".");
  const ext = original.slice(dot + 1).toLowerCase();
  const stem = original
    .slice(0, dot)
    .replace(/[^A-Za-z0-9._-]+/g, "-")
    .replace(/^[^A-Za-z0-9]+/, "")
    .replace(/-+$/, "")
    .slice(0, 100);
  return `${stem || "font"}.${ext}`;
}

/** Whether a file is a font type the kit takes. */
export function isFontFile(name: string): boolean {
  return /\.(woff2|woff|ttf|otf)$/i.test(name);
}

/** Load font bytes into the page as `family` at `weight`. */
export async function loadFontBytes(family: string, bytes: ArrayBuffer, weight: string): Promise<void> {
  const face = new FontFace(family, bytes, { weight, style: "normal", display: "swap" });
  await face.load();
  document.fonts.add(face);
}

// --------------------------------------------------------------------------
// uploaded bytes, kept across reloads
// --------------------------------------------------------------------------

const DB_NAME = "oxagen-theme-editor";
const STORE = "fonts";

function openDb(): Promise<IDBDatabase> {
  return new Promise((resolve, reject) => {
    const req = indexedDB.open(DB_NAME, 1);
    req.onupgradeneeded = () => req.result.createObjectStore(STORE);
    req.onsuccess = () => resolve(req.result);
    req.onerror = () => reject(req.error ?? new Error("IndexedDB did not open"));
  });
}

/** Keep an uploaded file's bytes, under the name it takes in fonts/. Fails quietly where storage is off. */
export async function saveFontBytes(name: string, bytes: ArrayBuffer): Promise<void> {
  try {
    const db = await openDb();
    await new Promise<void>((resolve, reject) => {
      const tx = db.transaction(STORE, "readwrite");
      tx.objectStore(STORE).put(bytes, name);
      tx.oncomplete = () => resolve();
      tx.onerror = () => reject(tx.error ?? new Error("IndexedDB write failed"));
    });
    db.close();
  } catch {
    // A private window or blocked storage keeps the font for this visit only.
  }
}

/** The kept bytes of an uploaded file, or null when this browser has none. */
export async function readFontBytes(name: string): Promise<ArrayBuffer | null> {
  try {
    const db = await openDb();
    const bytes = await new Promise<ArrayBuffer | null>((resolve, reject) => {
      const req = db.transaction(STORE, "readonly").objectStore(STORE).get(name);
      req.onsuccess = () => resolve((req.result as ArrayBuffer | undefined) ?? null);
      req.onerror = () => reject(req.error ?? new Error("IndexedDB read failed"));
    });
    db.close();
    return bytes;
  } catch {
    return null;
  }
}
