---
tags: [experiment, eeg, emg, qc, ladder, W-SD, S-SD, W-SL, S-SL, completed]
created: 2026-09-30
status: complete
recordings: [allego_1__uid0819-17-25-20, allego_2__uid0827-12-58-32, allego_0__uid0825-09-00-00, allego_2__uid0902-13-00-28, allego_0__uid0910-09-00-00, allego_0__uid0917-09-00-09, allego_0__uid0912-08-55-18, allego_0__uid0921-00-17-34]
---

# Which mice are scoreable at BOTH timepoints, judged on the 24 h windows

> [!abstract] TL;DR
> - **Worth manual scoring now:** **HLBWSD08**, **HLBWSL24** and **HLBSSL33**. Each passes every
>   automatic check at baseline AND recovery.
> - **Also worth scoring:** **HLBSSL31** and **HLBSSL35**. Stage 3 finds clear sleep structure in
>   both of their windows (recovery r@1min 0.647 and 0.703). The ladder cannot confirm the
>   connection at recovery, because that chip's reference inputs carry signal. This is not a
>   failure.
> - **Borderline:** HLBWSL23. Its baseline r@1min is 0.289, just under the 0.30 bar.
> - **S-SD has no scoreable mouse.**
>
> | batch | paired and scoreable | n |
> |---|---|---|
> | W-SD | HLBWSD08 | **1** |
> | S-SD | none | **0** |
> | W-SL | HLBWSL24 (+ HLBWSL23 borderline) | **1 (2)** |
> | S-SL | HLBSSL33 (+ HLBSSL31, HLBSSL35 on stage 3) | **1 (3)** |
>
> Nothing about sleep is concluded here. This page is about which animals can be scored at all.

## What was judged

The CSVs on the SKIM NAS were cut to the analysis windows Andrea set on 2026-09-29
([[02-procedures/per-mouse-csv-format]]):

| | window |
|---|---|
| baseline, every batch | 09:00 → 09:00, 24 h |
| recovery, ad libitum (W-SL, S-SL) | 09:00 → 09:00, 24 h |
| recovery, deprivation (W-SD, S-SD) | 13:00 → 09:00, 20 h. Both runs stopped at 09:05, so no longer window exists |

The earlier cards in `cards/out/` judged **whole files**, including an extra night in the S-SL
recovery and 15 h of extra time in the W-SD baseline. So the ladder was re-run on exactly these
windows by `eeg-emg-analysis/cards/window_recheck.py`:
- **Rung 2:** the cached 10 s QC features, computed on the full 262-channel original with its
  wire-free floor, were sliced to the epochs inside the window.
- **Rung 3 and up:** the stage-2 per-mouse files were sliced into `~/eeg-processed-windows/`, and
  stage 3 was re-run there.
- Neither the whole-file cards nor the stage-2 files were changed. The new cards are in
  `cards/out-windows/<cohort>/`, each with a `window` block.

**Validation.** The W-SL baseline window is 24.0 of the file's 24.39 h. On it, all eight positions
got the **same verdict** as their whole-file cards.

Two bugs were fixed before any result was used:
- The recorder's venv pairs NumPy 2 with the system SciPy, so stage 3 crashed. Stage 3 now runs
  under `/usr/bin/python3`.
- The file search also matched `2026-09-10-lightphase`, a 12 h light-only copy of the same
  recording. Only plain date folders are used now.

## Per mouse, baseline → recovery

Rung 2 figures are the strict EEG-and-EMG-in-the-same-epoch fraction and the longest unbroken
block; r is within-block r@1min, with the bar at 0.30.

