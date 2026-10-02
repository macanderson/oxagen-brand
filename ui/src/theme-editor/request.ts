/**
 * A theme request: what Update all sites sends to GitHub.
 *
 * The request holds only the fields the draft changes, in the shape
 * `theme/request.schema.json` gives it (written by `build/request.py`). The
 * editor opens GitHub's new-file page with the request filled in, and Mac
 * commits it to a new branch with his own login. The apply-theme workflow
 * then merges it into `theme/theme.json` on that branch's pull request.
 *
 * A request never names the wordmark face. It is fixed, so the request schema
 * has no `faces.wordmark` and the workflow refuses one. A gold change still
 * reaches the wordmarks' gold x and asterisk through `color.gold`.
 */
import {
  FACE_ROLES,
  ROLES,
  SHIPPED,
  type FaceChoice,
  type FaceRole,
  type Theme,
} from "./theme";

export const REPO = "oxageninc/brand";

/**
 * The longest new-file link the editor opens. On 2026-10-02 GitHub answered a
 * new-file link of about 6,900 characters with an error: a signed-out visit
 * redirects to sign-in with the whole link inside the redirect, and that
 * fails first. Past 9,000 characters every visit fails. The editor stops at
 * 6,000 and offers a download instead.
 */
export const MAX_URL_LENGTH = 6000;

/** The sections a request changes field by field. */
const PARTIAL_SECTIONS = ["color", "radius", "shadow", "spacing", "type"] as const;

export interface Change {
  /** The field, as a dotted path such as `color.gold`. */
  path: string;
  before: unknown;
  after: unknown;
}

type Json = null | boolean | number | string | Json[] | { [key: string]: Json };

function isObject(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}

/** Every leaf that differs between two JSON values, in the order `after` lists them. */
export function diffJson(before: unknown, after: unknown, prefix = ""): Change[] {
  if (isObject(before) && isObject(after)) {
    const keys = [...Object.keys(after), ...Object.keys(before).filter((k) => !(k in after))];
    return keys.flatMap((k) => diffJson(before[k], after[k], prefix ? `${prefix}.${k}` : k));
  }
  return JSON.stringify(before) === JSON.stringify(after) ? [] : [{ path: prefix, before, after }];
}

/** The part of `after` that differs from `before`, nested as the theme nests it. */
export function partialDiff(before: unknown, after: unknown): Json | undefined {
  if (isObject(before) && isObject(after)) {
    const out: { [key: string]: Json } = {};
    for (const key of Object.keys(after)) {
      const sub = partialDiff(before[key], after[key]);
      if (sub !== undefined) out[key] = sub;
    }
    return Object.keys(out).length ? out : undefined;
  }
  return JSON.stringify(before) === JSON.stringify(after) ? undefined : (after as Json);
}

/** A face choice as the request names it, or undefined when the role keeps its shipped face. */
export function faceRequest(role: FaceRole, choice: FaceChoice): Json | undefined {
  const shipped = SHIPPED.faces[role];
  switch (choice.kind) {
    case "shipped":
      return undefined;
    case "kit": {
      if (choice.family === shipped.family) return undefined;
      const face = ROLES.map((r) => SHIPPED.faces[r]).find((f) => f.family === choice.family);
      if (!face) return undefined;
      return {
        family: face.family,
        source: "kit",
        files: face.files.map((f) => ({ ...f })),
        fallback: [...face.fallback],
        features: [...face.features],
      };
    }
    case "google":
      return { family: choice.family, source: "google", weights: [...choice.weights].sort((a, b) => a - b) };
    case "upload":
      return {
        family: choice.family,
        source: "upload",
        files: choice.files.map((f) => ({ file: f.name, weight: f.weight })),
      };
  }
}

/** The fields a draft changes, for the diff view: theme fields, then faces. */
export function draftChanges(theme: Theme, faces: Record<FaceRole, FaceChoice>): Change[] {
  const out: Change[] = [];
  for (const section of PARTIAL_SECTIONS) {
    out.push(...diffJson(SHIPPED[section], theme[section], section));
  }
  for (const role of FACE_ROLES) {
    const face = faceRequest(role, faces[role]);
    if (face !== undefined) {
      out.push({ path: `faces.${role}`, before: SHIPPED.faces[role].family, after: face });
    }
  }
  return out;
}

