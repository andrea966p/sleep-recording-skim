"""The four noise-series mice over 24 h: overnight (dark) + light-phase runs of 2026-10-01/02, analysed together.

Runs: overnight allego_0__uid1001-21-00-07 (console cfdf8ebde0c6, 21:00:07 -> 09:02:02) and light phase
allego_0__uid1002-09-16-58 (8f84e3e62af6, 09:16:58 -> 21:02:02). Same four mice, nothing touched between the runs.
  A1 A/1 A/2    EMG OPEN (implant side)  -> EEG only: spectral description, never staged
  A2 A/33 A/34  EEG + EMG
  B1 B/1 B/2    EEG + EMG
  B2 B/33 B/34  EMG OPEN                 -> EEG only
What is computed, and from what (no raw read except via the QC bundles already on disk):
  1. staging table   OFFICIAL = pipeline stages 2-3 unchanged, stage-1 gate (official-noise-tests/processed);
                     DIAGNOSTIC orig/notch = the same stage 3 on the --all-verdicts split, as published and with the
                     EMG's 60/120 Hz notched in memory (qc/emg_mains_staging_test.py). The ladder verdict is separate.
  2. hourly table    per clock hour: wake % of in-block epochs (REM is folded into SLEEP: REM % is constructed by
                     the stager and is never reported), EEG delta (1-4 Hz) median over all epochs and over NREM epochs,
                     and the hum the QC gate sees (10 s epochs from the run's QC bundle): chip floor, EEG and EMG 60 Hz.
  3. disturbance     wake % inside each disturbed window of the canonical markers vs the rest of the light phase.
Epoch statistics are autocorrelated, so nothing here is a significance test; n = 2 staged mice, 4 EEGs.
usage: python3 qc/noise_mice_24h_2026_10_02.py OUTDIR FIGDIR
"""
import csv, glob, json, os, sys, textwrap, datetime as dt
import numpy as np
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt, matplotlib.dates as mdates

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import noise_mice_markers_2026_10_02 as MK

OUT, FIGD = sys.argv[1], sys.argv[2]; os.makedirs(OUT, exist_ok=True)
D = os.path.expanduser("~/radix/noise-tests/2026-10-02")
CACHE = os.path.expanduser(os.environ.get("EEG_CACHE_ROOT", "~/eeg-qc-cache"))
RUN = {"overnight": dict(base=MK.RUNS["overnight"], day="2026-10-01", diag="diag-emgtest-overnight"),
       "lightphase": dict(base=MK.RUNS["lightphase"], day="2026-10-02", diag="diag-emgtest-lightphase")}
MICE = {"A1": ("A", 1, "portA-slot1", False), "A2": ("A", 33, "portA-slot2", True),
        "B1": ("B", 1, "portB-slot1", True), "B2": ("B", 33, "portB-slot2", False)}   # True = EEG + EMG
COL = {"A1": "0.45", "A2": "tab:blue", "B1": "tab:red", "B2": "tab:purple"}
for r in RUN.values():
    r["t0"], r["fs"], r["n"], _ = MK.file_origin(r["base"])
LIGHTS_ON = MK.clock("2026-10-02 08:59:51.0"); LIGHTS_OFF = MK.clock("2026-10-02 21:01:11.5")


def one(pattern):
    hits = sorted(glob.glob(pattern))
    return hits[0] if len(hits) == 1 else None


def stage3(run, pos, cond):
    """features.json + hypnogram rows for one condition: official | orig | notch. None if not produced."""
    r = RUN[run]
    root = (os.path.join(D, "official-noise-tests", "processed", r["day"]) if cond == "official"
            else os.path.join(D, r["diag"], cond, r["day"]))
    f = one(os.path.join(root, f"{pos}_*_features.json")); h = one(os.path.join(root, f"{pos}_*_hypnogram.csv"))
    if not (f and h):
        return None
    feat = json.load(open(f))
    hyp = np.genfromtxt(h, delimiter=",", names=True, dtype=None, encoding=None)
    return feat, hyp


