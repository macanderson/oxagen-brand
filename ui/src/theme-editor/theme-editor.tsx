"use client";
/**
 * The theme editor on the `Pages/` stories: a Theme button in the corner opens
 * a panel, laid out like shadcn's theme builder, that restyles the page behind
 * it as you change the theme.
 *
 * Every control writes `--ox-*` variables on `<html>`. The semantic roles in
 * `globals.css` read those tokens, so the page, the marks, and the panel
 * follow, in light and dark. The draft lives in localStorage. Update all sites
 * turns the draft into a theme request and opens GitHub with it filled in;
 * the apply-theme workflow does the rest (see CHANGING.md, "Theme editor").
 *
 * `.storybook/preview.tsx` mounts it on every story with `page: true`. It is
 * not part of the kit: `src/index.ts` does not export it, and the bundle's
 * types leave this folder out. Add `theme-editor=open` to the iframe's query
 * string to open the panel on load.
 */
import * as React from "react";
import { Dialog as DialogPrimitive } from "@base-ui/react/dialog";
import {
  ArrowCounterClockwiseIcon,
  ArrowLeftIcon,
  ArrowSquareOutIcon,
  CopyIcon,
  DownloadSimpleIcon,
  PaletteIcon,
  WarningIcon,
  XIcon,
} from "@phosphor-icons/react";
import { OxagenIcon, OxagenWordmark, StellaWordmark } from "../components/brand";
import { Button } from "../components/button";
import { popoverSurface } from "../components/control-styles";
import { cn } from "../lib/utils";
import type { Hex } from "./color";
import { ColorField, Ratio, RangeField, Section, SelectField, Swatch, TextField } from "./controls";
import { applyVars, clearVars, isShipped, loadDraft, previewVars, saveDraft, shippedDraft, type Draft } from "./draft";
import { FaceEditor, WordmarkFace, type LoadState } from "./faces-section";
import { isFamilyName, loadFontBytes, loadGoogleFont, readFontBytes } from "./fonts";
import { STATE_NAMES, derivePalette, verifyPalette, type InkGrounds, type PaperGrounds } from "./palette";
import {
  MAX_URL_LENGTH,
  autoSummary,
  branchName,
  buildRequest,
  draftChanges,
  fitsInUrl,
  newFileUrl,
  requestChanges,
  requestFileName,
  requestText,
  uploadUrl,
  uploadsNeeded,
} from "./request";
import {
  FACE_ROLES,
  RADIUS_STEPS,
  SHIPPED,
  STEPS,
  clone,
  pxRem,
  remPx,
  typeProblems,
  TYPE_FLOOR_PX,
  type FaceChoice,
  type FaceRole,
  type ScaleName,
  type Theme,
} from "./theme";

export type Mode = "light" | "dark";

export interface ThemeEditorProps {
  /** The theme the page shows. The colour sections edit this theme's values. */
  mode: Mode;
  /** Open the panel on mount. Defaults to the `theme-editor=open` query parameter. */
  defaultOpen?: boolean;
}

function openFromUrl(): boolean {
  try {
    return new URLSearchParams(window.location.search).get("theme-editor") === "open";
  } catch {
    return false;
  }
}

const idleLoads = (): Record<FaceRole, LoadState> => ({ display: "idle", sans: "idle", mono: "idle" });

