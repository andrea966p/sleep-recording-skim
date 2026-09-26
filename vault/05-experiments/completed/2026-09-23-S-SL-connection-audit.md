---
tags: [experiment, eeg, emg, S-SL, connection, sleep, audit, retracted-claim]
created: 2026-09-23
status: revised-2026-09-26
recordings: [allego_0__uid0912-08-55-18, allego_0__uid0920-09-00-07, allego_0__uid0921-00-17-34]
cohort: S-SL
---

# S-SL: the batch has sleep data, and the attrition it seemed to show was not real

> [!abstract] TL;DR
> 🛑 **RETRACTION, 2026-09-26.** The first version of this page, written
> 2026-09-23, said five of eight positions were connected at baseline and only
> two survived to the endpoint, and that three electrodes went "from excellent to
> nothing". **That attrition did not happen.** It is an artifact of a
> contaminated QC floor. See
> [[03-troubleshooting/symptoms/contaminated-floor-rejects-good-eeg]].
>
> ⭐ **What is true: S-SL has sleep architecture, and a paired n = 3.** Stage 2
> and stage 3 were run on all three day folders for the first time on 2026-09-26.
> **A1/HLBSSL31, B1/HLBSSL33 and C1/HLBSSL35 are SCOREABLE at both timepoints.**
> This is the batch's real result and it is better than anything previously
> claimed for it.
>
> 🔑 **The EEG never degraded.** Every channel reads slope ≈ −1.55 and rms ≈ 70 µV
> at the endpoint, the same as baseline. D2 was genuinely dead at baseline
> (slope −0.076, rms 29.6 µV) and is **healthy** at the endpoint (−1.644, 78.0 µV).
> It recovered.
>
> ⚠️ **No sleep conclusion is drawn here.** The baseline is a clean 24 h ZT0→ZT0;
> the endpoint is 36.707 h starting 00:17 and is **dark-heavy** (16.0 h light /
> 20.71 h dark against 12/12). Mice are far more awake in the dark, so the
> whole-file "more wake at recovery" is mostly window composition, not biology.

## The two recordings

| | baseline | recovery, segment 1 | recovery, segment 2 |
|---|---|---|---|
| recording | `allego_0__uid0912-08-55-18` | `allego_0__uid0920-09-00-07` | `allego_0__uid0921-00-17-34` |
| window as run | 2026-09-12 08:55 → 09-13 08:59 | 2026-09-20 09:00 → 09-21 00:08 | 2026-09-21 00:17 → 09-22 13:00 |
| duration | **24.065 h** | **15.145 h** | **36.707 h** |
| protocol window | 24 h, ZT0 → ZT0 ✅ | none — wholly outside it | 28 h, 09-21 09:00 → 09-22 13:00 |
| `thresholds_hash` | `c54b0f83af37` | `01e11630dcbf` | `01e11630dcbf` |

> [!note] The two recovery files are ONE run that Allego split
> `uid0920` ends 09-21 00:08:48 and `uid0921` begins 00:17:34 — a gap of 8 min
> 46 s. The mouse problem on the Sunday is why the run was restarted and why
> sampling slipped from the Monday to the Tuesday. `uid0920` is reported here
> because it dates the attrition; **none of it belongs in the recovery numbers**,
> since the protocol window lies wholly inside `uid0921`.

> [!warning] The recovery cards cover the WHOLE file, not the protocol window
> The canonical window is the **last 28 h** of that 36.707 h recording — 09-21
> 09:00 to 09-22 13:00 — which is unbroken inside it. The cards were computed
> over all 36.707 h, so **every recovery percentage below includes 8.71 h that
> are outside the window**. They are reported as computed, not as the protocol
> window. See [[02-procedures/CANONICAL-recording-windows-and-protocol]].
>
> Why the file is longer than the protocol: sampling slipped from 09-21 to 09-22
> because of the mouse problem, and the recording was extended to meet it.

