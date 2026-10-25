#!/usr/bin/env python3
"""NOR object exploration from pose keypoints, per BEHAVIOR_SOP.md section 3.

    behav-venv/Scripts/python nor_explore.py <NOR-T1 dir> <NOR-T2 dir> <out_dir> --model model2
                                              [--oft <OFT features CSV>]

Each test dir holds pose/ (pose_infer.py), arena/corners.csv (oft_arena.py) and
arena/objects.csv (nor_objects.py). Writes per-clip exploration bouts, a per-mouse
table (T1/T2 exploration, d2, T1 location bias, exclusions) and the statistics.

The SOP rule, verbatim: "Exploration = the snout is directed at and within 2 cm of
the object. Excluded: sitting on the object; climbing or rearing with the forepaws
on the object; chewing or gnawing the object; and passing the object with the snout
oriented elsewhere." Per frame, from the keypoints:
  within 2 cm   nose at most NEAR_CM outside the object's footprint outline
  directed at   head vector (ear midpoint -> nose) within HEAD_DEG of the direction
                from the ear midpoint to the object centre, or nose within TOUCH_CM
  sitting on    body centre within ON_BODY_CM of the footprint, or a hind paw PAW_IN_CM inside it
  forepaws on   a confident fore paw PAW_IN_CM inside the footprint
TOUCH_CM and PAW_IN_CM were set 2026-10-25 from contact sheets of HLBNSSL41 / HLBNWSL47 T2 and
HLBNWSL45 T1, before any hand scoring. An "ears over the footprint" rule was tried and dropped the
same day: on the low blue prism it counted climbing over the object (review, 0/4 frames agreed).
Bouts shorter than MIN_BOUT_S do not count as bouts or set the latency; the seconds still count.
Chewing cannot be told from close sniffing from above and is NOT excluded: the
hand-scored subset measures what that costs. Run with no arguments for the self-test.
"""
import argparse
import csv
import json
import os
import pathlib
import statistics as st
import sys

import cv2
import numpy as np
from scipy import stats

import metrics
from oft_features import KCONF_MIN, clean, pick_on_floor, runs, to_cm

NEAR_CM = 2.0
HEAD_DEG = 45.0
ON_BODY_CM = 0.5
TOUCH_CM = 0.5              # nose this close counts as directed whatever the head angle (touching)
PAW_IN_CM = 0.5             # a paw must be this far inside the footprint: keypoint error grazes the edge
MERGE_GAP_S = 0.2           # bouts closer than this are one bout (keypoint flicker)
MIN_BOUT_S = 0.1            # shorter runs are keypoint flicker: no bout, no latency
PAWS = {"model1": (("left_forelimb", "right_forelimb"), ("left_hindlimb", "right_hindlimb")),
        "model2": (("left_forepaw", "right_forepaw"), ("left_hindpaw", "right_hindpaw"))}


def outside_cm(pts, hull):
    """Signed distance of each point to the footprint outline: > 0 outside, <= 0 on it. NaN stays NaN."""
    c = hull.astype(np.float32).reshape(-1, 1, 2)
    out = np.full(len(pts), np.nan)
    for i, (x, y) in enumerate(pts):
        if not np.isnan(x):
            out[i] = -cv2.pointPolygonTest(c, (float(x), float(y)), True)
    return out


def exploring(nose, ear_mid, body, fore, hind, hull, centre):
    """-> (explore, on_object) boolean arrays, one value per frame, for one object."""
    d_nose = outside_cm(nose, hull)
    head = nose - ear_mid
    to_obj = centre[None] - ear_mid
    with np.errstate(invalid="ignore", divide="ignore"):   # ears on the object centre: angle undefined, other rules decide
        cosang = np.sum(head * to_obj, 1) / (np.linalg.norm(head, axis=1) * np.linalg.norm(to_obj, axis=1))
    directed = (np.nan_to_num(cosang, nan=-1.0) >= np.cos(np.radians(HEAD_DEG))) | (d_nose <= TOUCH_CM)
    on_paw = lambda paws: np.any([outside_cm(p, hull) <= -PAW_IN_CM for p in paws], axis=0)
    on_object = (outside_cm(body, hull) <= ON_BODY_CM) | on_paw(hind) | on_paw(fore)
    ok = ~np.isnan(d_nose) & ~np.isnan(ear_mid[:, 0])
    return ok & (d_nose <= NEAR_CM) & directed & ~on_object, on_object


def merged_runs(mask, gap):
    """runs() with gaps of at most `gap` frames closed."""
    rs = runs(mask)
    out = []
    for a, b in rs:
        if out and a - out[-1][1] <= gap:
            out[-1] = (out[-1][0], b)
        else:
            out.append((a, b))
    return out


