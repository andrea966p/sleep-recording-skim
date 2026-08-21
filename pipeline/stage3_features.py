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

    Persistence and the REM-order check are computed on the RAW labels, BEFORE
    the minimum-bout merge, and WITHIN unbroken contact blocks only. Smoothing
    short bouts raises the autocorrelation of the state sequence with no new
    information, so computing them after the merge would inflate both. The
    architecture, bout and light/dark numbers ARE computed after the merge,
    because that is the lab scoring convention.

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

from core import qc_thresholds as T
from pipeline import pipeline_common as P

# numpy 2.0 removed np.trapz in favour of np.trapezoid. Bind once, here, so the
# pipeline runs on both. Without this the whole staging path dies on numpy >= 2
# with "module 'numpy' has no attribute 'trapz'".
_trapz = getattr(np, "trapezoid", None) or np.trapz


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
    bp = lambda lo, hi: _trapz(Pxx[:, (fr >= lo) & (fr < hi)],
                                 fr[(fr >= lo) & (fr < hi)], axis=1)
    return dict(n=n,
                eeg_rms=Ef.std(1), emg_rms=Mf.std(1),
                delta=bp(*T.BAND_DELTA),                    # REPORTING band
                delta_stg=bp(*T.BAND_DELTA_STAGING),        # STAGING band
                theta=bp(*T.BAND_THETA),
                total=bp(*T.BAND_TOTAL), norm=bp(*T.BAND_NORM))


def stage(f, ok):
    """Assign WAKE / NREM / REM. Thresholds are derived PER ANIMAL."""
    lab = np.full(f["n"], -1, dtype=int)
    idx = np.where(ok[:f["n"]])[0]
    if len(idx) == 0:
        return lab, {}, lab.copy()
    le = np.log10(np.clip(f["emg_rms"][idx], 1e-6, None))
    # STAGING uses BAND_DELTA_STAGING (0.5-4.5 Hz), matching the Japanese tool.
    # Reported delta elsewhere uses BAND_DELTA (1-4 Hz), matching the paper.
    td = np.log10(np.clip(f["theta"][idx] / np.clip(f["delta_stg"][idx], 1e-12, None),
                          1e-6, None))
    # FIX 10: degenerate-input fallback, copied from the Japanese tool
    # (sleepy_pipeline_refined.estimate_emg_threshold): fewer than 10 finite
    # values, or fewer than 2 distinct values, falls back to the MEDIAN rather
    # than letting the split routine produce nonsense.
    if len(le) < 10 or len(np.unique(le)) < 2:
        emg_thr = float(np.median(le))
        degenerate = True
    else:
        emg_thr = P.otsu_threshold(le)
        degenerate = False
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
    return lab, dict(degenerate_fallback=bool(degenerate),
                     emg_otsu_log10=float(emg_thr),
                     theta_delta_p80_log10=float(td_thr),
                     theta_delta_otsu_log10=float(td_thr_otsu)), lab_otsu


def steady_state_mask(lab, blocks):
    """Epochs whose PRECEDING and FOLLOWING epoch are the same state.

    IIIS exclude transition epochs from power-spectrum analysis only; staging
    and state totals still use every epoch. Evaluated WITHIN blocks, so a block
    edge is treated as a transition rather than reaching across a contact gap.
    SOURCE: Nakata et al., SLEEP 2025, doi:10.1093/sleep/zsae279.
    """
    m = np.zeros(len(lab), dtype=bool)
    for a, b in blocks:
        if b - a < 3:
            continue
        seg = lab[a:b]
        same = (seg[1:-1] == seg[:-2]) & (seg[1:-1] == seg[2:]) & (seg[1:-1] >= 0)
        m[a + 1:b - 1] = same
    return m


