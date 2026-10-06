#!/usr/bin/env python3
"""Did SOD1 change sleep? The four EEG/EMG batches as a 2x2 (SOD1 vs water x CSD vs ad lib), 2026-10-06.

Reads the stage-3 hypnograms of the analysis windows (the 2026-09-30 window re-check) and decides who is in from
the window cards (rung 3 PASS = official). Outcome: sleep % = (NREM+REM) / scored epochs inside contact blocks.
REM's share is fixed by construction, so only sleep vs wake is used. SOD1/water starts at tethering, so every
baseline is about a week ON treatment and before CSD.
Matched clock hours: the SD recoveries exist only 13:00 -> 09:00, so every change uses ZT4-24 (light ZT4-12,
dark ZT12-24). Tests: exact permutation of the difference in means, two-sided, every relabelling enumerated.

usage: python3 qc/sod_sleep_2x2_2026_10_06.py HYP_DIR [NOTCH_DIR]
  HYP_DIR   ~/eeg-processed-windows, or a copy holding <day>/*_hypnogram.csv and *_features.json
  NOTCH_DIR OUT/notch from qc/emg_mains_staging_test.py on the same day folders (sensitivity; NOT adopted)
"""
import csv, glob, json, os, sys
from itertools import combinations
import numpy as np
from scipy import optimize, stats

CARDS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "cards", "out-windows")
ARM = {"W-SD": ("water", "CSD"), "S-SD": ("SOD1", "CSD"), "W-SL": ("water", "ad lib"), "S-SL": ("SOD1", "ad lib")}
# Named on the 2026-09-30 window page: 31/35 recovery = rung 2 UNJUDGEABLE (the chip's floor carries signal) but
# stage 3 SCOREABLE; WSL23 baseline = r@1min 0.289 against the 0.30 bar.
SENS_ADD = {("S-SL", "R", "HLBSSL31"), ("S-SL", "R", "HLBSSL35"), ("W-SL", "B", "HLBWSL23")}
SEGS = {"24h": (0, 24), "ZT4-24": (4, 24), "L4-12": (4, 12), "D12-24": (12, 24), "L0-12": (0, 12)}


def sleep_pct(path):
    """{segment: (sleep %, scored hours)} plus wake % of every scored epoch (to check against features.json)."""
    with open(path) as fh:
        rows = [(float(r["zt_h"]), r["state"]) for r in csv.DictReader(fh)
                if r["in_block"] == "1" and r["state"] in ("WAKE", "NREM", "REM")]
    zt = np.array([z for z, _ in rows]); asleep = np.array([s != "WAKE" for _, s in rows])
    out = {}
    for k, (a, b) in SEGS.items():
        m = (zt >= a) & (zt < b)
        out[k] = (100 * asleep[m].mean() if m.sum() else np.nan, m.sum() * 4 / 3600)
    return out, 100 * (1 - asleep.mean())


def load(hyp_dir, notch_dir=None):
    recs = []
    for f in sorted(glob.glob(os.path.join(CARDS, "*", "*_card.json"))):
        c = json.load(open(f)); r = {x["number"]: x for x in c["rungs"]}
        hyp = (c["provenance"].get("processed_files") or {}).get("hypnogram")
        recs.append(dict(batch=c["cohort_id"], start=c["window"]["start_kst"], animal=c["animal_id"],
                         pos=c["position"], r2=r[2]["verdict"], r3=r[3]["verdict"], hyp=hyp))
    for b in ARM:  # the earlier window of each batch is its baseline
        first = min(x["start"] for x in recs if x["batch"] == b)
        for x in recs:
            if x["batch"] == b:
                x["tp"] = "B" if x["start"] == first else "R"
    out = []
    for x in recs:
        if not x["hyp"]:
            continue
        rel = os.path.join(os.path.basename(os.path.dirname(x["hyp"])), os.path.basename(x["hyp"]))
        src = os.path.join(notch_dir or hyp_dir, rel)
        feat = json.load(open(src.replace("_hypnogram.csv", "_features.json")))
        x["seg"], wake = sleep_pct(src)
        # reproduces stage 3 (a window with no contact block scores nothing and reports 0.0)
        assert np.isnan(wake) or abs(wake - feat["wake_pct"]) < 0.06, (src, wake, feat["wake_pct"])
        x["s3"], x["r1"] = feat["verdict"].split(":")[0], feat["persistence"]["1min"]["r"]
        key = (x["batch"], x["tp"], x["animal"])
        if notch_dir:  # the ladder only asks rung 3 of a rung 2 PASS
            x["official"] = x["r2"] == "PASS" and x["s3"] == "SCOREABLE"
            x["sens"] = x["official"] or (key in SENS_ADD and x["s3"] == "SCOREABLE")
        else:
            x["official"] = x["r3"] == "PASS"
            x["sens"] = x["official"] or key in SENS_ADD
        out.append(x)
    return out


