/**
 * Building a theme request, its file name, its GitHub link, and the length guard.
 */
import { describe, expect, it } from "vitest";
import {
  MAX_URL_LENGTH,
  autoSummary,
  branchName,
  buildRequest,
  cleanSummary,
  diffJson,
  draftChanges,
  fitsInUrl,
  newFileUrl,
  partialDiff,
  requestChanges,
  requestFileName,
  requestText,
  uploadUrl,
  uploadsNeeded,
} from "./request";
import { SHIPPED, clone, type FaceChoice, type Role } from "./theme";

const NOW = new Date("2026-10-01T23:05:42Z");

/** The first of `choices` that differs from `value`, so a test changes the theme whatever it ships. */
const other = <T,>(value: T, ...choices: T[]): T => choices.find((c) => c !== value) as T;

const shippedFaces = (): Record<Role, FaceChoice> => ({
  wordmark: { kind: "shipped" },
  display: { kind: "shipped" },
  sans: { kind: "shipped" },
  mono: { kind: "shipped" },
});

describe("the JSON diff", () => {
  it("lists each changed leaf with its path", () => {
    expect(diffJson({ a: 1, b: { c: 2, d: [1] } }, { a: 1, b: { c: 3, d: [1, 2] } })).toEqual([
      { path: "b.c", before: 2, after: 3 },
      { path: "b.d", before: [1], after: [1, 2] },
    ]);
  });

  it("returns nothing for equal values", () => {
    expect(diffJson(SHIPPED, clone(SHIPPED))).toEqual([]);
  });

  it("nests only the changed fields", () => {
    expect(partialDiff({ a: 1, b: { c: 2, d: 3 } }, { a: 1, b: { c: 2, d: 4 } })).toEqual({ b: { d: 4 } });
    expect(partialDiff({ a: 1 }, { a: 1 })).toBeUndefined();
  });
});

describe("the request", () => {
  it("holds only the fields the draft changes", () => {
    const theme = clone(SHIPPED);
    const gold = other(SHIPPED.color.gold, "#C99B2E", "#D9B13B");
    const panel = other(SHIPPED.color.ink.panel, "#1C1C1F", "#1A1A1D");
    const base = other(SHIPPED.radius.base, "0.5rem", "0.45rem");
    const size = other(SHIPPED.type.scales.app.body.size, "0.9375rem", "0.875rem");
    theme.color.gold = gold;
    theme.color.ink.panel = panel;
    theme.radius.base = base;
    theme.type.scales.app.body.size = size;
    const request = buildRequest(theme, shippedFaces(), "A deeper gold", NOW);
    expect(request).toEqual({
      $schema: "../request.schema.json",
      summary: "A deeper gold",
      requested_at: "2026-10-01T23:05Z",
      color: { gold, ink: { panel } },
      radius: { base },
      type: { scales: { app: { body: { size } } } },
    });
    expect(requestChanges(request)).toBe(true);
  });

  it("changes nothing for the shipped theme", () => {
    const request = buildRequest(clone(SHIPPED), shippedFaces(), "", NOW);
    expect(requestChanges(request)).toBe(false);
  });

  it("names a Google face by family and weights", () => {
    const faces = shippedFaces();
    faces.display = { kind: "google", family: "Inter", weights: [700, 400, 600, 500] };
    const request = buildRequest(clone(SHIPPED), faces, "", NOW);
    expect(request.faces).toEqual({ display: { family: "Inter", source: "google", weights: [400, 500, 600, 700] } });
    expect(request.summary).toBe("Inter for headings");
  });

  it("names uploaded files by the name they take in fonts/", () => {
    const faces = shippedFaces();
    faces.sans = {
      kind: "upload",
      family: "Aeonik",
      files: [
        { name: "Aeonik-Regular.otf", original: "Aeonik Regular.otf", weight: "400" },
        { name: "Aeonik-Bold.otf", original: "Aeonik-Bold.otf", weight: "700" },
      ],
    };
    const request = buildRequest(clone(SHIPPED), faces, "Aeonik for text", NOW);
    expect(request.faces).toEqual({
      sans: {
        family: "Aeonik",
        source: "upload",
        files: [
          { file: "Aeonik-Regular.otf", weight: "400" },
          { file: "Aeonik-Bold.otf", weight: "700" },
        ],
      },
    });
    expect(uploadsNeeded(faces)).toEqual(["Aeonik-Regular.otf", "Aeonik-Bold.otf"]);
  });

  it("names a kit face with its files, and leaves out a role that keeps its face", () => {
    const faces = shippedFaces();
    // The code face's family for headings, and the text face's own family for text.
    faces.display = { kind: "kit", family: SHIPPED.faces.mono.family };
    faces.sans = { kind: "kit", family: SHIPPED.faces.sans.family };
    const request = buildRequest(clone(SHIPPED), faces, "", NOW);
    const named = request.faces as Record<string, { files: unknown } | undefined>;
    expect(Object.keys(named)).toEqual(["display"]);
    expect(named.display?.files).toEqual(SHIPPED.faces.mono.files);
  });

  it("lists face changes in the diff view", () => {
    const faces = shippedFaces();
    faces.mono = { kind: "google", family: "JetBrains Mono", weights: [400] };
    expect(draftChanges(clone(SHIPPED), faces).map((c) => c.path)).toEqual(["faces.mono"]);
  });
});

