---
tags: [experiment, eeg, impedance, tether, slip-ring, electrodes]
created: 2026-08-05
status: active
---

# Tether comparison, 2026-08-05: does construction or the slip ring change the duty cycle?

> [!abstract] TL;DR
> Yesterday proved the electrodes are good and the contact is **intermittent**, flipping
> between connected and open within minutes. Today tests whether the **tether** is what
> flips it. Two newly built tethers exist, both with soldered joints under resin: a short
> one that still runs through the slip ring, and a long one that plugs straight onto the
> adapter board and skips the slip ring entirely.
>
> The animal is **B1**, chosen because its electrode is proven good and its contact flips
> at roughly a 50/50 rate, which is the easiest rate at which to see a change. **D2** stays
> plugged in and untouched the whole session as a control that costs nothing.
>
> The measurement is **not** "what does the impedance read". At a 50% flip rate a single
> reading is a coin toss. The measurement is **duty cycle**: out of 20 sweeps in a block,
> how many were connected.

Plan of record: `~/.claude/plans/peaceful-greeting-flute.md`.
Prior session: [[2026-08-04-movement-dependent-contact]] · register: [[impedance-sweep-register]]

## 1. Why this test, in one paragraph

On 2026-08-04 B1's EEG read **6.236 → 0.052 → 8.649 → 0.177 MΩ in 23 minutes**. The
0.052 MΩ value is inside the published 10 to 50 kΩ band and is the best number ever
recorded on this rig, so the electrode and the implant are good. Boards, pads, solder
and the static slip ring passed the DMM test fleet wide, and port, splitter and XDAQ
were exonerated when B1 worked in both port B and port D. What is left between a good
electrode and a good amplifier is the **tether and the slip ring**, and both have now
been rebuilt.

## 2. Design

Three arms, one animal, same day, fixed order.

| arm | B1's tether | slip ring | isolates |
| --- | --- | --- | --- |
| **A** | original, thin heatshrink joints | yes | **baseline** |
| **B** | new short, soldered + resin | yes | **joint construction** |
| **C** | new long custom, direct to adapter board | **no** | **the slip ring** |

Both new tethers are built the same way, soldered and resined. That is what makes
**C against B a clean single variable test of the slip ring**, and it is the reason the
long tether runs last rather than first.

> [!warning] C against A is not a single variable comparison
> It changes construction **and** removes the slip ring at the same time. It may not be
> used on its own to assign a cause. Only C against B can do that.

### Optional arm A2

Return to the original tether for a final 10 sweeps. Tests whether **unplugging and
replugging the headcap connector** is itself what moves the numbers, rather than the
tether. Run it if the arms disagree.

## 3. Animals, and why these ones

### B1, the test animal

| reason | evidence |
| --- | --- |
| electrode **proven good**, so a bad block means contact, not a dead electrode | 0.052 MΩ @ 179.7°, 16:47 on 2026-08-04 |
| **maximum documented volatility**, headroom in both directions | 166× across 23 min |
| baseline duty cycle near **50%**, the easiest rate to move | 2 of 4 readings connected |
| **port already discharged** as a confound | works alone in port B and alone in port D |
| single animal, no splitter baselines already exist | sweeps 4, 5, 6 of the 08-04 session |

### D2, the free concurrent control

A sweep reads **every connected port at once**, so leaving D2 in port D on its original
tether yields a control sample for every single sweep at zero extra effort.

- D2 churns during the session ⇒ the change is environmental or time of day, **not** the tether.
- D2 stays solid ⇒ the measurement is clean and B1's changes are real.

D2 earns this because it was connected on **both** channels in **every** sweep yesterday:
0.352/0.233 · 0.459/0.270 · 0.400/0.088.

> [!important] Do not touch D2. Do not swap its tether. That is the entire point of it.

### D1, the backup

If B1's baseline comes out **0/20 or 20/20** it is at floor or ceiling and no change can
be measured on it. Switch to D1, whose EMG flipped 41× yesterday (8.203 MΩ → 0.688 MΩ in
nine minutes). D1 is also in port D, so moving it into the test role costs the D2 control
or moves it to port A.

### Rejected

**A1 EMG, C1 EMG, C2 EMG** were connected in all four historical sweeps. They sit at the
**ceiling** and cannot demonstrate an improvement. **A2 and B2** have no single animal
baseline.

## 4. Configuration

- **No splitters.** One headstage per port ⇒ each animal lands on `/1` (EEG) and `/2` (EMG)
  of its port, **not** `/33` and `/34`. 32 channels per port. See [[CANONICAL-allego-channel-selection]].
