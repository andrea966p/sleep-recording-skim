#!/usr/bin/env python3
"""per_mouse_csv.py -- one CSV per mouse, from a STRIPPED recording.

WHY THIS EXISTS. The lab's analysis reads one table per animal, with the
recording's own timestamps in the same file. It does not read XDAT. The column
names follow the lab's reference MATLAB export
(`03_Data_Mouse/diane/20260816_H5A251F0209_A01__BSR.mat`, read 2026-09-29):

    timestamp_raw,timestamp_sec,datetime_kst,EEG,EMG
    57403264,0.000,2026-09-10 08:59:59.012,12.410,-3.020

  timestamp_raw   int64 from `<base>_timestamp.xdat`, VERBATIM. Allego's device
                  sample counter, so it is not zero-based: it counts from when
                  the Allego server session started, not from this recording.
  timestamp_sec   (timestamp_raw - first exported) / fs. Zero at the first row.
                  The reference .mat is built the same way (0.000, 0.001, ...),
                  and a gap in the counter shows up as a jump, not hidden.
  datetime_kst    status.start_time (UTC, ms) + (timestamp_raw - the FILE's first)
                  / fs, shown in KST. Absolute, so it is right in a trimmed CSV.
                  start_time is written by Allego when recording begins, so it is
                  accurate to about a second, not to a sample.
  EEG, EMG, ...   one column per ROLE the layout declares, upper-cased, in
                  microvolts, 3 decimals (Intan steps are 0.195 uV, so nothing
                  is rounded away that the amplifier resolved).

THE MAPPING FROM MOUSE TO COLUMN COMES FROM THE CALLER, AS LABELS. The recorder
knows which slot holds which mouse and which site carries which role; this tool
knows neither. It is handed `{"EEG": "A/1", "EMG": "A/2"}` per mouse and resolves
each label against the stripped sidecar's own `kept_labels`. A label that is
missing, or present twice, is REFUSED. A silent wrong-channel CSV would be the
worst thing this tool could produce, because nothing downstream could tell.

READS THE STRIPPED FILE, NOT THE RAW. Sixteen columns instead of 262, and the
strip has already verified those columns bit-exact against the original.

STREAMING. `np.fromfile` with an offset, one chunk at a time, never np.memmap
(see strip_channels._read_block: a memmap hit 9.26 GB RSS on a 5.26 GB file).
Each chunk is read ONCE and written to every mouse's CSV, rather than one pass
per mouse, which would read the file eight times.

VERIFICATION, NOT JUST WRITING. After each CSV is closed it is re-read: the row
count must equal the sample count, the first and last timestamp_raw must match
the timestamp file, and 1000 rows chosen in advance are parsed back and compared
against the xdat values (|diff| <= 0.0005 uV, the %.3f rounding). The sha256 is
taken over the bytes as they are written, and the uploader re-hashes the file
independently before it trusts that number.

AN ANALYSIS WINDOW, OPTIONALLY. `spec["window"] = {"start_kst": "2026-08-20 09:00",
"end_kst": "2026-08-21 09:00"}` exports only the samples whose time falls in
[start, end). Found through the timestamp counter, so a dropout inside the file
cannot shift it. If the recording does not cover the whole window, what it does
cover is exported and the shortfall at each end is RECORDED, in seconds, in the
report -- never silently. A window the recording does not touch is refused.

Run:
    PYTHONPATH=. python3 -m export.per_mouse_csv <stripped_base> --spec spec.json \
        [--out DIR] [--require-idle --source-base <raw base>]

spec.json:
    {"mice": [{"slot": "A1", "mouse_id": "HLBSSL31",
               "file_base": "20260921_HLBSSL31_R",
               "columns": {"EEG": "A/1", "EMG": "A/2"}}, ...],
     "meta": {...anything, copied into the report}}
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from convert import strip_channels as SC      # noqa: E402  (_read_block, rig_is_busy)
from core import paths as PATHS               # noqa: E402

TOOL = "export.per_mouse_csv"
TOOL_VERSION = "2026.09.29"

KST = timezone(timedelta(hours=9))
CHUNK = 65_536                      # samples per read; ~4 MB of CSV per mouse
BYTES_PER_ROW_EST = 58              # measured 55.5 on 2-role rows; margin for 3 roles
MIN_FREE_GB = 300.0                 # the same floor the stripper keeps on this disk
SPOT_ROWS = 1000
TOL_UV = 0.0005 + 1e-6


class ExportRefused(RuntimeError):
    """A precondition said no. Nothing was written."""


class ExportFailed(RuntimeError):
    """A CSV was written but did not verify. It is left as `.REJECTED`."""


# --------------------------------------------------------------------------- #
# inputs
# --------------------------------------------------------------------------- #

def read_stripped(base: str) -> dict:
    """The sidecar facts this tool needs, checked against the files on disk."""
    meta = json.loads(Path(base + ".xdat.json").read_text())
    st = meta.get("status") or {}
    prov = st.get("dataset_provenance") or []
    if not prov or not isinstance(prov, list):
        raise ExportRefused(
            f"{os.path.basename(base)} has no dataset_provenance; this tool reads "
            "STRIPPED recordings only, whose sidecar records which label is which "
            "column")
    labels = list(prov[-1].get("kept_labels") or [])
    n_ch = int((st.get("shape") or [0, 0])[1])
    if not labels or len(labels) != n_ch:
        raise ExportRefused(
            f"kept_labels has {len(labels)} entries but the file has {n_ch} "
            "columns; refusing to guess which is which")
    fs = float(st.get("samp_freq") or 0)
    if fs <= 0:
        raise ExportRefused("status.samp_freq is missing")
    data, ts = base + "_data.xdat", base + "_timestamp.xdat"
    n = os.path.getsize(data) // (n_ch * 4)
    n_ts = os.path.getsize(ts) // 8
    if n != n_ts:
        raise ExportRefused(f"data holds {n} samples but timestamps hold {n_ts}")
    if n == 0:
        raise ExportRefused(f"{os.path.basename(base)} holds no samples")
    if st.get("num_smpl") is not None and int(st["num_smpl"]) != n:
        raise ExportRefused(f"sidecar says num_smpl={st['num_smpl']}, files hold {n}")
    start = st.get("start_time")
    try:
        t0 = datetime.fromisoformat(str(start).replace("Z", "+00:00"))
    except ValueError:
        raise ExportRefused(f"status.start_time {start!r} is not an ISO time")
    return {"labels": labels, "n_ch": n_ch, "n": n, "fs": fs, "start_time": start,
            "t0": t0, "provenance": prov[-1], "dataset_checksum": st.get("dataset_checksum"),
            "data": data, "ts": ts}


def resolve_columns(spec: dict, labels: list[str]) -> list[dict]:
    """Each mouse's roles -> file column indices. Refuses any miss or ambiguity."""
    mice = spec.get("mice") or []
    if not mice:
        raise ExportRefused("the spec names no mice")
    out, seen_bases = [], set()
    for m in mice:
        fb = str(m.get("file_base") or "")
        if not fb or "/" in fb or fb.startswith("."):
            raise ExportRefused(f"bad file_base {fb!r}")
        if fb in seen_bases:
            raise ExportRefused(f"two mice share the file_base {fb!r}")
        seen_bases.add(fb)
        cols = m.get("columns") or {}
        if not cols:
            raise ExportRefused(f"{fb}: no columns")
        idx = {}
        for role, lab in cols.items():
            hits = [i for i, l in enumerate(labels) if l == lab]
            if len(hits) != 1:
                raise ExportRefused(
                    f"{fb}: role {role} wants {lab!r}, which appears {len(hits)} "
                    f"times in this file's kept_labels {labels}")
            idx[str(role).upper()] = hits[0]
        out.append({**m, "col_idx": idx})
    return out


