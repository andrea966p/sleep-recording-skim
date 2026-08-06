---
tags: [status, eeg, impedance, recording, data-quality, report, professor]
created: 2026-08-06
status: complete
---

# Rig status, 6 August 2026: what the rig can do, what it is doing, and how we know

---

# PART 0 — The very short version

> [!quote] Paste ready. Nothing below is needed to understand this.
> **Where we are.** The rig can carry 8 mice and that part works. Only **1 of 8 animals produces
> usable EEG**. That animal is the one we let recover for **16 days** before tethering, instead of
> the 8 to 10 days the others got.
>
> **What changed today.** We discovered that one position on the rig held a **cut cable with no
> mouse on it**, and it passed our quality test 22% of the time. That gave us our first true
> negative control. We now judge every channel against **112 amplifier inputs that have no
> electrode attached**, recorded at the same instant in the same file.
>
> **Why that matters.** Two things we believed were unsafe. First, a single impedance reading
> means nothing: an empty cable can read better than a real mouse. Second, once you filter a
> recording, **a bare wire produces a convincing EEG trace**, about 69 microvolts of it. So neither
> a good impedance number nor a good looking trace is evidence.
>
> **What we use instead.** We repeat each measurement 20 to 40 times and report the **fraction
> connected**, and we judge cleaned recordings by the **shape of the frequency spectrum**, which
> filtering cannot fake. Real brain activity falls steeply with frequency; noise is flat.
>
> **Result.** One animal, B1, is at **99.7% usable** with zero artefact and a clearly biological
> spectrum. Seven animals are indistinguishable from an unconnected amplifier. Statistics are
> Fisher exact tests against the unconnected control. All four channels that pass are highly
> significant, the weakest at p = 0.00003. Every other channel is not significant.
>
> **How to read it.** The bottleneck is **electrical contact**, not surgery and not the recording
> system. The single most promising lead is the **recovery time before tethering**, and the next
> experiment separates that from the tether that animal also received.

---

# PART 1 — The full report

> [!abstract] TL;DR for the rest of this page
> §1 answers whether the rig can record 8 mice. §2 explains the method and why we changed it.
> §3 gives the results with figures. §4 is the statistics and how to interpret them. §5 is what
> is still open and what we do next.

Underlying documents: [[2026-08-06-fleet-duty-cycle-census]] ·
[[2026-08-06-recording-data-quality-preregistration]] · [[2026-08-06-unloaded-chain-interference]] ·
[[eeg-artefact-and-railing-rejection-policy]] · [[2026-08-05-tether-comparison]] ·
day log [[2026-08-06]]

## 1. Can the rig record 8 mice at once?

**Capacity: yes, and it is not the constraint.** Four ports, a splitter on each, two mice per
port, **256 amplifier channels**. All 256 were enumerated and returned data. That is the hard
ceiling of the XDAQ Core, which supports 8 headstages, so the rig sits exactly at its design
limit.

**Yield: no.** Only **1 animal of 8** produces usable EEG. The limiting factor is the electrical
contact between the implanted electrode and the amplifier.

## 2. Method, and why we changed it today

### 2.1 The problem with our old measure

We used to judge an electrode by a single impedance reading, calling anything below 2 megohm
"connected". Today we found out what that number is worth.

The **A2 position on the rig holds a cut cable with no mouse attached to it**, still wired through
its rotating connector, its amplifier board and the shared splitter. It was measured 20 times
alongside the animals. **It passed the 2 megohm test 22% of the time**, with a best reading of
0.248 megohm.

We then found a much larger version of the same control that was already in every recording we
have ever made. **Each mouse is connected to only 2 of its chip's 16 amplifier inputs.** The other
14 are real amplifiers with **no wire attached**, and they are recorded anyway. Across four ports
that is **112 channels of pure nothing**, measured simultaneously with the animals.

![[2026-08-06-figA-threshold.png]]

**Figure A.** Grey: 2,240 readings from amplifier inputs with no electrode. Blue: all animal
channels. Green: B1. **21.4% of the bare wires pass the old 2 megohm mark.** At 0.5 megohm only
3.1% do, while B1 still passes 47.5% of the time. This is why the pass mark moved.

> [!warning] The consequence, stated plainly
> **Any channel scoring between 15 and 35 percent under the old rule was statistically
> indistinguishable from a cable attached to nothing.** Several of our historical judgements sat
> in exactly that band.

### 2.2 We measure duty cycle, not a single reading

