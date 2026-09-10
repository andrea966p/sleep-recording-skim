"""Grab ~30 s of live stream from Allego and save as .npy + labels."""
import time, numpy as np, sys
from radiens.allego_client import AllegoClient

OUT = sys.argv[1]
SECS = float(sys.argv[2]) if len(sys.argv) > 2 else 30.0

c = AllegoClient(); c.get_status()
t = c.get_channel_metadata().table
amp = t[t["ntv_chan_name"].astype(str).str.startswith("port_")]
counters = {}; sites = []
for _, r in amp.iterrows():
    p = str(r["port"]); counters[p] = counters.get(p, 0) + 1
    sites.append(f"{p}/{counters[p]}")

c.set_time_to_cache_head()
chunks = []; t0 = time.time(); tr_first = None; tr_last = None
while time.time() - t0 < SECS:
    time.sleep(1.0)
    sig, tr = c.get_signals()
    if sig is None or np.size(sig) == 0:
        continue
    a = np.asarray(sig)
    chunks.append(a)
    if tr_first is None: tr_first = tr
    tr_last = tr

X = np.concatenate(chunks, axis=1)
print("shape", X.shape, "range", tr_first, "->", tr_last, "dtype", X.dtype)
np.save(OUT + ".npy", X.astype(np.float32))
with open(OUT + ".labels.txt", "w") as fh:
    fh.write("\n".join(sites) + "\n")
print("n_sites", len(sites), "saved", OUT)
