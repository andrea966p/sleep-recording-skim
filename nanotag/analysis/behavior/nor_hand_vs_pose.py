#!/usr/bin/env python3
"""Blinded NOR hand scores (BORIS) against the two pose models, per BEHAVIOR_SOP.md section 3.

    python3 nor_hand_vs_pose.py <project.boris> <NOR_blind_key.csv> <pose_dir> <out_dir> --unblind

<pose_dir> holds nor_results_model{1,2}.csv and nor_bouts_model{1,2}.csv from nor_explore.py.
Reads the hand events straight from the BORIS project (state events, start/stop pairs), so no
export step is needed. An observation counts as scored only if it has at least one event.

The output names mice and groups: run it only after every clip is scored (hence --unblind).
Writes:
  per_clip.csv       seconds per object and bout counts, hand vs model1 vs model2
  per_mouse_d2.csv   d2 for mice with both trials hand scored
  summary.txt        per-clip seconds (r, ICC(A,1), bias, limits of agreement) and
                     frame-level agreement (Cohen's kappa, per-object precision / recall)
Per-object seconds come from nor_results (the published numbers); frame-level agreement from the
bout files, which differ from them by at most ~2 s per object (bout end frames). Run with no
arguments for the self-test.
"""
import argparse
import csv
import json
import os
import statistics as st
import sys

import numpy as np

import metrics

FPS = 30
CLIP_S = 600
HAND_OBJ = {"explore_A": "A", "explore_B": "B", "explore_familiar": "familiar", "explore_novel": "novel"}
OBJS = {"T1": ("A", "B"), "T2": ("familiar", "novel")}


def hand_bouts(events):
    """BORIS state events [time, subject, code, ...] -> [(object, start, end)]; asserts pairing."""
    open_, out = {}, []
    for e in sorted(events, key=lambda e: float(e[0])):
        t, code = float(e[0]), e[2]
        if code not in HAND_OBJ:
            continue
        if code in open_:
            out.append((HAND_OBJ[code], open_.pop(code), t))
        else:
            open_[code] = t
    assert not open_, f"unpaired state events: {sorted(open_)} (stop them in BORIS)"
    return out


def frames(bouts, objs):
    """Bouts -> per-frame label: 0 none, 1 first object, 2 second object."""
    lab = np.zeros(CLIP_S * FPS, dtype=np.int8)
    for o, s, e in bouts:
        lab[int(round(s * FPS)):int(round(e * FPS))] = objs.index(o) + 1
    return lab


def kappa(a, b, k=3):
    cm = np.zeros((k, k))
    np.add.at(cm, (a, b), 1)
    n = cm.sum()
    po, pe = np.trace(cm) / n, (cm.sum(0) * cm.sum(1)).sum() / n ** 2
    return (po - pe) / (1 - pe) if pe < 1 else float("nan")


def icc_a1(x, y):
    """ICC(A,1): two-way, absolute agreement, single rater (McGraw & Wong 1996)."""
    d = np.column_stack([x, y]).astype(float)
    n, k = d.shape
    gm = d.mean()
    msr = k * ((d.mean(1) - gm) ** 2).sum() / (n - 1)
    msc = n * ((d.mean(0) - gm) ** 2).sum() / (k - 1)
    mse = ((d - d.mean(1, keepdims=True) - d.mean(0, keepdims=True) + gm) ** 2).sum() / ((n - 1) * (k - 1))
    return (msr - mse) / (msr + (k - 1) * mse + k * (msc - mse) / n)


def agreement(h, m):
    h, m = np.asarray(h, float), np.asarray(m, float)
    d = m - h
    sd = d.std(ddof=1) if len(d) > 1 else float("nan")
    r = np.corrcoef(h, m)[0, 1] if len(h) > 2 else float("nan")
    icc = icc_a1(h, m) if len(h) > 2 else float("nan")
    return f"r {r:+.3f}, ICC(A,1) {icc:.3f}, bias {d.mean():+.2f} s, LoA {d.mean() - 1.96 * sd:+.2f} to {d.mean() + 1.96 * sd:+.2f} s"


