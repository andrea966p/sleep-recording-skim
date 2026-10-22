---
name: feedback_report_writing_style
description: "How andrea writes reports/docs and wants them written (voice, formatting)"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: afc80995-701c-426c-9215-ab482cb5a989
---

andrea's writing style for reports and operator docs (learned from her edited "final to print" version of the EEG troubleshooting report, 2026-06-28):

- **Voice:** informal, first-person ("I tried…", "turned out…"), practical lab-notebook tone. NOT academic/formal. She will always edit the draft afterward, so leave it easy to reword.
- **Expand acronyms inline on first use:** e.g. "signal-noise-ratio SNR ~12", "peak-to-peak (pk-pk)". Explain jargon in plain words for a non-expert reader.
- **ALLCAPS for critical do/don't warnings** inserted in-line, e.g. **DO NOT SWAP THE KONTEX USB CABLE**.
- **Honest real-world hedges/status** kept in: "for now it works well enough but won't be reliable on a long run, looking for alternatives", "haven't done it yet, needs me at the rig".
- **Punctuation:** prefers **commas over dashes**. Replace em-dashes "—" with commas (keep en-dash only in numeric ranges like 0.5–30 Hz). She sometimes uses a spaced " - ".
- **Flags AI-contributed bits explicitly** when she wants provenance, e.g. a bullet retitled "From claude code - Python environment:".
- Keeps **tables and concrete numbers** (RMS/pk-pk/SNR, voltages, pad maps).
- Likes a **TL;DR / "where we are right now"** block up top, then dated chronological sections, then a **"still open"** list at the end.

**Why:** matching her voice means fewer rewrites and docs she'll actually ship.
**How to apply:** draft in this style by default for any report/operator doc she'll hand off; see [[feedback_leave_guides]] and [[feedback_sudo_command_style]].
