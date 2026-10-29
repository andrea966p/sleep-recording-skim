"""Floor hits and animal spikes over a whole (even live) .xdat, counted as EVENTS (revised 2026-10-02).

Per 100 ms window:
  floor hit    : the chip-median of its 14 wire-free inputs' window max|x| (1-450 Hz) > 5x that
                 channel's chunk median (the allchip_scan_file rule, on comb-cleaned data)
  animal spike : window max|x| > 8 robust SD of the channel (1-100 Hz, comb-cleaned)
Mains is removed with the documented 3-cycle comb x[t] - x[t-50 ms] (D = fs/20), which nulls 60 Hz and
every harmonic and cannot ring. It does add an inverted echo 50 ms later, so hit windows are MERGED into
events (gaps <= 1 window) before anything is counted, and coincidence is EVENT overlap, not same-window.
The first version used a 150 ms comb without merging: every transient counted about twice, and an EEG
spike plus an EMG spike 150 ms apart counted as "same 100 ms" (code review 2026-10-02).
usage: python3 qc/night_spikes.py BASE
"""
import datetime as dt
import os, sys, json, numpy as np, scipy.signal as sg
base = sys.argv[1]
meta = json.load(open(base + ".xdat.json")); bm = meta["sapiens_base"]["biointerface_map"]
fs = int(meta["status"]["samp_freq"]); lab = [f"{p}/{s}" for p, s in zip(bm["port"], bm["site_num"])]; nch = len(lab)
assert fs % 20 == 0 and fs >= 500, f"fs={fs}: the 50 ms comb and 100 ms windows assume a 1 kHz-class rate"
ix = {l: i for i, l in enumerate(lab)}; path = base + "_data.xdat"; nsamp = os.path.getsize(path) // (nch * 4) - 5 * fs
fd = os.open(path, os.O_RDONLY)
ports = sorted({l.split("/")[0] for l in lab if l.split("/")[0] in "ABCD"})
chips = {f"{p}{k}": (p, b) for p in ports for k, b in ((1, 1), (2, 33))}
fl = {c: [ix[f"{p}/{q}"] for q in range(b + 2, b + 16)] for c, (p, b) in chips.items()}
an = {c: (ix[f"{p}/{b}"], ix[f"{p}/{b+1}"]) for c, (p, b) in chips.items()}
sosF = sg.butter(4, [1, 450], btype="band", fs=fs, output="sos"); sosA = sg.butter(4, [1, 100], btype="band", fs=fs, output="sos")
D, W, CH, PAD = fs // 20, fs // 10, 300 * fs, 2 * fs
H = {k: [] for k in [f"fl_{c}" for c in chips] + [f"eeg_{c}" for c in chips] + [f"emg_{c}" for c in chips]}
for c0 in range(2 * fs, nsamp, CH):
    a, b = c0 - PAD, min(nsamp, c0 + CH) + PAD
    X = np.fromfile(path, dtype=np.float32, count=(b - a) * nch, offset=a * nch * 4).reshape(b - a, nch)
    os.posix_fadvise(fd, a * nch * 4, (b - a) * nch * 4, os.POSIX_FADV_DONTNEED)
    cols = sorted({i for c in chips for i in fl[c] + list(an[c])}); P = {c: k for k, c in enumerate(cols)}
    Dx = X[:, cols].astype(np.float64).T; del X
    Dx = Dx[:, D:] - Dx[:, :-D]                                   # sample j <-> original a + D + j
    n = (min(nsamp, c0 + CH) - c0) // W
    s0 = c0 - a - D                                               # chunk start in comb coordinates
    def wmax(Y): Y = np.abs(Y[:, s0:s0 + n * W]); return Y.reshape(Y.shape[0], n, W).max(2)
    YF = wmax(sg.sosfiltfilt(sosF, Dx[[P[i] for c in chips for i in fl[c]]], axis=1))
    zF = YF / np.median(YF, 1, keepdims=True); k = 0
    for c in chips:
        H[f"fl_{c}"].append(np.median(zF[k:k + 14], 0) > 5); k += 14
    YA = sg.sosfiltfilt(sosA, Dx[[P[i] for c in chips for i in an[c]]], axis=1)
    med = np.median(YA, 1, keepdims=True); mad = np.median(np.abs(YA - med), 1, keepdims=True) * 1.4826 + 1e-9
    ZA = wmax((YA - med) / mad) > 8; k = 0
    for c in chips:
        H[f"eeg_{c}"].append(ZA[k]); H[f"emg_{c}"].append(ZA[k + 1]); k += 2
H = {k: np.concatenate(v) for k, v in H.items()}; nwin = len(H["fl_A1"]); hrs = nwin * W / fs / 3600
CHUNK_W = 30 * fs // W     # chance strata of 30 s: 300 s still let two trains busy together for a minute look coupled (review round 3)


