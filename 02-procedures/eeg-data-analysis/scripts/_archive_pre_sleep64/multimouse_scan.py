"""
multimouse_scan.py -- usability scan for multi-headstage XDAT recordings that
are too big to load into RAM. Memory-maps the _data.xdat and samples windows
spread across the whole recording.

For each candidate mouse slot (4 native chans: EEG_F, EEG_P, EMG_L, EMG_R):
  - raw per-chan RMS, pk-pk, %@rail  (is the electrode floating/open?)
  - EEG bipolar (F-P) RMS
  - 60 Hz mains-hum power fraction of the bipolar, RAW and after a 60 Hz notch
  - fraction of bipolar power that is physiological (0.5-40 Hz, notch applied)
  - EMG bipolar RMS
  - VERDICT: DEAD (not connected) / HUM (railed by 60 Hz) / MARGINAL / USABLE

Then, for LIVE slots only, builds a low-res overview PNG: EEG bipolar PSD,
theta/delta ratio over the whole recording (1 epoch/min), and EMG RMS over time
-- i.e. does the channel actually carry sleep/wake structure.

No project deps except numpy/scipy/matplotlib (the analysis venv).
"""
import sys, json, argparse
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy import signal

RAIL_UV = 6390.0          # RHD2216 full scale ~ +-6.4 mV
MAINS_HZ = 60.0           # Korea mains (see vault 60hz-mains-discovery)

# mouse slot layouts: name -> list of (mouse_label, port, base_row)
# each slot's 4 data rows = base+0 EEG_F, +1 EEG_P, +2 EMG_L, +3 EMG_R
LAYOUTS = {
    # 0713: 8 selected slots (2 per port), only 4 physically connected
    "eight": [("A1","A",0),("A2","A",32),("B1","B",64),("B2","B",96),
              ("C1","C",128),("C2","C",160),("D1","D",192),("D2","D",224)],
    # 0710 72h run: 4 mice, one per port
    "four":  [("A","A",0),("B","B",64),("C","C",128),("D","D",192)],
}


def load_meta(base):
    m = json.load(open(base + ".xdat.json"))["status"]
    return int(m["samp_freq"]), int(m["num_smpl"]), int(m["signals"]["total"])


def notch60(x, fs):
    # comb out mains + all harmonics up to Nyquist
    y = x
    h = MAINS_HZ
    while h < fs/2 - 1:
        b, a = signal.iirnotch(h, Q=30, fs=fs)
        y = signal.filtfilt(b, a, y)
        h += MAINS_HZ
    return y


def bandpower(f, Pxx, lo, hi):
    m = (f >= lo) & (f < hi)
    return np.trapezoid(Pxx[m], f[m])


