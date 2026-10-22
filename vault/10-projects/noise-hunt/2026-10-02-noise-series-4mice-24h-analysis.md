---
tags: [noise, eeg, emg, sleep, qc, analysis, nas]
created: 2026-10-02
status: complete
---

# The four noise-series mice over 24 h (2026-10-01 21:00 → 10-02 21:02): full analysis

> [!abstract] TL;DR
> **What this is:** the complete analysis of the first two noise-series recordings with mice: an overnight (dark) run and the following light-phase run, the same four mice, nothing touched between them. It ran on e10 after both runs finished. The full write-up of the series is [[2026-09-30-xdaq-noise-series]]; the methods audit is [[2026-10-02-noise-series-method-audit]].
>
> **The results, in order of weight:**
> 1. **Data are complete and on the NAS.** 23.78 h with zero dropped samples. 8 per-mouse CSVs with checksums verified at both ends, plus an analysis folder (see "Where everything is").
> 2. **First official verdict for a noise-series mouse.** B1's light phase is **SCOREABLE** with the pipeline unchanged (r@1min 0.407). Everything else is NO VERDICT at rung 2: the ground gate cannot judge these chips (audit C1). A1 and B2 are EEG-only, because their EMGs are open.
> 3. **All four EEGs are connected**, and the hum stayed steady for 24 h. B1's floor rose from 699 to 980 µV between the dark and the light phase with nothing touched. That rise alone flipped its official verdict.
> 4. **Removing mains from the EMG is a validity gain, not a way to pass.**
>    - Shuffle control: 0 of 100 recordings pass.
>    - The change tracks how much mains the EMG carries. Recordings with little mains do not change.
>    - The nocturnal wake contrast becomes physiological in 47 of 49 recordings (41 of 49 as published).
>    - Still not adopted: it would re-score published numbers. That is a decision for Andrea and the professor.
> 5. **System-wide events.**
>    - Night: four (the lights-ON plus three small ones at 01:59:56, 07:27:42 and 08:41:14), against a chance of 0.01.
>    - Light phase, outside Andrea's visit: three real ones (17:10:08, 18:12:11, 20:56:36) against a chance of 0.03.
>    - During the visit there are 10, but both ports were busy then, so chance is already 2.6.
>    - The air showers left no electrical trace at all.
> 6. **Code review:** two independent reviews found real defects. Several published numbers changed; all are listed below.

## Where everything is

| what | where |
|---|---|
| per-mouse CSVs (EEG, EMG, µV, 1 kHz), one folder per mouse per run | NAS `02_Data_Sleep/andrea/noise-tests/Baseline/20261001_POS-<slot>_B/` (overnight) and `20261002_POS-<slot>_B/` (light phase) |
| reading guide, findings, markers, figures, staging outputs, scans, scripts | NAS `02_Data_Sleep/andrea/noise-tests/ANALYSIS_2026-10-01_to_10-02_4mice_24h/` (`README.txt` first) |
| raw 134-channel file of the overnight (for re-scans elsewhere) | NAS `noise-tests/RAW_20261001_2100_overnight_4mice_cfdf8ebde0c6/` (the light-phase raw is on e10 and in the S3 archive) |
| everything on e10 | `~/radix/noise-tests/2026-10-02/` (`official-noise-tests/`, `diag-*`, `analysis-24h/`, `fullscans-v2/`, `emg-mains-test-all/`) |
| event markers in each file's own time base | [[2026-10-02-noise-MARKERS-overnight-uid1001-21-00-07.tsv]], [[2026-10-02-noise-MARKERS-lightphase-uid1002-09-16-58.tsv]] (from `qc/noise_mice_markers_2026_10_02.py`); also in the NAS analysis folder `markers/` |

The mice. Slot names are rig positions. The NAS keeps the `POS-<slot>` placeholders, by Andrea's decision: these mice are not used in experiments.

