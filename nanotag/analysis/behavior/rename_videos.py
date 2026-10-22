#!/usr/bin/env python3
"""Rename the HLBNSL behaviour videos from phone timestamps to mouse IDs.

    rename_videos.py <behavioral_videos_dir> [--apply]

The mice were run in ascending ID order within each session (user, 2026-10-20),
so the Nth video by timestamp in a folder is the Nth surviving mouse. Mouse 43
died 2026-09-28 and was never tested, so there are 9 mice, not 10.

Default is a dry run. --apply renames and writes rename_log.csv next to the
videos, which is enough to undo it.
"""
import argparse, csv, os, re, sys

# NS-SL = SOD1 in drinking water, NW-SL = UV water. 43 died before testing.
SOD1 = [41, 42, 44, 49]
WATER = [45, 46, 47, 48, 50]
ORDER = sorted(SOD1 + WATER)

def mouse_name(m):
    return f"HLBNSSL{m}" if m in SOD1 else f"HLBNWSL{m}"

# subfolder -> short test tag used in the new filename
TESTS = {
    "Y_maze":                        "Ymaze",
    "NOR/NOR_day1_OFT":              "OFT",
    "NOR/NOR_day2/NOR_day2_part1":   "NOR-T1",
    "NOR/NOR_day2/NOR_day2_part2":   "NOR-T2",
}

STAMP = re.compile(r"^(\d{8})_(\d{6})\.mp4$", re.I)


def plan(root):
    rows = []
    for sub, tag in TESTS.items():
        d = os.path.join(root, sub)
        if not os.path.isdir(d):
            sys.exit(f"missing folder: {d}")
        files = sorted(f for f in os.listdir(d) if STAMP.match(f))
        if len(files) != len(ORDER):
            sys.exit(f"{sub}: {len(files)} videos but {len(ORDER)} mice expected — "
                     "the order rule does not hold, stopping")
        for mouse, f in zip(ORDER, files):
            date, time = STAMP.match(f).groups()
            rows.append({"folder": sub, "test": tag, "mouse": mouse,
                         "group": "SOD1" if mouse in SOD1 else "water",
                         "old": f,
                         "new": f"{mouse_name(mouse)}_{tag}_{date}_{time}.mp4"})
    return rows


def main():
    p = argparse.ArgumentParser()
    p.add_argument("root")
    p.add_argument("--apply", action="store_true")
    a = p.parse_args()

    rows = plan(a.root)
    for sub in TESTS:
        print(f"\n### {sub}")
        for r in (r for r in rows if r["folder"] == sub):
            print(f"  {r['old']}  ->  {r['new']}")

    if not a.apply:
        print(f"\ndry run: {len(rows)} files. re-run with --apply to rename.")
        return

    # refuse to clobber, and refuse to run twice
    for r in rows:
        dst = os.path.join(a.root, r["folder"], r["new"])
        if os.path.exists(dst):
            sys.exit(f"target already exists, stopping: {dst}")
    for r in rows:
        os.rename(os.path.join(a.root, r["folder"], r["old"]),
                  os.path.join(a.root, r["folder"], r["new"]))
    log = os.path.join(a.root, "rename_log.csv")
    with open(log, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    print(f"\nrenamed {len(rows)} files. log -> {log}")


if __name__ == "__main__":
    main()
