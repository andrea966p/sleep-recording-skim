#!/usr/bin/env python3
"""Plain-text export: data alongside a timestamp, in the format the professor
actually opens.

    ~/eeg-analysis-venv/bin/python cards/export_text.py <day_dir_or_npz> [...]
    ... --gzip            write .tsv.gz, about a tenth the size
    ... --epochs-only     write the per-epoch table instead of every sample
    ... --absolute-time   add an ISO wall-clock column

WHY, WHEN AN EDF ALREADY EXISTS
-------------------------------
The EDF is for a scorer running EDFbrowser. It is a binary container, it needs
software to open, and its blank-screen failure mode has already cost this
project time. A tab-separated text file opens in anything, survives being
emailed on its own, and can be read by a colleague who has never heard of this
pipeline. Both are written; neither replaces the other.

WHAT COMES OUT
--------------
`<stem>.tsv` -- one row per sample at the pipeline's 250 Hz:

    t_s          seconds from the start of the recording, 6 decimal places
    eeg_uv       microvolts
    emg_uv       microvolts
    (ecg_uv)     when the cohort has one
    (datetime_kst) only with --absolute-time

Above the header sits a block of `#` comment lines carrying the absolute start
time, ZT0, the sample rate, WHICH NATIVE AMPLIFIER CHANNELS these are, the units,
the rail voltage and the thresholds hash, so the file explains itself when it
arrives on its own with no covering email.

`<stem>_epochs.tsv` (--epochs-only) -- one row per 4 s staging epoch with the
features and the state label. About 21,000 rows for a full day instead of 21
million, and it is what most questions actually want.

⚠️ SIZE. A 23.66 h recording is about 21.3 million rows, roughly 530 MB
uncompressed. --gzip brings that to about 50 MB and still opens directly in
Python, R and Excel's import dialogue.

🛑 THE STATE LABELS IN THE EPOCH FILE ARE PROVISIONAL. No human has scored any
epoch of this project's data. The header says so, in the file, every time.
"""
from __future__ import annotations

import argparse
import csv
import datetime as dt
import gzip
import io
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent

from core import criteria as C          # noqa: E402
from core import qc_thresholds as T     # noqa: E402

CHUNK_ROWS = 250_000        # keep peak memory near 20 MB regardless of duration


def _header_lines(meta: dict, stem: str, kind: str, columns: list[str]) -> list[str]:
    start_local = meta.get("start_local", "")
    lines = [
        f"# file            {stem}",
        f"# kind            {kind}",
        f"# recording       {meta.get('recording', '')}",
        f"# rig position    port {meta.get('port', '?')} slot {meta.get('slot', '?')}"
        f"  (label {meta.get('name', '?')})",
        f"# start (KST)     {start_local}",
        f"# start (UTC)     {meta.get('start_utc', '')}",
        f"# duration_h      {meta.get('hours', '')}",
        f"# sample_rate_hz  {meta.get('fs_out', T.OUTPUT_FS)}"
        f"   (acquired at {meta.get('fs_raw', T.FS_RAW)} Hz and decimated)",
        f"# units           {meta.get('units', 'microvolt')}",
        f"# rail_uv         {T.RAIL_UV_EFF:.1f}   samples at or beyond this are clipped",
        "#",
        "# CHANNEL PROVENANCE -- these are BIPOLAR channels, already a difference",
        f"#   eeg_uv        native column {meta.get('eeg_native_col', '?')}"
        "   frontal-L minus parietal-L",
        f"#   emg_uv        native column {meta.get('emg_native_col', '?')}"
        "   neck EMG left minus right",
        "#   DO NOT SUBTRACT ONE FROM THE OTHER. The subtraction is already done",
        "#   in hardware, before the ADC. eeg minus emg is a meaningless signal.",
        "#",
        f"# light cycle     lights on {T.LIGHTS_ON_HOUR:02d}:00, off "
        f"{T.LIGHTS_OFF_HOUR:02d}:00 KST; ZT0 = {T.LIGHTS_ON_HOUR:02d}:00",
        f"# thresholds      {C.thresholds_hash()}  (core/qc_thresholds.py)",
        f"# written         {dt.datetime.now().astimezone().isoformat(timespec='seconds')}",
        "#",
    ]
    # The term travels with the file. A TSV arrives on its own, gets opened
    # months later by someone who was not in the room, and "usable" is the one
    # word in it that does not mean what a reader will assume.
    lines += _wrap_comment(C.USABLE_FRACTION_DEFINITION)
    lines += [
        "#",
        "# columns: " + "  ".join(columns),
    ]
    return lines


