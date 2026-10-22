---
name: floor-threshold-fixed-per-chip
description: "2026-08-26: floor threshold fixed in core/criteria.py (per-chip scope, site_p1_median estimator, ground-validity guard FLOOR_MIN_HUM_UV 800 => UNJUDGEABLE). Rule: chosen on robustness, not on which animals pass; falsification_check is weak on real data."
metadata: 
  node_type: memory
  type: project
  originSessionId: aa023ba0-4d68-4842-9819-c574f4dde34b
  modified: 2026-08-26T01:53:22.858Z
---

**Fixed 2026-08-26 (commit `7c08f40`), supersedes the pooled-floor bug:** (1) `FLOOR_SCOPE = "chip"`: each chip is judged against its own wire-free sites (uid0825: pooled -1.94 for every chip vs per-chip -0.77 to -2.06; pooled made the whole rig look dead); (2) `FLOOR_ESTIMATOR = "site_p1_median"` (percentile per site, then median across sites; across-chip spread 1.16 -> 0.96); (3) ground-validity guard `FLOOR_MIN_HUM_UV = 800`: a chip whose wire-free inputs sit below 800 uV of 60 Hz has no ground reference and rung 2 returns UNJUDGEABLE, not FAIL (stops B1/HLBSSD13 being published as a dead animal). Physically railed B2/D1 stay rejected.

Details: [[2026-08-26-per-chip-floor-fix]]

🛑 The estimator was chosen on ROBUSTNESS grounds, NOT by looking at which animals it passes. 🔴 `falsification_check` returns ~0 % on real chips because floor sites fail the amplitude window first: do not cite a 0 % rate on real data as evidence the threshold is right. ⛔ lf/hf separates better than slope (A1, A2, C1, C2, D2 separated; B2, D1 not) but is NOT implemented: swapping the discriminator needs pre-registration and the falsification suite. Later problem: the 800 uV gate after the 2026-10-07 grounding fix ([[grounding-fix-2026-10-07-mains-collapsed]]).
