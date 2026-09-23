#!/usr/bin/env python3
"""strip_channels.py -- write a NEW, valid XDAT recording holding only the
channels a user actually recorded from. The original is never touched.

WHY THIS EXISTS. Allego records every channel the box has, always. On this rig
that is 262 (256 primary + 2 aux + 2 din + 2 dout) at 1000 Hz, which is
1.05 MB/s, 90 GB/day, and 843 GB sitting on the recording machine's own root
filesystem. Eight mice at two roles each is 16 of those 262 channels. Everything
else is an unwired amplifier input. Keeping only what is wired is a 13x
reduction -- a 75.7 GB twenty-hour run becomes about 5.8 GB -- which is what
makes routine off-machine archiving possible at all.

WHAT IT GUARANTEES
  - Bit-exactness. Every kept channel in the output is compared against the
    original, on the raw float32 bit patterns, and `strip()` RAISES unless they
    match. There is no code path that reports success without that check having
    passed. A tolerance is not used, because a tolerance would let NaN and -0.0
    through.
  - A valid sidecar. Every per-channel array in `biointerface_map` is subset
    (35 of its 36 keys are per-channel lists; `samp_freq` is a scalar),
    `status.signals` is recounted, the neighbourhood graph is pruned, and
    `status.dataset_checksum` is recomputed with the real formula (see below).
  - Reversibility of the one thing that is rewritten. `sys_chan_idx` and
    `absolute_idx` must be renumbered (see RENUMBER OR PRESERVE), so the
    original values are recorded in `status.dataset_provenance` and the mapping
    from output column to original row is never lost.
  - It refuses rather than guesses. Roughly half the code below is a refusal.

THE CHECKSUM FORMULA, MEASURED
    status.dataset_checksum == sha256(<base>_data.xdat || <base>_timestamp.xdat)
Verified byte-for-byte on allego_3__uid0828-09-26-12 and allego_0__uid0818-18-56-33
on 2026-09-11; the reverse concatenation does not match. So the stripper can
recompute the field correctly, in the same streaming pass that writes the data,
rather than leaving behind a checksum that describes a different file.

RENUMBER OR PRESERVE -- the distinction that matters most here
  `sys_chan_idx` and `absolute_idx` ADDRESS A ROW OF THE DATA RECORD. In every
  file on this rig they are exactly range(N). Preserved into a 16-channel file
  they would claim a channel lives at row 225 of a record that has 16 rows, and
  any reader that seeks by them would return ANOTHER CHANNEL'S BYTES. A silent
  wrong-channel bug is the worst failure this project can produce, so these two
  are renumbered to range(k).

  `ntv_chan_idx`, `ntv_chan_name`, `chan_name`, `port`, `site_num`, `is_selected`,
  `headstage_id`, `probe_id` and all the geometry are IDENTITY. `core.criteria
  .open_xdat` builds its labels from `port` + `site_num` alone and takes the
  array length as the channel count. Renumbering `site_num` would relabel A/33 as
  A/3, and every CohortSpec lookup would then silently resolve to the wrong
  mouse. These are preserved verbatim.

THE LAYOUT IS NOT UNIVERSAL. allego_0__uid0904-08-55-25 on this same rig has 134
channels, ports of 32, and selects sites /18../23. A keep list expressed as
indices and reused across recordings would read aux rows out of that file and
run off the end of it. So the keep set is resolved PER FILE from that file's own
metadata, `--keep-labels` is the safe form, and `--keep-index` is validated hard
and refused rather than clamped.

WHAT STRIPPING COSTS, AND WHY A QC BUNDLE MUST COME FIRST
  `core/criteria.py` derives every verdict in this project against WIRE-FREE
  AMPLIFIER INPUTS RECORDED IN THE SAME FILE -- sites /3../16 and /35../48 in a
  two-role cohort. Stripping to the 16 wired channels DELETES THAT FLOOR, and
  `compute_features` then exits with "N expected sites are not in this file's
  biointerface_map". A stripped file can never again be QC'd by this project's
  own criterion. The stripped copy is a convenience artifact; the original plus
  its QC bundle is the record of truth. `--dry-run` prints QC BUNDLE: MISSING in
  capitals when no bundle is present, and nothing here ever deletes an original.

DEPENDENCIES: numpy and the standard library only. No scipy, so this runs under
both `/opt/neurosurveillance/venv/bin/python3` (the only interpreter with
radiens, needed for the optional parse probe) and `~/eeg-analysis-venv`.

Usage
    python -m convert.strip_channels SRC_BASE [--out DIR]
        (--keep-selected | --keep-labels A/1,A/2,... | --keep-index 0,1,32,...)
        [--with-gpio] [--dry-run] [--verify full|spot] [--n-spot N]
        [--no-resume] [--force] [--radiens-probe] [--min-free-gb GB]
        [--allow-truncated] [--require-idle] [--report PATH]
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import random
import shutil
import socket
import subprocess
import sys
import time
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable, Iterable, Sequence

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from core import paths as PATHS  # noqa: E402

TOOL = "convert.strip_channels"
TOOL_VERSION = "2026.09.11"

# chan_type -> the section of the record it belongs to. The file orders sections
# pri, aux, din, dout; a keep set is refused if it would break that order.
TYPE_RANK = {"ai0": 0, "ai4": 1, "din0": 2, "dout0": 3}
TYPE_SIGNAL_KEY = {"ai0": "pri", "ai4": "aux", "din0": "din", "dout0": "dout"}

BYTES_PER_SAMPLE = 4          # float32 data
BYTES_PER_TIMESTAMP = 8       # int64 timestamps
DEFAULT_CHUNK_SAMPLES = 65_536


class StripRefused(RuntimeError):
    """A gate said no BEFORE anything was published. Nothing was written."""


class StripFailed(RuntimeError):
    """Bytes were written but did not verify. The output is quarantined."""


# --------------------------------------------------------------------------- #
# metadata reading and keep-set resolution
# --------------------------------------------------------------------------- #

def read_meta(base: str) -> dict:
    """Parse `<base>.xdat.json`. No validation; that is `_guard_source`'s job."""
    with open(base + ".xdat.json") as fh:
        return json.load(fh)


def channel_table(meta: dict) -> list[dict]:
    """One row per channel, in file order, from the file's own metadata."""
    bm = meta["sapiens_base"]["biointerface_map"]
    n = len(bm["port"])
    return [{"idx": i,
             "label": f"{bm['port'][i]}/{bm['site_num'][i]}",
             "chan_name": bm["chan_name"][i],
             "chan_type": bm["chan_type"][i],
             "port": bm["port"][i],
             "site_num": bm["site_num"][i],
             "ntv_chan_idx": bm["ntv_chan_idx"][i],
             "sys_chan_idx": bm["sys_chan_idx"][i],
             "is_selected": bool(bm["is_selected"][i])}
            for i in range(n)]


