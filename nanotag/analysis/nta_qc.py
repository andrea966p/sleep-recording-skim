#!/usr/bin/env python3
"""QC + rebin for nanotagViewer .nta CSV exports. stdlib only."""
import csv, re, sys, statistics as st
from datetime import datetime, timedelta

FMT = "%Y/%m/%d %H:%M:%S"

# Implant site: subcutaneous, entered at the neck and pushed caudally onto the
# back. Both animals' tags migrated to the RIGHT dorsolateral flank during
# recovery. Kissei's validated thresholds cover neck (170) and abdomen (150)
# only -- this site is neither, and 170 was written to both tags. Counts are
# therefore relative units, valid within this study only. Both tags share site,
# side and threshold, so between-animal comparison holds.
#
# Light schedule: lights on 09:00, off 21:00 (confirmed by user 2026-09-09)
LIGHTS_ON, LIGHTS_OFF = 9, 21

# Drop the opening window: handling + post-surgical. Measured at ~7-10x the rest
# of the light phase over the first 30 min, decayed by ~60 min. --skip N to change.
SKIP_FIRST_MIN = 60

def is_light(ts):
    return LIGHTS_ON <= ts.hour < LIGHTS_OFF

def parse(path):
    """-> (header dict, [(ts, count)], [(ts, temp)])"""
    with open(path, newline="", encoding="utf-8-sig") as f:
        rows = list(csv.reader(f))
    hdr = {"act_res": int(rows[0][2]), "temp_res": int(rows[0][5])}
    for kv in re.split(r"/(?=[A-Za-z][^:/]*:)", rows[1][1]):
        if ":" in kv:
            k, v = kv.split(":", 1)
            hdr[k.strip()] = v.strip()
    # find the data header row rather than assuming row 4
    i = next(i for i, r in enumerate(rows) if r and r[0] == "Date")
    if "Cross count(Integral)" in rows[i]:
        raise SystemExit(f"{path}: summarized export, not raw — column layout differs")
    act, temp = [], []
    hdr["temp_oor"] = 0
    for r in rows[i + 1:]:
        if not r or not r[0]:
            continue
        ts = datetime.strptime(r[0], FMT)
        if r[1].strip():
            act.append((ts, int(r[1])))
        if r[2].strip() == "Out of range":    # outside the tag's 30-45.8 degC window, e.g.
            hdr["temp_oor"] += 1              # a carcass cooling after sampling: no value
        elif r[2].strip():
            temp.append((ts, float(r[2])))
    return hdr, act, temp

def gaps(series, res):
    step = timedelta(seconds=res)
    return [(a[0], b[0]) for a, b in zip(series, series[1:]) if b[0] - a[0] != step]

def rebin(act, res, minutes):
    """Sum cross counts into `minutes` bins. Only emits complete bins."""
    width = timedelta(minutes=minutes)
    need = int(minutes * 60 / res)
    out, bucket, edge = [], [], None
    for ts, c in act:
        e = ts - timedelta(seconds=ts.timestamp() % width.total_seconds())
        if edge is None:
            edge = e
        if e != edge:
            out.append((edge, sum(bucket), len(bucket) == need))
            bucket, edge = [], e
        bucket.append(c)
    out.append((edge, sum(bucket), len(bucket) == need))
    return out

