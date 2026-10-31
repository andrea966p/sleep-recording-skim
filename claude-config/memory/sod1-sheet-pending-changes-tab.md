---
name: sod1-sheet-pending-changes-tab
description: "How Claude Code changes the HLB SOD1 intake Google Sheet: directly with the Google Sheets connector (since 2026-10-26), every change logged in the 'Pending changes instructions' tab. Workflow in the vault"
metadata:
  type: reference
---

Sheet `HLB_SOD1_Intake_Monitoring_SDSLNANO` (id 1jgQpYiUGzEwFpjAhy8SvCamGoeMFZEycLFpzwgfgxhs), tab `Pending changes instructions` (data from row 10): ① PENDING A:G, ② APPLIED I:Q (N old value, P verdict, Q comment), ③ HISTORY S:AA append-only. Last ID CHG-017 (HISTORY row 26); rework = CHG-xxx-R1.

Procedure: [[sod1-sheet-change-log-workflow]] · [[_hlb-sod1-hub]]

- ✅ Since 2026-10-26 Claude Code writes the sheet itself with the **Google Sheets connector** (`get_spreadsheet` grid read for formulas, `update_values`, `update_formulas`, `batch_clear_values`). Check `session_connectors_status` first; if Sheets is missing, STOP and tell Andrea. 🛑 Never fall back to Drive exports + hand-pasted TSVs or Claude for Sheets chat messages (both retired).
- 🛑 Show Andrea the exact cells (tab, range, header, old → new) and wait for OK before writing.
- Loop: ① row → re-read targets → write → ② row with old value → read back (formulas + #REF!/#VALUE!/#N/A/#ERROR!) → ③ row → clear ① and ② → read the log back.
- 🔴 Each section fills from row 10 on its own: the ① row goes at the first empty row of column A, NOT at HISTORY's next row (slip on 2026-10-26, fixed at once).
- 🔴 No log cell may start with `=`; every log cell < 300 chars; dates yyyy-mm-dd; find columns by header text; never insert rows/columns on batch tabs or the log tab; never type over a formula unless asked.
- Sheets API read quota per minute is small: batch reads into one grid read; on a quota error wait ~60 s.
- Registry has no gavage/SD-time column; such plans go in `Notes` (col X). Related: [[nanotag-sod1-hlbnsl]]
- 🔴 Config `DAILY PREPARATION CALCULATOR` and each batch tab `B36` are the DRINKING-WATER concentration (6.8 U/mL), shared by all batches. Gavage (0.2 mL = 20.4 U) is 102 U/mL: change only that batch row (CHG-011, S-SPF E48), never Config.
