import { InfoIcon } from "@phosphor-icons/react";
import { Button } from "../components/button";
import { eyebrow } from "../components/control-styles";
import {
  Popover,
  PopoverDescription,
  PopoverPopup,
  PopoverTitle,
  PopoverTrigger,
} from "../components/popover";
import { cn } from "../lib/utils";
import {
  Qualifier,
  RequestSteps,
  SiteCard,
  SiteFooter,
  SiteNav,
  SiteSection,
  siteWrap,
} from "./page-chrome";

function Hero() {
  return (
    <section id="top" className="relative isolate -mt-16 overflow-hidden">
      <div
        aria-hidden
        className="ox-grid-dots pointer-events-none absolute inset-0 -z-10"
      />
      <div className={cn(siteWrap, "pt-36 pb-24 max-md:pt-28 max-md:pb-16")}>
        <p className={eyebrow}>Security</p>
        <h1 className="mt-5 max-w-[18ch] text-m-h1 text-foreground max-lg:text-[3.5rem] max-sm:text-[2.5rem]">
          Don&apos;t hand your agents the keys.
        </h1>
        <p className="mt-6 max-w-[44rem] text-m-body text-muted-foreground">
          An agent under Oxagen has its own identity and a mandate. When a task
          needs a system, a scope, or an action the mandate does not already
          cover, the agent asks for it at the moment of use. A rule allows the
          request, denies it, or routes it to a person, and the record keeps
          the answer. For mediated connections, Oxagen uses the connection
          credential on the agent&apos;s behalf, and the agent does not receive
          it.
        </p>
        <Qualifier className="mt-3">For mediated connections.</Qualifier>
        <div className="mt-8 flex flex-wrap gap-3">
          <Button variant="outline" size="lg" render={<a href="#controls" />}>
            Inspect an agent&apos;s authority
          </Button>
        </div>
      </div>
    </section>
  );
}

const CONTROLS = [
  {
    title: "Agent identity",
    line: "Give each agent an identity you can govern.",
    body: "Register each agent as a principal in a supported identity system, with its own roles, scope, and accountable operator.",
    qualifier: "In supported identity systems.",
    action: "Explore agent identity",
  },
  {
    title: "Access requests",
    line: "Answer each request when the agent makes it.",
    body: "The agent requests an action. Your rule allows it, denies it, or routes it to a person. For mediated connections, the credential stays in Oxagen.",
    qualifier:
      "For actions routed through Oxagen, and for mediated connections.",
    action: "Follow an access request",
  },
  {
    title: "Approvals",
    line: "Put the decision in the right hands.",
    body: "Route the requests that need judgment to the people responsible, with the action and its context ready to review.",
    action: "See an approval",
  },
  {
    title: "Pause and revoke",
    line: "Stop the next action at the boundary.",
    body: "Pause a run or revoke authority for an agent, a tool, or a workspace. Oxagen records what the control stopped.",
    qualifier: "At the next supported boundary, for governed calls.",
    action: "Explore run controls",
  },
  {
    title: "Audit record",
    line: "Keep the decisions behind the workforce on record.",
    body: "Review who changed an agent's authority, approved a request, or adjusted its budget alongside the work that followed.",
    qualifier: "Governed administrative actions.",
    action: "Inspect the audit record",
  },
  {
    title: "Signed run records",
    line: "Share the evidence with the answer.",
    body: "Export a signed run record with its actions, decisions, costs, and evidence for independent inspection.",
    action: "Inspect a run export",
  },
] as const;

/** Where the controls above apply, open over the cards. */
function ScopePopover({ open }: { open: boolean }) {
  return (
    <Popover defaultOpen={open}>
      <PopoverTrigger
        render={
          <Button variant="outline" startIcon={<InfoIcon aria-hidden />}>
            Scope
          </Button>
        }
      />
      <PopoverPopup side="bottom" align="end" className="w-[22rem]">
        <PopoverTitle>Scope</PopoverTitle>
        <PopoverDescription>
          These controls apply to governed calls: actions routed through
          Oxagen that it checks and records. In observe mode, Oxagen records a
          call without enforcing it.
        </PopoverDescription>
        <PopoverDescription>
          For a mediated connection, Oxagen holds the credential and uses it on
          the agent&apos;s behalf. The agent does not receive it, and the
          record shows each use.
        </PopoverDescription>
      </PopoverPopup>
    </Popover>
  );
}

/**
 * The website's security page, the second website page. The registry has no
 * approved pricing line, so the kit shows this page in place of a pricing
 * page rather than invent plans and prices.
 *
 * The nav is the same sticky glass bar as the home page. The hero runs under
 * it on the graph-dot texture. The capability cards sit on the opaque `panel`
 * recipe, and the Scope popover opens over them on the translucent floating
 * surface.
 *
 * Every line comes from an approved, launch-released entry in `messages/`:
 * `access-keys`, `security-headline`, the `ie-*` and `mc-*` cards,
 * `access-request-model`, and the `keys-*` entries. The popover's text joins
 * the glossary's definitions of a governed action and a mediated connection.
 */
export function SecurityPage({ scopeOpen }: { scopeOpen: boolean }) {
  return (
    <div className="min-h-screen bg-background text-foreground">
      <SiteNav current="security" />
      <main>
        <Hero />

        <SiteSection
          id="controls"
          eyebrow="Controls"
          title="Agent controls"
          lead="Review how agent identities map to your access controls, how Oxagen handles connection credentials, and what each governed action records. Inspect the supported deployment and integration boundaries before granting authority."
          aside={<ScopePopover open={scopeOpen} />}
        >
          <div className="grid gap-4 md:grid-cols-2">
            {CONTROLS.map((control) => (
              <SiteCard key={control.title} {...control} />
            ))}
          </div>
        </SiteSection>

        <SiteSection
          id="request-model"
          eyebrow="Requests"
          title="The request model"
          lead="The usual model hands the agent a token with everything it might ever need and hopes it uses only some of it. Oxagen's model is a request. The agent holds its own identity and a mandate. When a task needs a system, a scope, or an action the mandate does not already cover, the agent asks for it at the moment of use."
          qualifier="For actions routed through Oxagen."
        >
          <RequestSteps className="max-w-[44rem]" />
        </SiteSection>
      </main>
      <SiteFooter />
    </div>
  );
}