def main(a):
    pj = json.load(open(a.project))
    key = {r["code"]: r for r in csv.DictReader(open(a.key))}
    res = {m: {r["mouse"]: r for r in csv.DictReader(open(os.path.join(a.pose, f"nor_results_model{m}.csv")))} for m in (1, 2)}
    pb = {m: {} for m in (1, 2)}
    for m in (1, 2):
        for r in csv.DictReader(open(os.path.join(a.pose, f"nor_bouts_model{m}.csv"))):
            pb[m].setdefault(r["clip"], []).append((r["object"], float(r["start_s"]), float(r["end_s"])))
    rows, lab = [], {"hand": [], 1: [], 2: []}
    for code, ob in sorted(pj["observations"].items()):
        if not ob["events"]:
            continue
        k = key[code]
        trial, mouse, clip = k["trial"].replace("NOR-", ""), k["mouse"], k["clip"].removesuffix(".mp4")
        objs, hb = OBJS[trial], hand_bouts(ob["events"])
        row = {"code": code, "mouse": mouse, "group": k["group"], "trial": trial}
        for o in objs:
            row[f"hand_{o}_s"] = round(sum(e - s for x, s, e in hb if x == o), 3)
            row[f"hand_{o}_bouts"] = sum(x == o for x, _, _ in hb)
            for m in (1, 2):
                row[f"m{m}_{o}_s"] = float(res[m][mouse][f"{trial}_{o}_s"])
        rows.append(row)
        lab["hand"].append(frames(hb, objs))
        for m in (1, 2):
            lab[m].append(frames(pb[m].get(clip, []), objs))
    assert rows, "no scored observations in the project"
    os.makedirs(a.out, exist_ok=True)
    cols = sorted({c for r in rows for c in r}, key=lambda c: (c not in ("code", "mouse", "group", "trial"), c))
    with open(os.path.join(a.out, "per_clip.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, cols)
        w.writeheader()
        w.writerows(rows)

    out = [f"NOR hand vs pose: {len(rows)} hand-scored clips ({', '.join(r['code'] for r in rows)})", ""]
    out.append("Per-clip seconds per object (each object of each clip is one point)")
    for m in (1, 2):
        h = [r[f"hand_{o}_s"] for r in rows for o in OBJS[r["trial"]]]
        p = [r[f"m{m}_{o}_s"] for r in rows for o in OBJS[r["trial"]]]
        out.append(f"  model{m} vs hand, all objects: {agreement(h, p)}")
        for o in ("A", "B", "familiar", "novel"):
            sub = [r for r in rows if f"hand_{o}_s" in r]
            if sub:
                out.append(f"    {o:9s} n={len(sub):2d}: {agreement([r[f'hand_{o}_s'] for r in sub], [r[f'm{m}_{o}_s'] for r in sub])}")
    out += ["", "Frame-level agreement (30 Hz, labels none / object 1 / object 2, all scored clips pooled)"]
    H = np.concatenate(lab["hand"])
    for name, P in (("model1 vs hand", np.concatenate(lab[1])), ("model2 vs hand", np.concatenate(lab[2])),
                    ("model1 vs model2", None)):
        ref = H if P is not None else np.concatenate(lab[2])
        P = P if P is not None else np.concatenate(lab[1])
        line = f"  {name}: kappa {kappa(ref, P):.3f}"
        for i, o in ((1, "object 1"), (2, "object 2")):
            tp = np.sum((P == i) & (ref == i))
            line += f"; {o} precision {tp / max(np.sum(P == i), 1):.2f} recall {tp / max(np.sum(ref == i), 1):.2f}"
        out.append(line)
    out.append("  (object 1 = A or familiar, object 2 = B or novel; for model1 vs model2, model2 is the reference)")

    d2rows = []
    for mouse in sorted({r["mouse"] for r in rows}):
        t2 = [r for r in rows if r["mouse"] == mouse and r["trial"] == "T2"]
        if t2:
            r = t2[0]
            d2rows.append({"mouse": mouse, "group": r["group"],
                           "hand_d2": metrics.discrimination_index(r["hand_novel_s"], r["hand_familiar_s"]),
                           "m1_d2": float(res[1][mouse]["d2"]), "m2_d2": float(res[2][mouse]["d2"])})
    if d2rows:
        with open(os.path.join(a.out, "per_mouse_d2.csv"), "w", newline="") as f:
            w = csv.DictWriter(f, list(d2rows[0]))
            w.writeheader()
            w.writerows(d2rows)
        out += ["", f"d2 per mouse (T2 hand scored, n={len(d2rows)})"]
        for m in (1, 2):
            out.append(f"  model{m} vs hand: {agreement([r['hand_d2'] for r in d2rows], [r[f'm{m}_d2'] for r in d2rows]).replace(' s', '')}")
        for g in sorted({r["group"] for r in d2rows}):
            gs = [r for r in d2rows if r["group"] == g]
            out.append(f"  {g:6s} n={len(gs)}: d2 hand {st.mean(r['hand_d2'] for r in gs):+.3f}, "
                       f"model1 {st.mean(r['m1_d2'] for r in gs):+.3f}, model2 {st.mean(r['m2_d2'] for r in gs):+.3f}")
    txt = "\n".join(out)
    open(os.path.join(a.out, "summary.txt"), "w").write(txt + "\n")
    print(txt)


def selftest():
    ev = [[1.0, "", "explore_A", "", ""], [2.5, "", "explore_A", "", ""], [3.0, "", "explore_B", "", ""],
          [4.0, "", "explore_B", "", ""], [0.5, "", "something_else", "", ""]]
    hb = hand_bouts(ev)
    assert hb == [("A", 1.0, 2.5), ("B", 3.0, 4.0)], hb
    lab = frames(hb, ("A", "B"))
    assert lab.sum() == 45 * 1 + 30 * 2 and lab[30] == 1 and lab[29] == 0
    try:
        hand_bouts(ev[:1])
        raise SystemExit("unpaired event not caught")
    except AssertionError:
        pass
    assert abs(kappa(lab, lab) - 1) < 1e-9
    x = np.array([10., 20, 30, 40])
    assert abs(icc_a1(x, x) - 1) < 1e-9 and icc_a1(x, x + 10) < icc_a1(x, x + 1)
    print("self-test ok")


if __name__ == "__main__":
    if len(sys.argv) == 1:
        selftest()
        sys.exit()
    p = argparse.ArgumentParser()
    for n in ("project", "key", "pose", "out"):
        p.add_argument(n)
    p.add_argument("--unblind", action="store_true", help="required: the output names mice and groups")
    a = p.parse_args()
    if not a.unblind:
        sys.exit("refusing to run without --unblind: the output names mice and groups")
    main(a)
