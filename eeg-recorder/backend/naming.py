#!/usr/bin/env python3
"""naming.py -- what a run is called once it leaves this machine.

Allego names its own files after the box and a timestamp:
`allego_0__uid0913-11-20-07`. That is unambiguous and completely unreadable, and
it is what the NAS folders were named after until 2026-09-13. People asked for
their own name on the folder, which is reasonable: the person looking for last
week's recovery cohort is not looking for `allego_0__uid0925`.

    folder    YYYYMMDD_<batch>_<CODE>
    files     YYYYMMDD_<batch>_<CODE>_<N>mice{_data.xdat,_timestamp.xdat,.xdat.json}

    20260925_HLBSSL_RSR/
        20260925_HLBSSL_RSR_8mice_data.xdat
        20260925_HLBSSL_RSR_8mice_timestamp.xdat
        20260925_HLBSSL_RSR_8mice.xdat.json
        20260925_HLBSSL_RSR_8mice.strip-report.json
        run.json  UPLOAD.json  qc/

THE RENAME HAPPENS ON THE NAS, NOT ON THIS MACHINE. The local stripped copy keeps
its Allego name, because the strip is resumable and idempotent on exactly that
name -- the report, the manifest keys and the "already stripped and verified"
check are all keyed to it. Renaming locally would make a re-run look like a new
file. The chain from human name back to machine file is not lost: every stripped
sidecar carries the source base, its uid and both source hashes in
`status.dataset_provenance`, and `run.json` travels in the same folder.

THE DATE IS THE RECORDING'S, IN LOCAL TIME, AND IT COMES FROM THE UID. Not from
today, and not from `actual_start`, which is UTC -- a 08:55 KST start is 23:55
UTC on the PREVIOUS day, and dating from it labelled the first real 24 h run a
day early. See `nas_upload.local_date_from_base`.
"""
from __future__ import annotations

import re

# Same character class as a mouse id (app.py SAFE). This becomes a directory name
# on a shared network share, so `../` and spaces are not negotiable.
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


def type_codes(slots: dict, cfg) -> str:
    """The code section of the folder name, from the occupied slots' types.

    ONE RUN CAN HOLD MICE OF DIFFERENT TYPES. The rig records all four ports at
    once, so a basal animal and a recovery animal can share a run, and the
    request ("recording types in the mice silos as recovery") assumed they agree.
    When they do not, every code present is joined in config order --
    `20260925_HLBSSL_BSR-RSR` -- rather than picking one and quietly filing half
    the animals under the wrong condition. Refusing instead would block a run for
    a naming detail, which is the mistake the mouse-id blocker already taught.
    """
    present = []
    for slot, v in sorted((slots or {}).items()):
        if not (v or {}).get("mouse_id"):
            continue
        code = cfg.type_code((v or {}).get("recording_type") or "basal")
        if code not in present:
            present.append(code)
    if not present:
        raise NamingError("no occupied slot, so there is no recording type to name")
    order = {cfg.type_code(t): i for i, t in enumerate(cfg.recording_types)}
    return "-".join(sorted(present, key=lambda c: order.get(c, 99)))


def n_mice(slots: dict) -> int:
    return sum(1 for v in (slots or {}).values() if (v or {}).get("mouse_id"))


def run_names(run, cfg, *, suffix: int = 1) -> dict:
    """{folder, file_base} for a run, or the Allego-named fallback.

    `suffix` > 1 appends `-2`, `-3`... to BOTH the folder and the file base, so
    two same-day runs of the same batch and condition stay distinguishable even
    after someone downloads them into one directory. It is resolved against the
    NAS once and then frozen on the run (`run.nas_dir`), because a resumed upload
    must land in the folder it started in, not create a new one.
    """
    from nas_upload import local_date_from_base
    date = local_date_from_base(run.base_name or "", run.actual_start).replace("-", "")

    batch = clean_batch(getattr(run, "batch_name", None))
    if not batch:
        # No name given: the old layout, unchanged. Nothing in the pipeline
        # depends on a batch name existing, so a blank field is not a failure.
        return {"folder": f"{date[:4]}-{date[4:6]}-{date[6:]}_{run.base_name}",
                "file_base": run.base_name, "renamed": False}

    tail = "" if suffix <= 1 else f"-{suffix}"
    stem = f"{date}_{batch}_{type_codes(run.slots, cfg)}{tail}"
    return {"folder": stem,
            "file_base": f"{stem}_{n_mice(run.slots)}mice",
            "renamed": True}


def preview(*, batch_name, slots, cfg, date_yyyymmdd) -> dict:
    """The same rule, for the UI, before any recording exists."""
    batch = clean_batch(batch_name)
    if not batch:
        return {"folder": None, "file_base": None, "renamed": False}
    stem = f"{date_yyyymmdd}_{batch}_{type_codes(slots, cfg)}"
    return {"folder": stem, "file_base": f"{stem}_{n_mice(slots)}mice",
            "renamed": True}
