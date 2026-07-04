---
tags:
  - procedure
  - eeg
  - emg
  - analysis
  - sleep
  - radiens
  - onboarding
created: 2026-06-27
status: complete
---

# EEG/EMG Data Guide — Reading and Analyzing Sleep Signals

> [!abstract] TL;DR — for non-technical readers
> **What this is.** A from-scratch guide to the two signals this rig records — **EEG** (brain waves) and **EMG** (neck-muscle activity) — and how to turn them into a **sleep score** (Wake / NREM / REM). Part 1 teaches you to read the traces **by eye**; Part 2 shows the **Python** that does it numerically.
>
> **Why it exists.** The operator running the rig is not an ephys expert. Before touching code you should be able to glance at a trace and say "that's NREM" or "that's just 60 Hz hum." This page builds that intuition first, then automates it.
>
> **How to read this page.** Read **Part 1 top to bottom** until the sleep-stage table feels obvious — that is the real skill. Only then go to **Part 2** (Python). Mapping/grounding are prerequisites and live elsewhere: [[signal-mapping-guide]], [[signal-quality-and-grounding]], [[grounding-reference-noise-concepts]]. Software: [[radiens-software-reference]].

> [!important] Prerequisites — do these first
> This guide assumes the channels are already **mapped** ([[signal-mapping-guide]]) and the signal is **clean and grounded** ([[signal-quality-and-grounding]]). If channels are railing or floating, **stop** — you cannot analyze a saturated trace. Fix grounding first.

---

# PART 1 — Understand by eye (become the expert before you touch code)

## 1. EEG vs EMG — what they are

Both are tiny voltages picked up by electrodes on/in the mouse, amplified by the headstage (Intan **RHD2216**), and digitized. They differ in **where they come from**, **how fast they wiggle**, and **how big they are**.

| | **EEG** (electroencephalogram) | **EMG** (electromyogram) |
|---|---|---|
| Comes from | Summed electrical activity of cortical neurons, picked up by a skull/dura electrode | Electrical activity of neck muscle fibers, picked up by a wire in/near the muscle |
| Tells you about | **Brain state** — sleep stage, arousal | **Movement / muscle tone** — awake-active, or REM atonia |
| Frequency band | slow, **~0.5–30 Hz** | fast, **~10–300 Hz** |
| Amplitude (this rig) | **~20–300 µV** | **~10–50 µV at rest**, up to **~1 mV** on movement |
| Sleep-staging role | the *shape* of the wave (slow vs fast) | the *level* (high tone = awake, flat = REM) |

> [!note] These ranges are this rig's verified working numbers
> The bands (EEG 0.5–30 Hz, EMG 10–300 Hz), amplitudes (EEG 20–300 µV; EMG ~10–50 µV rest, ~1 mV moving), the **noise floor ≈ 2–5 µV RMS** and the **amplifier rail = ±5 mV (≈ 10 mV pk-pk = saturated)** are all from [[signal-quality-and-grounding]] §3b. Reuse them; do not re-derive.

### Each channel is a *pair* (bipolar)
The RHD2216 is a **bipolar** amplifier: every recorded channel is already the **difference** of a `+` and a `−` wire.
- **EEG = EEG+ − EEG−**
- **EMG = EMG+ − EMG−**

A single wire alone carries mostly shared junk (drift, hum); the difference cancels that and leaves the real signal. In Allego this is **Paired Reference** (manual p70); in Part 2 it is one subtraction. There is **no separate reference electrode** on this chip — see [[grounding-reference-noise-concepts]].

> [!note] Channel numbering (recap from [[signal-mapping-guide]])
> `D/n` (Allego on-screen, 1-indexed) **= native channel `n−1` = `pri_(n−1)`**, and the **C3410 board pad = the native channel**. Our 8 recorded channels: M1 EEG±/EMG± = `D/1–D/4` (native 0–3); M2 EEG±/EMG± = `D/9–D/12` (native 8–11). In analysis we name them **by native index**, since data files store `pri_N`.

### What they look like (ASCII)