# ---- 1. staging table ------------------------------------------------------------------------------------------
rows = []
for m, (port, site, pos, staged) in MICE.items():
    for run in RUN:
        for cond in ("official", "orig", "notch"):
            s = stage3(run, pos, cond)
            if s is None:
                rows.append(dict(mouse=m, run=run, condition=cond, verdict="not produced (stage 1: EMG OPEN)" if cond == "official" else "missing"))
                continue
            f, _ = s; bl = f.get("by_light_phase") or {}
            p = (f.get("persistence") or {}).get("1min") or {}
            rows.append(dict(mouse=m, run=run, condition=cond, verdict=f["verdict"].split(":")[0], why=f["verdict"],
                             r_1min=p.get("r"), r_1min_shuffled=p.get("shuffled"), wake_pct=f.get("wake_pct"),
                             nrem_pct=f.get("nrem_pct"), hours_in_blocks=f.get("hours_in_blocks"),
                             light_h=(bl.get("light") or {}).get("hours"), light_wake_pct=(bl.get("light") or {}).get("wake_pct"),
                             dark_h=(bl.get("dark") or {}).get("hours"), dark_wake_pct=(bl.get("dark") or {}).get("wake_pct")))
keys = ["mouse", "run", "condition", "verdict", "r_1min", "r_1min_shuffled", "wake_pct", "nrem_pct", "hours_in_blocks",
        "light_h", "light_wake_pct", "dark_h", "dark_wake_pct", "why"]
with open(os.path.join(OUT, "staging_summary.csv"), "w", newline="") as fh:
    w = csv.DictWriter(fh, fieldnames=keys); w.writeheader(); [w.writerow({k: r.get(k, "") for k in keys}) for r in rows]
print("STAGING (official = unchanged pipeline on the stage-1 gate; orig/notch = diagnostic, QC bypassed)")
for r in rows:
    if r["mouse"] in ("A2", "B1"):
        print(f"  {r['mouse']} {r['run']:<10} {r['condition']:<8} {r['verdict']:<11} r@1min {r.get('r_1min')}  wake {r.get('wake_pct')} %"
              f"  (shuffled r {r.get('r_1min_shuffled')})")

# ---- 2. per-epoch series on a common clock -------------------------------------------------------------------------
def epochs(run, pos, cond):
    s = stage3(run, pos, cond)
    if s is None:
        return None
    _, h = s; t0 = RUN[run]["t0"]
    t = np.array([t0 + dt.timedelta(seconds=float(x) + 2.0) for x in h["t_s"]])     # 4 s epochs, centre
    return dict(t=t, state=np.asarray(h["state"]).astype(str), in_block=np.asarray(h["in_block"]).astype(bool),
                delta=np.asarray(h["delta"], float), theta_delta=np.asarray(h["theta_delta"], float),
                emg=np.asarray(h["emg_rms_uv"], float))

def cat(pos, cond):
    parts = [epochs(run, pos, cond) for run in RUN]
    parts = [p for p in parts if p is not None]
    return {k: np.concatenate([p[k] for p in parts]) for k in parts[0]} if parts else None

def bundle(run):
    z = np.load(os.path.join(CACHE, RUN[run]["base"] + ".npz"), allow_pickle=True)
    sites = [str(x) for x in z["sites"]]; ix = {s: i for i, s in enumerate(sites)}; es = float(z["epoch_s"])
    t0 = RUN[run]["t0"]; t = np.array([t0 + dt.timedelta(seconds=(k + .5) * es) for k in range(z["hum"].shape[0])])
    out = dict(t=t)
    for m, (port, site, _, _) in MICE.items():
        out[f"{m}_floor"] = np.median(z["hum"][:, [ix[f"{port}/{q}"] for q in range(site + 2, site + 16)]], 1)
        out[f"{m}_eeg60"] = z["hum"][:, ix[f"{port}/{site}"]]; out[f"{m}_emg60"] = z["hum"][:, ix[f"{port}/{site + 1}"]]
        out[f"{m}_emg_rail"] = z["rail"][:, ix[f"{port}/{site + 1}"]]
    return out

