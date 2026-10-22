---
tags: [experiment, eeg, sleep, W-SL, light-phase, provisional]
created: 2026-09-18
status: provisional
recordings: [allego_0__uid0910-09-00-00, allego_0__uid0917-09-00-09]
---

# W-SL light-phase sleep: baseline 2026-09-10 vs the run of 2026-09-17

> [!abstract] TL;DR
> The first sleep analysis of the W-SL batch. **Slow-wave activity declines
> monotonically across the light phase in every mouse on both recordings** —
> Process S discharging, reproduced across animals and a week apart. That is the
> strongest evidence here that the staging tracks real sleep.
>
> 🛑 **Only B2 is judgeable and accepted on both days.** Everything else changed
> status between recordings, so there is one within-animal comparison and no
> group statistics are warranted. ✅ **Re-derived 2026-09-26 after the floor fix:
> still n = 1.** D2 cannot pair, because its BASELINE fails scoreability, whatever
> its 09-17 connection verdict. See the re-card section at the end.
>
> 🔴 **Grounding got worse, not better.** 7 of 8 chips grounded on 09-10, 5 of 8
> on 09-17. A2, C1 and D1 lost their ground; A1 gained one and lost its EEG.

## What was compared

| | baseline | current |
|---|---|---|
| recording | `allego_0__uid0910-09-00-00` | `allego_0__uid0917-09-00-09` |
| start | 2026-09-10 08:59:59 KST, ZT0 | 2026-09-17 09:00:09 KST, ZT0 |
| full length | 24.39 h | 28 h scheduled, still running at analysis time |
| **window used** | **ZT0-12** | **ZT0-12** |

⚠️ The 09-17 file was **still being written**. Stage 1 and stage 2 therefore saw
different lengths and stage 3 died on the mismatch. The closed light phase was
used instead of patching stage 3 to tolerate inconsistent input. Re-run the whole
chain on the finished file before quoting any of this.

🛑 `allego_1__uid0909-21-17-52` is the **83 min pre-flight screen**, not the
baseline. It contains no scoreable sleep in any animal (`r@1min` 0.051-0.17,
7/7 REJECT) — 83 min of dark phase cannot, by construction.

## Sleep features, light phase ZT0-12

Judgeable = chip ground floor ≥ `FLOOR_MIN_HUM_UV` (800 µV). Accepted = stage 3
verdict SCOREABLE.

| | floor µV | sleep % | wake % | NREM % | latency | trans/h | NREM bout med | wake bout med | r@1min | SWA decline | status |
|---|---|---|---|---|---|---|---|---|---|---|---|
| A2 09-10 | 2560 | 84.1 | 15.9 | 72.8 | 0.7 min | 37.2 | 68 s | 40 s | 0.404 | −33% | accepted |
| A2 09-17 | 582 | 98.1 | 1.9 | 85.2 | 0.0 min | 28.8 | 120 s | 20 s | 0.097 | −25% | **UNJUDGEABLE** |
| B1 09-10 | 2147 | 88.9 | 11.1 | 75.8 | 0.0 min | 40.9 | 80 s | 28 s | 0.316 | −22% | rejected, wake 11.1% |
| B1 09-17 | 2907 | 77.8 | 22.2 | 63.6 | 2.9 min | 34.9 | 88 s | 28 s | 0.646 | −36% | accepted |
| B2 09-10 | 3449 | 81.4 | 18.6 | 71.7 | 11.7 min | 32.1 | 88 s | 46 s | 0.433 | −44% | accepted |
| B2 09-17 | 1670 | 77.3 | 22.7 | 66.8 | 16.5 min | 27.6 | 130 s | 24 s | 0.642 | −33% | accepted |
| C2 09-17 | 4084 | 37.7 | 62.3 | 32.2 | 0.0 min | 26.7 | 48 s | 52 s | 0.635 | −45% | accepted |
| D1 09-10 | 3346 | 80.8 | 19.2 | 69.5 | 1.3 min | 34.2 | 82 s | 40 s | 0.443 | −18% | accepted |
| D1 09-17 | 2 | 87.6 | 12.4 | 75.0 | 0.0 min | 36.4 | 72 s | 36 s | 0.302 | −28% | **UNJUDGEABLE** |
| D2 09-10 | 2870 | 92.0 | 8.0 | 79.7 | 0.0 min | 40.9 | 88 s | 20 s | 0.231 | −29% | rejected, r and wake |
| D2 09-17 | 2584 | 76.9 | 23.1 | 65.5 | 4.1 min | 35.9 | 76 s | 42 s | 0.476 | −43% | accepted; rung 2 **UNJUDGEABLE** (floor carrying signal, 2026-09-26) |

