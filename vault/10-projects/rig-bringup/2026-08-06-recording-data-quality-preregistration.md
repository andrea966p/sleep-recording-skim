---
type: experiment
area: rig-bringup
status: done
status-note: "active"
tags: [experiment, eeg, recording, data-quality, pre-registration, duty-cycle]
created: 2026-08-06
---

# Pre-registration: is the recorded data clean and usable, per mouse?

> [!warning] Updated 2026-10-22: The hum criterion used here ("hum is the direct readout of contact") fails when an animal has no ground: a floating A1 scored 100% usable by it, and the slope criterion replaced it. Hum fractions and slope fractions are not comparable [[2026-08-08-ground-fix-post-repin-night]] [[animal-card-and-verdict-ladder]].

> [!abstract] TL;DR
> Until now we have judged animals by impedance, which is a proxy. This afternoon we record
> the real thing and ask one question per mouse: **what fraction of the recording is actually
> usable data, and how long is the longest unbroken usable stretch.** No biology, no sleep
> scoring, no staging. Just whether the signal is real.
>
> The trick that made this morning's impedance work is reused here. Every mouse is wired to
> only 2 of its chip's 16 amplifier inputs, so the other 14 are **real amplifier inputs with
> no wire attached**, recorded simultaneously. They tell us exactly what "nothing" looks like
> in this recording, so every animal channel is judged against a control from the same
> session rather than against a number from the literature.
>
> Written before the recording started, so the thresholds cannot be tuned to flatter the
> result.

Recording: started manually 2026-08-06 afternoon, stopped ~17:00 KST. Files in `~/radix/data/`
as `allego_N__uid0806-HH-MM-SS`, XDAT format, **1000 Hz, all 256 primary channels**.
Impedance context: [[2026-08-06-fleet-duty-cycle-census]] · [[2026-08-06-unloaded-chain-interference]]

## 1. Why this supersedes impedance as the outcome

Impedance predicts **class, not yield**. On the 2 August run the pre-registered impedance
predictions came out **4 correct, 3 wrong, 1 void**. This morning we further learned that an
amplifier input with no wire on it reads below 2 MOhm 21.4% of the time and reached 0.051
MOhm, which is the best electrode value ever recorded on this rig. So impedance can say a
channel is probably connected; only the recording says the data is usable.

## 2. Channels

| group | sites | role |
| --- | --- | --- |
| **animal** | `/1` EEG, `/2` EMG, `/33` EEG, `/34` EMG on each of A, B, C, D | the 8 mice, 16 channels |
| **floor control** | `/3`-`/16` and `/35`-`/48` on each port | **real amplifier inputs, no wire attached**, 112 channels |
| **excluded** | `/17`-`/32` and `/49`-`/64` | inactive slots, internally tied, read ~0.051 MOhm and ~30 µV rms always. **Including them would destroy the control.** |

⚠️ A2 holds **no mouse**, only a cut tether through its slip ring and headstage. `A/33` and
`A/34` are therefore a **second, independent negative control** with the full cable attached.
They must not be reported as an animal.

## 3. Metrics, per channel, per 10 s epoch

| metric | why |
| --- | --- |
| **rms µV**, 0.5-300 Hz | connected 30-90 µV, floating 200-4700 µV per [[memory-eeg-rig-current-state\|eeg-rig-current-state]] |
| **60 Hz amplitude** | **the direct readout of contact on this rig**: connected 9-90 µV, open 1000-4700 µV, cleanly bimodal, about 100x |
| **fraction of samples railed** | clipping invalidates an epoch and once produced a retracted result |
| band powers 0.5-4, 4-9, 9-20, 20-50, 50-300 Hz | spectrum shape; catches a flat or noise-dominated channel that rms alone hides |

10 s epochs are chosen because this morning's impedance showed contact flipping **within
minutes**, so anything coarser would average across states.

## 4. The usable criterion, fixed now

An epoch on a channel is **USABLE** when all three hold:

1. **60 Hz amplitude below the 1st percentile of the floor-control distribution** pooled over
   the whole recording. This is the primary discriminator, because hum is the direct readout
   of contact on this rig.
