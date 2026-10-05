"""Presence / hand / wireless-receiver test of 2026-10-02 16:03-16:07 (Andrea at the rig, light-phase run 8f84e3e62af6).

Andrea's log: 16:03 in, standing 50 cm in front of the headstages, hand brought close to each (no touching); 16:04 out;
16:05 in again, waving hands; 16:06 waving a powered wireless EEG/EMG receiver (custom, 4 antennas, on the Dell PC) near
the headstages. Question: does a person, a hand, or that receiver show on the floors AND on the mice's EEG/EMG?

Per 1 s (1 s Hann, 1 Hz bins): 60 Hz line amplitude (peak), and a NON-MAINS band rms that drops every bin within 2 Hz of a
multiple of 20 Hz (at fs = 1000 every mains harmonic, folded or not, sits on a multiple of 20 Hz; a 1 s Hann main lobe
spans +-2 bins, so +-1 leaked mains on the floors: review 2026-10-02), for 1-45 and 100-450 Hz.
Window medians compare the conditions; a Welch comparison (receiver vs hand-waving) lists lines that appear only with the receiver.
Reads 16:00-16:09 only (~0.3 GB) at idle priority. Time origin = the file's status.start_time (09:16:58.153), not its name.
usage: nice -n 19 ionice -c3 python3 qc/presence_test_2026_10_02.py FIG.png
"""
import os, sys, json, datetime as dt
import numpy as np, scipy.signal as sg
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt, matplotlib.dates as mdates
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import noise_mice_markers_2026_10_02 as MK

BASE = os.path.join(MK.RAW, MK.RUNS["lightphase"])         # one source for the path AND the origin
T_FILE = MK.file_origin(MK.RUNS["lightphase"])[0].replace(tzinfo=None)
DAY = dt.date(2026, 10, 2)
WIN = [("absent (before)", "16:00:00", "16:03:00"), ("in front 50 cm + hand near each", "16:03:00", "16:04:00"),
       ("absent", "16:04:00", "16:05:00"), ("in front, waving hands", "16:05:00", "16:06:00"),
       ("waving wireless receiver", "16:06:00", "16:07:00"), ("after", "16:07:00", "16:09:00")]
END = "16:09:00"
FIG = sys.argv[1]

meta = json.load(open(BASE + ".xdat.json")); bm = meta["sapiens_base"]["biointerface_map"]
fs = int(meta["status"]["samp_freq"]); assert fs == 1000
lab = [f"{p}/{s}" for p, s in zip(bm["port"], bm["site_num"])]; nch = len(lab); ix = {l: i for i, l in enumerate(lab)}
path = BASE + "_data.xdat"; fd = os.open(path, os.O_RDONLY)
n_now = os.path.getsize(path) // (nch * 4) - 3 * fs
clk = lambda s: dt.datetime.combine(DAY, dt.time.fromisoformat(s))
a0 = int(round((clk("16:00:00") - T_FILE).total_seconds() * fs)); a1 = min(n_now, int(round((clk(END) - T_FILE).total_seconds() * fs)))
X = np.fromfile(path, dtype=np.float32, count=(a1 - a0) * nch, offset=a0 * nch * 4).reshape(-1, nch)
os.posix_fadvise(fd, a0 * nch * 4, (a1 - a0) * nch * 4, os.POSIX_FADV_DONTNEED)
CH = {"A1": ("A", 1), "A2": ("A", 33), "B1": ("B", 1), "B2": ("B", 33)}
FLOOR = {c: [ix[f"{p}/{q}"] for q in range(b + 2, b + 16)] for c, (p, b) in CH.items()}
ANI = {"A2 EEG": "A/33", "A2 EMG": "A/34", "B1 EEG": "B/1", "B1 EMG": "B/2", "A1 EEG": "A/1", "B2 EEG": "B/33",
       "A1 EMG (open)": "A/2", "B2 EMG (open)": "B/34"}
