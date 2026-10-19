---
tags: [procedure, sheet, hlb, sod1, nanotag, claude, canonical]
created: 2026-10-19
status: active
---

# Changing the SOD1 intake sheet: the "Pending changes instructions" tab

> [!abstract] TL;DR
> - **What this is:** the only route for Claude Code to change the Google Sheet `HLB_SOD1_Intake_Monitoring_SDSLNANO`
>   (Drive id `1jgQpYiUGzEwFpjAhy8SvCamGoeMFZEycLFpzwgfgxhs`). Claude Code **requests** a change, Claude for Sheets (the
>   Claude add-on inside the sheet) **applies** it, Claude Code **reviews** it. Set up 2026-10-19.
> - **Why:** the sheet has shared formulas and array formulas everywhere. An .xlsx export → re-upload destroys them, and
>   the earlier handover files on the workstation Desktop left no trail of what was actually changed.
> - 🔴 **Claude Code cannot write to the sheet.** There is no Google Sheets connector (only Google Drive, read-only for
>   cells; checked 2026-10-19). Claude Code reads the sheet as an .xlsx export and gives Andrea **paste-ready rows**.
> - **Every request names the exact tab and cell range,** says what the cell should contain afterwards, and says why.
> - **How to read this page:** the layout, then the loop, then the rules for writing a request. Project context:
>   [[_HLB-SOD1-project-hub]]; nanotag workflow: [[nanotag-recording-and-analysis]]; big picture:
>   [[01-infrastructure/system-overview]].

## Where it is

Tab **`Pending changes instructions`**. Rows 1–9 are frozen. Rows 2–6 hold the workflow text, row 8 the section titles,
row 9 the headers. Data starts at **row 10**. Three tables sit side by side so each can grow downward on its own:

| Section | Columns | Written by | Columns in order |
|---|---|---|---|
| **① PENDING** | **A:G** | Claude Code (via Andrea's paste) | A Change ID · B Requested (date) · C Target sheet · D Target range · E Instruction (what to change) · F Rationale / context · G Status |
| **② APPLIED** | **I:Q** | Claude for Sheets; P:Q by Claude Code | I Change ID · J Applied (date) · K Target sheet · L Range(s) changed · M Summary of what was done · N Previous value / formula · O Deviations / issues · **P Review verdict** · **Q Reviewer comments** |
| **③ HISTORY** | **S:AA** | Claude Code (via Andrea's paste), append-only | S Change ID · T Requested · U Applied · V Approved · W Target sheet · X Range(s) · Y Instruction · Z Summary of what was done · AA Reviewer comments |

Dropdowns: **G** = `Pending` / `In progress` / `Blocked`. **P** = `Awaiting review` / `Approved` / `Needs fix` / `Superseded`.
Dates are `yyyy-mm-dd`.

## The loop

1. **Request (Claude Code).** One row in ① per self-contained change, Status `Pending`. IDs run `CHG-001`, `CHG-002`, …
   A rework of a change keeps the number with a suffix: `CHG-001-R1`.
2. **Apply (Claude for Sheets).** It acts **only when Andrea tells it in the sheet's Claude chat**, e.g. "apply pending
   changes". For each row it applies, it writes a row in ② with `Awaiting review` and removes the row from ①. If it can't
   apply one, it sets ① Status to `Blocked` and writes the reason into F.
3. **Review (Claude Code).** Claude Code exports the sheet, checks every `Awaiting review` row against the actual cells
   (values AND formulas), and gives a verdict:
   - **Approved** → the row moves to ③ HISTORY and is deleted from ②.
   - **Needs fix** → a new request `CHG-xxx-R1` in ①, and the ② row is set to `Superseded`.
4. **③ HISTORY is append-only.** Nobody edits or deletes its rows.

Because Claude Code can't write, steps 1 and 3 end with Claude Code giving Andrea the text to paste, or a sentence to
give Claude for Sheets ("set P12 to Approved, Q12 to '…', then move CHG-001 to HISTORY").

## Rules for Claude Code when writing a request

- **Read the sheet first, the same day.** Export it (Drive `download_file_content`, export type
  `application/vnd.openxmlformats-officedocument.spreadsheetml.sheet`), decode, open with `openpyxl` twice: once for
  formulas, once with `data_only=True` for the computed values. The export is ~300 KB, so the tool saves it to a file.
  There is no system `openpyxl`: make a scratch venv (`python3 -m venv …; pip install openpyxl`).
- **Exact tab and range.** `NANOTAG registry` + `W19:W23, W25:W29`, never "the read column". Name the column header too,
  because letters drift when columns are added (the registry gained `W Live tag read` on 2026-10-19 and every column after
  it moved one letter).
- **Say what the cell must contain afterwards,** formula or value, and what it computes to. State the current content so
  Claude for Sheets can check it is editing the right thing.
- **Formulas stay formulas.** Never ask for a typed value over a formula unless that is the point of the change, and say
  so. A date that records something that already happened may be typed.
- **List the cells that should change as a consequence** (formulas downstream), so the review can check them.
- **Never ask for whole rows or columns to be inserted on a batch tab** (README rule), and never insert whole sheet rows on
  this tab (it shifts the other two sections). New entries go at the bottom of each section.
- **One request = one change** that can be approved or rejected on its own.
- 🔴 **No log cell may start with `=`.** The sheet reads it as a formula and shows `#ERROR!` (N12, CHG-003, 2026-10-19).
  Write old formulas as `S19-3`, or start the cell with a word.
- 🔴 **Keep every cell under 300 characters.** On 2026-10-19 the first paste cut three longer cells at 300 characters
  plus "…" (CHG-001 E/F, CHG-004 E), which would have handed Claude for Sheets a half note. Long text = split into
  two requests, or shorten. After every paste, Claude Code re-exports and diffs the pasted rows against the file.
- **Rationale** says why, with the date of the decision and who made it (usually Andrea), so the trail explains itself.

## Pasting rows (Andrea)

Claude Code saves the rows as a tab-separated file, one line per request, columns A→G (or P→Q, or S→AA). Open it, select
all, copy, click the first empty cell of the section's first column (for ① the first empty row in column **A** at or below
row 10), and paste. Google Sheets splits on the tabs. Check that the Status column landed on the dropdown. Request files
are kept in the repo under `nanotag/sheet-changes/`.

## Reviewing (Claude Code)

- Re-export the sheet. For each `Awaiting review` row in ②: open the ranges in L, compare formula and value with the
  request, check the downstream cells listed in the request, check no `#REF!`/`#VALUE!`/`#N/A` appeared anywhere.
- Read O (Deviations) and decide whether the deviation is acceptable.
- Write the verdict and comment as paste-ready text for P:Q, and for every `Approved` row the ③ HISTORY line (S:AA).

## History

> [!history]
> - **2026-10-19** — Round closed: verdicts, ③ HISTORY rows S10:AA13 and clearing of ② done by Claude for Sheets from one
>   pasted chat message (checked on export). 🔴 **An edit outside the log:** after the round, `NANOTAG registry`
>   R19:R23, R25:R29 changed from `=G+4` (10-16, CHG-003) to `=G+7` (10-19) with no request. Andrea confirmed it is
>   correct: the mice were single-housed on 2026-10-19, not 10-16. CHG-003's History row therefore describes a value that
>   was later replaced; log it as CHG-005 in the next round. Lesson: every review diffs ALL data tabs against the
>   previous export, which is how this was caught. Andrea: hand copy-paste of files is not an acceptable workflow; to be
>   redesigned (planned 2026-10-20). Until then Claude Code gives one message to paste into the Claude for Sheets chat.
> - **2026-10-19** — CHG-001 → CHG-004 applied by Claude for Sheets and verified on an export (no unexpected cell changed,
>   no new error except the log cell N12). All four Approved.
> - **2026-10-19** — Created. Tab layout checked against an export of the sheet (headers rows 8–9, dropdowns G10:G1000
>   and P10:P1000, freeze at row 10). First requests CHG-001 → CHG-004 drafted (tag read time, single-housing formula,
>   notes) in `nanotag/sheet-changes/2026-10-19_CHG-001-004.tsv`.