def physiology(f, lab, ok, spec_mask=None):
    """Do the three states behave like WAKE, NREM and REM should?

    If they do not, the clustering found something other than sleep and no
    architecture number from it is meaningful.
    """
    base = ok[:f["n"]] & (lab >= 0)
    if spec_mask is not None:
        base = base & spec_mask[:f["n"]]
    idx = np.where(base)[0]
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
            # this mirrors the STAGING discriminator, so it uses the staging band
            theta_delta=float(np.median(f["theta"][m]
                                        / np.clip(f["delta_stg"][m], 1e-12, None))),
            # IIIS-style: power relative to the 15-30 Hz band
            delta_density=float(f["delta"][m].sum()
                                / max(float(f["norm"][m].sum()), 1e-12)),
            theta_density=float(f["theta"][m].sum()
                                / max(float(f["norm"][m].sum()), 1e-12)))
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
    # WHICH OF THESE CAN ACTUALLY FAIL?
    # Verified against the staging rule on 2026-08-08 (council review):
    #   wake_has_highest_emg   FORCED  -- WAKE *is* the Otsu split on EMG
    #   rem_highest_theta_delta FORCED -- REM *is* the top of theta/delta
    #   rem_emg_low            FORCED  -- REM is a subset of non-wake, which is
    #                                     by definition below the EMG cut
    #   nrem_has_most_delta    NEAR-FORCED -- NREM is the residual after the
    #                                     high theta/delta epochs are removed
    #   nrem_largest_amplitude INFORMATIVE -- nothing in the rule constrains
    #                                     EEG amplitude
    # Reporting "5/5 PASS" as validation is therefore misleading. Only the
    # informative check is evidence.
    forced = {"wake_has_highest_emg": "FORCED by the WAKE rule",
              "rem_highest_theta_delta": "FORCED by the REM rule",
              "rem_emg_low": "FORCED, REM is a subset of non-wake",
              "nrem_has_most_delta": "NEAR-FORCED, NREM is the residual"}
    informative = {k: v for k, v in checks.items() if k not in forced}
    detail = {k: dict(passed=bool(v),
                      status=forced.get(k, "INFORMATIVE, can genuinely fail"))
              for k, v in checks.items()}
    return out, checks, bool(ok_all), detail, informative


def rem_order_null(lab, blocks, n_iter=200, seed=0):
    """Is 'REM is entered from NREM' more than the label composition forces?

    Null: keep each block's RUN LENGTHS and its multiset of run states, but
    permute the ORDER of the runs. That destroys any real sequential structure
    while preserving how much of each state there is and how consolidated it is,
    which is exactly what could otherwise manufacture a high transition rate.

    Returns (null_mean, null_sd, percentile_of_observed).
    """
    rng = np.random.default_rng(seed)
    obs = rem_entry_order(lab, blocks)[2]
    if np.isnan(obs):
        return float("nan"), float("nan"), float("nan")
    vals = []
    for _ in range(n_iter):
        shuffled = lab.copy()
        for a, b in blocks:
            seg = lab[a:b]
            if len(seg) < 3:
                continue
            edges = np.flatnonzero(np.diff(seg)) + 1
            starts = np.concatenate(([0], edges))
            ends = np.concatenate((edges, [len(seg)]))
            runs = [(seg[st], en - st) for st, en in zip(starts, ends)]
            rng.shuffle(runs)
            out, k = np.empty(len(seg), dtype=int), 0
            for v, ln in runs:
                out[k:k + ln] = v
                k += ln
            shuffled[a:b] = out
        v = rem_entry_order(shuffled, blocks)[2]
        if not np.isnan(v):
            vals.append(v)
    if not vals:
        return float("nan"), float("nan"), float("nan")
    vals = np.array(vals)
    pct = 100.0 * float((vals < obs).mean())
    return float(vals.mean()), float(vals.std()), pct


