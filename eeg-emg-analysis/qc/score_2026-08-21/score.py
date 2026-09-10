#!/usr/bin/env python3
"""Score allego_1__uid0819-17-25-20 (39.674 h, 8 positions).

Position labels are RIG POSITIONS. No animal identity is asserted anywhere here
and no prior verdict is carried in: this scores the file on its own evidence.

FLOOR: PER-CHIP, not pooled. The eight chips' wire-free inputs differ by more
than a full decade of slope in this file, so one pooled threshold is simultaneously
too harsh for seven of them and too lenient for one.

CRITERION: EEG by slope, EMG by hum. The slope test is a category error on EMG,
which is broadband and therefore flat; criteria.usable() refuses it outright.
"""
import sys, json
import numpy as np
sys.path.insert(0, '/home/skimlab/Monitoring_project/eeg-emg-analysis')
from core import criteria as C
from core import qc_thresholds as T

CACHE = '/home/skimlab/Monitoring_project/eeg-emg-analysis/qc/score_2026-08-21/features.npz'
BASE  = 'allego_1__uid0819-17-25-20'

d = np.load(CACHE, allow_pickle=True)
spec = C.CohortSpec(roles=('eeg', 'emg'))
feat = C.EpochFeatures(
    base=BASE, fs=int(d['fs']), epoch_s=int(d['epoch_s']), n_epochs=int(d['n_epochs']),
    n_samples=int(d['n_epochs'])*int(d['fs'])*int(d['epoch_s']),
    sites=[str(s) for s in d['sites']], spec=spec,
    hum=d['hum'], rms=d['rms'], rail=d['rail'], slope=d['slope'],
    delta=d['delta'], lfhf=d['lfhf'], slope_lo=d['slope_lo'], slope_hi=d['slope_hi'])

EP_MIN = feat.epoch_s / 60.0
GATE_MIN = 15.0
GATE_EP = int(np.ceil(GATE_MIN / EP_MIN))

def chip_floor(port, slot):
    """FloorStats from ONE chip's own wire-free inputs."""
    base = 1 if slot == 1 else 33
    ss = [f"{port}/{i}" for i in range(base+len(spec.roles), base+C.CHIP_REAL_CHANNELS)]
    cols = np.array([feat.col(s) for s in ss])
    fh = feat.hum[:, cols].ravel(); fs_ = feat.slope[:, cols].ravel()
    p = T.FLOOR_PERCENTILE
    return C.FloorStats(
        n_sites=len(cols), n_epochs=feat.n_epochs, n_samples=int(fh.size),
        hum_p1=float(np.percentile(fh,p)), hum_p5=float(np.percentile(fh,5)),
        hum_median=float(np.median(fh)),
        slope_p1=float(np.percentile(fs_,p)), slope_p5=float(np.percentile(fs_,5)),
        slope_median=float(np.median(fs_)), slope_min=float(fs_.min()))

pooled = C.floor_stats(feat)
rows = []
for port in 'ABCD':
    for slot in (1, 2):
        pos = f"{port}{slot}"
        fl = chip_floor(port, slot)
        r = {'position': pos, 'chip_slope_p1': round(fl.slope_p1,3),
             'chip_hum_p1': round(fl.hum_p1,1)}
        masks = {}
        for role, crit in (('eeg','slope'), ('emg','hum')):
            site = spec.site_of(pos, role)
            try:
                m = C.usable(feat, site, fl, crit, role=role)
                refused = None
            except C.CriterionRefused as e:
                m = np.zeros(feat.n_epochs, dtype=bool); refused = str(e)[:120]
            masks[role] = m
            c = feat.col(site)
            r[f'{role}_site']      = site
            r[f'{role}_frac']      = round(100*m.mean(), 1)
            r[f'{role}_block_min'] = round(C.longest_run(m)*EP_MIN, 1)
            r[f'{role}_med_rms']   = round(float(np.median(feat.rms[:,c])), 1)
            r[f'{role}_med_hum']   = round(float(np.median(feat.hum[:,c])), 1)
            r[f'{role}_med_slope'] = round(float(np.median(feat.slope[:,c])), 3)
            r[f'{role}_rail_frac'] = round(100*float((feat.rail[:,c]>0).mean()), 1)
            if refused: r[f'{role}_refused'] = refused
        both = masks['eeg'] & masks['emg']
        r['both_frac']      = round(100*both.mean(), 1)
        r['both_block_min'] = round(C.longest_run(both)*EP_MIN, 1)
        r['rung2_eeg_only'] = 'PASS' if C.longest_run(masks['eeg']) >= GATE_EP else 'FAIL'
        r['rung2_strict']   = 'PASS' if C.longest_run(both)        >= GATE_EP else 'FAIL'
        rows.append(r)

out = {'base': BASE, 'duration_h': round(feat.n_epochs*feat.epoch_s/3600,3),
       'n_epochs': feat.n_epochs, 'epoch_s': feat.epoch_s,
       'gate_min': GATE_MIN, 'floor_mode': 'per-chip',
       'pooled_slope_p1': round(pooled.slope_p1,3),
       'thresholds_hash': C.thresholds_hash(), 'positions': rows}
p='/home/skimlab/Monitoring_project/eeg-emg-analysis/qc/score_2026-08-21/scores.json'
json.dump(out, open(p,'w'), indent=2)

print(f"{BASE}  {out['duration_h']} h  {feat.n_epochs} epochs @ {feat.epoch_s}s")
print(f"pooled slope_p1 = {pooled.slope_p1:.3f}  (NOT used; per-chip floors used instead)\n")
h=f"{'pos':4} {'chip_p1':>8} | {'EEG%':>6} {'blk_min':>8} {'medRMS':>8} {'slope':>7} {'rail%':>6} | {'EMG%':>6} {'blk_min':>8} {'medRMS':>8} | {'both%':>6} {'blk':>7} {'STRICT':>7}"
print(h); print('-'*len(h))
for r in rows:
    print(f"{r['position']:4} {r['chip_slope_p1']:8.3f} | "
          f"{r['eeg_frac']:6.1f} {r['eeg_block_min']:8.1f} {r['eeg_med_rms']:8.1f} {r['eeg_med_slope']:7.2f} {r['eeg_rail_frac']:6.1f} | "
          f"{r['emg_frac']:6.1f} {r['emg_block_min']:8.1f} {r['emg_med_rms']:8.1f} | "
          f"{r['both_frac']:6.1f} {r['both_block_min']:7.1f} {r['rung2_strict']:>7}")
print(f"\nwrote {p}")