2. **rms between 10 and 150 µV.** A wide band deliberately: the 30-90 µV figure is the
   measured connected range but was measured on few animals, so the criterion allows margin
   on both sides rather than excluding real data on a number we are not sure of.
3. **railed fraction exactly zero** in the epoch.

Criterion 1 does the work; 2 and 3 are guards against a channel that is quiet for the wrong
reason.

> [!important] The threshold comes from the control in this recording, not from a fixed number
> Every previous threshold on this project was inherited from an earlier session or from the
> literature. Deriving the 60 Hz cut from the 112 unwired channels recorded **at the same
> time, on the same chips, in the same room** removes drift, room noise and session effects in
> one step. If the floor control's own distribution is not clearly separated from the animal
> channels, that is itself the result and no threshold will fix it.

**Per mouse, two primary outcomes:**

| outcome | definition |
| --- | --- |
| **usable fraction** | fraction of 10 s epochs where **EEG and EMG are both USABLE** |
| **longest unbroken usable block** | the longest run of consecutive usable epochs, in minutes |

> [!important] The second one matters more than the first
> Our only genuine sleep recording, C1 on 31 July, was scoreable because it contained a
> **single 8.1-hour unbroken block**, not because its total was high. Scattered usable minutes
> cannot be scored. **Report both, and lead with the block.**

Secondary, reported but not primary: usable fraction of EEG alone, of EMG alone, number of
transitions between usable and unusable per hour (the recording-domain equivalent of the
impedance flip count).

## 5. Pre-registered predictions from this morning's impedance

Written before the recording. This is a genuine test of whether impedance predicts yield.

| animal | impedance verdict, 0.5 MOhm vs floor | prediction for the recording |
| --- | --- | --- |
| **B1, new mouse** | recordable, both channels | **high usable fraction and one long block** |
| A1 | EMG only, p = 1e-16; EEG n.s. | EMG usable, **EEG not**, so usable fraction near zero |
| D2 | EMG only, p = 1e-16; EEG n.s. | same as A1 |
| B2, C1, C2, D1 | neither channel beats an unwired input | **near zero on both channels** |
| A2 | no mouse | **must score near zero. If it does not, the criterion is broken.** |

> [!danger] A2 is the falsification test for this entire analysis
> A2 has no animal. If the analysis reports A2 as having usable data, the criterion is wrong
> and **no other result in this document may be believed.** Check A2 first, before reading any
> animal's number.

## 6. Scope, stated so it is not exceeded

- ✅ **In scope:** is the data clean, is it usable, how much of it, per mouse.
- ❌ **Out of scope:** sleep staging, wake/NREM/REM, any biology. The professor's request was
  explicitly for data quality only.
- ❌ **No REM share, ever.** Not separable on this rig.
- ❌ **Never subtract EEG from EMG.** The signals are already bipolar; the chip subtracts
  before the ADC.

## 7. Protocol notes for the session

- 🛑 **No impedance sweeps while recording.** A sweep injects current into every channel and
  would write a large artefact into the data.
- 🛑 **Nothing touched:** rack, cages, tethers, splitters.
- All 256 primary channels recorded, 1000 Hz, about 1.84 GB/h. 845 GB free at the start.
- Record the start and stop clock times.

## 8. Implementation

Script: `eeg-emg-analysis/qc/usable_fraction_vs_floor.py`, run as
`python usable_fraction_vs_floor.py /home/skimlab/radix/data/allego_0__uid0806-12-45-02`.

**XDAT layout, verified on this file:** `float32`, **262 interleaved channels**
(256 primary + 2 aux + 2 din + 2 dout), values already in **µV**. Channel label comes from
`.xdat.json` → `sapiens_base.biointerface_map`, as `port` + `/` + `site_num`, in file order.
Sample count = filesize ÷ (262 × 4). Read with `np.memmap`, the file is several GB.

## 9. Results

**Recording:** `allego_0__uid0806-12-45-02`, started **12:45:02 KST**, 1000 Hz, all 256
primary channels. Stopped ~17:00.

