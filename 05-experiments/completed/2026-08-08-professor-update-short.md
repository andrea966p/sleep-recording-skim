---
tags: [status, eeg, report, professor, figures]
created: 2026-08-08
status: complete
---

# EEG rig update, 8 August 2026

Scope: the original EEG plus EMG cohort. Surgeries 21 to 23 July, first tethered 30 July, recorded through 7 August. Those eight animals have since been replaced, so the three recordings described here are the complete dataset from them. Full working record with every number, every retraction and every raw file reference: [[2026-08-08-full-update-for-professor]].

## Bottom line

1. **Two animals produced continuous, scoreable EEG and EMG across a full 24 hour light and dark cycle.** One of them gave 23.66 hours as a single unbroken block, which is the best recording the project has produced. The other gave 23.28 hours.
2. **The bottleneck was electrical contact in the tether chain.** Not the surgeries, not the implants, not the amplifier, not the room, and not mains hum.
3. **The fix is an engineering change and needs no new surgery.** One animal went from zero usable EEG to 87.9 percent after a tether swap alone, at only 8 days after surgery.
4. **Sleep and wake show real structure**, confirmed by two statistics that are capable of failing, plus the correct light and dark contrast.
5. **Scoring accuracy is still unmeasured.** No human has scored anything yet, and one threshold in the analysis is far more influential than is comfortable. Every architecture number should be read as provisional until a blind scoring set is scored.

## What was wrong

Electrode impedance was treated as a fact about an animal. It is not. Contact on this rig flips on its own, within minutes, in both directions, with nothing done to the animal. One electrode moved by a factor of 64 across 98 minutes on the first afternoon of measurement, and by a factor of 166 inside 23 minutes four days later.

![[2026-08-09-fig01-impedance-trajectories.png]]

No position shows the monotonic decline that a failing implant would produce. Channels recover from a fully open state as readily as they fail, which is the reason no new surgeries were scheduled. The best reading ever obtained on this rig, 0.052 megaohms, sits inside the published range for this electrode type and cannot be produced by a degraded implant.

Two further findings changed how every channel is judged.

**A good impedance reading does not mean a usable recording.** The animal with the most stable electrode on the rig, five sweeps across five days all below 0.35 megaohms, still yields only about 5 percent usable data, because its 331 microvolt signal is 296 microvolts of mains hum. Impedance can see that a wire is connected. It cannot see what is riding on it.

**A plausible looking trace is not evidence either.** Standard cleanup applied to an amplifier input with no wire attached produces a median of about 69 microvolts of EEG looking signal.

![[2026-08-09-fig03-signal-traces.png]]

What survives that trap is the shape of the spectrum, which filtering cannot manufacture, together with mains amplitude. Working animals sit far outside the range covered by wire free inputs on both measures at once, and the two measures are independent.

![[2026-08-09-fig04-spectra-and-discriminator.png]]

## Where the data stands

Six of eight positions fail, and they fail on the EEG channel, which is the channel that decides whether sleep can be scored at all.

![[2026-08-09-fig02-fleet-outcome.png]]

Tested formally: each channel was measured 20 times and compared against 2,240 readings from amplifier inputs with no wire attached, taken in the same sweeps. **Only four of sixteen channels beat an unconnected input after correcting for the sixteen tests, and three of those four are muscle channels**, so exactly one animal had a usable EEG that day.

![[2026-08-09-fig08-hardware-statistics.png]]

**One correction belongs here, found while rebuilding that figure.** The tether comparison of 5 August has been quoted throughout this project as a duty cycle going from 45 percent to 100 percent. That was computed at a 2 megaohm pass mark which was retired the following day, once a cut cable with no animal was found to pass 22 percent of the time at that threshold. Re scored at the corrected 0.5 megaohm pass mark, the same 40 sweeps give **5 of 20 to 2 of 20 for the EEG channel, so that half of the result disappears and points the other way**, while the muscle channel still improves from 0 of 20 to 7 of 20. The concurrent control animal fails to improve at either threshold, so the design is sound; the threshold was doing the work. **The tether conclusion does not rest on this block.** It rests on the recording, where D2 went from zero to 87.9 percent usable EEG with its implant untouched, which is the project's own rule that impedance screens and only a multi hour recording is an outcome. The figure now shows both thresholds rather than the flattering one.

The six failures are not six independent stories. One is a confirmed chewed tether, visible in the data as a channel quieter than a bare wire yet carrying nothing. Two show a correlation of 0.74 and 0.50 between their own two channels, where working animals sit at 0.07, which means one fault upstream of both channels rather than two coincidental electrode failures. Two have a working electrode on one channel and a floating one on the other through the same cable. One holds no animal at all and now serves as a permanent negative control. **Five of six point at the tether chain.**

One animal deserves separate mention. It carried the best electrode in the fleet on 31 July, survived deliberate provocation of every joint in its cable, and produced 8.73 hours of sleep in one unbroken block, which was the only real sleep data the project held until August. Its EEG was electrically open two days later and never recorded again, even though the impedance returned to a good value on 4 August.

![[2026-08-09-fig07-yield-timeline.png]]

