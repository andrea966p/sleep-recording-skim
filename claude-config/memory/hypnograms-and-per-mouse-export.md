---
name: hypnograms-and-per-mouse-export
description: "2026-08-22: first hypnograms (3 of 6 usable), per-mouse raw export, and B1+C1 animals gone with their tethers"
metadata:
  type: project
---

**2026-08-21/22. First hypnograms this project has ever produced, plus the per-mouse export.**

## 🔴 B1 AND C1 ANIMALS ARE GONE — found missing WITH THEIR TETHERS after the run stopped
⭐ **B1 had ALREADY failed with the PREVIOUS animal ⇒ that position is a HARDWARE fault: a GROUND
CONNECTION on the port, NOT surgery.** C1 was already withdrawn (EMG state-dependence collapsed).
⚠️ **Two tethers need repair/replacement. Cohort is down to 6.**

## HYPNOGRAMS: 6 produced, 3 usable
**✅ A1 (W 43.3 / N 52.1, r@1min 0.495) · A2 (52.3 / 43.3, 0.592) · D2 (54.2 / 42.8, 0.446).**
REM-from-NREM 70.9-82.4%, each above its own shuffled null.
🔴 **C2 (r 0.11) and D1 (r 0.001) REJECT — NOT sleep architecture.** Shuffled null ~0.00, bar 0.30.
**C2's 17.8% WAKE is implausible** (good animals 43-54%) — that is what fragmented contact looks
like after staging. D1 gives 1.92 h of 39.67.
🔑 **`r@1min` IS THE NUMBER THAT DECIDES IT.**
🔴 **B2 = NO STATES, and that is CORRECT**: EEG good (92.4%, 261 min block, mains 72.7 µV) but **EMG
OPEN at 535.8 µV**; WAKE is an Otsu cut on log EMG rms, so an open EMG makes it meaningless.
✅ **B2's EEG columns stay valid** (`eeg_rms_uv, delta, theta, theta_delta`) for spectral work.
🛑 **DID NOT invent an EEG-only stager** — published but not implemented/validated here.
🛑 **REM % in the summaries is FIXED BY CONSTRUCTION (top 20% of sleep) — NEVER report it.**
🛑 **ALL PROVISIONAL — no human has scored a single epoch. The kappa is still the gate.**

## PER-MOUSE EXPORT — `~/eeg-processed/per-mouse/<recording>/`, 35 GB
One folder per position: `.mat` (1.1 GB, full 1000 Hz) + `.txt` (3.1-3.5 GB, `time_s,eeg_uV,emg_uV`)
+ hypnogram + `_VERDICT.txt` in plain language. **NOT EDF** (user does not want EDF).
🔑 **Time vector NOT stored in the .mat** — at 1000 Hz it adds 1.14 GB and breaks MATLAB v5's 2 GB
limit (no h5py for v7.3). `t = (0:numel(S.eeg)-1)'/double(S.fs);`
✅ **Verified against source after export**: counts equal, channels byte-identical at spread points,
text matches .mat, 142,825,729 lines = 1/sample + header. **Do this check — a partial write looks
identical in `ls`.** Script `export/export_per_mouse.py`; procedure `02-procedures/eeg-data-analysis/per-mouse-export.md`.
⚠️ **`stage2_split.py` needs `--all-verdicts`** or OPEN positions are silently skipped.

## TWO OPERATIONAL GOTCHAS
🔴 **`nohup` IS NOT ENOUGH for a long job — use `setsid`.** My first export died leaving a **0-byte
.mat** because the launching shell timed out and SIGTERM'd the process group (nohup guards SIGHUP only).
🔴 **CORRECTION: I wrongly said the pipeline "had been unrunnable". FALSE — `/usr/bin/python3` has
numpy 1.26.4 + scipy 1.11.4 and runs it fine, as the vault already said.** True part: `~/eeg-analysis-venv`
has numpy 2.5 and **numpy 2.0 REMOVED `np.trapz`**; stages 1+3 now bind `np.trapezoid` with fallback.
🔑 **`radiens` is ONLY in the daemon venv and analysis does NOT need it: recording → daemon venv,
analysis → `/usr/bin/python3`.**

Related: [[emg-gate-passes-and-floor-bug]] · [[recording-2026-08-18-eight-new-mice]] · [[animal-card-verdict-ladder]]