### Smoke test on the first 90 seconds, before the real analysis

Run only to prove the pipeline is correct, **not a result**. n = 9 epochs.

> [!success] The falsification test passes
> The **floor control channels score 0.00% usable** and **A2, which has no mouse, scores
> 0.0%**. The criterion does not manufacture signal out of nothing, which is the thing that
> had to be true before any animal number could be believed.

Median 60 Hz amplitude per channel, µV, unnotched:

| connected | µV | | open | µV |
| --- | --- | --- | --- | --- |
| B1 EMG | **12.6** | | C2 EEG | 844 |
| D2 EMG | **25.7** | | B2 EEG | 1092 |
| C1 EMG | **26.7** | | D2 EEG | 1597 |
| B1 EEG | **39.1** | | A2 EEG (**no mouse**) | 3553 |
| | | | A1 EEG | 5574 |

**Cleanly bimodal, with nothing between 40 and 600 µV**, reproducing the 9-90 µV versus
1000-4700 µV signature measured across 41 earlier animal-recordings. The one value in the
valley is **A1's EMG at 609 µV**, which this morning's impedance called excellent
(p = 1e-16). Worth watching over the full recording.

### Interim analysis at 14:25, first 1.66 h, 597 epochs

The file was read while still being written, so no recording time was lost to this.

> [!success] The falsification test passes on real data
> **Floor control 0.00% usable. A2, which has no mouse, 0.0%.** Threshold derived from the
> 66,864 floor-control epochs in this file: **60 Hz amplitude < 388.1 µV**.

| animal | EEG usable | EMG usable | **both** | longest unbroken block |
| --- | --- | --- | --- | --- |
| **B1, new mouse** | **99.8%** | **99.7%** | **99.7%** | **39.5 min** |
| D2 | 0.0% | 86.1% | 0.0% | 0 |
| C1 | 0.0% | 36.3% | 0.0% | 0 |
| A1 | 0.0% | 5.2% | 0.0% | 0 |
| A2 (**no mouse**) | 0.0% | 0.0% | 0.0% | 0 |
| B2, C2, D1 | 0.0% | 0.0% | 0.0% | 0 |

> [!important] Only one animal has any usable EEG at all
> **Seven of seven implanted animals score 0.0% on EEG.** Sleep cannot be staged without EEG,
> so this recording yields **exactly one scoreable mouse**, which is what the morning
> impedance census predicted.

### Why each channel scores what it does

| channel | rms median | 60 Hz median | usable | interpretation |
| --- | --- | --- | --- | --- |
| B1 EEG `B/1` | 89 µV | 38.6 µV | 99.8% | clean signal |
| B1 EMG `B/2` | 18.3 µV | 11.5 µV | 99.7% | clean signal |
| D2 EMG `D/34` | 49.3 µV | 40.2 µV | 86.1% | genuinely good |
| C1 EMG `C/2` | **1834.6 µV** | 505.8 µV | 36.3% | **ambiguous, see below** |
| A1 EMG `A/2` | 331.5 µV | 296.0 µV | 5.2% | **hum-dominated** |

> [!note] A1's EMG resolves the impedance-versus-recording discrepancy
> Impedance called A1's EMG excellent this morning, p = 1e-16, 0.167 MOhm. In the recording
> its rms is **331 µV of which 296 µV is 60 Hz**, so almost all of its signal is mains.
> **Impedance measures that the wire is connected. It cannot see that what rides on the wire
> is hum.** This is the clearest demonstration yet of why the recording, not the impedance,
> is the outcome measure.

> [!warning] C1's EMG is genuinely open and we cannot resolve it today
> Its rms of 1834.6 µV is far larger than its 505.8 µV of hum accounts for, so there is
> substantial **non-hum broadband content**. That is either real EMG bursting or movement
> artefact, and **the two cannot be separated without video**. All cameras were removed from
> the room on 4 August. Reported at its pre-registered value of 36.3% and left open.

### Scorecard against the pre-registered predictions

