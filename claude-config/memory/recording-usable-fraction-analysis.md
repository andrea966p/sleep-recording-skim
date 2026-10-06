---
name: recording-usable-fraction-analysis
description: "The pre-registered per-mouse data-quality analysis of an Allego recording — scores each channel against unwired amplifier inputs recorded in the same file; script, XDAT layout facts, and the 2026-08-06 run"
metadata: 
  node_type: memory
  type: project
  originSessionId: 3430655c-999e-4bb1-abaa-9187f41c99d5
  modified: 2026-08-06T05:50:08.382Z
---

**Pre-registration** (written before the data existed): vault
`05-experiments/active/2026-08-06-recording-data-quality-preregistration.md`.
⛔ **THAT SCRIPT IS DELETED (2026-08-11).** It was one of three independent copies
of this criterion. The ONLY engine is now **`core/criteria.py`**, reached through
`cards/ladder.py`. See [[analysis-stack-audit-2026-08-11]].

⭐⭐ **THE IDEA: judge a recording against a control INSIDE the same file.** Each mouse uses
only 2 of its chip's 16 amp inputs, so **`/3`-`/16` and `/35`-`/48` are real amplifier inputs
with NO WIRE = 112 floor-control channels**, recorded simultaneously. Threshold is derived
from them, not inherited. ⚠️ **NEVER include `/17`-`/32` or `/49`-`/64`** — inactive slots,
internally tied, they would destroy the control. ⚠️ **A2 slot has no mouse ⇒ a second
independent control; CHECK IT FIRST, if A2 scores usable the analysis is broken.**

**Criterion per 10 s epoch (all three):** 60 Hz amplitude **< 1st percentile of the floor
distribution** · rms 10-150 µV · zero railed samples (rail = |v| ≥ 6389.6 µV).
**Primary outcomes per mouse: usable fraction (EEG AND EMG) + LONGEST UNBROKEN BLOCK.**
⭐ **The block matters more than the total** — our only real sleep recording scored because it
had one 8.1 h continuous block.

🔑 **XDAT LAYOUT, VERIFIED 2026-08-06:** `float32`, **262 interleaved channels** (256 pri + 2
aux + 2 din + 2 dout), values **already in µV**. Label = `.xdat.json` →
`sapiens_base.biointerface_map`, `port` + `/` + `site_num`, in file order. nsamp = filesize ÷
(262×4). Use `np.memmap`. Recordings land in **`~/radix/data/`**, fs **1000 Hz**, ~1.84 GB/h.

⚠️ **HARDWARE BANDPASS 1.10-475.17 Hz REACHES THE SAVED FILE** (Allego Signal Processing →
Stage **Hardware**). **Data and Visualization stage filters do NOT** (verified 2026-07-31).
⇒ **never change the Hardware stage for display purposes**; use Visualization.
⚠️ **The 1.10 Hz hardware high-pass attenuates the bottom of the delta band (0.5-4 Hz) before
saving and cannot be undone.** Self-consistent for us (all our thresholds were derived from
data carrying it) but matters when comparing delta power to the literature.

**RUN 2026-08-06:** `allego_0__uid0806-12-45-02`, started **12:45:02 KST**, stopped ~17:00.
Smoke test on the first 90 s: ✅ floor control **0.00% usable**, ✅ A2 no-mouse **0.0%**,
B1 100% both. Median 60 Hz **cleanly bimodal, nothing between 40 and 600 µV** — connected
B1 EMG 12.6 · D2 EMG 25.7 · C1 EMG 26.7 · B1 EEG 39.1; open 844-5574. Only valley value =
**A1 EMG 609 µV**, which impedance called excellent — watch it.