```
EEG, awake (low-amplitude, fast, "busy"):
   /\  /\/\   /\  /\/\/\   /\/\   ~40 µV, mixed fast rhythms

EEG, NREM sleep (high-amplitude, slow delta waves):
    ___          ___          ___
   /   \        /   \        /   \      ~200-300 µV, slow ~1-4 Hz rollers
  /     \______/     \______/     \

EEG, REM sleep (low-amplitude, regular theta ~6-9 Hz):
  /\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\   ~60 µV, steady "ringing"

EMG, awake & moving (large, dense, noisy):
  |#|#|##|#|#|##|#|#|##|#|#|##|#|#|   bursts to hundreds of µV-~1 mV

EMG, NREM (low, steady tone):
  ~~~~-~~~~-~~~~-~~~~-~~~~-~~~~-~~~~   low, flat-ish

EMG, REM (atonia — essentially flat, muscles "off"):
  ----------------------------------   near noise floor; the REM giveaway
```

---

## 2. The frequency bands (and which matter for mouse sleep)

EEG is described by how much power sits in standard frequency bands. These band names are **standard sleep-neuroscience domain knowledge** (well-established, textbook):

| Band | Approx. range | What it means for rodent sleep |
|---|---|---|
| **Delta (δ)** | ~0.5–4 Hz | **The NREM marker.** Big slow waves → lots of delta power = deep NREM |
| **Theta (θ)** | ~6–9 Hz (mouse) | **The REM marker.** Strong, regular theta dominates REM EEG |
| Alpha (α) | ~8–12 Hz | Less central to rodent staging than in humans |
| Beta (β) | ~15–30 Hz | Low-amplitude fast activity; present in active wake |
| Gamma (γ) | >30 Hz | High-frequency; mostly above our EEG analysis band, dropped by the 0.5–30 Hz filter |

> [!tip] The one ratio that does most of the work
> **Delta/Theta power ratio** separates the two sleep states: **high δ/θ → NREM**, **low δ/θ (theta wins) → REM**. Combined with the **EMG level** (high = Wake), those two numbers alone give a usable first-pass hypnogram (Part 2 §11).

---

## 3. Sleep-stage signatures (mouse) — the core skill

> [!important] This table is standard sleep-neuroscience domain knowledge
> The Wake / NREM / REM EEG+EMG signatures below are well-established textbook physiology, not rig-specific findings. The **amplitude numbers in parentheses** are this rig's ranges (from [[signal-quality-and-grounding]]); the *patterns* are universal.

| Stage | EEG looks like | EMG looks like | How you spot it **by eye** |
|---|---|---|---|
| **Wake** | Low-amplitude, **fast & mixed** (~40 µV, beta/theta) | **High and variable** — bursts with movement | EEG "busy" and small **+** EMG loud/jumpy. Movement artifacts everywhere. |
| **NREM** | **High-amplitude slow waves** (delta, ~200–300 µV); brief **spindles** (~10–15 Hz bursts) | **Low, steady tone** (low but present) | Big slow rollers in EEG **+** quiet but non-zero EMG. The "tall and slow" stage. |
| **REM** | **Low-amplitude, regular theta** (~6–9 Hz, ~60 µV) | **Atonia — essentially flat** (near noise floor) | Steady theta "ringing" in EEG **+** EMG drops to almost nothing. Flat EMG is the dead giveaway. |

> [!tip] The two-question decision tree
> 1. **Is the EMG loud/variable?** → **Wake.** (Muscle tone settles the question first.)
> 2. If EMG is quiet, **is the EEG big-and-slow or small-and-theta?**
>    - big slow delta → **NREM**
>    - small steady theta + flattest EMG → **REM**
>
> REM is the trap: its EEG can look superficially "awake-ish" (low amplitude), but the **EMG is at its flattest** — that contrast (active-looking brain, silent muscle) *is* REM.

```
A whole-night cartoon (hypnogram): Wake high, NREM mid, REM low
Wake  ─┐   ┌──┐        ┌─┐         ┌──
NREM   └───┘  └──┐  ┌──┘ └────┐ ┌──┘
REM             └──┘          └─┘        (REM episodes lengthen toward "morning")
```

---

## 4. Good biological signal vs artifact (read, don't restate)

Before any stage call, confirm the trace is **biology, not garbage**. The full good/marginal/bad cheat-sheet (with µV thresholds), the saturation/floating/hum signatures, and the per-session 5-minute check live in **[[signal-quality-and-grounding]] §3b–§3c** — use that as the bench reference. The 30-second version:

| You see | It's probably | Action |
|---|---|---|
| Centered trace, wiggling, EMG jumps when mouse moves | **Good biology** | Analyze |
| Flat line pinned at top/bottom (~10 mV pk-pk) | **Saturated / floating ground** | Stop → fix ground ([[signal-quality-and-grounding]] §2) |
| Dead-flat line | **Broken connection** | Check wiring/solder |
| Fat, regular ~60 Hz sine burying the signal | **Mains hum** (Korea = 60 Hz) | Notch + shielding ([[grounding-reference-noise-concepts]]) |
| One mouse's trace echoes the other's movements | **Cross-talk** (shared headstage) | [[signal-quality-and-grounding]] §3e |

> [!warning] You cannot stage a saturated trace
> A floating animal rails all channels at the ±5 mV limit and hides everything underneath. Sleep staging is only meaningful **after** grounding is verified. This is the whole point of "look first."

---

# PART 2 — Analyze in Python

> [!success] Scope of what's verified here
> Both the **live-metrics** path (`signal_metrics().get_metrics`) and the **offline XDAT file reader** (§7b) are now **bench-verified on this rig** (radiens 4.0.0, 2026-06-27 — recorded a 6 s test set and read it back). The reader below reflects the *actual* file format (float32 already in µV, 38 interleaved channels), not a guess.

## 5. The sampling-rate reality (read this before loading anything)

> [!warning] You acquire fast and decimate slow — there is no "record at 128 Hz" button
> The Allego/Intan hardware **minimum sampling rate is 1,000 S/s**. You **cannot acquire at 128–256 Hz** (the rates classic sleep-scoring papers use). This rig acquires at **30,000 S/s** (30 kHz — the Mode-dropdown default, see [[radiens-software-reference]]).
>
> **Standard practice:** acquire at ≥1 kHz (we run 30 kHz), then **decimate to 128–256 Hz offline** in Python before staging. Sleep EEG/EMG has no useful content above ~100 Hz, so decimation loses nothing for staging and makes everything faster. The decimation step is mandatory and shown in §8.

## 6. Environment

> [!warning] Use a SEPARATE analysis venv — the project venv's SciPy is broken (verified 2026-06-27)
> The project venv `/opt/neurosurveillance/venv` has **NumPy 2.2.6** but **no matching SciPy** — it falls back to the system SciPy (built for NumPy 1.x), so `import scipy.signal` **crashes** (`numpy.core.multiarray failed to import`). The SDK lives there, but the analysis stack does not work there.
>
> - The **XDAT reader** (§7b) is **NumPy-only** → runs anywhere, including the project venv.
> - For the **SciPy pipeline** (decimate/filter/PSD below), make a **dedicated analysis venv** with matched versions:

```bash
# Dedicated analysis environment (NOT the project venv)
python3 -m venv ~/analysis-env
~/analysis-env/bin/pip install "numpy>=2" "scipy>=1.13" matplotlib
~/analysis-env/bin/pip install mne          # optional: EDF export + interactive viewer
# verified working combo on this rig: numpy 2.5.0 + scipy 1.18.0

# The radiens SDK (live metrics, §7a) stays in the project venv:
/opt/neurosurveillance/venv/bin/python
```

## 7. Loading the data

