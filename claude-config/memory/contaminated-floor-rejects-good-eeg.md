---
name: contaminated-floor-rejects-good-eeg
description: "A contaminated QC floor made rung 2 report 0.0 % usable on healthy EEG; FIXED 2026-09-26 (floor slope steeper than -1.90 => UNJUDGEABLE). Never compare the floor with the animal (circular). Milder case 2026-10-06."
metadata:
  node_type: memory
  type: project
  originSessionId: e12a4d2d-f4ec-4c07-aac7-6552d9960701
  modified: 2026-09-26T04:03:44.078Z
---

**Found 2026-08-27, fixed 2026-09-26 (commits `a52133c` + `2cc5892`):** when a chip's wire-free floor carries signal, `floor_stats()` tightened the slope threshold to -2.4...-3.5 and healthy EEG (rms 66-95 uV, slope -1.35...-1.64) scored 0.0 %; 11 of 79 slope-judged cards were affected, nothing falsely passed. Fix: floor `slope_p1 < -1.90` => rung 2 UNJUDGEABLE. Discriminator is amplitude (victim = healthy rms; a real open electrode rails at 2000+ uV). A milder case slipped under -1.90 on 2026-10-06 (HLBSSD11, floor -1.52): signature = the rung-2 pass rate follows sleep state (wake 2 %, NREM 81 %).

Details: [[contaminated-floor-rejects-good-eeg]]

🛑 NEVER test the floor against the animal: "fraction of floor sites steeper than the animal's EEG" is CIRCULAR (a dead electrode is as flat as the floor) and the "typical floor site" test is falsified by uid0920 C1 (contamination is intermittent, the tail sets the threshold). Do not resurrect either. UNJUDGEABLE is NOT PASS. Do not count affected cards without filtering on the criterion the EEG role actually used (35 vs 11). 🔴 Stage 3 does not check the EEG is connected (it gates on stage 1's `epoch_ok`, not rung 2): it can score sleep from a dead EEG if the EMG is alive. Open: hum-judged EEG on a contaminated floor still FAILs by refusal.

Rules:
🛑 **Two detectors REJECTED by measurement — do not resurrect them:**
1. "fraction of floor sites steeper than the animal's EEG" (the 08-27 idea) is
   CIRCULAR: a dead electrode is as flat as the floor ⇒ scored 1.00/1.00/0.93 on
   the 3 genuinely open electrodes. No floor-vs-animal comparison can work.
2. "typical floor site" (median of per-site medians, −0.85) — falsified by
   uid0920 C1 (typical −0.77, threshold −3.00). Contamination can be
   INTERMITTENT; it lives in the tail, and the tail sets the threshold.
