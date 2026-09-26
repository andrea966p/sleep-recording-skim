#!/usr/bin/env python3
"""THE connection criterion. One implementation, used by everything.

WHAT THIS REPLACES
------------------
Before 2026-08-09 the same per-epoch loop existed three times:
  qc/usable_fraction_vs_floor.py       hum criterion, 2-role cohort
  qc/usable_fraction_vs_floor_ecg.py   hum + slope, 3-role cohort
  qc/plot_usable_timeline.py           a third inline copy with its own literals
and the filter chain existed five times, copy-pasted verbatim. Three copies of a
criterion is three criteria, because they drift. This module is the only one.

WHAT THE CRITERION IS
---------------------
A channel is judged per QC epoch against WIRE-FREE AMPLIFIER INPUTS RECORDED IN
THE SAME FILE. A mouse uses only a few of its chip's 16 inputs; the rest are
real inputs with no wire, going through the same amplifier, cable and room. They
are a free, simultaneous, perfect negative control.

Two criteria exist. BOTH ARE ALWAYS COMPUTED. You choose which one is reported.

  SLOPE  (default, and the safe one ON RAW DATA)
      log-log spectral slope over 1-40 Hz below the 1st percentile of the floor,
      plus rms in 10-150 uV, plus zero railed samples.
      Real EEG is steep, an unwired input is flat, and the band carries no mains
      harmonic, so it needs no notch. This is the criterion to use unless you
      have a reason not to.

      🔴 CORRECTED 2026-08-10. This docstring used to claim "FILTERING CANNOT
      MANUFACTURE SLOPE". IT CAN, and tests/test_criterion_falsification.py
      demonstrates it: a wire-free input put through the 0.5-30 Hz EEG band-pass
      measures a slope of -1.08 over 1-40 Hz, against 0.00 raw and -1.81 for
      real 1/f^1.8 EEG, and therefore scores 100.0 PERCENT USABLE. The 30 Hz
      filter corner lies inside the measurement band and its roll-off is read as
      slope. Filtering manufactures slope whenever a corner sits in the band.

      This never affected a published number, because compute_features reads the
      raw memmap and filters nothing. It is a live trap for anyone who feeds
      this function a cleaned signal, which is one line away at any time, so the
      precondition is now ENFORCED rather than documented -- see
      `check_bandlimit_validity`.

  HUM   (valid only on some cohorts, and the module checks)
      60 Hz amplitude below the 1st percentile of the floor, same rms and
      railing conditions. Works while connected and open channels sit in two
      separated modes, which was true of the original EEG+EMG cohort by a factor
      of about 100.

🔴 THE HUM CRITERION CAN BE CONFIDENTLY WRONG. An animal recording with no
ground at all scored 100.0 percent usable on hum and 0.0 percent on slope, on
the same epochs, because a floating bipolar pair rejects mains as common mode
and is therefore QUIET, and the hum criterion rewards quiet. `usable()` refuses
to return a hum number for any channel showing that contradiction. The refusal
is a hard error on purpose: the alternative is a publishable wrong number.

🛑 SLOPE JUDGES EEG, NOT EMG. Real EMG is broadband and therefore flat, so a
slope criterion applied to an EMG channel is a category error and will call a
working muscle channel dead. `usable()` raises if you try it. EMG connection is
judged on hum plus rms, or on state dependence against the EEG.

UNITS: everything is microvolts. Epochs are EPOCH_S_QC = 10 s, NOT the 4 s
staging epoch. A usable fraction at 10 s and one at 4 s are different numbers.
"""
from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Iterable, Sequence

import numpy as np

from core import qc_thresholds as T

# --------------------------------------------------------------------------- #
# cohort geometry
# --------------------------------------------------------------------------- #

CHIP_REAL_CHANNELS = 16
# THE DEFAULT, NOT A LAW. An RHD2216 exposes 16 amplifiers; on a C3442-split port
# each chip occupies 32 native slots, of which only the first 16 are real. Sites
# beyond 16 on such a chip (/17-/32, /49-/64) are INACTIVE and internally tied:
# they read low almost always, so including them in a floor would flatter the
# control and condemn every real animal. They are excluded by construction below,
# not by a filter.
#
# 🔴 THIS IS AN RHD2216 PROPERTY AND IT DOES NOT GENERALISE. An RHD2132 is 32
# REAL unipolar inputs, which is why the 2026-08-05 unipolar prep carries signal
# on /18../23 -- sites this constant would call inactive. Until 2026-09-14 the
# comment above stated the 16 as universal and the repo therefore held two
# contradictory claims about those six sites. Per-chip truth now lives in
# `ChipSpec.real_channels`; this constant is only its default.
#
# ⚠️ A larger `real_channels` does NOT mean a floor can be derived. On the
# unipolar headstage the unused real inputs are TIED TO GROUND (median 0.17 MOhm,
# measured 2026-08-05), so a floor built from them would flatter the control in
# exactly the way the inactive slots do. Such a chip must declare `floor=()` with
# a reason. See ChipSpec.

PORTS_DEFAULT = "ABCD"
SLOT_BASES_DEFAULT = (1, 33)   # site number of the first channel of each slot


class LayoutError(RuntimeError):
    """A rig layout that cannot be judged. Never guessed around."""


