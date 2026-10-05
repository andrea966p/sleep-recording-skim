"""Compare noise_scan JSON outputs (same rig, nothing changed) -> run-to-run spread per metric.
usage: python3 baseline_compare.py a.json b.json [c.json ...]"""
import sys, json, numpy as np
runs = [json.load(open(p)) for p in sys.argv[1:]]
# the gate-scale line PEAK when every run has it (noise_scan.py from 2026-10-02 on), else the legacy band rms
MKEY = "mains_peak" if all("mains_peak" in r for r in runs) else "mains"
print(f"60 Hz numbers: {MKEY} (" + ("59-61 Hz line peak, QC gate scale" if MKEY == "mains_peak" else "55-65 Hz band rms, legacy: x sqrt(2) for the gate") + ")")
def chip_vals(r):
    lab = r["labels"]; idx = {l: i for i, l in enumerate(lab)}
    out = {}
    for p in sorted({l.split("/")[0] for l in lab}):
        for name, base in ((p + "1", 1), (p + "2", 33)):
            fl = [idx[f"{p}/{s}"] for s in range(base + 2, base + 16) if f"{p}/{s}" in idx]
            if not fl: continue
            m = lambda key: float(np.median(np.asarray(r[key])[fl]))
            h = lambda k: float(np.median(np.asarray(r["harm"][str(k)])[fl]))
            e, g = idx[f"{p}/{base}"], idx[f"{p}/{base+1}"]
            out[name] = {"floor60": m(MKEY), "floor120": h(2), "floor180": h(3), "floor_bb1-45": m("bb"),
                         "floor_hf100-450": m("hf"), "EEG60": r[MKEY][e], "EMG60": r[MKEY][g],
                         "EEG_hf": r["hf"][e], "EMG_hf": r["hf"][g]}
    return out
V = [chip_vals(r) for r in runs]
keys = list(next(iter(V[0].values())).keys())
print("chip  metric              " + "  ".join(f"run{i+1:>8}" for i in range(len(V))) + "   max/min")
for chip in V[0]:
    for k in keys:
        xs = [v[chip][k] for v in V]
        print(f"{chip:4s}  {k:18s}" + "  ".join(f"{x:11.1f}" for x in xs) + f"   {max(xs)/max(min(xs),1e-9):6.2f}")
    print()
