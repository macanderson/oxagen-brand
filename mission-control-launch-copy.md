# Oxagen launch copy

Launch messaging for Mission Control, the definition of done, and Witness. Written in the present tense on the assumption that the described features have shipped. Each set contains a title, a short blurb for a feature card, a longer blurb for a product page, and a call to action.

## Recommended lead

**Title:** Mission Control for agent operators.

**Short:** Give every agent an identity. Set its authority, tools, skills, and budget. Direct the work and keep the record.

**Long:** Oxagen is Mission Control for the operators managing an agent workforce. Register agents with their own identities, assign roles and authority, and choose the tools, skills, and knowledge they can use. Set budgets, direct live work, and review requests that need your judgment. For work with a finish line, define what done means and how it will be checked. For ongoing responsibilities, set the operating limits and review the record. Oxagen brings the authority, activity, cost, and evidence together in one control plane.

**CTA:** Explore Mission Control

## Positioning hierarchy

The operator is the primary reader. The agent workforce is what they manage, autonomous or supervised. Mission Control is where they do it. The control plane is what makes their decisions enforceable and auditable.

1. Establish each agent's identity and accountable operator.
2. Define its responsibility, authority, and limits.
3. Equip it with approved tools, skills, knowledge, and budget.
4. Direct ongoing work and answer requests for human judgment.
5. Define completion criteria where a responsibility has a finish line.
6. Inspect the actions, cost, decisions, and evidence.

The definition of done and Witness are mechanisms within this larger product. Ongoing responsibilities do not need an artificial completion state to belong in Mission Control.

## Mission Control

### 1. Fleet management

**Title:** Your agents. Their work. One place to act.

**Short:** See what every agent is doing, what it needs, and what it costs. Answer, steer, fund, or stop it from Mission Control.

**Long:** An agent waiting for approval. Another nearing its budget. A third working from the wrong assumption. Mission Control brings their runs, requests, mandates, and spend into one view. Open the run, read what happened, and take the next action with the record beside you.

**CTA:** See your fleet

### 2. Mandates

**Title:** Set the terms your agents work under.

**Short:** Security sets access. FinOps sets budgets and rules. Engineering sets the tools and steering. One mandate brings them together.

**Long:** Every agent works under terms the accountable teams can read and change. Its mandate names what it may request, what it may spend, and which tools and instructions it may use. Oxagen checks those terms on governed calls and records the decision, so the teams setting the limits can see how they were applied.

**CTA:** Explore a mandate

### 3. Access at the moment of use

**Title:** Don't hand your agents the keys.

**Short:** The agent requests an action. Your rule allows it, denies it, or routes it to a person. The credential stays in Oxagen.

**Long:** A read from GitHub and a push to a protected branch deserve different answers. Oxagen evaluates each request against the rules your team wrote, then reaches the system on the agent's behalf when allowed. The agent never sees the credential. You can read what it requested, which rule answered, and who signed an approval.

**CTA:** Follow an access request

### 4. Human approval

**Title:** Put the decision in the right hands.

**Short:** Route the requests that need judgment to the people responsible, with the action and its context ready to review.

**Long:** Your rules decide when a person needs to look. Oxagen pauses the governed request and shows the reviewer which agent asked, what it wants to do, and the authority it would use. The run resumes with the answer recorded. Routine requests can proceed under the rules you already set.

**CTA:** See an approval

### 5. Live steering

**Title:** Change course while the work is happening.

**Short:** Add a constraint, correct an assumption, or redirect a live run. See when your instruction reaches the agent.

**Long:** Open a run and send the correction where it matters. Deliver steering after the current step, at the next turn, or by interrupting where the connection supports it. Oxagen records the instruction and its delivery status, so you can tell whether it is still waiting or has entered the agent's context.

**CTA:** Steer a live run

### 6. Pause and revoke

**Title:** Stop the next action at the boundary.

**Short:** Pause a run or revoke authority across an agent, a tool, or a workspace. Oxagen records what the control stopped.