@dataclass(frozen=True)
class ChipSpec:
    """One amplifier chip: its animal sites, and the wire-free floor beside them.

    A 64-channel port carries TWO of these (a C3442 splitter, bases 1 and 33); a
    32-channel port carries one (base 1). This is the unit the floor belongs to,
    because "through the same chip" is what the usable-fraction definition means.

    `floor` has three meanings and they are not interchangeable:

        None     derive `base+n .. base+real_channels-1`. PERMITTED ONLY when the
                 role sites are exactly base+0 .. base+n-1, because that is the
                 only arrangement the derivation describes. Anything else raises
                 rather than silently producing a plausible wrong answer.
        (a,b,..) use these absolute site numbers, validated.
        ()       THIS CHIP HAS NO FLOOR. Requires `floor_reason`.

    🔑 The empty case is not "the model does not fit". It is "no characterised
    wire-free control exists here", and the distinction decides what a future
    reader does about it. On the unipolar RHD2132 a floor COULD be derived from
    its 26 unused real inputs -- and must not be, because those inputs are tied
    to ground and would flatter the control. Encoding that as a shape mismatch
    invites someone to fix the shape; encoding it as absent evidence does not.
    """
    base: int
    role_sites: tuple[tuple[str, int], ...]      # (role, ABSOLUTE site number)
    real_channels: int = CHIP_REAL_CHANNELS
    floor: tuple[int, ...] | None = None
    floor_reason: str = ""

    def __post_init__(self):
        if not self.role_sites:
            raise LayoutError(f"chip at base {self.base} declares no roles")
        roles = [r for r, _ in self.role_sites]
        if len(set(roles)) != len(roles):
            raise LayoutError(f"chip at base {self.base} repeats a role: {roles}")
        sites = [n for _, n in self.role_sites]
        if len(set(sites)) != len(sites):
            raise LayoutError(
                f"chip at base {self.base}: two roles share a site number {sites}")
        lo, hi = self.base, self.base + self.real_channels - 1
        for role, n in self.role_sites:
            if not (lo <= n <= hi):
                raise LayoutError(
                    f"role {role!r} at site {n} is outside this chip's real "
                    f"channels {lo}..{hi}")

        if self.floor is None:
            # Derivation is only valid for the contiguous-from-base arrangement.
            want = tuple(range(self.base, self.base + len(self.role_sites)))
            if tuple(sites) != want:
                raise LayoutError(
                    f"chip at base {self.base} has role sites {sites}, which are "
                    f"not {list(want)}, so the floor `base+n .. base+"
                    f"{self.real_channels}` does not describe it. Declare the "
                    "floor explicitly, or declare `floor=()` with a reason if no "
                    "characterised wire-free control exists on this chip.")
            derived = tuple(range(self.base + len(self.role_sites),
                                  self.base + self.real_channels))
            object.__setattr__(self, "floor", derived)

        if self.floor == ():
            if not self.floor_reason.strip():
                raise LayoutError(
                    f"chip at base {self.base} declares no floor but gives no "
                    "reason. A missing control must say why it is missing, or "
                    "the next reader will assume it was an oversight and derive "
                    "one.")
            return

        f = set(self.floor)
        if f & set(sites):
            raise LayoutError(
                f"chip at base {self.base}: sites {sorted(f & set(sites))} are "
                "both an animal role and floor. An animal in its own control "
                "group makes the comparison meaningless.")
        outside = sorted(n for n in f if not (lo <= n <= hi))
        if outside:
            raise LayoutError(
                f"chip at base {self.base}: floor sites {outside} lie outside "
                f"the real channels {lo}..{hi}. On an RHD2216 those slots are "
                "inactive and internally tied; they read low and would flatter "
                "the control while condemning every real animal.")
        if len(f) < T.FLOOR_MIN_SITES:
            raise LayoutError(
                f"chip at base {self.base}: {len(f)} floor sites, fewer than "
                f"FLOOR_MIN_SITES={T.FLOOR_MIN_SITES}. A percentile over that "
                "few numbers is not an estimate.")

    @property
    def roles(self) -> tuple[str, ...]:
        return tuple(r for r, _ in self.role_sites)

    @property
    def has_floor(self) -> bool:
        return bool(self.floor)


@dataclass(frozen=True)
class PortSpec:
    """One XDAQ port: one chip without a splitter, two with one."""
    port: str
    chips: tuple[ChipSpec, ...]

    def __post_init__(self):
        if not self.chips:
            raise LayoutError(f"port {self.port} declares no chips")
        bases = [c.base for c in self.chips]
        if len(set(bases)) != len(bases):
            raise LayoutError(f"port {self.port} repeats a chip base: {bases}")


def _uniform_layout(roles: tuple[str, ...], ports: str,
                    slot_bases: tuple[int, ...]) -> tuple[PortSpec, ...]:
    """The legacy whole-rig layout, expressed in the per-port model.

    🔑 THE ONLY PLACE THE LEGACY FORMULA LIVES. Every accessor reads the layout
    this produces, so there is exactly one thing to prove identical, and
    tests/test_cohortspec_compat.py proves it against verbatim frozen copies.
    """
    return tuple(
        PortSpec(port=p, chips=tuple(
            ChipSpec(base=base,
                     role_sites=tuple((role, base + k)
                                      for k, role in enumerate(roles)))
            for base in slot_bases))
        for p in ports)


