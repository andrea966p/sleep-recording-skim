import json,os,numpy as np
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
from scipy.signal import iirnotch,butter,filtfilt,welch
from datetime import datetime,timedelta
from core import paths as PATHS
OUT=str(PATHS.VAULT_ATTACHMENTS)
PRE=str(PATHS.RAW_ROOT) + "/allego_0__uid0806-12-45-02"     # afternoon, BEFORE D2 swap
NIG=str(PATHS.RAW_ROOT) + "/allego_1__uid0806-16-57-38"     # overnight, AFTER D2 swap
def openx(b):
    d=json.load(open(b+".xdat.json")); bm=d['sapiens_base']['biointerface_map']
    lab=[f"{p}/{s}" for p,s in zip(bm['port'],bm['site_num'])]; n=len(lab)
    ns=os.path.getsize(b+"_data.xdat")//(n*4)
    return np.memmap(b+"_data.xdat",dtype=np.float32,mode="r",shape=(ns,n)),lab,ns
fs=1000; nb=[iirnotch(f,30,fs) for f in (60,120,180)]; bp=butter(4,[0.5/500,30/500],btype="band")
def chain(v):
    v=v-v.mean()
    for b,a in nb: v=filtfilt(b,a,v)
    return filtfilt(*bp,v)
# ---- FIG D: D2 spectrum before vs after the swap
fig,ax=plt.subplots(figsize=(9.5,6))
for base,lbl,col,ls in ((PRE,"D2 EEG  BEFORE swap (afternoon, original tether + slip ring)","tab:red","-"),
                        (NIG,"D2 EEG  AFTER swap (overnight, long tether, no slip ring)","tab:green","-")):
    x,lab,ns=openx(base); i=lab.index("D/33"); st=ns//2-300*fs
    y=chain(np.asarray(x[st:st+600*fs,i],dtype=np.float64))
    f,P=welch(y,fs,nperseg=4096); m=(f>=0.5)&(f<=45)
    ax.loglog(f[m],P[m],ls,lw=2.4,color=col,label=lbl)
x,lab,ns=openx(NIG); st=ns//2-300*fs
for s,lbl,col in (("B/1","B1 EEG overnight (reference, works)","tab:blue"),
                  ("A/33","A2 = NO MOUSE (control)","0.45"),("B/5","bare wire (floor control)","0.7")):
    y=chain(np.asarray(x[st:st+600*fs,lab.index(s)],dtype=np.float64))
    f,P=welch(y,fs,nperseg=4096); m=(f>=0.5)&(f<=45)
    ax.loglog(f[m],P[m],lw=1.4,color=col,ls="--" if "NO MOUSE" in lbl or "bare" in lbl else "-",label=lbl)
ax.set_xlabel("frequency (Hz)"); ax.set_ylabel("power spectral density  (µV²/Hz)")
ax.set_title("Fig D. D2's EEG before and after the tether swap.\nReal brain activity falls steeply; noise is flat.")
ax.grid(alpha=.3,which="both"); ax.legend(fontsize=8.5,loc="lower left")
fig.tight_layout(); fig.savefig(f"{OUT}/2026-08-07-figD-D2-before-after.png",dpi=130); plt.close(fig)
print("figD done")