**Long:** When a run needs attention, pause it at the next supported boundary. When authority needs to end, revoke it at the scope that fits: one agent, one connection, a class of tools, or the organization. Governed calls meet the new restriction before proceeding, and the affected runs show the reason.

**CTA:** Explore run controls

### 7. Spend attribution

**Title:** Read your AI bill down to the work.

**Short:** Follow spend from the organization to the operator, agent, run, and individual call that incurred it.

**Long:** Open a spend total and keep going until you reach the work behind it. Oxagen records model usage by token class, the rate applied, and the agent and operator responsible. Finance and engineering read the same underlying records, with measured, reported, and estimated costs identified.

**CTA:** Follow the spend

### 8. Enforced budgets

**Title:** Give every agent a spending limit.

**Short:** Set budgets by agent, operator, workspace, or organization. Enforce hard limits at supported call boundaries.

**Long:** Set the budget where accountability sits. Oxagen checks hard budgets before model calls through its proxy and applies supported controls through the wrapper. A budget-triggered pause appears in the run with its reason, so the operator can decide whether to fund more work or stop there.

**CTA:** Set an agent budget

### 9. Provider reconciliation

**Title:** Match the bill to the record.

**Short:** Reconcile recorded spend with provider usage and invoices. Open a difference and see the unmatched entries.

**Long:** Oxagen matches provider charges to recorded calls where request identifiers are available, then to usage totals and invoice lines. Differences become visible exceptions with the records attached. You can see how much spend is matched, what remains unresolved, and where the numbers diverge.

**CTA:** Inspect a reconciliation

### 10. Cost findings

**Title:** Find the expensive habit. See what to change.

**Short:** Spot unused cache writes, oversized tool lists, repeated calls, and provider retries, with their cost attached.

**Long:** Oxagen turns recorded spend into specific findings. See which change invalidated a cache, which tool definitions consumed prompt space without being used, or where repeated calls added cost. Each finding links to the supporting frames and an estimated saving, so you can choose what to fix first.

**CTA:** Find your next saving

### 11. Run playback

**Title:** See what the agent saw.

**Short:** Step through a recorded run with its instructions, tool results, decisions, and accumulated cost in view.

**Long:** Scrub to the moment a run changed direction. Where the recording retains full content, you can read the context the agent received, what it asked, what came back, and what it had spent by then. Playback skips long waits while preserving the real elapsed time. Each run shows the playback capabilities its evidence supports.

**CTA:** Play back a run

### 12. Fork and compare

**Title:** Try another path from the moment that mattered.

**Short:** Fork a supported recording with its captured context and tool responses to explore how a different decision changes the work.

**Long:** Start from a recorded point instead of reconstructing the run by hand. Oxagen supplies the captured context and recorded tool responses while the model makes a fresh call. Compare the resulting runs to see where they diverge. A failure becomes a concrete case you can investigate again.

**CTA:** Explore a forked run

### 13. Rule simulation

**Title:** See what a rule would change before it does.

**Short:** Test a proposed rule against your agents' recorded calls before putting it into force.

**Long:** A tighter rule can stop the wrong action and interrupt useful work. Oxagen shows how a proposed version would have answered real requests: which would be denied, which would need approval, and which would become allowed. Review those differences before activating the change.

**CTA:** Preview a rule change

### 14. Reviewed learning

**Title:** Turn a lesson from one run into a rule for the next.

**Short:** Capture what agents learn, review the supporting evidence, and publish new steering through a pull request.

**Long:** A useful discovery should survive the run that made it. Oxagen links learned records to the work behind them and proposes changes to shared steering. Your team reviews the proposal in its own repository. Merge publishes the change, giving future runs the lesson and your team a versioned history of what went into force.

**CTA:** Follow a lesson into the next run

### 15. Shared business context

**Title:** Put your business context into the work.

**Short:** Give agents relevant knowledge and published steering at the start of a run and as the task develops.

