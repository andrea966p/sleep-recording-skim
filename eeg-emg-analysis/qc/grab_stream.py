"""Grab ~30 s of live stream from Allego and save as .npy + labels."""
import time, numpy as np, sys
from radiens_core import AllegoClient
from radiens_core.models.signals import SignalType

OUT = sys.argv[1]
SECS = float(sys.argv[2]) if len(sys.argv) > 2 else 30.0

c = AllegoClient(); c.get_status()
meta = c.get_channel_metadata()
amp = SignalType.AMP
counters = {}; sites = []
for name, port in zip(meta.ntv_chan_names[amp], meta.ports[amp]):
    if not name.startswith("port_"):
        continue
    p = port.name; counters[p] = counters.get(p, 0) + 1
    sites.append(f"{p}/{counters[p]}")

chunks = []; t0 = time.time(); tr_first = None; tr_last = None; t_seen = None
while time.time() - t0 < SECS:
    time.sleep(1.0)
    lo, hi = c.get_status().streaming.primary_cache_t_range
    lo = t_seen if t_seen is not None else hi - 1.0      # only what arrived since the last poll
    if hi <= lo:
        continue
    arr = c.get_signals(time_range=[lo, hi], signals="all")
    if arr.amp is None or arr.amp.size == 0:
        continue
    a = np.asarray(arr.amp)
    chunks.append(a)
    t_seen = arr.time_range.sec[1]
    if tr_first is None: tr_first = arr.time_range.sec
    tr_last = arr.time_range.sec

X = np.concatenate(chunks, axis=1)
print("shape", X.shape, "range", tr_first, "->", tr_last, "dtype", X.dtype)
np.save(OUT + ".npy", X.astype(np.float32))
with open(OUT + ".labels.txt", "w") as fh:
    fh.write("\n".join(sites) + "\n")
print("n_sites", len(sites), "saved", OUT)
