#!/usr/bin/env python3
"""Day-1 open field (NOR habituation) features from pose keypoints.

    behav-venv/Scripts/python oft_features.py <pose_dir> <corners.csv> <out.csv> [--model model1]

`corners.csv`: clip stem, then the inner FLOOR corners in pixels, TL TR BR BL
(columns stem,x_tl,y_tl,x_tr,y_tr,x_br,y_br,x_bl,y_bl), from `oft_arena.py`.
The floor is mapped to 0..50 cm by a homography, so every distance is on the
floor plane; the camera is close and the walls tall, so a raised nose near a wall
lands outside 0..50, which is what the wall-rear proxy counts.

Definitions (BEHAVIOR_SOP section 2, decisions dated in its changelog):
body point = body_center; centre = inner 25 x 25 cm; thigmotaxis = within 5 cm of a
wall (metrics.thigmotaxis); immobile = speed < 2 cm/s held >= 2 s; bins 1 min;
object spots = the NOR T1 object centres, measured on day-2 video.
"""
import argparse
import csv
import pathlib

import cv2
import numpy as np
from scipy.ndimage import median_filter

import metrics

ARENA_CM = 50.0
CENTRE_LO, CENTRE_HI = 12.5, 37.5
KCONF_MIN = 0.3
MAX_GAP_S = 0.5               # interpolate body-point gaps up to this, leave longer ones NaN
MEDIAN_FRAMES = 5
IMMOBILE_CM_S, IMMOBILE_MIN_S = 2.0, 2.0
# mean T1 object centres over the 9 HLBNSL NOR-T1 clips (nor_objects.py, 2026-10-25; spread < 0.5 cm)
OBJECT_SPOTS_CM = {"obj_UL": (14.1, 13.4), "obj_LR": (35.7, 37.0)}
OBJECT_RADIUS_CM = 5.0
WALL_REAR_CM = 1.5            # nose this far outside the floor = head raised against a wall
ON_FLOOR_CM = 15.0            # body point further outside is not the mouse: rears project ~5 cm out, the ring light ~60 cm
CENTRE_HYST_CM = 1.0          # stops edge flicker counting as entries (36 of 80 were < 0.5 s)


def to_cm(xy_px, corners_px):
    H = cv2.getPerspectiveTransform(np.float32(corners_px),
                                    np.float32([[0, 0], [ARENA_CM, 0], [ARENA_CM, ARENA_CM], [0, ARENA_CM]]))
    flat = xy_px.reshape(-1, 1, 2).astype(np.float32)
    out = cv2.perspectiveTransform(np.nan_to_num(flat, nan=-1e6), H).reshape(xy_px.shape)
    out[np.isnan(xy_px)] = np.nan
    return out


def pick_on_floor(xy, kconf, bconf, body_i):
    """(N, D, K, 2) cm detections -> the best-conf one per frame whose body point lies
    within ON_FLOOR_CM of the floor (rejects the ring light outside the box)."""
    b = xy[:, :, body_i]
    on = (bconf > 0) & np.all((b >= -ON_FLOOR_CM) & (b <= ARENA_CM + ON_FLOOR_CM), axis=2)
    best = np.argmax(np.where(on, bconf, -1), axis=1)          # bconf is sorted, ties irrelevant
    rows = np.arange(len(xy))
    sel_xy, sel_k = xy[rows, best].copy(), kconf[rows, best].copy()
    none = ~on.any(axis=1)
    sel_xy[none], sel_k[none] = np.nan, 0
    return sel_xy, sel_k, none, best


def clean(track, kconf, fps):
    """Drop low-confidence samples, fill short gaps linearly, median-filter jitter
    within each tracked run (never across a gap)."""
    t = track.copy()
    t[kconf < KCONF_MIN] = np.nan
    ok = ~np.isnan(t[:, 0])
    if not ok.any():
        return t, 0.0
    idx = np.arange(len(t))
    for d in range(2):
        t[:, d] = np.interp(idx, idx[ok], t[ok, d])
    for a, b in runs(~ok):                       # re-blank gaps longer than MAX_GAP_S
        if b - a > MAX_GAP_S * fps:
            t[a:b] = np.nan
    for a, b in runs(~np.isnan(t[:, 0])):
        t[a:b] = median_filter(t[a:b], size=(MEDIAN_FRAMES, 1), mode="nearest")
    return t, ok.mean()


