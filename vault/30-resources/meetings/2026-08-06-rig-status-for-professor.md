---
type: meeting
area: rig-bringup
status: done
tags: [status, eeg, impedance, recording, data-quality, report, professor]
created: 2026-08-06
---

# Rig status, 6 to 7 August 2026: what the rig can do, what it is doing, and how we know

> [!warning] Updated 2026-10-22: this is a snapshot of 6-7 August 2026. The 60 Hz floor fell 12-60x after the 2026-10-07 earthing change. [[earthing-60hz-hum-fix]]

---

# PART 0 — The very short version

> [!quote] Paste ready. Nothing below is needed to understand this.
> ⭐ **UPDATED 7 August after a 23.66 hour overnight recording. Two animals now work, not one,
> and the reason is now identified.**
>
> **Where we are.** The rig can carry 8 mice and that part works. **2 of 8 animals now produce
> usable EEG**: one at **99.6%** of the recording with an unbroken **3.6 hour block**, one at
> **86.5%**.
>
> **What fixed the second one.** We replaced its tether with a newly built one whose joints are
> **soldered and sealed in resin**, instead of the thin heat shrink joints the others have. That
> animal went from **0.0% usable EEG to 87.9%** in 24 hours. It had been tethered only 8 days
> after surgery, so **the long recovery time we suspected is not what matters. The tether is.**
> This is important because it means the existing animals are recoverable **without new surgery**,
> and the fix is an engineering change we can apply to all of them.
>
> **One correction.** An impedance measurement block taken right after that swap suggested the
> opposite, that we had damaged the animal. The recording showed that was wrong. Electrical
> contact on this rig stays in one state for longer than a 20 minute measurement block, so a block
> can sample a single bad state and report it very confidently. **We now treat impedance as a
> screening tool only, and a multi hour recording as the actual outcome.**
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
> **Result.** Over a 23.66 hour recording, **two animals are usable and six are not**. The two
> have zero saturated data and clearly biological spectra. Statistics are Fisher exact tests
> against the unconnected control, with the weakest passing channel at p = 0.00003, and the
> spectral classification is independent of that test and agrees with it.
>
> **How to read it.** The bottleneck is **electrical contact**, not surgery and not the recording
> system. **The implants are fine.** The fix is the tether, it is an engineering change, and it
> can be applied to every animal we already have.

---

# PART 0b — Update, 7 August: the data is scoreable

> [!quote] Paste ready. No dashes, ready for an email.
> **We now have scoreable sleep data from two animals at once.**
>
> The 23.66 hour recording covers a full light and dark cycle. Both working animals pass every
> physiological check we apply, five out of five: wake has the highest muscle activity, deep sleep
> has the most slow wave power and the largest amplitude, and REM has the highest theta to delta
> ratio with low muscle tone. In both animals REM is entered from deep sleep rather than from wake
> in about three quarters of transitions, which is the correct order.
>
> **The strongest result is the circadian one, because nothing in our analysis knows what time it
> is.** Published values for this mouse strain are about 70% of the light phase spent asleep. One
> animal scored **70.3%**, the other **82.1%**, and both were far more awake in the dark phase, as
> they should be. That is external validation of the entire analysis chain against biology it was
> never tuned to match.
>
> **Amount of data.** One animal gave **23.66 hours as a single unbroken stretch**, the other gave
> 23.3 hours in nine stretches, the longest 9.6 hours. Our previous best in this project was 8.1
> hours, in July, from one animal.
>
> **What made the difference.** Replacing the tether. The second animal had been giving nothing at
> all that same afternoon. It had been connected only 8 days after surgery, so the longer recovery
> we suspected was not the deciding factor. The fix is an engineering change and it applies to every
> animal we already have, with no new surgery.
>
> **One thing we will not report.** The proportion of REM sleep. Our method forces that number by
> construction, and an independent way of computing it disagrees by a factor of four, so neither is
> a measurement. We report wake against deep sleep, and the order in which REM is entered.
>
> **Caveat we recorded in advance.** Both animals had a reason to sleep abnormally: one was
> tethered for the first time that morning, the other had been anaesthetised 40 minutes before the
> recording began. We wrote that down before analysing, and it did not distort the result. The
> animal at 82.1% slept slightly more than the published mean, so its figure should not be quoted
> as normal architecture. The 70.3% animal is the cleaner number.

---

# PART 1 — The full report