export function ThemeEditor({ mode, defaultOpen }: ThemeEditorProps) {
  const [draft, setDraft] = React.useState<Draft>(() => loadDraft());
  const [open, setOpen] = React.useState(() => defaultOpen ?? openFromUrl());
  const [publishAt, setPublishAt] = React.useState<Date | null>(null);
  const [loads, setLoads] = React.useState<Record<FaceRole, LoadState>>(idleLoads);

  // The preview: write the draft to <html> on every change, and keep it.
  React.useEffect(() => {
    applyVars(document.documentElement, previewVars(draft));
    saveDraft(draft);
  }, [draft]);
  // Leave a story that has no editor as the kit ships it.
  React.useEffect(() => () => clearVars(document.documentElement), []);

  // Load each chosen face into the page. A Google name waits for typing to stop.
  const facesKey = JSON.stringify(draft.faces);
  React.useEffect(() => {
    let live = true;
    const faces = JSON.parse(facesKey) as Record<FaceRole, FaceChoice>;
    const set = (role: FaceRole, state: LoadState) => {
      if (live) setLoads((l) => (l[role] === state ? l : { ...l, [role]: state }));
    };
    const timer = window.setTimeout(() => {
      for (const role of FACE_ROLES) {
        const choice = faces[role];
        if (choice.kind === "google" && isFamilyName(choice.family)) {
          set(role, "loading");
          loadGoogleFont(choice.family, choice.weights).then(
            () => set(role, "ready"),
            () => set(role, "failed"),
          );
        } else if (choice.kind === "upload" && choice.files.length && isFamilyName(choice.family)) {
          set(role, "loading");
          Promise.all(
            choice.files.map(async (f) => {
              const bytes = await readFontBytes(f.name);
              if (!bytes) throw new Error(`${f.name} is not stored in this browser`);
              await loadFontBytes(choice.family, bytes, f.weight);
            }),
          ).then(
            () => set(role, "ready"),
            () => set(role, "failed"),
          );
        } else {
          set(role, "idle");
        }
      }
    }, 400);
    return () => {
      live = false;
      window.clearTimeout(timer);
    };
  }, [facesKey]);

  const update = React.useCallback((change: (theme: Theme) => void) => {
    setDraft((d) => {
      const theme = clone(d.theme);
      change(theme);
      return { ...d, theme };
    });
  }, []);
  const setFace = React.useCallback((role: FaceRole, choice: FaceChoice) => {
    setDraft((d) => ({ ...d, faces: { ...d.faces, [role]: choice } }));
  }, []);

  const changes = draftChanges(draft.theme, draft.faces);
  const problems = [
    ...verifyPalette(draft.theme.color),
    ...typeProblems(draft.theme),
    ...faceProblems(draft.faces, loads),
  ];

  return (
    <DialogPrimitive.Root
      open={open}
      onOpenChange={(next) => {
        setOpen(next);
        if (!next) setPublishAt(null);
      }}
      modal={false}
      disablePointerDismissal
    >
      <DialogPrimitive.Trigger
        className={cn(
          popoverSurface,
          "fixed right-4 bottom-4 z-40 inline-flex h-10 cursor-pointer items-center gap-2 rounded-full px-4 text-sm font-medium outline-none focus-visible:ring-2 focus-visible:ring-ring",
        )}
      >
        <PaletteIcon className="size-4" aria-hidden />
        Theme
        {changes.length ? (
          <span className="rounded-full bg-foreground/10 px-1.5 font-mono text-sm tabular-nums">
            {changes.length}
            <span className="sr-only"> changes</span>
          </span>
        ) : null}
      </DialogPrimitive.Trigger>
      <DialogPrimitive.Portal>
        <DialogPrimitive.Popup
          className={cn(
            popoverSurface,
            "fixed inset-y-3 right-3 z-50 flex w-[min(420px,calc(100vw-24px))] flex-col overflow-hidden outline-none transition duration-200 data-[ending-style]:translate-x-4 data-[ending-style]:opacity-0 data-[starting-style]:translate-x-4 data-[starting-style]:opacity-0",
          )}
        >
          <header className="flex shrink-0 flex-col gap-1 border-b border-border/70 px-5 pt-4 pb-3 pr-12">
            <DialogPrimitive.Title className="text-a-h4 text-foreground">Theme</DialogPrimitive.Title>
            <DialogPrimitive.Description className="text-xs leading-normal text-muted-foreground">
              Changes preview on this page. Nothing reaches a site until you update all sites.
            </DialogPrimitive.Description>
            <DialogPrimitive.Close
              aria-label="Close"
              className="absolute top-3 right-3 inline-flex size-8 cursor-pointer items-center justify-center rounded-lg text-muted-foreground outline-none hover:bg-foreground/10 hover:text-foreground focus-visible:ring-2 focus-visible:ring-ring"
            >
              <XIcon className="size-4" aria-hidden />
            </DialogPrimitive.Close>
          </header>

          {publishAt ? (
            <PublishView
              draft={draft}
              problems={problems}
              changes={changes.length}
              now={publishAt}
              onBack={() => setPublishAt(null)}
            />
          ) : (
            <>
              <div className="flex min-h-0 flex-1 flex-col gap-5 overflow-y-auto px-5 pt-4 pb-10">
                <PrimarySection theme={draft.theme} update={update} />
                <SurfaceSection mode={mode} theme={draft.theme} update={update} />
                <TextSection mode={mode} theme={draft.theme} update={update} />
                <StateSection mode={mode} theme={draft.theme} update={update} />
                <Section
                  title="Fonts"
                  note="A Google family loads from fonts.google.com, and uploaded files load from your disk and stay in this browser."
                >
                  <WordmarkFace />
                  {FACE_ROLES.map((role) => (
                    <FaceEditor
                      key={role}
                      role={role}
                      choice={draft.faces[role]}
                      load={loads[role]}
                      onChange={(choice) => setFace(role, choice)}
                    />
                  ))}
                </Section>
                <RadiusSection theme={draft.theme} update={update} />
                <ShadowSection mode={mode} theme={draft.theme} update={update} />
                <SpacingSection theme={draft.theme} update={update} />
                <TypeSection theme={draft.theme} update={update} />
                <ChecksSection problems={problems} />
                <ChangesSection draft={draft} />
              </div>
              <footer className="flex shrink-0 flex-col gap-2 border-t border-border/70 px-5 py-3">
                <div className="flex flex-wrap items-center gap-1">
                  <Button
                    variant="ghost"
                    size="sm"
                    startIcon={<ArrowCounterClockwiseIcon aria-hidden />}
                    disabled={isShipped(draft)}
                    onClick={() => setDraft(shippedDraft())}
                  >
                    Reset
                  </Button>
                  <ExportButtons draft={draft} />
                </div>
                <Button
                  variant="primary"
                  className="w-full"
                  disabled={!changes.length}
                  onClick={() => setPublishAt(new Date())}
                >
                  Update all sites
                </Button>
              </footer>
            </>
          )}
        </DialogPrimitive.Popup>
      </DialogPrimitive.Portal>
    </DialogPrimitive.Root>
  );
}

