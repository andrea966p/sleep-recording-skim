---
type: experiment
area: hlb-sod1
status: active
created: 2026-11-04
summary: "Hand-scored arm-entry sequences for the 10 NS-SD / NW-SD Y-maze videos (2026-11-04, straight after the second SD day); same rules as HLBNSL, letters copied into the scoring CSV for ymaze_nssd.py"
cohort: NS-SD + NW-SD (HLBNSSD51-55, HLBNWSD56-60)
tags: [behaviour, y-maze, sleep-deprivation, ns-sd, nw-sd]
---

# 2026-11-04: NS-SD Y-maze hand scoring

> [!abstract] What this is
> Andrea writes the arm-entry sequence of each NS-SD Y-maze video here, by eye, with the HLBNSL rules
> ([[2026-10-25-HLBNSL-ymaze-hand-scoring]]), so SA % and arm entries are comparable between the cohorts. Claude then
> copies the letters into `nanotag/analysis/behavior/NSSD_ymaze_hand_scoring.csv` and runs `ymaze_nssd.py`
> ([[2026-11-03-NS-SD-run2-and-ymaze-runbook]]). Distance and velocity come from pose tracking, not from here.

## Rules (same as HLBNSL)
- The whole 480 s trial, from door closed.
- **Arm A** = the arm toward the ceiling vent, if visible in the new camera view; otherwise name the landmark you use in
  the first mouse's notes and keep it for all ten. Then **B** and **C** clockwise.
- An entry = **all four paws** inside the arm. A head dip or half-body entry does not count.
- A return into the same arm counts again (`aa`) only if all four paws went into the centre first.
- Letters in order, no spaces needed. Unsure: brackets with the time, e.g. `(b 3:12)`, decide later.
- Optional, against bias: score in a different order from the test order, without looking at the group.

Test order 51, 56, 52, 57, 53, 58, 54, 59, 55, 60, from 15:00, about 15 min per mouse (start times approximate).

Order confirmed by Andrea on 11-05: 60 last (an earlier office PC note saying 55 last was wrong).

Clips to score: `HLBN*_ymaze_trial480s.mp4`, each 480 s from the moment the hand is out of view (SOP changelog
2026-11-04), on the office PC in `~/ymaze_nssd/trial_8min/`.

## HLBNSSD51 (SOD1, about 15:00)
File:

Sequence:

```
cabcaccbcababccbcabcbcabacacbcb 
```

Notes:

## HLBNWSD56 (water, about 15:15)
File:

Sequence:

```
cabccbacbaccacbcacacbacbcababcbacbacbaaacc
```

Notes:

## HLBNSSD52 (SOD1, about 15:30)
File:

Sequence:

```
cbcabccabcbcabacbacbcacbbcbacabcab
```

Notes:

## HLBNWSD57 (water, about 15:45)
File:

Sequence:

```
cacabcabacabababcbacbababacabacabab
```

Notes: typed `n` for `b` throughout, corrected by Claude 2026-11-05 at Andrea's request (`n` is next to `b` on the keyboard).

## HLBNSSD53 (SOD1, about 16:00)
File:

Sequence:

```
cbbcacbacbabcabcbababcbacbabcababb
```

Notes:

## HLBNWSD58 (water, about 16:15)
File:

Sequence:

```
cbaccbcabcacbacbcabcbabcbacbacbcabcb
```

Notes:

## HLBNSSD54 (SOD1, about 16:30)
File:

Sequence:

```
cbcabcabacabacbcacbaacbbabcabcb
```

Notes:

## HLBNWSD59 (water, about 16:45)
File:

Sequence:

```
cbcabacabacabbacbabcbabababa
```

Notes:

## HLBNSSD55 (SOD1, about 17:00)
File:

Sequence:

```
cabcabcbbcacabccabcacbbacbbbcacacbcacbcacbbcabba
```

Notes:

## HLBNWSD60 (water, about 17:15)
File:

Sequence:

```
cbaccbacabacbaccbacbcbabcabacbcbaca
```

Notes:

## Still open
- [x] All ten sequences written.
- [x] Copied into the CSV and `ymaze_nssd.py` run (NS-SD next to HLBNSL, SA % vs real SD length), 2026-11-05: [[2026-11-05-NS-SD-ymaze-results]].