> [!warning] The three rung 2 tables below are KEPT FOR THE RECORD, not as evidence
> They are what the cards said on 2026-09-23. Every `0.0%` on ports A, C and D
> for the 09-20 and 09-21 recordings is a **floor artifact**, not a disconnected
> electrode — the chips' wire-free reference inputs were carrying signal, which
> pushed the slope threshold to −2.4…−3.5 where real EEG is −1.5. The baseline
> table (09-12) is unaffected: its floors are clean.
> See [[03-troubleshooting/symptoms/contaminated-floor-rejects-good-eeg]].

## Baseline — 2026-09-12, 24.065 h

| pos | animal | rung 2 CONNECTION | usable | longest block |
|---|---|---|---|---|
| A1 | HLBSSL31 | ✅ PASS | 90.6% | 94.8 min |
| B2 | HLBSSL34 | ✅ PASS | 88.0% | 51.2 min |
| C1 | HLBSSL35 | ✅ PASS | 87.0% | 72.7 min |
| C2 | HLBSSL39 | ✅ PASS | 79.8% | 67.3 min |
| B1 | HLBSSL33 | ✅ PASS | 73.8% | 53.3 min |
| D1 | HLBSSL40 | ❌ FAIL | 66.9% | **13.7 min** |
| A2 | HLBSSL32 | ❌ FAIL | 0.0% | 0.0 min |
| D2 | HLBSSL38 | ❌ FAIL | 0.0% | 0.2 min |

⚠️ **D1 is the row to read carefully.** At 66.9% usable it looks comparable with
B1's 73.8%, and it fails — because its longest unbroken block is 13.7 min against
a 15 minute bar. Usable percentage and scoreability are different questions, and
D1 is where they disagree. A2 and D2 are not marginal; they are flat zero.

## Recovery segment 1 — 2026-09-20, 15.145 h, outside the window

| pos | animal | rung 2 CONNECTION | usable | longest block |
|---|---|---|---|---|
| C2 | HLBSSL39 | ✅ PASS | 87.3% | 64.3 min |
| B1 | HLBSSL33 | ✅ PASS | 83.0% | 42.7 min |
| B2 | HLBSSL34 | ❌ FAIL | 26.7% | 5.8 min |
| A2 | HLBSSL32 | ⬜ UNJUDGEABLE | — | — |
| A1 | HLBSSL31 | ❌ FAIL | 0.0% | 0.0 min |
| C1 | HLBSSL35 | ❌ FAIL | 0.0% | 0.0 min |
| D1 | HLBSSL40 | ❌ FAIL | 0.0% | 0.0 min |
| D2 | HLBSSL38 | ❌ FAIL | 0.0% | 0.0 min |

🔑 **This is the table that dates the attrition.** It was taken on the Sunday
morning, before the recovery run proper, and A1, C1 and D1 already read 0.0%
while B2 already reads 26.7%. Every loss visible at the endpoint is already
here.

⚠️ **A2 is UNJUDGEABLE here and FAIL on the other two recordings.** Its chip read
ungrounded for this segment, so rung 2 could not be asked — which is not the same
as answering no. See [[03-troubleshooting/symptoms/weak-chip-ground-vs-open-electrode]].

## Recovery — 2026-09-21 to 09-22, 36.707 h as computed

| pos | animal | rung 2 CONNECTION | usable | longest block |
|---|---|---|---|---|
| C2 | HLBSSL39 | ✅ PASS | 82.7% | 52.8 min |
| B1 | HLBSSL33 | ✅ PASS | 78.2% | 44.7 min |
| B2 | HLBSSL34 | ❌ FAIL | 23.5% | 8.0 min |
| A1 | HLBSSL31 | ❌ FAIL | 0.0% | 0.0 min |
| A2 | HLBSSL32 | ❌ FAIL | 0.0% | 0.2 min |
| C1 | HLBSSL35 | ❌ FAIL | 0.0% | 0.0 min |
| D1 | HLBSSL40 | ❌ FAIL | 0.0% | 0.0 min |
| D2 | HLBSSL38 | ❌ FAIL | 0.0% | 0.0 min |

