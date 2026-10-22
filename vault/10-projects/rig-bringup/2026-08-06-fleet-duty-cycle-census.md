---
type: experiment
area: rig-bringup
status: done
tags: [experiment, eeg, impedance, duty-cycle, fleet, tether, recovery-time]
created: 2026-08-06
---

# Fleet duty cycle census, 2026-08-06: what all 8 mice actually do, and the mouse that works

> [!abstract] TL;DR
> We measured every animal on the rig 20 times in a row and counted how often each channel
> was electrically connected. The rig can physically carry 8 mice, that part is fine and
> proven. What it cannot do is keep them connected: on average only **1.8 of 8 animals**
> had both EEG and EMG at the same moment.
>
> One animal broke the pattern completely. A mouse implanted on 21 July that stayed in its
> home cage untethered until today was connected on **40 of 40 channel-sweeps with zero
> flips**. It is the only stable EEG in the fleet. It differs from the others in two ways at
> once, so we cannot yet say which one did it.

Prior session: [[2026-08-05-tether-comparison]] · root cause: [[2026-08-04-movement-dependent-contact]]
Register: [[impedance-sweep-register]] · files: `~/Downloads/impedance measurments/2026-08-06/01-fleet-census-20sweeps/`

## 1. Configuration

All 8 animals reconnected as before the tether experiment. Four ports, C3442 splitter on
each, **64 amp channels per port, 256 total**. Mouse 1 of a port sits on `/1` (EEG) and
`/2` (EMG), mouse 2 on `/33` and `/34`. See [[CANONICAL-allego-channel-selection]].

`remap.py` was re-run first, as required after any port change, and confirmed
`ntv 0-63 → A`, `64-127 → B`, `128-191 → C`, `192-255 → D`.

**A 256 channel sweep takes 31.4 s.** Sweeps were fired back to back, so the block is
20 sweeps in 9 min 54 s, 11:30:56 to 11:40:50 KST. Nothing was touched during it.

## 2. Result

Duty cycle = fraction of the 20 sweeps with |Z| < 2 MΩ. Flips = transitions between
connected and open across consecutive sweeps.

| animal | EEG duty | EMG duty | **both** | flips EEG / EMG | EEG median | EEG max |
| --- | --- | --- | --- | --- | --- | --- |
| **B1, new mouse** | **20/20 = 100%** | **20/20 = 100%** | **20/20 = 100%** | **0 / 0** | **0.813** | **1.531** |
| A1 | 4/20 = 20% | 19/20 = 95% | 4/20 = 20% | 4 / 2 | 4.311 | 7.760 |
| **A2 = NO MOUSE, control** | 5/20 = 25% | 4/20 = 20% | 1/20 = 5% | 7 / 5 | 4.526 | 8.278 |
| B2 | 3/20 = 15% | 3/20 = 15% | 1/20 = 5% | 4 / 5 | 4.287 | 8.192 |
| C1 | 6/20 = 30% | 4/20 = 20% | 1/20 = 5% | 9 / 6 | 3.627 | 8.582 |
| C2 | 7/20 = 35% | 8/20 = 40% | 3/20 = 15% | 6 / 12 | 2.888 | 6.639 |
| D1 | 7/20 = 35% | 3/20 = 15% | **0/20 = 0%** | 10 / 2 | 4.392 | 6.515 |
| D2 | 6/20 = 30% | 20/20 = 100% | 6/20 = 30% | 10 / 0 | 3.658 | 9.218 |

```
B1 new  EEG  CCCCCCCCCCCCCCCCCCCC   0 flips
B1 new  EMG  CCCCCCCCCCCCCCCCCCCC   0 flips
D2      EMG  CCCCCCCCCCCCCCCCCCCC   0 flips
A1      EMG  CCCCCCCCCCCCoCCCCCCC   2 flips
D2      EEG  ooCoooCoooCCooCoCooo  10 flips
D1      EEG  oCCCooCooCoCooooooCo  10 flips
```

> [!danger] ⭐⭐⭐ The A2 slot held NO MOUSE, and that changes how this whole table reads
> The A2 position is a **cut tether attached to nothing**, still wired through its slip ring,
> headstage and the shared splitter into port A. It is therefore an **unwired negative
> control**, the first one this project has ever had, and it was measured 20 times alongside
> the animals.
>
> It should have read open every sweep. It did not:
>
> ```
> A/33   min 0.248 MOhm @ 1.3 deg    5/20 below 2 MOhm
> A/34   min 0.654 MOhm @ 3.5 deg    4/20 below 2 MOhm
> ```
>
> **9 of 40 channel-sweeps = 22% of an empty tether reads "connected" at the 2 MOhm
> criterion.** Every duty cycle in the 15 to 35 percent band is therefore statistically
> indistinguishable from nothing being attached at all. See §3.

