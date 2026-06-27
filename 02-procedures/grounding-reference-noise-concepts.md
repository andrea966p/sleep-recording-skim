# Grounding vs Reference vs Tissue Noise vs Environmental Noise — concepts + the slip-ring color defect

> [!abstract] Why this page exists
> These four words get mixed up constantly, and mixing them up has already cost us days (a "grounding" fix that was really a floating animal; a "reference" pad that our chip doesn't even use). This page nails each term, maps it to **our** rig (RHD2216 bipolar, single/2-mouse), and documents the **slip-ring color-swap defect** that currently sends the animal ground **into nothing**. Read [[signal-quality-and-grounding]] and [[signal-mapping-guide]] alongside this.
> Created 2026-06-27.

---

## 1. The four concepts, kept strictly separate

| Concept | What it physically is | Purpose | In OUR rig | If wrong |
|---|---|---|---|---|
| **Ground (tissue / animal ground)** | A **DC wire tie** from the **animal's body/dura** to the amplifier's **0V common** | Holds the whole animal inside the amp's tiny input window (≈ ±5 mV) so signals don't slam the rails | **GREEN** tether wire ← a **spare right dura pin** → slip ring → **brass ground bus** → C3410 `GND` pad → chip GND | Animal **floats** → **every channel rails** at ~10–12 mV pk-pk (the bug we chased 06-19 → 06-27) |
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

| Signal | Tether colour | Slip-ring colour | C3410 pad |
|---|---|---|---|
| EEG (frontal left) | red | red | 0 |
| EEG (parietal left) | black | black | 1 |
| EMG (left) | yellow | yellow | 2 |
| EMG (right) | blue | blue | 3 |
| dura pin (frontal right) | green | green | 4 |
| dura pin (parietal right) | **white** | **brown** | 5 |
| Reference — copper tinned coil | **peach** | **magenta** | 6 |
| **Ground bus** | — | **orange** | (ground net) |

- **white↔brown** (pad 5) and **peach↔magenta** (pad 6) are **NOT errors** — just different colour conventions between the two parts. Map them by the **table**, never by colour name.
- **GREEN = the tissue/animal ground line** in this scheme (tapped from a spare right dura pin, routed to the ground bus). Functionally it is the animal ground, even though the connector position is labelled "dura pin frontal right / pad 4." Treat green as ground.
- **ORANGE (slip ring) = the ground-bus line.** For the animal ground to reach the bus, the slip-ring **orange** contact must mate the tether **green** contact.

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

**Fix = build a NEW slip ring**, resined so that the **orange (ground-bus) contact aligns with the tether's GREEN** (tissue ground). I.e. swap green↔orange back to the "should be" layout in the new build.

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

- tether **green** (tissue ground) → **ground bus** → C3410 `GND` → chip GND = **must beep** (this is the one that was broken).
- copper coil → pad **6** = beep (env-noise reference present).
- spot-check signal pads: tether red/black/yellow/blue → C3410 pads 0/1/2/3 = beep.
- confirm copper coil is **NOT** continuous with `GND` (env reference must stay separate from animal ground).
- confirm `REF` pad is **unconnected** (bipolar).

Then power: stream **raw** → railing should stay collapsed (see [[2026-06-27]] result: ch1 RMS 30 µV / SNR 11.7 when ground was good). Apply bandpass + 50 Hz notch + Paired Reference only after.

---

## 6. Action items

- [ ] **Build a new resin-potted slip ring** with **orange (ground bus) aligned to tether green** ("how it should be" layout). Current slip rings are unusable (green↔orange swap → animal ground floats).
- [ ] On the new build, keep copper coil → pad 6 (environmental reference); leave `REF` empty.
- [ ] DMM-verify per §5 before powering.
- [ ] Re-stream, confirm railing stays gone, then filter + evaluate.
- [ ] Carry the ground-electrode requirement into Tuesday's surgery (dura/bone pin → one tether pin as animal ground).

---

## Related
- [[signal-quality-and-grounding]] — grounding fix + how to judge signal (±5 mV rail, floating signature)
- [[signal-mapping-guide]] — pad ↔ native ↔ `D/n` ↔ site numbering
- [[2026-06-27]] — the day the grounding root cause was found + this color defect documented
- [[radiens-software-reference]] — Paired Reference / referencing (manual p70)
