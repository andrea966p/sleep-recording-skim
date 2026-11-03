#!/usr/bin/env python3
"""NS-SD / NW-SD cohort (HLBNSSD51-55 SOD1 vs HLBNWSD56-60 water), tag Run 1:
baseline vs SOD1 / water, with the same sleep, bout and rhythm analysis as the
HLBNSL batch (cohort.py, whose functions and figures are reused here).

    python3 nanotag/analysis/cohort_sd.py ~/Desktop/261030_HLBNSSD
    python3 nanotag/analysis/cohort_sd.py ~/Desktop/261030_HLBNSSD --run2 <Run 2 folder> [--vault]
    python3 nanotag/analysis/cohort_sd.py --demo

Run 1 is one contiguous file per mouse (10-22 09:00 -> 10-30 08:59:48, 12 s
activity, no temperature). Each file is scored whole, then split at BASE_END
into baseline and treatment. Writes to analysis/out/HLBNSSD/ ($NSSD_OUT overrides).

--run2 reads Run 2 (10-30 19:00 -> 11-04, one file per mouse) against the Run 1
baseline: undisturbed treatment days 8-10, SD efficacy, recovery after SD day 1
(windows in RUN2_PRE / SD / RECOVERY below). Writes to <out>/run2/; --vault also
copies its PNGs to vault/_attachments/ as VAULT_PREFIX + name.
"""
import argparse, csv, os, re, shutil, sys, statistics as st
from datetime import date, datetime, timedelta

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cohort as C
import numpy as np
from cohort import plt
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
C.OUT = os.environ.get("NSSD_OUT") or os.path.join(os.path.dirname(os.path.abspath(__file__)), "out", "HLBNSSD")
BASE_DAYS = (date(2026, 10, 22), date(2026, 10, 23))     # the two baseline ZT days

# --- Run 2, all times KST (2026-10-30 decision note + study note deviation).
# 🛑 The SD hours are the treatment: analysed, never removed as handling windows.
# Run 2 starts 10-30 19:00 (tag read 18:00-19:00); 10-30 09:00-19:00 is not
# recorded, light phase only, so nothing from 10-30 19:00 on is affected.
RUN2_PRE = (datetime(2026, 10, 31, 9), datetime(2026, 11, 3, 9))   # undisturbed, treatment days 8-10
SD = [("SD day 1", datetime(2026, 11, 3, 9), datetime(2026, 11, 3, 15)),
      ("SD day 2", datetime(2026, 11, 4, 9), datetime(2026, 11, 4, 15))]
# Only window between the two SD days. After SD day 2 the mice stay awake to
# their own Y-maze start, then Y-maze and sampling: no recovery sleep exists.
RECOVERY = [("ZT6-12", datetime(2026, 11, 3, 15), datetime(2026, 11, 3, 21)),
            ("dark", datetime(2026, 11, 3, 21), datetime(2026, 11, 4, 9))]
# Per-mouse Y-maze start (11-04, HH:MM, KST) = end of that mouse's SD and of its
# home-cage data. Missing -> data cut at the SD day 2 end, no wait window.
YMAZE_SHEET = os.path.join(os.path.dirname(os.path.abspath(__file__)), "behavior", "NSSD_ymaze_hand_scoring.csv")
VAULT_PREFIX = "2026-11-04-NSSD-run2-"
VAULT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "vault", "_attachments")

def read(path):
    """-> (mouse from the header tag ID, hdr, act, scored over the whole file)"""
    hdr, act, _ = parse(path)
    mouse = C.TAG[int(hdr["nanotag ID"][-5:])]
    assert not gaps(act, hdr["act_res"]), f"{path}: activity gaps, sleep_score assumes none"
    return mouse, hdr, act, sleep_score(act, C.K)

