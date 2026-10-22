---
type: reference
area: sleep-scoring
status: active
tags: [reference, eeg, scoring, algorithm, iiis, comparison]
created: 2026-08-08
---

# SleepyScore, the Japanese scoring tool: what its source code actually does

> [!abstract] TL;DR
> We were given the source of the tool used in Japan to score these recordings:
> `SleepyScoreApp_HM_260312_exported.m` (MATLAB GUI) and `sleepy_pipeline_refined.py`
> (a Python refactor of the same algorithm). Both implement the identical method, so the
> algorithm below is not inferred, it is read off the code.
>
> **The single most valuable finding: they do not use a percentile for REM.** Both thresholds,
> WAKE and REM, are **2-cluster k-means splits**, with the threshold taken as the mean of the two
> cluster centres. Our pipeline's REM rule is a hard-coded 80th percentile that forces REM to 20%
> of sleep by construction, which we have flagged as unreportable since 2026-08-03.
> **The reference tool solves exactly that problem, and our own "Otsu cross-check" is already
> the closer match to it.**
>
> Second finding: **their delta band for staging is a 0 to 4.5 Hz low-pass**, which conflicts with
> the 1-4 Hz we adopted from the paper earlier the same day. The paper's 1-4 Hz is the band used
> for **reporting spectra**; the tool's 0-4.5 Hz is the band used for **staging**. Those are two
> different jobs and we currently use one constant for both.

Source files: `~/Downloads/SleepyScoreApp_HM_260312_exported.m` (3,372 lines),
`~/Downloads/sleepy_pipeline_refined.py` (518 lines).
Paper method: [[2026-08-07-council-review-of-the-analysis-pipeline]] §4.1, Nakata et al. SLEEP 2025.

## 1. Their algorithm, exactly

```
fs = 250 Hz, epoch = 4 s, 1000 samples per epoch

EMG   2nd-order Butterworth HIGH-PASS at 30 Hz
      emg_integral   = sum(|filtered|) over the epoch      <- rectified integral
      emg_var        = var(raw)
      emg_activity   = emg_var / emg_integral

EEG   2nd-order Butterworth LOW-PASS  at 4.5 Hz  -> delta_integral = sum(|filtered|)
      2nd-order Butterworth BAND-PASS 6 to 9 Hz  -> theta_integral = sum(|filtered|)
      td_ratio = theta_integral / delta_integral

Spectra: Welch, BARTLETT window, nfft = 1024, reported to 120 Hz in 0.5 Hz bins

STAGING
  emg_thresh, sleep_mask = kmeans(emg_integral, k=2)
        wake cluster = the one with the HIGHER centre
        threshold reported = mean of the two centres
        ⚠️ sleep_mask comes from the CLUSTER ASSIGNMENT, not from the threshold
  td_thresh = kmeans(td_ratio[sleep_mask], k=2), threshold = mean of the two centres

  WAKE = emg_integral >  emg_thresh
  REM  = sleep_mask AND td_ratio > td_thresh
  NREM = sleep_mask AND NOT REM
  invalid (non-finite) -> -1

Stage codes: WAKE = 0, NREM = 10, REM = 20
```

Fallbacks when a recording is degenerate: fewer than 10 finite values, or fewer than 2 unique
values, falls back to the **median**. Worth copying; our pipeline currently just produces `{}`
thresholds in that case, which caused a `KeyError` crash on 2026-08-08.

## 2. Ours against theirs

| step | SleepyScore | ours | verdict |
| --- | --- | --- | --- |
| sample rate | 250 Hz | 1 kHz decimated to 250 Hz | ✅ same |
| epoch | 4 s | 4 s | ✅ same |
| theta band | **6-9 Hz** | 6-9 Hz | ✅ same |
| **REM threshold** | **k-means, 2 clusters, on T/D among sleep epochs** | **80th percentile → forces REM to 20%** | 🔴 **the big one** |
| **WAKE threshold** | k-means, 2 clusters, on EMG integral | **Otsu on log10(EMG rms)** | 🟡 both are 2-class splits on 1-D data, so these are near-equivalent in spirit |
| **delta band (staging)** | **low-pass 0-4.5 Hz** | 1-4 Hz since 2026-08-08 | ⚠️ conflict, see §3 |
| **EMG filter** | **high-pass 30 Hz** | band-pass 10-300 Hz | ⚠️ differs |
| **delta / theta features** | **time-domain rectified integral**, `sum(abs(filtered))` | **Welch PSD band power** | ⚠️ differs, see §4 |
| spectral window | Bartlett, nfft 1024 | Hann, nperseg 2048 | minor |
| degenerate-input fallback | median | none, previously crashed | 🟡 adopt theirs |
| minimum bout | **none anywhere in the code** | 3 epochs, 12 s, our house rule | confirms the paper: **not their rule** |

