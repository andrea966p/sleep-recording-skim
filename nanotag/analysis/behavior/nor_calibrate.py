#!/usr/bin/env python3
"""Calibrate the pose NOR scoring against blinded hand scoring, test it, and rerun the NOR analysis.

    python3 nor_calibrate.py <fit.boris> <test.boris> <NOR_blind_key.csv> <pose_dir> <out_dir> --unblind

<fit.boris> holds the clips the calibration is fitted on (rater 1), <test.boris> the held-out clips
(rater 2); <pose_dir> holds nor_bouts_model{1,2}.csv and nor_results_model{1,2}.csv from nor_explore.py.

What is calibrated, and what is not:
  - Hand timing is NOT the reference for timing: a key press can only come late. Each rater's lag is
    estimated (shift of the hand labels that maximises frame kappa against the model) and removed
    from the hand labels before any frame comparison. The model's timing is kept.
  - One gap is fitted: same-object bouts closer than it are joined AND the gap time is counted as
    exploration. This is an additive level correction (hand scorers bridge short pauses that the
    rule, frame by frame, does not count), NOT nor_explore.py MERGE_GAP_S: that one only groups bouts,
    its seconds stay the frames that pass the rule. Fitted on <fit.boris> by maximising ICC(A,1) of
    seconds per object, then tested on <test.boris>.
    Independent review 2026-11-02: the fitted gap is not stable (leave-one-clip-out moves it to the grid
    edge) and leaves a -4 s bias on the test rater; use it as a sensitivity analysis, not a validated
    setting. Rule-based seconds (gap 0.2 s) stay the published values.
Runs shorter than MIN_BOUT_S are absent from the bout files, so seconds at gap 0.2 s can differ from
nor_results by ~0.1 s per object.

Writes calibration.txt, nor_results_calibrated_model{1,2}.csv and nor_stats_calibrated_model{1,2}.txt.
Run with no arguments for the self-test.
"""
import argparse
import csv
import json
import os
import statistics as st
import sys

import numpy as np
from scipy import stats

import metrics
from nor_hand_vs_pose import FPS, OBJS, frames, hand_bouts, icc_a1, kappa

GAPS = [round(0.1 * i, 1) for i in range(2, 31)]        # 0.2 (current) to 3.0 s
MAX_LAG = 45                                              # frames, 1.5 s


def merge(bouts, gap):
    """Join consecutive bouts at the same object separated by at most `gap` s."""
    out = []
    for o, s, e in sorted(bouts, key=lambda b: b[1]):
        if out and out[-1][0] == o and s - out[-1][2] <= gap:
            out[-1] = (o, out[-1][1], max(e, out[-1][2]))
        else:
            out.append((o, s, e))
    return out


def unlag(lab, lag):
    """Move hand labels `lag` frames earlier (lag > 0: the hand pressed late)."""
    return np.concatenate([lab[lag:], np.zeros(lag, lab.dtype)]) if lag > 0 else lab


def load(boris, key, pose):
    """-> list of clips with hand bouts and both models' bouts."""
    clips = []
    for code, ob in sorted(json.load(open(boris))["observations"].items()):
        if ob["events"]:
            k = key[code]
            stem = k["clip"].removesuffix(".mp4")
            clips.append({"code": code, "trial": k["trial"].replace("NOR-", ""), "hand": hand_bouts(ob["events"]),
                          **{m: pose[m].get(stem, []) for m in (1, 2)}})
    return clips


def seconds(bouts, objs):
    return [sum(e - s for o, s, e in bouts if o == x) for x in objs]


def evaluate(clips, m, gap, lag):
    """-> dict of agreement measures for model m, merge gap, hand lag (frames)."""
    h, p, H, P = [], [], [], []
    for c in clips:
        objs, mb = OBJS[c["trial"]], merge(c[m], gap)
        h += seconds(c["hand"], objs)
        p += seconds(mb, objs)
        H.append(unlag(frames(c["hand"], objs), lag))
        P.append(frames(mb, objs))
    h, p = np.array(h), np.array(p)
    d = p - h
    return {"icc": icc_a1(h, p) if len(h) > 2 else float("nan"), "r": np.corrcoef(h, p)[0, 1] if len(h) > 2 else float("nan"),
            "bias": d.mean(), "mae": np.abs(d).mean(), "kappa": kappa(np.concatenate(H), np.concatenate(P))}