## The attrition

| pos | animal | 09-12 baseline | 09-20 segment 1 | 09-21 segment 2 | |
|---|---|---|---|---|---|
| B1 | HLBSSL33 | 73.8% | 83.0% | **78.2%** | ✅ held throughout |
| C2 | HLBSSL39 | 79.8% | 87.3% | **82.7%** | ✅ held throughout |
| B2 | HLBSSL34 | 88.0% | **26.7%** | 23.5% | 🔴 degraded BEFORE recovery |
| A1 | HLBSSL31 | 90.6% | **0.0%** | 0.0% | 🔴 lost BEFORE recovery |
| C1 | HLBSSL35 | 87.0% | **0.0%** | 0.0% | 🔴 lost BEFORE recovery |
| D1 | HLBSSL40 | 66.9% (FAIL) | 0.0% | 0.0% | ❌ never recovered |
| D2 | HLBSSL38 | 0.0% | 0.0% | 0.0% | ❌ never recovered |
| A2 | HLBSSL32 | 0.0% | UNJUDGEABLE | 0.0% | ❌ never recovered |

🛑 **This table measures the floor, not the electrodes. RETRACTED as attrition.**
The 2026-09-23 reading of it — that everything failed in the eight-day gap — was
wrong. The positions that "fail" here are exactly the positions whose reference
floor became contaminated, and their EEG is unchanged:

| pos | EEG slope 09-12 → 09-21 | EEG rms 09-12 → 09-21 | floor threshold 09-12 → 09-21 |
|---|---|---|---|
| A1 | −1.354 → −1.506 | 82.2 → 72.0 | −0.570 → **−2.384** |
| C1 | −1.614 → −1.544 | 94.8 → 68.0 | −0.456 → **−3.044** |
| D1 | −1.553 → −1.617 | 76.0 → 74.8 | −1.397 → **−2.881** |
| D2 | −0.076 → −1.644 | 29.6 → **78.0** | −0.725 → **−3.513** |
| B1 | −1.570 → −1.546 | 91.9 → 70.1 | −0.593 → −0.653 |
| C2 | −1.564 → −1.565 | 81.4 → 73.2 | −0.573 → −0.686 |

The only two chips whose floors stayed clean, B1 and C2, are the only two
positions that "passed". That is the whole pattern.

🛑 **RETRACTED.** This page previously read the table above as "baseline
connection quality did not predict which positions would last". There was nothing
to predict: no position was lost. A1 and C1 were the strongest at baseline and
they are still working at the endpoint — both are SCOREABLE in stage 3.

## Sleep architecture — stage 2 and stage 3, run 2026-09-26

Stage 2 and stage 3 had **never been run** on any S-SL recording until this date.
Day folders are `~/eeg-processed/2026-09-12`, `2026-09-20`, `2026-09-21`, each
with a hypnogram CSV, a features JSON and a summary per mouse.

### Baseline, 2026-09-12, 24.065 h, ZT0 → ZT0

| pos | animal | verdict | r@1min | WAKE | NREM | REM from NREM |
|---|---|---|---|---|---|---|
| C1 | HLBSSL35 | ✅ SCOREABLE | 0.678 | 41.4% | 53.7% | 85.1% |
| B1 | HLBSSL33 | ✅ SCOREABLE | 0.554 | 41.5% | 52.4% | 75.7% |
| A1 | HLBSSL31 | ✅ SCOREABLE | 0.532 | 34.0% | 61.3% | 68.9% |
| B2 | HLBSSL34 | ❌ REJECT | 0.225 | — | — | bar is 0.30 |
| D1 | HLBSSL40 | ❌ REJECT | 0.146 | — | — | implausible wake 9.6% |
| C2 | HLBSSL39 | ❌ REJECT | 0.09 | — | — | implausible wake 7.2% |

A2 and D2 were dropped at stage 2 (OPEN and DEAD) and have no files.

### Endpoint, 2026-09-21 → 09-22, 36.707 h as computed

