---
tags:
  - decision
  - kontex
  - xdaq
  - call-prep
  - scale-up
  - 32-mice
  - rig-finalization
created: 2026-07-28
updated: 2026-07-29
status: live
call_date: 2026-07-29
counterpart: KC Kong (KonteX Neuroscience)
attendees: Andrea, Prof. Kim Staci Jakyong, KC Kong
---
# 📞 KONTEX CALL — 2026-07-29, 11:30 Taipei / 12:30 Korea

> [!important] THIS IS THE ONLY DOCUMENT YOU NEED IN THE CALL.
> Self-contained on purpose. Nothing here requires opening another note.
> **§A** brief the professor · **§B** what is already settled, do not spend call time on it · **§C** the 11 questions that matter · **§D** the build and the money · **§E** what we must leave with · **§F** notes.
> Everything we know and how we learned it is in the appendix (§G), not in the call flow.

---

## §A. BRIEF THE PROFESSOR (send before the call)

**What we are buying.** An acquisition system to record **32 mice simultaneously** for chronic sleep EEG/EMG in continuous 72-hour runs. We record 8 today and that rig is completely full.

**Proposed build.** 2 × XDAQ ONE+ at the 1024-channel tier + 8 × Port Expander, reusing the Intan RHD2216 headstages we already own.

**Three facts that frame everything:**

1. **A "channel" is really a mouse slot.** Every system reserves 64 channels per animal no matter how few we use. **Mice = channels ÷ 64.** A 1024-channel box records **16 mice, not 64**. Our 8-mouse ceiling is 512 ÷ 64 = 8. It was arithmetic all along.
2. **32 mice always means two boxes.** No splitter, adapter or configuration changes this, in any ecosystem, at any price.
3. **The Port Expander is mandatory to reach 16 mice per box** — it is not an optional extra we can drop to save money.

**Decisions already taken:**
- **No Allego software licence** ($2,500–5,000/seat). It does not deliver the per-animal scheduling that justified it. The free Open Ephys GUI replaces it.
- **No commutators in this purchase.** We keep our slip rings. At 32 units they would have been the single largest line in the budget.
- **Recording start/stop will be global**, not per-mouse. No system offers per-animal scheduling at 16 animals. We record continuously and separate each user's data afterwards.

**The caveat, stated honestly.** This purchase is **not** our current bottleneck. Electrical contact is. No acquisition box fixes an open electrode. Decide carefully, **in parallel with** fixing contact.

> [!history] Updated 2026-08-03 — the caveat stands, its diagnosis does not
> This paragraph originally read "frontal electrodes are open on every mouse …
> we have no scoreable data yet … fixing surgical yield". Three corrections:
> we have **11.1 scoreable mouse-hours**; the failure is the **EEG channel
> `/1`**, not a frontal-vs-parietal distinction; and **EMG works through the
> identical implant, tether and slip ring on most animals**, so surgery is not
> demonstrated to be the cause. The free rig-side checks come first.
> See [[2026-08-03-two-8-mouse-runs]].

**Full written comparison:** `~/Downloads/DAQ-comparison-32-mice.docx`

---

## §B. SETTLED — DO NOT SPEND CALL TIME ON THESE

| Fact | How we know |
|---|---|
| Mice = XR channels ÷ 64. Core 512→8, ONE+ R1024→**16**, AIO→16 | Two independent Kontex figures |
| 32 mice = 2 boxes. Splitter fills a box, never exceeds it | Kontex + Intan datasheets |
| **Intan RHD2216 headstages work with the Port Expander** | **KC confirmed 28 Jul** |
| Port Expander = **$1,525/unit** | Kontex quote 262024 |
| SAdpt-XDAQ-OM12 = **$275/unit** | Kontex quote 262024 |
| Port Expander is **mandatory** for 16/box | NNX manual: "16 X3R32*", footnote "* Requires Port Expander" |
| Kontex officially supports the **Open Ephys GUI** for XR mode | kontex.io/software |
| **Open Ephys GUI already runs on our XDAQ Core** (1 headstage, 32 ch, 23 Jul) | Our own bench |
| A **Linux driver path exists** — Thunderbolt + stock `boltd`, libxdaq tested on Ubuntu 24.04 | Kontex developer portal |
| ONE+ has **Sys GND + Chassis GND** with per-node ESD DIP earth-coupling switches | NNX manual p.22 |
| Tether at 22.5 cm is fine on the digital side | KC's own 40 cm guidance |
| Global recording start/stop | Confirmed by **both** Kontex and Open Ephys |

