"""Build every number the 2026-08-08 figures need, from source files only.

Writes `derived/inputs.json`. The two heavy inputs are produced separately and
cached, because they read the 89 GB recording:

    python ../usable_fraction_vs_floor.py <recording-base> --npz derived/usable_overnight.npz
    python ../per_animal_forensics.py --json derived/forensics_overnight.json

Nothing here is transcribed from a vault document. Where a value can only come
from a write-up (older recordings whose raw files are no longer processed), it is
tagged `"provenance": "vault write-up"` so a reader can tell the difference.
"""
from __future__ import annotations

import csv
import glob
import json
from pathlib import Path

import numpy as np
from core import paths as PATHS

HERE = Path(__file__).resolve().parent
DERIVED = HERE / "derived"
PROC = PATHS.PROCESSED_ROOT / ("2026-08-06")
IMPDIR = PATHS.IMPEDANCE_ROOT

PASS_MOHM = 0.5
POS_SITES = {"A1": ("A/1", "A/2"), "A2": ("A/33", "A/34"),
             "B1": ("B/1", "B/2"), "B2": ("B/33", "B/34"),
             "C1": ("C/1", "C/2"), "C2": ("C/33", "C/34"),
             "D1": ("D/1", "D/2"), "D2": ("D/33", "D/34")}
FLOOR_SITES = [f"{p}/{i}" for p in "ABCD"
               for i in list(range(3, 17)) + list(range(35, 49))]

SWEEPS = [
    ("31 Jul 17:34", "2026-07-31/imp_2026-07-31_1734_8mice-64ch_PRE-run1.csv"),
    ("2 Aug 01:44", "2026-08-02/imp_2026-08-02_0144_8mice-64ch_PRE-run2.csv"),
    ("2 Aug 23:34", "2026-08-02/imp_2026-08-02_2334_8mice-64ch_POST-run2.csv"),
    ("4 Aug 16:33", "2026-08-04/imp_2026-08-04_1633_8mice-64ch_post-DMM-restart.csv"),
    ("4 Aug 16:56", "2026-08-04/imp_2026-08-04_1656_8mice-64ch_replication-B1B2C1-moving.csv"),
]
CENSUS = IMPDIR / "2026-08-06/01-fleet-census-20sweeps"
ARM_A = IMPDIR / "2026-08-05/armA-original"
ARM_B = IMPDIR / "2026-08-05/armB-short-soldered"


def read_sweep(path):
    out = {}
    with open(path, encoding="utf-8") as fh:
        rd = csv.reader(fh)
        next(rd)
        for row in rd:
            if len(row) >= 2 and row[0]:
                try:
                    out[row[0]] = float(row[1])
                except ValueError:
                    pass
    return out


def duty(folder, site):
    files = sorted(glob.glob(str(Path(folder) / "*.csv")))
    k = n = 0
    for f in files:
        d = read_sweep(f)
        if site in d:
            n += 1
            k += d[site] < PASS_MOHM
    return k, n


