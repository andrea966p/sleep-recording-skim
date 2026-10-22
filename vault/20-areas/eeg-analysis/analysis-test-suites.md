---
type: reference
area: eeg-analysis
status: active
created: 2026-10-22
summary: "How to run the eeg-emg-analysis test suites, and which of them verify nothing on e10 because their recordings are only in S3"
tags: [eeg, analysis, tests, regression]
---

# The analysis test suites: how to run them, and which ones verify nothing

> [!abstract] TL;DR
> The suites in `eeg-emg-analysis/tests/` are mostly **standalone scripts with a `main()`**, not
> pytest tests. Run each one directly with `PYTHONPATH=.` from the repo root.
> 🔴 **Two regression suites verify nothing on e10**: `test_criteria_regression.py` and
> `test_ladder_verdicts.py` need recordings that are no longer on disk. Since 2026-09-26 both say
> so and **exit 2**, which is "could not verify", not "failed" (1) and not "passed" (0).
> Checked by running both on 2026-10-22.

## Running them

```bash
cd ~/sleep-recording-skim/eeg-emg-analysis
PYTHONPATH=. /usr/bin/python3 tests/test_criterion_falsification.py
PYTHONPATH=. /usr/bin/python3 tests/test_cohort_schema.py
PYTHONPATH=. /usr/bin/python3 tests/test_ladder_verdicts.py
PYTHONPATH=. /usr/bin/python3 tests/test_criteria_regression.py
```

The last two exit 2 on e10 (see below). Without `PYTHONPATH=.` every suite stops on `ModuleNotFoundError: No module named 'core'`.

**pytest.** On 2026-10-22, 5 of the 15 files define `test_*` functions (`test_impedance_block_tools`,
`test_preflight_reason`, `test_record_block`, `test_stage1_cache_path`, `test_strip_channels`);
`tests/conftest.py` supplies the fixture so `test_strip_channels` works both ways. pytest collects
nothing from the other ten. A pytest is available in `~/eeg-test-venv` (created 2026-08-24 with
`--system-site-packages`, so it has the system numpy 1.26.4 / scipy 1.11.4 pair).
🛑 Do not reuse ~/eeg-analysis-venv for tests: its numpy 2.5 removed np.trapz; the test venv must inherit the system numpy 1.26.4 / scipy 1.11.4 pair (python 3.12.3, pytest 9.1.1 at creation).

## The two that verify nothing

| suite | needs | on e10, 2026-10-22 |
|---|---|---|
| `test_criteria_regression.py` | raw `allego_1__uid0806-16-57-38` under `EEG_RAW_ROOT` | prints `SKIPPED -- NOTHING WAS VERIFIED.`, exit 2 |
| `test_ladder_verdicts.py` | feature caches for uid0731 and uid0806 in `~/eeg-qc-cache` | prints `VERIFIED NOTHING: 2 of 2 recordings have no feature cache`, exit 2 |

Both recordings live only in S3 now ([[radix-s3-archive]], journal [[2026-09-26]]), so these suites can
be revived only by pulling the raw files back and setting `EEG_RAW_ROOT`.

> [!warning] A green line used to be a false claim
> Found 2026-08-24: both suites skipped and still exited 0, and `test_ladder_verdicts.py` printed
> "all ladder verdict tests pass: the ladder agrees with the vault's scoreable set on both recordings"
> after loading nothing. Fixed 2026-09-26 (commit `c5bbd55`): both now exit 2. 🛑 A suite that
> verified nothing must never read like a pass. [[2026-09-26]]

The claim in [[animal-card-and-verdict-ladder]] that the regression test "reproduces every published
number exactly" was true on 2026-08-09; it cannot be re-checked on e10 today.

The falsification suite (`test_criterion_falsification.py` + `tests/synth.py`) is the software positive
control: it writes real `.xdat` files with the truth fixed in advance and asserts direction and
ordering, never pinned values. [[2026-08-11-analysis-stack-audit-measurements]]
