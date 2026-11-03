// Build the HLB report .docx from the vault markdown draft.
// Plain black text: title, headings, bold/italic, lists, a few tables, figures with captions.
// Handles only the markdown subset the draft uses. Vault links become plain text; "Details: [[...]]" lines are dropped.
// Usage: NODE_PATH=<dir with node_modules/docx> node build_docx.js <draft.md> <out.docx>
const fs = require("fs");
const path = require("path");
const d = require("docx");

const [, , src, out] = process.argv;
const ATT = path.join(path.dirname(src), "..", "..", "_attachments");
const FONT = "Arial";

let md = fs.readFileSync(src, "utf8").replace(/^---\n[\s\S]*?\n---\n/, "");
md = md.replace(/⬜/g, "[pending]");

const linkText = (s) => s.replace(/\[\[([^\]|]+)\\?\|([^\]]+)\]\]/g, "$2").replace(/\[\[([^\]]+)\]\]/g, "$1");

function runs(text, base = {}) {
  // **bold**, *italic*, `code` -> runs
  const parts = linkText(text).split(/(\*\*[^*]+\*\*|\*[^*]+\*|`[^`]+`)/);
  return parts.filter(Boolean).map((p) => {
    if (p.startsWith("**")) return new d.TextRun({ ...base, text: p.slice(2, -2), bold: true });
    if (p.startsWith("*")) return new d.TextRun({ ...base, text: p.slice(1, -1), italics: true });
    if (p.startsWith("`")) return new d.TextRun({ ...base, text: p.slice(1, -1) });
    return new d.TextRun({ ...base, text: p });
  });
}

function pngSize(file) {
  const b = fs.readFileSync(file);
  return [b.readUInt32BE(16), b.readUInt32BE(20)];
}

function image(name) {
  const file = path.join(ATT, name);
  const [w, h] = pngSize(file);
  const W = 600; // px at 96 dpi, about 15.9 cm
  return new d.Paragraph({
    alignment: d.AlignmentType.CENTER,
    spacing: { before: 120, after: 60 },
    keepNext: true,
    children: [new d.ImageRun({ type: "png", data: fs.readFileSync(file), transformation: { width: W, height: Math.round((W * h) / w) } })],
  });
}

const border = { style: d.BorderStyle.SINGLE, size: 4, color: "000000" };
function table(rows) {
  const cells = rows.filter((r) => !/^\|\s*-/.test(r)).map((r) => r.trim().replace(/^\||\|$/g, "").split("|").map((c) => c.trim()));
  const ncol = cells[0].length;
  const total = 9638; // A4 text width in DXA at 2.5 cm margins
  const first = Math.round(total * (ncol > 4 ? 0.26 : 0.34));
  const rest = Math.floor((total - first) / (ncol - 1));
  const widths = [first, ...Array(ncol - 1).fill(rest)];
  widths[ncol - 1] += total - widths.reduce((a, b) => a + b, 0);
  return new d.Table({
    width: { size: total, type: d.WidthType.DXA },
    columnWidths: widths,
    borders: { top: border, bottom: border, left: border, right: border, insideHorizontal: border, insideVertical: border },
    rows: cells.map((r, i) => new d.TableRow({
      tableHeader: i === 0,
      children: r.map((c, j) => new d.TableCell({
        width: { size: widths[j], type: d.WidthType.DXA },
        margins: { top: 40, bottom: 40, left: 80, right: 80 },
        children: [new d.Paragraph({ children: runs(c, { size: 18, bold: i === 0 || undefined }) })],
      })),
    })),
  });
}

