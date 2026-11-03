---
type: experiment
area: hlb-sod1
status: active
created: 2026-11-03
summary: "HLB EEG re-score of the four batches (2026-11-03): 15 paired W/NR/R mice instead of 3; no detectable SOD1 effect on baseline sleep; after deprivation still one mouse per SD arm, and the S-SD one hinges on its artefact mask"
tags: [eeg, emg, sleep-scoring, hlb, sod1, result]
---

# HLB EEG sleep: re-score of the four batches (2026-11-03)

> [!abstract] TL;DR
> - **We were throwing away good mice.** I re-scored all 64 mouse-windows (4 batches × 8 mice ×
>   baseline/recovery) with the professor's SleepStager rule on a mains-free EMG
>   ([[hlb-eeg-scoring-method-2026-11]]). **15 mice now have usable W / NR / R in both windows**, against
>   3 whose two old verdicts were both SCOREABLE (the 2026-09-30 note counted 1, 0, 1 (2), 1 (3) per batch).
>   The gain is almost all in the ad libitum batches: W-SL 7 of 8, S-SL 6 of 8.
> - **The deprivation arms did not improve.** W-SD and S-SD still have one paired mouse each
>   (HLBWSD08, HLBSSD18). Their recoveries are mostly lost to dead EEG or technical EMG, not to the criteria.
> - **Baseline, SOD1 vs water** (on treatment, before deprivation): no detectable difference.
>   Sleep was 52.0 % vs 52.5 % of usable time (n = 10 vs 11, p = 0.81, 95 % CI −4.7 to +3.6 points),
>   and the smallest effect this sample could detect is about 6 points. EEG-alone NREM gives the same answer.
> - **Recovery − baseline:** no SOD1 effect without deprivation (S-SL +2.1 vs W-SL +0.1 points, p = 0.52).
>   With deprivation it is n = 1 per arm, a case. HLBWSD08 gains +9.3 points of sleep, a robust figure.
>   HLBSSD18 gains +18.1, but only **+1.5** if its EMG-rail artefact epochs (27 % of the recovery,
>   mostly vigorous wake) count as wake. Do not read anything into S-SD vs W-SD.
> - Every window was reviewed by agents reading the traces, and the newly usable ones were attacked
>   by skeptics. The review found three flaws in the screen. All three were fixed in code and
>   everything re-scored, and 7 borderline windows were demoted by review evidence (none promoted).
> - **Checked against Andrea, light phase only** (added the same day, from the workstation backup):
>   κ 0.952 over the 8,429 epochs of HLBSSL33 R she reviewed. The HMM, which never sees the rule,
>   reaches κ 0.930. W / NR / R shares match within 1 point. See [[#Check against Andrea's scoring]].

## Old vs new, per batch

| batch | paired W/NR/R, re-score | paired, old verdicts | baseline windows usable (A/B) | recovery windows usable (A/B) |
|---|---|---|---|---|
| W-SD (water + SD) | **1** (HLBWSD08) | 1 (HLBWSD08) | 3 of 8 | 1 of 8 |
| S-SD (SOD1 + SD) | **1** (HLBSSD18) | 0 | 4 of 8 | 1 of 8 |
| W-SL (water) | **7** | 1 (2) | 8 of 8 | 7 of 8 |
| S-SL (SOD1) | **6** | 1 (3) | 6 of 8 | 8 of 8 |

Tiers: **A** W/NR/R over the whole window, **B** W/NR/R on ≥ 6 light + ≥ 6 dark hours, **C** NREM
from the EEG alone, **D** sleep vs wake from the EMG alone, **X** nothing. Definitions and tests:
[[hlb-eeg-scoring-method-2026-11#Usability: the tests and the tiers]].

![[2026-11-03-hlb-eeg-fig1-tiers.png]]

## Results

All shares are of **usable** time. REM % is not reported (the rule partly fixes it by construction).
Exact numbers, per mouse, in `eeg-emg-analysis/rescore_2026_11/results/stats.txt` and `per_mouse_segments.csv`.

**1. Baseline, SOD1 vs water** (tier A/B, all four batches; every baseline was already on treatment)

| measure | segment | SOD1 | water | diff (points) | p | 95 % CI | MDE |
|---|---|---|---|---|---|---|---|
| sleep % | 24 h | 52.0 (n = 10) | 52.5 (n = 11) | −0.5 | 0.81 | −4.7, +3.6 | 6 |
| sleep % | light | 71.7 | 72.2 | −0.5 | 0.78 | −4.5, +3.4 | 6 |
| sleep % | dark | 31.1 | 32.6 | −1.5 | 0.61 | −7.2, +4.3 | 8 |
| NREM % | 24 h | 45.8 | 46.5 | −0.6 | 0.75 | −4.4, +3.2 | 5 |
| sleep %, SL batches only | 24 h | 51.9 (n = 6) | 54.3 (n = 8) | −2.4 | 0.39 | −7.7, +2.8 | 8 |
| EEG-alone NREM % | 24 h | 40.8 (n = 10) | 40.9 (n = 12) | −0.1 | 0.93 | −2.8, +2.5 | 4 |

p = exact permutation; CI = Welch; MDE = smallest difference detectable at 80 % power.

![[2026-11-03-hlb-eeg-fig2-baseline-sleep-by-hour.png]]

**2. Recovery − baseline, same mouse, ZT4–24** (the SD recoveries only exist from 13:00, so both
windows are cut to ZT4–24)

| comparison | n | change in sleep % (points) | p |
|---|---|---|---|
| S-SL vs W-SL (SOD1 without SD) | 6 vs 7 | +2.1 vs +0.1 | 0.52 |
| W-SD vs W-SL (SD, water) | 1 vs 7 | +9.3 vs +0.1 | a case |
| S-SD vs S-SL (SD, SOD1) | 1 vs 6 | +18.1 vs +2.1 | a case |
| S-SD vs W-SD | 1 vs 1 | +18.1 vs +9.3 | a case, and see below |

> [!warning] HLBSSD18's recovery depends on the artefact mask
> 27 % of HLBSSD18's recovery epochs touch the EMG rail. The skeptic showed they are flat ~400 µV
> plateaus during vigorous wake, and the screen excludes them. Counted as wake, its sleep gain falls
> from +18.1 to **+1.5** points (ZT4–24). No other paired mouse moves more than 1 point
> (HLBWSD08 stays at +9.3). The S-SD recovery is therefore not interpretable.

![[2026-11-03-hlb-eeg-fig3-recovery-minus-baseline.png]]

**3. NREM δ (slow-wave activity) in the first 4 h of recovery (ZT4–8), % of the same mouse's baseline ZT4–8:**
W-SD 114 % (n = 1) and S-SD 117 % (n = 1), against W-SL 107 % (n = 7) and S-SL 93 % (n = 6).
Both SD mice show the expected rebound, but each arm is one mouse.

![[2026-11-03-hlb-eeg-fig4-nrem-delta-time-course.png]]

![[2026-11-03-hlb-eeg-fig5-state-spectra.png]]

## Check against Andrea's scoring

Added 2026-11-03, after the workstation backup drive was plugged in. Source: Andrea's SleepStager save
`HLBSSL33_R_AN_261007-2034`, the only scored recording on the drive, now copied to
`~/sleep-data/hlb-rescore-2026-11/handscore/`. Script: `rescore_2026_11/handscore_check.py`, output in
`results/handscore_check_hlbssl33_r.txt`.

> [!warning] What this save is, and what it is not
> It is not blind scoring. It is the SleepStager rule's first pass, which Andrea reviewed epoch by
> epoch up to epoch 8,441 (ZT0–9.4, **light phase only**) and changed in 243 epochs (2.9 %).
> Agreement with any rule output is therefore partly built in. The independent parts are the HMM,
> which takes no rule input, and her 243 corrections.

| against Andrea's labels, epochs 1–8,441 | κ | agreement |
|---|---|---|
| SleepStager first pass (where she started) | 0.947 | 97.3 % |
| **re-score, final (gap EMG)** | **0.952** | 97.5 % |
| re-score rule on the 20–90 Hz EMG | 0.949 | 97.3 % |
| HMM second scorer (no rule input) | 0.930 | 96.2 % |
| EEG alone, NREM vs not | 0.883 | – |

- **Shares:** W 25.9 % (hers) vs 26.0 % (re-score), NR 62.3 vs 63.1 %, R 11.7 vs 10.9 %.
- **Her 243 corrections show the rule's remaining error.** It calls NREM where she saw REM onset
  (94) or wake (122). The re-score repeats the rule on 65 % of those epochs. The HMM gives her label
  on 69 % of them.
- **Implication:** where the rule and the HMM disagree is where a human should look first. In the
  13,159 epochs she has not reviewed, that is 664 epochs in 281 places, listed as a checklist in
  [[hlbssl33-r-review-list-rule-vs-hmm]].
- **Agents:** only 4 of the agents' contested epochs fall in her range. They matched her on 2,
  too few to judge.

### Dark phase, ZT12–15 (added 2026-11-03 evening)

Andrea then reviewed epochs 10,801–13,624 (ZT12.0–15.1, early dark) epoch by epoch and saved
(`last_epoch` 13,624). Epochs 8,442–10,800 were skipped (no change there). Same method, rule-anchored.
Output `results/handscore_check_hlbssl33_r_to13624.txt`; the save is copied to
`~/sleep-data/hlb-rescore-2026-11/handscore/save-to-13624/`. The light block re-counts to 231 corrections
because 12 of the 243 were set to X (artefact), which the kappa leaves out.

| against Andrea's labels | light 1–8,441 | **dark 10,801–13,624** | all 11,249 |
|---|---|---|---|
| SleepStager first pass | 0.947 | 0.947 | 0.952 |
| **re-score, final** | **0.952** | **0.941** | **0.954** |
| re-score rule, 20–90 Hz EMG | 0.949 | 0.947 | 0.953 |
| HMM (no rule input) | 0.930 | 0.886 | 0.927 |
| EEG alone, NREM vs not | 0.883 | 0.812 | 0.877 |

- **The re-score holds in the dark:** κ 0.941, 97.3 % agreement. Shares W 66.6 % (hers) vs 65.2 %,
  NR 32.1 vs 33.1 %, R 1.3 vs 1.7 %.
- **Her 69 dark corrections** are mostly NR → W (43) and R → W (16): brief arousals the rule kept as
  NREM, and theta-rich wake without atonia the rule called REM. Plus NR → R 7, R → NR 3.
- **The rule-vs-HMM list does not find the dark errors.** Of her 69 corrections, 23 (33 %) were on
  [[hlbssl33-r-review-list-rule-vs-hmm]]; of the 153 list epochs in the block, she changed 23 (15 %).
  The HMM is weaker in the dark (κ 0.886), so its disagreements point at the wrong places.

### Late dark, ZT18–21.1 (added 2026-11-03, late evening)

Andrea reviewed epochs 16,201–19,028 (ZT18.0–21.1) in full; 13,625–16,200 were skipped. Output
`results/handscore_check_hlbssl33_r_to19028.txt`, save copied to `handscore/save-to-19028/`.

| against Andrea's labels | light 1–8,441 | early dark 10,801–13,624 | **late dark 16,201–19,028** | all 14,077 |
|---|---|---|---|---|
| SleepStager first pass | 0.947 | 0.947 | 0.928 | 0.947 |
| **re-score, final** | **0.952** | **0.941** | **0.932** | **0.949** |
| re-score rule, 20–90 Hz EMG | 0.949 | 0.947 | 0.940 | 0.951 |
| HMM (no rule input) | 0.930 | 0.886 | 0.912 | 0.924 |
| EEG alone, NREM vs not | 0.883 | 0.812 | 0.828 | 0.868 |

- **Lowest of the three blocks, still κ 0.93.** 116 corrections in 2,828 epochs (4.1 %): NR → W 80,
  R → W 19, NR → R 16, W → NR 1.
- **The re-score over-counts sleep in the late dark:** NR 49.1 % vs her 46.6 %, sleep 56.5 vs 54.3 %
  (+2.2 points), because it keeps brief arousals as NREM. In the light and early dark the gap is ≤ 1.4
  points. The same rule scores both arms, so the bias should mostly cancel in SOD1 vs water; absolute
  sleep % in the dark is slightly high.
- **The list did better here but still missed half:** 54 of her 116 corrections (47 %) were on it, and
  54 of its 159 epochs in the block (34 %) needed a change.

## Every mouse

Each name opens the mouse's note: decision, numbers, overview figures, the agent scorer's calls on
the contested epochs, and the skeptic's verdict. "usable h" = hours where EEG and EMG both pass, light + dark.
Old: ✅ SCOREABLE, ❌ NOT SCOREABLE, ❔ NO VERDICT (the 2026-09-30 screen).

### W-SD: water + sleep deprivation

| mouse | rig | baseline | recovery | paired W/NR/R | old (B / R) | usable h, B / R (L+D) | EMG |
|---|---|---|---|---|---|---|---|
| [[hlb-eeg-hlbwsd01\|HLBWSD01]] | A1 | 🟢 A | 🟠 D | no | ✅ / ❌ | 24 (12+12) / 0 (0+0) | gap |
| [[hlb-eeg-hlbwsd02\|HLBWSD02]] | A2 | 🟢 A | 🟠 D | no | ✅ / ❌ | 24 (12+12) / 0 (0+0) | gap |
| [[hlb-eeg-hlbwsd03\|HLBWSD03]] | C1 | 🔴 X | 🔴 X | no | ❌ / ❌ | 18 (11+7) / 0 (0+0) | gap |
| [[hlb-eeg-hlbwsd04\|HLBWSD04]] | B2 | 🟡 C | 🟠 D | no | ❌ / ❌ | 24 (12+12) / 0 (0+0) | gap |
| [[hlb-eeg-hlbwsd06\|HLBWSD06]] | C2 | 🟠 D | 🟠 D | no | ❌ / ❌ | 7 (7+0) / 3 (3+0) | gap |
| [[hlb-eeg-hlbwsd07\|HLBWSD07]] | D1 | 🔴 X | 🔴 X | no | ❌ / ❌ | 0 (0+0) / 0 (0+0) | gap |
| [[hlb-eeg-hlbwsd08\|HLBWSD08]] | D2 | 🟢 A | 🟢 A | **yes** | ✅ / ✅ | 24 (12+12) / 20 (8+12) | gap |
| [[hlb-eeg-hlbwsd09\|HLBWSD09]] | B1 | 🔴 X | 🔴 X | no | ❌ / ❔ | 0 (0+0) / 0 (0+0) | gap |

### S-SD: SOD1 + sleep deprivation

| mouse | rig | baseline | recovery | paired W/NR/R | old (B / R) | usable h, B / R (L+D) | EMG |
|---|---|---|---|---|---|---|---|
| [[hlb-eeg-hlbssd11\|HLBSSD11]] | A1 | 🟢 A | 🔴 X | no | ❌ / ❌ | 23 (11+12) / 20 (8+12) | gap |
| [[hlb-eeg-hlbssd12\|HLBSSD12]] | A2 | 🟢 B | 🔴 X | no | ❌ / ❌ | 20 (12+8) / 8 (3+5) | gap |
| [[hlb-eeg-hlbssd13\|HLBSSD13]] | B1 | 🔴 X | – | no | ❔ / – | 8 (6+2) / – | gap |
| [[hlb-eeg-hlbssd14\|HLBSSD14]] | B2 | 🟠 D | 🟠 D | no | ❌ / ❔ | 0 (0+0) / 11 (6+5) | gap |
| [[hlb-eeg-hlbssd15\|HLBSSD15]] | C1 | 🟢 A | 🟠 D | no | ❌ / ❌ | 24 (12+12) / 5 (3+2) | gap |
| [[hlb-eeg-hlbssd16\|HLBSSD16]] | C2 | 🔴 X | 🔴 X | no | ❌ / ❌ | 13 (9+4) / 9 (3+6) | gap |
| [[hlb-eeg-hlbssd17\|HLBSSD17]] | B1 | – | 🔴 X | no | – / ❔ | – / 4 (3+1) | gap |
| [[hlb-eeg-hlbssd18\|HLBSSD18]] | D2 | 🟢 A | 🟢 A | **yes** | ❌ / ❌ | 24 (12+12) / 19 (8+11) | gap |
| [[hlb-eeg-hlbssd19\|HLBSSD19]] | D1 | 🔴 X | 🔴 X | no | ❌ / ❌ | 3 (2+1) / 19 (7+12) | gap |

HLBSSD13 (baseline) and HLBSSD17 (recovery) shared rig slot B1 and are two different mice, unpaired by design.

### W-SL: water, ad libitum

| mouse | rig | baseline | recovery | paired W/NR/R | old (B / R) | usable h, B / R (L+D) | EMG |
|---|---|---|---|---|---|---|---|
| [[hlb-eeg-hlbwsl21\|HLBWSL21]] | A1 | 🟢 A | 🟠 D | no | ❔ / ❌ | 23 (12+11) / 0 (0+0) | gap |
| [[hlb-eeg-hlbwsl22\|HLBWSL22]] | A2 | 🟢 A | 🟢 A | **yes** | ✅ / ❔ | 24 (12+12) / 24 (12+12) | gap |
| [[hlb-eeg-hlbwsl23\|HLBWSL23]] | B1 | 🟢 A | 🟢 A | **yes** | ❌ / ✅ | 22 (10+12) / 23 (11+12) | gap |
| [[hlb-eeg-hlbwsl24\|HLBWSL24]] | B2 | 🟢 A | 🟢 A | **yes** | ✅ / ✅ | 24 (12+12) / 24 (12+12) | gap |
| [[hlb-eeg-hlbwsl25\|HLBWSL25]] | C1 | 🟢 A | 🟢 A | **yes** | ❌ / ❔ | 24 (12+12) / 23 (12+11) | gap |
| [[hlb-eeg-hlbwsl26\|HLBWSL26]] | C2 | 🟢 B | 🟢 A | **yes** | ❌ / ❌ | 20 (11+9) / 24 (12+12) | gap |
| [[hlb-eeg-hlbwsl27\|HLBWSL27]] | D1 | 🟢 A | 🟢 A | **yes** | ✅ / ❔ | 24 (12+12) / 24 (12+12) | gap |
| [[hlb-eeg-hlbwsl29\|HLBWSL29]] | D2 | 🟢 A | 🟢 A | **yes** | ❌ / ❔ | 24 (12+12) / 24 (12+12) | gap |

### S-SL: SOD1, ad libitum

| mouse | rig | baseline | recovery | paired W/NR/R | old (B / R) | usable h, B / R (L+D) | EMG |
|---|---|---|---|---|---|---|---|
| [[hlb-eeg-hlbssl31\|HLBSSL31]] | A1 | 🟠 D | 🟢 A | no | ✅ / ❔ | 22 (12+10) / 24 (12+12) | gap |
| [[hlb-eeg-hlbssl32\|HLBSSL32]] | A2 | 🟢 A | 🟢 A | **yes** | ❌ / ❔ | 24 (12+12) / 24 (12+12) | gap |
| [[hlb-eeg-hlbssl33\|HLBSSL33]] | B1 | 🟢 A | 🟢 A | **yes** | ✅ / ✅ | 24 (12+12) / 24 (12+12) | gap |
| [[hlb-eeg-hlbssl34\|HLBSSL34]] | B2 | 🟢 A | 🟢 A | **yes** | ❌ / ❌ | 24 (12+12) / 24 (12+12) | gap |
| [[hlb-eeg-hlbssl35\|HLBSSL35]] | C1 | 🟢 A | 🟢 A | **yes** | ✅ / ❔ | 24 (12+12) / 24 (12+12) | gap |
| [[hlb-eeg-hlbssl38\|HLBSSL38]] | D2 | 🟠 D | 🟢 B | no | ❌ / ❔ | 0 (0+0) / 20 (11+9) | gap |
| [[hlb-eeg-hlbssl39\|HLBSSL39]] | C2 | 🟢 A | 🟢 A | **yes** | ❌ / ✅ | 24 (12+12) / 24 (12+12) | gap |
| [[hlb-eeg-hlbssl40\|HLBSSL40]] | D1 | 🟢 A | 🟢 A | **yes** | ❌ / ❔ | 24 (12+12) / 23 (12+11) | gap |

## Why the old screen lost these mice

25 windows are A or B now and were not SCOREABLE then. 18 of them stopped at rung 2: a chip floor
that carried signal or 60 Hz, or a "usable %" computed on the old EMG. The other 7 failed rung 3,
the r@1min of a 10–124 Hz EMG that mostly reads 60 Hz mains on this rig. Two examples the skeptics tested:

- HLBSSL32 baseline: the raw EMG carries 730 µV of 60 Hz. Between the harmonics the muscle
  separates cleanly. 60 Hz is *lower* in wake, so it cannot drive the wake calls, and the EEG agrees
  (δ AUC 0.95).
- HLBSSD18 baseline: the old r@1min was 0.028 on the hum band. The new one is 0.68 on the
  gap EMG, close to its whole-record persistence (0.77).

Details: [[hlb-eeg-scoring-method-2026-11#Why a re-score]].

## Review decisions

Eight Sonnet scorers read all 64 overviews and staged 456 contested epochs (rule vs HMM).
Their calls agreed with the rule in 59 %, with the HMM in 19 % and with neither in 22 %. 206 of the
456 calls were low confidence, which is what contested epochs are. Four Opus skeptics then tried to
refute the 36 newly usable or tier C windows, and a critic looked for missed data and junk.

**Fixed in code, all 64 re-scored** (method note, warning box): an EEG level gate (dead channels had
passed tier C), an alternation check on the EEG-alone scorer, and the δ AUC hour test limited to
mixed hours.

**Moved by review evidence** (`final_tiers.py`; only demotions, never promotions):

| window | screen → final | why |
|---|---|---|
| HLBSSD12 B | A → B | exactly 20 h; dark ZT18–24 EEG railed, ZT23 kept only by the all-wake exemption |
| HLBSSL38 R | A → B | exactly 20 h; B with the 20–90 Hz EMG; weakest δ separation of the A set |
| HLBWSL26 B | A → B | A only through the EMG-source switch at exactly 20 h; 124 µV mains on the EEG |
| HLBSSD11 R | C → X | EEG does not track state (1-min δ vs EMG r = −0.02; −0.74 at baseline) |
| HLBSSD12 R | C → X | C on exactly 6 light hours, 3 of them flat 400–500 µV EMG plateaus with a 16–20 Hz band |
| HLBSSD16 R | C → X | intermittent EEG contact; C exactly on its bar |
| HLBSSD17 R | C → X | the EEG-alone HMM split off a δ-railing cluster, not NREM |

A move from A to B changes no statistic, because B windows are scored on their usable hours. Full
reviews: `results/review_result.json`; each mouse note carries its own.

## Where everything is

- Method and tests: [[hlb-eeg-scoring-method-2026-11]]. Data layout for figures: [[hlb-eeg-data-backbone]].
  How to rerun: [[hlb-eeg-compute-runbook]].
- Code: `eeg-emg-analysis/rescore_2026_11/` (`ingest` → `features` → `score` → `final_tiers` →
  `backbone` → `stats` / `figures` / `review_pack` / `mouse_notes` / `overview_tables`).
- Small results in the repo: `eeg-emg-analysis/rescore_2026_11/results/` (recordings, screen summary,
  stats, per-mouse segments, final tiers, the full agent review, contested epochs).
- Large data, ThinkPad only for now: `~/sleep-data/hlb-rescore-2026-11/` (backbone 153 MB,
  epoch features 3.1 GB, arrays 40 GB; arrays and features rebuild from the NAS in about an hour).

## Still open

- **Human check, dark phase and other mice.** The check above covers one mouse in the light phase,
  starting from the rule's labels. Still missing: the dark phase, and any mouse scored blind.
- **Professor.** Confirm the gap EMG as the rule's input, the tier bars and the review fixes.
- **Rescue candidates the review named** (each needs a re-fit in `score.py`, not a hand edit):
  - HLBSSL31 B: the EEG fades after ZT20.5, and a fit on the connected part could pair HLBSSL31 (S-SL 7).
  - HLBSSD19 R: 19 both-usable hours, δ AUC 0.81, killed only by the gap EMG's η 0.64.
  - HLBSSD14 R: one dark hour short of B.
  - HLBSSD15 R: flat-EEG dropouts pollute its cuts.
- **Artefact epochs as wake.** EMG-rail epochs are mostly vigorous wake. Make "count them as wake" a
  standing sensitivity in `stats.py`. It matters for HLBSSD18 R and for any future SD recovery.
- **Estimator edge.** 18 of 64 windows get a different tier from the gap and the 20–90 Hz EMG
  (mostly η near 0.70). The tier rule handles it, but the professor should see the list (`tier_gap`, `tier_ss60` in `recordings.csv`).
- **Backbone off this laptop.** Copy `~/sleep-data/hlb-rescore-2026-11/backbone/` to the NAS and S3 so
  figures can be built from any machine.