| batch | pos | mouse | baseline | recovery | scoreable at both? |
|---|---|---|---|---|---|
| W-SD | D2 | **HLBWSD08** | PASS 92.7% / 53.8 min, r 0.487 | PASS 73.1% / 45.0 min, r 0.402 | ✅ |
| W-SD | A1 | HLBWSD01 | PASS 96.2%, r 0.475 | FAIL 0.3% | ❌ lost after CSD |
| W-SD | A2 | HLBWSD02 | PASS 77.1%, r 0.548 | FAIL 3.2% | ❌ lost after CSD |
| W-SD | C1 | HLBWSD03 | rung 3 **FAIL**: physiology `nrem_largest_amplitude`, r 0.411 | FAIL 0.0% | ❌ |
| W-SD | C2 | HLBWSD06 | rung 3 FAIL, r −0.013 | FAIL 38.0% | ❌ |
| W-SD | B1, B2, D1 | HLBWSD09, 04, 07 | FAIL | FAIL / UNJUDGEABLE | ❌ |
| S-SD | D2 | HLBSSD18 | PASS 78.7%, rung 3 FAIL r 0.028 | PASS 60.4%, rung 3 FAIL r −0.023 | ❌ EMG has no muscle-band modulation |
| S-SD | others | 11, 12, 14, 15, 16, 19 | FAIL | FAIL / UNJUDGEABLE | ❌ |
| S-SD | B1 | HLBSSD13 / HLBSSD17 | UNJUDGEABLE, baseline only | UNJUDGEABLE, recovery only | ❌ unpaired by design |
| W-SL | B2 | **HLBWSL24** | PASS 87.4% / 70.3 min, r 0.460 | PASS 77.6% / 16.3 min, r 0.682 | ✅ |
| W-SL | B1 | HLBWSL23 | PASS 94.2%, rung 3 FAIL **r 0.289** | PASS 76.7%, r 0.636 | 🟡 borderline |
| W-SL | A2, D1 | HLBWSL22, 27 | PASS, r 0.384 / 0.443 | UNJUDGEABLE (ungrounded chip) | ❌ |
| W-SL | D2 | HLBWSL29 | rung 3 FAIL r 0.177 | UNJUDGEABLE | ❌ |
| W-SL | C2 | HLBWSL26 | FAIL 0.0% | PASS 47.4%, rung 3 FAIL | ❌ |
| W-SL | A1, C1 | HLBWSL21, 25 | UNJUDGEABLE / FAIL | FAIL / UNJUDGEABLE | ❌ |
| S-SL | B1 | **HLBSSL33** | PASS 73.9% / 53.3 min, r 0.550 | PASS 78.6% / 44.7 min, r 0.718 | ✅ |
| S-SL | A1 | HLBSSL31 | PASS 90.5%, r 0.532 | UNJUDGEABLE (floor carries signal); **stage 3 SCOREABLE r 0.647** | 🟡 stage 3 only |
| S-SL | C1 | HLBSSL35 | PASS 87.0%, r 0.677 | UNJUDGEABLE (floor carries signal); **stage 3 SCOREABLE r 0.703** | 🟡 stage 3 only |
| S-SL | C2 | HLBSSL39 | rung 3 FAIL r 0.090 | PASS 83.0%, r 0.546 | ❌ |
| S-SL | B2 | HLBSSL34 | rung 3 FAIL r 0.225 | FAIL 19.4% | ❌ |
| S-SL | A2, D1, D2 | HLBSSL32, 40, 38 | FAIL | UNJUDGEABLE | ❌ |

## What changed against the whole-file cards

- **HLBWSD03, W-SD baseline:** was a rung 3 PASS on the 39.7 h file. On the 24 h window it fails
  the physiology check `nrem_largest_amplitude`. Its recovery fails anyway, so the paired count
  does not move.
- **HLBWSL23, W-SL baseline:** r 0.255 → 0.289, still under 0.30.
- Every other verdict moved by only a few points.

## Why HLBSSL31 and 35 are listed at all

At the S-SL recovery, five of the eight chips have a wire-free floor that itself carries signal
(slope threshold −2.4 to −3.5). Rung 2 therefore refuses to judge them, and returns UNJUDGEABLE,
not FAIL. See [[03-troubleshooting/symptoms/contaminated-floor-rejects-good-eeg]]. Stage 3 uses
stage 1's own gate, and it finds 24.0 h inside contact blocks, with within-block persistence well
above the bar, for both animals. Whether to score them is a human call. A 10-minute look at each
recovery CSV would settle it.

> [!quote] Paper-ready
> Animals were retained for analysis only if both the baseline and the recovery window passed an
> automated connection criterion (EEG and EMG simultaneously usable, judged against wire-free
> amplifier inputs recorded in the same file, with an unbroken block of at least 15 min) and a
> scoreability criterion (within-block 1-min state persistence r > 0.30).

## Files

- Cards on the windows: `eeg-emg-analysis/cards/out-windows/{W-SD,S-SD,W-SL,S-SL}/`
- Sliced stage 2 and stage 3 outputs: `~/eeg-processed-windows/<window date>/` (not in the repo)
- Sliced QC caches: `~/eeg-qc-cache/windows/`
- Run log: `~/eeg-processed-windows/recheck-2026-09-30.log`
- The CSVs: `02_Data_Sleep/andrea/<batch>/<Baseline|Recovery>/`, with pairing in each `info.json`

## Related

[[02-procedures/per-mouse-csv-format]] · [[02-procedures/CANONICAL-recording-windows-and-protocol]] ·
[[2026-09-23-S-SL-connection-audit]] · [[2026-09-02-S-SD-recovery-sleep]] ·
[[2026-08-28-W-SD-cohort-closeout]] · [[2026-09-18-W-SL-light-phase-sleep]]
