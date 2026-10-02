/**
 * The editor's draft: the theme with Mac's changes, and a face choice for each
 * role the editor may change. The wordmark face is fixed, so the draft holds
 * no choice for it. It lives in localStorage, so it survives a reload and a move to
 * another story, and it is written to `<html>` as CSS variables for the
 * preview.
 */
import {
  FACE_ROLES,
  SHIPPED,
  clone,
  themeVars,
  type FaceChoice,
  type FaceRole,
  type Theme,
} from "./theme";

export interface Draft {
  theme: Theme;
  faces: Record<FaceRole, FaceChoice>;
}

export const STORAGE_KEY = "oxagen-theme-editor-draft-v1";

export function shippedDraft(): Draft {
  return {
    theme: clone(SHIPPED),
    faces: Object.fromEntries(FACE_ROLES.map((r) => [r, { kind: "shipped" }])) as Record<FaceRole, FaceChoice>,
  };
}

function isObject(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}

/** `base` with every field `saved` holds in the same place and of the same kind. */
function overlay<T>(base: T, saved: unknown): T {
  if (isObject(base) && isObject(saved)) {
    const out: Record<string, unknown> = { ...base };
    for (const key of Object.keys(base)) {
      if (key in saved) out[key] = overlay((base as Record<string, unknown>)[key], saved[key]);
    }
    return out as T;
  }
  if (Array.isArray(base)) return (Array.isArray(saved) ? saved : base) as T;
  return (typeof saved === typeof base ? saved : base) as T;
}

function isFaceChoice(value: unknown): value is FaceChoice {
  if (!isObject(value)) return false;
  switch (value.kind) {
    case "shipped":
      return true;
    case "kit":
      return typeof value.family === "string";
    case "google":
      return typeof value.family === "string" && Array.isArray(value.weights);
    case "upload":
      return typeof value.family === "string" && Array.isArray(value.files);
    default:
      return false;
  }
}

/**
 * The saved draft, laid over the shipped theme so a field the theme gained
 * since the draft was saved takes its shipped value. A missing or unreadable
 * draft is the shipped theme. A draft saved before the wordmark face was
 * fixed may hold a wordmark choice, and loading drops it.
 */
export function loadDraft(storage: Pick<Storage, "getItem"> | undefined = safeStorage()): Draft {
  const fresh = shippedDraft();
  try {
    const raw = storage?.getItem(STORAGE_KEY);
    if (!raw) return fresh;
    const saved = JSON.parse(raw) as unknown;
    if (!isObject(saved)) return fresh;
    const faces = { ...fresh.faces };
    if (isObject(saved.faces)) {
      for (const role of FACE_ROLES) {
        const choice = saved.faces[role];
        if (isFaceChoice(choice)) faces[role] = choice;
      }
    }
    return { theme: overlay(fresh.theme, saved.theme), faces };
  } catch {
    return fresh;
  }
}

export function saveDraft(draft: Draft, storage: Pick<Storage, "setItem" | "removeItem"> | undefined = safeStorage()): void {
  try {
    if (isShipped(draft)) storage?.removeItem(STORAGE_KEY);
    else storage?.setItem(STORAGE_KEY, JSON.stringify(draft));
  } catch {
    // Storage is full or blocked. The draft still previews for this visit.
  }
}

/** localStorage, or undefined where the browser blocks it. */
function safeStorage(): Storage | undefined {
  try {
    return typeof window === "undefined" ? undefined : window.localStorage;
  } catch {
    return undefined;
  }
}

/** Whether a draft is the shipped theme with every face unchanged. */
export function isShipped(draft: Draft): boolean {
  return (
    JSON.stringify(draft.theme) === JSON.stringify(SHIPPED) &&
    FACE_ROLES.every((r) => draft.faces[r].kind === "shipped")
  );
}

const SHIPPED_VARS = themeVars(SHIPPED, shippedDraft().faces);

/** The variables a draft sets on `<html>`: only those that differ from the shipped theme. */
export function previewVars(draft: Draft): Record<string, string> {
  const vars = themeVars(draft.theme, draft.faces);
  return Object.fromEntries(Object.entries(vars).filter(([k, v]) => SHIPPED_VARS[k] !== v));
}

const SET_ATTR = "data-theme-editor-vars";

/** Write a draft's variables on `root`, and clear any the last draft set that this one does not. */
export function applyVars(root: HTMLElement, vars: Record<string, string>): void {
  const before = (root.getAttribute(SET_ATTR) ?? "").split(" ").filter(Boolean);
  for (const name of before) if (!(name in vars)) root.style.removeProperty(name);
  for (const [name, value] of Object.entries(vars)) root.style.setProperty(name, value);
  const names = Object.keys(vars);
  if (names.length) root.setAttribute(SET_ATTR, names.join(" "));
  else root.removeAttribute(SET_ATTR);
}

/** Remove every variable the editor set on `root`. */
export function clearVars(root: HTMLElement): void {
  applyVars(root, {});
}
