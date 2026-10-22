---
type: procedure
area: hlb-sod1
status: done
tags: [handover, nanotag, sheet, NS-SL, NW-SL]
created: 2026-09-28
---

> [!note] Filed in the vault 2026-10-05
> Copied verbatim from `~/Desktop/Andrea/nanotag/HANDOVER_sheet_fixes_2026-09-28.md` (SKIM workstation). The sheet read on 2026-10-05 shows its edits applied: Config `Nanotag mass (g)` row, Registry L (e.g. 41 = −1.3%), age 18.1 weeks, Day −4…Day 2 labels, recordings G4/E6/M7 text. **Points 10 and 11 (Run 2 discarded) are superseded** by [[2026-10-05-HLBNSL-sheet-handover-run2]]: Run 2 is now merged and analysed.

# Handover: fixes to the nanotag tabs of the SOD1 intake sheet

**Written:** 2026-09-28, by the analysis session, after going through every point with the user.

**Sheet:** Google Sheet `HLB_SOD1_Intake_Monitoring_SDSLNANO`, Drive id `1jgQpYiUGzEwFpjAhy8SvCamGoeMFZEycLFpzwgfgxhs`.

**Protocol it has to match:** `/home/skim/Downloads/Acute_SD_Behavioral_Protocol.pdf`. Its Day 0 is the Y-maze, Day 1 is NOR habituation, and Day 2 is the NOR test followed by sampling.

**Scope:** only the tabs `NANOTAG registry`, `NANOTAG recordings`, `NANOTAG History`, `NANOTAG sampling` and `NANOTAG behavioral`. Nothing below has been done yet.

## Rules for the agent doing this

- Edit the Google Sheet in place. Do **not** export it to .xlsx and re-upload it: that replaces formulas and array formulas.
- Several cells hold array formulas. They are marked below. Never type over one; add a new column to the right instead.
- Do **not delete rows** in `NANOTAG behavioral`. The mouse blocks are stacked vertically, so deleting a row moves every block below it. Clear the cell contents instead.
- The README says new columns go on the Registry tab, never on the batch tabs (W-SD, S-SD, W-SL, S-SL, NS-SL, NW-SL).
- Registry rows: NS-SL is rows 7–11 (41, 42, 43, 44, 49). NW-SL is rows 13–17 (45, 46, 47, 48, 50). Row 12 is the NW-SL banner; do not touch it.

---

## Settled facts (from the user)

- **Sampling date:** Friday 2026-10-02. The dates in Registry `T` (`=S+12`) are already correct.
- **Test days:** Day 0 = Wed 09-30, Y-maze. Day 1 = Thu 10-01, NOR habituation (open field). Day 2 = Fri 10-02, NOR training (T1), then NOR test (T2), then sampling.
- **Homecage baseline:** 3 days, 09:00 to 09:00. Mice 49 and 50 are the exception: 1 day, 2026-09-15 09:00 → 09-16 09:00.
- **Run 1:** started Sun 2026-09-20 10:00, extracted Mon 2026-09-28. The last 12 s bin is 08:59:48 for every mouse except 41, whose last bin is 08:57:00.
- **Run 2:** each tag was set to start 1 h after that mouse's extraction handling, and stops by itself around Sun 2026-10-04 13:00. **All run 2 data is discarded**, because it overlaps the behavioural testing.
- **Mouse HLBNSSL43:** died 2026-09-28 ~10:00. All of its data is discarded. Its log entries stay as they are, as a history record.
- **Tag position:** in every mouse, implanted under the skin at the neck and pushed toward the right. After healing it moved to the right dorsolateral flank.
- **Test times:** each test starts at 15:00 and mice go one at a time. This batch sleeps ad lib, so no sleep deprivation. The next batch will have sleep deprivation from 09:00 to 15:00, and every mouse will be kept awake until the last mouse has finished; the same applies to the NOR days.
- **No animal-welfare (IACUC) report is needed** for mouse 43.

## Open questions: all answered by the user on 2026-09-28

1. **Excluded window:** it is **2026-09-28** 08:45–11:00. Run 1 data ends at 08:59:48, so only 08:45–09:00 overlaps it.
2. **Liquid start:** **2026-09-17**, which is what the sheet already says. Leave Registry `R` (`=F+6`) and the intake grids as they are.
3. **Tag 20643:** explanted from mouse 43 and **kept**.

---

## Point 2: make the day labels match the protocol

The new labels for every mouse block in `NANOTAG behavioral`:

| Date | New label | Content |
|---|---|---|
| 2026-09-26 | Day −4 | handling (existing entries, keep) |
| 2026-09-27 | Day −3 | handling (keep) |
| 2026-09-28 | Day −2 | handling + tag extraction (keep) |
| 2026-09-29 | Day −1 | handling |
| 2026-09-30 | **Day 0** | Y-maze |
| 2026-10-01 | **Day 1** | NOR habituation |
| 2026-10-02 | **Day 2** | NOR training (T1), NOR test (T2), sampling |
| 2026-10-03 to 10-05 | none | clear these rows (after sampling) |

**Block layout.** Each block has a title row. Below it come a header row (+1), a Date/Day row (+2), then 10 day rows (+3 to +12) and a status row.
- Left blocks use columns B–G: B Date, C Day, D Time, E Stage, F Notes, G Score.
- Right blocks use columns I–N: I Date, J Day, K Time, L Stage, M Notes, N Score.

| Mouse | Title cell | Day rows |
|---|---|---|
| 41 | B9 | 12–21 |
| 42 | I9 | 12–21 |
| 43 | B24 | 27–36 |
| 44 | I24 | 27–36 |
| 49 | B39 | 42–51 |
| 45 | B57 | 60–69 |
| 46 | I57 | 60–69 |
| 47 | B72 | 75–84 |
| 48 | I72 | 75–84 |
| 50 | B87 | 90–99 |

- I39 and the matching cell beside B87 are scoring keys, not mice.
- Check the 43 and 50 row ranges before editing. They follow the same pattern, but only block 1 was read cell by cell.

**For each block (using mouse 41 as the example, rows 12–21):**
1. **Relabel the Day column.** C12:C18 becomes Day −4, Day −3, Day −2, Day −1, Day 0, Day 1, Day 2. The existing entries on rows 12–14 stay as they are; only the label changes.
2. **Move the test entries up.** They currently sit on the wrong dates: row 19 (10-03) says Y-Maze, row 20 (10-04) NOR Habituation, row 21 (10-05) NOR Test/Sampling.
   - Y-Maze goes to row 16 (09-30).
   - NOR Habituation goes to row 17 (10-01).
   - NOR Test / Sampling goes to row 18 (10-02).
   - Then clear the contents of rows 19–21, but keep the rows.
   - Row 20 text: change "Scheduled NOR Arena Familiarization (Day -1)" to "(Day 1)" when you move it.
3. **Leave the header formula alone.** B10 builds the dates from Registry `N` and `T`; after this change it already shows 09-30, 10-01 and 10-02.

**Tab-level text:**
- **E4:** "1 Day test · Scheduled Day -2 (2026-09-30 · All cohort mice)" becomes "Day 0 (2026-09-30 · All cohort mice) · 15:00".
- **Phase 3 and Phase 4 (row 4, to the right of E4):** "Day -1 (2026-10-01)" becomes "Day 1 (2026-10-01) · 15:00". "Day 0 (2026-10-02)" becomes "Day 2 (2026-10-02) · T1 15:00 → T2 +2 h → sampling".
- **B5 guide:** replace with "Single-row daily logging (7 days: 2026-09-26 to 2026-10-02) · Handling Day −4 to −1 → Y-Maze Day 0 → NOR Habituation Day 1 → NOR Test & Sampling Day 2 (protocol: Acute_SD_Behavioral_Protocol)".

**Registry headers:**
- N5 becomes "Y-maze (Day 0)".
- O5 becomes "NOR test + sampling (Day 2)".
- The formulas `N = T−2` and `O = T` stay as they are.

## Point 3: subtract the tag from body weight

The weight measured after surgery (Registry `K`) includes the implanted tag, about 2.7 g according to Kissei's spec. The weight before surgery (`I`) does not.

1. **Store the tag mass as a constant.** On `Config`, in the constants block, add a row: `Nanotag mass (g) | 2.7 | Kissei spec "about 2.7 g"; subtracted from any body weight measured with the tag implanted`. Refer to it with an absolute reference (for example `Config!$B$n`), or give it a named range such as `NANOTAG_MASS`.
2. **Registry L7:L11 and L13:L17:** `=IF(OR(I7="",K7=""),"",(K7-NANOTAG_MASS-I7)/I7)`.
3. **Registry I18:** replace "nanotag not weighted" with "I = body weight before surgery (no tag). K and sampling K include the ~2.7 g tag; L subtracts it."
4. **Sampling L7 onward** (currently `(K-J)/J`): the tag is in both weights, so it cancels in the numerator. Only the denominator is off.
   - If the tag is still implanted when the mouse is weighed at sampling: `=IF(OR(K7="",J7="",J7=0),"",(K7-J7)/(J7-NANOTAG_MASS))`.
   - If the tag is removed before that weighing: `(K7-(J7-NANOTAG_MASS))/(J7-NANOTAG_MASS)`.
   - Ask the user which case applies.