Q = [bundle(run) for run in RUN]; Q = {k: np.concatenate([q[k] for q in Q]) for k in Q[0]}
E = {m: {c: cat(pos, c) for c in ("orig", "notch")} for m, (_, _, pos, _) in MICE.items()}

start = RUN["overnight"]["t0"].replace(minute=0, second=0, microsecond=0)
hours = [start + dt.timedelta(hours=k) for k in range(25)]
def in_hour(t, h0):
    return (t >= h0) & (t < h0 + dt.timedelta(hours=1))
hrows = []
for h0 in hours[:-1]:
    lit = LIGHTS_ON <= h0 + dt.timedelta(minutes=30) < LIGHTS_OFF
    for m, (_, _, pos, staged) in MICE.items():
        row = dict(hour_start_kst=h0.strftime("%Y-%m-%d %H:%M"), light=int(lit), mouse=m)
        qm = in_hour(Q["t"], h0)
        row.update(floor60_uv=round(float(np.median(Q[f"{m}_floor"][qm])), 1) if qm.any() else "",
                   eeg60_uv=round(float(np.median(Q[f"{m}_eeg60"][qm])), 2) if qm.any() else "",
                   emg60_uv=round(float(np.median(Q[f"{m}_emg60"][qm])), 2) if qm.any() else "")
        for c in ("orig", "notch"):
            e = E[m][c]
            if e is None:
                continue
            k = in_hour(e["t"], h0)
            if c == "orig":
                ok = k & np.isfinite(e["delta"]) & (e["delta"] > 0)
                row["eeg_delta_median"] = round(float(np.median(e["delta"][ok])), 1) if ok.any() else ""
                nr = ok & (e["state"] == "NREM") & e["in_block"]
                row["eeg_delta_nrem_median"] = round(float(np.median(e["delta"][nr])), 1) if nr.sum() >= 30 else ""
            if staged:
                b = k & e["in_block"] & np.isin(e["state"], ["WAKE", "NREM", "REM"])
                row[f"n_epochs_{c}"] = int(b.sum())
                row[f"wake_pct_{c}"] = round(100 * float((e["state"][b] == "WAKE").mean()), 1) if b.sum() >= 150 else ""
        hrows.append(row)
hk = ["hour_start_kst", "light", "mouse", "n_epochs_orig", "wake_pct_orig", "n_epochs_notch", "wake_pct_notch",
      "eeg_delta_median", "eeg_delta_nrem_median", "floor60_uv", "eeg60_uv", "emg60_uv"]
with open(os.path.join(OUT, "hourly.csv"), "w", newline="") as fh:
    w = csv.DictWriter(fh, fieldnames=hk); w.writeheader(); [w.writerow({k: r.get(k, "") for k in hk}) for r in hrows]

# light vs dark summaries
print("\nLIGHT vs DARK (medians of hourly values; dark = 21:00-09:00, light = 09:00-21:00)")
summ = {}
for m in MICE:
    hr = [r for r in hrows if r["mouse"] == m]
    def med(key, lit):
        v = [float(r[key]) for r in hr if r["light"] == lit and r.get(key, "") != ""]
        return (float(np.median(v)), len(v)) if v else (np.nan, 0)
    d = {k: (med(k, 0), med(k, 1)) for k in ("wake_pct_orig", "wake_pct_notch", "eeg_delta_median", "eeg_delta_nrem_median",
                                              "floor60_uv", "eeg60_uv", "emg60_uv")}
    summ[m] = d
    print(f"  {m}: " + "; ".join(f"{k} dark {v[0][0]:.1f} (n {v[0][1]}) light {v[1][0]:.1f} (n {v[1][1]})" for k, v in d.items() if v[0][1] or v[1][1]))
