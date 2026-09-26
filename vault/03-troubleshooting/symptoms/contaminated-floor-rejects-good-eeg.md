---
tags: [troubleshooting, symptom, eeg, qc, verdict-ladder, floor, fixed]
created: 2026-09-26
first_observed: 2026-08-27
status: fixed
fixed: 2026-09-26
affects: [S-SL, W-SL, S-SD]
---

# A contaminated floor reports healthy EEG as 0.0% usable

> [!abstract] TL;DR
> 🔴 **Rung 2 can report `0.0% usable` on an electrode that is working perfectly.**
> It happens when the chip's wire-free reference inputs are themselves carrying
> signal. The floor's slope threshold then tightens past what real mouse EEG can
> achieve, and every epoch is rejected.
>
> 🔑 **The discriminator is the floor, not the electrode.** Real EEG on this rig
> sits at slope **−1.35 to −1.64** with rms **66–95 µV**. Any floor whose
> `slope_p1` is steeper than about **−1.7** is demanding more than genuine EEG
> delivers, so its FAIL verdicts mean nothing.
>
> ⭐ **11 cards of 79 are affected**, across S-SL, W-SL and S-SD. Measured by the
> scan below on 2026-09-26.
>
> ✅ **The error is one-directional.** Zero cards PASS on an over-flat floor, so
> nothing published is too optimistic because of this. It only ever rejects good
> data.
>
> ✅ **FIXED 2026-09-26 in `2cc5892`.** A grounded chip whose own slope threshold is
> steeper than `FLOOR_STEEPEST_VALID_SLOPE_P1` (−1.90) now yields UNJUDGEABLE, not
> FAIL. The four affected recordings were re-carded: exactly the 11 cards below
> moved, and nothing else in S-SD, S-SL, W-SD or W-SL did. See "The fix, as
> applied".
>
> 🛑 **NOT NEW.** This was diagnosed correctly on **2026-08-27** in
> [[05-experiments/completed/2026-08-27-B1-swap-baseline-20h-run]], which named the
> mechanism, said the verdict should be UNJUDGEABLE, and logged it as an open item.
> Nothing was done, and a month later it produced a wrong published conclusion for
> S-SL. **This page exists because a finding on one experiment page did not reach
> the engine or the other cohorts.**

## The mechanism

`core/criteria.py:666`, inside `floor_stats()`:

```python
grounded = hum_median >= T.FLOOR_MIN_HUM_UV
```

That is the **only** validity test on the floor. It asks whether the chip has a
ground reference, by checking that its wire-free inputs pick up mains hum. It
never asks the other question: **are those inputs actually flat?**

A wire-free input should have a flat spectrum, slope ≈ 0, because it is not
connected to anything. When it instead reads a steep slope, it is picking up
real signal, and it is no longer a negative control. The chip still reports
`grounded: true` — hum is fine — and the threshold is computed anyway:

```
threshold = slope_p1 of the wire-free inputs on this chip
```

With a contaminated floor that lands at −2.4 to −3.5. Real EEG is −1.5. Nothing
passes, and the card says `0.0% usable, longest unbroken block 0.0 min` with no
hedge at all.

## History: found once, then left

**2026-08-27** — diagnosed in full on the B1-swap baseline page. A1/HLBSSD11's EEG
was unchanged between two runs (rms 94 → 94 µV, slope −1.36 → −1.33) while its
usable fraction fell 31.0% → 0.0%, because chip A1's floor steepened from −1.523
to −2.437. That page listed the chip's fourteen per-site slopes and showed **seven
of them steeper than the animal's own EEG**. It stated the right verdict —
UNJUDGEABLE — and flagged the missing guard. It was filed as an open item on a
single experiment page.

**2026-09-26** — rediscovered from the other direction. Running stage 2 and stage 3
on the S-SL day folders for the first time produced well-formed hypnograms for six
animals that rung 2 called disconnected. Two engines disagreeing that hard is the
symptom.

### What is actually new this time

1. **It is not one chip on one recording.** 11 cards across S-SL, W-SL and S-SD.
2. **A bounded scan exists** (below), so the blast radius is known rather than feared.
3. **It has already corrupted a published conclusion** — the S-SL attrition claim,
   retracted 2026-09-26.
4. **Independent confirmation from a second engine.** Stage 3 does not use the
   floor, and it scores six of the "disconnected" animals as SCOREABLE with
   `r@1min` 0.40–0.73.
