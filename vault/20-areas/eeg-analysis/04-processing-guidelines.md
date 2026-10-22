---
type: reference
area: eeg-analysis
status: active
status-note: "complete"
tags: [procedure, eeg, analysis, guidelines, filtering, referencing, onboarding]
created: 2026-06-30
---

# 04 — Processing Guidelines (the science)

> [!success] ⭐ Channel selection is settled — see [[CANONICAL-allego-channel-selection]]
> **Select `/1`, `/2`, `/33`, `/34` per port. 16 channels for 8 mice.**
> `/1`=EEG and `/2`=EMG are ALREADY bipolar — never subtract them.
> Proven 2026-08-03 from the datasheet, the recorded metadata, and a
> measurement of all 64 slots on all four ports. **If anything below
> disagrees with that page, that page is right.**


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
> [!danger] ⚠️ CORRECTED 2026-08-01 — THE OLD MAPPING BELOW WAS WRONG. READ THIS BOX.
> The two lines struck through below said `EEG = native0 − native1` and `EMG = native2 − native3`. **THAT IS WRONG and it cost this project weeks.** The RHD2216 is a **BIPOLAR** amplifier: every channel has its own `+` and `−` pin and already reports the DIFFERENCE between them. Your 4 mouse wires land on the `+`/`−` pins of just TWO channels, not four.
>
> | native | Allego site (mouse A / mouse B) | what it ACTUALLY carries |
> | --- | --- | --- |
> | 0 / 32 | **`/1` / `/33`** | **EEG**, frontal vs parietal, ALREADY BIPOLAR |
> | 1 / 33 | **`/2` / `/34`** | **EMG**, neck pair, ALREADY BIPOLAR |
> | 2, 3 / 34, 35 | `/3`, `/4` / `/35`, `/36` | **NOTHING — empty pads, no wire by design** |
>
> **CORRECT USAGE:**
> ```
> EEG = native0          (do NOT subtract anything)
> EMG = native1          (do NOT subtract anything)
> natives 2 and 3        IGNORE — they are empty pads
> ```
>
> **Consequences of the old wrong mapping:** "EEG" was computed as `EEG − EMG`, which is meaningless; the empty pads `/3`,`/4` were measured and reported as 24 FAILED EMG SURGERIES when no wire was ever attached to them; and C1's genuine sleep architecture was invisible. Corrected on 2026-08-01, after the point was raised that it is not credible for every EMG implant to fail. See [[2026-08-01-channel-mapping-correction-first-sleep]].
>
> **Evidence (no assumption about pins required):** `/1` and `/2` are completely uncorrelated (r = 0.000 raw and in-band) — two single-ended electrodes millimetres apart on one hemisphere could not be; `/1` is stationary and delta-dominant while `/2` is bursty (70-300 Hz envelope CV 0.79 vs 0.21); `/2`'s muscle-band power ANTI-correlates with `/1`'s delta (ρ = −0.285); and `/3`,`/4` are statistically identical to channels known to have no wire attached.
>
> **In Allego, select only `/1, /2` and `/33, /34` per port** — 16 channels for 8 mice, not 32.

- ~~**EEG = `native0 − native1`** (left frontal − left parietal)~~ **← WRONG, see box above. EEG = `native0` alone.**
- ~~**EMG = `native2 − native3`** (neck L − neck R)~~ **← WRONG, see box above. EMG = `native1` alone; natives 2/3 are empty pads.**
- **Do NOT use Common Average Reference (CAR)** — it mixes the ± pairs and cross-contaminates. The scripts never apply CAR.
- `copper` (native 6) is an **environmental-noise** channel (cut shield), not a brain reference; optionally subtract it from EEG if mains noise is bad, but it is not a montage reference.

Background: [[grounding-reference-noise-concepts]].

## 3. Filters (what `eeg_pipeline.py` applies)

| Signal | Bandpass | Notch | Rationale |
|---|---|---|---|
| EEG | **0.5–30 Hz** | 60 Hz | sleep EEG content is < ~30 Hz (delta/theta/sigma); 0.5 Hz HP removes drift |
| EMG | **10–300 Hz** | 60 Hz | muscle tone is broadband; 10 Hz HP rejects movement/EEG bleed |

- Butterworth, **zero-phase** (`sosfiltfilt` / `filtfilt`) so peaks don't shift in time.
- **60 Hz** notch — **South Korea mains is 60 Hz** (corrected 2026-07-05; was wrongly 50 Hz). Also notch harmonics (120/180 Hz) when hum is strong. See [[60hz-mains-hum-discovery]].

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
