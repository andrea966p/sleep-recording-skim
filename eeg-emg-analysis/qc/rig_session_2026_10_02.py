"""Figures for the 2026-10-02 rig session inside the light-phase run 8f84e3e62af6 (allego_0__uid1002-09-16-58).

  figG  the meter-probe tests at 1 s: meter ON hover/touch cycles (16:22) and meter OFF touch (16:27)
  figH  the whole run, one 10 s epoch every 3 min, plus the session (15:15-16:40) every 30 s, events shaded
Events come from the canonical marker list (qc/noise_mice_markers_2026_10_02.py), which also writes MARKERS_*.tsv.
This script writes NO marker file: until 2026-10-02 it rewrote trials/MARKERS.tsv from its own list on every run and
would have deleted rows added by hand (review 2026-10-02). Time origin = the file's status.start_time, not its name.
Non-mains muscle band = 100-450 Hz minus every bin within 2 Hz of a multiple of 20 Hz (+-1 leaked mains: review).
Reads ~1.6 GB of the file at idle priority, page cache dropped.
usage: nice -n 19 ionice -c3 python3 qc/rig_session_2026_10_02.py FIGDIR
"""
import os, sys, json, textwrap, datetime as dt
import numpy as np
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt, matplotlib.dates as mdates

HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, ".."))
import noise_mice_markers_2026_10_02 as MK
from core import qc_thresholds as T

FIGD = sys.argv[1]
BASE = os.path.join(MK.RAW, MK.RUNS["lightphase"]); T0a, fs, N, _ = MK.file_origin(MK.RUNS["lightphase"])
T0 = T0a.replace(tzinfo=None); fs = int(fs); assert fs == 1000
c = lambda s: dt.datetime.combine(T0.date(), dt.time.fromisoformat(s))
EV = [dict(r, t=T0 + dt.timedelta(seconds=r["file_s"]), te=T0 + dt.timedelta(seconds=r["file_s_end"]) if r["file_s_end"] != "" else None)
      for r in MK.rows("lightphase")]            # from file_s, not the 0.1 s clock strings (review round 3)
SESSION = (c("15:15:00"), c("16:40:00"))
meta = json.load(open(BASE + ".xdat.json")); bm = meta["sapiens_base"]["biointerface_map"]
lab = [f"{p}/{s}" for p, s in zip(bm["port"], bm["site_num"])]; nch = len(lab); ix = {l: i for i, l in enumerate(lab)}
path = BASE + "_data.xdat"; fd = os.open(path, os.O_RDONLY); n = N - 3 * fs
CH = {"A1": ("A", 1), "A2": ("A", 33), "B1": ("B", 1), "B2": ("B", 33)}
COL = {"A1": "0.55", "A2": "tab:blue", "B1": "tab:red", "B2": "tab:purple"}
FL = {k: [ix[f"{p}/{q}"] for q in range(b + 2, b + 16)] for k, (p, b) in CH.items()}


def read(a, m):
    x = np.fromfile(path, dtype=np.float32, count=m * nch, offset=a * nch * 4).reshape(m, nch)
    os.posix_fadvise(fd, a * nch * 4, m * nch * 4, os.POSIX_FADV_DONTNEED); return x.astype(np.float64)


def epochs(t_start, t_end, step):          # gate-style 60 Hz line, 10 s epochs every `step` s
    ep = 10 * fs; w = np.hanning(ep); g = w.sum() / 2; fq = np.fft.rfftfreq(ep, 1 / fs); m60 = (fq >= 59) & (fq <= 61)
    tt, fl, emg = [], {k: [] for k in CH}, []
    for a in range(int(t_start * fs), min(int(t_end * fs), n - ep), int(step * fs)):
        X = read(a, ep); X -= X.mean(0); P = (np.abs(np.fft.rfft(X * w[:, None], axis=0)) / g)[m60].max(0)
        for k in CH: fl[k].append(np.median(P[FL[k]]))
        emg.append(P[ix["A/34"]]); tt.append(T0 + dt.timedelta(seconds=a / fs + 5))
    return np.array(tt), {k: np.array(v) for k, v in fl.items()}, np.array(emg)