| pos | animal | verdict | r@1min | WAKE | NREM | REM from NREM |
|---|---|---|---|---|---|---|
| C1 | HLBSSL35 | ✅ SCOREABLE | 0.734 | 49.4% | 45.8% | 82.9% |
| B1 | HLBSSL33 | ✅ SCOREABLE | 0.722 | 45.6% | 47.7% | 87.5% |
| A1 | HLBSSL31 | ✅ SCOREABLE | 0.632 | 42.4% | 51.8% | 79.1% |
| D1 | HLBSSL40 | ✅ SCOREABLE | 0.610 | 39.3% | 54.8% | 78.9% |
| C2 | HLBSSL39 | ✅ SCOREABLE | 0.502 | 42.3% | 51.8% | 80.3% |
| A2 | HLBSSL32 | ✅ SCOREABLE | 0.400 | 32.4% | 61.2% | 72.2% |
| B2 | HLBSSL34 | ❌ REJECT | 0.343 | — | — | physiology: nrem_has_most_delta |
| D2 | HLBSSL38 | ❌ REJECT | — | — | — | 100% wake, states missing |

🔴 **Six of eight are scoreable here.** Rung 2 called six of eight *disconnected*
on this same recording. That contradiction is what exposed the floor defect.

### Segment 1, 2026-09-20, 15.145 h — outside the protocol window

Five scoreable: A1 0.624, C1 0.680, B1 0.678, D1 0.484, C2 0.478. A2 rejects on
94.5% wake, B2 on physiology, D2 on 1.3% wake.

### ⭐ The paired set: n = 3 at rung 3

Scoreable at **both** protocol timepoints:

| animal | pos | baseline r@1min | endpoint r@1min |
|---|---|---|---|
| HLBSSL31 | A1 | 0.532 | 0.632 |
| HLBSSL33 | B1 | 0.554 | 0.722 |
| HLBSSL35 | C1 | 0.678 | 0.734 |

This supersedes every earlier claim about S-SL's n. It is **not** the "n = 2 at
rung 2" this page first reported, and it is not the n = 1 the batch was assumed
to have.

### 🛑 Why no sleep conclusion is drawn from it

The two windows are not comparable:

| | baseline | endpoint |
|---|---|---|
| light | 12.00 h | **16.00 h** |
| dark | 12.06 h | **20.71 h** |

The endpoint is dark-heavy, 56% against 50%, because it starts at 00:17 in the
middle of the dark phase. Mice are far more awake in the dark, so the whole-file
"more wake at the endpoint" is largely **window composition**. Split by phase:

| animal | light WAKE base → end | dark WAKE base → end |
|---|---|---|
| HLBSSL31 | 23.8 → 25.2 (+1.4) | 44.0 → 55.6 (+11.6) |
| HLBSSL33 | 21.1 → 25.2 (+4.1) | 61.9 → 61.3 (−0.6) |
| HLBSSL35 | 22.9 → 26.4 (+3.5) | 59.7 → 67.2 (+7.5) |

In the light phase all three move the same way by a small amount (+1.4 to +4.1).
In the dark the direction is inconsistent (−0.6 to +11.6). With n = 3 and no
statistics that light-phase shift is **suggestive at most**.

🔑 **This is the first concrete answer to the trimmed-window question.** Trimming
the endpoint to its protocol window, 09-21 09:00 → 09-22 13:00, drops exactly the
8.71 h of dark that skews it, giving 16 h light / 12 h dark. Still not the
baseline's 12/12, but far closer. See
[[02-procedures/CANONICAL-recording-windows-and-protocol]].

## What this does not support

- 🛑 **No sleep CONCLUSION, despite now having sleep data.** The baseline and
  endpoint windows differ in light/dark composition (12.0/12.06 h against
  16.0/20.71 h), which is enough on its own to produce the observed wake
  difference. Nothing here is a statement about the effect of sleep libido.