⭐⭐⭐ **INTERIM RESULT 14:25, first 1.66 h / 597 epochs (file read WHILE STILL RECORDING — no
time lost).** Threshold from 66,864 floor epochs = **60 Hz < 388.1 µV**. ✅ **Floor 0.00%
usable, A2 no-mouse 0.0% ⇒ falsification passed.**
**B1new 99.8% EEG / 99.7% EMG / 99.7% both, longest block 39.5 min** · D2 EMG 86.1% ·
C1 EMG 36.3% · A1 EMG 5.2% · **everything else 0.0%**.
🔴 **SEVEN OF SEVEN implanted animals score 0.0% EEG ⇒ exactly ONE scoreable mouse.**
⭐ **A1's EMG resolves the impedance-vs-recording gap: rms 331 µV of which 296 µV IS 60 Hz.
Impedance sees the wire is connected; it CANNOT see that hum rides on it.** ⇒ **the recording,
not impedance, is the outcome measure.**
⚠️ **C1 EMG stays OPEN**: rms 1834.6 µV ≫ its 505.8 µV hum ⇒ big non-hum content = real EMG
bursts or movement artefact, **unresolvable without video (cameras removed 2026-08-04)**.
📊 **Pre-registration scorecard: 6 hits, 1 partial (A1), 1 miss (C1 EMG)** — better than the
08-02 run's 4/3/1, and the two failures point in OPPOSITE directions ⇒ impedance is not biased,
just blind to signal quality.
⚠️ The **rms 10-150 µV guard**, not the hum threshold, is what binds A1 and C1. Left unchanged
(pre-registered). **A future version may raise the upper bound for EMG** — EMG bursts can
legitimately exceed 150 µV.

🔴⭐⭐⭐ **SECOND METHOD, AFTER TEXTBOOK POST-PROCESSING — SAME ANSWER.** Scripts
`eeg-emg-analysis/qc/spectral_shape_vs_floor.py` + `plot_filtered_traces_and_psd.py`.
⚠️ **These need `~/eeg-analysis-venv/bin/python` (numpy 2.5 + scipy 1.18). `/opt/neurosurveillance/venv`
CANNOT import scipy** (numpy 2 vs scipy built for numpy 1).
**Chain: notch 60/120/180 Hz (Q=30) + Butterworth 0.5-30 Hz, applied to animals AND to the 112
wire-free floor channels.**
🔴 **AFTER FILTERING, A CHANNEL WITH NO WIRE COMES OUT AT A MEDIAN 69 µV OF PLAUSIBLE
EEG-LOOKING SIGNAL (p95 423 µV). FILTERING MANUFACTURES A CONVINCING TRACE OUT OF NOTHING ⇒
"the filtered trace looks good" is NEVER evidence of contact.**
✅ **What survives filtering = SPECTRAL SHAPE.** Floor range: slope **[-1.10, -0.04]**, delta
fraction ~0.16. **B1 = slope -2.15, delta 0.47 ⇒ far outside, REAL.** B2 -0.47/0.17, C2
-0.38/0.17, D2 -0.38/0.17, A2-no-mouse -0.04/0.09 = **all inside the bare-wire range**.
⚠️ **A1, C1, D1 RAILED 2-7% of the time ⇒ clipping is nonlinear, UNRECOVERABLE by any filter.**
⇒ **Only B1 has EEG. Two independent methods (raw hum vs floor; spectral shape vs floor) agree,
and both correctly score the no-mouse A2 slot as nothing.**
📊 Figures in vault `05-experiments/attachments/2026-08-06-{traces-filtered,psd}.png`, from
10 min mid-recording. ⭐ **Traces use ONE FIXED ±400 µV y-scale for every panel — auto-scaling
would make every channel look like signal.** PSD log-log: B1 falls ~1/f, everything else flat.
📖 **Plain-language walkthrough of the whole method is §10-11 of the pre-registration doc** —
written because the reasoning got hard to follow.

See also [[fleet-duty-cycle-census-and-new-mouse]], [[eeg-analysis-pipeline]].


## From the memory index, trimmed there 2026-10-06 (kept here verbatim)

- ⭐⭐ **[USABLE FRACTION vs AN IN-FILE CONTROL](recording-usable-fraction-analysis.md).** XDAT = float32, 262 interleaved ch, µV. Hardware bandpass 1.10-475.17 Hz eats the bottom of delta.
