---
type: reference
area: allego
status: active
canonical: true
tags: [procedure, eeg, allego, channel-selection, canonical, critical]
created: 2026-08-03
priority: critical
---

# ⭐ CANONICAL — which Allego channels to select. Settled by measurement.

> [!warning] Updated 2026-10-22: this page is the answer for the bipolar EEG/EMG layout only. The unipolar layout used for ahyeon's 3 mice (run of 2026-10-15) selects sites `/18` to `/23` on ports A, B and C. [[rig-layout-and-recording-settings]]

> [!success] THE ANSWER
> **Select `/1`, `/2`, `/33`, `/34` on every port.**
> 16 channels total for 8 mice. Nothing else.
>
> ```
> A/1  A/2  A/33  A/34
> B/1  B/2  B/33  B/34
> C/1  C/2  C/33  C/34
> D/1  D/2  D/33  D/34
> ```
>
> `/1` = **EEG**, `/2` = **EMG** — for the mouse in splitter slot 1.
> `/33` = **EEG**, `/34` = **EMG** — for the mouse in splitter slot 2.
> All four are **already bipolar**. **Never subtract them from each other.**

This page exists because the answer was scattered across six documents, some of
which contradicted each other. **This page wins.** If another page disagrees,
this one is right and that one is stale — say so and fix it.

Verified 2026-08-03 three independent ways: the Intan datasheet, the recorded
Allego metadata, and a channel-by-channel measurement of all 64 slots on all
four ports of a real recording.

## 1. How the mouse is wired (the only wiring we use)

Every mouse: **four electrode wires to Intan C3410 adapter pads 0, 1, 2, 3, plus
GND.** That is all.

| C3410 pad | slip-ring colour | electrode | chip pin |
| --- | --- | --- | --- |
| **0** | red | EEG frontal-L | `in0+` |
| **1** | black | EEG parietal-L | `in0−` |
| **2** | yellow | EMG left | `in1+` |
| **3** | blue | EMG right | `in1−` |
| `GND` bus | green | parietal-R dura | animal ground (not a recorded channel) |
| `REF` | — | — | **empty by design** (the chip is bipolar) |

## 2. Why four pads become TWO channels

The RHD2216 is a **bipolar** chip. Datasheet, p1:

> "The RHD2216 contains an array of **16 amplifiers having independently
> accessible differential inputs (in0+, in0–, in1+, in1–, …)**."

Each amplifier takes **two** electrode pins and outputs **one** channel — the
difference, computed **in hardware, before the ADC**.

```
pad 0 (in0+) ─┐
              ├─► amplifier 0 ─► Allego /1  = EEG   (frontal-L − parietal-L)
pad 1 (in0−) ─┘

pad 2 (in1+) ─┐
              ├─► amplifier 1 ─► Allego /2  = EMG   (left − right)
pad 3 (in1−) ─┘
```

> [!danger] The two mistakes this page exists to prevent
> 1. **Do not select four channels per mouse.** Four pads are two channels.
>    Selecting `/1,/2,/3,/4` records one EEG, one EMG, and two floating inputs.
> 2. **Do not subtract in software.** `/1 − /2` computes *EEG minus EMG*, which
>    is meaningless. The chip already did the subtraction you are tempted to do.
>
> Both were made on this project and together they cost several weeks: 24
> floating inputs were reported as "failed EMG surgeries", and the one animal
> with real sleep looked like noise.

## 3. Why the second mouse starts at 33

Allego's metadata for our rig (`sensors_by_port`, read from a real recording):

```
port A: headstage_id = hstg__passthrough_64, num_channels = 64, connection_ntv_idx = 0
port B: ...                                  num_channels = 64, connection_ntv_idx = 64
port C: ...                                  num_channels = 64, connection_ntv_idx = 128
port D: ...                                  num_channels = 64, connection_ntv_idx = 192
```

Each port is 64 slots because the **C3442 splitter puts two RHD2216 chips on
one port**, and each chip occupies **32 slots** in the RHD2000 data stream —
of which only the first 16 are real. Datasheet, p20:

> "32 biopotential amplifiers sharing the chip with the ADC.
> **(Only channels 0-15 are active in the RHD2216.)**"

So per port: chip 1 = slots 0–31, chip 2 = slots 32–63. The second mouse's
amplifier 0 lands on **slot 32 = Allego `/33`**.

**Native index = `connection_ntv_idx` + offset.** Never assume the base —
read it from the file. Ports also exist at 32 ch (no splitter) and mixed
layouts, and assuming 64 mis-maps every older recording.

## 4. The proof — every slot on a port, measured

