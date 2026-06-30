"""
eeg_pipeline.py  --  Offline EEG/EMG processing for a sleep recording.

Pipeline (all offline, never in Allego):
    raw XDAT (uV, 1 kHz)
      -> bipolar derivation (EEG = n0-n1, EMG = n2-n3)
      -> bandpass  (EEG 0.5-30 Hz, EMG 10-300 Hz, Butterworth, zero-phase)
      -> 50 Hz notch
      -> decimate to target rate (default 256 Hz, anti-aliased)
      -> epoch into fixed windows (default 4 s)
      -> per-epoch band power (Welch) + EMG RMS + artifact flag
    Outputs:
      <base>_features.csv   one row per epoch
      prints a summary

Requires the analysis venv (numpy, scipy). See 01-environment-setup.md.

Usage:
    python eeg_pipeline.py <recording_base> [--config single_mouse|2mice32]
                           [--epoch 4] [--target-fs 256]
"""
import argparse
import numpy as np
from scipy import signal
from xdat_io import load_xdat, bipolar, BIPOLAR_DERIVATIONS

# rodent sleep bands (Hz)
BANDS = {"delta": (0.5, 4.0), "theta": (6.0, 9.0),
         "sigma": (10.0, 15.0), "total": (0.5, 30.0)}


def butter_band(x, fs, lo, hi, order=4):
    sos = signal.butter(order, [lo, hi], btype="band", fs=fs, output="sos")
    return signal.sosfiltfilt(sos, x)


def notch(x, fs, f0=50.0, Q=30.0):
    b, a = signal.iirnotch(f0, Q, fs)
    return signal.filtfilt(b, a, x)


def resample_to(x, fs, target):
    if target == fs:
        return x, fs
    g = np.gcd(int(target), int(fs))
    up, down = int(target) // g, int(fs) // g
    return signal.resample_poly(x, up, down), target


def band_power(epochs, fs):
    """epochs: (n_epochs, samples). Returns dict band -> (n_epochs,) power."""
    f, Pxx = signal.welch(epochs, fs=fs, nperseg=min(epochs.shape[1], int(fs * 2)), axis=1)
    out = {}
    for name, (lo, hi) in BANDS.items():
        m = (f >= lo) & (f < hi)
        out[name] = np.trapezoid(Pxx[:, m], f[m], axis=1)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("base")
    ap.add_argument("--config", default="single_mouse")
    ap.add_argument("--epoch", type=float, default=4.0, help="epoch length (s)")
    ap.add_argument("--target-fs", type=int, default=256)
    ap.add_argument("--artifact-uv", type=float, default=2000.0,
                    help="epoch flagged if |EEG| peak exceeds this (uV)")
    args = ap.parse_args()

    rec = load_xdat(args.base)
    fs = rec.fs
    print(f"loaded {rec.n_samples} samples @ {fs} Hz ({rec.n_samples/fs/60:.1f} min)")

    derivs = BIPOLAR_DERIVATIONS[args.config]
    eeg_label = next(l for l, *_ in derivs if "EEG" in l)
    emg_label = next((l for l, *_ in derivs if "EMG" in l), None)

    # build EEG (filtered) and EMG (filtered) for the FIRST mouse / pair.
    le, pe, me = derivs[0]  # EEG bipolar
    eeg = bipolar(rec.data, pe, me)
    eeg = notch(butter_band(eeg, fs, 0.5, 30.0), fs)

    emg = None
    emg_d = next((d for d in derivs if "EMG" in d[0]), None)
    if emg_d:
        emg = bipolar(rec.data, emg_d[1], emg_d[2])
        emg = notch(butter_band(emg, fs, 10.0, min(300.0, fs/2 - 1)), fs)

    # decimate
    eeg_ds, ds_fs = resample_to(eeg, fs, args.target_fs)
    emg_ds = resample_to(emg, fs, args.target_fs)[0] if emg is not None else None
    print(f"decimated to {ds_fs} Hz")

    # epoch
    ep = int(args.epoch * ds_fs)
    ne = eeg_ds.size // ep
    E = eeg_ds[:ne*ep].reshape(ne, ep)
    t = np.arange(ne) * args.epoch
    bp = band_power(E, ds_fs)
    eeg_rms = E.std(axis=1)
    ratio = bp["theta"] / (bp["delta"] + 1e-12)
    art = np.abs(E).max(axis=1) > args.artifact_uv
    emg_rms = (emg_ds[:ne*ep].reshape(ne, ep).std(axis=1) if emg_ds is not None
               else np.zeros(ne))

    # save
    cols = ["epoch", "t_s", "delta", "theta", "sigma", "total",
            "theta_delta", "eeg_rms_uv", "emg_rms_uv", "artifact"]
    arr = np.column_stack([np.arange(ne), t, bp["delta"], bp["theta"], bp["sigma"],
                           bp["total"], ratio, eeg_rms, emg_rms, art.astype(int)])
    out = rec.base + "_features.csv"
    np.savetxt(out, arr, delimiter=",", header=",".join(cols), comments="", fmt="%.4f")

    cl = ~art
    print(f"\nepochs={ne} ({args.epoch}s)  artifact={art.sum()} ({100*art.mean():.1f}%)")
    print(f"EEG RMS (clean): median={np.median(eeg_rms[cl]):.1f} uV")
    print(f"theta/delta: median={np.median(ratio[cl]):.2f}  range {ratio[cl].min():.2f}..{ratio[cl].max():.2f}")
    if emg is not None:
        print(f"EMG RMS (clean): median={np.median(emg_rms[cl]):.1f} uV "
              f"({'OPEN/railed' if np.median(emg_rms[cl])>1500 else 'plausible'})")
    print(f"wrote {out}  ({ne} rows)")


if __name__ == "__main__":
    main()
