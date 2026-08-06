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

| arm | window | sweeps | `B/1` B1 EEG | `B/2` B1 EMG | `D/1` D2 EEG | `D/2` D2 EMG |
| --- | --- | --- | --- | --- | --- | --- |
| **A** original | 16:36:59-16:55:59 | 20/20 | 9/20 = **45%** | 4/20 = **20%** | 8/20 = 40% | 20/20 = 100% |
| **B** short soldered | 17:46:17-18:05:17 | 20/20 | **20/20 = 100%** | **15/20 = 75%** | 3/20 = 15% | 19/20 = 95% |
| **C** long direct | | | | | | |

Fisher exact, arm B against arm A: `B/1` **p = 0.0001**, `B/2` **p = 0.0006**.
Controls: `D/1` p = 0.078 (went **down**), `D/2` not significant.

```
B1 EEG state, arm A:  CoooooooCCCCCoCCCooo     5 flips, median 2.913, max 9.089
B1 EEG state, arm B:  CCCCCCCCCCCCCCCCCCCC     0 flips, median 0.903, max 1.341
```

> [!success] The whole distribution moved, not just the threshold crossings
> B1's EEG never went open once in arm B, and its **worst** reading of 20 sweeps was
> 1.341 MΩ against a worst of 9.089 in arm A. Zero flips. The channel stopped behaving
> like an intermittent contact.

> [!success] The controls exclude a session-wide improvement
> Neither D2 channel improved. `D/1` went **down**, 40% → 15%. A drift in the room, the rig
> or the measurement would have lifted both animals together; they moved in opposite
> directions, so the change is specific to B1.

### ⚠️ Limitations of the A→B comparison, which cannot be removed

> [!danger] A against B confounds three things at once
> The swap required **isoflurane, handling, and re-plugging the headcap connector**. Arm A
> had **no** preceding anaesthesia. So four explanations fit the result equally well:
> 1. the soldered tether is genuinely better
> 2. **re-seating the connector** fixed a bad contact, which any swap would have done
> 3. the animal was **recovering from isoflurane** for part or all of arm B
> 4. some combination
>
> **Arm A2, the handling control, was ruled out on welfare grounds** — every tether change
> costs an isoflurane episode and the animal cannot absorb another. This is a legitimate
> constraint, not an oversight, and the limitation stands in the record instead.

> [!note] Partial evidence against the anaesthesia explanation
> Arm B drifts upward across the block: `B/1` first-10 median 0.741 → last-10 median 0.994,
> rho **+0.51** against sweep number; `B/2` rho +0.22. Consistent with recovery from
> isoflurane, since sweep 1 was only ~4 minutes after the swap.
>
> **But `B/1` stayed 10/10 connected in both halves.** If anaesthesia were doing the work,
> flips should have returned by the end of the block. They did not. Anaesthesia looks like a
> partial contributor to the magnitude, not the explanation for the effect.

> [!important] ⭐ Why arm C is still a valid test despite all of the above
> **Arm C also requires isoflurane, handling and a re-plug, so B and C carry the same
> exposure and it cancels.** B against C was always the designed single-variable test:
> both tethers are soldered and resined, and the only difference is the slip ring.
>
> Two protocol requirements follow:
> - **Start arm C's first sweep ~4 minutes after the swap**, matching arm B, so both arms
>   sit at the same point in post-anaesthesia recovery.
> - **Run 40 sweeps**, not 20. No extra anaesthesia, and it provides a well-recovered late
>   window to compare against arm B's late window.

> [!tip] The free substitute for arm A2
> Re-run a block **hours later with the tether untouched**. No handling, no isoflurane, no
> cost to the animal. If B1 still reads near 100%, anaesthesia is excluded and the tether
> result stands alone. If it has collapsed back toward 45%, the improvement was temporary,
> which would matter more.

## 11. 🔴 B1 died under isoflurane, and what that costs this experiment

B1 was lost on induction for the arm C tether swap, evening of 2026-08-05. Colony is now
**n = 7**: A1, A2, B2, C1, C2, D1, D2.

**Arms A and B are complete and stand.** 40 sweeps, both blocks clean, and they remain the
strongest result of the project.

**What is permanently lost:** arm C against arm B in the same animal. That was the only
comparison that isolated the **slip ring**, because it held tether construction constant.
No remaining animal has a soldered-tether block, and giving one would cost an isoflurane
episode per animal.

### Arm C, revised for 2026-08-06: D2

| channel | baseline, arms A + B pooled, original tether |
| --- | --- |
| `D/1` EEG | **11/40 = 27.5%** — headroom; 60% would reach p = 0.0032 at n = 40 |
| `D/2` EMG | **39/40 = 97.5%** — at the ceiling, so it serves as a **harm detector** |

D2 is the only remaining animal with a genuine duty-cycle baseline, and the comparison is
still **within-animal**. Every other candidate has isolated single sweeps only, which are
worthless as a baseline at a ~50% flip rate.

Protocol: D2 → long tether, **stay on port D**; **D1 onto port B as a free concurrent
control** (rig-end connection needs no anaesthesia); first sweep **~4 min after the swap**
to match arm B; **40 sweeps**; re-run `remap.py` first.

> [!danger] The claim has to change with the design
> D2's baseline is the **original heatshrink tether with the slip ring**. The long custom
> tether changes **construction and the slip ring together**. Tomorrow therefore tests
> **"does the new chain help"**, not **"is it the slip ring"**. The second claim is no
> longer available at any sample size without another anaesthesia per animal.

