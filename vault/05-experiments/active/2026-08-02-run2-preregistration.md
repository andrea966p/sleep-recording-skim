---
tags: [experiment, active, eeg, emg, preregistration, prediction, contact-intermittency]
created: 2026-08-02
status: COMPLETE — analysed 2026-08-03
priority: critical
---

# ✅ RUN 2 — PRE-REGISTERED PREDICTIONS (written BEFORE the data existed; scored 2026-08-03)

> [!abstract] TL;DR — for non-technical readers
> **What this is.** A set of predictions written down *before* a recording was analysed, so that tomorrow's result is a real test rather than a story fitted to whatever we find. See [[01-infrastructure/system-overview]] for the big picture.
>
> **Why it exists.** This project has already retracted one major result (2026-07-15) and corrected a second (the channel map, 2026-08-01). Both went wrong partly because conclusions were formed while looking at the data. Writing the predictions first removes that freedom.
>
> **How to read this page.** §3 is the prediction table. Tomorrow, fill in the "actual" column and mark each row HIT or MISS. Do not edit the predictions.

> [!quote] Paper-ready
> Electrode connection state was measured by impedance sweep immediately prior to a continuous recording, and per-animal data yield was predicted in advance from a pre-specified threshold; predictions were registered before analysis to permit unbiased evaluation of the impedance screen as a prospective quality gate.

## 1. The recording

| | |
| --- | --- |
| file | `~/radix/data/allego_2__uid0802-01-46-57` |
| started | **2026-08-02 01:46:57 KST** |
| config | 4 ports × 64 ch, `passthrough_64` / `default_8x8` |
| selection | **`/1, /2, /33, /34` per port = 16 channels** (first run with the CORRECTED map) |
| rate | 1000 Hz |
| status | RUNNING at time of writing, confirmed growing on disk |
| disk | 947 GB free — ample for a multi-day run (~3.7 GB/h) |

⚠️ Selection is display/QC only — **the file saves all 256 primary channels regardless**, so the no-wire controls (`/5-/16`) and tied floor (`/17-/32`) remain available for QC.

## 2. Pre-flight impedance (`imp_8mice_channelscorrect.csv`, taken immediately before start)

Read on the REAL channels only, per [[electrode-connection-state-test]]. Threshold: **Z < 2 MΩ = connected, > 3 MΩ = open**.

| mouse | EEG `/1` | class | EMG `/2` | class | **predicted** |
| --- | --- | --- | --- | --- | --- |
| **C2** | **1.146** | CONN | **0.168** | CONN | ⭐ **SCOREABLE** |
| D2 | 2.114 | **MARGINAL** | 0.023 | CONN | EMG only, EEG borderline |
| B1 | **0.133** | CONN | 7.099 | OPEN | EEG only |
| A1 | 4.446 | OPEN | 0.087 | CONN | EMG only |
| C1 | 5.720 | OPEN | 0.051 | CONN | EMG only |
| D1 | 3.980 | OPEN | 0.202 | CONN | EMG only |
| A2 | 5.962 | OPEN | 4.851 | OPEN | nothing |
| B2 | 5.771 | OPEN | 6.287 | OPEN | nothing |

**Sanity checks (all PASS):** empty pads `/3,/4` median **5.335 MΩ** vs no-wire control `/5-/16` **5.169 MΩ** — statistically identical, as they must be. Tied floor `/17-/32` **0.060 MΩ**. The sweep is valid.

### Movement since the 2026-07-31 sweep — channels recover as readily as they fail

| mouse | channel | then | now | change |
| --- | --- | --- | --- | --- |
| B1 | EEG | 1.717 | **0.133** | **13× BETTER** |
| C2 | EEG | 4.418 | **1.146** | open → connected |
| C1 | EEG | 0.465 | **5.720** | **connected → OPEN** (our best mouse lost it) |
| D2 | EEG | 0.660 | 2.114 | drifted into the grey zone |

Nothing was deliberately done to any of them. **Contact state moves in BOTH directions on a timescale of days.** This is the single most important operational fact about the rig.

## 3. ⭐ PREDICTIONS — do not edit after the run starts

| # | prediction | actual | HIT/MISS |
| --- | --- | --- | --- |
| **P1** | **C2 will be fully scoreable** (EEG + EMG, physiology PASS) | 0.74 h gated but only **0.06 h** inside testable blocks; 250 fragments, median **4 s**; longest block 3.7 min → **INSUFFICIENT** | **MISS** |
| **P2** | **A2 and B2 will yield nothing** | both 0.00 h; EEG gate 0 %, EMG ≤ 0.2 % | **HIT** |
| **P3** | **B1 will have good EEG and no EMG** | EEG best in fleet (14.0 % of epochs, lowest hum 2802 µV); EMG **0.0 %** | **HIT** |
| **P4** | **A1, C1, D1 will have good EMG and no EEG** | EMG 99.9 / 97.1 / 100 %; EEG **0.0 %** on all three | **HIT** |
| **P5** | **1 to 2 mice fully scoreable** (C2, possibly D2) | **0 mice** | **MISS** |
| **P6** | Impedance→yield rank correlation will again be strong (ρ < −0.7) | **ρ = −0.452**, and degenerate (only 1 non-zero yield) | **MISS** |
| **P7** | At least one channel will CHANGE STATE during the run | C2 EEG gate pass **11.2 % → 0.4 % → 0.7 %** by thirds; impedance 1.146 → 2.507 MΩ | **HIT** |
| **P8** | If the run exceeds ~29 h, light-phase NREM higher | run was **21.74 h** (< 29 h), and the light schedule is still undocumented | **VOID** |