@dataclass(frozen=True)
class CohortSpec:
    """Which sites belong to animals and which are wire-free floor.

    The floor is DERIVED from the number of roles, never typed in. That is what
    makes this correct for both cohorts at once:

        2 roles (eeg, emg)       animals /1-/2   and /33-/34
                                 floor   /3-/16  and /35-/48
        3 roles (eeg, emg, ecg)  animals /1-/3   and /33-/35
                                 floor   /4-/16  and /36-/48

    Getting this wrong by one site silently moves a real animal channel into the
    control group, which is why it is computed rather than listed.
    """
    roles: tuple[str, ...] = ("eeg", "emg")
    ports: str = PORTS_DEFAULT
    slot_bases: tuple[int, ...] = SLOT_BASES_DEFAULT
    # ADDED 2026-09-14, LAST and defaulting to empty, so every existing call site
    # -- CohortSpec(roles=("eeg","emg")) in eight files -- constructs exactly as
    # before, and equality, hashing and asdict() are unchanged.
    ports_spec: tuple[PortSpec, ...] = ()

    def __post_init__(self):
        # ONE internal representation. A legacy construction expands into the
        # same per-port layout an explicit one supplies, so there is one code
        # path rather than two that must be kept in step.
        layout = self.ports_spec or _uniform_layout(
            tuple(self.roles), self.ports, tuple(self.slot_bases))
        seen = [p.port for p in layout]
        if len(set(seen)) != len(seen):
            raise LayoutError(f"a port is declared twice: {seen}")
        object.__setattr__(self, "_layout", layout)

    # ---- the layout ----------------------------------------------------- #
    @property
    def layout(self) -> tuple[PortSpec, ...]:
        return self._layout          # type: ignore[attr-defined]

    @property
    def is_uniform(self) -> bool:
        """True when every chip on every port carries the same roles."""
        sigs = {c.roles for p in self.layout for c in p.chips}
        counts = {len(p.chips) for p in self.layout}
        return len(sigs) <= 1 and len(counts) <= 1

    def chip_of(self, position: str) -> ChipSpec:
        port, slot_i = position[0], int(position[1:])
        for p in self.layout:
            if p.port == port:
                if not (1 <= slot_i <= len(p.chips)):
                    raise LayoutError(
                        f"{position} does not exist: port {port} has "
                        f"{len(p.chips)} chip(s)")
                return p.chips[slot_i - 1]
        raise LayoutError(
            f"{position} names port {port}, which this spec does not describe "
            f"(it has {', '.join(p.port for p in self.layout)})")

    def roles_at(self, position: str) -> tuple[str, ...]:
        """The roles at ONE position. On a mixed rig, `spec.roles` is a union."""
        return self.chip_of(position).roles

    def positions(self) -> list[str]:
        return [f"{p.port}{i}"
                for p in self.layout
                for i in range(1, len(p.chips) + 1)]

    def animal_sites(self) -> dict[str, dict[str, str]]:
        """{"B1": {"eeg": "B/1", "emg": "B/2"}, ...}"""
        out: dict[str, dict[str, str]] = {}
        for p in self.layout:
            for slot_i, chip in enumerate(p.chips, start=1):
                out[f"{p.port}{slot_i}"] = {
                    role: f"{p.port}/{n}" for role, n in chip.role_sites}
        return out

    def floor_sites(self) -> list[str]:
        """Every wire-free site on the rig, in layout order.

        🔑 ORDER IS PART OF THE CONTRACT. floor_threshold_ci draws
        rng.integers against a fixed seed and indexes this list BY POSITION, so
        a reordering with an identical set moves every published confidence
        interval. tests/test_cohortspec_compat.py compares lists, not sets.
        """
        return [f"{p.port}/{i}"
                for p in self.layout
                for chip in p.chips
                for i in (chip.floor or ())]

    def site_of(self, position: str, role: str) -> str:
        sites = self.animal_sites().get(position)
        if sites is None:
            raise LayoutError(
                f"{position} is not a position in this spec; it has "
                f"{', '.join(self.positions())}")
        if role not in sites:
            raise LayoutError(
                f"{position} has no role {role!r}; it carries "
                f"{', '.join(sites)}. On a mixed rig `spec.roles` is the union "
                "across ports -- use roles_at(position) for one position.")
        return sites[role]

    def describe(self) -> str:
        """One line per port, for logs and card provenance."""
        out = []
        for p in self.layout:
            for i, c in enumerate(p.chips, start=1):
                floor = (f"floor {len(c.floor)} sites" if c.has_floor
                         else f"NO FLOOR ({c.floor_reason.strip().splitlines()[0]})")
                out.append(f"{p.port}{i}: {'+'.join(c.roles)} @ base {c.base}, "
                           f"{floor}")
        return "\n".join(out)


# --------------------------------------------------------------------------- #
# per-epoch feature extraction
# --------------------------------------------------------------------------- #

@dataclass
class EpochFeatures:
    """Per-epoch, per-site measurements. Everything downstream reads this."""
    base: str
    fs: int
    epoch_s: int
    n_epochs: int
    n_samples: int
    sites: list[str]
    spec: CohortSpec
    hum: np.ndarray = field(repr=False)      # (nep, nsite) 60 Hz amplitude, uV
    rms: np.ndarray = field(repr=False)      # (nep, nsite) uV
    rail: np.ndarray = field(repr=False)     # (nep, nsite) fraction railed
    slope: np.ndarray = field(repr=False)    # (nep, nsite) log-log 1-40 Hz
    delta: np.ndarray = field(repr=False)    # (nep, nsite) 1-4 Hz share of 1-40
    lfhf: np.ndarray = field(repr=False)     # (nep, nsite) sqrt power ratio
    # Sub-band slopes for the band-limit guard. Optional so that feature caches
    # written before 2026-08-10 still load; the guard reports "unknown" and says
    # so rather than silently passing when they are absent.
    slope_lo: np.ndarray | None = field(repr=False, default=None)  # 1-25 Hz
    slope_hi: np.ndarray | None = field(repr=False, default=None)  # 25-45 Hz

    def col(self, site: str) -> int:
        return self.sites.index(site)

    @property
    def hours(self) -> float:
        return self.n_samples / self.fs / 3600.0


def open_xdat(base: str) -> tuple[np.memmap, list[str], int, int]:
    """Open an Allego recording. Layout ALWAYS from the file's own metadata.

    Returns (memmap[n_samples, n_channels], labels, fs, n_samples).
    """
    meta_path = base + ".xdat.json"
    with open(meta_path) as fh:
        meta = json.load(fh)
    bm = meta["sapiens_base"]["biointerface_map"]
    fs = int(meta["status"]["samp_freq"])
    labels = [f"{p}/{s}" for p, s in zip(bm["port"], bm["site_num"])]
    nch = len(labels)
    data_path = base + "_data.xdat"
    n_samples = os.path.getsize(data_path) // (nch * 4)   # float32
    x = np.memmap(data_path, dtype=np.float32, mode="r", shape=(n_samples, nch))
    return x, labels, fs, n_samples


def file_integrity(base: str) -> dict:
    """Rung 0. Is the file physically sound? Cheap, metadata plus two stats."""
    meta_path = Path(base + ".xdat.json")
    data_path = Path(base + "_data.xdat")
    ts_path = Path(base + "_timestamp.xdat")
    out: dict = {"base": os.path.basename(base),
                 "meta_exists": meta_path.exists(),
                 "data_exists": data_path.exists(),
                 "timestamp_exists": ts_path.exists()}
    if not (meta_path.exists() and data_path.exists()):
        out["verdict"] = "MALFORMED"
        out["reason"] = "missing metadata or data file"
        return out

    meta = json.loads(meta_path.read_text())
    bm = meta["sapiens_base"]["biointerface_map"]
    fs = int(meta["status"]["samp_freq"])
    nch = len(bm["port"])
    data_bytes = data_path.stat().st_size
    n_data, rem_data = divmod(data_bytes, nch * 4)
    out.update(fs=fs, n_channels=nch, data_bytes=data_bytes,
               n_data_samples=int(n_data), data_remainder=int(rem_data),
               duration_h=round(n_data / fs / 3600.0, 3),
               start_time_utc=meta.get("status", {}).get("start_time"))

    if ts_path.exists():
        ts_bytes = ts_path.stat().st_size
        # timestamps are int64, one per sample
        n_ts, rem_ts = divmod(ts_bytes, 8)
        out.update(n_timestamp_samples=int(n_ts), timestamp_remainder=int(rem_ts))
    else:
        n_ts, rem_ts = None, None

    problems = []
    if rem_data:
        problems.append(f"data file has {rem_data} trailing bytes, not a whole sample")
    if rem_ts:
        problems.append(f"timestamp file has {rem_ts} trailing bytes")
    if n_ts is not None and n_ts != n_data:
        problems.append(f"{n_data} data samples but {n_ts} timestamp samples")
    out["problems"] = problems
    out["verdict"] = "INTACT" if not problems else "TRUNCATED"
    out["reason"] = "; ".join(problems) if problems else (
        f"{n_data:,} data samples = {n_ts:,} timestamp samples, remainder 0 and 0"
        if n_ts is not None else f"{n_data:,} samples, remainder 0")
    return out


