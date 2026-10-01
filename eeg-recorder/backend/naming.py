#!/usr/bin/env python3
"""naming.py -- where each mouse's data lands on the NAS, and what it is called.

Since 2026-09-29 the SKIM NAS is organised BY ANIMAL, not by run:

    02_Data_Sleep/<user>/<batch>/<Baseline|Recovery>/<YYYYMMDD>_<MOUSEID>_<B|R>/
        <YYYYMMDD>_<MOUSEID>_<B|R>.csv
        <YYYYMMDD>_<MOUSEID>_<B|R>.info.json

    02_Data_Sleep/andrea/HLBSSL/Recovery/20260921_HLBSSL31_R/

The condition folder and the B/R code come from the recording type chosen FOR
EACH MOUSE in the console, so a run mixing baseline and recovery animals files
each one correctly without any joined `BSR-RSR` code. There is no SD folder:
the batch id (HLBWSD, HLBSSD...) already says which arm an animal is in.

Before this, a run was one folder `03_Data_Mouse/<user>/YYYYMMDD_<batch>_<BSR|RSR>`
holding the stripped xdat, and a second run of the same day became `...-2`, a
suffix that said nothing about what was different. See the 2026-09-29 entry in
`vault/02-procedures/CANONICAL-recording-naming-and-inventory.md`.

A BATCH NAME IS REQUIRED. The batch is a level of the tree, so a run without one
has nowhere to go. Screens and tests type one too (`SCREEN`, `TEST`).

THE DATE IS THE RECORDING'S, IN LOCAL TIME, AND IT COMES FROM THE UID -- or, for a
run trimmed to an analysis window (results.window), the window's start date. Not from
today, and not from `actual_start`, which is UTC -- a 08:55 KST start is 23:55
UTC on the PREVIOUS day. See `nas_upload.local_date_from_base`.

THE LOCAL FILES KEEP THEIR ALLEGO NAMES. Only the per-mouse CSVs carry these
names, and every `info.json` records the Allego base it came from, so the chain
back to the raw file is never lost.
"""
from __future__ import annotations

import re

# Same character class as a mouse id (layout.MOUSE_ID_RE). This becomes a
# directory name on a shared network share, so `../` and spaces are not negotiable.
BATCH_RE = re.compile(r"^[A-Za-z0-9_-]{1,32}$")


class NamingError(ValueError):
    """A batch name or run that cannot produce a folder name. Never guessed around."""


def clean_batch(name: str | None) -> str | None:
    """Validate a batch name, or None if the operator left it blank."""
    n = (name or "").strip()
    if not n:
        return None
    if not BATCH_RE.match(n):
        raise NamingError(
            f"recording batch name {n!r}: letters, digits, hyphen and underscore "
            "only, 1 to 32 characters. It becomes a folder name on the NAS.")
    return n


def require_batch(name: str | None) -> str:
    """A batch name, which every run now needs. Refuses a blank one."""
    b = clean_batch(name)
    if not b:
        raise NamingError(
            "a recording batch name is required: it is the folder the mice are "
            "filed under on the NAS (02_Data_Sleep/<user>/<batch>/...). Use the "
            "registry batch id, e.g. HLBSSL, or SCREEN for a test.")
    return b


def n_mice(slots: dict) -> int:
    return sum(1 for v in (slots or {}).values() if (v or {}).get("mouse_id"))


def mouse_entry(*, date_yyyymmdd: str, batch: str, mouse_id: str, rtype: str,
                cfg, suffix: int = 1) -> dict:
    """The destination of one mouse. `suffix` > 1 appends `-2`, `-3`..."""
    stem = f"{date_yyyymmdd}_{mouse_id}_{cfg.type_code(rtype)}"
    if suffix > 1:
        stem = f"{stem}-{suffix}"
    cond = cfg.type_folder(rtype)
    return {"batch": batch, "condition_dir": cond, "folder": stem,
            "file_base": stem, "rel": f"{batch}/{cond}/{stem}"}


def mouse_folders(run, cfg) -> dict:
    """{slot: destination} for every occupied slot of a run."""
    from nas_upload import local_date_from_base
    date = local_date_from_base(run.base_name or "", run.actual_start).replace("-", "")
    # A run trimmed to an analysis window is dated by the WINDOW: the W-SD
    # baseline file starts 08-19 17:25, but the 24 h it contributes starts 08-20.
    win = ((getattr(run, "results", None) or {}).get("window") or {}).get("start_kst")
    if win:
        date = str(win)[:10].replace("-", "")
    batch = require_batch(getattr(run, "batch_name", None))
    out = {}
    for slot, v in sorted((run.slots or {}).items()):
        if not (v or {}).get("mouse_id"):
            continue
        out[slot] = {"slot": slot, "mouse_id": v["mouse_id"],
                     "recording_type": v.get("recording_type") or "basal",
                     **mouse_entry(date_yyyymmdd=date, batch=batch,
                                   mouse_id=v["mouse_id"],
                                   rtype=v.get("recording_type") or "basal", cfg=cfg)}
    if not out:
        raise NamingError("no occupied slot, so there is no mouse to name")
    return out


def preview(*, batch_name, slots, cfg, date_yyyymmdd) -> dict:
    """The same rule, for the UI, before any recording exists."""
    batch = clean_batch(batch_name)
    if not batch:
        return {"batch": None, "mice": [], "folder": None}
    mice = []
    for slot, v in sorted((slots or {}).items()):
        if not (v or {}).get("mouse_id"):
            continue
        e = mouse_entry(date_yyyymmdd=date_yyyymmdd, batch=batch, mouse_id=v["mouse_id"],
                        rtype=v.get("recording_type") or "basal", cfg=cfg)
        mice.append({"slot": slot, "mouse_id": v["mouse_id"], **e})
    return {"batch": batch, "mice": mice, "folder": mice[0]["rel"] if mice else None}
