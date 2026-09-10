---
name: eeg-60hz-saga
description: "The full 60Hz-hum / earth / contact / foil investigation — root-cause equation, what's proven, what's refuted, and the go/no-go gate"
metadata: 
  node_type: memory
  type: project
  originSessionId: 01d67996-fc6d-445a-b14a-bb600afc0cf8
  modified: 2026-07-22T01:20:41.006Z
---

🛑 **2026-08-02 CORRECTION — "RESEAT THE HEAD CONNECTOR" IS NOT A THING. NEVER SUGGEST IT.**
- **You CANNOT reseat an implanted electrode or EMG wire.** Only animal-side option = **change the tether**, which needs **ISOFLURANE** ⇒ animal stress + **RUINS THE BATCH mid-experiment**. Never do it casually or "to see if it helps".
- **INTERVENTION HIERARCHY:** **(1) FREE, no animal contact** = anything RIG-side of the slip ring: swap headstage · swap port · inspect/resolder **C3410 pads** · **DMM the slip-ring wires** · swap boards between animals. **(2) EXPENSIVE** = change tether (isoflurane, ruins batch) — needs a pre-argued reason. **(3) IMPOSSIBLE** = implanted wires/electrodes → new mice only.
- ⭐ **THE RIGHT FREE TEST — A1 and D1.** Both have **EMG connected 27.9h (0.087 / 0.202 MΩ)** and **EEG open the whole time (4.446 / 3.980)**, through the **SAME tether, slip ring, C3410 board, headstage, port**. ⇒ **their shared infrastructure is PROVEN GOOD by their own working EMG.** The EEG fault must lie in something channel-specific: **C3410 pads 0/1 solder joints ✅ accessible · the 2 EEG slip-ring wires ✅ accessible · slip-ring contacts ✅ accessible** · head-connector pins ❌ · implanted wires/electrodes ❌. **3 of 5 candidates are FREE to test, with pads 2/3 as a built-in working control.**
- ⚠️ **THE EEG/EMG ASYMMETRY DOES *NOT* PROVE AN IMPLANT FAULT.** A cold solder joint on pad 0/1 or ONE broken slip-ring wire gives the identical pattern. **RULE OUT THE FREE TIER BEFORE BLAMING IMPLANTS OR SCHEDULING SURGERY.**
- Procedure (~30 min, no animal): DMM continuity C3410 pad 0 & 1 back through the slip ring vs known-good pads 2 & 3 · inspect/reflow pad 0/1 joints under magnification · swap headstage, re-sweep · swap port, re-sweep. Only if all clean is the fault upstream of the slip ring.


⏳ **RUN 2 IN PROGRESS — started 2026-08-02 01:46:57 KST, `allego_2__uid0802-01-46-57`.** First run with the CORRECTED selection (`/1,/2,/33,/34` per port = 16 ch; verified in file metadata). **PREDICTIONS PRE-REGISTERED BEFORE ANY DATA: vault `05-experiments/active/2026-08-02-run2-preregistration.md` — fill in HIT/MISS, DO NOT edit the predictions.**
- **Pre-flight impedance predicts only 1/8 fully scoreable = C2** (EEG 1.146 / EMG 0.168). D2 marginal (EEG 2.114). B1 = EEG only (0.133, best on rig) but EMG dead 7.099. A1/C1/D1 = EMG only. A2/B2 = nothing.
- ⚠️⚠️ **CONTACT STATE MOVES IN *BOTH* DIRECTIONS OVER DAYS, with NOTHING done to the animals:** B1 EEG **1.717→0.133 (13× BETTER)** · C2 EEG 4.418→1.146 (open→conn) · **C1 EEG 0.465→5.720 (our best mouse LOST its EEG)** · D2 EEG 0.660→2.114. **Channels RECOVER as readily as they fail** ⇒ a deliberate reseat has a real chance.
- **RESEAT WAS RECOMMENDED AND NOT DONE** (B1 EMG; A1/C1/D1 EEG — each ONE channel short of scoreable, partner channel excellent). **This is now the highest-value outstanding action** if run 2 confirms ~1 scoreable mouse.
- ⭐ **KEY PREDICTION P8: if the run exceeds ~29 h, at least one mouse yields LIGHT-PHASE data and its NREM % will EXCEED its dark-phase NREM %.** No light-phase data with a living EEG has EVER been obtained. This is the strongest available independent confirmation that we measure real sleep.
- 🔴 **BLOCKER: the animal-room LIGHT SCHEDULE is still undocumented** (blank block waiting in vault `00-config/production-values.md`). **P8 CANNOT be evaluated without it — get lights-on/lights-off from the facility.**
- **ON STOP: take a SECOND impedance sweep IMMEDIATELY.** Two sweeps bracketing the run distinguish progressive degradation from random flipping = connector vs implant.


