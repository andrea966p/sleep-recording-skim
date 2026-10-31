#!/usr/bin/env python3
"""NS-SD / NW-SD cohort (HLBNSSD51-55 SOD1 vs HLBNWSD56-60 water), tag Run 1:
baseline vs SOD1 / water, with the same sleep, bout and rhythm analysis as the
HLBNSL batch (cohort.py, whose functions and figures are reused here).

    python3 nanotag/analysis/cohort_sd.py ~/Desktop/261030_HLBNSSD

Run 1 is one contiguous file per mouse (10-22 09:00 -> 10-30 08:59:48, 12 s
activity, no temperature). Each file is scored whole, then split at BASE_END
into baseline and treatment. Run 2 (10-30 19:00 -> 11-04, undisturbed window,
SD days, Y-maze) is not read yet. Writes to analysis/out/HLBNSSD/.
"""
import os, re, sys, statistics as st
from datetime import date, datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cohort as C
from nta_qc import parse, gaps, sleep_score

# --- cohort facts, from HLB_SOD1_Intake_Monitoring_SDSLNANO, NANOTAG registry +
# NANOTAG recordings + NANOTAG behavioral tabs, read 2026-10-31
C.SOD1 = {51, 52, 53, 54, 55}                # NS-SD: SOD1 6.8 U/mL in drinking water
C.WATER = {56, 57, 58, 59, 60}               # NW-SD: UV-sterilised water
C.SURGERY = {m: date(2026, 10, 12) for m in C.SOD1 | C.WATER}
C.TAG = {20639: 51, 20640: 52, 20641: 53, 20642: 54, 20643: 55,
         20644: 56, 20645: 57, 20646: 58, 20647: 59, 20648: 60}
C.NOTE = {59: "tag at the incision site (shoulder), not the flank",
          53: "sprayed urine over the cage 10-30"}
C.DROP, C.SHORT_BASELINE = set(), set()
# No handling or tests in Run 1 (behavioral tab: "No handling (SD batches: hand
# habituation not required)"); the 10-30 tag read is after Run 1 ended. Daily
# bottle weighing (both groups) is not removed, as in HLBNSL.
C.EXCLUDE = []
C.HANDLING_FROM, C.TEST_DAYS = date(2100, 1, 1), set()
# Baseline 10-22 09:00 -> 10-24 09:00 (recordings tab). Liquid monitoring Day 1 =
# 10-24; the clock time the bottles went in is not logged, so treatment is
# counted from the end of the logged baseline and the marker is drawn there.
BASE_END = datetime(2026, 10, 24, 9)
C.SOD1_START = (BASE_END, datetime(2026, 10, 24, 9, 30))
C.DAYS = "1–6"
C.SOD1_WHEN = "10-24, clock time not logged; marker at 09:00"
C.BASELINE_NOTE = "10-22 → 10-24, surgery day +10 to +12"
C.REMOVED_NOTE = "nothing removed: no handling or tests in Run 1"
C.REMOVED_SHORT = "nothing removed (no handling or tests in Run 1)"
C.OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out", "HLBNSSD")

def load(folder):
    """One file per mouse: score the whole contiguous series, then split it."""
    recs = []
    for f in sorted(x for x in os.listdir(folder) if x.endswith(".csv")):
        hdr, act, _ = parse(os.path.join(folder, f))
        mouse = C.TAG[int(hdr["nanotag ID"][-5:])]
        assert int(re.search(r"_(\d+)\.csv$", f).group(1)) == mouse, f"{f}: name vs tag ID"
        assert not gaps(act, hdr["act_res"]), f"{f}: activity gaps, sleep_score assumes none"
        scored = sleep_score(act, C.K)
        for period, keep in (("baseline", lambda t: t < BASE_END), ("treatment", lambda t: t >= BASE_END)):
            r = dict(mouse=mouse, group=C.group(mouse), period=period, files=[f], hdr=hdr, temp=[],
                     act=[x for x in act if keep(x[0])], scored=[x for x in scored if keep(x[0])])
            print(f"  {mouse} {period:9s} {r['act'][0][0]} -> {r['act'][-1][0]}  {len(r['act'])} bins")
            recs.append(r)
    return sorted(recs, key=lambda r: (r["period"], r["mouse"]))

