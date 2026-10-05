"""Is the EMG mains notch a VALIDITY gain or only a way to pass? Three tests over every ~/eeg-processed recording.

Context (audit C3): stage 3 stages WAKE by an Otsu cut on log EMG rms (10-124 Hz at the stored 250 Hz), and that rms
includes 60/120 Hz. qc/emg_mains_staging_test.py showed SCOREABLE 44 -> 69 of 100 with the EMG notched. r@1min, the
pass criterion, is the stager's own persistence statistic, so a higher r alone cannot show the staging is more TRUE.
This script asks three questions the notch could fail:
  1. NEGATIVE CONTROL  notch, then shuffle the EMG's 4 s epochs (EEG untouched): r@1min must collapse to ~0 and nothing
                       may pass. A pass here would mean the notched r is manufactured, not measured.
  2. DOSE-RESPONSE     the notch should change staging only where mains is a large, variable part of the EMG measure.
                       mains_share = median over valid epochs of 1 - (rms_notched / rms_orig)^2, on the stager's own
                       band-pass; mains_var = SD of log10(mains power) across epochs (a constant offset cannot move an
                       Otsu cut much; a fluctuating one can). Recordings with ~0 share must not change.
  3. PHYSIOLOGY        mice are nocturnal: within a recording that covers both phases (>= 3 h each in blocks), WAKE %
                       in the dark should exceed WAKE % in the light. The stager never sees the clock, so this is an
                       independent check. Count and median of (dark - light) before and after the notch.
Reuses the orig/notch stage-3 outputs of qc/emg_mains_staging_test.py (OUT/orig, OUT/notch); computes OUT/shuffle_notch.
Nothing is written beside the official files: inputs are symlinked into OUT, as in emg_mains_staging_test.py.
Recordings and mice repeat across day folders, so the n below are recordings, not independent animals.
usage: python3 qc/emg_notch_validation_2026_10_02.py OUT FIGDIR DAY_DIR [DAY_DIR ...]
"""
import csv, glob, hashlib, json, os, sys, textwrap
import numpy as np, scipy.signal as sg, scipy.stats as st
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import pipeline.stage3_features as S3

out_root, FIGD, days = sys.argv[1], sys.argv[2], sys.argv[3:]
real_load = np.load
MIN_PHASE_H = 3.0


class NpzDict(dict):
    @property
    def files(self):
        return list(self.keys())


def notch(emg, fs):
    emg = emg.astype(np.float64)
    for f0 in (60.0, 120.0):                     # identical to qc/emg_mains_staging_test.py
        if f0 < fs / 2 - 2:
            b, a = sg.iirnotch(f0, 30, fs); emg = sg.filtfilt(b, a, emg)
    return emg


def shuffled_notched_load(path, allow_pickle=True, **kw):
    z = real_load(path, allow_pickle=allow_pickle, **kw); d = NpzDict({k: z[k] for k in z.files})
    fs = int(d["fs"]); emg = notch(d["emg"], fs); ep = S3.T.EPOCH_S * fs; n = len(emg) // ep
    rng = np.random.default_rng(int(hashlib.sha256(os.path.basename(path).encode()).hexdigest()[:8], 16))
    E = emg[:n * ep].reshape(n, ep)[rng.permutation(n)]
    d["emg"] = np.concatenate([E.ravel(), emg[n * ep:]]).astype(np.float32)
    return d


def mains_metrics(npz):
    """mains share and variability of the stager's EMG measure, on valid epochs only."""
    z = real_load(npz, allow_pickle=True); fs = int(z["fs"]); ep = S3.T.EPOCH_S * fs
    sos = sg.butter(4, [S3.T.FILT_EMG[0], min(S3.T.FILT_EMG[1], fs / 2 - 1)], btype="band", fs=fs, output="sos")
    raw = z["emg"].astype(np.float64); n = len(raw) // ep
    ok = np.asarray(z["epoch_ok"][:n], bool)
    ro = sg.sosfiltfilt(sos, raw[:n * ep].reshape(n, ep), axis=1).std(1)
    rn = sg.sosfiltfilt(sos, notch(raw, fs)[:n * ep].reshape(n, ep), axis=1).std(1)
    k = ok & (ro > 0)
    if k.sum() < 100:
        return np.nan, np.nan, np.nan
    share = 1 - (rn[k] / ro[k]) ** 2
    mp = np.clip(ro[k] ** 2 - rn[k] ** 2, 1e-6, None)
    return float(np.median(share)), float(np.std(np.log10(mp))), float(np.median(ro[k]))


def feat(cond, day, stem):
    p = os.path.join(out_root, cond, day, stem + "_features.json")
    return json.load(open(p)) if os.path.exists(p) else None


def phase(f, which):
    b = ((f or {}).get("by_light_phase") or {}).get(which) or {}
    return (b.get("hours") or 0.0), b.get("wake_pct")