def events(h, gap=1):
    """Runs of hit windows, merging runs separated by <= gap empty windows -> [(start, end)] inclusive."""
    idx = np.flatnonzero(h)
    if idx.size == 0:
        return []
    out, s, e = [], idx[0], idx[0]
    for i in idx[1:]:
        if i - e <= gap + 1: e = i
        else: out.append((s, e)); s = e = i
    out.append((s, e)); return out


def overlap(ev_a, h_b):
    """How many events of A have at least one hit window of B inside their span."""
    return sum(bool(h_b[s:e + 1].any()) for s, e in ev_a)


EV = {k: events(v) for k, v in H.items()}
_fr = {c: H[f"fl_{c}"].mean() for c in chips}; _ref = max(min(_fr.values()), 1 / nwin)   # zeros INCLUDED (review round 3)
clean_set = {c for c in chips if _fr[c] <= 10 * _ref}
for _p in ports:                                                    # as allchip_scan_file: every port keeps its cleanest chip
    _pc = [c for c in chips if c.startswith(_p)]
    if _pc and not clean_set & set(_pc):
        clean_set.add(min(_pc, key=lambda c: _fr[c]))
print(f"{hrs:.2f} h scanned, {nwin} windows of 100 ms; counts are EVENTS (merged runs), per hour\n")
other = {c: [o for o in chips if o[0] != c[0]] for c in chips}
print("chip  floor ev/h | EEG ev/h  EMG ev/h  EEG&EMG ev/h | of those: own floor hit, other-port CLEAN floor hit")
for c in chips:
    both = [ev for ev in events(H[f"eeg_{c}"]) if H[f"emg_{c}"][ev[0]:ev[1] + 1].any()]
    oth = np.any([H[f"fl_{o}"] for o in other[c] if o in clean_set] or [np.zeros(nwin, bool)], 0)   # clean chips only
    print(f"{c}    {len(EV[f'fl_{c}'])/hrs:9.1f} | {len(EV[f'eeg_{c}'])/hrs:8.1f}  {len(EV[f'emg_{c}'])/hrs:8.1f}  {len(both)/hrs:11.1f} | "
          f"{overlap(both, H[f'fl_{c}'])}/{len(both)},  {overlap(both, oth)}/{len(both)} (other port = {'+'.join(other[c])})")
# CLEAN = floor-hit rate <= 10x the cleanest chip's over the file: the same rule as qc/allchip_scan_file.py (a fixed
# 200 events/h cut let B2 at 202/h out by 1 %, and would let a busy chip in on another rig -- review 2026-10-02)
clean = [c for c in chips if c in clean_set]                         # same set as above (file rule + cleanest chip per port)
print(f"\nclean floors (hit rate <= 10x the cleanest chip's, or the cleanest on its port): {', '.join(clean)}  ("
      + ", ".join(f"{c} {len(EV[f'fl_{c}']) / hrs:.1f}/h" for c in chips) + ")")
for _p in ports:
    if not any(_fr[c] > 0 for c in clean if c.startswith(_p)):
        print(f"WARNING: port {_p}: its clean floor never hits, so coincidences with it cannot be seen")
for i, a_ in enumerate(clean):
    for b_ in clean[i + 1:]:
        ea, hb = EV[f"fl_{a_}"], H[f"fl_{b_}"]
        # chance per 30 s stratum: A's event windows in it x B's hit rate in it. A whole-file (or 300 s) product is too
        # low when both rates rise together (a person at the rig): reviews 2026-10-02.
        exp = 0.0
        for k0 in range(0, nwin, CHUNK_W):
            k1 = min(nwin, k0 + CHUNK_W); nA = sum(max(0, min(e, k1 - 1) - max(s, k0) + 1) for s, e in ea)
            exp += nA * hb[k0:k1].mean()
        print(f"  {a_} events {len(ea)}, {b_} events {len(EV[f'fl_{b_}'])}; {a_} events overlapping a {b_} hit: "
              f"{overlap(ea, hb)} (chance ~{exp:.2f})")
        # when: clock time of each coincident event (window k starts at sample 2*fs + k*W), to check against known events
        # astimezone, not "+9 h": Allego 4 writes start_time in KST (+09:00), Allego 3 in UTC (Z). 2026-10-28
        t0 = dt.datetime.fromisoformat(meta["status"]["start_time"].replace("Z", "+00:00")).astimezone(dt.timezone(dt.timedelta(hours=9))).replace(tzinfo=None)
        hits = [s + int(np.flatnonzero(hb[s:e + 1])[0]) for s, e in ea if hb[s:e + 1].any()]   # the coincident instant: B's first hit
        if hits:
            print("    at " + ", ".join(f"{t0 + dt.timedelta(seconds=2 + s * W / fs):%m-%d %H:%M:%S.%f}"[:-5] for s in hits))