type Update = (change: (theme: Theme) => void) => void;

// --------------------------------------------------------------------------
// colour
// --------------------------------------------------------------------------

function PrimarySection({ theme, update }: { theme: Theme; update: Update }) {
  const p = derivePalette(theme.color);
  const ink = theme.color.ink.ink;
  const paper = theme.color.paper.paper;
  return (
    <Section
      title="Primary colour"
      note="The gold fills the marks' accent, the primary button, the focus ring, and the gold tints. Its bright and deep neighbours are derived from it."
    >
      <ColorField label="Gold" value={theme.color.gold} onChange={(hex) => update((t) => void (t.color.gold = hex))}>
        <Ratio fg={theme.color.gold} bg={ink} min={4.5} label="on ink" />
        <Ratio fg={ink} bg={theme.color.gold} min={4.5} label="ink on gold" />
      </ColorField>
      <div className="flex flex-col gap-1.5 pl-10 text-xs text-muted-foreground">
        <span className="flex items-center gap-2">
          <Swatch color={p.goldBright} />
          Bright <span className="font-mono">{p.goldBright}</span>
        </span>
        <span className="flex flex-wrap items-center gap-2">
          <Swatch color={p.goldDeep} />
          Deep <span className="font-mono">{p.goldDeep}</span>
          <Ratio fg={p.goldDeep} bg={paper} min={4.5} label="on paper" />
        </span>
      </div>
      <div className="flex flex-wrap items-center gap-4 rounded-2xl border border-border/70 bg-background/40 px-3 py-3 text-foreground">
        <OxagenWordmark className="h-6" />
        <StellaWordmark className="h-6" />
        <OxagenIcon className="size-7" />
        <Button variant="primary" size="sm" tabIndex={-1}>
          Primary
        </Button>
      </div>
      <details className="group flex flex-col gap-2">
        <summary className="cursor-pointer text-xs text-muted-foreground hover:text-foreground">Neighbours</summary>
        <div className="mt-2 flex flex-col gap-3">
          <RangeField
            label="Bright lightness"
            value={theme.color.gold_bright.lightness}
            min={0.6}
            max={0.98}
            step={0.01}
            shown={theme.color.gold_bright.lightness.toFixed(2)}
            onChange={(v) => update((t) => void (t.color.gold_bright.lightness = round(v, 2)))}
          />
          <RangeField
            label="Bright chroma"
            value={theme.color.gold_bright.chroma}
            min={0}
            max={0.3}
            step={0.005}
            shown={theme.color.gold_bright.chroma.toFixed(3)}
            onChange={(v) => update((t) => void (t.color.gold_bright.chroma = round(v, 3)))}
          />
          <RangeField
            label="Deep lightness"
            value={theme.color.gold_deep.lightness}
            min={0.2}
            max={0.75}
            step={0.01}
            shown={theme.color.gold_deep.lightness.toFixed(2)}
            onChange={(v) => update((t) => void (t.color.gold_deep.lightness = round(v, 2)))}
          />
          <RangeField
            label="Deep chroma"
            value={theme.color.gold_deep.chroma}
            min={0}
            max={0.3}
            step={0.005}
            shown={theme.color.gold_deep.chroma.toFixed(3)}
            onChange={(v) => update((t) => void (t.color.gold_deep.chroma = round(v, 3)))}
          />
        </div>
      </details>
    </Section>
  );
}

const GROUND_LABELS: [keyof InkGrounds & keyof PaperGrounds | "ink" | "paper", string][] = [
  ["ink", "Canvas"],
  ["void", "Below the canvas"],
  ["panel", "Panel"],
  ["hl", "Lifted row"],
  ["border", "Border"],
  ["rule", "Rule"],
];

