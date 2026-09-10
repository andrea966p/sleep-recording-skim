"""Same textbook filter chain applied to animals AND to wire-free floor controls.

Discriminators that survive filtering:
  post rms            - amplitude after notch + band-pass
  spectral slope      - real EEG is ~1/f (negative slope); filtered noise is flat
  delta fraction      - 0.5-4 Hz share of 0.5-30 Hz power
"""
import json,os,numpy as np
from scipy.signal import iirnotch, butter, filtfilt, welch
from core import paths as PATHS
BASE=str(PATHS.RAW_ROOT) + "/allego_0__uid0806-12-45-02"
d=json.load(open(BASE+".xdat.json")); bm=d['sapiens_base']['biointerface_map']
lab=[f"{p}/{s}" for p,s in zip(bm['port'],bm['site_num'])]; n=len(lab); fs=1000
nsamp=os.path.getsize(BASE+"_data.xdat")//(n*4)
x=np.memmap(BASE+"_data.xdat",dtype=np.float32,mode="r",shape=(nsamp,n))
T=600*fs; start=nsamp//2-T//2; RAIL=6389.6
nb=[iirnotch(f0,30,fs) for f0 in (60,120,180)]
bb=butter(4,[0.5/(fs/2),30/(fs/2)],btype="band")
def chain(v):
    v=v-v.mean()
    for b,a in nb: v=filtfilt(b,a,v)
    return filtfilt(*bb,v)
def feats(site):
    v=np.asarray(x[start:start+T,lab.index(site)],dtype=np.float64)
    rl=(np.abs(v)>=RAIL).mean(); y=chain(v)
    f,P=welch(y,fs,nperseg=4096); m=(f>=1)&(f<=30)
    sl=np.polyfit(np.log10(f[m]),np.log10(P[m]+1e-20),1)[0]
    band=(f>=0.5)&(f<=30); dl=P[(f>=0.5)&(f<=4)].sum()/P[band].sum()
    return rl,y.std(),sl,dl
FLOOR=[f"{p}/{i}" for p in "ABCD" for i in list(range(3,17))+list(range(35,49))]
F=np.array([feats(s) for s in FLOOR])
print(f"FLOOR CONTROL, {len(FLOOR)} wire-free inputs, SAME filter chain")
for i,nm in enumerate(["% railed","post rms uV","spectral slope","delta frac"]):
    q=np.percentile(F[:,i],[5,50,95])
    print(f"  {nm:16} p5 {q[0]:8.2f}   median {q[1]:8.2f}   p95 {q[2]:8.2f}")
lo,hi=np.percentile(F[:,2],[5,95]); rmax=np.percentile(F[:,1],95)
print(f"\n  ==> a channel is DISTINGUISHABLE from a wire only if it falls OUTSIDE")
print(f"      slope [{lo:.2f}, {hi:.2f}]  or  post rms > {rmax:.1f} uV\n")
A=[(f"{p}{m}",f"{p}/{e}") for p in "ABCD" for m,e in ((1,1),(2,33))]
print(f"{'animal EEG':12}{'%railed':>9}{'post rms':>10}{'slope':>8}{'delta':>8}   verdict")
for name,s in A:
    rl,r,sl,dl=feats(s)
    out = (sl<lo or sl>hi) or r>rmax
    vd=("RAILED >1%, unrecoverable" if rl>0.01 else
        ("differs from a bare wire" if out else "INDISTINGUISHABLE from a bare wire"))
    print(f"{name:12}{rl:8.1%}{r:10.1f}{sl:8.2f}{dl:8.2f}   {vd}"+("  <-NO MOUSE" if name=="A2" else ""))