> [!note] P8 revisited 2026-08-03 — still VOID, but for a different reason
> The light schedule is now documented (**on 09:00 / off 21:00 KST, ZT0 = 09:00**
> — [[production-values]]). Run 2 ran 01:46 → ~23:30, so it **did** span a full
> light phase, and the "< 29 h" condition was the wrong gate. P8 nonetheless
> stays VOID because Run 2 produced **zero usable epochs in any phase** — the
> prediction could not be evaluated at all.
>
> The light-phase test was instead settled on **Run 1's C1**, which straddles the
> 21:00 boundary: **33.1 % wake in the light phase vs 82.2 % in the dark**, i.e.
> 66.9 % asleep in the light against a published ~70 %. See
> [[2026-08-03-two-8-mouse-runs]].

> [!warning] Rescored 2026-08-03 under corrected thresholds — every verdict holds
> The numbers in the "actual" column were produced with the pre-2026-08-03 gate
> (open 300 µV, shorted 25 µV, rail 6300). Re-run under the corrected gate
> (open 150 µV, flat 11 µV / dead-channel 20 µV, rail 6376.8 µV), **Run 2 is
> 8/8 OPEN with 0.00 h usable in blocks for every animal** — so P1–P7 keep their
> HIT/MISS marks unchanged. Only the fine-grained percentages move.
>
> **P6 is the one that matters most.** It was pre-registered and it MISSED:
> impedance→yield gave ρ = −0.452, not the ρ = −0.941 fitted on Run 1. The
> decisive counterexample is B1, which read **0.133 MΩ** — the best EEG
> impedance in the fleet — and then ran fully open for 21.7 h. Impedance
> predicts **class, not yield**; [[electrode-connection-state-test]] is narrowed
> accordingly.

**Score: 4 HIT, 3 MISS, 1 VOID.**

> [!check] What the misses actually tell us — the screen predicts CLASS, not YIELD
> P2, P3 and P4 all hit: the pre-flight sweep called **which channel works on which animal** correctly every time. P1, P5 and P6 all missed: it did **not** predict usable hours. A channel can read 1.146 MΩ at rest and still chatter into uselessness under load, which is exactly what C2 did.
>
> This qualifies the earlier ρ = −0.941 claim. **Keep the sweep as a go/no-go on which animals are worth running; stop treating it as a yield forecast.**

> [!warning] P1 was re-evaluated after a scoring bug was found (2026-08-03)
> The first pass scored C2 at 0.74 h with `r@1min = +0.078` and called it "NO STRUCTURE". That statistic was invalid: it correlated across time gaps, and with 250 fragments of median 4 s it was **impossible to pass**, not failed. Under the corrected within-block statistic C2 has only 0.06 h inside testable blocks, so the honest verdict is **INSUFFICIENT** — the question could not be asked, rather than answered negatively. The P1 verdict is MISS either way. See [[2026-08-03-data-quality-report-for-professor]] §3.2.

**P8 is the scientifically important one.** No light-phase data with a living EEG exists yet. A higher NREM fraction in the light phase is the strongest independent confirmation available that we are measuring real sleep and not an artifact.

⚠️ **P8 cannot be evaluated until the animal room light schedule is documented** — still blank in `00-config/production-values.md`. **Get lights-on/lights-off from the animal facility before analysing.**

## 4. What was NOT done, and why it matters

> [!danger] ⚠️ CORRECTED 2026-08-02 — "RESEAT THE HEAD CONNECTOR" IS NOT A THING. I WAS WRONG.
> **You CANNOT reseat an electrode or an EMG wire after implantation.** They are implanted. The only animal-side intervention is **changing the tether**, and that requires **isoflurane** — which stresses the animal and **ruins the batch if an experiment is running**. It must never be done casually or "to see if it helps".
>
> **THE INTERVENTION HIERARCHY, by real cost:**
>
> | tier | what | cost | examples |
> | --- | --- | --- | --- |
> | **1. FREE** | everything on the RIG side of the slip ring | no animal contact at all | swap headstage · swap port · inspect/resolder C3410 pads · DMM the slip-ring wires · swap boards between animals |
> | **2. EXPENSIVE** | change the tether | **isoflurane, animal stress, RUINS THE BATCH mid-experiment** | only with a clear, pre-argued reason |
> | **3. IMPOSSIBLE** | implanted wires and electrodes | requires new mice | not an option for existing animals |
>
> **Everything I previously filed as "reseat" belongs in tier 1 or is not possible at all.** Plan interventions from tier 1 only, unless there is a specific argued reason to spend an animal.