def load(folder):
    """One file per mouse: score the whole contiguous series, then split it."""
    recs = []
    for f in sorted(x for x in os.listdir(folder) if x.endswith(".csv")):
        mouse, hdr, act, scored = read(os.path.join(folder, f))
        assert int(re.search(r"_(\d+)\.csv$", f).group(1)) == mouse, f"{f}: name vs tag ID"
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

# ------------------------------------------------------------------ Run 2
NAN = float("nan")
SHOULDER = 59            # tag over the shoulder: dark counts ~2x, absolute values not comparable

def ymaze_starts(path=YMAZE_SHEET):
    """{mouse: Y-maze start on SD day 2} from the scoring sheet; blank cells skipped"""
    if not os.path.exists(path):
        return {}
    with open(path, newline="", encoding="utf-8-sig") as f:
        return {int(r["mouse"][-2:]): datetime.combine(SD[1][1].date(),
                                                         datetime.strptime(r["ymaze_start"].strip(), "%H:%M").time())
                for r in csv.DictReader(f) if r["ymaze_start"].strip()}

def load_run2(folder, starts):
    """{mouse: (hdr, act, scored)}, scored over the whole file, then cut at the
    mouse's Y-maze start (or the SD day 2 end): after it come the Y-maze, sampling
    and the post-mortem tail, none of it home cage."""
    out = {}
    for f in sorted(x for x in os.listdir(folder) if x.endswith(".csv")):
        mouse, hdr, act, scored = read(os.path.join(folder, f))
        if str(mouse) not in f:
            print(f"  WARNING {f}: name does not contain {mouse}; mouse taken from the tag ID")
        assert mouse not in out, f"{f}: a second Run 2 file for {mouse}"
        end = starts.get(mouse, SD[1][2])
        if act[0][0] > RUN2_PRE[0] or act[-1][0] < SD[1][2] - timedelta(seconds=hdr["act_res"]):
            print(f"  WARNING {mouse}: Run 2 does not cover {RUN2_PRE[0]:%m-%d %H:%M} -> {SD[1][2]:%m-%d %H:%M}")
        out[mouse] = (hdr, [x for x in act if x[0] < end], [x for x in scored if x[0] < end])
        print(f"  {mouse} run2      {act[0][0]} -> {act[-1][0]}  used to {end:%m-%d %H:%M}  {f}")
    return out

def pct(scored, spans):
    """% of the recorded bins inside the half-open spans [a, b) scored asleep"""
    sel = [s for t, s in scored if any(a <= t < b for a, b in spans)]
    return 100 * sum(sel) / len(sel) if sel else NAN

def at_baseline(a, b):
    """the same clock window on each baseline ZT day (a dark window crosses midnight)"""
    return [(a - (C.zt_day(a) - d), b - (C.zt_day(a) - d)) for d in BASE_DAYS]

def window_rows(base, run2, starts):
    """per mouse: SD efficacy and recovery against the same clock hours at baseline.
    Minutes = % x window length, so a short gap does not shrink them."""
    rows = []
    for m in C.mice():
        if m not in run2:
            print(f"  WARNING {m}: no Run 2 file, left out of the SD and recovery measures")
            continue
        bs, sc = base[m]["scored"], run2[m][2]
        r = dict(mouse=m, group=C.group(m))
        for i, (_, a, b) in enumerate(SD, 1):
            pb, ps = pct(bs, at_baseline(a, b)), pct(sc, [(a, b)])
            r[f"base_sd{i}_hours_pct"] = round(pb, 1)
            r[f"sd{i}_pct"] = round(ps, 1)
            r[f"sd{i}_change_pts"] = round(ps - pb, 1)
            r[f"sd{i}_sleep_lost_min"] = round((pb - ps) * (b - a).total_seconds() / 6000, 1)
        y = starts.get(m)
        r["ymaze_start"] = f"{y:%H:%M}" if y else ""
        r["sd2_real_h"] = round((y - SD[1][1]).total_seconds() / 3600, 2) if y else NAN
        r["wait_pct"] = round(pct(sc, [(SD[1][2], y)]), 1) if y else NAN    # 15:00 -> own Y-maze
        for lab, a, b in RECOVERY:
            mins = (b - a).total_seconds() / 60
            pb, pr = pct(bs, at_baseline(a, b)), pct(sc, [(a, b)])
            r[f"base_{lab}_min"] = round(pb * mins / 100, 1)
            r[f"rec_{lab}_min"] = round(pr * mins / 100, 1)
            r[f"rebound_{lab}_min"] = round((pr - pb) * mins / 100, 1)
            r[f"rebound_{lab}_pts"] = round(pr - pb, 1)
        r["rebound_total_min"] = round(sum(r[f"rebound_{lab}_min"] for lab, _, _ in RECOVERY), 1)
        r["note"] = C.NOTE.get(m, "")
        rows.append(r)
    return rows

