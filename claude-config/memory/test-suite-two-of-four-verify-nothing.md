---
name: test-suite-two-of-four-verify-nothing
description: "2026-08-24: the analysis test suites are runnable scripts (not pytest), and two of the four silently verify nothing because their fixture recording is no longer on disk — one of them prints a success message claiming agreement it never checked"
metadata: 
  node_type: memory
  type: project
  originSessionId: aa023ba0-4d68-4842-9819-c574f4dde34b
  modified: 2026-08-24T10:16:15.295Z
---

🔴⭐⭐ **"3 test suites green = the contract" IS NOT CURRENTLY TRUE.** Measured 2026-08-24.

## FIRST, A CORRECTION I MADE AND HAD TO WITHDRAW
I claimed the suites "cannot be run because there is no pytest". **FALSE.** They are not pytest
tests at all — `tests/test_*.py` contain **zero `test_` functions**; they are standalone scripts
with module-level asserts or a `main()`. `pytest tests/` collects nothing and reports
`no tests ran`. **Run them as scripts, and PYTHONPATH must be set or every one dies on
`ModuleNotFoundError: No module named 'core'`:**
```bash
cd ~/sleep-recording-skim/eeg-emg-analysis
PYTHONPATH=. /usr/bin/python3 tests/test_cohort_schema.py
PYTHONPATH=. /usr/bin/python3 tests/test_criterion_falsification.py
PYTHONPATH=. /usr/bin/python3 tests/test_ladder_verdicts.py
PYTHONPATH=. /usr/bin/python3 tests/test_criteria_regression.py
```

## 🔴 WHAT ACTUALLY RUNS — all four exit 0, only TWO verify anything
| suite | exit | really tested? |
|---|---|---|
| `test_cohort_schema` | 0 | ✅ real, every assert runs |
| `test_criterion_falsification` | 0 | ✅ real, synthetic data, accepts signal + refuses the traps |
| `test_ladder_verdicts` | 0 | 🔴 **SKIPPED BOTH CASES** — "no cached features for uid0731", "regression_uid0806-16-57-38.npz: not cached" |
| `test_criteria_regression` | 0 | 🔴 prints **"SKIPPED -- NOTHING WAS VERIFIED"** and returns 0 anyway (`tests/test_criteria_regression.py:91,97`) |

🔴🔴 **`test_ladder_verdicts.py:139` PRINTS A FALSE CLAIM.** After skipping both cases it still
prints *"all ladder verdict tests pass: the ladder agrees with the vault's scoreable set on both
recordings"*. It agreed with nothing — it loaded nothing. **A green line from that script is not
evidence.** Fix: make a skip exit non-zero, or at minimum print SKIPPED instead of "pass".

## WHY THEY SKIP
Both need **`allego_1__uid0806-16-57-38`**, which is **NOT in `~/radix/data`** any more (15 xdat
files there, none from 08-06) and there is no cached feature npz for it
(`/tmp/eeg_pipeline_cache/` holds only `allego_1__uid0819-17-25-20_feat.npz`, and `CACHE_ROOT` is
under `/tmp` so it does not survive a reboot). Override with `EEG_RAW_ROOT=/path/to/data` if the
recording is restored. ⚠️ **NAS check failed: `ssh bilab-syn.tail8808c0.ts.net` → `Connection
refused` on port 22**, so whether the archive still holds it is UNCONFIRMED — see
[[nas-backup-stale-address-outage]] and [[raw-data-archive-and-recording-automation]].

## PYTEST, IF IT IS EVER WANTED
No pip and no pytest on `/usr/bin/python3`, `/opt/neurosurveillance/venv`, or
`~/eeg-analysis-venv`; system python is **PEP 668 externally-managed**, so a plain
`pip install` is refused and I cannot sudo. ✅ **No sudo needed** — a venv inheriting system
packages works:
```bash
/usr/bin/python3 -m venv --system-site-packages ~/eeg-test-venv
~/eeg-test-venv/bin/pip install pytest
```
Created 2026-08-24 at **`~/eeg-test-venv`**: python 3.12.3, **numpy 1.26.4 + scipy 1.11.4 (the same
versions the analysis runs on)**, pytest 9.1.1. 🔑 Use `--system-site-packages` so it inherits the
1.26/1.11 pair — do NOT reuse `~/eeg-analysis-venv`, whose numpy 2.5 removed `np.trapz`
([[hypnograms-and-per-mouse-export]]). ⚠️ pytest is useless until the scripts grow real `test_`
functions.

Related: [[animal-card-verdict-ladder]] (makes the "3 suites green" claim) ·
[[analysis-stack-audit-2026-08-11]] · [[recording-2026-08-24-new-8-mice]]
