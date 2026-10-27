---
type: procedure
area: hlb-sod1
status: active
canonical: true
tags: [procedure, sheet, hlb, sod1, nanotag, claude, canonical]
created: 2026-10-19
---

# Changing the SOD1 intake sheet: the "Pending changes instructions" tab

> [!info] 2026-10-26: Claude Code now edits the sheet directly with the Google Sheets connector (CHG-010 was the first change made this way). Hand-pasting TSV files and Claude for Sheets chat messages are retired. [[2026-10-26]]

> [!abstract] TL;DR
> - **What this is:** the only route for changing the Google Sheet `HLB_SOD1_Intake_Monitoring_SDSLNANO`
>   (Drive id `1jgQpYiUGzEwFpjAhy8SvCamGoeMFZEycLFpzwgfgxhs`). Every change gets a Change ID and leaves a trail in the
>   tab `Pending changes instructions`.
> - **Who writes:** Claude Code, through the **Google Sheets connector** (`get_spreadsheet`, `get_values`,
>   `update_values`, `update_formulas`, `batch_clear_values`). It writes the request, applies it, verifies it by
>   reading it back and files it in HISTORY, all in one session, after Andrea OKs the exact cells.
> - **Why the log:** the sheet has shared formulas and array formulas everywhere. An .xlsx export → re-upload destroys
>   them, and edits made without a log left no trail of what changed or why.
> - **How to read this page:** the layout, then the loop, then the rules. Project context: [[_hlb-sod1-hub]]; nanotag
>   workflow: [[nanotag-recording-and-analysis]]; big picture: [[nvr-system-overview]].

## Where it is

Tab **`Pending changes instructions`**. Rows 1–9 are frozen. Rows 2–6 hold the workflow text, row 8 the section titles,
row 9 the headers. Data starts at **row 10**. Three tables sit side by side so each can grow downward on its own:

| Section | Columns | Written by | Columns in order |
|---|---|---|---|
| **① PENDING** | **A:G** | Claude Code | A Change ID · B Requested (date) · C Target sheet · D Target range · E Instruction (what to change) · F Rationale / context · G Status |
| **② APPLIED** | **I:Q** | Claude Code | I Change ID · J Applied (date) · K Target sheet · L Range(s) changed · M Summary of what was done · N Previous value / formula · O Deviations / issues · **P Review verdict** · **Q Reviewer comments** |
| **③ HISTORY** | **S:AA** | Claude Code, append-only | S Change ID · T Requested · U Applied · V Approved · W Target sheet · X Range(s) · Y Instruction · Z Summary of what was done · AA Reviewer comments |

Dropdowns: **G** = `Pending` / `In progress` / `Blocked`. **P** = `Awaiting review` / `Approved` / `Needs fix` / `Superseded`.
Dates are `yyyy-mm-dd`.

## The loop (Claude Code, Google Sheets connector)

0. **Check the connector.** `session_connectors_status` must show Google Sheets connected and the tools loaded. If
   not, stop and tell Andrea. Never fall back to Drive exports and hand-pasted files.
1. **Read first, the same session.** Read the log tab and every target range with formulas: `get_spreadsheet` with
   `includeGridData` and the fields `userEnteredValue` + `formattedValue`. Find columns by their **header text**,
   never by letter.
2. **Show Andrea the exact cells** (tab, range, header, current value, new value) and wait for an OK.
3. **Request.** Write the row in ① at the first empty row of **column A** at or below row 10 (each section fills
   from row 10 on its own; do not use HISTORY's next row). Status `In progress`.
4. **Apply.** Read the target cells again right before writing, then write them (`update_values` for text and dates,
   `update_formulas` for formulas).
5. **Record.** Write the ② row: what was done, the **previous value or formula** (N), deviations (O), verdict
   `Awaiting review`.
6. **Verify.** Read back the changed cells and the cells that depend on them, with formulas. Check that formulas are
   still formulas and that no `#REF!` / `#VALUE!` / `#N/A` / `#ERROR!` appeared.
7. **File.** Append the row to ③ HISTORY (first empty row of column S), with the verification in AA. Then clear
   that change's cells in ① and ②, and read the log tab back once more.
8. A failed verification gets a rework `CHG-xxx-R1` instead of a HISTORY row.

③ HISTORY is append-only. Nobody edits or deletes its rows.

## Rules

- **Formulas stay formulas.** Never type a value over a formula unless the request says so. A date that records
  something that already happened may be typed.
- **List the cells that change as a consequence** (downstream formulas) and check them in step 6.
- **Never insert whole rows or columns** on a batch tab or on this tab (insertion shifts the other two sections).
  New columns go only on `Registry`, as its row-3 note says, and only when Andrea asks.
- **One Change ID = one change** that could be undone on its own.
- 🔴 **No log cell may start with `=`.** The sheet reads it as a formula and shows `#ERROR!` (N12, CHG-003,
  2026-10-19). Write old formulas as `S19-3`, or start the cell with a word.
- 🔴 **Keep every log cell under 300 characters.** Long text = split into two changes, or shorten.
- **Dates are `yyyy-mm-dd`.** The write tools parse `2026-10-26` as a date, the same as the existing HISTORY cells.
  Text that looks like a number or date and must stay text gets a leading `'`.
- **Rationale** says why, with the date of the decision and who made it (usually Andrea).
- **Read quota.** The Sheets API allows a limited number of reads per minute; batch reads into one grid read and
  wait a minute after a quota error.
- **Edits made by hand outside the log** are logged afterwards as a record-only change (see CHG-005).

## History

> [!history]
> - **2026-10-27** — CHG-011: `S-SPF` E48 (Day 6 `Water to add`) uses the gavage concentration 102 U/mL; HISTORY row 20. [[2026-10-27]]
> - **2026-10-26** — Route changed: Claude Code edits the sheet directly with the Google Sheets connector, keeping the
>   log. First change CHG-010 (Registry `Notes` X51:X55, X57:X61, SPF plan for 2026-10-27) written, verified by
>   read-back and filed in ③ HISTORY row 19. Paste files and Claude for Sheets chat messages retired.
> - **2026-10-24** — Round 2 (CHG-005 → CHG-009, sent 2026-10-21 as one chat message) applied 2026-10-24 and verified on
>   an export: every target cell right, formula-driven text followed, no error values. Claude for Sheets left the five rows
>   in ① PENDING as well as ②, against workflow step 2. The diff also found edits outside the log: new tabs `S-SPF` and
>   `W-SPF`, EEG `Registry` rows 50-61 (two new batches) and `NS-SL` C58 = 2.
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
