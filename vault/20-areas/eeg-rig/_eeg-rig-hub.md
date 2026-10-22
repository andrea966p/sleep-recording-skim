---
type: hub
area: eeg-rig
status: active
created: 2026-10-22
summary: "The physical EEG/EMG recording chain: electrodes, tethers, Intan headstages, XDAQ Gen-1, grounding, impedance and fault signatures"
tags: [hub, eeg, hardware]
---

# EEG rig

## What this is
The physical recording chain on `e10ubuntu`: implanted electrodes → tether → slip ring → C3410 → RHD2216 headstage → C3442 splitter → XDAQ Core Gen-1.
It covers grounding and shielding, impedance and DMM tests, the pre-flight screen and the signatures of hardware faults.
Allego settings live in `allego`, runs and the console in `recording-console`, scoring in `eeg-analysis`, growth past 8 mice in [[_rig-expansion-hub]].

## Current state
- 2026-10-15: ahyeon's unipolar run was lost to hardware: port B dropped off the SPI scan at 23:54 the night before and mouse C showed the pattern of a lost reference or ground contact at the head connector; the console now checks enumeration at start (commit 3793258). [[2026-10-15]]
- 2026-10-14: live read-only check: ports A, B, C enumerate 32 channels each; 60 Hz 1-4 µV on the channels in use (A/21 10.6 µV). [[2026-10-14]]
- 2026-10-09: the grounding fix held over 29.5 h: chip floors ≤ 239 µV every hour, A2 EMG 60 Hz 0.5-2.3 µV; light-switch spikes unchanged. [[2026-09-30-xdaq-noise-series]]
- 2026-10-07: isolated-earth socket plus the XDAQ chassis GND bonded to the earthed rack cut chip floors 12-60x. Side effect: the 800 µV ground gate now calls every chip UNJUDGEABLE. [[2026-10-06-noise-hunt-verdict]]
- 2026-10-02: the 2000 µV chip-floor proposal is falsified; the floor scale depends on the rig geometry. [[weak-chip-ground-vs-open-electrode]]
- 2026-09-30: the Gen-1 XDAQ Core has a chassis GND, wired to building earth. [[2026-09-30-xdaq-noise-series]]
- 2026-09-01: flicker of an open channel separates a bending tether from a severed one. [[tether-bend-vs-break-flicker]]
- 2026-08-26: the recurring B slot 1 fault followed the animal and its chewed tether, not the port. [[2026-08-27-B1-swap-baseline-20h-run]]
- 2026-08-04: electrodes and implants proven good; contact is intermittent within minutes and the trigger is unknown. [[2026-08-04-movement-dependent-contact]]

## Start here
- [[pre-flight-connection-screen]]: the check before any run that cannot be repeated
- [[weak-chip-ground-vs-open-electrode]]: "no EEG" is several faults; read the chip floor first
- [[per-animal-failure-signatures]]: telling open, shared-path and damaged channels apart
- [[intan-rhd2216-reference]]: the chip, why it is bipolar, why `REF` stays empty
- [[eeg-60hz-saga]]: the July 2026 hum, earth, contact and foil history

## Rules that must not be broken
- 🛑 Never suggest reseating an implanted electrode or EMG wire. The only animal-side option is a tether change under isoflurane, which ruins the batch. [[eeg-60hz-saga]]
- Do not schedule surgeries on contact evidence: the implants were proven good on 2026-08-04. [[2026-08-04-movement-dependent-contact]]
- The signals are already bipolar (`/1` EEG, `/2` EMG, `/33`, `/34` for the second mouse). Never subtract EEG from EMG. [[CANONICAL-allego-channel-selection]]
- The Allego 60 Hz notch is display-only; the saved data are raw (verified 2026-07-31 and 2026-10-01). [[eeg-60hz-saga]]
- Impedance sweeps need the stream OFF, and one sweep cannot classify a channel: use a block duty cycle. [[impedance-sweep-register]]
- UNJUDGEABLE is not FAIL: a low or collapsing chip floor means the rig could not answer, so re-mate the connectors and re-screen. [[weak-chip-ground-vs-open-electrode]]
- A recurrence argument is not a swap test: swap before naming a root cause. [[2026-08-27-B1-swap-baseline-20h-run]]
- One mouse per headstage, on the bottom SPI socket only (the top one is dead on the Core by design). [[eight-mouse-acquisition-setup]]
- Earth the XDAQ, never the animal; the animal is grounded only through its headstage GND lead. [[eeg-60hz-saga]]

## Open items
- [ ] Replace the 800 µV ground gate (`FLOOR_MIN_HUM_UV`, still 800 in `core/qc_thresholds.py` on 2026-10-22) before the next real recording. [[2026-10-06-noise-hunt-verdict]]
- [ ] Update the 2000 µV floor bar in [[pre-flight-connection-screen]] once a new gate exists.
- [ ] Reconcile "launch Allego with `--disable-gpu`" (procedures, `rig-check.sh`) with the 2026-09-16 blank-Monitor finding; Allego has run without it since 2026-10-15. [[2026-10-14]]
- [ ] Light-switch spikes reach the rig by a route the grounding fix did not close. [[2026-09-30-xdaq-noise-series]]
- [ ] The negative electrode of each bipolar pair has never been measured: neither Allego nor Open Ephys exposes `Zcheck pol sel`. [[impedance-sweep-register]]
- [ ] What triggers the contact flips, and the slip ring under load, are untested. [[2026-08-04-movement-dependent-contact]]
- [ ] Take the cable pull off the head connector on tethered unipolar runs (counterbalance or commutator). [[2026-10-15]]
- [ ] The pad 7 floating-input test was never run. [[experiment-pad7-floating-input-B1]]
- [ ] Contradictions waiting for Andrea: `_meta/contradictions/eeg-rig.md`.

## Everything here
![[area.base]]