/** Characters the request schema allows in a summary. */
const SUMMARY_CHARS = /[^A-Za-z0-9 .,:;()'/+&#%-]/g;

/** A summary the schema accepts: allowed characters, starting with a letter or digit, at most 120. */
export function cleanSummary(text: string): string {
  return text
    .replace(SUMMARY_CHARS, "")
    .replace(/\s+/g, " ")
    .trim()
    .replace(/^[^A-Za-z0-9]+/, "")
    .slice(0, 120)
    .trim();
}

const ROLE_WORDS: Record<FaceRole, string> = {
  display: "headings",
  sans: "text",
  mono: "code",
};

/** A summary written from the changes, for when Mac does not write one. */
export function autoSummary(theme: Theme, faces: Record<FaceRole, FaceChoice>): string {
  const parts: string[] = [];
  if (theme.color.gold !== SHIPPED.color.gold) parts.push(`gold ${theme.color.gold}`);
  const colours = diffJson(SHIPPED.color, theme.color).filter((c) => c.path !== "gold").length;
  if (colours) parts.push(`${colours} colour${colours === 1 ? "" : "s"}`);
  for (const role of FACE_ROLES) {
    const choice = faces[role];
    if (faceRequest(role, choice) !== undefined && choice.kind !== "shipped") {
      parts.push(`${choice.family} for ${ROLE_WORDS[role]}`);
    }
  }
  for (const [section, word] of [
    ["radius", "corners"],
    ["shadow", "shadows"],
    ["spacing", "spacing"],
    ["type", "type sizes"],
  ] as const) {
    if (diffJson(SHIPPED[section], theme[section]).length) parts.push(word);
  }
  if (!parts.length) return "";
  const text = parts.join(", ");
  return cleanSummary(text.charAt(0).toUpperCase() + text.slice(1));
}

/** The request file for a draft. It names only the roles in `FACE_ROLES`, so never the wordmark. */
export function buildRequest(
  theme: Theme,
  faces: Record<FaceRole, FaceChoice>,
  summary: string,
  now: Date,
): Record<string, Json> {
  const request: Record<string, Json> = {
    $schema: "../request.schema.json",
    summary: cleanSummary(summary) || autoSummary(theme, faces) || "Theme change",
    requested_at: now.toISOString().slice(0, 16) + "Z",
  };
  for (const section of PARTIAL_SECTIONS) {
    const part = partialDiff(SHIPPED[section], theme[section]);
    if (part !== undefined) request[section] = part;
  }
  const faceEntries: { [key: string]: Json } = {};
  for (const role of FACE_ROLES) {
    const face = faceRequest(role, faces[role]);
    if (face !== undefined) faceEntries[role] = face;
  }
  if (Object.keys(faceEntries).length) request.faces = faceEntries;
  return request;
}

/** Whether a request changes anything. */
export function requestChanges(request: Record<string, Json>): boolean {
  return [...PARTIAL_SECTIONS, "faces"].some((k) => k in request);
}

/** The request as the file holds it. */
export function requestText(request: Record<string, Json>): string {
  return `${JSON.stringify(request, null, 2)}\n`;
}

/** A lowercase slug of at most 40 characters. */
export function slugify(text: string): string {
  return text
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-+|-+$/g, "")
    .slice(0, 40)
    .replace(/-+$/, "");
}

/** `yyyy-mm-dd-hhmm` in UTC. */
export function stamp(now: Date): string {
  const iso = now.toISOString();
  return `${iso.slice(0, 10)}-${iso.slice(11, 13)}${iso.slice(14, 16)}`;
}

/** The request's file name in `theme/requests/`: `<yyyy-mm-dd-hhmm>-<slug>.json`. */
export function requestFileName(summary: string, now: Date): string {
  const slug = slugify(summary) || "theme";
  return `${stamp(now)}-${slug}.json`;
}

/** A branch name for a request that needs uploaded fonts: no slash, so GitHub reads it as one ref. */
export function branchName(summary: string, now: Date): string {
  return `theme-${stamp(now)}-${slugify(summary) || "request"}`;
}

/** GitHub's new-file page on `branch`, with the request filled in. */
export function newFileUrl(request: Record<string, Json>, fileName: string, branch = "main"): string {
  const params = new URLSearchParams({
    filename: `theme/requests/${fileName}`,
    value: requestText(request),
  });
  return `https://github.com/${REPO}/new/${branch}?${params.toString()}`;
}

/** Whether the new-file link fits under `MAX_URL_LENGTH`. */
export function fitsInUrl(url: string): boolean {
  return url.length <= MAX_URL_LENGTH;
}

/** GitHub's upload page for a folder on a branch. */
export function uploadUrl(folder: "fonts" | "theme/requests", branch = "main"): string {
  return `https://github.com/${REPO}/upload/${branch}/${folder}`;
}

/** The uploaded files a request needs on its branch before the workflow can apply it. */
export function uploadsNeeded(faces: Record<FaceRole, FaceChoice>): string[] {
  const names = new Set<string>();
  for (const role of FACE_ROLES) {
    const choice = faces[role];
    if (choice.kind === "upload") for (const f of choice.files) names.add(f.name);
  }
  return [...names];
}