def best_lag(clips, m, gap):
    return max(range(0, MAX_LAG + 1), key=lambda L: evaluate(clips, m, gap, L)["kappa"])


def fmt(e):
    return (f"ICC(A,1) {e['icc']:.3f}, r {e['r']:+.3f}, bias {e['bias']:+.2f} s, MAE {e['mae']:.2f} s, "
            f"frame kappa {e['kappa']:.3f}")


def analysis(pose_dir, m, gap, out_dir):
    """Per-mouse NOR endpoints from merged bouts, and the statistics nor_explore.py reports."""
    res = {r["mouse"]: r for r in csv.DictReader(open(os.path.join(pose_dir, f"nor_results_model{m}.csv")))}
    b = {}
    for r in csv.DictReader(open(os.path.join(pose_dir, f"nor_bouts_model{m}.csv"))):
        b.setdefault((r["mouse"], r["trial"]), []).append((r["object"], float(r["start_s"]), float(r["end_s"])))
    rows = []
    for mouse in sorted(res):
        (a, bb), (f, n) = (seconds(merge(b.get((mouse, t), []), gap), OBJS[t]) for t in ("T1", "T2"))
        rows.append({"mouse": mouse, "group": res[mouse]["group"], "T1_A_s": a, "T1_B_s": bb, "T1_total_s": a + bb,
                     "T1_location_bias": metrics.location_bias(a, bb), "T2_familiar_s": f, "T2_novel_s": n,
                     "T2_total_s": f + n, "d2": metrics.discrimination_index(n, f),
                     "exclusions": "; ".join(metrics.nor_exclusions(a, bb, f, n))})
    with open(os.path.join(out_dir, f"nor_results_calibrated_model{m}.csv"), "w", newline="") as fh:
        w = csv.DictWriter(fh, list(rows[0]))
        w.writeheader()
        w.writerows([{k: round(v, 3) if isinstance(v, float) else v for k, v in r.items()} for r in rows])
    inc = [r for r in rows if not r["exclusions"]]
    L = [f"NOR, HLBNSL, pose model{m}, merge gap {gap} s (calibrated), revised forepaw rule (SOP 2026-11-02)", "",
         "exclusions (SOP section 4): " + ("; ".join(f"{r['mouse']}: {r['exclusions']}" for r in rows if r["exclusions"]) or "none"), ""]
    for g in ("water", "SOD1"):
        d = [r["d2"] for r in inc if r["group"] == g]
        w = stats.wilcoxon(d, method="exact")
        L.append(f"d2 {g}: n={len(d)} mean {st.mean(d):+.3f} ± {st.stdev(d) / len(d) ** .5:.3f} SEM, vs 0 Wilcoxon p={w.pvalue:.3f} "
                 f"(smallest possible {2 / 2 ** len(d):.3f})")
    for k in ("d2", "T1_total_s", "T2_total_s", "T1_location_bias"):
        s_, w_ = ([r[k] for r in inc if r["group"] == g] for g in ("SOD1", "water"))
        u = stats.mannwhitneyu(s_, w_, method="exact")
        L.append(f"{k}: SOD1 {st.mean(s_):.3f} vs water {st.mean(w_):.3f}, Mann-Whitney p={u.pvalue:.3f}")
    pairs = [(r["T1_B_s"] / r["T1_total_s"], r["T2_novel_s"] / r["T2_total_s"]) for r in inc]
    w = stats.wilcoxon([y - x for x, y in pairs], method="exact")
    L.append(f"side check (novel object at the lower-right spot in every T2), n={len(pairs)}: lower-right share T1 "
             f"{st.mean(p[0] for p in pairs):.3f} -> T2 {st.mean(p[1] for p in pairs):.3f}, paired Wilcoxon p={w.pvalue:.3f}, "
             f"{sum(y > x for x, y in pairs)}/{len(pairs)} rose")
    for g in ("water", "SOD1"):
        gp = [(r["T1_B_s"] / r["T1_total_s"], r["T2_novel_s"] / r["T2_total_s"]) for r in inc if r["group"] == g]
        L.append(f"  {g}: T1 {st.mean(p[0] for p in gp):.3f} -> T2 {st.mean(p[1] for p in gp):.3f}, {sum(y > x for x, y in gp)}/{len(gp)} rose")
    open(os.path.join(out_dir, f"nor_stats_calibrated_model{m}.txt"), "w").write("\n".join(L) + "\n")
    return L