nsec = X.shape[0] // fs
f = np.fft.rfftfreq(fs, 1 / fs); w = np.hanning(fs); g = w.sum() / 2
keep = (np.abs((f + 10) % 20 - 10) > 2.0)                         # drop bins within 2 Hz of any multiple of 20 Hz
lo, hi = keep & (f >= 1) & (f <= 45), keep & (f >= 100) & (f <= 450)
def per_sec(cols):
    Y = X[: nsec * fs, cols].astype(np.float64).reshape(nsec, fs, len(cols)); Y = Y - Y.mean(1, keepdims=True)
    S = np.fft.rfft(Y * w[None, :, None], axis=1)
    line = np.abs(S[:, 60]) / g
    psd = (np.abs(S) ** 2) / (fs * (w ** 2).sum()) * 2           # one-sided PSD, uV^2/Hz, 1 Hz bins
    return line, np.sqrt(psd[:, lo].sum(1)), np.sqrt(psd[:, hi].sum(1))
t = [T_FILE + dt.timedelta(seconds=a0 / fs + k + .5) for k in range(nsec)]
res = {}
for c, cols in FLOOR.items():
    L, B, H = per_sec(cols); res[c + " floor"] = (np.median(L, 1), np.median(B, 1), np.median(H, 1))
for name, site in ANI.items():
    L, B, H = per_sec([ix[site]]); res[name] = (L[:, 0], B[:, 0], H[:, 0])

def wmask(s, e):
    s0, e0 = clk(s), (clk(e) if e else t[-1] + dt.timedelta(seconds=1))
    return np.array([s0 <= x < e0 for x in t])
print(f"{t[0]:%H:%M:%S} - {t[-1]:%H:%M:%S}, {nsec} s. Window medians (uV): 60 Hz line peak | non-mains 1-45 | non-mains 100-450")
hdr = "".join(f"{name[:22]:>24s}" for name, _, _ in WIN)
for key in ["A1 floor", "A2 floor", "B1 floor", "B2 floor", "A2 EEG", "A2 EMG", "B1 EEG", "B1 EMG", "A1 EEG", "B2 EEG",
            "A1 EMG (open)", "B2 EMG (open)"]:
    L, B, H = res[key]
    cells = []
    for _, s, e in WIN:
        m = wmask(s, e)
        cells.append(f"{np.median(L[m]):7.1f} {np.median(B[m]):6.1f} {np.median(H[m]):6.1f}" if m.any() else " " * 21)
    print(f"{key:14s} " + " | ".join(cells))
print("windows: " + " | ".join(f"{n} {s}-{e or 'now'}" for n, s, e in WIN))

# brief events: the most extreme 1 s value per window, relative to the "absent (before)" median
m0 = wmask("16:00:00", "16:03:00")
print("\nmost extreme 1 s value per window, x the 'absent (before)' median (floors/mice 60 Hz: min and max; non-mains 100-450: max)")
for key in ["A1 floor", "A2 floor", "B1 floor", "B2 floor", "A2 EEG", "A2 EMG", "B1 EEG", "B1 EMG", "A1 EMG (open)", "B2 EMG (open)"]:
    L, B, H = res[key]; ref_l, ref_h = np.median(L[m0]), np.median(H[m0]); cells = []
    for _, s, e in WIN[1:]:
        m = wmask(s, e)
        cells.append(f"60Hz {L[m].min()/ref_l:4.2f}-{L[m].max()/ref_l:4.2f} hf<= {H[m].max()/ref_h:5.1f}" if m.any() else " " * 26)
    print(f"{key:14s} " + " | ".join(cells))

# lines that appear only with the receiver: Welch, receiver vs hand-waving (person present in both)
m3, m4 = wmask("16:05:00", "16:06:00"), wmask("16:06:00", "16:07:00")
def welch(cols, m):
    k = np.where(m)[0]
    if k.size < 8:
        return None, None
    seg = X[k[0] * fs:(k[-1] + 1) * fs][:, cols].astype(float)
    fw, P = sg.welch(seg, fs=fs, nperseg=4 * fs, axis=0); return fw, np.median(P, axis=1) if P.ndim > 1 else P
