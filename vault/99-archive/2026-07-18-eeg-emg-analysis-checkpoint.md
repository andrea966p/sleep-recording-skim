---
tags: [decision, eeg, emg, analysis, checkpoint, sleep64]
created: 2026-07-18
status: complete
---

# EEG + EMG analysis codebase — strong checkpoint (2026-07-18)

> [!abstract] TL;DR
> I rebuilt the EEG/EMG analysis code into a clean standalone project at
> `Monitoring_project/eeg-emg-analysis/`, split into three jobs (quality check,
> convert, sleep analysis) over a shared core. The big win is that the **8-mouse
> channel enumeration is now derived from each file's own metadata and validated**,
> so an animal's channels can no longer be silently mislabeled. The old vault
> scripts predated the sleep64 8-headstage rig and carried real bugs, so I archived
> them. Every module was run end-to-end on a real 8-mouse recording. The signal
> ordering question (where filters and the bipolar difference go) is decided:
> BIPOLAR DIFFERENCE FIRST, then filter, then decimate.

## Why I did this

The rig is now a fixed 8-headstage, 8-mouse setup (the sleep64 map, 2026-07-13),
but the analysis scripts still living in the Obsidian vault predated it. They
defaulted to the old single-mouse map, `--config 2mice32` had started throwing
`KeyError` after a rename, `multimouse_scan.py` had four separate bugs, and
`eeg_pipeline.py` was quietly decimating the electromyography (EMG) signal down to
256 hertz and truncating its band to 10 to 127 hertz. For a "strong checkpoint" I
wanted correct code, in its own folder I can open from VSCode or MATLAB, fact
checked against recent reliable sources, with the channel map impossible to get
wrong. The user picked Python only (with MATLAB and European Data Format export),
a sleep module that stops at features plus a first-pass hypnogram, and a fresh
folder with the old scripts archived.

## What exists now

`Monitoring_project/eeg-emg-analysis/`:

- `core/` — `config.py` (every constant, one source of truth), `xdat_io.py` (XDAT
  reader, memory-mapped for the multi-hour 8-mouse files), `channel_map.py` (THE
  8-mouse map), `dsp.py` (the one signal pipeline).
- `qc/qc_scan.py` — the quick "is it scorable?" check. Run it after any rig change
  or new mouse.
- `convert/to_edf.py`, `convert/to_mat_csv.py` — export to European Data Format
  Plus (EDF+) and MATLAB `.mat` / comma-separated values.
- `sleep/features.py`, `sleep/hypnogram.py` — per-epoch features and a first-pass
  heuristic hypnogram plus a "is there real sleep here" biology gate.
- `README.md`, `examples/run_all.sh`, `requirements.txt`.

## The channel contract (the part that must never be wrong)

Always 8 mice: 4 XDAQ ports A/B/C/D, each split by a C3442 into 2 headstages.
Mice named M + port + slot: MA1 MA2 MB1 MB2 MC1 MC2 MD1 MD2. Slot 1 sits at the
port base, slot 2 at base plus 32. Global base rows are 0, 32, 64, 96, 128, 160,
192, 224. Per mouse, 4 consecutive native rows: +0 electroencephalography (EEG)
frontal-left (red, plus), +1 EEG parietal-left (black, minus), +2 EMG (yellow,
plus), +3 EMG (blue, minus). Green (parietal-right dura) is the ANIMAL GROUND to
the GND bus and is NOT recorded, and REF is empty because the RHD2216 is bipolar.
EEG and EMG are differenced offline.

The code DERIVES this from `sapiens_base.sensors_by_port` in each `.xdat.json`
(never hardcoded) and then VALIDATES it against the expected 8-slot, 64-channel
layout, printing a loud warning (or raising, in strict mode) if a file does not
match. Provenance for the montage itself is Iwasaki et al., STAR Protocols 2021,
from the professor's home lab (IIIS Tsukuba).

## The signal-processing order (the open planning question, now decided)

BIPOLAR DIFFERENCE FIRST, then filter, then decimate.

1. Bipolar difference on the raw wideband: EEG is row+0 minus row+1, EMG is row+2
   minus row+3. Subtracting the pair removes common-mode pickup (including shared
   60 hertz) before any filter touches it, and it is the montage a scorer expects.
2. Filter the bipolar signal, Butterworth, zero-phase: EEG bandpass 0.5 to 30
   hertz (NO mains notch, because the 30 hertz low-pass already sits below 60 and
   removes it, so a notch would only add ringing near the spindle band); EMG 60
   hertz notch plus harmonics THEN bandpass 10 to 100 hertz (the notch IS needed
   here because the EMG band spans 60).
3. Decimate, anti-aliased: EEG to 256 hertz, EMG kept at 500 hertz. EMG is
   deliberately NOT dropped to 256, which was the old bug.

Quality-check code does the opposite on purpose: it under-filters, so hum,
railing, and clipping stay visible.

> [!quote] Paper-ready
> EEG and EMG are formed as offline bipolar derivations from the raw 1 kilohertz
> wideband recording, then band-pass filtered with a zero-phase Butterworth filter
> (EEG 0.5–30 Hz; EMG 10–100 Hz with a 60 Hz notch and harmonics), and decimated
> (EEG 256 Hz, EMG 500 Hz) prior to epoching.

## Fact-check sources

Montage and 4-second epoch: Iwasaki et al., STAR Protocols 2021 (IIIS Tsukuba).
Theta 6 to 9 hertz over delta 0.5 to 4 hertz plus EMG root-mean-square as the
discriminators: SPINDLE (Miladinovic et al., PLoS Computational Biology 2019).
Validated automated scorers for the eventual handoff: AccuSleep (Barger et al.
2019), IntelliSleepScorer (2023, light gradient boosting machine), REST (SLEEP
Advances 2026, also 4-second epochs).

## Verification I actually ran

- `channel_map.py` on the 8-mouse run `allego_0__uid0713-12-59-49` printed all 8
  mice with the exact canonical rows; on the single-mouse test file it warned
  loudly and still produced the one mouse.
- `qc_scan.py` on the same 8-mouse run correctly flagged EVERY mouse as EEG OPEN
  with heavy 60 hertz hum and EMG railing, which matches the known reality of that
  recording (the open-frontal-electrode saga).
- On a short 8-mouse file (`allego_0__uid0715-09-35-16`, 6.6 minutes) features,
  hypnogram (with the biology gate correctly saying "no clear sleep biology"), EDF+
  (16 signals, EEG at 256 and EMG at 500 hertz), and `.mat` (8-mouse struct, EMG
  longer than EEG, proving the rate fix) all ran and read back cleanly.

## Still open

- No scoreable biology yet exists to validate the hypnogram against, because the
  frontal electrodes are still open on every mouse (see [[eeg-60hz-saga]]). The
  hypnogram is explicitly a NON-VALIDATED screening heuristic until then.
- The eventual rigorous path is the EDF+ handoff to a validated scorer (AccuSleep /
  SPINDLE / human); which one is not yet chosen, and it needs labeled calibration
  epochs we do not have yet.
- Impedance is not in the XDAT file; quality-check reminds you to read it live in
  Allego, and can ingest an exported impedance comma-separated values file if you
  save one.

## Related
- [[eeg-60hz-saga]] · [[allego-electrode-setup-sleep64]] ·
  [[04-processing-guidelines]] · [[tsukuba-sleep-recording-method]]
