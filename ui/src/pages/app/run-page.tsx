"use client";
// The product app's Run page, copied from oxageninc/product
// apps/app/src/features/run/ (run.tsx, header.tsx, stats.tsx, tabs.tsx,
// transcript-view.tsx, transcript-skin.tsx, work.tsx, outputs.tsx, parts.tsx)
// at fad620bcef (2026-10-02). It keeps the app's markup and classes, so the
// theme editor shows the page as the app draws it.
//
// It draws one live run, with the Transcript tab open, from the sample record
// in run-record.ts. What it leaves out: the other six tabs (their names and
// counts show, and they open nothing), the replay transport's playback and
// the transcript's search (the controls draw and do nothing), the chips'
// filtering, every dialog the header's buttons open, and the harness logo in
// the agent's avatar, which is a robot glyph here. A transcript row still
// opens and closes.
//
// The page will drift from the app. To refresh it, copy the same files from
// the app again and keep the data as props.
import * as React from "react";
import {
  CopyIcon,
  GitBranchIcon,
  RobotIcon,
  TreeStructureIcon,
} from "@phosphor-icons/react";
import { WORKSPACE } from "./fixtures";
import { Avatar, Badge, Money, RouteTabPanel, RouteTabs } from "./parts";
import { FEED, KINDS, RUN, type FeedRow, type Frame } from "./run-record";
import { AppFrame } from "./shell";
import {
  buttonDanger,
  buttonSecondary,
  eyebrow,
  eyebrowQuiet,
  kvTerm,
  kvValue,
  linkChip,
  mono,
  note,
  panel,
  panelBody,
  panelHeader,
  panelTitle,
  runStatNote,
  runStatStrip,
  runStatTerm,
  runStatTile,
  runStatValue,
} from "./styles";

/* ── Header ─────────────────────────────────────────────────────────────── */

/** The quiet pill every strip chip is. */
function Chip({ children, code = false, title }: { children: React.ReactNode; code?: boolean; title?: string }) {
  return (
    <span
      title={title}
      className={`inline-flex min-w-0 max-w-full items-center gap-[5px] whitespace-nowrap rounded-md border border-border bg-hl px-[7px] py-0.5 leading-normal tracking-[0.02em] text-muted-foreground ${code ? "font-mono text-[10.5px] font-medium" : "text-[11px] font-semibold"}`}
    >
      {children}
    </span>
  );
}

/** The agent's initials tile, with its harness in the corner. */
function AgentAvatar({ initials, size }: { initials: string; size: number }) {
  const badge = Math.max(10, Math.round(size * 0.46));
  return (
    <span
      aria-hidden="true"
      className="relative inline-block shrink-0 align-middle leading-none"
      style={{ width: size, height: size }}
    >
      <Avatar initials={initials} shape="agent" size={size} />
      <span
        className="absolute -bottom-[3px] -left-[3px] grid place-items-center rounded-full bg-background text-foreground ring-[1.5px] ring-background [&_svg]:size-full"
        style={{ width: badge, height: badge, padding: 1.5 }}
      >
        <RobotIcon weight="fill" />
      </span>
    </span>
  );
}

/** The agent's key and a line under it, in the compact card the header and the summary use. */
function AgentCard({ sub }: { sub: React.ReactNode }) {
  return (
    <span className="flex min-w-0 items-center gap-2.5 text-left inline-flex max-w-full rounded-[10px] border border-border bg-background py-[5px] pl-1.5 pr-[11px]">
      <AgentAvatar initials="SC" size={30} />
      <span className="flex min-w-0 flex-col max-w-[280px] leading-[1.3]">
        <span title={RUN.agentKey} className={`${mono} truncate text-[12px] text-foreground`}>
          {RUN.agentKey}
        </span>
        <span className="truncate text-[11.5px] text-muted-foreground">{sub}</span>
      </span>
    </span>
  );
}

