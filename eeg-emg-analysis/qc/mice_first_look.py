"""Quick look at each mouse in a short recording: EEG/EMG numbers, 10 s of traces, spectra.

usage: python3 qc/mice_first_look.py BASE OUT.png

Spectra are averaged over 4 s epochs AFTER dropping epochs that touch the amplifier rail or whose
rms is more than 5x the channel's median epoch rms (hardened 2026-10-02: a single whole-file Welch let
a 10 % artefact burst move a clean EEG's slope from -2.0 to -0.03). The kept fraction is printed.
Comparability: slope here is 2-40 Hz on the epoch-averaged spectrum and band shares use a 1-30 Hz
denominator; the pipeline's SLOPE_BAND_HZ (1-40, per epoch) and BAND_TOTAL differ, so treat these as
a first look, not as QC numbers. The EMG envelope uses 30-200 Hz (memory figures often use 10-300).
"""
import sys, numpy as np, scipy.signal as sg
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
sys.path.insert(0, "/home/skimlab/sleep-recording-skim/eeg-emg-analysis")
from core.criteria import open_xdat
from core import qc_thresholds as T
base = sys.argv[1]; out = sys.argv[2]
X, labels, fs, n = open_xdat(base); li = {l: i for i, l in enumerate(labels)}
mice = {"A1": ("A/1", "A/2"), "A2": ("A/33", "A/34"), "B1": ("B/1", "B/2"), "B2": ("B/33", "B/34")}
a, b = 5 * fs, n - 3 * fs
def bp(x, lo, hi): return sg.sosfiltfilt(sg.butter(4, [lo, hi], btype="band", fs=fs, output="sos"), x)
def robust_psd(x, ep=4):
    """Welch over 4 s epochs, keeping only epochs off the rail and within 5x the median epoch rms."""
    n_ep = len(x) // (ep * fs); E = x[: n_ep * ep * fs].reshape(n_ep, ep * fs)
    rms = E.std(1); keep = (np.abs(E).max(1) < T.RAIL_UV_EFF) & (rms <= 5 * np.median(rms))
    frac = float(keep.mean())                # reported as is: 0 % means every epoch was dirty
    f, P = sg.welch(E[keep] if keep.any() else E, fs, nperseg=ep * fs, axis=1)   # none clean: use all, flagged by 0 %
    return f, P.mean(0), frac
fig, ax = plt.subplots(5, 2, figsize=(15, 13), gridspec_kw={"width_ratios": [3, 1]})
t0 = 60; seg = slice((t0) * fs, (t0 + 10) * fs)
for r, (m, (ce, cm)) in enumerate(mice.items()):
    e = np.asarray(X[a:b, li[ce]], float); g = np.asarray(X[a:b, li[cm]], float)
    (f, Pe, ke), (_, Pg, kg) = robust_psd(e), robust_psd(g)
    sel = (f >= 2) & (f <= 40) & (np.abs(f - 60) > 3)
    slope = np.polyfit(np.log10(f[sel]), np.log10(Pe[sel]), 1)[0]
    band = lambda P, lo, hi: P[(f >= lo) & (f < hi)].sum() * (f[1] - f[0])
    tot = band(Pe, 1, 30)
    eb = bp(e, 1, 30); gb = bp(g, 30, 200)
    # EMG envelope variability (1 s)
    env = np.sqrt((gb[: len(gb) // fs * fs].reshape(-1, fs) ** 2).mean(1))
    rr = np.corrcoef(eb, bp(g, 1, 30))[0, 1]
    print(f"{m}: spectra kept EEG {ke*100:3.0f}% EMG {kg*100:3.0f}% of epochs | EEG 1-30 rms={eb.std():6.1f}  slope2-40={slope:5.2f}  delta1-4={band(Pe,1,4)/tot*100:4.0f}%  theta6-9={band(Pe,6,9)/tot*100:4.0f}%  "
          f"| EMG 30-200 rms={gb.std():7.1f} env p95/p5={np.percentile(env,95)/np.percentile(env,5):5.2f}  | r(EEG,EMG 1-30)={rr:+.2f}")
    tt = np.arange(10 * fs) / fs + t0
    ax[r, 0].plot(tt, bp(np.asarray(X[seg, li[ce]], float), 1, 30), lw=.6, label=f"{ce} EEG 1-30 Hz")
    ax[r, 0].plot(tt, bp(np.asarray(X[seg, li[cm]], float), 30, 200) - 400, lw=.6, color="C3", label=f"{cm} EMG 30-200 Hz (-400)")
    ax[r, 0].set_ylim(-1200, 500); ax[r, 0].set_title(m, loc="left"); ax[r, 0].legend(loc="upper right", fontsize=7)
    ax[r, 1].semilogy(f, Pe, label="EEG"); ax[r, 1].semilogy(f, Pg, color="C3", label="EMG"); ax[r, 1].set_xlim(0, 150)
    ax[r, 1].legend(fontsize=7)
# raw (unfiltered) EMG of the two suspicious ones
for c, col in (("A/2", "C1"), ("B/34", "C4")):
    ax[4, 0].plot(np.arange(2 * fs) / fs + t0, np.asarray(X[t0 * fs:(t0 + 2) * fs, li[c]], float), lw=.6, color=col, label=f"{c} RAW")
ax[4, 0].axhline(6389, ls=":", c="k"); ax[4, 0].axhline(-6389, ls=":", c="k"); ax[4, 0].legend(fontsize=7); ax[4, 0].set_title("raw open-looking EMG, 2 s (rail dotted)", loc="left")
ax[4, 1].axis("off"); ax[4, 0].set_xlabel("s"); fig.tight_layout(); fig.savefig(out, dpi=90)