## 2b. Everything re-scored against the no-mouse control

Fisher exact, each channel's 20 sweeps against the control's 40 channel-sweeps, one-sided.

| animal | at 2 MOhm (control 9/40 = 22%) | | at **0.5 MOhm** (control **1/40 = 2.5%**) | |
| --- | --- | --- | --- | --- |
| | EEG | EMG | EEG | EMG |
| A1 | 20% n.s. | 95% **5.3e-08** | 5% n.s. | 70% **2.9e-08** |
| **B1 new** | 100% **2.4e-09** | 100% **2.4e-09** | 30% **0.0042** | 65% **1.8e-07** |
| B2 | 15% n.s. | 15% n.s. | 0% n.s. | 0% n.s. |
| C1 | 30% n.s. | 20% n.s. | 0% n.s. | 0% n.s. |
| C2 | 35% n.s. | 40% n.s. | 5% n.s. | 10% n.s. |
| D1 | 35% n.s. | 15% n.s. | 5% n.s. | 0% n.s. |
| D2 | 30% n.s. | 100% **2.4e-09** | 5% n.s. | 70% **2.9e-08** |

### Figures

![[2026-08-06-figA-threshold.png]]

**Figure A.** Grey is 2,240 readings from amplifier inputs with **no electrode attached**; blue is
all animal channels; green is B1. **21.4% of the bare wires pass the old 2 MOhm mark**, against
3.1% at 0.5 MOhm, while B1 still passes 47.5% of the time. This single picture is the entire
argument for moving the pass mark.

![[2026-08-06-figB-duty-cycle.png]]

**Figure B.** Duty cycle per animal at 0.5 MOhm, red dashed line is the wire-free floor. Only four
bars clear it: **B1 on both channels, A1's EMG, D2's EMG**. Note that the **A2 bar, which is a cable
with no mouse on it, is the same height as several animals' EEG bars.**

> [!important] Only four channels in the entire fleet beat an empty tether
> **A1 EMG, B1-new EEG, B1-new EMG, D2 EMG.** That is 4 of 14 measured channels, in 7 animals.
> Everything else — including all of B2, all of C1, all of D1, both C2 channels, A1's EEG and
> D2's EEG — cannot be distinguished from a cable attached to nothing.

> [!success] The fix: move the criterion to |Z| < 0.5 MOhm
> At 2 MOhm the control false-positive rate is **22%**. At 0.5 MOhm it is **2.5%**, one
> reading in forty, while genuinely connected channels still score 30 to 70 percent. The
> 0.5 MOhm line separates real contact from pickup; the 2 MOhm line does not.
>
> Two consequences, both free:
> - **Adopt 0.5 MOhm as the connected criterion** for all future duty cycles. Re-score prior
>   blocks with it before quoting them.
> - **Leave the A2 slot exactly as it is.** A sweep reads every port at once, so this control
>   costs nothing and belongs in every future block.

> [!note] What this does to the 2026-08-05 tether result
> It does **not** overturn it. Arm B's B1 was 20/20 at 2 MOhm against a 22% control, which is
> still overwhelming. What it does damage is the **arm A "45% baseline"** — a substantial
> share of those 9 connected sweeps may have been threshold false positives, which means the
> true A-to-B effect is **larger**, not smaller. The arms were run before the control existed,
> so this is a reinterpretation, not a retraction.

> [!quote] Paper-ready
> Across 20 consecutive impedance sweeps of 8 chronically implanted mice, a mean of 1.80 of
> 8 animals had both EEG and EMG channels below 2 MOhm simultaneously. A disconnected tether
> measured concurrently through the same slip ring, headstage and splitter fell below the
> same 2 MOhm criterion in 9 of 40 channel-sweeps, so the criterion was tightened to
> 0.5 MOhm, at which the unwired control fell below threshold in 1 of 40 channel-sweeps.
> By that criterion 4 of 14 implanted channels differed significantly from the unwired
> control.

## 3. Can the rig record 8 mice simultaneously?