✅ **2026-08-02 IMPEDANCE VERDICT REVERSED — IT IS A VALID PRE-FLIGHT GATE.** The 2026-07-31 "impedance snapshots are NOT a go/no-go gate" was an artifact of the WRONG CHANNEL MAP (half the scored "electrodes" were bare pads).
- Read **ONLY `/1`(EEG) and `/2`(EMG)** — never include `/3`,`/4`. Against hours-of-usable-data from the 27.9h run: **spearman ρ = −0.941, p = 5.7e-08**, from a sweep taken ~2h BEFORE recording.
- **THRESHOLD: Z < 2 MΩ = connected (14/16 correct); Z > 3 MΩ = open.** (0.9 MΩ gives 13/16.) A mouse needs BOTH `/1` and `/2` under threshold to be scoreable.
- **Values wobble severalfold but CLASSIFICATION IS STABLE** (B1 EEG 0.222→0.623 = 2.8×, still CONN→CONN; pads 5.38→3.63, still OPEN→OPEN). **CLASSIFY, DO NOT QUOTE THE NUMBER.** A channel whose CLASS flips between back-to-back sweeps is genuinely intermittent — that IS the finding.
- The infamous **102× swing was REAL INFORMATION**: it was B2's EMG, which worked only 1.4h/27.9h. The sweep correctly flagged a flaky channel; it was misread as instrument noise.
- **Empty pads `/3,/4` median 5.902 MΩ vs no-wire control 5.557 MΩ** ⇒ independent impedance-side confirmation of the bipolar map.
- ⭐ **PRE-FLIGHT SOP: sweep impedance before every run, read `/1,/2,/33,/34`, predict yield in advance instead of after 28h.**
- **Allego channel SELECTION is display/QC only — the file saves ALL primary channels of every enumerated port regardless.** Selecting `/1,/2,/33,/34` loses nothing; controls stay available.


