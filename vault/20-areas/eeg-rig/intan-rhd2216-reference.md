---
type: reference
area: eeg-rig
status: active
status-note: "complete"
tags:
  - reference
  - intan
  - rhd2216
  - headstage
  - bipolar
  - eeg
  - emg
  - datasheet
created: 2026-06-27
source: 06-references/datasheets/Intan_RHD2000_series_datasheet.pdf
---

# Intan RHD2216 Chip Reference (bipolar headstage)

> [!abstract] TL;DR — for non-technical readers
> **What this is.** The chip-level facts for our headstage amplifier, the **Intan RHD2216**, taken straight from the official Intan RHD2000-series datasheet (every number below cites a page). This is the "why the hardware behaves this way" companion to the operator guides.
> **Why it exists.** Several rig decisions only make sense once you know the chip: why we **don't use a reference electrode**, why a floating animal makes every channel **slam to ±5 mV**, why DC offsets don't matter, and what filter bands the chip can do. Those all come from this datasheet.
> **How to read this page.** Skim §1 (the one big idea: bipolar vs unipolar). §2 = the numbers that govern recording (input range, gain, noise, filters). §3 = power/pins. Use it as a lookup; the operator workflow lives in [[signal-quality-and-grounding]], [[signal-mapping-guide]], and [[sleep-recording-operator-manual]].

> [!info] Source
> All facts cite `Intan_RHD2000_series_datasheet.pdf` ("RHD2216 / RHD2132 Digital Electrophysiology Interface Chips", 11 Dec 2012; updated 8 Dec 2023). Page numbers are the datasheet's own printed page footers. The **acquisition sample-rate minimum (1 kHz)** is an Allego/Radiens *software* limit, not a chip limit — see [[allego-sampling-rate]].

---

## 1. The one big idea — RHD2216 is **bipolar (differential)**, RHD2132 is unipolar

The RHD2000 family has three members (datasheet p2):

| Device | Amplifiers | Input pins | Reference |
|---|---|---|---|
| **RHD2216** (ours) | 16 | **16 × 2 differential inputs** (`in0+`,`in0−`,`in1+`,`in1−`,…) | **none** — each amplifier has its own +/− pair |
| RHD2132 | 32 | 32 **unipolar** inputs (`in0`,`in1`,…) | **1 common** reference input (`ref_elec`) |
| RHD2164 | 64 | 64 unipolar | 1 common reference |

The RHD2216 "contains an array of 16 amplifiers having **independently accessible differential inputs**" (p4). Each channel measures the **difference** between its own `+` and `−` pin — it is **self-referencing per pair**. There is no array-wide reference line on this chip.

> [!important] Why we leave `REF` empty and never set a reference electrode
> A common/reference electrode input (`ref_elec`) **only exists on the unipolar RHD2132/RHD2164** (datasheet p2, p5). On the **bipolar RHD2216 there is no `ref_elec` pin at all.** So the adapter's `REF` pad has nothing to drive on our chip → **leave `REF` unconnected.** Referencing is done *per pair* (the `−` electrode), or in software via **Paired Reference** (see [[signal-quality-and-grounding]] §3a). This is the chip-level reason behind the rule in [[grounding-reference-noise-concepts]].

> [!note] Bipolar inputs reject 50/60 Hz well — when impedances match
> Datasheet p2: *"The positive and negative amplifier inputs on the RHD2216 have **balanced input impedances**; this will provide the best rejection of common-mode noise (most commonly, 50/60 Hz interference) if all electrodes … are roughly the same impedance."* This is why decent, matched EEG/EMG electrodes on the RHD2216 already suppress mains hum (measured CMRR = 82 dB at 50/60 Hz, p7).

---

## 2. The numbers that govern recording

### 2.1 Input range — the ±5 mV rail (why a floating animal saturates)
| Parameter | Value | Page |
|---|---|---|
| **Amplifier AC input voltage range** | **±5.0 mV** | p7 |
| Allowable DC offset at input | ±0.4 V (ESD diodes conduct beyond this) | p7 |
| Input-referred offset (DSP removal off) | < ±100 µV | p7 |

> [!warning] This ±5 mV is the hard ceiling behind every "railed channel"
> The amplifier physically cannot see signal beyond **±5 mV** (≈10 mV peak-to-peak). When the animal is not tied to the chip ground, the whole animal's potential drifts out of this window and **every channel pegs at the rail** — the exact floating-animal signature in [[signal-quality-and-grounding]] §2 and the bug chased in [[2026-06-27]]. Datasheet Figure 1 (p8) shows a clean ±5.0 mV triangle at the edge of linearity.

> [!important] There are TWO ceilings, and the SAVED DATA rails at the higher one
> Added 2026-08-03 after measuring it. The ±5 mV above is the amplifier's
> **linear range**. The number you actually observe in a `.xdat` file is the
> **ADC full scale**, which follows from two values already on this page:
>
> ```
> V_LSB × (2^15 − 1)  =  0.195 µV × 32767  =  6389.6 µV  ≈  ±6.4 mV
> ```
>
> **Measured:** `max|sample|` = **6389.8 µV, identical to four significant
> figures on all 8 channels** of the 2026-07-31 recording. So:
>
> | | value | meaning |
> | --- | --- | --- |
> | ±5.0 mV | datasheet | edge of **linearity** — past this the amplifier is nonlinear |
> | **±6389.6 µV** | derived + measured | **hard digital ceiling** — samples cannot exceed it |
>
> Practical consequence: a channel at 11 mV peak-to-peak is badly misbehaving but
> is **not** yet pegged; true saturation is ~12.8 mV pk-pk. Analysis counts a
> sample as railed at **≥ 6376.8 µV** (99.8 % of full scale). See
> `02-procedures/eeg-data-analysis/pipeline/qc_thresholds.py`.