5. **An empirical bar.** Real EEG on this rig is slope −1.35 to −1.64 at rms
   66–95 µV, measured across S-SD, W-SL and S-SL.

The decisive table compares each EEG against its own floor, baseline vs
endpoint:

| pos | EEG slope 09-12 → 09-21 | EEG rms 09-12 → 09-21 | floor threshold 09-12 → 09-21 |
|---|---|---|---|
| A1 | −1.354 → **−1.506** | 82.2 → **72.0** | −0.570 → **−2.384** |
| C1 | −1.614 → **−1.544** | 94.8 → **68.0** | −0.456 → **−3.044** |
| D1 | −1.553 → **−1.617** | 76.0 → **74.8** | −1.397 → **−2.881** |
| D2 | −0.076 → **−1.644** | 29.6 → **78.0** | −0.725 → **−3.513** |
| B1 | −1.570 → −1.546 | 91.9 → 70.1 | −0.593 → −0.653 |
| C2 | −1.564 → −1.565 | 81.4 → 73.2 | −0.573 → −0.686 |

⭐ **The EEG did not change. The floor did.** Every channel sits at slope ≈ −1.55
and rms ≈ 70 µV on both days. Only the reference floor moved, and only on some
chips.

🔑 **D2 is the clearest case.** Its EEG was genuinely dead at baseline (slope
−0.076, rms 29.6 µV — flat and tiny). At the endpoint it is **healthy**
(−1.644, 78.0 µV). It recovered. Rung 2 reports it as 0.0% usable.

### The falsification that rules out a filter change

A change to the hardware bandpass would steepen every chip on the rig together.
B1 (−0.593 → −0.653) and C2 (−0.573 → −0.686) did not move at all. The effect is
**chip-specific**, so it is not a filter change — and those two unmoved chips are
exactly the two positions that "passed".

### Three independent lines agree the EEG was fine

1. **Stage 1 QC** called all 8 positions CLEAN or DIRTY on 09-20, against one
   OPEN and one DEAD at baseline. By that engine the rig got *better*.
2. **Stage 3** scores A1 on 09-20 at `r@1min` 0.624, WAKE 32.9% / NREM 58.1% —
   near-identical to A1 at baseline (0.532, 34.0% / 61.3%). Same animal, same
   architecture, eight days apart.
3. **The raw slope and rms** above are unchanged.

## The scan: which cards are affected

Read-only over every card JSON plus the cached features. No re-carding.

```bash
# criterion must be slope -- a card judged on `hum` never uses the slope floor
# bar at -1.7: real EEG here is -1.35 to -1.64, so a stricter floor is unmeetable
```

| cohort | recording | positions | status |
|---|---|---|---|
| S-SL | `allego_0__uid0920-09-00-07` | A1 C1 D1 D2 | ✅ confirmed on re-card (thresholds −2.77 to −3.39) |
| S-SL | `allego_0__uid0921-00-17-34` | A1 A2 C1 D1 D2 | ✅ confirmed |
| W-SL | `allego_0__uid0917-09-00-09` | D2 / HLBWSL29 | ✅ confirmed (slope −1.494, rms 66.4, threshold −2.103) |
| S-SD | `allego_1__uid0826-12-50-16` | A1 / HLBSSD11 | ✅ confirmed (slope −1.329, rms 94.5, threshold −2.437) |

**11 cards of the 79 judged on slope.**

### Three flagged cards are GENUINE failures, not artifacts

The discriminator is amplitude. A contaminated-floor victim has healthy rms; a
real open electrode rails.

| recording | pos | slope | rms | read |
|---|---|---|---|---|
| `uid0825-09-00-00` | D1 | −0.105 | **2759 µV** | ❌ open, FAIL stands |
| `uid0826-12-50-16` | D1 | −0.023 | **2701 µV** | ❌ open, FAIL stands |
| `uid0819-17-25-20` | B1 | −0.480 | **2080 µV** | ❌ the chewed tether, FAIL stands |

✅ **W-SD's 39.7 h pre-CSD baseline is CLEAN.** The project's best full-cohort
data does not carry this artifact. Its one flagged card is a true failure.

> [!warning] A first pass said 35 cards. That was wrong.
> 16 of those were judged on the **hum** criterion, where the stored slope floor
> is never used, and several flagged FAILs are real open electrodes. Always
> filter on the criterion the EEG role actually used before counting.

## The fix as first proposed

