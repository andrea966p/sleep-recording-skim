"""Recompute with ABSOLUTE delta power (uV^2), not the delta RATIO.

Four of five council advisors independently raised this: delta ratio is a ratio,
so broadband muscle or movement leaking into the EEG channel shrinks delta's
SHARE of power. That alone would produce r ~ -0.6 with no sleep involved.
Absolute delta power has no such denominator.
"""
import sys, numpy as np
sys.path.insert(0,'/home/skimlab/Monitoring_project/eeg-emg-analysis')
from core import criteria as C, qc_thresholds as T
BASE='/home/skimlab/radix/data/allego_1__uid0819-17-25-20'
spec=C.CohortSpec(roles=('eeg','emg'))
x,labels,fs,n=C.open_xdat(BASE)
ep=fs*10; nep=n//ep
want=sorted({s for r in spec.animal_sites().values() for s in r.values()}|set(spec.floor_sites()))
cols=np.array([labels.index(s) for s in want])
freqs=np.fft.rfftfreq(ep,1/fs)
band=(freqs>=1)&(freqs<=40); dband=(freqs>=1)&(freqs<=4)
win=np.hanning(ep); wg=np.sqrt((win**2).sum())
dabs=np.zeros((nep,len(cols))); drat=np.zeros_like(dabs); emgrms=np.zeros_like(dabs)
for k in range(nep):
    blk=np.asarray(x[k*ep:(k+1)*ep,cols],dtype=np.float64); blk-=blk.mean(0)
    emgrms[k]=blk.std(0)
    P=np.abs(np.fft.rfft(blk*win[:,None],axis=0))/wg; pw=P**2+1e-20
    dabs[k]=pw[dband].sum(0)          # ABSOLUTE delta power, uV^2
    drat[k]=pw[dband].sum(0)/pw[band].sum(0)
    if (k+1)%2000==0: print(f"  {k+1}/{nep}",flush=True)
np.savez_compressed('/tmp/claude-1000/-home-skimlab-Monitoring-project/4659f380-cff5-4540-b31f-cb4c24bcdd2d/scratchpad/absdelta.npz',
    dabs=dabs,drat=drat,rms=emgrms,sites=np.array(want),n_epochs=nep)
print("DONE",flush=True)
