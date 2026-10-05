"""Copy a local folder tree to the NAS and PROVE every byte arrived.

A CIFS read-back is vacuous while the page cache still holds the bytes that were just written (2026-09-11), so each
file is read back with posix_fadvise(DONTNEED) on the share before its sha256 is compared with the local file's.
Existing destination files are replaced only if their content differs. Writes go to <name>.part then os.replace, so a
reader never sees a half-written file. A SHA256SUMS listing of the whole tree is written at the destination root.
usage: python3 qc/nas_copy_verified.py SRC_DIR DEST_DIR [--dry-run]
"""
import hashlib, os, shutil, sys


def sha256(path, drop_cache=False):
    h = hashlib.sha256(); fd = os.open(path, os.O_RDONLY)
    try:
        if drop_cache:
            os.posix_fadvise(fd, 0, 0, os.POSIX_FADV_DONTNEED)
        while True:
            b = os.read(fd, 1 << 22)
            if not b:
                break
            h.update(b)
        return h.hexdigest()
    finally:
        os.close(fd)


def main(src, dst, dry):
    files = sorted(os.path.relpath(os.path.join(r, f), src) for r, _, fs in os.walk(src) for f in fs if f != "SHA256SUMS")
    sums, copied, same = [], 0, 0
    for rel in files:
        s, d = os.path.join(src, rel), os.path.join(dst, rel); hs = sha256(s)
        if os.path.exists(d) and sha256(d, drop_cache=True) == hs:
            same += 1; sums.append((hs, rel)); continue
        if dry:
            print(f"would copy {rel}"); sums.append((hs, rel)); continue
        os.makedirs(os.path.dirname(d), exist_ok=True)
        with open(s, "rb") as fi, open(d + ".part", "wb") as fo:
            shutil.copyfileobj(fi, fo, 1 << 22); fo.flush(); os.fsync(fo.fileno())
        os.replace(d + ".part", d)
        hd = sha256(d, drop_cache=True)
        if hd != hs:
            sys.exit(f"VERIFY FAILED {rel}: local {hs} remote {hd}")
        copied += 1; sums.append((hs, rel))
    if not dry:
        with open(os.path.join(dst, "SHA256SUMS.part"), "w") as fh:
            fh.write("".join(f"{h}  {r}\n" for h, r in sums))
        os.replace(os.path.join(dst, "SHA256SUMS.part"), os.path.join(dst, "SHA256SUMS"))
    print(f"{'DRY RUN: ' if dry else ''}{len(files)} files: {copied} copied and verified by read-back (cache dropped), {same} already identical")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], "--dry-run" in sys.argv)