# --------------------------------------------------------------------------- #
# formatting
# --------------------------------------------------------------------------- #

class _Clock:
    """Formats `datetime_kst` fast: one strftime per second, not per row."""

    def __init__(self, t0: datetime):
        self.t0_ms = int(round(t0.timestamp() * 1000))
        self._cache: dict[int, str] = {}

    def prefix(self, sec: int) -> str:
        p = self._cache.get(sec)
        if p is None:
            if len(self._cache) > 4096:
                self._cache.clear()
            p = datetime.fromtimestamp(sec, KST).strftime("%Y-%m-%d %H:%M:%S")
            self._cache[sec] = p
        return p


def format_rows(raw: np.ndarray, raw0: int, fs: float, clock: _Clock,
                cols: list[np.ndarray], raw_file0: int | None = None) -> str:
    """CSV text for one chunk. `cols` are float32 arrays, one per role.

    `raw0` is the first EXPORTED counter value (timestamp_sec is 0 there);
    `raw_file0` is the file's first, which `clock` (start_time) refers to.
    """
    raw_file0 = raw0 if raw_file0 is None else raw_file0
    d = raw - raw0
    dc = raw - raw_file0
    rl = raw.tolist()
    vals = [c.astype(np.float64).tolist() for c in cols]
    if fs == 1000.0:
        # exact integer milliseconds: no float drift over a 60 h file
        ds, dm = np.divmod(d, 1000)
        tot = clock.t0_ms + dc
        ts_s, ts_m = np.divmod(tot, 1000)
        sec = [f"{a}.{b:03d}" for a, b in zip(ds.tolist(), dm.tolist())]
        when = [f"{clock.prefix(a)}.{b:03d}" for a, b in zip(ts_s.tolist(), ts_m.tolist())]
    else:
        secs = d / fs
        sec = [f"{x:.6f}" for x in secs.tolist()]
        tot = clock.t0_ms + np.round(dc / fs * 1000).astype(np.int64)
        ts_s, ts_m = np.divmod(tot, 1000)
        when = [f"{clock.prefix(a)}.{b:03d}" for a, b in zip(ts_s.tolist(), ts_m.tolist())]
    if len(vals) == 2:
        a, b = vals
        return "".join([f"{r},{s},{w},{x:.3f},{y:.3f}\n"
                        for r, s, w, x, y in zip(rl, sec, when, a, b)])
    return "".join(f"{r},{s},{w}," + ",".join(f"{v:.3f}" for v in row) + "\n"
                   for r, s, w, *row in zip(rl, sec, when, *vals))


