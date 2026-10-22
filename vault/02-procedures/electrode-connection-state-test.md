---
tags: [procedure, eeg, emg, impedance, electrode-contact, signal-quality, qc, method]
created: 2026-07-31
status: active
priority: high
---

# How to tell OPEN from SHORTED from WORKING — the no wire control method

> [!warning] ⚠️ CHANNEL-MAP CORRECTION 2026-08-01 — this method is sound, but it was applied to the WRONG channels
> This page originally called sites `/1 /2 /3 /4` (and `/33-/36`) "the four mouse legs". **Wrong.** The RHD2216 is bipolar: **`/1` is the EEG and `/2` is the EMG, both already differential. `/3` and `/4` have no wire on them by design.**
>
> The method itself was RIGHT — and it is what exposed the error, because `/3`,`/4` matched the no-wire controls perfectly. They matched **because they ARE no-wire channels**. Apply the classifier to `/1` and `/2` only. See [[2026-08-01-channel-mapping-correction-first-sleep]].

> [!abstract] TL;DR — for non-technical readers
> **What this is.** A way to answer one question honestly: is this electrode actually connected to the mouse, or is it connected to nothing? For months we could not tell the difference, because a badly implanted electrode and a wire that is simply not attached produce almost the same number. See [[nvr-system-overview]] for the big picture.
>
> **Why it exists.** Every recording port contains spare amplifier inputs with no wire on them at all. Those spares are a free, perfect example of "not connected", measured by the same machine on the same day. Compare a real electrode against them and the answer stops being a guess. On 2026-07-31 this showed that most of our electrodes were reading exactly like nothing at all.
>
> **How to read this page.** The table in "The classifier" is the working tool. The two warning boxes are the mistakes that will fool you, and both of them fooled me first.

> [!quote] Paper-ready
> Electrode connection state was classified against an in situ open-circuit reference consisting of amplifier channels with unconnected headstage pads, measured in the same session on the same device. Legs whose impedance magnitude fell within the open-circuit reference distribution were classified as disconnected rather than high impedance, and channels with low impedance but no detectable physiological activity were classified as shorted; this three-state classification distinguishes acquisition-side connection failures from genuine electrode-tissue degradation.

> [!tip] THE WHOLE THING ON ONE CARD
> Every port already contains a **free, physically guaranteed open circuit**: the amplifier channels whose headstage pads have NOTHING attached. Measure those in the same session as your mouse legs, and you learn exactly what "no connection" looks like on this rig, that day, with that instrument. Then a leg is OPEN if it matches them.
>
> **Thresholds measured 2026-07-31:** Z > 0.9 MΩ = OPEN. Z 0.15 to 0.9 MΩ = connected. Z < 0.15 MΩ = SHORTED. **Confirm every "connected" leg with biology before trusting it.**

## Why this exists

For months this project read 5 to 8 MΩ on an electrode and called it "an open or high impedance electrode", which sounded like a surgical failure and drove a plan to make new mice. Nobody had ever measured what a channel with NO WIRE AT ALL reads on this hardware. On 2026-07-31 I did, and the answer was 5.233 MΩ, which is the same number. See [[2026-07-31-contact-intermittency-no-wire-control]].

## The three channel populations on every port

With the standard 64 channel per port setup (two RHD2216 headstages on a C3442 splitter):

| population | sites | what it is | how many |
| --- | --- | --- | --- |
| **REAL CHANNELS** | **1, 2 and 33, 34** | **`/1`=EEG, `/2`=EMG (both already bipolar)** | **4 per port** |
| ~~"legs" 3, 4, 35, 36~~ | 3, 4, 35, 36 | ⚠️ **EMPTY PADS, NOT ELECTRODES** (corrected 2026-08-01) — treat as extra no-wire controls | 4 per port |
| **CONTROL A, NO WIRE** | 5 to 16, 37 to 48 | real amplifier channels, pad present, nothing soldered to it | 24 per port |
| **CONTROL B, TIED** | 17 to 32, 49 to 64 | the internally tied empty half of each RHD2216 | 32 per port |

With ONE headstage per port and no splitter (32 channels per port), the same logic holds on sites 1 to 4, 5 to 16 and 17 to 32.

⚠️ **CONTROL A is the useful one.** It is an open circuit by construction. Control B is internally tied and tells you something different, namely whether the amplifier and the animal ground are healthy.

## Reference values, measured 2026-07-31

