#!/usr/bin/env python3
"""Phase 0/1 of the behaviour pipeline: inventory phone videos, then transcode
them to constant-frame-rate H.264 under blinded filenames.

    behavior/prep.py inventory  <video_dir> [-o inventory.csv]
    behavior/prep.py convert    <video_dir> <out_dir>
    behavior/prep.py verify     <video_dir> <out_dir>
    behavior/prep.py selftest

Why this exists: the Y-maze/NOR videos were filmed on a phone. Noldus guarantees
import only for files their own encoders wrote, and phones record VARIABLE frame
rate, which silently corrupts every time-based measure if EthoVision assumes a
constant time base. `convert` forces CFR 30 fps, bakes in the rotation metadata
(EthoVision ignores it and shows the video sideways) and downscales to 1080p.

`convert` also blinds: each output gets a random code, and code -> original is
written to blind_key.csv in the PARENT of out_dir, so the key does not sit in the
directory the scorer opens. Fill in the mouse/group/test columns by hand.
"""
import argparse, csv, json, os, random, string, subprocess, sys

TARGET_FPS = 30
TARGET_HEIGHT = 1080
DUR_TOL_S = 0.1          # a converted file that drifts more than this dropped frames
KEY_NAME = "blind_key.csv"
VIDEO_EXT = {".mp4", ".mov", ".avi", ".mkv", ".m4v", ".3gp"}


# --- pure helpers (covered by selftest) ------------------------------------

def parse_fps(frac):
    """'30000/1001' -> 29.97. Returns None for ffprobe's '0/0'."""
    if not frac or "/" not in frac:
        return None
    num, den = frac.split("/")
    num, den = float(num), float(den)
    return None if den == 0 else num / den


def is_vfr(r_frame_rate, avg_frame_rate, tol=0.01):
    """ffprobe reports the container rate and the measured average rate. They
    disagree on variable-frame-rate recordings, which is what phones produce."""
    r, a = parse_fps(r_frame_rate), parse_fps(avg_frame_rate)
    if r is None or a is None:
        return True                      # unknown rate is no safer than VFR
    return abs(r - a) > tol * max(r, a)


def duration_ok(before, after, tol=DUR_TOL_S):
    if before is None or after is None:
        return False
    return abs(before - after) <= tol


def code_for(name, rng):
    """Stable-length random code. Keeps the extension so players behave."""
    stem = "".join(rng.choice(string.ascii_uppercase + string.digits) for _ in range(6))
    return stem + os.path.splitext(name)[1].lower()


# --- ffprobe ---------------------------------------------------------------

def probe(path):
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-print_format", "json",
         "-show_streams", "-show_format", path],
        capture_output=True, text=True, check=True).stdout
    meta = json.loads(out)
    v = next((s for s in meta["streams"] if s.get("codec_type") == "video"), {})
    rotation = 0
    for sd in v.get("side_data_list", []) or []:
        if "rotation" in sd:
            rotation = sd["rotation"]
    # older ffprobe puts it in the stream tags instead
    rotation = rotation or int(v.get("tags", {}).get("rotate", 0) or 0)
    dur = v.get("duration") or meta.get("format", {}).get("duration")
    return {
        "file": os.path.basename(path),
        "duration_s": round(float(dur), 3) if dur else None,
        "width": v.get("width"), "height": v.get("height"),
        "codec": v.get("codec_name"),
        "r_frame_rate": v.get("r_frame_rate"),
        "avg_frame_rate": v.get("avg_frame_rate"),
        "vfr": is_vfr(v.get("r_frame_rate"), v.get("avg_frame_rate")),
        "rotation": rotation,
        "bitrate_kbps": round(int(meta.get("format", {}).get("bit_rate", 0)) / 1000)
                        if meta.get("format", {}).get("bit_rate") else None,
        "size_mb": round(os.path.getsize(path) / 1e6, 1),
    }


def videos_in(d):
    return sorted(os.path.join(d, f) for f in os.listdir(d)
                  if os.path.splitext(f)[1].lower() in VIDEO_EXT)


# --- commands --------------------------------------------------------------

FIELDS = ["file", "duration_s", "width", "height", "codec", "r_frame_rate",
          "avg_frame_rate", "vfr", "rotation", "bitrate_kbps", "size_mb"]


def cmd_inventory(args):
    files = videos_in(args.video_dir)
    if not files:
        sys.exit(f"no video files in {args.video_dir}")
    rows = [probe(p) for p in files]
    w = csv.DictWriter(open(args.out, "w", newline="") if args.out else sys.stdout,
                       fieldnames=FIELDS)
    w.writeheader()
    w.writerows(rows)
    vfr = sum(r["vfr"] for r in rows)
    rot = sum(1 for r in rows if r["rotation"])
    total = sum(r["duration_s"] or 0 for r in rows)
    print(f"\n{len(rows)} videos, {total/60:.1f} min total, "
          f"{vfr} variable-frame-rate, {rot} with rotation metadata",
          file=sys.stderr)