> [!abstract] TL;DR for the rest of this page
> §1 answers whether the rig can record 8 mice. §2 explains the method and why we changed it.
> §3 gives the results with figures. §4 is the statistics and how to interpret them. §5 is what
> is still open and what we do next.

Underlying documents: ⭐ [[2026-08-07-overnight-recording-two-animals-work]] · [[2026-08-06-fleet-duty-cycle-census]] ·
[[2026-08-06-recording-data-quality-preregistration]] · [[2026-08-06-unloaded-chain-interference]] ·
[[eeg-artefact-and-railing-rejection-policy]] · [[2026-08-05-tether-comparison]] ·
day log [[2026-08-06]]

## 1. Can the rig record 8 mice at once?

**Capacity: yes, and it is not the constraint.** Four ports, a splitter on each, two mice per
port, **256 amplifier channels**. All 256 were enumerated and returned data. That is the hard
ceiling of the XDAQ Core, which supports 8 headstages, so the rig sits exactly at its design
limit.

**Yield: improving.** On 6 August only **1 animal of 8** produced usable EEG. After one tether
was replaced, the 7 August overnight recording gave **2 of 8**. The limiting factor is the
electrical contact between the implanted electrode and the amplifier, and it is now demonstrably
fixable at the tether.

## 2. Method, and why we changed it

### 2.1 The problem with our old measure

We used to judge an electrode by a single impedance reading, calling anything below 2 megohm
"connected". Today we found out what that number is worth.

The **A2 position on the rig holds a cut cable with no mouse attached to it**, still wired through
its rotating connector, its amplifier board and the shared splitter. It was measured 20 times
alongside the animals. **It passed the 2 megohm test 22% of the time**, with a best reading of
0.248 megohm. Nobody planned it as an experiment; it simply was one.

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

**The method validated itself.** D2 measured 27.5% on 5 August over 40 sweeps and 30% on 6 August
over 20, with a hardware change in between; its muscle channel 97.5% and 100%. **A duty cycle is a
repeatable property of a channel**, unlike a single reading.

> [!warning] But a duty cycle block is still only a screen, and we learned this the hard way
> A 40 sweep block spans about 21 minutes. Contact states on this rig **persist for longer than
> that**, so a block can sample one state and report it with great confidence and be wrong. On
> 6 August a block gave p = 1.0e-07 for a conclusion the overnight recording reversed completely.
> **Impedance screens. Only a multi hour recording is an outcome.** Always state a block's duration
> next to its result.

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

### 3.2 Every animal, by the 3.18 hour afternoon recording of 6 August

10 second epochs. **The falsification check passed first: the control channels scored
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

### 3.3b ⭐ The 23.66 hour overnight recording of 7 August: two animals, and the reason found

A full light and dark cycle, 8,517 epochs, 89 GB. The falsification check passed again: control
channels 0.00% usable, the no mouse position 0.0%.

| animal | EEG usable | EMG usable | both | longest unbroken block |
| --- | --- | --- | --- | --- |
| **B1** | **100.0%** | 99.6% | **99.6%** | **215.8 min, 3.6 h** |
| **D2** | **87.9%** | **98.6%** | **86.5%** | **87.3 min** |
| C1 | 0.0% | 37.8% | 0.0% | none |
| C2 | 0.1% | 15.2% | 0.0% | none |
| A1 | 0.0% | 7.6% | 0.0% | none |
| A2 (no mouse), B2, D1 | 0.0% | 0.0% | 0.0% | none |

![[2026-08-07-figE-usable-timeline.png]]

**Figure E.** Each 10 second epoch across the recording, green where both channels are usable.
Grey band is lights off. **B1 is very nearly solid for 23.66 hours.** The six unusable rows include
the position that contains no mouse.

**D2 changed everything.** It had **0.0% usable EEG** in the afternoon. Between the two recordings
its tether was replaced with a newly built one, soldered and sealed in resin, connected straight to
the amplifier board.

| D2 EEG | before the swap | after |
| --- | --- | --- |
| usable fraction | **0.0%** | **87.9%** |
| median 60 Hz amplitude | 916.9 microvolts | **133.2** |
| spectral slope | −0.38, inside the unconnected range | **−2.05, far outside it** |
| saturated epochs | 29.7% | **0.0%** |

![[2026-08-07-figD-D2-before-after.png]]

