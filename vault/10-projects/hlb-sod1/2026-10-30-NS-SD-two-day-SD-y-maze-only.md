---
type: decision
area: hlb-sod1
status: done
created: 2026-10-31
summary: "NS-SD / NW-SD re-planned 2026-10-30: SD only Tue 11-03 + Wed 11-04 09:00-15:00, Y-maze Wed 15:00 then sampling, NOR dropped; tag Run 2 from 10-30 19:00 after a 09:00-19:00 gap"
cohort: NS-SD + NW-SD (HLBNSSD51-55, HLBNWSD56-60)
tags: [decision, nanotag, sod1, sleep-deprivation, y-maze, nor, ns-sd, nw-sd]
---

# 2026-10-30: NS-SD / NW-SD, two days of SD, Y-maze only, NOR dropped

> [!abstract] Decision
> **We chose** two days of sleep deprivation (Tue 11-03 and Wed 11-04, 09:00-15:00), the Y-maze at 15:00 on Wednesday,
> sampling straight after each mouse's Y-maze, and **no NOR**, **because** NOR needs three sessions and sleep after
> training, which the SD schedule and the staggered test times disturb unevenly between mice, while the Y-maze is one
> session that gives working memory, exploration and locomotion together (Andrea, 2026-10-30).
> Applied to the sheet as CHG-012 → CHG-016 on 2026-10-31 ([[sod1-sheet-change-log-workflow]]).
> Study: [[2026-10-19-NS-SD-NW-SD-nanotag-study]].

## The question
The 2026-10-21 plan had four SD days (Mon 11-02 → Thu 11-05), Y-maze Tue 11-03, NOR habituation Wed 11-04, NOR T1/T2
and sampling Thu 11-05 ([[hlb-sod1-design]]). Can NOR be run cleanly under SD with ten mice tested one after another,
and is the Y-maze enough to answer the cognition aim for HLB?

## Options
| Option | For | Against |
|---|---|---|
| Keep 4 d SD + Y-maze + NOR (old plan) | Same test set as HLBNSL | Three NOR sessions on SD days; memory consolidation after T1 depends on sleep, which SD and the test order change per mouse; sleepy mice explore less, so more fall under the 20 s exploration minimum; more handling |
| **2 d SD + Y-maze, no NOR (chosen)** | One session, no training or retention interval; alternation plus arm entries, distance and speed from one trial; less handling | Loses object recognition memory; the SD dose is shorter than the protocol's 4 days |

## Decision and reasons
- **Schedule (Andrea, 2026-10-30):** undisturbed Sat 10-31 → Mon 11-02; SD Tue 11-03 and Wed 11-04 09:00-15:00, gentle
  handling; Y-maze Wed 15:00 in the interleaved order 51, 56, 52, 57, 53, 58, 54, 59, 55, 60; sampling straight after
  each Y-maze. Mice stay awake until their own test, so the later mice get a longer SD.
- **Why NOR was dropped:** NOR needs habituation, T1, a retention interval and T2. Recognition memory consolidates in
  sleep after T1, so with staggered testing each mouse would get a different SD length and a different chance to sleep
  after training: a confound possibly larger than any SOD1 effect. That post-training SD impairs object recognition in
  mice is reported by Palchykova et al. 2006 (cited from memory, to verify before it goes to HLB).
- **HLBNSL NOR as a supporting point only:** in rested mice it needed counterbalancing and validated scoring to read
  cleanly (novel object always on the preferred side; the recognition result depends on the tracking model; hand
  scoring pending: [[2026-10-25-HLBNSL-nor-pose-results]]). Those are fixable design and scoring issues, not evidence
  that NOR fails, so they are not the main reason.
- **Why the Y-maze is enough for the cognition aim:** spontaneous alternation measures working memory, which is
  hippocampal and sensitive to SD; the same 480 s trial gives arm entries, distance and speed, so a change in
  alternation can be separated from a change in activity. HLBNSL ran the same test (hand-scored SA% SOD1 60.5 vs water
  62.8, n = 4 vs 5: [[2026-10-25-HLBNSL-ymaze-hand-scored-results]]), so SL vs SD can be shown side by side.

**How the data will be shown (plan, 2026-10-30):**
1. Undisturbed sleep, SOD1 vs water, 10-31 09:00 → 11-03 09:00 against baseline.
2. Equal SD dose in both arms: wake during each SD day and during the wait before the Y-maze, from the tags.
3. Recovery sleep Tue 15:00 → Wed 09:00, the only window between the two SD days.
4. Y-maze: SA%, arm entries, distance, speed.
5. Y-maze against each mouse's real SD length (09:00 Wed to its Y-maze start), coloured by arm; record every start time.
6. Per mouse: Tuesday's recovery sleep against Wednesday's alternation.
Each SOD1 mouse is tested next to a water mouse with almost the same SD length, so test slots can be analysed as pairs.

**Limits to state up front:** rested vs deprived is a comparison between batches (different mice, SOD1 15 vs 11 days,
age, date), not a within-batch control, so "consistent with" an SD effect, not "SD caused". HLBNSL tested in blocks
(all SOD1 first), the SD batch interleaves. n = 5 per arm: effect sizes, not p-values. Nanotag and EEG findings stay
separate ([[2026-10-06-eeg-and-nanotag-findings-reported-separately]]).

**Tag recording around the change:** Run 1 stopped at its programmed end 10-30 09:00. Tags were read 10-30 18:00-19:00,
all data extracted, and Run 2 reserved from 10-30 19:00 to Wed 11-04 19:00, 12 s activity only. Lost: 10-30
09:00-19:00, all light phase; the dark phase from 21:00 is recorded.

**Consequences:** SOD1 / UV water runs 11 days at sampling (10-24 → 11-04), not 12; age at sampling 17.3 weeks.
The analysis windows fixed on 2026-10-19 in the study note no longer fit; the new ones are listed there as a dated
deviation.

## What would make us revisit it
- A mouse cannot be kept awake to its test slot, or the tags show the two arms got different amounts of SD.
- HLB asks specifically for object recognition data.