def effect(rows, k, sel=lambda r: True, ci=True):
    """SOD1 and water values, SOD1 - water difference, exact-permutation 95% CI and p"""
    a = [r[k] for r in rows if r["group"] == "SOD1" and sel(r) and r[k] == r[k]]
    b = [r[k] for r in rows if r["group"] == "water" and sel(r) and r[k] == r[k]]
    d, lo, hi = C.perm_ci(a, b) if ci else (st.mean(a) - st.mean(b), NAN, NAN)
    return a, b, d, lo, hi, C.perm_p(a, b)

def eff_line(k, e):
    a, b, d, lo, hi, p = e
    ms = lambda v: f"{st.mean(v):7.1f} ± {st.stdev(v) / len(v) ** .5:4.1f} (n={len(v)})"
    ci = f" [{lo:+.1f}, {hi:+.1f}]" if lo == lo else ""
    return f"  {k:24s} SOD1 {ms(a)}  water {ms(b)}  SOD1 − water {d:+6.1f}{ci}  p={p:.3f}"

def paired_panel(ax, rows, keys, labels, title, ylim=(0, None)):
    """one thin line per mouse across conditions, thick = group mean ± SEM; hollow = 59"""
    x = np.arange(len(keys))
    for r in rows:
        g, dx = r["group"], -0.1 if r["group"] == "SOD1" else 0.1
        ax.plot(x + dx, [r[k] for k in keys], "-o", color=C.GCOL[g], alpha=0.4, lw=1, ms=5,
                mfc="white" if r["mouse"] == SHOULDER else C.GCOL[g])
    for g, dx in (("SOD1", -0.1), ("water", 0.1)):
        v = np.array([[r[k] for k in keys] for r in rows if r["group"] == g])
        ax.errorbar(x + dx, v.mean(0), v.std(0, ddof=1) / len(v) ** .5, color=C.GCOL[g], lw=2.5,
                    capsize=3, label=f"{g} (n = {len(v)})", zorder=4)
    ax.set_xticks(x, labels); ax.set_xlim(-0.5, len(keys) - 0.5); ax.set_ylim(*ylim)
    ax.set_title(title, loc="left", fontsize=10.5, color="0.1")
    ax.legend(frameon=False, fontsize=8.5)
    C.style(ax)

