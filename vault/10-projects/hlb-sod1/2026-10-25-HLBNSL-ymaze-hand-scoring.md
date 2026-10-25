---
type: experiment
area: hlb-sod1
status: active
created: 2026-10-25
summary: "Hand-scored arm-entry sequences for the 9 HLBNSL Y-maze videos: 41, 46, 50 first (threshold check), the other 6 after Andrea chose hand scoring as primary"
tags: [behaviour, y-maze, validation, hlbnsl]
---

# 2026-10-25: HLBNSL Y-maze hand scoring (threshold validation)

> [!abstract] TL;DR
> Andrea writes the arm-entry sequence of 3 videos by eye. Claude compares them with EthoVision
> at zone exit thresholds of 1, 2, 3 and 4 cm. The best match becomes the final threshold in
> `BEHAVIOR_SOP.md`, and [[2026-10-25-HLBNSL-ymaze-results]] loses "provisional".

## Rules (same for all 3 videos)
- Videos: `Desktop\Nanotag videos upright\Y-maze\trial_8min\` on `kaist-bilab-win`, the whole
  480 s clip (it already starts at door closed).
- Letters as in the EthoVision zones: **A** = the arm toward the ceiling vent, then **B** and **C**
  clockwise.
- An entry = **all four paws** inside the arm. A head dip or a half-body entry does not count.
- A return into the same arm counts again (`A A`) only if all four paws went into the centre
  first.
- Write the letters in order, no spaces needed. If unsure about one, put it in brackets with the
  time, e.g. `(B 3:12)`, and decide later.

## HLBNSSL41 (SOD1)
File: `HLBNSSL41_Ymaze_20260930_145651_trial480s.mp4`

Sequence:

```
 cabacabcacbacabccbaccabacbacbacbcbabcacabacbcabcaabacbacbcb
```

Notes:

## HLBNWSL46 (water)
File: `HLBNWSL46_Ymaze_20260930_161102_trial480s.mp4`

Sequence:

```
 cbacbcabcababccabacabcbacabcabccabcbcba
```

Notes: seems to be more regular compared to 41 for alternating the arm entries

## HLBNWSL50 (water)
File: `HLBNWSL50_Ymaze_20260930_165407_trial480s.mp4`

Sequence:

```
 cababcacabcacabcacabcbcbabcabcba
```

Notes:

## Redrawn zones with a gap (2026-10-25, trials 10-18, arenas `…b`)
Arm zones start about 3 cm into each arm, centre triangle in every arena (41b and 50b now have
one). Export: `Statistics-Nanotag_normalsleep_ymaze_gapzones.xlsx`.

| Mouse | Hand | Gap zones, 2-4 cm (entries / SA %) | Old zones, 3 cm |
|---|---|---|---|
| HLBNSSL41 | 59 / 63.2 | 61 / 62.7 | 63 / 67.2 |
| HLBNWSL46 | 39 / 62.2 | 42 / 60.0 | 49 / 66.0 |
| HLBNWSL50 | 32 / 56.7 | 35 / 45.5 | 38 / 52.8 |

- With the gap, the exit threshold barely matters: 2, 3 and 4 cm give the same numbers in 8 of 9
  mice. The gap does the job.
- **Entries now match the eye** (+2, +3, +3, i.e. 3-9 % too many, against 7-26 % before).
- **SA% per mouse still differs** by 0.5, 2.2 and 11.2 points. One misplaced entry changes up to
  three triplets, so with 30-60 entries a single disagreement moves SA% by several points.
- Redrawing moved some mice a lot (HLBNSSL49 58.8 → 45.7 %, HLBNWSL48 59.2 → 50.0 %): EthoVision SA%
  per mouse depends on how the zones are drawn. This supports hand scoring as the primary SA%.

## The other 6 mice (added 2026-10-25: Andrea decided to hand-score all 9)
Same rules as above. Hand scores become the primary SA% and arm-entry endpoint; EthoVision gives
distance and velocity, and is re-checked against all 9 after the arm zones are redrawn.

### HLBNSSL42 (SOD1)
File: `HLBNSSL42_Ymaze_20260930_151353_trial480s.mp4`

Sequence:

```
 cbabcbcabcabcbacbcabccabcacbcbcabbacbacbcacbcbacbacbc
```

Notes: seems to not like arm a

### HLBNSSL44 (SOD1)
File: `HLBNSSL44_Ymaze_20260930_152905_trial480s.mp4`

Sequence:

```
 cbacbacbcacbcaabcabcacabbcabababcabcabab
```

Notes: seems to spend a lot of time in the center

### HLBNSSL49 (SOD1)
File: `HLBNSSL49_Ymaze_20260930_154423_trial480s.mp4`

Sequence:

```
 cbcbaabcacbcbcabcbcabacbcbacabbcbacbacbab
```

Notes: i think this one doesn't perform well

### HLBNWSL45 (water)
File: `HLBNWSL45_Ymaze_20260930_155744_trial480s.mp4`

Sequence:

```
 cabcbacbacbcbcabcbacacabcabcabcabcabcbcacbabbcb
```

Notes: seems to perform good, maybe water mice actually perform better than sod1 mice, just my observation

### HLBNWSL47 (water)
File: `HLBNWSL47_Ymaze_20260930_162754_trial480s.mp4`

Sequence:

```
 cababcbacbacabcacbacbabcacabcabacabcba
```

Notes:

### HLBNWSL48 (water)
File: `HLBNWSL48_Ymaze_20260930_164116_trial480s.mp4`

Sequence:

```
 cbacbacbcacbcbccbacacbabcbabcacbacbc
```

Notes:

## EthoVision for comparison (filled in by Claude after scoring)

| Mouse | Hand entries | Hand SA % | 1 cm | 2 cm | 3 cm | 4 cm |
|---|---|---|---|---|---|---|
| HLBNSSL41 | 59 | 63.2 | 77 / 49.3 | 69 / 62.7 | 63 / 67.2 | 61 / 66.1 |
| HLBNWSL46 | 39 | 62.2 | 60 / 51.7 | 53 / 66.7 | 49 / 66.0 | 46 / 72.7 |
| HLBNWSL50 | 32 | 56.7 | 48 / 37.0 | 42 / 45.0 | 38 / 52.8 | 37 / 48.6 |

EthoVision cells are "arm entries / SA %" (entries = Max alternations + 2). Hand values scored
with `metrics.py` (re-entries kept); direct revisits by hand: 41 = 3, 46 = 2, 50 = 0.

## Result (2026-10-25)
- **SA%:** 3 cm matches the hand scores best: off by 4.0, 3.8 and 3.9 points (mean 3.9), against
  5.6 at 2 cm and 7.2 at 4 cm. The order of the 3 mice is the same as by hand.
- **Arm entries:** EthoVision counts more entries than the eye at every threshold. At 3 cm:
  +4 (41), +10 (46), +6 (50), i.e. 7 to 26 % too many. The exit threshold only stops false
  *re-entries*; the extra entries are partial entries (the centre-point crosses into the arm
  without all four paws), which only an arm zone starting further into the arm would remove.
- So 3 cm is kept for SA%. EthoVision arm entries are inflated against the four-paw criterion
  and are reported as a relative (locomotor) measure only.