def main():
    DERIVED.mkdir(exist_ok=True)
    out = {"pass_mohm": PASS_MOHM, "generated_from": "compute_inputs.py"}

    # ---- 1. impedance trajectories, the five single sweeps
    traj = {p: {"eeg": [], "emg": [], "labels": [lb for lb, _ in SWEEPS]}
            for p in POS_SITES}
    for _, rel in SWEEPS:
        d = read_sweep(IMPDIR / rel)
        for p, (se, sm) in POS_SITES.items():
            traj[p]["eeg"].append(d.get(se))
            traj[p]["emg"].append(d.get(sm))
    out["impedance_trajectory"] = traj
    out["impedance_trajectory_note"] = (
        "each point is ONE 20 second sweep, unrepeated; magnitude only; "
        "positive input of each bipolar pair")

    # ---- 2. fleet census duty cycles and the wire-free floor
    files = sorted(glob.glob(str(CENSUS / "*.csv")))
    sweeps = [read_sweep(f) for f in files]
    fk = fn = 0
    per_port = {p: [0, 0] for p in "ABCD"}
    for d in sweeps:
        for s in FLOOR_SITES:
            if s in d:
                fn += 1
                hit = d[s] < PASS_MOHM
                fk += hit
                per_port[s[0]][0] += hit
                per_port[s[0]][1] += 1
    census = {}
    for p, (se, sm) in POS_SITES.items():
        for ch, site in (("EEG", se), ("EMG", sm)):
            k = sum(1 for d in sweeps if site in d and d[site] < PASS_MOHM)
            n = sum(1 for d in sweeps if site in d)
            census[f"{p} {ch}"] = {"k": k, "n": n, "site": site,
                                   "position": p, "channel": ch}
    out["census"] = {"channels": census, "n_sweeps": len(sweeps),
                     "floor_k": fk, "floor_n": fn,
                     "floor_by_port": {p: v for p, v in per_port.items()},
                     "source": str(CENSUS)}

    # ---- 3. the tether comparison, arm A against arm B
    arms = {}
    for label, site in (("B1 EEG", "B/1"), ("B1 EMG", "B/2"),
                        ("D2 EEG, control", "D/1"), ("D2 EMG, control", "D/2")):
        ka, na = duty(ARM_A, site)
        kb, nb = duty(ARM_B, site)
        arms[label] = {"a_k": ka, "a_n": na, "b_k": kb, "b_n": nb, "site": site}
    out["tether_arms"] = arms

    # ---- 4. per recording sleep results, straight from the pipeline output
    recs = {}
    for f in sorted(PROC.glob("*_features.json")):
        d = json.loads(f.read_text())
        recs[f.name.replace("_features.json", "")] = {
            "name": d["name"], "verdict": d["verdict"],
            "hours_in_blocks": d["hours_in_blocks"], "n_blocks": d["n_blocks"],
            "longest_block_min": d["longest_block_min"],
            "wake_pct": d["wake_pct"], "nrem_pct": d["nrem_pct"],
            "persistence": {k: d["persistence"][k]["r"]
                            for k in ("1min", "5min", "10min")},
            "persistence_shuffled": {k: d["persistence"][k]["shuffled"]
                                     for k in ("1min", "5min", "10min")},
            "rem_from_nrem_pct": d["rem_from_nrem_pct"],
            "rem_null": d["rem_from_nrem_null"],
            "otsu_sensitivity": (d.get("otsu_sensitivity") or {}).get("rows"),
            "by_light_phase": d["by_light_phase"],
            "validity_stats_computed_on": d.get("validity_stats_computed_on"),
        }
    out["recordings"] = recs

    # scoreable animal hours per recording, computed by summing the hours of
    # every animal the pipeline marked SCOREABLE in that recording
    yields = {}
    for key, r in recs.items():
        stamp = key.split("_", 1)[1]
        yields.setdefault(stamp, {"scoreable_hours": 0.0, "animals": [],
                                  "provenance": "pipeline features files"})
        if r["verdict"] == "SCOREABLE":
            yields[stamp]["scoreable_hours"] += r["hours_in_blocks"]
            yields[stamp]["animals"].append(r["name"])
    # older recordings have no processed features files; their values come from
    # the write-ups and are labelled as such rather than silently mixed in
    yields["2026-07-10_72h"] = {"scoreable_hours": 0.0, "animals": [],
                                "provenance": "vault write-up"}
    yields["2026-07-13_20h"] = {"scoreable_hours": 0.0, "animals": [],
                                "provenance": "vault write-up"}
    yields["2026-07-31_27h9m"] = {"scoreable_hours": 10.4, "animals": ["C1"],
                                  "provenance": "vault write-up"}
    yields["2026-08-02_21h7m"] = {"scoreable_hours": 0.0, "animals": [],
                                  "provenance": "vault write-up"}
    out["yield_by_recording"] = yields

    # ---- 5. usable fraction, from the cached per epoch masks
    npz_path = DERIVED / "usable_overnight.npz"
    if npz_path.exists():
        z = np.load(npz_path, allow_pickle=True)
        names = [str(s) for s in z["animals"]]
        usable = {}
        for i, nm in enumerate(names):
            e, g = z["mask_eeg"][i], z["mask_emg"][i]
            both = e & g
            run = best = 0
            for v in both:
                run = run + 1 if v else 0
                best = max(best, run)
            usable[nm] = {"eeg_pct": 100 * float(e.mean()),
                          "emg_pct": 100 * float(g.mean()),
                          "both_pct": 100 * float(both.mean()),
                          "longest_both_min": best * int(z["epoch_s"]) / 60.0}
        out["usable"] = {"animals": usable,
                         "threshold_uv": float(z["threshold_uv"]),
                         "n_epochs": int(z["n_epochs"]),
                         "epoch_s": int(z["epoch_s"]),
                         "floor_pct": 100 * float(z["floor_mask"].mean()),
                         "source": str(npz_path)}
    else:
        print("NOTE: usable_overnight.npz not present yet")

    # ---- 6. per channel forensics
    fpath = DERIVED / "forensics_overnight.json"
    if fpath.exists():
        out["forensics"] = json.loads(fpath.read_text())
    else:
        print("NOTE: forensics_overnight.json not present yet")

    (DERIVED / "inputs.json").write_text(json.dumps(out, indent=1))
    print(f"wrote {DERIVED / 'inputs.json'}")
    if "usable" in out:
        for k, v in out["usable"]["animals"].items():
            print(f"  {k:4} EEG {v['eeg_pct']:6.1f}  EMG {v['emg_pct']:6.1f}  "
                  f"both {v['both_pct']:6.1f}  longest {v['longest_both_min']:7.1f} min")


if __name__ == "__main__":
    main()