def resolve_keep(meta: dict, *,
                 selected: bool = False,
                 labels: Sequence[str] | None = None,
                 indices: Sequence[int] | None = None,
                 with_gpio: bool = False) -> list[int]:
    """Resolve a keep set to ascending unique channel indices FOR THIS FILE.

    Exactly one of `selected`, `labels`, `indices` must be given. `with_gpio`
    additionally keeps every aux/din/dout channel.

    Refuses, rather than repairing:
      - more or fewer than one selection mode
      - an index outside range(N), or a duplicate
      - a label that is not in this file
      - an AMBIGUOUS label. GPIO labels are not unique: both aux channels are
        `GPIO-AIN/0`, both din are `GPIO-DIN/0`. Selecting GPIO by label is
        therefore refused outright; use --with-gpio or --keep-index.
      - `--keep-selected` on a file whose is_selected flags are all false
      - a keep set whose chan_type sections are out of pri,aux,din,dout order
    """
    modes = [("--keep-selected", selected),
             ("--keep-labels", labels is not None),
             ("--keep-index", indices is not None)]
    chosen = [name for name, on in modes if on]
    if len(chosen) != 1:
        raise StripRefused(
            "exactly one of --keep-selected / --keep-labels / --keep-index is "
            f"required; got {chosen or 'none'}")

    table = channel_table(meta)
    n = len(table)
    keep: set[int] = set()

    if selected:
        keep = {r["idx"] for r in table if r["is_selected"]}
        if not keep:
            raise StripRefused(
                "--keep-selected but no channel in this file has is_selected "
                "true. Allego's selection is display-only and is not retained "
                "across launches, so a file recorded after a fresh start can "
                "carry an empty selection. Name the channels explicitly with "
                "--keep-labels.")
    elif labels is not None:
        by_label: dict[str, list[int]] = {}
        for r in table:
            by_label.setdefault(r["label"], []).append(r["idx"])
        for lab in labels:
            lab = lab.strip()
            if not lab:
                continue
            hits = by_label.get(lab)
            if hits is None:
                near = sorted(l for l in by_label if l.startswith(lab.split("/")[0]))
                raise StripRefused(
                    f"label {lab!r} is not in this file ({n} channels). "
                    f"Labels on this port: {near[:12]}"
                    + (" ..." if len(near) > 12 else ""))
            if len(hits) > 1:
                raise StripRefused(
                    f"label {lab!r} is AMBIGUOUS in this file -- it matches "
                    f"channels {hits} ({', '.join(table[i]['chan_name'] for i in hits)}). "
                    "GPIO channels share a site number, so they cannot be "
                    "selected by label. Use --with-gpio or --keep-index.")
            keep.add(hits[0])
    else:
        seen: set[int] = set()
        for raw in indices:                      # type: ignore[union-attr]
            i = int(raw)
            if not (0 <= i < n):
                raise StripRefused(
                    f"index {i} is outside range(0, {n}) for this file. THIS IS "
                    "THE 134-CHANNEL TRAP: index lists are not portable between "
                    "recordings on this rig. Use --keep-labels.")
            if i in seen:
                raise StripRefused(f"index {i} given more than once")
            seen.add(i)
            keep.add(i)

    if with_gpio:
        keep |= {r["idx"] for r in table if r["chan_type"] != "ai0"}

    out = sorted(keep)
    if not out:
        raise StripRefused("the keep set is empty")

    ranks = []
    for i in out:
        t = table[i]["chan_type"]
        if t not in TYPE_RANK:
            raise StripRefused(
                f"channel {i} ({table[i]['chan_name']}) has unknown chan_type "
                f"{t!r}. status.signals cannot be recounted for a type this tool "
                "does not know, and guessing it would produce a sidecar that "
                "misdescribes the file.")
        ranks.append(TYPE_RANK[t])
    if any(b < a for a, b in zip(ranks, ranks[1:])):
        raise StripRefused(
            "the keep set would put channel sections out of pri,aux,din,dout "
            "order, which no XDAT reader expects")
    return out


# --------------------------------------------------------------------------- #
# the plan
# --------------------------------------------------------------------------- #

@dataclass(frozen=True)
class StripPlan:
    src_base: str
    dst_base: str
    fs: int
    n_samples: int
    n_channels_in: int
    n_channels_out: int
    keep: tuple[int, ...]
    keep_labels: tuple[str, ...]
    keep_chan_names: tuple[str, ...]
    keep_chan_types: tuple[str, ...]
    dropped_gpio: tuple[int, ...]
    signals_out: dict
    bytes_in: int
    bytes_out: int
    integrity_in: dict

    @property
    def saving(self) -> float:
        return 1.0 - (self.bytes_out / self.bytes_in) if self.bytes_in else 0.0


def _import_criteria():
    """`core.criteria` imports numpy only at module level, so this is safe here.

    Imported lazily all the same, so a broken analysis package cannot stop
    `--help` from working.
    """
    from core import criteria
    return criteria


def _guard_source(meta: dict, src_base: str, *, allow_truncated: bool) -> dict:
    """Every refusal that can be decided from metadata alone, before any I/O."""
    C = _import_criteria()
    integrity = C.file_integrity(src_base)
    if integrity["verdict"] != "INTACT" and not allow_truncated:
        raise StripRefused(
            f"source is {integrity['verdict']}: {integrity['reason']}. "
            "Stripping a truncated recording produces a smaller truncated "
            "recording and hides the damage. Pass --allow-truncated to "
            "override deliberately.")

    # A non-None spec block is a SECOND layout table that this tool does not
    # know how to rewrite. All four are None in every file on this rig; a
    # future Radiens release populating one must stop the tool, not be ignored.
    for path in (("sapiens_base", "biointerface_spec"),
                 ("radiens_sen_ext", "spec"),
                 ("radiens_proj_ext", "spec"),
                 ("SapiensBiointerface", "spec")):
        node = meta
        for key in path:
            node = node.get(key) if isinstance(node, dict) else None
        if node is not None:
            raise StripRefused(
                f"{'.'.join(path)} is populated in this file. It is a second "
                "channel-layout description that this tool does not rewrite, so "
                "the output sidecar would contradict the data. Refusing.")

    bm = meta["sapiens_base"]["biointerface_map"]
    n = len(bm["port"])
    # The NUMBER of per-channel arrays is DISCOVERED, never asserted (it is 35
    # today, alongside the scalar `samp_freq`), so a future Radiens release that
    # adds one is carried rather than silently dropped.
    bad = {k: len(v) for k, v in bm.items()
           if isinstance(v, list) and len(v) != n}
    if bad:
        raise StripRefused(
            f"biointerface_map arrays disagree on length (expected {n}): {bad}")

    status = meta["status"]
    if status["signals"]["total"] != n or status["shape"][1] != n:
        raise StripRefused(
            f"metadata disagrees with itself: biointerface_map has {n} channels, "
            f"signals.total is {status['signals']['total']}, shape[1] is "
            f"{status['shape'][1]}")

    data_bytes = os.path.getsize(src_base + "_data.xdat")
    rem = data_bytes % (n * BYTES_PER_SAMPLE)
    if rem:
        raise StripRefused(
            f"{data_bytes} data bytes is not a whole number of {n}-channel "
            f"float32 samples (remainder {rem})")
    return integrity


