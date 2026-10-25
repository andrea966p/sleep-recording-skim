#!/usr/bin/env python3
"""Y-maze endpoints from EthoVision XT raw-data exports, scored by metrics.py.

    ymaze_from_ethovision.py <export_dir> [-o ymaze_results.csv] [--no-centre MOUSE ...]

Reads every "Raw data-*.xlsx" (Analysis > Export > Raw Data, In zone per sample),
rebuilds the zone-visit list (consecutive samples in one zone = one visit, samples
in no zone are skipped), then uses metrics.arm_sequence / spontaneous_alternation,
so the SOP definition (re-entries kept) is applied, not EthoVision's.

--no-centre: for arenas drawn without a centre zone, a "no zone" stretch counts as a
centre visit. This also counts border flicker as centre visits, so treat it as a
fallback and re-track with a proper centre zone instead.

Needs openpyxl.
"""
import argparse, csv, glob, os, sys
import openpyxl

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from metrics import arm_sequence, spontaneous_alternation  # noqa: E402

ZONES = {"arm A": "A", "arm B": "B", "arm C": "C", "center": "centre"}


def zone_visits(samples, none_is_centre=False):
    """[zone or None per sample] -> visit list, consecutive repeats merged."""
    out = []
    for z in samples:
        if z is None:
            if not none_is_centre:
                continue
            z = "centre"
        if not out or out[-1] != z:
            out.append(z)
    return out


def read_export(path):
    rows = openpyxl.load_workbook(path, read_only=True, data_only=True).worksheets[0].iter_rows(values_only=True)
    n_header = int(next(rows)[1])
    meta = {}
    for _ in range(n_header - 3):
        r = next(rows)
        if r and r[0] and len(r) > 1:
            meta[str(r[0]).strip()] = r[1]
    header = next(rows)
    next(rows)                                        # units line
    cols = {}                                         # "In zone(arm A / center-point)" -> "A"
    for i, h in enumerate(header):
        if h and h.startswith("In zone("):
            name = h[len("In zone("):].split(" /")[0]
            if name in ZONES:
                cols[ZONES[name]] = i
    i_dist = next(i for i, h in enumerate(header) if h and h.startswith("Distance moved"))
    samples, dist, lost = [], 0.0, 0
    for r in rows:
        if r[0] is None:
            break
        if r[2] == "-":                               # subject not found
            lost += 1
        inz = [z for z, i in cols.items() if r[i] == 1]
        samples.append(inz[0] if inz else None)
        if isinstance(r[i_dist], (int, float)):
            dist += r[i_dist]
    return meta, samples, dist, lost, set(cols)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("export_dir")
    p.add_argument("-o", "--out", default="ymaze_results.csv")
    p.add_argument("--no-centre", nargs="*", default=[])
    a = p.parse_args()

    files = sorted(glob.glob(os.path.join(a.export_dir, "Raw data-*.xlsx")))
    if not files:
        sys.exit(f"no Raw data-*.xlsx in {a.export_dir}")
    out = []
    for f in files:
        meta, samples, dist, lost, zones = read_export(f)
        mouse = meta.get("Mouse")
        fallback = mouse in a.no_centre
        seq = arm_sequence(zone_visits(samples, none_is_centre=fallback))
        alts, n, sa = spontaneous_alternation(seq)
        n_s = len(samples)
        out.append({
            "mouse": mouse, "group": meta.get("Group"), "arena": meta.get("Arena settings"),
            "samples": n_s, "not_found": lost,
            "centre_s": round(samples.count("centre") / 30, 1),
            "no_zone_s": round(samples.count(None) / 30, 1),
            "entries": n, "alternations": alts,
            "sa_pct": None if sa is None else round(sa, 1),
            "distance_cm": round(dist, 1),
            "centre_fallback": fallback,
            "sequence": "".join(z for z in seq),
        })
    with open(a.out, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(out[0]))
        w.writeheader()
        w.writerows(out)
    for r in out:
        print({k: v for k, v in r.items() if k != "sequence"})
    print(f"-> {a.out}")


if __name__ == "__main__":
    # flicker into "no zone" inside one arm is not a new visit; with the fallback it is
    assert zone_visits(["A", None, "A", "centre", "A"]) == ["A", "centre", "A"]
    assert zone_visits(["A", None, "A"], none_is_centre=True) == ["A", "centre", "A"]
    main()