function RunHeader() {
  return (
    <header className="mb-[18px] flex flex-wrap items-start gap-[18px]">
      <div className="min-w-0">
        <p className={`${eyebrow} mb-2.5`}>Run</p>
        <h1 className="mb-1 break-words text-[19px] font-bold leading-tight text-foreground">{RUN.name}</h1>
        <span className="inline-flex min-w-0 max-w-full items-center gap-1.5">
          <button
            type="button"
            aria-label={`Copy run id ${RUN.id}`}
            className="inline-flex min-w-0 items-center gap-1 rounded-sm font-mono text-[11.5px] text-muted-foreground hover:text-foreground max-md:min-h-11"
          >
            <span className="min-w-0 break-all">{RUN.id}</span>
            <CopyIcon aria-hidden="true" className="size-3 flex-none opacity-70" />
          </button>
        </span>
        <div aria-label="Run identity" className="mt-2 flex flex-wrap items-center gap-[9px]">
          <AgentCard
            sub={
              <>
                {RUN.harness} · 41 runs 30d · <Money>$38.12</Money>
              </>
            }
          />
          <span role="status" className="inline-flex">
            <Badge tone="approval">parked</Badge>
          </span>
          <Badge tone="allowed" dot={false} mono title="The gateway answers every request before the call runs.">
            gateway
          </Badge>
          <Chip>task {RUN.task}</Chip>
        </div>
        <div className="mt-2 flex flex-wrap items-center gap-[9px]">
          <Chip>
            {RUN.harness}
            <span className="font-mono font-normal text-muted-foreground">{RUN.harnessVersion}</span>
          </Chip>
          <Chip code title="anthropic opus">
            {RUN.model}
          </Chip>
          <Chip title="Read from the harness settings the session recorded.">effort high</Chip>
          <Chip>thinking on</Chip>
          <Chip code>mode acceptEdits</Chip>
        </div>
        <div className="mt-1.5 flex min-w-0 flex-wrap items-center gap-1.5">
          <a href="#repository" className={linkChip}>
            {RUN.repository}
          </a>
          <a href="#branch" className={`${linkChip} font-mono text-[10.5px] font-medium`}>
            <GitBranchIcon aria-hidden="true" className="size-3 flex-none" />
            {RUN.branch}
          </a>
          <Chip>
            <span className="text-muted-foreground">no pull request</span>
          </Chip>
          <span className="inline-flex min-w-0 max-w-full items-center gap-1.5">
            <button type="button" className={`${linkChip} font-mono text-[10.5px] font-medium`}>
              <TreeStructureIcon aria-hidden="true" className="size-3 flex-none opacity-80" />
              <span className="min-w-0 truncate [direction:rtl] [text-align:left]">
                <bdi>{RUN.path}</bdi>
              </span>
            </button>
          </span>
        </div>
        <p className="mt-2 max-w-[70ch] text-[13px] text-muted-foreground">
          started <time>{RUN.started}</time>
        </p>
      </div>
      <div className="ml-auto flex flex-wrap items-start gap-2">
        <div className="flex flex-wrap gap-2">
          <button type="button" className={buttonSecondary}>
            ❙❙ Pause run
          </button>
          <button type="button" className={buttonSecondary}>
            Steer
          </button>
          <button type="button" className={buttonDanger}>
            Cancel
          </button>
        </div>
        <button type="button" className={buttonDanger}>
          Seal run
        </button>
        <button type="button" className={buttonSecondary}>
          Delivery report
        </button>
        <button type="button" disabled title="Export needs a sealed run." className={buttonSecondary}>
          Export
        </button>
      </div>
    </header>
  );
}

/* ── Summary and figures ────────────────────────────────────────────────── */

function SummaryPanel() {
  return (
    <section
      aria-labelledby="run-summary-title"
      className="rounded-xl border border-border bg-card px-[18px] py-4 text-card-foreground"
    >
      <div className="flex flex-wrap items-center justify-between gap-3">
        <h2 id="run-summary-title" className={`${eyebrowQuiet} m-0`}>
          Summary
        </h2>
        <Badge tone="quiet" dot={false}>
          <span className="text-[10.5px]">generated from the record</span>
        </Badge>
      </div>
      <div className="mt-2.5 flex flex-wrap items-center gap-2.5">
        <AgentCard sub={`${RUN.agentName} · ${RUN.harness}`} />
        <span className="font-mono text-[11.5px] text-muted-foreground">on behalf of →</span>
        <span className="inline-flex min-w-0 max-w-full items-center gap-[9px] rounded-full border border-border bg-background py-[5px] pl-1.5 pr-3 text-[12.5px] text-foreground">
          <Avatar initials={RUN.operatorInitials} size={30} />
          <span className="flex min-w-0 flex-col leading-tight">
            <b className="truncate font-semibold">{RUN.operator}</b>
            <span className="truncate font-mono text-[10.5px] text-muted-foreground">
              <span>operator</span>
              {" · "}
              <span>workspace.member</span>
              {" · "}
              <span>{WORKSPACE.slug}</span>
            </span>
          </span>
        </span>
      </div>
      <p className="mb-2.5 mt-3 max-w-[78ch] text-[15px] leading-[1.55] text-foreground">{RUN.summary}</p>
      <div className="mt-[13px] flex flex-wrap items-center gap-2.5 border-t border-border pt-[11px] font-mono text-[11px] text-muted-foreground">
        <span className="min-w-0 flex-1">
          generated by <b className="font-semibold text-muted-foreground">{RUN.summaryModel}</b> ·{" "}
          <time>{RUN.summaryAt}</time>
        </span>
        <button type="button" className={buttonSecondary}>
          Summarize
        </button>
        <a href="#actions" className={`${buttonSecondary} min-h-7 px-2.5 font-mono text-base`}>
          Check the summary against the frames
        </a>
      </div>
      <div className="mt-2">
        <div className="max-w-prose text-sm">
          <label
            className="flex items-center gap-2 text-muted-foreground"
            title="stella reads captured turns and uses organization credits."
          >
            <input type="checkbox" defaultChecked />
            Automatic run names and summaries
          </label>
        </div>
      </div>
    </section>
  );
}

