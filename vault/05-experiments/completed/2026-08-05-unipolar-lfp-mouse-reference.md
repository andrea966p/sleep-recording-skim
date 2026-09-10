---
tags: [experiment, eeg, emg, lfp, unipolar, impedance, reference-prep]
created: 2026-08-05
status: completed
---

# The unipolar LFP mouse, 2026-08-05: a working reference prep

> [!abstract] TL;DR
> A mouse from a **different surgery** was plugged into port A for about 20 minutes as a
> reference look. Different in every way from our eight: depth LFP electrodes, **unipolar**
> Intan headstage mounted **directly on the head**, SPI cable **straight into the XDAQ**,
> **no tether and no slip ring**.
>
> **All six wired sites were live at the same time, with clean physiological signal.** None
> of the eight bipolar mice has ever managed that on any day.
>
> ⚠️ It changes five variables at once, so it **cannot** tell us which one is our problem.
> It is a reference anchor, not an experiment.

Session: [[2026-08-05]] · sweep `2026-08-05/imp_2026-08-05_1723_A-unipolar-lfp-32ch_reference-prep.csv`

## 1. The prep

| | this mouse | our eight |
| --- | --- | --- |
| electrodes | depth LFP wires + EEG + EMG | epidural screws + EMG |
| montage | **unipolar**, every site vs REF | **bipolar** pairs |
| REF | shorted to GND, from a separate location | GND only, REF empty by design |
| headstage | Intan unipolar, **on the head** | RHD2216 on a C3410 adapter |
| path to XDAQ | **SPI cable direct** | tether → slip ring → fan-out |

Channel map on port A:

| site | signal |
| --- | --- |
| `A/18` | EMG 1 |
| `A/19` | LFP reference |
| `A/20` | LFP target |
| `A/21` | EEG frontal |
| `A/22` | EEG parietal |
| `A/23` | EMG 2 |

## 2. Signal, 10 s at 1 kHz, filters = Notch 60 + Low Pass 300

| derived signal | RMS µV | p2p µV | δ 0.5-4 | θ 4-9 | 50-300 |
| --- | --- | --- | --- | --- | --- |
| **EEG** `A/21 − A/22` | 41.8 | 348 | 19.4% | 36.1% | 24.0% |
| **EMG** `A/18 − A/23` | 66.7 | 1005 | 32.5% | 14.7% | 40.2% |
| **LFP** `A/20 − A/19` | 10.0 | 128 | 15.0% | 6.1% | 69.7% |

> [!success] This is real biology and it is scorable
> Power falls off **15 to 61×** from 1-10 Hz to 100-300 Hz. That 1/f shape is the signature
> of genuine neural signal; white noise would be flat. Spectral flatness in 50-300 Hz is
> 0.28 to 0.52, so the band is structured rather than noise. Amplitudes are physiological
> on every channel, and the animal was awake during the recording (theta 36%, high EMG),
> which is what the numbers say.
>
> **The EMG is the first unambiguous EMG on this project.**

## 3. ⚠️ 180 Hz, the third harmonic, is not filtered

| channel | 60 Hz | 120 Hz | **180 Hz** |
| --- | --- | --- | --- |
| `A/21` EEG frontal | 0.27% | 0.26% | **25.86%** |
| `A/19` LFP ref | 0.18% | 0.27% | **6.58%** |
| `A/18` EMG 1 | 0.16% | 0.28% | 2.91% |

The Data filter notches **60 only**, so the third harmonic passes straight through. On the
frontal EEG it is a quarter of all signal power.

**Irrelevant to sleep scoring** (0.5-30 Hz), **but it inflates EMG and LFP**, which live in
20-300 Hz. Fix = add Notch 180 (and 120) in Signal Processing → Data Filters.

> [!important] The low 60 Hz numbers are POST-notch
> A 60 Hz notch was active for this measurement, so 0.10-0.27% at 60 Hz does **not** mean
> the raw hum was low. The size of the 180 Hz harmonic says the opposite: mains coupling is
> present, it has simply been notched at the fundamental.

## 4. ⚠️ Impedance on this prep does not mean what it means on ours

```
A/18 EMG-1     0.206 MΩ  connected
A/19 LFP-ref   2.656 MΩ  "open"
A/20 LFP-tgt   2.396 MΩ  "open"
A/21 EEG-front 1.642 MΩ  connected
A/22 EEG-par   0.584 MΩ  connected
A/23 EMG-2     0.620 MΩ  connected
```

Two independent reasons the usual reading fails here:

1. **`A/19` and `A/20` read "open" and produced the largest signal in the whole set.** The
   2 MΩ threshold was calibrated on epidural screws. A fine-wire depth electrode has a much
   smaller tip and legitimately sits higher. **Do not call those two failed.**
2. **The 26 unwired channels read a median of 0.17 MΩ**, *better* than most of the real
   electrodes. On this headstage the unused inputs are tied to ground, so a low magnitude
   proves nothing at all.

⇒ On this prep, judge contact by **signal**, never by impedance.

## 5. What it does and does not tell us

> [!success] Worth carrying forward regardless of today's contact problem
> Because the montage is **unipolar, any montage can be computed offline** from the same
> recording: `A/21 − A/22` for EEG, `A/20 − A/19` for LFP, `A/18 − A/23` for EMG, or each
> site against ground. **Our eight mice are locked forever into whichever pair was soldered
> at the headstage.** That is a real argument for unipolar in the next cohort, independent
> of everything else.

> [!danger] It cannot assign a cause, and must not be reported as if it can
> This prep differs from ours in **five** ways at once: surgery, electrode type, montage,
> headstage, and the complete absence of tether and slip ring. Six live channels here is
> encouraging, but it identifies no single culprit. Only the paired within-animal tether
> arms ([[2026-08-05-tether-comparison]]) can do that.
>
> It is also **n = 1, about 20 minutes, one awake animal, and no duty cycle was measured**
> because a repeated sweep block was deliberately declined. We do not know whether this
> prep flips like ours do over hours.

## 6. Housekeeping found along the way

**The Allego recording path was set to the Obsidian vault directory**
(`/home/skimlab/Monitoring_project/Monitoring_project_obsidian_vault`). Pressing Record
would write XDAT files into the vault, and Syncthing would replicate them to PC 2. Change
it in Settings before any real recording on this rig.