> [!success] ⭐ Their WAKE rule and ours are closer than they look
> k-means with k=2 on a 1-D array and Otsu's method are both "split this distribution into two
> classes at the point that best separates them". Otsu maximises between-class variance; k-means
> minimises within-class variance. On 1-D data these are the same objective. **So our Otsu WAKE
> cut is a fair implementation of their approach** — which also means the ±25% sensitivity we
> measured on 2026-08-08 applies to their tool too.

## 3. ⚠️ The delta conflict, and how to resolve it

Earlier on 2026-08-08 we changed `BAND_DELTA` from 0.5-4 to **1-4 Hz**, citing the paper. The tool
uses a **low-pass at 4.5 Hz**, i.e. **0-4.5 Hz**. Both are correct, because they are used for
different things:

| purpose | band | source |
| --- | --- | --- |
| **staging** — the T/D ratio that separates NREM from REM | **0 to 4.5 Hz** | the tool's `delta_cutoff_hz = 4.5`, low-pass |
| **reporting** — delta power quoted in figures and text | **1 to 4 Hz** | the paper's "delta (1-4 Hz)" and "average of the EEG power of 1-4 Hz" |

**We currently use one constant for both jobs.** The fix is two constants, `BAND_DELTA_STAGING`
and `BAND_DELTA_REPORT`. Not applied yet.

⭐ Note that a 0-4.5 Hz low-pass on our data would include the 1.10 Hz hardware high-pass roll-off
region, but since that attenuation is already baked into the saved file it affects both labs' bands
equally on our recordings.

## 4. Time-domain integral versus PSD band power

They compute `sum(|band-pass filtered signal|)` per epoch. We compute Welch band power. These are
**not the same quantity**: a rectified integral is proportional to mean absolute amplitude, power
is proportional to amplitude squared. A T/D ratio built from integrals is therefore not numerically
comparable to one built from powers, and **any threshold transfers between the two only after
rescaling**.

This does not make either wrong. It does mean **we cannot quote their threshold values against our
features**, and it is one more reason the thresholds must be derived per dataset rather than
inherited.

## 5. Other things worth keeping

- **`.3eg` file format**, fully specified in `read_3eg_file`: repeating blocks of
  `[8-byte float64 timestamp][1000 × int16 EEG][1000 × int16 EMG]`, one block per 4 s epoch, file
  size an exact multiple of the block size. If we ever need to hand recordings to the Japanese tool,
  this is the writer spec.
- **`emg_activity = var(raw) / integral(|filtered|)`** — a feature we do not compute. It is a
  crude shape measure, high when EMG energy is concentrated in bursts rather than tonic. Might be
  useful for separating the movement artefact that we currently cannot distinguish on C1's EMG.
- The GUI exposes **manual spinner overrides** for all three thresholds (delta, theta, EMG) with a
  live hypnogram. So in practice **a human adjusts the automatic thresholds by eye**, which matches
  the paper's "semiautomatically analyzed ... followed by visual inspection".

## 6. What to do with this

| priority | action |
| --- | --- |
| 🔴 **1** | **Replace the 80th-percentile REM rule with a 2-cluster split.** This is the reference method, it removes the "REM is fixed by construction" problem, and our existing `rem_measured` Otsu cross-check is already most of the implementation |
| 🟡 2 | Split `BAND_DELTA` into staging (0-4.5 Hz) and reporting (1-4 Hz) constants |
| 🟡 3 | Adopt the **median fallback** for degenerate recordings instead of empty thresholds |
| 🟢 4 | Consider the 30 Hz EMG high-pass, and `emg_activity` as an extra feature |
| 🟢 5 | Keep the `.3eg` spec in case we need to feed their tool directly |

> [!danger] Do not apply item 1 before the kappa exists
> Swapping the REM rule changes every REM number we have. The 2026-08-07 council was explicit that
> method changes at n = 2 with no ground truth are unfalsifiable — we would not be able to tell
> whether the new rule is better. **The blind scoring packs are built and waiting**
> ([[2026-08-07-council-review-of-the-analysis-pipeline]] §6). Score them, then make this change
> and measure whether kappa improves.