def report(path):
    hdr, act, temp = parse(path)
    if SKIP_FIRST_MIN:
        cut = act[0][0] + timedelta(minutes=SKIP_FIRST_MIN)
        act = [(t, c) for t, c in act if t >= cut]
        temp = [(t, v) for t, v in temp if t >= cut]
        print(f"\n  [dropped first {SKIP_FIRST_MIN} min: handling/post-surgical]", end="")
    print(f"\n=== {path.split('/')[-1]} ===")
    print(f"  tag ID        {hdr.get('nanotag ID')}")
    print(f"  resolution    activity {hdr['act_res']}s / temperature {hdr['temp_res']}s")
    print(f"  thresholds    upper {hdr.get('Upper threshhold')} lower {hdr.get('Lower threshhold')}")
    print(f"  temp range    {hdr.get('Temperature range (degC)')}")
    print(f"  hdr starts    act {hdr.get('Start date_Activity')} | temp {hdr.get('Start date_Temparature')}")
    print(f"  activity      n={len(act)}  {act[0][0]} -> {act[-1][0]}"
          f"  ({(act[-1][0]-act[0][0]).total_seconds()/3600:.2f} h)")
    print(f"  temperature   n={len(temp)} {temp[0][0]} -> {temp[-1][0]}")

    ga, gt = gaps(act, hdr["act_res"]), gaps(temp, hdr["temp_res"])
    print(f"  gaps          activity {len(ga)}, temperature {len(gt)}")
    for a, b in (ga + gt)[:5]:
        print(f"                {a} -> {b}")

    counts = [c for _, c in act]
    zeros = sum(c == 0 for c in counts)
    print(f"  cross count   mean {st.mean(counts):.2f} median {st.median(counts)} "
          f"max {max(counts)} zeros {zeros}/{len(counts)} ({100*zeros/len(counts):.1f}%)")
    temps = [t for _, t in temp]
    oor = [t for t in temps if not 10 <= t <= 45]
    print(f"  temperature   min {min(temps):.3f} mean {st.mean(temps):.3f} max {max(temps):.3f} "
          f"out-of-range {len(oor)}")

    for label, sel in ((f"light {LIGHTS_ON:02d}-{LIGHTS_OFF:02d}",
                        [c for ts, c in act if is_light(ts)]),
                       (f"dark  {LIGHTS_OFF:02d}-{LIGHTS_ON:02d}",
                        [c for ts, c in act if not is_light(ts)])):
        print(f"  {label}   mean/12s {st.mean(sel):.2f} sum {sum(sel)}  n={len(sel)}")
    for label, sel in (("light", [t for ts, t in temp if is_light(ts)]),
                       ("dark ", [t for ts, t in temp if not is_light(ts)])):
        print(f"  {label} temp     mean {st.mean(sel):.3f} degC  n={len(sel)}")
    # Epoch-intensity classes: the standard way to handle these zero-inflated
    # counts in the literature (Sci Rep 2024, 10.1038/s41598-024-67024-7 -- rat,
    # 5 min bins, cut points 150/300). Cut points are BORROWED FROM THAT RAT
    # STUDY; set them from your own distribution before publishing.
    five = [(t, v) for t, v, ok in rebin(act, hdr["act_res"], 5) if ok]
    print("  5-min epoch intensity  immobile / mild / moderate / high:")
    for lab, sel in (("light", [v for t, v in five if is_light(t)]),
                     ("dark ", [v for t, v in five if not is_light(t)])):
        q = [0, 0, 0, 0]
        for v in sel:
            q[0 if v == 0 else 1 if v <= 150 else 2 if v <= 300 else 3] += 1
        print(f"    {lab} n={len(sel):3d}  " + "  ".join(f"{100*x/len(sel):5.1f}%" for x in q))

    # Counting is Nyquist-limited: vector wave is sampled at a fixed 25 Hz (p46),
    # so a bin cannot hold more than 12.5 upward crossings per second.
    peak = max(v for _, v in act)
    print(f"  saturation    peak {peak} / ceiling {int(12.5*hdr['act_res'])} "
          f"= {100*peak/(12.5*hdr['act_res']):.1f}% of the 25 Hz limit")

    print("  hourly mean cross count / 12 s bin:")
    for h in range(24):
        sel = [c for ts, c in act if ts.hour == h]
        if sel:
            m = st.mean(sel)
            mark = "L" if is_light(datetime(2026, 1, 1, h)) else "D"
            print(f"    {h:02d}:00 {mark} {m:6.2f} {'#' * round(m * 2)}")
    return hdr, act, temp

def write_rebinned(path, act, res, minutes):
    out = path.rsplit(".", 1)[0] + f"_act_{minutes}min.csv"
    with open(out, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["bin_start", "cross_count_sum", "complete"])
        w.writerows([(t.strftime(FMT), s, int(ok)) for t, s, ok in rebin(act, res, minutes)])
    print(f"  wrote {out}")

