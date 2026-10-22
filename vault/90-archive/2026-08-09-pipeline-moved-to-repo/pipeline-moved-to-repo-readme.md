---
tags: [archive, eeg, pipeline]
created: 2026-08-09
superseded-by: "eeg-emg-analysis/pipeline/"
---

# Archived: the pipeline code, as it stood in the vault on 2026-08-09

These are the exact files that lived in
`02-procedures/eeg-data-analysis/pipeline/` until 2026-08-09. **They are kept
only so a historical number can be reproduced. Do not run them.**

## Where the live code is now

`~/Monitoring_project/eeg-emg-analysis/pipeline/`

The operating manual stayed in the vault:
[[eeg-pipeline-manual]]. The new first step is
[[animal-card-and-verdict-ladder]].

## Why it moved

Two trees of code both claimed to be the analysis, and they disagreed about the
numbers:

| constant | vault `qc_thresholds.py` | `eeg-emg-analysis/qc/` |
| --- | --- | --- |
| epoch length | 4 s | 10 s |
| impedance pass mark | 2.0 MΩ | 0.5 MΩ |
| rail voltage | 6389.565 µV | 6389.6 µV (and 6390.0 in `core/config.py`) |

Beyond the constants, the usable-fraction loop existed in three copies and the
filter chain in five, all copy-pasted. Copies drift, and a drifted copy produces
a number nobody can trace.

Everything now imports `eeg-emg-analysis/core/qc_thresholds.py`, which is the
only place any of these are defined. The animal card prints that file's content
hash in its footer, so a figure can never silently have come from a different
set of numbers.

## What changed in the move, and what did not

**Changed, deliberately, each recorded at the constant:**

* `IMP_CONNECTED_MOHM` 2.0 → **0.5**. At 2.0 MΩ a cut tether attached to nothing
  reads "connected" in 22% of channel-sweeps, against 3.1% at 0.5. This affects
  only the reported "connected" count in `impedance_summary.csv`, which is a
  column and not a gate, so no animal moves into or out of the analysis.
* `EPOCH_S` split into `EPOCH_S_STAGING = 4` and `EPOCH_S_QC = 10`, which were
  always two different jobs pretending to be one constant.

**Not changed:** every threshold that decides a verdict. Proved by reproducing
each published usable fraction exactly, including the 415.0 µV floor threshold
from 953,904 wire-free measurements and B1's 215.8 minute unbroken block. The
regression suite is `eeg-emg-analysis/tests/test_criteria_regression.py`.
