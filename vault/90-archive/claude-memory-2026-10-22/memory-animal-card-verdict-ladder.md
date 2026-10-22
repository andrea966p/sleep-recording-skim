---
name: animal-card-verdict-ladder
description: "The ANIMAL CARD + six-rung VERDICT LADDER is now the analysis entry point; code consolidated into eeg-emg-analysis, cohort HLB-fem-profsurgery-troubleshooting"
metadata: 
  node_type: memory
  type: project
  originSessionId: 9e891ed8-8737-468b-92b3-91e670ec3574
  modified: 2026-08-09T02:15:54.458Z
---

Built 2026-08-09. Replaces "run a script and squint" with one A4 page + JSON per
animal-recording. **Start at vault `02-procedures/eeg-data-analysis/animal-card-and-verdict-ladder.md`.**

**Rungs:** 0 FILE · 1 IDENTITY · 2 CONNECTION · 3 SCOREABILITY · 4 ARCHITECTURE
(always PROVISIONAL until a kappa) · 5 EXPORT. 🔑 **A rung is not evaluated if the
one below failed — it reads BLOCKED and NO PANEL IS DRAWN.** INSUFFICIENT ("could
not ask") is deliberately distinct from FAIL.

**Code moved out of the vault** to `~/sleep-recording-skim/eeg-emg-analysis/`:
`core/qc_thresholds.py` is the ONLY constants file (vault copies archived at
`99-archive/2026-08-09-pipeline-moved-to-repo/`); `core/criteria.py` is the ONLY
usable-fraction engine (was 3 copies) and filter chain (was 5). Reconciled:
`IMP_CONNECTED_MOHM` 2.0 → **0.5**; `EPOCH_S` split into `EPOCH_S_STAGING=4` and
`EPOCH_S_QC=10`.

🔴 **Two guards that fire as hard errors:** the HUM criterion is refused when it
contradicts SLOPE (the no-ground signature) — **but only on EEG roles**, because
a healthy EMG is also quiet+flat; and SLOPE is refused on any non-EEG role.

🔑 **Rung 2 gates on LONGEST UNBROKEN BLOCK (≥15 min), not on total fraction.** A
fraction gate rejects C1 on 2026-07-31 (30.3% usable, but one 485.7 min block =
the project's only real sleep).

⭐ **Cohort manifest `cohorts/HLB-fem-profsurgery-troubleshooting.yaml`** makes the
ANIMAL the key, not the rig position — B1 was two different mice. Tether-arm
placements carry a TIME (D2's arm C swap was 16:27 on 08-06, between two
recordings that day). Husbandry fields are nearly all "not recorded" and the card
says so on every page; join a sheet with `--husbandry x.xlsx`.

**Three test suites, all green, and they are the contract:**
`tests/test_criteria_regression.py` reproduces every published number exactly
(floor 415.02 µV / 953,904 measurements; B1 99.62% / 215.80 min; D2 86.54% /
87.30 min). `tests/test_ladder_verdicts.py` reproduces the vault's scoreable set
16/16. **Any movement is a bug, not an improvement.**

Outputs: `cards/out/<cohort>/` (32 card JSON + PNG/PDF), cohort sheet, and
generated report `05-experiments/completed/2026-08-09-HLB-cohort-report-generated.md`
(NO typed-in numbers — regenerate with `cards/report_cohort.py`).

Related: [[eeg-analysis-pipeline]] · [[recording-usable-fraction-analysis]] ·
[[ground-fix-worked-2026-08-08]]


## From the memory index, trimmed there 2026-10-06 (kept here verbatim)

- ⭐⭐⭐ **[ANIMAL CARD + VERDICT LADDER](animal-card-verdict-ladder.md). READ BEFORE ANY ANALYSIS OR FIGURE.** Six rungs. `core/qc_thresholds.py` + `core/criteria.py` are the only engines. Rung 2 gates on longest unbroken block ≥15 min.