def effect_panel(ax, rows, eff, keys, labels, title):
    """per-mouse change (dots, mean tick), SOD1 - water with its 95% CI written above"""
    allv = [0]
    for i, k in enumerate(keys):
        a, b, d, lo, hi, p = eff[k]
        for g, dx in (("SOD1", -0.17), ("water", 0.17)):
            ms = [r["mouse"] for r in rows if r["group"] == g and r[k] == r[k]]
            v = [r[k] for r in rows if r["group"] == g and r[k] == r[k]]
            jit = (np.arange(len(v)) - (len(v) - 1) / 2) * 0.04
            for xx, yy, m in zip(i + dx + jit, v, ms):
                ax.plot(xx, yy, "o", color=C.GCOL[g], ms=6.5, mec=C.GCOL[g] if m == SHOULDER else "white",
                        mfc="white" if m == SHOULDER else C.GCOL[g], mew=1.3, zorder=3)
            ax.plot([i + dx - 0.12, i + dx + 0.12], [st.mean(v)] * 2, color=C.GCOL[g], lw=2.5)
            allv += v
        ax.text(i, 1.0, f"SOD1 − water {d:+.0f}\n95% CI [{lo:+.0f}, {hi:+.0f}]\np = {p:.2f}",
                ha="center", va="bottom", fontsize=8, color="0.2", transform=ax.get_xaxis_transform())
    ax.axhline(0, color="0.35", lw=1, zorder=1)
    span = max(allv) - min(allv) or 1
    ax.set_ylim(min(allv) - 0.1 * span, max(allv) + 0.1 * span)
    ax.set_xticks(range(len(keys)), labels); ax.set_xlim(-0.6, len(keys) - 0.4)
    ax.set_title(title, loc="left", fontsize=10.5, color="0.1", pad=44)
    C.style(ax)

def fig_sd(rows, eff):
    fig, ax = plt.subplots(1, 2, figsize=(12, 4.8), layout="constrained", gridspec_kw={"width_ratios": [1.3, 1]})
    paired_panel(ax[0], rows, ["base_sd1_hours_pct", "sd1_pct", "sd2_pct"],
                 ["Baseline\n09:00-15:00", "SD day 1\n11-03", "SD day 2\n11-04"],
                 "% of 09:00-15:00 asleep (immobility ≥ 48 s)", (0, 100))
    effect_panel(ax[1], rows, eff, ["sd1_change_pts", "sd2_change_pts"], ["SD day 1", "SD day 2"],
                 "Change from baseline (points)")
    fig.suptitle("SD efficacy, gentle handling 09:00-15:00, against the same mouse's baseline hours. "
                 f"Hollow = {SHOULDER} (tag at the shoulder: read its change, not its level)",
                 x=0.01, ha="left", fontsize=11, color="0.1")
    C.save(fig, "sd_efficacy")

def fig_recovery(rows, eff):
    labs = [lab for lab, _, _ in RECOVERY]
    fig, ax = plt.subplots(1, 3, figsize=(15, 4.8), layout="constrained")
    for i, (lab, a, b) in enumerate(RECOVERY):
        paired_panel(ax[i], rows, [f"base_{lab}_min", f"rec_{lab}_min"],
                     ["Baseline", f"After SD day 1\n{a:%m-%d %H:%M}-{b:%H:%M}"],
                     f"{lab}: minutes asleep of {(b - a).total_seconds() / 60:.0f}")
    effect_panel(ax[2], rows, eff, [f"rebound_{lab}_min" for lab in labs] + ["rebound_total_min"],
                 labs + ["total"], "Rebound = recovery − baseline (min)")
    fig.suptitle("Recovery after SD day 1 (the only window between the SD days; none exists after SD day 2). "
                 f"Hollow = {SHOULDER}", x=0.01, ha="left", fontsize=11, color="0.1")
    C.save(fig, "recovery")

# stems in <out>/run2/ -> vault/_attachments/VAULT_PREFIX + name + ".png"
VAULT_FIGS = {"sd_efficacy": "sd-efficacy", "recovery": "recovery", "fig2b_daily_sleep_mean": "daily-sleep",
              "fig7_change": "change-days-8-10", "fig3_zt_profile": "zt-profile-days-8-10",
              "fig1_actograms": "actograms"}

