"""Stage A of the 2026-11 HLB re-score: per-4-s-epoch features for every ingested recording.

EEG features are SleepStager's own (sleepstager.features.batch_spectral: 1-s Hann Welch, 1-Hz
bins, delta 1-4 / theta 6-9 / sigma 10-15 / beta 15-30 / low gamma 30-50 Hz), so the rule
downstream sees exactly what the professor's tool computes.

EMG is measured three ways, because our rig's EMG carries 60 Hz mains (up to mV on open leads):
  ss60  SleepStager's 20-90 Hz RMS and spike-proof tone with its notch moved to 60 Hz
        (our fork's setting). Still contains 2x-harmonic leakage on bad leads.
  gap   time domain 70-470 Hz band-pass with notches at every 60 Hz multiple (60..420):
        RMS and spike-proof tone. The mains-free measure (2026-10-06 rescue, kappa 0.95 vs notch).
  gapw  Welch power summed only in the bins >= 7 Hz from every 60 Hz multiple, 67-470 Hz
        (the 2026-10-06 definition, kept for parity).
Plus diagnostics: 60 Hz line amplitude on EEG and EMG, rail contact, flat EEG.

Writes OUT/<batch>/<B|R>/<mouse>/features.parquet, psd_eeg.npy (n x 50, 1..50 Hz, uV^2),
psd_emg.npy (n x 500, 0..499 Hz). Usage: features.py ARRAYS OUT [--jobs 4]
"""
import argparse, json, sys, time
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.signal import butter, iirnotch, sosfiltfilt, filtfilt, welch, tf2sos

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "SleepStager"))
from sleepstager import features as F  # noqa: E402

FS, EP = 1000, 4000
GAPS = [(lo, hi) for lo, hi in ((67, 113), (127, 173), (187, 233), (247, 293), (307, 353), (367, 413), (427, 470))]


def gap_filter(x):
    sos = butter(4, [70, 470], "bandpass", fs=FS, output="sos")
    y = sosfiltfilt(sos, x)
    for f0 in range(60, 480, 60):          # 60 Hz included: the band-pass alone takes only 13.5 dB off it
        b, a = iirnotch(f0, Q=f0 / 12.0, fs=FS)          # ~12 Hz wide at every harmonic
        y = filtfilt(b, a, y)
    return y


def tone_median(xf_epochs, win=500, hop=100):
    sq = xf_epochs ** 2
    cs = np.concatenate([np.zeros((sq.shape[0], 1)), np.cumsum(sq, axis=1)], axis=1)
    st = np.arange((sq.shape[1] - win) // hop + 1) * hop
    return np.median(np.sqrt((cs[:, st + win] - cs[:, st]) / win), axis=1)


def one(rec: Path, out_root: Path) -> str:
    meta = json.loads((rec / "meta.json").read_text())
    out = out_root / rec.relative_to(rec.parents[2])
    if (out / "features.parquet").exists():
        return f"skip {out}"
    out.mkdir(parents=True, exist_ok=True)
    t0 = time.time()
    eeg = np.load(rec / "eeg.npy").astype(np.float64)
    emg = np.load(rec / "emg.npy").astype(np.float64)
    assert not meta["counter_gaps"], "counter gaps need a NaN-aware grid"
    n = len(eeg) // EP
    E, M = eeg[: n * EP].reshape(n, EP), emg[: n * EP].reshape(n, EP)

    tbl = pd.DataFrame(F.batch_spectral(E, fs=FS))
    f, pe = welch(E, fs=FS, window="hann", nperseg=FS, noverlap=FS // 2, axis=1)
    np.save(out / "psd_eeg.npy", pe[:, 1:51].astype(np.float32))
    tbl["eeg_line60_uv"] = np.sqrt(2 * pe[:, 59:62].sum(1))
    tbl["eeg_rms"] = E.std(1)
    del pe

    rms, cv = F.batch_emg_features(M, fs=FS, mains=60.0)
    tbl["emg_rms_ss60"], tbl["emg_cv_ss60"] = rms, cv
    tbl["emg_tone_ss60"] = F.batch_emg_tone_median(M, fs=FS, mains=60.0)
    g = gap_filter(emg[: n * EP]).reshape(n, EP)
    tbl["emg_rms_gap"] = np.sqrt((g ** 2).mean(1))
    tbl["emg_tone_gap"] = tone_median(g)
    del g
    f, pm = welch(M, fs=FS, window="blackmanharris", nperseg=FS, noverlap=FS // 2, axis=1)
    np.save(out / "psd_emg.npy", pm[:, :500].astype(np.float32))
    gap_cols = np.concatenate([np.arange(lo, hi + 1) for lo, hi in GAPS])
    tbl["emg_rms_gapw"] = np.sqrt(pm[:, gap_cols].sum(1))
    tbl["emg_line60_uv"] = np.sqrt(2 * pm[:, 59:62].sum(1))
    tbl["emg_rms_raw"] = M.std(1)
    del pm

    tbl["eeg_rail"] = F.rail_touch(E, F.rail_levels(E, FS))
    tbl["emg_rail"] = F.rail_touch(M, F.rail_levels(M, FS))
    tbl["eeg_flat"] = E.std(1) < 2.0                      # < 2 uV over 4 s: no signal
    start = pd.Timestamp(meta["start_kst"])
    tbl.insert(0, "t_kst", start + pd.to_timedelta(np.arange(n) * 4, unit="s"))
    tbl.insert(0, "epoch", np.arange(1, n + 1))
    tbl.to_parquet(out / "features.parquet", index=False)
    (out / "meta.json").write_text(json.dumps({**meta, "n_epochs": n, "features_s": round(time.time() - t0, 1)}, indent=1))
    return f"ok {out} n={n} {time.time() - t0:.0f} s"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("arrays", type=Path)
    ap.add_argument("out", type=Path)
    ap.add_argument("--jobs", type=int, default=4)
    ap.add_argument("--only", nargs="*")
    a = ap.parse_args()
    recs = sorted(p.parent for p in a.arrays.glob("*/*/*/meta.json"))
    if a.only:
        recs = [r for r in recs if any(o in str(r) for o in a.only)]
    with ProcessPoolExecutor(a.jobs) as ex:
        for msg in ex.map(one, recs, [a.out] * len(recs)):
            print(time.strftime("%H:%M:%S"), msg, flush=True)


if __name__ == "__main__":
    main()
