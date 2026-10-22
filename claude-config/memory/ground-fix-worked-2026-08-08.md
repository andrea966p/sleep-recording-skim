---
name: ground-fix-worked-2026-08-08
description: Ground re-pin on 2026-08-08 restored EEG on 6 of 7 ECG-cohort mice; A1 left un-grounded as control stayed flat; impedance duty cycle no longer screens
metadata: 
  node_type: memory
  type: project
  originSessionId: ad1ca725-35bc-44d8-b02a-ed707ae385f9
  modified: 2026-08-08T07:21:21.600Z
---

**2026-08-08: the cerebellum ground re-pin WORKED, and it was controlled.** Six of the seven ECG-cohort mice were re-pinned (brown wire to the headstage GND pad). **A1 could not be re-pinned because of a wiring problem on that animal, so A1 is now a NO-GROUND control that shares the surgery batch and the tether with the six that were fixed.** A2 = the old B1 mouse on the short soldered tether = positive control.

⭐⭐⭐ **120 s live look: nine of 21 new-mouse channels went to a spectral slope steeper than -0.9, when the night before NOT ONE was steeper than -0.35.** D/33 -0.32 → **-1.79**, B/1 -0.30 → **-1.35**, D/1 -0.24 → -1.27, C/33 -0.20 → -1.05, D/2 -0.06 → -1.39, D/34 +0.09 → -1.66, B/35 -0.10 → -1.45. **The only three channels that did not move are A/1, A/2, A/3 — the un-grounded animal.**

⭐⭐ **A 30-sweep impedance block, PRE-REGISTERED before it ran, confirmed both predictions.** Impedance got **much worse on the six repaired mice** (B/33 96.7% → 0.0%, B/35 100% → 0.0%, D/34 83.3% → 0.0%, C/1 96.7% → 6.7%) and **barely moved on A1** (A/2 90.0% → 90.0%, A/3 100%/0 flips → 100%/0 flips). Block `~/Downloads/impedance measurments/2026-08-08/01-post-ground-fix-30sweeps/`, floor 2.6%.

🔑 **A LOW, STABLE, ZERO-FLIP IMPEDANCE CAN MEAN THE ANIMAL HAS NO GROUND** — the test current returns through the paired electrode, a real stable tissue path. **Zero flips is the tell: real failures on this rig are intermittent.**

⚠️⭐⭐ **NOW THAT THE GROUND WORKS, THE SWEEP NO LONGER SCREENS.** B2 read 0.0% duty on all three sites in the same hour its ECG site had slope -1.45; D/34 read 0.0% with slope -1.66; A1, definitely floating, read 83-100%. **Screen on the stream, not on the sweep.**

🔴 **NO ECG CHANNEL PASSES THE HEARTBEAT TEST YET.** All CV 0.35-0.58, needs <0.1 at 600-750 bpm. Some ECG sites gained a real spectral tilt but a tilt is not a QRS. Re-run on a quiet stretch of the night file before concluding anything about the ECG.

## ⭐⭐ 22:00 INTERIM, 5.5 h in (light phase only)

⭐⭐⭐ **FOUR RE-PINNED MICE PRODUCE REAL EEG; UNTIL YESTERDAY IT WAS ZERO.** usable-by-slope: **B2 57.5%, C2 71.6%, D1 70.3%, D2 63.7%**, median slopes -1.52 to -1.63, **lf/hf 20.9-29.3** (on 08-07 A/33 was the ONLY channel of 256 above 4.79). Control A2 87.8%, -1.66, 21.14. ✅ **A1 (no ground) 0.0% on ALL THREE**, slopes -0.14/+0.01/+0.04. 🔴 **B1 11.2% and C1 0.0% still fail** — ordinary intermittent contact, unrelated to ground.

🔴🔴 **THE HUM CRITERION IS DEAD ON THIS COHORT: A1, definitely floating, scores 100.0/74.6/100.0% "usable" by it.** No ground ⇒ mains is common mode ⇒ a bipolar pair rejects it ⇒ floating channel is QUIET (A1 median 60 Hz 44-78 µV vs unwired floor median **3962 µV**). ⛔ **BOTH `usable_fraction_vs_floor*.py` SCRIPTS ARE DELETED (2026-08-11)** — use `core/criteria.py` via `cards/ladder.py`, `CohortSpec(roles=("eeg","emg","ecg"))` (floor `/4`-`/16`,`/36`-`/48`), SLOPE criterion. 🔴 **The slope band's stated justification — "filtering cannot manufacture slope" — IS FALSE**; a guard now enforces raw input. See [[analysis-stack-audit-2026-08-11]]. ⚠️ **Hum-criterion and slope-criterion fractions are NOT comparable** — never table them with B1's 99.6% from 08-06/07.