A1 and C1 are absent: A1's EEG is dead on 09-17 (5.0 µV median) and both port C
slots were OPEN on 09-10 with broken EMG conductors. C1 on 09-17 reads SCOREABLE
with the file's best persistence (0.697) **on a chip whose floor is 7 µV** — the
exact trap the floor test exists to catch.

🛑 **REM is not reported.** Stage 3 defines it as the top 20% of theta/delta among
non-wake epochs, so its percentage and bout counts are fixed by the rule, not
measured; the field is named `rem_pct_CONSTRUCTED`. What is evidence is REM
ORDER, and REM was entered from NREM in **83.9-96.4%** of entries in every animal
on both days.

## Figures

![[2026-09-18-W-SL-fig01-hypnograms.png]]
**Fig 1.** Hypnograms, one mouse-recording per row, days paired under each mouse.
Grey = ungrounded chip: the states were computed but are not evidence. Red ticks
mark epochs that failed QC and carry no assignable stage (C2 only, 0.8%) — these
are gaps, not sleep and not wake.

![[2026-09-18-W-SL-fig02-timecourse.png]]
**Fig 2.** Per mouse, hourly. Each point is 900 epochs. **No interval is drawn**:
epochs within an animal are strongly autocorrelated, so a binomial or bootstrap
interval over them would be anticonservative. SWA is normalised to each animal's
own ZT0-1 mean because absolute delta depends on electrode impedance and
placement.

![[2026-09-18-W-SL-fig03-architecture.png]]
**Fig 3.** Per mouse. The two days are joined by a line **only where both are
judgeable and accepted** — a line from a real animal to an ungrounded chip would
draw a change that is not one. Only B2 qualifies.

⚠️ An earlier version of Fig 2 plotted a **mean across animals**. That compared
A2+B2+D1 against B1+B2+C2+D2 — largely different mice — and read as a
within-animal change. Retracted; nothing here is pooled.

## Findings

✅ **SWA declines monotonically ZT0 → ZT12 in every mouse, both recordings**,
100% down to 40-72%. Holds even on the ungrounded chips. Homeostatic sleep
pressure discharging, reproduced independently twice.

⭐ **B2, the only within-animal comparison:** sleep essentially unchanged
(81.4 → 77.3%) but restructured — NREM bouts 88 → 130 s, wake bouts 46 → 24 s,
transitions 32.1 → 27.6/h, `r@1min` 0.433 → 0.642. Same sleep, longer blocks.
**n = 1.**

🔴 **C2 stops sleeping in the back half of the light phase** — ~50% sleep at ZT0
falling to **4-11% over ZT9-12**, the shortest NREM bouts in the set (48 s median).
Its chip floor is 4084 µV, so this is the animal and not the hardware.

⚠️ **Four baseline animals were rejected for implausibly LOW wake** (A1 7.7%,
B1 11.1%, D2 8.0%, all under `WAKE_LO` = 15%). On 09-17 the same positions sit at
22-23%. Whether that is habituation or a shift in the per-animal Otsu cut is not
resolved here.

## What this does not support

- No group statistics: n = 3 and n = 4 with one animal in common.
- Rung 4 ARCHITECTURE is **provisional until a scoring kappa**.
- 09-17 is a truncated window of an unfinished recording.
- W-SL still has **no cohort manifest**, so `cards/ladder.py` cannot produce
  animal cards and these tables are ad hoc rather than card-derived.

## Provenance

Chain: `pipeline/stage1_qc.py` → `stage2_split.py` → `stage3_features.py`, ZT0-12.
Every threshold from `core/qc_thresholds.py`. Chip floors measured separately as
the 55-65 Hz amplitude of each chip's 14 wire-free inputs, median of 3 × 5 min in
ZT4-8. Figure export manifests are stored beside the images
(`*-export.json`): dimensions, dpi, transformations, uncertainty policy and
exclusion rule.

Figures built with the `scientific-visualization` skill, Okabe-Ito on white,
180 mm wide, 600 dpi. `palette_audit` reports grayscale ΔL\* = 8.2 between the two
day colours ("review"), so recording day is **also** encoded by marker shape.
PDF properties were NOT machine-inspected (`pypdf` absent) and nothing here is
checked against a journal's requirements.

## Added 2026-09-23 — the baseline now has a manifest, a QC bundle and a stripped copy

None of this changes a number above. The sleep analysis on this page was run
against the raw file and stands. What was missing was everything *around* it.

**The W-SL batch had no cohort manifest until 2026-09-23.** `cards/ladder.py`
requires `--cohort`, so the baseline had never been through the verdict ladder,
and `convert/strip_channels` refuses to strip a recording with no QC bundle —
stripping to 16 channels deletes the wire-free floor the connection criterion is
measured against, permanently. So the baseline had also never been stripped and
had never reached the NAS. It existed as raw on e10 and nowhere else.