## What the two working animals show

![[2026-08-09-fig05-hypnograms.png]]

Both animals are strongly awake in the dark phase and asleep in the light phase, which is the correct direction for a nocturnal animal, and nothing in the quality gate, the staging rule or the persistence statistic has any knowledge of the clock.

Two checks are capable of failing and both pass. State persists over minutes far above both a shuffled control and a synthetic bout calibration, and REM episodes are entered from non REM far more often than a permutation of the same state runs allows, by 5 to 12 standard deviations.

Both are tested against permutation nulls rather than quoted as bare numbers, and figure 9 shows the nulls themselves. No permutation of any recording reached the observed REM ordering in 2,000 attempts, and the persistence values sit far outside the range produced by shuffling the same labels within their own blocks. The same figure carries two deliberate admissions: **no confidence interval is placed on the persistence magnitude**, because the best recording is a single unbroken block and there is no independent replicate to resample, and **the smoothed values plotted sit above the raw label values quoted in the text**, because the 12 second minimum bout rule inflates this statistic by construction.

![[2026-08-09-fig09-sleep-statistics.png]]

The right hand panel of that figure is the quantitative form of the operational rule. Across the seven positions that hold an animal, the rank correlation between impedance and what was actually recorded is **rho 0.73 with an exact permutation p of 0.094, which is not significant**. D2 was connected in a single sweep out of twenty and still produced 87.9 percent usable EEG, while three other channels tied with it at one sweep out of twenty produced nothing at all, and a fourth, connected in none, also produced nothing. The position holding no animal is excluded from that test, since it cannot belong in a correlation about animals.

## What cannot be claimed

**The agreement with the published light phase sleep value is not independent confirmation.** The wake threshold is fitted per animal. Moving it by 25 percent moves one animal from 23 percent asleep in light to 89 percent, and the published value of about 70 percent is reachable from almost anywhere in that range.

![[2026-08-09-fig06-threshold-sensitivity.png]]

Three further limits, stated plainly:

* **No REM percentage.** Two independent rules disagree by a factor of five on this montage, so neither is a measurement. Only wake against non REM, plus the order of transitions, is reported.
* **The physiology checks previously reported as five out of five are not validation.** Four of the five are restatements of the staging rule and cannot fail. Only one, that non REM carries the largest amplitude, is informative.
* **No claim may rest on the absence of a signal.** Every control in place is negative, so they show that the pipeline does not invent signal. They do not yet show that it would find one. This matters the moment a result depends on a genotype with less delta power or a drug that suppresses REM.

Sample size is two animals.

One counterweight belongs here rather than in a footnote. The animal that held the B1 position in July was sacrificed on 5 August because its **skull electrode physically detached**. That is a real head side failure and it is the only direct physical evidence of an implant level problem in the whole cohort. It does not overturn the tether conclusion, which rests on a different animal recovering from zero to 87.9 percent usable EEG with its implant untouched, and on five of six failures showing shared path or cable signatures. It does mean head side attachment belongs on the watch list for the next cohort alongside tether construction.

## The two open items

1. **Blind human scoring and a Cohen kappa. This is the blocking item.** Three sets of 300 clips are built and verified unscored, and the decision rules were written down before any scoring began, so the outcome cannot be reinterpreted afterwards. Above 0.80 the current staging stands. Between 0.60 and 0.80 it is reported with its confusion matrix and treated as approximate. Between 0.40 and 0.60 it becomes a screening tool only. Below 0.40 automatic staging is abandoned. The REM specific value decides the REM question. The wake threshold is then placed by agreement with the human scorer, never by maximising the project's own statistics.
2. **A positive control by injecting a known signal.** Half a day of bench work, roughly 20 pounds of parts, no animals. It would also measure what the 1.10 hertz acquisition high pass does to the bottom of the delta band, which is currently only reasoned about.

## Notes on reading the figures

Tests used: Fisher exact with Jeffreys intervals for anything counted in sweeps or epochs, permutation nulls for the sleep statistics, and Spearman rank correlation for impedance against yield. Where a statistic could not be given an honest interval, none is given and the reason is written on the figure. Every figure is regenerated from source files by the scripts in `eeg-emg-analysis/qc/figures_2026-08-08/`, run with `~/eeg-analysis-venv/bin/python`. No figure contains a typed in measurement: the scripts refuse to run if a computed input is missing rather than falling back to a value copied from a document. Each figure ships alongside a PDF and a manifest recording its source files, transformations, uncertainty definition, palette and random seed, plus alt text. What was wrong with the previous set, and what changed, is recorded in [[figure-and-analysis-audit-2026-08-08]]. All measurements come from one 23.66 hour recording of 6 to 7 August unless stated otherwise. Processing is written on each figure. Traces are plotted on fixed vertical scales, because auto scaling makes every channel look like signal, and the windows shown were selected automatically as the window closest to the median amplitude of that channel, so no panel is a lucky or an unlucky moment. Position labels such as B1 and D2 identify rig positions, not individual animals. The animal in the B1 position changed on 6 August, because the original was sacrificed on 5 August after its skull electrode detached.
