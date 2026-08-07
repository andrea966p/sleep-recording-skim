---
tags: [experiment, eeg, recording, data-quality, tether, slip-ring, retraction]
created: 2026-08-07
status: complete
---

# Overnight recording, 23.66 h: two animals work, and yesterday's harm conclusion was wrong

> [!abstract] TL;DR
> We recorded for **23.66 hours**, a full light and dark cycle, and analysed it with the
> criterion written down **before** the recording started.
>
> **Two animals now produce usable data instead of one.** B1 is at 99.6% with an unbroken
> 3.6 hour block. **D2, which had 0.0% usable EEG yesterday afternoon, is now at 87.9%.**
>
> That last number **overturns what I concluded yesterday evening.** The tether swap on D2
> looked like clear harm in a 40 sweep impedance block. The recording shows the opposite: the
> swap **fixed D2's EEG**. The impedance block had caught the channel in a single long open
> state that happened to span all 21 minutes of it.

Recording: `allego_1__uid0806-16-57-38`, **2026-08-06 16:57:38 to 2026-08-07 16:37**, 1 kHz,
all 256 primary channels, 89.3 GB, 8,517 epochs of 10 s.
Method and criterion: [[2026-08-06-recording-data-quality-preregistration]].
What it corrects: [[2026-08-05-tether-comparison]] §13. Day before: [[2026-08-06]].

## 1. Result

**Falsification check passed first**, as always: floor control channels **0.00% usable**, the
no-mouse A2 position **0.0% usable**. Threshold derived from **953,904 floor-control epochs**:
60 Hz amplitude below **415.0 µV**.

| animal | EEG usable | EMG usable | **both** | longest unbroken block |
| --- | --- | --- | --- | --- |
| **B1** | **100.0%** | **99.6%** | **99.6%** | **215.8 min = 3.6 h** |
| **D2** | **87.9%** | **98.6%** | **86.5%** | **87.3 min** |
| C1 | 0.0% | 37.8% | 0.0% | none |
| C2 | 0.1% | 15.2% | 0.0% | none |
| A1 | 0.0% | 7.6% | 0.0% | none |
| B2 | 0.0% | 0.0% | 0.0% | none |
| D1 | 0.0% | 0.0% | 0.0% | none |
| **A2, no mouse** | **0.0%** | **0.0%** | **0.0%** | none |

![[2026-08-07-figE-usable-timeline.png]]

**Figure E.** Every 10 second epoch across the whole recording, green where both channels are
usable. Grey band is lights off, 21:00 to 09:00. **B1 is very nearly solid for 23.66 hours.**
D2 is dense but broken up. The other six rows, including the position that contains no mouse,
are empty.

### Confirmed independently by spectral shape

Same channels judged by the second method, which does not use the hum threshold at all. Floor
control slope range across this recording: **[−1.29, −0.07]**.

| animal EEG | % epochs railed | post-filter rms | **spectral slope** | delta fraction | verdict |
| --- | --- | --- | --- | --- | --- |
| **D2** | **0.0%** | 82.7 µV | **−2.05** | **0.47** | **real EEG** |
| **B1** | **0.0%** | 52.4 µV | **−1.81** | **0.32** | **real EEG** |
| C2 | 0.0% | 317.9 | −0.47 | 0.19 | bare-wire-like |
| **A2, no mouse** | 0.7% | 185.7 | −0.38 | 0.16 | bare-wire-like, as it must be |
| A1 | 4.1% | — | — | — | railed, unrecoverable |
| B2 | 1.5% | — | — | — | railed |
| C1 | 6.0% | — | — | — | railed |
| D1 | 3.1% | — | — | — | railed |

**D2's slope of −2.05 is now the steepest on the rig**, steeper than B1's.

## 2. 🔴 Retraction: the arm C tether swap did not harm D2. It fixed it.

### What I concluded yesterday, and why

D2 was swapped onto the **long custom tether plugged straight into the headstage, slip ring
removed**. A 40 sweep impedance block immediately afterwards gave:

- D2 EMG **10/15 → 0/40** below 0.5 MOhm, p = 8.4e-08
- D2 EEG median **3.450 → 8.249** MOhm
- untouched controls unchanged, so drift excluded
- EMG **flat across the block, rho −0.00**, so anaesthesia recovery excluded

I reported that as harm, flagged it provisional when D2 recovered 40 minutes later, and said
the overnight recording would settle it.

### What the recording says

| D2 EEG `D/33` | afternoon recording, **before** swap | overnight recording, **after** swap |
| --- | --- | --- |
| usable fraction | **0.0%** | **87.9%** |
| median 60 Hz amplitude | 916.9 µV | **133.2 µV** |
| spectral slope | −0.38, inside the bare-wire range | **−2.05, far outside it** |
| epochs railed | 29.7% | **0.0%** |
| D2 EMG usable | 86.1% | **98.6%** |

![[2026-08-07-figD-D2-before-after.png]]