| population | Z median | mains 55 to 65 Hz |
| --- | --- | --- |
| CONTROL A, no wire | 5.233 MΩ (p10 1.85, p90 7.60) | 2400 µV |
| CONTROL B, tied | 0.043 MΩ | **7.2 µV** |

**Control B at 7.2 µV is the amplifier noise floor of this rig, and it doubles as the animal ground check.** Per headstage medians on 2026-07-31 were 7.0, 6.5, 7.3, 8.3, 7.7, 7.2, 6.5, 7.1, so all 8 animals were correctly grounded. A headstage whose floor channels rail instead means THAT mouse's ground is not made.

## The classifier

| state | Z | mains | biology (delta 0.5 to 4 Hz) |
| --- | --- | --- | --- |
| **OPEN**, acting as an antenna | **> 0.9 MΩ** | 500 to 8000 µV | none |
| **SHORTED** to ground | **< 0.15 MΩ** | 7 to 146 µV | **none** |
| **WORKING** | **0.15 to 0.9 MΩ** | 13 to 61 µV | 68 to 91 µV |

> [!warning] TWO TRAPS THAT WILL FOOL YOU
> **1. A SHORTED leg looks QUIETER than a good one.** `A1 parietal` at 0.087 MΩ, `C2 parietal` at 0.139 MΩ and `D1 parietal` at 0.335 MΩ all had less hum than C1's working legs, and all three were dead. **Low hum is NOT proof of a good channel. Always check that biology is present.**
>
> **2. DO NOT use the impedance PHASE.** It is not reproducible between runs on this rig. Same legs, same physical state, phase went 140.4° → 33.3°, 36.4° → 140.1°, 144.7° → 17.5°, 172.1° → 11.3°. **Use magnitude alone.**

> [!danger] ⚠️ THE SHORTED TRAP CAUGHT US A SECOND TIME (2026-08-01) — hum alone CANNOT select scoreable windows
> On 2026-08-01, C2 looked "connected" (low hum) at 18:00-19:00 and 05:21-05:57 and was nearly scored as light-phase data. Those windows are **SHORTED**:
>
> | C2 window | EEG rms | apparent WAKE | persistence @1 min |
> | --- | --- | --- | --- |
> | genuinely working | **68.7 µV** | 34.1 % | **+0.747** |
> | shorted | 20.9 µV | 99.7 % | −0.003 |
> | shorted | 16.1 µV | 99.8 % | −0.002 |
>
> **GATE SCOREABLE WINDOWS ON THREE THINGS, NOT ONE:**
> 1. low mains (not open), **AND**
> 2. **EEG rms in the physiological range (~50-90 µV here; <25 µV means dead)**, **AND**
> 3. **temporal structure present** (sleep/wake persistence r ≫ 0 at 1 min).
>
> A dead channel scores as ~100 % WAKE with no persistence. That is the tell.

## How to measure the hum correctly

⚠️ **Use the 55 to 65 Hz BAND power, NOT a single 60.00 Hz FFT bin.** Mains is not exactly 60.00 Hz and it drifts, so the energy smears across neighbouring bins. Reading a single bin understates the hum by 4 to 5×. I made this mistake on 2026-07-31 and had to correct it mid analysis.

## Things confirmed about the instrument

- **The Allego notch filter does NOT reach the saved data.** Verified 2026-07-31 by parking the notch at 50 Hz, where nothing real lives, and checking the saved spectrum. 1 Hz bins across 47 to 53 Hz came out 2.457, 2.504, 2.354, 2.401, 2.365, 2.462, perfectly flat, no null. The `.xdat` primary data is RAW, hardware bandpass only. The notch is display side.
- **This is a useful trick in general:** to test whether any display filter touches the data, park it on a frequency where nothing real lives and look for the null.
- Units are `micro-volts` for primary channels, per the file metadata. **The rail is 6389.6 µV = `0.195 µV/LSB × 32767`, the 16-bit ADC full scale.** Confirmed by direct measurement 2026-08-03: `max|sample|` is 6389.8 µV, identical to four significant figures on all 8 channels. Use **6376.8 µV (99.8% of full scale)** as the clipping threshold; the older ±6300 figure was a guess that happened to be safe.

> [!note] Every sweep we have taken is catalogued in [[impedance-sweep-register]]
> Files were renamed 2026-08-03 so the name carries the date, time,
> configuration and which run it brackets. The pre-run-1 sweep is the **17:34**
> file, not the 17:51 one, which was taken in a different configuration.

