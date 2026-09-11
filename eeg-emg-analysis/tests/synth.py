#!/usr/bin/env python3
"""Write synthetic Allego recordings with KNOWN ground truth.

WHY THIS EXISTS. Every test in this repo until 2026-08-10 compared the pipeline
against numbers the pipeline itself had produced earlier. That proves the code
did not change. It cannot prove the code is right, and it would have stayed green
through the entire hum-criterion era, when a floating unreferenced amplifier
input was being reported as 100 percent usable EEG.

A test that can only pass is not evidence. This module builds recordings whose
answers are known BEFORE the pipeline runs, including channels designed to fool
the criterion, so `test_criterion_falsification.py` can assert what the engine
must REJECT as well as what it must accept.

The file format is the real one -- `<base>.xdat.json`, `<base>_data.xdat`
(float32, sample-major, microvolts) and `<base>_timestamp.xdat` (int64) -- so the
engine reads it through exactly the same `open_xdat` path as a real recording. No
test double, no monkeypatching, no second code path that could itself be wrong.

TWO CONSTRUCTION FACTS THAT COST AN AFTERNOON, WRITTEN DOWN SO THEY ARE NOT
REDISCOVERED:

1. AMPLITUDE MUST BE SET ON THE QUANTITY THE ENGINE MEASURES. `compute_features`
   takes the standard deviation of each 10 s epoch after removing that epoch's
   mean. For 1/f**1.8 noise most of the variance sits below 0.1 Hz, so a 10 s
   window that has had its mean removed keeps only a fraction of the global
   standard deviation -- pink noise scaled to a global 50 uV measures about
   6 uV per epoch, lands under RMS_LO_UV, and is rejected on AMPLITUDE while the
   slope criterion was calling it usable in 100% of epochs. Scaling naively
   therefore tests the amplitude window and silently never tests the criterion.
   `scale_to_epoch_rms` fixes this by measuring the way the engine measures.

2. THE FLOOR IS SITES /3 TO /16 IN A TWO-ROLE COHORT. Anything parked there is a
   control, not a test case. A "trap" channel placed at A/3 becomes part of the
   floor that defines the threshold it is then tested against. Each adversarial
   channel therefore gets its OWN recording, sitting at A/1 where a real
   electrode would be.
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
from scipy import signal as sg

FS = 1000
EPOCH_S = 10          # must match T.EPOCH_S_QC; asserted by the test module


# --------------------------------------------------------------------------- #
# noise shapes
# --------------------------------------------------------------------------- #

def pink(n: int, rng: np.random.Generator, exponent: float = 1.8) -> np.ndarray:
    """Noise with a 1/f**exponent power spectrum: the shape real EEG has.

    Built in the frequency domain so the log-log slope is exactly -exponent by
    construction, rather than approximated by a filter cascade whose own roll-off
    would then need testing.
    """
    f = np.fft.rfftfreq(n, 1 / FS)
    amp = np.zeros_like(f)
    amp[1:] = f[1:] ** (-exponent / 2.0)          # amplitude, hence /2
    spec = amp * (rng.normal(size=f.size) + 1j * rng.normal(size=f.size))
    return np.fft.irfft(spec, n=n)


def white(n: int, rng: np.random.Generator) -> np.ndarray:
    return rng.normal(size=n)


def bandlimited_white(n: int, rng: np.random.Generator,
                      lo: float = 0.5, hi: float = 30.0) -> np.ndarray:
    """THE TRAP. A wire-free input put through the EEG band-pass.

    The project's own README says this "looks like beautiful EEG, about 69 uV of
    it", and that judging it by eye is how an unconnected channel gets published.
    The criterion must reject it on its spectrum, with no help from the eye.
    """
    sos = sg.butter(4, [lo, hi], btype="band", fs=FS, output="sos")
    return sg.sosfiltfilt(sos, rng.normal(size=n))


def mains(n: int, amp_uv: float) -> np.ndarray:
    t = np.arange(n) / FS
    return amp_uv * np.sin(2 * np.pi * 60.0 * t)


def epoch_rms(x: np.ndarray) -> float:
    """Median per-epoch rms, measured EXACTLY as compute_features measures it."""
    ep = FS * EPOCH_S
    nep = len(x) // ep
    blk = x[:nep * ep].reshape(nep, ep)
    return float(np.median((blk - blk.mean(1, keepdims=True)).std(1)))


def scale_to_epoch_rms(x: np.ndarray, target_uv: float) -> np.ndarray:
    """Scale so the MEDIAN PER-EPOCH rms is target_uv. See construction fact 1."""
    cur = epoch_rms(x)
    if cur <= 0:
        raise ValueError("signal has no per-epoch variance to scale")
    return x * (target_uv / cur)


# --------------------------------------------------------------------------- #
# writing a recording
# --------------------------------------------------------------------------- #

def write(base: str | Path, channels: dict[str, np.ndarray], *,
          start_time_utc: str = "2026-08-10T00:00:00.000Z") -> str:
    """Write one synthetic recording. `channels` maps site label -> microvolts.

    Site labels use the real `PORT/NUMBER` form and are written into the
    biointerface_map exactly as Allego writes them, because `open_xdat` derives
    the layout from that map and must never be handed a shortcut.
    """
    base = str(base)
    sites = list(channels)
    n = len(next(iter(channels.values())))
    if any(len(v) != n for v in channels.values()):
        raise ValueError("all channels must be the same length")

    meta = {
        "status": {"samp_freq": FS, "start_time": start_time_utc,
                   "num_sig": len(sites)},
        "sapiens_base": {"biointerface_map": {
            "port": [s.split("/")[0] for s in sites],
            "site_num": [int(s.split("/")[1]) for s in sites],
            "ntv_chan_name": [f"ntv{i}" for i in range(len(sites))]}},
        "synthetic": True,
        "generated_by": "tests/synth.py -- NOT A RECORDING OF AN ANIMAL",
    }
    Path(base + ".xdat.json").write_text(json.dumps(meta, indent=1))

    arr = np.empty((n, len(sites)), dtype=np.float32)
    for i, s in enumerate(sites):
        arr[:, i] = channels[s].astype(np.float32)
    arr.tofile(base + "_data.xdat")
    np.arange(n, dtype=np.int64).tofile(base + "_timestamp.xdat")
    return base


def realistic_floor(n: int, rng: np.random.Generator) -> np.ndarray:
    """A wire-free amplifier input: spectrally flat, and LOUD with mains.

    Matches what this rig measures on unwired inputs -- a 60 Hz median of roughly
    2,000 to 4,000 uV against a flat spectrum. The floor must be realistic or the
    1st-percentile thresholds derived from it mean nothing.
    """
    return scale_to_epoch_rms(white(n, rng), 200.0) + mains(n, 3000.0)


def build(base: str | Path, a1: np.ndarray, *, seconds: int = 1800,
          seed: int = 20260810, a2: np.ndarray | None = None) -> str:
    """One port, one animal, 14 wire-free floor channels.

    `a1` is the channel under test, sitting where a real EEG electrode sits.
    `a2` defaults to a broadband EMG-like channel at 40 uV.

    Layout, which is `CohortSpec(roles=("eeg","emg"), ports="A", slot_bases=(1,))`:
        A/1        the channel under test        (the EEG role)
        A/2        broadband, EMG-like           (the EMG role)
        A/3..A/16  wire-free floor               (14 control sites)
    """
    rng = np.random.default_rng(seed)
    n = seconds * FS
    if len(a1) != n:
        raise ValueError(f"a1 has {len(a1)} samples, expected {n}")
    ch = {"A/1": a1,
          "A/2": a2 if a2 is not None
          else scale_to_epoch_rms(white(n, rng), 40.0)}
    for i in range(3, 17):
        ch[f"A/{i}"] = realistic_floor(n, rng)
    return write(base, ch)


# --------------------------------------------------------------------------- #
# the four channels under test, each with its answer stated here
# --------------------------------------------------------------------------- #

def connected_eeg(n: int, rng: np.random.Generator, rms_uv: float = 50.0):
    """Steep 1/f at a plausible amplitude. MUST be usable."""
    return scale_to_epoch_rms(pink(n, rng, 1.8), rms_uv)


def trap_bandpassed(n: int, rng: np.random.Generator, rms_uv: float = 69.0):
    """No wire, band-passed into the EEG band. Looks perfect. MUST be rejected."""
    return scale_to_epoch_rms(bandlimited_white(n, rng), rms_uv)


def floating_no_ground(n: int, rng: np.random.Generator):
    """The A1 signature: QUIET because a floating bipolar pair rejects mains as
    common mode, and FLAT because it carries no biology. The hum criterion
    rewards quiet and so calls this excellent; the slope criterion calls it dead.
    `usable()` MUST refuse rather than report either."""
    return scale_to_epoch_rms(white(n, rng), 60.0) + mains(n, 50.0)


def railed(n: int, _rng: np.random.Generator):
    """Pinned at the ADC ceiling. MUST be rejected."""
    return np.full(n, 6389.5)


# --------------------------------------------------------------------------- #
# a STRUCTURALLY COMPLETE sidecar, for the channel stripper
# --------------------------------------------------------------------------- #
# `write()` above is deliberately minimal -- it carries only the three fields
# `open_xdat` reads, and four falsification tests depend on it, so it must not
# change. The stripper, by contrast, rewrites the WHOLE biointerface_map, recounts
# status.signals, prunes the neighbourhood graph and recomputes dataset_checksum,
# so testing it against the minimal sidecar would exercise almost none of that.
#
# This writes the real shape instead: all 35 per-channel arrays plus the scalar
# samp_freq, the four signal counts, a site_hood graph, and a dataset_checksum
# computed with the MEASURED formula sha256(data || timestamp). Field names and
# value types were taken from allego_3__uid0828-09-26-12 on 2026-09-11.

_PRI, _AUX, _DIN, _DOUT = "ai0", "ai4", "din0", "dout0"
_TYPE_UNITS = {_PRI: "micro-volts", _AUX: "volts", _DIN: "binary", _DOUT: "binary"}


def gpio_labels() -> list[tuple[str, str]]:
    """The six non-primary channels every real recording on this rig carries.

    Note the site numbers COLLIDE by design -- both aux are GPIO-AIN/0 -- which
    is why the stripper refuses to select GPIO by label.
    """
    return [("GPIO-AIN/0", _AUX), ("GPIO-AIN/0", _AUX),
            ("GPIO-DIN/0", _DIN), ("GPIO-DIN/0", _DIN),
            ("GPIO-DOUT/0", _DOUT), ("GPIO-DOUT/0", _DOUT)]


def write_full_sidecar(base: str | Path,
                       channels: dict[str, np.ndarray] | list[tuple[str, np.ndarray]],
                       *,
                       chan_types: list[str] | None = None,
                       selected: list[bool] | None = None,
                       start_time_utc: str = "2026-09-11T00:00:00.000Z",
                       fs: int = FS,
                       headstage_id: str = "hstg__passthrough_64",
                       probe_id: str = "probe__default_8x8",
                       extra_array: str | None = None,
                       biointerface_spec=None) -> str:
    """Write a synthetic recording with a structurally complete sidecar.

    `channels` may be a list of (label, samples) pairs, so DUPLICATE labels are
    expressible -- the GPIO collision is a real property of the format and the
    stripper must be tested against it.

    `extra_array` adds a 36th per-channel array, to prove the stripper carries an
    unknown field rather than dropping it. `biointerface_spec` sets the field the
    stripper must REFUSE on.
    """
    base = str(base)
    items = list(channels.items()) if isinstance(channels, dict) else list(channels)
    labels = [lab for lab, _ in items]
    n = len(items[0][1])
    if any(len(v) != n for _, v in items):
        raise ValueError("all channels must be the same length")
    k = len(items)

    if chan_types is None:
        chan_types = [_PRI] * k
    if selected is None:
        selected = [t == _PRI for t in chan_types]
    if not (len(chan_types) == len(selected) == k):
        raise ValueError("chan_types and selected must match the channel count")

    ports = [lab.split("/")[0] for lab in labels]
    sites = [int(lab.split("/")[1]) for lab in labels]

    # ntv_chan_idx restarts at 0 per TYPE, exactly as Allego writes it
    ntv, per_type = [], {}
    for t in chan_types:
        ntv.append(per_type.get(t, 0))
        per_type[t] = per_type.get(t, 0) + 1

    names = []
    counters = {_PRI: 0, _AUX: 1, _DIN: 1, _DOUT: 1}
    for t in chan_types:
        if t == _PRI:
            names.append(f"pri_{counters[_PRI]}"); counters[_PRI] += 1
        else:
            stem = {_AUX: "aux", _DIN: "din", _DOUT: "dout"}[t]
            names.append(f"{stem}_{counters[t]}"); counters[t] += 1

    bm = {
        "chan_name": names,
        "chan_type": list(chan_types),
        "ntv_chan_idx": ntv,
        "ntv_chan_name": [f"port_{p}_{i}" for p, i in zip(ports, ntv)],
        "sys_chan_idx": list(range(k)),
        "absolute_idx": list(range(k)),
        "port": ports,
        "site_num": sites,
        "sensor_units": ["um"] * k,
        "site_shape": ["circle"] * k,
        "site_area": [254.469004940773] * k,
        "is_audio": [False] * k,
        "is_audio_left": [False] * k,
        "is_audio_right": [False] * k,
        "is_selected": [bool(b) for b in selected],
        "dsrc_uid": ["null________________________________"] * k,
        "sensor_uid": [f"{headstage_id}/{probe_id}.synthetic"] * k,
        "headstage_id": [headstage_id] * k,
        "probe_id": [probe_id] * k,
        "color_grp_idx": [2147483647] * k,
        "samp_freq": None,                      # the one scalar
    }
    for g in ("site_ctr_x", "site_ctr_y", "site_ctr_z",
              "site_ctr_tcs_x", "site_ctr_tcs_y", "site_ctr_tcs_z",
              "site_lim_x_min", "site_lim_x_max", "site_lim_y_min",
              "site_lim_y_max", "site_lim_z_min", "site_lim_z_max",
              "scs_to_tcs_x", "scs_to_tcs_y", "scs_to_tcs_z"):
        bm[g] = [float(i) for i in range(k)]
    if extra_array:
        bm[extra_array] = [f"x{i}" for i in range(k)]

    counts = {"pri": 0, "aux": 0, "din": 0, "dout": 0}
    for t in chan_types:
        counts[{_PRI: "pri", _AUX: "aux", _DIN: "din", _DOUT: "dout"}[t]] += 1

    hood = {}
    for i, t in enumerate(chan_types):
        if t != _PRI:
            continue
        friends = [{"ntv_chan_idx": ntv[j], "site_num": sites[j],
                    "radius_um": 40, "theta_deg": 90, "phi_deg": 90}
                   for j in range(k)
                   if j != i and chan_types[j] == _PRI and ports[j] == ports[i]]
        hood[str(ntv[i])] = {"home_ntv_chan_idx": ntv[i], "home_chan_nam": names[i],
                             "home_site_num": sites[i], "port": ports[i],
                             "max_radius": 500, "friends": friends}

    # data first: the checksum is over the bytes, so they must exist
    arr = np.empty((n, k), dtype=np.float32)
    for i, (_, v) in enumerate(items):
        arr[:, i] = np.asarray(v, dtype=np.float32)
    arr.tofile(base + "_data.xdat")
    np.arange(n, dtype=np.int64).tofile(base + "_timestamp.xdat")

    import hashlib
    h = hashlib.sha256()
    for suffix in ("_data.xdat", "_timestamp.xdat"):     # MEASURED order
        with open(base + suffix, "rb") as fh:
            for blk in iter(lambda: fh.read(1 << 20), b""):
                h.update(blk)

    meta = {
        "status": {
            "t_range": [0.0, n / fs], "samp_freq": fs, "shape": [n, k],
            "num_smpl": n,
            "signals": {"total": k, **counts},
            "timestamp_range": [0, n - 1], "dur": n / fs,
            "start_time": start_time_utc,
            "dataset_uid": "synthetic-0000-0000-0000-000000000000",
            "dataset_checksum": h.hexdigest(),
            "dataset_provenance": [], "user_label": "", "user_tags": "",
            "ext": {}, "is_live_recording": False,
        },
        "sapiens_base": {
            "biointerface_map": bm,
            "biointerface_spec": biointerface_spec,
            "biointerface_ancillary": {"sapiens_import_spec": {},
                                       "datafile_name": "", "annotate_bundle": {},
                                       "notes": "", "DSPfilter": {}},
            "neighborhoods": {"datasource_id": "", "site_hood": hood,
                              "max_radius": 500, "spatial_units": ""},
            "sigUnits": {f"sig_units_{g}": _TYPE_UNITS[t] for g, t in
                         (("pri", _PRI), ("aux", _AUX), ("din", _DIN), ("dout", _DOUT))},
            "sensors_by_port": {p: {"num_channels": 64, "headstage_id": headstage_id,
                                    "probe_id": probe_id, "connection_ntv_idx": 0}
                                for p in sorted(set(ports))},
            "zcheck_spec": {p: {"Zmag": None} for p in sorted(set(ports))},
            "port_map": {"port": None},
            "digital_out_spec": {"mode": ""},
        },
        "radiens_sen_ext": {"spec": None},
        "radiens_proj_ext": {"spec": None},
        "SapiensBiointerface": {"spec": None},
        "synthetic": True,
        "generated_by": "tests/synth.py write_full_sidecar -- NOT AN ANIMAL",
    }
    Path(base + ".xdat.json").write_text(json.dumps(meta, separators=(",", ":")))
    return base
