---
name: xdaq-gen1-has-chassis-gnd
description: Gen-1 XDAQ Core DOES have a chassis GND, wired to building earth; the 07-16 vault "no chassis GND" retraction is wrong. Noise series started 2026-09-30.
metadata:
  type: project
---

Andrea confirmed on 2026-09-30: the Gen-1 XDAQ Core has a chassis GND terminal and it is wired to the wall-socket (building) earth, continuity-tested. The vault claimed since 2026-07-16 that the Gen-1 has "no Chassis GND / no chassis ground terminal"; correction callouts were added to the five pages that said so.

**Why:** that false claim made earlier agents drop earth and shield-grounding tests as "not executable".
**How to apply:** treat chassis-GND tests (earth-wire lift, shield bond) as possible. Whether a separate Sys GND exists on the Gen-1 is still unverified.

Noise series log: `vault/05-experiments/active/2026-09-30-xdaq-noise-series.md`. Entry 1 (no mice, no tethers; slip-ring animal-side wires free) is NOT a baseline; port A shows a strong 120 Hz field that port B doesn't. Light switching spikes every chip at once, but the whole 52 h S-SL run had only 8 all-chip events (2 from the light timer) ⇒ frequent within-mouse spikes are NOT building transients. 2026-10-01 A/B/A: USB isolator (FIT1019) left mains + switch spikes unchanged but DOUBLED broadband noise on open inputs ⇒ record with the DIRECT cable; isolator parked pending a dummy-load test. Test files go in `~/radix/noise-tests/`, not `radix/data`. Script `eeg-emg-analysis/qc/noise_scan.py`. See [[backup-architecture-three-destinations]].


## From the memory index, trimmed there 2026-10-06 (kept here verbatim)

- ✅🔴⭐⭐ **[GEN-1 XDAQ HAS A CHASSIS GND, WIRED TO BUILDING EARTH — 2026-09-30](xdaq-gen1-has-chassis-gnd.md). NEWEST.** 07-16 "no chassis GND" claim WRONG. Noise series started (no mice); port A has a strong 120 Hz field. Tests → `~/radix/noise-tests/`.
