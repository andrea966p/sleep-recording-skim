// Lay out the blocks from html_blocks.py as a Word document.
//   NODE_PATH=$(npm root -g) node build_docx.js blocks.json IMG_DIR out.docx
// Run through build.sh, which does all pages in one go.
const fs = require("fs");
const path = require("path");
const {
  Document, Packer, Paragraph, TextRun, ImageRun, Table, TableRow, TableCell,
  WidthType, ShadingType, BorderStyle, AlignmentType, LevelFormat, HeadingLevel,
  Footer, PageNumber,
} = require("docx");

const [, , jsonPath, imgDir, outPath] = process.argv;
const blocks = JSON.parse(fs.readFileSync(jsonPath, "utf8"));
const title = (blocks.find((b) => b.t === "title") || {}).text || "";

const PAGE_W = 11906, MARGIN = 1134;                 // A4, 2 cm margins
const CONTENT_W = PAGE_W - 2 * MARGIN;               // 9638 DXA
const BODY = "Calibri", HEAD = "Georgia", MONO = "Consolas";
const MUTED = "56625C", RULE = "D6DCD8", NOTE_BG = "EEF3F1", HEAD_BG = "F0F2F1";

function runs(rs, base = {}) {
  return rs.map((r) => new TextRun({
    text: r.text,
    bold: r.b || base.bold,
    italics: r.i || base.italics,
    color: r.color || base.color,
    font: r.code ? MONO : base.font,
    size: r.code ? (base.size || 21) - 2 : base.size,
  }));
}

function pngSize(file) {
  const b = fs.readFileSync(file);
  return { w: b.readUInt32BE(16), h: b.readUInt32BE(20), data: b };
}

function table(b) {
  const ncol = Math.max(...b.rows.map((r) => r.cells.reduce((s, c) => s + c.colspan, 0)));
  // column weight: never narrower than its longest word, long prose gets half its length
  const wt = Array(ncol).fill(4);
  for (const r of b.rows) {
    let i = 0;
    for (const c of r.cells) {
      if (c.colspan === 1) {
        const text = c.runs.map((x) => x.text).join("").trim();
        const word = Math.max(...text.split(/\s+/).map((w) => w.length));
        wt[i] = Math.max(wt[i], word + 2, Math.min(text.length, 60) * 0.5);
      }
      i += c.colspan;
    }
  }
  const tot = wt.reduce((a, x) => a + x, 0);
  const widths = wt.map((x) => Math.floor((CONTENT_W * x) / tot));
  widths[0] += CONTENT_W - widths.reduce((a, x) => a + x, 0);
  const border = { style: BorderStyle.SINGLE, size: 4, color: RULE };
  const borders = { top: border, bottom: border, left: border, right: border };
  return new Table({
    width: { size: CONTENT_W, type: WidthType.DXA },
    columnWidths: widths,
    rows: b.rows.map((r) => {
      let i = 0;
      return new TableRow({
        tableHeader: r.head,
        children: r.cells.map((c) => {
          const w = widths.slice(i, i + c.colspan).reduce((a, x) => a + x, 0);
          i += c.colspan;
          return new TableCell({
            width: { size: w, type: WidthType.DXA },
            columnSpan: c.colspan,
            borders,
            shading: c.head ? { fill: HEAD_BG, type: ShadingType.CLEAR, color: "auto" } : undefined,
            margins: { top: 40, bottom: 40, left: 80, right: 80 },
            children: [new Paragraph({
              children: runs(c.runs, { size: 17, bold: c.head || undefined, color: c.head ? MUTED : undefined }),
            })],
          });
        }),
      });
    }),
  });
}

