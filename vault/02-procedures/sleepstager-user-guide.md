---
tags: [procedure, sleep-scoring, sleepstager, eeg, emg]
created: 2026-10-07
status: production
---

# SleepStager user guide: open, save, keys, and how to read the rule

> [!abstract] TL;DR — for non-technical readers
> **What this is.** SleepStager is the professor's desktop program for scoring mouse sleep by hand,
> one 4-second epoch at a time, as wake (W), NREM (NR) or REM (R). Since 2026-10-07 it opens the
> rig's per-mouse CSV files directly.
>
> **Why it exists.** Scoring is the step every sleep number depends on. The program puts the EEG,
> the EMG, the spectrogram and the muscle tone on one screen, proposes a first pass, and records
> every change you make, so a scoring can be checked and repeated.
>
> **How to read this page.** §1, §2 and §3 are at-a-glance tables: open/save/files, keys, what is
> on the screen. §4 is how to use the automatic first pass and its marks without being misled by
> them. The knowledge behind the calls (what θ/δ or RMS means, our conventions, the literature) is
> in [[06-references/sleep-scoring-handbook|the sleep scoring handbook]]. Changes to the program are
> logged in [[01-infrastructure/sleepstager/sleepstager-changes-and-backlog|SleepStager changes and backlog]].
> Big picture: [[01-infrastructure/system-overview]].

The full manual is the repository's `SleepStager/README.md` (sections 1–15). This page is the short
version for daily work on the HLB data. On Linux and Windows every `⌘` in the README is **Ctrl**.

---

## 1. Open · save · close — at a glance

| I want to… | Do this |
|---|---|
| **Start the program** on a recording | `~/.venvs/sleepstager/bin/sleepstager <file.csv>` (no file → a file dialog opens) |
| **Set it up the first time** | File → Settings…: your **initials**, the **data folder** (`~/sleep-data`), lab clock **+9 h** (KST) |
| **Stage a recording for the first time** | opening dialog → **Stage from raw** → staging-window dialog (below) → **OK** |
| **Continue where I stopped** | opening dialog → **Continue saved pass** (cursor returns to the last epoch) |
| **Save** | **Ctrl+S**. The first save creates a new time-stamped file set; later saves ask **Overwrite** (normal) or **Save as new** (snapshot) |
| **Save + one image per tagged transition** | **Ctrl+Shift+S** |
| **Save a picture of the screen** | **Ctrl+I** (goes into `images/`) |
| **Know if work is unsaved** | red **● not saved** at the end of the header line, and `*` in the window title (added 2026-10-07) |
| **Close** | close the window; it asks to save if there is unsaved work |
| **Open the next mouse** | **Ctrl+O** (asks to save first) |

> [!warning] "Stage from raw" on a recording that already has your save starts a NEW pass
> The saved labels are still loaded by time, but always choose **Continue saved pass** to carry on.

### The staging-window dialog (first open of a recording)

| Field | HLB value | Why |
|---|---|---|
| Light ON (ZT0) | **09:00** | lights on in the animal room; every HLB window starts 09:00 ([[02-procedures/CANONICAL-recording-windows-and-protocol]]) |
| Epoch | **4 s** | the only length the rule was checked at; also what the legacy tools read |
| Start / End | filled in from the file | the CSV is already cut to its 24 h (or 20 h) analysis window |
| Protocol: "sleep deprivation ends at" | **unticked** for Baseline and for SL Recovery · **ticked, 13:00** for SD Recovery (W-SD, S-SD) | the SD recovery CSV starts at 13:00; the window still starts at ZT0, so 09:00–13:00 shows as padding `U` |
| remember | ticked | the next mouse opens with the same values |

### Where the files are

Work on **local copies**. The NAS is storage only; never stage straight from `/mnt/skimnas`.

```text
NAS (read-only for us):  /mnt/skimnas/02_Data_Sleep/andrea/<batch>/<Baseline|Recovery>/<YYYYMMDD>_<MOUSE>_<B|R>/
Local working copy:      ~/sleep-data/<batch>/<Baseline|Recovery>/<YYYYMMDD>_<MOUSE>_<B|R>/
                         ├── <YYYYMMDD>_<MOUSE>_<B|R>.csv          the recording, never modified
                         ├── <YYYYMMDD>_<MOUSE>_<B|R>.info.json    channels, window, QC, sha256
                         └── 4-sec sleepstager/                    created by your first save
```

