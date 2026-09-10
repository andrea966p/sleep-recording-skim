"""Per-animal failure forensics on the 2026-08-06 overnight recording.

Distinguishes failure modes that all look like "OPEN" in stage 1:
  floating / open conductor -> huge hum, railing, flat spectrum
  shorted pair or lost ground -> LOW hum, low rms, flat spectrum, no signal
  one channel only          -> the other is fine => fault is that electrode
  both channels together    -> shared path (tether, ground, connector)
"""
import json,os,numpy as np
from scipy.signal import iirnotch,butter,filtfilt,welch
from core import paths as PATHS
B=str(PATHS.RAW_ROOT) + "/allego_1__uid0806-16-57-38"
d=json.load(open(B+".xdat.json")); bm=d['sapiens_base']['biointerface_map']
lab=[f"{p}/{s}" for p,s in zip(bm['port'],bm['site_num'])]; n=len(lab); fs=1000
ns=os.path.getsize(B+"_data.xdat")//(n*4)
x=np.memmap(B+"_data.xdat",dtype=np.float32,mode="r",shape=(ns,n))
ep=10*fs; RAIL=6389.6
# sample 120 epochs spread across the whole 23.66 h
idx=np.linspace(0,ns//ep-1,120).astype(int)
nb=[iirnotch(f,30,fs) for f in (60,120,180)]; bp=butter(4,[0.5/500,30/500],btype="band")
def chain(v):
    v=v-v.mean()
    for b,a in nb: v=filtfilt(b,a,v)
    return filtfilt(*bp,v)
win=np.hanning(ep); g=win.sum()/2; fr=np.fft.rfftfreq(ep,1/fs); m60=(fr>=59)&(fr<=61)
def stats(site):
    c=lab.index(site); hum=[];rms=[];rail=[];slo=[]
    for k in idx:
        v=np.asarray(x[k*ep:(k+1)*ep,c],dtype=np.float64)
        rail.append((np.abs(v)>=RAIL).mean()); rms.append(v.std())
        vv=v-v.mean()
        hum.append((np.abs(np.fft.rfft(vv*win)) /g)[m60].max())
        y=chain(v); f,P=welch(y,fs,nperseg=2048); mm=(f>=1)&(f<=30)
        slo.append(np.polyfit(np.log10(f[mm]),np.log10(P[mm]+1e-20),1)[0])
    return np.median(hum),np.median(rms),np.mean(rail),np.median(slo)
def corr(s1,s2):
    c1,c2=lab.index(s1),lab.index(s2); r=[]
    for k in idx[::4]:
        a=chain(np.asarray(x[k*ep:(k+1)*ep,c1],dtype=np.float64))
        b=chain(np.asarray(x[k*ep:(k+1)*ep,c2],dtype=np.float64))
        r.append(abs(np.corrcoef(a,b)[0,1]))
    return np.median(r)
ANI=[("A1","A/1","A/2"),("A2 NO MOUSE","A/33","A/34"),("B1","B/1","B/2"),("B2","B/33","B/34"),
     ("C1","C/1","C/2"),("C2 chewed","C/33","C/34"),("D1","D/1","D/2"),("D2","D/33","D/34")]
FL=["A/5","B/7","C/9","D/11","A/38","C/40"]
f=np.array([stats(s) for s in FL])
print(f"FLOOR (wire-free, n={len(FL)}): hum {np.median(f[:,0]):7.1f}  rms {np.median(f[:,1]):7.1f}  "
      f"rail {np.mean(f[:,2]):5.1%}  slope {np.median(f[:,3]):+.2f}\n")
print(f"{'animal':13}{'ch':5}{'hum uV':>9}{'rms uV':>9}{'railed':>8}{'slope':>7}   {'EEG~EMG r':>9}")
OUT={"recording":os.path.basename(B),"n_epochs_sampled":len(idx),"epoch_s":10,
     "filter":"notch 60/120/180 Hz Q=30 then 4th-order Butterworth 0.5-30 Hz, zero phase",
     "slope_band_hz":[1,30],"welch_nperseg":2048,
     "floor_sites":FL,
     "floor":{"hum_uv":float(np.median(f[:,0])),"rms_uv":float(np.median(f[:,1])),
              "railed":float(np.mean(f[:,2])),"slope":float(np.median(f[:,3])),
              "slope_min":float(f[:,3].min()),"slope_max":float(f[:,3].max()),
              "hum_min":float(f[:,0].min()),"hum_max":float(f[:,0].max())},
     "animals":{}}
for name,e,g_ in ANI:
    r=corr(e,g_)
    rec={"eeg_site":e,"emg_site":g_,"inter_channel_r":float(r)}
    for tag,s in (("EEG",e),("EMG",g_)):
        h,rm,ra,sl=stats(s)
        rec[tag.lower()]={"hum_uv":float(h),"rms_uv":float(rm),
                          "railed":float(ra),"slope":float(sl)}
        print(f"{name if tag=='EEG' else '':13}{tag:5}{h:9.1f}{rm:9.1f}{ra:8.1%}{sl:+7.2f}   "
              f"{r:9.2f}" if tag=="EEG" else
              f"{'':13}{tag:5}{h:9.1f}{rm:9.1f}{ra:8.1%}{sl:+7.2f}")
    OUT["animals"][name.split()[0]]=rec

import sys
if "--json" in sys.argv:
    p=sys.argv[sys.argv.index("--json")+1]
    json.dump(OUT,open(p,"w"),indent=1)
    print(f"\nwrote {p}")