def seconds(start, nsec):                   # 1 s Hann: 60 Hz line on floors and A2 EMG, A2 EMG muscle band
    a = int(round((c(start) - T0).total_seconds() * fs)); X = read(a, nsec * fs)
    w = np.hanning(fs); g = w.sum() / 2; f = np.fft.rfftfreq(fs, 1 / fs)
    hi = (np.abs((f + 10) % 20 - 10) > 2) & (f >= 100) & (f <= 450)
    def S(cols):
        Y = X[:, cols].reshape(nsec, fs, len(cols)); Y = Y - Y.mean(1, keepdims=True); return np.fft.rfft(Y * w[None, :, None], axis=1)
    fl = {k: np.median(np.abs(S(FL[k])[:, 60]) / g, 1) for k in CH}
    E = S([ix["A/34"]])[:, :, 0]; line = np.abs(E[:, 60]) / g
    musc = np.sqrt((np.abs(E) ** 2 / (fs * (w ** 2).sum()) * 2)[:, hi].sum(1))
    return np.array([T0 + dt.timedelta(seconds=a / fs + k + .5) for k in range(nsec)]), fl, line, musc


def inside(t, spans):
    m = np.zeros(len(t), bool)
    for s, e in spans:
        m |= (t >= s) & (t < e)
    return m


# ---- fig G: probe tests
touches = [(r["t"], r["te"]) for r in EV if r["event"].strip().startswith("touch") and "meter ON" in r["event"]]   # the 4 contacts, not the umbrella row
off = [(r["t"], r["te"]) for r in EV if r["event"].startswith("meter OFF")]
umbrella = [r for r in EV if r["event"].startswith("meter ON")][0]
panels = [("16:21:30", 115, "meter ON: hover / touch on A2's foil (black on chassis lug)", touches),
          ("16:26:45", 45, "meter OFF: floating lead touching A2's foil", off)]
fig, ax = plt.subplots(3, 2, figsize=(14, 9), sharex="col"); res = []
for col, (start, nsec, title, spans) in enumerate(panels):
    t, fl, line, musc = seconds(start, nsec); on = inside(t, spans)
    away = ~on & ~inside(t, [(s - dt.timedelta(seconds=2), e + dt.timedelta(seconds=2)) for s, e in spans])   # not within 2 s of a touch
    before = t < (umbrella["t"] - dt.timedelta(seconds=1) if col == 0 else spans[0][0] - dt.timedelta(seconds=2))   # no probe near the foil yet
    res.append(dict(title=title, a2=np.median(fl["A2"][on]) / np.median(fl["A2"][away]),
                    a2_vs_before=np.median(fl["A2"][on]) / np.median(fl["A2"][before]),
                    others=[np.median(fl[k][on]) / np.median(fl[k][away]) for k in ("A1", "B1", "B2")],
                    a2fl=(np.median(fl["A2"][away]), np.median(fl["A2"][on])), line=(np.median(line[away]), np.median(line[on])),
                    musc=(np.median(musc[away]), np.median(musc[on]))))
    for k in CH: ax[0, col].plot(t, fl[k], color=COL[k], lw=1, label=f"{k} floor")
    ax[1, col].plot(t, line, color="tab:blue", lw=1); ax[2, col].plot(t, musc, color="tab:green", lw=1)
    for s, e in spans:
        for a_ in ax[:, col]: a_.axvspan(s, e, color="tab:orange", alpha=.2)
    ax[0, col].set_title(title, loc="left", fontsize=9.5); ax[0, col].set_yscale("log"); ax[0, col].legend(fontsize=7.5, ncol=4)
    ax[2, col].xaxis.set_major_formatter(mdates.DateFormatter("%H:%M:%S"))
for r in res:
    print(f"{r['title']}: A2 floor {r['a2fl'][0]:.0f} -> {r['a2fl'][1]:.0f} uV (x{r['a2']:.2f}); other floors x"
          + "/".join(f"{v:.2f}" for v in r["others"]) + f"; touch vs before any probe x{r['a2_vs_before']:.2f}; A2 EMG 60 Hz {r['line'][0]:.1f} -> {r['line'][1]:.1f} uV; "
          f"muscle band {r['musc'][0]:.1f} -> {r['musc'][1]:.1f} uV")
