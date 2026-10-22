---
type: reference
area: rig-expansion
status: done
status-note: "open"
tags:
  - meeting
  - kontex
  - xdaq
  - acquisition
  - scale-up
  - call-prep
created: 2026-07-21
---

# Kontex Video Call Prep — KC Kong, 4 PM Today (2026-07-21)

> [!tip] Part of the rig expansion program
> Front door for all of this: **[[_rig-expansion-hub]]** (decision, vendor correspondence, wiring, open items).

> [!abstract] TL;DR — what this call is for
> You want a rig that records **16 mice at once** (and can grow to **32** later). Our current box (**XDAQ Core**) physically maxes out at **8 mice** — that is a hard wire limit, not a settings problem, so no adapter or trick fixes it. The plan is to buy a bigger box (**XDAQ ONE+** = 16), add **Port Expanders** for clean per-animal grounding, and later a second ONE+ + **SyncLink** for 32. Goal of the call: get **prices, a full parts list (quote), and confirm the Intan compatibility + PC/licensing questions** below. Prof. Kim Staci Jakyong is joining.

---

## PART 1 — Concepts so you can follow the call (plain-English)

Read this section once before the call. If KC uses one of these words, glance back here.

### What is the XDAQ?
The **XDAQ** is the data-acquisition box ("DAQ") — the hardware that reads the electrical signals off the mice and sends them to the PC. **Kontex** makes it. We already own the entry-level model, the **XDAQ Core** (Gen-1). Bigger models: **ONE+** (mid), **AIO** (top).

### What is a headstage?
A tiny amplifier chip that clips onto each mouse's implant and digitizes its brain/muscle signals. Ours is the **Intan RHD2216** (bipolar, 16-channel chip, but we only use ~4–6 channels: an EEG pair + an EMG pair). **One headstage = one mouse.**

### The ONE key fact that governs everything: "MISO lines"
- Each mouse's headstage needs its own private return wire to send data back. In this system that wire is called a **MISO line** (one physical twisted pair of wires).
- **1 mouse = 1 headstage = 1 MISO line.** Always. It does **not** matter that we only use 4 of the chip's 16 channels — the mouse still eats one whole MISO line.
- So the real question is never "how many channels" — it's **"how many MISO lines does the box have?"** That number = the max number of mice.

| Box | MISO lines total | **Max mice** |
|---|---|---|
| **XDAQ Core** (ours) | 8 | **8 — HARD limit, already full** |
| **XDAQ ONE+** | 16 | **16** |
| **2× ONE+ + SyncLink** | 32 | **32** |

