"""Scan ALL 256 amplifier channels in the live recording for anything biological.
If the 8-conductor tether has a different pinout, the signals are on sites we are not looking at.
Band powers straight off Welch, mains bins excluded, so no filter-design artefacts."""
import json, os
import numpy as np
from scipy.signal import welch
from core import paths as PATHS

BASE = str(PATHS.RAW_ROOT) + "/allego_0__uid0807-19-14-58"
FS = 1000.0
j = json.load(open(BASE + ".xdat.json"))
bm = j["sapiens_base"]["biointerface_map"]; NCH = j["status"]["signals"]["total"]
labels, counters = [], {}
for name in bm["ntv_chan_name"]:
    if str(name).startswith("port_"):
        p = str(name).split("_")[1]; counters[p] = counters.get(p, 0) + 1
        labels.append(f"{p}/{counters[p]}")
    else: labels.append(str(name))
nsamp = os.path.getsize(BASE + "_data.xdat") // (NCH * 4)
n = int(120 * FS)
X = np.memmap(BASE+"_data.xdat", dtype=np.float32, mode="r",
              shape=(nsamp, NCH))[nsamp-n-60000 : nsamp-60000]
print(f"scanning 256 amp channels, 120 s, file is {nsamp/FS/60:.0f} min long\n", flush=True)

WIRED = set()
for p in "ABCD":
    for i in (1,2,3,33,34,35): WIRED.add(f"{p}/{i}")
FLOORS = set()
for p in "ABCD":
    for i in list(range(4,17))+list(range(36,49)): FLOORS.add(f"{p}/{i}")

def mains_mask(f):
    m = np.ones_like(f, bool)
    for k in range(1, 9):
        m &= np.abs(f - 60*k) > 2.5
    return m

rows = []
for i, lab in enumerate(labels):
    if "/" not in lab: continue
    v = np.asarray(X[:, i], np.float64); v -= v.mean()
    f, P = welch(v, fs=FS, nperseg=4096)
    mm = mains_mask(f)
    def bp(lo, hi):
        b = (f >= lo) & (f <= hi) & mm
        return float(np.sqrt(np.trapezoid(P[b], f[b])))
    lf, hf = bp(1, 40), bp(100, 300)
    sl = np.nan
    b = (f >= 1) & (f <= 40) & mm
    if b.sum() > 5:
        sl = float(np.polyfit(np.log10(f[b]), np.log10(P[b]+1e-20), 1)[0])
    rows.append((lab, lf, hf, sl, lf/(hf+1e-9)))

rows.sort(key=lambda r: -r[1])
print(f"{'site':<7}{'class':<9}{'lf_1-40':>9}{'hf_100-300':>11}{'slope':>8}{'lf/hf':>8}")
print("-- top 20 channels by mains-free 1-40 Hz amplitude --")
for lab, lf, hf, sl, rat in rows[:20]:
    cls = "WIRED" if lab in WIRED else ("floor" if lab in FLOORS else "inactive")
    print(f"{lab:<7}{cls:<9}{lf:9.1f}{hf:11.1f}{sl:8.2f}{rat:8.2f}")

print("\n-- every WIRED site, in order --")
w = {r[0]: r for r in rows}
for p in "ABCD":
    for i, role in ((1,"EEG"),(2,"EMG"),(3,"ECG"),(33,"EEG"),(34,"EMG"),(35,"ECG")):
        lab = f"{p}/{i}"; _, lf, hf, sl, rat = w[lab]
        tag = "  <== CONTROL" if lab in ("A/33","A/34","A/35") else ""
        print(f"{lab:<7}{role:<5}{lf:9.1f}{hf:11.1f}{sl:8.2f}{rat:8.2f}{tag}")

fl = np.array([r[1] for r in rows if r[0] in FLOORS])
print(f"\nfloor 1-40 Hz (mains-free): median {np.median(fl):.1f}  p95 {np.percentile(fl,95):.1f}  min {fl.min():.1f}")