## 🔴🔴 WE HAVE ONLY EVER MEASURED HALF OF EACH ELECTRODE PAIR — found 2026-08-03

> [!danger] Every impedance number in this project is one input of a two-input pair
> The RHD2216 is bipolar: each amplifier has **two independent electrode pins**,
> `inX+` and `inX−`. Both are real electrodes in the animal. The signal is their
> difference.
>
> **The chip CAN measure them separately.** Datasheet Register 5 has a dedicated
> bit, `Zcheck pol sel`:
>
> > "The RHD2216 has two independent input pins for each amplifier, so an extra
> > register called **Zcheck pol sel** is provided to select between the positive
> > and negative amplifier input pins during electrode impedance testing. When
> > Zcheck pol sel is set to zero, Zcheck en connects the on-chip current
> > generator and elec_test to the **positive input terminal (inX+)**… When set to
> > one, the impedance testing circuitry is connected to the **negative input
> > terminal (inX−)**."
>
> **Radiens does not expose it.** Checked exhaustively 2026-08-03 across four
> independent sources — the installed `radiens` package, the Radiens Technical
> Documentation PDF, the online `radiens-core` API reference, and the
> **`radiens-core` 0.0.8 wheel source itself**:
>
> ```python
> # radiens_core/_converters/_impedance.py
> ImpedanceRequest(port=port_to_proto(p))            # port is the ONLY field
>
> # radiens_core/models/impedance.py
> class ImpedanceValue(BaseModel):
>     ntv_chan_idx: int
>     magnitude_ohm: float
>     phase_deg: float                                # three fields. no polarity.
>
> # radiens_core/allego_client.py
> def get_intan_impedance(self, port: FlexPort) -> Impedance:   # the ONLY impedance method
> ```
>
> - **One impedance method on the whole `AllegoClient` surface**, and it takes a
>   port and nothing else.
> - **No polarity field** anywhere in the request, the response, or the protobuf.
> - **No Intan register-write path at all.** The only register methods
>   (`load_all_mosi`, `transmit_mosi`, `read_wire_out`, `flash_sinaps`) are
>   **Sinaps-probe specific** and cannot reach the RHD chip. There is no back door.
> - The GUI Impedance tab offers only Magnitude / Phase / Run.
>
> With the chip default being `pol sel = 0`, our readings are **the positive
> input, and the negative electrode of every pair has never been measured.**
>
> *(Inference level: it is **proven at source level** that Radiens offers no way
> to select, set, or distinguish polarity, and no way to reach the register. That
> the reported value is specifically `inX+` follows from the chip default and is
> very likely, but is not separately confirmed — it could in principle be a fixed
> choice of `inX−`. Either way we see exactly one of the two electrodes.)*

### Which electrode, specifically, each number refers to

Combining the pad map ([[grounding-reference-noise-concepts]] §2) with
`pol sel = 0`:

| Allego channel | amplifier | impedance number is | **never measured** |
| --- | --- | --- | --- |
| **`/1`** ("EEG") | amp 0 | **EEG frontal-L** (pad 0, `in0+`) | **EEG parietal-L** (pad 1, `in0−`) |
| **`/2`** ("EMG") | amp 1 | **EMG L** (pad 2, `in1+`) | **EMG R** (pad 3, `in1−`) |

So "the EEG impedance was 6.7 MΩ" has always meant **the frontal electrode
specifically**, and the parietal electrode on the other half of the same
amplifier has never been measured once.

> [!note] This probably reconciles the old "frontal open, parietal fine" observation
> Earlier work reported frontal legs at 3.9–8.7 MΩ while "parietal on the same
> wire" read 0.2–1.1 MΩ, and built the frontal-sinus hypothesis on it. Under the
> corrected map those two numbers are far more likely to have been **`/1` and
> `/2`** — i.e. the **EEG amplifier's `+` input vs the EMG amplifier's `+`
> input** — mislabelled as frontal vs parietal by the wrong channel map.
>
> That is exactly our current finding stated in different words: **EEG open, EMG
> working.** Same data, same rig, wrong labels. Strong inference, not proven —
> but it removes the last piece of evidence that ever supported the frontal-sinus
> story.

### Why this matters more than it sounds

**It explains our biggest anomaly.** B1's EEG read **0.133 MΩ** before Run 2 — the
best EEG impedance in the fleet — and then ran fully open, 2802 µV hum, for all
21.7 h. If that number is `inX+` only, then `inX−` could have been open the whole
time and the sweep would look perfect. **A differential amplifier with one open
input produces exactly what we saw.**

