---
name: test-suite-two-of-four-verify-nothing
description: "The eeg-emg-analysis test suites are standalone scripts (not pytest) and two regression suites verify nothing on e10 because their recording is only in S3; since 2026-09-26 they exit 2. How to run them is in the vault"
metadata: 
  node_type: memory
  type: project
  originSessionId: aa023ba0-4d68-4842-9819-c574f4dde34b
  modified: 2026-10-22T00:00:00.000Z
---

Measured 2026-08-24, corrected 2026-10-22: the suites in `eeg-emg-analysis/tests/` are mostly standalone scripts (run with `PYTHONPATH=. /usr/bin/python3 tests/test_x.py` from the repo root), and `test_criteria_regression.py` and `test_ladder_verdicts.py` verify nothing on e10 (their recording `allego_1__uid0806-16-57-38` is only in S3). The 08-24 claim that they exit 0 and print a false success is OUTDATED: since 2026-09-26 both print "NOTHING WAS VERIFIED" and exit 2 (could not verify, not failed, not passed).

Details: [[analysis-test-suites]] · [[animal-card-verdict-ladder]] · [[analysis-stack-audit-2026-08-11]]

- 🛑 "3 test suites green" is not evidence of the ladder contract unless the regression suites actually ran: check the exit code is 0 and the output does not say SKIPPED.
- pytest lives in `~/eeg-test-venv` (`--system-site-packages`, numpy 1.26.4 + scipy 1.11.4). Do NOT reuse `~/eeg-analysis-venv`: its numpy 2.5 removed `np.trapz` ([[hypnograms-and-per-mouse-export]]).