function modeNote(mode: Mode, what: string): string {
  return `The ${mode} theme's ${what}. Switch the theme in the toolbar to edit the ${mode === "dark" ? "light" : "dark"} one.`;
}

function SurfaceSection({ mode, theme, update }: { mode: Mode; theme: Theme; update: Update }) {
  return (
    <Section title="Surfaces" note={modeNote(mode, "surfaces")}>
      {GROUND_LABELS.map(([key, label]) => {
        if (mode === "dark") {
          const k = key as keyof InkGrounds;
          return (
            <ColorField
              key={k}
              label={label}
              value={theme.color.ink[k]}
              onChange={(hex) => update((t) => void (t.color.ink[k] = hex))}
            />
          );
        }
        const k = (key === "ink" ? "paper" : key) as keyof PaperGrounds;
        return (
          <ColorField
            key={k}
            label={label}
            value={theme.color.paper[k]}
            onChange={(hex) => update((t) => void (t.color.paper[k] = hex))}
          />
        );
      })}
    </Section>
  );
}

function TextSection({ mode, theme, update }: { mode: Mode; theme: Theme; update: Update }) {
  const c = theme.color;
  if (mode === "dark") {
    const ground = c.ink.ink;
    return (
      <Section title="Text" note={`${modeNote(mode, "text")} Primary text is the paper colour.`}>
        <ColorField label="Body" value={c.text_on_ink.body} onChange={(h) => update((t) => void (t.color.text_on_ink.body = h))}>
          <Ratio fg={c.text_on_ink.body} bg={ground} min={4.5} label="on canvas" />
        </ColorField>
        <ColorField label="Secondary" value={c.text_on_ink.muted} onChange={(h) => update((t) => void (t.color.text_on_ink.muted = h))}>
          <Ratio fg={c.text_on_ink.muted} bg={ground} min={4.5} label="on canvas" />
          <Ratio fg={c.text_on_ink.muted} bg={c.ink.hl} min={4.5} label="on lifted row" />
        </ColorField>
        <ColorField label="Quietest" value={c.text_on_ink.dim} onChange={(h) => update((t) => void (t.color.text_on_ink.dim = h))}>
          <Ratio fg={c.text_on_ink.dim} bg={ground} label="on canvas" />
        </ColorField>
        <DimNote />
      </Section>
    );
  }
  const ground = c.paper.paper;
  const p = derivePalette(c);
  return (
    <Section title="Text" note={`${modeNote(mode, "text")} Primary text is the ink colour.`}>
      <ColorField label="Body" value={c.text_on_paper.body} onChange={(h) => update((t) => void (t.color.text_on_paper.body = h))}>
        <Ratio fg={c.text_on_paper.body} bg={ground} min={4.5} label="on canvas" />
      </ColorField>
      <ColorField label="Secondary" value={c.text_on_paper.muted} onChange={(h) => update((t) => void (t.color.text_on_paper.muted = h))}>
        <Ratio fg={c.text_on_paper.muted} bg={ground} min={4.5} label="on canvas" />
      </ColorField>
      <ColorField label="Quietest" value={c.text_on_paper.dim} onChange={(h) => update((t) => void (t.color.text_on_paper.dim = h))}>
        <Ratio fg={c.text_on_paper.dim} bg={ground} label="on canvas" />
      </ColorField>
      <DimNote />
      <RangeField
        label="Secondary text on a lifted row"
        value={c.text_on_paper.muted_text_lightness}
        min={0.3}
        max={0.7}
        step={0.005}
        shown={`lightness ${c.text_on_paper.muted_text_lightness.toFixed(3)}`}
        onChange={(v) => update((t) => void (t.color.text_on_paper.muted_text_lightness = round(v, 3)))}
      />
      <div className="flex flex-wrap items-center gap-2 text-xs text-muted-foreground">
        <Swatch color={p.mutedTextInk} />
        <span className="font-mono">{p.mutedTextInk}</span>
        <Ratio fg={p.mutedTextInk} bg={c.paper.hl} min={4.5} label="on lifted row" />
      </div>
    </Section>
  );
}

function DimNote() {
  return (
    <p className="text-xs leading-normal text-muted-foreground">
      The quietest text never carries meaning, so the build does not hold it to 4.5:1.
    </p>
  );
}

const STATE_LABELS: Record<(typeof STATE_NAMES)[number], string> = {
  allowed: "Allowed",
  approval: "Approval",
  denied: "Denied",
  proven: "Proven",
  failed: "Failed",
  critical: "Critical",
};

