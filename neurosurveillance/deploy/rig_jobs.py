#!/usr/bin/env python3
"""What the rig is chewing on right now, as bars. See rig-jobs.sh.

EVERY BAR IS MEASURED FROM BYTES ON DISK, never from a percentage a job printed.
A job that dies leaves its .part where it stopped, so a bar that does not move is
a job that is not moving. A job that prints "97%" and then hangs would look fine.

The target size is arithmetic, not a guess:
    data bytes = samples x channels x 4        (float32, interleaved)
so a strip's target comes from the SOURCE header and the channel count on its own
command line, and an upload's target is the size of the file it is copying.
"""
from __future__ import annotations

import glob
import json
import os
import re
import subprocess
import sys
import time

RAW = "/home/skimlab/radix/data"
STRIPPED = "/home/skimlab/radix/stripped"
NAS = "/mnt/skimnas/03_Data_Mouse"
LOGS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logs")
BYTES_PER_SAMPLE = 4

C = {"g": "\033[32m", "y": "\033[33m", "r": "\033[31m", "d": "\033[2m", "b": "\033[1m", "0": "\033[0m"}
if not sys.stdout.isatty():
    C = dict.fromkeys(C, "")


def gb(n: float) -> str:
    return f"{n / 1e9:.2f} GB"


def bar(frac: float, width: int = 32) -> str:
    frac = max(0.0, min(1.0, frac))
    fill = int(frac * width)
    colour = C["g"] if frac >= 0.999 else C["y"]
    return f"{colour}{'█' * fill}{C['d']}{'░' * (width - fill)}{C['0']} {frac * 100:5.1f}%"


def procs() -> list[tuple[int, str]]:
    out = subprocess.run(["ps", "-eo", "pid=,args="], capture_output=True, text=True).stdout
    keep = ("convert.strip_channels", "nas_upload.py", "cards/ladder.py",
            "radix-s3-archive.sh", "aws s3 cp")
    rows = []
    for line in out.splitlines():
        line = line.strip()
        if not line:
            continue
        pid, _, args = line.partition(" ")
        # A shell that merely MENTIONS a job is not that job. This is the trap
        # that left watcher loops spinning for hours: `pgrep -f strip_channels`
        # matches the very shell running the pgrep.
        if args.startswith(("/bin/bash -c", "bash -c", "sh -c")) or "rig_jobs" in args:
            continue
        if any(k in args for k in keep):
            rows.append((int(pid), args))
    return rows


def header(meta_path: str) -> tuple[int, int] | None:
    try:
        s = json.load(open(meta_path))["status"]
        return int(s["num_smpl"]), int(s["signals"]["total"])
    except Exception:
        return None


def elapsed(pid: int) -> str:
    try:
        secs = int(subprocess.run(["ps", "-o", "etimes=", "-p", str(pid)],
                                  capture_output=True, text=True).stdout.strip())
    except ValueError:
        return "?"
    h, rem = divmod(secs, 3600)
    return f"{h}h{rem // 60:02d}m" if h else f"{rem // 60}m{rem % 60:02d}s"


def eta(done: int, total: int, secs: float) -> str:
    if done <= 0 or secs <= 0 or done >= total:
        return ""
    left = (total - done) / (done / secs)
    h, rem = divmod(int(left), 3600)
    return f"  eta {h}h{rem // 60:02d}m" if h else f"  eta {rem // 60}m{rem % 60:02d}s"


