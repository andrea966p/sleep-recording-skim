---
name: emg-mains-corrupts-sleep-staging
description: "2026-10-02: stage 3's EMG rms (10-124 Hz at 250 Hz) includes the 60 Hz line; notching 60/120 Hz in the EMG turns 13/13 W-SL light-phase animals SCOREABLE (r@1min 0.59-0.69, wake 22-36 %) vs 8/13 officially. Shuffle control passes. NOT adopted: re-scores published numbers."
metadata:
  type: project
---

🔴⭐⭐⭐ **Mains in the EMG corrupts WAKE staging.** `pipeline/stage3_features.py` stages WAKE by an Otsu split of log EMG rms
(FILT_EMG 10-300 Hz, i.e. 10-124 Hz at the stored 250 Hz), with NO mains removal. An EMG carrying a 60 Hz line about the size of its
quiet tone (10-01 A2: 13-28 µV peak) loses the wake/sleep contrast.

Test (`qc/emg_mains_staging_test.py`: stage 3 unchanged, EMG 60+120 Hz notched Q 30 in memory, official npz SYMLINKED so nothing
official is overwritten; the 'orig' run reproduces every official verdict):
- 10-01 overnight A2: REJECT r@1min 0.19, wake 18.6 % → SCOREABLE 0.323, 29.7 %. B1 ~unchanged (line 4-5 µV).
- W-SL 09-17 + 09-10 light phase: official 8/13 scoreable, r 0.10-0.70, wake 1.9-62 % → **13/13, r 0.59-0.69, wake 22.5-35.8 %**.
- Negative control: notched EMG with 4 s epochs SHUFFLED → r@1min ≈ 0, REJECT (3/3). The notch does not manufacture persistence.

🛑 **NOT adopted.** Changing the EMG measure re-scores every published wake % / r@1min (S-SL n=3, W-SL, W-SD...). It needs dark/full-day
sets, the whole ~12 GB stage-2 archive (scheduled after a recording, heavy) and the falsification suite, then Andrea's decision.
⚠️ Stage 2's npz has `.files`; a dict stand-in needs a `files` property (`NpzDict`) or analyse() crashes.

Vault: noise-series Entry 7; audit C3. Related: [[recording-2026-10-01-noise-4mice-overnight]] · [[hypnograms-and-per-mouse-export]] ·
[[s-sl-has-sleep-data-n3]] · [[animal-card-verdict-ladder]]

**2026-10-02 21:31, whole archive:** 100 animal-recordings in ~/eeg-processed; unnotched reproduces 99/99 official verdicts; notched SCOREABLE 44 → 69 (27 up, 2 down: 07-31 C2 and 08-19 C1 fail physiology checks after the notch). Epoch-shuffle control not re-run at this scale; some dark-set notched WAKE % 72-88 % need a look. Light-phase 10-02 A2 0.290 → 0.440 repeats the overnight.

**2026-10-02 23:10, VALIDATED at archive scale (`qc/emg_notch_validation_2026_10_02.py`, Fig P):** notch+shuffled EMG passes 0/100; mains = median 68 % of the stager's EMG variance and the change tracks it (share < 0.2: no flips); dark > light WAKE 41 → 47 of 49 recordings with both phases (median +25 → +37 pts), unchanged in recordings already good. Evidence it is a validity gain. Still NOT adopted (pre-register + falsification suite + re-score).