def main(a):
    key = {r["code"]: r for r in csv.DictReader(open(a.key))}
    pose = {m: {} for m in (1, 2)}
    for m in (1, 2):
        for r in csv.DictReader(open(os.path.join(a.pose, f"nor_bouts_model{m}.csv"))):
            pose[m].setdefault(r["clip"], []).append((r["object"], float(r["start_s"]), float(r["end_s"])))
    fit, test = load(a.fit, key, pose), load(a.test, key, pose)
    assert fit and test and not {c["code"] for c in fit} & {c["code"] for c in test}, "fit and test clips must be disjoint"
    os.makedirs(a.out, exist_ok=True)
    out = [f"fit clips (rater 1): {', '.join(c['code'] for c in fit)}; test clips (rater 2): {', '.join(c['code'] for c in test)}", ""]
    chosen = {}
    for m in (1, 2):
        lag1, lag2 = best_lag(fit, m, 0.2), best_lag(test, m, 0.2)
        out.append(f"model{m}: hand lag rater 1 {lag1 / FPS:.2f} s, rater 2 {lag2 / FPS:.2f} s (removed from the hand labels)")
        grid = [(g, evaluate(fit, m, g, lag1)) for g in GAPS]
        g = max(grid, key=lambda x: (round(x[1]["icc"], 3), -x[0]))[0]
        chosen[m] = g
        for name, clips, lag in (("fit ", fit, lag1), ("test", test, lag2)):
            out.append(f"  {name} gap 0.2 s : {fmt(evaluate(clips, m, 0.2, lag))}")
            out.append(f"  {name} gap {g} s : {fmt(evaluate(clips, m, g, lag))}")
        out.append("  fit ICC by gap: " + ", ".join(f"{gg}:{e['icc']:.2f}" for gg, e in grid[::3]))
        out.append("")
    txt = "\n".join(out)
    open(os.path.join(a.out, "calibration.txt"), "w").write(txt + "\n")
    print(txt)
    for m in (1, 2):
        print("\n".join(analysis(a.pose, m, chosen[m], a.out)), "\n")


def selftest():
    b = [("A", 0.0, 1.0), ("A", 1.3, 2.0), ("B", 2.1, 2.5), ("A", 2.6, 3.0), ("A", 5.0, 6.0)]
    assert merge(b, 0.5) == [("A", 0.0, 2.0), ("B", 2.1, 2.5), ("A", 2.6, 3.0), ("A", 5.0, 6.0)], merge(b, 0.5)
    assert merge(b, 0.1) == sorted(b, key=lambda x: x[1])
    lab = np.array([0, 0, 1, 1, 0], np.int8)
    assert list(unlag(lab, 1)) == [0, 1, 1, 0, 0] and list(unlag(lab, 0)) == list(lab)
    assert np.allclose(seconds(b, ("A", "B")), [3.1, 0.4])
    print("self-test ok")


if __name__ == "__main__":
    if len(sys.argv) == 1:
        selftest()
        sys.exit()
    p = argparse.ArgumentParser()
    for n in ("fit", "test", "key", "pose", "out"):
        p.add_argument(n)
    p.add_argument("--unblind", action="store_true", help="required: the output names mice and groups")
    a = p.parse_args()
    if not a.unblind:
        sys.exit("refusing to run without --unblind: the output names mice and groups")
    main(a)