**It means we have never been able to compute the quantity that actually predicts
hum.** Our own relation is `differential_60Hz ≈ common_mode × electrode_Z_imbalance`
— an *imbalance* between the two inputs. We have only ever seen one of them, so
the imbalance has never been measurable. That is a large part of why impedance
predicted class but not yield.

### How to actually see both electrodes

| method | cost | what it gives |
| --- | --- | --- |
| **DMM at the C3410 pads, each pad vs the animal `GND` pad** | **free, no animal contact** | DC continuity per **individual** electrode, including every negative one. Not 1 kHz Z, but decisive for open vs connected — which is our whole question |
| **Ask NeuroNexus/Kontex to expose `Zcheck pol sel`** | one vendor email | proper per-electrode 1 kHz Z. **It is a single register bit they already drive**, and the API has no way to reach it — this is a genuine feature gap, not a usage error on our side. Worth raising on the Kontex thread |
| Check whether the Open Ephys GUI exposes polarity | an afternoon | unverified — worth testing, OE drives the same chip |
| Temporarily rewire a suspect electrode onto a positive pad | bench work | per-electrode Z for one channel at a time |

> [!important] This raises the value of the tier-1 bench test
> The DMM check was already the cheapest action available. It is now also the
> **only way we currently have to see the negative electrodes at all.** Probe each
> C3410 pad against the animal ground pad and record continuity per pad.

## ⚠️ IMPEDANCE PREDICTS CLASS, NOT YIELD — narrowed 2026-08-03

> [!warning] The ρ = −0.941 result below did NOT replicate. Read this box before the one under it.
> The claim "impedance predicts hours-of-usable-data" was fitted on a single
> recording (2026-07-31) and **pre-registered against Run 2 (2026-08-02), where
> it scored 4 HIT / 3 MISS / 1 VOID**. Every hit was *which channel is connected
> on which mouse*; every miss was *how many usable hours you get*. On Run 2 the
> yield correlation was **ρ = −0.452**, not −0.941.
>
> **The decisive counterexample:** B1 read **0.133 MΩ** before Run 2 — the best
> EEG impedance in the entire fleet — then ran at 2802 µV hum, fully open, for
> all 21.7 h. Resting impedance is not contact under load.
>
> **Second, harder limit — now checked against six primary papers (2026-08-03).**
>
> | source | electrode | impedance @ 1 kHz |
> | --- | --- | --- |
> | Choi 2010 | skull screw | < 100 kΩ (at 30 Hz) |
> | Hsieh 2024 | epidural 0.1 mm / MXene, in use | 10–29 kΩ |
> | Kim 2022 | stainless screw 0.8 mm | 10–50 kΩ |
> | Kim 2022 | HD contact, chronic | ~100 kΩ |
> | **ours, best in fleet** | dura pin | **73 kΩ** |
> | **ours, C1 (our best animal)** | dura pin | **465 kΩ** |
>
> **Our single best channel sits at the literature's worst acceptable value, and
> everything else is worse than anything published.** So `Z < 2 MΩ` is roughly
> **40× looser than the published norm** — it is an **open-circuit detector, not a
> quality bar**. A channel at 0.5–2 MΩ is a poor electrode that merely is not
> fully open, and calling it "CONNECTED" oversells it.
>
> ⚠️ **Do not cite Kappenman & Luck 2010 in support of our hum-vs-contact
> result.** They found *no* detectable effect of impedance on 60 Hz line noise —
> but they compared 5 kΩ vs 50 kΩ (two connected electrodes) in a well-shielded
> room, and say so explicitly. We are comparing connected vs **open circuit**, a
> different regime. Our bimodal 9–90 µV / 1000–4700 µV separation is our own
> empirical finding, not a replication of theirs.
> Full evaluation: [[electrode-failure-and-impedance-literature]].
>
> **What to use it for:** deciding which animals are worth running, and which
> channel to expect signal on. **Not** for forecasting yield, and never as
> evidence that an electrode is good.

