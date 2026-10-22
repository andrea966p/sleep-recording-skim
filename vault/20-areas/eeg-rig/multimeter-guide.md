---
tags:
  - procedure
  - headstage
  - intan
  - grounding
  - onboarding
created: 2026-06-27
status: complete
---

# Multimeter Guide — Bench-Testing the Headstage Chain with the Harden 661002 DMM

> [!abstract] TL;DR — for non-technical readers
> **What this is.** The one place that explains how to use our digital multimeter (DMM) to check the recording rig: is the headstage getting power, is the animal-ground wire actually connected end-to-end, are any wires shorted together, and is the SPI connector intact.
>
> **Why it exists.** The DMM steps were scattered across three other guides and the bench journals. We kept re-deriving "which dial position, which jack, what reading means what." This page is the consolidated, do-it-the-same-way-every-time reference, with the exact expected numbers from our own bench logs.
>
> **How to read this page.** §1 = the meter itself (dial + jacks). §2 = which mode for which test. §3 = the four core tests with expected readings. §4 = the reading-interpretation table (the part you'll glance at most). §5 = safety. Big picture: [[nvr-system-overview]]. For *what to do* with the results, see [[signal-quality-and-grounding]] and [[first-headstage-connection]].

---

## 1. The meter — Harden 661002

| Item | Setting |
|---|---|
| Meter | **Harden 661002** (handheld DMM) |
| Black probe | plug into **`COM`** jack |
| Red probe | plug into **`VΩmA`** jack |
| Continuity / "beep" | dial at the **`•)))▶|`** position (just **right of `200`**, **left of `hFE`**) |
| Resistance (Ω) | the **Ω side** of the dial — use **`20k`** or **`2k`** ranges for our checks |
| DC volts | the **`V⎓` side** — use the **`20`** range for our ~3.5 V rail |
| AC volts | the **`V~`** section, only **`200`** and **`600`** ranges (product listing, checked 2026-10-02). On `200` the last digit is 0.1 V, so it cannot see anything under ~0.1 V AC: too coarse for a floating foil's pickup. Use the recording itself for that (µV resolution) |

> [!note] This meter is manual-ranging
> You pick the range. For a ~3.5 V reading use the **`20`** DC-volt range (not `2`, which over-ranges, and not `200`, which loses resolution). For a near-zero continuity resistance use `200` Ω or `2k`.

> [!warning] The decoupling-cap RC ramp — the #1 false alarm on this rig
> In **beep / resistance** mode, touching VDD↔GND (or any rail with a decoupling capacitor across it) makes the meter **briefly show a climbing number** as the cap charges through the meter — e.g. our headstages ramp **`15 → 17 → 1`** on the `20k` range, with **no beep**. **That climb is the cap charging, NOT a short.**
> - **Real short** = a steady **~0 Ω** *and* a **beep** that stays on.
> - **Real open** = the meter jumps straight to **`1`** (the over-range "open" indicator) with no ramp.
> - **Cap ramp** = a number that climbs then settles to `1`, **no beep** → this is NORMAL, not a fault.
> Confirmed identical on both headstages, 2026-06-26 and 2026-06-27.

---

## 2. Which mode for which test

| Test | Power state | Dial mode | Range |
|---|---|---|---|
| (a) **VDD↔GND power present** | headstage **powered / streaming** | **DC volts `V⎓`** | `20` |
| (b) **Ground-chain continuity** | **POWER OFF** | **beep `•)))▶|`** (or Ω) | beep / `200` |
| (c) **VDD↔GND short check** | **POWER OFF** | **resistance Ω** | `20k` |
| (d) **SPI adjacent-pin shorts** | **POWER OFF** | **beep `•)))▶|`** | beep |

> [!important] Volts = power ON. Resistance/beep = power OFF.
> DC-volts is the *only* test you do on a live rail. **Continuity and resistance inject the meter's own test current** — never do them on a powered circuit (you get garbage readings and can disturb the rail). See §5.

---

## 3. The four core tests

### (a) VDD↔GND power test — "is the chip getting its 3.5 V?"

The RHD2216 is **bus-powered over the SPI cable at +3.2 V to +3.6 V** (Intan *RHD SPI Cable* spec, p4 Table 1; "the RHD USB interface board and RHD recording controller provide a 3.5 V supply to their SPI ports," p5). No power on that line → the chip is dead → `priSigs=0`.

1. Dial → **DC volts**, **`20`** range. Black → `COM`, red → `VΩmA`.
2. Black probe → headstage **`GND`** pad; red probe → headstage **`VDD`** pad (both labelled on the RHD2216 board).
3. **Stream** in Allego (use **Stream**, not Record — Record fires a real session/video).
4. Read:

| Reading | Meaning | Action |
|---|---|---|
| **~3.2–3.6 V** (we measure **`3.57V`**) | chip IS powered | power is fine — look elsewhere (SPI signal, mode, etc.) |
| **~0 V** or **≪3 V** | bus power not reaching the chip | trace where it drops (measure power pin at the SAdpt SPI socket, then C3026 ends) |

> [!tip] Ignore the open-lead "phantom 3.3 V"
> This cheap meter **drifts near ~3.3 V on open DC leads** (probes touching nothing). The real datum is the value **on the pads**: it rests near 0 with probes apart and **jumps to `3.57V` on pad contact**. Disregard any floating reading taken in mid-air (this exact mistake was logged 2026-06-19).

> [!example] Bench history
> `3.56V` (2026-06-19) and `3.57V` (2026-06-26) at headstage VDD↔GND while streaming — top of the Intan 3.2–3.6 V spec, both headstages. Power has **never** been the fault on this rig.

### (b) Ground-chain continuity — "does the animal ground reach chip GND end-to-end?"

This is the test that matters most for signal quality. The animal-ground path is:

```
animal dura pin → tether GREEN wire → slip ring → brass busbar → 1 wire → C3410 `GND` pad → headstage chip GND
```

A break anywhere = the animal floats = **every channel rails at ~10–12 mV pk-pk** (see [[signal-quality-and-grounding]]).

1. **Power off.** Dial → **beep `•)))▶|`**.
2. Beep each link; each must **beep** (≈0 Ω):
   - C3410 `GND` pad ↔ headstage chip GND
   - C3410 `GND` pad ↔ the soldered GND socket pin (across the new solder joint — the prime cold-joint suspect)
   - busbar screw ↔ C3410 `GND` pad
   - tether green wire ↔ busbar screw
   - **end-to-end:** animal dura pin ↔ chip GND
3. **Wiggle test:** while probing a joint, gently flex the wire/socket. The beep must **stay solid** — flicker = a cold/intermittent joint (re-flow it).

> [!example] Bench history (2026-06-27)
> Full ground chain beeped end-to-end with a stable wiggle test → **no cold joint.** The 2026-06-26 cold-joint theory was killed by this test; the real cause was the **animal** having no ground tie (a missing electrode), not a broken system-side joint.

> [!warning] After a new slip ring, also verify the env-reference separation
> Beep tether green → busbar → `GND` → chip GND (must beep), and confirm the **copper coil → pad 6** is **NOT** continuous with `GND`, and that the **`REF` pad is unconnected** (we are bipolar). Full procedure: [[grounding-reference-noise-concepts]] §5.

### (c) VDD↔GND short check — "are power and ground shorted?"

1. **Power off.** Dial → **resistance Ω**, **`20k`** range. Probes on **`VDD`** and **`GND`** pads.
2. Read against the cap-ramp caveat:

| Reading | Meaning |
|---|---|
| climbs (e.g. `15 → 17`) then settles to **`1`**, **no beep** | **normal** — decoupling-cap RC charge, NOT a short |
| steady **~0 Ω** **+ beep** | **real short** — do not power up; find the bridge |
| straight to **`1`**, no ramp | open (expected for VDD↔GND with no path other than the cap) |

> [!example] Bench history
> Both headstages: `15 → 17 → 1` ramp on `20k`, identical, no beep → **no VDD↔GND short** (2026-06-26/27). A transient `575`/`5` seen in beep mode earlier was the same cap-charge artifact, not a short.

### (d) SPI connector adjacent-pin shorts — "are neighbouring SPI pins bridged?"

The headstage SPI connector is a **12-pin Omnetics PZN-12** (Intan *RHD SPI Cable* spec, p1, p3–4). Pins are in two rows, **T1–T6 (top)** and **B1–B6 (bottom)**. A solder splash or crush bridging two neighbours can corrupt SPI.

1. **Power off** (headstage unplugged from the bridge). Dial → **beep `•)))▶|`**.
2. Beep **adjacent** pin pairs along a row: T1–T2, T2–T3, … T5–T6 (and B-row if the pins are reachable).
3. **No beep = good** (neighbours isolated). **Beep = a short** between those two pins → inspect/clean/reject.

> [!note] Limits of this test on our rig
> The Omnetics pins are very fine (connector body ≈ 4.5 × 4.3 × 2.0 mm, *RHD SPI Cable* spec p3). On 2026-06-27 only the **top-row** neighbour pairs (T1–T6) were testable; bottom-row and cross-row pairs were too fine for the probe tips. Top row showed **no beep / no short**, and the gold pins were visually straight (no bend/burn/oxide).

> [!important] This test cannot prove a *signal-pin contact* fault
> A bent or recessed signal pin that still isn't *shorted* will pass this beep test but still fail to clock — that fault only shows under live SPI. For the "headstage not detected" case, the decisive test is the **socket-swap** at the XDAQ, not the DMM. See [[intan-headstage-troubleshooting]].

---

## 4. Reading-interpretation table (glance here)

| What the meter shows | In beep/resistance mode means | In DC-volts mode means |
|---|---|---|
| **Beep + steady ~0 Ω** | solid connection (continuity) **or** a short (depends what you're probing) | — |
| **Steady ~0 Ω, no beep** | low resistance, just below the beep threshold | — |
| **Climbing number, no beep**, settles to `1` | **decoupling-cap RC charge — NOT a short** | — |
| **`1`** (lone digit, left-justified) | **open circuit** (over-range / no path) | over-range — pick a higher range |
| **`OL` / over-range** | open / out of range | over-range — pick a higher range |
| **~3.2–3.6 V** | — | **bus power present and correct** (expect `3.57V`) |
| **~0 V on pads** | — | **no bus power** at that point |
| **~3.3 V with probes in mid-air** | — | **phantom open-lead drift — ignore** |

---

## 5. Safety & good practice

> [!warning] Power state matters
> - **DC volts** is the only mode you use on a **powered/streaming** rig.
> - **Continuity and resistance inject the meter's own current** → only on a **powered-off / disconnected** circuit. Doing them live gives false numbers and can disturb the rail.

- **Black = `COM`, red = `VΩmA`.** Never leave the red lead in a current jack for these tests.
- **Tin or fold fine tether wire** before clamping into the busbar so the screw bites — fine-gauge wire slips out and gives a false open.
- **Wiggle every joint** you beep; a connection that's good only at rest is a cold joint waiting to fail under the animal.
- Re-confirm the **`REF` pad stays empty** (bipolar RHD2216) and the **copper coil stays off `GND`** whenever you rework the ground.

---

## Related
- [[signal-quality-and-grounding]] — what the railing/floating signatures mean and how to fix grounding (the "why" behind test b)
- [[grounding-reference-noise-concepts]] — ground vs reference vs noise; the slip-ring color defect; DMM verification list (§5)
- [[first-headstage-connection]] — the original bring-up where the VDD↔GND `3.56V` reading was first taken
- [[intan-headstage-troubleshooting]] — symptom→cause→fix table that calls these tests
- [[rig-assembly-guide]] — the assembly procedure whose pre-power checklist uses test (b)
- [[2026-06-27]] · [[2026-06-26]] — the bench sessions these readings come from
