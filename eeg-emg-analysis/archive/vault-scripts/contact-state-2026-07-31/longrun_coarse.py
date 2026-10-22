import json, numpy as np
from scipy import signal as sg

D = '/home/skimlab/radix/data/'
F = 'allego_1__uid0731-18-06-37'
OUT = '/tmp/claude-1000/-home-skimlab-Monitoring-project/2e35e17d-b26f-4f59-9057-abb378e299b4/scratchpad/'

meta = json.load(open(D + F + '.xdat.json'))
st = meta['status']
fs = st['samp_freq']; NC = st['signals']['total']; N = st['num_smpl']

legs, names = [], []
lbl = ['front', 'pariet', 'EMG+', 'EMG-']
for pi, p in enumerate('ABCD'):
    for mi, lo in enumerate([0, 32]):
        for k in range(4):
            legs.append(pi * 64 + lo + k); names.append(f'{p}{mi+1}/{lbl[k]}')
ctrl, cnames = [], []
for pi, p in enumerate('ABCD'):
    for lo in [20, 52]:
        for k in [0, 6]:
            ctrl.append(pi * 64 + lo + k); cnames.append(f'{p}/ctrl{lo+k+1}')
cols = legs + ctrl
allnames = names + cnames

sos_m = sg.butter(4, [55, 65], btype='band', fs=fs, output='sos')
sos_b = sg.butter(4, [0.5, 45], btype='band', fs=fs, output='sos')

WIN = 10        # seconds analysed
STRIDE = 60     # seconds between windows
mm = np.memmap(D + F + '_data.xdat', dtype='<f4', mode='r', shape=(N, NC))
starts = np.arange(0, N // fs - WIN, STRIDE)

mains = np.zeros((len(starts), len(cols)), dtype=np.float32)
bio = np.zeros((len(starts), len(cols)), dtype=np.float32)
clip = np.zeros((len(starts), len(cols)), dtype=np.float32)
sub_mains = np.zeros((len(starts), WIN, len(cols)), dtype=np.float32)  # per-second within window

for i, t in enumerate(starts):
    blk = np.asarray(mm[t * fs:(t + WIN) * fs, :], dtype=np.float64)[:, cols]
    m = sg.sosfiltfilt(sos_m, blk, axis=0)
    bb = sg.sosfiltfilt(sos_b, blk, axis=0)
    mains[i] = m.std(0); bio[i] = bb.std(0)
    clip[i] = (np.abs(blk) > 6300).mean(0)
    sub_mains[i] = m.reshape(WIN, fs, -1).std(1)
    if i % 100 == 0:
        print(f'{100*i/len(starts):.1f}%', flush=True)

np.savez_compressed(OUT + 'longrun_coarse.npz', mains=mains, bio=bio, clip=clip,
                    sub_mains=sub_mains, starts=starts, names=np.array(allnames),
                    nlegs=len(legs), fs=fs, win=WIN, stride=STRIDE,
                    start_time=st['start_time'], dur=st['dur'])
print('DONE', mains.shape)