---

## §C. THE 11 QUESTIONS THAT MATTER

### 🔴 Money — ask first, everything else is secondary

**Q1. ⭐ The package quote.** Itemised, volume-discounted, delivered to KAIST Daejeon:
`2 × ONE-R1024-SR64` · `8 × SAdpt-Port-EXP` · `32 × SAdpt-XDAQ-OM12` · `8 × KonteX HDMI cable` · optional `2 × SyncLink` · `DB25 breakout`.
**We have Port Expander ($1,525) and OM12 ($275). What we do not have is the ONE+ unit price — that is the single biggest unknown in the whole decision.** Lead time, shipping, import duty and VAT handling.

**Q2. Can the purchase be phased?** One ONE+ and 4 Port Expanders now for 16 mice, the second set later. Does phasing forfeit the volume discount?

**Q3. Commutators — price and discount only.** We are keeping our slip rings, so this is opportunistic: what would Standard and PRO cost at 32 units with a discount? Do they work with an Intan RHD2216 headstage?

### 🟠 What changes the build

**Q4. ⭐⭐ What does the Port Expander's ground isolation buy us, in microvolts?**
Open Ephys confirmed in writing (28 Jul) that with a **bipolar** montage *"this would already be independent referencing per animal, because each electrode is referenced to a local electrode on the same animal."* Our RHD2216 has no reference pin, so **we already have per-animal referencing for free**. That leaves the Port Expander adding **ground** isolation only. Our own bench cleared the shared port ground as a 60 Hz source, and a published 4-mouse shared-ground study measured inter-animal contamination at chance level.
**Is there a measured figure? Or is the honest answer that we buy it as a port multiplier and treat isolation as a bonus?**
Related: your figure says **SYS GND should be bonded to the XDAQ HDMI ground**, so isolation must sit downstream, per EXP port. Where exactly is the barrier, and what is its capacitance?

**Q4b. 🔴⭐ ADDED 2026-08-03 — expose `Zcheck pol sel` so we can measure BOTH electrodes of a bipolar pair.**
The RHD2216 is bipolar: each amplifier has two electrode pins, `inX+` and `inX−`,
and **both are real electrodes in the animal**. The Intan datasheet provides a
dedicated register bit, **`Zcheck pol sel`** (Register 5), precisely so each can be
impedance-tested separately — 0 selects `inX+`, 1 selects `inX−`.

**Radiens exposes no way to reach it.** Verified at source level in
`radiens-core` 0.0.8: `get_intan_impedance(port)` is the only impedance method,
`ImpedanceRequest` carries only a port, `ImpedanceValue` carries only
`ntv_chan_idx / magnitude_ohm / phase_deg`, and the only register-access methods
(`load_all_mosi`, `transmit_mosi`, `read_wire_out`, `flash_sinaps`) are
**Sinaps-probe specific** and cannot address the RHD chip.

**Consequence for us:** every impedance sweep this project has ever taken measures
**one electrode of each pair**. The other has never been measured. That is not a
cosmetic gap — the hum that tells us an electrode is open is driven by the
*imbalance* between the two inputs, so the quantity that predicts data quality has
been unmeasurable throughout. It already produced one concrete false reading: a
channel read 0.133 MΩ, the best in our fleet, and then recorded nothing but hum
for 21.7 hours.

**Ask:** can `Zcheck pol sel` be exposed in Allego and/or the Python API — as a
polarity argument to `get_intan_impedance`, or as a second value per channel? It
is a single bit you already drive. Is there any existing route we have missed?

**Q5. ⭐ Why two PCs, and is SyncLink actually needed?**
Three parts, and the first may dissolve the other two:
- **(a)** Mice 1-16 on box A and 17-32 on box B are **different animals in different chambers**. Nothing in sleep scoring compares them sample-by-sample. What we need is each mouse aligned to its own video, which we already do with a TTL pulse train. **Do the two boxes need to be sample-locked at all?** If not, SyncLink comes out of the build.
- **(b)** If two PCs are genuinely required, **why**? Is it the Open Ephys plugin enumerating one device per instance, or the driver, or Thunderbolt? Data rate is not the reason (31 MB/s at 30 kHz for all 32 mice).
- **(c)** If SyncLink is bought, **how does it behave under the Open Ephys GUI, and what appears in the recorded data?** Do the two boxes share a sample clock so that sample N on box A equals sample N on box B? Open Ephys synchronises within a single GUI instance, so with two PCs the GUI cannot sync across them.

