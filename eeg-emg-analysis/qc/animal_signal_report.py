"""Deep signal report for ONE animal, with its own in-file floor and a light/dark split.

Answers "how does this animal's signal actually look", rather than "does it pass a gate":
  - per 10 s epoch: rms, 60 Hz, railing, 1-40 Hz spectral slope, delta / theta / sigma ratios
  - usable fraction by the SLOPE criterion, split by LIGHT and DARK phase
  - longest unbroken usable block
  - EMG state dependence: does muscle tone fall when delta rises
  - a quick sleep/wake read from delta, WITH the +/-25% threshold sweep, because the circadian
    number is threshold-dependent and quoting it without the sweep is not allowed here

⚠️ The slope criterion is for EEG. EMG is broadband and is judged by state dependence instead.
⚠️ ZT is derived from the recording start time and the light schedule, NOT from any clock in the
   data. Lights on 09:00, lights off 21:00 KST, so ZT0 = 09:00.

Usage:
  python animal_signal_report.py BASE --eeg A/33 --emg A/34 [--port A] [--max-hours H]
"""
import argparse, json, os
from datetime import datetime
import numpy as np

ap = argparse.ArgumentParser()
ap.add_argument("base")
ap.add_argument("--eeg", required=True)
ap.add_argument("--emg", required=True)
ap.add_argument("--port", default=None, help="floor port, defaults to the EEG channel's port")
ap.add_argument("--max-hours", type=float, default=None)
ap.add_argument("--lights-on", type=int, default=9)
ap.add_argument("--lights-off", type=int, default=21)
args = ap.parse_args()

BASE = args.base
EPOCH_S = 10
RAIL_UV = 6389.6
RMS_LO, RMS_HI = 10.0, 150.0
PORT = args.port or args.eeg.split("/")[0]

