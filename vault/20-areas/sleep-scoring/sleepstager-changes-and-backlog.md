---
type: reference
area: sleep-scoring
status: active
tags: [infrastructure, sleepstager, sleep-scoring, changelog, backlog]
created: 2026-10-07
---

# SleepStager: changes we made, and what to improve next

> [!abstract] TL;DR — for non-technical readers
> **What this is.** The log of every change made to SleepStager for this lab, and the list of
> improvements still to make, in priority order.
>
> **Why it exists.** SleepStager is the professor's program. Any change to it changes how mice are
> scored, so each one is recorded here with what it touched and how it was checked, and each idea
> waits here until the professor and Andrea decide.
>
> **How to read this page.** §1 says where the code lives and how changes reach the professor. §2
> is the change log, newest first. §3 is the backlog. §4 is loose ideas. How to use the program:
> [[sleepstager-user-guide]]. Big picture: [[nvr-system-overview]].

## 1. Where the code lives

| | |
|---|---|
| Repository | `~/sleep-recording-skim/SleepStager/`, its **own** git repo inside the workspace |
| Remote | `github.com/somnocode/SleepStager` (the professor's) |
| Sync | **not** covered by `./skim` (`SleepStager/` is in the workspace `.gitignore` since 2026-10-08); it needs its own `git push` |
| Our branch | `csv-reader` (created 2026-10-07) |
| Installed here | `~/.venvs/sleepstager` (editable install: code edits take effect on the next start) |
| Tests | `python scripts/eval/check_recording.py` (synthetic `.mat` + CSV); `scripts/eval/compare_csv_mat.py <csv> <mat>`; the offscreen smoke tests in `HANDOFF.md` need legacy `.3eg` data |

> [!warning] As of 2026-10-08 `csv-reader` is in PR #1, waiting for the professor; the tone row is local only
> Commit `7feb666` on branch `csv-reader`, in [PR #1](https://github.com/somnocode/SleepStager/pull/1).
> Nothing reaches `main` until the professor merges it. The tone row stays uncommitted on the SKIM
> workstation (backup of every local change: `~/sleep-data/sleepstager-local-changes.patch`), and so do the rules card and
> `scripts/eval/compare_csv_mat.py` (untracked).

> [!tip] On another machine: the same SleepStager, with Andrea's local changes
> The local changes (tone row, resume fix = PR #2, rules card) travel with the vault as
> [[sleepstager-local-changes.patch|sleepstager-local-changes.patch]], made against `csv-reader` at `7feb666`.
> ```bash
> cd ~/sleep-recording-skim && ./skim pull
> git clone https://github.com/somnocode/SleepStager.git SleepStager      # ignored by ./skim
> cd SleepStager && git checkout csv-reader
> git apply ../vault/01-infrastructure/sleepstager/sleepstager-local-changes.patch
> uv venv ~/.venvs/sleepstager --python 3.11 && uv pip install -p ~/.venvs/sleepstager -e .
> ```
> **Data and saves are not in the repo.** Copy the recording from the NAS to `~/sleep-data/...` (check its sha256 against
> `info.json`), and copy the save folder `4-sec sleepstager/` (~18 MB) from the machine that last scored it, or the program
> starts from the rule's stages again. After any change to the local code: `git diff > ~/sleep-data/sleepstager-local-changes.patch`
> and copy it here.
> **Claude's memory** for this work is in the synced `claude-config/memory/` (merged 2026-10-09). A session started *inside*
> `SleepStager/` uses its own memory slug: start Claude Code from `~/sleep-recording-skim`, or link that slug's `memory` folder to
> `claude-config/memory` as on the workstation.

## 2. Change log (newest first)

| Date | Change | Files | How it was checked | State |
|---|---|---|---|---|
| 2026-10-08 | **Rules card, session-2 rules**: edges now say where REM starts (θ > δ + σ down, rule late), C11 (quiet wake inside W → W) and C12 (one-sided arousal in NR → NR); the R→W→R line moved to the handbook only, so the card still fits | `viewer.py` (`_RulesCard.EDGES`) | offscreen at Andrea's 2334×1362: shown, 320 of 338 px | **local only** |
| 2026-10-08 | **"scoring rules" card** under the feature sliders: decision order with W/NR/R chips, edges, what to recheck; the wake cut is the recording's own; hides itself when the window is too short | `viewer.py` (`_RulesCard`) | offscreen at 2570×1370 (shown, 304 px) and 1440×768 (hidden); `_restage_smoke.py` pass | **local only** (Andrea) |
| 2026-10-08 | **Resume no longer brings back cleared rule marks**: the save replaces the marks on every epoch it covers (before, the fresh rule's marks were merged with it, so every mark cleared before saving came back) | `viewer.py` (`_maybe_resume`) | offscreen on HLBSSL33 R save AN_261007-2034: before 47 cleared marks back in 1–840, after 0 (exactly the save's 6); `_machine_pass_smoke.py` ALL OK; the bug is in `main` too (reproduced on a `.3eg`), not from the CSV reader | in [PR #2](https://github.com/somnocode/SleepStager/pull/2) (new smoke check: FAIL on `main`, ok with the fix) |
| 2026-10-08 | **Display notch `n` cycles off → 50 Hz → 60 Hz → off** (was 50 Hz on/off); the mains line is measured at 50 and 60 Hz on load and the status bar names the one found; session JSON `notch_hz` + `line60_peak` (was `notch_50hz`, read by nothing). **Display only**: the feature notch (backlog 1) is unchanged | `viewer.py`, `README.md`, `HANDOFF.md`, `scripts/_restage_smoke.py` | offscreen on HLBSSL33 R: line 60 Hz EEG 11.3×, EMG 2.9×, 50 Hz ~1×; drawn EMG 60 Hz line 20.9× → 50 Hz notch 21.0× (and −5 % real signal) → 60 Hz notch 0.1× → off 20.9×, trace restored, table unchanged | in [PR #1](https://github.com/somnocode/SleepStager/pull/1) |
| 2026-10-07 | **Unsaved-work marker**: red `● not saved` at the end of the header, `*` in the title bar (Qt `[*]`), cleared on save | `viewer.py` | offscreen: open → clean, edit → marker, save → cleared | in [PR #1](https://github.com/somnocode/SleepStager/pull/1) |
| 2026-10-07 | **Dossier row "tone (spike-proof)"** (`emg_tone_med`) under EMG, with the wake cut in the footer | `viewer.py` | offscreen on HLBSSL33 R: 617 tone 13.4 > cut 13.3 (W), 682 8.0 (NR), 333 21.9, 164 8.8 | **local only**: not in the PR (Andrea, 2026-10-08) |
| 2026-10-07 | **Rig per-mouse CSV reader** `read_rig_csv`: device counter → breaks, start from row-0 `datetime_kst` checked against `info.json` to 2 ms (a 9 h slip is refused), mouse ID from `info.json`; SleepStager's own output CSVs are refused | `recording.py` | synthetic CSV test (same breaks/clock as the `.mat` test; KST-as-UTC refused; output CSV refused) | in [PR #1](https://github.com/somnocode/SleepStager/pull/1) |
| 2026-10-07 | `.mat` and CSV share one counter → segments routine (`_segments_from_counter`) | `recording.py` | synthetic `.mat` test unchanged | in [PR #1](https://github.com/somnocode/SleepStager/pull/1) |
| 2026-10-07 | **Equivalence on real data**: HLBSSL33 R CSV vs a `.mat` split independently from the raw xdat | new `scripts/eval/compare_csv_mat.py` | 86.4 M samples identical (max Δ 0.000000 µV), clock Δ 0 µs, rule cuts and all features identical, **21,600 / 21,600 stages identical**; re-run 2026-10-08, same: CSV route settled, comparison `.mat` deleted | script **local only** (not in the PR, Andrea 2026-10-08) |
| 2026-10-07 | CSV load uses **pyarrow** directly: 24 h opens in ~1.3 s at ~4.2 GB peak (pandas' pyarrow engine peaked at 13.5 GB) | `recording.py`, `pyproject.toml`, `INSTALL.md`, `README.md` | `/usr/bin/time` on HLBSSL33 R (warm cache) | in [PR #1](https://github.com/somnocode/SleepStager/pull/1) |
| 2026-10-07 | **No move** for the rig layout: a file in a folder named like itself (`20260921_HLBSSL33_R/`) is its own session folder; output goes to `4-sec sleepstager/` inside it | `saves.py` | offscreen open → save: file stays, outputs inside the rig folder | in [PR #1](https://github.com/somnocode/SleepStager/pull/1) |
| 2026-10-07 | `split_xdat.py` reads **stripped** 16-channel xdat (channel positions from the strip report's `keep_labels`, not bank×64) | `scripts/split_xdat.py` | dry run maps HLBSSL33 to columns 4/5 = `B/1`,`B/2`, matching its `info.json` | in [PR #1](https://github.com/somnocode/SleepStager/pull/1) |
| 2026-10-07 | File dialogs list `*.3eg *.mat *.csv`; Settings note mentions CSV/KST | `viewer.py`, `settings.py` | — | in [PR #1](https://github.com/somnocode/SleepStager/pull/1) |

## 3. Backlog (priority order)

| # | Item | Why | Evidence | Effort | Status |
|---|---|---|---|---|---|
| 1 | **Mains frequency for the EMG notch: 60 Hz here** (a Setting, or detect it), and look for the line at 60 Hz, not only 50 | the 20–90 Hz EMG band contains our 60 Hz mains, but the features notch 50 Hz (`features.py`, `session.py` uses the default) | HLBSSL33 R: 60 Hz = **18 % of NREM EMG power, 22.5 % of REM, 1.7 % of wake**; NREM EMG PSD at 60 Hz = 13× its neighbours; a 60 Hz notch moves the medians NR 6.5→5.9, R 5.9→5.2 µV and W/NR 4.15→4.55×. Vault 2026-10-02: mains in the EMG corrupts staging. **Mostly a problem of recordings made before the 2026-10-07 grounding fix** (all HLB batches): after it, A2's EMG 60 Hz fell from 26–33 to ~1 µV | small code change, but it **changes features and the rule's cuts** | ⏳ decide **before scoring more mice** (professor) |
| 2 | `batch_stage.py` / `run_cohort_raw.py` find rig CSVs (and skip `*_stages.csv` etc.) | the AUTO first pass for a whole HLB cohort | — | small | open |
| 3 | The rule's **"NR by default"**: epochs with δ at W/R level and atonic EMG are labelled NR | all 8 corrections on 2026-10-07 were NR→R/W of this kind (331–332, 765–767, 334, 838–839) | [[2026-10-07]] cases | measure on more mice first; then a mark (e.g. "low-δ NR") or require δ evidence for NR | idea, needs data |
| 4 | Separate **W→R after a brief awakening inside REM** (normal in wild-type) from **W→R after ≥40 s of wake** (narcolepsy-like) in the marks and in the analysis | they mean different things; only the second is a pathology marker (Scammell 2009; Fujiki 2009, see the [[sleep-scoring-handbook\|handbook §6]]) | 836–840 on 2026-10-07 | small | open |
| 5 | Count **microarousals** in `analyze_saves.py` (NR epochs with `emg_rms` ≫ `emg_tone_med` and a σ drop) | fragmentation is a likely SOD1 × deprivation outcome; hand-scoring them is inconsistent | convention C2 in the [[sleep-scoring-handbook\|handbook]] | medium | needs convention |
| 6 | Keep a record when a rule mark is accepted with `space` (today the `reason` is deleted) | the accepted marks are the microarousal / short-REM catalogue | — | small | open |
| 7 | Make the **minimum REM** length a setting (today: REM ≤ 8 s inside NREM is written NR) | depends on the convention the professor chooses | 764–766 | small | needs convention |
| 8 | Validate the rule on **rig** data: a fully hand-scored stretch (ZT0–2) per mouse, then count unmarked changes | the rule was validated only on legacy `.3eg` at 4 s | — | scorer time | open |
| 9 | Commit `csv-reader`, push, open a PR on `somnocode/SleepStager` | the professor reviews and merges | §2 | small | ✅ [PR #1](https://github.com/somnocode/SleepStager/pull/1) opened 2026-10-08; waiting for the professor |

## 4. Ideas (not prioritised)

- A heart-rate estimate from the ECG that leaks into the EMG (the beat is visible at ~9/s in HLBSSL33). ECG is retired on the rig as a measurement, so this would only ever be a curiosity, not a result.
- Show the spike-proof tone as a line in the EMG-tone lane, not only in the dossier.
- In the header, show which mark is open on the current epoch and its reason (`tone`, `onset`, `island`…).
- A "conventions" panel in the program listing the lab's scoring rules once the professor fixes them.

## How to add to this page

New change → add a row at the top of §2 (date, files, how it was checked, state) and a line in that
day's journal. New idea → §4; when someone decides it matters, move it to §3 with evidence. Keep
`SleepStager/README.md` in step with anything a user can see.