def cmd_convert(args):
    files = videos_in(args.video_dir)
    if not files:
        sys.exit(f"no video files in {args.video_dir}")
    os.makedirs(args.out_dir, exist_ok=True)
    key_path = os.path.join(os.path.dirname(os.path.abspath(args.out_dir)), KEY_NAME)
    if os.path.exists(key_path) and not args.force:
        sys.exit(f"{key_path} exists; refusing to re-blind (use --force)")

    rng = random.Random(args.seed)
    used, rows = set(), []
    for src in files:
        while True:
            code = code_for(src, rng)
            if code not in used:
                used.add(code)
                break
        dst = os.path.join(args.out_dir, code)
        # -vf fps= forces CFR; scale only downwards; autorotate is ffmpeg's default
        # so the rotation ends up baked into the pixels.
        vf = f"scale=-2:'min({TARGET_HEIGHT},ih)',fps={TARGET_FPS}"
        subprocess.run(
            ["ffmpeg", "-nostdin", "-y", "-i", src, "-vf", vf,
             "-c:v", "libx264", "-preset", args.preset, "-crf", str(args.crf),
             "-pix_fmt", "yuv420p", "-an", "-movflags", "+faststart", dst],
            check=True, capture_output=True)
        before, after = probe(src), probe(dst)
        rows.append({"code": code, "original_file": os.path.basename(src),
                     "mouse": "", "group": "", "test": "", "trial": "",
                     "duration_before_s": before["duration_s"],
                     "duration_after_s": after["duration_s"],
                     "duration_ok": duration_ok(before["duration_s"], after["duration_s"])})
        flag = "" if rows[-1]["duration_ok"] else "  <-- DURATION DRIFT"
        print(f"{os.path.basename(src)} -> {code}  "
              f"{before['duration_s']}s -> {after['duration_s']}s{flag}", file=sys.stderr)

    with open(key_path, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    bad = [r["code"] for r in rows if not r["duration_ok"]]
    print(f"\nkey -> {key_path}  (fill in mouse/group/test/trial by hand)", file=sys.stderr)
    if bad:
        print(f"WARNING {len(bad)} file(s) drifted >{DUR_TOL_S}s: {', '.join(bad)}",
              file=sys.stderr)


def cmd_verify(args):
    key_path = os.path.join(os.path.dirname(os.path.abspath(args.out_dir)), KEY_NAME)
    key = list(csv.DictReader(open(key_path)))
    fails = 0
    for row in key:
        src = os.path.join(args.video_dir, row["original_file"])
        dst = os.path.join(args.out_dir, row["code"])
        a, b = probe(src), probe(dst)
        problems = []
        if is_vfr(b["r_frame_rate"], b["avg_frame_rate"]):
            problems.append(f"still VFR ({b['r_frame_rate']} vs {b['avg_frame_rate']})")
        if abs((parse_fps(b["r_frame_rate"]) or 0) - TARGET_FPS) > 0.01:
            problems.append(f"fps {b['r_frame_rate']} != {TARGET_FPS}")
        if not duration_ok(a["duration_s"], b["duration_s"]):
            problems.append(f"duration {a['duration_s']} -> {b['duration_s']}")
        if b["rotation"]:
            problems.append(f"rotation metadata survived ({b['rotation']})")
        if problems:
            fails += 1
            print(f"FAIL {row['code']} ({row['original_file']}): {'; '.join(problems)}")
    print(f"\n{len(key) - fails}/{len(key)} converted files pass")
    sys.exit(1 if fails else 0)


def cmd_selftest(_args):
    assert abs(parse_fps("30000/1001") - 29.970) < 1e-3
    assert parse_fps("30/1") == 30.0
    assert parse_fps("0/0") is None and parse_fps(None) is None and parse_fps("30") is None

    assert not is_vfr("30/1", "30/1")
    assert not is_vfr("30000/1001", "30000/1001")
    assert is_vfr("30/1", "27/1")                 # phone VFR: measured rate lags
    assert is_vfr("30/1", "0/0")                  # unknown is treated as unsafe
    assert not is_vfr("30/1", "2997/100")         # 29.97 vs 30 is within 1%

    assert duration_ok(600.0, 600.05)
    assert not duration_ok(600.0, 600.5)          # half a second = frames lost
    assert not duration_ok(600.0, None)

    rng = random.Random(0)
    codes = {code_for("IMG_0001.MP4", rng) for _ in range(500)}
    assert len(codes) > 490, "codes collide too often"
    assert all(c.endswith(".mp4") and len(c) == 10 for c in codes)
    print("selftest ok")


def main():
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)

    i = sub.add_parser("inventory"); i.add_argument("video_dir")
    i.add_argument("-o", "--out"); i.set_defaults(func=cmd_inventory)

    c = sub.add_parser("convert"); c.add_argument("video_dir"); c.add_argument("out_dir")
    c.add_argument("--crf", type=int, default=18)
    c.add_argument("--preset", default="slow")
    c.add_argument("--seed", type=int, default=None)
    c.add_argument("--force", action="store_true")
    c.set_defaults(func=cmd_convert)

    v = sub.add_parser("verify"); v.add_argument("video_dir"); v.add_argument("out_dir")
    v.set_defaults(func=cmd_verify)

    sub.add_parser("selftest").set_defaults(func=cmd_selftest)
    args = p.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
