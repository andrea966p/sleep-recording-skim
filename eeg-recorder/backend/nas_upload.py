#!/usr/bin/env python3
"""nas_upload.py -- copy per-mouse CSVs to the SKIM Lab NAS, verifiably.

DESTINATION
    //skim-nas.tailec38b9.ts.net/SKIM_DATA  mounted at /mnt/skimnas
    files land in 02_Data_Sleep/<user>/<batch>/<Baseline|Recovery>/<YYYYMMDD>_<MOUSEID>_<B|R>/
    (naming.py owns that rule). Until 2026-09-29 it was one folder per RUN in
    03_Data_Mouse/<user>/, holding the stripped xdat.

WHY THIS IS PYTHON AND NOT A GENERALISATION OF radix-archive.sh
    That script moves raw .xdat to a DIFFERENT NAS (bilab-syn) over an ssh pipe,
    because Synology's rsync and OpenSSH-9's scp both misbehave there and because
    ssh gives no seekable remote file. None of that applies here: skim-nas is
    mounted, so the destination is an ordinary filesystem, resume is an offset
    rather than a `dd skip= | ssh "cat >>"` pipeline, and the receiving-side hash
    is a read() rather than a remote command. radix-archive.sh is left alone.

THE ONE THING THAT MAKES VERIFICATION REAL
    Reading a file back over CIFS normally comes out of the local page cache. On
    2026-09-11 a just-written 200 MB file read back at 1538 MB/s -- i.e. the
    "verification" was hashing our own memory and could not have failed. The same
    read after posix_fadvise(POSIX_FADV_DONTNEED) ran at 89.8 MB/s, the real
    network rate, and matched. So `_sha256_uncached` drops the cache first, and
    any verification that skips that step is worthless. At 90 MB/s a 6 GB
    stripped run costs about a minute to verify, which is cheap enough that there
    is no excuse for the fast, meaningless version.

THE MOUNT GUARD, WHICH IS NOT OPTIONAL
    A failed CIFS mount leaves /mnt/skimnas as an ordinary empty directory on the
    recording machine's own NVMe -- the same filesystem the amplifiers write to.
    An uploader that could not tell the difference would quietly fill it and take
    the rig down. `mountpoint` alone does NOT catch this, because an empty local
    directory IS a valid mountpoint. So every write is gated on reading a sentinel
    file that exists only on the share.

THIS MODULE NEVER DELETES ANYTHING LOCALLY. The per-mouse CSVs it uploads are
removed by postprocess.py, and only after every one of a run's CSVs verified --
they are regenerable from the stripped file, which stays.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import socket
import sys
import time
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable, Iterable, Sequence

MOUNT = Path(os.environ.get("SKIMNAS_MOUNT", "/mnt/skimnas"))
ROOT = os.environ.get("SKIMNAS_ROOT", "02_Data_Sleep")
SENTINEL = MOUNT / ROOT / ".skim-nas-share"


def set_root(root: str) -> None:
    """Take the root from config/users.yaml (`nas.root`), unless SKIMNAS_ROOT is set.

    The config value was loaded but ignored until 2026-09-29, so the destination
    was really decided by this module's default -- two places that could disagree.
    """
    global ROOT, SENTINEL
    if os.environ.get("SKIMNAS_ROOT"):
        return
    ROOT = str(root)
    SENTINEL = MOUNT / ROOT / ".skim-nas-share"
USERS = ("andrea", "diane", "ahyeon", "hyunmin", "staci")

CHUNK = 8 << 20
TOOL = "eeg-recorder.nas_upload"
TOOL_VERSION = "2026.09.29"


class UploadRefused(RuntimeError):
    """A precondition said no. Nothing was written to the NAS."""


class UploadFailed(RuntimeError):
    """Bytes were written but did not verify. The .part file is left in place."""


# --------------------------------------------------------------------------- #
# guards
# --------------------------------------------------------------------------- #

def local_date_from_base(base_name: str, fallback_iso: str | None = None) -> str:
    """The recording's date IN LOCAL TIME, from the uid Allego put in its name.

    WHY NOT `status.start_time` OR `actual_start`. Both are UTC. This rig runs on
    KST (UTC+9) and its recordings start at 09:00 local, which is 00:00 UTC the
    SAME day only by luck -- a 08:55 KST start is 23:55 UTC on the PREVIOUS day.
    Dating from UTC therefore labels a 2026-09-12 recording as 2026-09-11, which
    is what happened to the first real 24 h run: its NAS folder read
    `2026-09-11_allego_0__uid0912-08-55-18`, contradicting the uid in its own
    filename.

    The uid token IS already local (production-values records this), so it is the
    honest source. `allego_0__uid0912-08-55-18` -> month 09, day 12. The year is
    not in the uid, so it comes from the fallback timestamp, corrected when the
    UTC date has rolled either way across the boundary.
    """
    import re
    from datetime import datetime, timedelta, timezone
    m = re.search(r"uid(\d{2})(\d{2})-(\d{2})-(\d{2})-(\d{2})", base_name or "")
    fb = None
    if fallback_iso:
        try:
            fb = datetime.fromisoformat(str(fallback_iso).replace("Z", "+00:00"))
        except ValueError:
            fb = None
    if not m:
        return (fb.astimezone().strftime("%Y-%m-%d") if fb
                else datetime.now().astimezone().strftime("%Y-%m-%d"))
    month, day = int(m.group(1)), int(m.group(2))
    ref = (fb.astimezone() if fb else datetime.now().astimezone())
    for cand in (ref.year, ref.year - 1, ref.year + 1):
        try:
            d = datetime(cand, month, day)
        except ValueError:
            continue
        if abs((d.date() - ref.date()).days) <= 2:
            return d.strftime("%Y-%m-%d")
    return f"{ref.year:04d}-{month:02d}-{day:02d}"


def nas_status() -> dict:
    """Everything the UI needs to show a NAS pill, and the guard needs to decide."""
    mounted = os.path.ismount(MOUNT)
    sentinel = SENTINEL.is_file() and os.access(SENTINEL, os.R_OK)
    out = {"mount": str(MOUNT), "mounted": mounted, "sentinel_ok": sentinel,
           "ok": bool(mounted and sentinel), "root": ROOT}
    if mounted:
        try:
            st = os.statvfs(MOUNT)
            out["total_bytes"] = st.f_blocks * st.f_frsize
            out["free_bytes"] = st.f_bavail * st.f_frsize
        except OSError as exc:
            out["error"] = str(exc)
    if not mounted:
        out["hint"] = ("sudo systemctl start mnt-skimnas.mount, or just touch the "
                       "path -- mnt-skimnas.automount mounts it on access")
    elif not sentinel:
        out["hint"] = (f"{SENTINEL} is missing. Either the share is not really "
                       "mounted, or the sentinel was deleted. REFUSING to write: "
                       "an unmounted /mnt/skimnas is a directory on the rig's own "
                       "NVMe and filling it would take the rig down.")
    return out


def require_nas() -> dict:
    st = nas_status()
    if not st["ok"]:
        raise UploadRefused(st.get("hint", "the NAS is not usable"))
    return st


def user_dir(user: str) -> Path:
    """The owner's folder, validated against the known list.

    Not a cosmetic check: `user` reaches here from a form field, and a value like
    `../../11_Protocols` would otherwise write outside the EEG tree.
    """
    u = str(user).strip().lower()
    if u not in USERS:
        raise UploadRefused(
            f"unknown user {user!r}; known users are {', '.join(USERS)}. "
            "Add the person to config/users.yaml AND create their folder on the "
            "NAS before recording for them.")
    return MOUNT / ROOT / u


# --------------------------------------------------------------------------- #
# hashing
# --------------------------------------------------------------------------- #

def _sha256_local(path: Path, progress=None) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for blk in iter(lambda: fh.read(CHUNK), b""):
            h.update(blk)
    return h.hexdigest()


def sha256_uncached(path: Path) -> tuple[str, float]:
    """Hash a file on the SHARE, defeating the local page cache.

    Returns (hexdigest, MB/s). The rate is reported because it is the evidence
    that the read really crossed the network: a figure in the hundreds or
    thousands of MB/s means the cache was not dropped and the result proves
    nothing about what the NAS actually holds.
    """
    fd = os.open(path, os.O_RDONLY)
    try:
        try:
            os.posix_fadvise(fd, 0, 0, os.POSIX_FADV_DONTNEED)
        except (AttributeError, OSError):
            # Not fatal, but the caller must know the read may be cached.
            pass
        h = hashlib.sha256()
        t0 = time.time()
        total = 0
        while True:
            b = os.read(fd, CHUNK)
            if not b:
                break
            h.update(b)
            total += len(b)
        dt = max(time.time() - t0, 1e-9)
        return h.hexdigest(), (total / 1e6) / dt
    finally:
        os.close(fd)


# --------------------------------------------------------------------------- #
# the manifest
# --------------------------------------------------------------------------- #
# One JSON-lines file per destination, next to the code, recording what has been
# verified. Keyed on (relative path, size) like radix-archive.sh's TSV: a file
# whose local size changed is re-verified rather than assumed done.
#
# STATUS VOCABULARY CARRIES THE HONESTY.
#   VERIFIED        bytes were read back FROM THE SHARE with the cache dropped
#                   and the sha256 matched.
#   SIZE_ONLY       the sizes agree and nothing else was checked. NOT verified.
#                   Never counted as done; reported separately.
#   FAILED          a hash mismatch. The .part is left for inspection.
# A size check is not a verification and the manifest must not let anyone believe
# it was.

# Overridable at RUN TIME, not just import time. `path: Path = MANIFEST` as a
# default argument binds the value when the module is imported, so setting
# `nas_upload.MANIFEST` afterwards silently had no effect -- which let a test run
# write eight rows claiming files were VERIFIED on the real NAS when nothing had
# been uploaded. A stale VERIFIED row is not cosmetic: the uploader SKIPS files it
# finds there, so a later real run of the same name would have shipped nothing and
# reported success.
MANIFEST = Path(os.environ.get(
    "EEG_UPLOAD_MANIFEST",
    Path(__file__).resolve().parent.parent / "deploy" / "uploads.jsonl"))


def manifest_load(path: Path | None = None) -> dict:
    path = Path(path) if path else MANIFEST
    out: dict = {}
    if not path.exists():
        return out
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            rec = json.loads(line)
        except json.JSONDecodeError:
            continue
        out[(rec.get("rel"), rec.get("size"))] = rec
    return out


def manifest_put(rec: dict, path: Path | None = None) -> None:
    path = Path(path) if path else MANIFEST
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "a") as fh:
        fh.write(json.dumps(rec) + "\n")
        fh.flush()
        os.fsync(fh.fileno())


# --------------------------------------------------------------------------- #
# uploading one file
# --------------------------------------------------------------------------- #

def upload_file(src: Path, dst: Path, *, resume: bool = True,
                verify: bool = True, min_free_bytes: int = 10 << 30,
                progress: Callable[[str], None] | None = None) -> dict:
    """Copy one file to the share and verify it by cache-dropped read-back.

    Writes to `<dst>.part` and renames only after the hash matches, so a partial
    or corrupt transfer can never be mistaken for a finished one.
    """
    say = progress or (lambda _m: None)
    require_nas()
    src = Path(src)
    dst = Path(dst)
    size = src.stat().st_size
    local_sha = _sha256_local(src)

    st = os.statvfs(MOUNT)
    free = st.f_bavail * st.f_frsize
    if free - size < min_free_bytes:
        raise UploadRefused(
            f"the share has {free / 1e9:.1f} GB free and this file needs "
            f"{size / 1e9:.1f} GB, which would leave under the "
            f"{min_free_bytes / 1e9:.0f} GB reserve")

    dst.parent.mkdir(parents=True, exist_ok=True)
    part = dst.with_suffix(dst.suffix + ".part")

    # already there and verified?
    if dst.exists() and dst.stat().st_size == size:
        if not verify:
            return {"status": "SIZE_ONLY", "rel": dst.name, "size": size,
                    "note": "existed at the right size; not verified"}
        remote_sha, rate = sha256_uncached(dst)
        if remote_sha == local_sha:
            say(f"  already uploaded and verified: {dst.name}")
            return {"status": "VERIFIED", "rel": dst.name, "size": size,
                    "sha256": local_sha, "read_back_mb_s": round(rate, 1),
                    "note": "already present"}
        say(f"  {dst.name} exists but does not match; re-uploading")

    start = 0
    if resume and part.exists():
        have = part.stat().st_size
        if have <= size:
            start = have
            say(f"  resuming {dst.name} at {start / 1e6:.1f} MB of {size / 1e6:.1f} MB")
        else:
            part.unlink()

    t0 = time.time()
    with open(src, "rb") as fin, open(part, "r+b" if start else "wb") as fout:
        if start:
            fin.seek(start)
            fout.seek(start)
        while True:
            b = fin.read(CHUNK)
            if not b:
                break
            fout.write(b)
        fout.flush()
        os.fsync(fout.fileno())
    dt = max(time.time() - t0, 1e-9)
    wrote = size - start
    say(f"  wrote {wrote / 1e6:.1f} MB in {dt:.1f} s ({wrote / 1e6 / dt:.1f} MB/s)")

    if part.stat().st_size != size:
        raise UploadFailed(f"{dst.name}: wrote {part.stat().st_size} bytes, want {size}")

    if not verify:
        os.replace(part, dst)
        return {"status": "SIZE_ONLY", "rel": dst.name, "size": size,
                "sha256": local_sha, "note": "verification was disabled"}

    remote_sha, rate = sha256_uncached(part)
    if remote_sha != local_sha:
        raise UploadFailed(
            f"{dst.name}: sha256 mismatch after upload.\n"
            f"  local : {local_sha}\n  remote: {remote_sha}\n"
            f"The .part file is left in place for inspection.")
    if rate > 400:
        # Not a failure, but it means the fadvise did not take and the read may
        # have come from cache -- the reader deserves to know the check was weak.
        say(f"  WARNING: read-back ran at {rate:.0f} MB/s, far above the ~90 MB/s "
            "network rate. The page cache may not have been dropped, which would "
            "make this verification weak.")
    os.replace(part, dst)
    say(f"  VERIFIED {dst.name} ({rate:.1f} MB/s read-back)")
    return {"status": "VERIFIED", "rel": dst.name, "size": size,
            "sha256": local_sha, "read_back_mb_s": round(rate, 1),
            "write_mb_s": round(wrote / 1e6 / dt, 1)}


# --------------------------------------------------------------------------- #
# per-mouse destinations
# --------------------------------------------------------------------------- #

import re as _re
_SAFE = _re.compile(r"^[A-Za-z0-9_-]{1,40}$")


def mouse_dir(user: str, entry: dict) -> Path:
    """`<root>/<user>/<batch>/<condition>/<folder>`, every component checked.

    The components come from a form field (batch), config (condition) and a mouse
    id, each validated where it was entered; checking them again here costs
    nothing and means no future caller can walk this out of the user's tree.
    """
    parts = [entry.get("batch"), entry.get("condition_dir"), entry.get("folder")]
    for x in parts:
        if not x or not _SAFE.match(str(x)):
            raise UploadRefused(f"unsafe path component {x!r} in {entry}")
    return user_dir(user).joinpath(*parts)


def free_mouse_folder(user: str, entry: dict, *, limit: int = 9) -> dict:
    """`entry`, or its `-2`, `-3`... variant, whichever folder does not exist yet.

    Called ONCE per run; the answer is frozen on the run (results.nas_mouse_dirs)
    so a resumed upload lands in the folder it started in. A second folder for the
    same mouse on the same day is a real event -- a restarted recording -- and its
    info.json says which Allego file each one holds.
    """
    require_nas()
    stem = entry["folder"]
    for n in range(1, limit + 1):
        cand = dict(entry)
        if n > 1:
            cand["folder"] = cand["file_base"] = f"{stem}-{n}"
            cand["rel"] = f"{entry['batch']}/{entry['condition_dir']}/{cand['folder']}"
            cand["suffix_reason"] = (f"{stem} already existed on the NAS when this "
                                     "run was uploaded, holding a different recording")
        if not mouse_dir(user, cand).exists():
            return cand
    raise UploadRefused(f"{limit} folders already exist for {stem!r}; refusing to add "
                        "another. Something is wrong with the mouse id or the date.")


def _upload_checked(src: Path, dst: Path, rel: str, user: str, *,
                    resume: bool, verify: bool, say) -> dict:
    """upload_file, but a manifest row is only believed if the share agrees."""
    size = src.stat().st_size
    prior = manifest_load().get((rel, size))
    if prior and prior.get("status") == "VERIFIED":
        # 🔴 THE MANIFEST IS A CLAIM ABOUT THE NAS, SO CHECK THE NAS. On
        # 2026-09-15 four folders were tidied off the share and the manifest still
        # swore all of it was verified; trusting it would ship nothing and report
        # success. One stat per file.
        try:
            there = dst.exists() and dst.stat().st_size == size
        except OSError:
            there = False
        if there:
            say(f"  skip (already VERIFIED in the manifest): {dst.name}")
            return prior
        say(f"  manifest says {dst.name} is VERIFIED but it is NOT on the share "
            "-- uploading it again")
    rec = upload_file(src, dst, resume=resume, verify=verify, progress=say)
    rec.update(rel=rel, user=user, local_name=src.name,
               utc=datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
               host=socket.gethostname(), tool=TOOL, version=TOOL_VERSION)
    manifest_put(rec)
    return rec


def upload_mouse(csv_path: str | Path, user: str, entry: dict, info: dict, *,
                 expect_sha256: str | None = None, resume: bool = True,
                 verify: bool = True, progress=print) -> dict:
    """Upload one mouse's CSV, then its info.json. Returns the info as written.

    info.json is written LAST and only once the CSV has verified, so its presence
    in a folder means the folder is complete. It is written to a temporary name
    and renamed, so a reader never sees half of one.
    """
    say = progress or (lambda _m: None)
    require_nas()
    src = Path(csv_path)
    dest = mouse_dir(user, entry)
    fb = entry["file_base"]
    csv_dst = dest / f"{fb}.csv"
    say(f"{entry['rel']}")
    rec = _upload_checked(src, csv_dst, f"{entry['rel']}/{fb}.csv", user,
                          resume=resume, verify=verify, say=say)
    if expect_sha256 and rec.get("sha256") != expect_sha256:
        raise UploadFailed(
            f"{csv_dst.name}: the exporter hashed {expect_sha256} while writing it, "
            f"but the file now hashes {rec.get('sha256')}. It changed on disk "
            "between export and upload.")
    out = dict(info)
    out["upload"] = {
        "status": rec.get("status"), "dest": str(dest), "user": user,
        "csv": csv_dst.name, "bytes": rec.get("size"), "sha256_local": rec.get("sha256"),
        "sha256_remote": rec.get("sha256") if rec.get("status") == "VERIFIED" else None,
        "read_back_mb_s": rec.get("read_back_mb_s"),
        "utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "tool": TOOL, "version": TOOL_VERSION}
    if rec.get("status") == "VERIFIED":
        tmp = dest / f".{fb}.info.json.tmp"
        tmp.write_text(json.dumps(out, indent=2))
        os.replace(tmp, dest / f"{fb}.info.json")
    return out


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="nas_upload",
                                 description="SKIM Lab NAS status. Uploads are driven "
                                             "by the recorder's post-processing worker.")
    ap.add_argument("--status", action="store_true", help="print NAS status and exit")
    ap.parse_args(argv)
    print(json.dumps(nas_status(), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