- B1 → **port B**. D2 → **port D**, untouched.
- Four sites read every sweep: `B/1`, `B/2`, `D/1`, `D/2`.

## 5. Protocol per arm

1. Swap B1's tether at the headcap connector. Awake, **no anaesthesia**.
2. **Wait 5 minutes untouched.** Do not sweep during settling.
3. Fire **20 sweeps at roughly 60 s cadence**, about 20 minutes. Export every one.
4. Touch nothing during the block: not the animal, the cage, the tether or the rack.
5. Record arm start and end clock time.

About 2 hours including swaps.

> [!danger] Arm C only: the long tether does not rotate
> The cable **will twist** as the animal turns and will eventually bind. Watch it. If it
> binds, stop the block, note how many sweeps completed and where, untwist, restart the
> block. Do not sweep through a mechanically loaded tether.
>
> This configuration is a **bench diagnostic only**. It must never be proposed for an
> overnight run.

## 6. Files

```
~/Downloads/impedance measurments/2026-08-05/
├── armA-original/
├── armB-short-soldered/
└── armC-long-direct-noslipring/
```

Folders already created. Let Allego name files however it likes during a block; do not
fight the GUI mid session. **Batch rename from mtime at the end of the same day**, while
the mtimes are still true, into:

```
imp_2026-08-05_HHMM_B1-portB-D2-portD-32ch_arm<A|B|C>-NNN.csv
```

Same day matters, because [[impedance-sweep-register]] records that mtime stops being a
safe identity as soon as files are copied, synced or restored. `pipeline/stage2_split.py`
already globs recursively, so the subfolders need no code change.

## 7. Metrics, fixed before any data exists

Per arm, per channel (`B/1`, `B/2`, `D/1`, `D/2`):

| metric | definition |
| --- | --- |
| **duty cycle** | fraction of the 20 sweeps with \|Z\| < 2 MΩ. **Primary outcome.** |
| good fraction | fraction with \|Z\| < 0.5 MΩ |
| median \|Z\| | plus min and max across the block |
| **flip count** | transitions between connected and open across consecutive sweeps. Separates "steadily bad" from "rapidly flipping", which duty cycle alone cannot |
| phase | fraction near 180° (connected) against 30 to 55° (open signature) |

Comparison: **Fisher exact** on connected counts, arm against arm, per channel, with
confidence intervals.

## 8. Pre-registered predictions

Written **before** arm A. Yesterday's movement hypothesis was damaged partly because its
prediction was written after its first supporting sweep.

| if the fault is | then |
| --- | --- |
| **tether joints** | B ≫ A, and C ≈ B |
| **the slip ring** | C ≫ B, and B ≈ A |
| **both** | A < B < C, monotone |
| **neither** — headcap or implant interface | all three ≈ 50%, D2 solid throughout |
| **measurement or room** | D2 churns too, and no arm comparison means anything |

> [!important] Row four is a likely outcome and is not a failure
> If all three arms sit near 50%, the tether and the slip ring are both cleared **by
> measurement instead of by assumption**, and the search moves to the headcap connector
> and the electrode to skull interface. That is a real result and it should be written up
> as one.

## 9. Honest limits, stated before the data

- **20 sweeps per arm detects a large effect only.** 10/20 against 18/20 gives p ≈ 0.008,
  so 50% → 90% is detectable. 10/20 against 16/20 gives p ≈ 0.10, so **50% → 80% would not
  reach significance**. This is the accepted price of manual sweeping. An arm landing in
  that middle band should be **extended**, not argued about.
- **n = 1 animal.** A result here is a lead, not a fleet wide conclusion. D1 is the replicate.
- **Only the positive input of each pair is measured**, as always. `Zcheck pol sel` is
  unreachable in both Radiens and the Open Ephys plugin.
- **No movement covariate.** Cameras are removed, so this session says nothing about the
  movement hypothesis and must not try to.
- **Arms are not counterbalanced.** Monotone drift across the session would masquerade as
  an arm effect. D2 is the guard against exactly that, and is the second reason it stays
  plugged in.

## 10. Results

*To be filled after the session.*

| arm | window | sweeps | `B/1` duty | `B/2` duty | `D/1` duty | `D/2` duty |
| --- | --- | --- | --- | --- | --- | --- |
| A original |  |  |  |  |  |  |
| B short soldered |  |  |  |  |  |  |
| C long direct |  |  |  |  |  |  |

## 11. Verdict

*To be filled after the session.*

> [!quote] Paper-ready
> *To be written after the result, not before.*
