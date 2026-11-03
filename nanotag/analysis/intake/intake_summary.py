"""Liquid intake, SOD1 dose and body weight, SOD1 vs water, per batch (never pooled).
Reads the CSV copies of the Google Sheet HLB_SOD1_Intake_Monitoring_SDSLNANO in data/ (one per tab, fetched read-only
2026-11-03) and writes the figure vault/_attachments/2026-11-03-hlb-intake-fig1-intake-weight.png.
Usage: ~/hlb-eeg-venv/bin/python intake_summary.py   (needs numpy matplotlib)

Intake = In - Out of each mouse's own bottle, 1 g = 1 mL, as in the sheet. Dose = mL x 6.8 U/mL (Config!C7).
Comparison: difference of the per-mouse means (mouse = unit), exact permutation p, 95 % CI by inverting that test."""
import csv, itertools, os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "data")
FIG = os.path.join(HERE, "..", "..", "..", "vault", "_attachments", "2026-11-03-hlb-intake-fig1-intake-weight.png")
CONC = 6.8                                   # U/mL, sheet Config
EXCLUDE = {"HLBNSSL43"}                      # died 2026-09-28, "all data discarded" in the sheet
# (water tab, SOD1 tab, label); each pair is its own comparison
PAIRS = [("W-SD", "S-SD", "EEG, sleep deprivation"), ("W-SL", "S-SL", "EEG, normal sleep"),
         ("NW-SL", "NS-SL", "Nanotag HLBNSL, normal sleep"), ("NW-SD", "NS-SD", "Nanotag, SD (running)")]
# TOTAL row of each tab in the sheet (mL per mouse, mice in column order): guards the CSV transcription
SHEET_TOTAL = {"W-SD": [44.4, 67.0, 64.4, 90.7, 30.0, 44.0, 69.4, 48.0, 48.7],
               "S-SD": [47.7, 51.4, 65.6, 62.8, 67.8, 49.2, 46.9, 49.6, 54.8],
               "W-SL": [57.9, 54.0, 67.6, 61.4, 59.9, 51.5, 55.5, 51.2, 70.0],
               "S-SL": [73.3, 64.6, 56.2, 63.8, 53.6, 58.8, 56.4, 64.7],
               "NS-SL": [59.1, 63.7, 33.8, 60.9, 54.6], "NW-SL": [62.9, 84.2, 85.4, 77.4, 72.2],
               "NS-SD": [26.8, 33.4, 29.7, 30.1, 45.4], "NW-SD": [32.3, 41.5, 60.3, 53.8, 45.8]}
WATER, SOD = "#555555", "#3f7f93"

def num(s): return float(s) if s != "" else None

def load_intake(tab):
    """-> {mouse: [(day, in, out)]} with None for a missing weight"""
    rows = list(csv.reader(open(os.path.join(DATA, tab + ".csv"))))
    mice = [h[:-3] for h in rows[0][2::2]]
    return {m: [(int(r[0]), num(r[2 + 2 * i]), num(r[3 + 2 * i])) for r in rows[1:]] for i, m in enumerate(mice)}

def days(rows):
    """full-day measurements: day, mL, bottle emptied (Out near the ~45 g tare), big bottle (In > 100 g)"""
    return [dict(day=d, ml=round(i - o, 1), empty=(o <= 47 and i < 100), big=i > 100) for d, i, o in rows if i and o]

def perm(a, b, d=0.0):
    """exact two-sided permutation p for mean(a) - mean(b) = d, by shifting a (Pitman); vectorised over splits"""
    v = np.r_[np.asarray(a) - d, b]; n, N = len(a), len(a) + len(b)
    idx = np.array(list(itertools.combinations(range(N), n)))
    ind = np.zeros((len(idx), N)); ind[np.arange(len(idx))[:, None], idx] = 1
    s = ind @ v; stat = s / n - (v.sum() - s) / (N - n)
    return float(np.mean(np.abs(stat) >= abs(v[:n].mean() - v[n:].mean()) - 1e-9))

def compare(a, b):
    """mean(a) - mean(b), exact p, 95 % CI = the shifts d the exact test does not reject (grid, 0.3 % of the range)"""
    d0 = np.mean(a) - np.mean(b); sc = (max(a + b) - min(a + b)) or 1
    ok = [d for d in np.linspace(d0 - 1.5 * sc, d0 + 1.5 * sc, 501) if perm(a, b, d) > 0.05]
    return d0, perm(a, b), min(ok), max(ok)

