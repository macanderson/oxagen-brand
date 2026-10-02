"use client";
/**
 * The faces part of the theme editor. The wordmark role is read-only: its
 * face is fixed, Space Grotesk drawn at weight 600 (Mac, 2026-10-02). Each
 * other role takes the shipped face, a face the kit already ships, a Google
 * family, or uploaded files. Marketing headings is the display role: h1 to h3
 * on a marketing or customer site. App headings and every h4 to h6 take the
 * text face.
 */
import * as React from "react";
import { OxagenWordmark, StellaWordmark } from "../components/brand";
import { Button } from "../components/button";
import { inputBase } from "../components/control-styles";
import { cn } from "../lib/utils";
import { SelectField, TextField } from "./controls";
import {
  GOOGLE_SUGGESTIONS,
  WEIGHTS,
  fontFileName,
  isFamilyName,
  isFontFile,
  loadFontBytes,
  saveFontBytes,
  weightFromName,
} from "./fonts";
import {
  ROLES,
  SHIPPED,
  WORDMARK_STACK,
  choiceFamily,
  fontStack,
  type FaceChoice,
  type FaceRole,
  type Role,
  type UploadedFile,
} from "./theme";

export const ROLE_LABELS: Record<Role, string> = {
  wordmark: "Wordmark",
  display: "Marketing headings",
  sans: "Text",
  mono: "Code",
};

const ROLE_SAMPLES: Record<Role, string> = {
  wordmark: "oxagen stella",
  display: "Every agent has an owner",
  sans: "The rule allowed the request, and the record keeps the answer.",
  mono: "run_8fa21c  step 14  allowed",
};

/** The families the kit already has files for. */
const KIT_FAMILIES = [...new Set(ROLES.map((r) => SHIPPED.faces[r].family))];

/** The status of loading a face into the page. */
export type LoadState = "idle" | "loading" | "ready" | "failed";

type SourceKey = "shipped" | `kit:${string}` | "google" | "upload";

function sourceKey(choice: FaceChoice): SourceKey {
  if (choice.kind === "kit") return `kit:${choice.family}`;
  return choice.kind;
}

const UPLOAD_WEIGHTS = [
  ...WEIGHTS.map((w) => ({ value: String(w), label: String(w) })),
  { value: "100 900", label: "Variable, 100 to 900" },
];

/**
 * The wordmark role: its face, a line set in it, and the drawn marks. The
 * face is fixed, so the row has no picker. The marks paint their gold x and
 * asterisk from `--ox-gold`, so they follow the primary colour as it changes.
 */
export function WordmarkFace() {
  const face = SHIPPED.faces.wordmark;
  return (
    <div
      role="group"
      aria-label={ROLE_LABELS.wordmark}
      className="flex flex-col gap-2.5 rounded-2xl border border-border/70 bg-background/40 p-3"
    >
      <div className="flex items-center gap-2">
        <span className="min-w-0 flex-1 text-sm text-foreground">{ROLE_LABELS.wordmark}</span>
        <span className="text-xs text-muted-foreground">{face.family}</span>
      </div>
      <p
        className="truncate rounded-lg bg-muted/60 px-2.5 py-2 text-(length:--ox-a-h3) font-semibold text-foreground"
        style={{ fontFamily: WORDMARK_STACK }}
      >
        {ROLE_SAMPLES.wordmark}
      </p>
      <div className="flex items-center gap-4 text-foreground">
        <OxagenWordmark className="h-5" />
        <StellaWordmark className="h-5" />
      </div>
      <p className="text-xs leading-normal text-muted-foreground">
        The wordmark face is fixed. The gold x and asterisk follow the primary colour.
      </p>
    </div>
  );
}

