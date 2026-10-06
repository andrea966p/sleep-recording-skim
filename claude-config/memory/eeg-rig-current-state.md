---
name: eeg-rig-current-state
description: "The active EEG problem in full detail — channel law, the three channel signatures, what is free vs impossible to fix, run results, and the retractions. Detail extracted from MEMORY.md 2026-08-03."
metadata: 
  node_type: memory
  type: project
  originSessionId: 73d8f40f-8fe5-4e49-9c74-3b734c900c35
  modified: 2026-08-04T07:57:03.809Z
---

Full detail for the EEG rig, extracted out of `MEMORY.md` on 2026-08-03 to keep the index small. `MEMORY.md` carries one-line pointers into this file. Related: [[eeg-60hz-saga]], [[eeg-analysis-pipeline]], [[light-schedule-and-circadian-validation]], [[electrode-failure-literature]].

> 🏆⭐⭐⭐ **SUPERSEDED IN PART, 2026-08-04. READ [[movement-dependent-contact-root-cause]] FIRST.**
> The root cause is a **movement-dependent mechanical contact**, not electrode or implant failure. B1 EEG measured **0.052 MΩ with the mouse still vs 8.649 MΩ moving** — same animal, same port, same session, 166×. 0.052 MΩ is the best number ever recorded on this rig.
> **What that changes in this file:** every impedance number below measures **posture, not hardware**, and none of them is evidence about electrode condition. The "electrodes are failing / progressive loss" framing is WRONG. The free-vs-impossible fix hierarchy is obsolete: the rig-side items are all done and clean ([[dmm-continuity-test-result]]), and the fix is **mechanical** — strain relief, tether weight and counterbalance, connector retention, cable drag on the headcap. **Still absolutely no surgery, and now for a positive reason: the implants are proven good.**

## 🛑 Hard rules — never violate

- **NEVER SUGGEST "RESEATING" AN ELECTRODE/EMG WIRE — IMPOSSIBLE AFTER IMPLANTATION.** Only animal-side option = change tether = **ISOFLURANE, RUINS THE BATCH**. Hierarchy: **(1) FREE = rig-side of the slip ring** (swap headstage/port, inspect+resolder **C3410 pads**, **DMM slip-ring wires**); (2) expensive = tether; (3) impossible = implant → new mice.
- **"Make new mice" is SUPERSEDED — DO NOT schedule surgeries.**
- 🛑 **STOP QUOTING "~6% yield".** Both runs were commissioning tests, 2-6 d early vs our own ≥14 d SOP and ~1 d vs ≥7 d habituation. C1 is MORE impressive for it.
- 🔴 **REM NOT RELIABLY SEPARABLE — never report a REM share.** Percentile rule forces 20%, Otsu gives 24-48%, literature <10%. Report WAKE vs NREM + REM-entry-from-NREM only.
- **Signals are ALREADY bipolar — NEVER subtract EEG from EMG.**

## Channel law — SETTLED

⭐⭐⭐ Vault `02-procedures/CANONICAL-allego-channel-selection.md` **IS THE ONE PAGE. If any other page disagrees, it's stale.**

**SELECT `/1`,`/2`,`/33`,`/34` PER PORT = 16 ch for 8 mice.** Mouse wired to C3410 pads 0,1,2,3 + GND only. **PADS PAIR INTO AMPS:** pad0(`in0+`)=EEG frontal-L + pad1(`in0−`)=EEG parietal-L ⇒ amp0 = `/1` = **EEG**; pad2(`in1+`)=EMG-L + pad3(`in1−`)=EMG-R ⇒ amp1 = `/2` = **EMG**. Both ALREADY bipolar — chip subtracts before the ADC. 2nd mouse at `/33`,`/34` because the C3442 splitter puts 2 chips/port × 32 slots. Datasheet: "16 amplifiers … in0+, in0–, in1+, in1–"; "32 amplifiers … **only ch 0-15 active in the RHD2216**". **PROVEN 3 WAYS 2026-08-03** (datasheet · recorded `sensors_by_port` · measured all 64 slots on all 4 ports). ✅ `pipeline/derive_layout()` already correct.