**Q6. Ordering tier.** Confirm **ONE-R1024**, since R512 gives only 8 mice. Is **SR64 vs SR128** irrelevant to us (we never stimulate)? Is **R512 → R1024 a field firmware upgrade** or must it be specified at purchase?

**Q7. Exact part chain and quantities**, EXP port → Intan RHD2216, so we can put it on a purchase order without guessing. Can we reuse our existing 8 headstages and existing SAdpt-XDAQ-OM12 units?

### 🟡 Operational

**Q8. Ubuntu 24.04 headless setup.** A driver path exists; what we need is the **enrolment procedure** — group membership, udev rules for the Thunderbolt character devices, headless `boltd`. Which kernel and `boltd` versions does Kontex test against?

**Q9. Open Ephys plugin specifics.** Does it (a) bind **two XDAQ devices** in one instance, (b) enumerate a **Port Expander** so the 4 animals on a port appear as separately identifiable streams, (c) expose the **DB25 signals** (`DAQ ON`, `Sample CLK`, DI/DO) for our camera sync?
Also report: **XDAQ-OE v0.4.4-API10 has a packaging bug** — built for `shared/` while GUI 1.1.0 uses `shared-api10/`, so it fails to load until two symlinks are made by hand, and the fix must be re-applied after every reinstall. Is a fixed build coming?

**Q10. Our 36 cm analog run.** The electrode-to-headstage run is still ~36 cm against Intan's "ideally under 10 cm". Headstages sit at the chamber top and our slip ring is on the **analog** side, before the headstage. **What does Kontex recommend for this topology? Is there a head-mountable preamp option?**

**Q11. Physical layout.** With 2 boxes + 8 mains-powered Port Expanders + 32 chambers, the long run is rack-to-chamber. Our default is Port Expanders at the rack (short HDMI to the box, long run to the animal). **Which does Kontex recommend, and what is the maximum supported length on the long link?** What KonteX HDMI cable lengths exist?

**Q12. ⭐ Impedance polarity on the bipolar RHD2216 — we can only ever measure HALF of each electrode pair.** Added 2026-08-03, to send with the next batch.

The RHD2216 is bipolar: every amplifier takes two electrodes (`in0+`, `in0−`) and reports one difference. The chip **can** test either pin — Register 5 carries `Zcheck pol sel` precisely for this. But **neither piece of software we have exposes it**:

- **Radiens / Allego:** the gRPC impedance call is `ImpedanceRequest{port}` and returns one `zMag`/`zPhase` per channel. No polarity parameter anywhere in the API.
- **Open Ephys XDAQ-OE v0.4.4:** verified in the shipped binary. `Rhd2000Registers::setZcheckPolarity` **is compiled in** (`0x7a420`) but has **zero call sites**, while `setZcheckScale` (3), `setZcheckChannel` (1) and `enableZcheck` (1) are all called out of line from the impedance path. Its XML export carries one magnitude per amplifier and no polarity dimension.

⇒ Every impedance number this project owns is the **positive** input only. Our frontal EEG electrodes have been measured many times; **the parietal electrodes have never been measured at all.** This is not academic: B1 read 0.133 MΩ before Run 2, the best in the fleet, then ran fully open for 21.7 hours. An unmeasured negative electrode is a live candidate for that.

**The ask, in order of preference:**
1. Expose polarity in the **XDAQ-OE plugin** — run the existing pass twice with `setZcheckPolarity(ZcheckNegativeInput)` on the second, emit two values per amplifier. Small change to a plugin Kontex maintains.
2. If not the plugin, is there **any supported path** to reach Register 5 on our hardware (libxdaq, pylibxdaq, a scriptable register write)?
3. Failing both, confirm our reading of the chip so we can document the limitation honestly: on the RHD2216, does `Zcheck pol sel` select which of `inX+` / `inX−` the test DAC drives, and is the default the positive input?

Detail and evidence: [[impedance-sweep-register]], last section.

**Q13. Allego floods the log with IIR filter design errors whenever the Monitor band filter is changed.** Cosmetic as far as we can tell, but constant, and we would like it gone. Routing note: this one is Radiens/Allego, so it may belong with NeuroNexus rather than Kontex — worth asking Kontex anyway since XDAQ plus Allego is the bundle.

Three strings, from `~/.local/state/radiens/logs/radix.log` and `allegoserver.log`:

```
radix.py_bridge - ERROR - IirFilterDesign - py_bridge.dsp: Failed to design iir filter:
    Digital filter critical frequencies must be 0 < Wn < 1            (1142 in 77 min)
py_bridge.dsp: Failed to design iir filter:
    filter critical frequencies must be greater than 0                (208 in 42 s)
[KNL:cd14] failed to set dsp group  module=spikesorter
    error="DSP scraper/stage spike-sorter, fs=1000 - set DSP failed"   (40)
```

Root cause is visible one line earlier in the server log:

```
Created DSP ok  spec="DSP flow-thru [Port A/stage spike-sorter ()]  bandpass  fs=3e+04, f_cut=[3e+02, 6e+03]"
```

A **spike sorter** stage carries a hard-wired 300 to 6000 Hz band written for 30 kHz sampling. We run at 1 kHz, so it re-designs as `Wn = 6000 / 500 = 12`, which is illegal, and it fails on every filter change. **We do not use spike sorting at all — we record sleep EEG.**

**The ask:** can the spike-sorter stage be disabled, or suppressed for a sub-2 kHz configuration, so the log stops filling? We could not find a switch in the Signal Processing tab or the workspace file.

We have already established on our own bench that this does **not** touch the data: display band confirmed to apply (0.5 to 5 Hz test, trace visibly changes ⇒ rejection is per stage, not per group), and Allego filters never reach the saved `.xdat` (notch parked at 50 Hz, saved spectrum flat across 47 to 53 Hz). So this is log tidiness, not a data-integrity report. Detail: [[allego-iir-filter-design-errors]].

### ⚪ Only if time allows
AIO vs ONE+ — what is the integrated video processor, does it hardware-timestamp frames against the neural clock, and what is the price delta? · Can our Gen-1 Core serve as a third unit (+8 mice), or is there a trade-in? · Any customer running 16+ animals continuously for multiple days? · Warranty and RMA turnaround from Korea.

---

## §D. THE BUILD AND THE MONEY — fill in live

| # | Item | Part | Qty | Unit | Extended | ✓ |
|---|---|---|---|---|---|---|
| 1 | XDAQ ONE+, 1024 tier | ONE-R1024-SR64 | **2** | **⏳ THE UNKNOWN** | ⏳ | ☐ |
| 2 | Port Expander | SAdpt-Port-EXP | **8** | **$1,525** | **$12,200** | ☐ |
| 3 | Intan interface adapter | SAdpt-XDAQ-OM12(1) | **32** | **$275** | **$8,800** | ☐ |
| 4 | KonteX HDMI cable, box → Port Expander | ⏳ | **8** | ⏳ | ⏳ | ☐ length? |
| 5 | SyncLink | SyncLink | **0 or 2** | ⏳ | ⏳ | ☐ needed? |
| 6 | DB25 breakout board | ⏳ | 1–2 | ⏳ | ⏳ | ☐ |
| 7 | 200 W PSU + Thunderbolt cable | supplied | — | incl | — | ☐ |
| 8 | Acquisition PC | — | **1 or 2** | — | — | ☐ spec? |
| — | **PACKAGE PRICE, discounted** | — | — | — | **⏳ GET IN WRITING** | ☐ |

**Known so far: $21,000** (items 2 + 3). Everything else hinges on the ONE+ unit price.

**Not buying:** commutators (keeping slip rings) · Allego licence · C3442 splitters (cannot exceed the box ceiling and would undo the isolation).

---

## §E. WHAT WE MUST LEAVE WITH

1. ⭐ **The ONE+ unit price and a written package quote** to KAIST, with lead time
2. **Whether SyncLink is needed**, and if so how it behaves under the Open Ephys GUI
3. **Why two PCs**, and each machine's specification
4. **The exact part chain** EXP → RHD2216, with quantities
5. **Confirmation of the R1024 tier** and whether it is field-upgradable
6. **An answer on what the ground isolation is worth**, even if the answer is "unmeasured"
7. **Ubuntu headless enrolment procedure**
8. **A recommendation for the 36 cm analog run**
9. ⭐ **A yes or no on impedance polarity** (Q12) — whether we will ever be able to measure the second electrode of each bipolar pair in software. If the answer is no, we document it as a permanent limitation and rely on the multimeter instead
10. **A route to silencing the spike-sorter filter errors** (Q13), or confirmation that it belongs with NeuroNexus

---

## 📤 TO SEND 2026-08-04 — paste-ready

Two software asks, added 2026-08-03, to go out with the rest of the batch. Both
are written so they can be pasted straight into the email body.