**Capacity: yes, and it is not the constraint.** Four ports, splitters, 256 channels
enumerated cleanly and every one returned an impedance. This is the hard XDAQ Core
ceiling of 8 headstages and the rig sits exactly on it.

**Yield: no, and worse than the raw table suggests.** Against the unwired control, only
**four channels in seven animals** are genuinely connected, and only **one animal, the new
mouse, has a working EEG and EMG pair**. Counting animals that beat the control on both
channels, the rig is currently recording **1 of 8**.

The limit is electrical contact, exactly as established on 2026-08-04, and nothing in the
census contradicts that.

## 4. The three findings

### 4.1 The new mouse is categorically different, not marginally better

Implanted 21 July with the rest of the cohort, then kept in its home cage **untethered
until today**, and connected this morning to the **19.5 cm short soldered and resined
tether** from yesterday's arm B.

40 of 40 channel-sweeps connected. **Zero flips on either channel.** Worst EEG reading of
the whole block 1.531 MOhm.

Compare yesterday's arm B on the original B1: 20/20, 0 flips, median 0.903, max 1.341.
**The two blocks are nearly the same numbers.** Two different animals, same tether, same
signature.

### 4.2 Duty cycle reproduces across days

D2 was measured on 2026-08-05 as a control and again today, 24 hours apart, through a
port change and the addition of splitters:

| channel | 2026-08-05, 40 sweeps | 2026-08-06, 20 sweeps |
| --- | --- | --- |
| `D/1` D2 EEG | 11/40 = **27.5%** | 6/20 = **30%** |
| `D/2` D2 EMG | 39/40 = **97.5%** | 20/20 = **100%** |

> [!success] This is a method validation, and it matters more than it looks
> Duty cycle is a **stable per-channel property**, not a random walk. A single impedance
> reading is a coin toss, but 20 of them measure something real and repeatable. Every
> comparison in [[2026-08-05-tether-comparison]] rests on this and it now has direct
> evidence.

### 4.3 A2 is not an animal at all, it is the control

The A2 position holds a **cut tether attached to nothing**, still connected through its slip
ring, headstage and the port A splitter. There is no mouse. Its "duty cycle" of 25% and 20%
is the **false-positive rate of the 2 MOhm criterion**, and it is the single most useful
number produced today. See the callout in §2 and the re-scored table in §2b.

⚠️ **The splitter is still loaded.** Removing the animal did **not** unload the port A
splitter, because the A2 headstage remains plugged into it. So the improvement in A1's EMG
cannot be attributed to a lighter splitter load, and in any case the splitter was ruled out
on 2026-08-04.

## 5. ⚠️ The confound in the new mouse, stated plainly

The new mouse differs from the other seven in **two ways at the same time**:

| variable | new mouse | the other seven |
| --- | --- | --- |
| days from surgery to first tethering | **16 d** (21 Jul → 6 Aug) | **8-10 d** (21-23 Jul → 30 Jul) |
| tether | **19.5 cm short, soldered + resin** | original, thin heatshrink joints |

Our own SOP requires **≥14 d** post-op before tethering. **The new mouse is the first
animal in this project ever tethered SOP-compliant.** The other seven were all commissioning
animals tethered 4 to 6 days early.

**n = 1, two variables. Neither explanation can be claimed yet.**

> [!important] The planned D2 swap now disambiguates this for free
> D2 is a **day-8-tethered** animal with a solid 27.5-30% EEG baseline measured twice.
> - D2's EEG goes to near 100% on a new soldered tether ⇒ **construction is sufficient**,
>   recovery time is not the driver.
> - D2 improves only partly ⇒ **recovery time carries real weight**, and the fix for the
>   next batch is the ≥14 d SOP that already exists on paper and has never been followed.
>
> Unchanged: the long tether changes construction **and** removes the slip ring together,
> so it still cannot say "it is the slip ring". `D/2` at 100% is the **harm detector** — if
> it falls after the swap, the swap did damage.

## 6. Limits

- **One block, one time of day.** 10 minutes of a single morning.
- **No movement covariate.** Cameras are still out of the room.
- **Only the positive input of each bipolar pair is measured**, as always.
- The 08-05 D2 baseline was taken **without splitters**, today's **with** them. The splitter
  was ruled out as a cause of contact loss on 2026-08-04, so this is noted rather than
  treated as a confound.
- Duty cycle is an impedance measure. It predicts **class, not yield** — Run 2 showed
  4 hit / 3 miss / 1 void against pre-registration. It is not a promise of scoreable sleep.