def show_strip(pid: int, args: str) -> None:
    m = re.search(r"(/home/skimlab/radix/data/\S+)", args)
    if not m:
        return
    base = os.path.basename(m.group(1))
    hdr = header(f"{RAW}/{base}.xdat.json")
    keep = len(re.search(r"--keep-labels\s+(\S+)", args).group(1).split(",")) if "--keep-labels" in args else 0
    if "--with-gpio" in args:
        keep += 6
    part = f"{STRIPPED}/{base}_data.xdat.part"
    have = os.path.getsize(part) if os.path.exists(part) else 0
    done_file = f"{STRIPPED}/{base}_data.xdat"
    secs = int(subprocess.run(["ps", "-o", "etimes=", "-p", str(pid)],
                              capture_output=True, text=True).stdout.strip() or 0)
    if hdr and keep:
        target = hdr[0] * keep * BYTES_PER_SAMPLE
        if have == 0 and os.path.exists(done_file):
            # Write pass finished, .part renamed: the job is in the verify re-read.
            print(f"  {C['b']}strip{C['0']}  {base}  {keep} ch")
            print(f"         {bar(1.0)}  written, {C['y']}verifying bit-exactness{C['0']}  [{elapsed(pid)}]")
            return
        # The .part stays at full size THROUGH the verify re-read; it is renamed
        # only at the very end. So a bare 100% bar means "verifying", not "done".
        tail = (f"  {C['y']}verifying bit-exactness{C['0']}" if have >= target
                else f"{eta(have, target, secs)}")
        print(f"  {C['b']}strip{C['0']}  {base}  {keep} ch")
        print(f"         {bar(have / target)}  {gb(have)} / {gb(target)}  [{elapsed(pid)}]{tail}")
    else:
        print(f"  {C['b']}strip{C['0']}  {base}  [{elapsed(pid)}]")


def show_upload(pid: int, args: str) -> None:
    m = re.search(r"(/home/skimlab/radix/stripped/\S+)", args)
    base = os.path.basename(m.group(1)) if m else "?"
    parts = glob.glob(f"{NAS}/*/*/*.part")
    if not parts:
        print(f"  {C['b']}upload{C['0']} {base}  [{elapsed(pid)}]  verifying or finishing")
        return
    secs = int(subprocess.run(["ps", "-o", "etimes=", "-p", str(pid)],
                              capture_output=True, text=True).stdout.strip() or 0)
    for p in sorted(parts):
        have = os.path.getsize(p)
        # The target is the local file this .part is a copy of.
        stem = os.path.basename(p)[:-len(".part")]
        kind = "_timestamp.xdat" if stem.endswith("_timestamp.xdat") else "_data.xdat"
        src = f"{STRIPPED}/{base}{kind}"
        target = os.path.getsize(src) if os.path.exists(src) else 0
        name = os.path.basename(os.path.dirname(p)) + "/" + stem.split("_")[-1]
        if target:
            print(f"  {C['b']}upload{C['0']} {name}")
            print(f"         {bar(have / target)}  {gb(have)} / {gb(target)}  [{elapsed(pid)}]{eta(have, target, secs)}")
        else:
            print(f"  {C['b']}upload{C['0']} {name}  {gb(have)}  [{elapsed(pid)}]")


def show_nas_parts(seen: set) -> bool:
    """Any NAS .part is an upload in flight, whoever is writing it.

    The uploader is a LIBRARY as well as a command: sd-pipeline calls
    upload_recording() in-process, so there is no nas_upload.py process to find
    and a process-only view reports "nothing running" while gigabytes move. The
    bytes on the share are the honest signal.
    """
    shown = False
    for part in sorted(glob.glob(f"{NAS}/*/*/*.part")):
        if part in seen:
            continue
        have = os.path.getsize(part)
        stem = os.path.basename(part)[:-len(".part")]
        folder = os.path.basename(os.path.dirname(part))
        kind = "_timestamp.xdat" if stem.endswith("_timestamp.xdat") else "_data.xdat"
        # Target: the local stripped file this is a copy of. The remote name is
        # the batch-style rename, so match on the kind and the folder's own
        # UPLOAD/allego base rather than on the filename.
        target = 0
        for cand in glob.glob(f"{STRIPPED}/*{kind}"):
            if os.path.getsize(cand) >= have:
                target = max(target, 0) or os.path.getsize(cand)
                if abs(os.path.getsize(cand) - have) < have * 0.5:
                    target = os.path.getsize(cand)
                    break
        print(f"  {C['b']}upload{C['0']} {folder}  {stem.split('_')[-1]}")
        if target:
            print(f"         {bar(have / target)}  {gb(have)} / {gb(target)}"
                  f"{'  ' + C['y'] + 'verifying read-back' + C['0'] if have >= target else ''}")
        else:
            print(f"         {gb(have)} written")
        shown = True
    return shown


