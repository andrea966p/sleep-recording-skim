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
| **Environmental noise** | **External** EM — 50 Hz mains hum, equipment EMI — picked up by leads acting as antennas | — | Reduced by **shield (copper coil)** + **50 Hz notch** + short/twisted leads + (ideally) a Faraday cage | Big 50 Hz sine burying the signal |

> [!important] The one sentence to remember
> **Ground = a DC tie that keeps the animal in range (green wire → bus → chip GND). Reference = a baseline you subtract against.** They are different jobs. Our bipolar chip needs **ground (green)** and uses **no brain reference**; the **copper coil** is an **environmental-noise reference**, a third, separate thing.

### "Reference" is two different things — do not merge them
- **Brain reference** (biological): a tissue electrode. **Unipolar** systems (RHD2132) need it. **We are bipolar (RHD2216) → we do not use one → `REF` pad empty.**
- **Environmental reference** (the copper coil): a **non-biological** line that records ambient EM so you can subtract shared noise. This is what the professor means by "connect the copper for environment noise / reference."

Same word, opposite origin (inside the animal vs. outside the animal). Keep them apart.

---

## 2. How this maps onto our wiring (the PDF "color" table)

Source of truth = the **table**, not the wire colours (tether and slip ring use **different colour conventions**):

| Signal | Tether colour | Slip-ring colour | C3410 dest |
|---|---|---|---|
| EEG (frontal left) `+` | red | red | pad 0 |
| EEG (parietal left) `−` | black | black | pad 1 |
| EMG (left) `+` | yellow | yellow | pad 2 |
| EMG (right) `−` | blue | blue | pad 3 |
| dura pin (**frontal right**) | **white** | **brown** | **pad 5** |
| dura pin (**parietal right**) — **ANIMAL GROUND** | **green** | **orange** | **ground bus → `GND`** |
| Reference — copper tinned coil | **peach** | **magenta** | pad 6 |

> [!warning] Frontal/parietal corrected 2026-06-28
> Earlier versions of this table had **green = frontal-R / white = parietal-R** — that was **backwards**. Bench truth (operator + [[2026-06-27]] root-cause: "tether green → right **caudal** dura pin"): **green = parietal-R (caudal)**, **white = frontal-R**. Green is the **animal ground**; white is the leftover right-frontal dura electrode. Verify physically which right dura pin green sits on before powering.