with open(os.path.join(OUT, "light_dark_summary.json"), "w") as fh:
    json.dump({m: {k: dict(dark=v[0][0], dark_hours=v[0][1], light=v[1][0], light_hours=v[1][1]) for k, v in d.items()}
               for m, d in summ.items()}, fh, indent=1, default=float)

# ---- 3. disturbance windows -----------------------------------------------------------------------------------------
print("\nDISTURBANCE (light phase): wake % of in-block epochs inside each window vs the rest of the light phase")
drows = []
win = [(RUN["lightphase"]["t0"] + dt.timedelta(seconds=a), RUN["lightphase"]["t0"] + dt.timedelta(seconds=b), lab)
       for a, b, lab in MK.disturbed("lightphase")]
for m in ("A2", "B1"):
    for c in ("orig", "notch"):
        e = E[m][c]; lp = e["t"] >= RUN["lightphase"]["t0"]
        sc = e["in_block"] & np.isin(e["state"], ["WAKE", "NREM", "REM"])
        anyw = np.zeros(len(e["t"]), bool)
        for a, b, lab in win:
            k = lp & sc & (e["t"] >= a) & (e["t"] < b); anyw |= (e["t"] >= a) & (e["t"] < b)
            hb = lp & sc & (e["t"] >= a - dt.timedelta(hours=1)) & (e["t"] < a)
            drows.append(dict(mouse=m, condition=c, window=lab, start=a.strftime("%H:%M:%S"), end=b.strftime("%H:%M:%S"),
                              n_epochs=int(k.sum()), wake_pct=round(100 * float((e["state"][k] == "WAKE").mean()), 1) if k.any() else "",
                              wake_pct_hour_before=round(100 * float((e["state"][hb] == "WAKE").mean()), 1) if hb.any() else ""))
        rest = lp & sc & ~anyw & (e["t"] < LIGHTS_OFF)
        drows.append(dict(mouse=m, condition=c, window="rest of the light phase (09:17-21:01, windows excluded)",
                          n_epochs=int(rest.sum()), wake_pct=round(100 * float((e["state"][rest] == "WAKE").mean()), 1)))
dk = ["mouse", "condition", "window", "start", "end", "n_epochs", "wake_pct", "wake_pct_hour_before"]
with open(os.path.join(OUT, "disturbance.csv"), "w", newline="") as fh:
    w = csv.DictWriter(fh, fieldnames=dk); w.writeheader(); [w.writerow({k: r.get(k, "") for k in dk}) for r in drows]
for r in drows:
    print(f"  {r['mouse']} {r['condition']:<6} {r['window'][:44]:<44} wake {r['wake_pct']} % (n {r['n_epochs']})"
          + (f", hour before {r['wake_pct_hour_before']} %" if r.get("wake_pct_hour_before", "") != "" else ""))

# ---- figures ---------------------------------------------------------------------------------------------------------
mk = MK.rows("overnight") + MK.rows("lightphase")
def decorate(a, legend=True):
    a.axvspan(RUN["overnight"]["t0"], LIGHTS_ON, color="0.85", zorder=0)            # dark phase
    a.axvspan(LIGHTS_OFF, RUN["lightphase"]["t0"] + dt.timedelta(seconds=RUN["lightphase"]["n"] / RUN["lightphase"]["fs"]), color="0.85", zorder=0)
    a.axvspan(RUN["overnight"]["t0"] + dt.timedelta(seconds=RUN["overnight"]["n"] / RUN["overnight"]["fs"]), RUN["lightphase"]["t0"],
              color="w", hatch="//", ec="0.6", lw=0, zorder=0)                        # gap between the files
    for a0, b0, lab in win:
        a.axvspan(a0, b0, color="tab:orange", alpha=.25, zorder=1)
    for r in mk:
        if r["kind"] == "system":
            a.axvline(MK.clock(r["clock_kst"]), color="tab:green", lw=.7, ls=":", zorder=1)
    a.grid(alpha=.25); a.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M", tz=MK.KST))   # aware times: label in KST, not UTC
    if legend:
        a.legend(fontsize=7.5, ncol=4, loc="upper left")

