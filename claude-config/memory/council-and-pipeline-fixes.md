---
name: council-and-pipeline-fixes
description: "2026-08-07/08 — the LLM council review of the analysis pipeline, the IIIS Tsukuba reference check, and Fix 1 (minimum bout duration) with the raw-vs-smoothed split it forced"
metadata:
  type: project
---

**Vault: `20-areas/eeg-analysis/2026-08-07-council-review-of-the-analysis-pipeline.md`** = findings + the
7-fix plan of record + §4 the Fix 1 write-up.

## The council's findings (5 advisors + anonymised peer review)

🔴 **SELECTION BIAS, the worst one and previously unnamed:** the QC gate rejects epochs on
**contact**, contact is **movement**-driven, movement **is state** ⇒ CLEAN epochs are enriched for
quiet states and every downstream number inherits a bias correlated with the dependent variable.
**Test owed: rejection rate vs scored state, must be flat.**
🔴 **4 OF 5 PHYSIOLOGY CHECKS CANNOT FAIL** (I verified in code; the council said 3):
`wake_has_highest_emg` = the Otsu split restated · `rem_highest_theta_delta` = the p80 rule
restated · `rem_emg_low` forced because REM ⊂ non-wake · `nrem_has_most_delta` near-forced as the
residual. **Only `nrem_largest_amplitude` can fail. STOP reporting "physiology 5/5" as validation.**
🔴 **"Threshold-independent" is FALSE** — Otsu is refit per animal ⇒ animals not on a common scale.
🔴 **82.1% is not "about 70%"** — one hit + one miss reported as two confirmations.
🔴 **The 112 wire-free nulls are PSEUDOREPLICATED** (all 3 reviewers, none of the 5 advisors) —
shared board/reference/ground ⇒ effective n ≈ sessions, not 112.
🔴 **Only negative controls exist** — no positive control of known spectrum through the pipeline.
🔴 **Accuracy is UNMEASURED** — no scorer has run, no Cohen's kappa.
⛔ **"Modernise the staging" was REJECTED by the council**: multitaper/HMM/YASA/AccuSleep = busywork
at n=2 with zero ground truth, and sophisticated staging on unverified channels **hides** the
failure mode. Validate first.
⚠️ "Filtering makes 69 µV fake EEG" novelty was **challenged** — plausibly known instrumentation
behaviour; **do a literature check before building on it**.
📌 Council's single first action: **score 300 stratified random epochs/animal blind, compute kappa.**

## ⭐ IIIS Tsukuba reference check (done BEFORE writing the constant)

