---
type: experiment
area: hlb-sod1
status: done
tags: [experiment, eeg, emg, sod1, sleep, S-SD, W-SD, W-SL, S-SL, emg-rescue, hlb, analysis, completed]
created: 2026-10-06
recordings: [allego_1__uid0819-17-25-20, allego_2__uid0827-12-58-32, allego_0__uid0825-09-00-00, allego_2__uid0902-13-00-28, allego_0__uid0910-09-00-00, allego_0__uid0917-09-00-09, allego_0__uid0912-08-55-18, allego_0__uid0921-00-17-34]
---

# S-SD EMG rescue: muscle power between the 60 Hz harmonics, from the raw 1000 Hz file (2026-10-06)

> [!abstract] TL;DR
> - **Why.** Andrea asked for at least one S-SD mouse to be scored *with EMG* (not EEG only), so the SOD1 deprivation arm
>   can enter the comparison of [[2026-10-06-SOD1-sleep-EEG-2x2-quick-compute]]. Every S-SD mouse fails on its EMG. Stage 3
>   reads EMG over 10–124 Hz, and on these leads that band is 90–100 % mains.
> - **Method.** EMG power is measured from the raw 1000 Hz file, only in the gaps between 60 Hz harmonics (67–470 Hz).
>   Stage 3 is otherwise unchanged. The gate is stage 1's own gate without its EMG-mains clause. The same processing is
>   applied to every mouse in all four batches.
> - **Validation.** Where the EMG already worked, this reproduces the notch-validated staging: **κ median 0.95, minimum
>   0.89, 33 windows**, with wake within +1.8 points. The shuffled-EMG control rejects 57 of 57 windows (max r 0.038).
> - **Rescued: HLBSSD15 (S-SD, C1) at both timepoints**: r@1min 0.497 and 0.431, more wake in the dark than in the light
>   both times, REM entered from NREM above its null. HLBSSD18 is rescued at baseline only; its recovery EMG still carries
>   no state signal (r 0.03).
> - **SOD1 × CSD, one mouse per arm.** From 13:00 to 09:00 after CSD, HLBSSD15 (SOD1) slept **+6.6 points** more than at its
>   own baseline; HLBWSD08 (water) slept **+16.1**. The ad libitum controls changed +4.1 (SOD1, n = 2) and −0.2 (water, n = 3).
>   Interaction **−13.8 points** (dark −14.9, light −4.8). The SOD1 mouse rebounded less, but it also slept the most of
>   any mouse at baseline (63 % of 13:00–09:00 against HLBWSD08's 44 %). Ad libitum mice differ by up to 12.6 points among
>   themselves. **This is a case comparison, not a result.**
> - **Without deprivation there is still no SOD1 effect, now on n = 8 vs 10**: 55.7 vs 53.4 % of 24 h, +2.3 points,
>   p = 0.34, 95 % CI −2.6 to +7.1.
> - **Not adopted** into the pipeline: like the 10-02 notch, it would re-score published numbers.

## Why the S-SD EMGs failed

Medians from the rung-1 card (µV). "Mains-dominated" means the 60 Hz amplitude is about the size of the whole signal,
which is what an open or high-impedance lead picks up.

| mouse | EEG | EMG baseline (rms / 60 Hz) | EMG recovery (rms / 60 Hz) |
|---|---|---|---|
| HLBSSD18 (D2) | good both | 50 / 40, connected | 62 / 49, connected but flat |
| HLBSSD15 (C1) | good both | 455 / 592, mains-dominated | 397 / 506, mains-dominated |
| HLBSSD11 (A1) | intermittent at baseline | 48 / 10, good | 1172 / 1470, mains-dominated |
| HLBSSD16 (C2), HLBSSD12 (A2) | good EEG | 876–1412 µV of mains | same |
| HLBSSD14 (B2), HLBSSD19 (D1) | EEG dead at baseline | — | — |

For HLBSSD15, the harmonics at 60 and 120 Hz carry about 100 % of the power in 10–113 Hz. The official EMG measure was
reading mains and nothing else.

## Method

1. **Raw read on e10** (`extract`). For each 4 s epoch of every mouse-window: a Blackman-Harris Welch PSD at 1 Hz
   resolution of the raw 1000 Hz EMG. Power is kept in eight gaps, each 7 Hz clear of every 60 Hz multiple: 10–53, 67–113,
   127–173, 187–233, 247–293, 307–353, 367–413 and 427–470 Hz. A built-in self-check adds 1.8 mV of 60.3 Hz mains and its
   harmonics to white noise; the gap power moves by less than 5 %.
2. **Stage 3 unchanged** (`stage`), with two inputs swapped in memory:
   - `emg_rms` := √(gap power, 67–470 Hz). This is the primary measure; 10–470 Hz is the sensitivity variant.
   - The gate := stage 1's gate (EEG 60 Hz < 150 µV, EEG not flat, not clipped) **without** its "EMG 60 Hz < 150 µV"
     clause, and the EMG not railed.
   - Stage 3's own checks still decide SCOREABLE: r@1min > 0.30, wake 15–90 %, informative physiology.
3. **Negative control.** The same run, with the primary EMG measure shuffled within contact blocks.
4. **Inclusion.** The EEG is connected by rung 2's test applied to the EEG role alone (longest unbroken block ≥ 15 min),
   the window is gap67 SCOREABLE, and its shuffle control is REJECT.
5. **Every mouse, every batch.** Stage 2 was re-split with `--all-verdicts` for S-SD and both SL baselines, into a separate
   folder, so mice that stage 1 had dropped got files too. The official and the all-verdicts splits of the same mouse are
   identical sample for sample.

> [!warning] A gate correction, disclosed
> The first run used rung 2's per-epoch EEG mask as the gate. That mask fails the slope test in scattered epochs, which
> breaks windows into short blocks and depresses r@1min. It lost two windows that are scoreable officially (HLBWSD08
> recovery, r 0.40 → 0.12; HLBWSL24 recovery, 0.68 → 0.12), and HLBSSD15's recovery read r 0.14. The gate was then
> changed to stage 1's own gate minus one clause, which is identical to official staging on mice with working EMG. The
> change was driven by those validation failures, but it was made **after** the first run's S-SD results had been seen.
> Both runs are kept on e10 (`staged-eegmask/`, `staged-stage1/`).

## Validation: does the new measure agree where the EMG already worked?

Sleep vs wake, per epoch, on epochs scored by both.

| reference | windows | κ median | κ minimum | wake %, new − reference |
|---|---|---|---|---|
| notched stage 3 (validated 10-02) | 33 | **0.95** | 0.89 | +1.8 points |
| official stage 3 | 21 | 0.88 | 0.11 (HLBWSL25 recovery) | +2.8 points |

The official minimum is a window whose official staging is itself mains-corrupted: the notch moved it, and the new measure
agrees with the notch.

## Results

### Who is in

| batch | baseline | recovery | paired |
|---|---|---|---|
| W-SD (water, CSD) | 3 | 1 | HLBWSD08 |
| **S-SD (SOD1, CSD)** | **2** (HLBSSD15, 18) | **1** | **HLBSSD15** |
| W-SL (water, ad lib) | 7 | 3 | HLBWSL23, 24, 26 |
| S-SL (SOD1, ad lib) | 6 | 2 | HLBSSL33, 39 |

HLBSSL31, 32, 34, 35, 38 and 40 at the S-SL recovery, and HLBWSL22, 25, 27 and 29 at the W-SL recovery, are scoreable by the
new staging. They stay out because rung 2 cannot judge their EEG (contaminated or ungrounded chip floor).

### HLBSSD15, the checks that can fail

| check | baseline (08-25) | recovery (09-02 13:00 → 09-03 09:00) |
|---|---|---|
| r@1min (shuffled) | 0.497 (−0.007) | 0.431 (−0.008) |
| wake: light vs dark | 24.6 % < 49.6 % ✓ | 22.1 % < 35.5 % ✓ |
| REM entered from NREM (null) | 77.6 % (61.3 ± 1.6) ✓ | 85.5 % (65.8 ± 1.9) ✓ |
| informative physiology | pass | pass |
| hours scored | 20.9 of 24 | 12.9 of 20 (5.2 light, 7.7 dark) |

### Change after CSD, 13:00 → 09:00, sleep % (NREM + REM)

| mouse | arm | baseline | recovery | change | light ZT4–12 | dark ZT12–24 |
|---|---|---|---|---|---|---|
| **HLBSSD15** | SOD1 + CSD | 63.3 | 69.9 | **+6.6** | −1.0 | +14.1 |
| **HLBWSD08** | water + CSD | 43.7 | 59.8 | **+16.1** | +6.6 | +20.3 |
| HLBSSL33 | SOD1 ad lib | 45.5 | 51.3 | +5.8 | +4.2 | +6.8 |
| HLBSSL39 | SOD1 ad lib | 50.2 | 52.6 | +2.4 | −5.0 | +7.2 |
| HLBWSL23 | water ad lib | 49.9 | 55.6 | +5.7 | +6.8 | +5.0 |
| HLBWSL24 | water ad lib | 50.1 | 50.6 | +0.5 | +5.2 | −2.7 |
| HLBWSL26 | water ad lib | 57.7 | 50.9 | −6.8 | −5.0 | −7.1 |

- CSD effect in water (W-SD − W-SL): **+16.3** points. In SOD1 (S-SD − S-SL): **+2.5**.
- Interaction: **−13.8** points (light −4.8, dark −14.9). One mouse per SD arm, so no test is possible.
- Level after CSD: HLBSSD15 69.9 % against HLBWSD08 59.8 %. The SOD1 mouse slept *more* after CSD in absolute terms, and
  gained less.

### SOD1 vs water without deprivation (baselines, about a week on treatment)

| | n SOD1 / water | SOD1 | water | difference | p (exact) | Welch 95 % CI | g |
|---|---|---|---|---|---|---|---|
| 24 h | 8 / 10 | 55.7 | 53.4 | +2.3 | 0.34 | −2.6 to +7.1 | 0.44 |
| light ZT0–12 | 8 / 10 | 74.1 | 73.7 | +0.4 | 0.85 | −4.0 to +4.8 | 0.09 |
| dark ZT12–24 | 8 / 10 | 36.9 | 33.0 | +3.9 | 0.26 | −3.6 to +11.4 | 0.53 |

The same answer as the notch-only analysis (+2.5 points, p = 0.24).

### Every other measure, descriptive only (Andrea: "forget statistics, is there any effect on anything")

`qc/emg_rescue_2026_10_06.py measures`. "NREM rel. delta" is 1–4 Hz power as a share of 0.5–30 Hz, measured in NREM
epochs, so changes in electrode gain between recordings cancel out.

| baseline, no CSD | sleep % | NREM % | NREM bout | NREM bouts/h | NREM rel. delta |
|---|---|---|---|---|---|
| SOD1, n = 8 | 55.7 | 50.3 | 3.26 min | 9.5 | 0.315 |
| water, n = 10 | 53.4 | 47.7 | 2.71 min | 10.7 | 0.296 |
| S-SL vs W-SL (recorded 2 days apart) | | 50.1 vs 49.2 | 3.34 vs 2.73 | 9.2 vs 11.0 | 0.319 vs 0.295 |
| S-SD vs W-SD | | 51.0 vs 44.3 | 3.02 vs 2.64 | 10.1 vs 10.2 | 0.304 vs 0.299 |

| change, recovery − baseline | sleep, 13:00–09:00 | sleep, first 4 h | NREM bouts/h | wake bout | NREM rel. delta (R/B) |
|---|---|---|---|---|---|
| HLBSSD15, SOD1 + CSD | +6.6 | −0.2 | +0.8 | −0.26 min | ×0.93 |
| HLBWSD08, water + CSD | +16.1 | +10.3 | +3.4 | −1.51 min | ×0.86 |
| ad lib, 5 mice | −6.8 to +5.8 | −9.7 to +14.8 | −2.6 to +3.0 | −2.74 to +1.56 | ×0.93 to ×1.30 |

What the numbers show:
- **Sleep amount and NREM amount without CSD:** nothing beyond the spread between mice.
- **The rebound after CSD:** the water mouse's +16.1 lies clearly outside the ad libitum range; the SOD1 mouse's +6.6 sits
  at its edge, with no gain in the first 4 h. A smaller rebound under SOD1 is one reading. HLBSSD15's highest baseline of
  all is the other.
- **NREM slow-wave power:** neither deprived mouse shows a delta rebound (×0.86 and ×0.93; ×0.92 and ×0.91 in the first
  4 h). Repeated restriction is reported to blunt the delta rebound in rodents, and these recoveries follow 7 days of it.
  So there is no SWA response to compare between arms.
- **NREM consolidation:** at baseline, SOD1 mice have ~15–20 % longer and fewer NREM bouts, with the same NREM amount, in
  both batch pairs. The ranges overlap. A hint, not a finding.
- **REM:** cannot be assessed. Stage 3 makes REM a fixed top fraction of sleep (≈ 10 % in every mouse), so no effect
  can appear in it. A REM answer needs human scoring or a validated REM detector.

### Maximum rescue of both deprivation batches (Andrea: "try everything … on those EEG/EMG that are not clearly railing")

`extract-sd`, `stage-max`, `analyse-max`. All 32 W-SD and S-SD mouse-windows are run, every position, after the W-SD
recovery was also re-split with `--all-verdicts`. Only railing or flat epochs are excluded. There are two gates (stage 1's
gate minus its EMG-mains clause; a no-rail gate with no mains clause at all) and five EMG filters, each with its own
shuffle control. Per window, the first passing filter is taken, in a fixed order.

| EMG filter | κ vs notched staging (windows) | used? |
|---|---|---|
| gap67, 67–470 Hz | 0.95 (6) | yes |
| gap10, 10–470 Hz | 0.96 (6) | yes |
| gaplow, 10–113 Hz minus harmonics | 0.98 (33) | yes |
| gaphigh, 127–470 Hz | 0.95 (33) | yes |
| floor67, minus the chip's wire-free inputs | **0.26** (6) | **no**: it destroys the state signal on good EMGs |

Shuffle controls: 320 of 320 REJECT. **Nothing new is rescued.** Scoreable windows:

| | baseline | recovery | paired |
|---|---|---|---|
| S-SD | HLBSSD11*, 15, 18 | 15 | **HLBSSD15** |
| W-SD | HLBWSD01, 02, 08 | 08 | **HLBWSD08** |

\* HLBSSD11's baseline EEG is **not** intermittent. Rung 2 calls it so (longest block 6 min) only because its chip's
wire-free floor carried signal that day. The slope threshold was −1.52, against −0.76 to −0.97 on the other chips. A
healthy EEG with a median slope of −1.35 then passes in NREM (81 % of epochs) and fails in wake (2 %, wake defined by
the EMG). It is a milder form of the contaminated floor, below the −1.90 cut that would have made it UNJUDGEABLE. The
baseline counts; its recovery EMG has no state signal, so it stays unpaired.

Why the rest stay out:
- **W-SD recovery:** A1, A2 and B1 have flat (DEAD) EEG and B2 and C1 have OPEN EEG after the deprivation week, so they
  give 0 h. C2 reaches r 0.23 at best, and D1 0.03.
- **S-SD recovery:** HLBSSD16 reaches r 0.14 at best, HLBSSD14 0.11, the rest ≤ 0.05 under every filter and gate. Those
  EMGs carry no sleep/wake signal at any frequency.
- **HLBWSD03 baseline:** r 0.41–0.63, but it fails the informative physiology check (NREM is not the largest-amplitude
  state) under every filter. That is an EEG problem, which no EMG processing fixes.

The comparison does not move: HLBSSD15 +6.3 and HLBWSD08 +16.2 points over 13:00–09:00; −0.2 and +10.4 in the first
4 h; NREM relative delta ×0.93 and ×0.86. **One mouse per deprivation arm is the most these recordings can give.**

## Limitations

- **One mouse per deprivation arm.** HLBSSD15 against HLBWSD08 is a comparison of two animals.
- **Baseline imbalance.** HLBSSD15 slept the most of all 18 scoreable baselines (63.3 % of 13:00–09:00, dark 50.4 %). A high
  baseline leaves less room to rebound.
- **Coverage.** Only 12.9 of the 20 h of HLBSSD15's recovery are scored. If the gaps fall on one state, its percentage is biased.
- **What the rescued signal is.** It is what remains between the harmonics of a lead whose 10–113 Hz is all mains. It
  behaves like EMG on every check that can fail: persistence, dark > light wake, REM order, physiology. It may still be
  partly cable-movement artefact rather than muscle tone. Nobody has looked at the trace yet.
- **No human scoring**, as for every staging result in this project.

> [!quote] Paper-ready
> To recover EMG channels dominated by mains interference, EMG power was computed from the raw 1000 Hz signal only in
> frequency bands lying between the 60 Hz harmonics (67–470 Hz). On animals with intact EMG this measure reproduced
> conventional staging (Cohen's κ, median 0.95, minimum 0.89, 33 recordings). It allowed one SOD1-treated, sleep-deprived
> animal to be scored at both timepoints.

## Next

1. **A 10-minute look at HLBSSD15's recovery EMG** (Andrea). Pick one long wake bout and one long NREM bout in the
   hypnogram, then view 67–470 Hz with the notch on. Muscle tone should be visibly higher in wake.
2. **Adopting the gap measure, or the notch,** is the same pending decision as on 10-02. It needs pre-registration, the
   falsification suite and a re-score.

## Files

- Script: `eeg-emg-analysis/qc/emg_rescue_2026_10_06.py` (`extract` and `stage` on e10, `analyse` anywhere; runs its own
  mains-leakage self-check on start).
- Per-mouse table, every window, with the inclusion flag: [[2026-10-06-S-SD-EMG-rescue-per-mouse.tsv]].
- On e10: `~/eeg-ssd-allverdicts-2026-10-06/` (9.7 GB, all regenerable). It holds `whole/` and `windows/` (the stage-2
  all-verdicts splits), `emg/` (per-epoch band powers), `staged-stage1/` and `staged-eegmask/` (stage-3 outputs), and logs.

## Related

[[2026-10-06-SOD1-sleep-EEG-2x2-quick-compute]] · [[2026-10-02-noise-series-4mice-24h-analysis]] (the notch) ·
[[2026-09-02-S-SD-recovery-sleep]] · [[2026-09-30-scoreable-mice-on-the-24h-windows]] · [[_hlb-sod1-hub]]