**Predictions: 1 ✅ (A2 87.8%), 2 ❌ FAILED, 3 ✅ EXACT, 4 ❌ FAILED, 5 ✅.**
- 🔴 **P2 failed:** four mice cleared 57% usable but **longest unbroken block is 13 min**, not the 1 h predicted. I also named **B1** as a top candidate and it came 7th of 8; B2 and C2 worked and I did not name them. ⚠️ Part of the fragmentation is the criterion, not the rig — **waking EEG is genuinely flatter, so a per-epoch slope test breaks blocks for BIOLOGICAL reasons.** 🛑 **Do NOT loosen the threshold** (circular tuning, banned in `20-areas/sleep-scoring/blind-scoring-and-kappa.md`).
- 🔴 **P4 failed: STILL NO HEARTBEAT**, even on the quietest railing-free 5 min window of a night. Best ever = D1 `D/3` **CV 0.22** (was 0.31-0.58) but **bar is 0.10**. **The ECG does not work and the ground fix did not fix it.** ⛔ Script deleted 2026-08-11 with the ECG retirement.
- ✅ **P5, with a number: Spearman impedance duty vs usable fraction = -0.126 (p 0.56) over 24 ch, +0.000 over the 7 EEG ch excluding A1.** **B2 read 0.0% duty and gives 57.5% usable; A1 read 83-100% and gives nothing.** ⇒ **SCREEN ON THE STREAM, NOT THE SWEEP.**

**Overnight recording `allego_0__uid0808-16-17-36`, started 16:17:36 KST, ~4.1 GB/h, in `~/radix/data/`. andrea stops it herself on 2026-08-09.** Five predictions pre-registered in `10-projects/rig-bringup/2026-08-08-ground-fix-post-repin-night.md`, including the deliberately falsifiable one that **A1 scores 0.0% usable**.

⚠️ **A1 is n=1 and is NOT a randomised control** — it is the animal whose wiring would not cooperate. Strong evidence, not proof. Its EEG also drifted (96.7%/1 flip → 83.3%/8 flips) on a night nothing was done to it.

Supersedes the diagnosis in [[ecg-cohort-ground-miswired]]; the cohort itself is [[ecg-cohort-2026-08-07]]. Register updated: [[eeg-rig-current-state]].

## 2026-08-09: night ended, new ZT0 run started

✅ **`allego_0__uid0808-16-17-36` stopped at 16.39 h, 61.8 GB, INTACT** (data and timestamp both 59,003,520 samples, zero remainder). Covers a full dark phase. 🔴 **ONLY THE FIRST 5.5 h ARE SCORED — the dark phase is unscored and is the real outcome.**

**15-sweep block 08:42-08:50** → `~/Downloads/impedance measurments/2026-08-09/01-post-night-15sweeps/`, floor 2.3%. ⭐⭐ **A1's floating signature reproduced for the THIRD consecutive day** (86.7/80.0/**100.0% with 0 flips on ECG**; 08-07 was 96.7/90.0/100.0, 08-08 was 83.3/90.0/100.0). 🔴⭐⭐ **THIRD demonstration the sweep does not predict the recording: B2 and C2 read 0.0% on ALL SIX sites that morning after producing 57.5% and 71.6% usable EEG overnight; A1 read 86-100% and produced nothing.**

⭐ **New recording `allego_0__uid0809-09-00-00` started 09:00:00.07 KST = ZT0 (lights on).** Starting at ZT0 gives a clean complete light-then-dark cycle; the previous run started 16:17 mid-light-phase. **Prefer a ZT0 start for every long run.** 680 GB free, ~3.9 GB/h.

⭐ **New helper `eeg-emg-analysis/qc/start_recording_at.py HH:MM:SS`** — waits for the wall clock, applies the `set_recording_config()` workaround, streams on 20 s early, fires at the target instant, then **verifies by watching the destination directory grow** (never trust `get_status().recording.path`, it reports the client's cwd).

## EMG and ECG, examined properly 2026-08-08 night

🔴 **EMG validated on the CONTROL ONLY.** Real test = state dependence (tone falls when asleep): correlation of 1-min EMG amplitude vs EEG delta over usable minutes. **A2 r = −0.651 (n=261) STATE-DEPENDENT**; B1 −0.175, B2 −0.163 weak; C2 −0.024, D1 −0.123, **D2 +0.053 nothing**. ⚠️ **The slope criterion is a CATEGORY ERROR for EMG** — EMG is broadband 30-300 Hz, so a real EMG is legitimately flat. ❌ Burstiness FAILED as a discriminator (control 0.09 LOW, floating A1 0.54 HIGH). ❌ 30-300 Hz vs floor is another "quiet = pass" trap (all channels 0.12-0.80× floor).

🔴 **ECG DEAD ON 7 OF 7, now with a proper negative control.** Detector-free tests (envelope autocorrelation + 3-harmonic comb) run on **20 unwired floor inputs**: floor reaches **autocorr z 13.08 and comb score 1046.76**. No mouse channel beats it. ⚠️ **I WITHDREW my own earlier "CARDIAC" verdicts** — they were boundary artefacts (every "600.0 bpm" was the search-window edge) plus scores a bare wire also achieves. D2's `D/35` is the only curiosity (3-harmonic comb at 669 bpm) but comb 228.8 << floor max 1047 and its autocorr z 3.97 is below the floor MEDIAN. **Not a heartbeat.** ⛔ Both scripts deleted 2026-08-11: ECG is retired as a negative result, and keeping a detector for an absent signal invites someone to run it and find noise.


## From the memory index, trimmed there 2026-10-06 (kept here verbatim)

- ✅⭐⭐⭐ **[THE GROUND RE-PIN WORKED — 2026-08-08](ground-fix-worked-2026-08-08.md).** HUM CRITERION IS DEAD, use SLOPE. Slope is a CATEGORY ERROR for EMG.
