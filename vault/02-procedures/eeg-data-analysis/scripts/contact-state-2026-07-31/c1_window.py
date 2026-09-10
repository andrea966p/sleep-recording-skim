import json, numpy as np
from scipy import signal as sg

D = '/home/skimlab/radix/data/'
F = 'allego_1__uid0731-18-06-37'
OUT = '/tmp/claude-1000/-home-skimlab-Monitoring-project/2e35e17d-b26f-4f59-9057-abb378e299b4/scratchpad/'
st = json.load(open(D + F + '.xdat.json'))['status']
fs = st['samp_freq']; NC = st['signals']['total']; N = st['num_smpl']

T0, T1 = 0, int(8.70 * 3600)          # C1 frontal connected window
FRONT, PAR = 128, 129                  # port C natives 0,1
mm = np.memmap(D + F + '_data.xdat', dtype='<f4', mode='r', shape=(N, NC))

EP = 10                                # epoch seconds
nep = (T1 - T0) // EP
delta = np.zeros(nep); theta = np.zeros(nep); sigma = np.zeros(nep)
tot = np.zeros(nep); rms = np.zeros(nep); clip = np.zeros(nep); mains = np.zeros(nep)

sos = sg.butter(4, [0.5, 45], btype='band', fs=fs, output='sos')
sosm = sg.butter(4, [55, 65], btype='band', fs=fs, output='sos')
CH = 600                               # seconds per read
s = T0
while s < T1:
    e = min(s + CH, T1)
    blk = np.asarray(mm[s * fs:e * fs, [FRONT, PAR]], dtype=np.float64)
    raw = blk[:, 0] - blk[:, 1]
    f = sg.sosfiltfilt(sos, raw)
    mn = sg.sosfiltfilt(sosm, raw)
    n = (e - s) // EP
    R = raw[:n * EP * fs].reshape(n, EP * fs)
    Ff = f[:n * EP * fs].reshape(n, EP * fs)
    Mm = mn[:n * EP * fs].reshape(n, EP * fs)
    i0 = (s - T0) // EP
    fr, P = sg.welch(Ff, fs, nperseg=1024, axis=1)
    bp = lambda lo, hi: np.trapz(P[:, (fr >= lo) & (fr < hi)], fr[(fr >= lo) & (fr < hi)], axis=1)
    delta[i0:i0 + n] = bp(0.5, 4); theta[i0:i0 + n] = bp(5, 9)
    sigma[i0:i0 + n] = bp(10, 15); tot[i0:i0 + n] = bp(0.5, 45)
    rms[i0:i0 + n] = Ff.std(1); mains[i0:i0 + n] = Mm.std(1)
    clip[i0:i0 + n] = (np.abs(R) > 6300).mean(1)
    s = e
    print(f'{100*(s-T0)/(T1-T0):.1f}%', flush=True)

np.savez_compressed(OUT + 'c1_window.npz', delta=delta, theta=theta, sigma=sigma,
                    tot=tot, rms=rms, clip=clip, mains=mains, ep=EP, t0=T0,
                    start_time=st['start_time'])
print('DONE', nep, 'epochs')