| prediction | outcome | |
| --- | --- | --- |
| B1 high usable fraction and one long block | 99.7%, 39.5 min | ✅ **hit** |
| D2 EMG usable, EEG not | 86.1% / 0.0% | ✅ **hit** |
| B2, C2, D1 near zero on both | 0.0% throughout | ✅ **hit** ×3 |
| A2 near zero (falsification test) | 0.0% | ✅ **hit** |
| A1 EMG usable, EEG not | EEG 0.0% ✅ but EMG only **5.2%** | ⚠️ **partial** |
| C1 near zero on both | EMG **36.3%** | ❌ **miss** |

**6 hits, 1 partial, 1 miss.** Better than the 2 August run's 4 correct / 3 wrong / 1 void,
and the two failures are in **opposite** directions, so impedance is not biased optimistic or
pessimistic — it is simply blind to what rides on a connected wire.

### Note on the rms guard

Criterion 2, rms 10 to 150 µV, is the binding constraint on A1 and C1 rather than the hum
threshold. It was pre-registered deliberately wide and **has not been changed**. The
diagnostic above reports hum and rms separately so the effect of the guard is visible rather
than hidden, and a future analysis may wish to revisit the upper bound for EMG specifically,
since EMG bursts can legitimately exceed 150 µV.

### Decision taken at 14:25 (first pass)

**Recording continued rather than stopped.** The yield question is already answered and will
not change. **B1's longest unbroken block, 39.5 min out of 100, is the one number still
moving**, and block length is what decides scoreability. Running to 17:00 costs nothing.

---

# 10. What I actually did, in plain words

> [!abstract] Read this section if the rest of the page is hard to follow
> This is the whole analysis explained without jargon, in the order I did it, including the
> two figures and what they mean. Written 2026-08-06 because the method got complicated fast
> and the reasoning matters more than the numbers.

## 10.1 The problem I was trying to avoid

I want to know, for each mouse, whether the electrical signal we recorded is real brain
activity or just noise.

The hard part is that **noise can look exactly like brain activity once you filter it**. If I
take a channel with nothing attached to it, remove the 60 hertz hum from the electrical mains,
and keep only the 0.5 to 30 hertz range where sleep signals live, I get a wandering wiggly
line that looks perfectly plausible. So "the trace looks good" is not evidence. I needed
something better.

## 10.2 The trick: the rig measures "nothing" for us, 112 times over

Every mouse is connected to the recording chip through **only 2 of the chip's 16 amplifier
inputs**. One input pair carries the brain signal, one carries the neck muscle signal. The
other 14 inputs on that chip are **real amplifiers with no wire attached to them at all**.

They get recorded anyway, at the same moment, on the same hardware, in the same room. Across
the four ports that gives **112 channels of pure nothing**, recorded simultaneously with the
animals.

That is the control. Anything a real mouse channel does, it has to do **more** than these 112
do, or it is not evidence of a mouse.

> [!warning] One group had to be excluded and it matters
> Channels `/17` to `/32` and `/49` to `/64` are **inactive slots**. They are not amplifiers
> with nothing attached, they are internally tied together inside the chip, so they always
> read quiet and low. If I had included them in the control group, the control would have
> looked artificially good and every real animal would have looked bad by comparison. Only
> `/3` to `/16` and `/35` to `/48` are true "amplifier with no wire" channels.

Separately, and by luck, the **A2 position on the rig has no mouse in it** — just a cut cable.
So A2 is a second, completely independent control. It has the whole cable, the rotating
connector and the amplifier board attached, and no animal. If my analysis ever says A2 has
good data, my analysis is broken.

## 10.3 First pass: judging the raw signal

I cut the recording into **10 second pieces**, called epochs, and measured three things on
every channel in every piece:

| what I measured | in plain words |
| --- | --- |
| **60 hertz amplitude** | how much electrical mains hum is on this channel |
| **rms** | how big the signal is overall, roughly its average size |
| **railed fraction** | how often the amplifier hit its ceiling and could record no more |