> [!note] Routing
> **The polarity ask goes to Kontex** (their plugin, their hardware access path).
> **The Allego log ask is Radiens software**, so NeuroNexus may be the right
> owner, but send it to Kontex too since XDAQ plus Allego is the bundle they
> sell us. If Kontex bounces it, forward that one to NeuroNexus unchanged.

### Item 1 — impedance polarity on the bipolar RHD2216

```text
We use the RHD2216, which is a bipolar chip: each amplifier takes two electrodes
(in0+ and in0 minus) and reports their difference. For our sleep montage that
means one amplifier carries the frontal and parietal EEG pair, and another
carries the left and right neck EMG pair.

Our problem is that we can only ever measure one electrode of each pair. The
chip itself supports both: Register 5 carries a Zcheck polarity select bit,
which chooses whether the test current is driven into the positive or the
negative input. Neither piece of software we have exposes it.

In Radiens, the impedance call takes a port and returns one magnitude and one
phase per channel, with no polarity parameter in the API.

In the Open Ephys XDAQ plugin (XDAQ OE v0.4.4, API10) we checked the shipped
binary directly. Rhd2000Registers::setZcheckPolarity is compiled in, but it has
zero call sites, while setZcheckScale, setZcheckChannel and enableZcheck are all
called from the impedance path. The XML the plugin exports carries one magnitude
per amplifier and no polarity field. So the polarity bit is left at its default
and the same input is measured every time.

The consequence for us is concrete. Every impedance number in our records is the
positive input. Our frontal EEG electrodes have been measured many times, and
our parietal electrodes have never been measured at all. One animal read 0.133
megaohm before a run, the best value in the whole set, and then recorded an open
electrode for the full 21.7 hours. An unmeasured second electrode is a live
explanation for that, and at the moment we have no way to check it.

Three requests, in order of preference:

1. Could the XDAQ Open Ephys plugin expose polarity? Functionally this is
   running the existing measurement pass a second time with the polarity bit set
   to the negative input, and reporting two values per amplifier instead of one.

2. If not through the plugin, is there any supported way to reach Register 5 on
   our hardware, for example through libxdaq, pylibxdaq, or a scriptable
   register write?

3. If neither is possible, could you confirm our reading of the chip so that we
   can document the limitation accurately in our methods: on the RHD2216, does
   the Zcheck polarity bit select which of in0+ and in0 minus receives the test
   current, and is the power on default the positive input?

We are happy to test any build on our own Core.
```

### Item 2 — Allego IIR filter design errors

```text
Whenever we change the visualization band filter in the Allego Monitor tab, the
Radiens logs fill with filter design errors. Over one 77 minute session we
counted 1142 of them.

The three strings, from radix.log and allegoserver.log:

  radix.py_bridge ERROR IirFilterDesign, py_bridge.dsp: Failed to design iir
  filter: Digital filter critical frequencies must be 0 < Wn < 1

  py_bridge.dsp: Failed to design iir filter: filter critical frequencies must
  be greater than 0

  [KNL:cd14] failed to set dsp group, module=spikesorter, error="DSP
  scraper/stage spike sorter, fs=1000, set DSP failed"

The cause appears one line earlier in the server log:

  Created DSP ok spec="DSP flow-thru [Port A/stage spike sorter ()] bandpass
  fs=3e+04, f_cut=[3e+02, 6e+03]"

There is a spike sorter stage in the chain carrying a fixed 300 to 6000 hertz
band that was written for a 30 kilohertz sample rate. We acquire at 1 kilohertz,
so on redesign that band works out to a normalised frequency of 12, which is not
a legal filter, and the stage fails every time any filter is touched.

We do not use spike sorting at all. We record sleep EEG and EMG at 1 kilohertz.

Our question: can the spike sorter stage be disabled, or suppressed for a
configuration below 2 kilohertz, so that the log stops filling? We could not
find a switch for it in the Signal Processing tab or in the workspace file.

For completeness, we have already satisfied ourselves that this does not affect
our data, so please treat it as log tidiness rather than a data integrity
report. We confirmed on our own bench that the display band still applies (we
parked the Monitor band at 0.5 to 5 hertz and the trace visibly changed, so the
rejection is per stage and not per group), and that Allego filters never reach
the saved file (we parked the notch at 50 hertz, where nothing real lives, and
the saved spectrum is flat across 47 to 53 hertz).
```

---

## §F. NOTES DURING THE CALL

*(blank — fill live)*

---