Copy a mouse and check the copy is intact:

```bash
SRC=/mnt/skimnas/02_Data_Sleep/andrea/HLBSSL/Recovery/20260921_HLBSSL33_R
DST=~/sleep-data/HLBSSL/Recovery
mkdir -p "$DST" && cp -r "$SRC" "$DST"/
sha256sum "$DST/20260921_HLBSSL33_R/20260921_HLBSSL33_R.csv"   # must equal upload.sha256_remote in the info.json
```

A recording in its rig folder (`20260921_HLBSSL33_R/`) is **not moved** on save (since 2026-10-07). A
loose file anywhere else still gets an `<animal>-<B|R>/` folder created and is moved into it.

### What one save writes

Every file name is `<animal>_<B|R>_<initials>_<YYMMDD-HHMM>_…`, so two people can score the same mouse.

| File | One row per | What it holds | Read by |
|---|---|---|---|
| `_stages.csv` | epoch | stage, `present`, `phase`, `label_source`, band powers, 1–25 Hz spectrum | `scripts/analyze_saves.py` (the analysis) |
| `_review.csv` | epoch | the features the panel shows: `emg_rms`, **`emg_tone_med`** (spike-proof tone), θ/δ, γ fraction, σ, δ, rail flags, `borderline` | you, when checking numbers |
| `_tagged.csv` | tagged epoch | your `t` tags and the rule's marks, `source` (rule/scorer), `reason` | training data |
| `_transitions.csv` | candidate | every transition candidate and whether you tagged it | training data (negatives) |
| `.json` | — | window, ZT0, the rule's cuts, **every epoch you changed** (`restaged`), last epoch | provenance |
| `_<date>.png/.pdf` | ZT day | spectrogram over the hypnogram | a quick look |
| `images/` | — | Ctrl+Shift+S / Ctrl+I pictures | — |

`label_source` says who wrote each label: `rule` (the first pass, never touched), `restaged` (you changed it), `loaded`, `inherited`, `none`.

### Installing on a machine

On the SKIM workstation it is installed in `~/.venvs/sleepstager` (uv, Python 3.11; done 2026-10-07):

```bash
uv venv ~/.venvs/sleepstager --python 3.11
uv pip install -p ~/.venvs/sleepstager -e ~/sleep-recording-skim/SleepStager pyarrow
```

Mac/Windows: `SleepStager/INSTALL.md` (conda). The program is a separate git repository inside the
workspace (`SleepStager/`, remote `somnocode/SleepStager`); `./skim` does not sync it.

---

## 2. Keys — at a glance

| Group | Key | Does |
|---|---|---|
| **Move** | `←` / `→` | previous / next epoch |
| | `Shift+←` / `Shift+→` | previous / next **stage boundary** |
| | `,` / `.` | one window (≈20 s) back / forward |
| | `Home` / `End` | first / last epoch |
| | `Ctrl+Shift+↑` / `Ctrl+Shift+↓` | next / previous ZT0 or ZT12 |
| | type a number in the epoch box | jump there (Enter gives the keyboard back) |
| **Review** | `f` / `Shift+F` | next / previous **open rule mark** (the review queue) |
| | `g` / `Shift+G` | next / previous **W→R** (REM entered from wake) |
| | `v` / `b` | previous / next post-REM atonic-wake run |
| | `a` / `Shift+A` | next / previous borderline epoch (turn on in Review menu) |
| | `Ctrl+L` | the review items list (click a row to jump; `w e r space` work in it) |
| | `d` | **epoch dossier**: every feature of this epoch vs this mouse's W/NR/R medians |
| | `c` | check your transition tags against the current stages |
| **Stage** | `w` `e` `r` | set **W / NR / R**, clear the mark, move on |
| | `Shift+W` `Shift+E` `Shift+R` | set W\* / NR\* / R\* (staged but doubtful) |
| | `x` | **X**: cannot be staged (artifact) |
| | `t` | tag this epoch as the first epoch of a new stage (a clean transition) |
| | `space` | **restore the first-pass stage** and remove tag, flag and mark (does not move) |
| **View** | `↑` / `↓` | EEG gain (×1.3) |
| | `Shift+↑` / `Shift+↓` | EMG gain |
| | `n` | 50 Hz display notch (display only; our mains is **60 Hz**, so it does little here) |
| **File** | `Ctrl+S` · `Ctrl+Shift+S` · `Ctrl+I` · `Ctrl+O` · `Ctrl+K` | save · save + images · picture · open next · all keys |

