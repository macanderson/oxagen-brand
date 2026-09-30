// Render the template (lib/content.js) as a PDF with pdfkit. Geist, the house
// text face, is embedded from fonts/. Blanks are set in deep gold and
// underlined, which survives printing in black and white.

import { readFileSync } from "node:fs";
import PDFDocument from "pdfkit";
import { runs } from "./content.js";

const fontFile = (weight) =>
  readFileSync(new URL(`../fonts/geist-latin-${weight}.ttf`, import.meta.url));

const INK = "#09090B";
const BODY = "#27272A";
const MUTED = "#71717A";
const HAIRLINE = "#D4D4D8";
const HEAD_FILL = "#F4F4F5";
const BLANK = "#8A7223";

const MARGIN = 64;
const FOOTER_GAP = 28;

/**
 * Remove characters the embedded font cannot draw, so a name in another
 * script prints as what the font has instead of empty boxes.
 * @param {PDFKit.PDFDocument} pdf
 * @param {string} text
 */
function drawable(pdf, text) {
  const font = pdf._font?.font;
  if (!font?.hasGlyphForCodePoint) return text;
  let out = "";
  for (const ch of text) {
    const cp = ch.codePointAt(0);
    out += cp === 32 || font.hasGlyphForCodePoint(cp) ? ch : "";
  }
  return out.length === text.length ? out : out.replace(/ {2,}/g, " ");
}

/**
 * Write text with [[blanks]] at the cursor, wrapping inside `width`.
 * @param {PDFKit.PDFDocument} pdf
 * @param {string} text
 * @param {{ x?: number, y?: number, width: number, font?: string, size?: number, color?: string }} o
 */
function write(pdf, text, o) {
  const parts = runs(text);
  pdf.font(o.font ?? "body").fontSize(o.size ?? 10.5);
  parts.forEach((r, i) => {
    const last = i === parts.length - 1;
    const opts = {
      width: o.width,
      continued: !last,
      underline: r.blank,
      lineGap: 3,
    };
    pdf.fillColor(r.blank ? BLANK : (o.color ?? BODY));
    const t = drawable(pdf, r.text);
    if (i === 0 && o.x !== undefined) pdf.text(t, o.x, o.y ?? pdf.y, opts);
    else pdf.text(t, opts);
  });
}

/** @param {string} text */
const plain = (text) => runs(text).map((r) => r.text).join("");

/**
 * @param {PDFKit.PDFDocument} pdf
 * @param {number} needed points of vertical space
 */
function ensure(pdf, needed) {
  const bottom = pdf.page.height - pdf.page.margins.bottom;
  if (pdf.y + needed > bottom) pdf.addPage();
}

/**
 * @param {PDFKit.PDFDocument} pdf
 * @param {{ head: string[], rows: string[][], widths?: number[] }} block
 */
function table(pdf, block) {
  const left = pdf.page.margins.left;
  const full = pdf.page.width - left - pdf.page.margins.right;
  const n = block.head.length;
  const pct = block.widths ?? Array(n).fill(100 / n);
  const widths = pct.map((p) => (full * p) / 100);
  const pad = 6;

  const rowHeight = (cells, font) => {
    pdf.font(font).fontSize(9.5);
    return (
      Math.max(
        ...cells.map((t, i) =>
          pdf.heightOfString(plain(t) || " ", { width: widths[i] - pad * 2, lineGap: 3 }),
        ),
      ) +
      pad * 2
    );
  };

  const drawRow = (cells, isHead) => {
    const font = isHead ? "bold" : "body";
    const h = rowHeight(cells, font);
    ensure(pdf, h);
    const top = pdf.y;
    let x = left;
    cells.forEach((t, i) => {
      if (isHead) pdf.rect(x, top, widths[i], h).fill(HEAD_FILL);
      pdf.lineWidth(0.6).strokeColor(HAIRLINE).rect(x, top, widths[i], h).stroke();
      write(pdf, t || " ", {
        x: x + pad,
        y: top + pad,
        width: widths[i] - pad * 2,
        font,
        size: 9.5,
        color: isHead ? INK : BODY,
      });
      x += widths[i];
    });
    pdf.x = left;
    pdf.y = top + h;
  };

  // A table that fits on one page starts on a fresh page rather than split.
  const total =
    rowHeight(block.head, "bold") +
    block.rows.reduce((sum, row) => sum + rowHeight(row, "body"), 0);
  const usable = pdf.page.height - pdf.page.margins.top - pdf.page.margins.bottom;
  if (total < usable * 0.6) ensure(pdf, total);

  drawRow(block.head, true);
  for (const row of block.rows) drawRow(row, false);
  pdf.moveDown(0.8);
}