- 🛑 **No group statistics.** n = 3, no test was run, and none is warranted.
- ⚠️ **Rung 3 SCOREABLE is not rung 4.** Stage 3 emits architecture, but the
  ladder's rung 4 has not been evaluated for these animals. The `rem_pct` figure
  is `rem_pct_CONSTRUCTED` and is **fixed by the rule**, not measured — never
  quote it. What is evidence is REM's ORDER, the REM-from-NREM column.
- 🔴 **Stage 3 does not check that the EEG is connected.** It gates on stage 1's
  `epoch_ok`, not on the ladder's rung 2. On this batch that worked in our
  favour — the rung 2 verdicts were the wrong ones — but the general point
  stands: a SCOREABLE verdict from stage 3 is not independent confirmation that
  the electrode was good, and a real open electrode with a live EMG could still
  produce a wake/sleep split.
- ⚠️ **The recordings were judged under different thresholds**
  (`c54b0f83af37` against `01e11630dcbf`) and different code revisions.
- ⚠️ **Endpoint numbers cover the whole 36.707 h**, including 8.71 h outside the
  protocol window.
- ⚠️ **No husbandry.** `cohorts/S-SL.yaml` deliberately carries no sex, date of
  birth, surgery date, weights or tether date, so no age, weight or
  days-post-surgery can be reported for any animal here.
- ❌ **The rung 2 verdicts on 09-20 and 09-21 are not usable at all** until the
  floor validity fix lands and those recordings are re-carded.

## Provenance

Cards at `eeg-emg-analysis/cards/out/S-SL/`, generated by `cards/ladder.py` against
`cohorts/S-SL.yaml`. Both recordings are stripped to 16 channels, bit-exact, and
on the SKIM NAS as `20260912_HLBSSL_BSR/` and `20260921_HLBSSL_RSR/`; raw is in S3.

⚠️ **The card sets were regenerated in two passes.** On 2026-09-23
`allego_0__uid0921-00-17-34` was added to `cohorts/S-SL.yaml`, having been absent
from it entirely; its cards had lived under the throwaway console cohort
`auto-a91ef30eab66`, and the verdicts were identical either way. On 2026-09-26
`allego_0__uid0920-09-00-07` was added and **carded under this cohort for the
first time** — that is the segment-1 table above, and it is new evidence, not a
refile.

✅ **Every `auto-*` console cohort has now been retired from `cards/out/`.** Seven
existed. Two duplicated a named cohort, four were 0.6-to-8-minute aborted starts,
and one — `auto-df0f5562873b` — held this recording. 🔴 The `uid0917` set under
`auto-6255ffcf2575` was NOT a duplicate but a **stale** set that reached only
rung 3 and carried a nonexistent animal id, `HLBWSL7`; the current `cards/out/W-SL/`
set reaches rung 4 and names `HLBWSL27`. Deleting it removed that ghost from disk.

🛑 `allego_0__uid0913-11-20-07` is deliberately NOT in this manifest: 8.4 minutes,
an aborted start, no result.

Stage 2 and stage 3 outputs live in `~/eeg-processed/2026-09-12`, `2026-09-20`
and `2026-09-21` — hypnogram CSV, features JSON and summary per mouse. They are
NOT in the repo (too large); regenerate with:

```bash
cd eeg-emg-analysis && PYTHONPATH=. /usr/bin/python3 pipeline/stage2_split.py \
  allego_0__uid0912-08-55-18 allego_0__uid0920-09-00-07 allego_0__uid0921-00-17-34
```

then `pipeline/stage3_features.py` on each day folder. Stage 2 runs stage 1 QC
inline, so it also writes the `qc/` subfolder.

Not checked: figures (none drawn), rung 4 architecture, and the failure-signature
classification.

## Related

[[03-troubleshooting/symptoms/contaminated-floor-rejects-good-eeg]] ·
[[02-procedures/CANONICAL-recording-windows-and-protocol]] ·
[[02-procedures/CANONICAL-recording-naming-and-inventory]] ·
[[02-procedures/eeg-data-analysis/animal-card-and-verdict-ladder]] ·
[[05-experiments/completed/2026-09-18-W-SL-light-phase-sleep]]
