---
type: reference
area: eeg-analysis
status: superseded
status-note: "active"
superseded-by: "[[eeg-pipeline-manual]]"
tags: [scripts, eeg, scoring, methods, xdat]
created: 2026-08-03
---

# Sleep scoring — v2 (SUPERSEDED same day)

> [!warning] Updated 2026-10-22: `rescore_v2.py` is in `eeg-emg-analysis/archive/vault-scripts/rescore-v2-2026-08-03/`, and the pipeline path below was updated to `~/sleep-recording-skim/eeg-emg-analysis/pipeline/`. [[eeg-analysis-quickstart]]

> [!warning] Superseded 2026-08-03 by [[eeg-pipeline-manual]]
> `rescore_v2.py` fixed the persistence bug documented below and that fix is
> correct — it was carried forward unchanged. But its **QC thresholds were
> guesses**, and three of them were wrong:
>
> | | here | corrected | why |
> | --- | --- | --- | --- |
> | rail | 6300 µV | **6376.8 µV** | true rail is `0.195 × 32767` = 6389.6 µV, measured |
> | open | 300 µV | **150 µV** | mains is bimodal; the valley is at 134 µV, so 300 sat on the OPEN flank |
> | shorted | 25 µV | **split 11 / 20** | discarded 9.5 % of ALL epochs including real low-amplitude wake; a short is a CHANNEL property, not an epoch one |
>
> It also has a cosmetic reporting bug: animals whose verdict is set on an early
> return are written to the JSON but **omitted from the printed table**, so the
> console silently under-reports (caught on 2026-06-29/D1).
>
> **Use `~/sleep-recording-skim/eeg-emg-analysis/pipeline/` for all new work.** Keep this
> only to reproduce numbers published between 2026-08-03 morning and the pipeline.

Supersedes `../contact-state-2026-07-31/gate_and_score_all.py`, which contains a
statistics bug (see below).

Full explanation of everything here, written for a non-specialist reader:
[[2026-08-03-data-quality-report-for-professor]].

## Run it

```bash
export RESCORE_CACHE=/tmp/rescore_cache/
python3 rescore_v2.py <recording_base> [--force] [--json out.json]

# example
python3 rescore_v2.py allego_1__uid0731-18-06-37 --json run1.json
```

Pass 1 (feature extraction) must read the whole `.xdat`, so the first run takes
minutes to ~15 min depending on size. Results are cached; re-scoring is instant.
`--force` re-extracts.

## What it fixes

**BUG 1 — persistence was measured across time gaps.**
`r@1min` was computed as `np.correlate(...)[15]` on the array of epochs that
passed QC. Lag 15 epochs equals 60 s **only if those epochs are contiguous**.
Contact is intermittent, so that array is a concatenation of fragments and index
`k` / `k+15` can be hours apart.

- *False negative:* run-2 C2, 250 blocks of median 1 epoch → `r=+0.078`,
  reported "NO STRUCTURE". The test was **impossible to pass**, not failed.
- *False positive:* 07-13 D2 → `r=+0.854`, the best number in the project. Its
  longest contiguous block is **39 min of 100% WAKE**.

Fixed by computing autocorrelation strictly **within** each unbroken block, then
combining as a weighted mean. Blocks shorter than the lag contribute nothing.
The shuffle control permutes **within** blocks, so it isolates temporal order.

**Calibration** (synthetic alternating states, same code):

| true mean bout | measured `r@1min` |
| --- | --- |
| pure noise (4 s) | −0.035 |
| 30 s | +0.112 |
| 2 min | +0.214 |
| 4 min | +0.510 |
| 10 min | +0.703 |

So the `r > 0.30` threshold ≈ consolidated bouts of **3 min or longer**.

**BUG 2 — REM fraction is fixed by construction.**
`rem = (~wake) & (td >= percentile(td, 80))` makes the REM share an artefact of
the rule. It is still computed (needed to test REM's *order* properties) but the
field is named `rem_pct_CONSTRUCTED` and **must not be reported as a finding**.
What is evidence is that REM is entered from NREM, not WAKE.

## Channel map (corrected 2026-08-01)

RHD2216 is a **bipolar** chip — each channel is already a difference.

```
port base + 0   = /1    = EEG   <- use directly, do NOT subtract
port base + 1   = /2    = EMG   <- use directly, do NOT subtract
port base + 2,3 = /3,/4 = EMPTY PADS, no wire attached
second animal on a 64-ch splitter port: base+32, base+33 = /33, /34
```

**Layout is read from the file, never assumed.** Recordings exist at 64 ch/port
(two animals) and 32 ch/port (one animal), including mixed layouts such as
`A:64@0 B:32@64 C:64@96 D:64@160`. Assuming 64 would mis-map the older files.

## The gate — an epoch must pass all three

| test | rule | catches |
| --- | --- | --- |
| OPEN | 55–65 Hz < 300 µV on EEG **and** EMG | electrode not connected (open channels run 1000–4700 µV; connected 9–90 µV) |
| SHORTED | EEG rms ≥ 25 µV | dead/shorted channel (sits 16–21 µV, scores ~100% WAKE) |
| CLIPPED | railed fraction < 0.001 | amplifier saturation (cause of the 2026-07-15 retraction) |

## A mouse is SCOREABLE only if all four hold

1. ≥ 15 min usable **and** ≥ 15 min inside blocks ≥ 124 s
2. within-block `r@1min > 0.30` vs shuffle
3. physiology passes (WAKE highest EMG; NREM most delta + largest amplitude;
   REM highest theta/delta + low EMG)
4. wake fraction between 15% and 90%

Supporting evidence: REM entered from NREM (expect > 70%).

## Gotchas

> [!danger] `NPERSEG = 2048` — do not lower it
> At `nperseg=512` the resolution becomes 1.95 Hz, theta 6–9 Hz spans ONE FFT
> bin, and `np.trapz` over a single point returns **exactly zero**, silently
> destroying every REM measurement with no error raised.

- **Otsu threshold is per animal.** Never reuse one animal's threshold on
  another — that is what wrongly passed D2 on 2026-08-01.
- **Verdicts carry their reason.** `INSUFFICIENT` means the question could not be
  asked, which is *not* a negative result.
- **Animal names are positional.** `D2` in one recording is not necessarily the
  same animal as `D2` in another.