# --------------------------------------------------------------------------- #
# window
# --------------------------------------------------------------------------- #

def _parse_kst(s: str) -> datetime:
    t = datetime.fromisoformat(str(s).strip().replace(" ", "T"))
    return t.replace(tzinfo=KST) if t.tzinfo is None else t


def resolve_window(window: dict | None, info: dict, ts_first: int) -> dict:
    """[lo, hi) sample indices for a KST window, plus what was actually covered.

    Uses the timestamp COUNTER (binary search on a read-only memmap of the int64
    timestamps -- a few pages, not the file), so a gap inside the recording moves
    the index but never the time.
    """
    n, fs, t0 = info["n"], info["fs"], info["t0"]
    if not window:
        return {"lo": 0, "hi": n, "requested": None}
    ws, we = _parse_kst(window["start_kst"]), _parse_kst(window["end_kst"])
    if we <= ws:
        raise ExportRefused(f"window end {we} is not after its start {ws}")
    ts = np.memmap(info["ts"], dtype=np.int64, mode="r", shape=(n,))
    def raw_at(t):
        return ts_first + int(round((t - t0).total_seconds() * fs))
    lo = int(np.searchsorted(ts, raw_at(ws), side="left"))
    hi = int(np.searchsorted(ts, raw_at(we), side="left"))
    if hi <= lo:
        raise ExportRefused(
            f"the recording ({t0.astimezone(KST):%Y-%m-%d %H:%M:%S} for "
            f"{n / fs / 3600:.2f} h) does not overlap the window {window}")
    first_t = t0 + timedelta(seconds=(int(ts[lo]) - ts_first) / fs)
    last_t = t0 + timedelta(seconds=(int(ts[hi - 1]) - ts_first + 1) / fs)
    fmt = lambda t: t.astimezone(KST).strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
    return {"lo": lo, "hi": hi,
            "requested": {"start_kst": fmt(ws), "end_kst": fmt(we),
                          "hours": round((we - ws).total_seconds() / 3600, 4)},
            "actual": {"start_kst": fmt(first_t), "end_kst": fmt(last_t),
                       "hours": round((hi - lo) / fs / 3600, 4)},
            "missing_at_start_s": round(max(0.0, (first_t - ws).total_seconds()), 3),
            "missing_at_end_s": round(max(0.0, (we - last_t).total_seconds()), 3)}