🔴 **2026-08-02 FULL 8-MOUSE RESCORE (corrected map + 3-part gate) — D2 WITHDRAWN, REPLICATION IS n=2.** Vault `05-experiments/completed/2026-08-01-channel-mapping-correction-first-sleep.md` §3c, journal `04-journal/2026-08/2026-08-02.md`.
- **SCOREABLE: C1 8.73h (W 64.4/NREM 31.2/REM 4.4, PASS) · C2 4.02h (56.3/35.7/8.1, PASS but WEAK — NREM/WAKE delta only 19.6 vs 17.9 %).** ⚠️ **D2 FAILS physiology** (WAKE EEGrms 75.9 > NREM 72.3; delta 41.6 ≈ 42.1; REM EMG 27.4 > NREM 12.4) — it only passed on 2026-08-01 because it was scored on a hand-picked window with **C1's** hand-picked 25 µV EMG threshold. **NEVER reuse a threshold derived from one animal on another.** **A1, A2, B1, B2, D1 = INSUFFICIENT (0.00-0.07h).**
- ⭐ **B1 HAS THE BEST EEG IN THE FLEET — 11.8h at median 66.7 µV — AND IS UNSCOREABLE BECAUSE ITS EMG IS DEAD (0.2h).** 11.8h of data blocked by ONE channel.
- **COMPLEMENTARY FAILURE = the actionable finding: A1 and D1 have PERFECT EMG 27.9h and ZERO EEG; B1 has excellent EEG and no EMG.** Fix either side on those 3 animals ⇒ scoreable time roughly DOUBLES.
- **Per-mouse EEG good/EMG ok (h):** A1 0.0/27.9 · A2 0.0/0.0 · B1 **11.8**/0.2 · B2 0.0/1.4 · C1 8.7/27.9 · C2 4.2/26.8 · D1 0.0/27.9 · D2 4.2/27.8. **EEG failures are OPEN not shorted** (shorted only 4.3h across all 8).
- **28.9h good EEG exists · 17.0h overlaps working EMG · 12.75h passes physiology.** ALL scoreable windows 18:06-02:50 ⇒ **STILL NO LIGHT-PHASE DATA WITH A LIVING EEG.**
- **METHOD HARDENED:** (1) **3-PART GATE** = not open (mains<300µV both ch) AND **not shorted (EEG rms ≥25 µV)** AND not clipped — hum alone let shorted windows through; (2) **Otsu threshold per animal**, no hand-picked constants; (3) **verify persistence vs shuffle BEFORE reporting any hypnogram** — else report "NO STRUCTURE"; (4) **automatic physiology PASS/FAIL** — this is what caught D2. Scripts `score_all_mice.py` + `gate_and_score_all.py`.


⭐⭐🔴 **2026-08-01 BREAKTHROUGH — THE CHANNEL MAP WAS WRONG ALL ALONG. EMG ALWAYS WORKED. FIRST REAL SLEEP ARCHITECTURE.** Vault `05-experiments/completed/2026-08-01-channel-mapping-correction-first-sleep.md`. **READ BEFORE TRUSTING ANY EARLIER EEG/EMG NUMBER IN THIS FILE.**
- **RHD2216 IS BIPOLAR — each channel already reports its own `+`/`−` difference.** C3410 **pads 0+1 = ONE channel (native 0)**, **pads 2+3 = ONE channel (native 1)**. 4 pads → **2 channels, NOT 4**.
  - `native0` = Allego **`/1`** (mouse B: `/33`) = **EEG**, already bipolar → **use directly**
  - `native1` = **`/2`** (`/34`) = **EMG**, already bipolar → **use directly**
  - natives 2,3 = **`/3`,`/4`** (`/35`,`/36`) = **EMPTY PADS, NO WIRE BY DESIGN**
  - ❌ OLD WRONG: `EEG=native0−native1` (that is **EEG minus EMG**), `EMG=native2−native3` (empty pads).
  - **In Allego select only `/1,/2,/33,/34` per port = 16 ch for 8 mice, not 32.**