`floor_stats()` needs a second validity test beside `grounded`: whether the
floor's own slope distribution is flat enough to be a negative control. When it
is not, the correct verdict is **UNJUDGEABLE, not FAIL** — the same treatment an
ungrounded chip already gets, and for the same reason. When the negative control
is invalid, no connection verdict can be drawn. Saying FAIL asserts something
about the animal that the data does not support.

Then re-card the four affected recordings only — `uid0920`, `uid0921`, `uid0917`,
`uid0826`. The scan bounds the blast radius, so a full five-cohort re-card is not
needed.

🔑 **Do not set the bar at −1.7 in code.** That number is an empirical property
of this rig's EEG, measured in 2026-09, and it belongs in `core/qc_thresholds.py`
as a named, dated constant if it is used at all. The better test is on the floor's
own distribution — how far its median sits from zero — not on a comparison with
EEG.

## The fix, as applied — 2026-09-26

`floor_stats()` now returns `slope_valid`, and rung 2 gives UNJUDGEABLE when the
EEG is judged on slope and the floor is not valid. The test is on the floor's own
threshold, never on a comparison with the animal:

```python
slope_valid = slope_p1 >= T.FLOOR_STEEPEST_VALID_SLOPE_P1   # -1.90
```

Across every grounded chip in 13 recordings, chips carrying a healthy EEG that
read 0.0% have thresholds of −2.10 to −3.51, and every other chip sits at −1.73
or flatter. −1.90 is in that empty gap. `tests/test_contaminated_floor.py` pins
the behaviour, including a dead EEG on a clean floor that must still FAIL.

🔴 **Two detectors were tried and rejected, both measured:**

1. **The 2026-08-27 proposal: the fraction of floor sites steeper than this
   animal's EEG.** It is circular. A dead electrode is as flat as the floor, so
   every site is "steeper" than it. It scored 1.00 / 1.00 / 0.93 on the three
   genuinely open electrodes and would have turned real failures into
   UNJUDGEABLE. **No test that compares the floor with the animal can tell "the
   floor looks like EEG" from "the EEG looks like the floor".**
2. **The floor's typical site, median of per-site medians, bar −0.85.** It shipped
   in `a52133c` and was falsified within the hour by the first recording it had
   not been fitted on. `uid0920` C1 has a typical site of −0.77 but a threshold of
   −3.00: the contamination is intermittent, and it lives in the tail, which is
   what sets the threshold.

⚠️ **Open:**
- **It is an empirical gap, 0.37 wide, from one rig.** Its edges are W-SL
  `uid0917` D2 (−2.10, the flattest victim) and the three genuine failures
  (−1.72 to −1.73). A new chip landing inside it is a reason to re-measure.
- **The hum criterion has a second route in.** `check_hum_validity()` cross-checks
  hum against the slope threshold, so on a contaminated floor a hum-judged EEG
  still FAILs by refusal. No affected recording is hum-judged; all 32 hum cards
  are the pooled-floor HLB-fem cohort.
- **UNJUDGEABLE is not PASS.** The fix withdraws false FAILs. It cannot confirm
  that the electrodes on those chips are connected.

## The 2026-08-27 page already said what to do

Quoting its open item, which is still open:

> The guard that exists refuses a verdict when a chip is **ungrounded**. There is
> no guard for a chip whose floor is grounded but **spectrally contaminated**, and
> on that chip the slope criterion cannot discriminate in either direction.

It also supplies a better detector than the −1.7 bar used in the scan: on a
contaminated chip, **a large fraction of the floor's own sites are steeper than
the animal's EEG**. On A1 that was 7 of 14. That is a self-contained test needing
no external constant.

## Why this is the same family as two known bugs

- [[weak-chip-ground-vs-open-electrode]] — a weak ground masquerading as a dead
  electrode. Same shape: a reference problem misread as an animal problem.
- The **pooled-floor bug**, fixed 2026-08-26, which condemned a whole rig when one
  headstage floated. The per-chip floor fixed the scope but not the validity.

The unifying lesson: **the floor is a measurement too, and it can be wrong.** Every
verdict that quotes a threshold derived from data should state whether that
threshold was itself checked.

## Related

[[03-troubleshooting/symptoms/weak-chip-ground-vs-open-electrode]] ·
[[02-procedures/eeg-data-analysis/animal-card-and-verdict-ladder]] ·
[[05-experiments/completed/2026-09-23-S-SL-connection-audit]] ·
[[05-experiments/completed/2026-09-18-W-SL-light-phase-sleep]] ·
[[05-experiments/completed/2026-08-27-B1-swap-baseline-20h-run]]
