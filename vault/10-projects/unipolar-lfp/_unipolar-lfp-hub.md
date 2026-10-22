---
type: hub
area: unipolar-lfp
status: active
created: 2026-10-22
summary: "ahyeon's unipolar LFP mice on the XDAQ rig: the 2026-08-05 reference prep, the corrected channel map, and the 2026-10-15 30 h run lost to hardware"
tags: [hub, unipolar, lfp, ahyeon]
---

# Unipolar LFP

## What this is
Recordings of ahyeon's mice with unipolar RHD2132 headstages mounted on the head, one per port, SPI cable straight into the XDAQ, with depth LFP, EEG and EMG sites recorded single-ended.
The first look was a 20 minute reference prep on 2026-08-05; the console was made ready for a 30 h, three-mouse run on 2026-10-14.
That run (2026-10-15) was lost to hardware after 13 minutes, so no unipolar dataset from it exists yet.

## Current state
- 2026-10-15: the 30 h run `dca84de0cc7a` recorded only ports A and C for 773 s: port B left the SPI scan at 23:54 the night before and port C lost its reference; the console now warns on a missing port at start. [[2026-10-15-unipolar-lfp-run-ahyeon]]
- 2026-10-14: the only correct unipolar map is `/18` EMG left, `/19` LFP target, `/20` LFP reference, `/21` EMG right, `/22` EEG parietal, `/23` EEG frontal; the 10-minute rehearsal passed end to end. [[2026-10-15-unipolar-lfp-run-ahyeon]]
- 2026-08-05: a unipolar prep showed all six wired sites live at once with physiological signal (n = 1, about 20 minutes); its role names were later found to be a typo. [[2026-08-05-unipolar-lfp-mouse-reference]]

## Start here
- [[2026-10-15-unipolar-lfp-run-ahyeon]]: preparation, the lost run, and what to check before the next one
- [[2026-08-05-unipolar-lfp-mouse-reference]]: the reference prep and the impedance caveats
- [[rig-layout-and-recording-settings]]: the layout and setting definitions (§4)
- [[eeg-recording-console]]: the console's start-time enumeration check

## Rules that must not be broken
- Use only the corrected map (`/18` to `/23` above); read the 08-05 page's role names as site numbers only. [[2026-10-15-unipolar-lfp-run-ahyeon]]
- On unipolar preps judge contact by signal, never by impedance: unused inputs are tied to ground and depth electrodes legitimately read high. [[2026-08-05-unipolar-lfp-mouse-reference]]
- Before any run confirm that every port enumerates 32 channels on the console's state panel. [[2026-10-15-unipolar-lfp-run-ahyeon]]
- For a live quality check, remember that `get_signals()` carries the Allego visualization filters; analyse the recorded file. [[2026-10-15-unipolar-lfp-run-ahyeon]]
- Do not troubleshoot mouse A's 3.4 mV of 60 Hz: it is a known surgical issue that ahyeon knows about. [[2026-10-15-unipolar-lfp-run-ahyeon]]

## Open items
- [ ] ahyeon to reconnect ports B and C at the head and decide whether to reschedule. [[2026-10-15-unipolar-lfp-run-ahyeon]]
- [ ] A counterbalance arm or commutator for tethered unipolar runs. [[2026-10-15-unipolar-lfp-run-ahyeon]]
- [ ] Disposal of run `dca84de0cc7a` (abandon, or post-process the 13 min of A + C). [[2026-10-15-unipolar-lfp-run-ahyeon]]
- [ ] Contradictions: `_meta/contradictions/noise-unipolar.md`.

## Everything here
![[area.base]]
