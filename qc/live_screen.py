"""Live look v2: per-channel noise/shape + ECG heartbeat detection (independent biology test)."""
import numpy as np, sys
from scipy.signal import welch, butter, filtfilt, iirnotch, find_peaks

X = np.load(sys.argv[1] + ".npy")
SEL = ['A/1','A/2','A/3','A/33','A/34','A/35','B/1','B/2','B/3','B/33','B/34','B/35',
       'C/1','C/2','C/3','C/33','C/34','C/35','D/1','D/2','D/3','D/33','D/34','D/35']
FS = 1000.0; RAIL = 6389.6
ROLE = {1:'EEG',2:'EMG',3:'ECG',33:'EEG',34:'EMG',35:'ECG'}
SLOT = {1:'m1',2:'m1',3:'m1',33:'m2',34:'m2',35:'m2'}

def notched(v):
    for f0 in (60,120,180,240,300,360,420):
        b,a = iirnotch(f0, 30, FS); v = filtfilt(b,a,v)
    return v

def amp_at(f,P,f0,bw=1.0):
    m=(f>=f0-bw)&(f<=f0+bw); return np.sqrt(np.trapezoid(P[m],f[m])*2)

print(f"{'site':<7}{'mouse':<6}{'role':<5}{'rms':>8}{'60Hz':>8}{'rms_nohum':>10}{'slope':>7}{'delta':>7}{'HR_bpm':>8}{'HRcv':>7}")
res={}
for i,s in enumerate(SEL):
    port,site = s.split('/'); site=int(site)
    v = X[i].astype(np.float64); v -= v.mean()
    rms = float(np.sqrt((v**2).mean()))
    f,P = welch(v,fs=FS,nperseg=4096)
    hum = amp_at(f,P,60.0)
    vn = notched(v)
    b,a = butter(3,[0.5,45],btype='band',fs=FS); vf = filtfilt(b,a,vn)
    rms_nh = float(np.sqrt((vf**2).mean()))
    fn,Pn = welch(vn,fs=FS,nperseg=4096)
    band=(fn>=1)&(fn<=40)
    slope=float(np.polyfit(np.log10(fn[band]),np.log10(Pn[band]+1e-20),1)[0])
    d=(fn>=1)&(fn<=4)
    delta=float(np.trapezoid(Pn[d],fn[d])/np.trapezoid(Pn[band],fn[band]))
    # heartbeat: bandpass 5-100 Hz, find peaks, check interval regularity
    bb,aa = butter(3,[5,100],btype='band',fs=FS); vh = filtfilt(bb,aa,vn)
    thr = 4*np.median(np.abs(vh))/0.6745
    pk,_ = find_peaks(np.abs(vh), height=thr, distance=int(FS*0.05))
    hr=np.nan; cv=np.nan
    if len(pk)>50:
        ibi=np.diff(pk)/FS
        ibi=ibi[(ibi>0.05)&(ibi<0.3)]
        if len(ibi)>50:
            hr=60/np.median(ibi); cv=float(np.std(ibi)/np.mean(ibi))
    print(f"{s:<7}{port+SLOT[site]:<6}{ROLE[site]:<5}{rms:8.1f}{hum:8.1f}{rms_nh:10.1f}{slope:7.2f}{delta:7.2f}{hr:8.1f}{cv:7.2f}")
