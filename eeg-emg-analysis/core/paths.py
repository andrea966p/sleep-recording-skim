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
    EEG_CACHE_ROOT       per-recording feature caches. NOT scratch: see below
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
# Per-mouse CSVs made by export/per_mouse_csv.py, staged here until the recorder
# has uploaded and verified them. Also a sibling of RAW_ROOT, for the same reason.
PER_MOUSE_ROOT = _env("EEG_PER_MOUSE_ROOT", HOME / "radix" / "per-mouse")
PROCESSED_ROOT = _env("EEG_PROCESSED_ROOT", HOME / "eeg-processed")
IMPEDANCE_ROOT = _env("EEG_IMPEDANCE_ROOT", HOME / "Downloads" / "impedance measurments")
# The vault lives in the same repo as this code: sleep-recording-skim/vault.
VAULT_ROOT = _env("EEG_VAULT_ROOT", Path(__file__).resolve().parents[2] / "vault")
# NOT /tmp. A feature cache looks disposable and is not: once a recording has
# been stripped to 16 channels its wire-free floor is gone from the file forever,
# and this .npz is the only surviving record of it -- which is why
# convert/strip_channels refuses to strip a recording that has none. The default
# was /tmp/eeg_pipeline_cache until 2026-09-23, and tmpfiles.d empties /tmp on
# every boot: the 2026-09-22 reboot destroyed the bundles for three recordings
# that had already been stripped, recoverable only because each had been copied
# to the NAS beside its upload.
CACHE_ROOT = _env("EEG_CACHE_ROOT", HOME / "eeg-qc-cache")
FIGURE_STYLE_DIR = _env(
    "EEG_FIGURE_STYLE_DIR",
    HOME / "Monitoring_project" / ".claude" / "skills" / "scientific-visualization")

# conventional sub-locations, derived so they cannot drift from their root
# every image and figure file the vault embeds lives flat in _attachments/ (since 2026-10-22)
VAULT_ATTACHMENTS = VAULT_ROOT / "_attachments"


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
