"""Adapter for the 2026-08-08 figure set. Style and statistics come from
`cards/figs_common.py`; only this dated cohort's own constants live here.

WHY THIS IS NOW AN ADAPTER. Until 2026-08-10 this file and `cards/figs_common.py`
were two separate 300-line modules, and they had already drifted: the card module
had grown the verdict palette and two ink colours that this one never got. Of the
16 functions they shared, 13 were byte-identical copies and 3 differed only in how
they take an argument. Two copies of a statistics helper is two statistics
helpers, in exactly the way three copies of the usable-fraction loop turned out to
be three criteria.

So the shared 13 -- `save`, `holm_bh`, `block_bootstrap_ci`, `effective_n`,
`figure_with_caption`, the filters, the palette -- now have ONE definition, in
`cards/figs_common.py`. A figure drawn here and a card drawn there cannot again
disagree about what a Holm adjustment or an Okabe-Ito blue is.

What remains below is the part that is genuinely local: the file-naming and site
map of ONE cohort on ONE pair of recordings, and loaders that address an animal by
its RIG POSITION.

⚠️ POSITION IS NOT ANIMAL. `POS2FILE` keys are rig positions, and the B1 position
held two different mice across this project's history. That is tolerable here only
because this figure set is frozen to two recordings from a single day. Anything
that outlives those recordings must go through `cohorts/`, where the ANIMAL is the
key. Do not copy this map forward.
"""
from __future__ import annotations

import csv
import json

import numpy as np

# Re-export the whole shared surface. `import *` is deliberate here and nowhere
# else: these figure scripts are written against a flat namespace, and the
# alternative is 30 lines of explicit re-export that would go stale silently.
from cards.figs_common import *          # noqa: F401,F403
from cards.figs_common import PATHS      # noqa: F401

# --------------------------------------------------------------------------- #
# THIS COHORT, THESE TWO RECORDINGS
# --------------------------------------------------------------------------- #
PROC = PATHS.PROCESSED_ROOT / "2026-08-06"
RAW = PATHS.recording("allego_1__uid0806-16-57-38")

OVERNIGHT = "_2026-08-06_165738_23h40m"
AFTERNOON = "_2026-08-06_124502_3h11m"

POS2FILE = {"A1": "portA-slot1", "A2": "portA-slot2",
            "B1": "portB-slot1", "B2": "portB-slot2",
            "C1": "portC-slot1", "C2": "portC-slot2",
            "D1": "portD-slot1", "D2": "portD-slot2"}
POS_SITES = {"A1": ("A/1", "A/2"), "A2": ("A/33", "A/34"),
             "B1": ("B/1", "B/2"), "B2": ("B/33", "B/34"),
             "C1": ("C/1", "C/2"), "C2": ("C/33", "C/34"),
             "D1": ("D/1", "D/2"), "D2": ("D/33", "D/34")}


# --------------------------------------------------------------------------- #
# position-addressed loaders (the canonical module addresses files by path)
# --------------------------------------------------------------------------- #
def load_npz(pos, tag=OVERNIGHT):
    return np.load(PROC / (POS2FILE[pos] + tag + ".npz"), allow_pickle=True)


def load_features(pos, tag=OVERNIGHT):
    return json.loads((PROC / (POS2FILE[pos] + tag + "_features.json")).read_text())


def load_hypno(pos, tag=OVERNIGHT):
    with open(PROC / (POS2FILE[pos] + tag + "_hypnogram.csv")) as fh:
        return list(csv.DictReader(fh))