def show_ladder(pid: int, args: str) -> None:
    m = re.search(r"(/home/skimlab/radix/data/\S+)", args)
    base = os.path.basename(m.group(1)) if m else "?"
    coh = re.search(r"--cohort\s+(\S+)", args)
    print(f"  {C['b']}QC{C['0']}     {base}  cohort {coh.group(1) if coh else '?'}  "
          f"[{elapsed(pid)}]  reading the raw file")


def show_s3(pid: int, args: str) -> None:
    m = re.search(r"cp (\S+) s3://", args)
    if m:
        src = m.group(1)
        size = os.path.getsize(src) if os.path.exists(src) else 0
        print(f"  {C['b']}S3{C['0']}     {os.path.basename(src)}  {gb(size)} uploading  [{elapsed(pid)}]")
    else:
        print(f"  {C['b']}S3{C['0']}     archive sweep running  [{elapsed(pid)}]")


def recording() -> None:
    """A live recording is the one job with no .part and no process of its own."""
    newest, newest_t = None, 0.0
    for f in glob.glob(f"{RAW}/*_data.xdat"):
        t = os.path.getmtime(f)
        if t > newest_t:
            newest, newest_t = f, t
    if not newest:
        return
    age = time.time() - newest_t
    if age < 120:
        size = os.path.getsize(newest)
        print(f"  {C['b']}{C['r']}RECORDING{C['0']}  {os.path.basename(newest)[:-len('_data.xdat')]}  "
              f"{gb(size)}, growing  {C['r']}(do not start heavy disk work){C['0']}")


def queued() -> None:
    """Scripted queues that are waiting, not running: worth seeing."""
    out = subprocess.run(["ps", "-eo", "args="], capture_output=True, text=True).stdout
    # Match any scripted queue by shape rather than by a hard-coded list, or the
    # monitor silently stops mentioning jobs somebody added after it was written.
    seen = set()
    for line in out.splitlines():
        if "-c " in line or "rig_jobs" in line:
            continue
        m = re.search(r"/([\w.-]+(?:-pipeline\.py|-16ch\.sh|-qc\.sh))\b", line)
        if m and m.group(1) not in seen:
            seen.add(m.group(1))
            print(f"  {C['d']}queue{C['0']}  {m.group(1)}")


def once() -> None:
    print(f"\n{C['b']}rig jobs{C['0']}  {time.strftime('%F %T')}")
    recording()
    rows = procs()
    for pid, args in rows:
        if "convert.strip_channels" in args:
            show_strip(pid, args)
        elif "nas_upload.py" in args:
            show_upload(pid, args)
        elif "cards/ladder.py" in args:
            show_ladder(pid, args)
        elif "aws s3 cp" in args or "radix-s3-archive.sh" in args:
            show_s3(pid, args)
    uploading = show_nas_parts(set())
    queued()
    if not rows and not uploading:
        print(f"  {C['d']}nothing running{C['0']}")
    for f in sorted(glob.glob(f"{LOGS}/radix-s3-archive-*.state")):
        job = os.path.basename(f).split("-")[-1].removesuffix(".state")
        print(f"  {C['d']}S3 {job:9s} {open(f).read().strip()}{C['0']}")
    print()


def main() -> int:
    watch = "-w" in sys.argv or "--watch" in sys.argv
    every = 5
    for a in sys.argv[1:]:
        if a.isdigit():
            every = int(a)
    if not watch:
        once()
        return 0
    try:
        while True:
            sys.stdout.write("\033[H\033[J")
            once()
            time.sleep(every)
    except KeyboardInterrupt:
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