def enforce_min_bout(lab, blocks, min_ep):
    """Merge runs shorter than min_ep into the neighbouring state.

    Applied WITHIN unbroken contact blocks only. Merging across a block
    boundary would join epochs that may be hours apart -- the same class of
    error as the 2026-08-03 persistence bug.

    A short run is relabelled to whichever adjacent run is LONGER; ties go to
    the preceding run. Iterated until no run shorter than min_ep remains,
    because merging can create new short runs.

    Returns (new_lab, n_epochs_relabelled).
    """
    out = lab.copy()
    changed_total = 0
    for a, b in blocks:
        seg = out[a:b]
        if len(seg) < min_ep:
            continue
        # Repeat until stable. Merging one short run can create a new short run,
        # so one pass is not enough. A cap of len(seg) cannot be exceeded because
        # every merge strictly reduces the number of runs.
        for _ in range(len(seg)):
            edges = np.flatnonzero(np.diff(seg)) + 1
            starts = np.concatenate(([0], edges))
            ends = np.concatenate((edges, [len(seg)]))
            lens = ends - starts
            if len(lens) == 1:
                break
            short = np.flatnonzero(lens < min_ep)
            if len(short) == 0:
                break
            # merge the SHORTEST run first, so the result does not depend on
            # scan order
            i = int(short[np.argmin(lens[short])])
            prev_len = lens[i - 1] if i > 0 else -1
            next_len = lens[i + 1] if i + 1 < len(lens) else -1
            take = i - 1 if prev_len >= next_len else i + 1
            changed_total += int(lens[i])
            seg[starts[i]:ends[i]] = seg[starts[take]]
        out[a:b] = seg
    return out, changed_total