ax[0, 0].set_ylabel("floor 60 Hz line\n(uV peak, 1 s)"); ax[1, 0].set_ylabel("A2 EMG 60 Hz line\n(uV peak, 1 s)")
ax[2, 0].set_ylabel("A2 EMG muscle band\n100-450 Hz non-mains (uV rms)")
rON, rOFF = res
fig.suptitle(textwrap.fill(
    f"Probe tests on A2's foil, 2026-10-02 (orange = red tip touching the foil; medians, touching vs not). Meter ON: A2 floor x{rON['a2']:.2f} "
    f"vs hovering, x{rON['a2_vs_before']:.2f} vs before the probe came near, "
    f"other floors x{min(rON['others']):.2f}-{max(rON['others']):.2f}, A2 EMG 60 Hz x{rON['line'][1] / rON['line'][0]:.2f}. Meter OFF (floating "
    f"lead): A2 floor x{rOFF['a2']:.2f}, A2 EMG 60 Hz x{rOFF['line'][1] / rOFF['line'][0]:.2f} while its muscle band goes "
    f"x{rOFF['musc'][1] / rOFF['musc'][0]:.2f}: pickup, not movement", 160), fontsize=9.5)
fig.tight_layout(); fig.savefig(os.path.join(FIGD, "2026-10-02-noise-figG-probe-tests.png"), dpi=105); plt.close(fig)

# ---- fig H: whole run + session detail
t1, fl1, emg1 = epochs(0, n / fs - 15, 180)
t2, fl2, emg2 = epochs((SESSION[0] - T0).total_seconds(), (SESSION[1] - T0).total_seconds(), 30)
fig, ax = plt.subplots(2, 2, figsize=(15, 8), gridspec_kw=dict(width_ratios=[2, 1.3]))
for (tt, fl, emg), col in (((t1, fl1, emg1), 0), ((t2, fl2, emg2), 1)):
    for k in CH: ax[0, col].plot(tt, fl[k], ".-" if col else ".", ms=3, lw=.6, color=COL[k], label=f"{k} floor")
    ax[1, col].plot(tt, emg, ".-" if col else ".", ms=3, lw=.6, color="tab:blue", label="A2 EMG 60 Hz")
    ax[0, col].axhline(T.FLOOR_MIN_HUM_UV, color="k", ls="--", lw=.8); ax[0, col].set_yscale("log")
    for a_ in ax[:, col]:
        a_.grid(alpha=.25); a_.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))
for r in EV:
    if r["kind"] in ("test", "disturbance") and SESSION[0] <= r["t"] < SESSION[1]:
        for a_ in ax[:, 1]: a_.axvspan(r["t"], r["te"] or r["t"] + dt.timedelta(seconds=30), color="tab:orange", alpha=.25)
for a_ in ax[:, 1]: a_.set_xlim(*SESSION)
for a_ in ax[:, 0]: a_.axvspan(c("15:19:33"), c("16:33:30"), color="tab:orange", alpha=.15)
first, last = t1 < t1[0] + dt.timedelta(hours=1), t1 >= t1[-1] - dt.timedelta(hours=1)
b1a, b1b = np.median(fl1["B1"][first]), np.median(fl1["B1"][last]); e_a, e_b = np.median(emg1[first]), np.median(emg1[last])
ax[0, 0].set_title("whole light-phase run (one 10 s epoch every 3 min); shaded = Andrea's visit (15:19:33-16:33:30 by the data)", loc="left", fontsize=9.5)
ax[0, 1].set_title(f"{SESSION[0]:%H:%M}-{SESSION[1]:%H:%M}, one 10 s epoch every 30 s;\nshaded = each test or disturbance (canonical markers)", loc="left", fontsize=9.5)
ax[0, 0].set_ylabel("chip floor 60 Hz (uV peak, gate scale)"); ax[1, 0].set_ylabel("A2 EMG 60 Hz (uV peak)")
ax[0, 0].legend(fontsize=7.5, ncol=4); ax[1, 0].legend(fontsize=7.5)
print(f"B1 floor first hour {b1a:.0f} -> last hour {b1b:.0f} uV; A2 EMG 60 Hz {e_a:.1f} -> {e_b:.1f} uV")
fig.suptitle(textwrap.fill(f"Light-phase run 8f84e3e62af6, 2026-10-02: B1's floor goes {b1a:.0f} -> {b1b:.0f} uV (first vs last hour, untouched; gate "
             f"{T.FLOOR_MIN_HUM_UV:.0f}) and A2's EMG 60 Hz {e_a:.1f} -> {e_b:.1f} uV; the session's interventions are brief and the large ones "
             "local to A2", 165), fontsize=10)
fig.tight_layout(); fig.savefig(os.path.join(FIGD, "2026-10-02-noise-figH-light-phase-run-overview.png"), dpi=105); plt.close(fig)
print("figG + figH written")
