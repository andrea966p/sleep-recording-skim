#!/usr/bin/env python3
"""rebuild_02_data_sleep.py -- put the eight canonical recordings into the
per-mouse NAS tree, 02_Data_Sleep/<user>/<batch>/<Baseline|Recovery>/.

ONE-OFF, 2026-09-29. Until then the SKIM NAS held one folder per RUN in
03_Data_Mouse/andrea/ with the stripped xdat. Analysis now reads one CSV per
mouse, so every recording that answers a protocol question is re-exported here.

WHICH RECORDINGS, AND WHICH HOURS. One baseline and one recovery per batch, each
CUT TO ITS ANALYSIS WINDOW, set by Andrea 2026-09-29:
    baseline, every batch        09:00 -> 09:00 next day, 24 h
    recovery, ad libitum (SL)    09:00 -> 09:00 next day, 24 h
    recovery, deprivation (SD)   13:00 -> 09:00 next day, 20 h -- both SD
                                 recoveries were stopped at 09:05, so no longer
                                 window exists, and none can: the mice are sampled
A mouse folder is dated by its window's start, so the W-SD baseline (file started
08-19 17:25) is 20260820_..._B.

PAIRING. What matters is that a batch's baseline and recovery hold the SAME mice.
Each info.json says whether its mouse has the other half and where it is. S-SD B1
does not: HLBSSD13 was taken off the rig on 08-26 (chewed tether) and HLBSSD17
replaced it, so 13 has a baseline only and 17 a recovery only. Both go up, marked
unpaired; they cannot be compared. Superseded or off-protocol runs
(uid0819-09-00-00, uid0826-12-50-16, uid0920-09-00-07) are deliberately not
rebuilt: they stay on e10, S3 and the bilab NAS, and putting them back in the
per-mouse tree would recreate the duplicate folders this replaces.

WHO WAS WHERE. Resolved per rig position with the cohort manifests, the same
rule cards/ladder.py uses since c44e2c2: a per-animal `recordings` row naming
(base, position) wins; otherwise the placement in force at the recording's START
MOMENT, not its date.

THE SAME CODE PATH AS A LIVE RUN. Each recording becomes a run record in a
SEPARATE database (never the live runs.db) and goes through postprocess.Worker:
export, reserve folders, upload with cache-dropped read-back, info.json last,
local CSVs removed only after every one verified. There is no second
implementation of any of that here.

    # what would happen -- writes nothing
    /opt/neurosurveillance/venv/bin/python3 eeg-recorder/deploy/rebuild_02_data_sleep.py

    # do it, one recording at a time, refusing while the rig records
    ... rebuild_02_data_sleep.py --go [--only allego_0__uid0910-09-00-00]
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
sys.path.insert(0, str(REPO / "eeg-recorder" / "backend"))
sys.path.insert(0, str(REPO / "eeg-emg-analysis"))

from cohorts.load import load_manifest            # noqa: E402
from cohorts.schema import moment_from_base       # noqa: E402

# base, cohort manifest, registry batch stem, recording type, window start, end (KST)
CANONICAL = [
    ("allego_1__uid0819-17-25-20", "W-SD", "HLBWSD", "basal",    "2026-08-20 09:00", "2026-08-21 09:00"),
    ("allego_2__uid0827-12-58-32", "W-SD", "HLBWSD", "recovery", "2026-08-27 13:00", "2026-08-28 09:00"),
    ("allego_0__uid0825-09-00-00", "S-SD", "HLBSSD", "basal",    "2026-08-25 09:00", "2026-08-26 09:00"),
    ("allego_2__uid0902-13-00-28", "S-SD", "HLBSSD", "recovery", "2026-09-02 13:00", "2026-09-03 09:00"),
    ("allego_0__uid0910-09-00-00", "W-SL", "HLBWSL", "basal",    "2026-09-10 09:00", "2026-09-11 09:00"),
    ("allego_0__uid0917-09-00-09", "W-SL", "HLBWSL", "recovery", "2026-09-17 09:00", "2026-09-18 09:00"),
    ("allego_0__uid0912-08-55-18", "S-SL", "HLBSSL", "basal",    "2026-09-12 09:00", "2026-09-13 09:00"),
    ("allego_0__uid0921-00-17-34", "S-SL", "HLBSSL", "recovery", "2026-09-21 09:00", "2026-09-22 09:00"),
]
POSITIONS = ["A1", "A2", "B1", "B2", "C1", "C2", "D1", "D2"]
OWNER = "andrea"
STRIPPED = Path.home() / "radix" / "stripped"
RAW = Path.home() / "radix" / "data"
STATE_DB = Path.home() / ".local" / "state" / "eeg-recorder" / "rebuild-2026-09-29.db"
# The 8-mouse EEG+EMG layout every one of these was recorded with.
LAYOUT = {"setting": "eeg_emg", "setting_label": "EEG + EMG",
          "roles": {"eeg": 1, "emg": 2}, "headstage": "rhd2216_bipolar",
          "note": "reconstructed 2026-09-29 for the per-mouse rebuild"}


def who(cohort, base: str, pos: str):
    a = next((a for a in cohort.animals for r in a.recordings
              if r.base == base and r.position == pos), None)
    if a is None:
        when = moment_from_base(base)
        a = cohort.animal_at(pos, when) if when else None
    return a


def coverage(base: str, window: dict) -> dict:
    """What the stripped file actually covers of its window (reads the sidecar and
    a few timestamp pages only)."""
    from export import per_mouse_csv as E
    info = E.read_stripped(str(STRIPPED / base))
    import numpy as np
    ts0 = int(np.fromfile(info["ts"], dtype=np.int64, count=1)[0])
    w = E.resolve_window(window, info, ts0)
    return {k: v for k, v in w.items() if k not in ("lo", "hi")}


def pairings(rows: list[dict], cfg) -> None:
    """Mark every mouse paired (with its partner's folder) or unpaired."""
    import naming
    from nas_upload import local_date_from_base
    by_batch: dict = {}
    for p in rows:
        by_batch.setdefault(p["batch"], {})[p["rtype"]] = p
    for batch, d in by_batch.items():
        def rel(p, mid):
            date = p["window"]["start_kst"][:10].replace("-", "")
            return naming.mouse_entry(date_yyyymmdd=date, batch=batch, mouse_id=mid,
                                      rtype=p["rtype"], cfg=cfg)["rel"]
        for p in d.values():
            other = d.get("recovery" if p["rtype"] == "basal" else "basal")
            ids = {v["mouse_id"] for v in other["slots"].values()} if other else set()
            p["pairing"] = {}
            for pos, v in p["slots"].items():
                mid = v["mouse_id"]
                if mid in ids:
                    p["pairing"][pos] = {"paired": True, "partner": rel(other, mid),
                                         "partner_allego_base": other["base"]}
                else:
                    half = "recovery" if p["rtype"] == "basal" else "baseline"
                    p["pairing"][pos] = {
                        "paired": False,
                        "note": f"{mid} has no {half} recording in this batch; this "
                                "recording cannot be compared within the animal"}


def plan() -> list[dict]:
    out = []
    for base, cid, batch, rtype, ws, we in CANONICAL:
        cohort = load_manifest(cid)
        side = STRIPPED / f"{base}.xdat.json"
        start = json.loads(side.read_text())["status"]["start_time"] if side.exists() else None
        slots, missing = {}, []
        for pos in POSITIONS:
            a = who(cohort, base, pos)
            if a is None:
                missing.append(pos)
                continue
            slots[pos] = {"mouse_id": a.animal_id, "recording_type": rtype}
        window = {"start_kst": ws, "end_kst": we}
        out.append({"base": base, "cohort": cid, "batch": batch, "rtype": rtype,
                    "start_time": start, "slots": slots, "empty": missing,
                    "stripped": side.exists(), "window": window,
                    "coverage": coverage(base, window) if side.exists() else None})
    return out


def as_run(store, R, p: dict):
    """A run record that the worker will take from STRIPPED onward."""
    existing = [r for r in store.list(limit=500) if r.base_name == p["base"]]
    if existing:
        return existing[0]
    r = store.create(owner=OWNER, preset="8mice_eeg_emg", slots=p["slots"],
                     keep_labels=[f"{pos[0]}/{b}" for pos in p["slots"]
                                  for b in ((1, 2) if pos[1] == "1" else (33, 34))],
                     batch_name=p["batch"], dest_dir=str(RAW),
                     note=f"rebuild 2026-09-29 of {p['base']} into 02_Data_Sleep")
    for st in (R.SCHEDULED, R.STARTING, R.RECORDING, R.STOPPING, R.STOPPED, R.QC,
               R.STRIPPING):
        store.transition(r.run_id, st, detail="rebuild: recorded before the "
                                             "per-mouse workflow existed")
    return store.transition(
        r.run_id, R.STRIPPED, detail="rebuild: stripped copy already on disk",
        base_name=p["base"], base_path=str(RAW / p["base"]),
        actual_start=p["start_time"], layout=LAYOUT,
        results={"strip": {"dst_base": str(STRIPPED / p["base"])},
                 "window": p["window"], "pairing": p["pairing"],
                 "rebuild": {"cohort": p["cohort"], "identity_rule":
                             "cohort manifest: recordings row, else placement at "
                             "the start moment (cards/ladder.py since c44e2c2)"}})


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--go", action="store_true", help="actually export and upload")
    ap.add_argument("--only", action="append", default=[], help="limit to these bases")
    a = ap.parse_args(argv)

    import presets as P
    import naming
    cfg = P.load()
    rows = plan()
    pairings(rows, cfg)                  # over ALL rows, so --only still pairs correctly
    rows = [p for p in rows if not a.only or p["base"] in a.only]
    for p in rows:
        c = p["coverage"] or {}
        act = c.get("actual") or {}
        print(f"{p['batch']} {'BASELINE' if p['rtype'] == 'basal' else 'RECOVERY'}  "
              f"{p['base']}")
        print(f"  window  {p['window']['start_kst']} -> {p['window']['end_kst']}   "
              f"covered {act.get('start_kst', '?')} -> {act.get('end_kst', '?')}  "
              f"({act.get('hours', '?')} h; missing {c.get('missing_at_start_s', '?')} s "
              f"at start, {c.get('missing_at_end_s', '?')} s at end)")
        date = p["window"]["start_kst"][:10].replace("-", "")
        for pos, v in p["slots"].items():
            e = naming.mouse_entry(date_yyyymmdd=date, batch=p["batch"],
                                   mouse_id=v["mouse_id"], rtype=p["rtype"], cfg=cfg)
            pr = p["pairing"][pos]
            tag = "paired" if pr["paired"] else "UNPAIRED"
            print(f"  {pos:3s} {v['mouse_id']:9s} {tag:9s} {e['rel']}")
        if p["empty"]:
            print(f"{p['base']:30s} {','.join(p['empty'])}: no animal in the manifest -- not exported")
        if not p["stripped"]:
            print(f"{p['base']:30s} !! no stripped copy in {STRIPPED} -- cannot export")
        print()
    if not a.go:
        print("DRY RUN. Nothing was written. Re-run with --go to export and upload.")
        return 0

    import runs as R
    import postprocess as PP
    import nas_upload as NU
    NU.set_root(cfg.nas_root)
    if not NU.nas_status()["ok"]:
        print(f"REFUSED: {NU.nas_status().get('hint')}", file=sys.stderr)
        return 1
    store = R.RunStore(STATE_DB)
    w = PP.Worker(store, on_event=lambda m: print(m, flush=True))
    failed = 0
    for p in rows:
        if not p["stripped"]:
            failed += 1
            continue
        run = as_run(store, R, p)
        if run.state == R.DONE:
            print(f"{p['base']}: already DONE ({run.run_id})")
            continue
        if run.state in R.RETRY_TARGET:
            run = store.transition(run.run_id, R.RETRY_TARGET[run.state], detail="rebuild retry")
        out = w.process(run.run_id)
        print(f"{p['base']}: {out.state}" + (f" -- {out.error}" if out.error else ""), flush=True)
        if out.state != R.DONE:
            failed += 1
            print("stopping here; fix the cause and re-run -- finished recordings are skipped")
            break
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
