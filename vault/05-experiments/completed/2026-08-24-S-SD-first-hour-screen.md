---
tags: [experiment, eeg, emg, S-SD, screen, completed]
created: 2026-08-27
status: complete
recording: allego_0__uid0824-17-56-51
cohort: S-SD
---

# The first hour screen of the S-SD cohort

> [!info] Written on 2026-08-27, three days late
> This report was reconstructed from the raw file and the cached features, not from notes. Every
> number below was recomputed on 2026-08-27 with the **current** `core/criteria.py`, which was
> fixed on 2026-08-26 to use a per-chip floor with the `site_p1_median` estimator. Where that
> disagrees with the verdicts written into `cohorts/S-SD.yaml` on 24 August, both are shown and the
> difference is explained. The manifest numbers came from a floor that was **trimmed by hand** of
> sites that looked contaminated; these are untrimmed.

> [!abstract] TL;DR
> `allego_0__uid0824-17-56-51`, **2026-08-24 17:56:51 KST, 60.0 min, 3.6 GiB, RUNG 0 PASS.** First
> recording of cohort `S-SD` (HLBCSD11 to HLBCSD19), and **the first recording in this project with
> real animal identities** rather than position labels.
>
> **Four positions give a full clean hour of EEG: A2, C1, C2, D2.** Three of those four are EEG
> only, because their EMG channels are open. **Only D2 passes the strict gate** — EEG and EMG
> usable in the same epoch — at 89.2% with a 23.8 min unbroken block.
>
> 🔴 **B1 gives nothing on either channel** and its chip's wire-free floor is the weakest on the rig
> at 1491 µV. That was later shown to be **a chewed tether**, not the port.
> 🔴 **Surgical notes do not predict signal quality.** The two animals with the worst bleeding notes
> (HLBCSD11, HLBCSD18) are the ones with the best EMG, and the animal with no adverse note at all
> (HLBCSD13, at B1) gives nothing.
> 🛑 **An hour badly overstates a long run.** A2 and C2 both read 100% here. Over the following
> 24 h they read 79.7% and 50.3%, and by 26 August both had failed outright.

## Rung 0 — FILE: PASS

| | |
|---|---|
| Recording | `allego_0__uid0824-17-56-51` |
| Start | 2026-08-24 17:56:51 KST |
| Duration | 60.04 min, 360 epochs of 10 s |
| Samples | 3,602,000 at 1000 Hz, 262 channels |
| Data vs timestamps | equal, remainder 0 and 0 |
| Size | 3.6 GiB |

Features cached at `~/eeg-processed/2026-08-24/feat_allego_0__uid0824-17-56-51.npz`.

This is the run that followed the two Allego GPU crashes and the 6.5 GB log storm of the same day;
the crashed attempt sits in `~/radix/data/_quarantine-2026-08-24-crashed-run/`. Allego was launched
with `--disable-gpu` for this recording and stayed up.

## The floor, per chip

| pos | mouse | floor 60 Hz median | floor 60 Hz p1 | floor slope p1 | grounded |
|---|---|---|---|---|---|
| A1 | HLBCSD11 | 4396 µV | 3253 | **−1.862** | yes |
| A2 | HLBCSD12 | 4131 | 3994 | −0.379 | yes |
| **B1** | **HLBCSD13** | **1491** | **54** | −1.723 | yes, barely |
| B2 | HLBCSD14 | 5047 | 4669 | −0.892 | yes |
| C1 | HLBCSD15 | 5062 | 4781 | −0.399 | yes |
| C2 | HLBCSD16 | 5398 | 5162 | −0.394 | yes |
| D1 | HLBCSD19 | 2890 | 1400 | **−1.543** | yes |
| D2 | HLBCSD18 | 2807 | 1939 | −0.686 | yes |

B1's floor is a third of the rig's typical value and its 1st percentile is 54 µV. It clears the
800 µV grounded bar on the median only. **The day after this recording it fell to 246 µV and the
guard refused a verdict outright.**

## Rung 2 — CONNECTION

