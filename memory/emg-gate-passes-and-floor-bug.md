---
name: emg-gate-passes-and-floor-bug
description: "2026-08-21: the EMG gate finally PASSES on 4 positions of the 39.7 h run, and the pooled-floor bug in criteria.py was why it looked blocked"
metadata:
  type: project
---

**2026-08-21, scoring `allego_1__uid0819-17-25-20` (39.674 h, 8 positions).**

## 🔴🔴 THE POOLED FLOOR IN `criteria.floor_stats()` IS A BUG, NOT A SETTING
It pools all 112 wire-free inputs across all 8 chips. **The project's OWN definition, in the same
file, says "through the same chip".** On this run chip B1's floor is slope p1 **-2.079** / 1237 µV RMS
while the other seven are -0.68..-1.35 / 3451-4063 µV. Pooling gives **-1.633** = harsher than 7
chips' own floors, more lenient than the 8th.
**Effect: A1 reads 41.5% usable pooled vs 99.9% per-chip; longest block 9.3 min vs 457.5 min.
UNDER THE POOLED FLOOR EVERY POSITION FAILS THE 15-MIN GATE. Under per-chip, five pass.**
⚠️ **`floor_stats()` STILL POOLS — not yet fixed.** ⚠️ **The 2026-08-11 "EMG gate failed by every
experimental animal" used the pooled floor ⇒ THAT CONCLUSION MAY ITSELF BE AN ARTEFACT. Re-run before
citing it.** See [[analysis-stack-audit-2026-08-11]].

