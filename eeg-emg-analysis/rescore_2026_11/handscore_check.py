"""Re-score vs Andrea's SleepStager pass on HLBSSL33 Recovery (the only human-reviewed recording).

Her save is the SleepStager rule's first pass, reviewed epoch by epoch over the ranges she went through,
with her changes listed in the save's `restaged`. So agreement with any rule output is partly built in;
the HMM (no rule input) and her corrections are the independent part.
Ranges: 1-based inclusive epochs, e.g. `1-8441,10801-13624` (2026-11-03: light ZT0-9.4, then dark ZT12-15.1).
Default is 1..last_epoch, which is only right if she reviewed linearly from the start.
Usage: handscore_check.py SAVE_DIR EPOCH_DIR [RANGES]   (SAVE_DIR = the `4-sec sleepstager` folder, EPOCH_DIR = epochs/HLBSSL/R/HLBSSL33)
"""
import json, sys
from pathlib import Path

import numpy as np
import pandas as pd

from score import kappa


def report(lab, ok, A, orig, h, restaged):
    idx = np.array([r["epoch"] - 1 for r in restaged]); idx = idx[ok[idx]] if len(idx) else idx
    print(f"\n== {lab}: {ok.sum()} epochs reviewed, {len(idx)} changed by the scorer")
    for x, name in ((orig, "SleepStager first pass (her start)"), (h.stage.to_numpy(), "re-score (final)"),
                    (h.stage_ss60.to_numpy(), "re-score rule, 20-90 Hz EMG"), (h.stage_hmm.to_numpy(), "HMM (no rule input)")):
        q = ok & np.isin(x, ["W", "NR", "R"])
        print(f"  {name:<36} kappa {kappa(A[q], x[q]):.3f}  agree {100 * (A[q] == x[q]).mean():.1f} %  n={q.sum()}")
    eo = h.stage_eeg_only.to_numpy(); q = ok & np.isin(eo, ["NR", "WR"])
    a, b = A[q] == "NR", eo[q] == "NR"                                      # binary kappa, NREM vs not
    po, pe = (a == b).mean(), a.mean() * b.mean() + (1 - a.mean()) * (1 - b.mean())
    print(f"  {'EEG alone, NREM vs not':<36} kappa {(po - pe) / (1 - pe):.3f}")
    q = ok & np.isin(h.stage, ["W", "NR", "R"])
    for st in ("W", "NR", "R"):
        print(f"  {st:>2} share: hers {100 * (A[q] == st).mean():.1f} %, re-score {100 * (h.stage.to_numpy()[q] == st).mean():.1f} %")
    if len(idx):
        aft = A[idx]
        for c, name in (("stage", "re-score"), ("stage_hmm", "HMM")):
            print(f"  her corrections: {name} gives her new label in {100 * (h[c].to_numpy()[idx] == aft).mean():.0f} %")
        print(pd.crosstab(pd.Series(orig[idx], name="rule before"), pd.Series(aft, name="her label")).to_string())


def main(S: Path, E: Path, ranges: str | None):
    js = next(S.glob("*.json")); j = json.loads(js.read_text())
    A = pd.read_csv(next(S.glob("*_stages.csv")), usecols=["stage"]).stage.to_numpy()
    h = pd.read_parquet(E / "hypnogram.parquet")
    assert len(A) == len(h), "the save and the re-score must cover the same window"
    orig = A.copy()
    for r in j["restaged"]:
        orig[r["epoch"] - 1] = r["stage_before"]
    spans = [tuple(map(int, s.split("-"))) for s in (ranges or f"1-{j['last_epoch']}").split(",")]
    n = np.arange(1, len(A) + 1); scored = np.isin(A, ["W", "NR", "R"])
    print(f"{js.name}: {len(j['restaged'])} changed by the scorer, last_epoch {j['last_epoch']}, ranges {spans}")
    blocks = [(f"{a}-{b}", (n >= a) & (n <= b) & scored) for a, b in spans]
    if len(blocks) > 1:
        blocks.append(("all reviewed", np.any([m for _, m in blocks], axis=0)))
    for lab, ok in blocks:
        report(lab, ok, A, orig, h, j["restaged"])


if __name__ == "__main__":
    main(Path(sys.argv[1]), Path(sys.argv[2]), sys.argv[3] if len(sys.argv) > 3 else None)