function Stat({
  label,
  note: sub,
  tone,
  children,
}: {
  label: string;
  note?: React.ReactNode;
  tone?: "approval";
  children: React.ReactNode;
}) {
  return (
    <div className={runStatTile}>
      <span className={runStatTerm}>{label}</span>
      <span className={`${runStatValue} ${tone === "approval" ? "text-info" : ""}`}>{children}</span>
      {sub === undefined ? null : <span className={runStatNote}>{sub}</span>}
    </div>
  );
}

function StatRow() {
  return (
    <section aria-label="Run figures" className={`${runStatStrip} my-3`}>
      <Stat label="Tokens" note="152,904 in and 31,316 out">
        184,220
      </Stat>
      <Stat label="Prompts" note="one-shot session">
        1
      </Stat>
      <Stat label="Cost" note={<span className="font-mono text-[10.5px] text-muted-foreground">list price</span>}>
        <Money>$1.04</Money>
      </Stat>
      <Stat label="Wasted" note="the cost of steps that did not advance the task">
        <span className="text-muted-foreground">not recorded</span>
      </Stat>
      <Stat label="Wall clock" note="mostly waiting on a person">
        <span className="whitespace-nowrap tabular-nums">6m 06s</span>
      </Stat>
      <Stat label="Cache hit" note={<>saved about <Money>$0.62</Money></>}>
        71%
      </Stat>
    </section>
  );
}

/* ── Tabs ───────────────────────────────────────────────────────────────── */

function ParkedDot() {
  return (
    <span title="A call is parked for approval" className="ml-0.5 inline-block size-1.5 rounded-full bg-info align-middle">
      <span className="sr-only">A call is parked for approval</span>
    </span>
  );
}

const RUN_TABS = [
  { name: "transcript", label: "Transcript", count: "16" },
  { name: "issues", label: "Issues", count: "1" },
  { name: "actions", label: "Governed actions", count: "4", mark: <ParkedDot /> },
  { name: "cost", label: "Cost", count: <span className="text-muted-foreground">$1.04</span> },
  { name: "policy", label: "Policy", count: "4", mark: <ParkedDot /> },
  { name: "context", label: "Context", count: "2" },
  { name: "chain", label: "Chain and seal", count: "live" },
];

/* ── Transcript ─────────────────────────────────────────────────────────── */

const kindShape =
  "inline-flex items-center gap-1.5 rounded-md py-[3px] pr-2 font-mono text-[11px] focus-visible:outline-2 focus-visible:outline-ring max-md:min-h-9";
const kindPressed =
  "aria-pressed:bg-hl aria-pressed:shadow-[inset_0_0_0_1px_var(--rule)] aria-[pressed=false]:text-muted-foreground aria-[pressed=false]:[&>span:not([data-dot])]:line-through";
const txKind = `${kindShape} ${kindPressed} pl-1.5 text-muted-foreground aria-pressed:text-foreground`;
const txKindAll = `${kindShape} pl-2 text-muted-foreground hover:text-foreground`;
const txKindErrors = `${kindShape} ${kindPressed} pl-1.5 text-muted-foreground aria-pressed:text-error`;
const txKindCount = "text-[10px] tabular-nums text-muted-foreground";

const DOT: Record<string, string> = {
  prompt: "bg-fk-op shadow-[0_0_0_1px_color-mix(in_srgb,var(--fk-op)_40%,transparent)]",
  responses: "bg-fk-model shadow-[0_0_0_1px_color-mix(in_srgb,var(--fk-model)_40%,transparent)]",
  thinking: "bg-fk-model shadow-[0_0_0_1px_color-mix(in_srgb,var(--fk-model)_40%,transparent)]",
  tools: "bg-fk-tool shadow-[0_0_0_1px_color-mix(in_srgb,var(--fk-tool)_40%,transparent)]",
  usage: "bg-fk-gov shadow-[0_0_0_1px_color-mix(in_srgb,var(--fk-gov)_40%,transparent)]",
  recall: "bg-fk-ctx shadow-[0_0_0_1px_color-mix(in_srgb,var(--fk-ctx)_40%,transparent)]",
  seal: "bg-fk-gov shadow-[0_0_0_1px_color-mix(in_srgb,var(--fk-gov)_40%,transparent)]",
};

