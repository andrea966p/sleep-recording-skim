---
tags: [experiment, eeg, emg, W-SD, cohort, closeout, completed]
created: 2026-08-29
status: complete
cohort: W-SD
batch_status: SAMPLED 2026-08-28
---

# W-SD batch close-out: everything the cohort produced, first screen to sampling

> [!info] The batch is gone
> HLBCSD01 to HLBCSD10 were sampled on **2026-08-28**. Nothing on this page can be re-measured, and
> no intervention is possible. This is the complete record of what the batch produced and what it
> cost, written on 2026-08-29 from the raw files with the current analysis code.

> [!abstract] TL;DR
> Batch **W-SD**, ten male C57BL/6J, the **UV water arm** (0 U, the control against S-SD's SOD1),
> under **chronic sleep deprivation from Friday 2026-08-21 to sampling on Friday 2026-08-28**. Eight
> on the rig, one sacrificed early, one in the deprivation chamber untethered.
>
> ⚠️ **The rebound recording is the recovery-sleep window after the PENULTIMATE deprivation day** —
> 13:00 Thursday 2026-08-27 to 09:00 Friday 2026-08-28 — not a post-protocol endpoint. The protocol
> was still running when it was taken.
>
> ✅ **The pre-CSD baseline was the best data this rig has ever produced on a full cohort.**
> Recomputed with the per-chip floor: **five positions give real EEG and four pass strict rung 2
> over 39.7 hours** — A1 96.1% both roles, D2 92.8%, A2 82.2%, C1 66.4%, with unbroken EEG blocks
> of 7.6, 1.4, 4.2 and 8.9 hours.
>
> 🔴🔴 **The rebound recording, seven days later, produced one usable animal.** D2 alone.
> **The paired before/after comparison the whole arm exists for is n = 1.**
>
> 🔑 **The cause is now identified and it is not the implants. Four chips lost their ground
> reference during the seven days of deprivation** — A1 4976 → 1347 µV, A2 4396 → 1575, D1 4441 →
> 1814, B1 1275 → 593. **A1 and A2, the two best animals in the cohort, were lost this way**, and an
> 80 s check taken 21 minutes after the run ended showed both fully restored by a connector re-mate.
>
> 🔑 **The failure was visible in the first hour of the endpoint recording and was recorded rather
> than acted on.** That is the process change: [[pre-flight-connection-screen]].

## The batch

| | |
|---|---|
| Batch code | `W-SD`, HLBCSD01 to HLBCSD10 |
| Strain, sex | C57BL/6J (B6J-BomTac), male, n = 10 |
| DOB | 2026-04-27, so 17.6 weeks at sampling |
| Arrival | 2026-07-21 |
| Surgery | 2026-08-03 to 2026-08-05, Andrea and Diane |
| Tethering | 2026-08-10 |
| Drinking arm | **UV-sterilised water, 0 U** — the control arm against S-SD's SOD1 |
| Sleep condition | **chronic sleep deprivation, Friday 2026-08-21 to sampling Friday 2026-08-28**; daily bouts end at 13:00. **Thursday 08-27 is the penultimate day** |
| Sampling | **2026-08-28** |
| Source | `HLB_SOD1_Intake_Monitoring.xlsx`, sheets `Registry` (header row 5), `W-SD`, `Sampling` |

Rig positions, confirmed with Andrea on 2026-08-28:

| A1 | A2 | B1 | B2 | C1 | C2 | D1 | D2 |
|---|---|---|---|---|---|---|---|
| HLBCSD01 | HLBCSD02 | HLBCSD09 | HLBCSD04 | HLBCSD03 | HLBCSD06 | HLBCSD07 | HLBCSD08 |

**HLBCSD05** was sacrificed on 08-21 — *"08/20 kept jumping, 08/21 compromised, electrode ok,
internal bleeding intestines and spine dislocated cervical"*. ⭐ **Its electrode was found intact at
post mortem**, which is independent evidence that the implants survive and the failures are
downstream of the skull. **HLBCSD10** was added to the deprivation chamber on 08-21 untethered, so
it carries the treatment for the tissue endpoints and not for the sleep ones.

⚠️ **B1 held a different, unidentifiable animal until 2026-08-19 17:20**, when that animal chewed
and cut its tether. HLBCSD09 was moved in from the habituation rack that evening. The spreadsheet's
`XDAQ position` column holds one current value per animal, not a history, so the earlier animal
cannot be named. Nothing from before that time belongs to HLBCSD09.

### Water intake

Group mean **4.04 mL per mouse per day** (SD of daily means 1.46, SEM 0.46, n = 10 days) against a
3 mL reference; one-sample t against 3 mL gives **p = 0.051**, so intake is not significantly
different from the reference volume. Per mouse: 01 2.98 · 02 4.43 · 03 4.48 · 04 5.68 · 05 4.29
(7 days) · 06 3.00 · 07 4.91 · 08 3.03 · 09 3.40 · 10 no data.

HLBCSD01 has the lowest intake in the batch and the registry note *"struggling to drink water from
the glass tube after tethering"*, which is consistent.

## Every recording this batch produced

| file | date | duration | what it was |
|---|---|---|---|
| `allego_0__uid0818-18-56-33` | 08-18 | 0.107 h | first 6 min screen after tethering |
| `allego_1__uid0818-20-50-26` | 08-18 | 1.004 h | re-seat run the same evening |
| `allego_0__uid0819-09-00-00` | 08-19 | 8.278 h | daytime run, stopped 17:16 for the B1 animal swap |
| `allego_1__uid0819-17-25-20` | 08-19 to 08-21 | **39.674 h** | **the pre-CSD baseline** |
| — | Fri 08-21 to Thu 08-27 | — | **chronic sleep deprivation, daily bouts ending 13:00, no recording** |
| `allego_2__uid0827-12-58-32` | **Thu 08-27 13:00 → Fri 08-28 09:00** | **20.121 h** | **the recovery sleep after the PENULTIMATE SD day** |
| `allego_3__uid0828-09-26-12` | 08-28 | 0.023 h | 80 s check after the endpoint run |

All seven files are rung 0 INTACT with remainder 0 on both data and timestamps.

## ✅ The pre-CSD baseline, recomputed

`allego_1__uid0819-17-25-20`, 39.672 h, 14,282 epochs, per-chip floor with the `site_p1_median`
estimator. ⚠️ **These numbers differ from [[2026-08-21-39h-run-score]]**, which was written before
`floor_stats()` was fixed to be per-chip on 2026-08-26. They are more favourable, because the pooled
floor was too harsh for seven of the eight chips.

| pos | mouse | chip floor | EEG rms | slope | lf/hf | floor p99 | sep | EEG % | longest | h in ≥15 min blocks | EMG % | BOTH % |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| **A1** | HLBCSD01 | 4976 µV | 84 | −1.56 | 16.74 | 2.65 | ✅ | **99.9** | **457.5 min** | **39.49** | **96.2** | **96.1** |
| **D2** | HLBCSD08 | 4844 | 74 | −1.45 | 13.76 | 2.71 | ✅ | **98.5** | 86.2 min | **34.32** | **94.1** | **92.8** |
| **A2** | HLBCSD02 | 4396 | 115 | −1.49 | 14.32 | 3.85 | ✅ | **99.1** | 252.0 min | **36.05** | 82.8 | **82.2** |
| **C1** | HLBCSD03 | 5333 | 90 | −1.31 | 9.64 | 4.12 | ✅ | **98.8** | **536.7 min** | **36.47** | 67.3 | **66.4** |
| B2 | HLBCSD04 | 4336 | 108 | −1.42 | 13.49 | 2.98 | ✅ | 92.4 | 261.5 min | 22.38 | 0.0 | 0.0 |
| C2 | HLBCSD06 | 4483 | 2943 | −0.23 | 2.86 | 3.53 | ❌ | 32.8 | 20.7 min | 1.49 | 40.9 | 32.6 |
| D1 | HLBCSD07 | 4441 | 3901 | −0.71 | 2.68 | 7.15 | ❌ | 31.4 | 26.3 min | 1.28 | 6.5 | 3.3 |
| **B1** | HLBCSD09 | **1275** | 2080 | −0.48 | 2.91 | 9.78 | ❌ | 0.1 | — | 0.00 | 3.0 | 0.0 |

**Five positions carry real EEG. Four pass strict rung 2** — both roles usable in the same epoch,
inside blocks of fifteen minutes or more. A1 alone gives **39.5 hours** of EEG inside long blocks
out of a 39.7 hour recording.

> [!warning] C1 passes rung 2 here and was still withdrawn — the two are different rungs
> [[2026-08-21-39h-run-score]] withdrew C1 after its **EMG state-dependence** collapsed under
> falsification (−0.733 → −0.009 on absolute delta power) and its circadian EMG read inverted. That
> is a **rung 4** failure, about whether the muscle signal tracks behaviour. Rung 2 only asks
> whether the electrode is connected, and C1 was. **Both statements are true and they are not in
> conflict.** For any sleep-architecture purpose C1 stays withdrawn.
>
> ⚠️ C1's animal, HLBCSD03, has *"ate the tether 08/19"* in the registry and was found missing with
> its tether after this run was stopped. The withdrawal and the tether damage are the same story.

🔴 **B1 was never good.** HLBCSD09's chip floor read **1275 µV at the baseline**, already below the
2000 µV level that separates working from dead chips on this rig, and its EEG channel's 60 Hz sat at
**1.487× its own chip floor**, which is an open input riding the rail. It went on the rig on 08-19
and produced nothing at any point.

## 🔴 The rebound recording: recovery sleep after the penultimate SD day

`allego_2__uid0827-12-58-32`, 20.121 h, **Thursday 2026-08-27 12:58:30 → Friday 2026-08-28
09:05:45 KST**. It starts as that Thursday's deprivation bout ended at 13:00 and was stopped by hand
on the Friday morning, hours before sampling. **The CSD protocol was still running across this
window** — Thursday was the second to last day, not the end. Full report:
[[2026-08-27-W-SD-recovery-sleep]].

| pos | mouse | EEG rms | slope | lf/hf | sep | EEG % | longest | h ≥15 min | EMG % | BOTH % |
|---|---|---|---|---|---|---|---|---|---|---|
| **D2** | HLBCSD08 | 139 µV | −1.45 | 15.89 | ✅ | **74.2** | **45.3 min** | **2.90** | **98.5** | **73.0 ✅** |
| C2 | HLBCSD06 | 1537 | −0.73 | 3.32 | ❌ | 40.1 | 11.2 min | 0.00 | 65.6 | 38.2 🛑 |
| A2 | HLBCSD02 | 67 | −0.07 | 1.21 | ❌ | 3.2 | — | 0 | **99.2** | — |
| A1 | HLBCSD01 | 55 | −0.10 | 1.25 | ❌ | 0.3 | — | 0 | **98.4** | — |
| D1 | HLBCSD07 | 2087 | −0.03 | 2.14 | ❌ | 0.7 | — | 0 | 5.6 | — |
| B2 | HLBCSD04 | 4002 | +0.04 | 1.70 | ❌ | 0.0 | — | 0 | 0.0 | — |
| C1 | HLBCSD03 | 3901 | −0.07 | 0.98 | ❌ | 0.0 | — | 0 | 0.0 | — |
| B1 | HLBCSD09 | — | — | — | — | 🔴 UNJUDGEABLE, chip never grounded | | | | |

D2 is threshold-proof: 74.2 / 74.2 / 74.1% across a ±25% sweep of the floor threshold. C2's 40.1%
is not usable — its longest block is 11.2 min, nothing sits inside a 15 min block, and its lf/hf of
3.32 is **below** its own floor's 99th percentile of 3.79.

## 🔴🔴 What the seven days cost: four grounds, and the two best animals

Chip floor 60 Hz, the median across each chip's 14 wire-free inputs. The chips are rig hardware and
did not move between the two runs; the ground reference reaches them through the animal and its
tether.

| pos | mouse | pre-CSD baseline | recovery run | |
|---|---|---|---|---|
| **A1** | HLBCSD01 | 4976 µV | **1347** | 🔴 **−73%** |
| **A2** | HLBCSD02 | 4396 | **1575** | 🔴 **−64%** |
| **D1** | HLBCSD07 | 4441 | **1814** | 🔴 **−59%** |
| **B1** | HLBCSD09 | 1275 | **593** | 🔴 already weak, then **−53%** |
| C1 | HLBCSD03 | 5333 | 3524 | −34% |
| B2 | HLBCSD04 | 4336 | 4434 | unchanged |
| C2 | HLBCSD06 | 4483 | 4501 | unchanged |
| D2 | HLBCSD08 | 4844 | 4761 | unchanged |

**A1 and A2 were the two best animals in the cohort** — 96.1% and 82.2% on both roles across 39.7
hours — and both were lost to a ground fault, not to an electrode fault. The proof is in three
independent places:

1. **Their EEG channels stayed proportionally normal.** Each channel's own 60 Hz as a fraction of
   its chip's floor: A1 **0.032**, A2 **0.045**, against D2's working **0.032**. Relative to their
   own chips, nothing was wrong with those channels. The chip reference had collapsed underneath
   them.
2. **Their EMG worked all night through the same tether** — 98.4% and 99.2% — and A1's muscle
   amplitude was **2.73× higher in the dark**, which is genuine behavioural state dependence and
   cannot come from a floating input.
3. **An 80 s check 21 minutes after the run ended showed both fully restored.** A1's floor
   **1347 → 5026 µV**, A2's **1575 → 4490**, with EEG back at 91 and 134 µV, slope −1.43 and −1.53,
   and lf/hf 13.75 and 10.73 against floor 99th percentiles of 1.88 and 3.48. **Nothing was done to
   the electrodes.**

🔑 **B1 is the exception and the one genuine hardware fault.** Its floor **decayed monotonically
across the twenty hours** — 825, 691, 633, 663, 650, 619, 641, 657, 642, 615, 591, 579, 548, 548,
544, 507, 485, 480, 469, 478, 469 µV — where every previously recorded floating chip in this project
has been flat from first epoch to last. A slow slide over twenty hours is a conductor working loose.
**It did not come back when A1 and A2 did**, and it should be looked at before the next batch goes
on the rig.

## The scientific result

| | |
|---|---|
| Animals scoreable **before** CSD, strict rung 2 | **4** (A1, A2, C1, D2) — 3 after C1's rung 4 withdrawal |
| Animals scoreable **after** CSD | **1** (D2) |
| Animals scoreable on **both** sides | **1** (D2) |

🛑 **The recovery-sleep comparison for batch W-SD is n = 1.** It is reportable as a single-animal
case and it is not reportable as a group result. D2 / HLBCSD08, both roles:

| | pre-CSD, 39.7 h | recovery, 20.1 h |
|---|---|---|
| chip floor | 4844 µV | 4761 µV |
| EEG rms | 74 µV | 139 µV |
| EEG slope | −1.45 | −1.45 |
| EEG lf/hf | 13.76 | 15.89 |
| EEG usable | 98.5% | 74.2% |
| longest EEG block | 86.2 min | 45.3 min |
| EMG usable | 94.1% | 98.5% |
| **both roles, same epoch** | **92.8%** | **73.0%** |

Both files clear rung 2 comfortably, so the pair is analysable. 🛑 **The sleep architecture itself
stays PROVISIONAL.** No human has scored an epoch of it, and the blind-scoring **kappa** is the gate
on every rung 4 statement in this project.

⚠️ The tissue endpoints are unaffected by any of this. All ten animals, including HLBCSD10 which was
never tethered, carry the treatment.

## What this batch taught the rig

1. 🔑 **A weak chip ground is a distinct fault from an open electrode, and it hides.** The channel
   looks proportionally normal against its own chip while the whole chip's reference has collapsed.
   Written up as [[weak-chip-ground-vs-open-electrode]].
2. 🔑 **Working EMG on a position exonerates the implant and the tether for that position.** Both
   roles share the cable. A1 and A2 settled this in one line each.
3. 🔑 **A connection screen must gate the start of an unrepeatable recording, not annotate it.** The
   first hour of the endpoint run already said one of eight positions was working; the connector fix
   was applied after the run ended. Written up as [[pre-flight-connection-screen]].
4. 🔴 **The 800 µV grounded-chip gate is too low.** Across 32 chip-recordings, six chips sat below
   2000 µV and none produced EEG; the lowest floor that ever produced EEG was 2186 µV. A1, A2 and D1
   were scored FAIL when the honest answer was UNJUDGEABLE. ⚠️ **Not yet changed** — it rewrites
   verdicts in three published reports and is waiting on a decision.
5. ⭐ **Tether wear is the dominant failure mode of a long deprivation protocol.** Two animals ate
   their tethers, two were found missing with them, four grounds degraded over seven days, and the
   one electrode examined at post mortem was intact.

## Still open

- 🔴 **B1's hardware** — the 20 h monotonic ground decay and its failure to recover. Before the next
  batch.
- 🟡 **D2's hypnogram**, recovery against its own pre-CSD baseline. The only sleep result this batch
  can produce. 🛑 PROVISIONAL until the kappa.
- 🟡 **The `FLOOR_MIN_HUM_UV` decision**, see item 4 above.
- 🟡 **Retro-fit the pre-flight screen into the operator manual** so the next batch cannot repeat
  this. [[sleep-recording-operator-manual]].
- The blind-scoring **kappa**, still the gate on everything at rung 4.

## Provenance

- Raw: `~/radix/data/allego_{0,1,2,3}__uid08{18,19,27,28}-*` — seven files, all rung 0 INTACT
- Features: `~/eeg-processed/2026-08-19/feat_uid0819-17-25-20.npz` (14,282 × 128) and
  `~/eeg-processed/2026-08-27/feat_uid0827-12-58-32.npz` (7,243 × 128)
- Engine: `core/criteria.py`, `core/qc_thresholds.py` as of 2026-08-29
- Manifest: `eeg-emg-analysis/cohorts/W-SD.yaml`
- Husbandry: `HLB_SOD1_Intake_Monitoring.xlsx`, sheets `Registry`, `W-SD`, `Sampling`

## Related

[[2026-08-18-W-SD-cohort-first-screen]] · [[2026-08-21-39h-run-score]] ·
[[2026-08-27-W-SD-recovery-sleep]] · [[weak-chip-ground-vs-open-electrode]] ·
[[pre-flight-connection-screen]] · [[per-animal-failure-signatures]] ·
[[animal-card-and-verdict-ladder]]