d = json.load(open(BASE + ".xdat.json"))
bm = d["sapiens_base"]["biointerface_map"]
fs = int(d["status"]["samp_freq"])
lab = [f"{p}/{s}" for p, s in zip(bm["port"], bm["site_num"])]
nch = len(lab)
nsamp = os.path.getsize(BASE + "_data.xdat") // (nch * 4)
x = np.memmap(BASE + "_data.xdat", dtype=np.float32, mode="r", shape=(nsamp, nch))
ep = fs * EPOCH_S
nep = nsamp // ep
if args.max_hours:
    nep = min(nep, int(args.max_hours * 3600 // EPOCH_S))

# recording start time from the filename stamp: allego_0__uidMMDD-HH-MM-SS
stamp = os.path.basename(BASE).split("uid")[1]
mm, dd = int(stamp[0:2]), int(stamp[2:4])
hh, mi, ss = int(stamp[5:7]), int(stamp[8:10]), int(stamp[11:13])
t0 = datetime(2026, mm, dd, hh, mi, ss)
print(f"{os.path.basename(BASE)}   start {t0:%Y-%m-%d %H:%M:%S}   fs={fs}")
print(f"scoring {nep*EPOCH_S/3600:.2f} h, {nep} epochs of {EPOCH_S} s")
print(f"EEG {args.eeg}   EMG {args.emg}   floor = port {PORT} /4-/16 and /36-/48\n")

FLOOR = [f"{PORT}/{i}" for i in list(range(4, 17)) + list(range(36, 49))]
SITES = [args.eeg, args.emg] + FLOOR
cols = np.array([lab.index(s) for s in SITES])

freqs = np.fft.rfftfreq(ep, 1 / fs)
band = (freqs >= 1) & (freqs <= 40)
lgf = np.log10(freqs[band]); lgf_c = lgf - lgf.mean(); lgv = float((lgf_c ** 2).sum())
m60 = (freqs >= 59) & (freqs <= 61)
bD = (freqs >= 1) & (freqs <= 4)          # delta
bT = (freqs >= 6) & (freqs <= 9)          # theta
bS = (freqs >= 10) & (freqs <= 15)        # sigma
win = np.hanning(ep); wgain = win.sum() / 2

n = len(SITES)
rms = np.zeros((nep, n)); hum = np.zeros((nep, n)); rail = np.zeros((nep, n))
slope = np.zeros((nep, n)); dR = np.zeros((nep, n)); tR = np.zeros((nep, n)); sR = np.zeros((nep, n))

CH = 60  # epochs per read, keeps the memmap reads big and sequential
for a in range(0, nep, CH):
    b = min(a + CH, nep)
    raw = np.asarray(x[a * ep:b * ep, cols], dtype=np.float64)
    blk = raw.reshape(b - a, ep, n)
    blk = blk - blk.mean(1, keepdims=True)
    rms[a:b] = blk.std(1)
    rail[a:b] = (np.abs(blk) >= RAIL_UV).mean(1)
    P = np.abs(np.fft.rfft(blk * win[None, :, None], axis=1)) / wgain
    hum[a:b] = P[:, m60].max(1)
    pw = P ** 2 + 1e-20
    lg = np.log10(pw[:, band])
    slope[a:b] = (lgf_c[None, :, None] * (lg - lg.mean(1, keepdims=True))).sum(1) / lgv
    tot = pw[:, band].sum(1)
    dR[a:b] = pw[:, bD].sum(1) / tot
    tR[a:b] = pw[:, bT].sum(1) / tot
    sR[a:b] = pw[:, bS].sum(1) / tot
    if (b // CH) % 40 == 0:
        print(f"  ...{b}/{nep} epochs", flush=True)

E, G = 0, 1
fc = np.arange(2, n)
fl_slope = slope[:, fc].ravel()
THR = float(np.percentile(fl_slope, 1))

hrs = (np.arange(nep) * EPOCH_S) / 3600.0
clock = (t0.hour + t0.minute / 60 + hrs) % 24
light = (clock >= args.lights_on) & (clock < args.lights_off)
zt = (clock - args.lights_on) % 24

ok = (slope[:, E] < THR) & (rms[:, E] >= RMS_LO) & (rms[:, E] <= RMS_HI) & (rail[:, E] == 0)


def longest(m):
    best = cur = 0
    for v in m:
        cur = cur + 1 if v else 0
        best = max(best, cur)
    return best


print("\n" + "=" * 78)
print("SIGNAL QUALITY")
print("=" * 78)
print(f"floor ({len(FLOOR)} unwired inputs x {nep} epochs): slope p1 {THR:.2f}  "
      f"median {np.median(fl_slope):.2f}   60 Hz median {np.median(hum[:, fc]):.0f} uV")
fl_ok = np.mean([((slope[:, c] < THR) & (rms[:, c] >= RMS_LO) & (rms[:, c] <= RMS_HI)
                  & (rail[:, c] == 0)).mean() for c in fc])
print(f"FALSIFICATION: floor scores {fl_ok:.2%} usable (must be ~0)\n")
print(f"{'':18}{'EEG '+args.eeg:>14}{'EMG '+args.emg:>14}")
for nm, v in (("median slope", slope), ("median rms uV", rms), ("median 60 Hz uV", hum)):
    print(f"{nm:18}{np.median(v[:, E]):14.2f}{np.median(v[:, G]):14.2f}")
print(f"{'railed epochs':18}{(rail[:, E] > 0).mean():13.1%}{(rail[:, G] > 0).mean():13.1%}")
print(f"\nEEG usable (slope criterion)   {ok.mean():.1%} of {nep*EPOCH_S/3600:.2f} h "
      f"= {ok.sum()*EPOCH_S/3600:.2f} h")
print(f"  longest unbroken block       {longest(ok)*EPOCH_S/60:.1f} min "
      f"({longest(ok)*EPOCH_S/3600:.2f} h)")
print(f"  in LIGHT phase               {ok[light].mean():.1%}   ({light.sum()*EPOCH_S/3600:.1f} h)")
print(f"  in DARK phase                {ok[~light].mean():.1%}   "
      f"({(~light).sum()*EPOCH_S/3600:.1f} h)")

print("\n" + "=" * 78)
print("PHYSIOLOGY, on usable epochs only")
print("=" * 78)
u = ok
print(f"usable epochs {u.sum()}  ({u.sum()*EPOCH_S/3600:.2f} h)")
print(f"{'delta 1-4 Hz frac':22}{np.median(dR[u, E]):8.3f}")
print(f"{'theta 6-9 Hz frac':22}{np.median(tR[u, E]):8.3f}")
print(f"{'sigma 10-15 Hz frac':22}{np.median(sR[u, E]):8.3f}")

# EMG state dependence, 1 min bins over usable minutes
EPM = 60 // EPOCH_S
nm_ = nep // EPM
dm = dR[:nm_ * EPM, E].reshape(nm_, EPM).mean(1)
gm = rms[:nm_ * EPM, G].reshape(nm_, EPM).mean(1)
okm = u[:nm_ * EPM].reshape(nm_, EPM).mean(1) > 0.8
lm = light[:nm_ * EPM].reshape(nm_, EPM).mean(1) > 0.5
r_all = np.corrcoef(dm[okm], gm[okm])[0, 1] if okm.sum() > 20 else np.nan
print(f"\nEMG STATE DEPENDENCE  r(delta, EMG rms) at 1 min, over {int(okm.sum())} usable minutes")
print(f"  all           r = {r_all:+.3f}   (a working pair is clearly NEGATIVE)")
for nmz, sel in (("light phase", okm & lm), ("dark phase", okm & ~lm)):
    if sel.sum() > 20:
        print(f"  {nmz:14}r = {np.corrcoef(dm[sel], gm[sel])[0,1]:+.3f}   ({int(sel.sum())} min)")

# sleep/wake read from delta, with the mandatory threshold sweep
print("\n" + "=" * 78)
print("SLEEP / WAKE READ FROM DELTA, WITH THE MANDATORY +/-25% THRESHOLD SWEEP")
print("=" * 78)
v = dR[u, E]
hist, edges = np.histogram(v, bins=128)
cn = hist.astype(float) / hist.sum()
cen = (edges[:-1] + edges[1:]) / 2
w0 = np.cumsum(cn); m0 = np.cumsum(cn * cen); mT = m0[-1]
sig = (mT * w0 - m0) ** 2 / np.maximum(w0 * (1 - w0), 1e-12)
otsu = float(cen[np.argmax(sig)])
print(f"Otsu split on delta fraction = {otsu:.3f}")
print(f"{'threshold':>12}{'x':>7}{'% asleep ALL':>14}{'% asleep LIGHT':>16}{'% asleep DARK':>15}")
for f in (0.75, 0.90, 1.00, 1.10, 1.25):
    th = otsu * f
    asleep = np.zeros(nep, bool)
    asleep[u] = dR[u, E] > th
    a_all = asleep[u].mean()
    a_l = asleep[u & light].mean() if (u & light).sum() else np.nan
    a_d = asleep[u & ~light].mean() if (u & ~light).sum() else np.nan
    star = "  <== Otsu" if f == 1.00 else ""
    print(f"{th:12.3f}{f:7.2f}{a_all:13.1%}{a_l:15.1%}{a_d:14.1%}{star}")
print("\nLiterature for a mouse: roughly 70% of the LIGHT phase asleep, far less in the dark.")
print("The pipeline knows nothing about the clock, so a light/dark difference is EXTERNAL")
print("validation. It is only worth quoting if it survives the +/-25% sweep above.")

# per-ZT-hour profile
print("\n" + "=" * 78)
print("PER ZT HOUR  (ZT0 = lights on)")
print("=" * 78)
th = otsu
asleep = np.zeros(nep, bool); asleep[u] = dR[u, E] > th
print(f"{'ZT':>4}{'phase':>7}{'usable%':>9}{'asleep%':>9}{'med delta':>11}{'med EMG uV':>12}")
for h in range(24):
    sel = (zt >= h) & (zt < h + 1)
    if sel.sum() == 0:
        continue
    su = sel & u
    ph = "LIGHT" if h < (args.lights_off - args.lights_on) else "dark"
    a = asleep[su].mean() if su.sum() else np.nan
    print(f"{h:4d}{ph:>7}{ok[sel].mean():8.0%}{a:9.0%}"
          f"{np.median(dR[su, E]) if su.sum() else np.nan:11.3f}"
          f"{np.median(rms[su, G]) if su.sum() else np.nan:12.1f}")

# ---- day-to-day reproducibility, only meaningful with 2+ complete cycles ----
ncyc = int(hrs[-1] // 24) + 1
if ncyc >= 2:
    print("\n" + "=" * 78)
    print("DAY TO DAY REPRODUCIBILITY  (each 24 h cycle scored separately, same threshold)")
    print("=" * 78)
    print("A within-animal replication: the same measurement repeated on consecutive days.")
    print(f"{'cycle':>7}{'hours':>14}{'usable%':>9}{'aslp LIGHT':>12}{'aslp DARK':>11}"
          f"{'EMG light':>11}{'EMG dark':>10}{'r(d,EMG)':>10}")
    for c in range(ncyc):
        sel = (hrs >= c * 24) & (hrs < (c + 1) * 24)
        if sel.sum() < 3600 // EPOCH_S:
            continue
        su = sel & u
        sl, sd = su & light, su & ~light
        selm = sel[:nm_ * EPM].reshape(nm_, EPM).mean(1) > 0.5
        mm_ = okm & selm
        rr = np.corrcoef(dm[mm_], gm[mm_])[0, 1] if mm_.sum() > 20 else np.nan
        print(f"{c+1:7d}{c*24:6.0f}-{(c+1)*24:<7.0f}{ok[sel].mean():8.0%}"
              f"{asleep[sl].mean() if sl.sum() else np.nan:11.1%}"
              f"{asleep[sd].mean() if sd.sum() else np.nan:10.1%}"
              f"{np.median(rms[sl, G]) if sl.sum() else np.nan:11.1f}"
              f"{np.median(rms[sd, G]) if sd.sum() else np.nan:10.1f}{rr:10.3f}")
    print("\nThe threshold is the Otsu value from the WHOLE file, applied unchanged to both")
    print("cycles, so the rows are directly comparable and neither was fitted on its own data.")

np.savez(BASE + f"_{args.eeg.replace('/','')}_report.npz", sites=np.array(SITES),
         rms=rms, hum=hum, rail=rail, slope=slope, delta=dR, theta=tR, sigma=sR,
         light=light, zt=zt, usable=ok, thr=THR, otsu=otsu, fs=fs, epoch_s=EPOCH_S)
print(f"\nsaved per-epoch arrays to "
      f"{os.path.basename(BASE)}_{args.eeg.replace('/','')}_report.npz")
