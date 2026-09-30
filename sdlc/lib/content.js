// The SDLC template, as data. Both renderers (lib/docx.js and lib/pdf.js)
// read this one list of blocks, so the Word file and the PDF always say the
// same thing. Text inside [[double brackets]] is a blank the reader fills in.
// Renderers draw it as a highlighted placeholder.

/** @typedef {{ type: "h1" | "h2" | "h3" | "p" | "lead" | "note", text: string }} TextBlock */
/** @typedef {{ type: "bullets" | "numbered", items: string[] }} ListBlock */
/** @typedef {{ type: "table", head: string[], rows: string[][], widths?: number[] }} TableBlock */
/** @typedef {TextBlock | ListBlock | TableBlock | { type: "pagebreak" }} Block */

const MAX_COMPANY = 80;

/**
 * Clean a company name typed into a form. Removes control characters and
 * extra spaces, and caps the length. An empty name becomes "Your company".
 * @param {unknown} raw
 */
export function cleanCompany(raw) {
  const text = typeof raw === "string" ? raw : "";
  const clean = text
    .replace(/[\u0000-\u001f\u007f<>]/g, " ")
    .replace(/\s+/g, " ")
    .trim()
    .slice(0, MAX_COMPANY)
    .trim();
  return clean || "Your company";
}

/**
 * A file name for the download: the company name in lowercase with hyphens.
 * @param {string} company
 * @param {"docx" | "pdf"} ext
 */
export function fileName(company, ext) {
  const slug = company
    .toLowerCase()
    .normalize("NFKD")
    .replace(/[̀-ͯ]/g, "")
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-+|-+$/g, "")
    .slice(0, 60);
  return `${slug || "your-company"}-agent-sdlc.${ext}`;
}

/** @param {Date} date */
export function longDate(date) {
  return date.toLocaleDateString("en-US", {
    year: "numeric",
    month: "long",
    day: "numeric",
    timeZone: "UTC",
  });
}

/**
 * Split text into plain runs and [[placeholder]] runs.
 * @param {string} text
 * @returns {Array<{ text: string, blank: boolean }>}
 */
export function runs(text) {
  const out = [];
  const re = /\[\[([^\]]+)\]\]/g;
  let last = 0;
  let m;
  while ((m = re.exec(text))) {
    if (m.index > last) out.push({ text: text.slice(last, m.index), blank: false });
    out.push({ text: `[${m[1]}]`, blank: true });
    last = m.index + m[0].length;
  }
  if (last < text.length) out.push({ text: text.slice(last), blank: false });
  return out;
}

/**
 * The whole template for one company.
 * @param {{ company: string, date?: Date }} o
 * @returns {{ title: string, subtitle: string, meta: string, blocks: Block[] }}
 */
