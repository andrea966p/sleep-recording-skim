#!/usr/bin/env python3
"""STAGE 3 -- sleep staging and features, from the per-mouse files of stage 2.

Emits, per mouse:
    *_hypnogram.csv   epoch, t_s, ZT, light, state, EEG rms, delta, theta,
                      theta/delta, EMG rms, in_block
    *_features.json   architecture, bouts, persistence, physiology, ZT split
    *_summary.txt     the same, readable

Staging
    WAKE  high EMG -- Otsu split of log EMG rms, computed PER ANIMAL
    NREM  low EMG, low theta/delta
    REM   low EMG, high theta/delta

READ THIS BEFORE QUOTING ANY NUMBER
    The REM share is FIXED BY CONSTRUCTION. REM is defined as the top 20% of
    theta/delta among non-wake epochs, so its percentage is an artefact of the
    rule and not a measurement. The field is named rem_pct_CONSTRUCTED. What IS
    evidence is REM's ORDER: REM should be entered from NREM, not from wake.

    Persistence is computed WITHIN unbroken contact blocks only. Computing it
    across gaps is the bug that on 2026-08-03 produced both the project's
    largest false positive (+0.854 on 39 min of pure wake) and a false negative
    (+0.078 on data that could not possibly have passed).

Usage
    python3 stage3_features.py <day_dir_or_npz> [...]
"""
import argparse
import csv
import glob
import json
import os
import sys

import numpy as np
import scipy.signal as sg

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import qc_thresholds as T
import pipeline_common as P

WAKE, NREM, REM = 0, 1, 2
NAMES = {WAKE: "WAKE", NREM: "NREM", REM: "REM"}