def perm(a, b):
    """Exact two-sided permutation p for mean(a) - mean(b); also the smallest p these n can give."""
    pool, n = np.array(a + b, float), len(a)
    d = [pool[list(i)].mean() - np.delete(pool, i).mean() for i in combinations(range(len(pool)), n)]
    obs = np.mean(a) - np.mean(b)
    # equal n: the mirror relabelling is always as extreme, so the floor is 2/N; unequal n: 1/N
    return obs, np.mean(np.abs(d) >= abs(obs) - 1e-9), (2 if len(a) == len(b) else 1) / len(d)


def hedges_g(a, b):
    n1, n2 = len(a), len(b)
    if n1 < 2 or n2 < 2:
        return np.nan
    sp = np.sqrt(((n1 - 1) * np.var(a, ddof=1) + (n2 - 1) * np.var(b, ddof=1)) / (n1 + n2 - 2))
    return (np.mean(a) - np.mean(b)) / sp * (1 - 3 / (4 * (n1 + n2) - 9))


def mde_d(n1, n2, power=0.8, alpha=0.05):
    """Smallest Cohen's d a two-sample t-test detects with this power: a sensitivity analysis, not post-hoc power."""
    df, k = n1 + n2 - 2, np.sqrt(n1 * n2 / (n1 + n2)); tc = stats.t.ppf(1 - alpha / 2, df)
    # the lower tail is ~0 once d is large, and scipy's nct returns NaN there rather than 0
    f = lambda d: stats.nct.sf(tc, df, d * k) + np.nan_to_num(stats.nct.cdf(-tc, df, d * k)) - power
    return optimize.brentq(f, 0.01, 15) if f(15) > 0 else np.inf


def compare(label, a, b, la, lb):
    """a, b: {animal: value}."""
    va, vb = list(a.values()), list(b.values())
    s = f"  {label:<30} {la} n={len(va)} {np.mean(va) if va else np.nan:5.1f}  vs  {lb} n={len(vb)} " \
        f"{np.mean(vb) if vb else np.nan:5.1f}"
    if va and vb and len(va) + len(vb) > 2:
        obs, p, pmin = perm(va, vb); g = hedges_g(va, vb)
        s += f"  diff {obs:+5.1f} pts  p={p:.3f} (min possible {pmin:.2g})"
        if not np.isnan(g):
            sp = np.sqrt(((len(va) - 1) * np.var(va, ddof=1) + (len(vb) - 1) * np.var(vb, ddof=1))
                         / (len(va) + len(vb) - 2))
            ci = stats.ttest_ind(va, vb, equal_var=False).confidence_interval()
            md = mde_d(len(va), len(vb))
            s += f"  Welch 95% CI [{ci.low:+.1f}, {ci.high:+.1f}]  g={g:+.2f}  80%-power MDE d={md:.1f} = {md * sp:.0f} pts"
    elif va and vb:
        s += f"  diff {np.mean(va) - np.mean(vb):+5.1f} pts  (1 vs 1: no test)"
    else:
        s += "  NOT ESTIMABLE"
    print(s)