**Why 60 hertz hum is the key measurement.** Korean mains electricity runs at 60 hertz and it
leaks into everything. A properly connected electrode has a low impedance path, so the hum
mostly cancels out and sits at 9 to 90 microvolts. A disconnected electrode acts like an
antenna and the hum explodes to 1000 to 4700 microvolts. We measured that across 41 earlier
recordings. **It is about a hundredfold difference with almost nothing in between**, so it
separates connected from disconnected extremely well.

**How I picked the pass mark.** I did not choose a number. I took the 112 wire-free channels,
looked at all 66,864 of their 10 second pieces, and took the value that only the quietest 1
percent of them beat: **388 microvolts of hum**. A mouse channel counts as usable in that
piece if it is quieter than that, plus its overall size is sane, plus the amplifier never hit
its ceiling.

**The check that had to pass first.** I ran that criterion on the control channels themselves.
They scored **0.00 percent usable**, and the no-mouse A2 slot scored **0.0 percent**. Good, the
method is not inventing signal out of nothing. Only then did I look at the animals.

**Result:** B1 usable 99.7 percent of the time on both channels. D2's muscle channel 86
percent. Everything else near zero, and **every brain channel except B1's was at 0.0 percent**.

## 10.4 The fair objection, and the second pass

The objection is a good one: **that first pass judged the raw signal**, before any cleaning.
Maybe there is perfectly good brain activity hiding underneath the hum, and once we remove the
hum properly it appears. That is what you would normally do before scoring sleep by hand.

So I did the standard cleaning:

1. **Notch filters at 60, 120 and 180 hertz** — surgically remove the mains hum and its echoes.
2. **Band-pass 0.5 to 30 hertz** — keep only the frequency range sleep scoring uses, throw away
   everything above and below.

Then I judged again. But **crucially, I put the 112 wire-free control channels through exactly
the same cleaning**, so I could see what "nothing" looks like after cleaning too.

> [!danger] The result that decides everything
> After cleaning, a channel **with no wire attached** comes out at a median of **69 microvolts**
> of smooth, plausible, EEG-looking signal.
>
> **Filtering manufactures a convincing trace out of nothing.** This is why looking at cleaned
> traces cannot tell you whether a mouse is connected, and it is the single most important
> thing on this page.

## 10.5 What survives cleaning: the shape of the spectrum

Filtering can change how big a signal is, and it can remove specific frequencies. What it
cannot do is invent the **shape** of a real biological spectrum.

Real brain activity has a characteristic shape: **most of the power sits at low frequencies and
falls away steeply as frequency rises**. Physicists call this a one-over-f shape. Plot it on a
log-log graph and it is a downhill slope. Electrical noise, by contrast, is spread evenly
across frequencies, so it plots as a flat line.

So I measured two shape numbers per channel:

| number | what it means | real brain | bare wire |
| --- | --- | --- | --- |
| **spectral slope** | how steeply power falls as frequency rises | steeply negative | near flat |
| **delta fraction** | share of the power in the 0.5-4 hertz slow-wave band | high | low |

And again I measured them on the 112 wire-free controls, to find the range that "nothing"
occupies: **slope between −1.10 and −0.04, delta fraction around 0.16.**

| animal brain channel | slope | delta fraction | verdict |
| --- | --- | --- | --- |
| **B1** | **−2.15** | **0.47** | **far outside the bare-wire range. Real.** |
| B2 | −0.47 | 0.17 | inside the bare-wire range |
| C2 | −0.38 | 0.17 | inside the bare-wire range |
| D2 | −0.38 | 0.17 | inside the bare-wire range |
| A1, C1, D1 | — | — | amplifier railed 2 to 7 percent of the time |
| A2, no mouse | −0.04 | 0.09 | inside the bare-wire range, as it must be |

> [!important] Railing cannot be filtered away, and this is why
> When the hum is so large that the amplifier hits its ceiling, the tops and bottoms of the
> wave get **flattened off**. That is not a frequency you can subtract out, it is information
> that was destroyed at the moment of recording. A1, C1 and D1 are in that state for 2 to 7
> percent of the recording. **No amount of post-processing brings those channels back.**

## 10.6 The conclusion, and why I trust it