print("\nreceiver (16:06) vs hand-waving (16:05): bins >= 4x up, mains multiples of 20 Hz excluded (Welch 4 s, 0.25 Hz bins)")
for name, cols in [("floors A2 chip", FLOOR["A2"]), ("floors B1 chip", FLOOR["B1"]), ("A2 EEG", [ix["A/33"]]),
                   ("A2 EMG", [ix["A/34"]]), ("B1 EEG", [ix["B/1"]]), ("B1 EMG", [ix["B/2"]]),
                   ("A1 EMG open", [ix["A/2"]]), ("B2 EMG open", [ix["B/34"]])]:
    fw, P3 = welch(cols, m3); _, P4 = welch(cols, m4)
    if fw is None or P4 is None:
        print(f"  {name:14s} (window not in the file)"); continue
    ok = (np.abs((fw + 10) % 20 - 10) > 0.5) & (fw > 1) & (fw < 495)
    r = np.where(ok, P4 / (P3 + 1e-12), 0); top = np.argsort(r)[::-1][:6]
    hits = [f"{fw[i]:.2f} Hz x{r[i]:.0f}" for i in top if r[i] >= 4]
    print(f"  {name:14s} " + (", ".join(hits) if hits else "nothing >= 4x"))

# figure
fig, ax = plt.subplots(4, 1, figsize=(12, 12), sharex=True)
for c, col in zip(CH, ["0.55", "tab:blue", "tab:red", "tab:purple"]):
    ax[0].plot(t, res[c + " floor"][0], lw=.8, color=col, label=f"{c} floor")
for key, col in [("A2 EMG", "tab:blue"), ("B1 EMG", "tab:red"), ("A2 EEG", "tab:cyan"), ("B1 EEG", "tab:orange")]:
    ax[1].plot(t, res[key][0], lw=.8, color=col, label=key)
for key, col in [("A2 EMG", "tab:blue"), ("B1 EMG", "tab:red"), ("A2 floor", "k"), ("B1 floor", "0.5")]:
    ax[2].plot(t, res[key][2], lw=.8, color=col, label=key)
for key, col in [("A1 EMG (open)", "0.55"), ("B2 EMG (open)", "tab:purple")]:
    ax[3].plot(t, res[key][0], lw=.8, color=col, label=key)
ax[0].set_yscale("log"); ax[0].set_ylabel("floor 60 Hz line\n(uV peak, 1 s)")
ax[1].set_ylabel("60 Hz line on the mice\n(uV peak, 1 s)"); ax[1].set_yscale("log")
ax[2].set_ylabel("non-mains 100-450 Hz\n(uV rms, 1 s)"); ax[2].set_yscale("log")
ax[3].set_ylabel("open EMG 60 Hz\n(uV peak, 1 s)")
shade = {"in front 50 cm + hand near each": "tab:orange", "in front, waving hands": "tab:green", "waving wireless receiver": "tab:red"}
for a in ax:
    for name, s, e in WIN:
        if name in shade:
            a.axvspan(clk(s), clk(e), color=shade[name], alpha=.12)
    a.legend(fontsize=7.5, ncol=4, loc="upper left"); a.grid(alpha=.25)
for name, s, e in WIN:
    if name in shade:
        ax[0].text(clk(s), ax[0].get_ylim()[1], " " + name, fontsize=7.5, va="top", color=shade[name])
ax[3].xaxis.set_major_formatter(mdates.DateFormatter("%H:%M")); ax[3].set_xlabel("clock time 2026-10-02 (Andrea's log; absent outside the shaded windows)")
fig.suptitle(f"Presence test at the rig, 2026-10-02 {WIN[0][1][:5]}-{END[:5]}: person, hands and a powered wireless receiver near the headstages", fontsize=10.5)
fig.tight_layout(); fig.savefig(FIG, dpi=105); print("figure ->", FIG)
