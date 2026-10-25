#!/usr/bin/env python3
"""Find the inner floor corners of the OFT box in each trial clip.

    behav-venv/Scripts/python oft_arena.py <clip_dir> <out_dir>

Writes <out_dir>/corners.csv (TL TR BR BL, pixels) and one overlay PNG per clip.
**Look at every overlay** before using the corners: the framing shifts between
batch 1 videos, so each clip gets its own floor. A wrong corner can be fixed by
editing corners.csv by hand.

Method: median of 60 frames (removes the mouse), then each floor edge is the
strongest brightness step inside a band, fitted as a line over the middle of
the edge (the corners themselves are blurred by the wall diagonals).
"""
import argparse
import csv
import pathlib

import cv2
import numpy as np

# search bands as fractions of the frame, from the batch 1 framing (1080 x 1080)
BANDS = {"top": (0.16, 0.32), "bottom": (0.66, 0.82), "left": (0.18, 0.31), "right": (0.65, 0.81)}


def background(clip, n=60):
    cap = cv2.VideoCapture(str(clip))
    total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    frames = []
    for i in np.linspace(0, total - 1, n).astype(int):
        cap.set(cv2.CAP_PROP_POS_FRAMES, i)
        ok, fr = cap.read()
        if ok:
            frames.append(cv2.cvtColor(fr, cv2.COLOR_BGR2GRAY))
    cap.release()
    return np.median(frames, axis=0).astype(np.uint8)


def edge_line(bg, side):
    """-> (a, b): the edge as y = a*x + b (top/bottom) or x = a*y + b (left/right)."""
    g = cv2.GaussianBlur(bg, (5, 5), 0).astype(np.float32)
    horizontal = side in ("top", "bottom")
    img = g if horizontal else g.T                 # work as if the edge were horizontal
    grad = np.abs(cv2.Sobel(img, cv2.CV_32F, 0, 1, ksize=5))
    h, w = img.shape
    lo, hi = (int(f * h) for f in BANDS[side])
    xs = np.arange(int(0.35 * w), int(0.65 * w))
    ys = lo + np.argmax(grad[lo:hi, xs], axis=0)
    keep = np.abs(ys - np.median(ys)) < 6
    return np.polyfit(xs[keep], ys[keep], 1)


def corners(bg):
    t, b, l, r = (edge_line(bg, s) for s in ("top", "bottom", "left", "right"))

    def meet(hl, vl):                              # y = a1 x + b1 and x = a2 y + b2
        y = (hl[0] * vl[1] + hl[1]) / (1 - hl[0] * vl[0])
        return vl[0] * y + vl[1], y
    return [meet(t, l), meet(t, r), meet(b, r), meet(b, l)]


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("clip_dir", type=pathlib.Path)
    p.add_argument("out_dir", type=pathlib.Path)
    a = p.parse_args()
    a.out_dir.mkdir(parents=True, exist_ok=True)
    rows = []
    for clip in sorted(a.clip_dir.glob("*.mp4")):
        bg = background(clip)
        c = corners(bg)
        rows.append({"stem": clip.stem, **{f"{ax}_{k}": round(v, 1) for k, pt in zip(("tl", "tr", "br", "bl"), c)
                                           for ax, v in zip("xy", pt)}})
        ov = cv2.cvtColor(bg, cv2.COLOR_GRAY2BGR)
        cv2.polylines(ov, [np.int32(c)], True, (0, 0, 255), 1)
        cv2.imwrite(str(a.out_dir / f"{clip.stem}_floor.png"), ov)
        side = [np.hypot(*np.subtract(c[i], c[(i + 1) % 4])) for i in range(4)]
        print(clip.stem, "sides px", [round(s) for s in side])
    with open(a.out_dir / "corners.csv", "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)


if __name__ == "__main__":
    main()