🔴 **Allego map: `usrdef_sleep64` and built-in `Passthrough 64` are BYTE-EQUIVALENT — EITHER is correct** (the old "do NOT pick any other" warning meant the ARCHIVED repacking maps in `~/radix/devices/_archive_old_maps/`). Passthrough = site=native+1 → Mouse A ch 1-4, Mouse B 33-36. **No splitter (32 ch/port) = `Passthrough 32` + `Default 4x8`, select `/1-/4` only** (2nd mouse lands on natives 0-3, NOT /33-/36). Allego does NOT auto-pick a probe for passthrough. SOP: vault `02-procedures/allego-electrode-setup-sleep64.md`.

## 🔑 The three channel signatures (measured)

| state | rms | 60 Hz mains | other |
|---|---|---|---|
| **connected** | 30-90 µV | **6-20 µV** | structured spectrum, Z 0.07-2 MΩ |
| **floating / open** | 200-4700 µV | **150-4500 µV** | Z 5-9 MΩ |
| **inactive slot** | ~30 µV | **~3 µV** | HF ~93% flat, Z ~0.06 MΩ (internally tied) |

⚠️ **rms alone CANNOT separate connected-EMG from inactive slot** (both ~30 µV) — need mains + spectrum. ⚠️ **An unwired amp input and an open electrode are INDISTINGUISHABLE** (both float, both huge mains). Old `EEG=n0−n1` computed EEG minus EMG; 24 "failed EMG surgeries" were empty pads. **EMG mostly worked; EEG `/1` is the real failure.**

## 🔑 The bottleneck

**ELECTRICAL CONTACT, nothing else is close.** OPEN electrode = **36 of 41** animal-recordings (SHORTED 3, other 2). Median EEG mains **3379 µV** vs 300 µV limit; only 5/41 below it. **HUM IS A DIRECT READOUT OF CONTACT: connected 9-90 µV, open 1000-4700 µV (~100×, cleanly bimodal).** `differential_60Hz ≈ common_mode × electrode_Z_imbalance`.

✅ **RIG EXONERATED:** `allego_1__uid0629-12-05-09` = 9 µV hum, **100% gate pass**, 4.55 h unbroken — flawless (not scoreable: 96.7% wake = probable first-tethering acclimatisation).

🔴 **Contact FLIPS ON ITS OWN** (522× in 0.5 s); no-wire control proves 22/32 legs NOT CONNECTED (5.329 vs 5.233 MΩ control). Grounds 8/8 good, floor ~7 µV. **RULED OUT: splitter, slip-ring rotation, grounded brick, earth, environment.** FOIL works; **do NOT ground it**.

## 🔴🔴 Only half of each electrode pair has ever been measured

RHD2216 bipolar; chip CAN test either pin (datasheet Reg 5 `Zcheck pol sel`) but **Radiens exposes NO polarity** (gRPC = `ImpedanceRequest{port}` → one `zMag/zPhase` per chan). Default `pol_sel=0` ⇒ all our numbers = **inX+ only; the NEGATIVE electrode never measured.** ⭐ **EXPLAINS B1** (0.133 MΩ yet open 21.7 h). **FIX = DMM each C3410 pad vs GND pad** (free, sees negative side).

## ⭐ The free diagnostic

**A1 & D1: EMG perfect + EEG open through the SAME tether/slip-ring/board/headstage/port ⇒ shared path PROVEN GOOD → check pads 0/1 solder + the 2 EEG slip-ring wires (pads 2/3 = built-in control).** ⚠️ **The EEG/EMG asymmetry does NOT prove an implant fault** — a cold joint on pad 0/1 gives the same pattern. Rule out the free tier before blaming surgery.

⭐ **B1 = the fleet's BEST EEG but its EMG is dead; A1+D1 = perfect EMG, zero EEG.** Fixing either side doubles scoreable time → drives the tier-1 bench test.

⚠️ Bench test = **DISCRIMINATOR, not confirmation**: EEG = dura pin (82% literature failure), EMG = wire anchored in muscle (no comparable failure) — they do NOT share an electrode, so "EMG works ⇒ it's our solder" does not follow. See [[electrode-failure-literature]].