# M: quality over 24 h
fig, ax = plt.subplots(3, 1, figsize=(15, 10), sharex=True)
hc = [h0 + dt.timedelta(minutes=30) for h0 in hours[:-1]]
def hourly(key):
    return np.array([np.median(Q[key][in_hour(Q["t"], h0)]) if in_hour(Q["t"], h0).any() else np.nan for h0 in hours[:-1]])
for m in MICE:
    ax[0].plot(Q["t"], Q[f"{m}_floor"], ",", color=COL[m], alpha=.35); ax[0].plot(hc, hourly(f"{m}_floor"), "o-", ms=3, color=COL[m], label=f"{m} chip floor")
    ax[1].plot(Q["t"], Q[f"{m}_eeg60"], ",", color=COL[m], alpha=.35); ax[1].plot(hc, hourly(f"{m}_eeg60"), "o-", ms=3, color=COL[m], label=f"{m} EEG")
for m in ("A2", "B1"):
    ax[2].plot(Q["t"], Q[f"{m}_emg60"], ",", color=COL[m], alpha=.35); ax[2].plot(hc, hourly(f"{m}_emg60"), "o-", ms=3, color=COL[m], label=f"{m} EMG")
ax[0].axhline(800, color="k", ls="--", lw=.9); ax[0].text(hours[0], 820, " QC gate 800 uV", fontsize=8, va="bottom")
for a_, lab in zip(ax, ["chip floor, 60 Hz line\n(uV peak, QC gate scale)", "EEG 60 Hz line (uV peak)", "EMG 60 Hz line (uV peak)\n(A1, B2 EMG open: mV, not shown)"]):
    a_.set_yscale("log"); a_.set_ylabel(lab); decorate(a_)
ax[0].set_title("10 s epochs (dots) and hourly medians (lines). Grey = dark phase; hatched = 15 min between the files; orange = disturbed "
                "windows; green dotted = system-wide floor events", loc="left", fontsize=9)
ax[2].set_xlabel("clock time KST, 2026-10-01 21:00 -> 10-02 21:02")
b1 = summ["B1"]["floor60_uv"]; a2 = summ["A2"]["emg60_uv"]
fig.suptitle(f"Noise-series mice, signal quality over 24 h as the QC gate sees it. B1's floor: dark {b1[0][0]:.0f} -> light {b1[1][0]:.0f} uV "
             f"(hourly medians; the gate is 800). A2's EMG mains: dark {a2[0][0]:.1f} -> light {a2[1][0]:.1f} uV", fontsize=10.5)
fig.tight_layout(); fig.savefig(os.path.join(FIGD, "2026-10-02-noise-figM-24h-signal-quality.png"), dpi=105); plt.close(fig)