const out = [];
for (const b of blocks) {
  switch (b.t) {
    case "title":
      break;
    case "h1":
      out.push(new Paragraph({ heading: HeadingLevel.TITLE, children: runs(b.runs) }));
      break;
    case "h2":
      out.push(new Paragraph({ heading: HeadingLevel.HEADING_1, children: runs(b.runs) }));
      break;
    case "h3":
      out.push(new Paragraph({ heading: HeadingLevel.HEADING_2, children: runs(b.runs) }));
      break;
    case "kv":
      out.push(new Paragraph({ spacing: { after: 40 }, children: runs(b.runs) }));
      break;
    case "li":
      out.push(new Paragraph({
        numbering: { reference: "bullets", level: 0 },
        shading: b.style === "callout" ? { fill: NOTE_BG, type: ShadingType.CLEAR, color: "auto" } : undefined,
        spacing: { after: 80 }, children: runs(b.runs),
      }));
      break;
    case "ref":
      out.push(new Paragraph({
        numbering: { reference: "refs", level: 0 }, spacing: { after: 80 },
        children: runs(b.runs, { size: 18 }),
      }));
      break;
    case "table":
      out.push(table(b));
      out.push(new Paragraph({ spacing: { after: 60 }, children: [] }));
      break;
    case "img": {
      const f = path.join(imgDir, b.src);
      if (!fs.existsSync(f)) { console.error(`missing image ${f}`); break; }
      const { w, h, data } = pngSize(f);
      const wpx = 640;                                  // ~6.67 in at 96 dpi = content width
      out.push(new Paragraph({
        alignment: AlignmentType.CENTER, spacing: { before: 120 },
        children: [new ImageRun({ type: "png", data, transformation: { width: wpx, height: Math.round((wpx * h) / w) },
                                  altText: { title: b.alt, description: b.alt, name: b.src } })],
      }));
      break;
    }
    case "caption":
      out.push(new Paragraph({ spacing: { after: 200 }, children: runs(b.runs, { size: 18, color: MUTED }) }));
      break;
    default: {                                          // p and its styles
      const st = {
        eyebrow: { size: 16, color: MUTED, font: MONO },
        lede: { size: 23, color: MUTED },
        note: { size: 18, color: MUTED },
      }[b.style] || {};
      out.push(new Paragraph({
        shading: b.style === "callout" ? { fill: NOTE_BG, type: ShadingType.CLEAR, color: "auto" } : undefined,
        spacing: { after: 120 }, children: runs(b.runs, st),
      }));
    }
  }
}

const doc = new Document({
  title, creator: "HLB SOD1 nanotag analysis",
  styles: {
    default: { document: { run: { font: BODY, size: 21 } } },
    paragraphStyles: [
      { id: "Title", name: "Title", basedOn: "Normal", next: "Normal",
        run: { font: HEAD, size: 40, bold: true }, paragraph: { spacing: { after: 160 } } },
      { id: "Heading1", name: "Heading 1", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { font: HEAD, size: 28, bold: true },
        paragraph: { spacing: { before: 320, after: 120 }, outlineLevel: 0,
                     border: { top: { style: BorderStyle.SINGLE, size: 4, color: RULE, space: 6 } } } },
      { id: "Heading2", name: "Heading 2", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { font: HEAD, size: 23, bold: true }, paragraph: { spacing: { before: 200, after: 80 }, outlineLevel: 1 } },
    ],
  },
  numbering: { config: [
    { reference: "bullets", levels: [{ level: 0, format: LevelFormat.BULLET, text: "•", alignment: AlignmentType.LEFT,
      style: { paragraph: { indent: { left: 360, hanging: 240 } } } }] },
    { reference: "refs", levels: [{ level: 0, format: LevelFormat.DECIMAL, text: "%1.", alignment: AlignmentType.LEFT,
      style: { paragraph: { indent: { left: 400, hanging: 400 } } } }] },
  ] },
  sections: [{
    properties: { page: { size: { width: PAGE_W, height: 16838 },
                          margin: { top: MARGIN, bottom: MARGIN, left: MARGIN, right: MARGIN } } },
    footers: { default: new Footer({ children: [new Paragraph({ alignment: AlignmentType.RIGHT,
      children: [new TextRun({ text: `${title} · `, size: 16, color: MUTED }),
                 new TextRun({ children: [PageNumber.CURRENT], size: 16, color: MUTED })] })] }) },
    children: out,
  }],
});

Packer.toBuffer(doc).then((buf) => { fs.writeFileSync(outPath, buf); console.log(`wrote ${outPath}`); });