| slot | channels | animal | usable as |
|---|---|---|---|
| A1 | A/1 EEG, A/2 EMG | B6/J BomTac ♀, DOB 2026-04-12, no ID | **EEG only** (EMG open on the implant side) |
| A2 | A/33, A/34 | HLBWSL30 (W-SL) | EEG + EMG |
| B1 | B/1, B/2 | HLBSSD20 (S-SD) | EEG + EMG |
| B2 | B/33, B/34 | same strain, sex, DOB as A1 | **EEG only** (EMG open) |

## 1. Official verdicts (pipeline unchanged)

Stage 2 and stage 3 were run with the official code and the stage-1 gate. Output went into a separate root (`official-noise-tests/processed/`), so the test mice stay out of `~/eeg-processed`. The verdict ladder (`cards/ladder.py`) was re-run with the console's own run manifests, and the `qc` block in each NAS `info.json` was refreshed from those cards. The console had written those blocks before stage 3 existed.

| slot | overnight (dark, 12.03 h) | light phase (11.75 h) |
|---|---|---|
| A1 | NO VERDICT: floor slope −3.24 (floor contaminated) | NO VERDICT: slope −3.19 |
| A2 | NO VERDICT: slope −2.54; stage 3 REJECT r 0.19 | NO VERDICT: slope −2.39; stage 3 REJECT r 0.29 |
| B1 | NO VERDICT: floor 702 µV < 800; stage 3 SCOREABLE r 0.304 | **SCOREABLE**: rungs 0-3 PASS (93.7 % usable, r@1min 0.407), rung 4 PROVISIONAL |
| B2 | NO VERDICT: slope −3.44 | NO VERDICT: slope −3.38 |

"NO VERDICT" means the chip's wire-free control could not judge the connection. It is **not** a failure of the animal. B1's two verdicts differ only because its floor rose past the gate during the day (section 2). That is the audit's C1 finding, now shown by the official pipeline itself.

## 2. Signal quality over 24 h

![[2026-10-02-noise-figM-24h-signal-quality.png]]