## Run results

- ✅ **RUN 1 (07-31, 27.9 h `allego_1__uid0731-18-06-37`):** C1 **8.73 h**, single **8.1-hour unbroken block**, r@1min +0.744 / @5min +0.583 / @10min +0.435, physiology PASS. C2 also qualifies (1.69 h in-blocks, r +0.532, phys PASS) = **genuine n=2**.
- ✅ **RUN 2 (08-02, 21.74 h `allego_2__uid0802-01-46-57`): 0/8 scoreable, 8/8 OPEN.** Pre-reg **4 HIT / 3 MISS / 1 VOID** — impedance predicts **CLASS not YIELD**. Report `05-experiments/completed/2026-08-03-data-quality-report-for-professor.md`.
- ⭐ **FULL RESCORE OF EVERY RECORDING (2026-08-03): only ONE recording has real sleep.** 8 recordings / 41 animal-recordings / ~174 animal-hours → **~10.4 scoreable mouse-hours, ALL from 2026-07-31.** D2 correctly REJECTED (r=0.250 + phys FAIL). **72 h run and 20 h run = ZERO.** ⚠️ **6 "recoveries" found with the buggy metric were ALL FALSE** and discarded.
- ✅ **TIMELINE: surgery 21-23 Jul, tethered 30 Jul → Run 1 = day 8-10 post-op / ~28 h tethered.** BOTH RUNS WERE COMMISSIONING TESTS.

## Retractions

- 🛑 **2026-07-15 "first sleep biology" (td_sep −0.65) RETRACTED** — clipping artifact, 1/493 clean epochs, flips to +0.63 when railed epochs excluded. `earthing-60hz-hum-fix.md` retracted entirely (wrong device).
- 🛑 **Frontal-sinus hypothesis DROPPED** (built on the wrong channel map).
- ⚠️ **Do NOT cite Kappenman for our hum result** (they tested 5 vs 50 kΩ, we test connected vs OPEN).
- 🔴 **SCORING BUG #2 — persistence measured ACROSS TIME GAPS.** `gate_and_score_all.py` computed `r@1min` as `np.correlate(...)[15]` on the GATED array — lag 15 = 60 s ONLY if contiguous. FAILED BOTH WAYS: run2 C2 `+0.078` (impossible to pass) vs 07-13 D2 `+0.854` (its longest block is 39 min of 100% WAKE). Fix = within-block autocorrelation, in `stage3_features.py` and `scripts/rescore-v2-2026-08-03/rescore_v2.py`. `gate_and_score_all.py` SUPERSEDED.

## Hardware durables

Chip = **RHD2216** bipolar, `REF` empty by design; one 16-ch chip, Allego shows 32/port (natives 16-31 = empty floor). **Bottom SPI socket ONLY** — top dead BY DESIGN on XDAQ Core (NOT a defect, DON'T RMA): Core HDMI carries only MISO1/2, so the top socket's MISO3/4 are physically absent. **8-headstage ceiling is a HARD Core limit**; past 8 needs One+/AIO, not more adapters. **ONE mouse per headstage.** Animal ground = green → board `GND` pad. Headstages at chamber TOP, ~36 cm analog run.

**Surgery:** dedicated animal-ground dura/bone pin per mouse; EMG leads in muscle, tips stripped, anchored; clean sockets of dried blood before tethering; pre-closure DMM continuity + GUI impedance. Montage per Iwasaki/Funato/Yanagisawa 2021 (IIIS Tsukuba): bipolar LEFT EEG (frontal+parietal) + neck EMG, no cerebellum ref. EDF+ = scorer handoff.

**Prior validated:** 14.23 h 2-mouse stress test byte-perfect (82°C); 72 h run byte-perfect → endurance PROVEN.


## From the memory index, trimmed there 2026-10-06 (kept here verbatim)

- 🔴⭐⭐ **[FULL EEG RIG STATE](eeg-rig-current-state.md).** Channel law, signatures, retractions. ⚠️ Electrode-failure framing SUPERSEDED by the ground root cause.