### 2.2 Gain, ADC, resolution
| Parameter | Value | Page |
|---|---|---|
| Amplifier differential gain (midband) | **192 V/V** (45.7 dB) | p6 |
| Amplifier **DC** differential gain | **0 V/V — complete DC rejection** | p6 |
| ADC | on-chip **16-bit** | p1 |
| ADC step size (referred to electrode), `VLSB` | **0.195 µV** | p6 |
| Max ADC MUX switching `fMUX` | 1.05 MHz → 32 channels up to **30 kS/s each** | p1, p7 |

> [!note] DC is rejected on-chip
> Amplifier DC gain = 0 (p6): on-chip input capacitors block DC offsets from the electrode–tissue interface, "eliminating problems with built-in potentials" (p1). So slow electrode DC drift does **not** ride into the signal — useful to know when judging traces.

### 2.3 On-chip filters (sets the EEG/EMG bands)
The amplifier band is programmable on-chip (datasheet p6):

| Cutoff | Tunable range | On-chip register range | Roll-off |
|---|---|---|---|
| **Low-frequency 3-dB (`fL`, high-pass)** | 0.02 Hz – 1.0 kHz | **0.1 Hz – 500 Hz** | 1-pole below `fL` |
| **High-frequency 3-dB (`fH`, low-pass)** | 10 Hz – 20 kHz | **100 Hz – 20 kHz** | 3-pole 3rd-order Butterworth above `fH` |

Plus an **optional on-chip DSP high-pass** for amplifier offset removal (p1). These ranges comfortably cover our recording bands (EEG ≈ 0.5–30 Hz, EMG ≈ 10–300 Hz — see [[signal-quality-and-grounding]] §3b and [[eeg-emg-data-guide]]).

### 2.4 Noise and isolation
| Parameter | Value | Page |
|---|---|---|
| **Input-referred noise** `vni` | **2.4 µVrms** typical | p1, p7 |
| CMRR @ 50/60 Hz | 82 dB | p7 |
| PSRR | 75 dB | p7 |
| Crosstalk (adjacent amplifiers) | −68 dB | p7 |
| Input impedance `\|Zin\|` | 1300 MΩ @ 10 Hz; 13 MΩ @ 1 kHz | p7 |
| Input capacitance `Cin` | 12 pF | p7 |

> [!tip] The noise floor you see on screen
> 2.4 µVrms input-referred noise is why a clean, well-grounded but quiet channel reads only a few µV (the "noise floor" anchor in [[signal-quality-and-grounding]]). Anything reading thousands of µV is not signal — it is floating/hum.

---

## 3. Power and key pins (RHD2216)

| Pin(s) | Function | Page |
|---|---|---|
| `VDD`, `GND` | **3.3 V supply (3.2 – 3.6 V)**; all VDD common, all GND common | p5, p6 |
| `in0+`,`in0−`,`in1+`,`in1−`,… | **differential (bipolar) amplifier inputs** (RHD2216 only) | p5 |
| `ref_elec` | common reference — **RHD2132 only; absent on RHD2216** | p2, p5 |
| `CS`,`SCLK`,`MOSI`,`MISO` | 4-wire SPI (CMOS or LVDS via `LVDS_en`) | p5 |
| `ADC_ref` | needs 10 nF cap to ground; ≈1.225 V reference | p5 |
| `auxin1–3` | auxiliary ADC inputs (0.10–2.45 V) | p5 |

> [!check] Matches our bench reading
> Datasheet `VDD` spec **3.2–3.6 V** (p5/p6) — our measured headstage power was **3.57 V** ([[2026-06-27]]), i.e. healthy, near the top of range. The DMM power test target in [[multimeter-guide]] uses this spec.

> [!important] Sample-rate floor is software, not chip
> The datasheet specifies the **maximum** (30 kS/s/channel, p7) but no minimum — the chip can be clocked slower. The **1,000 S/s acquisition minimum is imposed by Allego/Radiens** (manual p176). For sleep recording: acquire at the 1 kHz minimum and **decimate to 128–256 Hz offline**. Full detail: [[allego-sampling-rate]].

---

## Related
- [[grounding-reference-noise-concepts]] — why `REF` is empty, ground vs reference (chip reason lives here in §1)
- [[signal-quality-and-grounding]] — the ±5 mV rail in practice; noise-floor cheat-sheet
- [[signal-mapping-guide]] — pad ↔ native channel ↔ `D/n`
- [[allego-sampling-rate]] — the 1 kHz software minimum + offline decimation
- [[eeg-emg-data-guide]] — using the bands/amplitudes this chip produces
- [[radiens-software-reference]] — the Allego software side