def compute_features(base: str,
                     spec: CohortSpec,
                     *,
                     epoch_s: int | None = None,
                     max_hours: float | None = None,
                     progress: Callable[[str], None] | None = print) -> EpochFeatures:
    """Single pass over the recording producing every per-epoch measurement.

    One pass, one set of numbers, so the hum and slope criteria are guaranteed to
    be talking about exactly the same epochs.
    """
    epoch_s = int(epoch_s or T.EPOCH_S_QC)
    x, labels, fs, n_samples = open_xdat(base)

    if max_hours:
        n_samples = min(n_samples, int(max_hours * 3600 * fs))
    ep = fs * epoch_s
    nep = n_samples // ep
    if nep < 1:
        raise SystemExit(f"{base}: only {n_samples} samples, less than one "
                         f"{epoch_s}s epoch")

    animal_sites = spec.animal_sites()
    wanted = sorted({s for roles in animal_sites.values() for s in roles.values()}
                    | set(spec.floor_sites()))
    missing = [s for s in wanted if s not in labels]
    if missing:
        raise SystemExit(
            f"{base}: {len(missing)} expected sites are not in this file's "
            f"biointerface_map: {', '.join(missing[:8])}"
            f"{' ...' if len(missing) > 8 else ''}\n"
            "The cohort spec does not match the recording. Do not hard-code a "
            "layout to work around this.")
    cols = np.array([labels.index(s) for s in wanted])

    freqs = np.fft.rfftfreq(ep, 1 / fs)
    m60 = (freqs >= 59) & (freqs <= 61)
    lo, hi = T.SLOPE_BAND_HZ
    band = (freqs >= lo) & (freqs <= hi)
    dband = (freqs >= T.BAND_DELTA[0]) & (freqs <= T.BAND_DELTA[1])
    hf = (freqs >= 100) & (freqs <= 300)
    for h in range(60, 481, 60):              # keep mains harmonics out of HF
        hf &= ~((freqs >= h - 2.5) & (freqs <= h + 2.5))

    lgf = np.log10(freqs[band])
    lgf_c = lgf - lgf.mean()
    lgf_var = float((lgf_c ** 2).sum())

    # Two adjoining sub-bands for the band-limit guard. A power law has the same
    # slope in both; a filter corner does not. See qc_thresholds.BANDLIMIT_*.
    def _subband(edges):
        m = (freqs >= edges[0]) & (freqs <= edges[1])
        lg_ = np.log10(freqs[m])
        c = lg_ - lg_.mean()
        return m, c, float((c ** 2).sum())

    b_lo, c_lo, v_lo = _subband(T.BANDLIMIT_LO_BAND)
    b_hi, c_hi, v_hi = _subband(T.BANDLIMIT_HI_BAND)

    win = np.hanning(ep)
    wgain = win.sum() / 2
    n = len(wanted)
    hum = np.zeros((nep, n), dtype=np.float32)
    rms = np.zeros_like(hum)
    rail = np.zeros_like(hum)
    slope = np.zeros_like(hum)
    delta = np.zeros_like(hum)
    lfhf = np.zeros_like(hum)
    slope_lo = np.zeros_like(hum)
    slope_hi = np.zeros_like(hum)

    for k in range(nep):
        blk = np.asarray(x[k * ep:(k + 1) * ep, cols], dtype=np.float64)
        blk -= blk.mean(0)
        rms[k] = blk.std(0)
        rail[k] = (np.abs(blk) >= T.RAIL_UV_EFF).mean(0)
        P = np.abs(np.fft.rfft(blk * win[:, None], axis=0)) / wgain
        hum[k] = P[m60].max(0)
        pw = P ** 2 + 1e-20
        lg = np.log10(pw[band])
        slope[k] = (lgf_c[:, None] * (lg - lg.mean(0))).sum(0) / lgf_var
        l_lo = np.log10(pw[b_lo])
        slope_lo[k] = (c_lo[:, None] * (l_lo - l_lo.mean(0))).sum(0) / v_lo
        l_hi = np.log10(pw[b_hi])
        slope_hi[k] = (c_hi[:, None] * (l_hi - l_hi.mean(0))).sum(0) / v_hi
        delta[k] = pw[dband].sum(0) / pw[band].sum(0)
        lfhf[k] = np.sqrt(pw[band].mean(0)) / np.sqrt(pw[hf].mean(0))
        if progress and (k + 1) % 300 == 0:
            progress(f"  ...{k + 1}/{nep} epochs")

    return EpochFeatures(base=base, fs=fs, epoch_s=epoch_s, n_epochs=nep,
                         n_samples=nep * ep, sites=wanted, spec=spec,
                         hum=hum, rms=rms, rail=rail, slope=slope,
                         delta=delta, lfhf=lfhf,
                         slope_lo=slope_lo, slope_hi=slope_hi)


# --------------------------------------------------------------------------- #
# the floor, and the thresholds it sets
# --------------------------------------------------------------------------- #