describe("the summary", () => {
  it("keeps only the characters the schema allows", () => {
    expect(cleanSummary("  <b>Gold!</b> — warmer  ")).toBe("bGold/b warmer");
    expect(cleanSummary("x".repeat(200))).toHaveLength(120);
  });

  it("is written from the changes when Mac writes none", () => {
    const theme = clone(SHIPPED);
    theme.color.gold = other(SHIPPED.color.gold, "#C99B2E", "#D9B13B");
    theme.color.paper.panel = other(SHIPPED.color.paper.panel, "#FAFAFA", "#FCFCFC");
    theme.spacing.unit = other(SHIPPED.spacing.unit, "0.3125rem", "0.25rem");
    expect(autoSummary(theme, shippedFaces())).toBe(`Gold ${theme.color.gold}, 1 colour, spacing`);
  });
});

describe("names and links", () => {
  it("names the file by time and summary", () => {
    expect(requestFileName("Inter for headings, a deeper gold", NOW)).toBe(
      "2026-10-01-2305-inter-for-headings-a-deeper-gold.json",
    );
    expect(requestFileName("", NOW)).toBe("2026-10-01-2305-theme.json");
  });

  it("names a branch with no slash", () => {
    expect(branchName("Aeonik for text", NOW)).toBe("theme-2026-10-01-2305-aeonik-for-text");
  });

  it("opens GitHub's new-file page with the request filled in", () => {
    const request = buildRequest(Object.assign(clone(SHIPPED), {}), shippedFaces(), "x", NOW);
    const url = new URL(newFileUrl(request, "2026-10-01-2305-x.json"));
    expect(url.origin + url.pathname).toBe("https://github.com/oxageninc/brand/new/main");
    expect(url.searchParams.get("filename")).toBe("theme/requests/2026-10-01-2305-x.json");
    expect(url.searchParams.get("value")).toBe(requestText(request));
    expect(newFileUrl(request, "f.json", "theme-x")).toContain("/new/theme-x?");
  });

  it("guards the link's length", () => {
    const theme = clone(SHIPPED);
    theme.color.gold = other(SHIPPED.color.gold, "#C99B2E", "#D9B13B");
    const small = newFileUrl(buildRequest(theme, shippedFaces(), "x", NOW), "f.json");
    expect(fitsInUrl(small)).toBe(true);
    for (const step of ["h1", "h2", "h3", "h4", "body", "micro"] as const) {
      theme.type.scales.marketing[step].leading += 0.01;
      theme.type.scales.app[step].leading += 0.01;
    }
    theme.shadow.ui.ink = "0 1px 2px oklch(0.15 0 0 / 0.07), 0 0 0 1px oklch(0.2 0 0 / 0.2), 0 8px 24px -6px oklch(0.1 0 0 / 0.3)";
    const big = newFileUrl(buildRequest(theme, shippedFaces(), "x".repeat(120), NOW), "f.json");
    expect(big.length).toBeGreaterThan(small.length);
    expect(fitsInUrl("x".repeat(MAX_URL_LENGTH + 1))).toBe(false);
  });

  it("links the upload pages", () => {
    expect(uploadUrl("fonts")).toBe("https://github.com/oxageninc/brand/upload/main/fonts");
    expect(uploadUrl("theme/requests", "theme-x")).toBe("https://github.com/oxageninc/brand/upload/theme-x/theme/requests");
  });
});
