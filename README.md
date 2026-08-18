# eeg-emg-analysis

Everything that happens after Allego writes a file to disk.

## Install

```bash
~/eeg-analysis-venv/bin/python -m pip install -e .
```

Use `~/eeg-analysis-venv/bin/python`. The `/opt/neurosurveillance` venv has a
numpy/scipy ABI mismatch and dies with `numpy.core.multiarray failed to import`.

Every filesystem location is an environment variable with the historical value as
its default, so nothing changes here and everything is overridable elsewhere:

```bash
~/eeg-analysis-venv/bin/python -m core.paths      # show what resolves to what
```

`EEG_RAW_ROOT` · `EEG_PROCESSED_ROOT` · `EEG_IMPEDANCE_ROOT` · `EEG_VAULT_ROOT` ·
`EEG_CACHE_ROOT` · `EEG_FIGURE_STYLE_DIR`.

## The one thing to run

```bash
# 1. verdicts: one JSON per animal-recording
~/eeg-analysis-venv/bin/python cards/ladder.py allego_1__uid0806-16-57-38 \
    --cohort HLB-fem-profsurgery-troubleshooting

# 2. the pages
~/eeg-analysis-venv/bin/python cards/render_card.py cards/out/HLB-fem-profsurgery-troubleshooting/
~/eeg-analysis-venv/bin/python cards/render_cohort_sheet.py cards/out/HLB-fem-profsurgery-troubleshooting/

# 3. the exports a human opens
~/eeg-analysis-venv/bin/python cards/export_text.py "$EEG_PROCESSED_ROOT/2026-08-06/"
```

Full explanation: vault
`02-procedures/eeg-data-analysis/animal-card-and-verdict-ladder.md`.

## Layout

```text
core/
  qc_thresholds.py   THE constants. Every number, with its provenance.
  criteria.py        THE connection criterion, the in-file floor, the filter chain.
  paths.py           every filesystem location, one env var each.
cohorts/
  schema.py          Animal and Cohort. Identity, ages, timelines, validation.
  load.py            manifest loading + husbandry spreadsheet join.
  *.yaml             one manifest per cohort.
cards/
  ladder.py          the six-rung verdict engine. No plotting.
  render_card.py     one A4 page per animal-recording.
  render_cohort_sheet.py
  export_text.py     TSV exports, full rate and per epoch.
  figs_common.py     THE style, status palette, statistics helpers and export.
pipeline/
  stage1_qc.py stage2_split.py stage3_features.py stage4_export_edf.py
  cohort_summary.py pipeline_common.py run_pipeline.sh
convert/
  to_mat_csv.py      stage 2 signals -> MATLAB .mat / CSV. Derives nothing.
qc/                  acquisition control and forensics scripts
  figures_2026-08-08/  a FROZEN figure set for two recordings of one day;
                       its figs_common.py is a thin adapter over cards/.
tests/               the regression suites AND the falsification suite
```

## Rules that the code enforces, not just documents

1. **One definition per constant.** `core/qc_thresholds.py` and nowhere else.
   Every card prints that file's content hash.
2. **The hum criterion refuses to run** on a channel where it contradicts the
   slope criterion, because that is the floating-no-ground signature. Hard error.
3. **The slope criterion refuses non-EEG roles.** Real EMG and ECG are broadband
   and therefore flat; a slope test calls a working muscle channel dead.
4. **The slope criterion refuses band-limited input.** A filter corner inside the
   measurement band is read as slope. Added 2026-08-10 — see below.
5. **A ladder rung is not evaluated if the rung below it failed**, and no panel
   is drawn for it.
6. **Impossible dates raise** rather than drawing a nonsense timeline.
7. **Missing husbandry data renders as "not recorded"**, never as blank.
8. **Figures carry no typed-in measurements.** A missing derived input is fatal.

## Tests

```bash
~/eeg-analysis-venv/bin/python tests/test_cohort_schema.py
~/eeg-analysis-venv/bin/python tests/test_criteria_regression.py
~/eeg-analysis-venv/bin/python tests/test_ladder_verdicts.py
~/eeg-analysis-venv/bin/python tests/test_criterion_falsification.py
```

