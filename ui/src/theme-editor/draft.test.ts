/**
 * The draft: what survives a reload, and what reaches `<html>`.
 */
import { describe, expect, it } from "vitest";
import { STORAGE_KEY, applyVars, clearVars, isShipped, loadDraft, previewVars, saveDraft, shippedDraft } from "./draft";
import { derivePalette } from "./palette";
import { SHIPPED, rampVars } from "./theme";

/** A gold that differs from the shipped one, whatever the kit ships. */
const NEW_GOLD = SHIPPED.color.gold === "#C99B2E" ? "#D9B13B" : "#C99B2E";

function memoryStorage(initial: Record<string, string> = {}) {
  const data = new Map(Object.entries(initial));
  return {
    data,
    getItem: (k: string) => data.get(k) ?? null,
    setItem: (k: string, v: string) => void data.set(k, v),
    removeItem: (k: string) => void data.delete(k),
  };
}

/** The slice of an element `applyVars` touches. */
function fakeRoot() {
  const props = new Map<string, string>();
  const attrs = new Map<string, string>();
  return {
    props,
    style: {
      setProperty: (k: string, v: string) => void props.set(k, v),
      removeProperty: (k: string) => {
        props.delete(k);
        return "";
      },
    },
    getAttribute: (k: string) => attrs.get(k) ?? null,
    setAttribute: (k: string, v: string) => void attrs.set(k, v),
    removeAttribute: (k: string) => void attrs.delete(k),
  };
}

describe("loading and saving", () => {
  it("starts from the shipped theme", () => {
    const draft = loadDraft(memoryStorage());
    expect(isShipped(draft)).toBe(true);
    expect(draft.theme).toEqual(SHIPPED);
  });

  it("round-trips a draft", () => {
    const storage = memoryStorage();
    const draft = shippedDraft();
    draft.theme.color.gold = NEW_GOLD;
    draft.faces.display = { kind: "google", family: "Example Sans", weights: [400, 700] };
    saveDraft(draft, storage);
    expect(loadDraft(storage)).toEqual(draft);
  });

  it("forgets the draft once it matches the shipped theme", () => {
    const storage = memoryStorage({ [STORAGE_KEY]: "{}" });
    saveDraft(shippedDraft(), storage);
    expect(storage.data.has(STORAGE_KEY)).toBe(false);
  });

  it("keeps the shipped value for a field the saved draft lacks or holds wrongly", () => {
    const saved = { theme: { color: { gold: "#C99B2E", ink: { panel: 7 } } }, faces: { mono: { kind: "nonsense" } } };
    const draft = loadDraft(memoryStorage({ [STORAGE_KEY]: JSON.stringify(saved) }));
    expect(draft.theme.color.gold).toBe("#C99B2E");
    expect(draft.theme.color.ink.panel).toBe(SHIPPED.color.ink.panel);
    expect(draft.theme.radius).toEqual(SHIPPED.radius);
    expect(draft.faces.mono).toEqual({ kind: "shipped" });
  });

  it("drops a wordmark choice saved before the wordmark face was fixed", () => {
    const mono = { kind: "google", family: "Example Mono", weights: [400] };
    const saved = { faces: { wordmark: { kind: "google", family: "Inter", weights: [600] }, mono } };
    const draft = loadDraft(memoryStorage({ [STORAGE_KEY]: JSON.stringify(saved) }));
    expect(Object.keys(draft.faces)).toEqual(["display", "sans", "mono"]);
    expect(draft.faces.mono).toEqual(mono);
    expect(previewVars(draft)["--ox-font-wordmark"]).toBeUndefined();

    const onlyWordmark = { faces: { wordmark: { kind: "upload", family: "Aeonik", files: [] } } };
    expect(isShipped(loadDraft(memoryStorage({ [STORAGE_KEY]: JSON.stringify(onlyWordmark) })))).toBe(true);
  });

  it("survives an unreadable draft", () => {
    expect(isShipped(loadDraft(memoryStorage({ [STORAGE_KEY]: "{not json" })))).toBe(true);
  });
});

describe("the preview", () => {
  it("sets nothing for the shipped theme", () => {
    expect(previewVars(shippedDraft())).toEqual({});
  });

  it("sets the gold, its neighbours, and the ramp for a new gold", () => {
    const draft = shippedDraft();
    draft.theme.color.gold = NEW_GOLD;
    const vars = previewVars(draft);
    const palette = derivePalette(draft.theme.color);
    expect(vars["--ox-gold"]).toBe(NEW_GOLD);
    expect(vars["--ox-gold-bright"]).toBe(palette.goldBright);
    expect(vars["--ox-gold-deep"]).toBe(palette.goldDeep);
    expect(vars["--ox-ember-soft"]).toBe(rampVars(NEW_GOLD)["--ox-ember-soft"]);
    expect(vars["--ox-ink"]).toBeUndefined();
  });

  it("sets a face's stack", () => {
    const draft = shippedDraft();
    draft.faces.mono = { kind: "google", family: "Example Mono", weights: [400] };
    expect(previewVars(draft)).toEqual({
      "--ox-font-mono": '"Example Mono", ui-monospace, "SF Mono", Menlo, Consolas, monospace',
    });
  });

  it("clears what an earlier draft set", () => {
    const root = fakeRoot();
    applyVars(root as unknown as HTMLElement, { "--ox-gold": "#C99B2E", "--ox-space": "0.3125rem" });
    applyVars(root as unknown as HTMLElement, { "--ox-gold": "#D9B13B" });
    expect([...root.props]).toEqual([["--ox-gold", "#D9B13B"]]);
    clearVars(root as unknown as HTMLElement);
    expect(root.props.size).toBe(0);
  });
});