# --- Immobility-defined sleep (IDS) ---------------------------------------
# Pack et al. 2006, Physiol Genomics 28:232-8 (10.1152/physiolgenomics.00139.2006):
# any run of continuous inactivity >= 40 s is scored sleep. 92% epoch-by-epoch
# agreement with simultaneous EEG/EMG in C57BL/6J (10-s epochs, 24 h, n=7).
# That validation used video, not an implanted accelerometer; no nanotag-vs-EEG
# validation exists yet. Nagai et al. 2020 (Sci Rep 10:19800, nanotag, 12 s)
# used >= 2 empty bins (24 s) instead; cohort.py reports that cutoff as well.
# 40 s is not a multiple of our 12 s bin: 4 bins = 48 s (conservative, under-
# calls sleep), 3 bins = 36 s (liberal). --k N to change; sensitivity printed.
#
# A bin counts as immobile iff cross count == 0, i.e. nothing crossed the
# threshold baked into the tag (170). A higher threshold therefore INFLATES
# scored sleep -- quiet wake reads as immobile. This is the main validity limit
# here, and it cannot be re-derived from .nta (see threshold note above).
SLEEP_MIN_BINS = 4

def sleep_score(act, k):
    """-> [(ts, asleep)]. Zero-count runs of >= k consecutive bins are sleep.
    Assumes act is gap-free and contiguous -- report() prints the gap count."""
    out, i = [], 0
    while i < len(act):
        j = i
        while j < len(act) and act[j][1] == 0:
            j += 1
        if j > i:                                    # zero run [i, j)
            asleep = (j - i) >= k
            out += [(t, asleep) for t, _ in act[i:j]]
            i = j
        else:
            out.append((act[i][0], False))
            i += 1
    return out

def bouts(scored, state):
    """-> [(start_ts, n_bins)] maximal runs of `state`.
    ponytail: bouts spanning a light/dark boundary get split by the phase
    filter in sleep_report. 3 transitions in this recording, so <=3 bouts
    affected; carry the pre-split series if bout-length stats become primary."""
    out, i = [], 0
    while i < len(scored):
        if scored[i][1] != state:
            i += 1
            continue
        j = i
        while j < len(scored) and scored[j][1] == state:
            j += 1
        out.append((scored[i][0], j - i))
        i = j
    return out

def merge_wake(scored, w):
    """Bridge wake runs of <= w bins that sit BETWEEN two sleep bouts, then
    re-score them as sleep. w=0 is the pure Pack criterion. Needed because a
    body-mounted sensor at 12 s resolution breaks a sleep bout on any single
    postural twitch: raw median wake bout here is one bin."""
    if not w:
        return scored
    out = [list(x) for x in scored]
    idx = {x[0]: j for j, x in enumerate(scored)}
    for start, n in bouts(scored, False):
        i = idx[start]
        if n <= w and i > 0 and i + n < len(out):        # flanked by sleep
            for j in range(i, i + n):
                out[j][1] = True
    return [tuple(x) for x in out]

