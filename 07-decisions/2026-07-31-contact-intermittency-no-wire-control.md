---
tags: [decision, eeg, 60hz, impedance, electrode-contact, intermittency, no-wire-control, critical]
created: 2026-07-31
status: active
priority: critical
---

# 2026-07-31 — Electrode legs are OPEN, not high impedance, and the state FLIPS on its own. Do not schedule new surgeries.

> [!danger] THIS OVERTURNS THE STANDING GUIDANCE
> The standing conclusion in [[eeg-60hz-saga]] and the memory index was: frontal electrodes are open on every mouse, implants CANNOT be reseated, therefore surgical yield is the critical path, therefore make new mice. **Today's evidence does not support that.** One mouse (C1) produced a clean, unclipped, physiological EEG pair, and it held steady through direct mechanical provocation. Meanwhile electrode legs were observed changing state SPONTANEOUSLY, mid recording, in half a second. **DO NOT schedule new surgeries on the old conclusion.**

## TL;DR

I spent the day taking the 60 Hz problem apart with the electricians standing in the room, and the answer is not what any of us expected.

- **The earth wiring the electricians installed changed nothing measurable.** Keep the bond, it is correct practice, but there was nothing to fix there. Released them.
- **The SPI splitter is now excluded by direct physical test**, not by inference. Pulled every splitter, ran the same measurement, same result.
- **All 8 animal grounds are good.** 128 internally tied control pins sat at a median of 7.2 µV of mains hum. The amplifier floor on this rig is about 7 µV, so there is NO elevated common mode and NO environmental problem.
- **22 of 32 electrode legs are electrically OPEN**, meaning statistically indistinguishable from an amplifier input with literally NO WIRE ATTACHED. This is the key new measurement and it is described in [[electrode-connection-state-test]].
- **Contact state FLIPS spontaneously.** I caught one leg going from 5869 µV to 11 µV, a 522× step, in 0.5 seconds, with nobody touching the rig.
- **C1 gave the project its first clean unclipped EEG pair.** 0.00 % clipping, 11.7 µV of mains hum on the bipolar pair, delta dominant, proper 1/f spectral falloff.
- **Impedance snapshots are NOT a valid go or no go gate any more.** They sample a bistable contact. One leg moved 102× in eleven minutes.

**Still open:** what actually causes the flips. I could not localise it, and I explicitly walked back one attempt to (see the retraction below).

---

## 1. What I measured and why it is trustworthy

Everything below rests on a control set that this project did not have before. Full method in [[electrode-connection-state-test]]. Short version, on every port:

| population | what it is | n (8 mouse run) |
| --- | --- | --- |
| **Legs** | real mouse electrodes, sites 1 to 4 and 33 to 36 | 32 |
| **CONTROL A, no wire** | real amplifier channels whose headstage pads have NOTHING attached, sites 5 to 16 and 37 to 48 | 96 |
| **CONTROL B, tied** | the internally tied empty half of each RHD2216, sites 17 to 32 and 49 to 64 | 128 |

Control A is the important one. It is a physically guaranteed open circuit, measured by the same instrument, in the same session, on the same chip. It tells me exactly what "open" looks like on THIS rig, so I no longer have to guess whether 5 MΩ means a bad electrode or no electrode.

### Method validation done first

- **The Allego notch filter does NOT reach the saved data.** I used the 50 Hz notch setting as a probe. Median across all 256 channels: 35 to 45 Hz = 7.9 µV, 45 to 55 Hz = 7.6 µV, 55 to 65 Hz = 63.5 µV, 65 to 75 Hz = 6.8 µV. Zoomed to 1 Hz bins across 47 to 53 Hz: 2.457, 2.504, 2.354, 2.401, 2.365, 2.462. Perfectly flat, NO null where the notch sits. The software filter is display side only, the `.xdat` holds raw. This retroactively validates every analysis in this session, and it answers a question that had been open in the vault.
- Units confirmed as `micro-volts` from the file metadata, not assumed. Clip threshold set at ±6300 µV against the real ±6390 µV rail.
- **Mains hum must be measured as a 55 to 65 Hz BAND, not a single 60.00 Hz FFT bin.** Mains is not exactly 60.00 Hz and it drifts, so the energy smears across bins. I made this mistake early in the day and it understated hum by 4 to 5×. Corrected everywhere below.

---

## 2. The headline result: legs match the no wire control

**8 mouse run**, 4 ports, splitters in:

| population | Z median | phase 20 to 170° | mains 55 to 65 Hz |
| --- | --- | --- | --- |
| CONTROL A, NO WIRE ATTACHED (n=96) | **5.233 MΩ** | 81 % | **2400 µV** |
| **Your 32 mouse legs** | **5.329 MΩ** | 66 % | **2667 µV** |
| CONTROL B, internally tied (n=128) | 0.043 MΩ | 0 % | 7.2 µV |

The median mouse leg is indistinguishable from a channel with nothing plugged into it.

Split the legs by behaviour and it sharpens further. The 22 loud legs sit at 86 % in the 20 to 170° phase band, matching Control A's 81 %. The 10 quiet legs sit at 20 %. Two clean populations, calibrated against physical ground truth.

**4 mouse run, ALL SPLITTERS PHYSICALLY REMOVED**, one headstage per port:

| population | Z median | phase 20 to 170° |
| --- | --- | --- |
| CONTROL A, no wire (n=48) | 4.764 MΩ | 73 % |
| **16 mouse legs** | **4.226 MΩ** | 56 % |
| CONTROL B, tied (n=64) | 0.096 MΩ | 0 % |

Same picture with the splitters gone. **The splitter hypothesis is now closed by direct test.**

---

## 3. Contact state flips on its own

### Observation 1, caught live mid recording

`B2 parietal`, during the 82 second 8 mouse recording, nobody touching anything:

```
60 Hz envelope, 10 s blocks (µV):
  4346  4369  3485  |  7  8  8  9  9
```

Transition at **t = 28.02 s**, spanning **0.5 seconds**, a **522× drop** from 5869 µV to 11 µV.

Before: rms 575 µV, 12.5 % clipping, open and acting as an antenna. After: rms 5.8 µV with NO biology, which is the amplifier floor. **It did not heal into a working electrode, it went from OPEN to SHORTED.** Both states broken, different flavours.

⚠️ **An electrode implanted in tissue does not change state 522× in half a second.** Tissue impedance does not do that, scar does not do that. That is metal losing or making contact with metal.

### Observation 2, across an hour

`B1 frontal` went **1.717 MΩ → 0.027 MΩ**, a 64× collapse from connected to dead short, in about an hour. This is the same animal whose parietal leg the vault records as "the best electrode contact this project has ever had" at 0.206 MΩ ([[experiment-pad7-floating-input-B1]]). Today that same parietal leg read 5.465 MΩ and then 6.695 MΩ, which is OPEN.

### Observation 3, chattering

`B1 frontal` later spent 55 continuous seconds bouncing between roughly 10 µV and 4400 µV, many times over, one second medians:

```
t=45 3471  46 444  47 18  48 12  49 2643  50 15  51 13  52 4152
t=53 3509  54 3775 55 3569 56 2972 57 3661 58 15  59 6   60 7
t=63 884   64 2665 65 2250 66 3763 67 1766 68 1430 69 13 70 3363
...continues bouncing through t=100
```

### Observation 4, the historical pattern finally explained

One leg moved **102×** between two impedance measurements eleven minutes apart (`B/34`, 0.061 → 6.231 MΩ), with nothing touched but the connector. Every impedance snapshot in this project has disagreed with the last one. **We were sampling a switch that flips on its own.**

---

## 4. C1: the first clean EEG, and it is mechanically solid

`C1`'s EEG pair, bipolar frontal minus parietal, 82 second run:

- mains hum **15 µV**, rms 83 µV, peak to peak 714 µV, **0.00 % clipping**
- delta 50.3 %, theta 18.8 %, alpha 6.2 %, beta 10.5 %, gamma 1.6 %
- 1/f sanity check: P(1 Hz) / P(10 Hz) = 8.7

> [!note] This is NOT a repeat of the 2026-07-15 mistake
> The 2026-07-15 "first sleep biology" result was retracted because it was a clipping artifact. **This channel clips exactly 0.00 % of samples.** That is the specific failure mode that forced the retraction, and it is absent here.

### The wiggle test, 101 s recording, C1 provoked directly

I had Andrea perturb one joint at a time while streaming: electrode 10 to 20 s, tether 30 to 40 s, slip ring wires 50 to 60 s, twisted the slip ring 70 to 80 s.

| phase | C1 frontal (µV) | C1 parietal (µV) |
| --- | --- | --- |
| quiet | 11.5 | 6.6 |
| **electrode** | 10.3 | 6.6 |
| quiet | 11.7 | 9.1 |
| **tether** | 13.0 | 8.6 |
| quiet | 14.0 | 8.9 |
| **slip ring wires** | 13.3 | 11.7 |
| quiet | 12.4 | 7.6 |
| **twist slip ring** | 10.9 | 7.2 |
| quiet | 11.4 | 7.4 |