def scan(base, layout, n_win=40, win_s=20):
    fs, n, tot = load_meta(base)
    mm = np.memmap(base + "_data.xdat", dtype="<f4", mode="r", shape=(n, tot))
    w = int(win_s * fs)
    starts = np.linspace(int(2*fs), n - w - int(2*fs), n_win).astype(int)

    slots = LAYOUTS[layout]
    # gather all needed rows once per window
    results = {}
    for lab, port, base_row in slots:
        rows = [base_row + k for k in range(4)]
        acc = {r: [] for r in rows}
        bip_eeg, bip_emg = [], []
        for s in starts:
            seg = np.asarray(mm[s:s+w, :])           # (w, tot) into RAM (~20 MB)
            F = seg[:, base_row+0].astype(np.float64)
            P = seg[:, base_row+1].astype(np.float64)
            EL = seg[:, base_row+2].astype(np.float64)
            ER = seg[:, base_row+3].astype(np.float64)
            for r, x in zip(rows, (F, P, EL, ER)):
                acc[r].append((x.std(), x.max()-x.min(),
                               100*np.mean(np.abs(x) > 0.98*RAIL_UV)))
            bip_eeg.append(F - P)
            bip_emg.append(EL - ER)
        # aggregate raw per-chan
        chan = {}
        for r in rows:
            a = np.array(acc[r])
            chan[r] = dict(rms=np.median(a[:,0]), pkpk=np.median(a[:,1]),
                           rail=np.median(a[:,2]))
        # bipolar spectra (average welch over windows)
        be = np.concatenate(bip_eeg)
        bm = np.concatenate(bip_emg)
        f, Pr = signal.welch(be, fs=fs, nperseg=fs*2)
        be_n = notch60(be, fs)
        f, Pn = signal.welch(be_n, fs=fs, nperseg=fs*2)
        tot_r = bandpower(f, Pr, 0.5, fs/2)
        hum_r = bandpower(f, Pr, 58, 62)
        tot_n = bandpower(f, Pn, 0.5, fs/2)
        hum_n = bandpower(f, Pn, 58, 62)
        phys_n = bandpower(f, Pn, 0.5, 40)
        results[lab] = dict(
            port=port, base=base_row, chan=chan,
            eeg_rms=be.std(), eeg_rms_n=be_n.std(),
            emg_rms=bm.std(),
            hum_frac_raw=hum_r/(tot_r+1e-9),
            hum_frac_notch=hum_n/(tot_n+1e-9),
            phys_frac_notch=phys_n/(tot_n+1e-9),
            f=f, Pr=Pr, Pn=Pn)
    return fs, n, results


def verdict(r):
    """Classify a slot from its metrics."""
    eF, eP = r['chan'][r['base']+0], r['chan'][r['base']+1]
    railed = eF['rail'] > 5 and eP['rail'] > 5
    # a not-connected slot: both EEG pads near-fully railed OR near-zero flat
    both_open = (eF['rail'] > 50 and eP['rail'] > 50)
    flat = r['eeg_rms'] < 3          # essentially no signal
    if flat:
        return "DEAD", "flat, no signal (not connected)"
    if both_open:
        return "DEAD", "both EEG pads railed (open/floating)"
    hum = r['hum_frac_raw']
    if hum > 0.5 and r['eeg_rms_n'] > 500:
        return "HUM", f"60Hz-dominated ({hum*100:.0f}% raw pwr), notch leaves {r['eeg_rms_n']:.0f}uV"
    if r['phys_frac_notch'] > 0.6 and 10 < r['eeg_rms_n'] < 800 and r['hum_frac_notch'] < 0.2:
        return "USABLE", f"physiological ({r['phys_frac_notch']*100:.0f}% in 0.5-40Hz), {r['eeg_rms_n']:.0f}uV"
    return "MARGINAL", f"hum {hum*100:.0f}%->{r['hum_frac_notch']*100:.0f}% notch, {r['eeg_rms_n']:.0f}uV, phys {r['phys_frac_notch']*100:.0f}%"


def print_table(tag, fs, n, results):
    print(f"\n########## {tag}  ({n/fs/3600:.2f} h @ {fs} Hz) ##########")
    hdr = f"{'slot':5s} {'port':4s} {'EEG_F rms/rail':>16s} {'EEG_P rms/rail':>16s} " \
          f"{'EEGbip':>8s} {'notch':>7s} {'60Hz%raw':>9s} {'->notch':>8s} {'phys%':>6s} {'EMGbip':>8s}  VERDICT"
    print(hdr); print("-"*len(hdr))
    verds = {}
    for lab, r in results.items():
        eF, eP = r['chan'][r['base']+0], r['chan'][r['base']+1]
        v, why = verdict(r)
        verds[lab] = (v, why)
        print(f"{lab:5s} {r['port']:4s} "
              f"{eF['rms']:8.0f}/{eF['rail']:4.0f}% {eP['rms']:8.0f}/{eP['rail']:4.0f}% "
              f"{r['eeg_rms']:8.0f} {r['eeg_rms_n']:7.0f} {r['hum_frac_raw']*100:8.0f}% "
              f"{r['hum_frac_notch']*100:7.0f}% {r['phys_frac_notch']*100:5.0f}% {r['emg_rms']:8.0f}  {v}")
    print()
    for lab,(v,why) in verds.items():
        print(f"   {lab}: {v} -- {why}")
    return verds