### 7a. Live quality numbers (VERIFIED) — `signal_metrics`
For a quick headless read of RMS / noise / peak-to-peak / SNR per channel (the same numbers as Allego's Signal Metrics tab):

```python
import numpy as np
# SDK quirk: radiens 4.0.0 uses np.NAN, removed in NumPy 2.x. Shim before import-use.
if not hasattr(np, "NAN"):
    np.NAN = np.nan

from radiens import AllegoClient

client = AllegoClient()
sm = client.signal_metrics().get_metrics(time_range=2.0, plot=False)
# sm.val shape ~ (1, 32, 6); columns = RMS, NOISE_UV, MAX_MIN_DIFF_ABS, SNR, EVENT_RATE, EVENT_MEAN
# MAX_MIN_DIFF_ABS ~ 10-12 mV  => that channel is railed/saturated (see signal-quality-and-grounding)
print(sm.val[0, :12, :])   # our 12 wired-region channels
```

This is for **judging signal quality live**, not for offline staging.

> [!warning] Headless raw-sample pulls are unreliable
> `AllegoClient.get_signals()` returns `(ndarray[channels×samples], list)`, but a **headless** call often returns **0 samples** — the sample cache is bound to the Allego GUI cache head ([[radiens-api-reference]]). Do **not** build offline analysis on `get_signals()`. Analyze the **recorded files** instead (§7b).

### 7b. Offline recordings — XDAT files (the real analysis path)
Recordings are saved in the open **XDAT** format ([[radiens-software-reference]]: raw signals + metadata, Python/MATLAB-friendly). A recording is a set of files sharing a base name:

An XDAT recording is a **three-file set** sharing a base name (verified 2026-06-27):

```
<base>_data.xdat        # float32 samples, interleaved by channel (NOT int16)
<base>_timestamp.xdat   # int64 per-sample timestamps (8 bytes/sample)
<base>.xdat.json        # metadata: sample rate, n samples, channel counts, channel↔site map
```

> [!success] Verified XDAT format (radiens 4.0.0, this rig)
> Read a 6 s test recording (`allego_0__uid…`) and confirmed the exact format:
> - `_data.xdat` = **float32** (4 bytes/sample/channel — file size = `num_smpl × total_channels × 4`). **NOT int16, and NO 0.195 µV scaling.**
> - Primary channels are **already in micro-volts** — JSON says `sig_units_pri = "micro-volts"` (aux = volts).
> - Channels are interleaved **sample-major**: each sample has `total` channels = `pri` (32) + `aux` (2) + `din` (2) + `dout` (2) = **38**. The amplifier channels are the **first `pri` columns**.
> - Metadata keys (all under `status`): `samp_freq` (e.g. 30000), `num_smpl`, `signals.{total,pri,aux,din,dout}`. The channel↔site map is under `sapiens_base.neighborhoods.site_hood.<i>.{home_ntv_chan_idx, home_chan_nam, home_site_num}`.

```python
import json
import numpy as np

def load_xdat(base_path):
    """Load an XDAT recording -> (pri[ch, samples] in microvolts, fs_hz, meta).

    Verified on radiens 4.0.0 / Allego XDAT, 2026-06-27. The _data.xdat is
    float32 and the primary channels are ALREADY in micro-volts (json
    sig_units_pri == "micro-volts") — no int16 conversion, no LSB scaling.
    Channels are interleaved: total = pri + aux + din + dout; the amplifier
    channels are the first `pri` columns.
    """
    with open(f"{base_path}.xdat.json") as f:
        meta = json.load(f)
    st  = meta["status"]
    fs  = st["samp_freq"]                 # e.g. 30000
    n   = st["num_smpl"]                  # total samples
    tot = st["signals"]["total"]          # ALL interleaved channels, e.g. 38
    pri = st["signals"]["pri"]            # amplifier channels, e.g. 32

    d = np.fromfile(f"{base_path}_data.xdat", dtype=np.float32)  # float32
    d = d.reshape(n, tot)                  # (samples, total_channels), sample-major
    pri_uv = d[:, :pri].T                  # (pri_channels, samples), already micro-volts
    return pri_uv, fs, meta

# data, fs, meta = load_xdat("/home/skimlab/radix/data/allego_0__uid0627-21-11-02")
# data.shape -> (32, num_smpl); units = microvolts; native channel i = data[i]
```

> [!note] SDK offline readers need the Radiens hub running
> `radiens` also ships `FileSystemClient.get_data_file_metadata()` and `VidereClient.link_data_file()` → `.signals()` for reading recordings, but those require the **Videre/Curate hub services** to be running (not just `allegoserver`); headless they fail with `Confirm ClientType.VIDERE is running`. The **direct file read above needs no services** — prefer it for headless analysis. (Also: `AllegoClient.set_recording_config()` has a request-serialization bug in radiens 4.0.0 — set the recording name/path from the Allego **Settings** GUI instead.)

> [!tip] EDF + MNE is still a fine alternative
> You can also export the recording to **EDF** from Videre and read it with **MNE** (§12) — EDF carries sample rate + channel labels. Use whichever fits; the direct XDAT reader above is the no-dependency path.

---

## 8. Preprocessing

All steps operate on `data[ch, samples]` in µV at the acquired rate `fs` (e.g. 30000 Hz).

### 8a. Decimate 30 kHz (or ≥1 kHz) → 250 Hz
`scipy.signal.decimate` applies an anti-alias filter then downsamples. Do it in stages for big factors (each stage ≤ ~13) to keep the filter stable.

```python
from scipy.signal import decimate

def to_250hz(sig, fs, target=250):
    """Decimate to ~target Hz in safe stages. Returns (sig_ds, fs_ds)."""
    factor = int(round(fs / target))
    fs_ds = fs
    out = sig
    # factor 30000/250 = 120 -> do it as 120 = 5 * 4 * 3 * 2 (each <=13)
    for f in _factorize(factor):
        out = decimate(out, f, ftype="iir", zero_phase=True, axis=-1)
        fs_ds //= f
    return out, fs_ds

def _factorize(n, max_step=12):
    steps = []
    for f in (5, 4, 3, 2):           # greedy small factors
        while n % f == 0 and f <= max_step:
            steps.append(f); n //= f
    if n != 1:                        # leftover prime factor
        steps.append(n)
    return steps

# eeg_ds, fs_ds = to_250hz(eeg_raw, fs)   # fs_ds == 250
```

### 8b. Bandpass — EEG 0.5–30 Hz, EMG 10–300 Hz
Use a Butterworth + zero-phase `filtfilt` (no time shift, important for staging epochs). Note the EMG upper band (300 Hz) needs `fs ≥ ~700 Hz`, so for EMG **decimate to ~1000 Hz, not 250 Hz** (or keep raw and decimate to 500–1000 Hz). EEG is happy at 250 Hz.

```python
from scipy.signal import butter, filtfilt

def bandpass(sig, fs, lo, hi, order=4):
    nyq = fs / 2.0
    b, a = butter(order, [lo / nyq, hi / nyq], btype="band")
    return filtfilt(b, a, sig, axis=-1)

# EEG band (on the 250 Hz EEG stream):
# eeg = bandpass(eeg_ds, 250, 0.5, 30)
# EMG band needs headroom for 300 Hz -> use a ~1000 Hz EMG stream:
# emg_1k, fs_emg = to_250hz(emg_raw, fs, target=1000)   # actually ~1 kHz
# emg = bandpass(emg_1k, fs_emg, 10, 300)
```

### 8c. 60 Hz mains notch (Korea)
```python
from scipy.signal import iirnotch, filtfilt

def notch_50(sig, fs, f0=50.0, Q=30.0):
    b, a = iirnotch(f0 / (fs / 2.0), Q)
    return filtfilt(b, a, sig, axis=-1)
```

### 8d. Paired-Reference subtraction (bipolar pairs) in code
Each real signal is the **difference of its + and − channel** (§1). With native indices: M1 EEG = native 0 − native 1; M1 EMG = native 2 − native 3; M2 EEG = native 8 − native 9; M2 EMG = native 10 − native 11.

```python
def paired(data, plus_idx, minus_idx):
    """Bipolar difference for one electrode pair (data indexed by NATIVE channel)."""
    return data[plus_idx] - data[minus_idx]

# Mouse 1:
# m1_eeg = paired(data, 0, 1)
# m1_emg = paired(data, 2, 3)
# Mouse 2:
# m2_eeg = paired(data, 8, 9)
# m2_emg = paired(data, 10, 11)
# Order: difference FIRST, then bandpass/notch the resulting bipolar signal.
```

---

## 9. Feature: EMG RMS (muscle tone level)
EMG staging uses the **level**, not the shape. Compute RMS in short windows (epochs); high = Wake, mid = NREM, lowest = REM.

```python
import numpy as np

def emg_rms(emg, fs, epoch_s=4.0):
    """RMS amplitude (uV) per non-overlapping epoch."""
    n = int(epoch_s * fs)
    n_ep = len(emg) // n
    ep = emg[: n_ep * n].reshape(n_ep, n)
    return np.sqrt(np.mean(ep ** 2, axis=1))   # one value per 4 s epoch
```

## 10. Feature: EEG band power / spectrogram
Use Welch PSD per epoch (or a spectrogram for the whole night). Integrate the PSD over each band to get delta and theta power.

```python
from scipy.signal import welch, spectrogram
import numpy as np

def band_power(eeg, fs, epoch_s=4.0):
    """Return (delta, theta) power arrays, one value per epoch."""
    n = int(epoch_s * fs)
    n_ep = len(eeg) // n
    ep = eeg[: n_ep * n].reshape(n_ep, n)
    d = np.zeros(n_ep); t = np.zeros(n_ep)
    for i, e in enumerate(ep):
        f, p = welch(e, fs, nperseg=min(n, int(fs * 2)))
        d[i] = p[(f >= 0.5) & (f < 4)].sum()    # delta
        t[i] = p[(f >= 6) & (f < 9)].sum()      # theta
    return d, t

# Whole-night spectrogram for eyeballing:
# f, tt, Sxx = spectrogram(eeg, fs, nperseg=int(fs*4))
# import matplotlib.pyplot as plt
# plt.pcolormesh(tt, f[f<30], 10*np.log10(Sxx[f<30]), shading="gouraud")
```

## 11. A simple threshold hypnogram (starting heuristic — NOT a validated scorer)

> [!warning] This is a teaching heuristic, not a publishable scorer
> Real sleep scoring uses tuned thresholds (per animal), epoch smoothing, manual review, and stage-transition rules — or a validated tool (AccuSleep, SPINDLE, etc.). The code below shows the *logic* (EMG splits Wake; δ/θ splits NREM vs REM). Treat its output as a draft to eyeball, never as ground truth.

```python
import numpy as np

def naive_hypnogram(eeg, emg_level, fs, epoch_s=4.0):
    """Return per-epoch stage labels: 'W', 'NR', 'R'. Heuristic only."""
    delta, theta = band_power(eeg, fs, epoch_s)
    dt_ratio = delta / (theta + 1e-9)

    # Thresholds: derive per-recording (here: simple percentiles as placeholders).
    emg_hi = np.percentile(emg_level, 60)   # above -> awake muscle tone
    dt_hi  = np.percentile(dt_ratio, 50)    # above -> delta-dominant (NREM)

    stages = []
    for emg_v, dt in zip(emg_level, dt_ratio):
        if emg_v > emg_hi:
            stages.append("W")              # loud muscle => Wake
        elif dt > dt_hi:
            stages.append("NR")             # quiet muscle + delta => NREM
        else:
            stages.append("R")              # quiet muscle + theta => REM
    return np.array(stages)

# emg_level must be on the SAME epoch grid as band_power (same epoch_s & fs).
# stages = naive_hypnogram(m1_eeg, emg_rms(m1_emg, fs_emg), fs)
```

The logic mirrors the §3 decision tree exactly: **EMG first (Wake), then δ/θ (NREM vs REM).**

## 12. MNE as an option (EDF + visualization)
MNE-Python is worth it when you want EDF interchange, an interactive scrollable viewer, or built-in spectral tools:

```python
import mne

# Read an EDF exported from Videre:
raw = mne.io.read_raw_edf("session.edf", preload=True)
raw.set_channel_types({"EMG1": "emg"})          # label types
raw.filter(0.5, 30, picks="eeg")                # EEG band
raw.notch_filter(50.0)                          # Korea mains
raw.plot()                                      # interactive scroll viewer
# raw.compute_psd().plot()                      # spectra for staging
```

For pure numerical staging, numpy/scipy (above) is enough; reach for MNE for **visualization and EDF exchange**.

---

## Related
- [[signal-quality-and-grounding]] — is the signal good enough to analyze? (rail/floating/hum, the µV cheat-sheet, 5-min check)
- [[signal-mapping-guide]] — which channel is which electrode (`D/n` = native+1; M1=D/1–4, M2=D/9–12)
- [[grounding-reference-noise-concepts]] — ground vs reference vs noise; why the bipolar chip uses no reference electrode
- [[radiens-software-reference]] — Allego/Videre GUI reference; Paired Reference (p70); XDAT format
- [[radiens-api-reference]] — `AllegoClient` Python SDK (live metrics, `get_signals` caveat)
- [[first-headstage-connection]] — bring-up + this rig's exact channel map
