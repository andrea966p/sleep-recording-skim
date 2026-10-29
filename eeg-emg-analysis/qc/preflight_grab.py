#!/usr/bin/env python3
"""Capture a stretch of Allego's live stream for the pre-flight screen.

This half exists only because of an interpreter split. `radiens-core` is installed
in /opt/neurosurveillance/venv, whose scipy is broken (it picks up the system
scipy built against numpy 1.x and dies with "numpy.core.multiarray failed to
import"). The measurement half therefore runs under /usr/bin/python3, which has
a working scipy but no radiens-core. This script grabs, that one measures.

    /opt/neurosurveillance/venv/bin/python3 preflight_grab.py <out.npz> [secs]

Writes the SELECTED channels only, with their site labels, in stream order.
"""
import sys
import time

import numpy as np

from radiens_core import AllegoClient
from radiens_core.models.signals import SignalType
from radiens_core.models.status import StreamMode

OUT = sys.argv[1]
SECS = float(sys.argv[2]) if len(sys.argv) > 2 else 300.0

client = AllegoClient()
status = client.get_status()
if status.streaming.stream_mode != StreamMode.ON:
    sys.exit("streaming is off - start it in Allego before running the screen")
fs = client.get_core_config().base_samp_freq

# get_signals() returns only the SELECTED channels, in dyn_sort order. Label them
# from the same channel metadata rather than assuming a montage: recordings exist at 32 and
# 64 channels per port and at mixed layouts, and a wrong assumption here mis-maps
# every channel silently.
meta = client.get_channel_metadata()
amp = SignalType.AMP
selected = set(meta.selected_sig_map[amp].ntv)
chosen = sorted((ntv, name) for ntv, name in zip(meta.sig_map[amp].ntv, meta.ntv_chan_names[amp])
                if ntv in selected)
ntv = [n for n, _ in chosen]
sites = [name for _, name in chosen]

chunks, seen_until, got = [], None, 0
t0 = time.time()
while time.time() - t0 < SECS:
    time.sleep(1.0)
    lo, hi = client.get_status().streaming.primary_cache_t_range
    lo = seen_until if seen_until is not None else hi - 1.0   # only what arrived since the last poll
    if hi <= lo:
        continue
    arr = client.get_signals(time_range=[lo, hi], signals={"amp": "selected"})
    sig = arr.amp
    if sig is None or np.size(sig) == 0:
        continue
    tr = arr.time_range.sec
    # Consecutive polls overlap when the cache has not advanced a full chunk;
    # concatenating blindly duplicates samples and flatters every stability
    # number computed downstream.
    if seen_until is not None and tr[0] < seen_until:
        keep = int(round((seen_until - tr[0]) * fs))
        if keep >= sig.shape[1]:
            continue
        sig = sig[:, keep:]
    chunks.append(np.asarray(sig, dtype=np.float32))
    seen_until = tr[1]
    got += chunks[-1].shape[1]
    print("  %5.1f s" % (got / fs), end="\r", flush=True)

if not chunks:
    sys.exit("no samples arrived - check that the stream is actually running")

X = np.concatenate(chunks, axis=1)
if X.shape[0] != len(sites):
    sys.exit("stream returned %d rows but %d channels are selected - refusing to "
             "guess the mapping" % (X.shape[0], len(sites)))

np.savez_compressed(OUT, signals=X, sites=np.array(sites), ntv=np.array(ntv), fs=fs)
print(" " * 30, end="\r")
print("captured %d channels x %.1f s -> %s" % (X.shape[0], X.shape[1] / fs, OUT))
