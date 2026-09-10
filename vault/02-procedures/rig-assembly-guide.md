---
tags:
  - procedure
  - headstage
  - intan
  - allego
  - grounding
  - onboarding
created: 2026-06-27
status: complete
---

# Rig Assembly Guide — Building the Recording Chain (Mouse → Allego)

> [!abstract] TL;DR — for non-technical readers
> **What this is.** A start-to-finish procedure for physically assembling the recording chain — from the mouse's electrode all the way to the XDAQ — in the right order, with the right orientations, and with the checks that must pass **before** you apply power.
>
> **Why it exists.** The bring-up log ([[first-headstage-connection]]) has all the parts and lessons but reads as a story, not a checklist. New operators need a clean "do this, then this" they can follow without re-reading the whole saga. Two mistakes have cost us days: a **missing animal ground** (animal floats → everything rails) and the **wrong Allego mode** (headstage reports 0 channels). This guide front-loads both.
>
> **How to read this page.** §1 = the chain and the parts. §2 = assemble in order. §3 = the ground bus (the part that's easy to get wrong). §4 = the pre-power checklist (do not skip). §5 = first power-on. Checks use [[multimeter-guide]]; the "why" is in [[signal-quality-and-grounding]].

---

## 1. The chain & the parts

```
mouse 4-pin dura electrode
        │  (colored wires)
        ▼
   tether (in-line epoxy connector)
        │
        ▼
   slip ring (rotary, 8-pin)
        │  (colored fan-out)
        ▼
   C3410 electrode adapter board  ── `GND` pad ◄── 1 wire ◄── brass busbar ◄── animal ground (green)
        │  (pads = native channel)         `REF` pad = EMPTY (bipolar)
        ▼
   RHD2216 headstage  (chip `intan RHD2216`)
        │  SPI (Omnetics PZN-12)
        ▼
   C3026 SPI interface cable (6 ft)
        │      [C3442 dual headstage adapter — only if 2 headstages on 1 cable]
        ▼
   SAdpt-XDAQ-OM12 bridge  (HDMI male → XDAQ ; 2× SPI female ← C3026)
        │  HDMI
        ▼
   XDAQ Core Gen-1  (Port 1 / front-panel HDMI)
        │  USB3
        ▼
   Allego  (mode = "XDAQ One (G1) with XR Headstage")
```

| Part | What it is |
|---|---|
| **C3410** | electrode adapter board — solder pads = native channels; has dedicated **`GND`** + **`REF`** pads |
| **RHD2216** | 16-ch **bipolar** headstage amplifier chip — bus-powered over SPI at 3.2–3.6 V |
| **C3026** | RHD SPI interface cable, 6 ft, Omnetics PZN-12 nano connector each end |
| **C3442** | RHD dual headstage adapter — lets **two** headstages share one SPI cable (optional) |
| **SAdpt-XDAQ-OM12** | bridge: HDMI male (→ XDAQ) + 2× Intan SPI female (← C3026) |
| **XDAQ Core Gen-1** | the DAQ (Opal Kelly USB `151f:0130`, serial `0C006218`) |
| **brass busbar** | 5-position grounding bar used as the star node for animal ground |

---

## 2. Assemble in order (electrode side → DAQ)

> [!warning] "Don't force" — every connector here is delicate
> Omnetics nano pins, fine tether wires, and the HDMI bridge all bend or crush if forced. If a connector resists, **stop, check orientation, and re-seat** — never push harder.

### Step 1 — Mouse electrode → tether
Mate the tether's in-line epoxy connector to the implant. Confirm the connector is fully seated and the keyed halves align. The 4-pin dura electrode carries: EEG pair, EMG pair, and (now standard) a **dedicated animal-ground pin** (see §3).

### Step 2 — Tether → slip ring (8-pin)
Our standard is the **8-channel slip-ring / 8-pin socket** (swapped in 2026-06-26). The slip ring lets the animal rotate without twisting wires.

> [!bug] Map by the wiring **table**, never by wire colour
> Tether and slip-ring use **different colour conventions** (e.g. tether `white` ↔ slip-ring `brown`; tether `peach` ↔ slip-ring `magenta`). These are **not errors** — match contacts by the wiring table in [[grounding-reference-noise-concepts]], not by colour name.

> [!bug] Known slip-ring defect — green↔orange swap (2026-06-27)
> The current resin-potted slip ring sends the tether **green (animal ground)** to a dead line (green/orange swapped on the slip-ring side) → **animal floats → railing returns.** It is **resin-potted → not re-pinnable → a new slip ring must be built** to the "how it should be" layout. Do **not** compensate at the busbar/tether end. Full detail: [[grounding-reference-noise-concepts]] §3.

### Step 3 — Slip ring → C3410 adapter board
The coloured fan-out lands on the C3410 solder pads. **Pad N = headstage native channel N** (identity). Record which pad each electrode wire is on — that is your signal map ([[signal-mapping-guide]]).

> [!important] `REF` pad stays EMPTY; `GND` pad is the anchor
> RHD2216 is **bipolar** — every channel is its own `+`/`−` pair, so there is **no reference electrode** (the `ref_elec` input only exists on the unipolar RHD2132). **Leave the C3410 `REF` pad unconnected.** Only the **`GND`** pad is used, fed from the animal-ground busbar (§3).

> [!tip] Reflow the C3410 before real recordings
> The electrode-side joints have shown bridges/icicles/cold joints. They don't affect detection but **wreck signal quality and risk shorts** — reflow and DMM-check (no bridge to `VDD`/`GND`) before recording.

### Step 4 — C3410 → RHD2216 headstage
Seat the headstage onto the adapter board's mating connector. Confirm full, even seating.

### Step 5 — Headstage SPI → C3026 cable
Plug the **C3026** into the headstage's **SPI** connector (the Omnetics PZN-12) — **not** the electrode connectors.

> [!note] SPI cable orientation is foolproof — by design
> The C3026 uses **self-aligning Omnetics PZN-12 polarized nano connectors; no guide pins required**, and signals pass straight through to an inverted connector at the other end. The cable is symmetric and **cannot be mis-mated** (Intan *RHD SPI Cable* spec, p1 Features; p4–5 Figs 5–8). Because of that flip, **wire colour is ambiguous** end-to-end — don't infer power/ground polarity from a wire colour (same doc, p5 Fig 8).

### Step 6 (optional) — C3442 dual headstage adapter
Only if running **two headstages on one SPI cable**. The C3442 lets two RHD chips share `CS`/`SCLK`/`MOSI` and splits the two `MISO` lines; plug the SPI cable into the **center** connector and a headstage on each **side** connector (Intan *RHD Dual Headstage Adapter*, p1–2).

> [!note] Termination — only matters on long cables
> Two headstages put their R1/R2/R3 100 Ω terminators in parallel → 50 Ω. Intan tested **6 ft with both headstages fine**; only **>6 ft** total needs the terminators removed from one board (same doc, p3). Our single bare headstage = correct 100 Ω → nothing to change. Do **not** confuse R1/R2/R3 with **R0** (the optional 0 Ω link that shorts the reference electrode to ground) — leave R0 alone.

### Step 7 — C3026 → SAdpt-XDAQ-OM12 → XDAQ
Plug the C3026 into one of the SAdpt's **SPI female** sockets, then the SAdpt's **HDMI male** into the XDAQ front-panel HDMI port. **Use Port 1** (other ports may be license/port-gated on a Gen-1 Core). Reseat the HDMI fully.

### Step 8 — XDAQ power & USB
Connect the **12 V USB-PD** supply (amber LED lit) and the **USB3** data cable to the host. The host must enumerate the device (`151f:0130`, USB SuperSpeed) — see [[xdaq-core-gen1-ubuntu-driver]].

---

## 3. The animal-ground bus (get this right or everything rails)

The amplifier input window is only **≈ ±5 mV**. If the animal's body is not tied to headstage ground, it **floats** and every channel slams the rails (~10–12 mV pk-pk). The ground path is:

```
animal dura pin → tether GREEN → slip ring → brass busbar (star node) → 1 wire → C3410 `GND` pad → chip GND
```

> [!important] The animal must carry the ground — not just the system
> Grounding the **busbar/headstage** is not enough; an **electrode must carry GND into the mouse.** Standard now (2026-06-27): a **spare dura-contacting skull pin → tether green → busbar → C3410 `GND`**. This is a **surgical requirement** for new implants — assign one spare dura pin as animal ground at implant time.

**Busbar build (star node):**
1. The 5-position brass bar is **one common node** (all screws bridged) — use it as a clean star hub, not as a way to separate mice.
2. Animal-ground wire(s) → end screws; **one** wire from the center screw → C3410 `GND` pad.
3. **Tin or fold** fine tether wire so the screw bites (it slips out otherwise).
4. Mount the busbar **close to the headstage** (short ground leads = smaller loop = less 60 Hz pickup).
5. Keep the bar **isolated** from other conductors (a stray short from the bar to a signal pad is bad).

> [!note] Two mice on one headstage share ONE ground
> The RHD2216 has exactly one ground. With two animals both greens land on the **same** busbar/`GND` net — there is no independent per-mouse ground without a second headstage. See [[signal-quality-and-grounding]].

The **copper tinned coil** (cable shield, cut at the mouse end) is an **environmental-noise reference**, not ground: it goes to **pad 6** (a recorded channel), **not** to `GND` ([[grounding-reference-noise-concepts]] §4).

---

## 4. Pre-power checklist (DO NOT SKIP)

> [!important] Beep before you power. Verify the mode after you power.
> Run all DMM checks **power off** first (procedures in [[multimeter-guide]]).

- [ ] **Ground continuity beeps end-to-end:** animal dura pin → tether green → busbar → C3410 `GND` → chip GND ([[multimeter-guide]] §3b). Wiggle-test each joint — must stay solid.
- [ ] **`REF` pad is unconnected** (bipolar).
- [ ] **Copper coil → pad 6**, and copper coil is **NOT** continuous with `GND`.
- [ ] **No VDD↔GND short** — resistance shows the cap RC-ramp (`15→17→1`, no beep), **not** a steady ~0 Ω + beep ([[multimeter-guide]] §3c).
- [ ] **No C3410 bridge** from a signal pad to `VDD`/`GND`.
- [ ] **SPI connector:** adjacent pins not shorted; gold pins straight, no bend/burn/oxide ([[multimeter-guide]] §3d).
- [ ] **C3026 seated on the SPI connector** (not the electrode connectors); **HDMI** fully seated; **Port 1**.
- [ ] **XDAQ powered** (12 V PD amber lit) and **USB3** enumerated on host.

---

## 5. First power-on & verify in Allego

1. **Set the Allego mode = "XDAQ One (G1) with XR Headstage"** (`XDAQ_ONE_REC`).

> [!warning] Wrong mode = false "0 channels"
> `SMARTBOX_PRO` connects and scans but reports **`priSigs=0`** with our hardware — it looks like a dead headstage but is just the wrong instrument profile. **Re-check the mode on every Allego relaunch** — it has silently reverted to `SMARTBOX_PRO` before. (Root cause of the entire 2026-06-18 false teardown — [[first-headstage-connection]].)

2. **Switching the mode resets the sample rate to 1000** — restore it to **`30000`** (30 kHz).
3. **Stream** (not Record — Record fires a real session + video). Confirm the port shows a channel count, e.g. Port D = 32, not 0.
4. Headless cross-check:
   ```bash
   /opt/neurosurveillance/venv/bin/python -c "from radiens import AllegoClient; print(AllegoClient().get_status().port_num_channels)"
   ```
   Expect e.g. `{<Port.D: 3>: 32}`, not `{}`.
5. Map channels ([[signal-mapping-guide]]), then judge signal quality ([[signal-quality-and-grounding]]) — stream **raw** first to confirm the railing is gone, then apply bandpass + 60 Hz notch + Paired Reference.

---

## Related
- [[first-headstage-connection]] — the original bring-up story + this rig's exact channel map
- [[multimeter-guide]] — the DMM checks referenced in §4 (continuity, short, power, SPI pins)
- [[signal-quality-and-grounding]] — grounding "why" + judging whether signal is good enough to record
- [[grounding-reference-noise-concepts]] — ground vs reference vs noise; slip-ring color defect; copper coil
- [[signal-mapping-guide]] — pad ↔ native ↔ `D/n` ↔ site mapping
- [[intan-headstage-troubleshooting]] — when assembly doesn't come up clean
- [[radiens-software-reference]] — Allego mode, sample rate, referencing (manual p70)