def run2(folder1, folder2, vault=False, sheet=YMAZE_SHEET):
    starts = ymaze_starts(sheet)
    print(f"Y-maze start times in {sheet}: {len(starts)} of 10")
    recs1 = load(folder1)
    r2 = load_run2(folder2, starts)
    C.OUT = os.path.join(C.OUT, "run2")
    os.makedirs(C.OUT, exist_ok=True)
    C.DAYS = "8–10 (Run 2, 10-31 → 11-02)"
    C.REMOVED_NOTE = ("nothing removed; SD 11-03 and 11-04 09:00-15:00 kept (the SD is the treatment); "
                      "10-30 09:00-19:00 not recorded; data end at each mouse's Y-maze start")
    C.REMOVED_SHORT = "nothing removed"
    base = {r["mouse"]: r for r in recs1 if r["period"] == "baseline"}
    inpre = lambda x: RUN2_PRE[0] <= x[0] < RUN2_PRE[1]
    pre = [dict(mouse=m, group=C.group(m), period="treatment", files=["run2"], hdr=h, temp=[],
                act=[x for x in act if inpre(x)], scored=[x for x in sc if inpre(x)])
           for m, (h, act, sc) in sorted(r2.items())]
    days = [row for r in list(base.values()) + pre for row in C.daily_rows(r)]
    summ = C.summarise(list(base.values()) + pre, days)
    C.write("daily_sleep_days_8_10.csv", days)
    C.write("summary_days_8_10.csv", summ)

    print(f"\n1. Undisturbed treatment days 8-10 ({RUN2_PRE[0]:%m-%d %H:%M} -> {RUN2_PRE[1]:%m-%d %H:%M}) "
          "vs baseline; mean ± SEM, exact permutation p")
    keys = ("total_sleep_min_per_day", "light_sleep_pct", "dark_sleep_pct", "counts_per_h_dark",
            "counts_per_h_light", "light_bout_mean_min", "dark_bout_mean_min", "RA")
    for k in keys:
        print(stat_line(summ, k))
    print(f"   without {SHOULDER}")
    for k in keys[:4]:
        print(stat_line(summ, k, lambda s: s["mouse"] != SHOULDER))

    rows = window_rows(base, r2, starts)
    C.write("sd_and_recovery_per_mouse.csv", rows)
    change = ["sd1_change_pts", "sd2_change_pts", "sd1_sleep_lost_min", "sd2_sleep_lost_min",
              "rebound_ZT6-12_min", "rebound_dark_min", "rebound_total_min"]
    eff = {k: effect(rows, k) for k in change}
    print("\n2. SD efficacy, % of 09:00-15:00 asleep vs the same hours at baseline (10-22, 10-23)")
    for k in ("base_sd1_hours_pct", "sd1_pct", "sd2_pct"):
        print(eff_line(k, effect(rows, k, ci=False)))
    for k in change[:4]:
        print(eff_line(k, eff[k]))
    for i in (1, 2):
        for g in ("SOD1", "water"):
            v = [r[f"sd{i}_change_pts"] for r in rows if r["group"] == g]
            print(f"  SD day {i} {g:5s}: {sum(x < 0 for x in v)} of {len(v)} mice slept less than at baseline")
    if starts:
        print("  wait 15:00 -> own Y-maze start (still SD):")
        for k in ("sd2_real_h", "wait_pct"):
            print(eff_line(k, effect(rows, k, ci=False)))
    else:
        print("  no Y-maze start times: SD day 2 analysed to 15:00 only, no wait window")
    print("\n3. Recovery after SD day 1, vs the same clock hours at baseline")
    for lab, _, _ in RECOVERY:
        for k in (f"base_{lab}_min", f"rec_{lab}_min", f"rebound_{lab}_pts"):
            print(eff_line(k, effect(rows, k, ci=False)))
    for k in change[4:]:
        print(eff_line(k, eff[k]))
    print(f"\n   without {SHOULDER}")
    for k in change:
        print(eff_line(k, effect(rows, k, lambda r: r["mouse"] != SHOULDER, ci=False)))
    print("\n4. Sleep after SD day 2 is not available: each mouse went from SD to its Y-maze and to "
          "sampling; tag data after the Y-maze start are not home cage and are cut.")

    days1 = [row for r in recs1 for row in C.daily_rows(r)]
    C.fig_actograms(recs1 + [dict(mouse=m, act=act) for m, (_, act, _) in r2.items()])
    C.fig_daily_mean(days1 + [d for d in days if d["period"] == "treatment"])
    C.fig_zt(list(base.values()) + pre)
    C.fig_change(summ)
    fig_sd(rows, eff)
    fig_recovery(rows, eff)
    if vault:
        for stem, name in VAULT_FIGS.items():
            dst = os.path.join(VAULT, f"{VAULT_PREFIX}{name}.png")
            shutil.copy(f"{C.OUT}/{stem}.png", dst)
            print(f"  copied {os.path.normpath(dst)}")