export function FaceEditor({
  role,
  choice,
  load,
  onChange,
}: {
  role: FaceRole;
  choice: FaceChoice;
  load: LoadState;
  onChange: (choice: FaceChoice) => void;
}) {
  const shipped = SHIPPED.faces[role];
  const family = choiceFamily(role, choice);
  const sourceOptions: { value: SourceKey; label: string }[] = [
    { value: "shipped", label: `${shipped.family} (shipped)` },
    ...KIT_FAMILIES.filter((f) => f !== shipped.family).map((f) => ({
      value: `kit:${f}` as SourceKey,
      label: `${f} (in the kit)`,
    })),
    { value: "google", label: "Google Fonts" },
    { value: "upload", label: "Uploaded files" },
  ];
  const suggestions = role === "mono" ? GOOGLE_SUGGESTIONS.mono : GOOGLE_SUGGESTIONS.text;
  const listId = `theme-editor-google-${role}`;

  const setSource = (key: SourceKey) => {
    if (key === "shipped") onChange({ kind: "shipped" });
    else if (key === "google")
      onChange({ kind: "google", family: suggestions[0] ?? "Inter", weights: role === "mono" ? [400, 500, 700] : [400, 500, 600, 700] });
    else if (key === "upload") onChange({ kind: "upload", family: "", files: [] });
    else onChange({ kind: "kit", family: key.slice(4) });
  };

  return (
    <div className="flex flex-col gap-2.5 rounded-2xl border border-border/70 bg-background/40 p-3">
      <SelectField
        label={ROLE_LABELS[role]}
        value={sourceKey(choice)}
        options={sourceOptions}
        onChange={setSource}
      />

      {choice.kind === "google" ? (
        <GoogleFields role={role} choice={choice} listId={listId} suggestions={suggestions} load={load} onChange={onChange} />
      ) : null}

      {choice.kind === "upload" ? <UploadFields choice={choice} load={load} onChange={onChange} /> : null}

      <p
        className={cn(
          "truncate rounded-lg bg-muted/60 px-2.5 py-2 text-foreground",
          role === "display" ? "text-(length:--ox-a-h3) font-semibold" : "text-sm",
        )}
        style={{ fontFamily: family ? fontStack(role, choice) : undefined }}
      >
        {ROLE_SAMPLES[role]}
      </p>
    </div>
  );
}

function GoogleFields({
  role,
  choice,
  listId,
  suggestions,
  load,
  onChange,
}: {
  role: FaceRole;
  choice: Extract<FaceChoice, { kind: "google" }>;
  listId: string;
  suggestions: string[];
  load: LoadState;
  onChange: (choice: FaceChoice) => void;
}) {
  const valid = isFamilyName(choice.family);
  const hint = !valid
    ? "Use the family's name as fonts.google.com spells it: letters, digits, spaces, and dashes."
    : load === "loading"
      ? "Loading from Google Fonts."
      : load === "failed"
        ? `Google Fonts has no family named ${choice.family} at these weights.`
        : role === "sans"
          ? "The workflow also fetches a TTF of this family, which the art's text is drawn from."
          : "The workflow fetches the latin files at these weights into fonts/.";
  return (
    <>
      <TextField
        label="Family"
        value={choice.family}
        list={listId}
        invalid={!valid || load === "failed"}
        hint={hint}
        onChange={(family) => onChange({ ...choice, family })}
      />
      <datalist id={listId}>
        {suggestions.map((s) => (
          <option key={s} value={s} />
        ))}
      </datalist>
      <fieldset className="flex flex-col gap-1.5">
        <legend className="mb-1 text-sm text-foreground">Weights</legend>
        <div className="flex flex-wrap gap-1.5">
          {WEIGHTS.map((w) => {
            const on = choice.weights.includes(w);
            return (
              <label
                key={w}
                className={cn(
                  "inline-flex cursor-pointer items-center gap-1 rounded-full border px-2 py-0.5 font-mono text-sm",
                  on ? "border-foreground/40 bg-foreground/10 text-foreground" : "border-border text-muted-foreground",
                )}
              >
                <input
                  type="checkbox"
                  className="sr-only"
                  checked={on}
                  onChange={() => {
                    const weights = on ? choice.weights.filter((x) => x !== w) : [...choice.weights, w];
                    if (weights.length) onChange({ ...choice, weights: weights.sort((a, b) => a - b) });
                  }}
                />
                {w}
              </label>
            );
          })}
        </div>
      </fieldset>
    </>
  );
}