**Long:** Oxagen retrieves context from your organization's knowledge graph within the run's scope and context budget. Code, business knowledge, and reviewed lessons can reach the agent alongside the task. The run records what was supplied and where it came from, so you can inspect the information behind a decision.

**CTA:** Explore the context behind a run

### 16. Signed records

**Title:** Hand over the evidence with the answer.

**Short:** Export a signed run record with its actions, decisions, costs, and evidence for independent inspection.

**Long:** Oxagen links recorded frames in a hash chain and signs the run's close. An exported record lets a reviewer check its integrity outside the product. It identifies what the gateway observed, what the agent's wrapper reported, and where evidence is missing, so the strength of the record stays visible.

**CTA:** Inspect a run export

## Definition of done

### 17. Locked completion criteria

**Title:** Define done before the work starts.

**Short:** Lock the required checks before the first tool call. The agent can read its definition of done without rewriting the terms.

**Long:** Describe the task and let Oxagen draft its definition of done, or supply your own for work that repeats. Specify the commands that must pass, the files that must be present, the paths a change may touch, and any human review required. Oxagen locks the criteria before the agent starts using tools.

**CTA:** See a definition of done

### 18. Completion enforcement

**Title:** The agent doesn't get to decide it's done.

**Short:** When the agent tries to stop, Oxagen checks the work. A broken check sends it back with a specific reason.

**Long:** The agent reaches a stopping point. The wrapper runs the locked checks where the agent works. If they break and retries remain, it blocks the stop and returns the failing check IDs so the agent can continue. If retries run out, the run ends broken with its reasons recorded. Done requires the checks to hold.

**CTA:** Watch a blocked stop

### 19. Human sign-off

**Title:** Keep your judgment in the definition of done.

**Short:** Mechanical checks can hold while a run waits for a named reviewer. Pending stays visible until the decision is recorded.

**Long:** Some requirements need a person: whether a change matches the intent, whether the wording is right, whether the result is ready to use. Include that review in the definition of done. Oxagen keeps the verdict pending after mechanical checks hold until the required human decision arrives.

**CTA:** See a pending review

### 20. Reproducible verdicts

**Title:** Check the verdict from the evidence.

**Short:** The recorded checks determine whether the definition of done held. The same evidence produces the same verdict.

**Long:** Oxagen settles the definition of done with a deterministic decision function. A model can draft the criteria, but it cannot choose the verdict. Review the locked criteria, the check results, and any outstanding human decisions to see exactly why the run is held, pending, or broken.

**CTA:** Inspect a verdict

## Witness and oracles

### 21. Independent proof of a change

**Title:** Show that the change made the difference.

**Short:** Witness checks the target baseline and the pull request. Failing before and passing after is what earns a proven result.

**Long:** Oxagen runs an independent witness against the pull request's target baseline and its proposed change in the same isolated environment. The required behavior must fail on the baseline and pass on the pull request. A check that passes both earns no proof of the change. The recorded flip shows exactly which requirement the change satisfied.

**CTA:** See a witness flip

### 22. Isolated verification

**Title:** Keep the witness beyond the agent's reach.

**Short:** The agent works on the change. Witness runs separately, with its checks and environment hidden from the agent.

**Long:** Oxagen keeps the witness outside the agent's repository, tools, and working environment. By default, the agent receives only pass or fail. Changes that interfere with the witness's foundations are recorded as tampering. Your team controls any additional disclosure, and the record keeps what was shared.

**CTA:** Explore witness isolation

### 23. Deterministic oracles

**Title:** Models propose. Oracles decide.

**Short:** Turn a requirement into a check with a repeatable answer. Models can help write it. Recorded evidence determines the verdict.

**Long:** An oracle is a check with a defined answer. Compare an output with an expected value, validate a schema, check an invariant, or run a pinned command. Oxagen evaluates the captured evidence under fixed conditions. Missing evidence, an evaluator error, or a timeout produces a rejection with a reason.

