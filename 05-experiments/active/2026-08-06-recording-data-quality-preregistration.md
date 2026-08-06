---
tags: [experiment, eeg, recording, data-quality, pre-registration, duty-cycle]
created: 2026-08-06
status: active
---

# Pre-registration: is the recorded data clean and usable, per mouse?

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
| **rms µV**, 0.5-300 Hz | connected 30-90 µV, floating 200-4700 µV per [[eeg-rig-current-state]] |
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

### Full recording

To be filled after the recording stops.