/**
 * @param {ReturnType<import("./content.js").template>} doc
 * @returns {Promise<Buffer>}
 */
export function renderPdf(doc) {
  const pdf = new PDFDocument({
    size: "LETTER",
    margins: { top: MARGIN, bottom: MARGIN + FOOTER_GAP, left: MARGIN, right: MARGIN },
    bufferPages: true,
    font: fontFile(400),
    info: { Title: doc.title, Subject: doc.subtitle, Creator: "Oxagen agent SDLC template" },
  });
  pdf.registerFont("body", fontFile(400));
  pdf.registerFont("medium", fontFile(500));
  pdf.registerFont("bold", fontFile(700));

  const chunks = [];
  pdf.on("data", (c) => chunks.push(c));
  const done = new Promise((resolve, reject) => {
    pdf.on("end", () => resolve(Buffer.concat(chunks)));
    pdf.on("error", reject);
  });

  const width = pdf.page.width - MARGIN * 2;
  const left = MARGIN;

  write(pdf, doc.title, { x: left, y: MARGIN, width, font: "bold", size: 28, color: INK });
  pdf.moveDown(0.4);
  write(pdf, doc.subtitle, { x: left, width, font: "body", size: 13, color: BODY });
  pdf.moveDown(0.5);
  write(pdf, doc.meta, { x: left, width, font: "body", size: 9, color: MUTED });
  pdf.moveDown(1.2);

  for (const block of doc.blocks) {
    switch (block.type) {
      case "h1":
      case "h2":
        ensure(pdf, 80);
        pdf.moveDown(0.6);
        write(pdf, block.text, { x: left, width, font: "bold", size: 17, color: INK });
        pdf.moveDown(0.4);
        break;
      case "h3":
        ensure(pdf, 60);
        pdf.moveDown(0.3);
        write(pdf, block.text, { x: left, width, font: "medium", size: 12.5, color: INK });
        pdf.moveDown(0.25);
        break;
      case "p":
      case "lead":
      case "note":
        ensure(pdf, 30);
        write(pdf, block.text, { x: left, width, color: BODY });
        pdf.moveDown(0.6);
        break;
      case "bullets":
      case "numbered":
        block.items.forEach((item, i) => {
          ensure(pdf, 20);
          const y = pdf.y;
          const mark = block.type === "numbered" ? `${i + 1}.` : "•";
          pdf.font("body").fontSize(10.5).fillColor(MUTED).text(mark, left + 4, y, { width: 18, lineBreak: false });
          write(pdf, item, { x: left + 22, y, width: width - 22, color: BODY });
          pdf.moveDown(0.3);
        });
        pdf.x = left;
        pdf.moveDown(0.4);
        break;
      case "table":
        table(pdf, block);
        break;
      case "pagebreak":
        pdf.addPage();
        break;
      default:
        break;
    }
  }

  // Footers. The bottom margin is lifted while each is drawn, or pdfkit would
  // treat the footer line as overflow and start a new page.
  const range = pdf.bufferedPageRange();
  for (let i = range.start; i < range.start + range.count; i++) {
    pdf.switchToPage(i);
    const saved = pdf.page.margins.bottom;
    pdf.page.margins.bottom = 0;
    pdf
      .font("body")
      .fontSize(8)
      .fillColor(MUTED)
      .text(
        `Made from the Oxagen agent SDLC template at sdlc.oxagen.sh. Page ${i + 1} of ${range.count}`,
        MARGIN,
        pdf.page.height - MARGIN,
        { width, lineBreak: false },
      );
    pdf.page.margins.bottom = saved;
  }

  pdf.end();
  return done;
}
