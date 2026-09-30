// GET /api/config tells the page whether the lead gate is on, so it can show
// the name and email fields. The server enforces the gate either way.

import { gateOn } from "../lib/lead.js";

/** @param {any} _req @param {any} res */
export default function handler(_req, res) {
  res.setHeader("Cache-Control", "no-store");
  return res.status(200).json({ gate: gateOn() });
}