def score_clip(npz, corners, objs, model):
    z = np.load(npz)
    fps, names = float(z["fps"]), list(z["kpt_names"])
    bi = names.index("body_center")
    xy, kconf, none, best = pick_on_floor(to_cm(z["xy"], corners), z["kconf"], z["bconf"], bi)
    track = lambda k: clean(xy[:, names.index(k)], kconf[:, names.index(k)], fps)[0]
    nose, body = track("nose"), track("body_center")
    ear_mid = (track("left_ear") + track("right_ear")) / 2
    raw = lambda k: np.where((kconf[:, names.index(k)] >= KCONF_MIN)[:, None], xy[:, names.index(k)], np.nan)
    fore, hind = ([raw(k) for k in ks] for ks in PAWS[model])
    res = {"frames": len(xy), "mouse_on_floor_pct": 100 * np.mean(~none),
           "distance_m": np.nansum(np.linalg.norm(np.diff(body, axis=0), axis=1)) / 100}
    bouts = []
    for o in objs:
        ex, on = exploring(nose, ear_mid, body, fore, hind, o["hull"], o["centre"])
        rs = [r for r in merged_runs(ex, int(MERGE_GAP_S * fps)) if r[1] - r[0] >= MIN_BOUT_S * fps]
        res[f"{o['role']}_s"] = ex.sum() / fps
        res[f"{o['role']}_bouts"] = len(rs)
        res[f"{o['role']}_latency_s"] = rs[0][0] / fps if rs else np.nan
        res[f"{o['role']}_on_object_s"] = on.sum() / fps
        bouts += [(o["role"], a / fps, b / fps) for a, b in rs]
    return res, sorted(bouts, key=lambda b: b[1])


def load_test(d, model, trial):
    d = pathlib.Path(d)
    with open(d / "arena" / "corners.csv", newline="") as fh:
        corners = {r["stem"]: np.array([[float(r[f"x_{c}"]), float(r[f"y_{c}"])] for c in ("tl", "tr", "br", "bl")])
                   for r in csv.DictReader(fh)}
    objs = {}
    with open(d / "arena" / "objects.csv", newline="") as fh:
        for r in csv.DictReader(fh):
            if trial == "T1":
                role = "A" if r["object"] == "obj_UL" else "B"          # identical objects: by position
            else:
                role = "novel" if r["colour"] == "blue" else "familiar"
            objs.setdefault(r["stem"], []).append({"role": role, "hull": np.array(json.loads(r["hull_cm"])),
                                                   "centre": np.array([float(r["cx_cm"]), float(r["cy_cm"])])})
    out = {}
    for npz in sorted((d / "pose").glob(f"*.{model}.npz")):
        stem = npz.name.split(".")[0]
        roles = sorted(o["role"] for o in objs[stem])
        assert roles == (["A", "B"] if trial == "T1" else ["familiar", "novel"]), f"{stem}: objects {roles}"
        out[stem.split("_")[0]] = (stem,) + score_clip(npz, corners[stem], objs[stem], model)
    return out


def group(mouse):
    return "SOD1" if mouse.startswith("HLBNS") else "water"