rows = []
for day in days:
    dname = os.path.basename(os.path.normpath(day))
    od = os.path.join(out_root, "shuffle_notch", dname); os.makedirs(od, exist_ok=True)
    for f in sorted(glob.glob(os.path.join(day, "port*.npz"))):
        stem = os.path.basename(f)[:-4]
        link = os.path.join(od, os.path.basename(f))
        if os.path.lexists(link) and os.path.realpath(link) != os.path.realpath(f):
            sys.exit(f"{link} points to {os.path.realpath(link)}, not {os.path.realpath(f)}: use a fresh OUT")
        if not os.path.lexists(link):
            os.symlink(os.path.realpath(f), link)
        S3.np.load = shuffled_notched_load
        try:
            sh = S3.analyse(link)
        except Exception as exc:                             # noqa: BLE001
            sh = {"verdict": f"ERROR: {exc}", "persistence": {"1min": {"r": None}}, "wake_pct": None}
        finally:
            S3.np.load = real_load
        share, mvar, rms = mains_metrics(f)
        fo, fn = feat("orig", dname, stem), feat("notch", dname, stem)
        r = dict(day=dname, mouse=stem.split("_")[0], file=stem, mains_share=share, mains_logsd=mvar, emg_rms_median_uv=rms,
                 shuffle_verdict=sh["verdict"].split(":")[0], shuffle_r=(sh["persistence"]["1min"] or {}).get("r"))
        for tag, fx in (("orig", fo), ("notch", fn)):
            p = ((fx or {}).get("persistence") or {}).get("1min") or {}
            lh, lw = phase(fx, "light"); dh, dw = phase(fx, "dark")
            r.update({f"{tag}_verdict": (fx or {}).get("verdict", "missing").split(":")[0], f"{tag}_r": p.get("r"),
                      f"{tag}_wake": (fx or {}).get("wake_pct"), f"{tag}_light_h": lh, f"{tag}_light_wake": lw,
                      f"{tag}_dark_h": dh, f"{tag}_dark_wake": dw})
        rows.append(r)
        print(f"{dname:<22}{r['mouse']:<13} share {share:6.3f} logsd {mvar:5.2f} | orig {r['orig_verdict']:<10} {r['orig_r']}"
              f" | notch {r['notch_verdict']:<10} {r['notch_r']} | shuffle {r['shuffle_verdict']:<10} {r['shuffle_r']}", flush=True)

keys = list(rows[0].keys())
with open(os.path.join(out_root, "notch_validation.csv"), "w", newline="") as fh:
    w = csv.DictWriter(fh, fieldnames=keys); w.writeheader(); w.writerows(rows)

fl = lambda v: np.nan if v in (None, "") else float(v)
A = {k: np.array([fl(r[k]) for r in rows]) for k in ("mains_share", "mains_logsd", "orig_r", "notch_r", "shuffle_r", "orig_wake", "notch_wake")}
sO = np.array([r["orig_verdict"] == "SCOREABLE" for r in rows]); sN = np.array([r["notch_verdict"] == "SCOREABLE" for r in rows])
sS = np.array([r["shuffle_verdict"] == "SCOREABLE" for r in rows])
dR, dW = A["notch_r"] - A["orig_r"], A["notch_wake"] - A["orig_wake"]
both_phase = np.array([r["orig_light_h"] >= MIN_PHASE_H and r["orig_dark_h"] >= MIN_PHASE_H and r["orig_light_wake"] is not None
                       and r["orig_dark_wake"] is not None for r in rows])
cO = np.array([fl(r["orig_dark_wake"]) - fl(r["orig_light_wake"]) if b else np.nan for r, b in zip(rows, both_phase)])
cN = np.array([fl(r["notch_dark_wake"]) - fl(r["notch_light_wake"]) if b else np.nan for r, b in zip(rows, both_phase)])
ok = np.isfinite(A["mains_share"]) & np.isfinite(dR)
rho_r = st.spearmanr(A["mains_share"][ok], np.abs(dR[ok])); okw = np.isfinite(A["mains_share"]) & np.isfinite(dW)
rho_w = st.spearmanr(A["mains_share"][okw], np.abs(dW[okw]))
lo = ok & (A["mains_share"] < 0.3)          # 0.05 held no recording on 2026-10-02 (lowest 0.07); below 0.3 the notch should change nothing
summary = dict(
    n=len(rows),
    scoreable=dict(orig=int(sO.sum()), notch=int(sN.sum()), shuffle_notch=int(sS.sum())),
    shuffle_r=dict(median=float(np.nanmedian(A["shuffle_r"])), p95_abs=float(np.nanpercentile(np.abs(A["shuffle_r"]), 95)),
                   max=float(np.nanmax(A["shuffle_r"]))),
    mains_share=dict(median=float(np.nanmedian(A["mains_share"])), p10=float(np.nanpercentile(A["mains_share"], 10)),
                     p90=float(np.nanpercentile(A["mains_share"], 90))),
    dose_response=dict(spearman_share_vs_abs_dr=[float(rho_r.statistic), float(rho_r.pvalue)],
                       spearman_share_vs_abs_dwake=[float(rho_w.statistic), float(rho_w.pvalue)],
                       low_share_lt_0p3=dict(n=int(lo.sum()), median_abs_dr=float(np.nanmedian(np.abs(dR[lo]))) if lo.any() else None,
                                              flips=int((sO[lo] != sN[lo]).sum()))),
    physiology=dict(n_both_phases=int(both_phase.sum()),
                    orig=dict(dark_gt_light=int(np.nansum(cO > 0)), median_dark_minus_light=float(np.nanmedian(cO))),
                    notch=dict(dark_gt_light=int(np.nansum(cN > 0)), median_dark_minus_light=float(np.nanmedian(cN))),
                    scoreable_both=dict(n=int((both_phase & sO & sN).sum()),
                                        orig_median=float(np.nanmedian(cO[both_phase & sO & sN])) if (both_phase & sO & sN).any() else None,
                                        notch_median=float(np.nanmedian(cN[both_phase & sO & sN])) if (both_phase & sO & sN).any() else None)))
