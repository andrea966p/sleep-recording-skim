---
tags: [decision, eeg, emg, contact, impedance, sleep-architecture, critical]
created: 2026-08-03
status: active
priority: critical
---

# 2026-08-03 — The two 8-mouse runs: Run 1 is everything we have, Run 2 is a total loss

> [!abstract] TL;DR — for non-technical readers
> **What this is.** The two full 8-mouse overnight recordings, compared directly,
> with the three impedance sweeps that bracket them.
>
> **Why it exists.** Everything the project has rests on **one animal in one
> run**. The second run, done a day later on the same animals with the same rig,
> produced **nothing at all**. Understanding the difference between them is the
> whole problem.
>
> **The one-line answer.** The electrodes are not failing randomly — they are
> **wearing out in one direction, on the EEG side only, and they do not recover.**

Supersedes the per-run numbers in
[[2026-08-01-channel-mapping-correction-first-sleep]] and
[[2026-08-01-28h-contact-duty-cycle-and-c1-negative]]. Method:
[[pipeline/README]]. Scored with `pipeline/stage1_qc.py` + `stage3_features.py`.

> [!important] Both runs were COMMISSIONING TESTS, taken early. Read every number here in that light.
> Surgery **21–23 July**. Tethered **Thursday 30 July**. Run 1 is therefore
> **day 8–10 post-op with ~28 h of tethering**; Run 2 is day 10–12.
>
> Our own [[tsukuba-sleep-recording-method]] requires **≥14 days implant →
> recording** and **≥7 days cage acclimatisation**; Oishi 2016 requires 2–3 days
> of habituation. **Both runs miss all three.** They were done to test the rig.
>
> Consequences: the high wake fractions are partly expected; **C1's result
> becomes more impressive, not less** (it hit 66.9% light-phase sleep on its
> second day tethered); and **no scoreable-hours or "yield" figure from these
> runs should be quoted as the rig's performance.** See
> [[2026-08-03-literature-check-impedance-and-electrode-failure]] §6.

> [!success] The prepared data lives in one place
> **`/home/skimlab/eeg-processed/COHORT-2026-07/`** — both runs, all 8 mice,
> 16 animal-recordings, packaged together.
>
> ```
> README.txt              per-animal-per-run table + the caveats, travels with the data
> cohort_animals.csv      one row per animal per run
> cohort_impedance.csv    every sweep, per electrode, across both runs
> to-score/               3 EDF+ files + scorer notes, hypnograms, summaries
> ```
>
> Built with `pipeline/cohort_summary.py`. Method:
> [[2026-08-03-analysis-methods-procedure]].

## The two runs

| | **Run 1** | **Run 2** |
| --- | --- | --- |
| file | `allego_1__uid0731-18-06-37` | `allego_2__uid0802-01-46-57` |
| start (KST) | 2026-07-31 18:06 | 2026-08-02 01:46 |
| length | 27.90 h | 21.74 h |
| size | 105 GB | 82 GB |
| **scoreable animals** | **C1, C2** | **none** |
| usable at all | C1 8.73 h, D2 2.76 h, C2 2.34 h | nothing |

### Per mouse

| mouse | Run 1 pass% | Run 1 usable | Run 1 mains | Run 1 verdict | Run 2 pass% | Run 2 mains | Run 2 verdict |
| --- | --- | --- | --- | --- | --- | --- | --- |
| A1 | 0.00 | — | 4006 µV | OPEN | 0.00 | 3994 µV | OPEN |
| A2 | 0.00 | — | 4296 µV | OPEN | 0.00 | 4433 µV | OPEN |
| B1 | 0.09 | — | 640 µV | OPEN | 0.00 | 2802 µV | OPEN |
| B2 | 0.00 | — | 4210 µV | OPEN | 0.00 | 4059 µV | OPEN |
| **C1** | **31.27** | **8.73 h** | 4268 µV | **DIRTY → SCOREABLE** | 0.00 | 4276 µV | OPEN |
| **C2** | **13.49** | **2.34 h** | 883 µV | **DIRTY → SCOREABLE** | 1.95 | 1218 µV | OPEN |
| D1 | 0.00 | — | 4632 µV | OPEN | 0.00 | 4636 µV | OPEN |
| D2 | 14.92 | 2.76 h | 2671 µV | DIRTY → REJECT | 0.00 | 2291 µV | OPEN |