def plan_strip(src_base: str, dst_base: str, keep: Sequence[int], *,
               allow_truncated: bool = False,
               meta: dict | None = None) -> StripPlan:
    meta = meta if meta is not None else read_meta(src_base)
    integrity = _guard_source(meta, src_base, allow_truncated=allow_truncated)

    table = channel_table(meta)
    n_in = len(table)
    keep = list(keep)
    n_samples = os.path.getsize(src_base + "_data.xdat") // (n_in * BYTES_PER_SAMPLE)

    signals_out = {"pri": 0, "aux": 0, "din": 0, "dout": 0}
    for i in keep:
        signals_out[TYPE_SIGNAL_KEY[table[i]["chan_type"]]] += 1
    signals_out["total"] = len(keep)

    kept = set(keep)
    dropped_gpio = tuple(r["idx"] for r in table
                         if r["chan_type"] != "ai0" and r["idx"] not in kept)

    return StripPlan(
        src_base=src_base, dst_base=dst_base,
        fs=int(meta["status"]["samp_freq"]),
        n_samples=int(n_samples),
        n_channels_in=n_in, n_channels_out=len(keep),
        keep=tuple(keep),
        keep_labels=tuple(table[i]["label"] for i in keep),
        keep_chan_names=tuple(table[i]["chan_name"] for i in keep),
        keep_chan_types=tuple(table[i]["chan_type"] for i in keep),
        dropped_gpio=dropped_gpio,
        signals_out=signals_out,
        bytes_in=(os.path.getsize(src_base + "_data.xdat")
                  + os.path.getsize(src_base + "_timestamp.xdat")),
        bytes_out=(n_samples * len(keep) * BYTES_PER_SAMPLE
                   + n_samples * BYTES_PER_TIMESTAMP),
        integrity_in=integrity)


# --------------------------------------------------------------------------- #
# the sidecar rewrite
# --------------------------------------------------------------------------- #

def _git_commit() -> str | None:
    try:
        out = subprocess.run(["git", "-C", str(Path(__file__).resolve().parent),
                              "rev-parse", "HEAD"],
                             capture_output=True, text=True, timeout=5)
        return out.stdout.strip() or None
    except Exception:
        return None


def rewrite_metadata(meta: dict, plan: StripPlan, *,
                     dataset_checksum: str,
                     source_data_sha256: str,
                     source_timestamp_sha256: str,
                     new_uid: str | None = None) -> dict:
    """Build the output sidecar. See RENUMBER OR PRESERVE in the module docstring.

    Everything outside `biointerface_map` and `neighborhoods.site_hood` is
    per-port or global -- `sigUnits`, `sig_proc_spec`, `zcheck_spec`, `port_map`,
    `digital_out_spec`, `biointerface_ancillary` -- and is copied verbatim.
    Confirmed by inspection on 2026-09-11: none of them carries a per-channel
    array, and `sig_proc_spec` is absent from some files (present in
    allego_3__uid0828-09-26-12, missing from allego_0__uid0904-08-55-25), so
    nothing here may require it.
    """
    import copy
    out = copy.deepcopy(meta)
    keep = list(plan.keep)
    k = len(keep)

    # --- biointerface_map: subset by LENGTH, not by a name whitelist --------- #
    bm = meta["sapiens_base"]["biointerface_map"]
    n_in = plan.n_channels_in
    bm_out: dict = {}
    for key, val in bm.items():
        if isinstance(val, list) and len(val) == n_in:
            bm_out[key] = [val[i] for i in keep]
        else:
            bm_out[key] = copy.deepcopy(val)   # scalars, e.g. samp_freq: None

    # The only two fields that address a row of the data record.
    bm_out["sys_chan_idx"] = list(range(k))
    bm_out["absolute_idx"] = list(range(k))
    out["sapiens_base"]["biointerface_map"] = bm_out

    # --- status ------------------------------------------------------------- #
    st = out["status"]
    st["shape"] = [plan.n_samples, k]
    st["num_smpl"] = plan.n_samples
    sig = dict(plan.signals_out)
    # `a != b != c` chains as `a != b and b != c`, which would only fire when
    # BOTH halves are wrong. Spell the intended assertion out.
    if not (sig["pri"] + sig["aux"] + sig["din"] + sig["dout"] == sig["total"] == k):
        raise StripFailed(f"signal recount is inconsistent: {sig}, k={k}")
    st["signals"] = {"total": sig["total"], "pri": sig["pri"], "aux": sig["aux"],
                     "din": sig["din"], "dout": sig["dout"]}
    source_uid = st.get("dataset_uid")
    st["dataset_uid"] = new_uid or str(uuid.uuid4())
    st["dataset_checksum"] = dataset_checksum

    prov = st.get("dataset_provenance")
    if not isinstance(prov, list):
        prov = []
    prov.append({
        "tool": TOOL, "version": TOOL_VERSION, "git_commit": _git_commit(),
        "utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
        "host": socket.gethostname(),
        "source_base": os.path.basename(plan.src_base),
        "source_dataset_uid": source_uid,
        "source_dataset_checksum": meta["status"].get("dataset_checksum"),
        "source_data_sha256": source_data_sha256,
        "source_timestamp_sha256": source_timestamp_sha256,
        "source_n_channels": n_in,
        "kept_count": k,
        "kept_out_of": n_in,
        # Makes the renumbering REVERSIBLE: output column j came from this row.
        "kept_orig_sys_chan_idx": [int(bm["sys_chan_idx"][i]) for i in keep],
        "kept_orig_file_index": [int(i) for i in keep],
        "kept_labels": list(plan.keep_labels),
        "kept_chan_names": list(plan.keep_chan_names),
        "renumbered_fields": ["sys_chan_idx", "absolute_idx"],
        "preserved_identity_fields": [
            "ntv_chan_idx", "ntv_chan_name", "chan_name", "port", "site_num",
            "is_selected", "headstage_id", "probe_id"],
        "timestamp_file": "copied verbatim",
        "numpy": np.__version__,
        "python": sys.version.split()[0],
    })
    st["dataset_provenance"] = prov

    tag = (f"stripped:{k}of{n_in}ch src={os.path.basename(plan.src_base)} "
           f"tool={TOOL}/{TOOL_VERSION}")
    old_tags = st.get("user_tags") or ""
    st["user_tags"] = f"{old_tags}; {tag}" if old_tags else tag

    # --- neighbourhood graph ------------------------------------------------ #
    # site_hood keys are str(ntv_chan_idx) of PRIMARY channels only (256 keys in
    # a 262-channel file, 128 in the 134-channel one). Keep the kept primaries
    # and filter each survivor's friends list, which is truthful: a dropped
    # neighbour is genuinely no longer in the file.
    hood = out.get("sapiens_base", {}).get("neighborhoods", {}).get("site_hood")
    if isinstance(hood, dict):
        kept_ntv = {int(bm["ntv_chan_idx"][i]) for i in keep
                    if bm["chan_type"][i] == "ai0"}
        new_hood = {}
        for key, entry in hood.items():
            try:
                native = int(key)
            except (TypeError, ValueError):
                continue
            if native not in kept_ntv:
                continue
            entry = copy.deepcopy(entry)
            friends = entry.get("friends")
            if isinstance(friends, list):
                entry["friends"] = [f for f in friends
                                    if int(f.get("ntv_chan_idx", -1)) in kept_ntv]
            new_hood[key] = entry
        out["sapiens_base"]["neighborhoods"]["site_hood"] = new_hood

    # --- sensors_by_port ---------------------------------------------------- #
    # Drop ports that lost every channel. `num_channels` is left alone for the
    # survivors: it describes the physical headstage, which really is a 64- or
    # 32-channel part and did not change because we wrote fewer columns.
    sbp = out.get("sapiens_base", {}).get("sensors_by_port")
    if isinstance(sbp, dict):
        kept_ports = {bm["port"][i] for i in keep}
        out["sapiens_base"]["sensors_by_port"] = {
            p: v for p, v in sbp.items() if p in kept_ports}

    anc = out.get("sapiens_base", {}).get("biointerface_ancillary")
    if isinstance(anc, dict) and anc.get("datafile_name"):
        anc["datafile_name"] = os.path.basename(plan.dst_base)
    return out