- **CAUGHT BY ANDREA REFUSING AN IMPLAUSIBLE RESULT** ("professor did the surgeries, impossible that ALL EMG failed, we're looking at the data wrong"). **LESSON: an implausible result is a bug report about your own method — audit the channel map FIRST.** The no-wire control already held the answer; `/3`,`/4` matched it **because they ARE no-wire**.
- **EVIDENCE (4 tests):** corr(`/1`,`/2`) = **r −0.003 raw / +0.000 in-band** (single-ended neighbours would correlate → independent differential pairs) · burstiness 70-300 Hz CV **0.79 vs 0.21** · `/2` muscle power vs `/1` delta **ρ = −0.285** · `/3`,`/4` identical to no-wire controls. Chip metadata is EMPTY in `.xdat` (`port_map` all null) so this had to come from the signals. ⚠️ Still worth confirming physically against the headstage wiring.
- ⭐ **C1 SLEEP ARCHITECTURE (8.70 h, 7829 epochs of 4 s, 99.9 % clean): WAKE 66.8 % / NREM 29.3 % / REM 3.9 %.** Physiology ALL correct: NREM delta 41.6 % + EEGrms 68.9 µV (highest) + EMG 15.1; REM th/de **1.90** + EMG **13.2** (lowest); WAKE EMG **48.3** (highest). Persistence **r +0.898@4s, +0.803@1min, +0.636@5min, +0.484@10min vs shuffle +0.014** (old wrong map gave +0.086@2min). Bouts WAKE mean 117.5 s (max 2284), NREM 34.5 s, REM 8.6 s (random = 8 s). Hourly wake **14.6 %→97.9 %**, NOT flat.
- **CORRECTED FLEET:** open time **61.6 %** (not 78.7) · **EMG works 5/8 mice** (A1,C1,C2,D1,D2 at 0-4.2 % open) · **EEG `/1` fails 8/8 (61.8-100 % open) ← THE REAL PROBLEM** · **21.0 SCOREABLE MOUSE-HOURS** (C1 8.7 h, C2 7.0 h, D2 5.3 h), **NOT ZERO**.
- 🐛 **SECOND BUG:** `nperseg=512` at 1 kHz → df 1.95 Hz → theta 6-9 Hz = **ONE FFT bin** → `np.trapz` returns **EXACTLY 0**. Use **`nperseg=2048`** (df 0.49). Encoded as a loud comment in `score_sleep_corrected.py`.
- **RETRACTED:** "EMG failed 23/24 & 16/16" · "ZERO scoreable mice" · "C1 shows NO sleep structure" · "78.7 % open" · the "frontal vs parietal" framing (it was EEG vs EMG channels).
- **STANDS:** no-wire control method · grounds 2.8 µV no drift over 27.9 h · environmental causes closed · contact intermittency + one-way degradation (but it is the **EEG** channel dying: C1 at 8.73 h, D2 at 5.30 h).
- **CAVEATS on the sleep result:** n=1, 8.7 h, dark phase; thresholds data-driven (EMG dip 25 µV, th/de 80th pct) NOT scorer-validated; REM bouts 8.6 s ⇒ REM% provisional. Positive-control on a public scored dataset still owed.
- **NEXT:** replicate on **C2 (7.0 h) and D2 (5.3 h)** → n=3 · all hardware effort to the **EEG channel `/1`** · still NO new surgeries · script `02-procedures/eeg-data-analysis/scripts/contact-state-2026-07-31/score_sleep_corrected.py`.


