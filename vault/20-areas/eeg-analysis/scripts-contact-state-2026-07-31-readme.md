---
type: reference
area: eeg-analysis
status: superseded
status-note: "active"
superseded-by: "[[eeg-pipeline-manual]]"
tags: [scripts, eeg, contact-intermittency, methods, xdat]
created: 2026-08-01
---

# Contact-state analysis scripts (2026-07-31 / 2026-08-01)

Reproduces every number in [[2026-08-01-28h-contact-duty-cycle-and-c1-negative]] from the raw `.xdat`.

> [!danger] DO NOT USE FOR NEW WORK — two separate bugs, both since fixed elsewhere
> These scripts are kept **only** to reproduce historical numbers. They contain:
>
> 1. **The wrong channel map** (`EEG = native0 − native1`, and `/3`,`/4` treated
>    as electrodes). The RHD2216 is bipolar — corrected 2026-08-01.
> 2. **`gate_and_score_all.py` measures persistence ACROSS CONTACT GAPS.**
>    `np.correlate(...)[15]` is a 60 s lag only if the epochs are contiguous;
>    they are not. This produced both the project's largest false positive
>    (+0.854 on a stretch that is 39 min of pure wake) and a false negative
>    (+0.078 on data that could not possibly have passed).
>
> **Use `02-procedures/eeg-data-analysis/pipeline/` instead.**

## Run order

```bash
cd ~/Monitoring_project/Monitoring_project_obsidian_vault/02-procedures/eeg-data-analysis/scripts/contact-state-2026-07-31

python3 longrun_coarse.py                       # pass 1: 105 GB -> longrun_coarse.npz  (~5 min)
python3 summarize_states.py  longrun_coarse.npz # duty cycles, segments, sensitivity
python3 c1_window.py                            # pass 2: full-rate window -> c1_window.npz
python3 c1_sleep_structure.py c1_window.npz     # the four sleep tests
```

Edit the `D` / `F` constants at the top of `longrun_coarse.py` and `c1_window.py` to point at a different recording. `c1_window.py` also needs `T0`/`T1` (the connected window, in seconds) and `FRONT`/`PAR` (the two natives to subtract) set for the leg you care about.

## Why the design looks like this

**Two passes, because the file is 105 GB.** `.xdat` is sample-interleaved, so reading a handful of columns still pulls every byte off disk (~630 MB/s measured). A continuous full-rate pass over all channels was measured at **0.6 % in 90 s**, about 4 hours to finish. Pass 1 therefore analyses a **10 s window every 60 s** — unbiased for duty cycle, ~1/6 the I/O. Pass 2 re-reads only the window of interest at full 1 kHz.

⚠️ **Consequence: flip counts from pass 1 are LOWER BOUNDS.** A flip contained entirely within the unobserved 50 s is invisible. Never quote them as exact.

**Band power, not single bins.** Mains is not exactly 60.00 Hz and it drifts. A single 60.00 Hz FFT bin understates hum by 4-5×. Everything uses the 55-65 Hz band.

**Zero-phase filtering.** `sosfiltfilt` with 4th-order Butterworth SOS, so group delay cannot smear the timing of a state transition. Each window is padded 5 s per side before filtering and the pad discarded, so filter transients never reach a reported number.

**Controls run for the entire recording.** 16 internally tied floor pins (2 per headstage) are analysed identically to the legs. They are the standing proof that any weird result is not the instrument drifting.

**Clipping gate before statistics.** `c1_sleep_structure.py` conditions every number on epochs with zero clipped samples and always reports the clean fraction; it refuses below 60 clean epochs. This encodes the 2026-07-15 retraction, where a result computed over railed epochs flipped sign once clean epochs were selected.

## The two thresholds

| constant | value | why |
| --- | --- | --- |
| `OPEN_UV` | 300 µV (55-65 Hz band RMS) | sits in the empty gap of a sharply bimodal distribution (legs are <150 or >500) |
| `BIO_UV` | 25 µV (0.5-45 Hz band RMS) | "not open" ≠ "usable" — a leg SHORTED to ground is quieter than a good one |

`summarize_states.py` prints a threshold sweep. The headline is robust (80.3 % → 76.8 % OPEN across 150-600 µV) but **five chattering legs are threshold-sensitive** and their duty cycles carry roughly ±15 points of uncertainty. See the decision doc §3.3.

## Outputs

- `longrun_coarse.npz` — `mains`, `bio`, `clip` per window per channel, plus `sub_mains` (per-second inside each window, for locating fast transitions)
- `c1_window.npz` — per-epoch `delta`, `theta`, `sigma`, `tot`, `rms`, `clip`, `mains`

Both are intermediates and are cheap to regenerate; they live in the session scratchpad rather than the vault.

## Related

- [[2026-08-01-28h-contact-duty-cycle-and-c1-negative]] — the results
- [[electrode-connection-state-test]] — the OPEN/SHORTED/WORKING classifier and its controls
- [[03-scripts-and-usage]] — the wider analysis script collection