def selftest():
    assert abs(perm([1, 2], [3, 4]) - 1 / 3) < 1e-9 and perm([1, 2], [1, 2]) == 1
    for tab, tot in SHEET_TOTAL.items():
        got = [round(sum(x["ml"] for x in days(r)), 1) for r in load_intake(tab).values()]
        assert got == tot, (tab, got, tot)

def fmt_cmp(r): return f"{r[0]:+.2f} [{r[2]:+.2f}, {r[3]:+.2f}] p={r[1]:.3f}"

def main():
    selftest()
    per, bw = {}, {}                            # per[tab][mouse] = list of day dicts
    for w, s, _ in PAIRS:
        for t in (w, s):
            per[t] = {m: days(r) for m, r in load_intake(t).items() if m not in EXCLUDE}
    # ---- intake tables
    print("INTAKE per arm: mean +/- SD over mouse-days, min, n mouse-days (mice); dose = mL x 6.8; flags = days < 2 / > 6 mL, bottle emptied, big bottle")
    mm = {}                                     # mouse means (all days; steady = day >= 3 and <= 6 mL)
    for t, d in per.items():
        sod = t.startswith("S") or t.startswith("NS")
        allv = [x for r in d.values() for x in r]; ml = np.array([x["ml"] for x in allv])
        mm[t] = {"all": [np.mean([x["ml"] for x in r]) for r in d.values() if r],
                 "steady": [np.mean([x["ml"] for x in r if x["day"] >= 3 and x["ml"] <= 6]) for r in d.values() if r]}
        dose = f"{ml.mean() * CONC:.1f} +/- {ml.std(ddof=1) * CONC:.1f}" if sod else "-"
        print(f"{t:6s} {'SOD1' if sod else 'water':5s} {ml.mean():.2f} +/- {ml.std(ddof=1):.2f} min {ml.min():.1f} n={len(ml)} ({len(d)} mice) "
              f"dose {dose} U | low {int((ml < 2).sum())} high {int((ml > 6).sum())} empty {sum(x['empty'] for x in allv)} big {sum(x['big'] for x in allv)} "
              f"| exact 5.0: {int((ml == 5).sum())}")
        for m, r in d.items():
            print(f"    {m} n={len(r):2d} mean {np.mean([x['ml'] for x in r]):.2f} min {min(x['ml'] for x in r):.1f} max {max(x['ml'] for x in r):.1f}")
    # ---- bottle type: water arms moved to ~250-300 g bottles (In > 100 g) mid-batch; same mouse, small vs big bottle days
    for t in ("W-SL", "NW-SL", "NW-SD"):
        d0 = 3 if t == "W-SL" else 1
        for m, r in per[t].items():
            sm = [x["ml"] for x in r if not x["big"] and x["day"] >= d0]; bg = [x["ml"] for x in r if x["big"]]
            if len(sm) >= 3 and len(bg) >= 3:
                print(f"bottle check {m}: small {np.mean(sm):.2f} mL (n={len(sm)}), big {np.mean(bg):.2f} mL (n={len(bg)}), diff {np.mean(bg) - np.mean(sm):+.2f}")
    drift = [np.mean([x["ml"] for x in r if 13 <= x["day"] <= 16]) - np.mean([x["ml"] for x in r if 3 <= x["day"] <= 12]) for r in per["S-SL"].values()]
    print(f"time drift without a bottle change, S-SL days 13-16 minus 3-12: mean {np.mean(drift):+.2f} mL (n={len(drift)})")
    # ---- weekend 2-day bottles (NS-SD / NW-SD): In on the Saturday row, Out on the Sunday row
    for t in ("NS-SD", "NW-SD"):
        r = load_intake(t); v = []
        for m, rows in r.items():
            i8 = [i for d, i, o in rows if d == 8][0]; o9 = [o for d, i, o in rows if d == 9][0]; v.append((i8 - o9) / 2)
        print(f"{t} weekend bottle 10-31 -> 11-02, (In - Out)/2 per mouse: {[round(x, 1) for x in v]} mean {np.mean(v):.2f}")
    # ---- SOD1 vs water (SOD1 minus water) per batch pair
    print("\nSOD1 - WATER intake (mL/mouse/day), per-mouse means, exact permutation; all days | steady (day >= 3, <= 6 mL)")
    for w, s, lab in PAIRS:
        print(f"{lab:32s} n={len(mm[s]['all'])} vs {len(mm[w]['all'])}: all {fmt_cmp(compare(mm[s]['all'], mm[w]['all']))} | steady {fmt_cmp(compare(mm[s]['steady'], mm[w]['steady']))}")
    # ---- body weight: % change from tethering (EEG) or 6 d after surgery (nanotag, tag in both weights) to sampling
    print("\nBODY WEIGHT")
    for f, start in (("Sampling.csv", "bw_tether_g"), ("NANOTAG_sampling.csv", "bw_6d_post_g")):
        for r in csv.DictReader(open(os.path.join(DATA, f))):
            a, b = num(r[start]), num(r["bw_sampling_g"])
            if r["batch"] in per and a and b and r["mouse"] not in EXCLUDE:
                bw.setdefault(r["batch"], {})[r["mouse"]] = (a, b, 100 * (b - a) / a)
    for t, d in bw.items():
        v = list(d.values())
        print(f"{t:6s} n={len(v)} start {np.mean([x[0] for x in v]):.1f} -> sampling {np.mean([x[1] for x in v]):.1f} g, change {np.mean([x[2] for x in v]):+.1f} % (range {min(x[2] for x in v):+.1f} to {max(x[2] for x in v):+.1f})")
    for w, s, lab in PAIRS:
        if w in bw and s in bw:
            print(f"{lab:32s} change % SOD1 - water: {fmt_cmp(compare([x[2] for x in bw[s].values()], [x[2] for x in bw[w].values()]))}")
    # 6 d after surgery, tag removed, vs before surgery (nanotag; Config 2.7 g tag): all before treatment started
    for f in ("NANOTAG_sampling.csv",):
        for t in ("NS-SL", "NW-SL", "NS-SD", "NW-SD"):
            v = [100 * ((num(r["bw_6d_post_g"]) - 2.7) - num(r["bw_pre_g"])) / num(r["bw_pre_g"]) for r in csv.DictReader(open(os.path.join(DATA, f)))
                 if r["batch"] == t and r["mouse"] not in EXCLUDE]
            print(f"{t:6s} 6 d post-surgery vs pre-surgery (tag 2.7 g removed): mean {np.mean(v):+.1f} %, min {min(v):+.1f} %, n={len(v)}")
    figure(mm, bw)

