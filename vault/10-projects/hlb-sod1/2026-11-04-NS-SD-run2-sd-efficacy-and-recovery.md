---
type: experiment
area: hlb-sod1
status: active
created: 2026-11-04
summary: "NS-SD / NW-SD tag Run 2 (10-30 19:00 → 11-04), 5 vs 5: SD effective and equal in both arms (all 10 mice below baseline on both SD days); recovery rebound after SD day 1 no detectable SOD1 difference (+188 vs +163 min, CI −68 to +130); undisturbed days 8-10 no detectable difference; Y-maze sequences still to score"
cohort: NS-SD + NW-SD (HLBNSSD51-55, HLBNWSD56-60)
tags: [experiment, nanotag, sod1, sleep-deprivation, recovery, ns-sd, nw-sd]
---

# NS-SD / NW-SD, tag Run 2: SD efficacy and recovery (2026-11-04)

> [!abstract] TL;DR
> - **SD worked, and equally in both arms.** All 10 mice slept less than at baseline in 09:00-15:00 on both SD days.
>   SD day 1: 10.3 vs 8.1 % asleep (SOD1 vs water), change −58.0 vs −64.7 points, SOD1 − water +6.7 (95 % CI −3.5 to
>   +16.6, p = 0.20). SD day 2: 16.4 vs 17.0 %, −51.9 vs −55.9 points (+4.0, CI −4.8 to +13.5, p = 0.35). Real SD on day 2,
>   09:00 to each mouse's Y-maze: 7.0 vs 7.2 h, 5 % asleep in the extra hours.
> - **Recovery after SD day 1: no detectable SOD1 difference.** Rebound against the same clock hours at baseline:
>   ZT6-12 +39 vs +41 min, dark +149 vs +122 min, total +188 vs +163 min, SOD1 − water +25 min (95 % CI −68 to +130,
>   p = 0.60). Both arms show a clear rebound, mostly in the dark phase.
> - **Undisturbed days 8-10 (10-31 → 11-03): no detectable difference.** Change in total sleep from baseline +75 vs
>   +71 min/day (p = 0.94); light, dark, bouts, rhythm amplitude all p ≥ 0.14. Same answer without 59.
> - **No sleep after SD day 2:** mice went from SD to the Y-maze and were kept awake until sampling (~20:00); the tags
>   stopped at 19:00.
> - 🛑 Report on its own: not pooled with the EEG cohorts, never "the nanotag agrees"
>   ([[2026-10-06-eeg-and-nanotag-findings-reported-separately]]).

## Data
- Raw: SKIM NAS `02_Data_Sleep/andrea/HLBNSD_raw/261104_HLBNSSD/` (20 files + 57 re-export + `README.txt`, sha256 read-back
  23/23, 2026-11-04); local `~/sleep-data/hlbnsd/261104_HLBNSSD/` (ThinkPad). Run 1 baseline from `261030_HLBNSSD`.
- Files 56-60 are named `HLBNSSD_*` but are the water mice HLBNWSD56-60; the code takes the mouse from the header tag ID.
- **HLBNWSD57's first CSV export was corrupted** on the USB stick (NUL bytes, rows spliced from 11-01 11:35). Andrea
  re-exported it from the same `.nta` (identical to the USB copy): `HLBNSSD_57_2_redone.csv`, 36,000 continuous 12 s rows,
  used here. The corrupted file stays on the NAS, marked in the README.
- HLBNWSD60's Run 2 starts 19:05, not 19:00 (25 bins); no window uses 19:00-19:05 on 10-30.
- Y-maze start times (Andrea, 2026-11-04): from 15:00, about 15 min per mouse in the order 51, 56, 52, 57, 53, 58, 54, 59,
  55, 60, the last finished about 17:40; entered as 15:00 + 15 min × position, so **approximate**. Mice were kept awake
  after the Y-maze until sampling at about 20:00. `nanotag/analysis/behavior/NSSD_ymaze_hand_scoring.csv`.

