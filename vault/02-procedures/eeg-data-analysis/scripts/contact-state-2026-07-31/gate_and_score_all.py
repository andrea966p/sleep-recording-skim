"""
Pass 2: gate scoreable epochs and score sleep for all 8 mice.
Reads all_mice_epochs.npz from score_all_mice.py.

THE THREE-PART GATE (2026-08-01 lesson: hum alone is NOT enough).
An epoch is scoreable only if ALL hold:
  1. NOT OPEN      - eeg_mains < 300 uV and emg_mains < 300 uV
  2. NOT SHORTED   - eeg_rms >= 25 uV   (a shorted channel sits at 16-21 uV,
                     scores ~100% WAKE, and has ZERO persistence)
  3. NOT CLIPPED   - eeg_clip < 0.001   (the 2026-07-15 lesson)
Then, per mouse, structure is VERIFIED before any state percentage is reported:
persistence at 1 min must be well above a shuffle control, otherwise the mouse
is reported as NO STRUCTURE rather than given a hypnogram.
"""
import sys
import numpy as np

NPZ = sys.argv[1] if len(sys.argv) > 1 else \
    '/tmp/claude-1000/-home-skimlab-Monitoring-project/2e35e17d-b26f-4f59-9057-abb378e299b4/scratchpad/all_mice_epochs.npz'
d = np.load(NPZ, allow_pickle=True)
mice = [str(x) for x in d['mice']]; EP = int(d['ep'])
delta, theta, sigma, tot = d['delta'], d['theta'], d['sigma'], d['tot']
eeg_rms, eeg_mains, eeg_clip = d['eeg_rms'], d['eeg_mains'], d['eeg_clip']
emg_rms, emg_mains = d['emg_rms'], d['emg_mains']

OPEN_UV, SHORT_UV, CLIP_F = 300.0, 25.0, 0.001
start = str(d['start_time'])

def clock(t_h, base=18 + 6/60):
    tot_h = base + t_h
    return f'{int(tot_h % 24):02d}:{int((tot_h % 1)*60):02d}' + ('+1d' if tot_h >= 24 else '')

print(f'recording start {start} (18:06 KST)   epochs {delta.shape[0]} x {EP}s = '
      f'{delta.shape[0]*EP/3600:.1f} h   mice {len(mice)}')
print(f'GATE: mains<{OPEN_UV:.0f}uV (not open) AND eeg_rms>={SHORT_UV:.0f}uV (not shorted) '
      f'AND clip<{CLIP_F} (not railed)\n')

