"""Does discarding railed epochs rescue the EEG channels?

For each animal: find epochs with ZERO railed samples, then measure spectral
shape on ONLY those epochs and compare to the wire-free floor distribution.
"""
import json,os,numpy as np
from scipy.signal import iirnotch, butter, filtfilt, welch
from core import paths as PATHS
BASE=str(PATHS.RAW_ROOT) + "/allego_0__uid0806-12-45-02"
d=json.load(open(BASE+".xdat.json")); bm=d['sapiens_base']['biointerface_map']
lab=[f"{p}/{s}" for p,s in zip(bm['port'],bm['site_num'])]; n=len(lab); fs=1000
nsamp=os.path.getsize(BASE+"_data.xdat")//(n*4)
x=np.memmap(BASE+"_data.xdat",dtype=np.float32,mode="r",shape=(nsamp,n))
ep=10*fs; nep=min(nsamp//ep,1200); RAIL=6389.6
nb=[iirnotch(f,30,fs) for f in (60,120,180)]; bb=butter(4,[0.5/500,30/500],btype="band")
def chain(v):
    v=v-v.mean()
    for b,a in nb: v=filtfilt(b,a,v)
    return filtfilt(*bb,v)
def shape(y):
    f,P=welch(y,fs,nperseg=2048); m=(f>=1)&(f<=30)
    sl=np.polyfit(np.log10(f[m]),np.log10(P[m]+1e-20),1)[0]
    b=(f>=0.5)&(f<=30)
    return sl,P[(f>=0.5)&(f<=4)].sum()/P[b].sum()
def perep(site):
    c=lab.index(site); r=np.zeros(nep); 
    for k in range(nep):
        v=np.asarray(x[k*ep:(k+1)*ep,c],dtype=np.float64)
        r[k]=(np.abs(v)>=RAIL).mean()
    return r
FLOOR=["B/5","C/7","A/9","D/11","B/38","C/40"]
fl=[]
for s in FLOOR:
    c=lab.index(s)
    for k in range(0,nep,7):
        fl.append(shape(chain(np.asarray(x[k*ep:(k+1)*ep,c],dtype=np.float64))))
fl=np.array(fl); slo,shi=np.percentile(fl[:,0],[5,95]); dhi=np.percentile(fl[:,1],95)
print(f"FLOOR (clean epochs, {len(fl)} samples): slope 5-95% [{slo:.2f},{shi:.2f}]  delta p95 {dhi:.2f}\n")
print(f"{'ch':10}{'ep':>5}{'%ep any rail':>14}{'longest rail run':>18}{'CLEAN ep':>10}{'slope':>8}{'delta':>7}   verdict")
for name,e,g in [(f"{p}{m}",f"{p}/{a}",f"{p}/{b}") for p in "ABCD" for m,a,b in ((1,1,2),(2,33,34))]:
    re_,rg=perep(e),perep(g)
    anyr=(re_>0); clean=~anyr
    run=best=0
    for v in anyr:
        run=run+1 if v else 0; best=max(best,run)
    idx=np.where(clean)[0]
    if len(idx)<5:
        print(f"{name+' EEG':10}{nep:5}{anyr.mean():13.1%}{best*10/60:15.1f} min{len(idx):10}      --     --   no clean epochs")
        continue
    S=np.array([shape(chain(np.asarray(x[k*ep:(k+1)*ep,lab.index(e)],dtype=np.float64)))
                for k in idx[::max(1,len(idx)//40)]])
    sl,dl=np.median(S,0)
    ok = sl<slo or dl>dhi
    both=(anyr & (rg>0)).sum()/max(1,anyr.sum())
    print(f"{name+' EEG':10}{nep:5}{anyr.mean():13.1%}{best*10/60:15.1f} min{len(idx):10}{sl:8.2f}{dl:7.2f}   "
          f"{'REAL EEG in clean epochs' if ok else 'STILL bare-wire-like'}  (EMG rails together {both:.0%})")
