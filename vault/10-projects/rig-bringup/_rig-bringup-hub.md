---
type: hub
area: rig-bringup
status: done
created: 2026-10-22
summary: "June to August 2026: getting the first valid EEG/EMG recordings from the XDAQ rig; ended with a 48 h control recording, and the living knowledge moved to the eeg-rig and eeg-analysis areas."
tags: [hub, bring-up, eeg, emg, grounding, tether]
---

# Rig bring-up hub: from the first headstage to the first valid recordings

## What this is
The effort of June to August 2026 to get scoreable EEG/EMG out of the XDAQ + Intan rig: first headstage, grounding, 60 Hz, channel map, contact and tether tests, the ECG cohort and its ground error, and the 48 h control run. It ended on 2026-08-11 with a working reference recording.
Many notes here were retracted or recomputed later and carry a banner pointing at what replaced them; read the banner before quoting a number.
It does not cover the cohorts that followed (see [[_hlb-sod1-hub]]), the noise hunt ([[2026-09-30-xdaq-noise-series]]) or the rig as it runs today ([[_eeg-rig-hub]]).

## Current state
- 2026-10-09: fixing the building ground (isolated-earth socket, XDAQ bolted to the earthed rack) collapsed the 60 Hz mains and held for 29.5 h; this belongs to the noise hunt, not to this project. [[2026-09-30-xdaq-noise-series]]
- 2026-08-11: one control mouse recorded 48.19 h from ZT0 to ZT0: 47.09 h (97.7%) usable EEG, zero railed epochs, an EMG that falls when the animal sleeps, and the same profile on both days. It is a single historical animal, not a standing reference. [[2026-08-11-a2-control-48h-reference-profile]] [[rig-bringup-lessons]]
- 2026-08-08: re-pinning the ground wire worked: four re-pinned mice gave 57 to 72% usable EEG over the first 5.5 h, the one animal that could not be re-pinned scored 0.0%, the hum criterion was dead on that cohort, and no ECG channel ever showed a heartbeat. [[2026-08-08-ground-fix-post-repin-night]]
- 2026-08-07: seven new EEG+EMG+ECG mice had recorded with no ground (the cerebellum pin was mated to a floating wire); low hum, perfect and flip-free impedance and no signal were all the same fault. [[2026-08-07-ecg-cohort-baseline]]
- 2026-08-07: a 23.66 h run gave two working animals (B1 EEG 100%, D2 EEG 87.9%); the tether swap that looked like harm to D2 had fixed it (0.0% to 87.9%), so the harm verdict was retracted. [[2026-08-07-overnight-recording-two-animals-work]]
- 2026-08-06: an unwired amplifier input reads "connected" below 2 MOhm 21.4% of the time and reached 0.051 MOhm; tether, slip ring and splitter are not leaking. Connection is judged at 0.5 MOhm against the in-file floor. [[2026-08-06-unloaded-chain-interference]] [[2026-08-06-fleet-duty-cycle-census]]
- 2026-08-05: a soldered, resin-encapsulated tether took B1's EEG duty cycle from 45% to 100% (20/20, old 2 MOhm criterion), but tether construction, connector re-seating and an isoflurane episode changed at once. [[2026-08-05-tether-comparison]]
- 2026-08-04: contact is intermittent and flips within minutes; the proposal that movement causes it failed the same day. [[2026-08-04-movement-dependent-contact]]
- 2026-08-03: of two 8-mouse runs, run 1 gave two scoreable animals (C1 8.73 h, C2 2.34 h) and run 2 none; both were commissioning tests on post-op day 8 to 12. [[2026-08-03-two-8-mouse-runs]]
- 2026-08-01: the channel map was wrong (EEG = native0 minus native1); `/1` is the EEG and `/2` the EMG, and C1 has real sleep architecture. This retracted the 2026-07-31 findings. [[2026-08-01-channel-mapping-correction-first-sleep]]
- 2026-07-15/16: shielding the headstages with foil cut single-ended 60 Hz by up to 450 times; the same-evening "first real sleep" was a railed channel and was retracted on 2026-07-16; the remaining hum tracked electrode impedance. [[2026-07-15-earth-and-sleep-council]] [[2026-07-16]]
- 2026-07-13: the first 72 h four-mouse run was byte-perfect (72.22 h) and had 0 of 4 scoreable animals (60 Hz hum), no video, and a throttled PC. [[2026-07-13-72h-4mouse-recording-audit]]
- 2026-07-02: a council checkpoint found no validated recording yet; the endurance run that followed passed on 2026-07-03 (14.23 h, zero dropped samples). [[2026-07-02-eeg-recording-checkpoint]]
- 2026-06-19: headstage detection was solved: the wrong Allego system mode, not hardware. On 2026-06-27 giving the animal a ground ended the railing. [[first-headstage-connection]] [[2026-06-28-eeg-recording-troubleshooting-report]]
- 2026-10-22: where the living knowledge went: rig hardware, grounding, impedance and fault signatures to [[_eeg-rig-hub]] (start with [[impedance-sweep-register]] and [[per-animal-failure-signatures]]); QC, the verdict ladder and the pipeline to [[_eeg-analysis-hub]] (start with [[animal-card-and-verdict-ladder]] and [[2026-08-07-rig-specification-and-analysis-method]]); Allego settings to [[eight-mouse-acquisition-setup]].

