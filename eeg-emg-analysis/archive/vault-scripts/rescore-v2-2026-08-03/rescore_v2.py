"""
Rescore any recording: corrected channel map + CONTIGUITY-AWARE persistence.

=============================================================================
WHY THIS SCRIPT REPLACES gate_and_score_all.py  (2026-08-03)
=============================================================================

TWO BUGS were found in the previous scorer. Both change which mice count as
"scoreable", in BOTH directions, so every historical verdict is affected.

BUG 1 — persistence was measured across time gaps.
    r@1min was computed as np.correlate(...)[15] on the GATED epoch array.
    Lag 15 epochs == 1 minute ONLY IF those epochs are contiguous in real time.
    Electrode contact is intermittent, so the gated array is a concatenation of
    fragments; index k and k+15 can be HOURS apart.
      - False negative: run-2 C2 had 250 blocks of median 1 epoch -> r=+0.078,
        reported "NO STRUCTURE". The statistic was untestable, not negative.
      - False positive: 0713 D2 scored r=+0.854, the best number in the project.
        Its longest contiguous block is 39.3 min of 100% WAKE. The correlation
        came from stitching fragments, not from sleep.
    FIX: compute autocorrelation strictly WITHIN each contiguous block, then
    combine as a weighted mean over blocks (weight = usable lag pairs). Blocks
    too short to contain the lag are excluded, not silently wrapped.

BUG 2 — REM fraction was fixed by construction.
    rem = (~wake) & (td >= np.percentile(td, 80)) makes the REM share an
    artefact of the percentile rule, not a measurement. We still compute it
    (it is needed to test REM's ORDER properties) but the REM PERCENTAGE is
    never reported as a finding. What IS evidence is that REM is entered from
    NREM rather than from WAKE - an order constraint no threshold can fake.

CHANNEL MAP (corrected 2026-08-01; RHD2216 is a BIPOLAR chip):
    port base + 0  = Allego /1  = EEG  (already a bipolar difference)
    port base + 1  = Allego /2  = EMG  (already a bipolar difference)
    port base + 2,3 = /3,/4     = EMPTY PADS, no wire attached
    second animal on a 64-ch splitter port: base+32, base+33 = /33, /34
The pre-2026-08-01 pipeline computed EEG = native0 - native1, i.e. EEG MINUS
EMG, and treated the empty pads as failed EMG surgeries.

LAYOUT IS READ FROM THE FILE, NEVER ASSUMED. Recordings exist at 64 ch/port
(splitter, two animals) and 32 ch/port (no splitter, one animal), including
mixed layouts such as A:64@0 B:32@64 C:64@96 D:64@160.

Usage:
    python3 rescore_v2.py <recording_base> [--force] [--json OUT.json]
"""
import json
import os
import sys
import numpy as np
from scipy import signal as sg

D = "/home/skimlab/radix/data/"
CACHE = os.environ.get("RESCORE_CACHE", "/tmp/rescore_cache/")
os.makedirs(CACHE, exist_ok=True)

# ---------------------------------------------------------------- parameters
EP = 4               # epoch length, seconds (standard for rodent sleep scoring)
NPERSEG = 2048       # Welch segment -> df = 0.49 Hz.
#                      DO NOT LOWER. At nperseg=512 (df=1.95 Hz) the theta band
#                      6-9 Hz spans ONE FFT bin and np.trapz over a single point
#                      returns EXACTLY ZERO, silently killing every REM test.
RAIL = 6300          # ADC rail in uV; |sample| > RAIL counts as clipped

# --- the three-part quality gate (an epoch must pass ALL THREE) -------------
OPEN_UV = 300.0      # 55-65 Hz mains amplitude above this => electrode OPEN.
#                      An open electrode is a floating antenna: it picks up mains
#                      at 10-15x this threshold. Real contact sits at 5-100 uV.
SHORT_UV = 25.0      # EEG rms below this => SHORTED / dead channel.
#                      A shorted channel sits at 16-21 uV, scores ~100% WAKE and
#                      has zero persistence. Without this test it masquerades as
#                      valid data (this is what wrongly passed D2 on 2026-08-01).
CLIP_F = 0.001       # fraction of railed samples above which the epoch is CLIPPED.
#                      A railed amplifier destroys the band-power ratios that all
#                      staging depends on (the 2026-07-15 retraction).