> [!success] REVERSED. The earlier "impedance is useless" verdict was an artifact of the WRONG CHANNEL MAP.
> *(Kept for the reasoning and the sweep data. The yield claim in it is narrowed by the box above.)*
> Re-read against ground truth from the 27.9 h recording, using only the REAL channels (`/1`=EEG, `/2`=EMG) and ignoring the empty pads `/3`,`/4`:
>
> **Spearman ρ = −0.941, p = 5.7e-08** between impedance magnitude and hours-of-usable-data — from a sweep taken ~2 h BEFORE the recording began.
>
> | threshold | classification accuracy |
> | --- | --- |
> | Z < 0.9 MΩ | 13/16 |
> | **Z < 2.0 MΩ** | **14/16** |
> | Z < 3.0 MΩ | 14/16 |
>
> **USE Z < 2 MΩ = CONNECTED, Z > 3 MΩ = OPEN, on sites `/1, /2, /33, /34` only.** A mouse needs BOTH `/1` and `/2` under threshold to be scoreable.
>
> ⚠️ 2026-08-03: "CONNECTED" here means **not open**, not **good** — see the
> narrowing box above. The rule held up as a *classifier* on Run 2 (C1 was the
> only mouse with both channels connected, and the only one that produced
> defensible sleep), but it does **not** predict how long that lasts.
>
> **The classification is STABLE across repeat sweeps even though the values wobble:**
> ```
> B1 EEG   0.222 -> 0.623  (2.8x)   CONN -> CONN   STABLE
> B1 EMG   0.329 -> 0.026  (0.08x)  CONN -> CONN   STABLE
> pad /3   5.380 -> 3.626           OPEN -> OPEN   STABLE
> pad /4   8.140 -> 4.887           OPEN -> OPEN   STABLE
> ```
> Even the notorious **102× swing was real information**: that channel was B2's EMG, and B2's EMG worked only 1.4 h out of 27.9 h in the recording. The sweep was correctly flagging a FLAKY channel; it was misread as instrument noise.
>
> **Independent confirmation of the bipolar map:** empty pads `/3,/4` median **5.902 MΩ** vs no-wire control **5.557 MΩ** — statistically identical. The impedance data independently says those pads have no wire.

### ⚠️ What still holds
Read only `/1, /2, /33, /34`. Including the empty pads `/3, /4` in any impedance summary is what made the measurement look worthless — half the "electrodes" being scored were bare pads. Values still wobble severalfold between sweeps, so **classify, do not quote the number**; and a channel whose CLASS flips between back-to-back sweeps is genuinely intermittent, which is itself the finding.

## ~~Impedance snapshots are not a go or no go gate~~ (SUPERSEDED, see above)

Contact state on this rig FLIPS ON ITS OWN. Documented instances: one leg moved 102× in eleven minutes, another stepped 522× in 0.5 seconds mid recording with nobody touching the rig, a third collapsed 64× over an hour.

**If you use impedance at all, take three measurements back to back without touching anything and read the VARIANCE, not the value.** A leg that moves between runs is not a leg you can score, whatever the number says.

## The wiggle test, for localising a mechanical fault

Provoke one joint at a time while streaming, and watch the 55 to 65 Hz envelope.

**⚠️ CONTROL FOR YOUR OWN BODY FIRST.** A bare finger near the tether is a 60 Hz antenna and will swing the hum whether or not the contact is bad. Wear nitrile gloves, or provoke with an insulated tool such as plastic tweezers or a wooden stick. Record a "hand held 2 cm away, no contact" baseline first, and treat anything smaller than that as noise.

**Protocol per joint:** 5 s quiet, about 5 s perturb, then 10 s quiet. The 10 s AFTER release is where the answer lives.

Order: hand near with no contact, head connector, tether near the head, tether mid span, slip ring, headstage body. About 2 minutes per mouse, so record one file per mouse.

**Reading it:**
- **TRANSIENT**, hum rises during the touch and returns on release → body coupling, IGNORE.
- **STEP**, level changes and STAYS changed after release → contact state change, this is the finding.

**The untouched mice are your best control.** On 2026-07-31, provoking C1 left A1 and D1 completely unmoved (A1 frontal held 5711 to 6250 µV, D1's EMG legs pinned to within a few µV), which proved the setup is not cross coupled and that no global artifact was in play.

## Related

- [[2026-07-31-contact-intermittency-no-wire-control]] — the decision doc this method came out of
- [[60hz-mains-hum-discovery]] — Korea mains is 60 Hz
- [[floating-cm-vs-contact-reconciliation]] — the common mode × impedance imbalance equation
- [[signal-quality-and-grounding]] — is the signal good enough to record
- [[eight-mouse-acquisition-setup]] — the port and site layout these populations come from
