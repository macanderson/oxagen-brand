import * as React from "react";
import type { Meta, StoryObj } from "@storybook/react-vite";

const meta = {
  title: "Foundations/Typography",
  parameters: { layout: "padded" },
} satisfies Meta;
export default meta;
type Story = StoryObj<typeof meta>;

type SampleTag = "h1" | "h2" | "h3" | "h4" | "h5" | "h6" | "p" | "small" | "code";

interface Sample {
  tag: SampleTag;
  /** The type utility the sample wears. */
  className: string;
  text: string;
}

/*
 * The samples name no face and no size. Each one takes both from the kit's
 * base rules for its element and from its type utility, and the caption under
 * it reads them back from the browser. No sample is below 14px, the floor for
 * every surface.
 */
const APP_SCALE: Sample[] = [
  { tag: "h1", className: "text-a-h1", text: "Refunds workspace" },
  { tag: "h2", className: "text-a-h2", text: "Policy review" },
  { tag: "h3", className: "text-a-h3", text: "Spend this week" },
  { tag: "h4", className: "text-a-h4", text: "Approvals waiting" },
  { tag: "h5", className: "text-sm", text: "Deploy step" },
  { tag: "h6", className: "text-xs", text: "Run details" },
  {
    tag: "p",
    className: "text-a-body",
    text: "Stella reads the run, checks it against the spend policy, and asks an owner before it deploys.",
  },
  {
    tag: "small",
    className: "text-xs text-muted-foreground",
    text: "Updated 4 minutes ago by the policy agent",
  },
  { tag: "code", className: "text-a-micro", text: "wo_01K6T9QX workspace.owner" },
];

const MARKETING_SCALE: Sample[] = [
  { tag: "h1", className: "text-m-h1", text: "Release notes for September" },
  { tag: "h2", className: "text-m-h2", text: "Approvals where the work is" },
  { tag: "h3", className: "text-m-h3", text: "One policy for every harness" },
  { tag: "h4", className: "text-m-h4", text: "Spend caps per workspace" },
  {
    tag: "p",
    className: "text-m-body",
    text: "Oxagen watches each run, stops the ones that break policy, and shows an owner what it cut and why.",
  },
  { tag: "code", className: "text-m-micro", text: "oxagen policy apply refunds.toml" },
];

/*
 * The heading rule. On a marketing or customer site, h1 to h3 wear
 * text-m-h1 to text-m-h3, which set Space Grotesk. In the app and the
 * internal tools, h1 to h3 wear text-a-h1 to text-a-h3, which read
 * --font-heading, Aeonik by default. Every h4 to h6 is Aeonik on both.
 */
const MARKETING_HEADINGS: Sample[] = [
  { tag: "h1", className: "text-m-h1", text: "Govern every agent" },
  { tag: "h2", className: "text-m-h2", text: "One record for every run" },
  { tag: "h3", className: "text-m-h3", text: "Approvals where the work is" },
  { tag: "h4", className: "text-m-h4", text: "Spend caps per workspace" },
];

const APP_HEADINGS: Sample[] = [
  { tag: "h1", className: "text-a-h1", text: "Refunds workspace" },
  { tag: "h2", className: "text-a-h2", text: "Policy review" },
  { tag: "h3", className: "text-a-h3", text: "Spend this week" },
  { tag: "h4", className: "text-a-h4", text: "Approvals waiting" },
];

/*
 * The face tokens. Aeonik sets --font-sans and, by default, --font-heading,
 * so an Aeonik sample matches both. Space Grotesk sets --font-display and
 * --font-wordmark, so a Space Grotesk sample matches both. The caption names
 * every match.
 */
const FACE_TOKENS = [
  "--font-display",
  "--font-heading",
  "--font-sans",
  "--font-mono",
  "--font-wordmark",
] as const;

interface Metrics {
  face: string;
  tokens: string[];
  size: string;
  weight: string;
  lineHeight: string;
}