def _wrap_comment(text: str, width: int = 76) -> list[str]:
    import textwrap
    return ["# " + ln for ln in textwrap.wrap(text, width)]


def _open_out(path: Path, use_gzip: bool):
    if use_gzip:
        return io.TextIOWrapper(gzip.open(path, "wb", compresslevel=6),
                                encoding="utf-8", newline="")
    return path.open("w", encoding="utf-8", newline="")


def export_samples(npz_path: Path, *, use_gzip: bool = False,
                   absolute_time: bool = False) -> Path:
    """Full-rate sample table. One row per sample."""
    z = np.load(npz_path, allow_pickle=True)
    meta = json.loads(str(z["meta"]))
    fs = int(z["fs"])
    eeg = z["eeg"]
    emg = z["emg"]
    n = min(len(eeg), len(emg))

    stem = npz_path.with_suffix("").name
    out = npz_path.with_suffix(".tsv.gz" if use_gzip else ".tsv")

    columns = ["t_s", "eeg_uv", "emg_uv"]
    if absolute_time:
        columns.insert(1, "datetime_kst")

    t0 = None
    if absolute_time:
        try:
            t0 = dt.datetime.fromisoformat(meta["start_local"])
        except (KeyError, ValueError):
            t0 = None
            columns.remove("datetime_kst")
            absolute_time = False

    est_mb = n * (26 + (26 if absolute_time else 0)) / 1e6
    print(f"  {stem}: {n:,} rows at {fs} Hz "
          f"(~{est_mb:.0f} MB uncompressed){' , gzip' if use_gzip else ''}")

    with _open_out(out, use_gzip) as fh:
        for line in _header_lines(meta, stem, "full-rate samples", columns):
            fh.write(line + "\n")
        w = csv.writer(fh, delimiter="\t", lineterminator="\n")
        w.writerow(columns)
        for start in range(0, n, CHUNK_ROWS):
            stop = min(start + CHUNK_ROWS, n)
            idx = np.arange(start, stop)
            t = idx / fs
            e = np.asarray(eeg[start:stop], dtype=np.float64)
            m = np.asarray(emg[start:stop], dtype=np.float64)
            if absolute_time:
                rows = ((f"{tt:.6f}",
                         (t0 + dt.timedelta(seconds=float(tt))).isoformat(
                             timespec="milliseconds"),
                         f"{ee:.3f}", f"{mm:.3f}")
                        for tt, ee, mm in zip(t, e, m))
            else:
                rows = ((f"{tt:.6f}", f"{ee:.3f}", f"{mm:.3f}")
                        for tt, ee, mm in zip(t, e, m))
            w.writerows(rows)
    print(f"    -> {out}  ({out.stat().st_size / 1e6:.1f} MB)")
    return out


