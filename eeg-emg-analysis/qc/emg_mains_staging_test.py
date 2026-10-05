#!/usr/bin/env python3
"""Does mains in the EMG change sleep staging? Stage 3, unchanged, with and without the EMG notched.

For each day folder: symlink its stage-2 per-mouse .npz files into OUT/<cond>/<day>/ (no data is copied,
and stage 3's outputs land in OUT, never beside the official files), then run pipeline.stage3_features.analyse
twice: 'orig' (as published) and 'notch' (EMG 60 and 120 Hz notched, Q 30, in memory only). The 'orig' run must
reproduce the official verdicts; that is the method check. Diagnostic only: adopting it would be a pre-registered
pipeline change with the falsification suite, not this script. Written 2026-10-02 after A2 of the 10-01 overnight
went from r@1min 0.19 (REJECT) to 0.323 (SCOREABLE) with its EMG notched.
usage: python3 qc/emg_mains_staging_test.py OUT DAY_DIR [DAY_DIR ...]
"""
import glob, json, os, sys
import numpy as np, scipy.signal as sg
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import pipeline.stage3_features as S3
out_root, days = sys.argv[1], sys.argv[2:]
real_load = np.load


class NpzDict(dict):
    """dict that also answers `.files`, like the NpzFile stage 3 normally gets."""
    @property
    def files(self):
        return list(self.keys())


def notched_load(path, allow_pickle=True, **kw):
    z = real_load(path, allow_pickle=allow_pickle, **kw); d = NpzDict({k: z[k] for k in z.files})
    fs = int(d["fs"]); emg = d["emg"].astype(np.float64)
    for f0 in (60.0, 120.0):
        if f0 < fs / 2 - 2:
            b, a = sg.iirnotch(f0, 30, fs); emg = sg.filtfilt(b, a, emg)
    d["emg"] = emg.astype(np.float32)
    return d


rows, checks = [], []
for day in days:
    files = sorted(glob.glob(os.path.join(day, "port*.npz")))
    res = {}
    for cond in ("orig", "notch"):
        od = os.path.join(out_root, cond, os.path.basename(os.path.normpath(day))); os.makedirs(od, exist_ok=True)
        S3.np.load = notched_load if cond == "notch" else real_load
        for f in files:
            link = os.path.join(od, os.path.basename(f))
            if os.path.lexists(link) and os.path.realpath(link) != os.path.realpath(f):
                # an OUT reused for a different day folder of the same name would silently re-test the OLD file
                sys.exit(f"{link} points to {os.path.realpath(link)}, not {os.path.realpath(f)}: use a fresh OUT")
            if not os.path.lexists(link):
                os.symlink(os.path.realpath(f), link)
            try:
                r = S3.analyse(link)
            except Exception as exc:
                print(f"  {cond} {os.path.basename(f)}: {type(exc).__name__}: {exc}"[:160])
                res.setdefault(os.path.basename(f), {})[cond] = ("ERROR", None, None, str(exc)[:60]); continue
            res.setdefault(os.path.basename(f), {})[cond] = (r["verdict"].split(":")[0], r["persistence"]["1min"]["r"],
                                                            r["wake_pct"], r["hours_in_blocks"])
    S3.np.load = real_load
    for f, d in res.items():
        o, n = d.get("orig"), d.get("notch")
        rows.append((os.path.basename(os.path.normpath(day)), f.split("_")[0], o, n))
        off = os.path.join(day, f[:-4] + "_features.json")                  # the METHOD CHECK: 'orig' must reproduce it
        if os.path.exists(off) and o:
            checks.append(json.load(open(off))["verdict"].split(":")[0] == o[0])
print(f"{'day':<22}{'mouse':<14}{'orig verdict':<14}{'r@1m':>7}{'wake%':>7} | {'notch verdict':<14}{'r@1m':>7}{'wake%':>7}")
for day, m, o, n in rows:
    fmt = lambda v: (f"{v[0]:<14}{(v[1] if v[1] is not None else float('nan')):7.3f}{(v[2] if v[2] is not None else float('nan')):7.1f}") if v else "-"
    print(f"{day:<22}{m:<14}{fmt(o)} | {fmt(n)}")
print(f"method check: 'orig' reproduces {sum(checks)}/{len(checks)} official verdicts found beside the inputs"
      + ("" if all(checks) else "  <-- MISMATCH: the diagnostic run is not the published stage 3"))
