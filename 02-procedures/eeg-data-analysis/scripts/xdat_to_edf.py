"""
xdat_to_edf.py  --  Convert an XDAT recording to EDF+ (the portable format
most EEG viewers / sleep tools import).

Writes the wired raw channels + the bipolar derivations. Values stay in uV;
int16 EDF scaling is set per channel with an integer symmetric physical range
(avoids EDF's 8-char header truncation and any min>=max edge case).

Open the result in EDFbrowser (use the 2.14+ build; the apt 2.06 build crashes
on launch on Ubuntu 24.04 -- see 05-quality-control.md / journal 2026-06-30).

Usage:
    python xdat_to_edf.py <recording_base> [--config single_mouse|2mice32]
"""
import argparse
import datetime
import os
import numpy as np
import pyedflib
from xdat_io import load_xdat, CHANNEL_MAPS, BIPOLAR_DERIVATIONS, bipolar


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("base")
    ap.add_argument("--config", default="single_mouse")
    args = ap.parse_args()

    rec = load_xdat(args.base)
    chans = [(f"{lab}_n{ntv}", rec.data[ntv].astype(np.float64))
             for ntv, lab in CHANNEL_MAPS[args.config].items()]
    for lab, p, m in BIPOLAR_DERIVATIONS[args.config]:
        chans.append((lab, bipolar(rec.data, p, m)))

    start = (datetime.datetime.fromisoformat(rec.start_time.replace("Z", "+00:00"))
             .replace(tzinfo=None)) if rec.start_time else datetime.datetime(2000, 1, 1)

    out = rec.base + ".edf"
    w = pyedflib.EdfWriter(out, len(chans), file_type=pyedflib.FILETYPE_EDFPLUS)
    w.setStartdatetime(start)
    headers = []
    for name, x in chans:
        pr = int(np.ceil(max(abs(x.min()), abs(x.max())) / 100.0) * 100) + 100
        headers.append(dict(label=name[:16], dimension="uV", sample_frequency=rec.fs,
                            physical_min=-pr, physical_max=pr,
                            digital_min=-32767, digital_max=32767,
                            transducer="", prefilter=""))
    w.setSignalHeaders(headers)
    w.writeSamples([x for _, x in chans])
    w.close()
    print(f"wrote {out}  {len(chans)} signals @ {rec.fs} Hz  "
          f"size={os.path.getsize(out)/1e9:.3f} GB")
    print("channels:", [n for n, _ in chans])


if __name__ == "__main__":
    main()
