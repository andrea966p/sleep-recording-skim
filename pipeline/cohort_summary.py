#!/usr/bin/env python3
"""Build one cohort-level package across several recordings of the SAME animals.

The per-day folders produced by stage 2 are per RECORDING. This walks a set of
them and produces a single view of the cohort: every animal, every run, what its
electrodes did, what came out, and what is scoreable.

Written for the 8-mouse cohort implanted 2026-07-21..23, which was recorded twice
(2026-07-31 and 2026-08-02).

    python3 cohort_summary.py --out "$EEG_PROCESSED_ROOT/COHORT-2026-07" \
        2026-07-31 2026-08-02
"""
import argparse
import csv
import glob
import json
import os
import shutil
import sys

from core import qc_thresholds as T
from core import paths as PATHS

ROOT = str(PATHS.PROCESSED_ROOT) + os.sep


def load_day(day_dir):
    """Return (recordings, animals, features, impedance) for one day folder."""
    recs, animals = [], []
    for j in sorted(glob.glob(os.path.join(day_dir, "qc", "qc_*.json"))):
        q = json.load(open(j))
        recs.append(q)
        for a in q["animals"]:
            animals.append(dict(day=q["day"], recording=q["recording"],
                                start_local=q["start_local"],
                                hours=q["hours"], **a))
    feats = {}
    for f in sorted(glob.glob(os.path.join(day_dir, "*_features.json"))):
        r = json.load(open(f))
        feats[(r["day"], r["name"])] = r
    imp = []
    ip = os.path.join(day_dir, "impedance", "impedance_summary.csv")
    if os.path.exists(ip):
        with open(ip, newline="") as fh:
            imp = list(csv.DictReader(fh))
    return recs, animals, feats, imp


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("days", nargs="+", help="day folder names, e.g. 2026-07-31")
    ap.add_argument("--root", default=ROOT)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()

    os.makedirs(a.out, exist_ok=True)
    all_recs, all_animals, all_feats, all_imp = [], [], {}, []
    for d in a.days:
        dd = os.path.join(a.root, d)
        if not os.path.isdir(dd):
            print(f"[skip] {dd} not found")
            continue
        r, an, fe, im = load_day(dd)
        all_recs += r
        all_animals += an
        all_feats.update(fe)
        for row in im:
            row["day"] = d
        all_imp += im

    # ---- per-animal-per-run CSV -------------------------------------------
    fields = ["day", "recording", "start_local", "hours", "name", "port", "slot",
              "verdict", "reason", "pct_pass", "gated_hours", "block_hours",
              "longest_block_min", "n_blocks", "median_block_s",
              "med_eeg_mains_uv", "med_emg_mains_uv", "med_eeg_rms_uv",
              "med_emg_rms_uv", "pct_epochs_railed",
              "scoreable", "r_1min", "wake_pct", "nrem_pct"]
    csv_path = os.path.join(a.out, "cohort_animals.csv")
    with open(csv_path, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=fields, extrasaction="ignore")
        w.writeheader()
        for an in all_animals:
            f = all_feats.get((an["day"], an["name"]))
            an = dict(an)
            if f:
                an["scoreable"] = "YES" if f["verdict"] == "SCOREABLE" else "no"
                an["r_1min"] = f["persistence"]["1min"]["r"]
                an["wake_pct"] = f["wake_pct"]
                an["nrem_pct"] = f["nrem_pct"]
            else:
                an["scoreable"] = "not reached"
            w.writerow(an)

    # ---- impedance across the cohort --------------------------------------
    if all_imp:
        ipath = os.path.join(a.out, "cohort_impedance.csv")
        with open(ipath, "w", newline="") as fh:
            keys = ["day"] + [k for k in all_imp[0] if k != "day"]
            w = csv.DictWriter(fh, fieldnames=keys, extrasaction="ignore")
            w.writeheader()
            w.writerows(all_imp)

    # ---- copy every scorer-facing artefact into one place -----------------
    sc = os.path.join(a.out, "to-score")
    os.makedirs(sc, exist_ok=True)
    copied = 0
    for d in a.days:
        for pat in ("*.edf", "*_SCORER-README.txt", "*_hypnogram.csv",
                    "*_summary.txt"):
            for f in glob.glob(os.path.join(a.root, d, pat)):
                shutil.copy2(f, os.path.join(sc, os.path.basename(f)))
                copied += 1

    # ---- readable report ---------------------------------------------------
    days = sorted({r["day"] for r in all_recs})
    names = sorted({an["name"] for an in all_animals})
    L = [f"EEG/EMG cohort package", "=" * 78, ""]
    for r in sorted(all_recs, key=lambda x: x["start_local"]):
        L.append(f"  {r['day']}  {r['recording']}  {r['hours']:.2f} h  "
                 f"start {r['start_local'][:19]}")
    L += ["", f"animals: {len(names)}   animal-recordings: {len(all_animals)}", ""]

    L += ["PER ANIMAL, PER RUN", "-" * 78]
    hdr = f"{'mouse':<6}" + "".join(f"{d[5:]:>26}" for d in days)
    L.append(hdr)
    for n in names:
        row = f"{n:<6}"
        for d in days:
            an = next((x for x in all_animals if x["day"] == d and x["name"] == n), None)
            if an is None:
                row += f"{'--':>26}"
                continue
            f = all_feats.get((d, n))
            if f is None:
                tag = an["verdict"]                 # never reached stage 3
            elif f["verdict"] == "SCOREABLE":
                tag = "SCOREABLE"
            else:
                tag = "REJECT"                      # reached stage 3 and failed it
            row += f"{tag:>13}{an['block_hours']:>7.2f}h{an['med_eeg_mains_uv']:>6.0f}"
        L.append(row)
    L += ["", "  columns per run: verdict | usable hours in blocks | median EEG mains uV",
          f"  (open-circuit limit is {T.OPEN_UV:.0f} uV; connected channels sit at 6-20 uV)", ""]

    sco = [(d, n) for (d, n), f in all_feats.items() if f["verdict"] == "SCOREABLE"]
    L += ["SCOREABLE", "-" * 78]
    if sco:
        for d, n in sorted(sco):
            f = all_feats[(d, n)]
            L.append(f"  {d}  {n}: {f['hours_in_blocks']:.2f} h in {f['n_blocks']} blocks, "
                     f"longest {f['longest_block_min']:.0f} min, "
                     f"r@1min {f['persistence']['1min']['r']}, "
                     f"WAKE {f['wake_pct']}% / NREM {f['nrem_pct']}%")
            lp = f["by_light_phase"].get("light")
            if lp:
                L.append(f"       light phase: {100-lp['wake_pct']:.1f}% asleep "
                         f"(published C57BL/6 value is ~70%)")
    else:
        L.append("  none")

    tot = sum(all_feats[k]["hours_in_blocks"] for k in all_feats
              if all_feats[k]["verdict"] == "SCOREABLE")
    animal_h = sum(an["hours"] for an in all_animals)
    L += ["", f"  scoreable total: {tot:.2f} h out of {animal_h:.0f} animal-hours recorded",
          ""]

    reasons = {}
    for an in all_animals:
        f = all_feats.get((an["day"], an["name"]))
        if f is None:
            k = an["verdict"]                       # never reached stage 3
        elif f["verdict"] == "SCOREABLE":
            k = "SCOREABLE"
        else:
            k = "REJECT at stage 3"
        reasons[k] = reasons.get(k, 0) + 1
    L += ["OUTCOME OF EVERY ANIMAL-RECORDING", "-" * 78]
    for k, v in sorted(reasons.items(), key=lambda x: -x[1]):
        L.append(f"  {k:<20} {v:>3} of {len(all_animals)}")
    L += ["",
          "  OPEN              electrode not electrically connected, nothing to analyse",
          "  REJECT at stage 3 usable data existed but failed the validity checks",
          "  SCOREABLE         passed every check, hand to a scorer"]

    L += ["", "READ BEFORE USING ANY OF THIS", "-" * 78,
          "  Both runs were RIG COMMISSIONING TESTS, taken early:",
          "    surgery 2026-07-21..23, tethered 2026-07-30",
          "    run 1 = day 8-10 after implant, ~1 day tethered",
          "    run 2 = day 10-12 after implant, ~2.5 days tethered",
          "  Our own protocol asks for at least 14 days after implant and at least",
          "  7 days of cage acclimatisation, so sleep amounts here are NOT baseline",
          "  and no yield figure from these runs describes the rig's performance.",
          "",
          "  Signals are ALREADY BIPOLAR. Do not subtract EEG from EMG.",
          "  Score only inside the windows listed in each _SCORER-README.txt.",
          "  Do not report a REM percentage (fixed by construction, see the method doc).",
          "",
          "FILES", "-" * 78,
          "  cohort_animals.csv     one row per animal per run",
          "  cohort_impedance.csv   every impedance sweep, per electrode",
          f"  to-score/              {copied} files: EDF+, scorer notes, hypnograms, summaries",
          "",
          "  method: 02-procedures/eeg-data-analysis/analysis-methods-and-justification.md",
          "  results: 05-experiments/completed/2026-08-03-two-8-mouse-runs.md",
          ]
    open(os.path.join(a.out, "README.txt"), "w").write("\n".join(L) + "\n")
    print("\n".join(L))
    print(f"\n[written] {a.out}")


if __name__ == "__main__":
    main()
