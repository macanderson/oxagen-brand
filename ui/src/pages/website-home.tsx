import { Button } from "../components/button";
import { eyebrow } from "../components/control-styles";
import { cell, DataTable } from "../components/data-table";
import { HexField } from "../components/hex-field";
import { cn } from "../lib/utils";
import {
  AnswerBadge,
  Qualifier,
  RequestSteps,
  SiteCard,
  SiteFooter,
  SiteNav,
  SiteSection,
  siteWrap,
  type RequestAnswer,
} from "./page-chrome";

function Hero() {
  return (
    <section id="top" className="relative isolate -mt-16 overflow-hidden">
      <div
        aria-hidden
        className="ox-hero-grid pointer-events-none absolute inset-0 -z-10"
      />
      <HexField className="ox-hex-float pointer-events-none absolute inset-0 -z-10 h-full w-full text-foreground" />
      <div className={cn(siteWrap, "pt-36 pb-28 max-md:pt-28 max-md:pb-20")}>
        <p className={eyebrow}>Workforce management for autonomous agents</p>
        <h1 className="mt-5 text-m-h1 text-foreground max-lg:text-[3.5rem] max-sm:text-[2.5rem]">
          <span className="hero-line-1">Your agents are a workforce now.</span>
          <br />
          Manage them like one.
        </h1>
        <p className="mt-6 max-w-[40rem] text-m-body text-muted-foreground">
          Give each agent an identity. Set its authority and budget, equip it
          with tools and skills, and review what it did and what its operators
          spent. Oxagen keeps the record of the actions it governs.
        </p>
        <div className="mt-8 flex flex-wrap gap-3">
          <Button variant="outline" size="lg" render={<a href="#how" />}>
            See how it works
          </Button>
        </div>
      </div>
    </section>
  );
}

const CLAUSES = [
  {
    title: "Access",
    meta: "Set by security",
    body: "Which identity the agent acts as, which systems it may request, which data and knowledge scope it may read, and which actions it may request.",
  },
  {
    title: "Budget and rules",
    meta: "Set by finance",
    body: "What the agent may spend, under which commercial terms, and the rules it must obey, such as approval thresholds and allowed vendors.",
  },
  {
    title: "Equipment",
    meta: "Set by engineering",
    body: "The knowledge the agent is handed at the start of a job, the skills and tools it may use, and the steering it runs under.",
  },
  {
    title: "Record",
    meta: "Kept by the platform",
    body: "What the run read, what it changed, what it cost, and which checks it passed. The platform keeps it.",
  },
] as const;

type SampleRequest = {
  agent: string;
  request: string;
  answer: RequestAnswer;
  by: string;
};

/** Sample rows in the Access page's own words (voice.md, UI strings). */
const REQUESTS: readonly SampleRequest[] = [
  {
    agent: "release-bot",
    request: "Read payments-api",
    answer: "allowed",
    by: "Rule repo-read",
  },
  {
    agent: "schema-migrator",
    request: "Push to main",
    answer: "denied",
    by: "Rule no-push-main",
  },
  {
    agent: "schema-migrator",
    request: "Push to release/2026.10",
    answer: "routed",
    by: "Waiting on Priya, rule release-branch",
  },
  {
    agent: "docs-writer",
    request: "Post to #release-notes",
    answer: "allowed",
    by: "Rule docs-channels",
  },
  {
    agent: "invoice-reconciler",
    request: "Spend over $20 on one run",
    answer: "routed",
    by: "Approved by Dana, rule spend-cap",
  },
];

const REQUEST_COLUMNS = [
  { label: "Agent" },
  { label: "Request" },
  { label: "Answer" },
  { label: "Decided by" },
] as const;