**Check:** Registry `L` should show these values.

| Mouse | L (was → now) |
|---|---|
| 41 | +7.6% → −1.3% |
| 42 | +8.5% → −0.3% |
| 43 | +8.6% → −1.1% |
| 44 | +6.3% → −2.2% |
| 49 | +15.6% → +6.0% |
| 45 | +7.5% → −1.3% |
| 46 | +9.6% → +0.3% |
| 47 | +10.2% → +0.7% |
| 48 | +7.3% → −1.3% |
| 50 | +8.6% → −0.3% |

## Point 4: age at sampling

- **Registry U7:U11 and U13:U17:** `=IF(AND(ISNUMBER(D7),ISNUMBER(T7)),ROUND((T7-D7)/7,1),"")`.
  - It currently uses `ROUNDUP(...,0)`, so 127 days (18.1 weeks) shows as 19 and falsely triggers the warning.
- **Check:** every mouse should show **18.1**. `NANOTAG sampling!E7` onward (an array formula pulling from the registry) should update by itself. Its amber warning (outside 17.5–18.5) should switch off.

## Point 5: baseline start for mice 49 and 50

- **Registry Q11 and Q17:** the formula `=F+13` gives 09-14. Change it to `=F11+14` (and `=F17+14`), which gives **2026-09-15**.
- **Registry V11 and V17** (currently empty): "Homecage baseline 1 day only: 2026-09-15 09:00 → 09-16 09:00".
- **Leave `R` and `S` as they are:** R11/R17 (`=F+16`, 09-17) and S (`=R+3`, 09-20).
- **Check:** in `NANOTAG recordings`, G13 (mouse 49) and G18 (mouse 50) are array formulas. They should now show 09-15. If they don't, find out what they read from; do not type over them.

## Point 6: History tab, tag 20643 (row 7)

- **B7:** "IN mouse" becomes "Explanted, kept (mouse dead 2026-09-28)".
- **G7:** "Active in NS-SL" becomes "HLBNSSL43 died 2026-09-28 ~10:00 during restraint for tag read. Run 1 data read (ends 09-28 08:59:48). All data from this mouse discarded from analysis. Tag explanted and kept".
- **Leave C7:E7 alone.** They are array formulas.

## Point 7: sampling tab, mouse 43 (row 9)

- **M9 (Sampling Info):** "NOT SAMPLED: died 2026-09-28".
- **S9 (Note):** "Excluded; all data discarded". Keep the row, and grey the text if the sheet's styling allows it.
- **A5 banner:** change "n=5" to "n=4 sampled (43 died 09-28)".
- **Only check, don't change:** the NS-SL intake grid and the Summary tab should not count 43's blank days after 09-28 as zero intake. If they do, report it; the user didn't approve changes there.

## Point 8: leave it

