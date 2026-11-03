"""Review packs for the 2026-11 HLB re-score: what a scorer looks at, as images.

Per recording, two PNGs in OUT/:
  <mouse>_<B|R>_overview.png  24 h: EEG spectrogram, delta and theta/delta, EMG against the rule's
                              cut, the rule's and the HMM's hypnograms, usable hours, the screen numbers
  <mouse>_<B|R>_epochs.png    up to 8 contested epochs (rule and HMM disagree, or the rule marked it),
                              each with +-2 epochs of raw EEG and mains-free EMG and the dossier numbers
plus OUT/contested_epochs.csv listing what was drawn, so a reviewer's call can be matched back.
Usage: review_pack.py ARRAYS EPOCHS OUT [--only ...]
"""
import argparse, json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.signal import butter, sosfiltfilt

from features import gap_filter

COL = {"W": "#d62728", "NR": "#1f77b4", "R": "#2ca02c", "X": "#7f7f7f", "U": "#ffffff"}
FS, EP = 1000, 4000


def hyp_row(ax, lab, y, h=0.8):
    lab = np.asarray(lab)
    cut = np.flatnonzero(lab[1:] != lab[:-1]) + 1
    for a, b in zip(np.r_[0, cut], np.r_[cut, len(lab)]):
        ax.add_patch(plt.Rectangle((a * 4 / 3600, y), (b - a) * 4 / 3600, h, color=COL.get(lab[a], "#fff"), lw=0))


def overview(d, s, h, f, psd, path):
    hrs = np.arange(len(h)) * 4 / 3600
    fig, ax = plt.subplots(5, 1, figsize=(16, 11), sharex=True,
                           gridspec_kw=dict(height_ratios=[2.2, 1.2, 1.2, 1.0, 0.4]))
    m = len(h) // 15 * 15
    spec = np.log10(psd[:m, :30].reshape(-1, 15, 30).mean(1)).T
    ax[0].imshow(spec, aspect="auto", origin="lower", extent=[0, m * 4 / 3600, 0.5, 30.5], cmap="magma",
                 vmin=np.percentile(spec, 2), vmax=np.percentile(spec, 98))
    ax[0].set_ylabel("EEG Hz (1-min)")
    ld = pd.Series(np.log10(f.delta_power)).rolling(15, center=True).median()
    ax[1].plot(hrs, ld, lw=0.5, color="k"); ax[1].set_ylabel("log10 δ")
    a2 = ax[1].twinx(); a2.plot(hrs, pd.Series(np.log10(f.theta_delta)).rolling(15, center=True).median(), lw=0.4, color="g")
    a2.set_ylabel("log10 θ/δ", color="g")
    src = s.get("emg_source", "gap")
    ax[2].plot(hrs, f[f"emg_rms_{src}"], lw=0.3, color="k"); ax[2].set_yscale("log")
    if s["emg_cut"]:
        ax[2].axhline(s["emg_cut"], color="r", lw=0.8)
    ax[2].set_ylabel(f"EMG {src} RMS µV")
    for y, c in ((2, "stage"), (1, "stage_hmm"), (0, "stage_eeg_only")):
        lab = h[c].replace({"WR": "W"}).to_numpy() if c == "stage_eeg_only" else h[c].to_numpy()
        hyp_row(ax[3], lab, y)
    ax[3].set_ylim(0, 3); ax[3].set_yticks([0.4, 1.4, 2.4], ["EEG-only (NR vs not)", "HMM", f"rule ({src} EMG)"])
    hyp_row(ax[4], np.where(h.hour_ok, "R", "W"), 0)
    ax[4].set_ylim(0, 1); ax[4].set_yticks([0.4], ["hour usable"])
    zt0 = h.zt_h.iloc[0]
    ax[4].set_xlabel(f"hours from window start (ZT{zt0:.1f}); lights off at ZT12")
    for a in ax:
        a.axvline(12 - zt0, color="orange", lw=1)
    fig.suptitle(f"{s['mouse']} {s['tp']} ({s['batch']}, {s['position']})   tier {s['tier']} (EMG {src})   η {s['eta']}   "
                 f"AUC δ(NR vs W) {s['auc_delta_recording']}   usable h {s['hours_both_ok']} "
                 f"({s['hours_both_ok_light']}L/{s['hours_both_ok_dark']}D)   κ rule-HMM {s['kappa_rule_hmm']}   "
                 f"wake L/D {s['wake_pct_light']}/{s['wake_pct_dark']} %   old: {s['old_qc']}", fontsize=10)
    fig.tight_layout(); fig.savefig(path, dpi=80); plt.close(fig)


