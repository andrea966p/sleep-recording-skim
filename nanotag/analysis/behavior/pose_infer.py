#!/usr/bin/env python3
"""Run a lab YOLO pose model over trial clips -> one .npz of keypoints per clip.

Models come from a labmate (repo `model1/`, `model2/`, each with a .txt keypoint
index). Inference settings are the ones in those .txt files, unchanged.

    behav-venv/Scripts/python pose_infer.py model1 <clip_dir> <out_dir>

Each .npz holds, per frame, the TOP_K best detections by box confidence:
xy (N, D, K, 2) pixels, kconf (N, D, K), bconf (N, D); NaN / 0 where there is none.
Plus kpt_names, fps, model, decoded (frames the loader returned).

One deviation from the .txt settings: max_det = TOP_K, not 1. With max_det 1,
model2 put the mouse on the ring light outside the box in 2.4 % of HLBNSSL41's
frames at box conf ~0.84 (review 2026-10-25). The top detection is the same either
way; oft_features.py picks the best detection that lies on the floor.
Needs the venv with CUDA torch + ultralytics (see vault OFT note).
"""
import argparse
import pathlib
import sys

import numpy as np

REPO = pathlib.Path(__file__).resolve().parents[3]
TOP_K = 3

MODELS = {
    "model1": dict(imgsz=1440, iou=0.7, kpts=[
        "nose", "left_ear", "right_ear", "thoracic_center", "left_forelimb",
        "right_forelimb", "tail_base", "left_hindlimb", "right_hindlimb",
        "tail_middle", "tail_tip", "body_center"]),
    "model2": dict(imgsz=544, iou=0.3, kpts=[
        "nose", "left_ear", "right_ear", "left_forepaw", "right_forepaw",
        "left_hindpaw", "right_hindpaw", "tail_base", "tail_middle",
        "tail_tip", "body_center"]),
}


def infer(model_name, clip, out):
    import cv2
    from ultralytics import YOLO
    m = MODELS[model_name]
    cap = cv2.VideoCapture(str(clip))
    n, fps = int(cap.get(cv2.CAP_PROP_FRAME_COUNT)), cap.get(cv2.CAP_PROP_FPS)
    cap.release()
    k = len(m["kpts"])
    xy = np.full((n, TOP_K, k, 2), np.nan, np.float32)
    kconf = np.zeros((n, TOP_K, k), np.float32)
    bconf = np.zeros((n, TOP_K), np.float32)
    model = YOLO(str(REPO / model_name / f"{model_name}.pt"))
    i = -1
    for i, r in enumerate(model.predict(source=str(clip), conf=0.05, iou=m["iou"], max_det=TOP_K,
                                        imgsz=m["imgsz"], device=0, stream=True, verbose=False)):
        if r.keypoints is None or len(r.keypoints) == 0:
            continue
        d = len(r.keypoints)                     # ultralytics returns boxes sorted by conf
        xy[i, :d] = r.keypoints.xy.cpu().numpy()
        kconf[i, :d] = r.keypoints.conf.cpu().numpy()
        bconf[i, :d] = r.boxes.conf.cpu().numpy()
    decoded = i + 1
    # a dropped source frame (HLBNSSL42: 17999) is tolerated; anything more shifts the time base
    assert decoded >= n - 1, f"{clip.name}: decoded {decoded} of {n} frames"
    if decoded != n:
        print(f"WARNING {clip.name}: decoded {decoded} of {n} frames", flush=True)
    np.savez_compressed(out, xy=xy[:decoded], kconf=kconf[:decoded], bconf=bconf[:decoded], fps=fps,
                        kpt_names=np.array(m["kpts"]), model=model_name, decoded=decoded)
    print(f"{clip.name}: {decoded} frames, mouse found in {np.mean(bconf[:decoded, 0] > 0):.1%}, "
          f"2nd detection in {np.mean(bconf[:decoded, 1] > 0):.1%}", flush=True)


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("model", choices=MODELS)
    p.add_argument("clip_dir", type=pathlib.Path)
    p.add_argument("out_dir", type=pathlib.Path)
    a = p.parse_args()
    a.out_dir.mkdir(parents=True, exist_ok=True)
    clips = sorted(a.clip_dir.glob("*.mp4"))
    if not clips:
        sys.exit(f"no .mp4 in {a.clip_dir}")
    for c in clips:
        out = a.out_dir / f"{c.stem}.{a.model}.npz"
        if out.exists():
            print(f"{c.name}: exists, skipped")
            continue
        infer(a.model, c, out)


if __name__ == "__main__":
    main()