> [!tip] `space` is "keep the rule's stage", not "keep my stage"
> On an epoch you re-staged, `space` puts the rule's stage back. To accept a mark on an epoch the
> rule got right, `space`; to change it, `w`/`e`/`r`. `space` also deletes the mark's `reason`, so
> if you want a record of a microarousal, use `Shift+E` (NR\*) instead.

Useful menus: **File → Change staging window…**, **File → Refit cuts excluding artifacts…** (after
marking `x` epochs), **Review →** which mark kinds are in the queue, and show/hide borderline marks.

---

## 3. What is on the screen

| Where | What | How to use it |
|---|---|---|
| **Header** | animal · date time · ZT · stage (`NR*` = flagged) · `re-staged A→B` · **● not saved** | always read the stage token before pressing a key |
| **EEG trace** | ≈20 s raw, current epoch shaded (violet = within 2 epochs of a boundary); θ/δ under each epoch | slow, large waves = NREM; regular ≈7 Hz waves = REM; small and fast = wake |
| **EMG trace** | same 20 s; the per-epoch **tone** (EMG RMS) under each epoch | bursts = movement; flat = sleep; the regular small spikes ≈9/s are the **heartbeat** leaking into the EMG |
| **Spectrogram** (lane 1) | EEG power 1–40 Hz, ±150 epochs | bright δ band = NREM; a bright line at θ with dark δ = REM |
| **EMG tone** (lane 2) | black = EMG RMS per epoch; grey band = range of the 0.5-s RMS inside the epoch; dashed = W/NR/R medians | tall grey band with its bottom at sleep level = a burst over quiet muscle |
| **Hypnogram** (lane 3) | W green, NR blue, R red; marks above; dark phase shaded | see bouts and where the marks are |
| **Right panel** | navigator · gains · counters (`marks n/total`, `W→R n`) · band profile · total power box · **feature sliders** | slider dot inside one stage's band = that stage is drawn bold |
| **Dossier** (`d`) | `this` · `28 s` (±3 epochs, geometric mean) · `pct` (percentile in this mouse) · W/NR/R medians; rows EMG, **tone (spike-proof)**, γ frac, θ/δ, θ sharp, δ, σ, γ, total, peak freq, θ peak | use it on every hard epoch; the meaning of each row is in the [[06-references/sleep-scoring-handbook#2. The measures, explained\|handbook §2]] |

---

## 4. The automatic first pass and its marks

### What the rule does

When a recording has no scoring, a rule stages every epoch and labels it `label_source = rule`.
It fits **three cuts to this recording** (nothing is typed in by hand; the values are in the save's JSON under `rule`):

1. **Wake vs sleep:** EMG RMS above an Otsu cut → **W**. HLBSSL33 R: `emg_cut` = 13.3 µV.
2. **REM:** among sleep epochs, θ/δ (averaged over ±8 s, geometric mean) above its 82nd percentile
   **and** δ power (±8 s) below its 15th percentile → **R**. HLBSSL33 R: θ/δ > e^−0.084 ≈ **0.92**, δ < e^7.18 ≈ **1,300 µV²**.
3. **Everything else asleep → NR.** This default is the rule's main blind spot (below).

Then it **marks** short or doubtful runs instead of smoothing them away.

> [!quote] Paper-ready (draft, until the scoring protocol is final)
> Sleep–wake states were scored manually in 4-s epochs with SleepStager, using the EEG and EMG
> traces, the EEG spectrogram and the per-epoch EMG tone. A rule fitted to each recording (an Otsu
> threshold on 20–90 Hz EMG RMS for wake; windowed θ/δ above its 82nd sleep percentile with δ power
> below its 15th percentile for REM) provided a first pass that the scorer reviewed epoch by epoch.

### The marks, and what to do with each

| Mark | What the rule is saying | What to check | Usual answer |
|---|---|---|---|
| `NR*` reason `tone` | EMG burst inside NREM, but the spike-proof tone stayed at sleep level | did the muscle work for **more than half** the epoch? dossier **tone (spike-proof)** vs the wake cut | NR (microarousal) → `space` |
| `W*` (short W inside sleep) | ≤8 s of wake between sleep | same question; σ and γ say if the brain left NREM | W if the burst fills the epoch (617), else NR |
| `NR*` reason `onset` / `R*` onset | θ is rising before a REM bout but δ is still high | where does θ take over and δ drop? | REM starts at the first θ-dominated, low-δ epoch (310) |
| `R*` (short R inside NREM) | REM-like run ≤16 s | δ at W/R level? atonic? | often a real short REM episode (764–766) |
| `W→R` | REM bout entered straight from wake (kept R) | is there **any NR** between the W and the R? | genuine ones are kept and tagged (838–840) |
| `rail` | the amplifier clipped (wire artifact) | off in the queue by default | usually `x` |

### Our data's known blind spot: "NR by default"

In HLBSSL33 every correction on 2026-10-07 (8 epochs) went **from NR to R or W**. They were all
epochs where δ was at wake/REM level (~1k) but the rule had no positive reason for W or R, so it
fell back to NR: the tail of a REM bout (331–332), a short REM episode (765–766), muscle tone
returning after REM (767, 334, 838–839).

> [!important] The one-glance check
> If the stage says **NR** but the **δ slider dot sits in the W band**, open the dossier.
> Atonic EMG → probably **R**. Tone present → probably **W**. Real NREM has δ near its own median
> (4k in HLBSSL33) and spindles (σ near 640).

### A review order that works

1. `g` through every **W→R**: the most likely real errors and the most interesting physiology.
2. `f` through `R*`, then `W*`, then the `NR*` tone bursts (the Review menu hides kinds you are not doing).
3. Walk **both edges of every REM bout** with `Shift+←`/`Shift+→`.
4. Tag clean transitions with `t` (the Review → transition candidate list visits them).
5. Save often. Look for **● not saved** before closing.

Before trusting unmarked epochs on a new mouse, score one stretch completely (e.g. ZT0–2, 1,800
epochs) and count how many unmarked epochs you changed (the JSON `restaged` list). Few → checking
only marks and edges is defensible; many → score fully.

---

## 5. Limits to keep in mind

- The rule was validated against human scoring only on the legacy `.3eg` recorder at 4 s, not on this rig.
- The EMG features notch **50 Hz**, but our mains is **60 Hz**: in HLBSSL33 R, 60 Hz is 18 % of the
  NREM EMG power and 22 % of REM ([[01-infrastructure/sleepstager/sleepstager-changes-and-backlog|backlog item 1]]).
- The heartbeat is visible in the EMG of HLBSSL33. It raises the quiet floor slightly; it does not change calls.
- Per-mouse values (δ 4k, EMG 27…) are relative to that recording. Never compare raw numbers across mice.

## Related

- [[06-references/sleep-scoring-handbook]] — the knowledge: measures, values, conventions, literature
- [[01-infrastructure/sleepstager/sleepstager-changes-and-backlog]] — what changed in the program, and what is next
- [[02-procedures/per-mouse-csv-format]] — the CSV the program now reads
- [[05-experiments/completed/2026-09-30-scoreable-mice-on-the-24h-windows]] — which mice to score
- [[02-procedures/blind-scoring-and-kappa]] — measuring agreement against a human
- [[06-references/sleepyscore-japan-scoring-tool-algorithm]] — the older Japanese tool SleepStager descends from
- [[2026-10-07]] — the first scoring session, case by case, with screenshots