| pos | mouse | EEG rms | slope | lf/hf | EEG % | longest | EMG rms | EMG % | BOTH % | longest BOTH | EEG rail | verdict |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| **D2** | HLBCSD18 | 79 µV | −1.57 | 16.62 | **100.0** | **60.0 min** | **33** | **89.2** | **89.2** | **23.8 min** | 0.0% | ✅ **PASS** |
| A2 | HLBCSD12 | 118 | −1.71 | 24.34 | **100.0** | **60.0 min** | 531 | 0.0 | 0.0 | — | 0.0% | EEG only |
| C2 | HLBCSD16 | 94 | −1.71 | 25.41 | **100.0** | **60.0 min** | 1001 | 0.0 | 0.0 | — | 0.0% | EEG only |
| C1 | HLBCSD15 | 105 | −1.84 | 28.29 | **99.7** | 41.3 min | 453 | 0.0 | 0.0 | — | 0.0% | EEG only |
| D1 | HLBCSD19 | 99 | −1.46 | 17.82 | 41.7 | 4.2 min | 928 | 0.0 | 0.0 | — | 15.3% | intermittent |
| A1 | HLBCSD11 | 98 | −1.39 | 17.49 | 3.3 | 0.3 min | **15** | **92.8** | 3.3 | 0.3 min | 18.3% | EMG only |
| B1 | HLBCSD13 | 3137 | +0.00 | 2.80 | 8.1 | 1.0 min | 2932 | 16.4 | 7.5 | 1.0 min | 66.9% | 🔴 nothing |
| B2 | HLBCSD14 | 4431 | −0.64 | 2.19 | 0.0 | — | 91 | 88.1 | 0.0 | — | 100.0% | EMG only |

The lf/hf separation test — animal median against its own chip's wire-free floor p99 — agrees on
six of eight: **A1 17.49 vs 12.18 · A2 24.34 vs 3.17 · C1 28.29 vs 2.74 · C2 25.41 vs 4.96 · D1
17.82 vs 10.69 · D2 16.62 vs 4.97 all separated**, while **B1 (2.80 vs 9.20) and B2 (2.19 vs 9.08)
do not separate.** So A1 and D1 have real EEG present even though the slope criterion scores them
low — see the reconciliation below.

## Where these numbers differ from the manifest, and why

| pos | manifest, 24 Aug, hand-trimmed floor | recomputed 27 Aug, untrimmed | floor slope p1 | floor lf/hf p99 |
|---|---|---|---|---|
| A1 | EEG 35.3%, longest 3.0 min | **3.3%, 0.3 min** | −1.862 | **12.18** |
| D1 | EEG 53.3%, longest 9.0 min | **41.7%, 4.2 min** | −1.543 | **10.69** |
| B1 | "NOTHING" | 8.1% | −1.723 | 9.20 |
| A2, C1, C2, D2 | 100 / 99.7 / 100 / 99.7% | 100 / 99.7 / 100 / 100% | −0.38 to −0.69 | 2.7 to 5.0 |

🔑 **The four positions that agree are exactly the four whose floors are shallow and clean. The
three that disagree are exactly the three whose floors are steep.** A1 and D1 sit on chips whose
own wire-free inputs have an lf/hf 99th percentile of 12.18 and 10.69, against 2.7 to 5.0
everywhere else. On such a chip the slope criterion has no discriminating power, and the trimming
that was done by hand on 24 August was a correct instinct without a rule behind it.

Threshold sensitivity, ±25% on the floor slope threshold, confirms which numbers can be trusted:

| pos | −25% | point | +25% |
|---|---|---|---|
| A2 | 100.0% / 60.0 min | 100.0% / 60.0 min | 100.0% / 60.0 min |
| C1 | 99.7 / 41.3 | 99.7 / 41.3 | 99.7 / 41.3 |
| C2 | 100.0 / 60.0 | 100.0 / 60.0 | 100.0 / 60.0 |
| D2 | 100.0 / 60.0 | 100.0 / 60.0 | 99.7 / 36.7 |
| **A1** | **48.6 / 4.7** | **3.3 / 0.3** | **0.0 / 0.0** |
| **D1** | **73.9 / 13.5** | **41.7 / 4.2** | **2.8 / 0.2** |
| **B1** | 21.9 / 7.3 | 8.1 / 1.0 | 0.0 / 0.0 |

**A2, C1, C2 and D2 do not move at all. A1, D1 and B1 move by 40 to 70 points.** Quote the first
four; do not quote the last three.

