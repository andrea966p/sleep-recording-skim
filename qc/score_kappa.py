#!/usr/bin/env python3
"""Compare a human's blind scoring against stage 3. Cohen's kappa + confusion.

Reports
-------
* **Cohen's kappa**, overall, with a bootstrap 95% confidence interval.
  Landis & Koch bands are printed as a reading aid, not as a pass mark.
* **Per-state kappa** (one state against the rest). REM is the one that matters:
  the pipeline forces REM to 20% of sleep by construction, so if the human does
  not agree on REM, that is the measurement telling us so.
* **Confusion matrix**, human as reference.
* **Prevalence warning** when the pack was stratified. Kappa is prevalence
  sensitive, so a stratified pack does not give the kappa you would get on the
  whole recording. Both are reported when an unstratified pack exists.

UNSURE items are excluded and counted separately.

Usage
    python3 score_kappa.py <SCORING_DIR> [--boot 2000]
"""
import argparse
import csv
import os
import random

import numpy as np

STATES = ["WAKE", "NREM", "REM"]


def kappa(a, b, labels):
    """Cohen's kappa for two label sequences."""
    n = len(a)
    if n == 0:
        return float("nan")
    idx = {l: i for i, l in enumerate(labels)}
    m = np.zeros((len(labels), len(labels)))
    for x, y in zip(a, b):
        m[idx[x], idx[y]] += 1
    po = np.trace(m) / n
    pe = float((m.sum(0) * m.sum(1)).sum()) / (n * n)
    return (po - pe) / (1 - pe) if pe != 1 else float("nan")


def band(k):
    if np.isnan(k):
        return "undefined"
    for lo, txt in ((0.81, "almost perfect"), (0.61, "substantial"), (0.41, "moderate"),
                    (0.21, "fair"), (0.0, "slight")):
        if k >= lo:
            return txt
    return "worse than chance"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("scoring_dir")
    ap.add_argument("--boot", type=int, default=2000)
    a = ap.parse_args()
    d = a.scoring_dir

    truth = {int(r["item"]): r for r in csv.DictReader(open(os.path.join(d, "_TRUTH_do_not_open.csv")))}
    sheet_path = os.path.join(d, "scoresheet.csv")
    if not os.path.exists(sheet_path):
        raise SystemExit(f"no scoresheet at {sheet_path}")
    human_raw = {int(r["item"]): (r["your_stage"] or "").strip().upper()
                 for r in csv.DictReader(open(sheet_path))}

    blank = [i for i, v in human_raw.items() if v == ""]
    unsure = [i for i, v in human_raw.items() if v == "UNSURE"]
    bad = sorted({v for v in human_raw.values() if v not in STATES + ["", "UNSURE"]})
    pairs = [(human_raw[i], truth[i]["auto_state"]) for i in sorted(truth)
             if human_raw.get(i) in STATES]
    if bad:
        print(f"⚠️  unrecognised answers ignored: {bad}")
    if not pairs:
        raise SystemExit("nothing scored yet")

    H = [p[0] for p in pairs]
    A = [p[1] for p in pairs]
    n = len(pairs)
    agree = sum(h == x for h, x in zip(H, A))

    print(f"\nBLIND SCORING vs STAGE 3   ({os.path.basename(d)})")
    print("=" * 66)
    print(f"items in pack        {len(truth)}")
    print(f"scored               {n}")
    print(f"left blank           {len(blank)}")
    print(f"marked UNSURE        {len(unsure)}   (excluded from kappa)")
    print(f"raw agreement        {100.0*agree/n:.1f}%   ({agree}/{n})")

    k = kappa(H, A, STATES)
    rng = random.Random(0)
    ks = []
    for _ in range(a.boot):
        s = [rng.randrange(n) for _ in range(n)]
        ks.append(kappa([H[i] for i in s], [A[i] for i in s], STATES))
    ks = [x for x in ks if not np.isnan(x)]
    lo, hi = (np.percentile(ks, 2.5), np.percentile(ks, 97.5)) if ks else (float("nan"),) * 2
    print(f"\nCohen's kappa        {k:.3f}   95% CI [{lo:.3f}, {hi:.3f}]   ({band(k)})")

    print("\nper-state kappa (that state against the rest)")
    for s in STATES:
        hs = [x if x == s else "OTHER" for x in H]
        as_ = [x if x == s else "OTHER" for x in A]
        ks_ = kappa(hs, as_, [s, "OTHER"])
        nh, na = H.count(s), A.count(s)
        print(f"  {s:5} k={ks_:6.3f}  ({band(ks_)})   human n={nh:4}  auto n={na:4}")

    print("\nconfusion matrix   rows = HUMAN, cols = stage 3")
    print(f"{'':8}" + "".join(f"{s:>8}" for s in STATES) + f"{'total':>8}")
    for hs in STATES:
        row = [sum(1 for h, x in zip(H, A) if h == hs and x == cs) for cs in STATES]
        print(f"{hs:8}" + "".join(f"{v:8}" for v in row) + f"{sum(row):8}")
    print(f"{'total':8}" + "".join(f"{A.count(s):8}" for s in STATES) + f"{n:8}")

    rd = open(os.path.join(d, "README.txt")).read() if os.path.exists(os.path.join(d, "README.txt")) else ""
    if "stratified" in rd:
        print("\n⚠️  THIS PACK IS STRATIFIED (equal n per automatic state).")
        print("    Kappa is prevalence sensitive, so this is a STRATIFIED kappa and is")
        print("    NOT the value you would get on the whole recording. Build an")
        print("    unstratified pack with --random to get the prevalence-matched one.")
    print("\nLandis & Koch bands are a reading aid, not a pass mark. What matters is")
    print("whether REM agrees: the pipeline FORCES REM to 20% of sleep by construction.")

    out = os.path.join(d, "kappa_result.txt")
    with open(out, "w") as fh:
        fh.write(f"n={n} agreement={100.0*agree/n:.1f}% kappa={k:.3f} CI=[{lo:.3f},{hi:.3f}]\n")
    print(f"\nwritten: {out}")


if __name__ == "__main__":
    main()