The first three are REGRESSION suites: they reproduce numbers already published
in the vault, exactly. **Any movement there is a bug, not an improvement.**

The fourth is different and it is the important one. It builds synthetic
recordings whose answers are known before the engine runs, and half its cases are
things the engine **must reject**. Movement there is *not* automatically a bug in
the test — it means the criterion stopped doing what it claims. The three
regression suites would have stayed green through the entire hum-criterion era,
while a floating unreferenced amplifier input was being reported as 100 percent
usable EEG. A test that can only pass is not evidence.

## Things that are true on this rig and cost weeks to learn

* **The signals are already bipolar.** `/1` is EEG, `/2` is EMG, and each is
  already a difference computed in hardware before the ADC. `/3` and `/4` are
  empty pads. Never subtract one from the other.
  🔴 A whole second implementation of this repo assumed the opposite — four rows
  per mouse, differenced offline — and survived until 2026-08-10, when it was
  deleted. It produced "EEG" that was EEG minus EMG and "EMG" that was one empty
  pad minus another, and it carried its own second constants file that disagreed
  with `core/qc_thresholds.py` about the delta band, the EMG band and the rail
  voltage. It never touched a published number, because the current pipeline
  never imported it. **If you find code that subtracts, it is not ours.**
* **A filtered wire-free input looks like beautiful EEG**, about 69 µV of it.
  Judge connection on the spectrum against the in-file floor, never by eye.
* 🔴 **Filtering DOES manufacture slope.** A wire-free input band-passed to
  0.5–30 Hz measures a 1–40 Hz slope of −1.08, against 0.00 raw and −1.81 for
  real EEG, and scores **100 % usable**. The criterion is valid only on raw data.
  This is now enforced: a scale-free check (a power law has the same slope in any
  sub-band; a filter corner does not) refuses band-limited input. Real recordings
  measure +0.29 to +1.02 against a −1.00 bar, so the guard is silent on them.
* 🔴 **ECG IS RETIRED. Do not add it back without new hardware.** Seven of seven
  animals showed no detectable heartbeat against a *real* null: unwired inputs in
  the same file reach autocorrelation z = 13.1 and comb score 1047, and nothing
  on any `/3` site beat that. Earlier "CARDIAC" verdicts were boundary artefacts
  and are withdrawn. The detectors (`cardiac_comb_test.py`,
  `heartbeat_on_quiet_stretch.py`) were deleted on 2026-08-10 because keeping a
  detector for an absent signal invites someone to run it and find noise.
  **The methods sentence is:** *ECG was attempted on a third bipolar site per
  animal and produced no heartbeat distinguishable from unwired amplifier inputs
  recorded simultaneously in the same file, in 7 of 7 animals; it is reported as
  a negative result and no cardiac measure is derived.*
  `CohortSpec(roles=("eeg","emg","ecg"))` still exists, because the 2026-08-07
  onward recordings physically have a third site and the FLOOR MUST START AT `/4`
  for those files. Retiring the measurement does not change where the floor is.
* 🔴 **Envelope variability does NOT validate an EMG channel here.** A1, which has
  no ground at all, scores 0.769 against a floor-derived bar of 0.319 — near the
  top of the cohort. A floating input is high impedance and picks up variable
  interference, so a test rewarding variability rewards having no electrode. This
  is the hum criterion's failure in a new costume. `qc/emg_state_dependence.py`
  prints the column as evidence against the test and emits no pass from it.
* **Impedance blocks screen; only a multi-hour recording is an outcome.** A
  21-minute block once gave p = 8.4e-08 for a conclusion the overnight recording
  reversed completely.
* **A low, stable, zero-flip impedance can mean no ground at all.** Every genuine
  contact failure here has been intermittent.
* **Railing is the open-electrode signature, not movement.** The position holding
  no animal rails 100% of the time.
* **Position labels are not animals.** The B1 position held two different mice.
  That is what `cohorts/` exists to fix.
