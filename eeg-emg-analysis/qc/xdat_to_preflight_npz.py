#!/usr/bin/env python3
"""Turn a short RECORDED .xdat into a pre-flight capture, wire-free inputs included.

qc/preflight_screen.py cannot check grounding from the live stream: get_signals() returns
only the SELECTED channels, so with the montage selected it reports NO FLOOR. Allego records
EVERY channel to the file, so a 1-5 min test recording (e.g. into ~/radix/noise-tests/, never
~/radix/data) already holds each chip's floor. This writes that file in preflight_grab.py's
format (signals ch x samples float32, sites = ntv_chan_name, ntv = native index, fs) so the
screen can grade grounding before a run without touching the channel selection:

    /usr/bin/python3 qc/xdat_to_preflight_npz.py BASE OUT.npz [t0_s] [dur_s]
    /usr/bin/python3 -m qc.preflight_screen --npz OUT.npz

Added 2026-10-02. Note what the floor can and cannot mean in the current rig geometry:
vault 10-projects/noise-hunt/2026-10-02-noise-series-method-audit.md (C1).
"""
import json, os, sys
import numpy as np

base, out = sys.argv[1], sys.argv[2]
t0 = float(sys.argv[3]) if len(sys.argv) > 3 else 0.0
dur = float(sys.argv[4]) if len(sys.argv) > 4 else None
meta = json.load(open(base + ".xdat.json"))
bm = meta["sapiens_base"]["biointerface_map"]; fs = float(meta["status"]["samp_freq"])
names, ntv = bm["ntv_chan_name"], bm["ntv_chan_idx"]
nch = len(names)
amp = [i for i, nm in enumerate(names) if str(nm).startswith("port_")]   # amplifier channels only
path = base + "_data.xdat"
nsamp = os.path.getsize(path) // (nch * 4)
a = int(t0 * fs); b = nsamp if dur is None else min(nsamp, a + int(dur * fs))
if b <= a:
    sys.exit(f"nothing to read: file has {nsamp / fs:.1f} s, asked for {t0:.0f} s onwards")
X = np.fromfile(path, dtype=np.float32, count=(b - a) * nch, offset=a * nch * 4).reshape(b - a, nch)
fd = os.open(path, os.O_RDONLY); os.posix_fadvise(fd, a * nch * 4, (b - a) * nch * 4, os.POSIX_FADV_DONTNEED)
order = sorted(amp, key=lambda i: int(ntv[i]))
np.savez_compressed(out, signals=np.ascontiguousarray(X[:, order].T, dtype=np.float32),
                    sites=np.array([str(names[i]) for i in order]),
                    ntv=np.array([int(ntv[i]) for i in order]), fs=fs)
print(f"{len(order)} amplifier channels x {(b - a) / fs:.1f} s from {os.path.basename(base)} -> {out}")
