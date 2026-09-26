---
name: contaminated-floor-rejects-good-eeg
description: "Rung 2 reported 0.0% usable on HEALTHY EEG when a chip's wire-free floor carried signal. FIXED 2026-09-26 (2cc5892): floor slope threshold steeper than -1.90 => UNJUDGEABLE. Never compare floor with the animal (circular)."
metadata:
  node_type: memory
  type: project
  originSessionId: e12a4d2d-f4ec-4c07-aac7-6552d9960701
  modified: 2026-09-26T04:03:44.078Z
---

🔴🔴 **A contaminated QC floor makes rung 2 report `0.0% usable` on a perfectly
working electrode.** `floor_stats()` in `core/criteria.py:666` validates the floor
ONLY on hum (`grounded = hum_median >= FLOOR_MIN_HUM_UV`). Nothing checks that the
wire-free reference inputs are actually spectrally FLAT. When they carry signal,
the slope threshold tightens to **−2.4…−3.5** where real EEG on this rig is
**−1.35 to −1.64** at rms 66–95 µV. Nothing passes, and the card says 0.0% with no
hedge.

🔑 **Discriminator is AMPLITUDE.** Artifact victim = healthy rms (66–95 µV). Real
open electrode = **rails at 2000+ µV** with slope near 0.

⭐ **11 of 79 slope-judged cards affected**, measured 2026-09-26:
`uid0921` (A1 A2 C1 D1 D2), `uid0920` (A1 C1 D1 D2), `uid0917` (D2/HLBWSL29),
`uid0826` (A1/HLBSSD11).
✅ **W-SD's 39.7 h pre-CSD baseline is CLEAN.** ✅ **No false PASSes** — the error
is one-directional, it only ever rejects good data.

🛑 **Known since 2026-08-27** — diagnosed completely on the B1-swap page
(mechanism, correct verdict UNJUDGEABLE, missing guard) and left as an open item
on one experiment page. A month later it produced a **wrong published conclusion**
for S-SL — an "attrition" of five electrodes that never happened. The lesson is
less the bug than the fact that a finding on one experiment page never reached the
engine or the other cohorts.

✅ **FIXED 2026-09-26, commits `a52133c` + `2cc5892`.** `FloorStats.slope_valid` =
floor's own `slope_p1 >= FLOOR_STEEPEST_VALID_SLOPE_P1` (−1.90); rung 2 →
UNJUDGEABLE when EEG is slope-judged and floor invalid. Measured gap over 13
recordings: victims −2.10…−3.51, everything else ≥ −1.73 (edge = the 3 genuine
open electrodes, −1.72/−1.73). Re-carded uid0920/0921/0917/0826: exactly the 11
cards moved, nothing else. Test: `tests/test_contaminated_floor.py`.

🛑 **Two detectors REJECTED by measurement — do not resurrect them:**
1. "fraction of floor sites steeper than the animal's EEG" (the 08-27 idea) is
   CIRCULAR: a dead electrode is as flat as the floor ⇒ scored 1.00/1.00/0.93 on
   the 3 genuinely open electrodes. No floor-vs-animal comparison can work.
2. "typical floor site" (median of per-site medians, −0.85) — falsified by
   uid0920 C1 (typical −0.77, threshold −3.00). Contamination can be
   INTERMITTENT; it lives in the tail, and the tail sets the threshold.

⚠️ Still open: `check_hum_validity()` cross-checks hum against the SLOPE threshold
⇒ hum-judged EEG on a contaminated floor still FAILs by refusal (no affected card
is hum-judged). UNJUDGEABLE ≠ PASS: S-SL paired n=3 is a STAGE 3 claim; ladder
can't confirm A1/C1 at endpoint. W-SL n stays 1 (D2 baseline fails rung 3).
S-SL ladder-level paired n = 1 (B1) after re-carding uid0912; stage 3 paired n = 3.

⚠️ **Do not count affected cards without filtering on the criterion the EEG role
actually used.** A first pass said 35; 16 of those were judged on `hum`, where the
slope floor is never used.

🔴 **Stage 3 does not check the EEG is connected** — it gates on stage 1's
`epoch_ok`, not rung 2. It can score sleep from a dead EEG if the EMG is alive.

Vault: `03-troubleshooting/symptoms/contaminated-floor-rejects-good-eeg.md`.
Related: [[weak-chip-ground-hides-as-electrode-failure]],
[[emg-gate-passes-and-floor-bug]], [[animal-card-verdict-ladder]].