def overview_png(base, tag, fs, n, results, verds):
    live = [l for l,(v,_) in verds.items() if v in ("USABLE","MARGINAL","HUM")]
    if not live:
        print("no live slots -> skip time-series PNG")
        # still emit a PSD-only figure of all slots
        live = list(results.keys())
    mm = np.memmap(base + "_data.xdat", dtype="<f4", mode="r",
                   shape=(n, load_meta(base)[2]))
    ep = 4*fs
    step = 60*fs                       # 1 epoch per minute
    idx = np.arange(0, n-ep, step)
    th = idx/fs/3600.0

    fig, axes = plt.subplots(len(live), 3, figsize=(16, 2.6*len(live)),
                             squeeze=False)
    for i, lab in enumerate(live):
        r = results[lab]; b = r['base']
        # (0) PSD raw vs notch
        ax = axes[i][0]
        ax.semilogy(r['f'], r['Pr'], color='crimson', lw=.7, label='raw')
        ax.semilogy(r['f'], r['Pn'], color='navy', lw=.7, label='60Hz notch')
        ax.set_xlim(0, 80); ax.axvline(60, color='gray', ls=':', lw=.6)
        ax.set_ylabel(f"{lab} ({verds[lab][0]})\nPSD");
        if i==0: ax.legend(fontsize=7); ax.set_title("EEG bipolar spectrum")
        # theta/delta + EMG over time via 1 epoch/min
        de=[]; tr=[]; em=[]
        for j in idx:
            seg = np.asarray(mm[j:j+ep, :])
            be = notch60(seg[:,b].astype(np.float64)-seg[:,b+1].astype(np.float64), fs)
            bm = seg[:,b+2].astype(np.float64)-seg[:,b+3].astype(np.float64)
            f,Px = signal.welch(be, fs=fs, nperseg=min(ep, fs*2))
            d=bandpower(f,Px,0.5,4); t=bandpower(f,Px,6,9)
            de.append(d); tr.append(t/(d+1e-9)); em.append(bm.std())
        de=np.array(de); tr=np.clip(np.array(tr),0,4); em=np.array(em)
        sm=lambda x,k=15: np.convolve(x,np.ones(k)/k,mode='same')
        ax=axes[i][1]
        ax.plot(th,tr,lw=.3,color='orange'); ax.plot(th,sm(tr),lw=1,color='red')
        ax.axhline(1,color='k',ls=':',lw=.5); ax.set_ylabel("theta/delta")
        if i==0: ax.set_title("theta/delta (sleep/wake cycling?)")
        ax=axes[i][2]
        ax.plot(th,em,lw=.3,color='green'); ax.plot(th,sm(em),lw=1,color='darkgreen')
        ax.set_ylabel("EMG RMS uV")
        if i==0: ax.set_title("EMG tone over time")
        if i==len(live)-1:
            for k in range(3): axes[i][k].set_xlabel("time (h)")
    fig.suptitle(f"{tag}  --  multi-mouse usability overview", y=1.0)
    plt.tight_layout()
    out = base + "_multimouse_overview.png"
    plt.savefig(out, dpi=85, bbox_inches='tight')
    print(f"wrote {out}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("base")
    ap.add_argument("layout", choices=list(LAYOUTS))
    ap.add_argument("--tag", default=None)
    ap.add_argument("--nwin", type=int, default=40)
    ap.add_argument("--no-png", action="store_true")
    a = ap.parse_args()
    base = a.base
    for suf in ("_data.xdat",".xdat.json"):
        if base.endswith(suf): base = base[:-len(suf)]
    tag = a.tag or base.split("__")[-1]
    fs, n, results = scan(base, a.layout, n_win=a.nwin)
    verds = print_table(tag, fs, n, results)
    if not a.no_png:
        overview_png(base, tag, fs, n, results, verds)