🔴⭐ **2026-08-01 — 27.9h RUN (⚠️ NUMBERS BELOW USE THE WRONG CHANNEL MAP, see breakthrough block above) (`allego_1__uid0731-18-06-37`, 105GB, 8 mice) ANSWERS THE DUTY-CYCLE QUESTION.** Vault `05-experiments/completed/2026-08-01-28h-contact-duty-cycle-and-c1-negative.md`, journal `04-journal/2026-08/2026-08-01.md`, **CODE IN VAULT** `02-procedures/eeg-data-analysis/scripts/contact-state-2026-07-31/`.
- ✅ **ENVIRONMENTAL CAUSES NOW CLOSED FOR GOOD.** 16 tied control pins over 27.9h: **median 2.8 µV, max 5.3, zero drift** across a full light/dark cycle. All 8 headstages identical (2.5-3.1). Do NOT revisit earth/room/splitter/grounding.
- 🔴 **78.7 % OF ALL LEG-TIME WAS OPEN.** Parietal legs 0-4 % open, **frontal legs 62-100 %**, **ALL 16 EMG legs 88-100 %**.
- 🔴 **TWO DISTINCT FAILURE MODES.** (A) **ONE-WAY IRREVERSIBLE DEGRADATION** — C1/front CONN 0→8.73h then OPEN 1149 min, never returns; D2/front same at 5.30h. Directional ⇒ progressive (drying/creep/fatigue), NOT bouncing contact. (B) **CHATTERING** — B1/front ≥372 flips, C2/front ≥165, B2/EMG+ ≥147.
- ⚠️ **C1's 8.7h window is the CLEANEST DATA EVER (99.9 % epochs zero-clipped, 3129/3131; mains 10.8 µV; rms 62.5 µV) BUT SHOWS *NO SLEEP STRUCTURE*.** Bimodality NEGATIVE (one smooth peak). **Bout lengths median 20 s = EXACTLY the random expectation** (decisive). Autocorr real but wrong scale (r +0.41@10s → ~0 by 10 min; shuffle +0.011). Hourly profile FLAT. POSITIVE control: rms rises 58.7→75.2 µV with delta quartile ⇒ plausibly real EEG, just no states. **Caveats: C1 EMG open 100 %, and 18:06-02:50 is dark/active phase — but a mouse still has sleep bouts, so LOGGED AS A NEGATIVE, not "inconclusive".**
- 📉 **YIELD: 8.7 usable EEG-pair hours / 223 mouse-hours = 3.9 %. ZERO scoreable mice** (no animal had a working EMG pair at ANY moment). **STILL ZERO SCOREABLE DATA.**
- **METHOD (reusable for 100GB+ files):** `.xdat` is sample-interleaved ⇒ any column subset still reads ALL bytes (~630 MB/s). Continuous full-rate pass measured **0.6 % in 90 s ≈ 4 h** → ABANDONED. **TWO-PASS: sample 10 s every 60 s for the survey, then re-read only the window of interest at full 1 kHz.** ⚠️ **Flip counts from pass 1 are LOWER BOUNDS** (flips inside the unobserved 50 s are invisible). Mains = **55-65 Hz BAND**; `sosfiltfilt` 4th-order Butterworth SOS (zero-phase, transitions not smeared); 5 s pad per side discarded. `OPEN_UV=300 µV` sits in the empty gap of the bimodal distribution — **swept 150-600 µV, headline moves only 80.3→76.8 %**, BUT **5 chattering legs ARE threshold-sensitive (B1/front, B2/EMG±, C2/front, D2/pariet) → ±15 pts, don't quote them precisely.** Clipping gate BEFORE any statistic (2026-07-15 lesson encoded; refuses <60 clean epochs).
- **NEXT:** inspect C1/D2 frontal connections physically while fresh · EMG bench investigation (16/16 open — this ALONE guarantees zero scoreable animals) · **1 MΩ resistor validation of Allego Zcheck STILL NOT DONE** · still NO new surgeries.


