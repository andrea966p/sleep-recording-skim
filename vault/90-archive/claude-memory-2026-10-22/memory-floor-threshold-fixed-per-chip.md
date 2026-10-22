---
name: floor-threshold-fixed-per-chip
description: "2026-08-26: the floor threshold in core/criteria.py is FIXED — per-chip instead of pooled, a robust site_p1_median estimator, and a ground-validity guard that reports an ungrounded chip as UNJUDGEABLE instead of a dead animal"
metadata: 
  node_type: memory
  type: project
  originSessionId: aa023ba0-4d68-4842-9819-c574f4dde34b
  modified: 2026-08-26T01:53:22.858Z
---

✅⭐⭐⭐ **THE POOLED-FLOOR BUG IS FIXED (2026-08-26).** Supersedes the "STILL UNFIXED" note in
[[emg-gate-passes-and-floor-bug]]. Three changes, all in `core/criteria.py` +
`core/qc_thresholds.py` + `cards/ladder.py`.

## 1. PER-CHIP FLOOR — `T.FLOOR_SCOPE = "chip"`
`floor_stats(feat, position)` now takes a position and uses only that port+slot's wire-free sites
(`floor_sites_of()`). `floor_stats(feat)` with no position still gives the old pooled floor, kept
only so old callers do not break. `falsification_check` and `floor_threshold_ci` now score/resample
**the floor they were actually given**, not the pooled site list. `ladder.rung2_connection`
re-derives a per-chip floor if handed a pooled one, and `analyse()` builds one floor per position.

⭐ **Measured on `allego_0__uid0825-09-00-00`: pooled threshold −1.94 for every chip, per-chip
thresholds −0.77 (A2) to −2.06 (B1).** Under pooled, EEG usable reads A2 12.4%, C1 20.2%, D2 10.6%
— i.e. **the whole rig looks dead**. Per-chip: A2 79.7%, C1 91.3%, D2 98.8%.

## 2. ESTIMATOR — `T.FLOOR_ESTIMATOR = "site_p1_median"`
Percentile **per site first, then the median across sites**, instead of pooling every (epoch, site)
value. A chip has only ~14 wire-free sites; pooling lets one unrepresentative site's lower tail set
the bar. 🔑 **Case that motivated it: chip A1. Every floor site has a FLAT median slope (+0.38 to
−0.74), yet `A/11`-`A/15` are partially coupled (rms 651-2696 µV, lf/hf 3.6-5.2) and their epoch
tails drag the pooled p1 to −1.59, the strictest bar on the rig.** Across-chip threshold spread
falls 1.16 → 0.96. 🛑 **Chosen on robustness grounds, NOT by looking at which animals it passes** —
it moves A1's threshold by 0.07 and does not change A1's verdict.

## 3. GROUND-VALIDITY GUARD — `T.FLOOR_MIN_HUM_UV = 800.0`
A chip whose wire-free inputs sit below 800 µV of 60 Hz has **no ground reference**, so its floor is
not a valid negative control. `FloorStats.grounded` is False and rung 2 returns **`UNJUDGEABLE`**
with the reason, instead of FAIL. 🔑 **This stops a hardware fault being reported as a dead mouse:
B1/HLBSSD13 (floor 246 µV) was being published as a failing animal for days.** 800 sits in an empty
gap — grounded chips measure 1138-5609 µV across every recording since 2026-08-07, floating ones
82-466 µV.

`FloorStats` now carries its own provenance: `scope`, `position`, `estimator`, `grounded`,
`validity_reason`, so a number can never be quoted without saying which inputs produced it.

## ✅ VALIDATION — IT DOES NOT MANUFACTURE PASSES
- `tests/test_criterion_falsification.py` **passes** (accepts real signal, separates the trap,
  refuses the no-ground signature, refuses the category error). `test_cohort_schema` passes.
- 🔑 **The two channels that PHYSICALLY rail stay rejected: B2 (railed in 99.3% of epochs, median
  4424 µV) → 0.0%; D1 (71.4%, 2760 µV) → 2.8%.** The fix only moves channels whose floor was wrong.
- Ordering of the animals is unchanged; it matches the independent trimmed-floor analysis to within
  a few points (D2 96.2 vs 98.8, C1 85.2 vs 91.3, A2 79.5 vs 79.7, C2 48.8 vs 50.3, A1 31.0 vs 36.8).

## 🔴 A CAVEAT FOUND WHILE VALIDATING — `falsification_check` IS WEAKER THAN IT LOOKS
It returns ~0.00% on every real chip, but **not because the discriminator works: floor sites are
LOUD (2000-4500 µV rms) and fail the `RMS_LO_UV..RMS_HI_UV` amplitude window before the slope test
is ever reached.** So on real data it tests the amplitude gate, not the floor threshold. It is still
meaningful on the synthetic suite, where amplitudes are in range. **Do not cite a 0% falsification
rate on real data as evidence the threshold is right.**

## 🟡 STILL OPEN — lf/hf SEPARATES BETTER THAN SLOPE, AND IS NOT IMPLEMENTED
Measured on the same file, animal lf/hf vs its own chip floor p99:
**A1 14.67/8.71, A2 13.91/3.11, C1 16.01/4.53, C2 9.52/3.35, D2 15.08/4.42 = separated;
B2 1.50/13.42 and D1 1.63/9.30 = not.** A clean split of the 5 real EEGs from the 2 open ones with
no overlap, where slope leaves A1 ambiguous. ⛔ **NOT implemented — swapping the discriminator is a
scientific redesign that needs pre-registration and the falsification suite, not a patch.**

Related: [[emg-gate-passes-and-floor-bug]] · [[recording-2026-08-25-24h-zt0-S-SD]] ·
[[animal-card-verdict-ladder]] · [[test-suite-two-of-four-verify-nothing]]


## From the memory index, trimmed there 2026-10-06 (kept here verbatim)

- ✅⭐⭐⭐ **[FLOOR THRESHOLD FIXED, PER-CHIP — 2026-08-26](floor-threshold-fixed-per-chip.md).** Ungrounded chip ⇒ rung 2 UNJUDGEABLE, not FAIL. Falsification suite passes.