Across the whole 101 s the frontal envelope ranged 2.2 to 30.3 µV, median 11.6. **Nothing we did moved it.**

Bipolar over the full 101 s: rms 65.0 µV, **mains 11.7 µV**, **0.00 % clipping**, delta 37.9 %, theta 27.7 %, alpha 7.7 %, beta 11.1 %, gamma 3.3 %.

Nice detail: theta was 18.8 % in the earlier resting recording and 27.7 % here, in a recording where the animal was being handled. Arousal and movement drive theta. I would not hang a paper on it, but the channel responds to the animal's state the way a real EEG channel should.

**So a correctly made connection on this rig is ROBUST.** You can grab the electrode, wiggle the tether, and twist the slip ring, and it does not flinch. That is a reference standard the project did not have before.

---

## 5. ⚠️ RETRACTION, made the same day

During the wiggle test, `B1 frontal` began chattering at about t = 45 s, near the slip ring manipulation, and never recovered. `A1` and `D1` did not move at all (A1 frontal held 5711 to 6250 µV, D1's EMG legs pinned to within a few µV across every phase), so it was NOT body coupling and NOT a global artifact.

I initially read this as evidence of a physical path between C1's slip ring region and B1's signal chain, and wrote that the fault was localised to the slip ring assembly.

**Andrea confirmed there is NO physical relationship between B1 and C1. That inference is RETRACTED.** The timing was coincidence and I over read it. Given that `B2 parietal` flipped 522× with nobody touching anything at all, spontaneous flips clearly happen on their own, and B1's chatter is most likely another one.

**What this costs us:** the fault is NOT localised. Provoking C1's electrode, tether and slip ring produced zero change, so those joints are cleared on that animal, but I have no positive evidence pointing at any specific joint on the others.

**What survives:** implants are not proven guilty, C1 proves the design can work and hold, and no surgery is justified on today's evidence.

---

## 6. The three states, and the trap

| state | Z | phase | mains | biology |
| --- | --- | --- | --- | --- |
| **OPEN** (antenna) | 1.2 to 10.6 MΩ | scattered | 500 to 8000 µV | none |
| **SHORTED** to ground | 0.04 to 0.34 MΩ | ~0° or ~180° | 7 to 146 µV | **none** |
| **WORKING** | 0.19 to 0.66 MΩ | ~0° or ~180° | 13 to 61 µV | delta 68 to 91 µV |

> [!warning] SHORTED LEGS LOOK BETTER THAN GOOD ONES ON HUM ALONE
> `A1 parietal` at 0.087 MΩ, `C2 parietal` at 0.139 MΩ and `D1 parietal` at 0.335 MΩ all read QUIETER than C1's good legs, and all three are DEAD, carrying 3 to 10 µV of delta. **Impedance alone cannot pass a channel. You must also confirm biology is present.**

### Correction to the phase criterion

I first proposed "open = Z > 1.5 MΩ AND phase 20 to 170°". **Phase is NOT reproducible between runs** and that rule is wrong. Same legs, same state class, phase all over the map: A1 frontal 140.4° → 33.3°, D1 frontal 36.4° → 140.1°, A1 EMG+ 144.7° → 17.5°, A1 EMG− 172.1° → 11.3°.

**Use MAGNITUDE alone**, calibrated against Control A's 10th percentile of 0.87 MΩ:

- **Z > 0.9 MΩ → OPEN**
- **Z 0.15 to 0.9 MΩ → connected**, confirm with biology before trusting it
- **Z < 0.15 MΩ → SHORTED**

---

## 7. EMG is a separate, near total failure

EMG legs failed **15 of 16** in the 8 mouse run and **8 of 8** in the no splitter run. That is **23 of 24 across two independent hardware configurations**.

This is systematic, not eight independent accidents, and it is a different problem from the EEG story. Candidates: how the leads are stripped and anchored in muscle, or the lead length acting as an antenna. Worth a dedicated bench test on one animal before any more surgeries.

**Consequence: ZERO fully scoreable mice today.** A scoreable animal needs a clean EEG pair AND a working EMG pair. C1 has the EEG and not the EMG.

---

## 8. Decisions taken

1. ✅ **Electricians released.** Earth bond stays, it is correct practice. No further electrical work is justified. Earth remains EXONERATED.
2. ✅ **Splitter permanently excluded**, by direct physical test.
3. 🛑 **NO new surgeries** on the current evidence.
4. 🛑 **Impedance snapshots are no longer a go or no go gate.** If used at all, take three back to back and read the VARIANCE, not the value.
5. ✅ **Both headstage maps are equivalent**, see §9.
6. ➡️ **Long multi hour recording started** to measure flip rate and per leg duty cycle. This is the first experiment able to quantify intermittency.

---

## 9. Housekeeping: the two headstage maps are IDENTICAL

The vault contained two active procedures giving different instructions:

- [[allego-electrode-setup-sleep64]] said headstage `usrdef_sleep64`, probe `usrdef_sleep64_probe`, "do NOT pick any other".
- [[eight-mouse-acquisition-setup]] said headstage `Passthrough 64`, probe `Default 8x8`, no local devices.

I diffed the files. `hstg__usrdef_sleep64.hstg` and `hstg__passthrough_64.hstg` contain **the exact same 64 native to site pairs**, both pure passthrough where site = native + 1. The md5 sums differ only because passthrough writes floats (`0.0`) and sleep64 writes ints (`0`). **Functionally there is zero difference, either is correct.** The sleep64 warning was aimed at the ARCHIVED repacking maps (`2mice32`, `dual_mouse_c3442`), not at `Passthrough 64`.

For one headstage per port with no splitter, the equivalent pair is **`Passthrough 32` + `Default 4x8`**, verified as 32 entries and pure passthrough, and confirmed as what Allego itself selects in that configuration.

---

> [!success] ANSWERED 2026-08-01 by the 27.9 h run — see [[2026-08-01-28h-contact-duty-cycle-and-c1-negative]]
> - ✅ **Whether C1 holds for hours: NO.** Connected 0 → 8.73 h, then OPEN for 1149 min and never recovers. The 101 s wiggle test was inside a genuinely good interval, but that interval ended.
> - ✅ **Flip rate and duty cycle: 78.7 % of all leg-time OPEN.** Yield = 8.7 usable EEG-pair hours from 223 mouse-hours = **3.9 %**, and **ZERO scoreable mice** because no animal had a working EMG pair at any moment.
> - ✅ **Do flips cluster or scatter: BOTH, and they are TWO DISTINCT MODES.** One-way irreversible degradation (C1 frontal, D2 frontal) versus chattering (B1 frontal ≥372 flips). Different faults, probably different fixes.
> - ✅ **Grounds hold for a full day:** 16 control pins, median 2.8 µV, max 5.3 over 27.9 h, no drift. Environmental causes CLOSED.
> - ⚠️ **NEW negative:** C1's clean window (99.9 % unclipped epochs) shows **NO sleep structure** — no bimodality, bout lengths identical to random, flat hourly profile. Still zero scoreable data.
> - ❌ Still NOT done: the 1 MΩ resistor validation of the Allego impedance check.

## 10. Still open

- **What causes the flips.** Micro motion inside the connector, thermal cycling, or something at the electrode tissue interface. I cannot separate these yet. A 0.5 s 522× step is hard to explain with tissue, but I have NO positive evidence pointing outside the head either.
- **Whether C1 holds for hours** or whether 101 s was just a long lucky interval. The multi hour run answers this.
- **Flip rate and duty cycle per leg**, which is the number that tells us how many scoreable mouse hours this rig actually yields.
- **Whether flips cluster in time**, which would suggest a shared cause, or scatter independently.
- **Why EMG fails at 23 of 24.**
- **The pad 7 floating input on B1** ([[experiment-pad7-floating-input-B1]], still not run) is now MORE interesting, since B1 is the animal that chattered. An unconnected slip ring wire sitting in a live amplifier input is a known antenna, and B1 is the mouse that has one.
- **Is the Allego impedance check itself trustworthy?** Never validated against a known resistor. Worth 5 minutes: put a 1 MΩ resistor between a headstage input and its GND pad and see if it reads 1 MΩ.

## Related

- [[electrode-connection-state-test]] — the reusable method, controls and thresholds from today
- [[2026-07-31]] — the day's journal
- [[60hz-mains-hum-discovery]] — Korea is 60 Hz, the notch was on the wrong line
- [[floating-cm-vs-contact-reconciliation]] — the CM × imbalance equation, still correct, today adds that many legs are fully OPEN rather than merely mismatched
- [[experiment-pad7-floating-input-B1]] — planned experiment, priority raised
- [[eight-mouse-acquisition-setup]], [[allego-electrode-setup-sleep64]] — reconciled in §9
- [[signal-quality-and-grounding]], [[headstage-shielding-faraday-foil]]