const body = [];
let listInstance = 0;
const lines = md.split("\n");
for (let i = 0; i < lines.length; i++) {
  let l = lines[i];
  if (!l.trim()) continue;
  if (/^(Details|Analysis and checks|Draft v|Sections marked)/.test(l) && l.includes("[[") ) continue;
  if (/^Sections marked|^Word version/.test(l)) continue;
  let m;
  if ((m = l.match(/^(#{1,3}) (.*)/))) {
    const level = [d.HeadingLevel.TITLE, d.HeadingLevel.HEADING_1, d.HeadingLevel.HEADING_2][m[1].length - 1];
    body.push(new d.Paragraph({ heading: level, children: runs(m[2]) }));
    continue;
  }
  if ((m = l.match(/^!\[\[(.+?)\]\]/))) { body.push(image(m[1])); continue; }
  if (/^\*Figure \d+\./.test(l)) {
    body.push(new d.Paragraph({ spacing: { after: 240 }, children: runs(l.slice(1, -1), { italics: true, size: 18 }) }));
    continue;
  }
  if (l.startsWith("|")) {
    const rows = [];
    while (i < lines.length && lines[i].startsWith("|")) rows.push(lines[i++]);
    i--;
    body.push(table(rows), new d.Paragraph({ spacing: { after: 60 }, children: [] }));
    continue;
  }
  const bullet = l.match(/^- (.*)/), num = l.match(/^\d+\. (.*)/);
  if (bullet || num) {
    // a list block: items plus indented continuation lines
    const ordered = !!num;
    const inst = ++listInstance;
    while (i < lines.length) {
      const b = lines[i].match(ordered ? /^\d+\. (.*)/ : /^- (.*)/);
      if (!b) break;
      let text = b[1];
      while (i + 1 < lines.length && /^ {2,}\S/.test(lines[i + 1])) text += " " + lines[++i].trim();
      body.push(new d.Paragraph({
        numbering: { reference: ordered ? "num" : "bul", level: 0, instance: ordered ? inst : undefined },
        spacing: { after: 80 },
        children: runs(text),
      }));
      i++;
    }
    i--;
    continue;
  }
  // paragraph: join following plain lines
  let text = l;
  while (i + 1 < lines.length && lines[i + 1].trim() && !/^(#|\||- |\d+\. |!\[\[|\*Figure)/.test(lines[i + 1])) text += " " + lines[++i].trim();
  body.push(new d.Paragraph({ spacing: { after: 160 }, children: runs(text) }));
}

const black = { color: "000000", font: FONT };
const doc = new d.Document({
  creator: "Andrea Piazzola",
  title: "HLB SOD1 report",
  styles: {
    default: { document: { run: { font: FONT, size: 21 }, paragraph: { spacing: { line: 276 } } } },
    paragraphStyles: [
      { id: "Title", name: "Title", basedOn: "Normal", run: { ...black, size: 32, bold: true }, paragraph: { spacing: { after: 240 } } },
      { id: "Heading1", name: "Heading 1", basedOn: "Normal", next: "Normal", quickFormat: true, run: { ...black, size: 26, bold: true }, paragraph: { spacing: { before: 360, after: 120 }, outlineLevel: 0, keepNext: true } },
      { id: "Heading2", name: "Heading 2", basedOn: "Normal", next: "Normal", quickFormat: true, run: { ...black, size: 22, bold: true }, paragraph: { spacing: { before: 240, after: 100 }, outlineLevel: 1, keepNext: true } },
    ],
  },
  numbering: {
    config: [
      { reference: "bul", levels: [{ level: 0, format: d.LevelFormat.BULLET, text: "•", alignment: d.AlignmentType.LEFT, style: { paragraph: { indent: { left: 360, hanging: 260 } } } }] },
      { reference: "num", levels: [{ level: 0, format: d.LevelFormat.DECIMAL, text: "%1.", alignment: d.AlignmentType.LEFT, style: { paragraph: { indent: { left: 360, hanging: 300 } } } }] },
    ],
  },
  sections: [{
    properties: { page: { margin: { top: 1418, bottom: 1418, left: 1134 + 284, right: 1134 + 284 } } },
    footers: { default: new d.Footer({ children: [new d.Paragraph({ alignment: d.AlignmentType.CENTER, children: [new d.TextRun({ children: [d.PageNumber.CURRENT], size: 18 })] })] }) },
    children: body,
  }],
});
d.Packer.toBuffer(doc).then((buf) => fs.writeFileSync(out, buf));