def main():
    pa = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    pa.add_argument("t1")
    pa.add_argument("t2")
    pa.add_argument("out_dir")
    pa.add_argument("--model", required=True, choices=list(PAWS))
    pa.add_argument("--oft", help="day 1 features CSV, for the locomotor check")
    a = pa.parse_args()
    os.makedirs(a.out_dir, exist_ok=True)
    t1, t2 = load_test(a.t1, a.model, "T1"), load_test(a.t2, a.model, "T2")
    assert set(t1) == set(t2), f"T1 mice {sorted(t1)} != T2 mice {sorted(t2)}"

    with open(os.path.join(a.out_dir, f"nor_bouts_{a.model}.csv"), "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["mouse", "trial", "clip", "object", "start_s", "end_s"])
        for trial, d in (("T1", t1), ("T2", t2)):
            for m, (stem, _, bouts) in sorted(d.items()):
                w.writerows([m, trial, stem, o, round(s, 3), round(e, 3)] for o, s, e in bouts)

    rows = []
    for m in sorted(t1, key=lambda m: (group(m) != "SOD1", m)):
        r1, r2 = t1[m][1], t2[m][1]
        tot1, tot2 = r1["A_s"] + r1["B_s"], r2["familiar_s"] + r2["novel_s"]
        rows.append({"mouse": m, "group": group(m),
                     "T1_A_s": r1["A_s"], "T1_B_s": r1["B_s"], "T1_total_s": tot1,
                     "T1_location_bias": metrics.location_bias(r1["A_s"], r1["B_s"]),
                     "T2_familiar_s": r2["familiar_s"], "T2_novel_s": r2["novel_s"], "T2_total_s": tot2,
                     "d2": metrics.discrimination_index(r2["novel_s"], r2["familiar_s"]),
                     "T2_novel_latency_s": r2["novel_latency_s"], "T2_familiar_latency_s": r2["familiar_latency_s"],
                     "T1_bouts": r1["A_bouts"] + r1["B_bouts"], "T2_bouts": r2["familiar_bouts"] + r2["novel_bouts"],
                     "T1_on_object_s": r1["A_on_object_s"] + r1["B_on_object_s"],
                     "T2_on_object_s": r2["familiar_on_object_s"] + r2["novel_on_object_s"],
                     "T1_distance_m": r1["distance_m"], "T2_distance_m": r2["distance_m"],
                     "exclusions": "; ".join(metrics.nor_exclusions(r1["A_s"], r1["B_s"], r2["familiar_s"], r2["novel_s"]))})
    with open(os.path.join(a.out_dir, f"nor_results_{a.model}.csv"), "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows([{k: round(v, 3) if isinstance(v, float) else v for k, v in r.items()} for r in rows])

    inc = [r for r in rows if not r["exclusions"]]
    lines = [f"NOR, HLBNSL, exploration from pose ({a.model}), SOP section 3 rule; NOT yet validated against hand scoring", "",
             "exclusions (SOP section 4): " + ("; ".join(f"{r['mouse']}: {r['exclusions']}" for r in rows if r["exclusions"]) or "none"), ""]
    for g in ("water", "SOD1"):
        d = [r["d2"] for r in inc if r["group"] == g and r["d2"] is not None]
        if len(d) >= 2:
            w = stats.wilcoxon(d, method="exact")
            lines.append(f"d2 {g}: n={len(d)} mean {st.mean(d):+.3f} ± {st.stdev(d) / len(d) ** .5:.3f} SEM, "
                         f"vs 0: Wilcoxon p={w.pvalue:.3f} (smallest possible {2 / 2 ** len(d):.3f})")
    lines.append("")
    for k in ("d2", "T1_total_s", "T2_total_s", "T1_location_bias", "T1_distance_m", "T2_distance_m"):
        s_ = [r[k] for r in inc if r["group"] == "SOD1" and r[k] is not None]
        w_ = [r[k] for r in inc if r["group"] == "water" and r[k] is not None]
        if len(s_) >= 2 and len(w_) >= 2:
            u = stats.mannwhitneyu(s_, w_, method="exact")
            lines.append(f"{k}: SOD1 {st.mean(s_):.3f} vs water {st.mean(w_):.3f}, Mann-Whitney U={u.statistic:.0f} p={u.pvalue:.3f}")
    # HLBNSL put the novel object where T1 object B stood (lower right) for every mouse: the novel side
    # was not counterbalanced, so compare each mouse's T2 novel share with its T1 share at that spot
    lines.append("")
    pairs = [(r["T1_B_s"] / r["T1_total_s"], r["T2_novel_s"] / r["T2_total_s"]) for r in inc
             if r["T1_total_s"] > 0 and r["T2_total_s"] > 0]
    w = stats.wilcoxon([b - a for a, b in pairs], method="exact")
    lines.append(f"side check (all included mice, n={len(pairs)}): lower-right share T1 {st.mean(p[0] for p in pairs):.3f} "
                 f"-> T2 (novel) {st.mean(p[1] for p in pairs):.3f}; paired Wilcoxon p={w.pvalue:.3f}; "
                 f"{sum(b > a for a, b in pairs)}/{len(pairs)} mice rose")
    for g in ("water", "SOD1"):
        gp = [(r["T1_B_s"] / r["T1_total_s"], r["T2_novel_s"] / r["T2_total_s"]) for r in inc if r["group"] == g]
        lines.append(f"  {g}: T1 {st.mean(p[0] for p in gp):.3f} -> T2 {st.mean(p[1] for p in gp):.3f}, "
                     f"{sum(b > a for a, b in gp)}/{len(gp)} rose")
    if a.oft:
        day1 = {r["mouse"]: float(r["distance_cm"]) / 100 for r in csv.DictReader(open(a.oft, newline=""))}
        lines.append("")
        for k in ("T1_total_s", "T2_total_s"):
            rho = stats.spearmanr([day1[r["mouse"]] for r in rows], [r[k] for r in rows])
            lines.append(f"day 1 distance vs {k} (all mice): Spearman rho={rho.statistic:+.2f} p={rho.pvalue:.3f}")
    txt = "\n".join(lines)
    open(os.path.join(a.out_dir, f"nor_stats_{a.model}.txt"), "w", encoding="utf-8").write(txt + "\n")
    print(txt)
    figures(rows, inc, a)


def figures(rows, inc, a):
    from ymaze_report import GCOL, GROUPS, panel, plt, style
    by = lambda k: {g: [r[k] for r in inc if r["group"] == g and r[k] is not None] for g in GROUPS}
    fig, ax = plt.subplots(1, 3, figsize=(11, 4.2), layout="constrained")
    panel(ax[0], by("d2"), "Discrimination index d2", -1, 1, chance=0)
    panel(ax[1], by("T1_total_s"), "T1 total exploration (s)", 0, None)
    panel(ax[2], by("T2_total_s"), "T2 total exploration (s)", 0, None)
    fig.suptitle(f"NOR, HLBNSL, pose {a.model} (provisional: not yet validated by hand scoring)",
                 x=0.01, ha="left", fontsize=12, color="0.1")
    for ext in ("png", "pdf"):
        fig.savefig(os.path.join(a.out_dir, f"nor_fig1_endpoints_{a.model}.{ext}"), dpi=300)
    plt.close(fig)

    fig, axx = plt.subplots(figsize=(5.5, 4.2), layout="constrained")
    day1 = {}
    if a.oft:
        for r in csv.DictReader(open(a.oft, newline="")):
            ul, lr = float(r["obj_UL_nose_within5cm_s"]), float(r["obj_LR_nose_within5cm_s"])
            day1[r["mouse"]] = lr / (ul + lr) if ul + lr > 0 else np.nan
    for r in inc:
        ys = [day1.get(r["mouse"], np.nan), r["T1_B_s"] / r["T1_total_s"], r["T2_novel_s"] / r["T2_total_s"]]
        axx.plot([0, 1, 2], ys, "-o", color=GCOL[r["group"]], alpha=0.75, ms=5, mec="white", lw=1.3)
    axx.axhline(0.5, color="0.45", ls="--", lw=1)
    axx.set_xticks([0, 1, 2], ["day 1\n(no objects)", "T1\n(object B)", "T2\n(novel)"])
    axx.set_xlim(-0.3, 2.3)
    axx.set_ylim(0, 1)
    axx.set_ylabel("Share at the lower-right spot", fontsize=9.5, color="0.2")
    axx.set_title("Lower-right spot = novel object in every T2", loc="left", fontsize=10.5, color="0.1")
    for g in GROUPS:
        axx.plot([], [], "-o", color=GCOL[g], label=g)
    axx.legend(frameon=False, fontsize=9)
    style(axx)
    for ext in ("png", "pdf"):
        fig.savefig(os.path.join(a.out_dir, f"nor_fig2_side_check_{a.model}.{ext}"), dpi=300)
    plt.close(fig)


def _selftest():
    sq = np.array([[20, 20], [23, 20], [23, 23], [20, 23]], float)      # 3 cm object, centre (21.5, 21.5)
    c = np.array([21.5, 21.5])
    assert np.allclose(outside_cm(np.array([[25.0, 21.5], [21.5, 21.5], [np.nan, np.nan]]), sq)[:2], [2.0, -1.5])
    nan2 = np.full((1, 2), np.nan)
    f = lambda nose, ear, body: exploring(np.array([nose], float), np.array([ear], float), np.array([body], float),
                                          [nan2, nan2], [nan2, nan2], sq, c)[0][0]
    assert f((24.5, 21.5), (27, 21.5), (30, 21.5))          # 1.5 cm away, facing it: explore
    assert not f((25.0, 21.5), (25.5, 19.0), (27, 15))      # 2 cm away, head pointing past it: passing by
    assert not f((26.0, 21.5), (28.5, 21.5), (32, 21.5))    # facing it but 3 cm away
    assert not f((22.0, 21.5), (24, 21.5), (21.5, 21.5))    # body on the object: sitting on it
    assert f((23.3, 23.0), (24.5, 20.0), (28, 18))          # touching the corner, head angled off-centre
    assert not f((18.0, 21.5), (21.5, 22.5), (26, 23))      # head over the object, nose 2 cm past it, pointing away: climbing
    assert merged_runs(np.array([1, 1, 0, 1, 0, 0, 0, 1], bool), 1) == [(0, 4), (7, 8)]
    print("nor_explore selftest ok")


if __name__ == "__main__":
    _selftest() if len(sys.argv) == 1 else main()
