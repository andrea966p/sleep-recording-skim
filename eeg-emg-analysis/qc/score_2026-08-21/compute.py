#!/usr/bin/env python3
"""One feature pass over the 39.7 h run, cached to npz.

Separate from the scoring so the 140 GB read happens exactly once and every
later question is answered from the cache.
"""
import sys, time
import numpy as np
sys.path.insert(0, '/home/skimlab/Monitoring_project/eeg-emg-analysis')
from core import criteria as C

BASE = '/home/skimlab/radix/data/allego_1__uid0819-17-25-20'
OUT  = '/home/skimlab/Monitoring_project/eeg-emg-analysis/qc/score_2026-08-21/features.npz'

t0 = time.time()
spec = C.CohortSpec(roles=('eeg', 'emg'))
f = C.compute_features(BASE, spec, progress=lambda s: print(s, flush=True))
np.savez_compressed(
    OUT, hum=f.hum, rms=f.rms, rail=f.rail, slope=f.slope,
    delta=f.delta, lfhf=f.lfhf, slope_lo=f.slope_lo, slope_hi=f.slope_hi,
    sites=np.array(f.sites), fs=f.fs, epoch_s=f.epoch_s, n_epochs=f.n_epochs)
print(f"DONE {f.n_epochs} epochs, {len(f.sites)} sites, {time.time()-t0:.0f}s -> {OUT}", flush=True)