- **white↔brown** (pad 5) and **peach↔magenta** (pad 6) are **NOT errors** — just different colour conventions between the two parts. Map them by the **table**, never by colour name.
- **GREEN = the tissue/animal ground line.** It carries the right-parietal dura pin but is **repurposed as the animal ground**: it does **not** go to a signal pad — it routes to the **ground bus → `GND`**. For ground to reach the bus, the slip-ring **orange** (ground-bus) contact must mate the tether **green** contact (this is the [§3](#3-the-defect--slip-ring-greenorange-swap-animal-ground--nothing) defect).
- **WHITE (slip-ring brown) = the right-frontal dura electrode → pad 5**, recorded as a real tissue channel (see [§2.1](#21-what-the-white--brown-wire-is-for) below).

### 2.1 What the white / brown wire is for

White (tether) = brown (slip-ring) = the **right-frontal dura pin** = a **real tissue electrode** (unlike the cut copper coil). Because green (its right-side partner) is consumed as ground, white can't form a right-hemisphere **bipolar pair** anymore. We still **resin it into the new slip ring and plug it on pad 5**, recorded as a single-ended dura channel.

Use it as a **software re-reference / spare cortical trace**: record pad 5, then in Radiens **Paired Reference (manual p70)** optionally subtract it from the left EEG/EMG channels (a referential montage against right-frontal cortex).

> [!important] White ≠ hardware `REF` pad
> White-on-pad-5 is a **recorded channel** you re-reference **in software**. It is **NOT** wired to the chip's `REF` pad — that stays **EMPTY** (RHD2216 is bipolar). Three different "reference-ish" things, do not merge: **white** = optional biological re-ref (recorded, pad 5); **copper coil** = environmental ref (pad 6, [§4](#4-the-copper-tinned-coil-environmental-reference--what-to-do-with-it)); **hardware `REF`** = unused.

### 2.2 Adapter-board plug map — how the C3410 pads SHOULD be plugged

This is the "should-be" build target for the new slip ring + fan-out:

| C3410 pad | Plug in (tether / slip-ring) | Signal | Role |
|---|---|---|---|
| **0** | red / red | EEG frontal-L | `+` of left EEG (pair 0−1) |
| **1** | black / black | EEG parietal-L | `−` of left EEG |
| **2** | yellow / yellow | EMG L | `+` of EMG (pair 2−3) |
| **3** | blue / blue | EMG R | `−` of EMG |
| **4** | — | (empty) | green vacated here → now ground, not a signal pad |
| **5** | white / brown | dura frontal-R | recorded re-ref / spare EEG (single-ended) |
| **6** | peach / magenta | copper coil | environmental-noise reference |
| **`GND`** | green / **orange** | dura parietal-R | **animal tissue ground** (→ brass bus → `GND`) |
| **`REF`** | — | (empty) | bipolar chip → no brain reference |

- **Pad 4 ends empty** (green moved to the ground bus). Recorded pads are therefore 0,1,2,3,5,6 — non-contiguous, so **select them explicitly** in channel-select (don't rely on a contiguous range; see [[signal-mapping-guide]]).
- Differential pairs in software: **0−1 = left EEG**, **2−3 = EMG**. Pad 5 (right-frontal) stands alone as the optional re-reference. Pad 6 (copper) = env-noise subtract.

---

## 3. The defect — slip-ring green↔orange swap (animal ground → nothing)

Diffing the "current status" vs "how it should be" diagrams, the **only** difference is the slip-ring right column, bottom two positions:

```
slip ring, current  : … brown, blue, GREEN, ORANGE   (green & orange positions wrong)
slip ring, should be: … brown, blue, ORANGE, GREEN
```

**Consequence:** the tether **green (tissue ground)** no longer mates the slip-ring **orange (ground bus)** line — it lands on a line that **goes nowhere**. So:

> **The animal's tissue ground does not reach the ground bus → the animal floats → the railing comes back.** This is the exact failure mode from §1 row 1, re-introduced by a single mis-potted pin.

Everything else in the chain is correct. It is **one** swap, but it is the **ground**, so it is fatal (ground is physical — it cannot be patched in software/mapping).

### Why we can't just re-pin it
The slip ring is **resin-potted with its pins** → the wiring is permanent → **not re-pinnable.** 

**Fix = build a NEW slip ring**, resined to the full [§2.2](#22-adapter-board-plug-map--how-the-c3410-pads-should-be-plugged) plug map:
- **orange (ground-bus) contact aligns with the tether's GREEN** (tissue ground) — i.e. swap green↔orange back to the "should be" layout. This is the rail-fix.
- **brown (right-frontal dura) contact aligns with tether WHITE → pad 5** — resin and plug this line too (recorded re-ref / spare EEG, [§2.1](#21-what-the-white--brown-wire-is-for)).
- red/black/yellow/blue → pads 0/1/2/3 and magenta (copper) → pad 6 unchanged.

> [!warning] Do not "fix" only one end later
> If anyone re-routes green/orange at the busbar/tether end to compensate, and *then* a corrected slip ring arrives, the two swaps stack and re-break the ground. The correct, permanent fix is **the new slip ring built to the "should be" layout**; leave the tether/busbar end matching the table.

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

- tether **green** (tissue ground) → slip-ring **orange** → **ground bus** → C3410 `GND` → chip GND = **must beep** (this is the one that was broken).
- tether **white** → slip-ring **brown** → C3410 **pad 5** = beep (right-frontal dura channel present).
- copper coil → pad **6** = beep (env-noise reference present).
- spot-check signal pads: tether red/black/yellow/blue → C3410 pads 0/1/2/3 = beep.
- confirm **pad 4 is unconnected** (green moved to ground bus → pad 4 is now empty).
- confirm copper coil is **NOT** continuous with `GND` (env reference must stay separate from animal ground).
- confirm white (pad 5) is **NOT** continuous with `GND` (it's a recorded electrode, not ground).
- confirm `REF` pad is **unconnected** (bipolar).

Then power: stream **raw** → railing should stay collapsed (see [[2026-06-27]] result: ch1 RMS 30 µV / SNR 11.7 when ground was good). Apply bandpass + 50 Hz notch + Paired Reference only after.

---

## 6. Action items

- [ ] **Build a new resin-potted slip ring** to the [§2.2](#22-adapter-board-plug-map--how-the-c3410-pads-should-be-plugged) plug map: **orange (ground bus) aligned to tether green** ("how it should be" layout). Current slip rings are unusable (green↔orange swap → animal ground floats).
- [ ] On the new build, also resin + plug **brown (white tether / right-frontal dura) → pad 5** (recorded re-ref / spare EEG); keep copper coil → pad 6 (environmental reference); leave **pad 4** and `REF` empty.
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
- [[2026-06-27]] — the day the grounding root cause was found + this color defect documented
- [[2026-06-28]] — frontal/parietal correction + decision to record white on pad 5 (this page's §2.1/§2.2)
- [[radiens-software-reference]] — Paired Reference / referencing (manual p70)
