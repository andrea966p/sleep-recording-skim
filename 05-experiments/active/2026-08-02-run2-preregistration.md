---
tags: [experiment, active, eeg, emg, preregistration, prediction, contact-intermittency]
created: 2026-08-02
status: RUNNING — analyse when stopped
priority: critical
---

# ⏳ RUN 2 — PRE-REGISTERED PREDICTIONS (written BEFORE the data exists)

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
| **P1** | **C2 will be fully scoreable** (EEG + EMG, physiology PASS) | | |
| **P2** | **A2 and B2 will yield nothing** | | |
| **P3** | **B1 will have good EEG and no EMG** | | |
| **P4** | **A1, C1, D1 will have good EMG and no EEG** | | |
| **P5** | **1 to 2 mice fully scoreable** (C2, possibly D2) | | |
| **P6** | Impedance→yield rank correlation will again be strong (ρ < −0.7) | | |
| **P7** | At least one channel will CHANGE STATE during the run (as C1 did at 8.73 h and D2 at 5.30 h in run 1) | | |
| **P8** | If the run exceeds ~29 h, **at least one mouse will produce LIGHT-PHASE data**, and its NREM % will be **HIGHER** than its dark-phase NREM % | | |

**P8 is the scientifically important one.** No light-phase data with a living EEG exists yet. A higher NREM fraction in the light phase is the strongest independent confirmation available that we are measuring real sleep and not an artifact.

⚠️ **P8 cannot be evaluated until the animal room light schedule is documented** — still blank in `00-config/production-values.md`. **Get lights-on/lights-off from the animal facility before analysing.**

## 4. What was NOT done, and why it matters

I recommended reseating the head connectors on B1 (EMG), A1, C1 and D1 (EEG) before starting — each is ONE channel short of being fully scoreable, and the swings above show recovery is plausible. **That was not done; the run was started as-is.**

This is a legitimate call (a long run on C2 alone still delivers the never-yet-obtained light phase), but it means the expected yield is **1 mouse**, and the reseat experiment remains outstanding. If run 2 confirms ~1 scoreable mouse, the reseat becomes the highest-value next action.

## 5. Analysis plan — fixed in advance

1. `score_all_mice.py` then `gate_and_score_all.py` (both in `02-procedures/eeg-data-analysis/scripts/contact-state-2026-07-31/`), unchanged.
2. Three-part gate: not open AND **not shorted (EEG rms ≥ 25 µV)** AND not clipped.
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