def _write_sidecar(path: str, obj: dict) -> None:
    """Compact, single-line, NaN-free -- matching how Allego's Go encoder writes.

    `allow_nan=False` makes Python raise rather than emit bare `NaN`, which is
    not valid JSON and which the Go reader rejects.
    """
    text = json.dumps(obj, separators=(",", ":"), allow_nan=False)
    with open(path, "w") as fh:
        fh.write(text)


# --------------------------------------------------------------------------- #
# verification
# --------------------------------------------------------------------------- #

def _read_block(path: str, lo: int, hi: int, n_channels: int) -> np.ndarray:
    """Read samples [lo, hi) as a (rows, n_channels) float32 array.

    DELIBERATELY NOT np.memmap. A memmap of the whole recording makes every page
    it touches resident, and `/usr/bin/time -v` measured a 9.26 GB peak RSS on a
    mere 5.26 GB file -- which on the 223 GB recording would grow without bound
    and would evict many gigabytes of page cache while the amplifiers are writing
    to the same filesystem. `np.fromfile` with an explicit offset keeps the
    resident set at one chunk, which is the whole point of streaming.
    """
    rows = hi - lo
    if rows <= 0:
        return np.empty((0, n_channels), dtype=np.float32)
    a = np.fromfile(path, dtype=np.float32, count=rows * n_channels,
                    offset=lo * n_channels * BYTES_PER_SAMPLE)
    if a.size != rows * n_channels:
        raise StripFailed(
            f"short read from {os.path.basename(path)}: wanted "
            f"{rows * n_channels} float32 at sample {lo}, got {a.size}")
    return a.reshape(rows, n_channels)


