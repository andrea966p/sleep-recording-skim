#!/usr/bin/env python3
"""STAGE 2 -- split the recording into one file per mouse.

Layout produced:

    <root>/YYYY-MM-DD/
        portC-slot1_2026-07-31_180637_27h54m.npz     signals + QC mask
        portC-slot2_2026-07-31_180637_27h54m.npz
        impedance/imp_8mice_corrected.csv            sweeps for that day
        impedance/impedance_summary.csv              parsed, per site
        qc/qc_summary.csv                            stage 1 verdicts
        qc/qc_<recording>.json                       full stage 1 output
        README.txt                                   what is in this folder

Each .npz holds
    eeg, emg        float32 @ 250 Hz, microvolts, already bipolar
    fs              250
    epoch_ok        bool, one entry per 4 s epoch, the stage 1 QC gate
    blocks          (n, 2) epoch index pairs of unbroken contact
    zt              float32, zeitgeber time per epoch (ZT0 = 09:00 KST)
    is_light        bool per epoch
    meta            JSON string: port, slot, verdict, thresholds, provenance

The channel data written here is ALREADY the bipolar difference the RHD2216
produces. Do not subtract anything from it.

Usage
    python3 stage2_split.py <recording_base> [--root DIR] [--include-dirty]
"""
import argparse
import csv
import glob
import json
import os
import re
import shutil
import sys
import datetime as dt

import numpy as np
import scipy.signal as sg

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import qc_thresholds as T
import pipeline_common as P
import stage1_qc as S1

DEFAULT_ROOT = os.environ.get("EEG_PROCESSED_ROOT",
                              "/home/skimlab/eeg-processed/")
IMP_DIR = os.environ.get("EEG_IMPEDANCE_DIR",
                         "/home/skimlab/Downloads/impedance measurments/")

# Split anything that HAS usable consolidated data. CLEAN and DIRTY both do --
# they differ in how much of the recording is usable, not in whether any of it
# is. INSUFFICIENT / OPEN / DEAD / CLIPPED have nothing to split.
#
# This default matters: C1 on 2026-07-31 is the best animal in the project
# (8.73 h in a single 4.4 h-median block) but is DIRTY, because the other 19 h
# of that recording is open. A CLEAN-only default silently drops it.
KEEP_VERDICTS = {"CLEAN", "DIRTY"}


# ---------------------------------------------------------------------------
def parse_impedance(path):
    """Parse an Allego impedance export.

    Only the /1 (EEG) and /2 (EMG) sites carry a wire. /3 and /4 are EMPTY PADS
    on the RHD2216 and their readings are meaningless -- including them is what
    produced the misleading impedance statistics before 2026-08-02.
    """
    rows = []
    with open(path, newline="", encoding="utf-8-sig") as fh:
        for r in csv.DictReader(fh):
            site = (r.get("SITE") or "").strip()
            m = re.match(r"^([A-H])/(\d+)$", site)
            if not m:
                continue
            port, ch = m.group(1), int(m.group(2))
            if ch not in (1, 2):
                continue
            try:
                mag = float(r.get("MAGNITUDE (MΩ)", "nan"))
                pha = float(r.get("PHASE (°)", "nan"))
            except ValueError:
                continue
            rows.append(dict(
                port=port, site=ch, kind="EEG" if ch == 1 else "EMG",
                magnitude_mohm=mag, phase_deg=pha,
                connected=bool(mag < T.IMP_CONNECTED_MOHM),
                literature_good=bool(mag <= T.IMP_GOOD_MOHM),
                source=os.path.basename(path)))
    return rows


def collect_impedance(day, out_dir, explicit=None):
    """Copy the impedance sweeps belonging to this day into the day folder."""
    os.makedirs(out_dir, exist_ok=True)
    files = list(explicit or [])
    if not files and os.path.isdir(IMP_DIR):
        target = dt.datetime.strptime(day, "%Y-%m-%d").date()
        for f in sorted(glob.glob(os.path.join(IMP_DIR, "*.csv"))):
            mtime = dt.date.fromtimestamp(os.path.getmtime(f))
            # a sweep taken the evening before or the morning after a run still
            # belongs to that run
            if abs((mtime - target).days) <= 1:
                files.append(f)
    rows = []
    for f in files:
        shutil.copy2(f, os.path.join(out_dir, os.path.basename(f)))
        rows.extend(parse_impedance(f))
    if rows:
        with open(os.path.join(out_dir, "impedance_summary.csv"), "w",
                  newline="") as fh:
            w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
            w.writeheader()
            w.writerows(rows)
    return files, rows