const buttonShape =
  "inline-flex items-center justify-center gap-[7px] rounded-[7px] border border-border px-2 py-[3px] font-mono text-[11.5px] font-medium text-foreground transition-colors hover:border-rule hover:bg-hl aria-pressed:border-rule aria-pressed:bg-hl focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-ring disabled:cursor-not-allowed disabled:opacity-45 max-md:min-h-9";
const txButton = `${buttonShape} min-w-[30px] bg-card`;
const txGhost = `${buttonShape} min-w-[30px] bg-transparent`;
const txPlayButton = `${buttonShape} min-w-[74px] bg-card`;
const txSeg = "ml-1 inline-flex gap-0.5 rounded-lg border border-border bg-void p-0.5";
const txSegButton =
  "inline-flex min-w-[30px] items-center justify-center rounded-[7px] border border-transparent bg-transparent px-2 py-[3px] font-mono text-[11.5px] font-medium text-foreground hover:bg-hl aria-pressed:border-rule aria-pressed:bg-hl max-md:min-h-9";
const txCount = "ml-1 whitespace-nowrap text-[10.5px] tabular-nums text-muted-foreground";
const txBurn =
  "flex items-center gap-2 whitespace-nowrap text-[10.5px] tabular-nums text-muted-foreground max-md:flex-wrap max-md:whitespace-normal";
const txProse = "min-w-0 whitespace-pre-wrap [overflow-wrap:anywhere]";
const txProseLine = "min-w-0 truncate";
const txs = "flex min-w-0 flex-col font-mono text-[12.5px] leading-[1.65] text-foreground";
const txTools = "flex flex-wrap items-center gap-2 pb-2.5";
const txSearch =
  "w-[220px] max-w-full max-md:w-full rounded-lg border border-border bg-void px-2.5 py-1.5 font-mono text-base text-foreground placeholder:text-muted-foreground focus-visible:outline-2 focus-visible:outline-offset-0 focus-visible:outline-ring max-md:text-base";

const chipShape = "whitespace-nowrap rounded-[5px] border bg-card px-1.5 font-mono text-[10.5px] leading-[1.6] tabular-nums";
const CHIP = {
  plain: `${chipShape} border-border text-muted-foreground`,
  ok: `${chipShape} border-border text-success`,
  err: `${chipShape} border-border text-error`,
  cost: `${chipShape} border-rule text-foreground`,
  burn: `${chipShape} border-border text-muted-foreground`,
  gov: `${chipShape} border-info/40 text-info hover:text-foreground focus-visible:outline-2 focus-visible:outline-ring`,
} as const;

const CLAWD = " ▐▛███▜▌\n▝▜█████▛▘\n  ▘▘ ▝▝";

function FrameChip({ frame, children }: { frame: Frame; children: React.ReactNode }) {
  return (
    <a href={`#fr-${frame.seq}`} className={CHIP.gov}>
      {children}
    </a>
  );
}

/** The first line of a prose row, as the closed row shows it. */
function closedLine(text: string): string {
  return text.split("\n")[0] ?? "";
}

function Fold({
  open,
  label,
  closedGlyph,
  onToggle,
  className = "",
}: {
  open: boolean;
  label: string;
  closedGlyph: "⏵" | "⋯";
  onToggle: () => void;
  className?: string;
}) {
  return (
    <button type="button" className={`tx-fold ${className}`} aria-expanded={open} aria-label={label} onClick={onToggle}>
      {open ? "⏶" : closedGlyph}
    </button>
  );
}

function Prose({ text, open, onToggle }: { text: string; open: boolean; onToggle: () => void }) {
  return (
    <div className={open ? txProse : txProseLine}>
      <Fold open={open} label={open ? "Show less" : "Show in full"} closedGlyph="⏵" onToggle={onToggle} className="pr-[1ch]" />
      {open ? text : (
        <span className="cursor-pointer" onClick={onToggle}>
          {closedLine(text)}
        </span>
      )}
    </div>
  );
}

function Cells({ line, margin }: { line: React.ReactNode; margin?: React.ReactNode }) {
  return (
    <div className="tx-cells">
      <div className="tc">{line}</div>
      <div className="tm">{margin}</div>
    </div>
  );
}