hdr = f'{"mouse":6s} {"scoreable":>10s} {"WAKE%":>6s} {"NREM%":>6s} {"REM%":>6s} {"r@1min":>7s} {"shuf":>6s}  verdict'
print(hdr); print('-'*len(hdr))
results = {}
for i, m in enumerate(mice):
    ok = ((eeg_mains[:, i] < OPEN_UV) & (emg_mains[:, i] < OPEN_UV) &
          (eeg_rms[:, i] >= SHORT_UV) & (eeg_clip[:, i] < CLIP_F) &
          (delta[:, i] > 0) & (theta[:, i] > 0) & (emg_rms[:, i] > 0))
    hrs = ok.sum() * EP / 3600
    if ok.sum() < 225:      # <15 min of scoreable data
        print(f'{m:6s} {hrs:9.2f}h {"":>6s} {"":>6s} {"":>6s} {"":>7s} {"":>6s}  INSUFFICIENT')
        results[m] = None
        continue
    le = np.log10(emg_rms[ok, i]); td = np.log10(theta[ok, i] / delta[ok, i])
    # EMG threshold: midpoint between the two modes, found by minimising
    # within-class variance (Otsu) on the log-EMG histogram
    hist, edges = np.histogram(le, bins=48)
    cen = (edges[:-1] + edges[1:]) / 2; w = hist.astype(float)
    best, thr = -1, np.median(le)
    for k in range(4, 44):
        w0, w1 = w[:k].sum(), w[k:].sum()
        if w0 < 20 or w1 < 20:
            continue
        m0 = (w[:k]*cen[:k]).sum()/w0; m1 = (w[k:]*cen[k:]).sum()/w1
        v = w0*w1*(m0-m1)**2
        if v > best:
            best, thr = v, cen[k]
    wake = le >= thr
    td_thr = np.percentile(td, 80)
    nrem = (~wake) & (td < td_thr); rem = (~wake) & (td >= td_thr)
    x = (~wake).astype(float); x -= x.mean()
    ac = np.correlate(x, x, 'full')[len(x)-1:]; ac /= ac[0]
    lag1m = ac[15] if len(ac) > 15 else np.nan
    rng = np.random.default_rng(0); xs = rng.permutation(x)
    acs = np.correlate(xs, xs, 'full')[len(xs)-1:]; acs /= acs[0]
    verdict = 'SCOREABLE' if lag1m > 0.3 else 'NO STRUCTURE - do not report states'
    print(f'{m:6s} {hrs:9.2f}h {100*wake.mean():6.1f} {100*nrem.mean():6.1f} '
          f'{100*rem.mean():6.1f} {lag1m:+7.3f} {acs[1]:+6.3f}  {verdict}')
    results[m] = dict(ok=ok, wake=wake, nrem=nrem, rem=rem, thr=thr,
                      hrs=hrs, lag1m=lag1m, i=i, verdict=verdict)

print('\nPHYSIOLOGY CHECK — WAKE must have the highest EMG; NREM the most delta and')
print('biggest amplitude; REM the highest theta/delta and the lowest EMG.')
print(f'{"mouse":6s} {"state":5s} {"EMG":>7s} {"EEGrms":>7s} {"delta%":>7s} {"th/de":>6s}   {"ok?":>4s}')
for m, R in results.items():
    if not R or R['lag1m'] <= 0.3:
        continue
    i, ok = R['i'], R['ok']
    dp = 100*delta[ok, i]/tot[ok, i]; ratio = theta[ok, i]/delta[ok, i]
    vals = {}
    for nm, msk in [('WAKE', R['wake']), ('NREM', R['nrem']), ('REM', R['rem'])]:
        if msk.sum() < 5:
            continue
        vals[nm] = (np.median(emg_rms[ok, i][msk]), np.median(eeg_rms[ok, i][msk]),
                    np.median(dp[msk]), np.median(ratio[msk]))
    good = ('WAKE' in vals and 'NREM' in vals and
            vals['WAKE'][0] > vals['NREM'][0] and vals['NREM'][2] > vals['WAKE'][2] and
            vals['NREM'][1] > vals['WAKE'][1])
    if 'REM' in vals:
        good = good and vals['REM'][3] > vals['NREM'][3] and vals['REM'][0] < vals['WAKE'][0]
    for nm, v in vals.items():
        print(f'{m if nm=="WAKE" else "":6s} {nm:5s} {v[0]:7.1f} {v[1]:7.1f} {v[2]:7.1f} {v[3]:6.2f}'
              + (f'   {"PASS" if good else "FAIL":>4s}' if nm == 'WAKE' else ''))

print('\nSCOREABLE WINDOWS (clock time, start 18:06 KST):')
for m, R in results.items():
    if not R:
        continue
    ok = R['ok']; h = np.arange(len(ok))*EP/3600
    segs, cur, s0 = [], ok[0], 0
    for j in range(1, len(ok)):
        if ok[j] != cur:
            segs.append((cur, h[s0], h[j])); cur, s0 = ok[j], j
    segs.append((cur, h[s0], h[-1]))
    good = [(a, z) for c, a, z in segs if c and (z-a) > 0.25]
    if good:
        print(f'  {m:4s} ' + ' '.join(f'[{clock(a)}-{clock(z)}]' for a, z in good[:6]))
