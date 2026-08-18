import json,os,numpy as np
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy.signal import iirnotch, butter, filtfilt, welch
from core import paths as PATHS
BASE=str(PATHS.RAW_ROOT) + "/allego_0__uid0806-12-45-02"
OUT=str(PATHS.VAULT_ATTACHMENTS); os.makedirs(OUT,exist_ok=True)
d=json.load(open(BASE+".xdat.json")); bm=d['sapiens_base']['biointerface_map']
lab=[f"{p}/{s}" for p,s in zip(bm['port'],bm['site_num'])]; n=len(lab); fs=1000
nsamp=os.path.getsize(BASE+"_data.xdat")//(n*4)
x=np.memmap(BASE+"_data.xdat",dtype=np.float32,mode="r",shape=(nsamp,n))
T=600*fs; start=nsamp//2-T//2
nb=[iirnotch(f,30,fs) for f in (60,120,180)]; bb=butter(4,[0.5/500,30/500],btype="band")
def chain(v):
    v=v-v.mean()
    for b,a in nb: v=filtfilt(b,a,v)
    return filtfilt(*bb,v)
def get(s): return chain(np.asarray(x[start:start+T,lab.index(s)],dtype=np.float64))
ROWS=[("B1 EEG  B/1","B/1"),("B2 EEG  B/33","B/33"),("D2 EEG  D/33","D/33"),
      ("C2 EEG  C/33","C/33"),("A2 EEG (NO MOUSE)  A/33","A/33"),
      ("floor: bare wire  B/5","B/5"),("floor: bare wire  C/7","C/7")]
sig={l:get(s) for l,s in ROWS}
# FIG 1 traces, identical y scale
W=20*fs; t=np.arange(W)/fs
fig,ax=plt.subplots(len(ROWS),1,figsize=(13,11),sharex=True,sharey=True)
for a,(l,_) in zip(ax,ROWS):
    a.plot(t,sig[l][:W],lw=.6,color="tab:blue" if l.startswith("B1") else "0.35")
    a.set_ylabel(l,rotation=0,ha="right",va="center",fontsize=9)
    a.set_ylim(-400,400); a.grid(alpha=.2)
ax[0].set_title("20 s after 60/120/180 Hz notch + 0.5-30 Hz band-pass, IDENTICAL y scale (±400 µV)")
ax[-1].set_xlabel("seconds")
fig.tight_layout(); fig.savefig(f"{OUT}/traces_filtered.png",dpi=130); plt.close(fig)
# FIG 2 PSD
fig,a=plt.subplots(figsize=(9,6))
for l,_ in ROWS:
    f,P=welch(sig[l],fs,nperseg=4096); m=(f>=0.5)&(f<=45)
    a.loglog(f[m],P[m],lw=2 if l.startswith("B1") else 1,
             color="tab:blue" if l.startswith("B1") else None,label=l)
a.set_xlabel("Hz"); a.set_ylabel("PSD µV²/Hz"); a.grid(alpha=.3,which="both")
a.set_title("Power spectrum. Real EEG falls as 1/f; a bare wire is flat.")
a.legend(fontsize=8); fig.tight_layout(); fig.savefig(f"{OUT}/psd.png",dpi=130)
print("wrote", OUT)
for l,_ in ROWS: print(f"  {l:26} rms {sig[l].std():7.1f} uV")