**Registry V9 (43's note):** leave the text unchanged. The user confirmed no IACUC report is needed.

## Point 9: leave it

**Mouse 43's entries in `NANOTAG behavioral`:** leave them unchanged; they are a history log. Point 2 still relabels its Day column and moves its test rows, the same as the other blocks.

## Point 10: recording windows (`NANOTAG recordings`)

**Header text:**
- **G4:** "12 days (Split 8d + 4d)" becomes "Analysed: homecage baseline 3 d + Run 1 8 d. Run 2 recorded, discarded".
- **E6 (formula text):** rewrite so it no longer says "Protocol requires 12 days total: Run 1 = 8 days, Run 2 = 4 days". Instead: "Run 1 = 8 days (Sun 09-20 10:00 → Mon 09-28 ~09:00). Run 2 = from 1 h after extraction handling until auto-stop Sun 10-04 ~13:00; discarded because it overlaps behavioural testing (Day 0 to Day 2)."
- **G7:** leave as "HOMECAGE ACTIVITY (3-Day: 09:00 AM - 09:00 AM Day 3)". Add "(49, 50: 1 day, 09-15)".
- **M7:** "(12 Days Total: 8-Day Run 1 + 4-Day Run 2 Split)" becomes "(Run 1 8 d analysed · Run 2 discarded)".
- **P8:** "Run 2 Status (4d)" becomes "Run 2 Status (discarded)".

**New columns to the right of U** (G and M are array formulas, so don't put times there):
- **Baseline start / end:** 2026-09-14 09:00 / 2026-09-17 09:00. Mice 49 and 50: 2026-09-15 09:00 / 2026-09-16 09:00.
- **Run 1 start / last bin:** 2026-09-20 10:00 / 2026-09-28 08:59:48. Mouse 41's last bin is 08:57:00.
- **Run 2 start:** take the exact value from the `Start date_Activity` field in each mouse's run 2 CSV header once it has been exported. The handling log gives approximate extraction times for most mice; 47 and 48 only say "PM Session".
- **Run 2 planned stop:** 2026-10-04 ~13:00 (auto). Note that this is after sampling on 10-02.
- **Excluded windows:** see point 11.

**Status cells:**
- **I9:I18 (homecage data lifecycle):** "Analysed 2026-09-28". J/K/L (activity, temperature, sleep): "done".
- **R/S/T/U for run 1:** "Run 1 analysed 2026-09-28; Run 2 discarded".
- **Row 11 (mouse 43):** I11 and R11 become "Excluded: mouse died 09-28, all data discarded".

## Point 11: excluded window

In the "Excluded windows" column from point 10, for every mouse: "2026-09-28 08:45–11:00, tag extraction handling (run 1 data ends 08:59:48, so 08:45–09:00 is removed)".

## Point 12: test times and the order mice are tested in

Planned times go in the Time column (D/K) of the Day 0–2 rows in each behavioral block. Actual times get filled in on the day.

- **Day 0, Y-maze:** "Cages to holding room 14:30 (30 min, ~150 lux) · 15:00 start, one mouse at a time · 8 min free exploration + 2 min 70% EtOH clean/dry".
- **Day 1, NOR habituation:** "Holding room 14:30 · 15:00 start, one at a time · 10 min empty arena 50×50 cm, 20 lux".
- **Day 2, NOR test:** "T1 from 15:00 one at a time (10 min, 2 identical objects) → each mouse's own T2 = its T1 + 2 h (first ~17:10) → sampling straight after T2 (first ~17:25)".
- **Record the actual T1 start, T2 start and dissection time for each mouse.** Use `NANOTAG sampling!P` (Dissection time) for the last one. With 9 mice tested one at a time, sampling will run from about 17:25 to 19:00, so the actual time matters for the oxidative-stress assays.
- **This batch (NS-SL, NW-SL):** no sleep deprivation. The mice are undisturbed from 09:00 until the move to the holding room.
- **For the next sleep-deprivation batch** (not this sheet section, carry it forward):
  - Deprivation runs 09:00–15:00, and every mouse is kept awake until the last mouse has finished; the same on the NOR days.
  - Log each mouse's test start and end, plus the time the whole group's wake period ended.
  - Two things to settle with the user before that batch:
    - The protocol's 30-minute holding-room acclimation clashes with deprivation running until 15:00.
    - It isn't clear whether the mice are kept awake during the 2 h NOR retention interval.

## Tag position (user note)

- **Registry P7:P11 and P13:P17** (Surgery notes, currently empty): "Implanted under the skin at the neck, pushed toward the right; after healing migrated to the right dorsolateral flank".
- **`NANOTAG recordings` F9:F18 (Surgery Notes):** check whether these mirror Registry `P` through a formula. If so, leave them; if not, copy the same text in.
- **`NANOTAG recordings` config block (rows 4–6):** add a cell "Activity threshold 170/170 (Kissei mouse-neck value). Actual site: right flank, not validated by Kissei; counts are relative units within this study".

---

## Not approved, don't do

- Changing how battery days are counted (History `E`).
- Removing the "Battery Replaced" column.
- Changing the SOD1 bottle count on Config.
- Adding the substrain (6JBomTac).
- Changing any intake grid or the Summary tab.

## Separate from the sheet: analysis code

For whoever runs `analysis/cohort.py`. Not the sheet agent's job. **Done 2026-09-28** in `analysis/cohort.py`.

- **Drop mouse 43** from every table, figure and test. Part 1 is then n=4 SOD1 against n=5 water.
- **Mask the point 11 window:** 2026-09-28 08:45–11:00.
- **Don't read part 2 / run 2** from the HLBNSL folder, and keep `load()` from picking up a `*part2*` folder.
- **Record the tag site in the code comments:** right flank, threshold 170 (the neck value).
