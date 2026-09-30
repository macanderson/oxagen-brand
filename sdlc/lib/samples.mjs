// Write a sample Word file and PDF for one company name, so a person can open
// them before a deploy: `npm run samples -- "Acme Robotics" /tmp/out`.

import { mkdirSync, writeFileSync } from "node:fs";
import { join } from "node:path";
import { cleanCompany, fileName, template } from "./content.js";
import { renderDocx } from "./docx.js";
import { renderPdf } from "./pdf.js";

const company = cleanCompany(process.argv[2] ?? "Acme Robotics");
const dir = process.argv[3] ?? "samples";
mkdirSync(dir, { recursive: true });

const doc = template({ company });
const docx = await renderDocx(doc);
const pdf = await renderPdf(doc);
writeFileSync(join(dir, fileName(company, "docx")), docx);
writeFileSync(join(dir, fileName(company, "pdf")), pdf);
console.log(`${fileName(company, "docx")} ${docx.length} bytes`);
console.log(`${fileName(company, "pdf")} ${pdf.length} bytes`);