function RowView({ row, open, onToggle }: { row: FeedRow; open: boolean; onToggle: () => void }) {
  switch (row.kind) {
    case "prompt":
      return (
        <Cells
          line={
            <div className="tx-ln tx-user">
              <span className="sr-only">You</span>
              <Prose text={row.text} open={open} onToggle={onToggle} />
            </div>
          }
          margin={
            open ? (
              <>
                <span className="mg-note">{RUN.operator} (operator)</span>
                <span className="mg-note">task {RUN.task}</span>
                <span className="mg-note">first prompt</span>
              </>
            ) : null
          }
        />
      );
    case "text":
      return (
        <Cells
          line={
            <div className="tx-ln tx-say">
              <span className="sr-only">Agent</span>
              <Prose text={row.text} open={open} onToggle={onToggle} />
            </div>
          }
        />
      );
    case "thinking": {
      const lines = row.text.split("\n").length;
      return (
        <Cells
          line={
            <div className="tx-ln tx-think">
              <div className="flex min-w-0 items-baseline gap-[1ch]">
                <button type="button" className="tx-fold flex-none" aria-expanded={open} onClick={onToggle}>
                  <span aria-hidden="true">{open ? "⏶ " : "⏵ "}</span>
                  {lines} lines of thinking
                </button>
                {open ? null : (
                  <span className="min-w-0 cursor-pointer truncate" onClick={onToggle}>
                    {closedLine(row.text)}
                  </span>
                )}
              </div>
              {open ? <div className={txProse}>{row.text}</div> : null}
            </div>
          }
        />
      );
    }
    case "tool": {
      const failed = row.state === "err";
      const lines = row.output === null ? 0 : row.output.split("\n").length;
      return (
        <Cells
          line={
            <>
              <div className="tx-ln tx-call" data-state={row.state}>
                {failed ? (
                  <span aria-hidden="true" className="tx-x">
                    ✗
                  </span>
                ) : null}
                <span className="tx-head" onClick={onToggle}>
                  <span className={failed ? "tx-name tx-err" : "tx-name"}>{row.name}</span>
                  <span className="tx-arg">{row.arg}</span>
                </span>
              </div>
              {open ? (
                <div>
                  {row.output === null ? null : (
                    <div className="tx-res">
                      <pre className={failed ? "tx-out tx-err" : "tx-out"}>{row.output}</pre>
                    </div>
                  )}
                  {row.parked === null ? null : (
                    <div className="tx-res">The call waits for a person to approve it.</div>
                  )}
                  <div className="tx-res flex flex-wrap items-baseline gap-[1ch]">
                    <FrameChip frame={row.frame}>
                      {row.frame.type} · fr {row.frame.seq}
                    </FrameChip>
                  </div>
                </div>
              ) : null}
            </>
          }
          margin={
            <>
              {row.diff === null ? null : (
                <span className={CHIP.plain}>
                  <span className="text-success">+{row.diff.added}</span>{" "}
                  <span className="text-warning">−{row.diff.removed}</span>
                </span>
              )}
              {row.duration === null ? null : <span className={failed ? CHIP.err : CHIP.plain}>{row.duration}</span>}
              {row.diff === null && lines > 1 ? <span className={failed ? CHIP.err : CHIP.plain}>{lines} lines</span> : null}
              {row.parked === null ? null : (
                <FrameChip frame={{ type: "approval", seq: row.parked }}>
                  <span aria-hidden="true">⏸ </span>parked · fr {row.parked}
                </FrameChip>
              )}
              {row.gate === null ? null : (
                <FrameChip frame={{ type: "policy", seq: row.gate.seq }}>
                  <span aria-hidden="true">⚖ </span>
                  {row.gate.decision} · fr {row.gate.seq}
                </FrameChip>
              )}
              <Fold open={open} label={open ? "Hide the call" : "Show the call"} closedGlyph="⋯" onToggle={onToggle} />
            </>
          }
        />
      );
    }
    case "usage":
      return (
        <Cells
          line={<div className="tx-ln tx-quiet truncate">{row.line}</div>}
          margin={
            <>
              <span className={CHIP.plain}>{row.effort}</span>
              <span className={CHIP.cost} title="list price">
                <Money>{row.cost}</Money>
              </span>
              <span className={CHIP.burn} title="list price">
                Σ <Money>{row.spent}</Money>
              </span>
              <FrameChip frame={row.frame}>
                {row.frame.type} · fr {row.frame.seq}
              </FrameChip>
            </>
          }
        />
      );
  }
}

/** A style that also sets a CSS custom property, such as a row's `--depth`. */
type StyleWithVariables = React.CSSProperties & Record<`--${string}`, string>;

/** Every row here sits at the top level: no subagent ran. */
const TOP: StyleWithVariables = { "--depth": "0" };

