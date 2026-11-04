#!/usr/bin/env python3
"""Y-maze measures from pose keypoints: distance, speed, immobility, time per arm,
and model-scored arm entries (a check against the hand letters, never the endpoint).

    behav-venv/Scripts/python ymaze_pose.py pick <clip_dir> <arena.csv>
    behav-venv/Scripts/python ymaze_pose.py features <pose_dir> <arena.csv> <out.csv> --model model2

Pose first, unchanged: `pose_infer.py model2 <clip_dir> <pose_dir>` (and model1 for the cross-check).

`pick` shows each clip's median background (no mouse): click the maze CENTRE, then the end of
arm A, B, C in the hand-scoring order (A = toward the ceiling vent, then clockwise). Enter keeps,
r redoes, Esc skips. It writes arena.csv and an overlay PNG per clip: look at every overlay.

The 4 points map the video onto an ideal Y (arms 120 deg apart, ARM_CM from centre to end, the
SOP's calibration value) by a homography, so distances are in floor cm like EthoVision's. Wide-angle
parallax is not removed, so distance and speed stay secondary endpoints (SOP, Y-maze section).

Zones: a point belongs to the arm whose axis it is closest to in angle, and is in that arm once
its projection on the axis passes CENTRE_CM, else in the centre. A model entry needs the body
centre to reach ENTRY_CM along the arm; it ends when the body is back under CENTRE_CM, so a
re-entry into the same arm needs a visit to the centre, like the four-paw rule. ENTRY_CM is a
calibration knob: set it from the HLBNSL hand sequences before reading model entries.
"""
import argparse
import csv
import pathlib
import sys

import numpy as np

import metrics
from oft_features import IMMOBILE_CM_S, IMMOBILE_MIN_S, clean, runs

ARM_CM = 35.0                 # maze centre to arm end, SOP (design value, measure before trusting cm)
CENTRE_CM = 4.0               # projection below this = centre triangle (arm width unknown: ponytail, measure it)
ENTRY_CM = 7.0                # body centre this far along an arm = an entry (calibrate on HLBNSL)
ON_MAZE_CM = ARM_CM + 10.0    # body point further from the centre is not the mouse
ARMS = ("A", "B", "C")
# ideal Y in image-like coordinates (y down): A up, B and C clockwise
ANG = np.deg2rad([-90.0, 30.0, 150.0])
AXES = np.stack([np.cos(ANG), np.sin(ANG)], axis=1)
REAL = np.vstack([[0.0, 0.0], ARM_CM * AXES]).astype(np.float32)


def homography(points_px):
    import cv2
    return cv2.getPerspectiveTransform(np.float32(points_px), REAL)


def to_cm(xy_px, H):
    import cv2
    flat = np.nan_to_num(xy_px.reshape(-1, 1, 2).astype(np.float32), nan=-1e6)
    out = cv2.perspectiveTransform(flat, H).reshape(xy_px.shape)
    out[np.isnan(xy_px)] = np.nan
    return out


def zones(p):
    """(N, 2) cm -> arm index 0..2 per frame (by angle), projection along it, and in_arm mask."""
    proj = p @ AXES.T                               # (N, 3) projection on each arm axis
    arm = np.argmax(np.nan_to_num(proj, nan=-1e9), axis=1)
    along = proj[np.arange(len(p)), arm]
    return arm, along, along >= CENTRE_CM


def model_entries(p):
    """Arm-entry letters from the body track, with the centre as the only way to re-enter."""
    arm, along, _ = zones(p)
    seq, cur = [], None                             # cur = arm we are counted in, None = centre
    for a, d in zip(arm, along):
        if np.isnan(d):
            continue
        if cur is None and d >= ENTRY_CM:
            cur = a
            seq.append(ARMS[a])
        elif cur is not None and (d < CENTRE_CM or a != cur):
            cur = None if d < ENTRY_CM else a
            if cur is not None:
                seq.append(ARMS[a])                 # straight from one arm into another (a jump)
    return seq


def features(npz, H):
    z = np.load(npz)
    fps, names = float(z["fps"]), list(z["kpt_names"])
    bi = names.index("body_center")
    xy = to_cm(z["xy"], H)                          # (N, D, K, 2)
    body_all = xy[:, :, bi]
    on = (z["bconf"] > 0) & (np.linalg.norm(np.nan_to_num(body_all, nan=1e6), axis=2) <= ON_MAZE_CM)
    best = np.argmax(np.where(on, z["bconf"], -1), axis=1)
    rows = np.arange(len(xy))
    track, kc = xy[rows, best, bi].copy(), z["kconf"][rows, best, bi].copy()
    none = ~on.any(axis=1)
    track[none], kc[none] = np.nan, 0
    body, ok = clean(track, kc, fps)
    n, tracked = len(body), ~np.isnan(body[:, 0])

    step = np.linalg.norm(np.diff(body, axis=0), axis=1)
    half = int(fps) // 2                            # speed over a centred 1 s window, as the open field
    speed = np.full(n, np.nan)
    speed[half:n - half] = np.linalg.norm(body[2 * half:] - body[:n - 2 * half], axis=1) * fps / (2 * half)
    immobile = np.zeros(n, bool)
    for a, b in runs(speed < IMMOBILE_CM_S):
        if (b - a) / fps >= IMMOBILE_MIN_S:
            immobile[a:b] = True

    arm, along, in_arm = zones(body)
    seq = model_entries(body)
    f = {
        "frames": n,
        "mouse_on_maze_pct": 100 * np.mean(~none),
        "body_tracked_pct": 100 * tracked.mean(),
        "distance_m": np.nansum(step) / 100,
        "mean_speed_cm_s": np.nansum(step) / (tracked.sum() / fps),
        "immobile_s": immobile.sum() / fps,
        "immobile_bouts": len(runs(immobile)),
        "centre_time_pct": 100 * (tracked & ~in_arm).sum() / tracked.sum(),
        **{f"arm_{c}_time_pct": 100 * (tracked & in_arm & (arm == i)).sum() / tracked.sum() for i, c in enumerate(ARMS)},
        "model_arm_entries": len(seq),
        "model_sa_pct": metrics.spontaneous_alternation(seq) if len(seq) >= 3 else np.nan,
        "model_sequence": "".join(seq).lower(),
    }
    per_min = int(60 * fps)
    for i, s in enumerate(range(0, n - 1, per_min), 1):
        f[f"dist_min{i:02d}_m"] = np.nansum(step[s:s + per_min]) / 100
    return f


