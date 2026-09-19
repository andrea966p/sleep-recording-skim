#!/usr/bin/env python3
"""The epoch-grid guard in stage 3 must REFUSE a stage 2 file whose per-epoch
arrays disagree with its own signal length, and must leave good files alone.

WHY THIS EXISTS. On 2026-09-18 stage 3 was run against a recording that was
still being written. Stage 1 had fixed the epoch grid at 14,918 rows; stage 2
later read 14,963 epochs of signal from the grown file. `analyse` did
`ok = ok[:n]`, which leaves `ok` SHORT rather than padding it, so the trailing
45 epochs were never labelled and silently vanished. The run then died deep in
`otsu_sensitivity` on a broadcast error -- which was luck. Had `zt` been trimmed
the same way, it would have produced a plausible wrong answer with no error.

This test fails if that path ever becomes silent again.

    python3 tests/test_epoch_grid_guard.py
"""
import os
import sys
import tempfile

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core import qc_thresholds as T
from pipeline.stage3_features import InconsistentEpochGrid, check_epoch_grid

FS_OUT = 250
PASSED = FAILED = 0


def check(name, ok, detail=""):
    global PASSED, FAILED
    if ok:
        PASSED += 1
        print("  pass  %s" % name)
    else:
        FAILED += 1
        print("  FAIL  %s  %s" % (name, detail))


def grid(n_signal_epochs, n_rows):
    """A per-epoch array set as stage 2 would write it."""
    return {"epoch_ok": np.ones(n_rows, dtype=bool),
            "zt": np.linspace(0, 12, n_rows),
            "is_light": np.ones(n_rows, dtype=bool)}


def main():
    print("epoch-grid guard")

    # A consistent file must pass untouched.
    n = 10800
    try:
        check_epoch_grid("good.npz", n, grid(n, n))
        check("consistent grid is accepted", True)
    except InconsistentEpochGrid as exc:
        check("consistent grid is accepted", False, str(exc))

    # The measured 2026-09-18 case: signal longer than the epoch arrays.
    try:
        check_epoch_grid("live.npz", 14963, grid(14963, 14918))
        check("short epoch arrays are refused", False, "no exception raised")
    except InconsistentEpochGrid as exc:
        msg = str(exc)
        check("short epoch arrays are refused", True)
        check("message names every short array",
              all(k in msg for k in ("epoch_ok", "zt", "is_light")), msg)
        check("message gives both counts",
              "14963" in msg and "14918" in msg, msg)
        check("message names the cause",
              "still being written" in msg, msg)
        check("message gives the fix",
              "stage1_qc" in msg and "stage2_split" in msg, msg)

    # The opposite direction must refuse too: arrays LONGER than the signal
    # would index past the end of the labels.
    try:
        check_epoch_grid("long.npz", 14918, grid(14918, 14963))
        check("long epoch arrays are refused", False, "no exception raised")
    except InconsistentEpochGrid:
        check("long epoch arrays are refused", True)

    # A single disagreeing array is enough; they do not have to agree with
    # each other before being compared to the signal.
    arrays = grid(n, n)
    arrays["zt"] = np.linspace(0, 12, n - 1)
    try:
        check_epoch_grid("one_bad.npz", n, arrays)
        check("one short array is enough to refuse", False, "no exception")
    except InconsistentEpochGrid as exc:
        check("one short array is enough to refuse", True)
        check("message names only the offender",
              "zt" in str(exc) and "epoch_ok has" not in str(exc), str(exc))

    print("\n%d passed, %d failed" % (PASSED, FAILED))
    return 1 if FAILED else 0


if __name__ == "__main__":
    raise SystemExit(main())