function Transcript() {
  const [open, setOpen] = React.useState<ReadonlySet<number>>(() => new Set());
  const toggle = (index: number) =>
    setOpen((prev) => {
      const next = new Set(prev);
      if (!next.delete(index)) next.add(index);
      return next;
    });
  const total = FEED.length;
  return (
    <section aria-label="Transcript" className={txs}>
      <div className={txTools}>
        <input type="search" placeholder="Search the transcript…" aria-label="Search the transcript" className={txSearch} />
        <div role="group" aria-label="Filter the transcript" className="flex flex-wrap gap-[3px]">
          {KINDS.map((kind) => (
            <button key={kind.group} type="button" aria-pressed className={txKind}>
              <span data-dot="" aria-hidden="true" className={`size-2 flex-none rounded-[2px] ${DOT[kind.group] ?? ""}`} />
              <span>{kind.label}</span>
              <span className={txKindCount}>{kind.count}</span>
            </button>
          ))}
          <button type="button" className={txKindAll}>
            none
          </button>
          <button type="button" aria-pressed={false} className={txKindErrors}>
            <span>✗ errors</span>
            <span className={txKindCount}>1</span>
          </button>
        </div>
      </div>
      <div role="group" aria-label="Playback" className="rpbar">
        <button type="button" className={txButton} aria-label="Rewind" title="Rewind">
          ⏮
        </button>
        <button type="button" className={txButton} aria-label="Step back" title="Step back">
          ◀
        </button>
        <button type="button" className={txPlayButton}>
          <span aria-hidden="true">❙❙ </span>
          pause
        </button>
        <button type="button" className={txButton} aria-label="Step forward" title="Step forward" disabled>
          ▶
        </button>
        <button type="button" className={txButton} aria-label="To the end" title="To the end" disabled>
          ⏭
        </button>
        <div className="rp-track">
          <div className="rp-rail" aria-hidden="true">
            <div className="rp-fill" style={{ width: "100%" }} />
          </div>
          <div className="rp-marks" aria-hidden="true">
            {FEED.map((row, index) =>
              row.kind === "prompt" || row.kind === "tool" ? (
                <i
                  key={row.at}
                  className={row.kind === "prompt" ? "m-user" : row.state === "err" ? "m-err" : "m-tool"}
                  style={{ left: `${(index / total) * 100}%` }}
                />
              ) : null,
            )}
          </div>
          <input
            type="range"
            className="rp-range"
            aria-label="Scrub through the transcript"
            aria-valuetext={`${total} / ${total}`}
            min={0}
            max={total}
            step={1}
            defaultValue={total}
          />
        </div>
        <span className="rp-time">
          <span>6m 06s</span>
          <span>6m 06s</span>
        </span>
        <span role="group" aria-label="Playback speed" className={txSeg}>
          {[1, 2, 3, 6].map((value) => (
            <button key={value} type="button" aria-pressed={value === 1} className={txSegButton}>
              {value}×
            </button>
          ))}
        </span>
        <span className={txCount}>
          {total} / {total}
        </span>
        <button type="button" aria-pressed={false} className={`${txGhost} ml-auto`}>
          expand thinking
        </button>
      </div>
      <div className="term cc">
        <div className="term-top">
          <div />
          <div className="term-bar">
            <span className="term-dots" aria-hidden="true">
              <i />
              <i />
              <i />
            </span>
            <span className="term-t">
              <b>{RUN.task}</b>
              {[RUN.agentKey, RUN.model, "1 turn", "11 steps", `${total} entries`].join(" · ")}
            </span>
            <span className="term-h">
              <span className={CHIP.ok}>
                <span aria-hidden="true">● </span>live
              </span>
              <span className={txBurn}>
                <span>burn</span>
                <span className="h-1 w-[120px] overflow-hidden rounded-[2px] bg-hl">
                  <i aria-hidden="true" className="block h-full bg-info" style={{ width: "21%" }} />
                </span>
                <b className="font-semibold text-foreground">
                  <Money>$1.04</Money>
                </b>
                <span>
                  of <Money>$5.00</Money> list price
                </span>
              </span>
            </span>
          </div>
          <div />
        </div>
        <div className="rp-body">
          <div className="tr tr-banner">
            <div className="tg" />
            <div className="tc">
              <div className="tx-banner">
                <pre aria-hidden="true" className="tx-clawd">
                  {CLAWD}
                </pre>
                <div>
                  <b>Claude Code</b>
                  <span className="tx-dim"> v{RUN.harnessVersion}</span>
                  <div className="tx-dim">{RUN.model}</div>
                </div>
              </div>
            </div>
            <div className="tm" />
          </div>
          {FEED.map((row, index) => (
            <div key={`${row.at}-${row.kind}`} data-kind={row.kind} style={TOP}>
              <div className="tr">
                <div className="tg">
                  <time>{row.at}</time>
                </div>
                <RowView row={row} open={open.has(index)} onToggle={() => toggle(index)} />
              </div>
            </div>
          ))}
          <div className="tr tr-foot">
            <div className="tg" />
            <div className="tc">
              <div className="tx-working">
                <span aria-hidden="true" className="tx-spin" />
                <span className="tx-word">Working…</span>
              </div>
            </div>
            <div className="tm" />
          </div>
        </div>
      </div>
      <div className="mt-3">
        <p className={`${note} m-0`}>
          The transcript is what the agent showed its operator. The gateway’s own frames sit behind the ⚖ chips.
        </p>
      </div>
    </section>
  );
}

/* ── The work: changes and outputs ──────────────────────────────────────── */