🔴⭐ **SUPERSEDED IN PART 2026-07-31 — "FRONTAL ELECTRODES ARE OPEN ON EVERY MOUSE → MAKE NEW MICE" IS NO LONGER SUPPORTED. DO NOT SCHEDULE SURGERIES ON IT.** Vault: `05-experiments/completed/2026-07-31-contact-intermittency-no-wire-control.md`, method `02-procedures/electrode-connection-state-test.md`, journal `04-journal/2026-07/2026-07-31.md`.
- **NEW CONTROL that changes the interpretation:** every port has amplifier channels with NO WIRE ATTACHED (sites 5-16 / 37-48). They read **Z median 5.233 MΩ, mains 2400 µV**. The 32 mouse legs read **Z median 5.329 MΩ, mains 2667 µV** = STATISTICALLY IDENTICAL. So 5-8 MΩ means **NOT CONNECTED**, not "high-impedance electrode". 22/32 legs OPEN.
- **CONTACT STATE FLIPS SPONTANEOUSLY**: B2 parietal 5869→11 µV (**522×**) in **0.5 s** mid-recording, untouched; B/34 **102× in 11 min**; B1 frontal 1.717→0.027 MΩ (64×) in ~1 h. ⇒ **IMPEDANCE SNAPSHOTS ARE NOT A GO/NO-GO GATE.** Use variance across 3 back-to-back reads.
- ⭐ **FIRST CLEAN UNCLIPPED EEG PAIR: C1.** Bipolar mains **11.7 µV**, **0.00 % clipping**, rms 65 µV, delta 37.9 % / theta 27.7 %, 1/f ratio 8.7. NOT a repeat of the 2026-07-15 clipping artifact — clip is exactly zero. **Survived direct provocation** (electrode, tether, slip-ring wires, slip-ring twist): envelope 2.2-30.3 µV, unmoved ⇒ a properly made connection IS robust.
- **COMMON MODE IS NOT THE PROBLEM ANY MORE**: 128 internally-tied control pins at **median 7.2 µV**; all **8/8 animal grounds good** (floor medians 6.5-8.3 µV). Amplifier floor ≈ 7 µV. Earth again showed NO benefit → electricians released, bond kept.
- **SPLITTER now excluded by DIRECT PHYSICAL TEST** (all splitters pulled, legs still match no-wire control), not just inference.
- **3-STATE CLASSIFIER (magnitude ONLY — PHASE IS NOT REPRODUCIBLE, it swung 140°→33°, 36°→140° on the same legs):** Z>0.9 MΩ = OPEN · Z 0.15-0.9 = connected · Z<0.15 = SHORTED. ⚠️ **SHORTED legs look QUIETER than good ones** (7-13 µV, zero biology) → ALWAYS confirm biology, never pass a leg on hum alone.
- **MEASURE HUM AS THE 55-65 Hz BAND, NOT a single 60.00 Hz bin** — mains drifts, single-bin understates 4-5×.
- ✅ **Allego notch is DISPLAY-SIDE ONLY, never reaches `.xdat`** (parked it at 50 Hz, saved spectrum flat 47-53 Hz: 2.457/2.504/2.354/2.401/2.365/2.462, no null). All raw analyses valid.
- **EMG failed 23/24 legs** across two independent configs = its own systematic defect. **ZERO fully scoreable mice** (need clean EEG pair AND EMG pair; C1 has EEG only).
- ⚠️ **RETRACTED SAME DAY:** I claimed the fault was localised to the slip ring because B1 chattered during C1's wiggle test. Andrea confirmed B1 and C1 share NOTHING → coincidence, retracted. **Fault is NOT localised**; cause of flips still unknown (connector micro-motion vs thermal vs tissue).
- **OPEN:** flip rate / duty cycle per leg (multi-hour run started 2026-07-31), does C1 hold for hours, why EMG fails, and **is the Allego Zcheck itself trustworthy** (never validated against a known 1 MΩ resistor — 5-min test, worth doing).
- Headstage maps: `usrdef_sleep64` and `Passthrough 64` are **byte-equivalent passthrough**, either is fine; no-splitter = `Passthrough 32` + `Default 4x8`.