function StateSection({ mode, theme, update }: { mode: Mode; theme: Theme; update: Update }) {
  const p = derivePalette(theme.color);
  const side = mode === "dark" ? "ink" : "paper";
  const ground = mode === "dark" ? theme.color.ink.ink : theme.color.paper.paper;
  // The surface a status word has the least contrast on: the lifted row.
  const worst: Hex = mode === "dark" ? theme.color.ink.hl : theme.color.paper.hl;
  return (
    <Section
      title="States"
      note={`${modeNote(mode, "state marks")} A mark needs 3:1. Its text stop, the colour for words, is derived from it and needs 4.5:1.`}
    >
      {STATE_NAMES.map((name) => {
        const stop = p.stateText[name][mode];
        return (
          <ColorField
            key={name}
            label={STATE_LABELS[name]}
            value={theme.color.states[name][side]}
            onChange={(hex) => update((t) => void (t.color.states[name][side] = hex))}
          >
            <Ratio fg={theme.color.states[name][side]} bg={ground} min={3} label="mark" />
            <span className="inline-flex items-center gap-1">
              <Swatch color={stop} className="size-3.5" />
              <Ratio fg={stop} bg={worst} min={4.5} label="words" />
            </span>
          </ColorField>
        );
      })}
      {mode === "dark" ? (
        <>
          <RangeField
            label="Text stop lightness"
            value={theme.color.state_text_lightness_on_ink}
            min={0.5}
            max={0.9}
            step={0.005}
            shown={theme.color.state_text_lightness_on_ink.toFixed(3)}
            onChange={(v) => update((t) => void (t.color.state_text_lightness_on_ink = round(v, 3)))}
          />
          <RangeField
            label="Destructive lift"
            value={theme.color.destructive_lift_on_ink}
            min={0}
            max={0.2}
            step={0.005}
            shown={theme.color.destructive_lift_on_ink.toFixed(3)}
            onChange={(v) => update((t) => void (t.color.destructive_lift_on_ink = round(v, 3)))}
          />
          <div className="flex flex-wrap items-center gap-2 text-xs text-muted-foreground">
            <Swatch color={p.destructive.dark} />
            Destructive <span className="font-mono">{p.destructive.dark}</span>
            <Ratio fg={p.destructive.dark} bg={ground} min={4.5} label="on canvas" />
          </div>
        </>
      ) : null}
    </Section>
  );
}

// --------------------------------------------------------------------------
// shape
// --------------------------------------------------------------------------

function RadiusSection({ theme, update }: { theme: Theme; update: Update }) {
  const base = remPx(theme.radius.base);
  return (
    <Section title="Corners" note="Every corner multiplies the base. A card and a panel take the card step.">
      <RangeField
        label="Base"
        value={base / 16}
        min={0}
        max={1.2}
        step={0.025}
        shown={`${base.toFixed(1)}px`}
        onChange={(v) => update((t) => void (t.radius.base = `${round(v, 3)}rem`))}
      />
      <SelectField
        label="Card"
        value={theme.radius.card}
        options={RADIUS_STEPS.map((s) => ({
          value: s,
          label: `${s}, ${(base * (theme.radius.steps[s] ?? 1)).toFixed(1)}px`,
        }))}
        onChange={(v) => update((t) => void (t.radius.card = v))}
      />
      <RangeField
        label="Website corner"
        value={remPx(theme.radius.site) / 16}
        min={0}
        max={1.5}
        step={0.0625}
        shown={`${remPx(theme.radius.site).toFixed(0)}px`}
        onChange={(v) => update((t) => void (t.radius.site = pxRem(Math.round(v * 16))))}
      />
      <div className="flex gap-2" aria-hidden>
        {(["sm", "lg", "2xl"] as const).map((s) => (
          <div
            key={s}
            className="h-10 flex-1 border border-border bg-card"
            style={{ borderRadius: `var(--ox-radius-${s})` }}
          />
        ))}
      </div>
    </Section>
  );
}

const SHADOW_PRESETS: { label: string; value: string }[] = [
  { label: "None", value: "none" },
  { label: "Hairline", value: "0 1px 2px oklch(0.15 0 0 / 0.07)" },
  { label: "Soft", value: "0 2px 8px -2px oklch(0.15 0 0 / 0.12)" },
  { label: "Medium", value: "0 8px 24px -8px oklch(0.15 0 0 / 0.25)" },
  { label: "Deep", value: "0 25px 50px -12px rgb(0 0 0 / 0.6)" },
];