## Time course — always look at it

Per 10 min block, EEG usable %:

| pos | 17:56 | 18:06 | 18:16 | 18:26 | 18:36 | 18:46 |
|---|---|---|---|---|---|---|
| A2 | 100 | 100 | 100 | 100 | 100 | 100 |
| C1 | 100 | 98 | 100 | 100 | 100 | 100 |
| C2 | 100 | 100 | 100 | 100 | 100 | 100 |
| D2 | 100 | 100 | 100 | 100 | 100 | 100 |
| **D1** | **73** | **55** | **17** | **5** | **22** | **78** |
| A1 | 3 | 3 | 8 | 0 | 0 | 5 |
| B1 | 0 | 0 | 10 | 15 | 23 | 0 |
| B2 | 0 | 0 | 0 | 0 | 0 | 0 |

⭐ **D1 is intermittent, not dead.** It starts at 73%, collapses to 5% in the middle of the hour and
recovers to 78% by the end. A single number for D1 is a lie in either direction. This is the
movement-dependent contact behaviour, on the timescale of minutes.

Per 10 min block, EMG usable %:

| pos | 17:56 | 18:06 | 18:16 | 18:26 | 18:36 | 18:46 |
|---|---|---|---|---|---|---|
| A1 | 100 | 100 | 83 | 85 | 97 | 92 |
| B2 | 100 | 100 | 100 | 43 | 87 | 98 |
| D2 | 78 | 90 | 75 | 100 | 100 | 92 |
| B1 | 0 | 0 | 15 | 25 | 58 | 0 |
| A2, C1, C2, D1 | 0 | 0 | 0 | 0 | 0 | 0 |

🔑 **The two roles fail independently.** A1 and B2 have excellent muscle channels and no EEG; A2,
C1 and C2 have perfect EEG and no muscle. Only D2 has both. **Never describe a position as
"working" without saying which role.**

## 🔴 Surgical notes do not predict signal quality

| mouse | pos | surgical note | result |
|---|---|---|---|
| HLBCSD18 | D2 | *lots superficial bleeding after skin incision, lots of bleeding from 4 holes* | ✅ the only full PASS |
| HLBCSD11 | A1 | *bleeding F-L eeg, struggle to induce anesthesia, hiccups strong* | best EMG on the rig |
| HLBCSD15 | C1 | *bleeding P-L eeg* | 99.7% EEG |
| **HLBCSD13** | **B1** | **none** | **nothing on either channel** |
| HLBCSD12, 14, 16, 19 | A2, B2, C2, D1 | none | mixed |

**The animal with the cleanest surgery gives the worst data and the animal with the worst bleeding
gives the best.** Do not use intraoperative notes to triage animals, and do not offer them to the
professor as an explanation for a failure.

## What happened next

- 2026-08-25: 24 h ZT0-to-ZT0 run, [[2026-08-25-S-SD-24h-ZT0-run]]. B1's chip fell to 246 µV and
  the code refused a verdict. A2 and C2's perfect hours became 79.7% and 50.3%.
- 2026-08-26: B1's animal HLBCSD13 was pulled with a **chewed tether**, HLBCSD17 put in the same
  slot, and the port was exonerated. [[2026-08-27-B1-swap-baseline-20h-run]].
- 2026-08-26: `floor_stats()` was fixed to be per-chip with the `site_p1_median` estimator, which is
  why this report can be recomputed at all.

## Still open, from this run

1. 🔴 The **contaminated floor** problem that A1 and D1 show here is the same one A1 shows on
   26 August. It still has no guard in the code. Hand trimming is not a rule.
2. 🟡 Four of eight EMG channels were already open on day one of this cohort. That is a tethering
   or connector question, not an implant question.

## Provenance

- Raw: `~/radix/data/allego_0__uid0824-17-56-51{_data,_timestamp}.xdat` + `.xdat.json`
- Features: `~/eeg-processed/2026-08-24/feat_allego_0__uid0824-17-56-51.npz`, 360 × 128
- Engine: `core/criteria.py`, `core/qc_thresholds.py` as of 2026-08-27
- Cohort: `cohorts/S-SD.yaml`; husbandry from `HLB_SOD1_Intake_Monitoring.xlsx` sheet `Registry`
