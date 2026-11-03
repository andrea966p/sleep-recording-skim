"""Stage 0 of the 2026-11 HLB re-score: per-mouse CSV on the SKIM NAS -> verified local float32 arrays.

For every <batch>/<Baseline|Recovery>/<folder>/<folder>.csv under the NAS root:
  1. copy to a local temp file while hashing (sha256 must equal info.json upload.sha256_remote),
  2. parse EEG, EMG, timestamp_raw with pyarrow,
  3. check the sample counter is continuous (gaps are recorded, never hidden),
  4. write eeg.npy, emg.npy (float32 uV, 1000 Hz) + meta.json, delete the temp CSV.
The NAS is only read. Output: OUT/<batch>/<B|R>/<mouseID>/.

Usage: ingest.py OUT [--jobs 2] [--only HLBSSL33_R ...]
"""
import argparse, hashlib, json, shutil, sys, time
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np
import pyarrow.csv as pacsv

NAS = Path("/mnt/skimnas/02_Data_Sleep/andrea")
BATCHES = ["HLBWSD", "HLBSSD", "HLBWSL", "HLBSSL"]


def one(info_path: Path, out_root: Path) -> str:
    info = json.loads(info_path.read_text())
    tp = "B" if info["condition"] == "Baseline" else "R"
    out = out_root / info["batch"] / tp / info["mouseID"]
    if (out / "meta.json").exists():
        return f"skip {out}"
    out.mkdir(parents=True, exist_ok=True)
    src = info_path.with_name(info["upload"]["csv"])
    tmp = out / "tmp.csv"
    h, t0 = hashlib.sha256(), time.time()
    with open(src, "rb") as f, open(tmp, "wb") as g:
        while b := f.read(16 << 20):
            h.update(b)
            g.write(b)
    sha = h.hexdigest()
    if sha != info["upload"]["sha256_remote"]:
        tmp.unlink()
        return f"FAIL sha {src}"
    tbl = pacsv.read_csv(tmp, convert_options=pacsv.ConvertOptions(
        include_columns=["timestamp_raw", "EEG", "EMG"],
        column_types={"EEG": "float32", "EMG": "float32", "timestamp_raw": "int64"}))
    with open(tmp, "rb") as f:
        f.readline()
        first = f.readline().decode().split(",")[2]
        f.seek(-200, 2)
        last = f.read().decode().strip().splitlines()[-1].split(",")[2]
    ts = tbl["timestamp_raw"].to_numpy()
    d = np.diff(ts)
    gaps = [{"at_sample": int(i + 1), "missing": int(d[i] - 1)} for i in np.flatnonzero(d != 1)]
    np.save(out / "eeg.npy", tbl["EEG"].to_numpy())
    np.save(out / "emg.npy", tbl["EMG"].to_numpy())
    meta = {k: info[k] for k in ("mouseID", "batch", "condition", "position", "channels", "allego_base", "window", "pairing")}
    meta.update(fs=1000.0, n=int(len(ts)), start_kst=first, end_kst=last, counter_gaps=gaps, csv_sha256=sha, sha_ok=True,
                old_qc_verdict=info.get("qc", {}).get("verdict"), old_qc_why=info.get("qc", {}).get("why"),
                old_qc_rungs=[(r["name"], r["verdict"], r["headline"]) for r in info.get("qc", {}).get("rungs", [])],
                source_csv=str(src), ingest_s=round(time.time() - t0, 1))
    (out / "meta.json").write_text(json.dumps(meta, indent=1))
    tmp.unlink()
    return f"ok {out} {len(ts)/3.6e6:.2f} h gaps={len(gaps)} {meta['ingest_s']} s"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("out", type=Path)
    ap.add_argument("--jobs", type=int, default=2)
    ap.add_argument("--only", nargs="*")
    a = ap.parse_args()
    infos = sorted(p for b in BATCHES for p in (NAS / b).glob("*/*/*.info.json"))
    if a.only:
        infos = [p for p in infos if any(o in p.name for o in a.only)]
    print(f"{len(infos)} recordings", flush=True)
    with ProcessPoolExecutor(a.jobs) as ex:
        for msg in ex.map(one, infos, [a.out] * len(infos)):
            print(time.strftime("%H:%M:%S"), msg, flush=True)


if __name__ == "__main__":
    sys.exit(main())
