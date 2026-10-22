---
name: sod1-sleep-eeg-2x2-2026-10-06
description: "2026-10-06 quick compute, the 4 EEG batches (W-SD, S-SD, W-SL, S-SL) as SOD1 x CSD 2x2: no detectable SOD1 sleep effect without deprivation; SOD1 after deprivation NOT answerable from EEG (S-SD n=0 at recovery); EEG baselines are ON treatment"
metadata:
  node_type: memory
  type: project
  originSessionId: ba319075-08f2-4c06-88e2-0a6494ba100a
  modified: 2026-10-06T02:11:22.418Z
---

Andrea asked (2026-10-06) whether SOD1 changed sleep, comparing the SD and SL batches. Vault page:
`10-projects/hlb-sod1/2026-10-06-SOD1-sleep-EEG-2x2-quick-compute.md`. Script: `eeg-emg-analysis/qc/sod_sleep_2x2_2026_10_06.py HYP_DIR [NOTCH_DIR]`.

- 🔑 **SOD1/water starts at TETHERING** (intake grid Day 1; S-SD Day 1 = 08-18), so every EEG "baseline" is ~1 week ON treatment and pre-CSD. Baseline = the SOD1-without-deprivation test; recovery − baseline = CSD (SD batches) or time (SL). Compare on ZT4–24 (13:00→09:00), the only hours the SD recoveries have.
- **No detectable SOD1 effect without deprivation:** 61.1 vs 60.6 % of 24 h asleep, n 3 vs 6, exact p 0.96 (official); EMG-notched 56.2 vs 53.7 %, n 6 vs 8, p 0.24, CI −1.8 to +6.9 pts.
- 🔴 **SOD1 after deprivation is NOT answerable from the EEG.** S-SD has no scoreable recovery under either staging; HLBSSD18 becomes scoreable at baseline only with the notch (recovery wake 12.8 %, r 0.02). W-SD rebound HLBWSD08 +11.9 (notched +16.3) pts, n = 1. ⇒ open from the EEG.
- 🔴 **Official W-SL baseline is mains-inflated:** dark-phase sleep 44–64 % → 26–41 % notched, so its "−8 pts at endpoint" is artefact. Notch also makes HLBWSL23 and HLBSSL39 paired. Notch outputs: e10 `~/eeg-notch-windows-2026-10-06/` (orig reproduced 42/42).

- ⭐ **Same day, S-SD EMG RESCUE (Andrea: "at least 1", "with EMG, not EEG only"):** EMG power BETWEEN the 60 Hz harmonics (67–470 Hz) from the RAW 1000 Hz file + stage 1's gate minus its EMG-mains clause, stage 3 otherwise unchanged, every mouse of all 4 batches (`qc/emg_rescue_2026_10_06.py`). Validated κ 0.95 (min 0.89, 33 windows) vs notched staging; shuffle 57/57 REJECT. **HLBSSD15 scoreable at both timepoints** ⇒ S-SD paired n = 1: rebound +6.6 vs water HLBWSD08 +16.1, interaction −13.8 pts, BUT HLBSSD15 had the highest baseline of all 18 ⇒ a case. Baseline SOD1 vs water now n 8 vs 10, +2.3 pts p 0.34. 🔴 First run's gate (rung-2 EEG mask) fragmented blocks and lost 2 good windows; replaced AFTER seeing S-SD results, disclosed. Vault `2026-10-06-S-SD-EMG-rescue-between-harmonics`. e10 outputs `~/eeg-ssd-allverdicts-2026-10-06/` (9.7 GB, regenerable).

- **Descriptive "any effect on anything" (`measures` subcommand):** nothing on sleep/NREM amount or NREM relative delta. Neither deprived mouse has a delta (SWA) rebound (×0.86, ×0.93) ⇒ no SWA arm comparison. Hint only: baseline SOD1 NREM bouts ~15–20 % longer/fewer in BOTH batch pairs; ranges overlap. 🛑 REM unassessable (constructed share ≈ 10 % in everyone).

- **MAXIMUM rescue of W-SD + S-SD (same evening):** 2 gates × 5 EMG filters (gap67, gap10, gaplow, gaphigh, floor67), every position, only railing/flat excluded, shuffle 320/320 REJECT. floor67 FAILS validation (κ 0.26); others κ 0.95–0.98. **Nothing new**: paired stays HLBSSD15 vs HLBWSD08. W-SD recovery EEGs DEAD/OPEN after CSD; S-SD recovery EMGs no state signal at any band (best r 0.14). ⇒ one mouse per SD arm is the ceiling of these recordings.

**Why:** the user will ask this again for the final HLB report, and the on-treatment baseline is easy to misread as pre-treatment.
**How to apply:** EEG answer: "no detectable effect without deprivation; after deprivation n = 1 per arm (smaller rebound in the SOD1 mouse, confounded by its high baseline)". Report it SEPARATELY from nanotag: [[feedback-sod1-eeg-nanotag-separate]]. Any cross-batch EEG wake % needs the notch sensitivity beside it. Related: [[nanotag-sod1-hlbnsl]], [[emg-mains-corrupts-sleep-staging]], [[skim-nas-per-mouse-csv-layout]], [[s-sd-recovery-sleep-run-2026-09-02]].


## From the memory index, trimmed there 2026-10-06 (kept here verbatim)

- 🧪⭐⭐⭐ **[DID SOD1 CHANGE SLEEP? 4 EEG BATCHES AS A 2x2 — 2026-10-06](sod1-sleep-eeg-2x2-2026-10-06.md). NEWEST.** EEG baselines are ON treatment (SOD1 from tethering). No detectable SOD1 effect without SD (61.1 vs 60.6 %, p 0.96; notched p 0.24). 🔴 SOD1 after SD NOT answerable from EEG (S-SD n=0 at recovery) ⇒ NS-SD nanotag. Official W-SL baseline mains-inflated.