# ---------------------------------------------------------------------------
def epoch_features(eeg, emg, fs):
    """Per-epoch band powers and amplitudes from the decimated signals."""
    n = int(len(eeg) // (fs * T.EPOCH_S))
    E = eeg[:n * fs * T.EPOCH_S].reshape(n, fs * T.EPOCH_S)
    M = emg[:n * fs * T.EPOCH_S].reshape(n, fs * T.EPOCH_S)

    sos_e = sg.butter(4, list(T.FILT_EEG), btype="band", fs=fs, output="sos")
    sos_m = sg.butter(4, [T.FILT_EMG[0], min(T.FILT_EMG[1], fs / 2 - 1)],
                      btype="band", fs=fs, output="sos")
    Ef = sg.sosfiltfilt(sos_e, E, axis=1)
    Mf = sg.sosfiltfilt(sos_m, M, axis=1)

    nper = min(T.NPERSEG, fs * T.EPOCH_S)
    fr, Pxx = sg.welch(Ef, fs, nperseg=nper, axis=1)
    bp = lambda lo, hi: np.trapz(Pxx[:, (fr >= lo) & (fr < hi)],
                                 fr[(fr >= lo) & (fr < hi)], axis=1)
    return dict(n=n,
                eeg_rms=Ef.std(1), emg_rms=Mf.std(1),
                delta=bp(*T.BAND_DELTA), theta=bp(*T.BAND_THETA),
                total=bp(*T.BAND_TOTAL))


def stage(f, ok):
    """Assign WAKE / NREM / REM. Thresholds are derived PER ANIMAL."""
    lab = np.full(f["n"], -1, dtype=int)
    idx = np.where(ok[:f["n"]])[0]
    if len(idx) == 0:
        return lab, {}, lab.copy()
    le = np.log10(np.clip(f["emg_rms"][idx], 1e-6, None))
    td = np.log10(np.clip(f["theta"][idx] / np.clip(f["delta"][idx], 1e-12, None),
                          1e-6, None))
    emg_thr = P.otsu_threshold(le)
    wake = le >= emg_thr
    td_thr = np.percentile(td, 80)          # <- fixes REM share by construction
    lab[idx] = np.where(wake, WAKE, np.where(td < td_thr, NREM, REM))

    # Second, INDEPENDENT REM cut: Otsu on theta/delta among non-wake epochs.
    # The percentile rule above forces REM to 20% of sleep; the literature value
    # for mice is <10%, so that rule cannot produce a reportable REM share.
    # Otsu finds the split the data supports, so rem_pct_otsu IS measurable.
    lab_otsu = lab.copy()
    nw = idx[~wake]
    if len(nw) >= 50:
        td_nw = td[~wake]
        td_thr_otsu = P.otsu_threshold(td_nw)
        lab_otsu[nw] = np.where(td_nw < td_thr_otsu, NREM, REM)
    else:
        td_thr_otsu = float("nan")
    return lab, dict(emg_otsu_log10=float(emg_thr),
                     theta_delta_p80_log10=float(td_thr),
                     theta_delta_otsu_log10=float(td_thr_otsu)), lab_otsu


def physiology(f, lab, ok):
    """Do the three states behave like WAKE, NREM and REM should?

    If they do not, the clustering found something other than sleep and no
    architecture number from it is meaningful.
    """
    idx = np.where(ok[:f["n"]] & (lab >= 0))[0]
    out = {}
    for v, nm in NAMES.items():
        m = idx[lab[idx] == v]
        if len(m) == 0:
            out[nm] = None
            continue
        out[nm] = dict(
            n_epochs=int(len(m)),
            emg_rms=float(np.median(f["emg_rms"][m])),
            eeg_rms=float(np.median(f["eeg_rms"][m])),
            delta_pct=float(np.median(100 * f["delta"][m]
                                      / np.clip(f["total"][m], 1e-12, None))),
            theta_delta=float(np.median(f["theta"][m]
                                        / np.clip(f["delta"][m], 1e-12, None))))
    checks, ok_all = {}, True
    have = all(out.get(k) for k in ("WAKE", "NREM", "REM"))
    if have:
        checks["wake_has_highest_emg"] = (
            out["WAKE"]["emg_rms"] > out["NREM"]["emg_rms"]
            and out["WAKE"]["emg_rms"] > out["REM"]["emg_rms"])
        checks["nrem_has_most_delta"] = (
            out["NREM"]["delta_pct"] > out["WAKE"]["delta_pct"]
            and out["NREM"]["delta_pct"] > out["REM"]["delta_pct"])
        checks["nrem_largest_amplitude"] = (
            out["NREM"]["eeg_rms"] >= out["REM"]["eeg_rms"])
        checks["rem_highest_theta_delta"] = (
            out["REM"]["theta_delta"] > out["NREM"]["theta_delta"]
            and out["REM"]["theta_delta"] > out["WAKE"]["theta_delta"])
        checks["rem_emg_low"] = out["REM"]["emg_rms"] < out["WAKE"]["emg_rms"]
        ok_all = all(checks.values())
    else:
        ok_all = False
    return out, checks, bool(ok_all)


def rem_entry_order(lab, blocks):
    """REM should be entered from NREM. Counted WITHIN blocks only."""
    from_n = tot = 0
    for a, b in blocks:
        seg = lab[a:b]
        for k in range(1, len(seg)):
            if seg[k] == REM and seg[k - 1] != REM:
                tot += 1
                if seg[k - 1] == NREM:
                    from_n += 1
    return from_n, tot, (100.0 * from_n / tot if tot else float("nan"))


# ---------------------------------------------------------------------------
def analyse(npz_path):
    z = np.load(npz_path, allow_pickle=True)
    meta = json.loads(str(z["meta"]))
    fs = int(z["fs"])
    eeg, emg = z["eeg"], z["emg"]
    ok = z["epoch_ok"]
    blocks = [tuple(map(int, b)) for b in z["blocks"]]
    zt = z["zt"]

    f = epoch_features(eeg, emg, fs)
    n = f["n"]
    ok = ok[:n]
    blocks = [(a, min(b, n)) for a, b in blocks if a < n and min(b, n) - a >= T.MIN_BLOCK]
    lab, thr, lab_otsu = stage(f, ok)

    in_block = np.zeros(n, dtype=bool)
    for a, b in blocks:
        in_block[a:b] = True

    sel = in_block & (lab >= 0)
    counts = {NAMES[v]: int((lab[sel] == v).sum()) for v in NAMES}
    tot_ep = max(int(sel.sum()), 1)

    sleep = ((lab == NREM) | (lab == REM)).astype(float)
    pers = {}
    for name, sec in (("1min", 60), ("5min", 300), ("10min", 600)):
        lg = sec // T.EPOCH_S
        bl = [(a, b) for a, b in blocks if (b - a) >= 2 * lg + 1]
        r, pairs, used, shuf = P.within_block_persistence(sleep, bl, lag=lg)
        pers[name] = dict(r=None if np.isnan(r) else round(float(r), 3),
                          shuffled=None if np.isnan(shuf) else round(float(shuf), 3),
                          pairs=int(pairs), blocks=int(used))

    phys, checks, phys_ok = physiology(f, lab, sel)
    rn, rt, rpct = rem_entry_order(lab, blocks)

    # measured (not constructed) REM share, and REM as a fraction of sleep --
    # literature for mice is REM < 10% of total sleep
    n_sleep_otsu = int(((lab_otsu[sel] == NREM) | (lab_otsu[sel] == REM)).sum())
    n_rem_otsu = int((lab_otsu[sel] == REM).sum())
    rem_measured = dict(
        rem_pct_of_recording=round(100 * n_rem_otsu / tot_ep, 1),
        rem_pct_of_sleep=round(100 * n_rem_otsu / n_sleep_otsu, 1)
        if n_sleep_otsu else None,
        nrem_pct=round(100 * float((lab_otsu[sel] == NREM).sum()) / tot_ep, 1),
        method="Otsu split of log theta/delta among non-wake epochs",
        literature_rem_pct_of_sleep="<10 for mouse")

    bt = {}
    for v, nm in NAMES.items():
        lens = np.concatenate([P.bout_lengths(lab[a:b], v) for a, b in blocks]) \
            if blocks else np.array([], dtype=int)
        bt[nm] = dict(n=int(len(lens)),
                      median_s=int(np.median(lens) * T.EPOCH_S) if len(lens) else 0,
                      mean_s=round(float(lens.mean() * T.EPOCH_S), 1) if len(lens) else 0.0,
                      max_s=int(lens.max() * T.EPOCH_S) if len(lens) else 0)

    # light vs dark, now that the cycle is known (ZT0 = 09:00 KST)
    lt = P.is_light(zt[:n])
    phase = {}
    for nm, m in (("light", lt & sel), ("dark", (~lt) & sel)):
        if m.sum() < T.MIN_BLOCK:
            phase[nm] = None
            continue
        phase[nm] = dict(
            hours=round(float(m.sum() * T.EPOCH_S / 3600), 2),
            wake_pct=round(100 * float((lab[m] == WAKE).mean()), 1),
            nrem_pct=round(100 * float((lab[m] == NREM).mean()), 1),
            rem_pct_CONSTRUCTED=round(100 * float((lab[m] == REM).mean()), 1))

    wake_pct = 100 * counts["WAKE"] / tot_ep
    r1 = pers["1min"]["r"]
    reasons = []
    if sel.sum() * T.EPOCH_S / 60 < T.MIN_BLOCK_MINUTES:
        reasons.append(f"only {sel.sum() * T.EPOCH_S / 60:.1f} min in blocks")
    if r1 is None or r1 <= T.R_THRESH:
        reasons.append(f"within-block r@1min={r1} <= {T.R_THRESH}")
    if not phys_ok:
        failed = [k for k, v in checks.items() if not v] or ["states missing"]
        reasons.append("physiology FAIL: " + ", ".join(failed))
    if not (T.WAKE_LO <= wake_pct <= T.WAKE_HI):
        reasons.append(f"implausible wake {wake_pct:.1f}%")
    verdict = "SCOREABLE" if not reasons else "REJECT: " + "; ".join(reasons)

    res = dict(
        file=os.path.basename(npz_path), port=meta["port"], slot=meta["slot"],
        name=meta["name"], day=meta["day"], start_local=meta["start_local"],
        recording=meta["recording"], qc_verdict=meta["qc"]["verdict"],
        verdict=verdict,
        epochs_in_blocks=int(sel.sum()),
        hours_in_blocks=round(float(sel.sum() * T.EPOCH_S / 3600), 3),
        n_blocks=len(blocks),
        longest_block_min=round(max((b - a for a, b in blocks), default=0)
                                * T.EPOCH_S / 60, 1),
        wake_pct=round(wake_pct, 1),
        nrem_pct=round(100 * counts["NREM"] / tot_ep, 1),
        rem_pct_CONSTRUCTED=round(100 * counts["REM"] / tot_ep, 1),
        rem_measured=rem_measured,
        persistence=pers, thresholds_used=thr,
        physiology=phys, physiology_checks=checks, physiology_pass=phys_ok,
        rem_entries=int(rt), rem_from_nrem=int(rn),
        rem_from_nrem_pct=None if np.isnan(rpct) else round(float(rpct), 1),
        bouts=bt, by_light_phase=phase,
        light_cycle=f"on {T.LIGHTS_ON_HOUR:02d}:00 / off {T.LIGHTS_OFF_HOUR:02d}:00 KST",
        pipeline_version="2026-08-03")

    stem = npz_path[:-4]
    with open(stem + "_hypnogram.csv", "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["epoch", "t_s", "zt_h", "light", "state", "eeg_rms_uv",
                    "delta", "theta", "theta_delta", "emg_rms_uv", "in_block"])
        for k in range(n):
            w.writerow([k, k * T.EPOCH_S, round(float(zt[k]), 4),
                        int(lt[k]), NAMES.get(int(lab[k]), "EXCLUDED"),
                        round(float(f["eeg_rms"][k]), 2),
                        f"{f['delta'][k]:.4g}", f"{f['theta'][k]:.4g}",
                        f"{f['theta'][k] / max(f['delta'][k], 1e-12):.4g}",
                        round(float(f["emg_rms"][k]), 2), int(in_block[k])])
    json.dump(res, open(stem + "_features.json", "w"), indent=1, default=P.jsafe)
    open(stem + "_summary.txt", "w").write(_summary(res))
    return res


