---
name: recording-2026-10-01-noise-4mice-overnight
description: "First noise-series overnight WITH mice (4 mice, console run cfdf8ebde0c6, 2026-10-01/02) and the light-phase run: placeholder IDs POS-slot, A1/B2 EMG open, all four UNJUDGEABLE at official rung 2. Facts in the vault"
metadata:
  type: project
---

Console run `cfdf8ebde0c6` (batch `noise-tests`, ports A+B, whole dark phase 10-01 21:00 to 10-02 09:02, 12.03 h, zero dropped samples) plus light-phase run `8f84e3e62af6` (09:16 to 21:11). Mouse ids are placeholders `POS-<slot>` on the NAS (A2 = HLBWSL30, B1 = HLBSSD20, A1 and B2 an unnumbered B6/J female). A1 and B2 EMG are open (implant side). Official rung 2: all four UNJUDGEABLE overnight; B1 flipped to PASS untouched in the light run (floor 702 to 971, audit C1).

Details: [[2026-09-30-xdaq-noise-series]] (Entries 5-9) · [[2026-10-02-noise-series-4mice-24h-analysis]] · [[2026-10-02-light-phase-run-rig-session]] · [[2026-10-02-noise-series-method-audit]]

- ⚠️ Andrea's clock ran at least 8 s ahead of e10: never trust a reported second without a sync photo of Allego time plus phone.
- 🔴 The gate reads the 59-61 Hz line PEAK (10 s Hann): never compare a band-pass std with 800 / 2000. A stale `current-recording.txt` can raise a false STALL on the next run (fix was not deployed). Console runs arm the watchdog since 2026-10-14 (the old "do not arm" line is stale).
- 🔴 Scan counts made before 23:00 on 10-02 are WRONG: use `fullscans-v2/`. If a `_feat.npz` ever lands in `~/radix/data`, move it out before 01:30 (S3 cannot delete).
- The tether copper shield was never inserted into any pad: do not repeat the 06-28 pad-6 plan. Do not propose new noise trials: [[noise-hunt-verdict-2026-10-06]].
- The 60/120 Hz EMG notch was validated on this series (SCOREABLE 44 to 69, shuffle control not re-run at scale) but is NOT adopted: [[emg-mains-corrupts-sleep-staging]].