# ---------------------------------------------------------------------------
def decimate_to(x, fs_in, fs_out):
    """Anti-aliased decimation. Integer factors only, applied in stages."""
    if fs_in == fs_out:
        return x.astype(np.float32), fs_in
    assert fs_in % fs_out == 0, f"{fs_in} -> {fs_out} is not an integer ratio"
    q = fs_in // fs_out
    for f in _factors(q):
        x = sg.decimate(x, f, ftype="iir", zero_phase=True)
    return x.astype(np.float32), fs_out


def _factors(q):
    out = []
    for p in (5, 4, 3, 2):
        while q % p == 0 and q > 1:
            out.append(p)
            q //= p
    if q > 1:
        out.append(q)
    return out


# ---------------------------------------------------------------------------
def _read_columns(base, N, NC, fs, eeg_cols, emg_cols):
    """One sequential chunked pass over the raw file for all wanted columns."""
    cols = list(eeg_cols) + list(emg_cols)
    ne = len(eeg_cols)
    buf = np.empty((len(cols), N), dtype=np.float32)
    mm = np.memmap(os.path.join(P.DATA_DIR, base + "_data.xdat"),
                   dtype="<f4", mode="r", shape=(N, NC))
    try:
        step = fs * 600             # ten minutes at a time
        for s in range(0, N, step):
            e = min(s + step, N)
            # index the columns directly. `mm[s:e, :][:, cols]` would first
            # materialise ALL columns for the chunk -- 1.8 GB per hour at 128
            # channels -- which OOM-killed this script on 2026-08-03.
            buf[:, s:e] = mm[s:e, cols].T
            print(f"  read {100 * e / N:5.1f}%", end="\r", flush=True)
    finally:
        del mm
    print(" " * 24, end="\r")
    return buf[:ne], buf[ne:]


def split_recording(base, root=DEFAULT_ROOT, clean_only=False,
                    impedance=None, force=False):
    qc = S1.qc_recording(base)
    if qc is None:
        raise SystemExit(f"{base}: no animals in layout")

    keep = {"CLEAN"} if clean_only else set(KEEP_VERDICTS)
    day_dir = P.day_folder(root, dt.datetime.fromisoformat(qc["start_local"]))
    os.makedirs(day_dir, exist_ok=True)
    os.makedirs(os.path.join(day_dir, "qc"), exist_ok=True)

    json.dump(qc, open(os.path.join(day_dir, "qc", f"qc_{base}.json"), "w"),
              indent=1, default=P.jsafe)
    _write_qc_csv(qc, os.path.join(day_dir, "qc", "qc_summary.csv"))

    imp_files, imp_rows = collect_impedance(
        qc["day"], os.path.join(day_dir, "impedance"), explicit=impedance)

    meta = P.load_meta(base)
    info = P.recording_info(base, meta)
    labels, eeg_cols, emg_cols = P.derive_layout(meta)
    fs, N, NC = info["fs"], info["n_samp"], info["n_chan"]
    local = dt.datetime.fromisoformat(qc["start_local"])

    d = S1.extract_features(base)
    written = []

    # Which animals are we writing? Decide BEFORE touching the raw file, so it
    # is read exactly once no matter how many mice come out of it. Reading a
    # single column from a (N, 128) memmap is a strided walk over the whole
    # file, so doing it per mouse would re-read 105 GB per animal.
    todo = []
    for i, lab in enumerate(labels):
        a = qc["animals"][i]
        if a["verdict"] not in keep:
            print(f"  skip {a['name']}: {a['verdict']} -- {a['reason']}")
            continue
        fn = P.mouse_filename(lab["port"], lab["slot"], local, info["hours"], ".npz")
        path = os.path.join(day_dir, fn)
        if os.path.exists(path) and not force:
            print(f"  exists {fn}")
            written.append(path)
            continue
        todo.append((i, lab, fn, path))

    if todo:
        sig = _read_columns(base, N, NC, fs,
                            [eeg_cols[i] for i, *_ in todo],
                            [emg_cols[i] for i, *_ in todo])
    for k, (i, lab, fn, path) in enumerate(todo):
            a = qc["animals"][i]
            eeg_d, fso = decimate_to(sig[0][k], fs, T.OUTPUT_FS)
            emg_d, _ = decimate_to(sig[1][k], fs, T.OUTPUT_FS)

            ok, _ = S1.gate(d, i)
            blks = np.array([b for b in P.blocks_of(ok)
                             if b[1] - b[0] >= T.MIN_BLOCK], dtype=np.int64)
            if blks.size == 0:
                blks = np.zeros((0, 2), dtype=np.int64)
            offs = np.arange(len(ok)) * T.EPOCH_S
            zt = P.zt_hours(local, offs).astype(np.float32)

            m = dict(recording=base, port=lab["port"], slot=lab["slot"],
                     name=lab["name"],
                     eeg_native_col=int(eeg_cols[i]), emg_native_col=int(emg_cols[i]),
                     bipolar=True, subtract_anything=False,
                     start_local=qc["start_local"], start_utc=qc["start_utc"],
                     day=qc["day"], hours=info["hours"],
                     fs_raw=fs, fs_out=int(fso), epoch_s=T.EPOCH_S,
                     units="microvolt",
                     lights_on=T.LIGHTS_ON_HOUR, lights_off=T.LIGHTS_OFF_HOUR,
                     qc=a, thresholds=qc["thresholds"],
                     impedance_files=[os.path.basename(f) for f in imp_files],
                     pipeline_version="2026-08-03")
            np.savez_compressed(path, eeg=eeg_d, emg=emg_d, fs=np.int32(fso),
                                epoch_ok=ok, blocks=blks, zt=zt,
                                is_light=P.is_light(zt),
                                meta=json.dumps(m, default=P.jsafe))
            sz = os.path.getsize(path) / 1e6
            print(f"  wrote {fn}  ({sz:.0f} MB, {a['verdict']})")
            written.append(path)

    _write_readme(day_dir, qc, written, imp_files, imp_rows)
    return day_dir, written


