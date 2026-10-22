---
type: hub
area: noise-hunt
status: active
created: 2026-10-22
summary: "The Sep-Oct 2026 60 Hz noise investigation on the XDAQ rig: verdict 'mostly a ghost', then the electrician's grounding fix that removed the EMG mains on 2026-10-07; foil busbar A/B/A and per-mouse reliability still open"
tags: [hub, noise, grounding, 60hz]
---

# Noise hunt

## What this is
A time-bound project (2026-09-30 to 2026-10-09) to find where the 60 Hz and building noise on the XDAQ rig comes from, one change at a time, first without mice and then with four mice (A1, A2, B1, B2).
It ended in a verdict that the room noise was mostly a ghost except the EMG mains, and in the electrician's isolated-earth socket plus XDAQ-to-rack bond of 2026-10-07, which removed that mains at the source.
Why the hum appeared in July and August, and the ground gate itself, live in [[_eeg-rig-hub]]; the unipolar mice recorded after the fix are in [[_unipolar-lfp-hub]].

## Current state
- 2026-10-14: no automatic ground detector is supportable on post-fix data; replacing the 800 µV hum gate would unblock only B1 of uid1007, because the slope-validity gate keeps A1, A2 and B2 UNJUDGEABLE; the era-gate option (c) is waiting for Andrea. [[2026-10-14]]
- 2026-10-09: the grounding fix held over 29.5 h: chip floors under 240 µV every hour, A2 EMG 60 Hz 0.5-2.3 µV, A2 scores without the notch (r@1min 0.615); light-switch spikes unchanged. [[2026-09-30-xdaq-noise-series]]
- 2026-10-07: the isolated-earth socket and the XDAQ bonded to the earthed rack cut chip floors 12-60x and A2's EMG 60 Hz from 26-33 to 1 µV; the 800 µV ground gate now calls every chip UNJUDGEABLE. [[2026-09-30-xdaq-noise-series]]
- 2026-10-06: verdict: with per-mouse faults set aside, the remaining noise is mostly a ghost; the EMG mains is the only real one and a 60/120 Hz notch removes it (not adopted). [[2026-10-06-noise-hunt-verdict]]
- 2026-10-02: first 24 h with four mice analysed [[2026-10-02-noise-series-4mice-24h-analysis]]; the trial plan was written [[2026-10-02-noise-troubleshooting-plan]].

## Start here
- [[2026-10-06-noise-hunt-verdict]]: the answer, and what the 10-07 fix changed
- [[2026-09-30-xdaq-noise-series]]: the running narrative, Entries 1-12
- [[2026-10-02-noise-series-method-audit]]: what the measurements can and cannot say (C1 gate, C3 notch)
- [[2026-10-02-noise-troubleshooting-plan]]: the trials, scaled down; foil busbar and Phase 3 still open
- [[2026-10-02-noise-series-4mice-24h-analysis]]: the first 24 h with four mice

## Rules that must not be broken
- Recommendation of 2026-10-06 (Claude's; Andrea decides): no new environmental-noise trials or spending beyond the cheap socket and foil busbar (no Phase 2 boxes, Faraday cage, T3 or expensive earthing); put the effort into per-mouse reliability. [[2026-10-06-noise-hunt-verdict]]
- Never write "all our EEG is clean": before 2026-08-08 the hum was in mV on some channels, and light switching still spikes the EEG. [[2026-10-06-noise-hunt-verdict]]
- Judge every recording by its QC verdict, and any future noise trial by our scripts, not the official QC, while the 800 µV gate stands. [[2026-10-02-noise-troubleshooting-plan]]
- Do not undo the socket or the rack bond, and copy both at E7: they changed together and cannot be split. [[2026-09-30-xdaq-noise-series]]
- A foil needs a solid low-ohm bond; a loose or floating wire on a foil adds mains to that mouse's EMG. [[2026-10-02-noise-troubleshooting-plan]]
- The EMG notch is not adopted: it would re-score published numbers, so it is Andrea's decision. [[2026-10-06-noise-hunt-verdict]]
- Test the Raspberry Pi cameras A/B/A before adding them for good. [[2026-10-09]]

## Open items
- [ ] Foil busbar (T2a/T2b) as an A/B/A test, judged against the new floors (about 40 µV); no entry yet records the busbar fitted. [[2026-10-02-noise-troubleshooting-plan]]
- [ ] Phase 3, per-mouse reliability: counterbalance arm and slip ring, judged on long runs. [[2026-10-02-noise-troubleshooting-plan]]
- [ ] Replace the 800 µV ground gate (still 800 in `core/qc_thresholds.py` on 2026-10-22); era gate option (c) awaits Andrea. [[2026-10-14]]
- [ ] Andrea's decision on the notch, now only for recordings made before 2026-10-07. [[2026-10-06-noise-hunt-verdict]]
- [ ] Light-switch spikes: not changed by the fix. [[2026-09-30-xdaq-noise-series]]
- [ ] Facilities' AHU and chiller log for 10-01 and 10-02, for the unexplained building events. [[2026-10-06-noise-hunt-verdict]]
- [ ] Cameras A/B/A before they are re-added. [[2026-10-09]]
- [ ] Contradictions: `_meta/contradictions/noise-unipolar.md`.

## Everything here
![[area.base]]