@dataclass
class FloorStats:
    n_sites: int
    n_epochs: int
    n_samples: int
    hum_p1: float | None
    hum_p5: float | None
    hum_median: float | None
    slope_p1: float | None
    slope_p5: float | None
    slope_median: float | None
    slope_min: float | None
    # Provenance of THIS floor. Reported on every card so a number can never be
    # quoted without saying which wire-free inputs produced it.
    scope: str = "pooled"          # "chip" | "pooled"
    position: str = ""             # the chip, when scope == "chip"
    estimator: str = "pooled_p1"   # see qc_thresholds.FLOOR_ESTIMATOR
    grounded: bool = True          # False => floor is not a valid control
    validity_reason: str = ""
    # `grounded` is not enough. A grounded floor can still carry signal, and then
    # it is no control for the SLOPE criterion. `slope_flat` is that second test;
    # the hum criterion does not depend on it. See
    # qc_thresholds.FLOOR_MAX_SITE_MEDIAN_SLOPE.
    site_median_slope: float | None = None
    slope_flat: bool = True
    slope_validity_reason: str = ""
    # `available` is a SPEC fact, known before a byte is read: this chip's layout
    # declares no characterised wire-free control. `grounded` is a MEASURED fact:
    # a floor exists and says the chip is floating. Keeping them apart matters --
    # conflating them would print "the headstage has no ground reference" about a
    # unipolar prep that was perfectly grounded.
    available: bool = True
    unavailable_reason: str = ""

    @classmethod
    def unavailable(cls, position: str, reason: str) -> "FloorStats":
        """A floor that does not exist. Percentiles are None, never NaN.

        🔴 NaN WOULD FABRICATE A VERDICT. `_raw_mask` does
        `feat.slope[:, c] < floor.slope_p1`; every comparison against NaN is
        False, so a NaN floor yields an all-False mask, which reads as a
        perfectly ordinary 0% usable -- a FAIL invented for an animal nobody can
        judge. None raises instead.
        """
        return cls(n_sites=0, n_epochs=0, n_samples=0,
                   hum_p1=None, hum_p5=None, hum_median=None,
                   slope_p1=None, slope_p5=None, slope_median=None,
                   slope_min=None,
                   scope="chip", position=position, estimator="none",
                   grounded=False, validity_reason=reason,
                   slope_flat=False, slope_validity_reason=reason,
                   available=False, unavailable_reason=reason)

    def as_dict(self) -> dict:
        return {k: (round(v, 3) if isinstance(v, float) else v)
                for k, v in self.__dict__.items()}


def _percentile(values: np.ndarray, p: float, estimator: str) -> float:
    """Percentile of a floor statistic, estimated over a small, heterogeneous set.

    values is (n_epochs, n_sites).

    "pooled_p1" throws every (epoch, site) value into one pot, which lets the
    lower tail of a single unrepresentative site set the threshold for the whole
    chip. "site_p1_median" takes the percentile within each site first and then
    the median across sites, so one bad site is a minority vote rather than the
    decider. See qc_thresholds.FLOOR_ESTIMATOR for the measurement that motivated
    this.
    """
    if estimator == "pooled_p1":
        return float(np.percentile(values, p))
    if estimator == "site_p1_median":
        return float(np.median(np.percentile(values, p, axis=0)))
    raise ValueError(f"unknown floor estimator {estimator!r}")


def floor_sites_of(spec: CohortSpec, position: str) -> list[str]:
    """The wire-free sites on the SAME port and slot as `position`.

    This is what "through the same chip" in USABLE_FRACTION_DEFINITION means.

    An EMPTY list means this chip has no characterised wire-free control -- see
    ChipSpec. It does not mean zero sites were found; callers must treat it as
    "no verdict is available", never as "the floor is zero".
    """
    return [f"{position[0]}/{i}" for i in (spec.chip_of(position).floor or ())]


def floor_stats(feat: EpochFeatures,
                position: str | None = None,
                *,
                estimator: str | None = None) -> FloorStats:
    """Thresholds come from the wire-free inputs IN THIS FILE, never from memory.

    position=None reproduces the historical POOLED floor across all chips. That
    is kept only so old callers keep working; it contradicts this project's own
    definition of usable fraction and it condemns a whole rig when one headstage
    floats. Pass a position.
    """
    estimator = estimator or T.FLOOR_ESTIMATOR
    if position is None:
        # A pooled floor across a MIXED rig is not a number about anything: it
        # would average chips whose control sites differ in count and in kind.
        if not feat.spec.is_uniform:
            raise LayoutError(
                "floor_stats(position=None) pools every chip on the rig, but "
                "this spec is not uniform:\n" + feat.spec.describe() +
                "\nPass a position.")
        sites, scope = feat.spec.floor_sites(), "pooled"
    else:
        sites, scope = floor_sites_of(feat.spec, position), "chip"
        if not sites:
            return FloorStats.unavailable(
                position, feat.spec.chip_of(position).floor_reason.strip())
    fc = np.array([feat.col(s) for s in sites])
    fh = feat.hum[:, fc]
    fs_ = feat.slope[:, fc]
    p = T.FLOOR_PERCENTILE
    hum_median = float(np.median(fh))
    grounded = hum_median >= T.FLOOR_MIN_HUM_UV
    reason = "" if grounded else (
        f"wire-free inputs on this chip sit at {hum_median:.0f} uV of 60 Hz, "
        f"below the {T.FLOOR_MIN_HUM_UV:.0f} uV that a GROUNDED chip shows. The "
        "headstage has no ground reference, so its wire-free inputs are not a "
        "valid negative control and no connection verdict can be drawn from "
        "them. This is a HARDWARE fault at the chip, not a statement about the "
        "animal.")
    # 🔑 THE FLOOR IS A MEASUREMENT TOO. A wire-free input has no source, so its
    # typical epoch is spectrally flat. If this chip's typical floor site is
    # steep, its inputs are carrying signal and the slope threshold derived from
    # them demands more than real EEG delivers. Anchored at zero on the floor
    # alone -- never compared with the animal, which would call every DEAD
    # electrode's floor contaminated. See FLOOR_MAX_SITE_MEDIAN_SLOPE.
    site_median_slope = float(np.median(np.median(fs_, axis=0)))
    slope_flat = site_median_slope >= T.FLOOR_MAX_SITE_MEDIAN_SLOPE
    slope_reason = "" if slope_flat else (
        f"the typical wire-free input on this chip has a spectral slope of "
        f"{site_median_slope:.2f}, steeper than the "
        f"{T.FLOOR_MAX_SITE_MEDIAN_SLOPE:.2f} that any clean floor on this rig "
        "has shown. A wire-free input has no source and should be flat, so these "
        "inputs are carrying signal and are not a valid negative control for the "
        "slope criterion. No slope verdict can be drawn from them. This is a "
        "statement about the chip's control, not about the animal.")
    return FloorStats(
        n_sites=len(fc), n_epochs=feat.n_epochs, n_samples=int(fh.size),
        hum_p1=_percentile(fh, p, estimator), hum_p5=_percentile(fh, 5, estimator),
        hum_median=hum_median,
        slope_p1=_percentile(fs_, p, estimator), slope_p5=_percentile(fs_, 5, estimator),
        slope_median=float(np.median(fs_)), slope_min=float(fs_.min()),
        scope=scope, position=position or "", estimator=estimator,
        grounded=grounded, validity_reason=reason,
        site_median_slope=site_median_slope, slope_flat=slope_flat,
        slope_validity_reason=slope_reason)