def verify_bit_exact(src_base: str, dst_data: str, keep: Sequence[int], *,
                     n_channels_in: int, n_channels_out: int, n_samples: int,
                     mode: str = "full", n_spot: int = 64, seed: int = 0,
                     chunk_samples: int = DEFAULT_CHUNK_SAMPLES,
                     progress: Callable[[str], None] | None = None) -> dict:
    """Compare kept columns of the output against the original, BIT-EXACTLY.

    The comparison is on the uint32 view of the float32 bytes, not on the float
    values, so NaN (which is never equal to itself) and -0.0 (which compares
    equal to +0.0) cannot slip through.

    mode="full" walks the entire file in chunks. mode="spot" checks the first
    sample, the last sample, and `n_spot` random windows -- it exists only for
    the 223 GB recording, and is never the default, because a full local re-read
    of 92 GB takes about half a minute on this NVMe.
    """
    keep = list(keep)
    src_data = src_base + "_data.xdat"
    compared = 0
    windows = 0

    def cmp_block(lo: int, hi: int) -> None:
        nonlocal compared, windows
        a = _read_block(src_data, lo, hi, n_channels_in)[:, keep].view(np.uint32)
        b = _read_block(dst_data, lo, hi, n_channels_out).view(np.uint32)
        if a.shape != b.shape or not np.array_equal(a, b):
            diff = int((a != b).sum()) if a.shape == b.shape else -1
            raise StripFailed(
                f"BIT MISMATCH in samples [{lo}, {hi}): {diff} differing "
                f"float32 values. The output does NOT contain the source data.")
        compared += hi - lo
        windows += 1

    if mode == "full":
        for lo in range(0, n_samples, chunk_samples):
            hi = min(lo + chunk_samples, n_samples)
            cmp_block(lo, hi)
            if progress and (lo // chunk_samples) % 200 == 0 and lo:
                progress(f"  verify {100.0 * lo / n_samples:5.1f}%")
    elif mode == "spot":
        win = 4096
        rng = random.Random(seed)
        offsets = {0, max(0, n_samples - win)}
        for _ in range(n_spot):
            offsets.add(rng.randrange(0, max(1, n_samples - win)))
        for lo in sorted(offsets):
            cmp_block(lo, min(lo + win, n_samples))
    else:
        raise StripRefused(f"unknown verify mode {mode!r}; use full or spot")

    return {"mode": mode, "windows": windows, "samples_compared": compared,
            "samples_total": n_samples, "exact": True}


# --------------------------------------------------------------------------- #
# guards that need the filesystem, not just the metadata
# --------------------------------------------------------------------------- #

def rig_is_busy(raw_root: Path | None = None, *, within_s: float = 120.0,
                source_base: str | Path | None = None,
                settle_s: float = 5.0) -> str | None:
    """Is Allego writing right now? Returns a reason string, or None if idle.

    Deliberately radiens-free, so this works from `~/eeg-analysis-venv` too, and
    so it cannot itself perturb `allegoserver` -- which is known to crash under
    some API calls.

    RECENT MTIME IS THE ONLY SIGNAL USED, and that is a correction of this
    function's first version. `status.is_live_recording` looks like the obvious
    test and is NOT USABLE: a recording that ends abnormally never has its
    sidecar rewritten, so the flag stays true forever. Measured 2026-09-11 --
    allego_0__uid0829-08-34-39 still claims to be live ten days after its last
    byte. Trusting it would have made this tool refuse to run on this rig
    permanently. See `stale_live_flags()`, which reports the same field as what
    it really is: a marker of a recording that did not shut down cleanly.

    Reading 223 GB while the amplifiers write to the same filesystem is exactly
    what `neurosurveillance/deploy/radix-archive.sh` goes to such lengths to
    avoid, and this tool reads just as hard.

    🔴 THE FILE BEING STRIPPED IS JUDGED BY GROWTH, NOT BY MTIME. `source_base`
    names the recording this strip is about to read, and mtime cannot tell "a
    recording that stopped four seconds ago" from "a recording being written
    right now" -- both are recent. Every strip that follows a stop starts within
    seconds of it, so the mtime rule refused the file it was asked to strip.

    That defect was invisible on real runs and certain on short ones: the QC
    bundle runs first, and on a 24 h recording it takes tens of minutes, so the
    mtime aged past the window BY ACCIDENT. On a five-minute bench run QC took
    two seconds and the guard fired. Found 2026-09-14 by running it.

    The honest test for the source is whether anything is still appending to it:
    measure, wait, measure again. Other recordings keep the mtime rule, because
    for them "recently written" is exactly the danger.
    """
    root = Path(raw_root) if raw_root else PATHS.RAW_ROOT
    if not root.exists():
        return None

    src_data = None
    if source_base:
        src_data = Path(str(source_base) + "_data.xdat").resolve()

    now = time.time()
    for p in root.glob("*_data.xdat"):
        try:
            if src_data and p.resolve() == src_data:
                continue                      # judged separately, below
            age = now - p.stat().st_mtime
        except OSError:
            continue
        if age < within_s:
            return f"{p.name} was written {age:.0f} s ago"

    # The source: is anything still appending to it?
    if src_data and src_data.exists():
        try:
            a = src_data.stat().st_size
            time.sleep(settle_s)
            b = src_data.stat().st_size
        except OSError:
            return None
        if b != a:
            return (f"{src_data.name} is STILL GROWING ({a} -> {b} bytes over "
                    f"{settle_s:.0f} s) -- the recording has not stopped")
    return None


def stale_live_flags(raw_root: Path | None = None,
                     *, within_s: float = 120.0) -> list[str]:
    """Recordings whose sidecar still says is_live_recording while being idle.

    Not a liveness test -- see `rig_is_busy`. This is a CRASH MARKER: Allego
    rewrites the flag when a recording stops cleanly, so a stale true means that
    recording ended some other way (the app died, or the host went down). Worth
    surfacing because such a file is also the most likely to be truncated.
    """
    root = Path(raw_root) if raw_root else PATHS.RAW_ROOT
    if not root.exists():
        return []
    now = time.time()
    out = []
    for p in sorted(root.glob("*.xdat.json")):
        try:
            if not json.loads(p.read_text()).get("status", {}).get("is_live_recording"):
                continue
        except Exception:
            continue
        data = Path(str(p)[: -len(".xdat.json")] + "_data.xdat")
        try:
            idle = data.exists() and (now - data.stat().st_mtime) >= within_s
        except OSError:
            idle = True
        if idle:
            out.append(p.name)
    return out


def qc_bundle_present(src_base: str) -> bool:
    """Is there a feature cache for this recording?

    Stripping DELETES the in-file wire-free floor, after which this project's own
    criterion can never be applied to the recording again (see the module
    docstring). The cache written by `cards/ladder.py --cache` is the only
    surviving record of that floor, so its absence is worth shouting about.
    """
    name = os.path.basename(src_base)
    for cand in (PATHS.CACHE_ROOT / f"{name}.npz",
                 PATHS.CACHE_ROOT / name / "features.npz"):
        if cand.exists():
            return True
    return False


def _free_bytes(path: Path) -> int:
    st = os.statvfs(path)
    return st.f_bavail * st.f_frsize


# --------------------------------------------------------------------------- #
# the stripper
# --------------------------------------------------------------------------- #

def strip(src_base: str, dst_base: str, keep: Sequence[int], *,
          chunk_samples: int = DEFAULT_CHUNK_SAMPLES,
          resume: bool = True,
          verify: str = "full",
          n_spot: int = 64,
          radiens_probe: bool = False,
          min_free_gb: float = 300.0,
          allow_truncated: bool = False,
          require_idle: bool = False,
          gpio_never_connected: bool = False,
          meta: dict | None = None,
          progress: Callable[[str], None] | None = print) -> dict:
    """Write the stripped triple and RAISE unless every gate passes.

    Raises StripRefused if a precondition says no (nothing was written) or
    StripFailed if bytes were written but did not verify (the output is renamed
    to `<dst>.REJECTED.<utc>.*` so it can never be mistaken for a good file).
    """
    say = progress or (lambda _m: None)
    meta = meta if meta is not None else read_meta(src_base)
    plan = plan_strip(src_base, dst_base, keep,
                      allow_truncated=allow_truncated, meta=meta)

    if require_idle:
        busy = rig_is_busy(source_base=src_base)
        if busy:
            raise StripRefused(f"the rig looks busy: {busy}. Refusing to compete "
                               "with a live recording for the same disk.")

    dst_dir = Path(dst_base).parent
    PATHS.ensure(dst_dir)
    marker = dst_dir / ".eeg-stripped-root"
    if not marker.exists():
        marker.write_text(
            "Channel-stripped copies of Allego recordings, written by "
            f"{TOOL}.\nThese are NOT raw recordings: the in-file wire-free floor "
            "has been removed,\nso core/criteria.py cannot QC them. The originals "
            f"live in {PATHS.RAW_ROOT}.\n")

    free = _free_bytes(dst_dir)
    if free - plan.bytes_out < min_free_gb * 1e9:
        raise StripRefused(
            f"only {free / 1e9:.1f} GB free at {dst_dir} and the output needs "
            f"{plan.bytes_out / 1e9:.1f} GB, which would leave less than the "
            f"{min_free_gb:.0f} GB reserve. At the measured 90 GB/day this rig "
            "would run out of room mid-recording.")

    n = plan.n_samples
    k = plan.n_channels_out
    n_in = plan.n_channels_in
    keep_l = list(plan.keep)
    dst_data, dst_ts = dst_base + "_data.xdat", dst_base + "_timestamp.xdat"
    dst_json = dst_base + ".xdat.json"
    part_data, part_ts = dst_data + ".part", dst_ts + ".part"

    # ---- already done? ---------------------------------------------------- #
    if resume and os.path.exists(dst_json) and os.path.exists(dst_data):
        try:
            done = json.load(open(dst_json))
            want = done["status"]["dataset_checksum"]
            got = _sha256_concat(dst_data, dst_ts)
            if want == got and done["status"]["shape"] == [n, k]:
                say(f"already stripped and verified: {dst_base}")
                return {"status": "already_done", "dst_base": dst_base,
                        "dataset_checksum": got, "plan": _plan_dict(plan)}
            say("existing output does not verify; rewriting")
        except Exception:
            say("existing output is unreadable; rewriting")

    # ---- resume a partial run --------------------------------------------- #
    h_data, h_all = hashlib.sha256(), hashlib.sha256()
    row_bytes = k * BYTES_PER_SAMPLE
    start_row = 0
    if resume and os.path.exists(part_data):
        have = os.path.getsize(part_data)
        start_row = have // row_bytes
        keepable = start_row * row_bytes
        if keepable != have:
            # a torn tail from a kill mid-write; discard the partial row
            with open(part_data, "r+b") as fh:
                fh.truncate(keepable)
        if start_row > n:
            say("partial output is longer than the source; starting over")
            os.remove(part_data)
            start_row = 0
        if start_row:
            say(f"resuming at sample {start_row:,} of {n:,}")
            with open(part_data, "rb") as fh:
                for blk in iter(lambda: fh.read(8 << 20), b""):
                    h_data.update(blk)
                    h_all.update(blk)
    mode = "r+b" if start_row else "wb"

    # ---- the single streaming pass ---------------------------------------- #
    # Per-DROPPED-channel statistics come free from the chunk already in RAM, and
    # are what Gate B is judged on.
    drop_idx = list(plan.dropped_gpio)
    dmin = np.full(len(drop_idx), np.inf)
    dmax = np.full(len(drop_idx), -np.inf)
    dnan = np.zeros(len(drop_idx), dtype=np.int64)
    # Gate B must tell a SIGNAL from a SPECK OF NOISE, and min/max cannot: a
    # single one-sample glitch on an unconnected input has exactly the same min
    # and max as a real pulse train. Count transitions, and count samples that
    # sit away from the level the channel rests at.
    dtrans = np.zeros(len(drop_idx), dtype=np.int64)
    dneq = np.zeros(len(drop_idx), dtype=np.int64)
    dfirst = np.full(len(drop_idx), np.nan)
    dlast = np.full(len(drop_idx), np.nan)

    src_data_path = src_base + "_data.xdat"
    t0 = time.time()
    try:
        os.nice(19)
    except OSError:
        pass
    with open(part_data, mode) as out_fh:
        if start_row:
            out_fh.seek(start_row * row_bytes)
        for lo in range(start_row, n, chunk_samples):
            hi = min(lo + chunk_samples, n)
            block = _read_block(src_data_path, lo, hi, n_in)
            buf = np.ascontiguousarray(block[:, keep_l])
            raw = buf.tobytes()
            out_fh.write(raw)
            h_data.update(raw)
            h_all.update(raw)
            if drop_idx:
                d = block[:, drop_idx].astype(np.float64, copy=False)
                nanmask = np.isnan(d)
                if nanmask.any():
                    dnan += nanmask.sum(axis=0)
                    d = np.where(nanmask, np.nan, d)
                    dmin = np.fmin(dmin, np.nanmin(d, axis=0))
                    dmax = np.fmax(dmax, np.nanmax(d, axis=0))
                else:
                    dmin = np.minimum(dmin, d.min(axis=0))
                    dmax = np.maximum(dmax, d.max(axis=0))
                if bool(np.isnan(dfirst).all()):
                    dfirst = d[0].copy()
                if bool(np.isnan(dlast).all()):
                    stacked = d
                else:
                    stacked = np.vstack([dlast.reshape(1, -1), d])
                dtrans += (np.diff(stacked, axis=0) != 0).sum(axis=0)
                dneq += (d != dfirst).sum(axis=0)
                dlast = d[-1].copy()
            if (lo // chunk_samples) % 100 == 0 and lo > start_row:
                pct = 100.0 * (lo - start_row) / max(1, n - start_row)
                say(f"  strip {pct:5.1f}%  ({(lo - start_row) / 1e6:.1f} M samples)")
        out_fh.flush()
        os.fsync(out_fh.fileno())
    say(f"data written in {time.time() - t0:.1f} s")

    # ---- timestamps: per-sample, so copied verbatim ----------------------- #
    h_ts = hashlib.sha256()
    with open(src_base + "_timestamp.xdat", "rb") as fin, open(part_ts, "wb") as fout:
        for blk in iter(lambda: fin.read(8 << 20), b""):
            fout.write(blk)
            h_ts.update(blk)
            h_all.update(blk)
        fout.flush()
        os.fsync(fout.fileno())
    src_ts_sha = _sha256_file(src_base + "_timestamp.xdat")
    if h_ts.hexdigest() != src_ts_sha:
        _quarantine(dst_base, [part_data, part_ts])
        raise StripFailed("the timestamp copy does not match the source hash")

    # ---- GATE A: bit-exactness -------------------------------------------- #
    say(f"gate A: bit-exactness ({verify})")
    try:
        vres = verify_bit_exact(src_base, part_data, keep_l,
                                n_channels_in=n_in, n_channels_out=k,
                                n_samples=n, mode=verify, n_spot=n_spot,
                                chunk_samples=chunk_samples, progress=say)
    except StripFailed:
        _quarantine(dst_base, [part_data, part_ts])
        raise
    say(f"  exact over {vres['samples_compared']:,} samples")

    # ---- GATE B: dropped GPIO evidence ------------------------------------ #
    table = channel_table(meta)
    dropped_report = []
    live_din = []
    # A DROPPED DIGITAL INPUT IS REFUSED ONLY ON EVIDENCE OF A SIGNAL.
    #
    # The first version refused whenever a dropped din was not perfectly
    # constant. On 2026-09-13 that blocked the strip of a 24 h, 90 GB recording
    # because din_1 showed ONE transition pair: a single 1 ms blip 2.43 h in,
    # flat for the other 23.99 h, on an input with nothing plugged into it. A
    # camera frame pulse at 15 fps would be ~1.3 million transitions over the
    # same window. "Not constant" cannot separate those; counting can.
    #
    # Refuse on either signature of something real:
    #   - two or more complete pulses (>= 4 transitions), or
    #   - a level held away from its resting value for more than a second.
    # Anything smaller is recorded with its exact counts and does not block.
    MIN_TRANSITIONS_TO_REFUSE = 4     # 2 complete pulses
    MIN_SAMPLES_TO_REFUSE = 1000      # 1 s at 1 kHz
    for j, i in enumerate(drop_idx):
        row = table[i]
        # bool() around the WHOLE expression: `and` returns its second operand,
        # so `bool(a) and np_scalar` is a numpy bool_, which json refuses.
        const = bool(dmin[j] == dmax[j] and dnan[j] == 0)
        rec = {"idx": i, "chan_name": row["chan_name"],
               "chan_type": row["chan_type"],
               "min": None if not np.isfinite(dmin[j]) else float(dmin[j]),
               "max": None if not np.isfinite(dmax[j]) else float(dmax[j]),
               "n_nan": int(dnan[j]), "constant": const,
               "transitions": int(dtrans[j]),
               "samples_off_resting": int(dneq[j]),
               "resting_level": None if not np.isfinite(dfirst[j]) else float(dfirst[j])}
        dropped_report.append(rec)
        if row["chan_type"] == "din0" and (
                int(dtrans[j]) >= MIN_TRANSITIONS_TO_REFUSE
                or int(dneq[j]) > MIN_SAMPLES_TO_REFUSE):
            live_din.append(rec)
    gate_b_override = None
    if live_din and gpio_never_connected:
        # THE OPERATOR ASSERTS NOTHING WAS EVER WIRED TO THE GPIO HEADER.
        #
        # The thresholds below stay as they are, because they will be
        # load-bearing the moment the XDAQ -> Pi hardware sync is wired. This
        # escape hatch is for recordings from the era when the header was
        # empty, where a "live" din can only be noise on a floating input. It
        # is recorded in the report so the claim is auditable, never silent.
        gate_b_override = {
            "reason": "operator asserts nothing was connected to the GPIO header",
            "asserted_via": "--gpio-never-connected",
            "channels": live_din,
        }
        for r in live_din:
            say(f"  GATE B OVERRIDDEN for {r['chan_name']}: "
                f"{r['transitions']} transitions, {r['samples_off_resting']} samples "
                f"off resting, on an input asserted to be unconnected")
        live_din = []
    if live_din:
        _quarantine(dst_base, [part_data, part_ts])
        names = ", ".join(
            f"{r['chan_name']} ({r['transitions']} transitions, "
            f"{r['samples_off_resting']} samples off its resting level)"
            for r in live_din)
        raise StripFailed(
            f"GATE B: dropping a LIVE digital input: {names}. din is where a "
            "camera frame pulse or TTL sync arrives; discarding a varying one is "
            "unrecoverable. Re-run with --with-gpio, or name the din channels "
            "explicitly in --keep-index.")
    for r in dropped_report:
        if r["chan_type"] == "din0" and not r["constant"]:
            say(f"  note: dropped {r['chan_name']} is not perfectly flat "
                f"({r['transitions']} transitions, {r['samples_off_resting']} "
                f"samples off resting) -- far below the threshold for a real "
                f"signal, recorded in the report and NOT blocking")
        elif not r["constant"]:
            # Normal for aux (an analog sensor always wanders) and for dout
            # (a line we drive ourselves, reconstructible and not data).
            say(f"  note: dropped {r['chan_name']} ({r['chan_type']}) varies "
                f"{r['min']:.6g}..{r['max']:.6g} -- recorded in the report")

    # ---- publish: data, timestamps, SIDECAR LAST -------------------------- #
    dataset_checksum = h_all.hexdigest()
    out_meta = rewrite_metadata(
        meta, plan,
        dataset_checksum=dataset_checksum,
        source_data_sha256=_sha256_file(src_base + "_data.xdat"),
        source_timestamp_sha256=src_ts_sha)
    os.replace(part_data, dst_data)
    os.replace(part_ts, dst_ts)
    _write_sidecar(dst_json, out_meta)      # last: it is the commit record

    # ---- GATES C, D, E ---------------------------------------------------- #
    C = _import_criteria()
    integ = C.file_integrity(dst_base)
    problems = []
    if integ["verdict"] != "INTACT":
        problems.append(f"gate C: output is {integ['verdict']}: {integ['reason']}")
    elif integ["n_channels"] != k:
        problems.append(f"gate C: output has {integ['n_channels']} channels, want {k}")

    try:
        _x, labels, fs2, n2 = C.open_xdat(dst_base)
        del _x
        if tuple(labels) != plan.keep_labels:
            problems.append("gate D: open_xdat labels differ from the plan")
        if fs2 != plan.fs or n2 != n:
            problems.append(f"gate D: open_xdat gives fs={fs2}, n={n2}; "
                            f"want fs={plan.fs}, n={n}")
    except Exception as exc:
        problems.append(f"gate D: open_xdat raised {exc!r}")

    probe = None
    if radiens_probe:
        probe = _radiens_probe(dst_base, expect_channels=k, expect_fs=plan.fs)
        if probe.get("skipped"):
            say(f"gate E: SKIPPED, question left open -- {probe.get('question')}")
        elif not probe.get("ok"):
            problems.append(f"gate E: radiens could not parse the output: "
                            f"{probe.get('error')}")

    if problems:
        _quarantine(dst_base, [dst_data, dst_ts, dst_json])
        raise StripFailed("; ".join(problems))

    report = {
        "status": "verified",
        "tool": TOOL, "version": TOOL_VERSION,
        "utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "src_base": src_base, "dst_base": dst_base,
        "plan": _plan_dict(plan),
        "dataset_checksum": dataset_checksum,
        "data_sha256": h_data.hexdigest(),
        "timestamp_sha256": h_ts.hexdigest(),
        "verify": vres,
        "integrity_out": integ,
        "dropped_gpio": dropped_report,
        "radiens_probe": probe,
        "qc_bundle_present": qc_bundle_present(src_base),
        "gate_b_override": gate_b_override,
        "source_unclean_shutdown": os.path.basename(src_base) + ".xdat.json"
                                   in stale_live_flags(),
        "elapsed_s": round(time.time() - t0, 1),
    }
    say(f"VERIFIED  {dst_base}  "
        f"{plan.bytes_in / 1e9:.2f} -> {plan.bytes_out / 1e9:.2f} GB "
        f"({100 * plan.saving:.1f}% smaller)")
    if not report["qc_bundle_present"]:
        say("WARNING: NO QC BUNDLE for the source. The stripped copy has no "
            "wire-free floor and can never be QC'd again.")
    return report


# --------------------------------------------------------------------------- #
# small helpers
# --------------------------------------------------------------------------- #

def _jsonable(obj):
    """Coerce numpy scalars/arrays so bookkeeping cannot fail after a good strip.

    The stripped data is already on disk and verified by the time a report is
    written. Losing the report to a TypeError would throw away the provenance
    record of work that actually succeeded, so this is deliberately forgiving.
    """
    if isinstance(obj, (np.integer,)):
        return int(obj)
    if isinstance(obj, (np.floating,)):
        return float(obj)
    if isinstance(obj, (np.bool_,)):
        return bool(obj)
    if isinstance(obj, np.ndarray):
        return obj.tolist()
    return str(obj)


def _sha256_file(path: str, block: int = 8 << 20) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for blk in iter(lambda: fh.read(block), b""):
            h.update(blk)
    return h.hexdigest()


def _sha256_concat(data_path: str, ts_path: str, block: int = 8 << 20) -> str:
    """sha256(data || timestamp) -- the measured formula for dataset_checksum."""
    h = hashlib.sha256()
    for path in (data_path, ts_path):
        with open(path, "rb") as fh:
            for blk in iter(lambda: fh.read(block), b""):
                h.update(blk)
    return h.hexdigest()


def _quarantine(dst_base: str, files: Iterable[str]) -> list[str]:
    """Rename a failed output so nothing can mistake it for a good recording."""
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    moved = []
    for f in files:
        if os.path.exists(f):
            tag = f.replace(dst_base, f"{dst_base}.REJECTED.{stamp}")
            os.replace(f, tag)
            moved.append(tag)
    return moved


def _plan_dict(plan: StripPlan) -> dict:
    return {"fs": plan.fs, "n_samples": plan.n_samples,
            "n_channels_in": plan.n_channels_in,
            "n_channels_out": plan.n_channels_out,
            "keep": list(plan.keep), "keep_labels": list(plan.keep_labels),
            "keep_chan_names": list(plan.keep_chan_names),
            "signals_out": plan.signals_out,
            "bytes_in": plan.bytes_in, "bytes_out": plan.bytes_out,
            "saving_pct": round(100 * plan.saving, 2),
            "integrity_in": plan.integrity_in}


# A probe failure that means "no hub to ask", not "the file is bad". Measured
# 2026-09-11: this host has only `allegoserver`; there is no Videre server binary
# under /opt/allego (only videre_man.md and videre_cheat_sheet.md), so
# FileSystemClient has nothing to connect to and fails with gRPC code 14.
_PROBE_UNAVAILABLE_MARKERS = (
    "ClientType.VIDERE",
    "StatusCode.UNAVAILABLE",
    "Error code: 14",
    "failed to connect to all addresses",
    "Connection refused",
)


def _radiens_probe(dst_base: str, *, expect_channels: int, expect_fs: int) -> dict:
    """GATE E: can the Radiens stack itself still parse the output?

    The question is real and cannot be answered by reading code, because the
    output keeps `sensors_by_port[port].num_channels` at the physical headstage
    size while writing fewer columns. But it can only be ANSWERED where a Videre
    hub exists, and this host does not have one -- `FileSystemClient` talks to
    the Videre file hub, not to `allegoserver`.

    So an unreachable hub returns `skipped`, which the caller must NOT treat as a
    failure: "we could not ask" is not "the file is broken". Only a hub that
    answers and rejects the file fails the gate. When the gate is skipped the
    question stays OPEN and the report says so, rather than implying a pass.
    """
    try:
        from radiens import FileSystemClient
    except ImportError as exc:
        return {"ok": None, "skipped": True,
                "error": f"radiens not importable: {exc}",
                "question": "unproven: no radiens in this interpreter"}
    try:
        fsc = FileSystemClient()
        md = fsc.get_data_file_metadata(dst_base + "_data.xdat")
        got_ch = getattr(md, "num_sigs", None) or getattr(md, "num_channels", None)
        return {"ok": True, "skipped": False, "reported": str(md)[:400],
                "channels": got_ch, "expected_channels": expect_channels}
    except Exception as exc:
        text = f"{type(exc).__name__}: {exc}"
        if any(m in text for m in _PROBE_UNAVAILABLE_MARKERS):
            return {"ok": None, "skipped": True, "error": text,
                    "question": "unproven: no Videre hub is running on this host, "
                                "so whether the Radiens reader accepts a stripped "
                                "file is UNTESTED"}
        return {"ok": False, "skipped": False, "error": text}


def default_dst(src_base: str, out_dir: str | os.PathLike | None = None) -> str:
    """Same base NAME in STRIPPED_ROOT, so `open_xdat(base)` call sites are
    unchanged and the two files are obviously the same recording."""
    root = Path(out_dir) if out_dir else PATHS.STRIPPED_ROOT
    return str(root / os.path.basename(src_base))


# --------------------------------------------------------------------------- #
# CLI
# --------------------------------------------------------------------------- #

def _print_dry_run(plan: StripPlan, meta: dict, src_base: str,
                   dst_dir: Path) -> None:
    table = channel_table(meta)
    kept = set(plan.keep)
    print(f"source      {src_base}")
    print(f"            {plan.n_channels_in} ch x {plan.n_samples:,} samples "
          f"@ {plan.fs} Hz = {plan.n_samples / plan.fs / 3600:.3f} h")
    print(f"            integrity {plan.integrity_in['verdict']}: "
          f"{plan.integrity_in['reason']}")
    print(f"output      {plan.dst_base}")
    print(f"            {plan.n_channels_out} ch, "
          f"{plan.bytes_in / 1e9:.2f} -> {plan.bytes_out / 1e9:.2f} GB "
          f"({100 * plan.saving:.1f}% smaller)")
    free = _free_bytes(dst_dir) if dst_dir.exists() else _free_bytes(Path.home())
    print(f"free space  {free / 1e9:.1f} GB -> "
          f"{(free - plan.bytes_out) / 1e9:.1f} GB after")
    print(f"signals     {plan.signals_out}")
    print()
    print("  out  orig  chan_name  type   label      selected")
    for j, i in enumerate(plan.keep):
        r = table[i]
        print(f"  {j:3d}  {r['sys_chan_idx']:4d}  {r['chan_name']:9s}  "
              f"{r['chan_type']:5s}  {r['label']:9s}  "
              f"{'yes' if r['is_selected'] else '-'}")
    dropped_gpio = [table[i] for i in plan.dropped_gpio]
    if dropped_gpio:
        print()
        print("  dropped non-primary channels (gate B judges these):")
        for r in dropped_gpio:
            print(f"       {r['chan_name']:9s}  {r['chan_type']:5s}  {r['label']}")
    print()
    if qc_bundle_present(src_base):
        print("QC BUNDLE: present")
    else:
        print("QC BUNDLE: MISSING -- stripping deletes the in-file wire-free "
              "floor, and")
        print("           without a cached feature set this recording can never "
              "be QC'd again.")
        print("           Run: cards/ladder.py <base> --cohort <id> --cache "
              f"{PATHS.CACHE_ROOT}/{os.path.basename(src_base)}.npz")
    # settle_s=0 here: the dry run is a report, not a gate, and it must not
    # pause five seconds to print a line.
    busy = rig_is_busy(source_base=src_base, settle_s=0)
    if busy:
        print(f"RIG BUSY:  {busy}")
    stale = stale_live_flags()
    if stale:
        print(f"NOTE:      {len(stale)} recording(s) still flagged "
              f"is_live_recording while idle, i.e. they did not shut down "
              f"cleanly: {', '.join(stale)}")
    print("\n(dry run: nothing was written)")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        prog="strip_channels",
        description="Write a new XDAT recording holding only the named channels.")
    ap.add_argument("src_base",
                    help="recording base name (looked up under EEG_RAW_ROOT) "
                         "or a full base path, with no _data.xdat suffix")
    ap.add_argument("--out", default=None,
                    help=f"output directory (default {PATHS.STRIPPED_ROOT})")
    sel = ap.add_mutually_exclusive_group(required=True)
    sel.add_argument("--keep-selected", action="store_true",
                     help="keep the channels the file's own is_selected flags name")
    sel.add_argument("--keep-labels", default=None,
                     help="comma-separated port/site labels, e.g. A/1,A/2,A/33")
    sel.add_argument("--keep-index", default=None,
                     help="comma-separated file indices; validated against THIS "
                          "file and refused if out of range")
    ap.add_argument("--with-gpio", action="store_true",
                    help="also keep every aux/din/dout channel")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--verify", choices=("full", "spot"), default="full")
    ap.add_argument("--n-spot", type=int, default=64)
    ap.add_argument("--no-resume", action="store_true")
    ap.add_argument("--force", action="store_true",
                    help="re-strip even if a verified output already exists")
    ap.add_argument("--radiens-probe", action="store_true",
                    help="gate E: prove the Radiens stack can parse the output")
    ap.add_argument("--min-free-gb", type=float, default=300.0)
    ap.add_argument("--allow-truncated", action="store_true")
    ap.add_argument("--require-idle", action="store_true",
                    help="refuse if Allego looks like it is writing")
    ap.add_argument("--gpio-never-connected", action="store_true",
                    help="gate B: drop a 'live' din anyway, because nothing was "
                         "wired to the GPIO header when this was recorded. "
                         "Recorded in the report as gate_b_override.")
    ap.add_argument("--chunk-samples", type=int, default=DEFAULT_CHUNK_SAMPLES)
    ap.add_argument("--report", default=None,
                    help="where to write the JSON report "
                         "(default <dst_base>.strip-report.json)")
    a = ap.parse_args(argv)

    src_base = PATHS.recording(a.src_base)
    for suffix in ("_data.xdat", ".xdat.json"):
        if not os.path.exists(src_base + suffix):
            print(f"error: {src_base + suffix} does not exist", file=sys.stderr)
            return 2
    dst_base = default_dst(src_base, a.out)

    try:
        meta = read_meta(src_base)
        keep = resolve_keep(
            meta,
            selected=a.keep_selected,
            labels=a.keep_labels.split(",") if a.keep_labels else None,
            indices=[int(x) for x in a.keep_index.split(",")] if a.keep_index else None,
            with_gpio=a.with_gpio)
        plan = plan_strip(src_base, dst_base, keep,
                          allow_truncated=a.allow_truncated, meta=meta)
    except StripRefused as exc:
        print(f"REFUSED: {exc}", file=sys.stderr)
        return 1
    except (KeyError, ValueError) as exc:
        print(f"REFUSED: malformed metadata: {exc!r}", file=sys.stderr)
        return 1

    if a.dry_run:
        _print_dry_run(plan, meta, src_base, Path(dst_base).parent)
        return 0

    try:
        report = strip(src_base, dst_base, keep,
                       chunk_samples=a.chunk_samples,
                       resume=not a.no_resume and not a.force,
                       verify=a.verify, n_spot=a.n_spot,
                       radiens_probe=a.radiens_probe,
                       min_free_gb=a.min_free_gb,
                       allow_truncated=a.allow_truncated,
                       require_idle=a.require_idle,
                       gpio_never_connected=a.gpio_never_connected,
                       meta=meta)
    except StripRefused as exc:
        print(f"REFUSED: {exc}", file=sys.stderr)
        return 1
    except StripFailed as exc:
        print(f"FAILED: {exc}", file=sys.stderr)
        return 1

    report_path = a.report or (dst_base + ".strip-report.json")
    Path(report_path).write_text(json.dumps(report, indent=2, default=_jsonable))
    print(f"report      {report_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