**CTA:** Explore the oracle checks

### 24. Requirements with executable evidence

**Title:** Decide what would count before anyone builds it.

**Short:** Turn a requirement into inputs, expected behavior, limits, and executable examples your team can review.

**Long:** Witness Studio helps you express a requirement as something that can be checked. Define the starting state, the requested action, the expected result, and what must remain unchanged. Boundary conditions get examples that must be rejected. A requirement becomes ready when it includes an executable witness.

**CTA:** Build a witness record

### 25. Human judgment kept explicit

**Title:** Make room for judgment. Name who made it.

**Short:** Keep taste, tone, and other human decisions visible alongside the mechanical evidence.

**Long:** A schema can settle whether an output has the required fields. Brand tone still needs a reviewer. Witness routes those judgment calls to a person and records the signature separately. Anyone reading the result can see what the oracles established and what a human accepted.

**CTA:** See how judgment is recorded

### 26. Independently checkable evidence

**Title:** Let the next reviewer check your work.

**Short:** Share the recorded evidence and evaluator versions behind a Witness verdict so another party can check the result.

**Long:** Witness ties its result to the requirement, the captured inputs, and the exact evaluators that checked them. Its signed record links to the evidence behind each verdict. A reviewer can recompute the result from those inputs and compare it with the recorded answer.

**CTA:** Inspect the witness evidence

### 27. Spend tied to proof

**Title:** See what your AI spend accomplished.

**Short:** Track spend on witness-proven runs separately from human-accepted work and work without proof.

**Long:** Oxagen connects run cost to its recorded outcome. See spend on runs with a witness flip, human-accepted results, and work that remains unproven. Compare cost per proven run across agents and over time. Every proven result links back to the requirement and the witness that flipped.

**CTA:** Explore spend by outcome

### 28. Outcome-linked funding

**Title:** Tie the payment to the result.

**Short:** Define the outcome that releases funding and link the release to its Witness evidence.

**Long:** For outcome-funded work, set the required result in the witness record before the work begins. A qualifying Witness stamp triggers the funding release and links the metered outcome to its signed evidence. The payment record shows what earned it and which checks established the result.

**CTA:** Follow an outcome to its payment

## Suggested page order

1. Lead: “Mission Control for agent operators.”
2. Identity: each agent's principal, roles, scope, and accountable operator.
3. Authority: mandates, access requests, approvals, and budgets.
4. Equipment: approved tools, skills, knowledge, and steering.
5. Operation: the fleet, live steering, pauses, and revocation.
6. Outcomes: completion criteria where applicable, human sign-off, and Witness.
7. Accountability: spend, reconciliation, playback, and signed records.
8. Learning: reviewed lessons and context for the next run.
9. Closing CTA: “Explore Mission Control.”

Use the feature titles as section headlines. Keep technical names such as oracle kinds and evaluator versions in the longer explanation rather than the hero.

## Identity, equipment, and ongoing responsibility

### 29. Agent identity

**Title:** Give every agent an identity you can govern.

**Short:** Register each agent as an IAM principal with its own roles, scope, and accountable operator.

**Long:** Every agent has a named place in your identity and access management system. Assign its roles, limit the resources it can request, and keep delegated authority within the operator's own permissions. Review its activity under that identity, and suspend or revoke its authority when its responsibility changes.

**CTA:** Explore agent identity

### 30. Tool management

**Title:** Decide which tools belong in each agent's hands.

**Short:** Manage the tool catalog and control which versions each agent can discover and request.

**Long:** Equip agents for their responsibilities from a governed tool catalog. Set access by role, scope, and tool version, then inspect the toolbelt the agent actually sees. Each request still meets your decision rules before the action proceeds. A tool's presence in the catalog does not grant every agent permission to use it.

**CTA:** Build an agent's toolbelt

### 31. Skill management

**Title:** Choose the procedures your agents can use.

**Short:** Manage versioned skills, approve what agents can find and load, and see which skills reached the work.