Electrical contact on this rig **switches on and off within minutes** with nothing being touched.
We established that on 4 August, watching one channel move from 6.236 to 0.052 to 8.649 megohm in
23 minutes.

So a single reading is close to a coin toss. We now fire the measurement **20 to 40 times in a row
and report the fraction that come back connected**. One sweep of all 256 channels takes 31.4
seconds and the process is automated, so a 20 sweep block costs 10 minutes unattended.

**The method validated itself today.** D2 measured 27.5% yesterday over 40 sweeps and 30% today
over 20, with a hardware change in between; its muscle channel 97.5% and 100%. **A duty cycle is a
stable, repeatable property of a channel.**

### 2.3 Judging the recording itself, and a trap we nearly fell into

Impedance says the wire is connected. It cannot say the signal on the wire is brain activity. So we
recorded 3.18 hours and judged the data directly, using a criterion **written down before the
recording started** so the thresholds could not be tuned to flatter the result.

The obvious approach is to apply the standard cleaning, a 60 hertz notch for mains interference and
a 0.5 to 30 hertz band pass, and look at the traces. **We tested that approach by running the 112
wire free channels through the identical cleaning.**

> [!danger] The result that changed how we judge everything
> **A channel with no wire attached comes out at a median of 69 microvolts of smooth, plausible,
> EEG looking signal.**
>
> Filtering manufactures a convincing trace out of nothing. **Looking at cleaned traces cannot tell
> you whether an electrode is connected.**

What filtering **cannot** fake is the **shape of the frequency spectrum**. Real neural activity puts
most of its power at low frequencies and falls away steeply, the so called one over f shape. Noise
is spread evenly and is flat. So we classify by spectral slope and by the share of power in the
0.5 to 4 hertz band, always against the unconnected controls in the same file.

## 3. Results

### 3.1 Every animal, by impedance

![[2026-08-06-figB-duty-cycle.png]]

**Figure B.** Duty cycle per animal at the corrected 0.5 megohm mark, red dashed line is the
wire free floor. **Only four bars clear it: B1 on both channels, A1's muscle channel, D2's muscle
channel.** Everything else is at or below the level of a cable attached to nothing.

### 3.2 Every animal, by the recording

3.18 hours, 10 second epochs. **The falsification check passed first: the control channels scored
0.00% usable and the no mouse position scored 0.0%.** Only then did we read the animals.

| animal | EEG usable | EMG usable | both | longest unbroken block |
| --- | --- | --- | --- | --- |
| **B1, the 16 day recovery mouse** | **99.8%** | **99.7%** | **99.7%** | **39.5 min** |
| D2 | 0.0% | 86.1% | 0.0% | none |
| C1 | 0.0% | 36.3% | 0.0% | none |
| A1 | 0.0% | 5.2% | 0.0% | none |
| B2, C2, D1 | 0.0% | 0.0% | 0.0% | none |
| A2, no mouse | 0.0% | 0.0% | 0.0% | none |

**Seven of seven implanted animals score 0.0% on EEG.** Sleep cannot be staged without EEG.

### 3.3 The same conclusion, reached a second way

![[2026-08-06-traces-filtered.png]]

**Figure C.** Twenty seconds per channel after cleaning, **every panel at an identical plus or
minus 400 microvolt scale**. That fixed shared scale is what makes the comparison honest: recording
software auto scales by default, which would zoom into each channel's noise until every panel looked
beautiful. B1 is smooth and rolling with visible slow waves. Everything else, including the no mouse
position and the bare wires, is dense high frequency hash.

![[2026-08-06-psd.png]]

**Figure D.** The same channels as power against frequency, both axes logarithmic. **B1, the thick
blue line, falls steeply from about 2 hertz across five orders of magnitude.** Every other line is a
flat plateau at a different height. **Height is loudness. Shape is biology.** Only B1 has the shape.

Numerically, the unconnected controls occupy a spectral slope range of **−1.10 to −0.04**. B1 sits
at **−2.15 with a delta fraction of 0.47**. B2, C2, D2 and the no mouse position are all inside the
control range.

### 3.4 The one animal that works, and the unresolved reason

The working animal was implanted on 21 July with the rest of the cohort, then **kept in its home
cage untethered until 6 August, 16 days after surgery**. The other seven were tethered on 30 July,
**8 to 10 days after surgery**. Our own protocol requires **at least 14 days**, so this is the first
animal in the project ever tethered in line with it, and it is the best animal we have ever had.

