---
name: contaminated-floor-rejects-good-eeg
description: "Rung 2 reports 0.0% usable on HEALTHY EEG when the chip's wire-free floor is spectrally contaminated. 11 cards affected. Known since 2026-08-27, still unfixed."
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

**Fix, not yet applied:** add a floor-validity test on the floor's own slope
distribution → **UNJUDGEABLE, not FAIL**, same as an ungrounded chip. Best
detector (from the 08-27 page): what fraction of the floor's sites are steeper
than the animal's EEG — 7 of 14 on that chip. Then re-card four recordings only.

⚠️ **Do not count affected cards without filtering on the criterion the EEG role
actually used.** A first pass said 35; 16 of those were judged on `hum`, where the
slope floor is never used.

🔴 **Stage 3 does not check the EEG is connected** — it gates on stage 1's
`epoch_ok`, not rung 2. It can score sleep from a dead EEG if the EMG is alive.

Vault: `03-troubleshooting/symptoms/contaminated-floor-rejects-good-eeg.md`.
Related: [[weak-chip-ground-hides-as-electrode-failure]],
[[emg-gate-passes-and-floor-bug]], [[animal-card-verdict-ladder]].