def pick(clip_dir, out_csv):
    import cv2
    from oft_arena import background
    rows = []
    for clip in sorted(clip_dir.glob("*.mp4")):
        bg = cv2.cvtColor(background(clip), cv2.COLOR_GRAY2BGR)
        pts = []

        def click(ev, x, y, *_):
            if ev == cv2.EVENT_LBUTTONDOWN and len(pts) < 4:
                pts.append((x, y))
        cv2.namedWindow(clip.stem, cv2.WINDOW_NORMAL)
        cv2.setMouseCallback(clip.stem, click)
        while True:
            show = bg.copy()
            for i, pt in enumerate(pts):
                cv2.circle(show, pt, 6, (0, 0, 255), 2)
                cv2.putText(show, "OABC"[i], (pt[0] + 8, pt[1] - 8), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
            cv2.imshow(clip.stem, show)
            k = cv2.waitKey(30) & 0xFF
            if k == ord("r"):
                pts.clear()
            elif k == 13 and len(pts) == 4 or k == 27:
                break
        cv2.destroyWindow(clip.stem)
        if len(pts) != 4:
            print(clip.stem, "skipped")
            continue
        for i in range(1, 4):
            cv2.line(show, pts[0], pts[i], (0, 0, 255), 1)
        cv2.imwrite(str(out_csv.parent / f"{clip.stem}_arena.png"), show)
        rows.append({"stem": clip.stem, **{f"{ax}_{c}": v for c, pt in zip("oabc", pts) for ax, v in zip("xy", pt)}})
        print(clip.stem, pts)
    with open(out_csv, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)


def _selftest():
    # synthetic camera: 10 px/cm, centre at (500, 500), so the homography is a pure scale + shift
    pts = REAL * 10 + 500
    H = homography(pts)
    assert np.allclose(to_cm(np.array([[500.0, 150.0]]), H), [[0, -35]], atol=1e-3)   # arm A end
    # centre -> A (20 cm) -> centre -> B -> centre -> C -> centre -> A, 1 cm steps
    path = [np.zeros(2)]
    for a in (0, 1, 2, 0):
        out = [AXES[a] * d for d in range(1, 21)]
        path += out + out[::-1] + [np.zeros(2)]
    p = np.array(path)
    assert model_entries(p) == ["A", "B", "C", "A"]
    # a head dip to 5 cm (between CENTRE_CM and ENTRY_CM) is not an entry
    dip = np.array([AXES[1] * d for d in (0, 2, 5, 2, 0)])
    assert model_entries(dip) == []
    # re-entry into the same arm counts only after the centre
    wobble = np.array([AXES[0] * d for d in (0, 10, 5, 10, 2, 10)])
    assert model_entries(wobble) == ["A", "A"]
    arm, along, in_arm = zones(np.array([[0.0, -20], [0.0, 1.0]]))
    assert arm[0] == 0 and in_arm[0] and not in_arm[1]
    print("ymaze_pose selftest ok")


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)
    pk = sub.add_parser("pick")
    pk.add_argument("clip_dir", type=pathlib.Path)
    pk.add_argument("arena", type=pathlib.Path)
    fe = sub.add_parser("features")
    fe.add_argument("pose_dir", type=pathlib.Path)
    fe.add_argument("arena", type=pathlib.Path)
    fe.add_argument("out", type=pathlib.Path)
    fe.add_argument("--model", required=True, choices=["model1", "model2"])
    a = p.parse_args()
    if a.cmd == "pick":
        return pick(a.clip_dir, a.arena)
    with open(a.arena, newline="") as fh:
        arena = {r["stem"]: [[float(r[f"x_{c}"]), float(r[f"y_{c}"])] for c in "oabc"] for r in csv.DictReader(fh)}
    rows = []
    for npz in sorted(a.pose_dir.glob(f"*.{a.model}.npz")):
        stem = npz.name.split(".")[0]
        f = features(npz, homography(arena[stem]))
        rows.append({"stem": stem, "mouse": stem.split("_")[0], "model": a.model,
                     **{k: v if isinstance(v, str) else round(float(v), 4) for k, v in f.items()}})
        print(stem, f"{f['distance_m']:.1f} m, {f['mean_speed_cm_s']:.1f} cm/s, model entries {f['model_arm_entries']}")
    with open(a.out, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)


if __name__ == "__main__":
    _selftest() if len(sys.argv) == 1 else main()