json.dump(summary, open(os.path.join(out_root, "notch_validation_summary.json"), "w"), indent=1)
print(json.dumps(summary, indent=1))

fig, ax = plt.subplots(2, 2, figsize=(13, 10))
bins = np.linspace(-0.2, 1.0, 49)
for v, lab, c in ((A["orig_r"], "as published", "0.5"), (A["notch_r"], "EMG notched", "tab:blue"), (A["shuffle_r"], "notched + EMG epochs shuffled", "tab:red")):
    ax[0, 0].hist(v[np.isfinite(v)], bins=bins, histtype="step", lw=1.6, color=c, label=f"{lab} (n {np.isfinite(v).sum()})")
ax[0, 0].axvline(.3, color="k", ls="--", lw=.8); ax[0, 0].set_xlabel("r@1min"); ax[0, 0].set_ylabel("recordings"); ax[0, 0].legend(fontsize=8)
ax[0, 0].set_title(f"1. negative control: shuffled -> SCOREABLE {sS.sum()} of {len(rows)}, median r {summary['shuffle_r']['median']:+.3f}", fontsize=9.5, loc="left")
cc = np.where(sO & sN, "tab:green", np.where(~sO & sN, "tab:orange", np.where(sO & ~sN, "tab:red", "0.6")))
ax[0, 1].scatter(A["mains_share"], dR, c=cc, s=18); ax[0, 1].axhline(0, color="k", lw=.6)
ax[0, 1].set_xlabel("mains share of the stager's EMG measure (median over epochs)"); ax[0, 1].set_ylabel("r@1min change (notched - published)")
ax[0, 1].set_title(f"2. dose-response: Spearman |dr| vs share {rho_r.statistic:+.2f} (orange: REJECT->SCOREABLE)", fontsize=9.5, loc="left")
ax[1, 0].scatter(A["mains_share"], dW, c=cc, s=18); ax[1, 0].axhline(0, color="k", lw=.6)
ax[1, 0].set_xlabel("mains share of the stager's EMG measure"); ax[1, 0].set_ylabel("WAKE % change (notched - published)")
ax[1, 0].set_title(f"   |dWAKE| vs share {rho_w.statistic:+.2f}", fontsize=9.5, loc="left")
ax[1, 1].scatter(cO, cN, c=cc, s=22); lim = [-60, 80]; ax[1, 1].plot(lim, lim, color="k", lw=.5)
ax[1, 1].axhline(0, color="k", lw=.6); ax[1, 1].axvline(0, color="k", lw=.6); ax[1, 1].set_xlim(lim); ax[1, 1].set_ylim(lim)
ax[1, 1].set_xlabel("dark - light WAKE %, as published"); ax[1, 1].set_ylabel("dark - light WAKE %, EMG notched")
ph = summary["physiology"]
ax[1, 1].set_title(f"3. physiology ({ph['n_both_phases']} recordings with both phases): dark > light {ph['orig']['dark_gt_light']} -> "
                   f"{ph['notch']['dark_gt_light']}", fontsize=9.5, loc="left")
for a in ax.flat:
    a.grid(alpha=.25)
fig.suptitle(textwrap.fill(f"Does the EMG mains notch make staging more valid? {len(rows)} animal-recordings in ~/eeg-processed. "
             f"SCOREABLE {sO.sum()} as published, {sN.sum()} notched, {sS.sum()} notched+shuffled. Median dark-light WAKE contrast "
             f"{ph['orig']['median_dark_minus_light']:+.1f} -> {ph['notch']['median_dark_minus_light']:+.1f} points. Diagnostic, not adopted.", 150), fontsize=10)
fig.tight_layout(); fig.savefig(os.path.join(FIGD, "2026-10-02-noise-figP-emg-notch-validation.png"), dpi=105); plt.close(fig)
print("figure P written")