LAG_S = 60           # persistence lag: 1 minute
LAG = LAG_S // EP    # = 15 epochs
MIN_BLOCK = 2 * LAG + 1   # a block must hold at least one full lag pair (31 ep = 124 s)
R_THRESH = 0.30      # within-block persistence needed to call a mouse SCOREABLE
WAKE_LO, WAKE_HI = 15.0, 90.0   # plausible wake fraction; outside => artefact


def derive_layout(meta):
    """Map mice -> (EEG column, EMG column) from the recording's own metadata."""
    sbp = meta["sapiens_base"]["sensors_by_port"]
    mice, eeg, emg = [], [], []
    for port in sorted(sbp):
        s = sbp[port]
        if not isinstance(s, dict):
            continue
        n, base = s.get("num_channels"), s.get("connection_ntv_idx")
        if n is None or base is None:
            continue
        # 64-ch port = splitter carrying TWO animals; 32-ch port carries one.
        for k, off in enumerate([0, 32] if n >= 64 else [0]):
            mice.append(f"{port}{k+1}")
            eeg.append(base + off)
            emg.append(base + off + 1)
    return mice, eeg, emg


def extract(F, force=False):
    """Pass 1: per-epoch features for every animal. Cached."""
    meta = json.load(open(D + F + ".xdat.json"))
    st = meta["status"]
    fs, NC, N = int(st["samp_freq"]), st["signals"]["total"], st["num_smpl"]
    mice, eeg_cols, emg_cols = derive_layout(meta)
    out = CACHE + F + "_ep.npz"
    if os.path.exists(out) and not force:
        d = dict(np.load(out, allow_pickle=True))
        d["mice"] = [str(x) for x in d["mice"]]
        return d
    if not mice:
        return None

    NM = len(mice)
    cols = eeg_cols + emg_cols
    sos_eeg = sg.butter(4, [0.5, 30], btype="band", fs=fs, output="sos")
    sos_emg = sg.butter(4, [10, min(300, fs/2 - 1)], btype="band", fs=fs, output="sos")
    sos_mn = sg.butter(4, [55, 65], btype="band", fs=fs, output="sos")

    nep = (N // fs) // EP
    Z = lambda: np.zeros((nep, NM), dtype=np.float32)
    delta, theta, tot = Z(), Z(), Z()
    eeg_rms, eeg_mains, eeg_clip = Z(), Z(), Z()
    emg_rms, emg_mains = Z(), Z()

    mm = np.memmap(D + F + "_data.xdat", dtype="<f4", mode="r", shape=(N, NC))
    CH = 900
    s = 0
    while s < nep * EP:
        e = min(s + CH, nep * EP)
        blk = np.asarray(mm[s*fs:e*fs, :][:, cols], dtype=np.float64)
        E = sg.sosfiltfilt(sos_eeg, blk[:, :NM], axis=0)
        M = sg.sosfiltfilt(sos_emg, blk[:, NM:], axis=0)
        Xe = sg.sosfiltfilt(sos_mn, blk[:, :NM], axis=0)
        Xm = sg.sosfiltfilt(sos_mn, blk[:, NM:], axis=0)
        n = (e - s) // EP
        i0 = s // EP
        r = lambda a: a[:n*EP*fs].reshape(n, EP*fs, NM)
        Ee, Mm_, Xee, Xmm = r(E), r(M), r(Xe), r(Xm)
        raw_e = blk[:n*EP*fs, :NM].reshape(n, EP*fs, NM)
        fr, P = sg.welch(Ee, fs, nperseg=min(NPERSEG, EP*fs), axis=1)
        bp = lambda lo, hi: np.trapz(P[:, (fr >= lo) & (fr < hi), :],
                                     fr[(fr >= lo) & (fr < hi)], axis=1)
        delta[i0:i0+n] = bp(0.5, 4)
        theta[i0:i0+n] = bp(6, 9)
        tot[i0:i0+n] = bp(0.5, 30)
        eeg_rms[i0:i0+n] = Ee.std(1)
        emg_rms[i0:i0+n] = Mm_.std(1)
        eeg_mains[i0:i0+n] = Xee.std(1)
        emg_mains[i0:i0+n] = Xmm.std(1)
        eeg_clip[i0:i0+n] = (np.abs(raw_e) > RAIL).mean(1)
        s = e
        print(f"  {100*s/(nep*EP):.0f}%", end="\r", flush=True)
    d = dict(mice=mice, delta=delta, theta=theta, tot=tot, eeg_rms=eeg_rms,
             eeg_mains=eeg_mains, eeg_clip=eeg_clip, emg_rms=emg_rms,
             emg_mains=emg_mains, fs=fs, start_time=str(st.get("start_time", "")),
             hours=N/fs/3600)
    np.savez_compressed(out, **{k: np.array(v) if k == "mice" else v
                                for k, v in d.items()})
    print(f"  [cached] {out}")
    return d


def blocks_of(ok):
    """Contiguous runs of True as (start, stop) index pairs, stop exclusive."""
    idx = np.where(ok)[0]
    if len(idx) == 0:
        return []
    brk = np.where(np.diff(idx) > 1)[0]
    starts = np.concatenate(([0], brk + 1))
    stops = np.concatenate((brk + 1, [len(idx)]))
    return [(idx[a], idx[b-1] + 1) for a, b in zip(starts, stops)]


def otsu_threshold(v, bins=48):
    """Two-class split of a 1-D distribution by maximising between-class variance."""
    hist, edges = np.histogram(v, bins=bins)
    cen = (edges[:-1] + edges[1:]) / 2
    w = hist.astype(float)
    best, thr = -1.0, float(np.median(v))
    for k in range(4, bins - 4):
        w0, w1 = w[:k].sum(), w[k:].sum()
        if w0 < 20 or w1 < 20:
            continue
        m0 = (w[:k]*cen[:k]).sum()/w0
        m1 = (w[k:]*cen[k:]).sum()/w1
        val = w0*w1*(m0-m1)**2
        if val > best:
            best, thr = val, cen[k]
    return thr


def within_block_persistence(sleep, blocks, lag=LAG, rng=None):
    """Autocorrelation of the sleep indicator at `lag`, computed WITHIN blocks.

    Returns (r, n_pairs, n_blocks_used, r_shuffled).

    This is the fix for BUG 1. Every product pairs two epochs that are genuinely
    `lag` epochs apart in REAL TIME, because both come from the same unbroken
    stretch of contact. Blocks shorter than the lag contribute nothing rather
    than silently contributing a cross-gap pair.

    The shuffle control permutes labels WITHIN each block, preserving block
    structure and overall sleep fraction, so it isolates temporal ordering.
    """
    num = den = 0.0
    pairs = 0
    used = 0
    nums = dens = 0.0
    rng = rng or np.random.default_rng(0)
    for a, b in blocks:
        seg = sleep[a:b]
        if len(seg) < lag + 1:
            continue
        used += 1
        x = seg - seg.mean()
        if not np.any(x):
            continue
        num += float((x[:-lag] * x[lag:]).sum())
        den += float((x * x).sum())
        pairs += len(seg) - lag
        xs = rng.permutation(seg).astype(float)
        xs -= xs.mean()
        nums += float((xs[:-lag] * xs[lag:]).sum())
        dens += float((xs * xs).sum())
    r = num/den if den > 0 else np.nan
    rs = nums/dens if dens > 0 else np.nan
    return r, pairs, used, rs


def bouts(labels, val):
    out, run = [], 0
    for v in labels:
        if v == val:
            run += 1
        elif run:
            out.append(run)
            run = 0
    if run:
        out.append(run)
    return np.array(out, dtype=int)


def score(d, verbose=True):
    """Pass 2: gate, stage, and evaluate each animal. Returns a result dict."""
    mice = d["mice"]
    delta, theta, tot = d["delta"], d["theta"], d["tot"]
    eeg_rms, eeg_mains, eeg_clip = d["eeg_rms"], d["eeg_mains"], d["eeg_clip"]
    emg_rms, emg_mains = d["emg_rms"], d["emg_mains"]
    res = {}

    for i, m in enumerate(mice):
        # ---- the three-part gate ----------------------------------------
        not_open = (eeg_mains[:, i] < OPEN_UV) & (emg_mains[:, i] < OPEN_UV)
        not_short = eeg_rms[:, i] >= SHORT_UV
        not_clip = eeg_clip[:, i] < CLIP_F
        finite = (delta[:, i] > 0) & (theta[:, i] > 0) & (emg_rms[:, i] > 0)
        ok = not_open & not_short & not_clip & finite

        blks = blocks_of(ok)
        long_blks = [(a, b) for a, b in blks if (b - a) >= MIN_BLOCK]
        gated_h = ok.sum() * EP / 3600
        block_h = sum(b - a for a, b in long_blks) * EP / 3600

        R = dict(mouse=m, gated_hours=round(float(gated_h), 3),
                 block_hours=round(float(block_h), 3),
                 n_blocks=len(blks), n_long_blocks=len(long_blks),
                 longest_block_min=round(max((b-a for a, b in blks), default=0)*EP/60, 1),
                 pct_not_open=round(100*float(not_open.mean()), 1),
                 pct_not_short=round(100*float(not_short.mean()), 1),
                 pct_not_clip=round(100*float(not_clip.mean()), 1),
                 med_eeg_mains=round(float(np.median(eeg_mains[:, i])), 1),
                 med_eeg_rms=round(float(np.median(eeg_rms[:, i])), 1),
                 verdict=None)

        # A mouse needs enough data INSIDE usable blocks, not merely in total.
        if ok.sum() < 225 or block_h * 3600 < 900:   # <15 min either way
            R["verdict"] = "INSUFFICIENT"
            res[m] = R
            continue

        # ---- staging ------------------------------------------------------
        le = np.log10(emg_rms[ok, i])
        td = np.log10(theta[ok, i] / delta[ok, i])
        thr = otsu_threshold(le)
        wake_g = le >= thr
        td_thr = np.percentile(td, 80)
        # NOTE: this percentile rule FIXES the REM share by construction.
        # REM% is therefore never reported as a finding; only REM's ORDER is.
        lab_g = np.where(wake_g, 0, np.where(td < td_thr, 1, 2))

        lab = np.full(len(ok), -1, dtype=int)
        lab[ok] = lab_g
        sleep = (lab == 1) | (lab == 2)

        r, pairs, used, r_shuf = within_block_persistence(
            sleep.astype(float), long_blks)
        # Report several lags. The 2026-08-01 "first real sleep" claim quoted
        # r@10min, so comparability requires more than the 1-minute figure.
        # Calibration of this statistic (synthetic alternating states):
        #   pure noise -0.035 | 30s bouts +0.112 | 2min +0.214
        #   4min +0.510 | 10min +0.703
        # so r>0.3 at 1 min corresponds to consolidated bouts of roughly 3 min+.
        multi = {}
        for lab_s, sec in [("1min", 60), ("5min", 300), ("10min", 600)]:
            lg = sec // EP
            blk_l = [(a, b) for a, b in blks if (b - a) >= 2*lg + 1]
            rr, pp, uu, ss = within_block_persistence(sleep.astype(float), blk_l, lag=lg)
            multi[lab_s] = dict(r=None if np.isnan(rr) else round(float(rr), 3),
                                shuf=None if np.isnan(ss) else round(float(ss), 3),
                                pairs=int(pp), blocks=int(uu))
        R["persistence_by_lag"] = multi

        wake_pct = 100 * float((lab_g == 0).mean())
        R.update(wake_pct=round(wake_pct, 1),
                 nrem_pct=round(100*float((lab_g == 1).mean()), 1),
                 rem_pct_CONSTRUCTED=round(100*float((lab_g == 2).mean()), 1),
                 r_within=None if np.isnan(r) else round(float(r), 3),
                 r_shuffled=None if np.isnan(r_shuf) else round(float(r_shuf), 3),
                 lag_pairs=int(pairs), blocks_used=int(used))

        # ---- physiology (must hold, or staging is not believable) ---------
        dp = 100*delta[ok, i]/tot[ok, i]
        ratio = theta[ok, i]/delta[ok, i]
        vals = {}
        for nm, v in [("WAKE", 0), ("NREM", 1), ("REM", 2)]:
            msk = lab_g == v
            if msk.sum() >= 5:
                vals[nm] = dict(emg=float(np.median(emg_rms[ok, i][msk])),
                                eeg=float(np.median(eeg_rms[ok, i][msk])),
                                delta_pct=float(np.median(dp[msk])),
                                th_de=float(np.median(ratio[msk])))
        phys = ("WAKE" in vals and "NREM" in vals and
                vals["WAKE"]["emg"] > vals["NREM"]["emg"] and
                vals["NREM"]["delta_pct"] > vals["WAKE"]["delta_pct"] and
                vals["NREM"]["eeg"] > vals["WAKE"]["eeg"])
        if "REM" in vals:
            phys = phys and (vals["REM"]["th_de"] > vals["NREM"]["th_de"] and
                             vals["REM"]["emg"] < vals["WAKE"]["emg"])
        R["physiology"] = vals
        R["physiology_pass"] = bool(phys)

        # ---- REM entry order (within blocks only) -------------------------
        # Physiologically REM is entered from NREM, essentially never from WAKE.
        # No amplitude threshold can manufacture this; it is a sequence property.
        frm_n = frm_w = 0
        nrem_b, wake_b, rem_b = [], [], []
        for a, b in long_blks:
            seg = lab[a:b]
            for k in range(len(seg)-1):
                if seg[k+1] == 2 and seg[k] != 2:
                    if seg[k] == 1:
                        frm_n += 1
                    elif seg[k] == 0:
                        frm_w += 1
            nrem_b.append(bouts(seg, 1)); wake_b.append(bouts(seg, 0))
            rem_b.append(bouts(seg, 2))
        tot_entry = frm_n + frm_w
        R["rem_entries"] = tot_entry
        R["rem_from_nrem_pct"] = round(100*frm_n/tot_entry, 1) if tot_entry else None
        cat = lambda L: np.concatenate([x for x in L if len(x)]) if any(len(x) for x in L) else np.array([])
        for nm, L in [("nrem", nrem_b), ("wake", wake_b), ("rem", rem_b)]:
            bl = cat(L) * EP
            R[f"{nm}_bout_median_s"] = int(np.median(bl)) if len(bl) else None
            R[f"{nm}_bout_max_s"] = int(bl.max()) if len(bl) else None

        # ---- final verdict -------------------------------------------------
        reasons = []
        if r is None or np.isnan(r) or r <= R_THRESH:
            reasons.append(f"within-block r={r:.3f}<={R_THRESH}")
        if not phys:
            reasons.append("physiology FAIL")
        if not (WAKE_LO <= wake_pct <= WAKE_HI):
            reasons.append(f"implausible wake {wake_pct:.1f}%")
        if R["rem_from_nrem_pct"] is not None and R["rem_from_nrem_pct"] < 70 and tot_entry >= 10:
            reasons.append(f"REM entered from WAKE {100-R['rem_from_nrem_pct']:.0f}%")
        R["verdict"] = "SCOREABLE" if not reasons else "REJECT: " + "; ".join(reasons)
        res[m] = R

    if verbose:
        print(f"{'mouse':6}{'gated':>8}{'inBlocks':>10}{'longest':>9}"
              f"{'r_win':>8}{'shuf':>7}{'wake%':>7}{'REMfromN':>10}  verdict")
        print("-" * 100)
        for m, R in res.items():
            if R["verdict"] == "INSUFFICIENT":
                print(f"{m:6}{R['gated_hours']:7.2f}h{R['block_hours']:9.2f}h"
                      f"{R['longest_block_min']:8.1f}m{'':>8}{'':>7}{'':>7}{'':>10}  INSUFFICIENT")
            else:
                print(f"{m:6}{R['gated_hours']:7.2f}h{R['block_hours']:9.2f}h"
                      f"{R['longest_block_min']:8.1f}m"
                      f"{(R['r_within'] if R['r_within'] is not None else float('nan')):8.3f}"
                      f"{(R['r_shuffled'] if R['r_shuffled'] is not None else float('nan')):7.3f}"
                      f"{R['wake_pct']:7.1f}"
                      f"{(R['rem_from_nrem_pct'] if R['rem_from_nrem_pct'] is not None else float('nan')):9.0f}%"
                      f"  {R['verdict']}")
    return res


if __name__ == "__main__":
    F = sys.argv[1]
    d = extract(F, force="--force" in sys.argv)
    if d is None:
        sys.exit("no ports populated")
    print(f"\n{F}  {d['hours']:.2f} h  start={d['start_time']}  mice={d['mice']}")
    res = score(d)
    if "--json" in sys.argv:
        out = sys.argv[sys.argv.index("--json") + 1]
        def jsafe(o):
            if isinstance(o, (np.integer,)):
                return int(o)
            if isinstance(o, (np.floating,)):
                return float(o)
            if isinstance(o, np.ndarray):
                return o.tolist()
            return str(o)
        json.dump({"recording": F, "hours": float(d["hours"]),
                   "start_time": str(d["start_time"]), "mice": res},
                  open(out, "w"), indent=1, default=jsafe)
        print(f"[json] {out}")