## ✅ THE EMG GATE PASSES — THE KAPPA IS UNBLOCKED
r (EMG amplitude vs EEG delta, 1-min bins), bar -0.30: **C1 -0.755, A1 -0.580, A2 -0.524, D2 -0.488**
(C2 -0.389 but see below). Previous best on an experimental animal was -0.174; the only passer ever
was a control at -0.734. **C1 beats that control and is not a control.**
🔑 **Result is FLOOR-INDEPENDENT**: with NO usability restriction at all, A1 -0.580, A2 -0.525,
C1 -0.733, D2 -0.485. So it is not an artefact of my floor fix.
🔑 **Shared-path check — SIGN MATTERS**: r(rms_eeg, rms_emg) **NEGATIVE = physiological** (NREM raises
EEG amplitude while muscle tone falls); **POSITIVE = shared artefact.** A1 -0.673, A2 -0.525,
C1 -0.388, D2 -0.323 physiological; **C2 +0.812 ⇒ SHARED PATH, its gate result is NOT trustworthy.**
🔑 **Nocturnal check (no threshold)**: EMG dark/light — A2 6.4x, A1 4.4x, D2 4.1x (10-19 µV light,
68-78 µV dark, matching the old 48 h control's 31/73). **C1 INVERTED 0.78x**; C2 34x at 672 µV = not muscle.

## VERDICT (RIG POSITIONS, no animal identity)
**FULL PASS = A1, A2, D2.** ⚠️ **C1**: best EEG + strongest r but INVERTED circadian EMG — unresolved.
⚠️ **C2**: gate passes, physiology says no. **B2 = EEG only** (92.4%, 261 min block; EMG open 427 µV).
**D1 = FAIL and DEGRADED MID-RUN** (hours 0-8 29-82%, then 0-28%). **B1 = DEAD** (0.0%, railed 54%,
LOUDER than its own chip floor).
⭐ **A1 held ONE UNBROKEN 7.6 h usable block and was 100% in all 39 hourly bins — longest ever here.**
🛑 **STILL NOT A SLEEP RESULT.** No hypnogram, no % asleep. Rung 4 stays PROVISIONAL until the kappa.

🔑 EEG judged by SLOPE, EMG by HUM+amplitude — `criteria.usable()` REFUSES slope on EMG (broadband).
⚠️ `qc/emg_state_dependence.py` Test 2 (burstiness) crashes on a numpy/scipy ABI mismatch in
`/opt/neurosurveillance/venv`; Test 2 is diagnostic-only so the gate is unaffected. Its printed line
about "A1, which has no ground at all" is STALE TEXT about a DIFFERENT cohort.

Artefacts + scripts: `eeg-emg-analysis/qc/score_2026-08-21/`. Report:
vault `05-experiments/completed/2026-08-21-39h-run-score.md`.
Related: [[animal-card-verdict-ladder]] · [[recording-2026-08-18-eight-new-mice]]


## How far back the floor bug reaches (MEASURED 2026-08-21, not assumed)
**All four substantive recordings have DIVERGING chips**, and in every one the pooled value is
**too harsh for exactly 7 of 8 chips, too lenient for exactly 1**:
`08-08 16.39h` pooled -1.328, chips -1.540..-0.800 (lenient chip = D1) ·
`08-09 48h control` -1.352, -1.666..-0.840 (D1) ·
`08-18 1h screen` -1.510, -1.942..-0.407 (B1) ·
`08-19 39.7h` -1.633, -2.079..-0.676 (B1).
🔑 **DIRECTION RULE: where pooled was harsher, a FAIL is suspect but a PASS is CONSERVATIVE and
SURVIVES.** ⇒ **the A2 48 h control's 47.09/48.19 h stands** (its chip -0.976 vs pooled -1.352);
only that one too-lenient chip per run has suspect passes.

## ⭐⭐ THE CONTROL THAT MATTERS: re-ran the 08-08 EMG gate per-chip
**It moves exactly ONE animal: B2 -0.156 → -0.366 (crosses the bar).** A2 control -0.734→-0.713,
C2 -0.174→-0.180, D1 +0.023→+0.028, D2 +0.010→-0.135 (still fails).
⇒ **The floor fix does NOT manufacture passes. The four passes on the 39.7 h run are a REAL change
in the data.** ⚠️ Corrects the 08-11 audit: **"no experimental animal passes" is FALSE (B2 does)**,
but 3 of 4 still fail so the wider claim stands.


## 🔴 FALSIFICATION ROUND 2026-08-21 — C1 AND C2 ARE WITHDRAWN, n=3 NOT 4
🔴🔴 **THE DELTA *RATIO* CARRIES EMG-BAND POWER IN ITS DENOMINATOR** ⇒ muscle/movement bleed into the
EEG channel drives r negative **in a dead animal**. Recomputed vs **ABSOLUTE delta power (µV²)**:
**A1 -0.580→-0.705, A2 -0.525→-0.686, D2 -0.485→-0.661 ALL STRENGTHEN** (opposite of the artefact's
prediction) but **C1 COLLAPSES -0.733→-0.009** and **C2 REVERSES -0.689→+0.595**.
⛔ **C1 AND C2 WITHDRAWN. SURVIVORS = A1, A2, D2 ONLY.** ⚠️ **C1 had the BEST number on the rig and
was the artefact; its inverted circadian EMG had already flagged it.**
🔑 **ALWAYS TEST STATE-DEPENDENCE ON ABSOLUTE DELTA POWER, NOT THE RATIO.**
✅ **Per-chip criterion applied to the 112 wire-free inputs: 0/112 pass the 15-min gate** ⇒ it is NOT
measuring chip self-similarity. 🔴 **BUT the fixed `r <= -0.30` BAR IS CROSSABLE BY INTERFERENCE —
16/112 wire-free channels reach it. REPLACE IT WITH A PER-CHIP NULL** (each EMG vs its own chip's 14
wire-free channels): A1 z-2.96, A2 -2.12, D2 -1.68 below their null; B1/B2/D1 INSIDE theirs (a real
negative control, agrees with the hardware verdicts).
⚠️ **Per-chip floor = 14 samples not 112 ⇒ trades bias for variance; NO bootstrap CI computed yet.**
⭐ **LESSON: the animal with the best number was the wrong one. Both withdrawn animals had ALREADY
been contradicted by a simple independent check. A strong number that disagrees with basic
physiology is a WARNING, not a puzzle.**