/** A shadow the theme accepts: the characters `theme.schema.json` allows. */
const SHADOW_PATTERN = /^[A-Za-z0-9 .,%()/#+-]{1,200}$/;

function ShadowSection({ mode, theme, update }: { mode: Mode; theme: Theme; update: Update }) {
  const side = mode === "dark" ? "ink" : "paper";
  return (
    <Section title="Shadows" note={modeNote(mode, "shadows")}>
      {(
        [
          ["ui", "Under a control"],
          ["pop", "Under a menu or dialog"],
        ] as const
      ).map(([key, label]) => (
        <ShadowField
          key={`${key}-${side}`}
          label={label}
          value={theme.shadow[key][side]}
          shipped={SHIPPED.shadow[key][side]}
          onChange={(v) => update((t) => void (t.shadow[key][side] = v))}
        />
      ))}
    </Section>
  );
}

function ShadowField({
  label,
  value,
  shipped,
  onChange,
}: {
  label: string;
  value: string;
  shipped: string;
  onChange: (value: string) => void;
}) {
  const [text, setText] = React.useState(value);
  React.useEffect(() => setText(value), [value]);
  const presets = [{ label: "Shipped", value: shipped }, ...SHADOW_PRESETS.filter((p) => p.value !== shipped)];
  const preset = presets.find((p) => p.value === value)?.label ?? "Custom";
  const valid = SHADOW_PATTERN.test(text);
  return (
    <div className="flex flex-col gap-2">
      <SelectField
        label={label}
        value={preset}
        options={[...presets.map((p) => ({ value: p.label, label: p.label })), { value: "Custom", label: "Custom" }]}
        onChange={(name) => {
          const p = presets.find((x) => x.label === name);
          if (p) onChange(p.value);
        }}
      />
      <TextField
        label={`${label}, as CSS`}
        value={text}
        invalid={!valid}
        hint={valid ? undefined : "A box-shadow takes letters, digits, spaces, and . , % ( ) / # + -"}
        onChange={(v) => {
          setText(v);
          if (SHADOW_PATTERN.test(v)) onChange(v);
        }}
      />
      <div className="h-8 rounded-xl border border-border bg-card" style={{ boxShadow: valid ? text : value }} aria-hidden />
    </div>
  );
}

function SpacingSection({ theme, update }: { theme: Theme; update: Update }) {
  const px = remPx(theme.spacing.unit);
  return (
    <Section title="Spacing" note="Every padding, gap, and margin is a whole number of units.">
      <RangeField
        label="Unit"
        value={px}
        min={2}
        max={8}
        step={1}
        shown={`${px}px, so p-4 is ${px * 4}px`}
        onChange={(v) => update((t) => void (t.spacing.unit = pxRem(v)))}
      />
    </Section>
  );
}

const SCALE_LABELS: Record<ScaleName, string> = { marketing: "Marketing", app: "App" };

function TypeSection({ theme, update }: { theme: Theme; update: Update }) {
  return (
    <Section
      title="Type sizes"
      note={`Marketing sets landing pages, posts, and docs. App sets the web app and the internal tools. Each size is a whole number of pixels, ${TYPE_FLOOR_PX} or more.`}
    >
      {(["marketing", "app"] as const).map((scale) => {
        const h1 = remPx(theme.type.scales[scale].h1.size);
        const shippedH1 = remPx(SHIPPED.type.scales[scale].h1.size);
        const factor = h1 / shippedH1;
        return (
          <div key={scale} className="flex flex-col gap-2">
            <RangeField
              label={`${SCALE_LABELS[scale]} scale`}
              value={round(factor, 2)}
              min={0.7}
              max={1.5}
              step={0.05}
              shown={`${Math.round(factor * 100)}%`}
              onChange={(f) =>
                update((t) => {
                  for (const step of STEPS) {
                    const px = Math.max(TYPE_FLOOR_PX, Math.round(remPx(SHIPPED.type.scales[scale][step].size) * f));
                    t.type.scales[scale][step].size = pxRem(px);
                  }
                })
              }
            />
            <details>
              <summary className="cursor-pointer text-xs text-muted-foreground hover:text-foreground">
                {SCALE_LABELS[scale]} steps
              </summary>
              <div className="mt-2 grid grid-cols-3 gap-2">
                {STEPS.map((step) => {
                  const px = Math.round(remPx(theme.type.scales[scale][step].size));
                  const low = px < TYPE_FLOOR_PX;
                  return (
                    <label key={step} className="flex flex-col gap-1 text-xs text-muted-foreground">
                      {step}
                      <input
                        type="number"
                        min={TYPE_FLOOR_PX}
                        max={160}
                        step={1}
                        value={px}
                        aria-invalid={low || undefined}
                        aria-describedby={`theme-editor-floor-${scale}`}
                        onChange={(e) => {
                          const next = Math.round(Number(e.target.value));
                          if (next >= 1 && next <= 160) update((t) => void (t.type.scales[scale][step].size = pxRem(next)));
                        }}
                        className="h-8 rounded-lg border border-input-border bg-input-bg px-2 font-mono text-xs text-input-fg aria-invalid:border-input-invalid-border"
                      />
                    </label>
                  );
                })}
              </div>
              <p
                id={`theme-editor-floor-${scale}`}
                className={cn(
                  "mt-2 text-xs leading-normal",
                  STEPS.some((step) => remPx(theme.type.scales[scale][step].size) < TYPE_FLOOR_PX)
                    ? "text-error-ink"
                    : "text-muted-foreground",
                )}
              >
                Every step is {TYPE_FLOOR_PX}px or more, the micro step too. The build refuses a smaller size.
              </p>
            </details>
          </div>
        );
      })}
    </Section>
  );
}

// --------------------------------------------------------------------------
// checks, changes, export
// --------------------------------------------------------------------------

function faceProblems(faces: Record<FaceRole, FaceChoice>, loads: Record<FaceRole, LoadState>): string[] {
  const out: string[] = [];
  for (const role of FACE_ROLES) {
    const choice = faces[role];
    if (choice.kind === "google" && !isFamilyName(choice.family)) out.push(`The ${role} face needs a Google family name.`);
    if (choice.kind === "google" && loads[role] === "failed") {
      out.push(`Google Fonts has no family named ${choice.family} at the weights chosen for the ${role} face.`);
    }
    if (choice.kind === "upload" && !isFamilyName(choice.family)) out.push(`The ${role} face needs a family name.`);
    if (choice.kind === "upload" && !choice.files.length) out.push(`The ${role} face needs at least one uploaded file.`);
  }
  return out;
}

function ChecksSection({ problems }: { problems: string[] }) {
  return (
    <Section title="Checks" note="The build runs the same checks, and it refuses a theme that fails one.">
      {problems.length ? (
        <ul className="flex flex-col gap-1.5">
          {problems.map((p) => (
            <li key={p} className="flex gap-2 text-xs leading-normal text-error-ink">
              <WarningIcon className="mt-0.5 size-3.5 shrink-0" aria-hidden />
              {p}
            </li>
          ))}
        </ul>
      ) : (
        <p className="text-xs text-muted-foreground">The build accepts these colours, faces, and sizes.</p>
      )}
    </Section>
  );
}

function short(value: unknown): string {
  if (typeof value === "string") return value;
  const text = JSON.stringify(value);
  return text.length > 60 ? `${text.slice(0, 57)}...` : text;
}

function ChangesSection({ draft }: { draft: Draft }) {
  const changes = draftChanges(draft.theme, draft.faces);
  return (
    <Section title="Changes">
      {changes.length ? (
        <ul className="flex flex-col gap-1 font-mono text-sm leading-relaxed">
          {changes.map((c) => (
            <li key={c.path} className="flex flex-col rounded-lg bg-muted/60 px-2 py-1">
              <span className="text-foreground">{c.path}</span>
              <span className="text-muted-foreground">
                <span className="line-through">{short(c.before)}</span> to {short(c.after)}
              </span>
            </li>
          ))}
        </ul>
      ) : (
        <p className="text-xs text-muted-foreground">No changes yet. The page shows the shipped theme.</p>
      )}
    </Section>
  );
}

function download(name: string, text: string) {
  const url = URL.createObjectURL(new Blob([text], { type: "application/json" }));
  const a = document.createElement("a");
  a.href = url;
  a.download = name;
  a.click();
  window.setTimeout(() => URL.revokeObjectURL(url), 1000);
}

function ExportButtons({ draft }: { draft: Draft }) {
  const [copied, setCopied] = React.useState(false);
  const make = () => {
    const now = new Date();
    const request = buildRequest(draft.theme, draft.faces, "", now);
    return { name: requestFileName(String(request.summary), now), text: requestText(request) };
  };
  return (
    <>
      <Button
        variant="ghost"
        size="sm"
        startIcon={<CopyIcon aria-hidden />}
        onClick={() => {
          void navigator.clipboard?.writeText(make().text).then(() => {
            setCopied(true);
            window.setTimeout(() => setCopied(false), 1500);
          });
        }}
      >
        {copied ? "Copied" : "Copy JSON"}
      </Button>
      <Button
        variant="ghost"
        size="sm"
        startIcon={<DownloadSimpleIcon aria-hidden />}
        onClick={() => {
          const { name, text } = make();
          download(name, text);
        }}
      >
        Download JSON
      </Button>
    </>
  );
}

// --------------------------------------------------------------------------
// update all sites
// --------------------------------------------------------------------------

function PublishView({
  draft,
  problems,
  changes,
  now,
  onBack,
}: {
  draft: Draft;
  problems: string[];
  changes: number;
  now: Date;
  onBack: () => void;
}) {
  const [summary, setSummary] = React.useState(() => autoSummary(draft.theme, draft.faces));
  const request = buildRequest(draft.theme, draft.faces, summary, now);
  const fileName = requestFileName(String(request.summary), now);
  const uploads = uploadsNeeded(draft.faces);
  const branch = uploads.length ? branchName(String(request.summary), now) : "main";
  const url = newFileUrl(request, fileName, branch);
  const fits = fitsInUrl(url);
  const empty = !requestChanges(request);

  return (
    <>
      <div className="flex min-h-0 flex-1 flex-col gap-5 overflow-y-auto px-5 pt-4 pb-10">
        <Section
          title="Update all sites"
          note={`This sends a theme request that holds your ${changes} change${changes === 1 ? "" : "s"}. You commit it on GitHub with your own login.`}
        >
          <TextField
            label="Summary"
            value={summary}
            onChange={setSummary}
            hint={`It becomes the commit message. The file is theme/requests/${fileName}.`}
          />
          {problems.length ? (
            <div className="flex flex-col gap-1.5 rounded-xl border border-error/40 bg-error/5 p-3 text-xs text-error-ink">
              <p className="font-medium">The build will refuse this theme until these clear:</p>
              <ul className="list-disc pl-4">
                {problems.map((p) => (
                  <li key={p}>{p}</li>
                ))}
              </ul>
            </div>
          ) : null}
        </Section>

        <Section title="Steps">
          <ol className="flex list-decimal flex-col gap-2.5 pl-4 text-sm leading-normal text-foreground">
            {uploads.length ? (
              <>
                <li>
                  Upload {uploads.length === 1 ? "this file" : "these files"} to <span className="font-mono">fonts/</span>:{" "}
                  <span className="font-mono text-xs">{uploads.join(", ")}</span>. On GitHub, choose Create a new branch, name it{" "}
                  <span className="font-mono text-xs">{branch}</span>, and select Propose changes, then Create pull request.{" "}
                  <a className="underline underline-offset-2" href={uploadUrl("fonts")} target="_blank" rel="noreferrer">
                    Open the upload page
                  </a>
                </li>
                <li>
                  Open the request on GitHub below, and choose Commit directly to the{" "}
                  <span className="font-mono text-xs">{branch}</span> branch.
                </li>
              </>
            ) : (
              <>
                <li>Open GitHub. The new-file page shows the request, filled in.</li>
                <li>
                  Choose Create a new branch for this commit and start a pull request, then select Propose changes. Main
                  requires checks to pass, so a change goes in through a branch and a pull request.
                </li>
                <li>Select Create pull request.</li>
              </>
            )}
            <li>
              The apply-theme workflow runs on the pull request. It fetches any Google face, runs every generator, commits
              the result to the branch, and comments with what changed.
            </li>
            <li>Review the pull request and its checks, then merge it. The fan-out workflow then opens a sync pull request in every site.</li>
          </ol>
        </Section>

        {!fits ? (
          <p className="rounded-xl border border-border bg-muted/60 p-3 text-xs leading-normal text-foreground">
            This request is too long for a GitHub link: {url.length.toLocaleString("en-US")} characters, and the limit is{" "}
            {MAX_URL_LENGTH.toLocaleString("en-US")}. Download it, then upload it to{" "}
            <span className="font-mono">theme/requests/</span> on the{" "}
            <a className="underline underline-offset-2" href={uploadUrl("theme/requests", branch)} target="_blank" rel="noreferrer">
              upload page
            </a>
            .
          </p>
        ) : null}

        <details>
          <summary className="cursor-pointer text-xs text-muted-foreground hover:text-foreground">Request</summary>
          <pre className="mt-2 max-h-64 overflow-auto rounded-xl bg-muted/60 p-3 font-mono text-sm leading-relaxed text-foreground">
            {requestText(request)}
          </pre>
        </details>
      </div>
      <footer className="flex shrink-0 flex-wrap items-center gap-2 border-t border-border/70 px-5 py-3">
        <Button variant="ghost" size="sm" startIcon={<ArrowLeftIcon aria-hidden />} onClick={onBack}>
          Back to editing
        </Button>
        {fits ? (
          <Button
            variant="primary"
            size="sm"
            className="ml-auto"
            disabled={empty}
            endIcon={<ArrowSquareOutIcon aria-hidden />}
            onClick={() => window.open(url, "_blank", "noopener")}
          >
            Open GitHub
          </Button>
        ) : (
          <Button
            variant="primary"
            size="sm"
            className="ml-auto"
            disabled={empty}
            startIcon={<DownloadSimpleIcon aria-hidden />}
            onClick={() => download(fileName, requestText(request))}
          >
            Download request
          </Button>
        )}
      </footer>
    </>
  );
}

function round(value: number, digits: number): number {
  return Number(value.toFixed(digits));
}