**Figure D.** D2's EEG power spectrum before the swap (red) and after (green), with B1 as a
working reference (blue) and the two unconnected controls (dashed grey). Before the swap D2 is a
**flat plateau at 10⁴**, indistinguishable in shape from a cable attached to nothing. After the
swap it **falls steeply and tracks B1**, and shows structure in the delta and theta range. This
is the same channel, the same animal, 24 hours apart.

> [!danger] The correction, stated plainly
> **The arm C swap improved D2's EEG from unusable to 87.9% usable.** My "harm" conclusion was
> wrong. It was based on a 40 sweep block spanning 21 minutes, and the channel was in one long
> open state for all of it.

### The methodological lesson, which is the valuable part

> [!important] Even a 40 sweep duty cycle can be unrepresentative
> We adopted duty cycles precisely because a single reading is a coin toss. This shows the fix
> was **necessary but not sufficient**. Contact states on this rig persist for **longer than a
> 21 minute block**, so a block can sample one state and report it with a p value of 8e-08.
>
> **Impedance blocks are a screening tool. Only a multi-hour recording is an outcome.** Duty
> cycle blocks should be reported with their **duration** stated prominently and should never
> be used alone to conclude that an intervention caused harm or benefit.

## 3. ⭐ This answers yesterday's main open question

Yesterday's confound: the one working animal, B1, had **both** 16 days of recovery before
tethering **and** a newly built soldered tether. Two variables, one animal, and no way to say
which mattered.

The disambiguation was pre-registered in [[2026-08-06-fleet-duty-cycle-census]] §5:

> If D2 jumps to near 100%, **tether construction alone is sufficient** and recovery time is not
> the driver. If D2 improves only partly, recovery time carries real weight.

**D2 was tethered on 30 July, 8 days after surgery**, well short of our 14 day protocol, and it
had 0.0% usable EEG. After receiving a new chain it is at **87.9%**.

> [!success] Long recovery is not required. The chain is sufficient.
> An animal tethered at **day 8** now produces usable EEG for most of a 24 hour recording. The
> improvement came from replacing the tether chain, not from waiting longer.
>
> This is good news operationally: it means the existing cohort is **recoverable without new
> surgery**, and that the fix is an engineering change we can apply to every animal.

⚠️ **What it does not say.** It does not mean recovery time is irrelevant to implant health, only
that it is not what is gating signal quality right now. And it is **n = 1 per condition**.

## 4. What changed in D2's chain, and what we still cannot separate

| | before | after |
| --- | --- | --- |
| tether | original, thin heat-shrink joints | **new, long, soldered under resin** |
| slip ring | **present** | **removed, tether goes straight to the headstage** |
| connector | seated since 30 July | **re-seated during the swap** |
| anaesthesia | none | **one isoflurane episode** |

Four things changed together. **"Does the new chain help" is answered: yes, decisively. "Is it
the slip ring" is not answered and cannot be, at any sample size, without another anaesthesia
episode per animal.** The vault predicted exactly this limitation before the experiment ran.

> [!note] Where this leaves the slip-ring question
> On 2026-08-05, arm B improved B1 dramatically **with** the slip ring still in place. Now arm C
> has improved D2 dramatically **without** it. **Both new chains worked.** What the two arms have
> in common is the **soldered, resin-encapsulated construction**, not the presence or absence of
> the slip ring. That points at joint construction as the active ingredient, though it remains
> circumstantial.

## 5. Limits

- **n = 1 animal per condition**, and each swap bundles four changes.
- The A2 position is a cable and is reported only as a control.
- **Only the positive input of each electrode pair is ever measured.**
- **No video**, so contact dropouts still cannot be related to behaviour.
- This document reports **data quality only**. No staging, no biology, no time in state.

> [!quote] Paper-ready
> Over a 23.66 h recording spanning a full light and dark cycle, two of eight implanted animals
> produced signal that differed from simultaneously acquired unconnected amplifier inputs, with
> usable fractions of 99.6% and 86.5% of 10 s epochs and longest uninterrupted intervals of 3.6 h
> and 1.5 h. In one animal, replacement of the tether chain raised the usable EEG fraction from
> 0.0% to 87.9% and reduced median 60 Hz amplitude from 916.9 to 133.2 microvolts, with spectral
> slope moving from −0.38, inside the unconnected distribution, to −2.05, outside it.

## 6. Next

1. **We now have two animals and a full light and dark cycle**, which for the first time since
   31 July makes a **circadian validation** possible: the proportion of sleep in the light phase
   should approach the literature value of roughly 70%. That is the natural next analysis and it
   is a genuine, threshold-independent check on the whole pipeline.
2. **Apply the new chain to more animals.** The result says this is an engineering fix, not a
   surgical one, so the existing cohort is recoverable.
3. **Export B1 and D2 to EDF+** for manual scoring.
4. C1's EMG remains ambiguous and needs video.
