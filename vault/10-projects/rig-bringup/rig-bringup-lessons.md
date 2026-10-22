---
type: reference
area: rig-bringup
status: active
created: 2026-10-22
summary: "What the June-August 2026 bring-up taught, in the order it was learned, and what carries over to later runs (the hardware and the methods) and what does not (the animals)."
tags: [lessons, bring-up, eeg, method]
---

# Rig bring-up: lessons, and what carries over to later runs

> [!abstract] What this is
> The bring-up notes are a record in the order things happened, and many of their first answers were retracted.
> This page keeps the lessons that survived, each with the note that proves it, and the one rule about animals
> that the A2 control page did not carry. The map of the project is [[_rig-bringup-hub]].

Sources: the notes linked per row, and the journal days [[2026-08-09]], [[2026-08-11]] and [[2026-08-18]].

## What carries across runs, and what does not

> [!danger] The animals do not carry over
> **The A2 mouse is gone. It is a historical single animal, not a standing reference.** Every run has new mice unless Andrea says otherwise (stated 2026-08-18, the day eight newly operated mice went on the rig, [[2026-08-18]]), and a rig position is not an animal: `A1`, `B2`, `D2` name a port and a slot, nothing more. **Do not carry the numbers of [[2026-08-11-a2-control-48h-reference-profile]], or the label "the A2 control", into a later cohort.** Judge each file against the wire-free floor inside that same file.

What does carry across runs is the hardware and the method, not the animals:

- **Hardware properties.** The wire-free amplifier inputs (floor `/4`-`/16` and `/36`-`/48` on a three-channel mouse layout; never `/17`-`/32` or `/49`-`/64`, which are inactive and internally tied), the per-chip 60 Hz floor, the headstage grounding, the tether construction, the channel law. [[2026-08-06-unloaded-chain-interference]]
- **Start any run longer than a day at ZT0 (lights on, 09:00).** It costs nothing, makes light and dark equal in length, and removes a correction from every circadian number. Helper: `eeg-emg-analysis/qc/start_recording_at.py HH:MM:SS`. [[2026-08-11-a2-control-48h-reference-profile]] [[2026-08-09]]
- **The EMG state-dependence test.** Correlate 1-minute EMG amplitude with the same animal's EEG delta fraction over its usable minutes. A working pair is NEGATIVE (the sign convention is delta against EMG amplitude, so it is not the same metric as the older `r@1min`). [[2026-08-11-a2-control-48h-reference-profile]]
- **The threshold sweep.** Quote the +/-25% sweep of the sleep/wake cut next to any "asleep in the light" percentage. The ordering (light above dark) is threshold-independent, the absolute value is not. Never pick the threshold that lands on the literature value: that is circular. [[2026-08-11-a2-control-48h-reference-profile]]

## Lessons, in the order they were learned

| # | Lesson | Learned | Proof |
|---|---|---|---|
| 1 | A controller that connects is not a controller in the right mode. A wrong Allego system mode reports zero channels and looks like dead hardware; two days went on a hardware fault that did not exist. | 2026-06-19 | [[first-headstage-connection]] |
| 2 | An animal with no ground floats and rails. The ground must reach the tissue, not only the headstage. | 2026-06-27 | [[2026-06-28-eeg-recording-troubleshooting-report]] |
| 3 | An intact file is not a usable recording. 72.22 h, byte-perfect, was still 0 of 4 scoreable. Check integrity and signal separately. | 2026-07-13 | [[2026-07-13-72h-4mouse-recording-audit]] |
| 4 | Reject railed epochs before computing any metric. A saturated channel produced a fake sleep signature that flipped sign once the railed epochs were removed. | 2026-07-16 | [[2026-07-16]] |
| 5 | Check the channel map first. The chip is already bipolar: `/1` is the EEG and `/2` the EMG; subtracting them manufactured "24 failed EMG surgeries". | 2026-08-01 | [[2026-08-01-channel-mapping-correction-first-sleep]] |
| 6 | Compute persistence inside unbroken blocks only. Across contact gaps it hid real sleep and invented fake sleep (21.0 scoreable hours became about 11.1). Never quote a REM percentage. | 2026-08-03 | [[2026-08-03-two-8-mouse-runs]] |
| 7 | Contact is intermittent: a state flips within minutes and can persist for tens of minutes. A movement trigger was proposed and disproved the same day. | 2026-08-04 | [[2026-08-04-movement-dependent-contact]] |
| 8 | Impedance predicts class, not yield. Pre-register predictions and record the misses. | 2026-08-03 | [[2026-08-02-run2-preregistration]] |
| 9 | An unwired amplifier input reads "connected" about a fifth of the time at 2 MOhm and reached 0.051 MOhm. Judge every channel against the wire-free inputs in the same file; one low reading is never evidence of contact. | 2026-08-06 | [[2026-08-06-unloaded-chain-interference]] |
| 10 | Impedance blocks screen; only a multi-hour recording is an outcome. A 40-sweep, 21-minute block gave p = 1.0e-07 for a conclusion that was exactly backwards. | 2026-08-07 | [[2026-08-07-overnight-recording-two-animals-work]] |
| 11 | A low, stable, zero-flip impedance on every channel is how a wiring error behaves, not how electrodes fail. Here the cerebellum ground was mated to a floating wire. | 2026-08-07 | [[2026-08-07-ecg-cohort-baseline]] |
| 12 | Once the animal has a ground, a floating channel is quiet. The hum criterion hands a no-ground animal a perfect score; use the spectral slope, and screen on the live stream, not the sweep. | 2026-08-08 | [[2026-08-08-ground-fix-post-repin-night]] |
| 13 | A control proves the instrument, not the cohort. A2 passing the EMG test showed the measurement works; it said nothing about the six re-pinned mice. | 2026-08-11 | [[2026-08-11-a2-control-48h-reference-profile]] |

## Rules the notes keep returning to

- **Never suggest reseating an electrode or an EMG wire.** Implanted wires cannot be reseated; the only animal-side change is a new tether, which needs isoflurane and can ruin a running batch. Do not schedule surgeries. [[2026-08-02-run2-preregistration]]
- **Signals are already bipolar.** Never subtract EEG from EMG. [[2026-08-01-channel-mapping-correction-first-sleep]]
- **Reject at epoch level, never repair.** [[eeg-artefact-and-railing-rejection-policy]]
- **Do not loosen a threshold to rescue a result.** That is circular tuning. [[2026-08-08-ground-fix-post-repin-night]]
