#!/usr/bin/env python3
"""Stage the HLBNSL nanotag data for the SKIM NAS in the per-mouse layout the EEG
uploads use (02_Data_Sleep/<user>/<batch>/<period>/<date>_<mouse>_<B|T>/), then
copy it with the verified copier the EEG side already has.

    /usr/bin/python3 nanotag/analysis/export_nas.py DATA_DIR STAGING_DIR [ANALYSIS_DIR]
    /usr/bin/python3 eeg-emg-analysis/qc/nas_copy_verified.py STAGING_DIR /mnt/skimnas/02_Data_Sleep/andrea

STAGING/<HLBNSSL|HLBNWSL>/<Baseline|Treatment>/<YYYYMMDD>_<mouse>_<B|T>/
    <same>.csv        one row per 12 s bin, every run of the period joined:
                      time_kst, cross_count, temperature_c (one value per 5 min),
                      run, excluded (1 = inside an EXCLUDE window), sleep
                      (1/0, blank where excluded)
    <same>.info.json  provenance, excluded windows, verdict
    raw/              the nanotagViewer exports as read off the tag (.nta + .csv)
ANALYSIS_DIR (optional) is staged as HLBNSL_nanotag_ANALYSIS_<today>/.
Mouse 43 is staged too (raw kept), with verdict EXCLUDED.
"""
import csv, hashlib, json, os, shutil, sys
from datetime import date, datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from cohort import (files, excluded, group, EXCLUDE, DROP, SHORT_BASELINE, K,
                    SOD1_START, LIGHTS_ON)
from nta_qc import sleep_score, LIGHTS_OFF

STEM = {"SOD1": "HLBNSSL", "water": "HLBNWSL"}
COHORT = {"SOD1": ("NS-SL", "SOD1 6.8 U/mL in drinking water, sleep ad libitum"),
          "water": ("NW-SL", "UV-sterilised water, sleep ad libitum")}
PERIOD = {"baseline": ("Baseline", "B"), "treatment": ("Treatment", "T")}
SITE = ("s.c., entered at the neck and pushed right; migrated to the right dorsolateral "
        "flank. Threshold 170 = Kissei mouse-neck value, not validated for the flank: "
        "counts are relative units within this study")
FMT = "%Y-%m-%d %H:%M:%S"

def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()

def verdict(mouse, period):
    if mouse in DROP:
        return "EXCLUDED: HLBNSSL43 died 2026-09-28 during restraint for the tag read; all data discarded"
    if mouse in SHORT_BASELINE and period == "baseline":
        return "NOT ANALYSED: 1-day baseline (2026-09-15); group baseline uses the 3-day mice only"
    return "ANALYSED"

def stage(folder, out):
    by = {}
    for period, run, mouse, path, data in files(folder):
        by.setdefault((mouse, period), []).append((run, path, data))
    for (mouse, period), runs in sorted(by.items()):
        g = group(mouse)
        mid = f"{STEM[g]}{mouse}"
        rows = []
        for run, path, (hdr, act, temp) in sorted(runs):
            t = dict(temp)
            sl = dict(sleep_score(act, K))      # scored per file, as in cohort.load
            for ts, c in act:
                x = excluded(ts)
                rows.append((ts, c, t.get(ts, ""), run, int(x), "" if x else int(sl[ts])))
        rows.sort()
        pname, code = PERIOD[period]
        name = f"{rows[0][0]:%Y%m%d}_{mid}_{code}"
        d = os.path.join(out, STEM[g], pname, name)
        os.makedirs(os.path.join(d, "raw"), exist_ok=True)
        csv_path = os.path.join(d, f"{name}.csv")
        with open(csv_path, "w", newline="") as f:
            w = csv.writer(f)
            w.writerow(["time_kst", "cross_count", "temperature_c", "run", "excluded", "sleep"])
            w.writerows((r[0].strftime(FMT), *r[1:]) for r in rows)
        run_info = []
        for run, path, (hdr, act, temp) in sorted(runs):
            for p in (path, path[:-4] + ".nta"):
                if os.path.exists(p):
                    shutil.copy2(p, os.path.join(d, "raw", os.path.basename(p)))
            run_info.append(dict(run=run, file=os.path.basename(path), csv_sha256=sha256(path),
                                 header_start=hdr.get("Start date_Activity"),
                                 first_bin=act[0][0].strftime(FMT), last_bin=act[-1][0].strftime(FMT),
                                 n_bins=len(act), temp_out_of_range=hdr["temp_oor"]))
        first, last = rows[0][0], rows[-1][0]
        info = dict(
            mouseID=mid, batch=STEM[g], cohort=COHORT[g][0], condition=COHORT[g][1],
            recording_type=period, folder=name, verdict=verdict(mouse, period),
            device=dict(type="nanotag (Kissei Comtec), implanted", tag_id=hdr["nanotag ID"],
                        activity_res_s=hdr["act_res"], temperature_res_s=hdr["temp_res"],
                        threshold_upper=hdr.get("Upper threshhold"),
                        threshold_lower=hdr.get("Lower threshhold"),
                        temperature_range_C=hdr.get("Temperature range (degC)")),
            implant_site=SITE,
            lights_kst=f"on {LIGHTS_ON:02d}:00, off {LIGHTS_OFF:02d}:00 (ZT0 = {LIGHTS_ON:02d}:00)",
            sod1_start_kst=SOD1_START[0].strftime(FMT) + " to " + SOD1_START[1].strftime("%H:%M"),
            first_bin=first.strftime(FMT), last_bin=last.strftime(FMT), runs=run_info,
            excluded_windows=[dict(start=a.strftime(FMT), end=b.strftime(FMT), reason=why)
                              for a, b, why in EXCLUDE if a <= last and b > first],
            n_bins=len(rows), n_excluded=sum(r[4] for r in rows),
            sleep_scoring=f"Pack et al. 2006 immobility: >= {K} consecutive zero-count 12 s bins "
                          f"(>= {K * 12} s), scored per file (nanotag/analysis/nta_qc.py sleep_score)",
            csv=dict(columns=["time_kst", "cross_count", "temperature_c", "run", "excluded", "sleep"],
                     sha256=sha256(csv_path), bytes=os.path.getsize(csv_path)),
            exporter=dict(tool="nanotag/analysis/export_nas.py",
                          utc=datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")),
            docs="vault/20-areas/nanotag/nanotag-recording-and-analysis.md")
        with open(os.path.join(d, f"{name}.info.json"), "w") as f:
            json.dump(info, f, indent=2, ensure_ascii=False)
        print(f"  {name}: {len(rows)} bins, {info['n_excluded']} excluded, {len(run_info)} run(s), "
              f"{info['verdict'].split(':')[0]}")

def demo():
    assert verdict(43, "treatment").startswith("EXCLUDED")
    assert verdict(49, "baseline").startswith("NOT ANALYSED") and verdict(49, "treatment") == "ANALYSED"
    print("demo ok")

if __name__ == "__main__":
    if sys.argv[1:2] == ["--demo"]:
        demo()
    elif len(sys.argv) in (3, 4):
        stage(sys.argv[1], sys.argv[2])
        if len(sys.argv) == 4:
            dst = os.path.join(sys.argv[2], f"HLBNSL_nanotag_ANALYSIS_{date.today():%Y-%m-%d}")
            shutil.copytree(sys.argv[3], dst, dirs_exist_ok=True)
            print(f"  analysis -> {dst}")
    else:
        raise SystemExit(__doc__)
