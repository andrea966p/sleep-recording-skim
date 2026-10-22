---
tags: [procedure, eeg, control, validation, calibration, bench, planned]
created: 2026-08-08
status: PLANNED, not scheduled
---

# Positive control: pushing a known signal through the whole pipeline

> [!abstract] TL;DR — for non-technical readers
> **What this is.** A bench test where we feed the recording system a signal we made ourselves, of
> a shape and size we already know, and check that what comes out the far end of the analysis
> matches. No animals involved.
>
> **Why it exists.** Every control this project has built is a **negative** one: an empty cable, a
> wire with no electrode, a slot with no mouse. Those prove the pipeline **rejects nothing**. Not
> one of them proves it **finds something**. A pipeline that returned "no signal" for every input
> would pass all of our current checks.
>
> **Status: planned, not scheduled.** Raised by the 2026-08-07 council review as the one thing
> genuinely missing. Written up now so it is ready whenever bench time appears.

Origin: [[2026-08-07-council-review-of-the-analysis-pipeline]] §1.7 and §8.5.

## 1. What it would settle

| question | currently | after this test |
| --- | --- | --- |
| does the pipeline recover a signal that is definitely there? | **never tested** | measured |
| is our microvolt scale correct end to end? | assumed from the datasheet, 0.195 µV/bit | verified |
| ⭐ **how much delta does the 1.10 Hz hardware high-pass actually eat?** | **unknown, standing open item** | **measured as a transfer function** |
| does the spectral-slope discriminator recover a known slope? | assumed | verified |
| does the impedance measurement read a known resistance correctly? | never checked against a standard | verified |

> [!important] ⭐ The frequency-response half of this closes a standing open item
> The acquisition high-pass sits at **1.10 Hz** and irreversibly attenuates the bottom of the delta
> band before the file is written. We have flagged this repeatedly and never quantified it. A swept
> sine gives the exact attenuation at 0.5, 0.75, 1, 2 and 4 Hz, which is the number needed to decide
> whether to change the setting before the next long run.

## 2. Bill of materials

| item | note |
| --- | --- |
| function generator, sine and noise, 0.1 Hz to 1 kHz | a USB scope-generator or a phone DAC through a decent audio interface is adequate |
| **resistive divider, about 1000:1** | e.g. **10 kΩ in series with 10 Ω**, output taken across the 10 Ω. A 1 V output becomes ~1 mV, and 100 mV becomes ~100 µV |
| precision resistors for the impedance check | **100 kΩ**, **1 MΩ**, 1% or better |
| short screened leads, crocodile clips | keep leads short, this is a µV-level measurement |
| a spare headstage and adapter board | ⚠️ **never** the one on an animal |

> [!danger] 🛑 Bench only, never near an animal
> Nothing in this procedure goes anywhere near an implanted mouse. Injecting a driven signal into a
> connected animal is not a controlled exposure. Use a spare chain.
>
> ⚠️ The RHD2216 input range is **±5 mV**. Anything above that rails and the test is meaningless.
> Verify the divider output on a multimeter or scope **before** connecting the headstage.

## 3. The four tests

### 3.1 Amplitude accuracy

Inject a **10 Hz sine at a known amplitude**, target **200 µV peak to peak** after the divider.
Record 60 s. Run the normal pipeline.

**Pass:** recovered amplitude within **±10%** of the injected value, and rms consistent with a sine
of that amplitude (`rms = amplitude / √2`).

**If it fails:** the µV scale is wrong somewhere between the ADC and our analysis, and every
absolute number this project has published is affected.

### 3.2 ⭐ Frequency response, including the 1.10 Hz question

Inject a **constant-amplitude sine, stepped** through **0.5, 0.75, 1.0, 1.5, 2, 4, 6, 9, 15, 30, 60
and 100 Hz**, 60 s at each. Same amplitude at every step.

**Report:** recovered amplitude against frequency, normalised to the 10 Hz point. That is the
transfer function of the whole chain.

**Expect:** a roll-off below about 1.1 Hz and above about 475 Hz, matching the hardware bandpass.

**The number we want:** attenuation at **0.5 and 0.75 Hz**. If it is severe, the delta band we
report is being shaped by the filter and the setting should be revisited before the next long run.

### 3.3 Spectral slope recovery

Inject **synthetic noise with a known spectral slope** — pink noise is slope −1, brown noise is
slope −2. Both are generatable in one line.

**Pass:** the pipeline's measured slope over 1-30 Hz recovers the injected slope within **±0.2**.

**Why it matters:** the slope discriminator is what separates a real electrode from a wire-free
input, with working animals at −1.81 and −2.05 against a floor of −1.29 to −0.07. **If the measured
slope is biased, that entire classification is shifted.**

### 3.4 Impedance against a known resistor

Replace the electrode with a **100 kΩ** resistor between the input and ground, sweep, then repeat
with **1 MΩ**.

**Pass:** readings within **±20%** of the true value, with a phase near **0° or 180°**, that is,
purely resistive.

**Why it matters:** we have never checked the impedance measurement against a standard. It would
also calibrate the phase interpretation we adopted on 2026-08-07 — resistive near 0/180°,
electrode interface −20° to −60°, pure capacitance near −90°.

## 4. Acceptance criteria, fixed in advance

| test | pass |
| --- | --- |
| amplitude | within ±10% |
| frequency response | roll-off matches the stated 1.10 to 475 Hz hardware band |
| spectral slope | recovered within ±0.2 of injected |
| impedance | within ±20% of the resistor, phase near 0° or 180° |

**Any failure invalidates a class of published number, so record the result whichever way it goes.**

## 5. Roughly what it costs

Half a day of bench time and about £20 of parts, most of which the lab already has. No animals, no
anaesthesia, no rig downtime beyond the use of a spare headstage.

## 6. Why it is worth doing eventually

> [!quote] The argument in one line
> A pipeline that returned "no signal" for every input would pass **every control this project
> currently has**. The negative controls prove we do not hallucinate signal. Only a positive control
> proves we do not miss it.

Given that six of eight animals in the last cohort returned nothing, and that the failure was real
rather than analytical, that asymmetry has not yet cost us anything. **It would matter the moment a
result depends on an absence** — a genotype with less delta power, a drug that suppresses REM, any
claim of the form "this manipulation reduced X".
