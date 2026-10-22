---
tags: [reference, hardware, wireless, pinnacle, eeg, emg, lfp, pons, purchase]
created: 2026-10-16
status: open
---

# Pinnacle wireless EEG + pons LFP + EMG for up to 16 mice: verified setup and purchase

> [!success] SETTLED WITH THE PROFESSOR (2026-10-19), supersedes the 3-channel K9-SL plan below
> - **Head unit: 4-channel 8474-HR, custom.** Quote model (Andrea's recollection, check the quote): **8474-HR-SE4-C**,
>   4 channels = 2 EEG + 2 fully independent (differential) channels. Professor asks Pinnacle for:
>   **EEG high-pass 0.5 Hz, possibly 0.1 Hz** (stock seizure = 1.0 Hz), and the **fully independent configuration**.
> - **Custom headmount PCB, designed by us.** Pinnacle connector, via holes for screws/wires, EMG wire pads.
>   We solder the electrodes ourselves. **Must fit within 6 mm** on the mouse skull.
> - All 16 mice on ONE PC is the target (to be confirmed by Pinnacle and the pilot).
> - Still open: exact pin map of the custom unit, its connector drawing, and what the 2 EEG channels reference.
> - **Pin map (corrected 2026-10-19):** "2 EEG + 2 independent" = Pinnacle's **4-channel standard configuration** (catalog p.10):
>   CH1 = EEG1 − COMMON, CH2 = EEG2 − COMMON, CH3 = LFP+ − LFP− (pons pair), CH4 = EMG A − EMG B, + 1 GROUND. 8 pins, **no spare**
>   (the "2nd GND" idea was wrong: two ground pins exist only in the 3-ch fully independent layout). No custom pin order needed.
>   Headmount socket is female, openings up (catalog p.13 photos). Concept drawing: `attachments/2026-10-19-custom-headmount-concept.png`
>   (script `attachments/headmount_drawing.py`). Pitch 1.27 mm and orientation still to confirm with Pinnacle's drawing.

> [!abstract] TL;DR, where we are (2026-10-16)
> From Claude Code: I checked the handover brief (`wireless_mouse_sleep_eeg_emg_lfp_handover.md`) against Pinnacle's
> own store, website, 2026 catalog and 2025 brochure, two papers that ran the system, and 10 min of ahyeon's unipolar data.
>
> - **THE HANDOVER HAS THE PART NUMBERS WRONG.** The system is **8200-K9-SL** ($4,237, ONE mouse: head unit + dongle).
>   **8200-K10-SL/SE** is the mouse *accessory kit* ($884.25, headmounts, screws, batteries, no electronics).
>   K9 is NOT rat-only, the same hardware works for mice and rats.
> - **Input range is ±465 µV, fixed** (gain 2600 V/V, 14-bit). The ±480 µV in the handover belongs to the older 12-bit unit.
>   No gain option exists for the 2 EEG/1 EMG unit.
> - **Decision rule from the handover:** (1) EEG + LFP + EMG at once: **PASS on paper** (2 referential channels + 1 differential).
>   (2) LFP range will not clip: **CONDITIONAL**, fine for sleep scoring and P-wave detection, marginal for P-wave amplitude
>   analysis. (3) 6-pin headmount that we wire ourselves: **PASS** (8201-SS). All three still need Pinnacle's written confirmation.
> - **72 h runs: record at 512 Hz, not 1024 Hz.** 1024 Hz is rated exactly 3 days, zero margin, and a published group lost data to batteries.
> - **16 mice:** one dongle per mouse (ships in each kit), Windows PCs only, Pinnacle publishes NO per-PC limit.
>   Published: 4 at once tested (Morrone 2023), 10 at once run for 72 h (Kolling 2026).
> - **NO TTL INPUT ON THE WIRELESS UNIT.** Our video sync design (Pi pulse into the EEG file) cannot work with it.
> - **List cost for 16 mice ≈ $71,300** (16 × K9-SL + 4 × K10), before Korean distributor pricing, PCs and spares.
> - **My recommendation: a 4-mouse pilot first** (4 × K9-SL + 1 × K10 ≈ $17,830), not 16 at once. Details in §8.

Provenance labels used below: ✅ = I read it at the primary source myself today. 🔎 = a research agent read it at a
primary source (URL given) and I did not re-open it. ❓ = not published anywhere we could find, goes to Pinnacle.

---

## 1. What the handover got wrong

| Handover says | Actually | Source |
|---|---|---|
| 8200-K10-SL = wireless mouse system | Accessory kit, $884.25: 8201-SS headmounts, 8209 + 8212 screws (8 each), 8226 silver epoxy, 8241-F screwdriver, 8249 test source, box of 60 zinc-air cells, 8275 battery cap, 9005 powered USB hub, 8254 needle, 8255 multimeter, 8276 supplemental battery | ✅ [store K10](https://store.pinnaclet.com/products/8200-k10-sl-accessory-kit-for-wireless-mouse-sleep-system) |
| 8200-K9-SL = rat system, do not order | The wireless hardware kit, $4,237: 8274-SL head unit, 8274-D dongle, 9052 USB extension, driver disc, manuals. "All hardware is compatible with mice or rats." Rat accessory kit is K11 | ✅ [store K9](https://store.pinnaclet.com/products/8200-k9-sl-2-eeg-1emg-wireless-mouse-system-for-sleep), ✅ [wireless page](https://www.pinnaclet.com/EEG_EMG_Systems_Wireless.html) |
| ~$4,237 for "the system" | $4,237 buys ONE head unit, so ONE mouse at a time | ✅ store K9 |
| Input range ±480 µV | ±465 µV on the current 8274-HR (2600 V/V, 14-bit, 57 nV/bit). The website and catalog print "+/- 465 mV", a unit typo (57 nV × 2¹⁴ ≈ 0.93 mV pk-pk) | ✅ [brochure © 2025](https://www.pinnaclet.com/PDF/Pinnacle_EEG_EMG_Brochure.pdf) |
| 5 connections: EEG, LFP, EMG+, EMG−, one ground/reference | 6: the headmount has separate **EEG COMMON** (reference) and **AGND** (ground) pins | ✅ [catalog 2026](https://www.pinnaclet.com/PDF/catalog.pdf) p.13 |
| 8209 = 0.10-inch screw (diameter) | Pinnacle never says which dimension 0.10" is. 8209 = 0.10" (anterior), 8212 = 0.12" (posterior, "to facilitate the curvature of the skull") | 🔎 store 8209 / 8212 pages |
| Sirenia licence included | Sirenia **Acquisition** is free (unlimited PCs). **Sleep Pro** scoring is extra, $2,362.50 per PC | ✅ catalog ("free Sirenia® Acquisition software"), 🔎 store 9035, 🔎 [EULA](https://www.pinnaclet.com/PDF/Pinnacle%20EULA.pdf) |

> [!warning] Pinnacle's own pages disagree on what is inside the K9-SL
> The store lists the **8274-SL** head unit (sold alone $2,898 to $3,042.90, the older generation). The 2026 catalog p.6 lists
> the **8274-HR-SL** (sold alone $4,000, ✅ [store search](https://store.pinnaclet.com/search?q=8274&type=product)).
> The $237 gap between the kit and an HR unit alone suggests HR, but GET IT IN WRITING before ordering.

## 2. Verified spec of the 8274-HR wireless head unit

| | Value | |
|---|---|---|
| Channels | 3: 2 EEG + 1 EMG (sleep config "SL") | ✅ brochure |
| Referencing | CH1 and CH2 each vs a shared EEG COMMON, CH3 = differential pair, GROUND separate. Drawn for Pinnacle's 3-channel standard mouse configuration; the wireless unit uses the same 8201-SS headmount, so it is very likely the same, ❓ confirm | ✅ catalog p.10 + p.13 |
| Gain / range / resolution | 2600 V/V fixed, ±465 µV, 14 bits, 57 nV/bit | ✅ brochure |
| Hardware high-pass | EEG 0.5 Hz (sleep), EMG 10 Hz | ✅ brochure |
| Low-pass / anti-alias | "Software Configurable Low-Pass Filters: N/A" for wireless. Actual anti-alias corner per rate: ❓ | ✅ [industry catalog](https://www.pinnaclet.com/PDF/industry_catalog.pdf) p.3 |
| Sample rates | 256, 512, 1024, 2000 Hz. Pinnacle's Python driver only lists 1024/512/256/128 | ✅ brochure, 🔎 [Morelia API](https://github.com/Pinnacle-Technology-Inc/Python-POD-API) |
| Battery life, 3-ch | 256 Hz 7 d · 512 Hz 6 d · 1024 Hz 3 d · 2000 Hz 2 d. "Bluetooth interference may affect battery lifetime" | ✅ brochure |
| Battery | Zinc-air size 13 (PR48), disposable, $59.95 per 60. Swap needs the mouse in hand | ✅ store K10 |
| TTL / sync input | **N/A** on wireless (tethered Pinnacle has 4 TTL in/out) | ✅ industry catalog p.3 |
| Mass | 3.8 g (brochure) or 3.9 g (website), incl. battery and headmount. Morrone measured ~3.4 g | ✅ brochure, ✅ Morrone 2023 |
| Radio | Bluetooth to a USB dongle (driver code points to Bluetooth LE) | ✅ website, 🔎 Morelia API |
| Software | Sirenia 3.3.4, **Windows 10/11 only**, i5/Ryzen 5, 8 GB RAM, 1 GB VRAM ("onboard video not recommended"). Native file = PVFS; a free Batch EDF Converter exists | ✅ [download page](https://www.pinnaclet.com/sirenia-download.html), 🔎 [drivers page](https://www.pinnaclet.com/drivers.html) |
| Lost data | Sirenia draws gaps for lost packets; the Python API fills a lost 40-sample packet with NaN | 🔎 Sirenia change log, 🔎 Morelia API |
| Status | All wireless SKUs listed as available, no discontinuation notice found | 🔎 store |

## 3. How our three signals map onto the headmount

8201-SS pins, catalog p.13 (✅): **EEG 1, EEG 2, EEG COMMON, AGND, EMG A, EMG B**.

```
 CH1 = EEG1 screw (cortex)       − EEG COMMON (reference screw)
 CH2 = pons depth wire (DV 4.5)  − EEG COMMON (same reference)
 CH3 = EMG A − EMG B             (differential, nuchal)
 AGND = separate ground screw
```

- Per mouse that is **3 skull screws** (EEG1, COMMON, AGND) + 1 depth wire + 2 EMG leads, not the 2 screws the handover assumes.
  Whether COMMON and AGND may share one screw: ❓ ask Pinnacle. (On our Intan unipolar mice REF is shorted to GND, but that tells us nothing about Pinnacle's front end.)
- The pons channel is **pons minus the COMMON screw**, a single-ended signal, not a local LFP. Offline, CH2 − CH1 = pons minus cortex (COMMON cancels).
  A local bipolar pons LFP would need a 4-channel unit (8400-K40-SE31M, 3 EEG/1 EMG, seizure config), 🔎 listed but not evaluated.
- **Reference placement:** the published single-ended mouse P-wave recordings reference to a **cerebellar screw**
  (Tsunematsu 2020, 🔎). A published 8274-HR-SL + 8201-SS study put the shared reference on the posterior right screw and the
  ground on the anterior right screw, mount front 3 mm anterior to bregma (✅ Kolling 2026). Pinnacle's own screw-hole map: ❓.
- The 8201-SS via holes take a screw directly OR a wire lead ("Insert electrode screws into via holes or use pre-soldered wire
  leads", ✅ catalog p.13), so a cerebellar reference or the pons wire can come in on a lead. Screws with leads: 8403 (0.10"), $11.38 each 🔎.
  Pinnacle states "Depth electrodes can be soldered to headmounts for LFP recordings" (✅ catalog p.11, general statement, not specific to the wireless unit).
  Their own depth headmount 8201-DEP is 2.2 mm Pt/Ir for hippocampus, no EMG, so it is no use for the pons. Single-ended Pt/Ir depth electrodes 8425-PR-3/-5/-8 (3/5/8 mm) exist ✅ catalog.
- **LABEL EVERY VIA HOLE AND CHECK IT WITH THE 8249 TEST SOURCE AND THE MULTIMETER BEFORE CEMENT.** Our 08-08 root cause was a cerebellum ground on the wrong pin (memory note `ecg-cohort-ground-miswired`).

## 4. Will ±465 µV clip?

### 4.1 Literature (pons)

| Event | Amplitude | Setup | Source |
|---|---|---|---|
| Mouse P-wave, REM, dorsal pons | ~0.3 mV negative, ~0.4 mV pk-pk (read off figures) | bipolar wires, subcoeruleus DV −3.5 vs caudal pontine reticular nucleus **DV −4.5**, Intan RHD2132 at 1 kHz | ✅ Schott, Baik, Chung, Weber 2023 Nat Commun, [PMC10318054](https://europepmc.org/article/PMC/PMC10318054) |
| Motor artefacts on the same channel | they removed outlier waveforms ">0.5 mV" (3 SD) | same | ✅ same, Methods |
| Mouse P-wave, single-ended vs cerebellar screw | ~0.2 mV, up to ~0.4-0.5 mV in examples | silicon probe 3.75-4.3 mm deep | 🔎 Tsunematsu 2020 eLife [10.7554/eLife.52244](https://doi.org/10.7554/eLife.52244); Tsunematsu 2023 Sleep [10.1093/sleep/zsad193](https://doi.org/10.1093/sleep/zsad193) |
| Rat P-waves | 70-280 µV | review | 🔎 Gott 2017 [10.3389/fnhum.2017.00089](https://doi.org/10.3389/fnhum.2017.00089) |
| P-wave rate | ~0.6-1 /s in REM, ~0.05-0.1 /s in NREM | | 🔎 Schott 2023, Tsunematsu 2020 |

Note: **DV −4.5 mm is exactly where Schott put their REFERENCE tip** (caudal pontine reticular nucleus). Their P-wave tip was 1 mm higher, in the subcoeruleus.
Which nucleus we target at DV 4.5 (and the AP/ML) matters for how big the P-waves will be: ❓ for us (ahyeon / Andrea).

### 4.2 Our own data (ahyeon's 10-min unipolar rehearsal, 10-14 21:08, lights off, mice mostly awake)

Single-ended vs the Intan REF (shorted to GND at a separate site), the closest thing we have to "depth wire vs COMMON screw".
High-pass 0.5 Hz (Pinnacle EEG), EMG high-pass 10 Hz (Pinnacle EMG). Script: `eeg-emg-analysis/qc/wireless_range_clip_check.py`, data copied from the NAS `02_Data_Sleep/ahyeon/10minutes_test/`.

| Mouse (slot) | LFP_TGT max | LFP_TGT 1-s windows > 465 µV | EEG_F max | EEG_F windows > 465 | EMG (L−R) max | EMG windows > 465 | EMG samples > 465 |
|---|---|---|---|---|---|---|---|
| B6JF020113 (C) | 522 µV | 0.2 % | 534 µV | 1.0 % | 2213 µV | **17.9 %** | 0.21 % |
| B6JF020114 (B) | 921 µV | 1.5 % | 1042 µV | 2.7 % | 2051 µV | **45.5 %** | 0.30 % |
| B6JF020112 (A) | 8.8 mV pk-pk of 60 Hz on every channel (known surgical fault): **> 465 µV in ~2/3 of all samples**, the channel would sit on the rail | | | | | | |

LIMITS: 10 min, awake, NO REM, so it says nothing yet about P-waves. Is LFP_TGT in ahyeon's mice the pons DV 4.5 target? ❓
The 30 h run that would have given REM was lost on 10-15 after 13 min ([[2026-10-15]]).

### 4.3 Verdict

- **Sleep scoring (EEG1 + EMG): OK.** EEG flat-tops in ≤ 3 % of awake seconds. The EMG flat-tops in 18-46 % of awake seconds,
  but scoring only needs "EMG high vs low", and sleep EMG sits far below the rail. DO NOT USE IT FOR EMG AMPLITUDE ANALYSIS IN WAKE.
- **P-wave detection (count, timing): probably OK.** Typical mouse P-waves (0.1-0.45 mV) sit under the rail. Detection is threshold-based, so a flat-topped P-wave still counts.
- **P-wave amplitude, waveform, spectra: AT RISK.** Headroom is close to 1×. The biggest P-waves and anything near the 0.5 mV artefact level will flat-top.
- **Hippocampus would fail** (sharp waves > 2.5 mV, dentate spikes 2-4 mV in rat, larger in mouse, 🔎 Buzsáki 2015, Bragin 1995). Not our target, noted in case it changes.
- **A BAD GROUND BECOMES UNRECOVERABLE.** On the XDAQ (±5 mV) we can notch mains out afterwards. On a ±465 µV unit mains of mouse-A size rails the channel, and clipped data cannot be notched. Ground QA at surgery matters more with Pinnacle than with our rig.
- More range exists only as **8274-SE3-EI** "Extended input range", 3 EEG seizure, NO EMG, $2,898 ✅ store. Its range is not published (❓).
  Ask Pinnacle for a 2 EEG/1 EMG unit with the EI range on EEG2 only.

## 5. Battery and sampling rate for 48-72 h

- **512 Hz** for every run longer than 48 h: rated 6 days, about 2× margin. Nyquist 256 Hz is enough for scoring (EEG 0.5-30 Hz, EMG power above 10 Hz) and for P-waves (70-180 ms long, 🔎 Gott 2017).
- **1024 Hz only for runs ≤ 48 h.** Rated 3 days, and battery life drops with Bluetooth traffic (✅ brochure). Morrone 2023 (✅): "upward of 72-h of recording at 1,024 samples/s", yet "2 mice had battery issue causing data loss for half of the SD period". Kolling 2026 (✅) did run 72 h at 1000 Hz with an 8276 "jump-start" battery at the start to spare the main cell.
- **2000 Hz never for these runs** (rated 2 days).
- A fresh cell every run. Peel the tab and wait 5 min before inserting (✅ Morrone 2023). A mid-run swap means picking up the mouse.
- Zinc-air cells: 4 × K10 kits bring 4 boxes = 240 cells. 16 mice per run ⇒ ~15 runs before buying more ($59.95 per 60).

## 6. Sixteen mice: radio, dongles, PCs

What is known:
- **One 8274-D dongle + one USB extension per kit** (✅ store K9). The dongle firmware has 4 connection slots (🔎 Morelia code), but nothing says Sirenia uses more than one. DO NOT PLAN ON SHARING DONGLES.
- **Pinnacle publishes no limit per dongle, per PC or per Sirenia instance** (🔎 website, catalog, download page all silent).
- Morrone 2023 (✅): "We have tested up to 4 simultaneous 8274 recordings", "a potential for upward of 16 on one computer depending on Bluetooth traffic". Also "electrical/Bluetooth interference from traffic in normal housing rooms can interfere with EEG/EMG signals", and they prefer "a dedicated testing room".
- Kolling 2026 (✅): "simultaneous data acquisition from up to 10 mice across distinct Bluetooth channels" (number of PCs not stated).
- **Windows 10/11 only** (✅). Our machines are all Ubuntu, so these are NEW PCs. Linux support of the Python API: ❓.
- If we ever use Pinnacle's own video: at most 4 cameras per PC (✅ catalog p.22 "Up to four cameras can be added to a single video system").

> [!success] DECIDED 2026-10-20 (supersedes the topology below): ONE custom PC, ASUS PRIME B550-PLUS, single-slot GPU + 4 PCIe x1 USB cards, 4 dongles per card = 16 (12 now, 4 in January). Unstable ⇒ second identical PC, move 2 cards (8 + 8). Details: [[2026-10-20]].

Proposed topology (only verified constraints, the rest flagged):
1. 16 × K9-SL kits, each dongle on its own 9052 extension, placed close to the cages it serves (distance guidance: ❓).
2. **Start with 4 PCs × 4 mice**, which is the published tested load (Morrone) and the Pinnacle video limit. Move to **2 PCs × 8** only after Pinnacle confirms in writing AND the pilot shows no gaps with 8 units on one PC.
3. Survey the room's 2.4 GHz traffic with Sirenia's RF Sniffer (🔎 change log 2.2.5) before the first run. Move the rack WiFi router to 5 GHz, keep the Pis on Ethernet with WiFi/Bluetooth off (engineering judgement, not a Pinnacle spec).

RF risks:
- **GROUNDED FOIL OR A FARADAY BOX AROUND THE CAGE WILL BLOCK 2.4 GHz.** Our tethered shielding approach does not carry over. Pinnacle sells acrylic cages and a "(Wireless)" lid variant (🔎 catalog p.23).
- The lab is moving to E7, so the radio environment there is unknown. Test there, not in the current room.

## 7. Video sync: the real conflict

Our sync decision ([[2026-07-27-video-eeg-sync-recording-architecture]]) needs a TTL pulse from each Pi recorded INTO the EEG file ("frame N to sample S, no clocks").
**The wireless 8274 has no TTL input** (✅ industry catalog p.3), so that design cannot be built on it. Options:
- Pinnacle's own video ("within 100 ms" 🔎 video brochure / "± one video frame" 🔎 catalog p.22), max 4 cameras per PC, Windows.
- Host-clock timestamps only (drift unmeasured over 72 h).
- Skip video for this project. (The room currently has no cameras anyway.)
This is a decision for Andrea / the professor, not a vendor question.

## 8. What to buy

US online list prices, USD, 2026-10-16. The store ships to the US only. In Korea Pinnacle lists **VIVO Solutions** (✅ [distributors page](https://www.pinnaclet.com/distributors.html): info@vivosolutions.co.kr, +82-31-701-7980), so the real price will differ.

**Recommended: pilot first (4 mice, one PC)**

| Item | Qty | Unit | Total |
|---|---|---|---|
| 8200-K9-SL wireless hardware kit (head unit + dongle) | 4 | 4,237.00 | 16,948.00 |
| 8200-K10-SL/SE mouse accessory kit (4 surgeries) | 1 | 884.25 | 884.25 |
| 8403 0.10" screw with wire lead (cerebellar reference / ground on a lead) | 8 | 11.38 | 91.04 |
| **Pilot total** | | | **17,923.29** |
| Windows 10/11 PC (i5/Ryzen 5, 8 GB, discrete GPU, 1 TB) | 1 | local | ? |

Pilot pass criteria before ordering the other 12: 72 h at 512 Hz with no battery death; pons channel clipped in < 1 % of REM seconds; gaps < 0.1 % of the run with 4 units on one PC in the E7 room; the pin map confirmed with the test source.

**Full 16 (if the pilot passes)**

| Item | Qty | Unit | Total |
|---|---|---|---|
| 8200-K9-SL | 16 | 4,237.00 | 67,792.00 |
| 8200-K10-SL/SE | 4 | 884.25 | 3,537.00 |
| **Core total** | | | **71,329.00** |
| Spare 8201-SS headmounts (failed surgeries) | 8 | 36.28 | 290.24 |
| Optional spare head unit 8274-HR-SL | 1 | 4,000.00 | 4,000.00 |
| Optional Sirenia Sleep Pro (only if scoring in Sirenia) | per PC | 2,362.50 | |
| Windows PCs | 2-4 | local | |

If Pinnacle confirms one dongle serves 4 units: 4 × K9-SL + 12 × 8274-HR-SL alone = $64,948 instead of $67,792 (saves $2,844). Not worth it unless confirmed.
Mouse acclimation dummy 8274-AC ($47): 🔎 listed as unavailable on the store.

## 9. Questions for Pinnacle (get answers IN WRITING before the PO)

1. Does today's 8200-K9-SL ship the 8274-HR-SL (14-bit, ±465 µV) or the 8274-SL? Store and 2026 catalog disagree. Is a battery included?
2. Confirm the input range is ±465 µV (catalog prints "mV"), and that it is the same on the EMG channel.
3. Wireless referencing: EEG1 and EEG2 each against EEG COMMON, EMG A minus EMG B, AGND separate, same as the tethered standard mouse configuration?
4. 8201-SS: which via hole is EEG1, EEG2, COMMON, AGND, and how is the board oriented? Can a pons depth wire (DV 4.5 mm) be soldered into the EEG2 via? Can COMMON be a cerebellar screw on a lead? Can COMMON and AGND share one screw?
5. Can you build a 2 EEG/1 EMG sleep unit with the extended input range on EEG2? What is the "-EI" range, price and lead time?
6. Anti-alias low-pass corner at 512 and 1024 Hz.
7. Realistic battery life at 512 and 1024 Hz with 16 units in one room.
8. Units per dongle, per PC and per Sirenia instance; recommended USB layout and maximum dongle distance; behaviour inside metal racks or shielded enclosures.
9. Does the head unit buffer during a dropout? How do gaps appear in PVFS and EDF? Are timestamps from the sample counter or host arrival time? Drift between units over 72 h?
10. Any way to put an external sync pulse into the data, given no TTL?
11. Is the Python API (ptech-morelia) supported on Linux for the 8274-HR?
12. EMG lead length on the 8201-SS (website table says N/A).
13. Korean price and lead time via VIVO Solutions, warranty, expected head-unit lifetime.
14. Can we have the 8295 user manual and the surgery guide before purchase?

### Email draft (to VIVO Solutions, cc sales@pinnaclet.com). Written with no dashes as punctuation, part numbers kept as they are.

> Subject: Pinnacle wireless EEG/EMG for 16 mice, technical questions before ordering
>
> Dear VIVO Solutions team,
>
> We are a sleep research lab at KAIST and we are planning to buy Pinnacle wireless EEG/EMG systems for up to 16 mice,
> starting with a pilot of 4 units. Each mouse will carry one cortical EEG screw, one depth wire in the pons (about 4.5 mm
> deep), and nuchal EMG. Recordings will run for 48 to 72 hours. Before we order, could you please forward these questions
> to Pinnacle Technology and send us their answers in writing:
>
> 1. Does the 8200-K9-SL kit currently ship with the 8274-HR-SL or the 8274-SL head unit? Is a battery included?
> 2. Please confirm the input range of the 8274-HR-SL is plus or minus 465 µV (the catalog prints mV), on the EEG and on the EMG channel.
> 3. Are EEG1 and EEG2 both referenced to the EEG COMMON pin, with EMG A and EMG B differential and AGND separate?
> 4. On the 8201-SS headmount, which via hole is EEG1, EEG2, COMMON and AGND? Can we solder a depth wire into the EEG2 via, and can COMMON and AGND share one screw?
> 5. Is a 2 EEG/1 EMG sleep unit available with the extended input range on EEG2? What is that range, the price and the lead time?
> 6. What is the anti aliasing filter corner at 512 Hz and at 1024 Hz?
> 7. What battery life should we expect at 512 Hz and 1024 Hz with 16 units in one room?
> 8. How many head units can one dongle, one PC and one Sirenia instance support, and what USB layout and dongle distance do you recommend?
> 9. How are lost packets shown in PVFS and EDF exports, how are timestamps generated, and is there any way to add an external sync pulse?
> 10. Is the Morelia Python API supported on Linux?
> 11. Could you send the 8295 user manual and the surgery guide?
> 12. Please quote 4 units of 8200-K9-SL and 1 unit of 8200-K10-SL/SE, delivered to KAIST, with lead time and warranty.
>
> Thank you very much,
> Andrea Piazzola

## 10. Still open

- [ ] Andrea / ahyeon: exact pons target (nucleus, AP/ML), and is it the same as LFP_TGT in ahyeon's current unipolar mice? If yes, her next run with REM gives a direct P-wave clipping test (rerun `eeg-emg-analysis/qc/wireless_range_clip_check.py` on REM epochs).
- [ ] Decide on video sync for this project (§7).
- [ ] Send the email in §9 (Andrea), then file the answers here.
- [ ] Windows PCs: buy new or reuse? None of our machines run Windows.
- [ ] Head mass: 3.8-3.9 g + cement + depth wire on a 20-30 g mouse. Check against our animal protocol.

## Sources (all accessed 2026-10-16)

Pinnacle: [store K9-SL](https://store.pinnaclet.com/products/8200-k9-sl-2-eeg-1emg-wireless-mouse-system-for-sleep) ·
[store K10](https://store.pinnaclet.com/products/8200-k10-sl-accessory-kit-for-wireless-mouse-sleep-system) ·
[store search 8274](https://store.pinnaclet.com/search?q=8274&type=product) ·
[wireless page](https://www.pinnaclet.com/EEG_EMG_Systems_Wireless.html) ·
[EEG/EMG brochure © 2025](https://www.pinnaclet.com/PDF/Pinnacle_EEG_EMG_Brochure.pdf) ·
[catalog 2026](https://www.pinnaclet.com/PDF/catalog.pdf) (pp. 6, 10, 11, 13) ·
[industry catalog](https://www.pinnaclet.com/PDF/industry_catalog.pdf) (p. 3) ·
[Sirenia download](https://www.pinnaclet.com/sirenia-download.html) ·
[distributors](https://www.pinnaclet.com/distributors.html) ·
[Morelia Python API](https://github.com/Pinnacle-Technology-Inc/Python-POD-API).

Papers: Schott AL, Baik J, Chung S, Weber F (2023) Nat Commun, "A medullary hub for controlling REM sleep and pontine waves", PMC10318054 ·
Morrone C … Yu WH (2023) Front Aging Neurosci, "Concurrent behavioral and electrophysiological longitudinal recordings for in vivo assessment of aging", PMC9891465 ·
Kolling L … Marcinkiewcz CA (2026) Alzheimer's & Dementia 22(8):e71687, "Dorsal raphe tau pathology disrupts sleep-wake orchestration…", PMC13449038 ·
Tsunematsu T et al. (2020) eLife 10.7554/eLife.52244 · Tsunematsu T et al. (2023) Sleep 10.1093/sleep/zsad193 ·
Gott JA, Liley DTJ, Hobson JA (2017) Front Hum Neurosci 10.3389/fnhum.2017.00089.