def _summary(r):
    L = [f"{r['name']}  (port {r['port']}, slot {r['slot']})  {r['day']}",
         "=" * 70,
         f"source recording   {r['recording']}",
         f"start (local)      {r['start_local']}",
         f"light cycle        {r['light_cycle']}",
         f"stage 1 QC         {r['qc_verdict']}",
         f"VERDICT            {r['verdict']}",
         "",
         f"usable in blocks   {r['hours_in_blocks']:.2f} h in {r['n_blocks']} "
         f"blocks, longest {r['longest_block_min']:.1f} min",
         "",
         "architecture (of epochs inside blocks)",
         f"  WAKE  {r['wake_pct']:>5.1f}%",
         f"  NREM  {r['nrem_pct']:>5.1f}%",
         f"  REM   {r['rem_pct_CONSTRUCTED']:>5.1f}%   <- FIXED BY CONSTRUCTION, "
         f"do not report as a finding",
         "",
         "persistence (within unbroken blocks; calibration: noise -0.035, "
         "4 min bouts +0.510)"]
    for k, v in r["persistence"].items():
        L.append(f"  r@{k:<6} {v['r']}   shuffled {v['shuffled']}   "
                 f"pairs {v['pairs']}, blocks {v['blocks']}")
    L += ["", f"REM entered from NREM  {r['rem_from_nrem']}/{r['rem_entries']} "
              f"= {r['rem_from_nrem_pct']}%  (expect > {T.REM_FROM_NREM_MIN:.0f}%)",
          "", f"physiology pass: {r['physiology_pass']}"]
    for k, v in r["physiology_checks"].items():
        L.append(f"  {'PASS' if v else 'FAIL'}  {k}")
    L += ["", "median values by state"]
    for nm in ("WAKE", "NREM", "REM"):
        p = r["physiology"].get(nm)
        if p:
            L.append(f"  {nm:<5} n={p['n_epochs']:<7} EMG {p['emg_rms']:8.1f} uV  "
                     f"EEG {p['eeg_rms']:8.1f} uV  delta {p['delta_pct']:5.1f}%  "
                     f"theta/delta {p['theta_delta']:.3f}")
    L += ["", "bouts (inside blocks)"]
    for nm in ("WAKE", "NREM", "REM"):
        b = r["bouts"][nm]
        L.append(f"  {nm:<5} n={b['n']:<6} median {b['median_s']:>5} s   "
                 f"mean {b['mean_s']:>7.1f} s   max {b['max_s']:>6} s")
    rm = r["rem_measured"]
    L += ["", "REM measured independently (Otsu on theta/delta, NOT the "
              "percentile rule)",
          f"  REM {rm['rem_pct_of_recording']}% of scored time, "
          f"{rm['rem_pct_of_sleep']}% of sleep   "
          f"(literature for mouse: {rm['literature_rem_pct_of_sleep']}% of sleep)"]
    L += ["", "by light phase (ZT0 = lights on)"]
    for nm in ("light", "dark"):
        p = r["by_light_phase"].get(nm)
        L.append(f"  {nm:<6} " + ("no data" if not p else
                 f"{p['hours']:.2f} h  WAKE {p['wake_pct']:.1f}%  "
                 f"NREM {p['nrem_pct']:.1f}%  REM {p['rem_pct_CONSTRUCTED']:.1f}%"))
    lp = r["by_light_phase"].get("light")
    if lp:
        L += ["", "  Literature check: C57BL/6 mice sleep ~70% of the LIGHT "
                  "phase (NREM 62.0 +/- 7.8 %/12 h).",
              f"  This animal: {100 - lp['wake_pct']:.1f}% asleep in the light "
              f"phase.  " + ("consistent" if 45 <= (100 - lp["wake_pct"]) <= 90
                             else "OUTSIDE the normal range")]
    return "\n".join(L) + "\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("paths", nargs="+", help="day folder(s) or .npz file(s)")
    a = ap.parse_args()
    targets = []
    for p in a.paths:
        if os.path.isdir(p):
            targets += sorted(glob.glob(os.path.join(p, "port*.npz")))
        else:
            targets.append(p)
    if not targets:
        raise SystemExit("no per-mouse .npz files found -- run stage 2 first")
    for t in targets:
        r = analyse(t)
        print(f"\n{r['file']}")
        print(f"  {r['verdict']}")
        print(f"  {r['hours_in_blocks']:.2f} h in blocks, "
              f"r@1min {r['persistence']['1min']['r']}, "
              f"WAKE {r['wake_pct']}% / NREM {r['nrem_pct']}%, "
              f"REM from NREM {r['rem_from_nrem_pct']}%")


if __name__ == "__main__":
    main()