function Row({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <>
      <dt className={`${kvTerm} text-[11px]`}>{label}</dt>
      <dd className={`${kvValue} text-sm`}>{children}</dd>
    </>
  );
}

function DiffStat({ added, removed }: { added: number; removed: number }) {
  return (
    <span className="whitespace-nowrap font-mono">
      <b className="text-success">+{added}</b> <b className="text-warning">−{removed}</b>
    </span>
  );
}

const FILES = [
  { name: "migrations/0147_invoice_currency.sql", added: 38, removed: 0 },
  { name: "db/schema/invoices.sql", added: 3, removed: 0 },
] as const;

function ChangesPanel() {
  return (
    <section aria-labelledby="run-panel-changes" className={panel}>
      <div className={panelHeader}>
        <h3 id="run-panel-changes" className={panelTitle}>
          Changes
        </h3>
      </div>
      <div className={panelBody}>
        <dl className="grid grid-cols-[auto_1fr] items-baseline gap-x-4 gap-y-[7px]">
          <Row label="Pull request">
            <span className="text-muted-foreground">none yet (the run is still working)</span>
          </Row>
          <Row label="Base">
            <span className="text-muted-foreground">not recorded</span>
          </Row>
          <Row label="Checks">
            <span className="text-muted-foreground">none reported</span>
          </Row>
          <Row label="Diff">
            <span>
              <DiffStat added={41} removed={0} /> <span className="text-muted-foreground">in 2 files</span>
            </span>
          </Row>
        </dl>
        <ul className="mt-2 border-t border-border">
          {FILES.map((file) => (
            <li
              key={file.name}
              className="flex min-w-0 justify-between gap-2.5 border-b border-border py-[5px] text-[11.5px]"
            >
              <span className="min-w-0 truncate font-mono">{file.name}</span>
              <DiffStat added={file.added} removed={file.removed} />
            </li>
          ))}
        </ul>
        <div className="mt-2 flex">
          <a href="#transcript" className={`${buttonSecondary} min-h-7 px-2.5 text-base`}>
            Open the diff in the transcript
          </a>
        </div>
      </div>
    </section>
  );
}

type OutputKind = "file" | "commit" | "gate";

const GLYPH: Record<OutputKind, React.ReactNode> = {
  file: (
    <>
      <path d="M14 3H7a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V8z" />
      <path d="M14 3v5h5M9 13h6M9 17h4" />
    </>
  ),
  commit: (
    <>
      <circle cx="6" cy="6" r="2.5" />
      <circle cx="6" cy="18" r="2.5" />
      <circle cx="18" cy="8" r="2.5" />
      <path d="M6 8.5v7M18 10.5c0 4-3.5 4-6 5.5" />
    </>
  ),
  gate: (
    <>
      <rect x="4" y="11" width="16" height="10" rx="2" />
      <path d="M8 11V7a4 4 0 0 1 8 0v4" />
    </>
  ),
};

function Glyph({ kind }: { kind: OutputKind }) {
  return (
    <svg
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="1.7"
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden="true"
      className="size-[13px]"
    >
      {GLYPH[kind]}
    </svg>
  );
}

const OUTPUTS: readonly {
  kind: OutputKind;
  name: string;
  state: "written" | "created" | "awaiting";
  stat: { added: number; removed: number } | null;
  seq: number;
  where: string | null;
  note: string | null;
}[] = [
  { kind: "file", name: "migrations/0147_invoice_currency.sql", state: "written", stat: { added: 38, removed: 0 }, seq: 11, where: RUN.repository, note: null },
  { kind: "file", name: "db/schema/invoices.sql", state: "written", stat: { added: 3, removed: 0 }, seq: 12, where: RUN.repository, note: null },
  { kind: "commit", name: "Add the invoice currency column", state: "created", stat: null, seq: 21, where: "release/2026.10", note: null },
  {
    kind: "gate",
    name: "git push origin release/2026.10",
    state: "awaiting",
    stat: null,
    seq: 26,
    where: null,
    note: "Rule release-branch routes it to a person.",
  },
];

const linkQuiet =
  "rounded-sm text-[11.5px] text-muted-foreground underline decoration-rule underline-offset-2 hover:text-foreground focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-ring";