# N: sleep-wake over 24 h (A2, B1), orig vs EMG-notched
fig, ax = plt.subplots(3, 1, figsize=(15, 9.5), sharex=True, gridspec_kw=dict(height_ratios=[1, 1, 1.6]))
for i, m in enumerate(("A2", "B1")):
    for j, (c, y) in enumerate((("orig", 1.0), ("notch", 0.0))):
        e = E[m][c]; ok = e["in_block"] & np.isin(e["state"], ["WAKE", "NREM", "REM"])
        wake = ok & (e["state"] == "WAKE"); slp = ok & ~wake
        ax[i].scatter(e["t"][wake], np.full(wake.sum(), y + .25), marker="|", s=40, lw=.4, color="tab:orange")
        ax[i].scatter(e["t"][slp], np.full(slp.sum(), y - .1), marker="|", s=40, lw=.4, color="tab:blue")
    ax[i].set_yticks([1.1, 0.1]); ax[i].set_yticklabels(["as published", "EMG notched"]); ax[i].set_ylim(-.5, 1.6)
    ax[i].set_ylabel(f"{m}\n(orange WAKE,\nblue SLEEP)"); decorate(ax[i], legend=False)
    for c, ls in (("orig", "--"), ("notch", "-")):
        v = [float(r[f"wake_pct_{c}"]) if r.get(f"wake_pct_{c}", "") != "" else np.nan for r in hrows if r["mouse"] == m]
        ax[2].plot(hc, v, ls, marker="o", ms=3, color=COL[m], label=f"{m} {'as published' if c == 'orig' else 'EMG notched'}")
ax[2].set_ylabel("WAKE % per hour\n(in-block epochs)"); ax[2].set_ylim(0, 100); decorate(ax[2])
ax[2].set_xlabel("clock time KST, 2026-10-01 21:00 -> 10-02 21:02")
sw = {m: {c: summ[m][f"wake_pct_{c}"] for c in ("orig", "notch")} for m in ("A2", "B1")}
fig.suptitle(textwrap.fill("Sleep-wake of the two staged mice over 24 h (DIAGNOSTIC staging, QC bypassed). Hourly WAKE %, dark vs light (median of hours): "
             + "; ".join(f"{m} as published {sw[m]['orig'][0][0]:.0f} vs {sw[m]['orig'][1][0]:.0f}, notched {sw[m]['notch'][0][0]:.0f} vs "
                         f"{sw[m]['notch'][1][0]:.0f}" for m in sw), 170), fontsize=10)
fig.tight_layout(); fig.savefig(os.path.join(FIGD, "2026-10-02-noise-figN-24h-sleep-wake.png"), dpi=105); plt.close(fig)

# O: EEG delta over 24 h, all four mice (EEG-only description for A1, B2)
fig, ax = plt.subplots(2, 1, figsize=(15, 8), sharex=True)
for m in MICE:
    v = np.array([float(r["eeg_delta_median"]) if r.get("eeg_delta_median", "") != "" else np.nan for r in hrows if r["mouse"] == m])
    ax[0].plot(hc, v / np.nanmedian(v), "o-", ms=3, color=COL[m], label=f"{m}" + (" (EEG only)" if not MICE[m][3] else ""))
for m in ("A2", "B1"):
    v = np.array([float(r["eeg_delta_nrem_median"]) if r.get("eeg_delta_nrem_median", "") != "" else np.nan for r in hrows if r["mouse"] == m])
    ax[1].plot(hc, v / np.nanmedian(v), "o-", ms=3, color=COL[m], label=f"{m} NREM epochs (as published)")
ax[0].set_ylabel("EEG delta 1-4 Hz, all epochs\n(hourly median / mouse's median)"); ax[1].set_ylabel("EEG delta in NREM\n(hourly median / mouse's median)")
for a_ in ax:
    a_.set_yscale("log"); decorate(a_)
ax[1].set_xlabel("clock time KST, 2026-10-01 21:00 -> 10-02 21:02")
rat = {m: summ[m]["eeg_delta_median"][1][0] / summ[m]["eeg_delta_median"][0][0] for m in MICE}
fig.suptitle("EEG slow-wave power over 24 h, all four mice. Light / dark ratio of hourly delta medians: "
             + ", ".join(f"{m} {rat[m]:.2f}" for m in MICE) + "  (A1, B2: EEG only, their EMG is open)", fontsize=10.5)
fig.tight_layout(); fig.savefig(os.path.join(FIGD, "2026-10-02-noise-figO-24h-eeg-delta.png"), dpi=105); plt.close(fig)
print("\nwritten:", ", ".join(sorted(os.listdir(OUT))), "+ figures M, N, O")
