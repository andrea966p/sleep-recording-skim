---
type: experiment
area: hlb-sod1
status: done
created: 2026-10-22
summary: "W-SL batch, 83 min screen on the new 8-core tether (2026-09-09) and the first 5.5 h of the 09-10 ZT0 baseline: best screen the rig had produced; A1 = ground-screw contact fault, port C EMGs broken"
recordings: [allego_1__uid0909-21-17-52, allego_0__uid0910-09-00-00]
cohort: W-SL
tags: [experiment, eeg, emg, w-sl, screen, tether]
---

# W-SL: the 83 min screen on the 8-core tether, and the first hours of the 09-10 baseline

> [!info] Promoted 2026-10-22 from the Claude memory note of 2026-09-09/10
> No journal exists for 2026-09-09 or 2026-09-10; these numbers were recorded only in Claude's memory, written from ad
> hoc screen scripts against `core/criteria.py` (not committed). The batch's sleep analysis is
> [[2026-09-18-W-SL-light-phase-sleep]] and its verdict cards (2026-09-26) supersede the per-position calls below where
> they differ. The 09-10 baseline is judged in [[2026-09-30-scoreable-mice-on-the-24h-windows]].

> [!abstract] TL;DR
> **Question.** Does the new batch on the thicker 8-core tether connect before its ZT0 baseline?
> **Answer.** Best screen this rig had produced: 7 of 8 chips grounded (floors 3441-4658 µV), 7 of 8 EEG channels
> 96.6-100 % usable, each beating its own chip's floor lf/hf p99 in 96-100 % of epochs. A1's chip read ungrounded;
> C1's EMG was a broken conductor. The tether is confounded with a fresh connector re-mate, and the file is 83 min of
> dark phase only.

## Setup
- Screen: `allego_1__uid0909-21-17-52`, Wed 2026-09-09 21:17:52 → 22:40:54 KST, 1.383 h, 498 QC epochs (10 s), fs 1000,
  64 sites per port. Rung 0 INTACT, remainder 0/0.
- New batch of 8 mice (W-SL), new thicker tether built from 8-core wire. IDs were not yet in a manifest at the time.
- Baseline: `allego_0__uid0910-09-00-00`, started 09:00:00 KST (ZT0) by a cron one-shot; numbers below at 5.5 h, all
  light phase.

## Result: the screen

| pos | floor µV | EEG usable / longest | EMG |
|---|---|---|---|
| A1 | 69, ungrounded | UNJUDGEABLE | real, cv 42 % |
| A2 | 3733 | 99.6 % / 77.7 min | real, 49 % of epochs > 150 µV |
| B1 | 4352 | 99.6 % / 41.5 min | real, strict rung 2 94.6 % |
| B2 | 4170 | 96.6 % / 29.0 min | real, strict 78.5 % |
| C1 | 3738 | 100.0 % / 83.0 min | dead, fixed 693 µV |
| C2 | 4658 | 98.4 % / 35.3 min | real, 66 % of epochs > 150 µV |
| D1 | 4379 | 97.8 % / 20.5 min | real, strict 79.1 % |
| D2 | 3441 | 99.8 % / 75.2 min | real, strict 90.6 % |

- **C1 EMG is a broken conductor:** locked at 693 µV, cv 4.6 %, max/min 1.25, hum ÷ own floor 0.245 (partially
  conducting). Its EEG is the best channel in the file. Same EMG-only tether break C1 showed on 2026-08-26
  ([[2026-08-27-B1-swap-baseline-20h-run]]).
- Cross-checks: flicker cv 4.7-17.6 %, max/min 1.4-2.4 everywhere (no bending or torsion signature); |r| EEG vs EMG
  0.015-0.181 (no shared path); railing 0.0 % except C2 EMG 0.4 %; EEG rms 58-105 µV; flat per-10-min time course.
- `RMS_HI_UV = 150` alarm: A2 (49 %) and C2 (66 %) of epochs sat above 150 µV, so their strict rung-2 numbers (51 %,
  34 %) were an amplitude-gate artefact. **Retracted the next day as a tether property** (see below).

## Result: correction of 2026-09-10, A1 is a ground-electrode fault
- Claude had first advised a connector re-mate for A1. **Andrea corrected it: every connector is mated correctly; the
  fault is surgical**, poor contact between pin and dura after implantation.
- The data say which electrode: what failed on A1 is the chip's 14 **wire-free** inputs (56 µV against 2897-4951 µV on
  the other seven). No electrode is attached to those, so the level is set by the ground / reference return: the
  **cerebellum ground screw's contact**, not the EEG electrode.
- A1's EEG, judged against the seven other chips' floors on 5.5 h of the baseline: lf/hf 26.53 (working range
  19.9-26.6), slope −1.78 (working −1.70 to −1.80), rms 84 µV, beats those floors' lf/hf p99 in 99.9 % of epochs.
  Its floor is flat over 5.5 h (56 → 53 µV): a stable missing connection, not a decay.
- Open at the time: A1's EEG is probably scoreable but the code says UNJUDGEABLE, because rung 2 needs a valid control
  on its own chip. A rescue against a floor pooled from the other seven chips would need a decision and its own label.

## Result: the 09-10 baseline at 5.5 h
- 7 of 8 EEG at 99.3-100 %, longest blocks 107-330 min (A2 and D2 unbroken for the whole file so far).
- Five pass strict rung 2: B1 97.9 % (89.8 min block), D2 96.8 %, B2 95.1 %, D1 93.5 %, A2 89.1 %.
- In the light phase EMG rms is 27-51 µV and the 150 µV gate clips nothing: the screen's over-150 epochs were wake in
  the dark phase, not the 8-core wire.
- **C2's EMG broke overnight** (worked 22:40, dead at 09:00): locked at 1157-1412 µV, hum ÷ own floor 0.261, 2.6 %
  railing. C1 EMG has the identical signature. Both slots of port C, EMG only, both EEGs good. A shared C-branch fault
  is a hypothesis, not a finding: a swap test is owed before naming a cause.

## What it means / what it does not mean
- 83 min, entirely dark phase, one file: a 1 h snapshot overstates a 24 h run ([[2026-08-25-S-SD-24h-ZT0-run]]).
- The 8-core tether is confounded with a fresh re-mate: the 2026-09-01 bench re-seat also fixed all eight grounds with
  the old tether ([[2026-09-02-S-SD-recovery-sleep]]). Credit for the wire needs the floors to hold after days of wear.
- Later: by 09-17 grounding had got worse (5 of 8 chips grounded) and only B2 / HLBWSL24 pairs across the batch's two
  timepoints ([[2026-09-18-W-SL-light-phase-sleep]]).

## Unlogged files noticed at the time
- `allego_0__uid0904-08-55-25`, 30.0 h, 09-04 08:55 → 09-05 14:55, 57.9 GB, 32 sites per port (4 positions), and
  `allego_0__uid0829-08-34-39` (59.2 h, "not ours"): see [[CANONICAL-recording-naming-and-inventory]].