def centre_entries(p, lo=CENTRE_LO, hi=CENTRE_HI, hyst=CENTRE_HYST_CM):
    """Entries into the centre square with hysteresis: in once inside the square shrunk
    by `hyst`, out once outside it grown by `hyst`. Gaps keep the state; the starting
    position is not an entry."""
    state, n = None, 0
    for x, y in p:
        if np.isnan(x):
            continue
        deep = lo + hyst <= x <= hi - hyst and lo + hyst <= y <= hi - hyst
        out = not (lo - hyst <= x <= hi + hyst and lo - hyst <= y <= hi + hyst)
        if state is None:
            state = lo <= x <= hi and lo <= y <= hi
        elif deep and not state:
            state, n = True, n + 1
        elif out:
            state = False
    return n


def runs(mask):
    """-> list of (start, stop) index pairs of True runs."""
    m = np.concatenate([[False], mask, [False]]).astype(int)
    d = np.diff(m)
    return list(zip(np.flatnonzero(d == 1), np.flatnonzero(d == -1)))


def features(npz, corners):
    z = np.load(npz)
    fps, names = float(z["fps"]), list(z["kpt_names"])
    bi, ni = names.index("body_center"), names.index("nose")
    xy, kconf, none, best = pick_on_floor(to_cm(z["xy"], corners), z["kconf"], z["bconf"], bi)
    n = len(xy)
    body, body_ok = clean(xy[:, bi], kconf[:, bi], fps)
    nose, _ = clean(xy[:, ni], kconf[:, ni], fps)

    step = np.linalg.norm(np.diff(body, axis=0), axis=1)          # NaN across gaps
    # speed = displacement across a centred 1 s window: per-frame steps would add jitter up
    half = int(fps) // 2
    speed = np.full(n, np.nan)
    speed[half:n - half] = np.linalg.norm(body[2 * half:] - body[:n - 2 * half], axis=1) * fps / (2 * half)
    track = [None if np.isnan(p[0]) else (p[0], p[1]) for p in body]
    tracked = ~np.isnan(body[:, 0])

    immobile = np.zeros(n, bool)
    for a, b in runs(speed < IMMOBILE_CM_S):
        if (b - a) / fps >= IMMOBILE_MIN_S:
            immobile[a:b] = True

    inside = lambda p, lo, hi: (p[:, 0] >= lo) & (p[:, 0] <= hi) & (p[:, 1] >= lo) & (p[:, 1] <= hi)
    centre = inside(body, CENTRE_LO, CENTRE_HI)

    f = {
        "frames": n,
        "mouse_found_pct": 100 * np.mean(z["bconf"][:, 0] > 0),
        "mouse_on_floor_pct": 100 * np.mean(~none),
        # frames where the model's top detection was off the floor (ring light) and got replaced or dropped
        "top_detection_rejected_pct": 100 * np.mean((z["bconf"][:, 0] > 0) & ((best > 0) | none)),
        "body_conf_ok_pct": 100 * body_ok,
        "body_tracked_pct": 100 * tracked.mean(),
        "distance_cm": np.nansum(step),
        "mean_speed_cm_s": np.nansum(step) / (tracked.sum() / fps),
        "immobile_s": immobile.sum() / fps,
        "immobile_bouts": len(runs(immobile)),
        "centre_time_s": centre.sum() / fps,
        "centre_time_pct": 100 * centre.sum() / tracked.sum(),
        # no centre latency: the mouse is released near the centre, so it is ~0 by design
        "centre_entries": centre_entries(body),
        "thigmotaxis_pct": 100 * metrics.thigmotaxis(track, ARENA_CM),
    }
    per_min = int(60 * fps)
    bins = [np.nansum(step[i:i + per_min]) for i in range(0, n - 1, per_min)][:10]
    for i, d in enumerate(bins, 1):
        f[f"dist_min{i:02d}_cm"] = d
    f["habituation_ratio_last3_first3"] = sum(bins[-3:]) / sum(bins[:3])
    f["habituation_slope_cm_per_min"] = np.polyfit(np.arange(1, len(bins) + 1), bins, 1)[0]

    for q, (xs, ys) in {"q_UL": (0, 0), "q_UR": (1, 0), "q_LR": (1, 1), "q_LL": (0, 1)}.items():
        mx = (body[:, 0] >= 25) == bool(xs)
        my = (body[:, 1] >= 25) == bool(ys)
        f[f"{q}_pct"] = 100 * (mx & my & tracked).sum() / tracked.sum()
    nose_ok = ~np.isnan(nose[:, 0])
    for k, (ox, oy) in OBJECT_SPOTS_CM.items():
        near = np.hypot(nose[:, 0] - ox, nose[:, 1] - oy) <= OBJECT_RADIUS_CM
        f[f"{k}_nose_within5cm_s"] = near.sum() / fps
    a, b = f["obj_UL_nose_within5cm_s"], f["obj_LR_nose_within5cm_s"]
    f["object_spot_bias"] = metrics.location_bias(a, b) if a + b > 0 else np.nan

    out = nose_ok & ((nose[:, 0] < -WALL_REAR_CM) | (nose[:, 0] > ARENA_CM + WALL_REAR_CM) |
                     (nose[:, 1] < -WALL_REAR_CM) | (nose[:, 1] > ARENA_CM + WALL_REAR_CM))
    wr = [r for r in runs(out) if (r[1] - r[0]) / fps >= 0.3]   # ignore single-frame keypoint jumps
    f["wall_rear_proxy_n"] = len(wr)
    f["wall_rear_proxy_s"] = sum(b - a for a, b in wr) / fps
    return f