**Nakata et al., SLEEP 2025, doi:10.1093/sleep/zsae279** (Funato/Yanagisawa), via PubMed.
✅ match: **4 s epochs**, **theta 6-9 Hz**, episode duration = total time ÷ episode count.
❌ differ: **delta 1-4 Hz** (we use 0.5-4) · **artifact epochs are INCLUDED in their state totals**
(we exclude) · they exclude artifact + **transition epochs from SPECTRA only** (we don't) ·
power normalised as **% of mean total power over 15-30 Hz** (we don't) · **≥7 d recovery THEN ≥9 d
habituation on the tether** (we tethered day 8-10 with ~1 d habituation — large protocol gap).
🔴 **THERE IS NO MINIMUM BOUT RULE IN THE IIIS METHOD.** Our 12 s / 3-epoch rule is a **HOUSE
CONVENTION** and `qc_thresholds.MIN_BOUT_EPOCHS` says so. **Never attribute it to IIIS.**

## ✅ Fix 1 DONE 2026-08-08 — minimum bout duration

`MIN_BOUT_EPOCHS = 3` + `enforce_min_bout()`: runs < 3 epochs **merged into the longer neighbour**,
shortest first, iterated to stability, **within blocks only**.
⚠️ First implementation had an **iteration cap of 100 per block — far too low** for ~21k epochs;
only 115 epochs merged and short bouts survived. Fixed to `range(len(seg))`.
**Effect:** B1 bout counts 1232/1672/971 → **205/258/98**, medians 12/4/4 s → **84/40/22 s**.
Epochs relabelled B1 9.78%, D2 12.64%. ✅ **Circadian barely moved** (D2 70.3→70.4%, B1 82.1→81.2%).

🔑⭐⭐ **THE TRAP IT EXPOSED: smoothing INFLATES our validity statistics by construction.**
B1 `r@1min` 0.603 → **0.742**; REM-from-NREM 73.9% → **82.7%**. And the r calibration
(noise −0.035, 4-min bouts +0.510) was derived on UNSMOOTHED labels.
✅ **FIX: persistence + REM-order now computed on `lab_raw` BEFORE the merge; architecture, bouts
and light/dark computed AFTER.** JSON carries `validity_stats_computed_on`. Pipeline version
`2026-08-08`. Backups `*.py.bak`.

**Current state, all 16 files re-run + stage 4 regenerated:** B1 overnight SCOREABLE r=0.603,
WAKE/NREM 50.2/46.0, asleep-in-light **81.2%** · D2 overnight SCOREABLE r=0.499, 43.4/50.0,
**70.4%** · B1 afternoon SCOREABLE r=0.481, 73.2% · other 13 REJECT.

## ✅ ALL 4 IIIS ALIGNMENT ITEMS APPLIED 2026-08-08 (delta last and alone)

(a) **Transition epochs excluded from SPECTRA ONLY** — `steady_state_mask()`, an epoch counts only
if the preceding AND following epoch share its state, **evaluated within blocks**. Staging and
state totals still use every epoch. **5.3-7.5% excluded.**
(b) **`BAND_NORM = (15,30)`** ⇒ new per-state `delta_density`/`theta_density` = band ÷ 15-30 Hz,
IIIS style. ⚠️ our EEG filter is 0.5-30 vs their 0.5-100, so the band top sits on our roll-off:
internally consistent, NOT numerically identical to theirs.
(c) **State totals both ways** — `of_scored_epochs` + `of_whole_recording` + `unscored_pct_of_recording`.
⚠️ **My first version was DEGENERATE**: "% of epochs in blocks" can never differ from "% of scored
epochs" because **blocks contain only passing epochs by construction**. Fixed to the whole-recording
denominator ⇒ D2 1.6% unscored, C1 100%.
(d) **`BAND_DELTA` 0.5-4 → 1.0-4.0 Hz.** ⭐ Also suits our hardware: the **1.10 Hz acquisition
high-pass** already ate 0.5-1.1 Hz irreversibly, so a 0.5 Hz edge was integrating nothing.
**Isolated effect (B1):** WAKE/NREM 50.2/46.0 → 50.2/46.2 · REM order 73.9 → 73.0 · r@1min
**unchanged at 0.603** (correct — the WAKE split is Otsu on EMG) · **REM theta/delta 1.680 → 1.995,
REM/NREM separation 4.55× → 5.00×** · asleep-in-light 81.2 → 81.0%. Physiology still 5/5.

⭐⭐ **D2 STAYS AT 70.3% ASLEEP IN LIGHT (literature ~70%) THROUGH ALL FOUR METHOD CHANGES** —
min-bout, transition exclusion, renormalisation and the delta band. That robustness is worth more
than the number itself.

**Current: B1 overnight r=0.603, 50.2/46.2, 81.0% · D2 r=0.499, 43.5/49.9, 70.3% · B1 afternoon
r=0.481, 73.4% · other 13 REJECT.** Stage 3+4 re-run on all 16, `by-mouse/` relinked.

## 🔴 ✅ FIX 4 DONE 2026-08-08 — THE OTSU SWEEP, AND IT DAMAGED THE CIRCADIAN CLAIM

Swept the WAKE cut **±25% in LINEAR µV** (0.75/0.9/1.0/1.1/1.25; ∓0.097 in log10).
`OTSU_SENSITIVITY_MULTIPLIERS` + `otsu_sensitivity()`; written to JSON **and** the text summary.

| animal | reported asleep-in-light | range | **swing** |
| --- | --- | --- | --- |
| B1 afternoon | 73.4% | 60.9-82.8 | 21.9 pts |
| B1 overnight | 81.0% | 54.4-90.3 | 35.9 pts |
| **D2 overnight** | **70.3%** | **23.0-88.9** | **65.9 pts** |

🔴 **A ±25% shift in ONE per-animal threshold moves D2 from 23% to 89% asleep in light. The ~70%
literature value is reachable from almost anywhere in that range ⇒ the circadian agreement is NOT
the independent confirmation it was presented as.** **NEVER call it threshold-independent. Always
quote the swing beside the number** (the summary now prints it automatically).
⚠️ **CORRECTION TO MY OWN EARLIER CLAIM: I called D2's 70.3% "the cleaner number". WRONG on this
axis** — D2 is the MOST fragile animal (65.9 vs B1's 35.9). Proximity to the literature mean says
nothing about robustness.
⭐ **What it really diagnoses:** a ±0.097 log shift only moves things this much if the **EMG
distribution has no clear bimodal valley** — Otsu is cutting inside a continuum. Ranking tracks
signal quality (B1 EMG hum 15.2 µV / 0.0% unscored vs D2 26.6 µV / 1.6%). **More useful than the
circadian agreement was.**
✅ The "survived 4 method changes" claim still stands, **but those were the wrong parameters to
stress-test — the WAKE cut was the sensitive one and was the one we had not varied.**
🛑 **TEMPTING FIX TO REFUSE:** B1's persistence peaks at mult 0.9 (r=0.689) not at Otsu (0.603).
**Do NOT tune the threshold to maximise r@1min** — that makes our only independent validity
statistic circular.
🐛 Bug found+fixed: `stage()` returns `{}` for thr when a recording has no usable epochs ⇒
`KeyError: emg_otsu_log10` on all 13 REJECT animals. Guarded; all 16 re-run clean.
⇒ **FIX 2 (human-scored ground truth + Cohen's kappa) IS NOW THE BLOCKING ITEM** — without it
there is no principled way to place the WAKE cut, and every architecture number inherits that.

## 🟡 FIX 2 — KAPPA HARNESS BUILT 2026-08-08, AWAITING A HUMAN SCORER

**`qc/make_scoring_set.py`** + **`qc/score_kappa.py`** (need `~/eeg-analysis-venv/bin/python`).
**Packs ready and verified UNSCORED:** `portB-slot1_..._SCORING/` (300 items, 27 MB) and
`portD-slot2_..._SCORING/` (300 items, 23 MB) in `/home/skimlab/eeg-processed/2026-08-06/`.
Open `score.html`: keys **1/2/3/4** = WAKE/NREM/REM/unsure, backspace = back, progress kept in
localStorage, "save CSV" → `scoresheet.csv`. Then `python3 score_kappa.py <SCORING_DIR>`.

**Design:** 20 s per item, **score the shaded centre 4 s epoch** (matches the lab's 5-epoch view) ·
**random order** so bout structure can't be followed · **stratified equal-n per auto state** because
REM is only 4-7% · **fixed y-axis** (auto-scaling leaks state) · auto label never shown, truth in
`_TRUTH_do_not_open.csv` · **UNSURE allowed and excluded from kappa**.
⚠️ **Stratified ⇒ a STRATIFIED kappa, NOT prevalence-matched** to the recording (the script warns).
`--random` builds a prevalence-matched pack.
**Reports:** kappa + bootstrap 95% CI · per-state kappa · confusion matrix (human = rows) · raw
agreement · blank/UNSURE counts. Landis & Koch printed as a reading aid, **not a pass mark**.
✅ **Harness validated** against a simulated scorer with 15% injected disagreement + 3% UNSURE, in a
**temp copy** so no fake sheet could touch the real pack: recovered 82.0% agreement, **κ=0.730,
CI [0.661, 0.791]**, symmetric confusion. Arithmetic correct.
🔴 **SCORE D2 FIRST** — it is the animal whose circadian number swings **65.9 pts** across the Otsu
sweep and whose 70.3% is load-bearing in the professor handout.
⭐ **What it unblocks:** places the WAKE cut on evidence not Otsu · lets the **percentile REM rule**
be replaced by an absolute theta/delta threshold · **fix 3 (selection-bias test) is GATED behind it**
because it needs human-scored states to plot rejection rate against.

📌 **STILL OWED — the council's most serious items, untouched by the alignment work:** kappa vs
blind human scoring (fix 2) · **rejection-rate-vs-state selection-bias test (fix 3)** · relabel the
physiology checks honestly + persistence-shuffle null (fix 5) · cluster the null by session (fix 6)
· positive control (fix 7). **Fix 4 (Otsu ±25% sweep) is the cheapest and would shore up the
circadian claim immediately.**
📌 Then fixes 2-7: kappa harness · rejection-rate-vs-state · Otsu ±25% sweep · relabel physiology
checks honestly · cluster the null by session · positive control.

See also [[recording-usable-fraction-analysis]], [[eeg-analysis-pipeline]],
[[staging-circadian-validation-2026-08-07]].


## ⭐⭐⭐ THE JAPANESE SCORING TOOL'S SOURCE CODE, READ 2026-08-08

`~/Downloads/SleepyScoreApp_HM_260312_exported.m` + `sleepy_pipeline_refined.py` (same algorithm).
**Full read-off: vault `20-areas/sleep-scoring/sleepyscore-japan-scoring-tool-algorithm.md`.**

🔴⭐⭐ **THEY DO NOT USE A PERCENTILE FOR REM. BOTH THRESHOLDS ARE 2-CLUSTER K-MEANS SPLITS**
(threshold = mean of the two cluster centres): WAKE on the **EMG rectified integral**, REM on
**theta/delta among SLEEP epochs only**. ⇒ **This solves our worst problem** — our p80 rule forces
REM to 20% by construction. **Our existing `rem_measured` Otsu cross-check is already most of the
implementation.**
⭐ **Their WAKE rule ≈ ours**: k-means k=2 on 1-D and Otsu optimise the same split ⇒ our Otsu cut is
a fair implementation of theirs, **and the ±25% sensitivity we found applies to THEIR tool too.**

**Their exact algorithm** (fs 250, epoch 4 s): EMG **2nd-order Butterworth HIGH-PASS 30 Hz** →
`sum(|filt|)`; EEG **LOW-PASS 4.5 Hz** → delta integral; **band-pass 6-9 Hz** → theta integral;
`td = theta/delta`. Welch with **Bartlett** window, nfft 1024. Stage codes **WAKE=0, NREM=10,
REM=20**. Degenerate input (<10 finite or <2 unique) → **median fallback**.

⚠️ **CONFLICTS WITH MY OWN CHANGE EARLIER THE SAME DAY:** I set `BAND_DELTA` to 1-4 Hz from the
paper; **the tool low-passes at 4.5 Hz (0-4.5) for STAGING**. Both right for different jobs —
**paper 1-4 Hz = REPORTING spectra, tool 0-4.5 Hz = STAGING**. We use one constant for both;
**split it**.
⚠️ Their delta/theta are **TIME-DOMAIN RECTIFIED INTEGRALS**, not Welch band powers ⇒ **their
threshold values CANNOT be transferred to our features** without rescaling.
✅ **Confirms: NO minimum-bout rule anywhere in their code** — our 12 s rule stays a house convention.
🗂️ **`.3eg` format fully specified** (`read_3eg_file`): repeating
`[8-byte float64 timestamp][1000×int16 EEG][1000×int16 EMG]` per 4 s epoch — the writer spec if we
ever feed their tool.
💡 They also compute **`emg_activity = var(raw)/integral(|filt|)`**, a burst-vs-tonic shape measure
we don't have — possibly useful for **C1's ambiguous EMG** (real bursts vs movement artefact).
💡 The GUI has **manual spinner overrides on all three thresholds with a live hypnogram** ⇒ in
practice **a human tunes the automatic thresholds by eye**, matching the paper's "semiautomatic +
visual inspection".

🛑 **NOTHING APPLIED, DELIBERATELY.** Swapping the REM rule changes every REM number, and the
council said method changes at n=2 with no ground truth are unfalsifiable.
**ORDER: score the blind packs → get kappa → THEN swap to the k-means REM rule and measure whether
kappa improves.**
📌 New fixes 8/9/10: **k-means REM rule (gated behind kappa)** · split `BAND_DELTA` into
staging 0-4.5 / reporting 1-4 · median fallback for degenerate recordings.


## ✅ FIXES 3, 5, 6, 9, 10 DONE 2026-08-08 — three of the council's findings did NOT survive measurement

⭐⭐ **FIX 3 — THE SELECTION BIAS IS *NOT* OPERATING.** `qc/selection_bias_test.py`. The stated test
is impossible (a rejected epoch HAS no state), so it tests the mechanism: how much was rejected, and
whether rejected epochs carry **higher EMG** (= movement = wake).
**B1 overnight 0.0% rejected · B1 afternoon 0.0% · D2 1.3%, Cliff's δ = −0.171 (rejected epochs are
QUIETER, the OPPOSITE direction).** ⇒ **Two of three recordings could not have been biased at all.**
Correct concern in principle, **does not apply to this dataset**.

⭐⭐ **FIX 5 — REM ORDER *SURVIVED* ITS NULL, IT IS REAL EVIDENCE.** `rem_order_null()` permutes the
ORDER of state runs within blocks, preserving run lengths + composition.
**B1 overnight 72.4% vs null 56.6±1.6 (~9.9 SD) · B1 afternoon 81.1% vs 62.8±3.8 (~4.8 SD) ·
D2 78.4% vs 64.5±1.2 (~11.6 SD). All at the 100th percentile.**
⇒ **Now our SECOND informative check, and the stronger one.** Physiology checks also relabelled in
JSON + summary: 4 of 5 marked FORCED, only `nrem_largest_amplitude` INFORMATIVE, new
`physiology_informative_pass`. **Never quote "5/5 PASS" again.**

🟡 **FIX 6 — PSEUDOREPLICATION: THE TWO METHODS DISAGREE, BOTH REPORTED.**
`qc/floor_pseudoreplication.py`: **ICC by port = 0.000, effective n = 110.7 of 112** ⇒ channels are
effectively exchangeable, the reviewers' concern does not materialise. **BUT the cluster bootstrap
(resampling the 4 PORTS) is 4.8× wider** — [384.2, 513.4] vs [402.1, 429.2] on the 413.1 µV
threshold. ⚠️ That width is mostly an artefact of **only 4 clusters**. **Conservative position:
quote the CLUSTER interval anyway.**

✅ **FIX 9** — two delta bands: `BAND_DELTA_STAGING = (0.5,4.5)` drives the theta/delta ratio (the
Japanese tool's low-pass); `BAND_DELTA = (1.0,4.0)` stays the reporting band (the paper). Applied to
staging, physiology and the Otsu sweep.
✅ **FIX 10** — degenerate-input **median fallback**, copied from the Japanese tool; sets
`degenerate_fallback`. Previously this path crashed.

🐛 **BUGS FOUND AND FIXED TODAY:** min-bout merge capped at **100 iterations** (needed `len(seg)`;
only 115 of 2083 epochs merged) · **`nm` shadowed** by two later loop variables → TypeError in the
REM null · **`KeyError: emg_otsu_log10`** on all 13 REJECT animals · **"state totals both ways" was
degenerate** (blocks contain only passing epochs, so "% of epochs in blocks" ≡ "% of scored epochs")
→ replaced with the whole-recording denominator.

📌 **ONLY TWO GENUINELY OPEN COUNCIL ITEMS LEFT: the KAPPA (packs waiting) and a POSITIVE CONTROL**
(needs a signal generator = bench work). Everything else is measured or explicitly deferred.

🗂️ **VAULT UPDATED EXTENSIVELY 2026-08-08:** correction banners on
`2026-08-07-staging-preregistration` and `2026-08-07-overnight-recording-two-animals-work` ·
supersession banner on `analysis-methods-and-justification` · pointer block on `_eeg-analysis-hub` ·
**~15 new glossary terms** and **9 new symptoms** in `eeg-analysis-problems` · new refs
`sleepyscore-japan-scoring-tool-algorithm` + `per-animal-failure-signatures` · journal
`04-journal/2026-08/2026-08-08.md` · 4 new `_INDEX.md` entries.


## 🏁 CLOSED OUT 2026-08-08 — only TWO items open, both by choice

⭐⭐ **`20-areas/sleep-scoring/blind-scoring-and-kappa.md` = THE SOP + PRE-REGISTERED DECISION RULES.**
Written **before any epoch was scored**, so the result cannot be reinterpreted afterwards:
**κ≥0.80** keep current staging · **0.60-0.80** report with the confusion matrix, treat automatic
architecture as approximate · **0.40-0.60** screening tool only, hand-score anything published ·
**<0.40** stop using automatic staging, the pipeline is a signal-provenance instrument.
🔑 **REM per-state κ decides the REM question: ≥0.60 → swap to the Japanese tool's k-means split;
0.40-0.60 → swap but still never report a REM share; <0.40 → accept permanently that REM is not
separable and SAY SO in the methods rather than quietly omitting it.**
🔑 **WAKE cut: choose the multiplier that maximises agreement WITH THE HUMAN.**
🛑 **NEVER choose the threshold that maximises `r@1min`** (B1 peaks at mult 0.9) — that makes our
own validity statistic circular. Human agreement is EXTERNAL and safe.
📦 **3 packs ready** in `/home/skimlab/eeg-processed/2026-08-06/`: `portD-slot2_..._SCORING` (300,
stratified) · `portB-slot1_..._SCORING` (300, stratified) · **`portD-slot2_SCORING_random`
(299, UNSTRATIFIED = prevalence-matched)**. **Score D2 stratified FIRST.**

📋 **`20-areas/eeg-analysis/positive-control-known-signal-injection.md` = SPECIFIED, NOT SCHEDULED.**
Every control we have is NEGATIVE ⇒ they prove we don't hallucinate signal, **not that we find it**.
**A pipeline returning "no signal" for every input would pass every check we currently have.**
4 tests: amplitude (±10%) · **frequency response ⭐ which finally measures what the 1.10 Hz hardware
high-pass does to delta at 0.5/0.75 Hz** · spectral-slope recovery (±0.2, validates the discriminator
that separates a real electrode from a wire) · impedance vs 100 kΩ/1 MΩ resistors (±20%, phase ~0/180°).
BOM: function generator + **~1000:1 divider (10 kΩ / 10 Ω)** + precision resistors. Half a day, ~£20,
**no animals**. 🛑 Bench only, spare headstage, **RHD2216 input range ±5 mV — verify the divider
before connecting.**

⚠️ It only starts to cost us **the moment a result depends on an ABSENCE** (a genotype with less
delta, a drug that suppresses REM, any "manipulation reduced X" claim).

**PIPELINE NOW:** version `2026-08-08`, `*.py.bak` backups. New constants `MIN_BOUT_EPOCHS`,
`BAND_NORM`, `BAND_DELTA_STAGING`, `EXCLUDE_TRANSITION_EPOCHS_FROM_SPECTRA`,
`OTSU_SENSITIVITY_MULTIPLIERS`; new functions `enforce_min_bout`, `steady_state_mask`,
`otsu_sensitivity`, `rem_order_null`, degenerate median fallback. New scripts in `qc/`:
`make_scoring_set.py`, `score_kappa.py`, `selection_bias_test.py`, `floor_pseudoreplication.py`,
`per_animal_forensics.py`.


## From the memory index, trimmed there 2026-10-06 (kept here verbatim)

- ⭐⭐⭐ **[COUNCIL REVIEW + PIPELINE FIXES](council-and-pipeline-fixes.md).** 3 council findings did NOT survive measurement. 4 of 5 physiology checks CANNOT FAIL.
