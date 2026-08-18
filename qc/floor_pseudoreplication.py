#!/usr/bin/env python3
"""How independent are the wire-free floor channels really?

The council's peer reviewers all flagged, independently, that our 112 wire-free
amplifier inputs are NOT 112 independent samples: they share a board, a
reference, a ground and a room, so their noise is correlated. Every threshold we
derive from that distribution has an unknown width.

This quantifies it two ways:

  1. **Intraclass correlation by port.** How much of the variance in a channel's
     60 Hz amplitude is explained by which PORT it sits on? High ICC means the
     port, not the channel, is the unit of replication.
  2. **Cluster bootstrap.** Resample whole PORTS rather than channels and see how
     much wider the confidence interval on the 1st-percentile threshold becomes.
     The ratio of the two CI widths is the honest inflation factor.

Usage
    python3 floor_pseudoreplication.py <recording_base> [--epochs 400]
"""
import argparse
import json
import os

import numpy as np

PORTS = "ABCD"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("base")
    ap.add_argument("--epochs", type=int, default=400)
    ap.add_argument("--boot", type=int, default=2000)
    a = ap.parse_args()

    d = json.load(open(a.base + ".xdat.json"))
    bm = d["sapiens_base"]["biointerface_map"]
    lab = [f"{p}/{s}" for p, s in zip(bm["port"], bm["site_num"])]
    n = len(lab)
    fs = int(d["status"]["samp_freq"])
    ns = os.path.getsize(a.base + "_data.xdat") // (n * 4)
    x = np.memmap(a.base + "_data.xdat", dtype=np.float32, mode="r", shape=(ns, n))

    # wire-free inputs, EEG+EMG cohort layout
    floor = {p: [f"{p}/{i}" for i in list(range(3, 17)) + list(range(35, 49))]
             for p in PORTS}
    ep = 10 * fs
    idx = np.linspace(0, ns // ep - 1, a.epochs).astype(int)
    win = np.hanning(ep)
    g = win.sum() / 2
    fr = np.fft.rfftfreq(ep, 1 / fs)
    m60 = (fr >= 59) & (fr <= 61)

    per_chan, chan_port = [], []
    for p in PORTS:
        for s in floor[p]:
            c = lab.index(s)
            vals = []
            for k in idx:
                v = np.asarray(x[k * ep:(k + 1) * ep, c], dtype=np.float64)
                v -= v.mean()
                vals.append((np.abs(np.fft.rfft(v * win)) / g)[m60].max())
            per_chan.append(np.array(vals))
            chan_port.append(p)
    per_chan = np.array(per_chan)
    chan_port = np.array(chan_port)
    print(f"floor channels {len(per_chan)}   epochs sampled {len(idx)}   "
          f"total readings {per_chan.size}")

    # ---- 1. ICC by port, on per-channel medians
    med = np.median(per_chan, axis=1)
    grand = med.mean()
    groups = [med[chan_port == p] for p in PORTS]
    k = np.mean([len(gp) for gp in groups])
    ms_between = sum(len(gp) * (gp.mean() - grand) ** 2 for gp in groups) / (len(groups) - 1)
    ms_within = sum(((gp - gp.mean()) ** 2).sum() for gp in groups) / (len(med) - len(groups))
    icc = (ms_between - ms_within) / (ms_between + (k - 1) * ms_within)
    icc = float(np.clip(icc, 0, 1))
    n_eff = len(med) / (1 + (k - 1) * icc)
    print(f"\nICC by port                {icc:.3f}")
    print(f"design effect              {1 + (k - 1) * icc:.2f}")
    print(f"nominal n (channels)       {len(med)}")
    print(f"EFFECTIVE n                {n_eff:.1f}")

    # ---- 2. cluster bootstrap of the 1st-percentile threshold
    rng = np.random.default_rng(0)
    flat = per_chan.ravel()
    naive, clust = [], []
    for _ in range(a.boot):
        s = rng.integers(0, len(flat), len(flat))
        naive.append(np.percentile(flat[s], 1))
        ports = rng.choice(list(PORTS), len(PORTS))
        pool = np.concatenate([per_chan[chan_port == p].ravel() for p in ports])
        clust.append(np.percentile(pool, 1))
    ci_n = np.percentile(naive, [2.5, 97.5])
    ci_c = np.percentile(clust, [2.5, 97.5])
    w_n, w_c = ci_n[1] - ci_n[0], ci_c[1] - ci_c[0]
    print(f"\n1st-percentile threshold   {np.percentile(flat,1):.1f} µV")
    print(f"  naive CI   (resample channels) [{ci_n[0]:7.1f}, {ci_n[1]:7.1f}]  width {w_n:7.1f}")
    print(f"  cluster CI (resample PORTS)    [{ci_c[0]:7.1f}, {ci_c[1]:7.1f}]  width {w_c:7.1f}")
    print(f"  INFLATION FACTOR {w_c / w_n:.1f}x")
    print("\n>> Quote the CLUSTER interval. The naive one treats correlated")
    print("   channels as independent and is too narrow.")


if __name__ == "__main__":
    main()
