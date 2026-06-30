---
tags: [procedure, eeg, analysis, guidelines, filtering, referencing, onboarding]
created: 2026-06-30
status: complete
---

# 04 — Processing Guidelines (the science)

> [!abstract] TL;DR
> The decisions behind the scripts: which bipolar pair, which filters, why decimate to 256 Hz, how to flag artifacts, and the pass/fail criteria for "is this recording usable". Follow these so results are consistent and publishable. Hub: [[_eeg-analysis-hub]].

## 1. Record raw, process offline (always)

Acquire **raw wideband at 1 kHz** in Allego; do all filtering/referencing/decimation **offline**. Reasons:
- Reversible — you can re-filter differently without re-recording.
- Correct anti-aliasing on decimation (done in software with a proper low-pass).
- Nothing irreversible is baked into the master file.

Allego's Signal Processing filters at the **Visualization** stage are display-only (fine); **Hardware/Data** stage bake into the saved file (avoid for the master).

## 2. Referencing — bipolar, no CAR

The chip (RHD2216) is **bipolar**: each pair self-references. So:
- **EEG = `native0 − native1`** (left frontal − left parietal). This is the sleep EEG.
- **EMG = `native2 − native3`** (neck L − neck R).
- **Do NOT use Common Average Reference (CAR)** — it mixes the ± pairs and cross-contaminates. The scripts never apply CAR.
- `copper` (native 6) is an **environmental-noise** channel (cut shield), not a brain reference; optionally subtract it from EEG if mains noise is bad, but it is not a montage reference.

Background: [[grounding-reference-noise-concepts]].

## 3. Filters (what `eeg_pipeline.py` applies)

| Signal | Bandpass | Notch | Rationale |
|---|---|---|---|
| EEG | **0.5–30 Hz** | 50 Hz | sleep EEG content is < ~30 Hz (delta/theta/sigma); 0.5 Hz HP removes drift |
| EMG | **10–300 Hz** | 50 Hz | muscle tone is broadband; 10 Hz HP rejects movement/EEG bleed |

- Butterworth, **zero-phase** (`sosfiltfilt` / `filtfilt`) so peaks don't shift in time.
- **50 Hz** notch (Korea/EU mains). Change to 60 Hz if ever recording on 60 Hz mains.

## 4. Decimation — 1 kHz → 256 Hz

Classic rodent sleep scoring uses ~128–256 Hz; all the relevant EEG/EMG bands sit well below ~100 Hz, so 256 Hz (Nyquist 128) is ample. The pipeline uses `scipy.signal.resample_poly` (exact rational 1000→256 = 32/125, with anti-alias). Acquire 1 kHz, decimate offline → identical staging data, smaller files. Detail: [[allego-sampling-rate]].

## 5. Epoching + features

- Default **4 s epochs** (set `--epoch`; 8 s and 10 s are also common). At 256 Hz a 4 s epoch = 1024 samples.
- Per-epoch **band power** via Welch PSD, integrated over:
  - **delta 0.5–4 Hz** (high in NREM),
  - **theta 6–9 Hz** (rodent theta; high in REM and active wake),
  - **sigma 10–15 Hz** (spindles), **total 0.5–30 Hz**.
- **theta/delta ratio** is the workhorse discriminator: low = delta-rich (NREM), high = theta-rich (REM / active wake).
- **EMG RMS** per epoch separates REM (atonia, low EMG) from active wake (high EMG) — *when EMG works*.

## 6. Artifacts

- An epoch is flagged `artifact=1` if the filtered EEG peak exceeds a threshold (`--artifact-uv`, default 2000 uV) — grooming/chewing/movement transients.
- Flagged epochs should be excluded from band-power statistics and left unscored (or scored as artifact). The scripts report the artifact %.
- A *single* huge transient is normal; **pervasive** rail-touching means a hardware problem (see below).

## 7. QC pass criteria (decide before trusting a recording)

Run `qc_report.py` and check:

| Check | Pass | Fail → meaning |
|---|---|---|
| EEG channel RMS | tens–low-hundreds uV | thousands uV → **floating/open** |
| EEG % @rail | ~0 % | high % → open electrode or ungrounded animal |
| All channels rail together | no | yes → **animal not grounded** (the railing saga) |
| theta/delta over time | clearly cycles | flat → no state structure / dead signal |
| Impedance (in Allego, separate) | 0.1–1 MΩ | ≫5 MΩ → **open electrode** |

Reference good result (single mouse, 2026-06-29): EEG bipolar RMS ~136 uV, ~0 % artifact, theta/delta cycling 0.4↔3 = clean, scoreable EEG. EMG read ~7 MΩ (open) → EMG columns unusable that session.

> [!important] EEG-only limit
> Without working EMG you can separate **Wake vs NREM** from EEG alone, but **not REM from active wake** (both are theta-rich; EMG atonia is the discriminator). Note this in any EEG-only dataset.

## 8. Naming / housekeeping

- Keep the XDAT 3-file set together; derived files share the base name (`_features.csv`, `_qc_overview.png`, `.edf`, `_256hz.csv`).
- Don't hand-edit the master. Re-run a script to regenerate any derivative.
- If the rig wiring changes, edit `CHANNEL_MAPS` in `scripts/xdat_io.py` once.

## Related
- [[_eeg-analysis-hub]] · [[03-scripts-and-usage]] · [[grounding-reference-noise-concepts]] · [[allego-sampling-rate]] · [[eeg-emg-data-guide]]
