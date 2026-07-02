"""
xdat_to_csv.py  --  Export an XDAT recording's wired channels to CSV.

WARNING: at full 1 kHz a multi-hour recording is millions of rows (~1 GB) and
will NOT open in Excel/LibreOffice (>1,048,576 row limit). Either open it in
Python/pandas, or pass --target-fs to decimate (e.g. 256 Hz -> ~4x smaller and
Excel-openable for short recordings).

Usage:
    python xdat_to_csv.py <recording_base> [--config single_mouse]
                          [--target-fs 0]      # 0 = keep native rate (raw)
    (2mice32 config DEPRECATED 2026-07-01 -- one mouse per headstage; see xdat_io.py)
                          [--bipolar]          # also add bipolar derivations
"""
import argparse
import numpy as np
import pandas as pd
from scipy import signal
from xdat_io import load_xdat, CHANNEL_MAPS, BIPOLAR_DERIVATIONS, bipolar


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("base")
    ap.add_argument("--config", default="single_mouse")
    ap.add_argument("--target-fs", type=int, default=0)
    ap.add_argument("--bipolar", action="store_true")
    args = ap.parse_args()

    rec = load_xdat(args.base)
    fs = rec.fs
    chans = [(f"{lab}_n{ntv}", rec.data[ntv].astype(np.float64))
             for ntv, lab in CHANNEL_MAPS[args.config].items()]
    if args.bipolar:
        for lab, p, m in BIPOLAR_DERIVATIONS[args.config]:
            chans.append((lab, bipolar(rec.data, p, m)))

    out_fs = fs
    if args.target_fs and args.target_fs != fs:
        g = np.gcd(args.target_fs, fs)
        up, down = args.target_fs // g, fs // g
        chans = [(n, signal.resample_poly(x, up, down)) for n, x in chans]
        out_fs = args.target_fs

    n = len(chans[0][1])
    df = pd.DataFrame({"time_s": np.arange(n) / out_fs})
    for name, x in chans:
        df[name] = x
    suffix = f"_{out_fs}hz" if out_fs != fs else "_raw"
    out = f"{rec.base}{suffix}.csv"
    df.to_csv(out, index=False, float_format="%.2f")
    import os
    print(f"wrote {out}  rows={n}  cols={list(df.columns)}  "
          f"size={os.path.getsize(out)/1e9:.3f} GB  fs={out_fs}")
    if n > 1_048_576:
        print("NOTE: too many rows for Excel/LibreOffice -> open in pandas, "
              "or re-run with --target-fs 256")


if __name__ == "__main__":
    main()
