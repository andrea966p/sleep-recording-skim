---
name: sod1-sheet-pending-changes-tab
description: "How Claude Code changes the HLB SOD1 intake Google Sheet: request rows in the 'Pending changes instructions' tab, Claude for Sheets applies, Claude Code reviews; Claude Code has NO write access, Andrea pastes"
metadata:
  type: reference
---

Sheet `HLB_SOD1_Intake_Monitoring_SDSLNANO` (Drive id 1jgQpYiUGzEwFpjAhy8SvCamGoeMFZEycLFpzwgfgxhs), tab **`Pending changes instructions`** (set up by Claude for Sheets 2026-10-19). Data from row 10.
- ① PENDING **A:G** (ID, requested date, target sheet, target range, instruction, rationale, Status Pending/In progress/Blocked) — Claude Code.
- ② APPLIED **I:Q** — Claude for Sheets writes I:O; Claude Code sets **P** verdict (Awaiting review/Approved/Needs fix/Superseded) + **Q** comment.
- ③ HISTORY **S:AA**, append-only — Claude Code moves Approved rows here.
- IDs CHG-001…, rework CHG-001-R1. Never insert whole sheet rows on that tab; append at the bottom of each section.
- Claude for Sheets acts only when Andrea says "apply pending changes" in the sheet's chat.

🔴 **No Google Sheets connector exists** (only Drive; checked 2026-10-19). Read = Drive `download_file_content` export xlsx (~300 KB, saved to file) → scratch venv with openpyxl (no system openpyxl), load twice (formulas + data_only). Write = paste-ready TSV in `nanotag/sheet-changes/` that Andrea pastes, or a sentence for Claude for Sheets.

🔴 **Cells over 300 chars get cut to 300 + "…" on paste** (seen 10-19). Keep every request cell ≤ 300 chars, and diff the pasted rows against the TSV after each paste.

🔴 No log cell may start with `=` (shows #ERROR!). Review = export, check target cells + downstream + diff ALL other input cells against the previous export + scan for #-errors. CHG-001…004 approved 10-19.

🔴 **Andrea (2026-10-19): copy-pasting TSV files by hand is NOT an acceptable workflow; fix it (planned 10-20).** Until then give ONE message to paste into the Claude for Sheets chat that carries the full request/verdict text, never files to paste into cells.

**Why:** the sheet's shared/array formulas die on xlsx re-upload, and the old Desktop handover files left no trail of what was changed.
**How to apply:** for any sheet change follow `vault/02-procedures/sod1-sheet-change-log-workflow.md`: export first, exact tab + range + header name, expected result and downstream cells, rationale with decision date. Related: [[nanotag-sod1-hlbnsl]].