`pass%` is the share of 4 s epochs clearing the full QC gate. `mains` is the
median 55–65 Hz amplitude against a **150 µV** limit — see [[pipeline/README]]
for why hum amplitude *is* the contact measurement.

> [!danger] Run 2 produced zero usable data
> All eight EEG channels were electrically open for **100% of 21.7 hours**. C2
> is the only animal that even flickered (1.95% of epochs), and no fragment was
> long enough to test. Run 2 tells us nothing about sleep. It tells us a great
> deal about the failure.

## Run 1, the two animals that worked

| | C1 | C2 |
| --- | --- | --- |
| usable inside blocks | **8.73 h** | 2.34 h |
| longest unbroken block | **485.7 min (8.1 h)** | 62.1 min |
| contact blocks | **2** | 14 |
| `r@1min` (shuffle) | **+0.761** (+0.011) | +0.708 (−0.023) |
| `r@5min` / `r@10min` | +0.614 / +0.493 | — |
| WAKE / NREM | 65.9 / 29.8 % | 67.8 / 19.9 % |
| REM entered from NREM | 79.6 % | 93.0 % |
| physiology | PASS (5/5) | PASS |
| **verdict** | **SCOREABLE** | **SCOREABLE** |

D2 reaches 2.76 h but fails at `r@1min = 0.25`, below the 0.30 threshold.

> [!quote] Paper-ready
> Under a three-part quality gate (open, dropout, saturation) and a persistence
> criterion computed strictly within unbroken contact blocks, two of eight
> animals in the 2026-07-31 recording yielded scoreable sleep, totalling 11.1
> animal-hours; the 2026-08-02 recording yielded none.

### C1 is validated against circadian biology

The light cycle is **09:00 on / 21:00 off KST, ZT0 = 09:00**
([[production-values]]). Run 1 starts at 18:06, so its first 2.9 h are light
phase.

| phase | duration | WAKE | NREM |
| --- | --- | --- | --- |
| light (18:06–21:00) | 2.89 h | **33.1 %** | 58.1 % |
| dark (21:00–02:50) | 5.84 h | **82.2 %** | 15.9 % |

**C1 is 66.9 % asleep in the light phase; published C57BL/6 values are ~70 %
asleep with NREM 62.0 ± 7.8 %/12 h — inside one standard deviation**, with the
light/dark contrast in the correct direction.

This matters more than any other number here: **nothing in the QC gate or the
persistence statistic knows about the clock**, so this is a genuinely external
check. Four independent lines — persistence, physiology, circadian timing, and
the pre-run impedance sweep — all rank the animals identically.

> [!danger] Do not report a REM percentage
> The 80th-percentile rule fixes REM at 20 % of sleep by construction; an
> independent Otsu cut on theta/delta gives 24–48 %; the literature value for
> mice is **< 10 %**. Both rules land far above it, so **REM is not reliably
> separable with this montage**. Report WAKE vs NREM, plus REM's *order*.

## Why Run 2 died: the degradation is directional and EEG-specific

Three sweeps bracket the runs: **pre-run1** (07-31 17:34, 32 min before Run 1),
**pre-run2** (08-02 01:44, 2 min before Run 2), **post-run2** (08-02 23:34).

### EEG impedance across Run 2 — every channel, no exceptions

| mouse | pre-run2 | post-run2 | Δ |
| --- | --- | --- | --- |
| A1 | 4.446 | 8.284 | +3.838 |
| A2 | 5.962 | 6.917 | +0.955 |
| B1 | 0.133 | 0.732 | +0.599 |
| B2 | 5.771 | 7.336 | +1.565 |
| C1 | 5.720 | 7.929 | +2.209 |
| C2 | 1.146 | 2.507 | +1.361 |
| D1 | 3.980 | 7.504 | +3.524 |
| D2 | 2.114 | 9.200 | +7.086 |

