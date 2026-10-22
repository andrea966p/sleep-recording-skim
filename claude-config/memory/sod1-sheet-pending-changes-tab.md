---
name: sod1-sheet-pending-changes-tab
description: "How Claude Code changes the HLB SOD1 intake Google Sheet: request rows in the 'Pending changes instructions' tab, Claude for Sheets applies, Claude Code reviews; Claude Code has NO write access. Workflow in the vault"
metadata:
  type: reference
---

Sheet `HLB_SOD1_Intake_Monitoring_SDSLNANO` (Drive id 1jgQpYiUGzEwFpjAhy8SvCamGoeMFZEycLFpzwgfgxhs), tab `Pending changes instructions` (data from row 10): Claude Code writes requests (A:G), Claude for Sheets applies them (I:O) when Andrea says "apply pending changes" in the sheet chat, Claude Code reviews (P verdict, Q comment) and moves Approved rows to history (S:AA). IDs CHG-001..., rework CHG-001-R1.

Details: [[sod1-sheet-change-log-workflow]] · [[_hlb-sod1-hub]]

- 🔴 There is NO Google Sheets connector (Drive only): read = export xlsx via Drive `download_file_content`, load with openpyxl in a scratch venv (twice: formulas and data_only). Claude Code cannot write the sheet.
- 🛑 Andrea (2026-10-19): hand-copy-pasting TSV files is NOT an acceptable workflow. Give ONE message for the Claude for Sheets chat that carries the full request or verdict text, never files to paste into cells.
- 🔴 Cells over 300 characters get cut on paste: keep every request cell <= 300 chars. No log cell may start with `=`. Never insert whole sheet rows on that tab; append at the bottom of each section.
- Review = export, check target cells and downstream cells, diff ALL other input cells against the previous export, scan for #-errors. Related: [[nanotag-sod1-hlbnsl]]