function OutputsSpine() {
  return (
    <section
      aria-label="Run outputs"
      className="rounded-xl border border-border bg-card px-[18px] pb-[13px] pt-[15px] text-card-foreground"
    >
      <div className="mb-3 flex flex-wrap items-center gap-2.5">
        <h2 className={`${eyebrowQuiet} m-0`}>Outputs</h2>
        <span className="ml-auto font-mono text-[11px] text-muted-foreground">3 artifacts · 2 reads · 1 gate</span>
        <a href="#reads" className={linkQuiet}>
          Hide reads
        </a>
      </div>
      <ol className="relative m-0 list-none py-0 pl-[30px] before:absolute before:bottom-1.5 before:left-[11px] before:top-1.5 before:w-px before:content-[''] before:bg-gradient-to-b before:from-rule before:from-[78%] before:to-transparent">
        <li className="relative flex min-w-0 flex-wrap items-baseline gap-2 py-[5px]">
          <span aria-hidden="true" className="absolute -left-[23px] top-3 h-px w-[9px] bg-rule" />
          <span className="min-w-0 text-[11.5px] text-muted-foreground">
            read{" "}
            <b className="break-all font-mono text-[11px] font-medium text-muted-foreground">db/schema/invoices.sql</b>,{" "}
            <b className="break-all font-mono text-[11px] font-medium text-muted-foreground">db/README.md</b>
          </span>
        </li>
        {OUTPUTS.map((node) => {
          const gate = node.kind === "gate";
          return (
            <li key={node.name} className="relative min-w-0 py-[7px]">
              <span
                aria-hidden="true"
                className={`absolute -left-[30px] top-1.5 grid size-[23px] place-items-center rounded-full border bg-card ${
                  node.state === "awaiting" ? "border-info/55 text-info" : "border-border text-muted-foreground"
                }`}
              >
                <Glyph kind={node.kind} />
              </span>
              <div className={`min-w-0 ${gate ? "rounded-[10px] border border-info/40 bg-info/10 px-3 py-2.5" : ""}`}>
                <div className="flex min-w-0 flex-wrap items-center gap-2">
                  <b className="min-w-0 max-w-full truncate font-mono text-[13px] font-semibold text-foreground">{node.name}</b>
                  <Badge tone={node.state === "awaiting" ? "approval" : "allowed"}>{node.state}</Badge>
                  {node.stat === null ? null : (
                    <span className={`${mono} shrink-0 text-[11px] tabular-nums`}>
                      <b className="font-semibold text-success">+{node.stat.added}</b>{" "}
                      <b className="font-semibold text-warning">&minus;{node.stat.removed}</b>
                    </span>
                  )}
                  <a
                    href={`#fr-${node.seq}`}
                    title="Open the frame that recorded this"
                    className="shrink-0 rounded-md border border-border bg-background px-1.5 py-px font-mono text-[10.5px] text-muted-foreground hover:border-rule hover:text-foreground"
                  >
                    fr {node.seq}
                  </a>
                </div>
                <div className="mt-[3px] flex flex-wrap items-baseline gap-2 text-[11.5px] leading-normal">
                  {node.where === null ? null : (
                    <span className="min-w-0 font-mono text-[11px] text-muted-foreground [overflow-wrap:anywhere]">{node.where}</span>
                  )}
                  {node.note === null ? null : (
                    <span className="min-w-0 text-muted-foreground [overflow-wrap:anywhere]">{node.note}</span>
                  )}
                </div>
                {gate ? (
                  <div className="mt-[9px] flex flex-wrap items-center gap-2.5">
                    <a href="#actions" className={`${buttonSecondary} min-h-7 px-2.5 text-base`}>
                      Review the approval
                    </a>
                    <span className="text-[11px] text-muted-foreground">the run is stopped here until someone answers</span>
                  </div>
                ) : null}
              </div>
            </li>
          );
        })}
      </ol>
      <p className="mt-[11px] flex flex-wrap items-center gap-x-2 gap-y-1 border-t border-border pt-2.5 text-[11px] text-muted-foreground">
        <span>In frame order.</span>
      </p>
    </section>
  );
}

/* ── Page ───────────────────────────────────────────────────────────────── */

/** The Run page: the header, the summary, the figures, the tabs with Transcript open, and the work beside them. */
export function RunPage() {
  return (
    <AppFrame
      current="fleet"
      crumbs={[
        { text: "A-Intel", href: "#organization" },
        { text: WORKSPACE.name, href: "#workspace" },
        { text: "Fleet", href: "#fleet" },
        { text: RUN.id, href: null, mono: true },
      ]}
    >
      <div className="flex flex-col">
        <RunHeader />
        <div className="grid grid-cols-1 items-start gap-3.5 min-[67.5rem]:grid-cols-[minmax(0,2fr)_minmax(0,1fr)]">
          <div className="flex min-w-0 flex-col">
            <SummaryPanel />
            <StatRow />
            <div className="mb-4 mt-0.5">
              <RouteTabs
                label="Run sections"
                panel="run-tab-panel"
                selected="transcript"
                onSelect={() => {}}
                tabs={RUN_TABS}
              />
            </div>
            <RouteTabPanel panel="run-tab-panel" className="flex flex-col gap-3.5">
              <Transcript />
            </RouteTabPanel>
          </div>
          <aside aria-label="Work" className="grid min-w-0 grid-cols-1 gap-3">
            <ChangesPanel />
            <OutputsSpine />
          </aside>
        </div>
      </div>
    </AppFrame>
  );
}