def otsu_sensitivity(f, ok, blocks, zt, thr_log, in_block):
    """How far do the headline numbers move if the WAKE cut is wrong?

    The Otsu threshold is refit per animal, so "threshold-independent" is not a
    claim we can make. This sweeps the cut by +/-25% IN LINEAR uV and reports
    what happens to WAKE %, to sleep in the light phase, and to persistence.

    Architecture numbers use the SMOOTHED labels and persistence uses the RAW
    labels, exactly as the headline pipeline does, so the rows are comparable
    to the reported values.
    """
    n = f["n"]
    idx = np.where(ok[:n])[0]
    if len(idx) == 0:
        return []
    le = np.log10(np.clip(f["emg_rms"][idx], 1e-6, None))
    td = np.log10(np.clip(f["theta"][idx] / np.clip(f["delta_stg"][idx], 1e-12, None),
                          1e-6, None))
    td_thr = np.percentile(td, 80)
    lt = P.is_light(zt[:n])
    rows = []
    for mult in T.OTSU_SENSITIVITY_MULTIPLIERS:
        thr = thr_log + np.log10(mult)          # +/-25% in linear uV
        lab_r = np.full(n, -1, dtype=int)
        wake = le >= thr
        lab_r[idx] = np.where(wake, WAKE, np.where(td < td_thr, NREM, REM))
        lab_s, _ = enforce_min_bout(lab_r.copy(), blocks, T.MIN_BOUT_EPOCHS)
        sel = in_block & (lab_s >= 0)
        tot = max(int(sel.sum()), 1)
        light = lt & sel
        asleep_light = (100.0 * float(((lab_s[light] == NREM) | (lab_s[light] == REM)).mean())
                        if light.sum() else float("nan"))
        sleep_raw = ((lab_r == NREM) | (lab_r == REM)).astype(float)
        lg = 60 // T.EPOCH_S
        bl = [(a, b) for a, b in blocks if (b - a) >= 2 * lg + 1]
        r, _, _, _ = P.within_block_persistence(sleep_raw, bl, lag=lg)
        rows.append(dict(
            multiplier=float(mult),
            threshold_uv=round(float(10 ** thr), 2),
            wake_pct=round(100.0 * float((lab_s[sel] == WAKE).sum()) / tot, 1),
            nrem_pct=round(100.0 * float((lab_s[sel] == NREM).sum()) / tot, 1),
            asleep_in_light_pct=None if np.isnan(asleep_light) else round(asleep_light, 1),
            r_1min_raw=None if np.isnan(r) else round(float(r), 3)))
    return rows


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
    # LAB SCORING CONVENTION: a state shorter than MIN_BOUT_EPOCHS (12 s) is not
    # counted as that state. See qc_thresholds.MIN_BOUT_EPOCHS for provenance.
    lab_raw = lab.copy()
    lab, n_merged = enforce_min_bout(lab, blocks, T.MIN_BOUT_EPOCHS)
    lab_otsu, _ = enforce_min_bout(lab_otsu, blocks, T.MIN_BOUT_EPOCHS)

    in_block = np.zeros(n, dtype=bool)
    for a, b in blocks:
        in_block[a:b] = True

    sel = in_block & (lab >= 0)
    counts = {NAMES[v]: int((lab[sel] == v).sum()) for v in NAMES}
    tot_ep = max(int(sel.sum()), 1)

    # VALIDITY STATISTICS ARE COMPUTED ON THE *RAW* LABELS.
    # Smoothing short bouts raises the autocorrelation of the state sequence by
    # construction, so computing persistence on the smoothed labels would
    # inflate it with no new information (B1: 0.603 -> 0.742 on 2026-08-08).
    # The r@1min calibration in qc_thresholds (noise -0.035, 4 min bouts +0.510)
    # was derived on UNSMOOTHED labels, so it only applies here.
    sleep = ((lab_raw == NREM) | (lab_raw == REM)).astype(float)
    pers = {}
    for name, sec in (("1min", 60), ("5min", 300), ("10min", 600)):
        lg = sec // T.EPOCH_S
        bl = [(a, b) for a, b in blocks if (b - a) >= 2 * lg + 1]
        r, pairs, used, shuf = P.within_block_persistence(sleep, bl, lag=lg)
        pers[name] = dict(r=None if np.isnan(r) else round(float(r), 3),
                          shuffled=None if np.isnan(shuf) else round(float(shuf), 3),
                          pairs=int(pairs), blocks=int(used))

    # Spectral summaries exclude TRANSITION epochs (IIIS). Staging and state
    # totals above are unaffected.
    # thr is {} when a recording has no usable epochs at all
    sens = (otsu_sensitivity(f, ok, blocks, zt, thr["emg_otsu_log10"], in_block)
            if "emg_otsu_log10" in thr else [])
    if sens:
        base = [r for r in sens if r["multiplier"] == 1.0][0]
        al = [r["asleep_in_light_pct"] for r in sens if r["asleep_in_light_pct"] is not None]
        wk = [r["wake_pct"] for r in sens]
        sens_summary = dict(
            rows=sens,
            wake_pct_range=[min(wk), max(wk)],
            wake_pct_swing=round(max(wk) - min(wk), 1),
            asleep_in_light_range=[min(al), max(al)] if al else None,
            asleep_in_light_swing=round(max(al) - min(al), 1) if al else None,
            note="WAKE cut swept +/-25% in linear uV. The Otsu threshold is refit per "
                 "animal, so the circadian result is NOT threshold-independent; this "
                 "states how much it depends on the cut. Required by the council review.")
    else:
        sens_summary = None

    spec_mask = (steady_state_mask(lab, blocks)
                 if T.EXCLUDE_TRANSITION_EPOCHS_FROM_SPECTRA else None)
    phys, checks, phys_ok, phys_detail, phys_informative = physiology(
        f, lab, sel, spec_mask=spec_mask)
    phys_informative_pass = bool(phys_informative) and all(phys_informative.values())
    n_spec = int((sel & (spec_mask if spec_mask is not None else True)).sum())
    spectra_info = dict(
        exclude_transition_epochs=bool(T.EXCLUDE_TRANSITION_EPOCHS_FROM_SPECTRA),
        epochs_used_for_spectra=n_spec,
        epochs_scored=int(sel.sum()),
        pct_excluded_as_transition=round(100.0 * (int(sel.sum()) - n_spec)
                                         / max(int(sel.sum()), 1), 1),
        normalisation_band_hz=list(T.BAND_NORM),
        note="IIIS: exclude artifact and transition epochs from SPECTRA only; "
             "power expressed relative to 15-30 Hz. doi:10.1093/sleep/zsae279")
    # Also on RAW labels: smoothing deletes isolated single-epoch REM, which
    # mechanically raises the fraction of REM entered from NREM.
    rn, rt, rpct = rem_entry_order(lab_raw, blocks)
    rn_s, rt_s, rpct_s = rem_entry_order(lab, blocks)
    rem_null_mean, rem_null_sd, rem_null_pct = rem_order_null(lab_raw, blocks)

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
        literature_rem_pct_of_sleep_mouse=10.0,
        reliable=False,
        caveat=("REM is NOT reliably separable with this montage. Both the "
                "percentile rule and the Otsu cut put REM far above the "
                "literature value of <10% of sleep, so neither is a "
                "measurement. Report WAKE vs NREM, plus the ORDER property "
                "that REM is entered from NREM. Do not report a REM share."))

    n_scored = int((lab_raw >= 0).sum())
    min_bout = dict(
        min_bout_epochs=int(T.MIN_BOUT_EPOCHS),
        min_bout_s=int(T.MIN_BOUT_EPOCHS * T.EPOCH_S),
        epochs_relabelled=int(n_merged),
        pct_of_scored_epochs=round(100.0 * n_merged / n_scored, 2) if n_scored else 0.0,
        rule="runs shorter than the minimum are merged into the longer neighbouring state, within blocks only",
        provenance="LAB CONVENTION, not from the IIIS reference (see qc_thresholds.MIN_BOUT_EPOCHS)")

    # STATE TOTALS BOTH WAYS.
    # Ours: percentage of SCORED epochs (rejected epochs excluded entirely).
    # IIIS include artifact epochs in their state totals, which they can do
    # because a human still assigns a stage to an artifact epoch. We cannot --
    # our rejected epochs are OPEN electrodes with no signal to score. So the
    # comparable presentation is percentage of the WHOLE recording with the
    # unscored fraction stated explicitly.
    # NOTE: blocks contain only PASSING epochs by construction, so a
    # "percentage of epochs in blocks" is identical to "percentage of scored
    # epochs" and tells you nothing. The informative denominator is the WHOLE
    # RECORDING, which exposes how much was thrown away.
    totals_both_ways = dict(
        of_scored_epochs={NAMES[v]: round(100.0 * counts[NAMES[v]] / tot_ep, 1)
                          for v in NAMES},
        of_whole_recording={NAMES[v]: round(100.0 * counts[NAMES[v]] / max(n, 1), 1)
                            for v in NAMES},
        unscored_pct_of_recording=round(100.0 * (n - int(sel.sum())) / max(n, 1), 1),
        recording_epochs=int(n), scored_epochs=int(sel.sum()),
        note="IIIS include artifact epochs in state totals (doi:10.1093/sleep/zsae279). "
             "Our rejected epochs are open electrodes with no scorable signal, so they "
             "cannot be assigned a stage. Percentages of scored epochs are NOT directly "
             "comparable to published values without this denominator.")

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
        physiology_detail=phys_detail,
        physiology_informative_checks=phys_informative,
        physiology_informative_pass=phys_informative_pass,
        physiology_caveat=("4 of the 5 checks are FORCED by the staging rule and "
                           "cannot fail. Do NOT report '5/5 PASS' as validation. "
                           "Only physiology_informative_pass is evidence."),
        rem_entries=int(rt), rem_from_nrem=int(rn),
        rem_from_nrem_pct=None if np.isnan(rpct) else round(float(rpct), 1),
        rem_from_nrem_pct_smoothed=None if np.isnan(rpct_s) else round(float(rpct_s), 1),
        rem_from_nrem_null=dict(
            null_mean_pct=None if np.isnan(rem_null_mean) else round(rem_null_mean, 1),
            null_sd_pct=None if np.isnan(rem_null_sd) else round(rem_null_sd, 1),
            observed_percentile_of_null=(None if np.isnan(rem_null_pct)
                                         else round(rem_null_pct, 1)),
            method="run-order shuffle within blocks; run lengths and state "
                   "composition preserved, sequence destroyed",
            note="If the observed value sits inside the null, 'REM is entered from "
                 "NREM' is forced by label composition and is NOT evidence."),
        validity_stats_computed_on=("RAW labels, before the minimum-bout merge. "
                                    "Smoothing inflates both persistence and REM order "
                                    "by construction; architecture and bouts below are "
                                    "computed on the SMOOTHED labels."),
        bouts=bt,
        min_bout=min_bout, spectra=spectra_info, otsu_sensitivity=sens_summary,
        state_totals=totals_both_ways, by_light_phase=phase,
        light_cycle=f"on {T.LIGHTS_ON_HOUR:02d}:00 / off {T.LIGHTS_OFF_HOUR:02d}:00 KST",
        pipeline_version="2026-08-08")

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
         "persistence (RAW labels, within unbroken blocks; calibration: noise -0.035, "
         "4 min bouts +0.510)"]
    for k, v in r["persistence"].items():
        L.append(f"  r@{k:<6} {v['r']}   shuffled {v['shuffled']}   "
                 f"pairs {v['pairs']}, blocks {v['blocks']}")
    nl = r.get("rem_from_nrem_null") or {}
    L += ["", f"REM entered from NREM  {r['rem_from_nrem']}/{r['rem_entries']} "
              f"= {r['rem_from_nrem_pct']}%  (expect > {T.REM_FROM_NREM_MIN:.0f}%)",
          f"  shuffled null: {nl.get('null_mean_pct')}% +/- {nl.get('null_sd_pct')}%"
          f"   observed sits at the {nl.get('observed_percentile_of_null')}th pct of the null",
          "  >> if the observed value is inside the null, this is forced by label",
          "     composition and is NOT evidence.",
          "", f"physiology pass: {r['physiology_pass']}"]
    for k, v in r["physiology_checks"].items():
        st = r.get("physiology_detail", {}).get(k, {}).get("status", "")
        L.append(f"  {'PASS' if v else 'FAIL'}  {k:24} {st}")
    L += [f"  >> INFORMATIVE CHECKS ONLY: {r.get('physiology_informative_pass')}",
          "     4 of 5 checks are FORCED by the staging rule and cannot fail.",
          "     Do not report '5/5 PASS' as validation."]
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
    L += ["", "REM cross-check (Otsu on theta/delta, independent of the "
              "percentile rule)",
          f"  REM {rm['rem_pct_of_recording']}% of scored time, "
          f"{rm['rem_pct_of_sleep']}% of sleep",
          f"  literature for mouse: REM is "
          f"<{rm['literature_rem_pct_of_sleep_mouse']:.0f}% of total sleep",
          "  >> REM IS NOT RELIABLY SEPARABLE HERE. Both rules land far above",
          "     the literature value, so neither is a measurement. Report WAKE",
          "     vs NREM and REM's ORDER only. Do not report a REM share."]
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
    if r.get("otsu_sensitivity"):
        sv = r["otsu_sensitivity"]
        L += ["", "WAKE-cut sensitivity (Otsu threshold swept +/-25% in linear uV)",
              f"  {'mult':>6}{'thr uV':>9}{'WAKE%':>8}{'asleep light%':>15}{'r@1min':>9}"]
        for x in sv["rows"]:
            L.append(f"  {x['multiplier']:>6}{x['threshold_uv']:>9}{x['wake_pct']:>8}"
                     f"{str(x['asleep_in_light_pct']):>15}{str(x['r_1min_raw']):>9}")
        L += [f"  >> asleep-in-light swings {sv['asleep_in_light_swing']} points "
              f"across the sweep",
              "     The Otsu cut is REFIT PER ANIMAL, so this result is NOT",
              "     threshold-independent. Quote this swing next to the headline",
              "     number, and never call the circadian check threshold-free."]

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