def floor_threshold_ci(feat: EpochFeatures, criterion: str = "slope",
                       n_boot: int = 2000, ci: float = 95.0,
                       seed: int = 20260810,
                       position: str | None = None,
                       estimator: str | None = None) -> dict:
    """Sampling uncertainty of the floor threshold, and what it does to a fraction.

    WHY THIS EXISTS. Every usable fraction in this project is a comparison against
    the 1st percentile of the wire-free floor, and that percentile is ITSELF AN
    ESTIMATE from a finite number of unwired sites. Until 2026-08-10 no output
    carried its uncertainty, so a fraction was quoted as though the threshold
    behind it were exact.

    🔑 THE RESAMPLING UNIT IS THE SITE, NOT THE EPOCH. Epochs within one unwired
    input are strongly autocorrelated -- contact state and interference persist
    for minutes -- so resampling epochs would treat ~950,000 correlated numbers as
    independent draws and produce an interval far too narrow to be honest. There
    are only 14 to 104 floor SITES, and that is the real sample size.
    """
    estimator = estimator or T.FLOOR_ESTIMATOR
    rng = np.random.default_rng(seed)
    sites = (floor_sites_of(feat.spec, position) if position
             else feat.spec.floor_sites())
    # An empty site list used to reach np.percentile and raise there, which read
    # as a numpy bug rather than as the real situation: this chip declares no
    # characterised control, so there is no threshold to put an interval around.
    if not sites:
        reason = (feat.spec.chip_of(position).floor_reason.strip() if position
                  else "no floor sites on this rig")
        return {"available": False, "criterion": criterion, "position": position,
                "reason": reason, "n_sites": 0}
    fc = np.array([feat.col(s) for s in sites])
    src = feat.slope if criterion == "slope" else feat.hum
    p = T.FLOOR_PERCENTILE
    n_sites = len(fc)
    draws = np.empty(n_boot)
    for b in range(n_boot):
        pick = rng.integers(0, n_sites, n_sites)          # sites, with replacement
        draws[b] = _percentile(src[:, fc[pick]], p, estimator)
    lo, hi = np.percentile(draws, [(100 - ci) / 2, 100 - (100 - ci) / 2])
    point = _percentile(src[:, fc], p, estimator)
    return {"criterion": criterion, "n_floor_sites": int(n_sites),
            "point": point, "lo": float(lo), "hi": float(hi), "ci": ci,
            "n_boot": n_boot,
            "note": "resampled over SITES; epochs within a site are not independent"}


def usable_fraction_interval(feat: EpochFeatures, site: str, floor: FloorStats,
                             criterion: str, ci_dict: dict) -> dict:
    """The usable fraction recomputed at both ends of the floor threshold's CI.

    This is the interval that should be quoted beside a usable fraction. It is
    NOT a confidence interval on the animal: it is the range the number moves
    across purely because the wire-free floor was estimated from a finite number
    of sites. If it is wide, the fraction was never a precise quantity.
    """
    c = feat.col(site)
    amp = (feat.rms[:, c] >= T.RMS_LO_UV) & (feat.rms[:, c] <= T.RMS_HI_UV)
    norail = feat.rail[:, c] == 0
    src = feat.slope[:, c] if criterion == "slope" else feat.hum[:, c]
    out = {}
    for key in ("point", "lo", "hi"):
        out[key] = float((amp & norail & (src < ci_dict[key])).mean())
    # lo/hi of the THRESHOLD map to lo/hi of the FRACTION in the same direction
    # for both criteria, since both are "below the threshold passes".
    return {"fraction": out["point"],
            "fraction_lo": min(out["lo"], out["hi"]),
            "fraction_hi": max(out["lo"], out["hi"]),
            "threshold_ci": ci_dict}


def falsification_check(feat: EpochFeatures, floor: FloorStats,
                        criterion: str = "slope") -> dict:
    """Score the floor channels with their own criterion. This MUST come out low.

    If wire-free inputs score usable, the criterion is measuring nothing and no
    animal number from this file means anything. Run it before believing a
    result, not after.
    """
    # Score the floor THIS threshold came from. Scoring the pooled site list
    # against a per-chip threshold compares a chip to other chips' hardware and
    # reports the mismatch as a criterion failure.
    sites = (floor_sites_of(feat.spec, floor.position)
             if floor.scope == "chip" and floor.position
             else feat.spec.floor_sites())
    # Same as above: scoring the floor against itself is meaningless when there
    # is no floor. Saying so beats an arr.max() on an empty array.
    if not floor.available or not sites:
        return {"applicable": False, "criterion": criterion,
                "position": floor.position,
                "reason": floor.unavailable_reason or "no floor sites",
                "n_sites": 0}
    fracs = []
    for site in sites:
        m = _raw_mask(feat, site, floor, criterion)
        fracs.append(float(m.mean()))
    arr = np.array(fracs)

    # 🔑 THE BAR MUST BE STATED RELATIVE TO FLOOR_PERCENTILE, NOT AS A CONSTANT.
    # Until 2026-08-10 this returned `passes = mean < 0.01`. But the threshold
    # the floor is scored against IS the floor's own 1st percentile, so about
    # FLOOR_PERCENTILE percent of floor epochs fall below it BY CONSTRUCTION.
    # With FLOOR_PERCENTILE = 1 the expected value of this mean is 0.01 and the
    # old test was a coin flip on noise: the falsification suite measured 1.03%
    # on synthetic data and the check reported FAILURE for a floor that was
    # behaving exactly as it must.
    #
    # The real question is whether the floor scores NEAR its construction value
    # or far above it. Three times the expected rate is the alarm: that would
    # mean the discriminator is not separating anything and the percentile is
    # cutting into a distribution the animals also occupy.
    expected = T.FLOOR_PERCENTILE / 100.0
    return {"criterion": criterion,
            "n_floor_sites": len(fracs),
            "mean_usable_fraction": float(arr.mean()),
            "max_usable_fraction": float(arr.max()),
            "expected_by_construction": expected,
            "passes": bool(arr.mean() <= 3.0 * expected)}


