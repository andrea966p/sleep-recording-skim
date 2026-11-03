---
type: procedure
area: hlb-sod1
status: active
created: 2026-11-03
summary: "How to rerun the 2026-11 HLB EEG re-score from the NAS CSVs: environment, the five scripts, timings, checks, what to look at when a number moves"
tags: [eeg, procedure, compute, hlb]
---

# HLB EEG re-score: compute runbook

> [!abstract] TL;DR
> On any machine with the SKIM NAS mounted at `/mnt/skimnas` and ≈ 60 GB free: make the venv,
> run five scripts in order. The 2026-11-03 run took ≈ 75 min on the ThinkPad, almost all of it
> the NAS copy (≈ 100 MB/s through Tailscale; `tailscaled` is the bottleneck, not the CPU). No GPU
> is needed: nothing is trained.

## Environment

```bash
uv venv -p 3.12 ~/hlb-eeg-venv
VIRTUAL_ENV=~/hlb-eeg-venv uv pip install numpy scipy pandas pyarrow scikit-learn hmmlearn matplotlib
```

```bash
git clone https://github.com/somnocode/SleepStager.git ~/sleep-recording-skim/SleepStager
```

The scripts import SleepStager's `features` and `rule` from `~/sleep-recording-skim/SleepStager`
(`main`, commit used on 2026-11-03: see `git -C SleepStager rev-parse HEAD` in the run log of
[[hlb-eeg-sleep-overview]]) and the project's `pipeline/pipeline_common.py` for r@1min.
Versions on 2026-11-03: Python 3.12, numpy 2.5.4, scipy 1.18.1, pyarrow 26.0.0, hmmlearn 0.3.3.

## Run

From `~/sleep-recording-skim/eeg-emg-analysis/rescore_2026_11`, with `D=~/sleep-data/hlb-rescore-2026-11`:

```bash
~/hlb-eeg-venv/bin/python ingest.py $D/arrays --jobs 3
```

```bash
~/hlb-eeg-venv/bin/python features.py $D/arrays $D/epochs --jobs 3
```

```bash
~/hlb-eeg-venv/bin/python score.py $D/epochs
```

Then the review figures, a first backbone (screen tiers only) and the final tiers. The final tiers
are the screen's tiers minus the demotions in `final_tiers.py`'s `OVERRIDES`, each with its review
evidence (2026-11-03: 7 windows):

```bash
~/hlb-eeg-venv/bin/python review_pack.py $D/arrays $D/epochs $D/review
```

```bash
~/hlb-eeg-venv/bin/python backbone.py $D/epochs $D/backbone
```

```bash
~/hlb-eeg-venv/bin/python final_tiers.py $D/backbone $D/review/final_tiers.json
```

The final backbone, statistics, figures, mouse notes and overview tables, chained so that one
failure stops the rest (never a wait loop):

```bash
P=~/hlb-eeg-venv/bin/python; V=~/sleep-recording-skim/vault; $P backbone.py $D/epochs $D/backbone $D/review/final_tiers.json && $P stats.py $D/backbone $D/results && $P figures.py $D/backbone $V/_attachments && $P mouse_notes.py $D/backbone $D/review $V && $P overview_tables.py $D/backbone $D/review/final_tiers.json > $D/overview_tables.md
```

`mouse_notes.py` needs `$D/review/review_result.json`, the agent review's output (archived in
`results/`). The per-batch tables in [[hlb-eeg-sleep-overview]] are pasted from `overview_tables.md`.

Every script skips what already exists except `score.py`, `backbone.py` and `review_pack.py`, which
overwrite. `--only <text>` restricts any of them to paths containing the text (`--only HLBSSD15`).

| script | per recording | memory | notes |
|---|---|---|---|
| `ingest.py` | ≈ 190 s with 3 jobs (NAS bound) | 3.5 GB per job | fails loudly on a sha256 mismatch |
| `features.py` | ≈ 47 s | 4.2 GB per job | asserts no counter gaps |
| `score.py` | ≈ 20 s (two HMMs, two EMG measures) | < 1 GB | prints one line per recording; an error skips that recording |
| `review_pack.py` | ≈ 15 s | < 1 GB | random seed 20261103 picks the contested epochs |

## Checks after a run

- `ingest.log`: 64 lines `ok … gaps=0`, no `FAIL sha`.
- `score.log`: 64 lines, no `ERROR`. The positive control **HLBSSL33 R** must read tier A,
  24 h usable, κ rule–HMM ≈ 0.9, wake ≈ 28 % light / 63 % dark.
- HLBSSD19 B (a dead EEG with a step-switching EMG) must stay tier X; HLBWSD01 R and HLBSSL38 B (dead EEG, log10 δ < 1) must not reach C.

## When a number moves

Change one thing, rerun from the stage it touches, and diff `epochs/screen_summary.csv` against
the archived copy in the repo (`eeg-emg-analysis/rescore_2026_11/results/`). A threshold change
is a method change: write it into [[hlb-eeg-scoring-method-2026-11]] with the date and the reason,
and never choose a threshold by which mice it lets in.
