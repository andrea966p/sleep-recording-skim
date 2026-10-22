---
name: emg-mains-corrupts-sleep-staging
description: "2026-10-02: stage 3's EMG rms (10-124 Hz at 250 Hz) includes the 60 Hz line; notching 60/120 Hz validated (SCOREABLE 44 -> 69/100, shuffle 0/100, dark>light 47/49) but NOT adopted (re-scores published numbers)."
metadata:
  type: project
---

**2026-10-02:** stage 3 stages WAKE by an Otsu split of log EMG rms with NO mains removal, so a 60 Hz line the size of the quiet EMG tone destroys the wake/sleep contrast. Notching 60+120 Hz: W-SL light phase 8/13 -> 13/13 scoreable; archive-wide SCOREABLE 44 -> 69 of 100 (unnotched reproduces 99/99 official verdicts); epoch-shuffled control 0/100; dark > light WAKE 41 -> 47 of 49. 2026-10-06 mains-FREE EMG measure from the raw 1 kHz file (gaps between harmonics, 67-470 Hz) reproduces the notched staging at kappa 0.95. After the 2026-10-07 grounding fix new recordings need no notch ([[grounding-fix-2026-10-07-mains-collapsed]]).

Details: [[2026-10-02-noise-series-4mice-24h-analysis]] (method audit [[2026-10-02-noise-series-method-audit]]; 10-06 follow-up [[2026-10-06-S-SD-EMG-rescue-between-harmonics]])

🛑 NOT adopted: changing the EMG measure re-scores every published wake % / r@1min; it needs pre-registration, the falsification suite and Andrea's decision. Do not apply the notch to official numbers. Code gotcha (not in the vault): stage 2's npz has `.files`; a dict stand-in needs a `files` property (`NpzDict`) or `analyse()` crashes.

Rules:
🛑 **NOT adopted.** Changing the EMG measure re-scores every published wake % / r@1min (S-SL n=3, W-SL, W-SD...). It needs dark/full-day
sets, the whole ~12 GB stage-2 archive (scheduled after a recording, heavy) and the falsification suite, then Andrea's decision.
