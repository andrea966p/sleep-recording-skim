---
type: incident
area: eeg-analysis
status: active
tags: [troubleshooting, symptom, eeg, analysis, pipeline, python]
created: 2026-08-03
---

# EEG analysis — what to do when a step misbehaves

> [!warning] Updated 2026-10-22: The commands here assume the old vault `pipeline/` folder. The code is now in `~/sleep-recording-skim/eeg-emg-analysis/`; run a stage as `PYTHONPATH=. python3 pipeline/<stage>.py` from there, or it stops with `ModuleNotFoundError: No module named 'core'`. The operating manual is [[eeg-pipeline-manual]]. [[eeg-analysis-quickstart]]

> [!abstract] TL;DR — for non-technical readers
> **What this is.** A symptom lookup for the analysis side only, everything
> that happens *after* a recording exists on disk. Rig, electrode and grounding
> problems are not here.
>
> **Why it exists.** Most of these have already cost us real time, and several
> of them fail **silently**: no error, no crash, just a wrong number. A silent
> failure you have seen before is cheap; one you have not is expensive.
>
> **How to read this page.** Find your symptom in the table, jump to the
> section. Terms you do not recognise are in [[eeg-analysis-glossary]].
>
> Procedure: [[_eeg-analysis-hub]].

## Symptom index