🛑 **RETRACTED 2026-07-16 — the "FIRST SLEEP BIOLOGY EVER RECORDED" (A1 of `uid0715-18-58-54`, td_sep −0.65) was a CLIPPING ARTIFACT. There is still ZERO scoreable sleep data.**
- A1 was HARD-SATURATED: raw max hits the rail EXACTLY (+6389.6µV of a 6390 rail), std ≈ 4050µV vs <300µV for real mouse bipolar EEG. **Only 1 of 493 epochs had zero clipped samples**; median epoch was 19.3% clipped. I had reported "clips 19.3%" as a minor caveat — that number is the median WITHIN-epoch clip fraction, i.e. essentially EVERY epoch was railed, not 1 in 5.
- **Threshold sensitivity kills it outright**: td_sep = −0.65 (all epochs) → −0.66 (<20% clipped) → **+0.63 (<10% clipped, n=150) → +0.64 (<5%)**. The effect **FLIPS SIGN** once railed epochs are excluded ⇒ the "NREM" pattern came ENTIRELY from clipping covarying with EMG. A railed amp is non-linear; its spectrum is meaningless.
- **LESSON: never verdict a channel without first rejecting clipped epochs, and never report rail% as a median without also reporting the FRACTION OF EPOCHS THAT ARE CLEAN (`keep%`).** A metric computed on saturated data measures the artifact, not the brain. `state_scan.py` now hard-refuses: `UNSCOREABLE (only N clean epochs)` when clean epochs ≤60, and never falls back to dirty data.
- **Overnight 2026-07-15 22:47→09:00 (10.2h, foil, 7 mice) = 0/7.** A1/B1/C1 UNSCOREABLE (7%/1%/0% clean). A2, C2, D1, D2 scoreable but no biology (td_sep +0.28/+0.04/+0.23/+0.23). C1's apparent "SLEEP-LIKE −0.26" came from 3 clean epochs via the same fallback bug. **A1 did NOT replicate.** Run was <24h so the circadian test was NOT run.
- Still true: **every pre-foil archive shows NOTHING** — 72h Jul10 0/8 with circadian power 0.0% on every slot, 20h Jul13 0/8, 14h Jul02 0/2, 4.5h Jun29 0/1. But foil-vs-no-foil is now **untested for SLEEP** — foil's proven win is the single-ended 60Hz collapse, nothing more.
- **THE WALL IS NOW RAIL SATURATION, NOT HUM.** Channels swinging ±6390µV are gain/offset/contact failures, not something notching can fix. Next bar = clean unrailed channels FIRST, then a ≥24h run with a real circadian rhythm.

The EEG rig has produced **zero scoreable sleep data to date** (72h, 20h, and all 2026-07-15 runs). Full detail lives in the vault: `04-journal/2026-07/2026-07-15.md` (the decisive day), `07-decisions/2026-07-15-earth-and-sleep-council.md` (5-advisor council), `02-procedures/floating-cm-vs-contact-reconciliation.md`, `02-procedures/earthing-60hz-hum-fix.md`, `02-procedures/60hz-mains-hum-discovery.md`.

**Root-cause equation (council 2026-07-15, 3 advisors re-ran raw xdat):**
`differential_60Hz ≈ common_mode_mains(floor) × electrode_Z_imbalance(binding variable)`
One mains source drives everything (PLV=1.00 across all slots). Bipolar montage does NOT reject it (bip/cm≈2) because leg impedances are mismatched. **Contact matching sets both the level AND the stability**; earth sets the floor. Korea mains = **60 Hz** (not 50 — that error cost weeks).

**PROVEN WINS**
- 🎉 **Aluminium foil on the headstages = biggest win ever** (2026-07-15). Single-ended 60Hz collapsed up to 2 orders of magnitude (A2 frontal 3604→8µV; B1 legs 694/3805→54/79µV). Produced **B1 = first ever good channel**: legs 54/79µV matched 1.5×, notch resid 108µV, phys 95%, delta 30% delta-dominant — and real brain, not a quiet dead input (dead D2 = delta 1%). This is **Intan's own advice** (`intantech.com/files/Intan_noise_reduction_techniques.pdf`): foil-covered box ≈ as good as a wire-mesh cage; mains couples via capacitance C1 into the amp input, a grounded cage re-terminates C1.
- **Foil rules we still break:** shield MUST tie to a ground point OUTSIDE it (ours looks FLOATING → most of ~40dB left on the table = biggest cheap win remaining); must touch NOTHING inside (NOT the animal, NOT headstage GND — keep tissue isolated from the cage); cover all sides. Foil blocks E-field only, NOT magnetic — for magnetic use geometry (twist each bipolar pair; Intan names RHD2216 twisted pairs explicitly).

