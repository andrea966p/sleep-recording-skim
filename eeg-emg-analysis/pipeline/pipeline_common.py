#!/usr/bin/env python3
"""Shared helpers: layout derivation, naming, time handling, block maths."""
import datetime as dt
import json
import os
import re

import numpy as np

from core import qc_thresholds as T
from core import paths as PATHS

DATA_DIR = str(PATHS.RAW_ROOT) + os.sep


# ---------------------------------------------------------------------------
# layout
# ---------------------------------------------------------------------------
def load_meta(base):
    return json.load(open(os.path.join(DATA_DIR, base + ".xdat.json")))


def derive_layout(meta):
    """Return (labels, eeg_cols, emg_cols) read from the file's own metadata.

    NEVER assume 64 channels per port. Recordings exist at 32 ch/port (one
    animal), 64 ch/port (two animals behind a splitter) and mixed layouts such
    as A:64@0 B:32@64 C:64@96 D:64@160. Assuming a layout mis-maps every
    older file.
    """
    sbp = meta["sapiens_base"]["sensors_by_port"]
    labels, eeg, emg = [], [], []
    for port in sorted(sbp):
        s = sbp[port]
        n = s.get("num_channels")
        base = s.get("connection_ntv_idx")
        offsets = [0, 32] if n >= 64 else [0]
        for slot, off in enumerate(offsets, start=1):
            labels.append({"port": port, "slot": slot, "name": f"{port}{slot}"})
            eeg.append(base + off)      # /1 = EEG, bipolar, use directly
            emg.append(base + off + 1)  # /2 = EMG, bipolar, use directly
    return labels, eeg, emg


def recording_info(base, meta):
    st = meta["status"]
    fs = int(st["samp_freq"])
    n_samp = int(st["num_smpl"])
    n_chan = int(st["signals"]["total"])
    start_utc = st.get("start_time", "")
    return dict(fs=fs, n_samp=n_samp, n_chan=n_chan, hours=n_samp / fs / 3600,
                start_utc=start_utc, base=base)


# ---------------------------------------------------------------------------
# time
# ---------------------------------------------------------------------------
def parse_start_local(base, start_utc):
    """Local (KST) start time.

    Prefer the UTC timestamp in the metadata and convert. Fall back to the
    uidMMDD-HH-MM-SS token in the filename, which Allego already writes in
    LOCAL time -- mixing the two is how a recording lands in the wrong day
    folder, so the source actually used is returned alongside.
    """
    if start_utc:
        s = start_utc.replace("Z", "+00:00")
        try:
            t = dt.datetime.fromisoformat(s)
            if t.tzinfo is None:
                t = t.replace(tzinfo=dt.timezone.utc)
            local = t.astimezone(dt.timezone(dt.timedelta(hours=T.TZ_OFFSET_HOURS)))
            return local, "metadata_utc"
        except ValueError:
            pass
    m = re.search(r"uid(\d{2})(\d{2})-(\d{2})-(\d{2})-(\d{2})", base)
    if m:
        mo, da, hh, mi, ss = (int(x) for x in m.groups())
        year = 2026
        return dt.datetime(year, mo, da, hh, mi, ss,
                           tzinfo=dt.timezone(dt.timedelta(hours=T.TZ_OFFSET_HOURS))), "filename_uid"
    raise ValueError(f"cannot determine start time for {base}")


def zt_hours(local_dt, offsets_s):
    """Zeitgeber time in hours for an array of second offsets from start.

    ZT0 = lights on = 09:00 KST. Returns values in [0, 24).
    """
    start_h = local_dt.hour + local_dt.minute / 60 + local_dt.second / 3600
    return (start_h - T.LIGHTS_ON_HOUR + np.asarray(offsets_s) / 3600.0) % 24.0


def is_light(zt):
    return np.asarray(zt) < (T.LIGHTS_OFF_HOUR - T.LIGHTS_ON_HOUR)


def fmt_duration(hours):
    total_min = int(round(hours * 60))
    return f"{total_min // 60:d}h{total_min % 60:02d}m"


def mouse_filename(port, slot, local_dt, hours, ext):
    """port + slot + date + start time + total length, as requested."""
    return (f"port{port}-slot{slot}"
            f"_{local_dt:%Y-%m-%d}"
            f"_{local_dt:%H%M%S}"
            f"_{fmt_duration(hours)}{ext}")


def day_folder(root, local_dt):
    return os.path.join(root, f"{local_dt:%Y-%m-%d}")


# ---------------------------------------------------------------------------
# blocks
# ---------------------------------------------------------------------------
def blocks_of(ok):
    """Contiguous runs of True as (start, stop) pairs, stop exclusive."""
    idx = np.where(ok)[0]
    if len(idx) == 0:
        return []
    brk = np.where(np.diff(idx) > 1)[0]
    starts = np.concatenate(([0], brk + 1))
    stops = np.concatenate((brk + 1, [len(idx)]))
    return [(int(idx[a]), int(idx[b - 1] + 1)) for a, b in zip(starts, stops)]


def otsu_threshold(v, bins=48):
    """Two-class split by maximising between-class variance. Per animal only."""
    hist, edges = np.histogram(v, bins=bins)
    cen = (edges[:-1] + edges[1:]) / 2
    w = hist.astype(float)
    best, thr = -1.0, float(np.median(v))
    for k in range(4, bins - 4):
        w0, w1 = w[:k].sum(), w[k:].sum()
        if w0 < 20 or w1 < 20:
            continue
        m0 = (w[:k] * cen[:k]).sum() / w0
        m1 = (w[k:] * cen[k:]).sum() / w1
        val = w0 * w1 * (m0 - m1) ** 2
        if val > best:
            best, thr = val, cen[k]
    return thr


def within_block_persistence(sleep, blocks, lag=T.LAG, rng=None):
    """Autocorrelation at `lag`, computed strictly WITHIN unbroken blocks.

    Every product pairs two epochs genuinely `lag` epochs apart in REAL time.
    Blocks shorter than the lag contribute nothing rather than silently
    contributing a cross-gap pair. The shuffle permutes within blocks, so it
    isolates temporal ordering while preserving block structure and sleep
    fraction.
    """
    num = den = nums = dens = 0.0
    pairs = used = 0
    rng = rng or np.random.default_rng(0)
    for a, b in blocks:
        seg = np.asarray(sleep[a:b], dtype=float)
        if len(seg) < lag + 1:
            continue
        used += 1
        x = seg - seg.mean()
        if not np.any(x):
            continue
        num += float((x[:-lag] * x[lag:]).sum())
        den += float((x * x).sum())
        pairs += len(seg) - lag
        xs = rng.permutation(seg)
        xs = xs - xs.mean()
        nums += float((xs[:-lag] * xs[lag:]).sum())
        dens += float((xs * xs).sum())
    return (num / den if den > 0 else np.nan, pairs, used,
            nums / dens if dens > 0 else np.nan)


def bout_lengths(labels, val):
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


def jsafe(o):
    if isinstance(o, (np.integer,)):
        return int(o)
    if isinstance(o, (np.floating,)):
        return None if not np.isfinite(o) else float(o)
    if isinstance(o, np.ndarray):
        return o.tolist()
    if isinstance(o, (dt.datetime,)):
        return o.isoformat()
    raise TypeError(f"{type(o)} not serialisable")
