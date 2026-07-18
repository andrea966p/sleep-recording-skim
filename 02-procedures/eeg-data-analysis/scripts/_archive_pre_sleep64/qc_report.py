"""
qc_report.py  --  Quick signal-quality check for an XDAT recording.

Prints a per-channel table (RMS, pk-pk, % near amplifier rail) and writes a
3-panel overview PNG (delta power / theta-delta ratio / EEG RMS over the whole
recording) so you can confirm at a glance that:
  - the EEG is real (RMS tens-to-low-hundreds uV, not railed),
  - grounding held (channels not all pinned at the +-6.4 mV rail),
  - sleep/wake structure is present (theta/delta ratio cycles).

Requires the analysis venv (numpy, scipy, matplotlib).

Usage:
    python qc_report.py <recording_base> [--config single_mouse]
                        [--epoch 4]
    (2mice32 config DEPRECATED 2026-07-01 -- one mouse per headstage; see xdat_io.py)
"""
import argparse
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy import signal
from xdat_io import load_xdat, CHANNEL_MAPS, BIPOLAR_DERIVATIONS, bipolar

RAIL_UV = 6390.0  # RHD2216 full-scale ~ +-6.4 mV


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("base")
    ap.add_argument("--config", default="single_mouse")
    ap.add_argument("--epoch", type=float, default=4.0)
    args = ap.parse_args()

    rec = load_xdat(args.base)
    fs = rec.fs

    print(f"{rec.n_samples} samples @ {fs} Hz ({rec.n_samples/fs/60:.1f} min)\n")
    print(f"{'channel':14s} {'RMS_uV':>9s} {'pkpk_uV':>9s} {'%@rail':>7s}  read")
    for ntv, lab in CHANNEL_MAPS[args.config].items():
        x = rec.data[ntv].astype(np.float64)
        rms = x.std(); pk = x.max() - x.min()
        rail = 100 * np.mean(np.abs(x) > 0.98 * RAIL_UV)
        if rail > 5: tag = "OPEN/railed"
        elif "EEG" in lab and rms < 300: tag = "clean EEG"
        else: tag = ""
        print(f"  {lab+'_n'+str(ntv):12s} {rms:9.1f} {pk:9.1f} {rail:7.1f}  {tag}")

    # overview from the first EEG bipolar pair
    le, pe, me = BIPOLAR_DERIVATIONS[args.config][0]
    eeg = bipolar(rec.data, pe, me)
    ep = int(args.epoch * fs); ne = eeg.size // ep
    E = eeg[:ne*ep].reshape(ne, ep)
    f, Pxx = signal.welch(E, fs=fs, nperseg=min(ep, fs*2), axis=1)
    band = lambda lo, hi: np.trapezoid(Pxx[:, (f >= lo) & (f < hi)],
                                       f[(f >= lo) & (f < hi)], axis=1)
    delta, theta = band(0.5, 4), band(6, 9)
    ratio = theta / (delta + 1e-12)
    th = np.arange(ne) * args.epoch / 3600.0
    sm = lambda x, k=15: np.convolve(x, np.ones(k)/k, mode="same")

    fig, ax = plt.subplots(3, 1, figsize=(13, 7), sharex=True)
    ax[0].plot(th, delta, lw=.3, color="steelblue"); ax[0].plot(th, sm(delta), lw=1, color="navy")
    ax[0].set_ylabel("delta 0.5-4\n(uV^2)")
    ax[0].set_title(f"{le}  |  {rec.n_samples/fs/3600:.1f} h  |  {args.epoch:g}s epochs")
    r = np.clip(ratio, 0, 4)
    ax[1].plot(th, r, lw=.3, color="orange"); ax[1].plot(th, sm(r), lw=1, color="red")
    ax[1].axhline(1, color="k", ls=":", lw=.6); ax[1].set_ylabel("theta/delta")
    ax[2].plot(th, E.std(axis=1), lw=.4, color="green")
    ax[2].set_ylabel("EEG RMS\n(uV)"); ax[2].set_xlabel("time (h)")
    plt.tight_layout()
    out = rec.base + "_qc_overview.png"
    plt.savefig(out, dpi=90)
    print(f"\nwrote {out}")


if __name__ == "__main__":
    main()