const PROOFS = [
  {
    title: "Governed calls",
    line: "One object, checked at the governed call.",
    body: "Identity, knowledge scope, permitted action, commercial terms, outcome, and audit record are one typed contract, checked when the agent makes a governed call, not reconstructed after the incident.",
    qualifier: "For actions routed through Oxagen.",
  },
  {
    title: "Rules",
    line: "Three answers, one rule.",
    body: "A rule names a capability, a condition, and one effect: allow, deny, or route to a person. For governed calls, Oxagen checks it before the handler runs, so a denied action does not reach the code that would have done it.",
    qualifier: "For governed calls.",
  },
  {
    title: "Cost",
    line: "Cost is a recorded row.",
    body: "Each governed action carries its recorded cost, attributed to the person, the agent, and the run, with measured, reported, and estimated costs marked. The Spend page and the run record read the same rows.",
  },
  {
    title: "Wrappers",
    line: "Whoever built the agent.",
    body: "Claude Code, the Agent SDK, or a custom loop, with a supported wrapper beside it. The wrapper records and gates governed calls from beside the agent. Oxagen does not run it.",
    qualifier: "With a supported wrapper.",
  },
] as const;

/**
 * The website's home page. The nav is the sticky glass bar, and the hero runs
 * under it, so the hex field and the grid show through the bar at rest. The
 * Product menu opens over the hero's headline. Scroll to see the sections
 * pass under the bar.
 *
 * Every line comes from an approved, launch-released entry in `messages/`:
 * `hero-eyebrow`, `hero-headline`, `mc-mandates`, `claim-one-mandate`, the
 * `clause-*` entries, `mc-access-requests`, `access-keys`, the `keys-*`
 * entries, `section-audit`, and the `proof-*` entries. Headings and card
 * titles are plain nouns, and an approved line that is a sentence opens the
 * body under them.
 */
export function HomePage({ productMenuOpen }: { productMenuOpen: boolean }) {
  return (
    <div className="min-h-screen bg-background text-foreground">
      <SiteNav productMenuOpen={productMenuOpen} />
      <main>
        <Hero />

        <SiteSection
          id="mandate"
          eyebrow="Mandate"
          title="Set the terms your agents work under."
          lead="Identity systems say who the agent is. Gateways say which tools it can call. Billing says what it consumed. Prompt repositories say what it was told. Oxagen binds those into one mandate per agent, checks it on the actions routed through Oxagen, and keeps a record another person can read."
          qualifier="Checked on the actions routed through Oxagen."
        >
          <div className="grid gap-4 md:grid-cols-2">
            {CLAUSES.map((clause) => (
              <SiteCard key={clause.title} {...clause} />
            ))}
          </div>
        </SiteSection>

        <SiteSection
          id="how"
          eyebrow="Access requests"
          title="Answer each request when the agent makes it."
          lead="The agent asks. A rule you wrote answers. For mediated connections, the credential stays in Oxagen."
          qualifier="For actions routed through Oxagen, and for mediated connections."
        >
          <div className="grid gap-10 lg:grid-cols-[minmax(0,5fr)_minmax(0,7fr)] lg:items-start">
            <RequestSteps />
            <figure className="m-0 min-w-0">
              <div className="overflow-hidden rounded-2xl border border-border bg-card">
                <DataTable label="Sample access requests" columns={REQUEST_COLUMNS}>
                  {REQUESTS.map((row) => (
                    <tr key={`${row.agent}-${row.request}`}>
                      <td className={cn(cell, "font-medium text-foreground")}>
                        {row.agent}
                      </td>
                      <td className={cn(cell, "font-mono text-xs")}>
                        {row.request}
                      </td>
                      <td className={cell}>
                        <AnswerBadge answer={row.answer} />
                      </td>
                      <td className={cn(cell, "text-muted-foreground")}>
                        {row.by}
                      </td>
                    </tr>
                  ))}
                </DataTable>
              </div>
              <figcaption className="mt-3">
                <Qualifier>Sample rows from the Access page.</Qualifier>
              </figcaption>
            </figure>
          </div>
        </SiteSection>

        <SiteSection
          id="record"
          eyebrow="Record"
          title="Follow the action back to its authority."
          lead="Review which agent requested an action, on whose behalf, which rule answered, and who approved it when a person was required. Inspect the recorded result and cost alongside that decision."
        >
          <div className="grid gap-4 md:grid-cols-2">
            {PROOFS.map((proof) => (
              <SiteCard key={proof.title} {...proof} />
            ))}
          </div>
        </SiteSection>
      </main>
      <SiteFooter />
    </div>
  );
}