def _selftest():
    sq = [[100, 100], [600, 100], [600, 600], [100, 600]]
    p = to_cm(np.array([[[350.0, 350.0], [np.nan, np.nan]]]), sq)
    assert np.allclose(p[0, 0], [25, 25]) and np.isnan(p[0, 1]).all()
    assert runs(np.array([0, 1, 1, 0, 1], bool)) == [(1, 3), (4, 5)]
    t, ok = clean(np.array([[0, 0], [1, 1], [9, 9], [3, 3], [4, 4]], float),
                  np.array([1, 1, 0, 1, 1.0]), fps=30)
    assert ok == 0.8 and np.allclose(t[2], [2, 2])          # 1-frame gap interpolated
    # a short good run between two long gaps keeps its own value, not the 0 fill
    tr = np.array([[7.0, 7.0]] * 2 + [[np.nan, np.nan]] * 20 + [[9.0, 9.0]] * 2 + [[np.nan, np.nan]] * 20)
    t, _ = clean(tr, np.where(np.isnan(tr[:, 0]), 0, 1.0), fps=30)
    assert np.allclose(t[22:24], 9) and np.isnan(t[2:22]).all()
    assert clean(tr, np.zeros(len(tr)), fps=30)[1] == 0.0  # nothing confident: no crash
    # off-floor top detection (ring light) loses to the on-floor second one
    xy = np.full((1, 2, 1, 2), np.nan); xy[0, 0, 0] = [-30, 60]; xy[0, 1, 0] = [20, 20]
    sel, k, none, best = pick_on_floor(xy, np.ones((1, 2, 1)), np.array([[0.9, 0.5]]), 0)
    assert best[0] == 1 and np.allclose(sel[0, 0], [20, 20]) and not none[0]
    # edge flicker is not an entry; a real crossing in and back is one
    flick = [(12.0, 25.0), (12.6, 25.0), (12.4, 25.0), (12.7, 25.0)]
    assert centre_entries(np.array(flick)) == 0
    assert centre_entries(np.array([(5.0, 25.0), (20.0, 25.0), (5.0, 25.0), (20.0, 25.0)])) == 2
    print("oft_features selftest ok")


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("pose_dir", type=pathlib.Path)
    p.add_argument("corners", type=pathlib.Path)
    p.add_argument("out", type=pathlib.Path)
    p.add_argument("--model", required=True, choices=["model1", "model2"])
    a = p.parse_args()
    with open(a.corners, newline="") as fh:
        corners = {r["stem"]: np.array([[float(r[f"x_{c}"]), float(r[f"y_{c}"])]
                                        for c in ("tl", "tr", "br", "bl")]) for r in csv.DictReader(fh)}
    rows = []
    for npz in sorted(a.pose_dir.glob(f"*.{a.model}.npz")):
        stem = npz.name.split(".")[0]
        rows.append({"stem": stem, "mouse": stem.split("_")[0], "model": a.model,
                     **{k: round(float(v), 4) for k, v in features(npz, corners[stem]).items()}})
        print(stem, f"{rows[-1]['distance_cm']:.0f} cm, centre {rows[-1]['centre_time_pct']:.1f} %")
    with open(a.out, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)


if __name__ == "__main__":
    import sys
    _selftest() if len(sys.argv) == 1 else main()