def contested(d, rec_arrays, s, h, f, path, rng, n=8):
    if not s["emg_cut"]:                      # no joint staging: nothing contested to show
        return []
    usable = h.hour_ok & ~h.artifact
    src, cut = s["emg_source"], s["emg_cut"]
    dis = usable & (h.stage != h.stage_hmm) & h.stage.isin(["W", "NR", "R"]) & h.stage_hmm.isin(["W", "NR", "R"])
    marked = usable & (h.flag != "")
    pool = np.r_[rng.permutation(np.flatnonzero(dis))[: n - n // 4], rng.permutation(np.flatnonzero(marked & ~dis))[: n // 4]]
    pool = np.sort(pool[(pool >= 2) & (pool < len(h) - 3)])
    if not len(pool):
        return []
    eeg = np.load(rec_arrays / "eeg.npy", mmap_mode="r"); emg = np.load(rec_arrays / "emg.npy", mmap_mode="r")
    sos = butter(4, [0.5, 40], "bandpass", fs=FS, output="sos")
    ss60_sos = np.vstack([butter(2, [20, 90], "bandpass", fs=FS, output="sos"),
                          butter(2, [59, 61], "bandstop", fs=FS, output="sos")])
    eeg_sc = 4 * float(np.median(f.eeg_rms))
    nr_d = float(np.median(np.log10(f.delta_power[h.stage == "NR"])))
    fig, ax = plt.subplots(len(pool), 1, figsize=(16, 2.8 * len(pool)))
    ax = np.atleast_1d(ax); rows = []
    for k, i in enumerate(pool):
        a, b = (i - 2) * EP, (i + 3) * EP
        x = sosfiltfilt(sos, np.asarray(eeg[a - 2000:b + 2000], float))[2000:-2000]
        y = np.asarray(emg[a - 2000:b + 2000], float)
        y = (gap_filter(y) if src == "gap" else sosfiltfilt(ss60_sos, y))[2000:-2000]
        t = np.arange(len(x)) / FS - 8
        # fixed scales for the whole recording: EEG in units of 4x its median rms, EMG in units of 4x the wake cut
        ax[k].plot(t, np.clip(x / eeg_sc, -1.1, 1.1) + 1.2, lw=0.4, color="k")
        ax[k].plot(t, np.clip(y / (4 * cut), -1.1, 1.1) - 1.2, lw=0.4, color="m")
        for j in range(6):
            ax[k].axvline(-8 + 4 * j, color="0.7", lw=0.5)
        ax[k].axvspan(0, 4, color="y", alpha=0.15)
        txt = []
        for j in range(i - 2, i + 3):
            txt.append(f"rule {h.stage[j]} | HMM {h.stage_hmm[j]} {h.flag[j]}\n"
                       f"δ {np.log10(f.delta_power[j]):.2f} (NR med {nr_d:.2f})  θ/δ {f.theta_delta[j]:.2f}  σ {np.log10(f.sigma_power[j]):.2f}\n"
                       f"EMG {f[f"emg_rms_{src}"][j] / cut:.2f}× cut  tone {f[f"emg_tone_{src}"][j] / cut:.2f}× cut")
        for j, tx in enumerate(txt):
            ax[k].text(-8 + 4 * j + 0.05, 3.3, tx, fontsize=7, va="top")
        ax[k].set_ylim(-2.4, 3.4); ax[k].set_yticks([1.2, -1.2], ["EEG", "EMG"]); ax[k].set_xlim(-8, 12)
        ax[k].set_title(f"[{k + 1}] epoch {i + 1}  ({h.t_kst[i]:%H:%M:%S} KST, ZT{h.zt_h[i]:.2f})  rule {h.stage[i]}  HMM {h.stage_hmm[i]}"
                        f"{'  mark ' + h.flag[i] if h.flag[i] else ''}", fontsize=8, loc="left")
        rows.append(dict(mouse=s["mouse"], tp=s["tp"][0], panel=k + 1, epoch=int(i + 1), t_kst=str(h.t_kst[i]),
                         rule=h.stage[i], hmm=h.stage_hmm[i], mark=h.flag[i]))
    fig.suptitle(f"{s['mouse']} {s['tp']}: contested epochs (yellow = the epoch; labels rule/HMM; EMG trace scaled to ±4× the wake cut; "
                 f"δ, σ log10 µV²)", fontsize=9)
    fig.tight_layout(); fig.savefig(path, dpi=80); plt.close(fig)
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("arrays", type=Path); ap.add_argument("epochs", type=Path); ap.add_argument("out", type=Path)
    ap.add_argument("--only", nargs="*")
    a = ap.parse_args(); a.out.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(20261103); rows = []
    for d in sorted(p.parent for p in a.epochs.glob("*/*/*/score.json")):
        if a.only and not any(o in str(d) for o in a.only):
            continue
        s = json.loads((d / "score.json").read_text())
        h = pd.read_parquet(d / "hypnogram.parquet"); f = pd.read_parquet(d / "features.parquet")
        stem = f"{s['mouse']}_{s['tp'][0]}"
        overview(d, s, h, f, np.load(d / "psd_eeg.npy"), a.out / f"{stem}_overview.png")
        rows += contested(d, a.arrays / d.relative_to(a.epochs), s, h, f, a.out / f"{stem}_epochs.png", rng)
        print(stem, flush=True)
    pd.DataFrame(rows).to_csv(a.out / "contested_epochs.csv", index=False)


if __name__ == "__main__":
    main()
