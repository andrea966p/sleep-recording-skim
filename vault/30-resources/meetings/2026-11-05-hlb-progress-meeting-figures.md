---
type: meeting
area: hlb-sod1
status: active
created: 2026-11-03
summary: "Figure set for the HLB SOD1 progress meeting with the professor on 2026-11-05: one style, one figure per slide (design, nanotag sleep, hourly profile, EEG baseline and recovery, behaviour, activity forest plot, tissue), with slide captions; slots 09 to 11 kept for intake and NS-SD Run 2"
tags: [hlb, sod1, figures, professor]
---

# HLB SOD1 progress meeting, 2026-11-05: figures

One figure per slide, white background, water in dark grey and SOD1 in teal throughout. Each dot is one mouse,
the cross is the group mean ± SEM. Every number is re-plotted from an existing results file or result note, nothing
was re-analysed. The story these figures follow is [[2026-11-02-hlb-sod1-final-report-draft]].

Script: `nanotag/analysis/report/meeting_figures.py` (one function per figure, sources in each docstring).
Run it with `~/hlb-eeg-venv/bin/python`; it needs the SKIM NAS mounted (HLBNSL tables) and the tissue outputs in
`nanotag/analysis/out/tissue/` (made by `tissue/cayman_extract.py` and `tissue/cayman_analyse.py`).

## 01 Design: every cohort on one time axis

![[2026-11-05-hlb-meeting-fig01-design-timeline.png]]

The four EEG/EMG cohorts each held a single group (W-SD, S-SD, W-SL, S-SL), so any group difference there is also a
cohort difference. The two nanotag cohorts kept SOD1 and water mice together (HLBNSL 4 vs 5, NS-SD 5 vs 5), which is
where SOD1 vs water is a fair comparison. EEG cohorts: 7 days of SD, 4 h a day (09:00 to 13:00); NS-SD: 6 h on 11-03
and 11-04, Y-maze at 15:00 on 11-04, then sampling.

## 02 Nanotag: total sleep, change from baseline

![[2026-11-05-hlb-meeting-fig02-nanotag-sleep.png]]

Change in total sleep from baseline to treatment, per mouse, in each nanotag cohort (never pooled). SOD1 minus water
was +11 min/day in HLBNSL (95 % CI −130 to +156) and +16 min/day in NS-SD before SD (95 % CI about −18 to +58), so no
detectable effect. HLBNSL shows 3 vs 4 here because mice 49 and 50 had no usable baseline, and its rise in both groups
comes from handling and test days, not from treatment.

## 03 Nanotag: sleep across the day on treatment

![[2026-11-05-hlb-meeting-fig03-nanotag-24h-profile.png]]

Hourly share of time asleep on treatment in HLBNSL (SOD1 4, water 5), mean ± SEM, handling and test windows removed.
The two groups overlap at nearly every hour, in the light (about 74 vs 72 % asleep) and in the dark. The NS-SD
profile is not drawn here because its hourly data sit on the office PC; it looks the same
(`2026-10-31-NSSD-run1-zt-profile.png` in [[2026-10-31-NS-SD-run1-nanotag-baseline-vs-sod1]]).

## 04 EEG: baseline sleep, SOD1 vs water

![[2026-11-05-hlb-meeting-fig04-eeg-baseline.png]]

Sleep as a share of usable time at baseline, already on treatment, in the 21 mice with usable sleep stages from the
four EEG cohorts (SOD1 10, water 11). 52.0 vs 52.5 % over 24 h (p = 0.81, 95 % CI −4.7 to +3.6 points), and the same
in the light and dark phases. The smallest difference this sample could detect is about 6 points.
[[hlb-eeg-sleep-overview]]

## 05 EEG: recovery minus baseline

![[2026-11-05-hlb-meeting-fig05-eeg-recovery.png]]

Change in sleep from baseline to recovery in the same mouse, ZT4 to 24. Without SD, SOD1 and water did not differ
(+2.1 vs +0.1 points, n = 6 vs 7, p = 0.52). After SD only one mouse per arm is usable: HLBWSD08 gains +9.3 points,
HLBSSD18 +18.1, but only +1.5 (open circle) if its EMG artefact epochs count as wake, so the SD comparison is two
single cases and cannot be read.

## 06 Behaviour with normal sleep (HLBNSL)

![[2026-11-05-hlb-meeting-fig06-behaviour.png]]

Y-maze alternation and arm entries, open-field distance and NOR discrimination index, SOD1 4 vs water 5. Both groups
alternate above chance (60.5 vs 62.8 %) and prefer the novel object, with no detectable SOD1 effect on memory; SOD1
mice entered more arms (48 vs 38) and walked further (64 vs 51 m). The NOR panel shows pose model2 per mouse (the
only per-mouse NOR table on this machine); the report table quotes model1 (+0.34 vs +0.37), same conclusion
(p = 0.73 model1, 0.91 model2), and the novel object was always the same object on the same side.

## 07 Activity: three readouts, one direction

![[2026-11-05-hlb-meeting-fig07-activity-signal.png]]

Standardised SOD1 minus water difference (Hedges g, 95 % CI) for the three activity readouts, each in its own cohort:
Y-maze arm entries +1.19, open-field distance +1.66 and NS-SD dark-phase tag activity change +1.38. All point to
more activity with SOD1, but the exact tests give p = 0.063, 0.11 and 0.040 at 4 to 5 mice per group, so this is a
trend to test, not a finding. The CIs are a normal approximation, which is why one excludes 0 while its exact
rank test does not.

## 08 Tissue: SOD activity and MDA (EEG cohorts)

![[2026-11-05-hlb-meeting-fig08-tissue.png]]

Total SOD activity (Cayman kit method) in hippocampus and heart, and hippocampal MDA, per mouse, in the four EEG
cohorts (n under each group). Hippocampal SOD shows no SOD1 effect (p = 0.66); hippocampal MDA is higher in the SD
cohorts (p = 0.007) with or without SOD1; heart SOD shows a crossover (interaction p = 0.0006). Each group is its own
cohort, and SD mice were sampled about a day after the last SD bout, so none of this is causal.
[[2026-11-02-EEG-cohorts-tissue-SOD-MDA-reanalysis]]

## 09 to 11: still to come
- 09: intake and dose received (another figure, being made separately).
- 10 and 11: NS-SD Run 2 (sleep during and after SD) and the Y-maze after SD; data on 2026-11-04.

## Notes for checking the draft (found while making the figures, the draft is unchanged)
- Report section 5 still quotes the 2026-10-06 quick compute (61.1 vs 60.6 % of 24 h asleep); the 2026-11-03
  re-score gives 52.0 vs 52.5 % ([[hlb-eeg-sleep-overview]]).
- Report section 7, heart: the percentages (water SD +15 % over normal sleep, SOD1 SD −10 %, SOD1 normal sleep +11 %
  over water) come from the sheet method, while the table beside them uses the Cayman values, which give +39 %,
  −20 % and +26 %. The interaction p is the same either way.
- [[hlb-sod1-design]], batch table: the W-SL and S-SL date ranges are swapped. The sheet `Registry` gives W-SL
  08-31 → 09-18 and S-SL 09-03 → 09-21 (S-SL sampling slipped to 09-22), matching the EEG recording dates.
- From the sheet `Registry`, liquid monitoring started 11 days before the first SD bout in W-SD and S-SD, so "about
  2 weeks on SOD1 or water" before SD in section 7 is closer to 1.5 weeks. By the sheet's CSD start and recovery
  recording dates, both SD cohorts had 7 SD days (the draft says 7 to 8).