# --------------------------------------------------------------------------- #
# the criteria themselves
# --------------------------------------------------------------------------- #

def _raw_mask(feat: EpochFeatures, site: str, floor: FloorStats,
              criterion: str) -> np.ndarray:
    """Per-epoch boolean mask, with NO validity guard. Internal use only.

    🔑 THE SINGLE CHOKEPOINT. Every criterion reaches the floor through here, so
    this is the one place that can stop a missing floor from becoming a number.
    """
    if not floor.available:
        raise CriterionRefused(
            f"no wire-free floor exists for {site}: {floor.unavailable_reason} "
            "No usable fraction can be computed against a control that was "
            "never characterised.")
    c = feat.col(site)
    amplitude_ok = (feat.rms[:, c] >= T.RMS_LO_UV) & (feat.rms[:, c] <= T.RMS_HI_UV)
    no_railing = feat.rail[:, c] == 0
    if criterion == "hum":
        discriminator = feat.hum[:, c] < floor.hum_p1
    elif criterion == "slope":
        discriminator = feat.slope[:, c] < floor.slope_p1
    else:
        raise ValueError(f"unknown criterion {criterion!r}, expected 'hum' or 'slope'")
    return amplitude_ok & no_railing & discriminator


USABLE_FRACTION_DEFINITION = (
    "\"Usable fraction\" is this project's own term and is not standard in the "
    "sleep literature, so it is defined wherever it is first used. It is the "
    f"percentage of {T.EPOCH_S_QC} s epochs in which a channel's spectrum beats "
    f"the {T.FLOOR_PERCENTILE}st percentile of AMPLIFIER INPUTS WITH NO WIRE "
    "ATTACHED, recorded simultaneously through the same chip, cable and room in "
    "the same file. It is a CONNECTION measure, not a data-quality score and not "
    "an artefact-rejection rate: the discarded epochs are ones in which the "
    "electrode was not demonstrably connected, NOT ones judged too noisy to use.")
# 🔑 WRITE THIS OUT, EVERY TIME. Reported bare, "71.6% usable EEG" reads to a
# referee as "we threw away 28% of the data for reasons of our own", which is a
# far worse claim than the one actually being made and is not recoverable later
# in the paragraph. `cards/` and the exports embed this string rather than
# paraphrasing it, so the definition cannot drift between two outputs.


class CriterionRefused(RuntimeError):
    """Raised when a criterion is not valid for this channel, with the evidence."""


def check_hum_validity(feat: EpochFeatures, site: str, floor: FloorStats) -> dict:
    """Is the hum criterion trustworthy for THIS channel in THIS file?

    The test is disagreement with the slope criterion on the same epochs. Quiet
    and spectrally flat at the same time is the floating-no-ground signature, not
    an electrode.
    """
    hum_frac = float(_raw_mask(feat, site, floor, "hum").mean())
    slope_frac = float(_raw_mask(feat, site, floor, "slope").mean())
    contradicts = (hum_frac >= T.HUM_CONTRADICTION_HUM_MIN
                   and slope_frac <= T.HUM_CONTRADICTION_SLOPE_MAX)
    return {"site": site, "hum_fraction": hum_frac, "slope_fraction": slope_frac,
            "contradiction": contradicts,
            "median_hum_uv": float(np.median(feat.hum[:, feat.col(site)])),
            "floor_hum_median_uv": floor.hum_median}


def check_bandlimit_validity(feat: EpochFeatures, site: str) -> dict:
    """Is the SLOPE criterion being shown raw data, or something already filtered?

    A power law is scale free: 1/f noise has the same log-log slope in any
    sub-band. A filter corner is not scale free. So the slope measured over
    25-45 Hz minus the slope over 1-25 Hz is ~0 for anything the criterion is
    entitled to judge, and strongly negative for a band-limited signal.

    MEASURED (see qc_thresholds.BANDLIMIT_*): every scale-free case -- raw
    wire-free input, real 1/f^1.8 EEG, 1/f^1.5, and the acquisition high-pass --
    lands within +/-0.11, while a 0.5-30 Hz band-pass lands at -11.25.

    Returns a dict with `verdict` in {"raw", "band_limited", "unknown"}.
    "unknown" means the feature cache predates 2026-08-10 and does not carry the
    sub-band slopes; it is reported honestly rather than treated as a pass.
    """
    out = {"site": site, "drop": None, "threshold": T.BANDLIMIT_MAX_DROP}
    if feat.slope_lo is None or feat.slope_hi is None:
        out["verdict"] = "unknown"
        out["reason"] = ("feature cache has no sub-band slopes; rebuild it with "
                         "--rebuild to enable the band-limit guard")
        return out
    c = feat.col(site)
    drop = float(np.median(feat.slope_hi[:, c]) - np.median(feat.slope_lo[:, c]))
    out["drop"] = drop
    out["verdict"] = "band_limited" if drop < T.BANDLIMIT_MAX_DROP else "raw"
    return out