| What you see | Section |
| --- | --- |
| `numpy.core.multiarray failed to import` | [1](#1-numpy-core-multiarray-failed-to-import) |
| Fewer mice came out than went in | [2](#2-fewer-mice-came-out-than-went-in) |
| `no per-mouse .npz files found -- run stage 2 first` | [2](#2-fewer-mice-came-out-than-went-in) |
| `<base>: no animals in layout` | [3](#3-base-no-animals-in-layout) |
| Stage 2 re-runs but the file does not change | [4](#4-a-stage-re-runs-but-nothing-changes) |
| Stage 1 takes 15 minutes again after a reboot | [4](#4-a-stage-re-runs-but-nothing-changes) |
| Theta power is exactly `0.0` everywhere, REM never appears | [5](#5-theta-is-exactly-zero-and-rem-never-appears-silent) |
| `r@1min` is implausibly high on obviously bad data | [6](#6-ratmin-is-implausible-silent) |
| The recording landed in the wrong day folder | [7](#7-the-recording-landed-in-the-wrong-day-folder) |
| The best animal vanished from the results | [8](#8-the-best-animal-vanished) |
| Impedance table has rows for `/3` and `/4` | [9](#9-impedance-rows-for-3-and-4) |
| Every channel reads about 30 µV rms and I cannot tell them apart | [10](#10-everything-reads-about-30-v-and-you-cannot-tell-channels-apart) |
| EDF opens but the screen is blank | [11](#11-edf-opens-but-the-screen-is-blank) |
| One animal passes and a near-identical one does not | [12](#12-one-animal-passes-and-a-near-identical-one-does-not) |
| Allego floods the log with filter errors | [[allego-iir-filter-design-errors]] |

---

## 1. `numpy.core.multiarray failed to import`

**Cause.** You used the wrong Python. `/opt/neurosurveillance/venv` has a numpy
and scipy built against different versions, an ABI mismatch. It is fine for the
session daemon and broken for analysis.

**Fix.** Use the system interpreter.

```bash
python3 stage1_qc.py allego_1__uid0731-18-06-37
```

Check which one you are on if unsure:

```bash
which python3
```

Expect `/usr/bin/python3`. If it says anything under `/opt/neurosurveillance`,
deactivate the virtual environment first.

> [!note] Confirmed still correct 2026-08-22, with the reason spelled out
> `/usr/bin/python3` has **numpy 1.26.4 + scipy 1.11.4**, which match.
> `/opt/neurosurveillance/venv` has **numpy 2.2.6** but no scipy of its own, so it
> falls through to the system scipy compiled against numpy 1.x — hence the crash.
> 🔑 **`radiens` lives ONLY in the daemon venv, and analysis does not need it.**
> radiens is for talking to Allego (starting and stopping recordings). Reading
> `.xdat` needs nothing but numpy. So: **recording → daemon venv, analysis →
> system python3.**

> [!warning] If you use `~/eeg-analysis-venv` instead, you meet the opposite problem
> That venv has **numpy 2.5.0**, and numpy 2.0 **removed `np.trapz`**. Before
> 2026-08-22 the pipeline used it and died with
> `module 'numpy' has no attribute 'trapz'`. Stages 1 and 3 now bind
> `np.trapezoid` when it exists and fall back to `np.trapz`, so the pipeline runs
> on **either** numpy. Nothing else in the pipeline is numpy-2 sensitive as of
> this date, but that has not been exhaustively checked.

---

## 2. Fewer mice came out than went in

**This is the most common confusion and it is usually correct behaviour.**

Stage 2 writes only animals whose stage 1 verdict is `CLEAN` or `DIRTY`. A mouse
whose electrode was `OPEN` all night has no per-mouse file because it has no
data, not because the split failed.

**Check what stage 1 actually said before assuming a bug:**

```bash
python3 stage1_qc.py <recording_base>
```

It prints a verdict and a **reason** per animal. Read the reason.

**If you want every mouse anyway** — handing a complete set to a colleague, or
inspecting a failure — use the archival flag:

```bash
python3 stage2_split.py --all-verdicts <recording_base>
```

The verdict still travels inside `meta["qc"]` and in the folder `README.txt`, so
an `OPEN` animal cannot be mistaken for a scoreable one.

> [!warning] `--all-verdicts` is for handover, not for choosing data
> Do not use it to pick data to analyse. It exists so a complete set can be
> shipped without the missing mice looking like a processing failure.

`no per-mouse .npz files found -- run stage 2 first` from stage 3 means the same
thing one step later: stage 2 wrote nothing into that day folder.

---

## 3. `<base>: no animals in layout`

**Cause.** The pipeline derives the channel layout from `sensors_by_port` in the
recording metadata, and found no port carrying a usable slot. Usually the
recording was made with a channel selection that does not match the rig, for
example only `/1` selected, or a probe map that repacks channels.

**Fix.** Check what the file says it contains:

```bash
python3 -c "import json,sys; d=json.load(open(sys.argv[1]))['status']; print(d['signals']); print(d.get('sensors_by_port'))" \
    /home/skimlab/radix/data/<base>.xdat.json
```

Expected for the 8 mouse rig: four ports at 64 channels each, `/1 /2 /33 /34`
selected per port. If it does not match, the recording itself was set up wrong,
which is an acquisition problem: [[CANONICAL-allego-channel-selection]].

> [!warning] Never hard-code a layout to work around this
> Recordings exist in this project at 32 channels per port, 64 per port, and
> mixed (`A:64@0 B:32@64 C:64@96 D:64@160`). The layout must stay derived.

---

## 4. A stage re-runs but nothing changes

**Cause.** Both stage 1 and stage 2 skip work that already exists. Stage 1
caches its per-epoch features, stage 2 refuses to overwrite an existing
`.npz`.

**Fix.** Force it.

```bash
python3 stage1_qc.py --force <recording_base>     # recompute features
python3 stage2_split.py --force <recording_base>  # overwrite existing files
```

**The mirror image of this** — stage 1 taking 15 minutes again when you expected
it to be instant — is the same mechanism. The cache lives under `$HOME`:

```
EEG_QC_CACHE   default /home/skimlab/eeg-qc-cache/  (was /tmp until 2026-09-23)
```

It used to live in `/tmp`, which is cleared on reboot; that destroyed three QC bundles on 2026-09-22 and the cache moved to `$HOME` on 2026-09-23.
Point it somewhere persistent if that matters:

```bash
export EEG_QC_CACHE=/home/skimlab/eeg-processed/_cache
```

Other overrides: `EEG_DATA_DIR`, `EEG_PROCESSED_ROOT`, `EEG_IMPEDANCE_DIR`.

> [!important] Always `--force` stage 1 after changing a threshold
> Editing `qc_thresholds.py` does not invalidate the cache. Without `--force`
> you will get the old verdicts and believe the new thresholds changed nothing.

---

## 5. Theta is exactly zero and REM never appears (SILENT)

**Cause.** `nperseg` was lowered. Frequency resolution is `df = fs / nperseg`.
At `nperseg = 512` and `fs = 1000`, `df = 1.95 Hz`, so the 6 to 9 hertz theta
band spans a **single** frequency bin, and integrating over one point returns
exactly `0.0`.

**No error is raised.** Every REM measurement quietly becomes zero.

**Fix.** Leave `NPERSEG = 2048` alone. `df = 0.49 Hz`, theta spans about six
bins. If you ever must change it, check the bin count first:

```python
n_bins = (9.0 - 6.0) / (fs / nperseg)   # must be comfortably > 1
```

Full explanation in [[eeg-analysis-glossary]] under `nperseg`.

---

## 6. `r@1min` is implausible (SILENT)

**Symptom.** A persistence value that is far too good on data you can see is
bad, or far too poor on data that should pass.

**Cause.** Autocorrelation computed **across** contact gaps. Once failing epochs
are dropped, the array is stitched fragments, so epoch `k` and epoch `k+15` can
be hours apart in real time while sitting next to each other in memory. A one
minute lag is only one minute if the epochs are contiguous.

**This failed in both directions:** `+0.854` on a stretch that is 39 minutes of
pure wake (the project's largest false positive), and `+0.078` on data that could
not possibly have passed.

**Fix.** Compute it strictly inside unbroken `blocks`, then take a weighted mean
across blocks. The current pipeline does this. The superseded
`scripts/contact-state-2026-07-31/gate_and_score_all.py` does **not** — do not
resurrect it, and treat any `r` value quoted from before 2026-08-03 as
unreliable. The corrected implementation is
`scripts/rescore-v2-2026-08-03/rescore_v2.py` and it is folded into
`stage3_features.py`.

> [!danger] The same trap applies to anything with a time lag
> Bout length, transition probability, spectral change over time. If your
> statistic looks backwards or forwards in time, it must not cross a block
> boundary.

---

## 7. The recording landed in the wrong day folder

**Cause.** Two timestamps disagree and they are in different time zones.
Allego's metadata `start_time` is **UTC**; the `uidMMDD-HH-MM-SS` token in the
filename is **local (KST)**. Mixing them puts a recording a day out.

**Fix.** The pipeline takes the day from `start_time` converted to KST, and
records which source it used as `start_source` in the QC JSON. Check that field
before deciding a folder is wrong.

```bash
python3 -c "import json,sys; print(json.load(open(sys.argv[1]))['start_source'])" \
    /home/skimlab/eeg-processed/<date>/qc/qc_<recording>.json
```

Recording directories on the video side are UTC as well — same trap, different
system.

---

## 8. The best animal vanished

**Cause.** `--clean-only`.

C1 on 2026-07-31 is the best animal in the project, 8.73 hours inside a single
block, and its verdict is `DIRTY`, because the other 19 hours of that recording
are open. `--clean-only` silently drops it.

**Fix.** Do not default to clean-only. `DIRTY` means "the recording is patchy",
not "the data is bad".

---

## 9. Impedance rows for `/3` and `/4`

**Cause.** A raw sweep file was read instead of the parsed
`impedance_summary.csv`. Pads 2 and 3 on the connector are wired to EMG, and
`/3` and `/4` correspond to **empty amplifier inputs with no wire on them**.
They float, so they read as multi-megaohm and drag every summary statistic
towards "everything is broken".

**Fix.** Read only `/1` and `/2`. The pipeline already filters this; if you are
looking at a sweep by hand, filter it yourself. Including the empty pads is what
produced the misleadingly bleak early impedance statistics.

> [!warning] An unwired amplifier input and an open electrode are indistinguishable
> Both float, both show huge mains. Impedance alone cannot separate them.

---

## 10. Everything reads about 30 µV and you cannot tell channels apart

**Cause.** rms alone cannot distinguish a **connected EMG channel** from an
**inactive slot**. Both sit near 30 µV.

**Fix.** Use three signatures together, never rms alone:

| state | rms | 60 Hz mains | other |
| --- | --- | --- | --- |
| connected | 30 to 90 µV | **6 to 20 µV** | structured spectrum, Z 0.07 to 2 MΩ |
| floating / open | 200 to 4700 µV | **150 to 4500 µV** | Z 5 to 9 MΩ |
| inactive slot | ~30 µV | **~3 µV** | ~93% of power above the EEG band, flat; Z ~0.06 MΩ (internally tied) |

Mains amplitude is the discriminator, not amplitude.

---

## 11. EDF opens but the screen is blank

**Symptom.** EDFbrowser reports "the files are opened but no signals are added
to the screen", or the window shows flat or empty traces.

**Cause is almost never the file.** Our EDF+C export has been validated byte by
byte: header 1024 bytes, `EDF+C`, three signals, file size exact to the byte,
and decoded records reproduce the `.npz` rms to one decimal place. Round-trip
error is 0.195 µV, exactly one LSB, which is pure quantisation.

**Fix, in order:**

1. In the signal dialog, select the signals **and** click *Add*, then *Close*.
   Selecting alone does nothing.
2. Set the vertical scale. EDFbrowser defaults to `default_amplitude = 100` µV
   with `default_fit_signals_to_pane = 0`. An open-electrode channel carries
   about 3500 µV of hum, so the trace is drawn far outside the pane and the
   screen looks empty. Turn *fit to pane* on, or raise the amplitude.
3. Remember the third signal is the annotations channel, not data.

**If you genuinely suspect the file,** verify rather than guess:

```bash
python3 -c "
import numpy as np
h=open('FILE.edf','rb').read(1024)
print(h[192:236])   # header bytes, record count, signal count
"
```

---

## 12. One animal passes and a near-identical one does not

**Cause.** Almost always the per-animal Otsu threshold on EMG.

The wake/sleep split is computed **per animal**, because muscle tone amplitude
depends on where the wires ended up in that individual's neck. Two animals with
similar-looking traces can legitimately land on different thresholds.

**Fix.** Nothing — this is correct. What is *not* correct is reusing one
animal's threshold on another, which is what wrongly passed D2 on 2026-08-01.

**Also check** that you are not comparing animals across recordings by name.
Names are **positional**: `D2` in one recording is not necessarily the same
mouse as `D2` in another.

---

## 13. A position produces NO states at all: `physiology FAIL: states missing`

**Cause.** Its **EMG electrode is open**, so there are zero epochs that pass QC and
nothing to stage. Seen on B2, 2026-08-19: EEG mains 72.7 µV (fine), **EMG mains
535.8 µV** against the 150 µV `OPEN_UV` limit. Stage 1 requires **both** channels
under the limit, because WAKE is separated from sleep by an Otsu split on
**log EMG RMS**. With an open EMG that cut measures amplifier noise.

**This is the correct answer, not a failure to try.** Do not work around it by
forcing a threshold.

**What you can still use.** The hypnogram CSV is written, with `state` = `EXCLUDED`
on every epoch, but the **EEG-derived columns are valid** for all epochs:
`eeg_rms_uv`, `delta`, `theta`, `theta_delta`, `zt_h`. Fine for spectral work.

⚠️ **Do not invent an EEG-only stager to fill the gap.** Single-EEG mouse staging is
a real published approach (https://www.nature.com/articles/s41598-021-90332-1) but
this project has neither implemented nor validated one, and an unvalidated staging
algorithm is exactly how a confidently wrong result is produced.

---

## The one that is not an analysis problem

> [!danger] If most of your data fails QC, the analysis is not the problem
> The bottleneck in this project is **electrical contact at the electrode**, and
> nothing else is close. An open electrode appears in 36 of 41 animal
> recordings. Median EEG mains is 3379 µV against a 150 µV limit. No threshold
> choice, no filter and no scoring method recovers a channel that was not
> electrically connected.
>
> Rig side: [[signal-quality-and-grounding]],
> [[2026-07-31-contact-intermittency-no-wire-control]],
> [[electrode-failure-and-impedance-literature]].

## Related
- [[_eeg-analysis-hub]] — the ordered procedure
- [[eeg-analysis-glossary]] — every term and parameter
- [[analysis-methods-and-justification]] — what is standard and what is ours
- [[allego-iir-filter-design-errors]] — acquisition-side filter log noise
- `02-procedures/eeg-data-analysis/pipeline/README.md` — the operating manual


---

## Symptoms added 2026-08-08

### The filtered trace looks like beautiful EEG but the animal is not connected
**Cause.** Notch + band-pass applied to a **wire-free amplifier input** yields a median **69 µV of
smooth, plausible, EEG-looking signal**. Filtering manufactures a convincing trace from nothing.
**Fix.** Never judge by trace morphology. Classify by **spectral slope against the in-file floor**.
See [[per-animal-failure-signatures]] and [[2026-08-06-recording-data-quality-preregistration]] §10.

### Impedance says the channel is excellent, the recording says it is noise
**Cause.** Impedance measures that the **wire is connected**; it cannot see what rides on it. A1's
EMG was called excellent (p = 1e-16) while 296 of its 331 µV rms was mains hum.
**Fix.** Impedance screens, the recording decides.

### A duty-cycle block gives a hugely significant result that a recording later reverses
**Cause.** A 40-sweep block spans ~21 min and contact states persist longer than that, so the block
can sample **one state** and report it at p = 1e-07. This happened on 2026-08-06 and was reversed.
**Fix.** Quote the block's **duration** beside its duty cycle. Never conclude harm or benefit from a
block alone.

### Bout counts are enormous and median bouts are one epoch
**Cause.** No minimum bout duration was enforced. B1 showed 1,672 NREM bouts with a 4 s median.
**Fix.** `MIN_BOUT_EPOCHS = 3`. Counts fell six- to tenfold and medians rose to 40-84 s.

### Persistence jumps after a change that added no information
**Cause.** Smoothing short bouts raises the state sequence's autocorrelation **by construction**.
`r@1min` went 0.603 → 0.742 with no new data.
**Fix.** Compute persistence and the REM-order check on the **raw** labels, architecture on the
smoothed ones.

### "Physiology 5/5 PASS" but the states are still not trustworthy
**Cause.** Four of the five checks **restate the staging rule** and cannot fail.
**Fix.** Report `physiology_informative_pass` only. The summary now prints which checks are forced.

### The circadian result agrees beautifully with the literature
**Cause.** It may be a coincidence of where the WAKE threshold landed. ±25% on the Otsu cut moves
D2 from **23% to 89%** asleep in the light phase.
**Fix.** Quote the sweep's swing beside the number. The summary prints it automatically.

### stage2_split.py fills `impedance/` with the wrong files
**Cause.** It flattens sweep blocks together and pulls in other days' sweeps.
**Fix.** Check `impedance/` after every stage 2 run.

### `KeyError: emg_otsu_log10`
**Cause.** `stage()` returns an empty threshold dict for a recording with no usable epochs.
**Fix.** Guarded 2026-08-08; a median fallback now mirrors the Japanese tool's behaviour.
