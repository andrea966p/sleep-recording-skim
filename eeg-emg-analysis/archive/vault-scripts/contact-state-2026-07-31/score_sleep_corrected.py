"""
Sleep scoring with the CORRECTED channel map (2026-08-01).

THE MAP (RHD2216 is BIPOLAR — each channel already reports its own +/- difference):
    native 0  = Allego /1  = EEG  (frontal vs parietal)   <- use directly, do NOT subtract
    native 1  = Allego /2  = EMG  (neck pair)             <- use directly, do NOT subtract
    native 2,3= Allego /3,/4 = EMPTY PADS, no wire        <- ignore
    (mouse B on the splitter: natives 32,33 = /33,/34)

The old pipeline computed EEG = native0 - native1, which is EEG minus EMG, and
treated the empty pads /3,/4 as failed EMG electrodes. See
05-experiments/completed/2026-08-01-channel-mapping-correction-first-sleep.md

Usage:  python3 score_sleep_corrected.py <recording_base> <port_index> <mouse:1|2> <start_h> <end_h>
   e.g. python3 score_sleep_corrected.py allego_1__uid0731-18-06-37 2 1 0 8.70   # C1
"""
import sys
import json
import numpy as np
from scipy import signal as sg

D = '/home/skimlab/radix/data/'
F = sys.argv[1] if len(sys.argv) > 1 else 'allego_1__uid0731-18-06-37'
PORT = int(sys.argv[2]) if len(sys.argv) > 2 else 2       # A=0 B=1 C=2 D=3
MOUSE = int(sys.argv[3]) if len(sys.argv) > 3 else 1      # 1 or 2 (splitter half)
T0_H = float(sys.argv[4]) if len(sys.argv) > 4 else 0.0
T1_H = float(sys.argv[5]) if len(sys.argv) > 5 else 8.70

st = json.load(open(D + F + '.xdat.json'))['status']
fs = st['samp_freq']; NC = st['signals']['total']; N = st['num_smpl']
EEG_CH = PORT * 64 + (0 if MOUSE == 1 else 32)
EMG_CH = EEG_CH + 1
print(f'EEG = col {EEG_CH} ({"ABCD"[PORT]}/{1 if MOUSE==1 else 33}) | '
      f'EMG = col {EMG_CH} ({"ABCD"[PORT]}/{2 if MOUSE==1 else 34})')

# --- SOP parameters (04-processing-guidelines) ------------------------------
EP = 4                       # 4 s epochs
NPERSEG = 2048               # df = 0.49 Hz.
# !! DO NOT LOWER NPERSEG. At nperseg=512 (df=1.95 Hz) the theta band 6-9 Hz
# !! contains ONE FFT bin and np.trapz over a single point returns EXACTLY ZERO.
# !! That bug silently zeroed every theta value on 2026-08-01.
sos_eeg = sg.butter(4, [0.5, 30], btype='band', fs=fs, output='sos')
sos_emg = sg.butter(4, [10, 300], btype='band', fs=fs, output='sos')
RAIL = 6300                  # +/-6390 uV amplifier rail

T0, T1 = int(T0_H * 3600), int(T1_H * 3600)
nep = (T1 - T0) // EP
delta = np.zeros(nep); theta = np.zeros(nep); sigma = np.zeros(nep)
tot = np.zeros(nep); emg = np.zeros(nep); clip = np.zeros(nep); eeg_rms = np.zeros(nep)

mm = np.memmap(D + F + '_data.xdat', dtype='<f4', mode='r', shape=(N, NC))
s = T0
while s < T1:
    e = min(s + 600, T1)
    b = np.asarray(mm[s*fs:e*fs, [EEG_CH, EMG_CH]], dtype=np.float64)
    E = sg.sosfiltfilt(sos_eeg, b[:, 0])
    M = sg.sosfiltfilt(sos_emg, b[:, 1])
    n = (e - s) // EP; i0 = (s - T0) // EP
    Ee = E[:n*EP*fs].reshape(n, EP*fs)
    Mm = M[:n*EP*fs].reshape(n, EP*fs)
    R = b[:n*EP*fs, 0].reshape(n, EP*fs)
    fr, P = sg.welch(Ee, fs, nperseg=NPERSEG, axis=1)
    bp = lambda lo, hi: np.trapz(P[:, (fr >= lo) & (fr < hi)], fr[(fr >= lo) & (fr < hi)], axis=1)
    delta[i0:i0+n] = bp(0.5, 4)      # NREM marker
    theta[i0:i0+n] = bp(6, 9)        # REM marker (SOP band)
    sigma[i0:i0+n] = bp(10, 15)      # spindles
    tot[i0:i0+n] = bp(0.5, 30)
    emg[i0:i0+n] = Mm.std(1)
    eeg_rms[i0:i0+n] = Ee.std(1)
    clip[i0:i0+n] = (np.abs(R) > RAIL).mean(1)
    s = e