def usable(feat: EpochFeatures, site: str, floor: FloorStats,
           criterion: str = "slope", *, role: str | None = None,
           allow_refused: bool = False) -> np.ndarray:
    """Per-epoch usable mask for one site. THE function everything else calls.

    role, if given, is checked against the criterion:
      - slope on a non-EEG role RAISES. Real EMG and ECG are broadband and
        therefore flat, so a slope test calls a working muscle channel dead.
      - hum on a channel that contradicts the slope criterion RAISES, because
        that is the no-ground signature.

    allow_refused=True downgrades a refusal to a returned all-False mask, for
    callers that want to record the refusal rather than crash on it.
    """
    if criterion == "slope" and role is not None and role.lower() != "eeg":
        msg = (f"slope criterion applied to a {role.upper()} channel ({site}). "
               "Real EMG and ECG are broadband and therefore spectrally flat, so "
               "this test calls a working channel dead. Use 'hum' plus rms for "
               "non-EEG roles, or judge EMG by state dependence against the EEG.")
        if not allow_refused:
            raise CriterionRefused(msg)
        return np.zeros(feat.n_epochs, dtype=bool)

    # 🛑 THE SLOPE CRITERION IS ONLY VALID ON UNFILTERED INPUT.
    # A filter corner inside the measurement band is read as spectral slope, so
    # a band-passed wire-free channel scores 100% usable. That is not a
    # hypothetical: it is what `chain()` twelve lines below produces, and the
    # temptation to "clean the signal first" is exactly how it would happen.
    if criterion == "slope":
        bl = check_bandlimit_validity(feat, site)
        if bl["verdict"] == "band_limited":
            msg = (f"slope criterion refused for {site}: its spectrum is BAND "
                   f"LIMITED, not raw. The log-log slope over "
                   f"{T.BANDLIMIT_HI_BAND[0]:g}-{T.BANDLIMIT_HI_BAND[1]:g} Hz is "
                   f"{bl['drop']:+.2f} steeper than over "
                   f"{T.BANDLIMIT_LO_BAND[0]:g}-{T.BANDLIMIT_LO_BAND[1]:g} Hz, "
                   f"against a bar of {T.BANDLIMIT_MAX_DROP:+.2f}. A power law is "
                   "scale free and cannot do that; a filter corner can. Judging "
                   "slope here measures the filter, not the electrode, and a "
                   "wire-free input treated this way scores 100% usable. Pass "
                   "the RAW signal.")
            if not allow_refused:
                raise CriterionRefused(msg)
            return np.zeros(feat.n_epochs, dtype=bool)

    # 🛑 THE HUM GUARD IS AN EEG TEST AND MUST NOT BE APPLIED TO EMG OR ECG.
    # It fires on "quiet AND spectrally flat", which is the floating-no-ground
    # signature ON AN EEG CHANNEL. On an EMG channel that description is a
    # HEALTHY channel: real muscle activity is broadband and therefore flat.
    # Applying it to EMG made C1's muscle channel score 0.0% on 2026-07-31 when
    # it is in fact usable in 97.6% of epochs, which then dragged the animal
    # holding this project's only 8.1 hour unbroken sleep block down to FAIL.
    if criterion == "hum" and (role is None or role.lower() == "eeg"):
        v = check_hum_validity(feat, site, floor)
        if v["contradiction"]:
            msg = (f"hum criterion refused for {site}: it calls "
                   f"{100 * v['hum_fraction']:.1f}% of epochs usable while the "
                   f"slope criterion calls {100 * v['slope_fraction']:.1f}% usable. "
                   f"Quiet (median 60 Hz {v['median_hum_uv']:.0f} uV against a "
                   f"wire-free floor median of {v['floor_hum_median_uv']:.0f} uV) "
                   "and spectrally flat at the same time is a FLOATING channel "
                   "with no ground, not an electrode. Report the slope criterion.")
            if not allow_refused:
                raise CriterionRefused(msg)
            return np.zeros(feat.n_epochs, dtype=bool)

    return _raw_mask(feat, site, floor, criterion)


# --------------------------------------------------------------------------- #
# summarising a mask
# --------------------------------------------------------------------------- #

def longest_run(mask: Sequence[bool]) -> int:
    """Longest unbroken run of True, in epochs."""
    best = cur = 0
    for v in mask:
        cur = cur + 1 if v else 0
        best = max(best, cur)
    return best


def runs(mask: np.ndarray) -> list[tuple[int, int]]:
    """[(start, stop_exclusive), ...] for every unbroken True run."""
    out: list[tuple[int, int]] = []
    start = None
    for i, v in enumerate(mask):
        if v and start is None:
            start = i
        elif not v and start is not None:
            out.append((start, i))
            start = None
    if start is not None:
        out.append((start, len(mask)))
    return out


def summarise(feat: EpochFeatures, mask: np.ndarray) -> dict:
    """Fraction, hours, longest block. ALWAYS states epochs as well as time."""
    n_usable = int(mask.sum())
    longest_ep = longest_run(mask)
    return {
        "n_epochs_total": int(feat.n_epochs),
        "n_epochs_usable": n_usable,
        "epoch_s": feat.epoch_s,
        "usable_fraction": float(mask.mean()) if feat.n_epochs else 0.0,
        "usable_hours": round(n_usable * feat.epoch_s / 3600.0, 3),
        "longest_block_epochs": int(longest_ep),
        "longest_block_minutes": round(longest_ep * feat.epoch_s / 60.0, 1),
        "insufficient": bool(feat.n_epochs < T.MIN_USABLE_EPOCHS),
    }


# --------------------------------------------------------------------------- #
# the shared filter chain (was copy-pasted verbatim in five files)
# --------------------------------------------------------------------------- #

def chain(x: np.ndarray, fs: int, *, band: tuple[float, float] | None = None,
          notch: Iterable[float] = (60.0, 120.0, 180.0)) -> np.ndarray:
    """Notch the mains harmonics, then band-pass. Zero-phase throughout.

    ⚠️ THIS IS THE FUNCTION THAT MANUFACTURES FAKE EEG. Put a wire-free input
    through it and you get a median of about 69 uV of smooth, plausible,
    EEG-shaped signal. It is correct and necessary for display and for staging,
    and it is NEVER evidence that a channel is connected. Judge connection on
    the unfiltered spectrum, via criteria above.
    """
    import scipy.signal as sg
    band = band or T.FILT_EEG
    y = np.asarray(x, dtype=np.float64)
    for f0 in notch:
        if f0 < fs / 2:
            b, a = sg.iirnotch(f0, 30.0, fs)
            y = sg.filtfilt(b, a, y)
    hi = min(band[1], fs / 2 - 1)
    sos = sg.butter(4, [band[0], hi], btype="bandpass", fs=fs, output="sos")
    return sg.sosfiltfilt(sos, y)


# --------------------------------------------------------------------------- #
# provenance
# --------------------------------------------------------------------------- #

def thresholds_hash() -> str:
    """Short content hash of qc_thresholds.py, printed on every card."""
    import hashlib
    path = Path(T.__file__)
    return hashlib.sha256(path.read_bytes()).hexdigest()[:12]