## §G. APPENDIX — what we learned, and when

Kept out of the call flow deliberately. This is the audit trail, not the agenda.

| Date | Learned | Source |
|---|---|---|
| 2026-05-28 | Linux/driver questions routed to KC; ONE+/Core2/AIO are Thunderbolt, driver = stock `thunderbolt` + `boltd` | Kontex developer portal |
| 2026-07-14 | Dead top SPI socket is **by design** on the Core (MISO3/4 absent). Not a defect, do not RMA | NeuroNexus |
| 2026-07-18 | The 8-headstage Core ceiling is a hard wire-count limit | Jeff, NeuroNexus |
| **2026-07-21** | **First KC call.** Custom 4-socket adapter impossible · Port Expander recommended for per-mouse grounding · 2nd XDAQ = 2nd Allego seat · ~40 cm headstage run too long | KC Kong |
| 2026-07-23 | **Quote 262024, $10,002.89** — Port Expander retrofit for the **current 8-mouse Core only**. Port Expander $1,525, SAdpt-XDAQ-OM12 $275, SAdpt-CORE-OM12 $350. Valid to 2026-08-20, confidential | Kontex |
| 2026-07-23 | Open Ephys GUI **validated on our own XDAQ Core** (1 headstage, 32 ch). Found XDAQ-OE v0.4.4 packaging bug | Our bench |
| 2026-07-23 | Open Ephys reply 1: extension board **dead**; framed board as "max 4 animals"; RHD2216 supported; software free; **no isolation product** | Margarida, Open Ephys |
| **2026-07-28** | **KC confirms Intan headstages work with the Port Expander** → XDAQ un-blocked | KC Kong |
| 2026-07-28 | **The channel law**: mice = channels ÷ 64. ONE+ sold in R512 (8 mice) and R1024 (16 mice) tiers; ports are licence-gated. **Port Expander mandatory for 16/box** | NNX manual (not on the Kontex website) |
| 2026-07-28 | **Our Core has NO isolation at all** — "Signal Isolation: No", one power circuit for all 8 mice. Even ONE+ without an expander commons ports 2-4 | NNX manual p.9, p.22 |
| 2026-07-28 | Vendor **hedges** its own isolation claim: *"In theory... however... it is best for users to experiment with various ground settings"* | NNX manual §4.3 |
| 2026-07-28 | **Allego cannot schedule 16 animals independently** — per-port only, ports cap at 8, ONE+ has 4. "Split-ports mode" is documented nowhere → **do not buy the licence** | Radiens API docs |
| 2026-07-28 | Intan **no longer sells directly**; White Mountain Systems is sole distributor, no Korea presence, closed until 2 Aug, 90-day warranty | intantech.com |
| 2026-07-28 | Intan's isolation claim is **unspecified** — "isolated from the controller and from earth ground" names neither other ports; no barrier capacitance published | Intan user guide |
| 2026-07-28 | Literature: 4 mice on one **shared-ground** Open Ephys board, 48 h chronic, inter-animal correlation **at chance** | eNeuro 2022 |
| 2026-07-28 | Intan: analog electrode-to-headstage run **ideally under 10 cm**; headstage GND must **not** connect to the Faraday cage | Intan noise app note |
| **2026-07-28** | **Open Ephys reply 2: bipolar already gives independent per-animal REFERENCING.** Port Expander therefore adds **ground** isolation only → justify it as a **port multiplier**, not the 60 Hz fix. Also: 8 animals per board confirmed; per-animal ground isolation impossible on their hardware; global start/stop confirmed | Open Ephys support |
| 2026-07-29 | Port Expander is **mains powered** (5 V 1 A USB-C). The March 2024 manual's "battery powered" line describes an earlier revision | Kontex front-panel figure |

### Corrections we made to our own earlier beliefs
- ~~"Our 8 mice sit in isolated pairs"~~ → they share **one** power circuit across all four ports
- ~~"The radiens API gives per-animal scheduling"~~ → per **port**, and 16 animals do not map onto 4 ports
- ~~"Intan ports are confirmed isolated"~~ → implied, never stated port-to-port, no specification
- ~~"The Port Expander is battery powered"~~ → mains powered on the current revision
- ~~"Open Ephys board maxes at 4 animals"~~ → 8, vendor-confirmed in writing
- ~~"Shortening the analog run is free"~~ → lid-mounting is a published design; the real fix is head-mounted amplification, a rig redesign
- ~~"Proven on our own bench is a differentiator"~~ → dropped; all three products are built for this