function normaliseStack(stack: string): string {
  return stack.replace(/["'\s]/g, "").toLowerCase();
}

function firstFamily(stack: string): string {
  return (stack.split(",")[0] ?? "").trim().replace(/^["']|["']$/g, "");
}

function round(value: number): string {
  return String(Math.round(value * 100) / 100);
}

/** Reads the face, size, weight and line height the browser resolved. */
function readMetrics(element: Element): Metrics {
  const style = getComputedStyle(element);
  const root = getComputedStyle(document.documentElement);
  const stack = normaliseStack(style.fontFamily);
  const tokens = FACE_TOKENS.filter(
    (name) => normaliseStack(root.getPropertyValue(name)) === stack,
  );
  const size = Number.parseFloat(style.fontSize);
  const line = Number.parseFloat(style.lineHeight);
  return {
    face: firstFamily(style.fontFamily),
    tokens,
    size: `${round(size)}px`,
    weight: style.fontWeight,
    lineHeight: Number.isFinite(line) && size > 0 ? round(line / size) : "normal",
  };
}

function Fact({ term, children }: { term: string; children: React.ReactNode }) {
  return (
    <div className="flex gap-1.5">
      <dt className="text-dim">{term}</dt>
      <dd className="text-muted-foreground">{children}</dd>
    </div>
  );
}

function Specimen({ sample }: { sample: Sample }) {
  const frame = React.useRef<HTMLDivElement>(null);
  const [metrics, setMetrics] = React.useState<Metrics | null>(null);

  React.useLayoutEffect(() => {
    const element = frame.current?.firstElementChild;
    if (!element) return;
    setMetrics(readMetrics(element));
    // Web fonts can load after the first paint. Read again once they have.
    let live = true;
    void document.fonts?.ready.then(() => {
      if (live) setMetrics(readMetrics(element));
    });
    return () => {
      live = false;
    };
  }, [sample]);

  return (
    <div className="flex flex-col gap-2 border-b border-border py-5 last:border-b-0">
      <div ref={frame} className="min-w-0 [overflow-wrap:anywhere]">
        {React.createElement(
          sample.tag,
          { className: sample.className },
          sample.text,
        )}
      </div>
      <dl className="flex flex-wrap gap-x-5 gap-y-1 font-mono text-xs">
        <Fact term="Element">{sample.tag}</Fact>
        <Fact term="Class">{sample.className}</Fact>
        {metrics && (
          <>
            <Fact term="Face">{metrics.face}</Fact>
            {metrics.tokens.length > 0 && (
              <Fact term="Tokens">{metrics.tokens.join(" = ")}</Fact>
            )}
            <Fact term="Size">{metrics.size}</Fact>
            <Fact term="Weight">{metrics.weight}</Fact>
            <Fact term="Line height">{metrics.lineHeight}</Fact>
          </>
        )}
      </dl>
    </div>
  );
}

function Scale({ samples, label }: { samples: Sample[]; label?: string }) {
  return (
    <div className="flex max-w-[880px] flex-col">
      {label ? (
        <p className="text-sm font-semibold text-muted-foreground">{label}</p>
      ) : null}
      {samples.map((sample) => (
        <Specimen
          key={`${sample.tag}-${sample.className}-${sample.text}`}
          sample={sample}
        />
      ))}
    </div>
  );
}

/** The dense scale for panels, tables and logs. */
export const AppScale: Story = {
  name: "App scale",
  render: () => <Scale samples={APP_SCALE} />,
};

/** The large scale for landing pages and posts. Docs use the app scale. */
export const MarketingScale: Story = {
  name: "Marketing scale",
  render: () => <Scale samples={MARKETING_SCALE} />,
};

/**
 * Headings on each surface. A marketing or customer site sets h1 to h3 in
 * Space Grotesk. The app and the internal tools set them in Aeonik. Every h4
 * is Aeonik.
 */
export const Headings: Story = {
  name: "Headings",
  render: () => (
    <div className="flex flex-col gap-10">
      <Scale label="Marketing and customer sites" samples={MARKETING_HEADINGS} />
      <Scale label="App and internal tools" samples={APP_HEADINGS} />
    </div>
  ),
};