I previously recommended "reseating the head connectors" on B1 (EMG) and A1, C1, D1 (EEG). **That recommendation was invalid and is withdrawn** — see the box above. Nothing was owed before this run started, and the run being started as-is was correct.

Expected yield remains **1 mouse (C2)**. The genuinely available next action is the tier-1 bench test below, which costs nothing and touches no animal.

## ⭐ THE RIGHT NON-INVASIVE TEST — bench the accessible chain on A1 and D1

**A1 and D1 are near-perfect diagnostic cases and cost nothing to investigate.**

Each has **EMG connected for the full 27.9 h (0.087 and 0.202 MΩ)** and **EEG open the entire time (4.446 and 3.980 MΩ)**. Both signals travel through **the same tether, the same slip ring, the same C3410 board, the same headstage, the same port**.

⇒ **The shared infrastructure on those two animals is PROVEN GOOD by their own working EMG.** Whatever kills their EEG must be in something that differs between the two channels:

| differs between EEG and EMG | accessible without the animal? |
| --- | --- |
| C3410 **pads 0/1 solder joints** (EEG) vs pads 2/3 (EMG) | ✅ **YES — inspect and resolder** |
| the two **slip-ring wires** carrying EEG | ✅ **YES — DMM continuity** |
| the **slip ring contacts** for those two lines | ✅ **YES** |
| head-connector pins for EEG | ❌ animal side |
| implanted EEG wires / electrodes | ❌ requires new mice |

**Three of the five candidates are free to test.** And the test has a built-in control: pads 2/3 on the same board, through the same slip ring, are demonstrably working.

> [!important] This is why the EEG/EMG asymmetry does NOT prove an implant fault
> It is tempting to read "EMG fine, EEG dead, same animal" as proof that the EEG *implant* failed. **It is not.** A cold solder joint on pad 0 or 1, or one broken slip-ring wire, produces exactly the same pattern — and both are fixable at the bench without touching the mouse.
>
> **Rule out the free tier before concluding anything about the implants, and long before anyone schedules surgery.**

**Procedure (no animal contact, ~30 min):**
1. With the animal disconnected at the slip ring (rig side only), DMM continuity from **C3410 pad 0** and **pad 1** back through the slip-ring wiring. Compare against **pads 2 and 3**, which are known good.
2. Inspect the pad 0/1 solder joints under magnification. Reflow anything suspect.
3. Swap that animal's **headstage** to a known-good one; re-sweep impedance.
4. Swap the **port**; re-sweep.
5. Only if all four come back clean is the fault upstream of the slip ring — i.e. tether or implant — and only then is a tier-2 tether change worth arguing for.



## 5. Analysis plan — fixed in advance

1. `score_all_mice.py` then `gate_and_score_all.py` (both in `02-procedures/eeg-data-analysis/scripts/contact-state-2026-07-31/`), unchanged.
2. Three-part gate: not open AND **not shorted (EEG rms ≥ 25 µV)** AND not clipped. ⚠️ *Thresholds superseded 2026-08-03 — the 25 µV rule discarded 9.5 % of all epochs including real low-amplitude wake, and is now split into an epoch-level dropout test (11 µV) and a channel-level dead-electrode test (20 µV median). Verdicts above are unchanged. See [[pipeline/README]].*
3. Otsu EMG threshold **per animal**. **Never reuse one animal's threshold on another** — that is what wrongly passed D2 on 2026-08-01.
4. Report a hypnogram ONLY if persistence at 1 min clears a shuffle control, and ONLY if the physiology ordering PASSES.
5. **Take a SECOND impedance sweep the moment the run stops.** Two sweeps bracketing a long recording is what distinguishes progressive degradation from random flipping — connector problem vs implant problem.

## 6. Success criteria

| outcome | interpretation |
| --- | --- |
| C2 scoreable + physiology PASS | **n=3 across runs. The sleep result is solid.** |
| Light-phase NREM > dark-phase NREM | ⭐ **Independent confirmation of real sleep.** Biggest possible win. |
| Yield matches prediction (±1 mouse) | The impedance pre-flight gate is validated prospectively — a genuinely useful SOP. |
| Yield much worse than predicted | The pre-flight gate does not survive prospective testing; go back to the classifier. |

## Related

- [[2026-08-01-channel-mapping-correction-first-sleep]] — the corrected map, the rescore, the impedance re-read
- [[electrode-connection-state-test]] — the classifier and the pre-flight thresholds
- [[2026-08-02]] — day journal
- [[04-processing-guidelines]] — corrected EEG/EMG mapping
