---
tags: [procedure, eeg, emg, signal-quality, shielding, faraday, mains-hum, 60hz, critical, discovery]
created: 2026-07-15
status: active
priority: critical
---

# ⭐🎉 Headstage shielding (Faraday foil) — the intervention that produced the first real sleep signal

> [!abstract] TL;DR — for non-technical readers
> **What this is.** On 2026-07-15 we wrapped the Intan headstages in ordinary aluminium kitchen foil. The 60 Hz mains interference on the electrodes collapsed by up to a hundredfold, and for the first time in the project's history a recording contained genuine, measurable mouse sleep. This page is what we did, why it works, and how to do it properly (we did it badly and it still worked).
>
> **Why it exists.** For months every recording was drowned in 60 Hz hum and we blamed surgery, then grounding, then earth, then the splitter. The actual dominant coupling path was an electric field reaching the amplifier input through the air. A shield blocks it. This is the single highest-value intervention found so far. See [[01-infrastructure/system-overview]] for the big picture.
>
> **How to read this page.** [[#The evidence]] is why we believe it. [[#How to do it properly]] is the procedure. [[#The three rules we are still breaking]] is the free improvement still on the table. [[#What foil does NOT fix]] stops you expecting too much.

> [!quote] Paper-ready
> Aluminium foil shielding of the headstages reduced single-ended 60 Hz pickup on connected electrodes by up to two orders of magnitude (3604 to 8 µV). Following shielding, a bipolar EEG channel showed sleep architecture — a sustained reduction in EMG tone accompanied by delta-enriched EEG (Cliff's delta of the theta/delta ratio between low- and high-EMG epochs = -0.65) — a pattern absent from 111 hours of previously acquired recordings.

> [!danger] This is not a hack. It is the manufacturer's own first-line recommendation.
> Intan's application note *Noise Reduction Techniques* (10 December 2024) states plainly: **"A cardboard box covered in aluminum foil is equally effective at stopping electric fields as an expensive wire-mesh cage."** We spent weeks on grounding theory while skipping step 4 of the vendor's own checklist.

---

## The evidence

### Before and after the foil, same rig, minutes apart
Single-ended 60 Hz amplitude per electrode leg (`uid0715-17-58-36` → `uid0715-18-18-43`):

| slot | leg | before foil | after foil | change |
|---|---|---|---|---|
| A2 | frontal | 3604 µV | **8 µV** | **450x** |
| B1 | frontal / parietal | 694 / 3805 µV | **54 / 79 µV** | ~13x / ~48x |
| C1 | frontal | 3623 µV | **39 µV** | **93x** |
| D1 | frontal | 161 µV | **24 µV** | 7x |
| D2 | frontal | 631 µV | **66 µV** | 10x |

### The result that matters — the first sleep ever recorded here
A 164-minute run (`uid0715-18-58-54`) on the foiled rig. Slot **A1** showed textbook architecture: EMG high (~1000 µV, active) for 0.2 h, then **dropped to ~250 µV and held for a solid hour**, then jumped back with bouts. During that quiet hour **theta/delta sat at ~0.2** (delta dominating theta 5 to 1 = NREM). The delta-versus-EMG scatter is **bimodal, two distinct clusters** = two behavioural states.

### The comparison that proves it was the foil
Every archival recording on this PC, re-analysed with the same corrected method ([[#See also]]):

| recording | duration | slots | sleep biology | circadian |
|---|---|---|---|---|
| 72 h Jul 10 | 72.2 h | 8 | **0/8** | **0.0% on every slot** |
| 20 h Jul 13 | 20.1 h | 8 | **0/8** | n/a |
| 14 h Jul 02 | 14.2 h | 2 | **0/2** | n/a |
| 4.5 h Jun 29 | 4.6 h | 1 | **0/1** | n/a |
| **2.7 h Jul 15, foiled** | 2.7 h | 7 | **1/7 (A1, td_sep -0.65)** | n/a |

**2.7 hours of foiled data contains more real biology than 72 hours of unfoiled data.** The 72 h run scored **circadian power 0.0% on all 8 slots** — three full days with zero day/night rhythm, which a live mouse physically cannot do. Those files are byte-perfect recordings of noise.

## Why it works (the mechanism, from Intan's note)

The AC wiring in the walls sits at 220 V and oscillates at 60 Hz. It couples to the amplifier input **through the air** as an electric field, modelled as a capacitive voltage divider: a tiny capacitance C1 from the mains wiring to your electrode/headstage, against C2 (about 12 pF) from the amplifier input to ground. Even a minuscule C1 delivers millivolts to an input that is trying to resolve microvolts.

A Faraday cage **is tied to ground, and that gives C1 a new termination point, so the interfering signal never reaches the amplifier**. The shield does not "absorb" the noise; it gives it somewhere else to go.

This also explains the clipping we chased for weeks: Intan notes that in unshielded rigs the mains pickup is often **large enough to saturate the amplifier**, which makes it non-linear, so instead of a clean 60 Hz sine you get a distorted one **with harmonics at 120, 180, 240 Hz that a 60 Hz notch cannot remove**. Kill it at the source and the notch finally works.

## How to do it properly

Our version was, in Andrea's words, "badly wrapped", and it still produced the best result in project history. Doing it properly should be better again.

1. **Wrap the headstages, electrodes and the animal's immediate surroundings.** Intan: "The tissue, electrodes, and Intan headstages should be placed inside the Faraday cage. The Intan controller and computer... should be located outside the cage."
2. **Cover all sides.** "Small holes in the conductive material do not matter, but it is important to cover all sides of the experiment, even the bottom."
3. **Tie the shield to a ground point OUTSIDE the cage.** This is the step we are missing. Intan: connect it to the controller's chassis/IO ground terminal, "or you can connect the cage to another ground point in your lab. Experiment with different ground points and see which one works best. You don't have to use a thick wire for this connection."
4. **Do not let the shield touch anything inside it.** Especially not the animal, the implant, or the headstage GND.
5. **Verify by measurement, not by eye** — record 30-60 s and check single-ended 60 Hz per leg in absolute µV (see [[#See also]]). Target under 50 µV per leg.

## The three rules we are still breaking

> [!warning] Free improvement still on the table (as of 2026-07-15 night)
> 1. **The foil is FLOATING (not grounded).** Intan is explicit that the shield works *because* it is tied to ground. A floating shield still helped enormously here, but we are probably leaving most of the available ~40 dB (100-fold) unclaimed. **Grounding the foil is the single cheapest remaining win.**
> 2. **Possible contact with the animal.** Photos suggest foil may be near or touching the implant. Intan: "The GND terminal on the Intan headstage should be connected to the tissue via a ground electrode or skull screw, but this **should not be connected to the Faraday cage or to any external ground**... Try to keep your tissue electrically isolated from the Faraday cage." Our animal must stay grounded ONLY through the headstage.
> 3. **Partial coverage.** Cover all sides, including underneath.

## What foil does NOT fix

- **Magnetic fields.** "Faraday cages block electric fields, but they do not block low-frequency magnetic fields." The only fix for magnetic pickup is **geometry** — reduce the loop area formed by signal wire → tissue → reference wire → headstage. Intan's remedies: **bundle or twist** the pair, and **keep the electrode-to-headstage wires short (ideally under 10 cm)**. They name our exact chip: *"Twisted pairs of wires are useful for recording from pairs of electrodes using the bipolar-input Intan RHD2216 chip."*
- **Electrode contact.** Foil does not fix an open or mismatched leg. A1 still clips 19.3% after foiling. Contacts must reach 0.1-1 MΩ, matched within 2-3x per pair.
- **Clipping already in recorded data.** Clipped samples are gone forever, no filter recovers them.

> [!info] Where "twist the wires" applies, and where it does NOT
> It applies ONLY to the **analog** stretch between the electrodes and the headstage input. It does NOT apply to the SPI cable, the tether, or the slip ring downstream of the headstage — the Intan chip **digitises at the headstage**, and Intan states "data on the interface cables is purely digital and immune to noise pickup."

## Our architecture, in context (do not panic about the tether)

Our headstages sit at the **top of the chambers**, roughly **36 cm** of analog run from the animal (about 30 cm brain to slip ring, plus 6 cm slip ring to headstage). This is a legitimate, published arrangement, not a design error:
- A published tethered-mouse-EEG rig uses a 6-wire slip ring (Digikey #1528-1152-ND, about $23) with amplifiers' "extended head-stages" **placed on top of the cage lid** and raw analog down a **~64 cm** tether — longer than ours. They do report artifacts from "contact wearing, resulting in increased contact resistance of the slip ring."
- **IIIS Tsukuba** (Iwasaki/Funato/Yanagisawa — our montage reference) likewise runs headmount → recording cable → **slip ring** → AD converter → filter amplifier, with no head preamp.
- **Pinnacle** (the commercial standard) DOES amplify at the head (100x preamp) before the commutator, marketed as "head-mounted amplification to produce exceptionally clean waveforms, even during animal movement."

So the lid-mounted headstage is the **noisier trade-off**, which you compensate for with shielding, grounding and low-impedance matched contacts. Intan's under-10 cm rule assumes their head-mounted design. **The foil is exactly that compensation, and it worked.**

> [!check] Slip-ring rotation was TESTED and is NOT the problem
> Hypothesis: animal rotation changes slip-ring contact resistance and causes the clean-to-bad swings. **Refuted by direct experiment** (`uid0715-18-36-10`): deliberately twisting B1's slip ring barely moved it (201 µV, CV 9%, the steadiest slot), while an UNTOUCHED control (C1) swung 18x on its own. A well-matched low-impedance pair is robust even to deliberate slip-ring movement; a bad leg is unstable all by itself.

## Commutators the field uses

| type | product |
|---|---|
| Analog, cheap | Digikey #1528-1152-ND, 6-wire (~$23) |
| Analog, lab-grade | **Dragonfly SL-10** (dragonflyinc.com), Campden Instruments 6/10-ch mouse commutators, Triangle Biosystems |
| Analog + head preamp | **Pinnacle** low-torque mouse commutator |
| **Digital SPI (Intan-ready)** | Doric, LabMaker, Alpha Omega, Cambridge NeuroTech, NeuroTek |

## Honest limits of this discovery

> [!warning] This is a FIRST, not a validated system. Do not repeat the 2026-07-14 mistake of declaring victory off one clip.
> - **One channel, one 2.7 h recording.** A1 only. Six of seven slots still show no sleep biology.
> - **A1 clips 19.3%** — roughly 1 in 5 epochs must be rejected as artifact.
> - **B1 looked beautiful and FAILED the biology test** (td_sep +0.20). Its EMG floor at 28 µV is almost certainly a **dead EMG electrode**, not atonia. Clean-looking is not the same as sleep.
> - **The bar that matters is the one every archive failed:** a recording of at least 24 h showing a real circadian rhythm. Until that lands, this is promising, not proven.

## See also
- [[2026-07-15]] — the full day's journal, §7b (the foil) and §8 (the breakthrough and archive re-analysis).
- [[2026-07-15-earth-and-sleep-council]] — the 5-advisor council that established `differential_60Hz ≈ common_mode(floor) × electrode_Z_imbalance(binding variable)`.
- [[floating-cm-vs-contact-reconciliation]] — why early bring-up worked without an earth wire.
- [[earthing-60hz-hum-fix]] — earthing the XDAQ (still worth doing; earth sets the floor).
- [[60hz-mains-hum-discovery]] — Korea mains is 60 Hz, not 50.
- `02-procedures/eeg-data-analysis/scripts/state_scan.py` — ⭐ the corrected analysis tool. Derives layout from `sensors_by_port`, filters scorer-style, and gates on `td_sep` (theta/delta separation between low- and high-EMG epochs), the only test that distinguishes real sleep from structured noise.
- Sources: [Intan — Noise Reduction Techniques (PDF)](https://intantech.com/files/Intan_noise_reduction_techniques.pdf) · [Intan — RHD Recording Headstages](https://intantech.com/RHD_headstages.html) · [KonteX — Reducing Interference During Electrophysiology Recording Sessions](https://www.kontex.io/post/reducing-interference-during-electrophysiology-recording-sessions) · [Frontiers — Continuous Monitoring via Tethered EEG in Mice](https://www.frontiersin.org/articles/10.3389/fnbeh.2017.00172/full) · [Pinnacle — 3-ch mouse EEG/EMG](https://www.pinnaclet.com/3-channel-eeg-emg-systems-mice.html)
