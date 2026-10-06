// One slide per report figure: the image, fitted, with its report caption below.
//   node build_pptx.js report.json IMG_DIR out.pptx
// Run through build.sh.
const fs = require("fs");
const path = require("path");
const pptxgen = require("pptxgenjs");

const [, , jsonPath, imgDir, outPath] = process.argv;
const blocks = JSON.parse(fs.readFileSync(jsonPath, "utf8"));

// ponytail: plain hex instead of theme colours; applying a theme needs a helper
// outside this repo, and the deck has two colours.
const INK = "1B211E", MUTED = "56625C";
const W = 13.333, H = 7.5, M = 0.4, CAP_H = 1.55;   // caption box fits the longest caption (Figure 4) at 11 pt

const pres = new pptxgen();
pres.layout = "LAYOUT_WIDE";
pres.title = "HLBNSL nanotag figures";
pres.theme = { headFontFace: "Cambria", bodyFontFace: "Calibri" };
pres.defineSlideMaster({
  title: "FIGURE",
  background: { color: "FFFFFF" },
  objects: [{ placeholder: { options: { name: "caption", type: "body", x: M, y: H - M - CAP_H, w: W - 2 * M, h: CAP_H,
                                        fontSize: 11, color: INK, valign: "top", margin: 0 },
                             text: "" } }],
  slideNumber: { x: W - M - 0.5, y: H - 0.32, w: 0.5, h: 0.25, fontSize: 9, color: MUTED, align: "right" },
});

function pngSize(file) {
  const b = fs.readFileSync(file);
  return { w: b.readUInt32BE(16), h: b.readUInt32BE(20) };
}

pres.addSection({ title: "Figures" });
for (let k = 0; k < blocks.length; k++) {
  const b = blocks[k], cap = blocks[k + 1];
  if (b.t !== "img" || !cap || cap.t !== "caption") continue;
  const f = path.join(imgDir, b.src);
  const { w, h } = pngSize(f);
  const boxW = W - 2 * M, boxH = H - 2 * M - CAP_H - 0.2;
  const s = Math.min(boxW / w, boxH / h);
  const slide = pres.addSlide({ masterName: "FIGURE", sectionTitle: "Figures" });
  slide.addImage({ path: f, x: (W - w * s) / 2, y: M, w: w * s, h: h * s, altText: b.alt,
                   objectName: path.basename(b.src, ".png") });
  slide.addText(cap.runs.map((r) => ({ text: r.text, options: { bold: !!r.b, italic: !!r.i } })),
                { placeholder: "caption" });
}

pres.writeFile({ fileName: outPath }).then(() => console.log(`wrote ${outPath}`));