# --- GATE: clipped or degenerate epochs excluded BEFORE any statistic -------
ok = (clip < 0.001) & (delta > 0) & (theta > 0) & (emg > 0)
print(f'epochs {nep} ({nep*EP/3600:.2f} h)  usable {ok.sum()} = {100*ok.mean():.1f}%')
if ok.sum() < 60:
    sys.exit('UNSCOREABLE: too few clean epochs')

le = np.log10(emg[ok]); td = np.log10(theta[ok] / delta[ok])

# --- thresholds -------------------------------------------------------------
# EMG_THR: read off the DIP in the bimodal log10(EMG) histogram. Print the
# histogram and re-read it per animal; do not blindly reuse this number.
EMG_THR = 1.40                       # 10^1.40 = 25 uV, C1 2026-08-01
TD_THR = np.percentile(td, 80)       # provisional; REM% is sensitive to this
wake = le >= EMG_THR
nrem = (~wake) & (td < TD_THR)
rem = (~wake) & (td >= TD_THR)

print(f'\nEMG threshold {10**EMG_THR:.0f} uV | theta/delta threshold {10**TD_THR:.2f}')
print(f'WAKE {100*wake.mean():5.1f}%  NREM {100*nrem.mean():5.1f}%  REM {100*rem.mean():5.1f}%')

print('\nlog10(EMG) histogram — CONFIRM IT IS BIMODAL and that EMG_THR sits in the dip:')
h, ed = np.histogram(le, bins=24)
for i in range(24):
    mark = '  <-- EMG_THR' if ed[i] <= EMG_THR < ed[i+1] else ''
    print(f'  {ed[i]:6.2f}..{ed[i+1]:6.2f} {"#"*int(50*h[i]/h.max())} {h[i]}{mark}')

# --- physiology check: the states must differ in the CORRECT directions -----
print('\nPHYSIOLOGY CHECK (median per state) — NREM must have the most delta and the')
print('biggest amplitude; REM the highest theta/delta and the lowest EMG; WAKE the highest EMG.')
dp = 100 * delta[ok] / tot[ok]; sp = 100 * sigma[ok] / tot[ok]
print(f'{"state":6s} {"EMG uV":>8s} {"EEGrms":>8s} {"delta%":>8s} {"sigma%":>8s} {"th/de":>7s}')
for nm, m in [('WAKE', wake), ('NREM', nrem), ('REM', rem)]:
    if m.sum() == 0:
        continue
    print(f'{nm:6s} {np.median(emg[ok][m]):8.1f} {np.median(eeg_rms[ok][m]):8.1f} '
          f'{np.median(dp[m]):8.1f} {np.median(sp[m]):8.1f} '
          f'{np.median((theta[ok]/delta[ok])[m]):7.2f}')

# --- bouts + persistence ----------------------------------------------------
def bouts(mask, label):
    runs, cur, L = [], mask[0], 1
    for v in mask[1:]:
        if v == cur:
            L += 1
        else:
            runs.append((cur, L)); cur, L = v, 1
    runs.append((cur, L))
    r = [L for v, L in runs if v]
    if r:
        print(f'  {label:5s} n={len(r):4d}  median {np.median(r)*EP:5.0f}s  '
              f'mean {np.mean(r)*EP:6.1f}s  max {max(r)*EP:5.0f}s')

print(f'\nBOUT STRUCTURE (random expectation = {2*EP}s):')
bouts(wake, 'WAKE'); bouts(nrem, 'NREM'); bouts(rem, 'REM')

x = (~wake).astype(float); x -= x.mean()
ac = np.correlate(x, x, 'full')[len(x)-1:]; ac /= ac[0]
print('\nSLEEP/WAKE PERSISTENCE (autocorr of sleep indicator):')
for k in [1, 15, 75, 150, 450, 900]:
    if k < len(ac):
        print(f'   lag {k*EP:5d}s ({k*EP/60:5.1f} min): r = {ac[k]:+.3f}')
rng = np.random.default_rng(0); xs = rng.permutation(x)
acs = np.correlate(xs, xs, 'full')[len(xs)-1:]; acs /= acs[0]
print(f'   SHUFFLE CONTROL lag {EP}s: r = {acs[1]:+.3f}')

print('\nHOURLY:')
h = np.arange(ok.sum()) * EP / 3600
print(f'{"hr":>3s} {"WAKE%":>6s} {"NREM%":>6s} {"REM%":>6s}')
for k in range(int(np.ceil(h[-1]))):
    m = (h >= k) & (h < k+1)
    if m.sum() < 50:
        continue
    print(f'{k:3d} {100*wake[m].mean():6.1f} {100*nrem[m].mean():6.1f} {100*rem[m].mean():6.1f}')
