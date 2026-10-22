<%*
// New-note wizard. Runs when a note is created in 00-inbox (Templater folder template).
// Asks what the note is and where it belongs, writes the frontmatter the vault schema
// needs (see CLAUDE.md), names the file and moves it into place.
// Cancel at any prompt and the blank note simply stays in 00-inbox.
const TYPES = ["experiment", "procedure", "reference", "decision", "incident", "meeting", "hub"];
const LABEL = {
  experiment: "experiment: a run, result, analysis, pre-registration, audit",
  procedure: "procedure: steps someone follows",
  reference: "reference: fact sheet, spec, concept, how something works, vendor email",
  decision: "decision: a choice between options, a council review",
  incident: "incident: something broke, or a symptom and its fix",
  meeting: "meeting: lab meeting, slides, report for the professor",
  hub: "hub: front page of a NEW project or area",
};
const type = await tp.system.suggester(t => LABEL[t], TYPES, false, "What is this note?");
if (!type) return;
const homes = app.vault.getAllLoadedFiles()
  .filter(f => f.children && /^(10-projects|20-areas)\/[^/]+$/.test(f.path))
  .map(f => f.path).sort();
const places = type === "hub"
  ? ["10-projects (new project)", "20-areas (new area)"]
  : homes.concat(["30-resources/meetings", "30-resources/vendors", "30-resources/literature", "00-inbox"]);
let folder = await tp.system.suggester(p => p, places, false, "Where does it belong?");
if (!folder) return;
const title = await tp.system.prompt("Title (a few words)");
if (!title) return;
const today = tp.date.now("YYYY-MM-DD");
const slug = title.toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/^-+|-+$/g, "");
let key = folder.startsWith("30-resources") || folder === "00-inbox" ? "" : folder.split("/")[1];
let name = ["experiment", "decision", "incident", "meeting"].includes(type) ? `${today}-${slug}` : slug;
if (type === "hub") {
  key = slug;
  folder = `${folder.split(" ")[0]}/${key}`;
  name = `_${key}-hub`;
}
if (tp.file.find_tfile(name)) { new Notice(`A note called "${name}" already exists. Pick another title.`); return; }
await tp.file.move(`${folder}/${name}`);
const SKEL = { experiment: "Experiment", procedure: "Procedure", reference: "Reference",
               decision: "Decision", incident: "Incident", meeting: "Meeting", hub: "Hub" };
tR += "---\n";
tR += `type: ${type}\n`;
if (key) tR += `area: ${key}\n`;
tR += `status: ${type === "experiment" ? "planned" : "active"}\n`;
tR += `created: ${today}\n`;
if (type === "hub") tR += `summary: ""\n`;
tR += "tags: []\n---\n\n";
tR += `# ${title}\n\n`;
tR += await tp.file.include(`[[${SKEL[type]}]]`);
%>