**REFUTED / RULED OUT — do not re-run**
- **SPI splitter**: same mice hum identically with and without it; floor sites clean both ways.
- **Slip-ring rotation**: deliberately twisting B1's slip ring barely moved it (201µV, CV 9%, steadiest slot) while UNTOUCHED C1 swung 18× (CV 53%). Rotation does NOT cause the clean↔bad swings. A matched low-Z pair is robust even to deliberate twisting; a bad leg is unstable on its own.
- **Grounded power brick**: no effect (phys still 7-30%, no 60Hz collapse). Suspect USB-PD bricks are isolated so an earthed AC plug never bonds to the DC/XDAQ ground. Untested: DMM from XDAQ ground → wall earth pin (~0Ω = earthed, open = isolation blocked).
- **"Long analog tether is backwards"** — I overstated this; withdrawn. A published rig uses a 6-wire slip ring (Digikey #1528-1152-ND, $23) with amps on the **cage lid** and raw analog down a **~64cm** tether (ours ~36cm = 30 brain→slip ring + 6 →headstage, SHORTER). **IIIS Tsukuba (our montage reference) also runs analog through a slip ring**, no head preamp. **Pinnacle** (commercial standard) DOES amplify at the head (100× preamp) → "clean waveforms even during movement". Intan's <10cm rule applies to THEIR head-mounted design. Lid-mount = legitimate but noisier trade-off; compensate with shielding + grounding + matched low-Z contacts.
- Commutators the field uses: **analog** = Dragonfly SL-10, Campden 6/10-ch, Triangle Biosystems, Digikey #1528-1152-ND; **analog + head preamp** = Pinnacle; **digital SPI (Intan-ready)** = Doric, LabMaker, Alpha Omega, Cambridge NeuroTech, NeuroTek.

**CORRECTIONS to earlier claims**
- Rig is a **Gen-1 XDAQ Core with NO Sys GND port** — anything saying "CORE2 Chassis GND port" is the **WRONG DEVICE** (vault still needs fixing).
- "Earthing fix VALIDATED 2026-07-14" was **OVERSTATED**: rested on one ~42s single-electrode clip while the other electrode was dirty on the same earth; not a controlled before/after. Corrected in `2026-07-14.md`.
- Earth the **XDAQ**, never the animal (Intan + KonteX). Animal grounded ONLY via headstage leads.

**GO/NO-GO GATE before any real overnight run** (per connected pair, live, held ≥10 min untouched): single-ended 60Hz <50µV both legs; rail% ≈0; bip/cm <0.3; notch residual <150µV; delta-dominant (θ/δ<1); impedance 0.1-1MΩ both legs matched within 2-3×; EMG modulates on a nudge. Differential hum can NOT be rescued by notch+bipolar; rail-clipping is irreversible. USABLE verdicts certify Wake/NREM only — never REM unless EMG is independently validated.

**Impedance TEST 1 (2026-07-15)**: port A contacts confirmed bad — A1 frontal 0.82MΩ good but parietal 7.14MΩ open (8.7× imbalance); A2 both EEG legs open (8.9/8.4MΩ). Grounded floor sites 0.04-0.2MΩ read fine → amp OK, electrodes bad. Does NOT clear the earth question (untestable while contacts are open).

**OPEN EXPERIMENT (2026-07-22, NOT YET RUN)**: On C3322 board (RHD2216), B1's tether has an EMPTY slip-ring wire plugged into **pad 7 = a live amplifier input** (not GND). Far end open at slip ring → long floating antenna into amp → OpenEphys-admin's exact crosstalk warning. Fingerprint present: B1 parietal (0.206MΩ, BEST electrode on rig) reads 79-80µV post-foil = HIGHEST of any good leg (A2_P 12, D2_P 46, D1_F 89, B1_P 80). Test on B1: ground pad 7 (jumper empty pin→GND net, keeps 2-pin anchor), re-measure B1 parietal single-ended 60Hz. Drop 80→~10-40µV = crosstalk confirmed, fix every mouse. NOT a rescue (B1 frontal OPEN + EMG dead). Protocol: vault `02-procedures/experiment-pad7-floating-input-B1.md`.

See also [[eeg-qc-tooling]].
