"""Hourly hum of the four noise-series mice, read from the runs' QC bundles (no raw read).

usage: python3 qc/hourly_hum_bundle.py OUT.csv BASE [BASE ...]
BASE is the Allego base name (the bundle is EEG_CACHE_ROOT/BASE.npz, default ~/eeg-qc-cache). For every clock hour:
the chip floor (median over the chip's 14 wire-free inputs of the gate's 10 s 60 Hz line peak), EEG and EMG 60 Hz, and
the fraction of 10 s epochs with the EMG on the rail. Hourly value = median over the hour's epochs (>= 10 min of data).
Same estimator as the 2026-10-02 24 h table (qc/noise_mice_24h_2026_10_02.py), so the two can be compared directly.
"""
import csv, os, sys, datetime as dt
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import noise_mice_markers_2026_10_02 as MK

CACHE = os.path.expanduser(os.environ.get("EEG_CACHE_ROOT", "~/eeg-qc-cache"))
MICE = {"A1": ("A", 1), "A2": ("A", 33), "B1": ("B", 1), "B2": ("B", 33)}


def epochs(base):
    z = np.load(os.path.join(CACHE, base + ".npz"), allow_pickle=True)
    sites = [str(x) for x in z["sites"]]; ix = {s: i for i, s in enumerate(sites)}; es = float(z["epoch_s"])
    t0 = MK.file_origin(base)[0]
    t = np.array([t0 + dt.timedelta(seconds=(k + .5) * es) for k in range(z["hum"].shape[0])])
    out = {"t": t}
    for m, (p, s) in MICE.items():
        out[f"{m}_floor"] = np.median(z["hum"][:, [ix[f"{p}/{q}"] for q in range(s + 2, s + 16)]], 1)
        out[f"{m}_eeg60"] = z["hum"][:, ix[f"{p}/{s}"]]
        out[f"{m}_emg60"] = z["hum"][:, ix[f"{p}/{s + 1}"]]
        out[f"{m}_emgrail"] = z["rail"][:, ix[f"{p}/{s + 1}"]].astype(float)
    return out, es


def main(out_csv, bases):
    rows = []
    for base in bases:
        E, es = epochs(base)
        h0 = E["t"][0].replace(minute=0, second=0, microsecond=0)
        while h0 <= E["t"][-1]:
            m = (E["t"] >= h0) & (E["t"] < h0 + dt.timedelta(hours=1))
            if m.sum() * es >= 600:
                r = {"run": base, "hour_start_kst": h0.strftime("%Y-%m-%d %H:%M"), "light": int(9 <= h0.hour < 21),
                     "n_epochs": int(m.sum())}
                for k in E:
                    if k != "t":
                        r[k] = round(float(np.median(E[k][m])), 3) if not k.endswith("rail") else round(float(E[k][m].mean()), 4)
                rows.append(r)
            h0 += dt.timedelta(hours=1)
    with open(out_csv, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
    print(f"wrote {out_csv}: {len(rows)} hours")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2:])