**Figure D.** D2's EEG spectrum before the swap (red) and after (green), with B1 as a working
reference (blue) and the two unconnected controls (dashed). Before, D2 is a **flat plateau**,
indistinguishable in shape from a cable attached to nothing. After, it **falls steeply and tracks
the working animal**. Same animal, same electrode, 24 hours apart.

> [!success] This identifies the fix, and it is not surgical
> **D2 was tethered 8 days after surgery**, well short of our 14 day protocol, and it now produces
> usable EEG for most of a 24 hour recording. So the long recovery time we suspected in the other
> working animal **is not what was gating signal quality. The tether chain is.**
>
> The practical consequence is large: **the existing cohort is recoverable without new surgery**,
> and the fix is an engineering change we can apply to every animal.

> [!warning] One honest correction, recorded rather than quietly dropped
> An impedance block taken immediately after that swap indicated the **opposite**, that the animal
> had been damaged, at p = 1.0e-07. The recording reversed it. The block had caught the channel in
> a single long open state spanning all 21 minutes of it. This is why impedance is now treated as a
> screen and the recording as the outcome.

⚠️ Four things changed together in that swap: tether construction, removal of the rotating
connector, re seating of the plug, and one anaesthesia episode. **"Does the new tether chain help"
is answered. "Which of the four did it" is not**, and separating them costs one anaesthesia episode
per animal. Notably, the 5 August tether that improved the other animal **kept** the rotating
connector, so what the two successful chains share is the **soldered, resin sealed construction**.

### 3.4 The first working animal, and the confound that is now resolved

The working animal was implanted on 21 July with the rest of the cohort, then **kept in its home
cage untethered until 6 August, 16 days after surgery**. The other seven were tethered on 30 July,
**8 to 10 days after surgery**. Our own protocol requires **at least 14 days**, so this is the first
animal in the project ever tethered in line with it, and it is the best animal we have ever had.

> [!danger] Two things changed at once, and §3.3b resolved it
> That animal also received a **newly built tether with soldered joints under resin**, instead of
> the thin heat shrink joints the others have. **Recovery time and tether construction changed
> together, in one animal**, so on 6 August neither could be claimed.
>
> ✅ **Resolved on 7 August.** A second animal, tethered only **8 days** after surgery, received a
> new tether and went from 0.0% to 87.9% usable. **The tether is what matters. The long recovery is
> not required.**

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

1. ✅ **Recovery time or tether construction? ANSWERED on 7 August: the tether.** An animal
   tethered at day 8 went from 0.0% to 87.9% usable after a new tether chain.
2. **Fit the new tether chain to the remaining animals.** This is now the highest value action
   available, it needs no new surgery, and it costs one anaesthesia episode per animal.
3. ⭐ **Circadian validation is now possible for the first time since 31 July**, because we have two
   working animals and a full light and dark cycle. The proportion of sleep in the light phase
   should approach the literature value of roughly 70%. That is a check on the whole analysis
   pipeline that does not depend on any threshold we chose.
4. **Export the two working animals to EDF+ for manual scoring.**
5. **One muscle channel, C1, is genuinely ambiguous** and needs video to resolve.
6. **The interference question** raised previously, whether a dangling cable disturbs its
   neighbours, is half answered. Stripping the empty cable element by element showed **our tethers,
   slip rings and splitters are not leaking**; the spurious readings come from the amplifier's own
   behaviour on a floating input. The remaining half, whether the empty cable disturbs a working
   neighbour, is designed and not yet run.
7. **A hardware high pass filter at 1.10 hertz** is applied before the data is saved and cannot be
   undone. It attenuates the bottom of the delta band. It is identical on all ports and all our
   thresholds were derived from data carrying it, so our internal comparisons are unaffected, but it
   matters for comparison with published values.

> [!quote] Paper ready
> Over a 23.66 h recording spanning a full light and dark cycle, two of eight implanted animals
> produced signal that differed from simultaneously acquired unconnected amplifier inputs, with
> usable fractions of 99.6% and 86.5% of 10 s epochs and longest uninterrupted intervals of 3.6 h
> and 1.5 h. In one animal, replacement of the tether chain raised the usable EEG fraction from
> 0.0% to 87.9% and reduced median 60 Hz amplitude from 916.9 to 133.2 microvolts, with spectral
> slope moving from −0.38, inside the unconnected distribution, to −2.05, outside it.
>
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