> [!warning] Welfare, before the next induction
> An animal was lost on induction. Vaporiser setting, flow and warming should be checked
> before D2 goes under, since D2 is the healthiest animal remaining and the one with the
> 0.017 MΩ channel.

## 12. Verdict

**Interim, arms A and B only.** Replacing a thin-heatshrink tether with a soldered and
resined one, on B1, took its EEG duty cycle from **45% to 100%** and its EMG from **20% to
75%**, with the worst reading of 20 sweeps falling from 9.089 MΩ to 1.341 MΩ and flips from
5 to 0. Concurrent controls in a second animal did **not** improve, ruling out session-wide
drift.

**The effect is real and large. Its cause is not yet isolated**, because the swap bundled
tether construction, connector re-seating and an isoflurane episode, and the handling
control was ruled out on welfare grounds.

> [!quote] Paper-ready
> Electrode contact was quantified as a duty cycle, the proportion of repeated 1 kHz
> impedance sweeps below 2 MΩ, rather than as a single measurement, because the contact
> was found to alternate between connected and open states within minutes. In one animal,
> replacing a heat-shrink-jointed tether with a soldered and resin-encapsulated one raised
> the EEG duty cycle from 9 of 20 sweeps to 20 of 20 (p = 0.0001, Fisher exact) while a
> concurrently measured control animal showed no improvement. Because the exchange also
> involved re-seating the headstage connector under anaesthesia, the improvement cannot be
> attributed to tether construction alone.

---

# 13. Arm C finally ran, on D2, 2026-08-06 — and it went the wrong way

**Configuration:** D2 moved to the **long custom tether, plugged directly into the headstage,
slip ring removed entirely**. D2 stayed on port D, mouse-2 position, so `D/33` = EEG and
`D/34` = EMG. Splitters in, 256 channels. `remap.py` re-run and confirmed before scoring.

**Blocks, all 2026-08-06, scored at |Z| < 0.5 MOhm against the wire-free floor channels
recomputed inside each block.**

| block | clock | D2 EEG `D/33` | D2 EMG `D/34` |
| --- | --- | --- | --- |
| morning census | 11:30-11:41, 20 sweeps | 1/20 = 5.0%, median 3.658 | 14/20 = **70.0%**, median 0.373 |
| **pre-swap baseline** | 15:57-16:04, 15 sweeps | 0/15 = 0.0%, median 3.450 | 10/15 = **66.7%**, median 0.437 |
| **arm C, long, no slip ring** | 16:27-16:47, 40 sweeps | 0/41 = 0.0%, median **8.235** | **0/41 = 0.0%**, median **1.820** |

**Harm test on the EMG:** 10/15 against 0/41 below 0.5 MOhm, **p = 8.4e-08**. At the looser
2 MOhm line, 15/15 against 25/41, **p = 0.0025**. D2's EEG median roughly doubled, 3.450 to
8.235.

> [!danger] The harm detector fired, and that is why it was in the design
> D2 was chosen precisely because its EMG was a **working channel that could show damage**.
> It did. A channel that was connected in two out of three sweeps is now connected in none.

### Both alternative explanations are excluded

**Session-wide drift is excluded.** B1 on port B was untouched throughout and did not move:
33.3% before, 34.1% during. The no-mouse A2 cable did not move either, 0.0% to 4.9%.

**Anaesthesia recovery is excluded.** In arm B the improvement **drifted upward across the
block** as the animal woke, rho +0.51 against sweep number. Here D2's EMG is **completely flat
across all 40 sweeps, rho −0.00, p = 0.99**, first-half median 1.743 against last-half 1.899,
and its EEG gets slightly **worse** across the block, rho +0.38, p = 0.014. There is no
recovery curve. This is a stable new state.

### ⭐ What it does to the slip-ring hypothesis

| arm | tether | slip ring | animal | outcome |
| --- | --- | --- | --- | --- |
| **B** | short, soldered + resin | **yes** | B1 | 45% → **100%** |
| **C** | long, soldered + resin | **no** | D2 | 67% → **0%** |

Both tethers are soldered and resined, so construction is approximately held constant and the
slip ring is the main difference. **The direction is the opposite of "the slip ring is the
problem."** If anything the slip ring is doing something useful, most plausibly providing
mechanical decoupling.

> [!warning] This is a lead, not a conclusion
> **Different animals and different tether lengths.** The clean within-animal version of this
> comparison died with B1 on 5 August and cannot be recovered without an anaesthesia episode
> per animal. Do not state it more strongly than "arm C went the wrong way, and the slip-ring
> hypothesis now has evidence against it."

### 🔧 The mechanism to check first, and it is free

§5 of this page predicted exactly this failure mode: **the long tether cannot rotate, so it
twists as the animal turns and eventually binds.** A tether under tension pulling on the
headcap is a highly plausible cause of a sudden, stable, non-recovering degradation on both
channels at once.

**Action: inspect the tether for twist, tension or binding. If found, untwist and re-run 20
sweeps.** If D2's EMG returns, the correct conclusion is "the long tether binds", not "the new
chain is bad", and that is a very different engineering problem.

🛑 **Do not revert D2 under anaesthesia on the same day.** The data is recorded and the
decision keeps.
