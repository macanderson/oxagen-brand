// The optional lead gate. It is off unless the Vercel project sets
// SDLC_LEAD_GATE=on. When it is on, a download needs a first name, a last
// name, and a work email, and the lead goes to the Oxagen lead endpoint
// (apps/api/src/routes/v1/cms.ts in the oxagen repo), which stores it and
// syncs it to Attio. intent "demo" records the lead without sending the
// ebook email that endpoint sends by default.

const LEADS_URL = "https://api.oxagen.sh/v1/cms/leads";
const EMAIL = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

export function gateOn() {
  return (process.env.SDLC_LEAD_GATE ?? "off").trim().toLowerCase() === "on";
}

/** @param {unknown} v */
const one = (v) => (Array.isArray(v) ? v[0] : v);

/** @param {unknown} v @param {number} max */
const field = (v, max) => {
  const s = one(v);
  return typeof s === "string" ? s.replace(/\s+/g, " ").trim().slice(0, max) : "";
};

/**
 * Read the lead fields from a form body.
 * @param {Record<string, unknown>} input
 * @returns {{ ok: true, bot: boolean, lead: { firstName: string, lastName: string, email: string } } | { ok: false }}
 */
export function readLead(input) {
  const firstName = field(input.firstName, 120);
  const lastName = field(input.lastName, 120);
  const email = field(input.email, 320).toLowerCase();
  // The hidden "website" field is a honeypot. People never fill it in.
  const bot = field(input.website, 200).length > 0;
  if (!firstName || !lastName || !EMAIL.test(email)) return { ok: false };
  return { ok: true, bot, lead: { firstName, lastName, email } };
}

/**
 * Send one lead. A failure is logged and returned, never thrown, so a slow
 * or broken lead endpoint does not block the download.
 * @param {{ firstName: string, lastName: string, email: string, company: string, format: string, pagePath?: string }} o
 */
export async function sendLead(o) {
  const url = process.env.SDLC_LEADS_URL || LEADS_URL;
  try {
    const res = await fetch(url, {
      method: "POST",
      headers: { "content-type": "application/json" },
      body: JSON.stringify({
        firstName: o.firstName,
        lastName: o.lastName,
        email: o.email,
        company: o.company === "Your company" ? undefined : o.company,
        intent: "demo",
        source: "sdlc-template",
        pagePath: o.pagePath?.slice(0, 1000),
        message: `Asked for the agent SDLC template as ${o.format}.`,
      }),
      signal: AbortSignal.timeout(5000),
    });
    if (!res.ok) console.error(`[sdlc] lead endpoint answered ${res.status}`);
    return res.ok;
  } catch (err) {
    console.error(`[sdlc] lead endpoint failed: ${err instanceof Error ? err.message : err}`);
    return false;
  }
}