def stat_line(rows, k, sel=lambda r: True):
    """baseline and treatment group means ± SEM, exact permutation p, change p"""
    line = f"  {k:26s}"
    for per in ("baseline", "treatment"):
        vs = {g: [s[k] for s in rows if s["group"] == g and s["period"] == per and sel(s)]
              for g in ("SOD1", "water")}
        for g, v in vs.items():
            line += f" {per[:4]} {g:5s} {st.mean(v):7.4g}±{st.stdev(v) / len(v) ** .5:<6.2g}"
        line += f" p={C.perm_p(vs['SOD1'], vs['water']):.2f} |"
    tl = {s["mouse"]: s[k] for s in rows if s["period"] == "treatment" and sel(s)}
    bl = {s["mouse"]: s[k] for s in rows if s["period"] == "baseline" and sel(s)}
    a = [tl[m] - bl[m] for m in sorted(C.SOD1) if m in tl]
    b = [tl[m] - bl[m] for m in sorted(C.WATER) if m in tl]
    return line + f" change SOD1 {st.mean(a):+7.3g} water {st.mean(b):+7.3g} p={C.perm_p(a, b):.3f}"

def main(folder):
    os.makedirs(C.OUT, exist_ok=True)
    recs = load(folder)
    print(f"loaded {len(recs)} recordings, {len({r['mouse'] for r in recs})} mice")
    days = [row for r in recs for row in C.daily_rows(r)]
    summ = C.summarise(recs, days)
    C.write("daily_sleep.csv", days)
    C.write("summary_per_mouse.csv", summ)

    keys = [k for k, _ in C.SLEEP_KEYS + C.RHYTHM_KEYS] + [
        "counts_per_h_light", "L5_start_ZT", "light_bouts_per_h", "dark_bouts_per_h",
        "total_sleep_k2_24s", "total_sleep_k3_36s", "total_sleep_k5_60s"]
    print(f"\nper-mouse means, IDS >= {C.K * 12}s; mean ± SEM, exact permutation p")
    for k in keys:
        print(stat_line(summ, k))
    # 59's tag sits over the shoulder: does the result hold without it?
    print("\nsensitivity: without 59 (tag not on the flank)")
    for k in ("total_sleep_min_per_day", "light_sleep_pct", "dark_sleep_pct", "counts_per_h_dark", "RA"):
        print(stat_line(summ, k, lambda s: s["mouse"] != 59))
    # bottle time on 10-24 is not logged: treatment without its first ZT day
    print("\nsensitivity: treatment days 2-6 only (ZT days 10-25 -> 10-29)")
    late = [d for d in days if d["period"] == "baseline" or d["zt_date"] >= "2026-10-25"]
    rows = [dict(mouse=m, group=C.group(m), period=per,
                 **{k: C.mean(d[k] for d in late if d["mouse"] == m and d["period"] == per)
                    for k in ("total_sleep_min", "light_sleep_pct", "dark_sleep_pct")})
            for m in C.mice() for per in ("baseline", "treatment")]
    for k in ("total_sleep_min", "light_sleep_pct", "dark_sleep_pct"):
        print(stat_line(rows, k))

    C.fig_actograms(recs)
    C.fig_daily(days)
    C.fig_zt(recs)
    C.fig_daily_mean(days)
    C.fig_groups(summ, C.COMPARE_SLEEP, "fig4_summary", "Sleep, SOD1 vs water")
    C.fig_groups(summ, C.COMPARE_RHYTHM, "fig6_rhythm", "Activity and daily rhythm, SOD1 vs water")
    C.fig_change(summ)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit(__doc__)
    main(sys.argv[1])