function UploadFields({
  choice,
  load,
  onChange,
}: {
  choice: Extract<FaceChoice, { kind: "upload" }>;
  load: LoadState;
  onChange: (choice: FaceChoice) => void;
}) {
  const inputId = React.useId();
  const [error, setError] = React.useState("");

  const add = async (list: FileList | null) => {
    if (!list) return;
    const files = [...list];
    const bad = files.filter((f) => !isFontFile(f.name));
    if (bad.length) {
      setError(`${bad.map((f) => f.name).join(", ")} is not a .woff2, .woff, .ttf, or .otf file.`);
    } else {
      setError("");
    }
    const family = choice.family || guessFamily(files[0]?.name ?? "");
    if (!isFamilyName(family)) {
      setError("Type the family name first, then add the files.");
      return;
    }
    const added: UploadedFile[] = [];
    for (const file of files.filter((f) => isFontFile(f.name))) {
      const name = fontFileName(file.name);
      const weight = weightFromName(file.name);
      const bytes = await file.arrayBuffer();
      await saveFontBytes(name, bytes);
      try {
        await loadFontBytes(family, bytes, weight);
      } catch {
        setError(`${file.name} did not load as a font. Check that the file is not damaged.`);
        continue;
      }
      added.push({ name, original: file.name, weight });
    }
    const kept = choice.files.filter((f) => !added.some((a) => a.name === f.name));
    onChange({ ...choice, family, files: [...kept, ...added] });
  };

  const renamed = choice.files.filter((f) => f.name !== f.original);
  return (
    <>
      <TextField
        label="Family"
        value={choice.family}
        invalid={choice.family !== "" && !isFamilyName(choice.family)}
        hint={
          choice.family !== "" && !isFamilyName(choice.family)
            ? "A family name takes letters, digits, spaces, and dashes."
            : "The name the CSS asks for, such as Aeonik."
        }
        onChange={(family) => onChange({ ...choice, family })}
      />
      <div className="flex flex-col gap-1.5">
        <label htmlFor={inputId} className="text-sm text-foreground">
          Files
        </label>
        <input
          id={inputId}
          type="file"
          multiple
          accept=".woff2,.woff,.ttf,.otf"
          onChange={(e) => {
            void add(e.target.files);
            e.target.value = "";
          }}
          className={cn(inputBase, "min-h-8 cursor-pointer py-1 text-xs file:mr-2 file:border-0 file:bg-transparent file:text-xs file:font-medium file:text-foreground")}
        />
        {error ? <p className="text-xs text-error-ink">{error}</p> : null}
        {load === "failed" ? <p className="text-xs text-error-ink">One or more files did not load. Upload them again.</p> : null}
      </div>
      {choice.files.length ? (
        <ul className="flex flex-col gap-1.5">
          {choice.files.map((f) => (
            <li key={f.name} className="flex items-center gap-2">
              <span className="min-w-0 flex-1 truncate font-mono text-xs text-foreground" title={f.name}>
                {f.name}
              </span>
              <select
                aria-label={`Weight of ${f.name}`}
                value={f.weight}
                onChange={(e) =>
                  onChange({
                    ...choice,
                    files: choice.files.map((x) => (x.name === f.name ? { ...x, weight: e.target.value } : x)),
                  })
                }
                className={cn(inputBase, "min-h-7 w-auto py-0.5 pr-7 text-xs")}
              >
                {UPLOAD_WEIGHTS.map((w) => (
                  <option key={w.value} value={w.value}>
                    {w.label}
                  </option>
                ))}
              </select>
              <Button
                variant="ghost"
                size="xs"
                onClick={() => onChange({ ...choice, files: choice.files.filter((x) => x.name !== f.name) })}
              >
                Remove
              </Button>
            </li>
          ))}
        </ul>
      ) : null}
      {renamed.length ? (
        <p className="text-xs leading-normal text-muted-foreground">
          Rename {renamed.map((f) => `${f.original} to ${f.name}`).join(", ")} before you upload, because a file name
          in fonts/ takes letters, digits, dots, dashes, and underscores.
        </p>
      ) : null}
    </>
  );
}

/** A family name from a file name: `Aeonik-Bold.otf` gives Aeonik. */
function guessFamily(fileName: string): string {
  const stem = fileName.replace(/\.[^.]+$/, "").split(/[-_]/)[0] ?? "";
  const words = stem.replace(/([a-z])([A-Z])/g, "$1 $2").replace(/[^A-Za-z0-9 ]/g, "").trim();
  return isFamilyName(words) ? words : "";
}