def sleep_report(act, temp, res, k, hourly=True):
    scored = sleep_score(act, k)
    m = res / 60.0
    print(f"  --- sleep (IDS, immobility >= {k} bins = {k*res}s) ---")
    for lab, keep in (("light", True), ("dark ", False)):
        sel = [(t, s) for t, s in scored if is_light(t) == keep]
        tst = sum(s for _, s in sel)
        b = [n for _, n in bouts(sel, True)]
        w = [n for _, n in bouts(sel, False)]
        print(f"    {lab} {100*tst/len(sel):5.1f}% asleep   "
              f"{tst*m:6.1f} of {len(sel)*m:6.1f} min recorded")
        if b:
            print(f"          sleep bouts {len(b):4d}  mean {st.mean(b)*m:5.2f}"
                  f"  median {st.median(b)*m:5.2f}  max {max(b)*m:6.2f} min"
                  f"   {60*len(b)/(tst*m):5.2f}/h asleep")
            print(f"          wake  bouts {len(w):4d}  mean {st.mean(w)*m:5.2f}"
                  f"  median {st.median(w)*m:5.2f}  max {max(w)*m:6.2f} min")
    # Does the temperature channel see sleep at all? (rat study 10.1038/s41598-024-67024-7
    # called nano tag temperature too subtle and blamed implant location)
    smap = dict(scored)
    ts_ = [(v, smap[t]) for t, v in temp if t in smap]
    for lab, keep in (("asleep", True), ("awake ", False)):
        sel = [v for v, s in ts_ if s == keep]
        if sel:
            print(f"    temp while {lab}  mean {st.mean(sel):.3f} degC  n={len(sel)}")
    if hourly:
        print("    hourly % asleep:")
        for h in range(24):
            sel = [s for t, s in scored if t.hour == h]
            if sel:
                p = 100 * sum(sel) / len(sel)
                mark = "L" if is_light(datetime(2026, 1, 1, h)) else "D"
                print(f"      {h:02d}:00 {mark} {p:5.1f}% {'#' * round(p / 3)}")
    print("    bout merging (bridge wake gaps <= w bins) -- sleep bouts light / dark:")
    for w in (0, 1, 2, 5):
        row = []
        for keep in (True, False):
            sel = [(t, s) for t, s in merge_wake(scored, w) if is_light(t) == keep]
            b = [n for _, n in bouts(sel, True)]
            row.append(f"n={len(b):4d} mean {st.mean(b)*m:5.2f} max {max(b)*m:6.2f}min"
                       f" tst {100*sum(s for _, s in sel)/len(sel):4.1f}%")
        print(f"      w={w} ({w*res:2d}s)  " + "   |   ".join(row))
    print("    criterion sensitivity (% asleep light / dark):")
    for kk in (2, 3, 4, 5, 10):
        s2 = sleep_score(act, kk)
        li = [s for t, s in s2 if is_light(t)]
        da = [s for t, s in s2 if not is_light(t)]
        print(f"      >={kk:2d} bins ({kk*res:3d}s)  {100*sum(li)/len(li):5.1f}% /"
              f" {100*sum(da)/len(da):5.1f}%")

def write_sleep(path, act, res, k):
    out = path.rsplit(".", 1)[0] + f"_sleep_k{k}.csv"
    sc = dict(sleep_score(act, k))
    with open(out, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["bin_start", "cross_count", "asleep", "phase"])
        w.writerows([(t.strftime(FMT), c, int(sc[t]), "light" if is_light(t) else "dark")
                     for t, c in act])
    print(f"  wrote {out}")

def demo():
    """self-check: rebin sums and flags partial bins"""
    t0 = datetime(2026, 1, 1, 0, 0, 0)
    act = [(t0 + timedelta(seconds=12 * i), 1) for i in range(7)]  # 1 min = 5 bins + 2
    r = rebin(act, 12, 1)
    assert r[0] == (t0, 5, True), r
    assert r[1] == (t0 + timedelta(minutes=1), 2, False), r
    # sleep: 0,0,0,0,5,0,0,0 at 12s -> first zero run is 4 bins (sleep at k=4),
    # trailing run is 3 bins (not sleep at k=4, sleep at k=3)
    a = [(t0 + timedelta(seconds=12 * i), c) for i, c in enumerate([0, 0, 0, 0, 5, 0, 0, 0])]
    assert [x[1] for x in sleep_score(a, 4)] == [1, 1, 1, 1, 0, 0, 0, 0]
    assert [x[1] for x in sleep_score(a, 3)] == [1, 1, 1, 1, 0, 1, 1, 1]
    assert bouts(sleep_score(a, 4), True) == [(t0, 4)]
    assert bouts(sleep_score(a, 4), False) == [(t0 + timedelta(seconds=48), 4)]
    print("demo ok")

if __name__ == "__main__":
    args = sys.argv[1:]
    if args[:1] == ["--demo"]:
        demo()
    else:
        while args[:1] in (["--skip"], ["--k"]):
            if args[0] == "--skip":
                SKIP_FIRST_MIN = int(args[1])
            else:
                SLEEP_MIN_BINS = int(args[1])
            args = args[2:]
        for p in args:
            hdr, act, temp = report(p)
            sleep_report(act, temp, hdr["act_res"], SLEEP_MIN_BINS)
            for m in (1, 5):
                write_rebinned(p, act, hdr["act_res"], m)
            write_sleep(p, act, hdr["act_res"], SLEEP_MIN_BINS)