> [!warning] Two "clever" ideas were already proven impossible — don't let the call re-open them
> - "Use the spare channels / a DDR trick to fit 16 on our Core" → impossible.
> - "A special 4-socket adapter to get 16 on the Core" → impossible (the missing wires literally don't exist on the Core).
> Both fail for the same reason: **you can't create MISO lines that the box doesn't physically have.** The Core is 8, period. The only way to more mice is a bigger box.

### The two accessories that matter
- **Port Expander (SAdpt-Port-EXP):** splits one port into up to 4 separate animal connections, and — the important part for us — gives **each mouse its own isolated ground and reference**. Without it, all the mice share one ground at the box, which can make them electrically interfere with each other. KC recommended this *unprompted*. This matters a LOT for us because we've been fighting **60 Hz hum / grounding problems** for weeks (the "EEG 60 Hz saga"). Clean per-animal grounding could directly help.
- **SyncLink:** a box that locks two (or more) XDAQs to the exact same clock so their recordings line up in time. Needed only for the 32-mouse (two-box) future.
- **SAdpt-XDAQ-OM12:** the little adapter that lets our **Intan** headstages plug into the **Kontex** XDAQ. This is our current bridge between the two ecosystems.

### Why we're staying with XDAQ (not switching to Open Ephys / Intan's own box)
All these systems use the *same* Intan chips, so our headstages work either way. But we already run the **XDAQ + Allego/Radiens** software, our channel maps, our analysis code, our written procedures. Staying on XDAQ ONE+ means **everything we've built carries over** — that's the reliability + reuse argument. Switching would throw that away.

---

## PART 2 — Where the plan stands (our decision going in)

- **16 mice → buy 1× XDAQ ONE+.** Native 16 headstages, stays in our existing software world.
- **32 mice (later) → 2× ONE+ + SyncLink** (shared clock).
- **Add Port Expanders** for independent per-animal ground/reference (crosstalk protection + helps our hum problem).
- **Do NOT** spend money on Core adapters/extra headstages hoping to reach 16 — the Core is maxed at 8.

We are NOT expecting to be talked out of ONE+. The call is about **pricing, exact parts, and closing the compatibility/logistics unknowns.**

---

## PART 3 — Questions to ask KC (in priority order)

### 🔴 Must-answer (these decide the whole purchase)
1. **Does the Port Expander work with our Intan RHD2216 headstages** (through the SAdpt-XDAQ-OM12 / Omnetics path), or only with Kontex's own "XR" headstages? — *The entire 4-animals-per-port + isolated-grounding benefit depends on this. If it's Kontex-XR-only, the plan changes.*
2. **Official quote for a 16-mouse ONE+ build.** Ask for the full bill of materials + price + lead time:
   - 1× XDAQ ONE+
   - Port Expanders (how many? one per port = 4?)
   - 16× Intan headstage interface adapters (SAdpt-XDAQ-OM12) + SPI cables
   - any commutators / slip-rings / tethers Kontex supplies
3. **A second XDAQ — does it need a second PC AND a second software license?** *(Their SyncLink docs say "each XDAQ → its own PC" — need this confirmed for cost + lab-space planning.)*

### 🟡 Important
4. **Port Expander price** (per unit) — flagged as our highest-value single item given the grounding history.
5. **32-mouse setup: one PC or two?** Can one PC host both Allego instances, and how do two linked units show up in Allego/Radiens?
6. **Does the top-tier AIO reach 32 mice in a single box** (more ports), or is 32 always two units? — *Might be simpler than two boxes + SyncLink; worth a price comparison.*

### 🟢 Nice-to-have / housekeeping
7. The **$75 custom re-routing adapter** KC offered earlier — now that we understand the Core is capped at 8, is there **any** real use for it in our setup, or should we drop it?
8. **Lead times** on ONE+, Port Expander, SyncLink (procurement planning).
9. Any **academic / multi-unit discount**?

---

## PART 4 — Facts to have on hand if KC asks

- **We own:** XDAQ **Core Gen-1**, currently running a validated **8-mouse rig** (all 8 MISO lines in use).
- **Headstages:** Intan **RHD2216**, bipolar, ~4–6 channels used per mouse (EEG pair + EMG pair).
- **Software:** Allego (acquisition) + Radiens/Videre, with our `sleep64` sensor map.
- **Our pain point:** ongoing **60 Hz hum / grounding** trouble at 8 mice — reason the per-animal isolation of the Port Expander is attractive.
- **New rig likely in a different building;** hardware video-sync is NOT part of this decision.
- Prof. **Kim Staci Jakyong** joining the call.

---

## PART 5 — During the call: capture these
- [ ] Prices: ONE+, Port Expander (×?), SyncLink, adapters/cables
- [ ] Confirmed answer on Intan RHD2216 + Port Expander compatibility
- [ ] Confirmed answer on 2nd PC / 2nd license
- [ ] Lead times
- [ ] Whether AIO can do 32 single-box
- [ ] Any next step KC wants (formal quote email, PO process)

## Related
- [[2026-07-21-acquisition-device-16-32-mice-and-kontex-thread]] — the decision + full email log
- [[intan-rhd-spi-wiring-and-headstage-limits]] — the physics (why 8 / 16 / 32)
- [[kontex-xdaq-hardware-reference]] — Kontex primary-source docs
- [[eeg-60hz-saga]] — grounding history (why per-animal isolation matters)

---

# PART 6 — DEEP TECHNICAL OVERVIEW (full reference, under your eyes)

> [!abstract] How this was built
> Four research passes (SPI wiring · connectors/chain · RHD2216 signal · noise/grounding) over the vault + the Intan datasheets in `06-references/datasheets/`, then cross-checked against the datasheet PDFs directly. Every hard number below is from the Intan RHD2000-series datasheet, the RHD SPI cable spec, or the vault's own measured values. Points where two vault sources disagree are flagged ⚠️ — raise them only if relevant.

## 6.0 The whole chain in one picture (mouse → PC)

```
mouse dura implant (EEG pair + EMG pair + 1 ground pin)
  → tether (custom cable)
  → SLIP-RING / commutator (8-pin rotary joint — lets mouse spin)      ← ANALOG here, most noise-sensitive
  → C3410 electrode adapter board (solder pads; GND + REF pads)
  → RHD2216 HEADSTAGE  ★ ANALOG → DIGITAL happens here ★
  → C3026 SPI cable (6 ft, Omnetics PZN-12 both ends)                  ← DIGITAL from here on, noise-immune
  → [C3442 dual adapter, if 2 headstages share one cable]
  → SAdpt-XDAQ-OM12 (SPI sockets → HDMI)
  → HDMI cable (carries SPI/LVDS, NOT video)
  → XDAQ Core Gen-1 (Opal Kelly 151f:0130)
  → USB3
  → PC → Allego / Radiens (records XDAT format)
```

> [!important] Correction to a common assumption
> The **slip-ring sits on the ANALOG side, BEFORE the headstage** — not on the SPI cable. The headstage lives at the top of the chamber with a ~36 cm analog run down to the animal, and the rotary joint is in that analog stretch. So the rotating joint carries fragile **microvolt analog** signals, which is exactly why it is the most noise-prone link. Everything AFTER the headstage is digital SPI and essentially noise-immune.

## 6.1 SPI — the digital layer, and why "8 mice" is a wire limit

**SPI = Serial Peripheral Interface**, a 4-signal digital bus. The XDAQ's FPGA is the master; each RHD headstage is a slave.

| Signal | Direction | Job |
|---|---|---|
| **CS** (chip-select) | master → chip | "start talking now" — pulled low to begin a data frame |
| **SCLK** (serial clock) | master → chip | the metronome; sequences 16-bit words |
| **MOSI** (master out) | master → chip | commands (which channel to sample, config) |
| **MISO** (master in) | **chip → master** | the digitized neural data coming back |

**The cable** (Intan RHD SPI cable spec, `datasheets/Intan_RHD2000_SPI_cable.pdf`): 12 conductors = **2 power/ground + 10 signal wires as 5 twisted LVDS pairs**. The 5 pairs are **CS, SCLK, MOSI, MISO1, MISO2**. Connector = self-aligning Omnetics **PZN-12** polarized nano (keyed, can't mis-mate). Supply 3.2–3.6 V (controllers give 3.5 V). Cable runs to several metres.

**LVDS** = Low-Voltage Differential Signaling: each signal travels as a *pair* of wires with opposite voltage; the receiver reads only the difference. Noise hits both wires equally → subtracts out. Twisting tightens the cancellation. This is why the SPI cable needs **no shielding** and survives metres of run — and why the digital half of the chain is immune to the 60 Hz problem that plagues the analog half.

**The one hard fact — 1 cable = exactly 2 chips:** CS/SCLK/MOSI are **broadcast identically** to both chips; but there are only **two return lines, MISO1 and MISO2** — one chip drives each. Two return wires = a hard ceiling of two chips per cable. The datasheet states it plainly: *"Number of Intan RHD2000 chips supported per cable = 2."*

**Why it is NOT a "DDR" trick:** DDR would mean cramming two chips onto ONE MISO wire by using both clock edges. Impossible here — MISO1 and MISO2 are **two physically separate twisted pairs**, each with its own 100 Ω termination resistor inside the FPGA. One chip = one physical wire. Nothing to time-share.

**C3442 Dual Headstage Adapter:** the little Y-board that realizes "2 chips per cable" — shares CS/SCLK/MOSI to both headstages, routes one chip's MISO to MISO1 and the other's to MISO2. Using it consumes **both** MISO lines of that cable — nothing spare left.

**Mapping to the boxes** (vendor-authoritative, from KC + NeuroNexus, matches our working 8-mouse rig):

| DAQ | MISO pairs / HDMI port | Chips/port | Ports | **Max mice** |
|---|---|---|---|---|
| **XDAQ Core** (ours) | 2 (MISO1/2) | 2 | 4 | **8 — HARD** |
| **XDAQ ONE/ONE+** | 4 (MISO1–4) | 4 | 4 | **16** |
| 2× ONE+ + SyncLink | 4 | 4 | 8 | **32** |

The Core's dead "top socket" is wired to **MISO3/MISO4 — wires that physically don't exist on the Core**. By design. Do NOT RMA (confirmed twice: NeuroNexus Jeff + distributor VIVO).

**Bandwidth is NOT our limit.** At our ~1 kHz × ~4 channels the data rate per mouse is ~16 kbit/s — trivial vs the chip's 30 kS/s × 16-ch ceiling (~16.8 Mbit/s). The constraint is wire count (MISO lines), full stop.

## 6.2 The RHD2216 chip — what it does to the signal

**"Bipolar" =** each of the 16 amplifiers has its own **+ and − input pair** and reports only the *difference*. Every channel carries its own reference (its − wire). **There is NO shared reference pin** on the RHD2216 — that's why the adapter's `REF` pad is empty by design. (Its unipolar siblings RHD2132/2164 DO have a common `ref_elec` pin; the 2216 does not.)

**Key specs** (Intan RHD2000-series datasheet, verified):

| Parameter | Value |
|---|---|
| Amplifiers | 16, differential +/− pairs |
| ADC | on-chip **16-bit**, LSB ≈ 0.195 µV at the electrode |
| Max sample rate | 30 kS/s per channel (1.05 MS/s aggregate MUX) |
| Midband gain | **192 V/V** (96 × 2) |
| DC gain | 0 — input caps block electrode DC offset |
| Input-referred noise | **2.4 µV rms** (the noise floor — nothing reads quieter) |
| AC input range ("the rail") | **±5.0 mV** datasheet ⚠️ (see flag) |
| Programmable high-pass (low cutoff) | 0.1 Hz – 500 Hz |
| Programmable low-pass (high cutoff) | 100 Hz – 20 kHz |
| CMRR @ 50/60 Hz | **82 dB — but only if the two electrodes are impedance-matched** |
| Input impedance | ~13 MΩ @ 1 kHz; input cap ~12 pF |
| Max SCLK | ~24 MHz (Intan spec; one extraction read 25 MHz — treat as approximate) |

**On-chip impedance measurement:** the chip injects a tiny known AC current into a chosen electrode through a selectable series cap (0.1/1/10 pF) and reads the resulting voltage → impedance = V/I. This is what Allego's **Impedance** tab does. Test current must stay small (amps saturate past the rail: 5 nA into 1 MΩ = 5 mV = right at the edge). The ~12 pF package cap (≈13 MΩ @ 1 kHz) biases *high*-impedance readings, so absolute MΩ on an already-open electrode is approximate — the good-vs-bad distinction still holds.
**⚠️ Allego gotcha: NEVER call impedance while streaming** — `GetIntanImpedance` during acquisition crashes allegoserver. Pause first.

**After the amplifier:** amplify → on-chip analog band-pass filter → 16-bit digitize → SPI serial stream → XDAQ → USB → PC. Digitizing *at the animal* (before the long cable) is what makes the system cable-noise-immune.

**Software (Allego/Radiens):** CAR (common-average reference) stays **OFF** for a bipolar montage. Notch set to **60 Hz** (Korea) — but notch runs *after* the amp, so it cleans the display but cannot un-clip a saturated leg. Lab processing order: **bipolar subtract → band-pass → decimate** (subtract common-mode hum first).

**What the signals look like** (why noise matters):

| Signal | Amplitude | Band |
|---|---|---|
| EEG | ~20–300 µV (sleep slow-waves higher) | delta ~0.5–4 Hz (NREM), theta ~4–8 Hz (REM); record ~0.5–30 Hz |
| EMG | ~10–50 µV rest, up to ~1 mV on movement | broadband, record ~10–300 Hz |

Real EEG (tens of µV) sits only ~10× above the 2.4 µV floor and can be 100–1000× *below* raw 60 Hz hum. That's the squeeze.

## 6.3 The 60 Hz noise mechanism — the heart of it

**The master equation the lab measured:**
```
differential_60Hz_at_amp  ≈  common_mode(mains floor)  ×  electrode_impedance_imbalance
```

- **Where hum comes from:** building wiring (220 V, **60 Hz** in Korea) radiates an electric field; every high-impedance electrode lead is an antenna. Coupling is **capacitive** (a tiny stray capacitance vs the amp's ~12 pF input cap forms a divider). A bare lead can pick up ~10 mV — ~1000× the brain signal.
- **Why bipolar SHOULD kill it:** the hum lands on both legs of a pair nearly equally (common-mode); subtracting the pair cancels equal things. CMRR = 82 dB **in theory**.
- **Why it doesn't (our problem):** that cancellation only works if the two legs are **impedance-matched**. Datasheet, verbatim: *"...best rejection of common-mode noise (most commonly 50/60 Hz) IF all electrodes are roughly the same impedance."* A mismatched pair converts common-mode INTO differential hum that no notch and no subtraction can remove.
- **Measured proof (mouse B1, same headstage/foil, electrodes mm apart):** frontal 7.641 MΩ → 4262 µV of 60 Hz; parietal 0.206 MΩ → 80 µV. A **~53× impedance ratio produced a ~53× hum ratio.** Not a hypothesis — a measured proportionality.

**Ground vs reference vs shield — three different things (constantly confused):**
- **Ground** = DC wire (dura pin → slip-ring → board `GND` → headstage) that keeps the animal inside the amp's ±5 mV window. Missing/open ground → animal floats → **every channel rails**. One per animal. A low-impedance ground also lowers the common-mode floor.
- **Biological reference** = what unipolar systems subtract against. **We don't use one** (bipolar chip, no ref pin).
- **Shield** (foil / Faraday) = intercepts the capacitive field. Separate job.
- **Rule:** ground the animal **only through the headstage** — a second animal-side ground to earth/rack/PC makes a ground loop and the hum returns.

**Shielding (foil):** wrapping the headstages in aluminium foil dropped single-ended 60 Hz pickup by up to ~450× (3604 → 8 µV) — the single biggest win. Mechanism: gives the coupling capacitance somewhere else to drain. **Foil stays ON but stays FLOATING** — grounding it was dropped 2026-07-16 (no headroom left; a global shield can't fix one open leg among balanced neighbours; Gen-1 Core has no chassis-ground terminal anyway). Foil blocks *electric* fields, NOT magnetic — magnetic fix is geometry: twist each +/− pair, keep the analog run short (applies only to the pre-headstage analog stretch).

~~**The root cause right now:** **every frontal EEG electrode is open on every mouse (3/3)** — 3.9–8.7 MΩ with nonphysical positive phase (a real electrode-tissue interface is capacitive → phase ≤ 0). An electrode floating in air reads 2.5–7 MΩ. Frontal and parietal are the same wire electrically, so the failure is **anatomical/surgical** — lead hypothesis: the **frontal sinus** (air cavity, pin lands in air). **Implants can't be reseated — you make new mice.** Surgical yield is the critical path, not electronics.~~

> [!danger] 🔴 RETRACTED — the premise, the hypothesis and the conclusion are all wrong
> - **There is no frontal-vs-parietal asymmetry.** That came from the wrong
>   channel map (corrected 2026-08-01). What fails is the **EEG channel `/1`**;
>   the **EMG channel `/2`** works on most animals.
> - **The frontal-sinus hypothesis was built entirely on the mis-mapping** and
>   has no evidence behind it. Drop it.
> - **"You make new mice" does not follow.** The high-impedance open-circuit
>   readings still stand, but Hsieh et al. (*eNeuro* 2024) report **82% of
>   epidural preparations lose ≥1 electrode within 3 weeks** — this is the known
>   baseline for the electrode type, not a surgical-skill problem. Their own fix
>   is a **different electrode design** (1.0 mm epidural, or MXene: 82% → 18%).
> - The free rig-side bench test has **still not been done**.
>
> See [[electrode-failure-and-impedance-literature]] and
> [[2026-08-03-two-8-mouse-runs]].

**Go/No-Go impedance gate (screen in Allego GUI BEFORE every run):** both legs 0.1–1 MΩ, phase ≤ 0, pair imbalance ≤ 2–3×, reject anything in the 2.5–7 MΩ floating band.

## 6.4 What the Port Expander actually fixes (honest)

**Helps:** gives each animal an **isolated, dedicated ground + reference** node, so on a shared 16-mouse box **one animal's noisy/open ground can't inject hum into the other 15**. It's also the mechanism that makes 16 animals on one ONE+ physically real (4 isolated animal ports per HDMI port). This is genuine scale-up value and why KC recommended it unprompted.

**Does NOT fix:**
- A single animal's **open frontal electrode** — that's surgical, internal to one animal. Isolation between animals does nothing for it.
- The **impedance-imbalance term** for any individual pair (our current binding problem).
- It does **not** replace foil shielding (different job).
- It is preventative for the scale-up, **not** a fix for a problem we have today at 1–2 mice (our floating rig was never the binding constraint; earth was exonerated).

**Bottom line:** ONE+ + Port Expanders are the correct *scaling* purchase. But no box upgrade produces sleep data while the frontal electrodes are open — clear that surgical gate in the next cohort regardless of which DAQ you buy.

## 6.5 ⚠️ Open discrepancies / confirm before quoting numbers
- **Amp rail: ±5.0 mV (datasheet) vs ±6.4 mV (our analysis code + 60Hz notes).** Both appear in the vault. Datasheet says ±5.0 mV; the ±6.4 mV may reflect a different gain/filter config. Confirm the effective saturation point in OUR Allego config before quoting a rail.
- **CMRR 82 dB** is the datasheet spec *under matched impedances* — do NOT quote it as our achieved rejection; ours is far lower because of the imbalance.
- **Max SCLK** ~24 MHz — one extraction read 25 MHz; approximate, not load-bearing for us.
- **16.8 Mbit/s per-chip** figure is derived arithmetic (1.05 MHz × 16 bit), not a quoted line.
- **Does the Port Expander's isolation actually drive Intan RHD2216 grounds** (vs Kontex XR only)? — unconfirmed; this is the #1 must-ask.
- **Frontal-sinus hypothesis** fits the pattern but is unproven at surgery.
- ~~**Still ZERO scoreable sleep recordings** — circadian test can't run meaningfully until frontal electrodes work.~~ ⚠️ **Superseded 2026-08-03:** we have **11.1 scoreable mouse-hours**, and the **circadian test has run and passed** on C1 (66.9 % asleep in the light phase vs a published ~70 %). The failing channel is the **EEG `/1`**, not "frontal electrodes" — that framing came from the wrong channel map. See [[2026-08-03-two-8-mouse-runs]].

## 6.6 One-line glossary
- **DAQ** — data-acquisition box (the XDAQ).
- **Headstage** — per-mouse amplifier chip (RHD2216).
- **SPI** — 4-wire digital bus chip↔box (CS/SCLK/MOSI/MISO).
- **MISO line** — one data-return wire = one chip = one mouse. The scaling limit.
- **LVDS** — differential signaling that makes the digital cable noise-immune.
- **CMRR** — how well a differential amp rejects shared (common-mode) noise; collapses if the electrode pair is impedance-mismatched.
- **Common-mode** — signal identical on both legs (e.g. mains hum); bipolar subtraction cancels it *if legs match*.
- **Port Expander** — Kontex accessory: 1 port → up to 4 isolated per-animal ports.
- **SyncLink** — locks 2+ XDAQs to one clock (for 32 mice).
- **Rail / clip** — signal exceeds the amp's ±5 mV window; those samples are lost, unrecoverable.
