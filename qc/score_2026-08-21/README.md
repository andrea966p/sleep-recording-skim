# Scoring of allego_1__uid0819-17-25-20 (39.674 h, 2026-08-21)

Report: vault `05-experiments/completed/2026-08-21-39h-run-score.md`

| file | what |
|---|---|
| `compute.py` | one feature pass over the 140 GB file, cached to `features.npz` (427 s) |
| `score.py` | rungs 0-2 per position, **per-chip floor**, EEG by slope / EMG by hum |
| `scores.json` | the numbers |
| `emg_gate_perchip.json` | the EMG state-dependence gate, recomputed per-chip |
| `features.npz` | 14,282 epochs x 128 sites; regenerate with `compute.py` |

## Why a per-chip floor and not the library's

`core.criteria.floor_stats()` POOLS all 112 wire-free inputs across all eight chips.
The project's own `USABLE_FRACTION_DEFINITION`, in that same file, says the comparison
is against inputs "recorded simultaneously **through the same chip**".

On this recording the chips are not interchangeable: chip B1's floor sits at slope p1
-2.079 / 1237 uV RMS while the other seven sit at -0.68..-1.35 / 3451-4063 uV. The
pooled value of -1.633 is harsher than seven chips' own floors and more lenient than
the eighth. **Under the pooled floor every position fails the 15-minute block gate.**

`floor_stats()` is NOT fixed. These scripts compute the per-chip floor alongside it.
Fixing the library, and re-checking earlier results that used the pooled value, is owed.

## Run it

    cd ~/Monitoring_project/eeg-emg-analysis
    PYTHONPATH=. /opt/neurosurveillance/venv/bin/python3 qc/score_2026-08-21/compute.py
    PYTHONPATH=. /opt/neurosurveillance/venv/bin/python3 qc/score_2026-08-21/score.py

`radiens` and the deps live only in `/opt/neurosurveillance/venv`.