> [!danger] Two things changed at once, so neither can be claimed
> That animal also received a **newly built tether with soldered joints under resin**, instead of
> the thin heat shrink joints the others have. **Recovery time and tether construction changed
> together, in one animal.** We cannot yet say which one is responsible, and we should resist the
> temptation to announce that longer recovery fixes the problem.

## 4. Statistics, and how to interpret them

**Test used: Fisher exact test**, one sided, comparing the number of connected readings on an animal
channel against the number of connected readings from the unconnected control channels in the same
block. Fisher exact is the correct choice because these are small counts of successes and failures
in two groups, where the chi squared approximation is unreliable.

**Why the control is inside the same block.** Every threshold on this project used to be inherited
from an earlier session or from the literature. Deriving it instead from channels recorded **at the
same instant, on the same chips, in the same room** removes drift, room noise and session effects in
one step, and it makes the comparison self validating: if the control does not separate from the
animals, that is the result and no threshold will fix it.

| channel | connected | p against control |
| --- | --- | --- |
| B1 EEG | 6/20 | **3e-05** |
| B1 EMG | 13/20 | **1.8e-07** |
| A1 EMG | 14/20 | **2.9e-08** |
| D2 EMG | 14/20 | **2.9e-08** |
| all other channels | 0 to 2 of 20 | not significant |

**How to read a not significant result here.** It does **not** mean the electrode is broken. It
means the channel cannot be distinguished from an amplifier with no wire attached, on this
measurement, in this block. Given that we have measured a working electrode at 0.052 megohm on this
same rig, the most likely reading is that these electrodes are fine and the **contact** is not being
made.

**Known limits, stated deliberately.**
- **n = 1 animal** for the working case. This is a lead, not a fleet wide conclusion.
- **Impedance predicts class, not yield.** Today's pre registered predictions came out **6 hits, 1
  partial, 1 miss**, better than the 2 August run's 4 correct, 3 wrong, 1 void. The two failures
  point in opposite directions, so impedance is not biased optimistic or pessimistic. It is simply
  blind to what rides on a connected wire. **A1 is the demonstration**: impedance called its muscle
  channel one of the best on the rig, and in the recording 296 of its 331 microvolts are mains hum.
- **Only the positive input of each electrode pair can be measured.** The chip can test the other
  side but neither the manufacturer's software nor the open source alternative exposes the control.
  This is with the vendor.
- **No video.** All cameras were removed from the room on 4 August, so we cannot yet relate contact
  dropouts to what the animal is physically doing.

## 5. Still open, and what we do next

1. **Recovery time or tether construction?** The single most valuable question on the board. The
   next experiment separates them by giving a newly built tether to an animal tethered at day 8.
2. **A tether swap performed this evening produced an ambiguous result** and is written up as
   provisional. The animal appeared to worsen sharply, then fully recovered 40 minutes later, which
   is consistent with our known behaviour of contact states persisting for tens of minutes. An
   overnight recording, which cannot be fooled by which moment we sampled, will settle it.
3. **One muscle channel, C1, is genuinely ambiguous** and needs video to resolve.
4. **The interference question** raised previously, whether a dangling cable disturbs its
   neighbours, is half answered. Stripping the empty cable element by element showed **our tethers,
   slip rings and splitters are not leaking**; the spurious readings come from the amplifier's own
   behaviour on a floating input. The remaining half, whether the empty cable disturbs a working
   neighbour, is designed and not yet run.
5. **A hardware high pass filter at 1.10 hertz** is applied before the data is saved and cannot be
   undone. It attenuates the bottom of the delta band. It is identical on all ports and all our
   thresholds were derived from data carrying it, so our internal comparisons are unaffected, but it
   matters for comparison with published values.

> [!quote] Paper ready
> Electrode contact was quantified as a duty cycle, the proportion of repeated 1 kHz impedance
> sweeps below a threshold, rather than as a single measurement, because contact was found to
> alternate between connected and open states within minutes. Thresholds were derived from
> amplifier inputs with no electrode attached, acquired simultaneously in the same session, which
> passed a 2 MOhm criterion in 21.4% of readings and a 0.5 MOhm criterion in 3.1%. In recorded data,
> the same unconnected inputs yielded a median root mean square amplitude of 69 microvolts of
> spectrally flat signal after 60, 120 and 180 Hz notch and 0.5 to 30 Hz band pass filtering,
> demonstrating that filtered trace morphology alone is insufficient to establish electrode
> connection. Channels were therefore classified by spectral slope relative to the unconnected
> distribution. One of eight animals fell outside that distribution.