export function template({ company, date = new Date() }) {
  const c = company;
  const today = longDate(date);
  return {
    title: `${c} agent SDLC`,
    subtitle: `How ${c} builds and ships software with agents, at every hour of the week.`,
    meta: `Version 1. Made on ${today} from the Oxagen agent SDLC template at sdlc.oxagen.cloud.`,
    blocks: [
      { type: "h2", text: "About this document" },
      {
        type: "p",
        text: `This document sets out how ${c} builds and ships software with agents. Agents do most of the work. People set the rules, make the calls only a person can make, and read the record.`,
      },
      {
        type: "table",
        head: ["Item", "Value"],
        widths: [30, 70],
        rows: [
          ["Owner", "[[Name and role]]"],
          ["Approved by", "[[Name and role]]"],
          ["Date", today],
          ["Next review", "[[Date, 90 days from now]]"],
          ["Applies to", "[[Repositories and teams]]"],
        ],
      },

      { type: "h2", text: "Reasons for the change" },
      {
        type: "p",
        text: "Our old process was made for people. Every change waited for a person to read it. Work stopped at night and on weekends.",
      },
      {
        type: "p",
        text: "Agents can work all 168 hours of a week. A 40-hour work week covers 40 of them. In this process, the work keeps moving at every hour, and people still own every change.",
      },

      { type: "h2", text: "Principles" },
      {
        type: "numbered",
        items: [
          "People own every change. Each agent run has a named operator.",
          "Each agent has its own identity. Agents do not share accounts or keys.",
          "Rules come first. People write the rules before the work starts.",
          "Checks read every change. People read the record, plus the requests a rule sends to them.",
          "One issue, one change. A small change is easy to check and easy to undo.",
          "Automatic checks (CI) are the only place code is built and tested.",
          "Every action a rule covers goes on the record.",
          "Work moves at every hour. People review on their own schedule.",
        ],
      },

      { type: "h2", text: "Roles" },
      {
        type: "table",
        head: ["Role", "Who", "Job"],
        widths: [20, 25, 55],
        rows: [
          ["Operator", "[[Name]]", "Owns the agents' runs. Reads the record each day. Answers the requests a rule sends to a person."],
          ["Agent", "[[Agent names and tools]]", "Writes, checks, and merges changes under the rules."],
          ["Review agent", "[[Tool]]", "Reads each change and rates each finding from P0 to P3."],
          ["Triage agent", "[[Tool]]", "Sets the priority, size, and area of each new issue."],
          ["Security", "[[Name]]", "Writes the access rules: which systems and data each agent may ask for."],
          ["Finance", "[[Name]]", "Writes the budget rules: what each agent and each run may spend."],
          ["Engineering", "[[Name]]", "Writes the equipment rules: the tools, skills, and checks each agent uses."],
          ["Maintainer", "[[Name]]", "Makes the calls only a person can make: product direction, new rules, and exceptions."],
        ],
      },

      { type: "h2", text: "The ten stages" },
      {
        type: "p",
        text: "Each change moves through ten stages. Agents run every stage. People come in at the points marked in the rules.",
      },
      { type: "h3", text: "1. Issue" },
      {
        type: "p",
        text: "Every change starts as an issue. The issue gives the problem, the files, how to check the work, and a list that says what done looks like. It also gives an estimate in agent minutes.",
      },
      {
        type: "bullets",
        items: [
          "Problem: [[What is wrong or missing]]",
          "Files: [[Paths]]",
          "How to check it: [[Steps or test names]]",
          "Done when: [[A checklist]]",
          "Estimate: [[Agent minutes]]",
        ],
      },
      { type: "h3", text: "2. Triage" },
      {
        type: "p",
        text: "A triage agent sets the priority (P0 to P4), the size, and the area. The person or agent who files the issue adds only the triage label.",
      },
      { type: "h3", text: "3. Claim" },
      {
        type: "p",
        text: "An agent claims an issue or a change before it writes. One change has one writer. A claim lasts [[90]] minutes, and the agent renews it while it works.",
      },
      { type: "h3", text: "4. Build" },
      {
        type: "p",
        text: "The agent makes a branch from the latest main. It makes the change, adds tests for the change, and opens a pull request that names the issue.",
      },
      { type: "h3", text: "5. Check" },
      {
        type: "p",
        text: "Automatic checks run on every push: build, lint, types, tests, and coverage. An agent reads a failed check as soon as it fails and pushes a fix. Nobody re-runs a check just to hope it passes.",
      },
      { type: "h3", text: "6. Review" },
      {
        type: "p",
        text: "Review agents read the change and rate each finding from P0 to P3. A P0 blocks the change. The pass rule below decides what gets fixed on this change. Every finding left over goes into one follow-up issue.",
      },
      {
        type: "table",
        head: ["Review pass", "Fix on this change"],
        widths: [30, 70],
        rows: [
          ["Pass 1", "P0, P1, and P2"],
          ["Pass 2", "P0 and P1"],
          ["Pass 3 and later", "P0 only"],
        ],
      },
      { type: "h3", text: "7. Merge" },
      {
        type: "p",
        text: "A change merges when every check passes, no P0 or P1 finding is open, and there is no conflict with main. [[An agent merges it / A person approves it]].",
      },
      { type: "h3", text: "8. Release" },
      {
        type: "p",
        text: "A merge to main deploys. A database change carries a label, and the checks apply it before the code that needs it goes live.",
      },
      { type: "h3", text: "9. Watch" },
      {
        type: "p",
        text: "When main breaks, a check opens a P0 issue. The fix goes straight to main. The check closes the issue when main is green again. The time between the two is our recovery time.",
      },
      { type: "h3", text: "10. Learn" },
      {
        type: "p",
        text: "Each run ends with a note on the issue: minutes planned, minutes spent, what shipped, and what the next agent should know.",
      },

      { type: "h2", text: "Rules" },
      {
        type: "p",
        text: "A rule answers each request an agent makes. It has three answers: allow, deny, or send to a person. The team that owns the system writes the rule.",
      },
      {
        type: "table",
        head: ["Request", "Owner", "Answer"],
        widths: [50, 20, 30],
        rows: [
          ["Merge a change with passing checks and no open P0 or P1", "Engineering", "Allow"],
          ["Push straight to main", "Engineering", "Deny, except a fix for a broken main"],
          ["Change a database schema", "Engineering", "Allow with the migration label"],
          ["Spend more than [[amount]] on one run", "Finance", "Send to a person"],
          ["Read customer data in production", "Security", "Send to a person"],
          ["Add a new tool or skill to an agent", "Engineering", "Send to a person"],
          ["[[Your request]]", "[[Owner]]", "[[Answer]]"],
          ["[[Your request]]", "[[Owner]]", "[[Answer]]"],
        ],
      },

      { type: "h2", text: "Checks" },
      {
        type: "p",
        text: "Checks do the reading a person used to do by hand. Each one runs on every push.",
      },
      {
        type: "table",
        head: ["Check", "Blocks a merge", "Our tool"],
        widths: [45, 20, 35],
        rows: [
          ["Build", "Yes", "[[Tool]]"],
          ["Lint", "Yes", "[[Tool]]"],
          ["Type check", "Yes", "[[Tool]]"],
          ["Unit tests", "Yes", "[[Tool]]"],
          ["Coverage floor of [[percent]]", "Yes", "[[Tool]]"],
          ["Browser tests for the key flows", "Yes", "[[Tool]]"],
          ["Security scan", "Yes", "[[Tool]]"],
          ["Database migration check", "Yes", "[[Tool]]"],
          ["[[Your check]]", "[[Yes or no]]", "[[Tool]]"],
        ],
      },

      { type: "h2", text: "Severity" },
      {
        type: "table",
        head: ["Level", "Meaning", "Example", "Blocks a merge"],
        widths: [12, 22, 40, 26],
        rows: [
          ["P0", "Broken or unsafe", "Data loss, a security hole, or a main branch that does not build", "Yes, at every pass"],
          ["P1", "Wrong result", "A feature does the wrong thing", "Yes, on passes 1 and 2"],
          ["P2", "Should fix", "A missing test or an unclear error message", "Fixed on pass 1, then carried to the follow-up issue"],
          ["P3", "Nice to have", "A name or a style choice", "No"],
        ],
      },

      { type: "h2", text: "Decisions for people" },
      { type: "p", text: "People make these calls:" },
      {
        type: "bullets",
        items: [
          "Product direction and what to build next",
          "New rules and changes to rules",
          "Requests a rule sends to a person",
          "Spend above the budget",
          "Work that needs a credential, a test rig, or real money",
        ],
      },
      { type: "p", text: "People do not have to:" },
      {
        type: "bullets",
        items: [
          "Read every line of every change",
          "Re-run checks",
          "Chase the status of a change",
          "Merge by hand when the checks and rules allow it",
        ],
      },

      { type: "h2", text: "The daily record" },
      { type: "p", text: "Each day at [[time]], the operator reads:" },
      {
        type: "bullets",
        items: [
          "What merged, and what each change cost",
          "What is waiting on a person",
          "What failed, and how long main was broken",
          "Agent minutes planned against agent minutes spent",
        ],
      },

      { type: "h2", text: "Scoreboard" },
      {
        type: "table",
        head: ["Measure", "How we count it", "Target", "Now"],
        widths: [28, 42, 15, 15],
        rows: [
          ["Changes merged per day", "Merged pull requests on main", "", ""],
          ["Merges outside work hours", "Share merged outside [[9 am to 6 pm]] on weekdays", "", ""],
          ["Issue to merge", "Median hours from issue opened to change merged", "", ""],
          ["Recovery time", "Median time from main broken to main green", "", ""],
          ["Agent minutes", "Minutes spent against minutes planned", "", ""],
          ["Cost per change", "Agent spend divided by changes merged", "", ""],
        ],
      },

      { type: "h2", text: "Rollout plan" },
      {
        type: "table",
        head: ["Week", "Steps", "Owner", "Done"],
        widths: [12, 58, 18, 12],
        rows: [
          ["1", "Pick one repository. Write the rules. Give each agent its own identity.", "[[Name]]", ""],
          ["2", "Move every check into CI. Make CI the only place code is built and tested.", "[[Name]]", ""],
          ["3", "Turn on review agents and the pass rule. Let agents merge changes that pass.", "[[Name]]", ""],
          ["4", "Read the record each day. Track the scoreboard. Change the rules that slow the work.", "[[Name]]", ""],
        ],
      },

      { type: "h2", text: "Oxagen's role" },
      {
        type: "p",
        text: "Oxagen is workforce management for autonomous agents. It gives each agent an identity and a mandate: its access, its budget and rules, and its tools and skills. For actions routed through Oxagen, a rule answers each request, and Oxagen keeps the record of what each agent did and what it cost. Learn more at oxagen.sh.",
      },

      { type: "h2", text: "Sign-off" },
      {
        type: "table",
        head: ["Name", "Role", "Date", "Signature"],
        widths: [30, 25, 20, 25],
        rows: [
          ["", "", "", ""],
          ["", "", "", ""],
          ["", "", "", ""],
        ],
      },
    ],
  };
}
