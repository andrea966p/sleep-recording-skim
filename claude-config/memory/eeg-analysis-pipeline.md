---
name: eeg-analysis-pipeline
description: "The canonical 3-stage EEG pipeline (QC -> per-mouse split -> sleep features), its file layout, and every literature/measurement-backed threshold"
metadata: 
  node_type: memory
  type: project
  originSessionId: 21a6d0c8-6c66-4695-9945-f1f3d834eb58
  modified: 2026-08-03T03:21:40.412Z
---

**THE canonical analysis path, built 2026-08-03.** Vault
`02-procedures/eeg-data-analysis/pipeline/`. Supersedes `rescore_v2.py` and
everything in `scripts/`. Use system `python3`, NOT the
`/opt/neurosurveillance` venv (numpy/scipy ABI mismatch).

```
stage1_qc.py       raw .xdat -> per-animal verdict (CLEAN/DIRTY/OPEN/DEAD/CLIPPED/INSUFFICIENT)
stage2_split.py    -> /home/skimlab/eeg-processed/YYYY-MM-DD/
                      portC-slot1_2026-07-31_180637_27h54m.npz  (250 Hz, uV, bipolar)
                      impedance/  qc/  README.txt
stage3_features.py -> *_hypnogram.csv, *_features.json, *_summary.txt
stage4_export_edf.py -> *.edf (EDF+C) + *_SCORER-README.txt  <- HUMAN scoring hand-off
qc_thresholds.py   SINGLE SOURCE OF TRUTH, every constant carries its provenance
```

⭐ **STAGE 4 = the endpoint "usable to score manually".** Dependency-free EDF+
writer (old `xdat_to_edf.py` needed pyedflib AND computed bipolar derivations =
retracted model — do NOT resurrect). Physical range pinned to **±6389.56 µV** so
the EDF step = hardware LSB 0.195 µV; validated round-trip error **exactly 1 LSB**.
⚠️ Use 6389.56 not 6389.565 — **EDF header fields are 8 ASCII chars**, so
`-6389.565` truncates while the positive field doesn't → asymmetric range +
fractional-LSB bias on every sample. **3 deliberate choices: (1) automatic
hypnogram NOT written into the EDF (score blind, compare after); (2) rejected
epochs LEFT IN PLACE, not cut (splicing discontinuous time destroys bout-length
perception — same class as the persistence bug); (3) `_SCORER-README.txt` lists
the exact windows worth scoring.**

📄 **Report §6.5 = the step-by-step raw→scorable procedure** (what/why/code/source
per step) in `05-experiments/completed/2026-08-03-data-quality-report-for-professor.md`.
Report §7 (old scripts) is banner-flagged SUPERSEDED.

⭐ **THRESHOLDS RE-DERIVED FROM DATA 2026-08-03** (1,137,955 pooled epochs,
41 animal-recordings) — the old ones were guesses:

- **RAIL = 6389.6 µV = 0.195 µV/LSB × 32767.** MEASURED: max|sample| is
  6389.8 µV on all 8 channels = 16-bit ADC full scale. A hardware ceiling, not
  the amplifier's analogue range. Old value 6300 was a guess.
- **OPEN = 150 µV** (was 300). Mains amplitude is BIMODAL in log space:
  connected mode 84 µV, open mode 3731 µV, **valley at 134 µV**. 300 sat on the
  rising flank of the OPEN mode = permissive.
- **The old `SHORT_UV = 25 µV` was WRONG and was the ONLY load-bearing
  constant.** Split into `FLAT_UV = 11 µV` (epoch dropout; 11 is the measured
  minimum between the amplifier noise floor and real signal) and
  `DEAD_CHANNEL_UV = 20 µV` (channel median — a short is a CHANNEL property,
  not an epoch property). Old 25 µV discarded 9.5% of ALL epochs including
  real low-amplitude wake; at 13 an extra animal passed, at 40 C1's r fell
  0.74 -> 0.43. The channel/epoch split removes that sensitivity.
- **CLIP_FRAC = 0** (any railed sample). FREE: results identical for 0, 1e-3,
  1e-2 — clipping is NOT load-bearing, railed epochs are already caught by OPEN.
- **Impedance: literature says epidural screws are 5-50 kΩ at 1 kHz, ≤10 kΩ
  confirms contact. Our BEST channel in the fleet is 73 kΩ.** So our 2 MΩ
  "connected" bar is ~40× looser than the norm and is an OPEN-CIRCUIT DETECTOR,
  not a quality bar. A channel at 0.5-2 MΩ is a POOR electrode that merely
  isn't fully open.

✅ **SENSITIVITY SWEPT: the conclusions do NOT depend on the thresholds.**
C1 is invariant (r=0.74, 8.7h) in EVERY variant tested; C2 survives every
variant (r 0.31-0.72). A conclusion that moved with a threshold wouldn't be
reportable.

Filename law: `port{PORT}-slot{SLOT}_{YYYY-MM-DD}_{HHMMSS}_{NNhNNm}.npz`.
Slot 1 = native offset 0 (`/1`,`/2`), slot 2 = offset 32 (`/33`,`/34`).

⚠️ **Day-folder date comes from metadata UTC `start_time` converted to KST.**
The `uidMMDD-HH-MM-SS` filename token is ALREADY LOCAL. Mixing them puts a
recording in the wrong day and shifts every ZT by 9 h. See [[eeg-60hz-saga]],
[[eeg-analysis-codebase]].

📄 **HAND THIS TO THE PROFESSOR: `02-procedures/eeg-data-analysis/analysis-methods-and-justification.md`**
— standalone, steps 0-6, each with what/why/code/published-source, opening with a
**standard-vs-ours table**. Report §6.5 is the short version and points at it.

🛑 **FRAMING CORRECTION (Andrea pushed back, was right): we are NOT deviating from
standard method. Never say "we deliberately differ from the literature".**
(1) **Record wide-band + filter offline IS the standard** (Intan/OpenEphys/Radiens
defaults; our own `04-processing-guidelines` §1). (2) **Our analysis DOES remove
60 Hz** — the 0.5-30 Hz band-pass excludes it by construction. (3) **Line-noise
bad-channel rejection is standard** (PREP pipeline, EEGLAB `clean_rawdata`); only
the threshold is ours, and those are always data-derived.
✅ **TELL ANDREA TO TURN THE ALLEGO NOTCH ON** — it is DISPLAY-ONLY (verified
2026-07-31: parked at 50 Hz, saved spectrum flat, no null), never reaches `.xdat`.
⚠️ **The ONE non-standard piece = `r@1min` persistence: it is a VALIDITY CHECK,
not a scoring rule** (assigns no epoch to a stage). Label it as ours.
🔑 **The unusual thing about this project is NOT the method, it is how much data
must be discarded — a hardware problem no analysis choice fixes.**


## From the memory index, trimmed there 2026-10-06 (kept here verbatim)

- ⭐⭐🔑 [THE ANALYSIS PIPELINE](eeg-analysis-pipeline.md) · [Scoring bug #2](eeg-analysis-codebase.md) · [QC tooling](eeg-qc-tooling.md) · [60 Hz saga](eeg-60hz-saga.md) · [First bring-up](project_first_headstage_bringup.md)