Port C of `allego_1__uid0731-18-06-37` (C1 is the project's best animal).
40 windows × 4 s sampled across 8 h. Abridged; the same structure holds on
ports A, B and D.

| offset | Allego | native | rms µV | **mains µV** | delta% | HF% | what it is |
| --- | --- | --- | --- | --- | --- | --- | --- |
| **0** | **C/1** | 128 | 66.3 | **9.4** | 32.6 | 4.1 | ✅ **EEG, connected** |
| **1** | **C/2** | 129 | 57.0 | **6.2** | 22.1 | 60.7 | ✅ **EMG, connected** |
| 2 | C/3 | 130 | 1106 | 973 | 13.2 | 2.1 | floating input |
| 3 | C/4 | 131 | 1112 | 1022 | 8.2 | 2.0 | floating input |
| … | C/5–C/16 | … | 87–4543 | 76–4428 | — | — | floating inputs (amps 2–15, no wires) |
| 16–31 | C/17–C/32 | 144–159 | **32–36** | **3.3** | 0.2 | 93 | inactive slots (chip 1 has only 16 amps) |
| **32** | **C/33** | 160 | 2628 | **2438** | 0.0 | 13.2 | ⚠️ mouse 2 EEG — **open** in this run |
| **33** | **C/34** | 161 | 81.4 | **20.0** | 17.0 | 55.8 | ✅ **mouse 2 EMG, connected** |
| 34–47 | C/35–C/48 | … | 2198–4641 | 2046–4526 | — | — | floating inputs |
| 48–63 | C/49–C/64 | 176–191 | **28–46** | **2.9** | 0.2 | 92 | inactive slots (chip 2) |

Port A cross-check: `A/1` open (4165 µV mains) but **`A/2` connected (9.2 µV,
HF 78.7%)** — the exact "EMG works, EEG doesn't" signature we see everywhere.
Port D: `D/2` connected at 8.8 µV. Structure identical on all four ports.

## 5. 🔑 The three signatures — use these to tell what you are looking at

| | rms | **55–65 Hz mains** | spectrum | impedance |
| --- | --- | --- | --- | --- |
| **Connected electrode** | 30–90 µV | **6–20 µV** | structured: EEG delta-rich, EMG HF-rich | 0.07–2 MΩ |
| **Floating / open input** | 200–4700 µV | **150–4500 µV** | no structure | ~5–9 MΩ |
| **Inactive slot** | ~30 µV | **~3 µV** | flat, HF ≈ 93% | **~0.06 MΩ** (internally tied) |

Three things worth internalising:

1. **Mains amplitude is the contact readout.** Connected vs open differ by
   ~100×, cleanly bimodal, valley at 134 µV. You do not need an impedance sweep
   to know whether an electrode is connected — the hum tells you continuously,
   during the recording.
2. **rms alone cannot distinguish a connected EMG from an inactive slot** — both
   sit near 30 µV. You need the mains level and the spectrum.
3. **An unwired amplifier input and an open electrode look identical.** Both
   float and collect mains. So "huge hum" means *the amplifier's inputs are not
   both terminated in tissue*; it does not by itself say which side failed.

## 6. Selecting it in Allego

Per the SOP in [[allego-electrode-setup-sleep64]]: use a plain passthrough map
(`usrdef_sleep64` and the built-in `Passthrough 64` are byte-equivalent — either
is correct), then select per port:

```
1, 2, 33, 34
```

Selection is **display-only** — the saved `.xdat` contains all 256 channels
regardless. So a wrong selection costs you nothing on disk, and analysis should
always derive the layout from `sensors_by_port` rather than trusting what was
ticked in the GUI.

> [!note] No splitter (32 ch/port)
> With one headstage per port, use `Passthrough 32` and select `/1, /2` only.
> There is no second mouse, and `/33`–`/36` do not exist on that port.

## 7. Impedance, and what it does not tell you

The impedance sweep reports **one number per amplifier**, and on a bipolar chip
that number is **one of the two electrodes** — by chip default the positive
input:

| channel | the impedance number is | **never measured** |
| --- | --- | --- |
| `/1` "EEG" | **EEG frontal-L** (pad 0, `in0+`) | EEG parietal-L (pad 1, `in0−`) |
| `/2` "EMG" | **EMG left** (pad 2, `in1+`) | EMG right (pad 3, `in1−`) |

The chip *can* measure either side — datasheet Register 5, `Zcheck pol sel` —
but **Radiens exposes no way to select it** (verified in the `radiens-core`
0.0.8 source: `ImpedanceRequest` carries only a port, `ImpedanceValue` carries
only `ntv_chan_idx / magnitude_ohm / phase_deg`, and there is no Intan
register-write path at all). Detail and consequences:
[[electrode-connection-state-test]].

## 8. Pages that defer to this one

[[eight-mouse-acquisition-setup]] · [[allego-electrode-setup-sleep64]] ·
[[signal-mapping-guide]] · [[grounding-reference-noise-concepts]] ·
[[04-processing-guidelines]] ·
[[2026-08-01-channel-mapping-correction-first-sleep]]

Analysis implementation: [[eeg-pipeline-manual]] — `derive_layout()` reads
`sensors_by_port` and applies exactly the rule on this page.
