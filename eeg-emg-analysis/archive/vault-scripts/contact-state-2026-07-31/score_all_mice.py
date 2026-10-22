"""
Rescore ALL 8 mice over a full recording with the CORRECTED channel map.

MAP (RHD2216 bipolar): native0 = /1 = EEG (already bipolar)
                       native1 = /2 = EMG (already bipolar)
                       natives 2,3 = /3,/4 = EMPTY PADS, ignore
Mouse B on the splitter sits at natives 32,33 = /33,/34.

Pass 1 (this script): one sweep over the file -> per-4s-epoch features for the
16 real channels. Pass 2 (gate_and_score_all.py): gating + scoring, cheap, offline.

Usage: python3 score_all_mice.py [recording_base]
"""
import sys
import json
import numpy as np
from scipy import signal as sg

D = '/home/skimlab/radix/data/'
F = sys.argv[1] if len(sys.argv) > 1 else 'allego_1__uid0731-18-06-37'
OUT = '/tmp/claude-1000/-home-skimlab-Monitoring-project/2e35e17d-b26f-4f59-9057-abb378e299b4/scratchpad/all_mice_epochs.npz'

st = json.load(open(D + F + '.xdat.json'))['status']
fs = st['samp_freq']; NC = st['signals']['total']; N = st['num_smpl']

mice, eeg_cols, emg_cols = [], [], []
for pi, p in enumerate('ABCD'):
    for mi, off in enumerate([0, 32]):
        mice.append(f'{p}{mi+1}')
        eeg_cols.append(pi*64 + off)        # /1 or /33  -> EEG
        emg_cols.append(pi*64 + off + 1)    # /2 or /34  -> EMG
cols = eeg_cols + emg_cols
NM = len(mice)

EP = 4
NPERSEG = 2048   # df=0.49Hz. DO NOT LOWER: at 512, theta 6-9Hz = 1 bin -> trapz = 0
RAIL = 6300
sos_eeg = sg.butter(4, [0.5, 30], btype='band', fs=fs, output='sos')
sos_emg = sg.butter(4, [10, 300], btype='band', fs=fs, output='sos')
sos_mn  = sg.butter(4, [55, 65],  btype='band', fs=fs, output='sos')

nep = (N // fs) // EP
Z = lambda: np.zeros((nep, NM), dtype=np.float32)
delta, theta, sigma, tot = Z(), Z(), Z(), Z()
eeg_rms, eeg_mains, eeg_clip = Z(), Z(), Z()
emg_rms, emg_mains = Z(), Z()

mm = np.memmap(D + F + '_data.xdat', dtype='<f4', mode='r', shape=(N, NC))
CH = 900                       # seconds per chunk
s = 0
while s < nep * EP:
    e = min(s + CH, nep * EP)
    blk = np.asarray(mm[s*fs:e*fs, :][:, cols], dtype=np.float64)
    E = sg.sosfiltfilt(sos_eeg, blk[:, :NM], axis=0)
    M = sg.sosfiltfilt(sos_emg, blk[:, NM:], axis=0)
    Xe = sg.sosfiltfilt(sos_mn, blk[:, :NM], axis=0)
    Xm = sg.sosfiltfilt(sos_mn, blk[:, NM:], axis=0)
    n = (e - s) // EP; i0 = s // EP
    r = lambda a: a[:n*EP*fs].reshape(n, EP*fs, NM)
    Ee, Mm_, Xee, Xmm = r(E), r(M), r(Xe), r(Xm)
    raw_e = blk[:n*EP*fs, :NM].reshape(n, EP*fs, NM)
    fr, P = sg.welch(Ee, fs, nperseg=NPERSEG, axis=1)
    bp = lambda lo, hi: np.trapz(P[:, (fr >= lo) & (fr < hi), :],
                                 fr[(fr >= lo) & (fr < hi)], axis=1)
    delta[i0:i0+n] = bp(0.5, 4); theta[i0:i0+n] = bp(6, 9)
    sigma[i0:i0+n] = bp(10, 15); tot[i0:i0+n] = bp(0.5, 30)
    eeg_rms[i0:i0+n] = Ee.std(1); emg_rms[i0:i0+n] = Mm_.std(1)
    eeg_mains[i0:i0+n] = Xee.std(1); emg_mains[i0:i0+n] = Xmm.std(1)
    eeg_clip[i0:i0+n] = (np.abs(raw_e) > RAIL).mean(1)
    s = e
    print(f'{100*s/(nep*EP):.1f}%', flush=True)

np.savez_compressed(OUT, mice=np.array(mice), ep=EP,
                    delta=delta, theta=theta, sigma=sigma, tot=tot,
                    eeg_rms=eeg_rms, eeg_mains=eeg_mains, eeg_clip=eeg_clip,
                    emg_rms=emg_rms, emg_mains=emg_mains,
                    start_time=st['start_time'], dur=st['dur'])
print('DONE', delta.shape)
