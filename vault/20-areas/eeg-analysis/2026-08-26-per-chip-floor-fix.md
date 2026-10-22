---
type: incident
area: eeg-analysis
status: done
created: 2026-10-22
summary: "The wire-free floor was pooled across all eight chips; since 2026-08-26 each animal is judged against its own chip, with a per-site estimator and an ungrounded-chip guard"
tags: [eeg, qc, floor, verdict-ladder, fixed]
first_observed: 2026-08-21
fixed: 2026-08-26
---

# The pooled wire-free floor, fixed per chip (2026-08-26)

> [!abstract] TL;DR
> 🔴 Until 2026-08-26 `core/criteria.py::floor_stats()` pooled the wire-free inputs of all eight
> amplifier chips into one threshold, although the criterion's own definition says "through the same
> chip". One floating headstage could drag the pooled floor steep and fail the whole rig.
>
> ✅ Fixed 2026-08-26 (commit `7c08f40`, "Judge each animal against its own chip's wire-free floor")
> with three changes, all still in the code on 2026-10-22: `FLOOR_SCOPE = "chip"`,
> `FLOOR_ESTIMATOR = "site_p1_median"`, `FLOOR_MIN_HUM_UV = 800.0`.
>
> Written 2026-10-22 from the Claude memory file of 2026-08-26 (there is no journal note for that
> day), checked against `core/qc_thresholds.py`, `core/criteria.py` and the notes linked below.

## How it was found

Scoring the 39.7 h run on 2026-08-21 showed chip B1's floor at slope p1 −2.079 while the other seven
sat at −0.68 to −1.35; the pooled value (−1.633) was harsher than seven chips' own floors and more
lenient than the eighth. In all four substantive recordings checked that day the pooled value was too
harsh for exactly 7 of 8 chips. Direction rule: under the pooled floor a FAIL is suspect and a PASS is
conservative. Evidence: [[2026-08-21-39h-run-score]], [[animal-card-and-verdict-ladder]] (its
"Which floor" section was written before the fix).

## The three changes

1. **Per-chip floor, `FLOOR_SCOPE = "chip"`.** `floor_stats(feat, position)` uses only that
   port+slot's wire-free sites. Called without a position it still returns the old pooled floor, kept
   only so old callers do not break. `falsification_check` and `floor_threshold_ci` score and resample
   the floor they are given; `ladder.rung2_connection` re-derives a per-chip floor if handed a pooled one.
2. **Estimator, `FLOOR_ESTIMATOR = "site_p1_median"`.** The 1st percentile is taken per site first,
   then the median across sites, so one partly coupled site cannot set the bar for a chip of ~14 sites.
   Motivating case (code comment): chip A1 on `allego_0__uid0825-09-00-00`, sites A/11-A/15 dragged
   the pooled p1 to −1.59.
   Every A1 floor site had a flat median slope (+0.38 to −0.74), but A/11-A/15 were partly coupled (rms 651-2696 µV, lf/hf 3.6-5.2). The across-chip threshold spread fell from 1.16 to 0.96.
   🛑 **Chosen on robustness grounds, NOT by looking at which animals it passes.** It moves A1's
   threshold by 0.07 and does not change A1's verdict.
3. **Ground-validity guard, `FLOOR_MIN_HUM_UV = 800.0`.** A chip whose wire-free inputs carry less
   than 800 µV of 60 Hz has no ground reference, so its floor is no negative control: rung 2 returns
   **UNJUDGEABLE** with the reason, not FAIL. This stopped B1/HLBSSD13 (floor 246 µV) being reported
   as a failing animal. `FloorStats` carries `scope`, `position`, `estimator`, `grounded` and
   `validity_reason`, so a number always says which inputs produced it.

## Effect

Recomputed numbers for the 2026-08-25 S-SD run (A1 31.0 → 36.8 %, C1 85.2 → 91.3 %, D2 96.2 → 98.8 %,
B1 1.0 % → UNJUDGEABLE) are in [[2026-08-25-S-SD-24h-ZT0-run]]. The two physically railing channels on
that run stayed rejected. On uid0825 itself the pooled floor made the rig look dead: EEG usable A2 12.4 %, C1 20.2 %, D2 10.6 % pooled against A2 79.7 %, C1 91.3 %, D2 98.8 % per chip. The two physically railing channels stayed rejected (B2 railed 99.3 % of epochs, median 4424 µV, 0.0 % usable; D1 71.4 %, 2760 µV, 2.8 %). The animals' ordering was unchanged and matched an independent trimmed-floor analysis within a few points (D2 96.2 vs 98.8, C1 85.2 vs 91.3, A2 79.5 vs 79.7, C2 48.8 vs 50.3, A1 31.0 vs 36.8). The 800 µV guard sat in an empty gap at the time: grounded chips 1138-5609 µV in every recording since 2026-08-07, floating ones 82-466 µV. Per the memory record, `tests/test_criterion_falsification.py` and
`test_cohort_schema` passed after the change.

> [!warning] The per-chip threshold range on uid0825 is quoted two ways
> The 2026-08-26 memory record gives per-chip thresholds of −0.77 (A2) to −2.06 (B1) against a
> pooled −1.94; the comment at `FLOOR_SCOPE` in `core/qc_thresholds.py` gives −0.95 (A2) to −2.38 (B1).
> Not settled; logged as EA-9 in the eeg-analysis contradictions file.

## Caveats recorded at the time

- 🔴 **`falsification_check` is weaker than it looks on real data.** It returns ~0.00 % on every real
  chip because floor sites are loud (2000-4500 µV rms) and fail the `RMS_LO_UV..RMS_HI_UV` window before
  the slope test is reached. On real data it tests the amplitude gate, not the floor threshold. Do not
  cite a 0 % falsification rate on real data as evidence the threshold is right. It is meaningful on
  the synthetic suite.
- 🟡 **lf/hf separated the animals better than slope on uid0825** (animal lf/hf against its own chip floor p99: A1 14.67/8.71, A2 13.91/3.11, C1 16.01/4.53, C2 9.52/3.35, D2 15.08/4.42 separated; B2 1.50/13.42 and D1 1.63/9.30 not). ⛔ Not implemented: swapping the discriminator is a
  redesign that needs pre-registration and the falsification suite. See [[weak-chip-ground-vs-open-electrode]].
- A per-chip floor has ~14 sites, not 112: it trades bias for variance.

## Since then

- 2026-09-26: a grounded floor that itself carries signal got its own guard (slope p1 steeper than
  −1.90 ⇒ UNJUDGEABLE). [[contaminated-floor-rejects-good-eeg]]
- 2026-10-07 / 2026-10-14: after the grounding fix every chip floor sits far below 800 µV, so the
  ground guard calls every chip UNJUDGEABLE; the 800 µV "empty gap" had already been crossed before
  the fix (chips at 687, 769, 787 µV with physiological EEG). Replacing it is Andrea's decision.
  [[2026-10-14]]
