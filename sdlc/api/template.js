// GET or POST /api/template?company=<name>&format=docx|pdf|gdoc
//
// Returns the SDLC template for one company as a download. The page's form
// and the form in the oxagen.sh blog post both land here, and neither needs
// JavaScript. "gdoc" sends the reader to /google-docs, which downloads the
// Word file and shows how to open it in Google Docs.
//
// With the lead gate on (lib/lead.js), a request without a valid name and
// email goes back to the page's form with the company and format filled in.

import { cleanCompany, fileName, template } from "../lib/content.js";
import { renderDocx } from "../lib/docx.js";
import { gateOn, readLead, sendLead } from "../lib/lead.js";
import { renderPdf } from "../lib/pdf.js";

const TYPES = {
  docx: "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
  pdf: "application/pdf",
};

/** @param {unknown} v */
const one = (v) => (Array.isArray(v) ? v[0] : v);

/** @param {unknown} v */
function format(v) {
  const f = String(one(v) ?? "").toLowerCase();
  if (f === "pdf") return "pdf";
  if (f === "gdoc" || f === "google" || f === "google-docs") return "gdoc";
  return "docx";
}

/**
 * @param {import("http").IncomingMessage & { query: Record<string, unknown>, body?: unknown }} req
 * @param {import("http").ServerResponse & { status: (n: number) => any, send: (b: unknown) => any }} res
 */
export default async function handler(req, res) {
  if (!["GET", "HEAD", "POST"].includes(req.method ?? "")) {
    res.setHeader("Allow", "GET, POST");
    return res.status(405).send("Use GET or POST.");
  }
  const input =
    req.method === "POST" && req.body && typeof req.body === "object"
      ? /** @type {Record<string, unknown>} */ (req.body)
      : req.query;
  const company = cleanCompany(one(input.company));
  const fmt = format(input.format);
  const query = new URLSearchParams({ company, format: fmt });

  // pass=1 comes from /google-docs after the lead was sent. The gate is a
  // marketing gate, not access control, the same as the oxagen.sh ebook gate.
  if (gateOn() && one(input.pass) !== "1") {
    const read = readLead(input);
    if (!read.ok) {
      res.setHeader("Location", `/?${query}#template`);
      res.setHeader("Cache-Control", "no-store");
      return res.status(303).end();
    }
    if (!read.bot) {
      await sendLead({
        ...read.lead,
        company,
        format: fmt,
        pagePath: String(req.headers.referer ?? ""),
      });
    }
  }

  if (fmt === "gdoc") {
    // The Google Docs page downloads the Word file itself. With the gate on,
    // the lead has already been sent, so that download skips the gate.
    if (gateOn()) query.set("pass", "1");
    res.setHeader("Location", `/google-docs?${query}`);
    res.setHeader("Cache-Control", "no-store");
    return res.status(303).end();
  }

  const doc = template({ company });
  const body = fmt === "pdf" ? await renderPdf(doc) : await renderDocx(doc);
  res.setHeader("Content-Type", TYPES[fmt]);
  res.setHeader("Content-Disposition", `attachment; filename="${fileName(company, fmt)}"`);
  res.setHeader("Content-Length", String(body.length));
  res.setHeader("Cache-Control", "no-store");
  res.setHeader("X-Content-Type-Options", "nosniff");
  return res.status(200).send(req.method === "HEAD" ? "" : body);
}