## Start here
- [[rig-bringup-lessons]]: the lessons that survived, and what carries over to later runs.
- [[2026-08-01-channel-mapping-correction-first-sleep]]: the channel map; read before trusting any earlier EEG/EMG analysis.
- [[2026-08-06-unloaded-chain-interference]]: the wire-free floor, the control every later analysis rests on.
- [[2026-08-08-ground-fix-post-repin-night]]: the ground error, the pre-registered test and what failed.
- [[2026-08-11-a2-control-48h-reference-profile]]: the 48 h recording and the method it established.

## Rules that must not be broken
- **Impedance screens; only a multi-hour recording is an outcome.** State a block's duration next to its duty cycle and never conclude harm or benefit from a block alone. [[2026-08-07-overnight-recording-two-animals-work]]
- **Judge every channel against the wire-free inputs in the same file.** One low impedance reading is never evidence of contact. [[2026-08-06-unloaded-chain-interference]]
- **On the bipolar RHD2216 montage the signals are already bipolar: `/1` (`/33`) is EEG, `/2` (`/34`) is EMG. Never subtract EEG from EMG.** Unipolar preps are derived differently ([[_unipolar-lfp-hub]]). [[2026-08-01-channel-mapping-correction-first-sleep]]
- **Never suggest reseating an electrode or an EMG wire, and do not schedule surgeries.** Implanted wires cannot be reseated; a tether change costs an isoflurane episode. [[2026-08-02-run2-preregistration]]
- **Never report a REM percentage.** [[2026-08-03-two-8-mouse-runs]]
- **Reject railed epochs before computing any metric.** A saturated channel can fake a sleep signature. [[2026-07-16]]
- **After the ground is fixed, screen on the live stream, not the sweep; a stable, flip-free low impedance can mean no ground at all.** [[2026-08-08-ground-fix-post-repin-night]] [[2026-08-07-ecg-cohort-baseline]]
- **Quote the threshold sweep beside any "asleep in the light" percentage, and never choose a threshold because it matches the literature.** [[2026-08-11-a2-control-48h-reference-profile]]
- **The animals do not carry across runs: every run has new mice unless Andrea says otherwise, and a rig position is not an animal.** [[rig-bringup-lessons]]

## Open items
- [ ] The pad 7 floating-input test on B1 was never run and its animal was euthanised on 2026-08-05: close it or re-target it (Andrea). [[experiment-pad7-floating-input-B1]]
- [ ] Part B of the interference test (does a dangling cable disturb a working neighbour) was designed and never run; the eight mice were replaced on 2026-08-07. [[2026-08-06-unloaded-chain-interference]]
- [ ] Which part of the tether chain does the work is still unanswered: construction, slip ring, connector re-seating and anaesthesia changed together; soldered and resin-encapsulated joints are the leading, circumstantial candidate. [[2026-08-07-overnight-recording-two-animals-work]]
- [ ] Only the positive input of each electrode pair has ever been measured. [[2026-08-07-rig-specification-and-analysis-method]]
- [ ] C1's persistence is quoted as +0.744 and as +0.761 in different notes (two gates); the logged resolution is in `_meta/contradictions/rig-bringup.md`. [[2026-08-03-two-8-mouse-runs]]

## Everything here
![[area.base]]