## Method
`nanotag/analysis/cohort_sd.py --run2`, runbook [[2026-11-03-NS-SD-run2-and-ymaze-runbook]]. Sleep = immobility ≥ 48 s,
12 s bins. SOD1 − water = exact permutation p, CI by inversion, mouse = unit. HLBNWSD59 (tag at the shoulder) read as
change, every change repeated without it. Console: `nanotag/analysis/out/HLBNSSD/run2_console.txt` (git-ignored).

## Results

**SD efficacy, % of 09:00-15:00 asleep, against the same mouse's baseline hours (10-22, 10-23)**

| | SOD1 (5) | water (5) | SOD1 − water, 95 % CI | p |
|---|---|---|---|---|
| baseline 09:00-15:00 | 68.3 ± 3.7 | 72.8 ± 1.7 | −4.6 | 0.33 |
| SD day 1 (11-03) | 10.3 ± 2.2 | 8.1 ± 1.7 | +2.2 | 0.47 |
| SD day 2 (11-04) | 16.4 ± 3.6 | 17.0 ± 3.8 | −0.5 | 0.92 |
| change, day 1 (points) | −58.0 ± 4.5 | −64.7 ± 1.0 | +6.7 (−3.5, +16.6) | 0.20 |
| change, day 2 (points) | −51.9 ± 3.0 | −55.9 ± 2.7 | +4.0 (−4.8, +13.5) | 0.35 |
| sleep lost, day 1 (min) | 209 ± 16 | 233 ± 4 | −24 (−60, +13) | 0.19 |
| real SD, day 2 (h) | 7.0 ± 0.4 | 7.2 ± 0.4 | −0.2 | 0.69 |

![[2026-11-04-NSSD-run2-sd-efficacy.png]]

**Recovery after SD day 1 (11-03 15:00 → 11-04 09:00), against the same clock hours at baseline**

| rebound (min) | SOD1 (5) | water (5) | SOD1 − water, 95 % CI | p |
|---|---|---|---|---|
| ZT6-12 (15:00-21:00) | +39 ± 9 | +41 ± 5 | −2 (−27, +26) | 0.89 |
| dark (21:00-09:00) | +149 ± 32 | +122 ± 16 | +27 (−56, +120) | 0.47 |
| total | +188 ± 38 | +163 ± 18 | +25 (−68, +130) | 0.60 |

![[2026-11-04-NSSD-run2-recovery.png]]

**Undisturbed treatment days 8-10 (10-31 09:00 → 11-03 09:00), change from baseline**

| | SOD1 | water | p |
|---|---|---|---|
| total sleep (min/day) | +75 | +71 | 0.94 |
| light sleep (points) | +5.3 | +1.9 | 0.21 |
| dark sleep (points) | +5.2 | +8.0 | 0.29 |
| dark activity (counts/h) | −423 | −1,160 | 0.14 |
| rhythm amplitude | +0.008 | +0.014 | 0.89 |

![[2026-11-04-NSSD-run2-change-days-8-10.png]]

![[2026-11-04-NSSD-run2-actograms.png]]

## Reading
- SD did what it was meant to: 3.5 to 4 h of sleep removed on day 1, equally with SOD1 or water, so the recovery and the
  Y-maze compare like with like.
- The rebound is clear in both arms, and SOD1 neither enlarged nor shrank it within what 5 vs 5 can see (the CI spans
  about −1 h to +2 h). Immobility shows rebound as extra minutes only, not its depth.
- Run 1's dark-activity lead (+616 vs +265 counts/h, p = 0.040) did not hold on days 8-10: dark activity fell in both
  arms (−423 vs −1,160, p = 0.14).
- The 11-02 dark phase is quieter in every mouse of both arms in the actograms; it raises days 8-10 sleep for all and
  does not bias SOD1 vs water. Cause unknown (ask Andrea).

## Still open
- [ ] Y-maze: score the arm sequences from the videos into the sheet, then `behavior/ymaze_nssd.py` (runbook step 3).
- [ ] 11-02 dark phase quieter in all mice: anything in the room that night?
- [ ] Weekend bottle 10-31 → 11-02 (intake note): one bottle for two days?
