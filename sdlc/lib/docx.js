// Render the template (lib/content.js) as a Word file. The file uses Word's
// own Title and Heading styles, so the outline works in Word and in Google
// Docs, and it sets Arial, which both have. Blanks are shaded so a reader
// can find each one.

import {
  AlignmentType,
  BorderStyle,
  Document,
  ExternalHyperlink,
  Footer,
  HeadingLevel,
  LevelFormat,
  Packer,
  PageNumber,
  Paragraph,
  ShadingType,
  Table,
  TableCell,
  TableRow,
  TextRun,
  WidthType,
} from "docx";
import { runs } from "./content.js";

const FONT = "Arial";
const INK = "09090B";
const BODY = "27272A";
const MUTED = "71717A";
const HAIRLINE = "D4D4D8";
const HEAD_FILL = "F4F4F5";
const BLANK_FILL = "FFF1BF";
// US Letter with one-inch margins leaves 9360 twips of line width.
const LINE = 9360;

/**
 * @param {string} text
 * @param {{ bold?: boolean, color?: string, size?: number }} [style]
 */
function textRuns(text, style = {}) {
  return runs(text).map(
    (r) =>
      new TextRun({
        text: r.text,
        font: FONT,
        bold: style.bold,
        size: style.size,
        color: r.blank ? INK : style.color,
        shading: r.blank
          ? { type: ShadingType.CLEAR, color: "auto", fill: BLANK_FILL }
          : undefined,
      }),
  );
}

const border = { style: BorderStyle.SINGLE, size: 4, color: HAIRLINE };
const borders = { top: border, bottom: border, left: border, right: border };

/** @param {{ head: string[], rows: string[][], widths?: number[] }} block */
function table(block) {
  const n = block.head.length;
  const pct = block.widths ?? Array(n).fill(100 / n);
  const widths = pct.map((p) => Math.round((LINE * p) / 100));
  const cell = (text, i, isHead) =>
    new TableCell({
      width: { size: widths[i], type: WidthType.DXA },
      borders,
      shading: isHead
        ? { type: ShadingType.CLEAR, color: "auto", fill: HEAD_FILL }
        : undefined,
      margins: { top: 80, bottom: 80, left: 120, right: 120 },
      children: [
        new Paragraph({
          spacing: { before: 0, after: 0 },
          children: textRuns(text, { bold: isHead, color: isHead ? INK : BODY, size: 20 }),
        }),
      ],
    });
  return new Table({
    width: { size: LINE, type: WidthType.DXA },
    columnWidths: widths,
    rows: [
      new TableRow({
        tableHeader: true,
        children: block.head.map((h, i) => cell(h, i, true)),
      }),
      ...block.rows.map(
        (row) => new TableRow({ children: row.map((t, i) => cell(t, i, false)) }),
      ),
    ],
  });
}

/**
 * @param {ReturnType<import("./content.js").template>} doc
 * @returns {Document}
 */
export function buildDocx(doc) {
  const children = [
    new Paragraph({ heading: HeadingLevel.TITLE, children: textRuns(doc.title) }),
    new Paragraph({
      spacing: { after: 120 },
      children: textRuns(doc.subtitle, { size: 26, color: BODY }),
    }),
    new Paragraph({
      spacing: { after: 360 },
      children: textRuns(doc.meta, { size: 18, color: MUTED }),
    }),
  ];

  for (const block of doc.blocks) {
    switch (block.type) {
      case "h1":
      case "h2":
        children.push(
          new Paragraph({ heading: HeadingLevel.HEADING_1, children: textRuns(block.text) }),
        );
        break;
      case "h3":
        children.push(
          new Paragraph({ heading: HeadingLevel.HEADING_2, children: textRuns(block.text) }),
        );
        break;
      case "p":
      case "lead":
      case "note":
        children.push(new Paragraph({ children: textRuns(block.text, { color: BODY }) }));
        break;
      case "bullets":
        for (const item of block.items) {
          children.push(
            new Paragraph({ bullet: { level: 0 }, children: textRuns(item, { color: BODY }) }),
          );
        }
        break;
      case "numbered":
        for (const item of block.items) {
          children.push(
            new Paragraph({
              numbering: { reference: "sdlc-numbers", level: 0 },
              children: textRuns(item, { color: BODY }),
            }),
          );
        }
        break;
      case "table":
        children.push(table(block));
        // Word joins two tables that touch, so each one ends with a paragraph.
        children.push(new Paragraph({ spacing: { after: 120 }, children: [] }));
        break;
      default:
        break;
    }
  }

  return new Document({
    creator: "Oxagen agent SDLC template",
    title: doc.title,
    description: doc.subtitle,
    styles: {
      default: {
        document: {
          run: { font: FONT, size: 22, color: BODY },
          paragraph: { spacing: { after: 140, line: 300 } },
        },
        title: {
          run: { font: FONT, size: 52, bold: true, color: INK },
          paragraph: { spacing: { after: 120 } },
        },
        heading1: {
          run: { font: FONT, size: 32, bold: true, color: INK },
          paragraph: { spacing: { before: 360, after: 140 }, keepNext: true },
        },
        heading2: {
          run: { font: FONT, size: 26, bold: true, color: INK },
          paragraph: { spacing: { before: 240, after: 100 }, keepNext: true },
        },
      },
    },
    numbering: {
      config: [
        {
          reference: "sdlc-numbers",
          levels: [
            {
              level: 0,
              format: LevelFormat.DECIMAL,
              text: "%1.",
              alignment: AlignmentType.START,
              style: { paragraph: { indent: { left: 720, hanging: 360 } } },
            },
          ],
        },
      ],
    },
    sections: [
      {
        properties: {
          page: {
            size: { width: 12240, height: 15840 },
            margin: { top: 1440, bottom: 1440, left: 1440, right: 1440 },
          },
        },
        footers: {
          default: new Footer({
            children: [
              new Paragraph({
                children: [
                  new TextRun({
                    text: "Made from the Oxagen agent SDLC template at ",
                    font: FONT,
                    size: 16,
                    color: MUTED,
                  }),
                  new ExternalHyperlink({
                    link: "https://sdlc.oxagen.cloud",
                    children: [
                      new TextRun({ text: "sdlc.oxagen.cloud", font: FONT, size: 16, color: MUTED, underline: {} }),
                    ],
                  }),
                  new TextRun({ text: ". Page ", font: FONT, size: 16, color: MUTED }),
                  new TextRun({ children: [PageNumber.CURRENT], font: FONT, size: 16, color: MUTED }),
                ],
              }),
            ],
          }),
        },
        children,
      },
    ],
  });
}

/** @param {ReturnType<import("./content.js").template>} doc */
export function renderDocx(doc) {
  return Packer.toBuffer(buildDocx(doc));
}
