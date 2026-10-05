"""Scan a whole Allego .xdat for SYSTEM-WIDE transients: one event on the wire-free floor inputs of chips on
EVERY port in the same 100 ms. Wire-free inputs carry no biology, so an event that reaches both ports at once is
electrical and building-wide (e.g. a light switch); one confined to a port is local (a hand, a tether, a mouse).

usage: python3 -m qc.allchip_scan_file BASE OUT.csv
Reads in 300 s chunks with np.fromfile + posix_fadvise(DONTNEED), so the page cache is not flooded.

Detector. 100 ms max |y| of y = the 50 ms comb x[t] - x[t-50 ms] (cancels 60 Hz and every harmonic, cannot ring),
band-passed 1-450 Hz, divided by that channel's chunk median; a chip is HIT when the median over its 14 floor
inputs exceeds 5x. (Until 2026-10-02 an 8-notch IIR chain did this: it rang 100-200 ms ahead of a sharp transient,
so rows came 1-2 windows early with a fraction of the true size -- review 2026-10-02.)
Vote (revised 2026-10-02 after the second review):
  * CONTAMINATION IS DECIDED ONCE PER FILE. A chip whose floor-hit rate over the file is > 10x the cleanest chip's
    (e.g. a railing open EMG on that chip) does not vote. Deciding it per 300 s chunk let busy chips back in.
  * A SYSTEM-WIDE event needs >= 75 % of the voting chips AND at least one voting chip on every port. A port-local
    disturbance plus one noisy chip on the other port used to pass as "all-chip".
  * Each event is a run of qualifying windows (gaps <= 0.5 s merged). It is reported at its PEAK window, with the
    maximum over the run of every chip's floor Z and of the EEG/EMG 100 ms peaks.
  * CHANCE = a LOCAL circular-shift null: within each 300 s chunk every port but the first is shifted 2-30 s against the
    others (chips of one port move together, so their dependence is kept) and the events that would qualify are counted.
    Shifting by up to a whole chunk let two ports that are busy together for a minute look coupled (review round 3).
  * Contamination counts never-hitting chips in the reference (zeros used to be skipped, letting railing chips vote);
    the scan warns when a port's only voter never hits. An event is placed at the earliest window reaching 0.8x its
    peak, not at the comb's echo.
Time origin = the file's status.start_time (UTC, ms) in KST, not the uid in the name.
"""
import os, sys, csv, json, datetime as dt
import numpy as np, scipy.signal as sg

NULL_SHIFTS, MERGE_S, ZHIT, CH_S = 200, 0.5, 5.0, 300
SHIFT_S = (2.0, 30.0)     # null shifts of one port vs the other: local in time (review 2026-10-02 round 3)


def need_of(n):
    return max(2, int(np.ceil(0.75 * n)))


def events_of(q, merge_w):
    """[(start, end)] runs of True in q, merging gaps of <= merge_w windows."""
    idx = np.flatnonzero(q)
    if idx.size == 0:
        return []
    out, s, e = [], idx[0], idx[0]
    for i in idx[1:]:
        if i - e <= merge_w:
            e = i
        else:
            out.append((s, e)); s = e = i
    out.append((s, e)); return out


def contamination(rate, port_of, nwin):
    """Voting chips: hit rate <= 10x the CLEANEST chip's, zeros included (a never-hitting chip used to be skipped as the
    reference, so busy chips set it and railing chips voted again: review round 3), floor = one hit per file; every port
    keeps its cleanest chip. Returns (vote, warnings)."""
    ref = max(float(rate.min()), 1.0 / max(nwin, 1)); vote = rate <= 10 * ref; warn = []
    for p in sorted(set(port_of)):
        m = port_of == p
        if m.any() and not (vote & m).any():
            vote[np.flatnonzero(m)[np.argmin(rate[m])]] = True
        if m.any() and not (rate[vote & m] > 0).any():
            warn.append(f"port {p}: its voting chip never hits in this span, so no system-wide event can be detected there")
    return vote, warn


def peak_window(score, s, e):
    """Earliest window of the run [s, e] reaching 0.8x the run's maximum score: the transient, not the 50 ms comb's
    equally large inverted echo, which an argmax picks half the time (review round 3)."""
    seg = score[s:e + 1]; return s + int(np.flatnonzero(seg >= 0.8 * seg.max())[0])