def demo():
    """self-check of the Run 2 window slicing"""
    a, b = SD[0][1:]
    assert at_baseline(a, b) == [(datetime(2026, 10, 22, 9), datetime(2026, 10, 22, 15)),
                                 (datetime(2026, 10, 23, 9), datetime(2026, 10, 23, 15))]
    dark = at_baseline(*RECOVERY[1][1:])                      # crosses midnight, stays in baseline
    assert dark == [(datetime(2026, 10, 22, 21), datetime(2026, 10, 23, 9)),
                    (datetime(2026, 10, 23, 21), datetime(2026, 10, 24, 9))] and dark[-1][1] <= BASE_END
    step = timedelta(seconds=12)
    span = lambda t0, t1: [t0 + step * i for i in range(int((t1 - t0) / step))]
    # baseline: asleep exactly 09:00-15:00 -> the half-open windows see 100 % and 0 %
    bs = [(t, 9 <= t.hour < 15) for t in span(datetime(2026, 10, 22, 9), BASE_END)]
    assert pct(bs, at_baseline(a, b)) == 100 and pct(bs, at_baseline(*RECOVERY[0][1:])) == 0
    # Run 2: SD day 1 every 4th bin asleep (25 %), ZT6-12 after it all asleep, SD day 2 awake;
    # Y-maze at 15:30 on 11-04 -> wait window 15:00-15:30
    t1 = datetime(2026, 11, 3, 9)
    sc = [(t, (i % 4 == 0) if t < t1 + timedelta(hours=6) else t < t1 + timedelta(hours=12))
          for i, t in enumerate(span(t1, datetime(2026, 11, 4, 15, 30)))]
    y = {51: datetime(2026, 11, 4, 15, 30)}
    r = window_rows({m: dict(scored=bs) for m in C.mice()}, {m: (None, None, sc) for m in C.mice()}, y)[0]
    assert (r["sd1_pct"], r["sd1_change_pts"], r["sd1_sleep_lost_min"]) == (25, -75, 270), r
    assert r["sd2_pct"] == 0 and r["sd2_real_h"] == 6.5 and r["wait_pct"] == 0, r
    assert r["rebound_ZT6-12_min"] == 360 and r["rebound_dark_min"] == 0, r
    import tempfile
    with tempfile.NamedTemporaryFile("w", suffix=".csv", delete=False) as f:
        f.write("test_order,mouse,group,ymaze_start\n1,HLBNSSD51,SOD1,15:04\n2,HLBNWSD56,water,\n")
    assert ymaze_starts(f.name) == {51: datetime(2026, 11, 4, 15, 4)}
    os.unlink(f.name)
    print("demo ok")

if __name__ == "__main__":
    pa = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    pa.add_argument("run1", nargs="?", help="Run 1 folder (one CSV per mouse)")
    pa.add_argument("--run2", help="Run 2 folder (one CSV per mouse)")
    pa.add_argument("--ymaze", default=YMAZE_SHEET, help="Y-maze sheet with each mouse's start time")
    pa.add_argument("--vault", action="store_true", help="copy the Run 2 PNGs to vault/_attachments")
    pa.add_argument("--demo", action="store_true", help="self-check of the Run 2 window slicing")
    a = pa.parse_args()
    if a.demo:
        demo()
    elif not a.run1:
        pa.error("give the Run 1 folder")
    elif a.run2:
        run2(a.run1, a.run2, a.vault, a.ymaze)
    else:
        main(a.run1)
