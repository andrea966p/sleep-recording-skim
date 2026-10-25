#!/usr/bin/env python3
"""Locate the NOR objects in each trial clip, in floor cm.

    behav-venv/Scripts/python nor_objects.py <clip_dir> <corners.csv> <out.csv>

The objects are the only saturated colour on the white floor (HLBNSL: red pyramids,
blue prism in T2). Median of 60 frames removes the mouse; each colour blob gives
its centroid, its footprint-edge distance to the two nearest walls (both in cm on
the floor plane), its colour and its footprint outline (convex hull, cm). Run with no arguments for the self-test.
"""
import csv
import json
import pathlib
import sys

import cv2
import numpy as np

from oft_features import ARENA_CM, OBJECT_SPOTS_CM, to_cm

MIN_AREA_PX = 150
GROW_PX = 8                 # how far from the colour blob a grey side face may reach (about 0.75 cm)
DARK_FRAC = 0.8             # grey side face: darker than 0.8 x the floor around the object
EXPECTED = {"NOR-T1": ("red", "red"), "NOR-T2": ("red", "blue")}   # (upper left, lower right)


def blobs(bgr, corners):
    """-> list of dicts (cx, cy, x0, x1, y0, y1 in cm, colour) for each object."""
    hsv = cv2.cvtColor(bgr, cv2.COLOR_BGR2HSV)
    floor = np.zeros(hsv.shape[:2], np.uint8)
    cv2.fillPoly(floor, [np.int32(corners)], 255)
    mask = ((hsv[..., 1] > 80) & (hsv[..., 2] > 40) & (floor > 0)).astype(np.uint8)
    n, lab, st, _ = cv2.connectedComponentsWithStats(cv2.morphologyEx(mask, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8)))
    out = []
    for i in range(1, n):
        if st[i, cv2.CC_STAT_AREA] < MIN_AREA_PX:
            continue
        blob = (lab == i).astype(np.uint8)
        ys, xs = np.nonzero(blob)
        hue = hsv[ys, xs, 0]                                  # OpenCV hue 0-180: red ~0/180, blue ~110
        n_blue, n_red = np.sum((hue >= 90) & (hue <= 135)), np.sum((hue < 15) | (hue > 165))
        # the blue prism's grey side band is unsaturated: add dark pixels attached to the colour blob
        near = cv2.dilate(blob, np.ones((2 * GROW_PX + 1,) * 2, np.uint8)) & (floor > 0)
        ring = cv2.dilate(blob, np.ones((4 * GROW_PX + 1,) * 2, np.uint8)) & ~near & (floor > 0)
        dark = (hsv[..., 2] < DARK_FRAC * np.median(hsv[..., 2][ring > 0])) & (near > 0)
        grown = cv2.morphologyEx((blob | dark).astype(np.uint8), cv2.MORPH_CLOSE, np.ones((3, 3), np.uint8))
        nlab, glab = cv2.connectedComponents(grown)
        grown = glab == glab[ys[0], xs[0]]                    # only what touches the colour blob
        ys, xs = np.nonzero(grown)
        cm = to_cm(np.stack([xs, ys], 1).astype(np.float32)[None], corners)[0]
        out.append(dict(cx=cm[:, 0].mean(), cy=cm[:, 1].mean(), x0=cm[:, 0].min(), x1=cm[:, 0].max(),
                        y0=cm[:, 1].min(), y1=cm[:, 1].max(),
                        hull=cv2.convexHull(cm.astype(np.float32)).reshape(-1, 2).astype(float),
                        colour="blue" if n_blue > 0.6 * len(hue) else "red" if n_red > 0.6 * len(hue) else "unknown"))
    return sorted(out, key=lambda b: b["cx"] + b["cy"])           # upper-left object first


def main():
    clip_dir, corners_csv, out = map(pathlib.Path, sys.argv[1:4])
    with open(corners_csv, newline="") as fh:
        corners = {r["stem"]: np.array([[float(r[f"x_{c}"]), float(r[f"y_{c}"])] for c in ("tl", "tr", "br", "bl")])
                   for r in csv.DictReader(fh)}
    rows = []
    for clip in sorted(clip_dir.glob("*.mp4")):
        cap = cv2.VideoCapture(str(clip))
        idx = np.linspace(0, int(cap.get(cv2.CAP_PROP_FRAME_COUNT)) - 1, 60).astype(int)
        frames = []
        for i in idx:
            cap.set(cv2.CAP_PROP_POS_FRAMES, i)
            ok, fr = cap.read()
            if ok:
                frames.append(fr)
        cap.release()
        med = np.median(frames, axis=0).astype(np.uint8)
        bs = blobs(med, corners[clip.stem])
        test = clip.stem.split("_")[1]
        assert len(bs) == 2, f"{clip.stem}: {len(bs)} objects found, expected 2"
        if test in EXPECTED:
            assert tuple(b["colour"] for b in bs) == EXPECTED[test], f"{clip.stem}: colours {[b['colour'] for b in bs]}"
        for b, spot in zip(bs, OBJECT_SPOTS_CM.values()):
            assert np.hypot(b["cx"] - spot[0], b["cy"] - spot[1]) < 3, f"{clip.stem}: object at {b['cx']:.1f}, {b['cy']:.1f}"
        for k, b in zip(("obj_UL", "obj_LR"), bs):
            rows.append({"stem": clip.stem, "object": k, "colour": b["colour"],
                         "cx_cm": round(b["cx"], 2), "cy_cm": round(b["cy"], 2),
                         "edge_to_x_wall_cm": round(b["x0"] if k == "obj_UL" else ARENA_CM - b["x1"], 2),
                         "edge_to_y_wall_cm": round(b["y0"] if k == "obj_UL" else ARENA_CM - b["y1"], 2),
                         "footprint_cm": round(max(b["x1"] - b["x0"], b["y1"] - b["y0"]), 2),
                         # footprint outline in floor cm, for the exploration distance (nor_explore.py)
                         "hull_cm": json.dumps(np.round(b["hull"], 2).tolist())})
        print(clip.stem, [(r["object"], r["colour"], r["cx_cm"], r["cy_cm"], r["edge_to_x_wall_cm"], r["edge_to_y_wall_cm"])
                          for r in rows if r["stem"] == clip.stem], flush=True)
    with open(out, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)


def _selftest():
    img = np.full((600, 600, 3), 200, np.uint8)
    cv2.rectangle(img, (190, 190), (210, 210), (0, 0, 220), -1)      # red square at 20 cm (BGR)
    cv2.rectangle(img, (390, 390), (410, 410), (220, 0, 0), -1)      # blue square at 40 cm
    bs = blobs(img, np.array([[0, 0], [500, 0], [500, 500], [0, 500]], float))
    assert [b["colour"] for b in bs] == ["red", "blue"], bs
    assert abs(bs[0]["cx"] - 2.0 * 10) < 0.2 and abs(bs[1]["x0"] - 39.0) < 0.2
    assert len(bs[0]["hull"]) >= 4 and abs(bs[0]["hull"][:, 0].max() - 21.0) < 0.2
    print("nor_objects selftest ok")


if __name__ == "__main__":
    _selftest() if len(sys.argv) == 1 else main()