# --------------------------------------------------------------------------- #
# export
# --------------------------------------------------------------------------- #

def _sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for blk in iter(lambda: fh.read(8 << 20), b""):
            h.update(blk)
    return h.hexdigest()


def _git_commit() -> str | None:
    try:
        import subprocess
        return subprocess.run(["git", "rev-parse", "HEAD"], cwd=Path(__file__).parent,
                              capture_output=True, text=True, timeout=5).stdout.strip() or None
    except Exception:
        return None


def verify_csv(path: Path, *, n: int, first_raw: int, last_raw: int, roles: list[str],
               spot: dict[int, int], expect: dict[int, list[float]]) -> dict:
    """Re-read a finished CSV. Raises ExportFailed on any disagreement."""
    header = "timestamp_raw,timestamp_sec,datetime_kst," + ",".join(roles)
    with open(path, "rb") as fh:
        first_line = fh.readline().decode().rstrip("\n")
        if first_line != header:
            raise ExportFailed(f"{path.name}: header {first_line!r}, want {header!r}")
        data_start = fh.tell()
        rows = 0
        last_line = b""
        tail = b""
        for blk in iter(lambda: fh.read(8 << 20), b""):
            rows += blk.count(b"\n")
            tail = (tail + blk)[-512:]
        last_line = tail.rstrip(b"\n").rsplit(b"\n", 1)[-1]
        if rows != n:
            raise ExportFailed(f"{path.name}: {rows} data rows, want {n}")
        fh.seek(data_start)
        first = fh.readline().split(b",")
        if int(first[0]) != first_raw or int(last_line.split(b",")[0]) != last_raw:
            raise ExportFailed(f"{path.name}: first/last timestamp_raw do not match "
                               "the timestamp file")
        worst = 0.0
        for i, off in spot.items():
            fh.seek(off)
            parts = fh.readline().decode().rstrip("\n").split(",")
            got = [float(x) for x in parts[3:]]
            want = expect[i]
            if len(got) != len(want):
                raise ExportFailed(f"{path.name}: row {i} has {len(got)} values")
            for g, w in zip(got, want):
                if np.isnan(g) or np.isnan(w):
                    # NaN never compares, so max() would silently skip it
                    if not (np.isnan(g) and np.isnan(w)):
                        raise ExportFailed(f"{path.name}: row {i} reads {got}, xdat has {want}")
                    continue
                worst = max(worst, abs(g - w))
            if worst > TOL_UV:
                raise ExportFailed(f"{path.name}: row {i} reads {got}, xdat has {want}")
    return {"rows": rows, "spot_rows": len(spot), "spot_max_abs_diff_uv": worst}