`cohorts/W-SL.yaml` now exists. Ladder verdicts for the baseline:

| pos | animal | 2 CONN | 3 SCORE | 4 ARCH |
|---|---|---|---|---|
| A1 | HLBWSL21 | UNJUDGEABLE | BLOCKED | BLOCKED |
| A2 | HLBWSL22 | PASS | PASS | PROVISIONAL |
| B1 | HLBWSL23 | PASS | FAIL | BLOCKED |
| B2 | HLBWSL24 | PASS | PASS | PROVISIONAL |
| C1 | HLBWSL25 | FAIL | BLOCKED | BLOCKED |
| C2 | HLBWSL26 | FAIL | BLOCKED | BLOCKED |
| D1 | HLBWSL27 | PASS | PASS | PROVISIONAL |
| D2 | HLBWSL29 | PASS | FAIL | BLOCKED |

⚠️ **These are rung verdicts, not this page's accepted set.** The ladder asks
whether the sleep question can be asked at all; the analysis above then applies
its own stage-3 criteria on top, including the `WAKE_LO` rejections in the
section on implausibly low wake. The two sets are allowed to differ and do.

The baseline is now stripped (**22 channels, not 16** — gate B refused to drop
`din_1`, which carries 460 transitions in this recording where every other
recording has it flat) and verified on the SKIM NAS at
`20260910_HLBWSL_BSR/`, with its QC bundle alongside. Naming
and inventory: [[CANONICAL-recording-naming-and-inventory]].

## Added 2026-09-26 — re-carded after the floor-validity fix; the n is still 1

`allego_0__uid0917-09-00-09` was re-carded with the fix to `floor_stats()` that
adds a second validity test on the floor: a grounded chip whose own slope
threshold is steeper than `FLOOR_STEEPEST_VALID_SLOPE_P1` (−1.90) is not a valid
negative control for the slope criterion, and the verdict is UNJUDGEABLE, not
FAIL. See [[contaminated-floor-rejects-good-eeg]].

**One verdict changed: D2 / HLBWSL29, rung 2 FAIL → UNJUDGEABLE.** Its chip's
threshold is −2.103 where D2's own EEG reads −1.494 at 66.4 µV. The other seven
cards are unchanged at every rung.

⚠️ **D2 is the closest call in the whole scan.** −2.10 is the flattest
contaminated threshold on the rig, 0.20 past the bar; the steepest valid one is
−1.73. It is on the right side of a measured empty gap, but it is the case to
re-examine first if the bar is ever revisited.

| pos | animal | 09-10 rung 2 | 09-10 rung 3 | 09-17 rung 2 | 09-17 rung 3 | pairs? |
|---|---|---|---|---|---|---|
| A1 | HLBWSL21 | UNJUDGEABLE | BLOCKED | FAIL | BLOCKED | ❌ |
| A2 | HLBWSL22 | PASS | PASS | UNJUDGEABLE | BLOCKED | ❌ |
| B1 | HLBWSL23 | PASS | FAIL (r 0.255) | PASS | PASS | ❌ |
| **B2** | **HLBWSL24** | PASS | PASS (r 0.454) | PASS | PASS (r 0.697) | ✅ |
| C1 | HLBWSL25 | FAIL | BLOCKED | UNJUDGEABLE | BLOCKED | ❌ |
| C2 | HLBWSL26 | FAIL | BLOCKED | PASS | FAIL | ❌ |
| D1 | HLBWSL27 | PASS | PASS | UNJUDGEABLE | BLOCKED | ❌ |
| D2 | HLBWSL29 | PASS | **FAIL (r 0.174)** | **UNJUDGEABLE** | BLOCKED | ❌ |

🔑 **D2 was never going to change the n.** The worry recorded here on 2026-09-26
was that a connected D2 on 09-17 would make a second pair. But D2 fails
scoreability at **baseline**: the ladder gives `r@1min` 0.174 over the full file,
and this page's own ZT0-12 analysis rejected it on r and on wake at 8.0%. No
09-17 verdict could pair it. B2 remains the only within-animal comparison.

⚠️ **The fix also cannot say D2 is connected on 09-17.** UNJUDGEABLE means the
chip has no valid control, not that the electrode passed. Stage 3 accepts it at
`r@1min` 0.476 and the raw EEG looks healthy (slope −1.494, 66.4 µV), which is
suggestive, but stage 3 does not test connection.

✅ **B2's floor is valid with room to spare**: threshold −1.38, 0.52 inside the
bar. Its PASS is also on one of the stricter floors on the rig, so if anything
it is conservative.

## Related

[[recording-2026-09-17-HLBW_SL-28h]] · [[animal-card-verdict-ladder]] ·
[[weak-chip-ground-hides-as-electrode-failure]] · [[live-signal-quality-terms]]