**Figure M.** The 60 Hz line the QC gate reads (10 s epochs from each run's QC bundle; lines are hourly medians), from 21:00 to 21:02 the next day. Grey is the dark phase, the hatched band is the 15 min between the two files, orange marks the disturbed windows, and green dotted lines mark the system-wide events. The A1, A2 and B2 floors and every EEG hold flat. **B1's floor sits under the 800 µV gate all night (hourly median 699 µV) and over it all day (980 µV).** A2's EMG mains wanders between 14 and 30 µV: 17 µV dark, 21 µV light, highest from 13:00 to 17:00. Nobody touched either mouse.

| slot | chip floor dark → light (µV) | EEG 60 Hz dark / light (µV) | EEG 60 Hz ÷ own floor | EMG 60 Hz dark / light (µV) |
|---|---|---|---|---|
| A1 | 2882 → 2915 | 20.2 / 20.1 | 0.007 | open (4.8 mV) |
| A2 | 2121 → 2123 | 3.3 / 2.9 | 0.002 | 16.8 / 21.0 |
| B1 | **699 → 980** | 6.8 / 6.2 | 0.010 (dark) | 4.5 / 4.6 |
| B2 | 1941 → 1934 | 3.9 / 3.9 | 0.002 | open (4.9 mV) |

The EEG ÷ floor ratio is this project's discriminator for a connected EEG: about 0.03 or less means connected, about 1 or more means open ([[weak-chip-ground-vs-open-electrode]]). **All four EEGs are connected.**

## 3. Sleep-wake over 24 h (the two mice with EMG; DIAGNOSTIC)

![[2026-10-02-noise-figN-24h-sleep-wake.png]]

**Figure N.** Stage 3 unchanged, run as published and with the EMG's 60/120 Hz notched (diagnostic, QC bypassed). The strips show 4 s epochs, orange WAKE and blue SLEEP. REM is folded into sleep because the stager constructs REM %, so it is never reported. The bottom panel is WAKE % per hour. Both mice are more awake in the dark, as nocturnal mice should be.

| | r@1min overnight / light | WAKE % (24 h hourly medians), dark vs light |
|---|---|---|
| A2 as published | 0.19 / 0.29 (both REJECT) | 18 vs 11 |
| A2 EMG notched | **0.323 / 0.44 (both SCOREABLE)** | 26 vs 22 |
| B1 as published | 0.304 / 0.407 (SCOREABLE) | 30 vs 18 |
| B1 EMG notched | 0.308 / 0.426 | 31 vs 19 |

The shuffled-label null r@1min is between −0.02 and +0.01 in every run. **Caveats:**
- n = 2 mice, and nobody has hand-scored an epoch (kappa is still the gate).
- WAKE % over 24 h (about 24 %) is low for this project's good animals (43-54 %) and for C57BL/6 norms. The Otsu cut is fitted per animal, so absolute WAKE % is provisional; the dark-light direction is the robust part.
- Andrea's visit falls inside the light phase (section 5).

## 4. EEG slow-wave power over 24 h (all four mice)

![[2026-10-02-noise-figO-24h-eeg-delta.png]]

**Figure O.** EEG delta (1-4 Hz) power, as hourly medians normalised to each mouse's own median; the bottom panel uses NREM epochs only.
- **All epochs, light ÷ dark:** A1 0.96, A2 1.07, B1 1.30, B2 1.14.
- **NREM only:** A2 1.05, B1 1.18. B1's NREM delta peaks in the first light hour and declines across the light phase, the textbook slow-wave decay.

A1 and B2 cannot be staged: their EMG is open, and this project has deliberately not built an EEG-only stager. Their EEG is still valid for spectral work.
- **B2** follows B1's light > dark pattern.
- **A1** shows no light-dark modulation. A1 also carries the highest EEG hum (20 µV), so its EEG is connected but the least informative of the four.

## 5. Disturbances: Andrea's visit and the air showers

Times come from the canonical markers. **Andrea's visit began at 15:19:33 by the data** (the message said about 15:35). The last event of the visit is at 16:33:30; the end of the visit was not logged.

| window (light phase) | A2 WAKE %, as published / notched | B1 WAKE %, as published / notched |
|---|---|---|
| rest of the light phase (windows excluded) | 10.4 / 19.9 | 17.8 / 18.8 |
| Andrea's visit 15:19-16:40 | **20.4 / 34.3** | 12.8 / 13.4 |
| air showers 17:21:30-17:27 | 18.3 / 32.9 | 72.0 / 78.0 (awake from 17:18:40, before the shower) |
| air showers 17:34-17:37 | 0.0 / 0.0 (n = 45 epochs) | 55.6 / 95.6 |

A2 was about twice as awake during the visit. B1 was not.

![[2026-10-02-noise-figI-air-shower.png]]

**Figure I.** The air shower at 17:22:14 on Andrea's clock, which ran at least 8 s ahead of e10, so the true switch-on was at or before 17:22:06 (dashed line). The new step detector (|d/dt| of the 50 ms comb) sees steps of about 0.1 mV.
- **No step reached two chips at once, and no floor moved** (×1.00-1.02). A step on two chips would have had to clear 116 µV (the second-lowest chip threshold; A2 79, B1 116, B2 362, A1 573 µV, since A1 and B2 have busy baselines).
- The 3 single-chip steps are all on B1, during a 2.5-4 mV burst on B1's own EMG: that mouse moving.
- A2, asleep, bursts its EMG ×11 at +9.6 s or later after the true switch-on. A burst from quiet happens by chance within 11 s about 11 % of the time. **Arousal possible, not shown.**

![[2026-10-02-noise-figJ-air-shower-2.png]]

**Figure J.** The 17:35:50 air shower (Andrea's clock), shown with both readings of the Allego time 29937.4 s: 17:34:12.5 if Allego shows stream time, 17:35:55.5 if it shows file time. There were no system-wide or single-chip steps and no floor change. A2 was already awake.

## 6. System-wide events and the splitter

![[2026-10-02-noise-figL-system-events-both-runs.png]]

**Figure L.** An event counts as system-wide when it reaches the voting floors on **both ports** in the same 100 ms; chips whose own floors fire constantly are left out of the vote (this rule was rewritten after the second code review, see section 8).
Chance comes from a *local* null: one port's hits shifted 2-30 s against the other's, so two ports that are busy at the same time do not count as coupled.
- **Overnight: 4 events, chance 0.01.** The lights-ON at 08:59:51.0, plus three smaller ones that reached both clean floors (A2 and B1) at 01:59:56.5, 07:27:42.5 and 08:41:13.8. Their cause is unknown: no video, and a building load at night is possible.
- **Light phase: 13 events.**
  - Outside the visit: 3, chance 0.03. These are **17:10:08** (all 4 chips ×61-115, the day's strongest), **18:12:11** and **20:56:36**, all unexplained.
  - Inside the visit: 10, against a chance of 2.58. Both ports were busy then (hands, probe, a person at the rack), so most of these are co-activity rather than one building transient.
- The lights-OFF at 21:01:11.5 stays under the bar (B1 ×1.2).
- The air showers left nothing.

A2+B1 floor coincidences (`night_spikes`, chance per 30 s stratum):
- overnight: 4, chance 0.06;
- light phase: 10, chance 8.7. During the visit both floors were busy, so these are at chance.

**Splitter (uid0921, two 1 h blocks, chance per 30 s stratum):** the two mice sharing a splitter coincide at 1.1/0.7/1.1/0.9× (night) and 0.9/0.4/0.9/0.8× (day). Mice on different ports coincide at 1.0× (0.6-1.4) and 1.0× (0.4-2.0). **No coupling**, the same conclusion as on 10-01.

## 7. Is the EMG mains notch a validity gain? (whole archive)

![[2026-10-02-noise-figP-emg-notch-validation.png]]

**Figure P.** Every recording in `~/eeg-processed` (100). Stage 3 was run as published, with the EMG notched, and notched with the EMG's 4 s epochs shuffled. The unnotched run reproduces 99 of 99 official verdicts.
1. **Negative control:** notched + shuffled passes 0 of 100, with median r@1min −0.002 and maximum 0.029. The notched persistence is measured, not manufactured.
2. **Dose-response:** mains is typically **68 % of the variance in the stager's EMG measure** (10th-90th percentile 12-98 %). The change follows that share: Spearman 0.53 for |Δr| and 0.66 for |ΔWAKE|.
   - Below a share of 0.2 (15 recordings) nothing flips: |Δr| median 0.014, |ΔWAKE| ≤ 1.6 points.
   - At 0.8 or more (34 recordings), 22 go REJECT → SCOREABLE.
   - Recordings and animals repeat across folders, so the n count recordings and the p values are optimistic.
3. **Physiology** (the stager never sees the clock): in the 49 recordings covering both phases, dark WAKE % exceeds light WAKE % in 41 as published and **47 notched**. The median contrast goes from +25 to **+37 points**. In the 29 recordings scoreable both ways it barely moves (+36 → +37). The notch repairs the broken recordings and leaves the good ones alone.

![[2026-10-02-noise-figK-emg-notch-all-days.png]]

**Figure K.** The same 100 recordings: SCOREABLE 44 → 69 (27 up, 2 down). The two that drop fail a physiology check after the notch, not r: 07-31 C2 (`nrem_largest_amplitude`) and 08-19 C1.

> [!quote] Paper-ready
> In this rig the EMG measure used for wake staging was dominated by mains (median 68 % of its variance). Removing 60/120 Hz from the EMG left recordings with little mains unchanged, could not create sleep persistence from shuffled EMG (0/100), and restored the nocturnal wake excess in 47 of 49 recordings that cover both phases (41/49 before).

Not adopted: adopting it is a pre-registered pipeline change with the falsification suite, and it would re-score published numbers.

## 8. What the code review changed (two independent reviewers, verified and fixed)

| published claim | corrected |
|---|---|
| Fig B: "the transient arrives about 0.25 s after the timer" | no such delay: it was the fraction of a second lost to the file-name clock. The event is at 08:59:51.0 on the file clock |
| overnight: "one all-chip event (lights-ON); nothing system-wide 01:05-08:50" | **4** system-wide events (chance 0.01); 3 of them in 01:05-08:50 (the old vote let busy chips vote and rang ahead of transients) |
| light phase: "32 all-chip events, chance 1.33" | **13**: 3 outside the visit (chance 0.03) and 10 inside it (chance 2.58, both ports busy). The rest were local to port A plus noisy B2 |
| light A2-B1 coincidences "chance 0.08" | 8.7 (chance local to 30 s; whole-file rates are far too low while both floors are busy) |
| air showers: "no switching step" | true, now at a two-chip sensitivity of 116-149 µV (the old detector only saw steps of about 1-2 mV) |
| meter OFF: A2 muscle band "×0.42" | ×0.83 (mains leaked into the ±1-bin band). The 60 Hz line still rose ×1.15 while the muscle band did not, so the pickup verdict stands |
| meter ON: "+25-40 % per touch" | median ×1.22 during the four contacts (vs hovering; ×1.21 vs before the probe came near) |
| presence: B1 floor dip "×0.61" | ×0.51 (one-second extremes depend on where the 1 s bins fall) |
| "A2's EMG 60 Hz drifts 15 → 30 µV over the day" | it wanders 14-30 µV and returns to about 20 µV by 21:00 (that reading ended at 16:35) |
| A2 air-shower burst "+1.4 s (chance ~3 %)" | +9.6 s or later from the true switch-on (Andrea's clock ran ahead), chance about 11 % |
| splitter 0.8/0.8/1.2/0.7 (night) | 1.1/0.7/1.1/0.9 (chance local to 30 s), same conclusion |

Bugs fixed in code:
- `pipeline/stage1_qc.py` wrote its feature cache **into `~/radix/data`** whenever it was given a full path (`os.path.join` restarts at an absolute component). Two such files, from today's diagnostic runs, were moved out before the 01:30 S3 job could archive them for good; a regression test was added.
- The scan tools now take the time origin from `status.start_time`, not the file name.
- `emg_mains_staging_test.py` refuses a stale symlink and prints its own method check.
- `rig_session_2026_10_02.py` no longer rewrites a marker file.
- Figure titles are computed, not typed.

## Reproduce

```bash
cd ~/sleep-recording-skim/eeg-emg-analysis
python3 qc/noise_mice_markers_2026_10_02.py OUT                       # markers, both runs
python3 qc/noise_mice_24h_2026_10_02.py OUT FIGDIR                     # tables + Figs M, N, O
python3 qc/emg_notch_validation_2026_10_02.py OUT FIGDIR ~/eeg-processed/20*/   # Fig P (after emg_mains_staging_test.py)
python3 -m qc.allchip_scan_file /home/skimlab/radix/data/<base> OUT.csv
python3 qc/night_spikes.py /home/skimlab/radix/data/<base>
python3 qc/air_shower_2026_10_02.py 17:12:00 17:27:30 figI.png 17:22:14 andrea
```

Run analysis with `/usr/bin/python3`, at idle priority, and never while the rig records.

## Open

- What were 17:10:08, 18:12:11, 20:56:36 and the three night events? Facility loads are the first suspect. A building log, or a sensor on the rack's mains, would settle it.
- Adopting the EMG notch is a decision: pre-register it, run the falsification suite, re-score the affected papers' numbers.
- Air-shower arousal: time each start on one clock tied to the file. A photo of Allego's time display next to the phone clock fixes both the convention and the phone's offset.
- The ground gate (C1) needs replacing; B1 shows why.