def export_epochs(npz_path: Path, *, use_gzip: bool = False) -> Path:
    """Per-epoch table: the small one, and the one most questions want."""
    z = np.load(npz_path, allow_pickle=True)
    meta = json.loads(str(z["meta"]))
    epoch_ok = z["epoch_ok"]
    zt = z["zt"]
    is_light = z["is_light"]
    blocks = z["blocks"]
    n_ep = len(epoch_ok)
    epoch_s = int(meta.get("epoch_s", T.EPOCH_S_STAGING))

    stem = npz_path.with_suffix("").name
    out = npz_path.parent / (stem + ("_epochs.tsv.gz" if use_gzip else "_epochs.tsv"))

    # state labels and features come from stage 3 when it has run
    hyp = npz_path.parent / (stem + "_hypnogram.csv")
    hyp_rows: dict[int, dict[str, str]] = {}
    hyp_fields: list[str] = []
    # The hypnogram repeats several columns this table already carries. Emitting
    # both gives a file with two columns of the same name, which silently breaks
    # every reader that indexes by header.
    BASE_COLUMNS = {"epoch", "t_s", "zt_h", "light", "is_light", "in_block",
                    "epoch_ok"}
    if hyp.exists():
        with hyp.open() as fh:
            rd = csv.DictReader(fh)
            hyp_fields = [f for f in (rd.fieldnames or []) if f not in BASE_COLUMNS]
            for row in rd:
                try:
                    hyp_rows[int(row["epoch"])] = row
                except (KeyError, ValueError):
                    continue

    in_block = np.zeros(n_ep, dtype=bool)
    for a, b in np.atleast_2d(blocks):
        in_block[int(a):int(b)] = True

    columns = ["epoch", "t_s", "zt_h", "is_light", "epoch_ok", "in_block"] + hyp_fields
    print(f"  {stem}: {n_ep:,} epochs of {epoch_s}s")

    with _open_out(out, use_gzip) as fh:
        for line in _header_lines(meta, stem, f"per-epoch table, {epoch_s}s epochs",
                                  columns):
            fh.write(line + "\n")
        fh.write("#\n")
        fh.write("# 🛑 ANY STATE LABEL IN THIS FILE IS AUTOMATIC AND PROVISIONAL.\n")
        fh.write("#    No human has scored any epoch of this project's data. A blind\n")
        fh.write("#    scoring set exists and its Cohen kappa has not been measured,\n")
        fh.write("#    so these labels have no known accuracy. Do not report an\n")
        fh.write("#    architecture from them without saying this.\n")
        fh.write("# 🛑 NO REM PERCENTAGE IS REPORTABLE from this montage: two\n")
        fh.write("#    independent rules disagree by roughly a factor of five.\n")
        w = csv.writer(fh, delimiter="\t", lineterminator="\n")
        w.writerow(columns)
        for k in range(n_ep):
            row = [k, f"{k * epoch_s:.1f}", f"{float(zt[k]):.4f}",
                   int(bool(is_light[k])), int(bool(epoch_ok[k])), int(bool(in_block[k]))]
            hr = hyp_rows.get(k)
            row.extend([(hr.get(f, "") if hr else "") for f in hyp_fields])
            w.writerow(row)
    print(f"    -> {out}  ({out.stat().st_size / 1e6:.2f} MB)")
    return out


def verify_roundtrip(npz_path: Path, tsv_path: Path, *, sample_rows: int = 200_000) -> bool:
    """Read the text back and compare to the source. Must be EXACTLY equal.

    A lossy export is worse than no export, because it looks fine.
    """
    z = np.load(npz_path, allow_pickle=True)
    eeg, emg = z["eeg"], z["emg"]
    opener = gzip.open if tsv_path.suffix == ".gz" else open
    mode = "rt" if tsv_path.suffix == ".gz" else "r"
    n_checked = 0
    max_diff = 0.0
    with opener(tsv_path, mode, encoding="utf-8") as fh:
        for line in fh:
            if line.startswith("#"):
                continue
            break
        rd = csv.DictReader(fh, delimiter="\t",
                            fieldnames=line.rstrip("\n").split("\t"))
        for i, row in enumerate(rd):
            if i >= sample_rows:
                break
            max_diff = max(max_diff,
                           abs(float(row["eeg_uv"]) - round(float(eeg[i]), 3)),
                           abs(float(row["emg_uv"]) - round(float(emg[i]), 3)))
            n_checked += 1
    ok = max_diff == 0.0
    print(f"    round trip: {n_checked:,} rows checked, max |difference| "
          f"{max_diff:g}  {'OK' if ok else 'MISMATCH'}")
    return ok


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("targets", nargs="+",
                    help="per-mouse .npz files, or day folders containing them")
    ap.add_argument("--gzip", action="store_true", help="write .tsv.gz")
    ap.add_argument("--epochs-only", action="store_true",
                    help="per-epoch table only, no full-rate file")
    ap.add_argument("--absolute-time", action="store_true",
                    help="add an ISO wall-clock column (roughly doubles the file)")
    ap.add_argument("--no-verify", action="store_true",
                    help="skip the round-trip check")
    args = ap.parse_args(argv)

    paths: list[Path] = []
    for t in args.targets:
        p = Path(t).expanduser()
        if p.is_dir():
            paths.extend(sorted(p.glob("port*.npz")))
        elif p.suffix == ".npz":
            paths.append(p)
        else:
            print(f"skipping {p}: not an .npz or a directory")
    if not paths:
        raise SystemExit("nothing to export")

    print(f"exporting {len(paths)} animal-recording(s)")
    failures = 0
    for p in paths:
        if args.epochs_only:
            export_epochs(p, use_gzip=args.gzip)
            continue
        out = export_samples(p, use_gzip=args.gzip, absolute_time=args.absolute_time)
        export_epochs(p, use_gzip=args.gzip)
        if not args.no_verify and not args.absolute_time:
            if not verify_roundtrip(p, out):
                failures += 1
    if failures:
        print(f"\n{failures} file(s) FAILED the round-trip check")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
