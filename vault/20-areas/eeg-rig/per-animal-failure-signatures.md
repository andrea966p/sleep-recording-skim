---
tags: [troubleshooting, symptom, eeg, emg, tether, diagnosis]
created: 2026-08-07
---

# Telling failure modes apart when every animal just says "OPEN"

> [!abstract] TL;DR — for non-technical readers
> **What this is.** Stage 1 labels a bad animal `OPEN` and stops there. That one word hides at
> least four different faults which need different fixes. This page is how to tell them apart from
> the recording alone, with no extra hardware and no handling of the animal.
>
> **Why it exists.** On 2026-08-06 six of eight animals were `OPEN`. Treating them as one problem
> would have been wrong: one had a chewed tether, one had a perfectly good muscle channel, and two
> looked like a shared wiring fault rather than two independent electrode failures.
>
> **How to read it.** §1 is the lookup table. §2 is the worked example on all eight positions.
> Big picture: [[2026-08-07-rig-specification-and-analysis-method]].

## 1. The four signatures

Measure, per channel, over epochs spread across the whole recording: **60 Hz hum**, **rms**,
**fraction of epochs railed**, **spectral slope after notch + 0.5-30 Hz band-pass**, and
**the correlation between the animal's own two channels** after the same filtering.

| signature | hum | railed | slope | EEG~EMG correlation | fault | fix |
| --- | --- | --- | --- | --- | --- | --- |
| **working** | **very low**, 15-135 µV | 0% | **steep, < −1.2** | **low, < 0.1** | none | — |
| **floating / open conductor** | **very high**, 4000-6000 µV | 2-7% | flat | low to moderate | that electrode or its wire is not connected | tether chain |
| **shared path** | high on **both** channels | both rail | flat | **high, > 0.5** | one fault upstream of both channels: ground, connector, tether body | tether chain, check ground pin |
| **damaged / partially conducting** | **intermediate**, 1000-1400 µV, and **quieter than the wire-free floor** | near 0% | flat | low | conductors damaged but not fully open, e.g. **chewed tether** | replace tether |

> [!important] ⭐ The correlation between an animal's own two channels is the useful new one
> EEG and EMG are different electrodes in different tissue. **If they are both real, they should
> barely correlate.** Working animals sit at **0.07 to 0.08**. When both channels are riding the
> same noise, the correlation climbs, and **> 0.5 means one shared fault, not two coincidences.**

> [!warning] 🛑 Spectral slope judges EEG. It does NOT judge EMG.
> Real EMG is broadband, so a flat spectrum is **expected** for a working muscle channel and cannot
> be used against it. For EMG, judge by **hum** and by whether rms exceeds what hum alone explains.

> [!warning] The wire-free floor is not the quietest thing on the rig
> On this recording the floor itself sat at **hum 2276 µV, rms 2440 µV, 2.7% railed**. A damaged
> tether can read **quieter than the floor** while still carrying no signal. Quiet is not good.

## 2. Worked example: all 8 positions, 2026-08-06 overnight recording

`allego_1__uid0806-16-57-38`, 23.66 h, 120 epochs sampled across the whole recording.
**Wire-free floor: hum 2275.9 µV, rms 2440.3 µV, 2.7% railed, slope −0.47.**

| position | ch | hum µV | rms µV | railed | slope | EEG~EMG r | reading |
| --- | --- | --- | --- | --- | --- | --- | --- |
| **B1** | EEG | **38.2** | 70.9 | 0.0% | **−1.97** | **0.08** | ✅ **working** |
| | EMG | **15.2** | 54.1 | 0.0% | −1.28 | | |
| **D2** | EEG | **134.1** | 123.2 | 0.0% | **−1.96** | **0.07** | ✅ **working** |
| | EMG | **26.6** | 43.9 | 0.0% | −1.33 | | |
| **A1** | EEG | 5312.0 | 3986.1 | 2.8% | −0.25 | 0.23 | EEG **floating**; EMG **connected but hum-dominated** |
| | EMG | **264.4** | 278.1 | 0.0% | −1.11 | | |
| **C1** | EEG | 5813.5 | 4282.7 | 6.8% | −0.34 | 0.13 | EEG **floating**; ⭐ EMG **genuinely connected** |
| | EMG | **75.9** | 544.2 | 1.2% | −0.62 | | |
| **C2** | EEG | 1076.3 | 1693.4 | 0.3% | −0.40 | 0.19 | 🦷 **damaged tether**, both channels |
| | EMG | 1331.0 | 1788.1 | 0.4% | −0.36 | | |
| **D1** | EEG | 6196.8 | 4519.7 | 2.8% | −0.28 | **0.74** | 🔴 **shared path**, one fault not two |
| | EMG | 5363.2 | 4072.0 | 7.0% | +0.12 | | |
| **B2** | EEG | 778.7 | 2829.9 | 0.5% | −0.57 | **0.50** | **shared path**, mixed |
| | EMG | 3667.1 | 3708.4 | 6.0% | −0.33 | | |
| **A2** | EEG | 2546.4 | 2454.0 | 1.6% | −0.37 | 0.49 | **NO MOUSE**, the control |
| | EMG | 4506.5 | 3538.2 | 5.8% | −0.29 | | |

### What each animal actually needs

- **C2 — the chewed tether is confirmed by the data.** Both channels sit at intermediate hum,
  **quieter than the wire-free floor**, with almost no railing and no signal. That is a partially
  conducting, damaged cable, not an open electrode and not a dead animal. **Replace the tether.**
- **C1 — the best salvage candidate on the rig.** Its EMG hum is **75.9 µV**, inside the measured
  connected band of 9-90 µV, so that electrode is genuinely making contact. Its EEG is fully
  floating. ⚠️ Its EMG rms of 544 µV is far more than hum explains, so there is large non-hum
  content that is **either real muscle activity or movement artefact, and video is the only way to
  separate them.**
- **A1 — one good half.** EMG connected at 264 µV hum but swamped by it; EEG floating. Same shape
  as C1, one grade worse.
- **D1 and B2 — shared-path faults.** Correlations of **0.74 and 0.50** say both channels are
  riding one common potential, so this is **one fault upstream of both**, in the ground, connector
  or tether body. It is not two independent electrode failures. Check the ground pin mating before
  assuming anything about the implants.
- **A2 — no animal.** Behaves as the control should.

> [!success] Five of six failures point at the tether chain, not the implants
> One chewed cable, two shared-path faults, and two animals with a **working electrode on one
> channel and a floating one on the other through the same tether**. None of that is a pattern of
> failing implants. It is consistent with [[2026-08-07-rig-specification-and-analysis-method]]
> Part 1 claim 4: the tether chain is the fix.

> [!quote] Paper-ready
> Channels failing a quality gate were further classified by 60 Hz amplitude, saturation rate,
> post-filter spectral slope and the correlation between an animal's own two recording channels.
> Working animals showed inter-channel correlations of 0.07 to 0.08, whereas failing animals
> reached 0.74, indicating a single shared fault upstream of both channels rather than independent
> electrode failures.

## 3. How to run it

`eeg-emg-analysis/qc/per_animal_forensics.py <recording_base>`, using
`~/eeg-analysis-venv/bin/python` because it needs scipy. It samples epochs across the whole
recording rather than one window, so a transient state cannot dominate the answer.