def figure(mm, bw):
    plt.rcParams.update({"font.size": 13, "axes.spines.top": False, "axes.spines.right": False})
    fig, ax = plt.subplots(2, 4, figsize=(15, 7.5), facecolor="white")
    rng = np.random.default_rng(1)
    def panel(a, groups, ylab):
        for x, (v, c) in enumerate(groups):
            a.scatter(x + rng.uniform(-.13, .13, len(v)), v, s=42, color=c, alpha=.8, lw=0, zorder=3)
            a.hlines(np.mean(v), x - .3, x + .3, color="k", lw=2.5, zorder=4)
        a.set_xlim(-.6, 1.6); a.set_xticks([0, 1]); a.set_xticklabels(["water", "SOD1"])
        if ylab: a.set_ylabel(ylab)
    for j, (w, s, lab) in enumerate(PAIRS):
        a = ax[0, j]; panel(a, [(mm[w]["all"], WATER), (mm[s]["all"], SOD)], "mL per mouse per day" if j == 0 else "")
        a.axhline(3.0, color="#bbbbbb", ls="--", lw=1, zorder=1); a.set_ylim(0, 8.5); a.set_title(f"{lab}\n{w} / {s}", fontsize=12)
        b = ax[1, j]
        if w in bw and s in bw:
            panel(b, [([x[2] for x in bw[w].values()], WATER), ([x[2] for x in bw[s].values()], SOD)], "body weight change (%)" if j == 0 else "")
            b.axhline(0, color="#bbbbbb", lw=1, zorder=1); b.set_ylim(-11, 4)
        else:
            b.axis("off"); b.text(.5, .5, "not yet weighed\n(sampling 2026-11-04)", ha="center", va="center", transform=b.transAxes, color="#555555")
    fig.tight_layout(); fig.savefig(FIG, dpi=200); print("figure ->", os.path.normpath(FIG))

if __name__ == "__main__":
    main()