**Only B1 has real brain activity.** Two completely separate methods say so:

- the **raw** method, based on mains hum against a 112 channel control, and
- the **cleaned** method, based on spectral shape against the same control after identical
  filtering.

They share no assumptions and no thresholds, and they agree. Both also correctly report that
the **no-mouse A2 slot has nothing**, which is the test that would have caught either of them
being wrong.

# 11. The two figures, and what they show

Both are in `05-experiments/attachments/`, generated from **10 minutes taken from the middle of
the recording**, so nothing was cherry-picked from a good moment.

## 11.1 Filtered traces

![[2026-08-06-traces-filtered.png]]

**What it is:** 20 seconds of signal from seven channels, after the 60/120/180 hertz notch and
the 0.5 to 30 hertz band-pass. Top is B1. Below it are three other mice, then the no-mouse A2
slot, then two bare-wire control channels.

**The one rule that makes it honest: every panel uses the identical vertical scale, plus or
minus 400 microvolts.** If each panel were auto-scaled to fit its own data, which is what
recording software does by default, every one of these would look like a beautiful signal. The
software would simply zoom into the noise until it filled the panel. **A fixed shared scale is
what makes the comparison meaningful.**

**What it shows:** B1 is smooth and rolling, with visible slow waves. Everything else is dense
high-frequency hash. B2's hash is smaller than the others, but it is still hash, with no slow
structure. And the bare wires at the bottom look qualitatively like the mice above them, which
is exactly the point.

## 11.2 Power spectrum

![[2026-08-06-psd.png]]

**What it is:** the same channels, but instead of showing signal over time it shows **how much
power sits at each frequency**. Both axes are logarithmic, which is the standard way to view
this, because it turns the expected one-over-f relationship into a straight downhill line.

**What it shows:** B1, the thick blue line, climbs at the far left and then **falls steeply and
continuously** from about 2 hertz onward, dropping roughly five orders of magnitude by 40
hertz. That is the signature of real neural activity.

Every other line is a **flat plateau** across the whole range. Flat means the power is spread
evenly over all frequencies, which is the definition of noise. The no-mouse A2 line and the
bare-wire lines are flat in exactly the same way as the animal channels are, at different
heights. **Height is loudness. Shape is biology. B1 is the only line with the shape.**

The drop-off that all lines share above about 30 hertz is just the band-pass filter doing its
job, and carries no information.

> [!quote] Paper-ready
> Recorded signals were assessed against 112 simultaneously acquired amplifier inputs that had
> no electrode attached, providing a within-session null distribution. After 60, 120 and 180 Hz
> notch filtering and 0.5-30 Hz band-pass, unconnected inputs yielded a median root mean square
> amplitude of 69 microvolts of spectrally flat signal, demonstrating that filtered trace
> morphology alone is insufficient to establish electrode connection. Channels were therefore
> classified by spectral slope and delta fraction relative to the unconnected distribution. One
> of eight animals fell outside that distribution.

---

# 12. Can we just reject the railed epochs and keep the 24 hours?

Proposed 2026-08-06: mark railed epochs as missing, keep the rest of the night, report the
rejection rate. **The principle is correct and is now our standing policy**, written up in
[[eeg-artefact-and-railing-rejection-policy]]. It does not rescue this recording, and the
measurement showing why is in §4 of that page.

Three sentences of summary:

1. **The unit was wrong.** "7% railed" was a fraction of **samples**. At the **epoch** level the
   same channel is **77.6%**, because one railed sample spoils a whole 10 s epoch.
2. **The railing is not movement.** A1 and D1 rail in unbroken blocks of 91 and 130 minutes, and
   the **A2 position, which has no mouse in it, rails 100% of the time**.
3. **Rejection does not help.** Keeping only the perfectly clean epochs, the surviving spectral
   shape still sits inside the bare-wire range for B2, C2, C1 and D2. Those epochs are not
   spoiled EEG, they are not EEG.

**B1 is unaffected: 0 railed epochs in 782.** If that holds for 24 hours it is a complete
artefact-free record needing no rejection at all.