def shift_null(hit, vote, port_of, need, merge_w, lo_w, hi_w, rng, n_shifts=NULL_SHIFTS):
    """Expected number of qualifying EVENTS when every port but the first is shifted by +-[lo_w, hi_w] windows
    (circularly, within this span): keeps each port's own timing and within-port dependence, destroys only the
    cross-port alignment, and stays local in time so ports that are busy together for a minute do not look coupled."""
    n = hit.shape[1]; ports = sorted(set(port_of))
    if n < 2 * hi_w + 1:
        return 0.0
    tot = 0
    for _ in range(n_shifts):
        hs = hit.copy()
        for p in ports[1:]:
            m = port_of == p; hs[m] = np.roll(hit[m], int(rng.integers(lo_w, hi_w + 1)) * int(rng.choice([-1, 1])), axis=1)
        tot += len(events_of(qualify(hs, vote, port_of, need), merge_w))
    return tot / n_shifts


def qualify(hit, vote, port_of, need):
    """Windows where >= need voting chips hit and every port with a voter has a hit."""
    hv = hit[vote]; ok = hv.sum(0) >= need
    for p in sorted(set(port_of[vote])):
        ok &= hit[vote & (port_of == p)].any(0)
    return ok


def main(base, out):
    meta = json.load(open(base + ".xdat.json"))
    bm = meta["sapiens_base"]["biointerface_map"]; fs = int(meta["status"]["samp_freq"])
    assert fs % 20 == 0 and fs >= 500, f"fs={fs}: the 50 ms comb and 100 ms windows assume a 1 kHz-class rate"
    lab = [f"{p}/{s}" for p, s in zip(bm["port"], bm["site_num"])]; nch = len(lab); ix = {l: i for i, l in enumerate(lab)}
    ports = sorted({l.split("/")[0] for l in lab if l.split("/")[0] in "ABCD"})
    chips = [(p, s) for p in ports for s in (1, 33) if f"{p}/{s + 15}" in ix]
    names = [f"{p}{1 if s == 1 else 2}" for p, s in chips]; port_of = np.array([p for p, _ in chips])
    fl = {c: [ix[f"{c[0]}/{q}"] for q in range(c[1] + 2, c[1] + 16)] for c in chips}
    an = {c: [ix[f"{c[0]}/{c[1]}"], ix[f"{c[0]}/{c[1] + 1}"]] for c in chips}
    cols = sorted({i for c in chips for i in fl[c] + an[c]}); pos = {c: i for i, c in enumerate(cols)}
    start = (dt.datetime.fromisoformat(meta["status"]["start_time"].replace("Z", "+00:00")) + dt.timedelta(hours=9)).replace(tzinfo=None)
    path = base + "_data.xdat"; nsamp = os.path.getsize(path) // (nch * 4)
    W, DC, CH, PAD = fs // 10, fs // 20, CH_S * fs, 2 * fs
    sos = sg.butter(4, [1, 450], btype="band", fs=fs, output="sos")
    fd = os.open(path, os.O_RDONLY)
    FZ, EEG, EMG, chunk_of = [], [], [], []                     # per 100 ms window, whole file
    for ci, c0 in enumerate(range(0, nsamp, CH)):
        a, b = max(0, c0 - PAD), min(nsamp, c0 + CH + PAD)
        lo, hi = (c0 - a) // W, (min(nsamp, c0 + CH) - a) // W
        if hi <= lo:
            continue                                            # last chunk shorter than one window
        raw = np.fromfile(path, dtype=np.float32, count=(b - a) * nch, offset=a * nch * 4).reshape(b - a, nch)
        os.posix_fadvise(fd, a * nch * 4, (b - a) * nch * 4, os.POSIX_FADV_DONTNEED)
        D = np.ascontiguousarray(raw[:, cols].T, dtype=np.float64); del raw
        Y = np.zeros_like(D); Y[:, DC:] = D[:, DC:] - D[:, :-DC]; Y[:, :DC] = Y[:, DC:2 * DC]
        Y = sg.sosfiltfilt(sos, Y, axis=1)
        nw = Y.shape[1] // W; E = np.abs(Y[:, :nw * W]).reshape(len(cols), nw, W).max(2)
        Z = E / (np.median(E[:, lo:hi], 1, keepdims=True) + 1e-9)
        FZ.append(np.array([np.median(Z[[pos[i] for i in fl[c]]], 0) for c in chips])[:, lo:hi].astype(np.float32))
        EEG.append(np.array([E[pos[an[c][0]]] for c in chips])[:, lo:hi].astype(np.float32))
        EMG.append(np.array([E[pos[an[c][1]]] for c in chips])[:, lo:hi].astype(np.float32))
        chunk_of.append(np.full(hi - lo, ci))
        print(f"{(start + dt.timedelta(seconds=c0 / fs)):%m-%d %H:%M}  {100 * min(nsamp, c0 + CH) / nsamp:5.1f}%", flush=True)
    FZ, EEG, EMG, chunk_of = np.concatenate(FZ, 1), np.concatenate(EEG, 1), np.concatenate(EMG, 1), np.concatenate(chunk_of)
    hit = FZ > ZHIT; nwin = hit.shape[1]
    hit[:, :int(2 * fs / W)] = False; hit[:, -int(2 * fs / W):] = False          # file-edge filter artefact
    # ---- contamination, once per file
    rate = hit.mean(1); vote, warn = contamination(rate, port_of, nwin)
    need = need_of(int(vote.sum())); merge_w = int(round(MERGE_S * fs / W))
    q = qualify(hit, vote, port_of, need); evs = events_of(q, merge_w)
    # ---- chance: local circular-shift null (ports shifted 2-30 s against each other), per chunk
    rng = np.random.default_rng(0); expected = 0.0
    lo_w, hi_w = int(SHIFT_S[0] * fs / W), int(SHIFT_S[1] * fs / W)
    per_chunk = []
    for ci in np.unique(chunk_of):
        k = np.flatnonzero(chunk_of == ci); e_ = shift_null(hit[:, k], vote, port_of, need, merge_w, lo_w, hi_w, rng)
        expected += e_; per_chunk.append((k[0] * W / fs, (k[-1] + 1) * W / fs, e_))
    with open(out[:-4] + ".chance.csv" if out.endswith(".csv") else out + ".chance.csv", "w") as fh:   # lets a reader split chance by period
        fh.write("chunk_start_file_s,chunk_end_file_s,expected_events\n")
        fh.write("".join(f"{a_:.1f},{b_:.1f},{e_:.4f}\n" for a_, b_, e_ in per_chunk))
    with open(out, "w", newline="") as fh:
        wr = csv.writer(fh)
        wr.writerow(["t_s", "clock", "n_chips_hit", "ports_hit"] + [f"floorZ_{n}" for n in names] + [f"EEG_uV_{n}" for n in names]
                    + [f"EMG_uV_{n}" for n in names] + ["run_s", "n_voting", "excluded"])
        excl = "+".join(n for n, v in zip(names, vote) if not v)
        for s, e in evs:
            seg = slice(s, e + 1); pk = peak_window(FZ[vote].sum(0), s, e)
            t = pk * W / fs; nh = int(hit[vote, pk].sum()); ph = "+".join(p for p in ports if hit[vote & (port_of == p), pk].any())
            wr.writerow([f"{t:.1f}", (start + dt.timedelta(seconds=t)).strftime("%m-%d %H:%M:%S.%f")[:-5], nh, ph]
                        + [f"{v:.0f}" for v in FZ[:, seg].max(1)] + [f"{v:.0f}" for v in EEG[:, seg].max(1)]
                        + [f"{v:.0f}" for v in EMG[:, seg].max(1)] + [f"{(e - s + 1) * W / fs:.1f}", int(vote.sum()), excl])
    print(f"floor-hit rate per chip over the file (% of 100 ms windows): "
          + ", ".join(f"{n} {100 * r:.3f}" for n, r in zip(names, rate)) + f"; not voting: {excl or 'none'}")
    for w_ in warn:
        print("WARNING: " + w_)
    print(f"{len(evs)} system-wide events (>= {need} of {int(vote.sum())} voting chips, every port); chance from a local "
          f"circular-shift null (ports shifted {SHIFT_S[0]:g}-{SHIFT_S[1]:g} s against each other): {expected:.2f} events", flush=True)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
