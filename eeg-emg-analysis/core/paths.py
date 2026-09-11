#!/usr/bin/env python3
"""Every filesystem location this project reads or writes, in one place.

WHY THIS EXISTS. Before 2026-08-10 there were 31 copies of `/home/skimlab/...`
spread across the scripts, including one inside `tests/test_criteria_regression.py`
-- which meant THE REGRESSION SUITE, the thing the README calls "the contract",
could not run on anybody else's machine. A contract that only one laptop can
check is not a contract. A reviewer who cannot re-run the numbers has to take
them on trust, and this project's whole argument is that it does not ask for
trust.

Each location is an environment variable with the value that has always been
used as its default, so nothing changes for the machine this was written on and
everything becomes overridable everywhere else:

    EEG_RAW_ROOT         where Allego writes .xdat recordings
    EEG_STRIPPED_ROOT    where channel-stripped copies of those recordings go
    EEG_PROCESSED_ROOT   where stage 2 writes per-animal .npz day folders
    EEG_IMPEDANCE_ROOT   the impedance sweep CSV folders, one per date
    EEG_VAULT_ROOT       the Obsidian vault that receives figures and reports
    EEG_CACHE_ROOT       scratch for the per-recording feature caches
    EEG_FIGURE_STYLE_DIR the scientific-visualization skill's scripts/assets

Nothing here creates a directory as a side effect of being imported. Ask for one
with `ensure()` at the point you are about to write.
"""
from __future__ import annotations

import os
from pathlib import Path

HOME = Path.home()


def _env(name: str, default: Path) -> Path:
    v = os.environ.get(name)
    return Path(v).expanduser() if v else default


# --------------------------------------------------------------------------- #
# roots
# --------------------------------------------------------------------------- #
RAW_ROOT = _env("EEG_RAW_ROOT", HOME / "radix" / "data")

# A SIBLING of RAW_ROOT, deliberately NOT a subdirectory of it.
# `neurosurveillance/deploy/radix-archive.sh` archives whatever `ls -1 "$SRC"`
# returns for SRC=RAW_ROOT, the pipeline globs the same directory, and Allego
# itself scans it. A stripped twin placed inside RAW_ROOT would therefore be
# archived a second time and would appear to every one of those readers as
# another recording with the same base name and a different channel count.
# Putting it one level across keeps it out of every existing glob for free.
STRIPPED_ROOT = _env("EEG_STRIPPED_ROOT", HOME / "radix" / "stripped")
PROCESSED_ROOT = _env("EEG_PROCESSED_ROOT", HOME / "eeg-processed")
IMPEDANCE_ROOT = _env("EEG_IMPEDANCE_ROOT", HOME / "Downloads" / "impedance measurments")
VAULT_ROOT = _env("EEG_VAULT_ROOT",
                  HOME / "Monitoring_project" / "Monitoring_project_obsidian_vault")
CACHE_ROOT = _env("EEG_CACHE_ROOT", Path("/tmp/eeg_pipeline_cache"))
FIGURE_STYLE_DIR = _env(
    "EEG_FIGURE_STYLE_DIR",
    HOME / "Monitoring_project" / ".claude" / "skills" / "scientific-visualization")

# conventional sub-locations, derived so they cannot drift from their root
VAULT_ATTACHMENTS = VAULT_ROOT / "05-experiments" / "attachments"
VAULT_COMPLETED = VAULT_ROOT / "05-experiments" / "completed"


# --------------------------------------------------------------------------- #
# helpers
# --------------------------------------------------------------------------- #
def recording(base: str) -> str:
    """Resolve a recording to a full base path.

    Accepts either a bare recording name (`allego_1__uid0806-16-57-38`), which is
    looked up under RAW_ROOT, or a path, which is returned as given. That is what
    lets a script take `--base <name>` on any machine and an absolute path when
    the file lives somewhere unusual.
    """
    p = Path(base).expanduser()
    if p.is_absolute() or os.sep in base:
        return str(p)
    return str(RAW_ROOT / base)


def cache(name: str) -> Path:
    """A path inside the feature cache. Does not create the directory."""
    return CACHE_ROOT / name


def ensure(path: Path) -> Path:
    """Create a directory (and parents) and return it. Call at write time."""
    path.mkdir(parents=True, exist_ok=True)
    return path


def describe() -> str:
    """Human-readable resolution report, for a card footer or a --paths flag."""
    rows = [("EEG_RAW_ROOT", RAW_ROOT),
            ("EEG_STRIPPED_ROOT", STRIPPED_ROOT),
            ("EEG_PROCESSED_ROOT", PROCESSED_ROOT),
            ("EEG_IMPEDANCE_ROOT", IMPEDANCE_ROOT),
            ("EEG_VAULT_ROOT", VAULT_ROOT),
            ("EEG_CACHE_ROOT", CACHE_ROOT),
            ("EEG_FIGURE_STYLE_DIR", FIGURE_STYLE_DIR)]
    width = max(len(k) for k, _ in rows)
    return "\n".join(
        f"{k:{width}}  {v}{'' if Path(v).exists() else '   [MISSING]'}"
        for k, v in rows)


if __name__ == "__main__":
    print(describe())