def export(stripped_base: str, spec: dict, out_dir: str | Path, *,
           require_idle: bool = False, source_base: str | None = None,
           min_free_gb: float = MIN_FREE_GB, chunk: int = CHUNK,
           progress=print) -> dict:
    say = progress or (lambda _m: None)
    base = str(stripped_base)
    name = os.path.basename(base)
    out = Path(out_dir)
    report_path = out / f"{name}.per-mouse-report.json"

    info = read_stripped(base)
    mice = resolve_columns(spec, info["labels"])
    n_file, fs = info["n"], info["fs"]
    ts_file0 = int(np.fromfile(info["ts"], dtype=np.int64, count=1)[0])
    win = resolve_window(spec.get("window"), info, ts_file0)
    lo0, hi0 = win["lo"], win["hi"]
    n = hi0 - lo0

    if require_idle:
        busy = SC.rig_is_busy(source_base=source_base)
        if busy:
            raise ExportRefused(f"the rig is busy ({busy}); exporting now would do "
                                "heavy disk work during a live recording")

    out.mkdir(parents=True, exist_ok=True)
    need = n * BYTES_PER_ROW_EST * len(mice)
    free = SC._free_bytes(out)
    if free - need < min_free_gb * 1e9:
        raise ExportRefused(
            f"{free / 1e9:.0f} GB free, the CSVs need about {need / 1e9:.0f} GB, "
            f"which would leave less than {min_free_gb:.0f} GB")

    prior = {}
    if report_path.exists():
        try:
            prior = {m["file_base"]: m for m in json.loads(report_path.read_text())["mice"]}
        except Exception:
            prior = {}

    ts_first = int(np.fromfile(info["ts"], dtype=np.int64, count=1, offset=lo0 * 8)[0])
    ts_last = int(np.fromfile(info["ts"], dtype=np.int64, count=1, offset=(hi0 - 1) * 8)[0])

    # which mice still need writing?
    todo, done = [], []
    for m in mice:
        csv = out / f"{m['file_base']}.csv"
        p = prior.get(m["file_base"])
        if (p and csv.exists() and csv.stat().st_size == p.get("bytes")
                and p.get("columns") == m.get("columns")
                and p.get("allego_base") == name and p.get("window") == win.get("requested")
                and _sha256_file(csv) == p.get("sha256")):
            say(f"  already exported and verified: {csv.name}")
            done.append(p)
        else:
            todo.append(m)

    import zlib
    rng = np.random.default_rng(zlib.crc32(name.encode()))
    spot_idx = np.unique(np.concatenate([[lo0, hi0 - 1], rng.integers(lo0, hi0, SPOT_ROWS)]))
    spot_set = set(int(i) for i in spot_idx)
    clock = _Clock(info["t0"])

    writers = []
    for m in todo:
        roles = list(m["col_idx"])
        part = out / f"{m['file_base']}.csv.part"
        fh = open(part, "wb")
        head = ("timestamp_raw,timestamp_sec,datetime_kst," + ",".join(roles) + "\n").encode()
        fh.write(head)
        h = hashlib.sha256(head)
        writers.append({"m": m, "roles": roles, "fh": fh, "h": h, "part": part,
                        "pos": len(head), "spot": {}, "expect": {}})

    t_start = time.time()
    try:
        for lo in range(lo0, hi0 if todo else lo0, chunk):
            hi = min(hi0, lo + chunk)
            block = SC._read_block(info["data"], lo, hi, info["n_ch"])
            raw = np.fromfile(info["ts"], dtype=np.int64, count=hi - lo, offset=lo * 8)
            want_here = [i for i in spot_set if lo <= i < hi]
            for w in writers:
                cols = [block[:, w["m"]["col_idx"][r]] for r in w["roles"]]
                text = format_rows(raw, ts_first, fs, clock, cols, raw_file0=ts_file0)
                b = text.encode()
                if want_here:
                    # byte offset of every spot row inside this chunk
                    offs = np.flatnonzero(np.frombuffer(b, dtype=np.uint8) == 10)
                    for i in want_here:
                        k = i - lo
                        w["spot"][i] = w["pos"] + (0 if k == 0 else int(offs[k - 1]) + 1)
                        w["expect"][i] = [float(block[k, w["m"]["col_idx"][r]])
                                          for r in w["roles"]]
                w["fh"].write(b)
                w["h"].update(b)
                w["pos"] += len(b)
            if lo > lo0 and ((lo - lo0) // chunk) % 200 == 0:
                pct = 100.0 * (hi - lo0) / n
                say(f"  {pct:5.1f}%  {(hi - lo0) / fs / 3600:.2f} h of {n / fs / 3600:.2f} h "
                    f"({time.time() - t_start:.0f} s)")
                if require_idle:
                    busy = SC.rig_is_busy(source_base=source_base, settle_s=0)
                    if busy:
                        raise ExportRefused(
                            f"a recording started while exporting ({busy}); stopped so "
                            "as not to compete with it. Retry after it ends.")
        for w in writers:
            w["fh"].flush()
            os.fsync(w["fh"].fileno())
            w["fh"].close()
    except BaseException:
        for w in writers:
            try:
                w["fh"].close()
            except Exception:
                pass
        raise

    results = list(done)
    for w in writers:
        m = w["m"]
        csv = out / f"{m['file_base']}.csv"
        try:
            chk = verify_csv(w["part"], n=n, first_raw=ts_first, last_raw=ts_last,
                             roles=w["roles"], spot=w["spot"], expect=w["expect"])
        except ExportFailed:
            w["part"].rename(w["part"].with_suffix(
                f".REJECTED.{datetime.now(timezone.utc):%Y%m%dT%H%M%SZ}"))
            raise
        os.replace(w["part"], csv)
        say(f"  VERIFIED {csv.name}: {chk['rows']} rows, "
            f"{csv.stat().st_size / 1e9:.2f} GB")
        results.append({
            "file_base": m["file_base"], "csv": csv.name, "slot": m.get("slot"),
            "mouse_id": m.get("mouse_id"), "columns": m.get("columns"),
            "roles": w["roles"], "allego_base": name, "window": win.get("requested"),
            "bytes": csv.stat().st_size, "sha256": w["h"].hexdigest(),
            "verify": chk})

    t0 = info["t0"]
    report = {
        "tool": TOOL, "version": TOOL_VERSION, "git_commit": _git_commit(),
        "utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "stripped_base": base, "allego_base": name,
        "samplingRate": fs, "n_samples": n, "duration_h": round(n / fs / 3600, 4),
        "startTime_utc": info["start_time"],
        "startTime_kst": t0.astimezone(KST).strftime("%Y-%m-%d %H:%M:%S.%f")[:-3],
        "timestamp_raw_first": ts_first, "timestamp_raw_last": ts_last,
        "window": {k: v for k, v in win.items() if k not in ("lo", "hi")} if win.get("requested") else None,
        "file": {"n_samples": n_file, "duration_h": round(n_file / fs / 3600, 4),
                 "timestamp_raw_first": ts_file0, "window_sample_range": [lo0, hi0]},
        "stripped_dataset_checksum": info["dataset_checksum"],
        "source": {k: info["provenance"].get(k) for k in
                   ("source_base", "source_dataset_uid", "source_dataset_checksum",
                    "source_data_sha256", "source_timestamp_sha256", "kept_labels")},
        "meta": spec.get("meta") or {},
        "mice": sorted(results, key=lambda r: r["file_base"]),
    }
    tmp = report_path.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(report, indent=2))
    os.replace(tmp, report_path)
    say(f"exported {len(results)} mice in {time.time() - t_start:.0f} s -> {out}")
    return report


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="per_mouse_csv", description=__doc__.split("\n")[0])
    ap.add_argument("stripped_base")
    ap.add_argument("--spec", required=True, help="JSON file naming mice, file bases, columns")
    ap.add_argument("--out", help="output dir (default <PER_MOUSE_ROOT>/<base>)")
    ap.add_argument("--require-idle", action="store_true")
    ap.add_argument("--source-base", help="the RAW recording, judged by growth when idle-checking")
    a = ap.parse_args(argv)
    spec = json.loads(Path(a.spec).read_text())
    out = a.out or (PATHS.PER_MOUSE_ROOT / os.path.basename(a.stripped_base))
    try:
        export(a.stripped_base, spec, out, require_idle=a.require_idle,
               source_base=a.source_base)
    except ExportRefused as exc:
        print(f"REFUSED: {exc}", file=sys.stderr)
        return 2
    except ExportFailed as exc:
        print(f"FAILED: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