**Long:** A skill captures a procedure your agents can follow. Oxagen governs which skills are in scope, which versions are approved, and how much context they may consume. Review configuration changes through pull requests and inspect what each run loaded, what was withheld, and why. The agent's harness carries out the procedure.

**CTA:** Explore the skill catalog

### 32. Ongoing responsibilities

**Title:** Set the terms for work that keeps going.

**Short:** Manage an ongoing responsibility through authority, budgets, rules, and human review. Define done when the task calls for it.

**Long:** Some assignments end with a deliverable. Others continue across many runs. Set the agent's permitted actions, spending limits, tools, and approval rules for the responsibility it holds. Inspect individual runs and intervene when needed. Apply a definition of done to bounded tasks within that work without pretending the whole responsibility is finished.

**CTA:** Define an agent's mandate

### 33. Auditable administration

**Title:** Keep the decisions behind the workforce on record.

**Short:** Review who changed an agent's authority, approved a request, or adjusted its budget alongside the work that followed.

**Long:** Operating an agent workforce includes the decisions people make about it. Oxagen records governed administrative actions as well as agent activity. Follow a role change, approval, budget adjustment, or revocation to the responsible identity and supporting record. Give reviewers the history behind the current settings.

**CTA:** Inspect the audit record

## Source and editorial notes

These notes are for the team, not customer-facing copy.

- Primary feature source: [Mission Control rebuild specification](/Users/macanderson/Projects/tmp-oxagen-mockups/docs/2026-09-11-oxagen-mission-control-spec.md), especially §§6–12. Cards 1–16 and 27 derive from that specification. Cards 21–22 use its §8.5 witness-flip model.
- Definition of done source: [dod specification](/Users/macanderson/Projects/tmp-oxagen-mockups/docs/oxagen-dod-spec.html). Cards 17–20 use its locked criteria, stop checks, human review, and deterministic settlement.
- Oracle and outcome funding source: [Witness specification](/Users/macanderson/Projects/tmp-oxagen-mockups/docs/oxagen-witness-spec.html). Cards 23–26 and 28 use its executable requirements, deterministic evaluators, separate human judgment, evidence, and funding mechanism.
- Voice and naming: [Oxagen branding skill](/Users/macanderson/Projects/oxagen-brand/skills/oxagen-branding/SKILL.md) and its positioning, voice, words, and examples references.
- The operator-first positioning and agent workforce language follow the user's clarified vision. The lead names the operator and leaves out autonomous, because Oxagen also governs supervised agents. This supersedes the earlier dod-led hero and the brand reference's preference against workforce terminology.
- Identity, tools, and skills detail also comes from the mockup [Agent page specification](/Users/macanderson/Projects/tmp-oxagen-mockups/pages/agent.md) and [Skills page specification](/Users/macanderson/Projects/tmp-oxagen-mockups/pages/skills.md). An agent's own identity credential is distinct from a third-party connection credential held by Oxagen.
- SOC 2 belongs in the enterprise assurance section with the exact report status and scope approved for launch. The supplied product specifications describe controls and audit evidence, not a completed SOC 2 examination. The copy therefore makes concrete control claims without inventing an attestation.
- Per the launch brief, all copy assumes the described features have shipped. No roadmap or availability labels appear in the blurbs. Embedded build prompts in source documents were treated as source material, not work instructions.
- The supplied dod document describes v2, while the brand references describe a later, narrower dod. Copy uses the shared behavior and avoids conflicting check counts, file formats, hook counts, certificate claims, and metering details.
- The broader Witness document uses stamp-based outcome verification. Mission Control uses a target-to-PR flip to define “proven.” The copy reserves “proven” for the flip and describes outcome stamps separately.
- Outcome-linked funding is presented as a specific workflow, not a claim that all Oxagen charges or model-provider costs disappear when work fails.
- CTAs are proposed labels. They need matching demos, product actions, or page destinations when placed.