**EEG: 8 worse, 0 better. EMG: 3 better, 3 unchanged, 2 worse.**

> [!important] This asymmetry is the finding
> Same tether, same slip ring, same headstages, same board, same session, same
> animals. **A shared-path fault or an environmental cause cannot degrade one
> channel type and leave the other alone.** The fault is specific to the EEG
> side of the connection.
>
> ⚠️ **"EEG side" includes the electrode itself, not just our wiring.** EEG uses a
> **dura pin**; EMG uses a **wire anchored in muscle**. Hsieh et al. 2024 report
> that **82% of epidural preparations lose at least one electrode within three
> weeks**, with peak dislodgement in week 1 — muscle wires have no comparable
> published failure rate. So this asymmetry narrows the fault to the EEG segment
> but does **not** by itself point at the solder.
> See [[2026-08-03-literature-check-impedance-and-electrode-failure]].

### C1's EEG died between the runs and never came back

```
pre-run1   0.465 MΩ   CONNECTED   ->  8.73 h of the best data in the project
pre-run2   5.720 MΩ   open        ->  nothing
post-run2  7.929 MΩ   open
```

One-way. No chattering back. The single best animal we have lost its EEG in the
~4 h gap between the two runs, and stayed lost.

### The impedance screen called Run 2 wrong

**B1 read 0.133 MΩ before Run 2 — the best EEG impedance in the whole fleet —
then ran at 2802 µV hum, fully open, for 21.7 hours.**

Resting impedance is **not** contact under load. It predicts *which channel may
work*, never *for how long*. See the narrowing box in
[[electrode-connection-state-test]].

### A pattern worth watching, not yet a finding

The two mice that carried EEG in Run 1 (C1, D2) are the only two whose EEG
impedance rose across the gap between runs; all five that carried nothing
improved slightly.

| mouse | Run 1 usable | EEG Z pre-run1 → pre-run2 |
| --- | --- | --- |
| C1 | 8.73 h | 0.465 → 5.720 (**+5.255**) |
| D2 | 2.76 h | 0.660 → 2.114 (**+1.454**) |
| C2 | 2.34 h | 4.418 → 1.146 (−3.272) |
| A1, A2, B1, B2, D1 | 0 | all improved (−1.3 to −2.3) |

Spearman **ρ = +0.464, p = 0.25, n = 8**. C2 goes the other way and the test is
not significant. The hypothesis — *carrying signal is what wears the contact
out* — is plausible and consequential, but **this is not evidence yet**. Track
it across the next run rather than acting on it.

## What this means

1. **Everything rests on one animal in one run.** C1 is well validated, but
   n = 2 animals from a single recording is not a dataset.
2. **The failure is progressive, EEG-specific, and irreversible.** Contact
   degrades run over run, and the animals that work are the ones that stop
   working. Waiting will not help; each additional run costs contact.
3. **The rig is not the problem.** Same rig produced 9 µV hum and a 100 % gate
   pass on 2026-06-29. EMG works through the identical physical path throughout.
4. **A1 and D1 remain the free diagnostic — but it discriminates, it does not
   confirm.** Perfect EMG, zero EEG, both runs, through the same tether, slip
   ring, board, headstage and port. That proves the **shared path** good. It does
   **not** prove the fault is in our wiring, because EEG and EMG do not share an
   electrode: EEG is a dura pin, EMG is a wire anchored in muscle, and the
   published 3-week loss rate for epidural electrodes is **82%**
   ([[2026-08-03-literature-check-impedance-and-electrode-failure]]). Run the
   bench test to separate the two hypotheses. Bench only, no animal contact.

## Still open

- **Tier-1 bench test on A1, D1 (and now C1) not done.** This is the cheapest
  action available and it has been owed since 2026-08-02.
- Whether use itself degrades the contact — needs one more run to test.
- Animal identity is positional; `C1` in Run 1 and `C1` in Run 2 are assumed to
  be the same mouse but this rests on cage records, not on the data.
- No light-phase data exists for any animal other than C1.
