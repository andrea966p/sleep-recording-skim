---
tags:
  - procedure
  - grounding
  - reference
  - noise
  - eeg
  - emg
  - headstage
  - onboarding
created: 2026-06-27
status: complete
---

# Grounding vs Reference vs Tissue Noise vs Environmental Noise — concepts + the slip-ring color defect

> [!abstract] Why this page exists
> These four words get mixed up constantly, and mixing them up has already cost us days (a "grounding" fix that was really a floating animal; a "reference" pad that our chip doesn't even use). This page nails each term, maps it to **our** rig (RHD2216 bipolar, single/2-mouse), and documents the **slip-ring color-swap defect** that currently sends the animal ground **into nothing**. Read [[signal-quality-and-grounding]] and [[signal-mapping-guide]] alongside this.
> Created 2026-06-27.

---

## 1. The four concepts, kept strictly separate

| Concept | What it physically is | Purpose | In OUR rig | If wrong |
|---|---|---|---|---|
| **Ground (tissue / animal ground)** | A **DC wire tie** from the **animal's body/dura** to the amplifier's **0V common** | Holds the whole animal inside the amp's tiny input window (≈ ±5 mV) so signals don't slam the rails | **GREEN** (animal ground) ← the **right parietal (caudal) dura pin** → slip-ring **GREEN** (ground-bus contact) → **brass ground bus** → C3410 `GND` pad → chip GND | Animal **floats** → **every channel rails** at ~10–12 mV pk-pk (the bug we chased 06-19 → 06-27) |
| **Reference — brain/biological** | A **tissue** point (e.g. cerebellar screw) that signals are measured **against** | Gives unipolar channels a baseline | **NOT USED.** RHD2216 is **bipolar**: every channel = its own **+ minus −** pair, so each pair self-references. C3410 **`REF` pad stays EMPTY** | Wiring a brain ref on a bipolar chip = pointless / confusing |
| **Reference — environmental (the copper coil)** | The tether cable's **shield / drain braid** ("copper tinned coil"). **Cut at the mouse end** → touches **no tissue** | Captures **ambient EM noise along the cable** so it can be drained or subtracted | **Copper tinned coil → pad 6** = a **recorded environmental-noise channel** (subtract in software later). **NOT ground, NOT a brain reference** | Confusing it with ground or brain-ref; soldering it to `GND` instead of pad 6 (different technique — see §4) |
| **Tissue noise** | Biological junk **from the animal** — EMG bleeding into EEG, movement artifact, ECG/heartbeat | — | Reduced by **paired/differential** recording (Paired Reference, manual p70) + good electrode placement | EEG contaminated by muscle, etc. |
| **Environmental noise** | **External** EM — 60 Hz mains hum, equipment EMI — picked up by leads acting as antennas | — | Reduced by **shield (copper coil)** + **60 Hz notch** + short/twisted leads + (ideally) a Faraday cage | Big 60 Hz sine burying the signal |

> [!important] The one sentence to remember
> **Ground = a DC tie that keeps the animal in range (green wire → bus → chip GND). Reference = a baseline you subtract against.** They are different jobs. Our bipolar chip needs **ground (green)** and uses **no brain reference**; the **copper coil** is an **environmental-noise reference**, a third, separate thing.

### "Reference" is two different things — do not merge them
- **Brain reference** (biological): a tissue electrode. **Unipolar** systems (RHD2132) need it. **We are bipolar (RHD2216) → we do not use one → `REF` pad empty.**
- **Environmental reference** (the copper coil): a **non-biological** line that records ambient EM so you can subtract shared noise. This is what the professor means by "connect the copper for environment noise / reference."

Same word, opposite origin (inside the animal vs. outside the animal). Keep them apart.

---

## 2. The DEFINITIVE plug map (2026-06-28)

Single source of truth = this table (**slip-ring colour → C3410 pad → signal**). The tether uses a **different** colour convention — **map by slip-ring colour + signal, never by tether colour name.**

| C3410 pad | Slip-ring colour | Signal |
|---|---|---|
| **0** | red | EEG frontal-L (`+`) |
| **1** | black | EEG parietal-L (`−`) |
| **2** | yellow | EMG L (`+`) |
| **3** | blue | EMG R (`−`) |
| **4** | brown | dura **frontal-R** (right-frontal cortex) |
| **5** | purple | **nothing** — spare line: soldered + resined to the strip & plugged to pad 5, but **no electrode behind it** (carries no signal) |
| **6** | orange | copper coil = **environmental-noise** reference |
| **`GND` bus** | green | dura **parietal-R** = **animal tissue ground** |
| **`REF`** | — | (empty) — bipolar → no brain reference |

> [!warning] Frontal/parietal corrected 2026-06-28
> Green = **parietal-R (caudal)** = animal ground. The right-**frontal** dura pin is the separate **brown / pad 4** line. Earlier tables had frontal/parietal backwards (and had ground on *orange*). Verify physically which right dura pin the green/ground wire sits on before powering.

- **Ground = slip-ring GREEN** → brass bus → C3410 `GND`. Carries dura parietal-R; does **not** go to a signal pad.
- **Pad 4 (brown) = dura frontal-R** = a real recorded right-frontal cortical channel (single-ended; see [§2.1](#21-what-the-brown--pad-4-dura-frontal-r-wire-is-for)).
- **Pad 5 (purple) = nothing.** Physically present (resined + plugged) but no electrode → it will **float / rail** → **deselect it, do not record.** It exists only to fill the strip position.
- **Pad 6 (orange) = copper coil** = environmental-noise reference ([§4](#4-the-copper-tinned-coil-environmental-reference--what-to-do-with-it)).
- **`REF` empty** (bipolar).

### 2.1 What the brown / pad 4 (dura frontal-R) wire is for

Slip-ring **brown → pad 4** = the **right-frontal dura pin** = a **real tissue electrode** (unlike the cut copper coil). Because green (its right-side partner) is consumed as ground, it can't form a right-hemisphere **bipolar pair** — so it's recorded **single-ended** on pad 4.

Use it as a **software re-reference / spare cortical trace**: record pad 4, then in Radiens **Paired Reference (manual p70)** optionally subtract it from the left EEG/EMG channels (a referential montage against right-frontal cortex).

> [!important] Pad 4 ≠ hardware `REF` pad
> Pad 4 is a **recorded channel** you re-reference **in software**. It is **NOT** wired to the chip's `REF` pad — that stays **EMPTY** (RHD2216 is bipolar). Three different "reference-ish" things, do not merge: **pad 4 (brown)** = optional biological re-ref (recorded); **copper coil (pad 6, orange)** = environmental ref ([§4](#4-the-copper-tinned-coil-environmental-reference--what-to-do-with-it)); **hardware `REF`** = unused.

### 2.2 Build / select notes

> [!danger] 🔴 CORRECTED 2026-08-03 — pads are NOT channels. Two pads make ONE channel.
> The two bullets below were written before the bipolar correction and are wrong
> in a way that matters. **You do not select pads in Allego — you select
> amplifiers**, and on the RHD2216 each amplifier consumes **two adjacent pads**
> as its `+` and `−` inputs (datasheet: *"16 amplifiers having independently
> accessible differential inputs (in0+, in0–, in1+, in1–, …)"*). The `+`/`−`
> labels already present in the §2 table are exactly that pairing.
>
> | pads | chip pins | amplifier | Allego | what it actually is |
> | --- | --- | --- | --- | --- |
> | **0, 1** | `in0+`, `in0−` | amp 0 | **`/1`** | **left EEG**, frontal-L − parietal-L — already bipolar |
> | **2, 3** | `in1+`, `in1−` | amp 1 | **`/2`** | **EMG**, L − R — already bipolar |
> | 4, 5 | `in2+`, `in2−` | amp 2 | `/3` | dura frontal-R vs **nothing** — half-open |
> | 6, 7 | `in3+`, `in3−` | amp 3 | `/4` | copper env-ref vs **nothing** — half-open |
>
> **Select `/1` and `/2` only** (plus `/33`, `/34` for the second animal on a
> splitter port). That is the entire montage in two channels.
>
> **Do NOT subtract anything in software.** The chip already did it.
> `0−1` and `2−3` are performed in hardware, before the ADC.

- ~~**Recorded pads = 0,1,2,3,4,6.** Pad 5 (purple) carries nothing → **deselect.** So the recorded set is non-contiguous (skips 5) → **select pads explicitly** in channel-select, don't rely on a contiguous range (see [[signal-mapping-guide]]).~~
- ~~Differential pairs in software: **0−1 = left EEG**, **2−3 = EMG**. Pad 4 (right-frontal) stands alone as the optional re-reference. Pad 6 (copper) = env-noise subtract.~~

> [!important] On THIS single-mouse 8-pin rig, `/3` and `/4` are HALF-wired, not empty
> ⚠️ **Scope: this applies to the single-mouse 8-pin configuration described on
> this page, NOT to the current 8-mouse rig.** On the 8-mouse rig only four
> electrode wires plus ground are fitted per animal, so `/3` and `/4` genuinely
> have nothing on either input — see [[eight-mouse-acquisition-setup]] §2, and the
> impedance sweeps confirm it (`/3`,`/4` read the same as the no-wire control).
>
> On the single-mouse rig with brown and orange fitted:
>
> - **Pad 4 (brown) is a real right-frontal dura electrode** on `in2+`, with
>   `in2−` (pad 5, purple) **open** → `/3` is a genuine brain electrode wired
>   against nothing, which is why it floats and rails.
> - **Pad 6 (orange) is the copper environmental-noise coil** on `in3+`, with
>   `in3−` open. Same situation.
>
> Neither is usable as-is: a differential amplifier with one open input produces
> noise regardless of what sits on the other input. **To use either, its negative
> input must be wired to something** — a second dura point for pad 5, or a local
> return for pad 7. Given that mains hum is our dominant problem, pairing the
> copper coil properly is worth considering for a future build.
- Ground (green) and `REF` are not recorded channels.

---

## 3. The defect — slip-ring green↔orange swap (animal ground → nothing)

In the [§2](#2-the-definitive-plug-map-2026-06-28) definitive map, **green = animal ground → brass bus → `GND`** and **orange = copper / environmental ref → pad 6**. The old (current) slip ring has the **green and orange contacts swapped**:

```
slip ring, should be:  green → ground bus,  orange → pad 6 (copper/env)
slip ring, current   : green → pad 6 line,  orange → ground bus   (swapped)
```

**Consequence:** the animal-ground **green** wire lands on the **pad-6 (env) line** — an amplifier **input**, not the ground bus — so the animal is never tied to `GND`. So:

> **The animal's tissue ground does not reach the ground bus → the animal floats → the railing comes back.** This is the exact failure mode from §1 row 1, re-introduced by a single mis-potted swap.

Everything else in the chain is correct. It is **one** swap, but it is the **ground**, so it is fatal (ground is physical — it cannot be patched in software/mapping).

### Why we can't just re-pin it
The slip ring is **resin-potted with its pins** → the wiring is permanent → **not re-pinnable.** 

**Fix = build a NEW slip ring**, resined to the full [§2](#2-the-definitive-plug-map-2026-06-28) plug map:
- **green → ground bus** (not the pad-6 line) — swap green↔orange back. This is the rail-fix.
- **orange → pad 6** (copper / environmental ref).
- **brown → pad 4** (dura frontal-R, recorded re-ref / spare — [§2.1](#21-what-the-brown--pad-4-dura-frontal-r-wire-is-for)).
- **purple → pad 5** (spare/nothing — still soldered + resined + plugged, but no electrode).
- red/black/yellow/blue → pads 0/1/2/3 unchanged.

> [!warning] Do not "fix" only one end later
> If anyone re-routes green/orange at the busbar/tether end to compensate, and *then* a corrected slip ring arrives, the two swaps stack and re-break the ground. The correct, permanent fix is **the new slip ring built to the §2 map**; leave the tether/busbar end matching the table.

---

## 4. The copper tinned coil (environmental reference) — what to do with it

- It is the tether cable's **shield**, and it was **cut at the electrode/mouse end** → it picks up **no tissue signal**, only **environmental EM** along the cable run.
- **Professor's instruction:** still connect it to a pin on the tether 8-socket (→ pad 6) — as an **environmental-noise / reference** line.
- So **copper coil → pad 6 = a recorded environmental-noise channel.** Later you can **subtract** it from the EEG/EMG channels in software (referencing, manual p70) to cancel shared ambient noise.
- **It is NOT:**
  - the animal ground (that's **green** → bus → `GND`), nor
  - a brain reference (bipolar chip → none).

> [!note] Two valid ways to use a cut shield — we use (a)
> **(a) Recorded reference (our choice):** shield → pad 6 amp input → record it → subtract in software. Gives a measurable env-noise trace.
> **(b) Passive shielding:** shield → `GND` → drains env noise to ground (no recorded channel).
> Per professor we do **(a)** (a pin on the socket = pad 6), not (b). Don't solder the coil to `GND` — that would merge it with the animal ground and lose the separate noise reference.

---

## 5. Verification (DMM, continuity/beep) after the new slip ring

Beep each path end-to-end, by the **table** (not colour):

- **green** (tissue ground) → slip-ring **green** → **ground bus** → C3410 `GND` → chip GND = **must beep** (this is the one that was broken).
- **brown** → C3410 **pad 4** = beep (dura frontal-R recorded channel present).
- copper coil → slip-ring **orange** → pad **6** = beep (env-noise reference present).
- spot-check signal pads: red/black/yellow/blue → C3410 pads 0/1/2/3 = beep.
- **purple → pad 5** = beep to pad 5 only (line present), but confirm **nothing else** hangs off it (no electrode) → it stays deselected.
- confirm copper coil (pad 6) is **NOT** continuous with `GND` (env reference must stay separate from animal ground).
- confirm pad 4 and pad 5 are **NOT** continuous with `GND` (they're inputs, not ground).
- confirm `REF` pad is **unconnected** (bipolar).

Then power: stream **raw** → railing should stay collapsed (see [[2026-06-27]] result: ch1 RMS 30 µV / SNR 11.7 when ground was good). Apply bandpass + 60 Hz notch + Paired Reference only after.

---

## 6. Action items

- [ ] **Build a new resin-potted slip ring** to the [§2](#2-the-definitive-plug-map-2026-06-28) plug map: **green → ground bus** (fixes the rail), **orange → pad 6** (copper/env). Current slip rings are unusable (green↔orange swap → animal ground floats).
- [ ] On the new build also resin + plug: **brown → pad 4** (dura frontal-R, recorded re-ref/spare) and **purple → pad 5** (spare line, no electrode → deselect); leave `REF` empty.
- [ ] DMM-verify per §5 before powering.
- [ ] Re-stream, confirm railing stays gone, then filter + evaluate.
- [ ] Carry the ground-electrode requirement into Tuesday's surgery (dura/bone pin → one tether pin as animal ground).

---

## Related
- [[signal-quality-and-grounding]] — grounding fix + how to judge signal (±5 mV rail, floating signature)
- [[signal-mapping-guide]] — pad ↔ native ↔ `D/n` ↔ site numbering
- [[intan-rhd2216-reference]] — chip reason `REF` is empty (bipolar; no `ref_elec` pin)
- [[multimeter-guide]] — how to run the §5 continuity checks
- [[rig-assembly-guide]] — where the ground bus + copper coil attach during assembly
- [[sleep-recording-operator-manual]] — full ordered workflow
- [[tsukuba-sleep-recording-method]] — ⭐ the published IIIS Tsukuba method our montage follows (bipolar left EEG, neck EMG, NO reference/cerebellum screw); validates this rig's design
- [[2026-06-27]] — the day the grounding root cause was found + this color defect documented
- [[2026-06-28]] — frontal/parietal correction + definitive plug map (brown→pad 4 recorded, purple→pad 5 nothing, green=ground, orange→pad 6); this page's §2
- [[radiens-software-reference]] — Paired Reference / referencing (manual p70)