def report(recs, which, title):
    inc = [x for x in recs if x[which]]
    print(f"\n=== {title} ===")
    print("  per mouse, sleep % (scored h):  24h | ZT4-24 | light ZT4-12 | dark ZT12-24   [r@1min]")
    for x in sorted(inc, key=lambda x: (x["batch"], x["animal"], x["tp"])):
        sg = x["seg"]; f = lambda k: f"{sg[k][0]:5.1f} ({sg[k][1]:4.1f})"
        print(f"  {x['batch']} {x['tp']} {x['animal']} {x['pos']}  {f('24h')} | {f('ZT4-24')} | "
              f"{f('L4-12')} | {f('D12-24')}  [{x['r1']:.3f}]")

    def val(batch, tp, seg):
        return {x["animal"]: x["seg"][seg][0] for x in inc if x["batch"] == batch and x["tp"] == tp}

    def delta(batch, seg):
        b, r = val(batch, "B", seg), val(batch, "R", seg)
        return {k: r[k] - b[k] for k in b if k in r}

    print("  -- n per cell (B = baseline, on treatment, pre-CSD; R = recovery / endpoint; P = paired)")
    for b in ARM:
        print(f"     {b} {ARM[b][0]:>5} {ARM[b][1]:<6}  B={len(val(b, 'B', '24h'))}  R={len(val(b, 'R', '24h'))}"
              f"  P={len(delta(b, 'ZT4-24'))}  {sorted(delta(b, 'ZT4-24'))}")
    print("  -- 1. SOD1 vs water at BASELINE (~1 week of treatment, no CSD yet), all four batches")
    for seg, nm in (("24h", "sleep % 24 h"), ("L0-12", "sleep % light ZT0-12"), ("D12-24", "sleep % dark ZT12-24")):
        compare(nm, {**val("S-SL", "B", seg), **val("S-SD", "B", seg)},
                {**val("W-SL", "B", seg), **val("W-SD", "B", seg)}, "SOD1", "water")
    print("     same, ad lib batches only (no batch confound from W-SD)")
    compare("sleep % 24 h", val("S-SL", "B", "24h"), val("W-SL", "B", "24h"), "S-SL", "W-SL")
    print("  -- 2. SOD1 vs water at the ad lib ENDPOINT, ZT4-24 (S-SL R vs W-SL R)")
    for seg in ("ZT4-24", "L4-12", "D12-24"):
        compare(f"sleep % {seg}", val("S-SL", "R", seg), val("W-SL", "R", seg), "S-SL", "W-SL")
    print("  -- 3. CHANGE recovery - baseline, same clock hours (paired within mouse)")
    for seg in ("ZT4-24", "L4-12", "D12-24"):
        print(f"     {seg}: " + "   ".join(f"{b} " + ", ".join(f"{k} {v:+.1f}" for k, v in sorted(delta(b, seg).items()))
                                          for b in ARM if delta(b, seg)))
        compare(f"CSD effect, water  {seg}", delta("W-SD", seg), delta("W-SL", seg), "W-SD", "W-SL")
        compare(f"SOD1 effect, ad lib {seg}", delta("S-SL", seg), delta("W-SL", seg), "S-SL", "W-SL")
        compare(f"SOD1 effect, CSD   {seg}", delta("S-SD", seg), delta("W-SD", seg), "S-SD", "W-SD")
    print("  -- 4. recovery level after CSD, ZT4-24 (no baseline needed)")
    compare("sleep % ZT4-24", val("S-SD", "R", "ZT4-24"), val("W-SD", "R", "ZT4-24"), "S-SD", "W-SD")


def selfcheck():
    o, p, pmin = perm([1, 2, 3], [10, 11, 12])
    assert o == -9 and abs(p - 0.1) < 1e-9 and abs(pmin - 0.1) < 1e-9  # 3 vs 3: 20 relabellings, 2 as extreme
    assert abs(perm([5, 6], [5, 6])[1] - 1) < 1e-9
    assert abs(mde_d(10, 10) - 1.325) < 0.01  # G*Power: n = 10 per group, 80 %, alpha .05 two-sided


if __name__ == "__main__":
    selfcheck()
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    recs = load(os.path.expanduser(sys.argv[1]))
    report(recs, "official", "OFFICIAL: rung 3 PASS on the window cards")
    report(recs, "sens", "SENSITIVITY: + HLBSSL31/35 recovery (stage 3 only) + HLBWSL23 baseline (r 0.289)")
    if len(sys.argv) > 2:
        nrec = load(os.path.expanduser(sys.argv[1]), os.path.expanduser(sys.argv[2]))
        report(nrec, "official", "EMG NOTCHED (60/120 Hz, NOT adopted): rung 2 PASS + notched stage 3 SCOREABLE")
        report(nrec, "sens", "EMG NOTCHED + the same sensitivity additions")
    out = os.path.join(os.path.expanduser(sys.argv[1]), "sod_sleep_2x2_per_mouse.tsv")
    with open(out, "w") as fh:
        fh.write("staging\tbatch\ttreatment\tcondition\ttimepoint\tanimal\tposition\trung2\tstage3\tr1min\t"
                 "included\tincluded_sensitivity\t" + "\t".join(f"sleep_{k}\th_{k}" for k in SEGS) + "\n")
        for cond, rr in (("official", recs), ("emg_notched", nrec if len(sys.argv) > 2 else [])):
            for x in rr:
                fh.write("\t".join(map(str, [cond, x["batch"], *ARM[x["batch"]], x["tp"], x["animal"], x["pos"],
                                             x["r2"], x["s3"], x["r1"], int(x["official"]), int(x["sens"])]))
                         + "\t" + "\t".join(f"{x['seg'][k][0]:.2f}\t{x['seg'][k][1]:.2f}" for k in SEGS) + "\n")
    print(f"\nper-mouse table: {out}")
