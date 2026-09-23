#!/usr/bin/env python3
"""STAGE 1 -- is this mouse scoreable? Is the data clean?

Reads the raw .xdat once, computes per-epoch quality features for every animal,
and emits a per-animal QC verdict with the REASON attached.

Verdicts
    CLEAN         every test passes, enough consolidated data -> go to stage 2
    DIRTY         usable data exists but is fragmented or partly contaminated
    OPEN          electrode not electrically connected (dominant failure mode)
    DEAD          channel never carried EEG (shorted / broken)
    CLIPPED       amplifier saturated for most of the recording
    INSUFFICIENT  too little usable data to ask the question at all

INSUFFICIENT is NOT a negative result. It means the test could not be run.

Usage
    python3 stage1_qc.py <recording_base> [<recording_base> ...] [--force]
    python3 stage1_qc.py --all
"""
import argparse
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


# Derived from the single root rather than carrying its own /tmp default, which
# is how this ended up with two independent cache locations that could disagree.
# EEG_QC_CACHE still wins if set, for anything that already exports it.
from core import paths as _PATHS
CACHE = os.environ.get("EEG_QC_CACHE", str(_PATHS.CACHE_ROOT) + "/")
os.makedirs(CACHE, exist_ok=True)


# ---------------------------------------------------------------------------
def extract_features(base, force=False):
    """Pass 1: per-epoch features for every animal in the file. Cached.

    One sequential read of the raw file. Everything downstream works off these
    features, so the 400 GB of raw data is never touched twice.
    """
    out = os.path.join(CACHE, base + "_feat.npz")
    if os.path.exists(out) and not force:
        d = dict(np.load(out, allow_pickle=True))
        d["labels"] = json.loads(str(d["labels_json"]))
        return d

    meta = P.load_meta(base)
    info = P.recording_info(base, meta)
    fs, N, NC = info["fs"], info["n_samp"], info["n_chan"]
    labels, eeg_cols, emg_cols = P.derive_layout(meta)
    if not labels:
        return None
    NM = len(labels)
    cols = eeg_cols + emg_cols

    sos_eeg = sg.butter(4, list(T.FILT_EEG), btype="band", fs=fs, output="sos")
    sos_emg = sg.butter(4, [T.FILT_EMG[0], min(T.FILT_EMG[1], fs / 2 - 1)],
                        btype="band", fs=fs, output="sos")
    sos_mn = sg.butter(4, list(T.FILT_MAINS), btype="band", fs=fs, output="sos")

    nep = (N // fs) // T.EPOCH_S
    Z = lambda: np.zeros((nep, NM), dtype=np.float32)
    delta, theta, tot = Z(), Z(), Z()
    eeg_rms, eeg_mains, eeg_clip = Z(), Z(), Z()
    emg_rms, emg_mains = Z(), Z()

    mm = np.memmap(os.path.join(P.DATA_DIR, base + "_data.xdat"),
                   dtype="<f4", mode="r", shape=(N, NC))
    CHUNK_S = 900
    s = 0
    while s < nep * T.EPOCH_S:
        e = min(s + CHUNK_S, nep * T.EPOCH_S)
        blk = np.asarray(mm[s * fs:e * fs, :][:, cols], dtype=np.float64)
        n = (e - s) // T.EPOCH_S
        i0 = s // T.EPOCH_S
        E = sg.sosfiltfilt(sos_eeg, blk[:, :NM], axis=0)
        M = sg.sosfiltfilt(sos_emg, blk[:, NM:], axis=0)
        Xe = sg.sosfiltfilt(sos_mn, blk[:, :NM], axis=0)
        Xm = sg.sosfiltfilt(sos_mn, blk[:, NM:], axis=0)
        r = lambda a: a[:n * T.EPOCH_S * fs].reshape(n, T.EPOCH_S * fs, NM)
        Ee, Mm_, Xee, Xmm = r(E), r(M), r(Xe), r(Xm)
        raw_e = blk[:n * T.EPOCH_S * fs, :NM].reshape(n, T.EPOCH_S * fs, NM)

        fr, Pxx = sg.welch(Ee, fs, nperseg=min(T.NPERSEG, T.EPOCH_S * fs), axis=1)
        bp = lambda lo, hi: _trapz(Pxx[:, (fr >= lo) & (fr < hi), :],
                                     fr[(fr >= lo) & (fr < hi)], axis=1)
        delta[i0:i0 + n] = bp(*T.BAND_DELTA)
        theta[i0:i0 + n] = bp(*T.BAND_THETA)
        tot[i0:i0 + n] = bp(*T.BAND_TOTAL)
        eeg_rms[i0:i0 + n] = Ee.std(1)
        emg_rms[i0:i0 + n] = Mm_.std(1)
        eeg_mains[i0:i0 + n] = Xee.std(1)
        emg_mains[i0:i0 + n] = Xmm.std(1)
        eeg_clip[i0:i0 + n] = (np.abs(raw_e) >= T.RAIL_UV_EFF).mean(1)
        s = e
        print(f"  extract {100 * s / (nep * T.EPOCH_S):5.1f}%", end="\r", flush=True)
    del mm
    print(" " * 30, end="\r")

    d = dict(delta=delta, theta=theta, tot=tot, eeg_rms=eeg_rms,
             eeg_mains=eeg_mains, eeg_clip=eeg_clip, emg_rms=emg_rms,
             emg_mains=emg_mains, fs=fs, hours=info["hours"],
             start_utc=info["start_utc"], base=base,
             labels_json=json.dumps(labels))
    np.savez_compressed(out, **d)
    d["labels"] = labels
    return d


# ---------------------------------------------------------------------------
def gate(d, i):
    """The QC gate for one animal. Returns (ok_mask, diagnostics)."""
    eeg_mains, emg_mains = d["eeg_mains"][:, i], d["emg_mains"][:, i]
    eeg_rms, eeg_clip = d["eeg_rms"][:, i], d["eeg_clip"][:, i]
    delta, theta, emg_rms = d["delta"][:, i], d["theta"][:, i], d["emg_rms"][:, i]

    not_open = (eeg_mains < T.OPEN_UV) & (emg_mains < T.OPEN_UV)
    not_flat = eeg_rms >= T.FLAT_UV
    not_clip = eeg_clip <= T.CLIP_FRAC
    finite = (delta > 0) & (theta > 0) & (emg_rms > 0)
    ok = not_open & not_flat & not_clip & finite

    diag = dict(
        pct_not_open=round(100 * float(not_open.mean()), 2),
        pct_not_flat=round(100 * float(not_flat.mean()), 2),
        pct_not_clip=round(100 * float(not_clip.mean()), 2),
        pct_pass=round(100 * float(ok.mean()), 2),
        med_eeg_mains_uv=round(float(np.median(eeg_mains)), 1),
        med_emg_mains_uv=round(float(np.median(emg_mains)), 1),
        med_eeg_rms_uv=round(float(np.median(eeg_rms)), 1),
        med_emg_rms_uv=round(float(np.median(emg_rms)), 1),
        pct_epochs_railed=round(100 * float((eeg_clip > 0).mean()), 2),
    )
    return ok, diag


def qc_one(d, i, label):
    ok, diag = gate(d, i)
    blks = P.blocks_of(ok)
    long_blks = [(a, b) for a, b in blks if (b - a) >= T.MIN_BLOCK]
    gated_h = ok.sum() * T.EPOCH_S / 3600
    block_h = sum(b - a for a, b in long_blks) * T.EPOCH_S / 3600

    R = dict(port=label["port"], slot=label["slot"], name=label["name"],
             gated_hours=round(float(gated_h), 3),
             block_hours=round(float(block_h), 3),
             n_blocks=len(blks), n_long_blocks=len(long_blks),
             longest_block_min=round(max((b - a for a, b in blks), default=0)
                                     * T.EPOCH_S / 60, 1),
             median_block_s=int(np.median([b - a for a, b in blks]) * T.EPOCH_S)
             if blks else 0,
             **diag)

    # ---- channel-level failure modes, checked before anything epoch-level ---
    if diag["med_eeg_rms_uv"] < T.DEAD_CHANNEL_UV:
        R["verdict"] = "DEAD"
        R["reason"] = (f"channel median EEG rms {diag['med_eeg_rms_uv']} uV "
                       f"< {T.DEAD_CHANNEL_UV} uV: never carried EEG")
        return R
    if diag["pct_not_open"] < 5.0:
        R["verdict"] = "OPEN"
        R["reason"] = (f"electrode open for {100 - diag['pct_not_open']:.1f}% of "
                       f"the recording (median mains {diag['med_eeg_mains_uv']} uV "
                       f"vs {T.OPEN_UV} uV limit)")
        return R
    if diag["pct_not_clip"] < 5.0:
        R["verdict"] = "CLIPPED"
        R["reason"] = f"amplifier railed in {100 - diag['pct_not_clip']:.1f}% of epochs"
        return R

    if block_h * 60 < T.MIN_BLOCK_MINUTES:
        R["verdict"] = "INSUFFICIENT"
        R["reason"] = (f"only {block_h * 60:.1f} min inside blocks >= "
                       f"{T.MIN_BLOCK * T.EPOCH_S} s "
                       f"(need {T.MIN_BLOCK_MINUTES:.0f} min); "
                       f"question cannot be asked, this is not a negative result")
        return R

    # ---- clean vs dirty ----------------------------------------------------
    frag = block_h / gated_h if gated_h > 0 else 0.0
    R["consolidation"] = round(float(frag), 3)
    if diag["pct_pass"] >= 90.0 and frag >= 0.9:
        R["verdict"] = "CLEAN"
        R["reason"] = (f"{diag['pct_pass']:.1f}% of epochs pass all tests, "
                       f"{frag * 100:.0f}% of usable time is in long blocks, "
                       f"mains {diag['med_eeg_mains_uv']} uV")
    else:
        R["verdict"] = "DIRTY"
        R["reason"] = (f"usable but fragmented: {diag['pct_pass']:.1f}% of epochs "
                       f"pass, {len(blks)} contact blocks, median block "
                       f"{R['median_block_s']} s")
    return R


# ---------------------------------------------------------------------------
def qc_recording(base, force=False):
    d = extract_features(base, force=force)
    if d is None:
        return None
    meta = P.load_meta(base)
    info = P.recording_info(base, meta)
    local, src = P.parse_start_local(base, info["start_utc"])
    labels = d["labels"]

    animals = [qc_one(d, i, lab) for i, lab in enumerate(labels)]
    return dict(recording=base, hours=round(float(info["hours"]), 3),
                fs=int(info["fs"]),
                start_utc=info["start_utc"],
                start_local=local.isoformat(), start_source=src,
                day=f"{local:%Y-%m-%d}",
                thresholds=dict(open_uv=T.OPEN_UV, flat_uv=T.FLAT_UV,
                                dead_uv=T.DEAD_CHANNEL_UV,
                                clip_frac=T.CLIP_FRAC,
                                rail_uv=round(T.RAIL_UV_EFF, 1),
                                epoch_s=T.EPOCH_S),
                animals=animals)


def print_table(res):
    print(f"\n{res['recording']}  {res['hours']:.2f} h  "
          f"start {res['start_local']} ({res['start_source']})  day={res['day']}")
    print(f"{'mouse':<7}{'port':<6}{'slot':<6}{'pass%':>8}{'gated_h':>9}"
          f"{'block_h':>9}{'longest_m':>11}{'mains_uV':>10}{'rms_uV':>8}  verdict")
    print("-" * 118)
    for a in res["animals"]:
        print(f"{a['name']:<7}{a['port']:<6}{a['slot']:<6}{a['pct_pass']:>8.2f}"
              f"{a['gated_hours']:>9.2f}{a['block_hours']:>9.2f}"
              f"{a['longest_block_min']:>11.1f}{a['med_eeg_mains_uv']:>10.1f}"
              f"{a['med_eeg_rms_uv']:>8.1f}  {a['verdict']}")
        print(f"{'':<7}{'':<6}{'':<6}  -> {a['reason']}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("bases", nargs="*")
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--json", default=None)
    a = ap.parse_args()

    bases = a.bases
    if a.all:
        import glob
        bases = sorted(os.path.basename(f).replace(".xdat.json", "")
                       for f in glob.glob(os.path.join(P.DATA_DIR, "*.xdat.json")))
    out = []
    for b in bases:
        try:
            r = qc_recording(b, force=a.force)
        except Exception as exc:                      # noqa: BLE001
            print(f"[skip] {b}: {exc}")
            continue
        if r is None:
            print(f"[skip] {b}: no animals in layout")
            continue
        out.append(r)
        print_table(r)
    if a.json:
        json.dump(out, open(a.json, "w"), indent=1, default=P.jsafe)
        print(f"\n[json] {a.json}")


if __name__ == "__main__":
    main()