def _write_qc_csv(qc, path):
    new = not os.path.exists(path)
    fields = ["recording", "day", "start_local", "name", "port", "slot",
              "verdict", "reason", "pct_pass", "gated_hours", "block_hours",
              "longest_block_min", "n_blocks", "median_block_s",
              "med_eeg_mains_uv", "med_eeg_rms_uv", "med_emg_rms_uv",
              "pct_epochs_railed"]
    with open(path, "a", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=fields, extrasaction="ignore")
        if new:
            w.writeheader()
        for a in qc["animals"]:
            w.writerow(dict(recording=qc["recording"], day=qc["day"],
                            start_local=qc["start_local"], **a))


def _write_readme(day_dir, qc, written, imp_files, imp_rows):
    n_conn = sum(1 for r in imp_rows if r["connected"])
    n_good = sum(1 for r in imp_rows if r["literature_good"])
    lines = [
        f"EEG/EMG processed data -- {qc['day']}",
        "=" * 60,
        f"recording      {qc['recording']}",
        f"start (local)  {qc['start_local']}  [source: {qc['start_source']}]",
        f"start (UTC)    {qc['start_utc']}",
        f"duration       {qc['hours']:.2f} h",
        f"raw rate       {qc['fs']} Hz    written at {T.OUTPUT_FS} Hz",
        f"light cycle    lights on {T.LIGHTS_ON_HOUR:02d}:00, off "
        f"{T.LIGHTS_OFF_HOUR:02d}:00 KST; ZT0 = {T.LIGHTS_ON_HOUR:02d}:00",
        "",
        "Signals are the RHD2216 BIPOLAR channels. /1 = EEG, /2 = EMG.",
        "Use them directly. Do NOT subtract one from the other.",
        "",
        "QC verdicts",
        "-" * 60,
    ]
    for a in qc["animals"]:
        lines.append(f"  {a['name']:<5} {a['verdict']:<13} {a['reason']}")
    lines += ["", f"Files written: {len(written)}"]
    for w in written:
        lines.append("  " + os.path.basename(w))
    lines += ["", "Impedance"]
    if imp_files:
        for f in imp_files:
            lines.append("  " + os.path.basename(f))
        lines.append(f"  sites read: {len(imp_rows)} (only /1 and /2 -- "
                     f"/3 and /4 are empty pads)")
        lines.append(f"  connected (< {T.IMP_CONNECTED_MOHM} MOhm): "
                     f"{n_conn}/{len(imp_rows)}")
        lines.append(f"  at literature quality (<= {T.IMP_GOOD_MOHM} MOhm = "
                     f"100 kOhm): {n_good}/{len(imp_rows)}")
        lines.append("  NOTE resting impedance predicts WHICH channel is "
                     "connected, not how many usable hours it yields.")
    else:
        lines.append("  none found for this day")
    open(os.path.join(day_dir, "README.txt"), "w").write("\n".join(lines) + "\n")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("bases", nargs="+")
    ap.add_argument("--root", default=DEFAULT_ROOT)
    ap.add_argument("--clean-only", action="store_true",
                    help="write only CLEAN animals (drops usable DIRTY ones)")
    ap.add_argument("--impedance", nargs="*", default=None)
    ap.add_argument("--force", action="store_true")
    a = ap.parse_args()
    for b in a.bases:
        print(f"\n=== {b}")
        day_dir, written = split_recording(
            b, root=a.root, clean_only=a.clean_only,
            impedance=a.impedance, force=a.force)
        print(f"  -> {day_dir}  ({len(written)} mouse files)")


if __name__ == "__main__":
    main()
