---
tags: [experiment, eeg, staging, hypnogram, circadian, pre-registration]
created: 2026-08-07
status: active
---

# Pre-registration: sleep staging of the two working animals

> [!abstract] TL;DR
> Written **before** stage 3 was run, so the caveats cannot be invented afterwards to explain an
> awkward number. Both animals that produced clean data have a specific reason to sleep abnormally
> on this particular recording. If they read as unusually awake, **that is the expected result and
> is not evidence of a data problem.**

Data: `/home/skimlab/eeg-processed/2026-08-06/`, recording `allego_1__uid0806-16-57-38`,
23.66 h, full light and dark cycle. Quality: [[2026-08-07-overnight-recording-two-animals-work]].

## 1. What is being run

```bash
python3 stage3_features.py /home/skimlab/eeg-processed/2026-08-06
```

Canonical stage 3. **WAKE** by Otsu split of log EMG rms computed **per animal**, then NREM and REM
by theta/delta. Persistence is computed **within unbroken contact blocks only**, which is the fix
for the 2026-08-03 bug that produced both the project's largest false positive (+0.854 on 39 min of
pure wake) and a false negative (+0.078 on data that could not have failed).

The six OPEN animals are expected to reject themselves. **B1 and D2 are the two to report.**

## 2. 🔴 The two confounds, registered before looking

| animal | confound | why it matters |
| --- | --- | --- |
| **B1** | **tethered for the first time that morning** | this recording is its first day on the tether |
| **D2** | **under isoflurane about 40 minutes before the recording started** | early hours are post-anaesthesia |

> [!danger] The precedent that makes this a real risk
> On 2026-06-29, animal D1 produced **technically flawless data** — 9 µV hum, 100% gate pass — and
> was **95% awake**. That was explained as first-tethering acclimatisation, not an artefact. B1 is
> in exactly that situation now.

**Therefore:** an unusually high wake fraction in either animal is **uninformative about data
quality**. It must not be used to question the recording, and the recording must not be used to
claim normal sleep architecture.

**Planned sensitivity check:** if either animal reads as heavily awake, re-examine the **second
half** of the recording separately, by which point acclimatisation and anaesthesia have both had
more than 12 h to wash out. Registered now so it is not a post-hoc rescue.

## 3. Circadian comparison, framed narrowly

Stage 3 emits the ZT split automatically. ZT was verified correct on B1's file: **ZT 7.96 → 7.62,
`is_light` 0.493**, so a full cycle is covered and the UTC versus local trap was handled.

Literature norm, C57BL/6: **~70% asleep in the light phase, NREM 62.0 ± 7.8 %/12 h.**

This is normally a **threshold-independent** validation, because nothing in the QC gate or the
persistence statistic knows about the clock. ⚠️ **This time it is not a clean validation**, because
of §2. The point of running it now is to have the machinery working and the caveats on record for
the next cohort.

## 4. 🛑 What may not be reported, whatever comes out

- **No REM share, ever.** It is fixed by construction: REM is defined as the top 20% of theta/delta
  among non-wake epochs, so its percentage is an artefact of the rule. The field is even named
  `rem_pct_CONSTRUCTED`. Report **WAKE versus NREM**, and REM's **order** — entered from NREM,
  expect >70%.
- **Never subtract EEG from EMG.** The RHD2216 is bipolar and already subtracted before the ADC.
- **No claim about sleep architecture as biology.** This is a rig validation recording, from a
  cohort where six of eight animals produce nothing.

## 5. Results

**Three scoreable animal-recordings.** Before today the project had two, both from 31 July.

| | **B1 overnight** | **D2 overnight** | B1 afternoon |
| --- | --- | --- | --- |
| verdict | **SCOREABLE** | **SCOREABLE** | **SCOREABLE** |
| usable in blocks | **23.66 h in 1 block** | 23.28 h in 9 blocks, longest 576.4 min | 3.18 h in 1 block |
| WAKE / NREM | 46.1% / 46.8% | 41.7% / 46.8% | 24.4% / 65.0% |
| **persistence r@1min** | **0.603** (shuffled 0.01) | 0.499 (shuffled −0.001) | 0.481 |
| r@5min / r@10min | 0.463 / 0.425 | 0.234 / 0.146 | — |
| **REM entered from NREM** | **73.9%** | **79.5%** | 79.6% |
| **physiology** | **5/5 PASS** | **5/5 PASS** | PASS |

Calibration for the persistence statistic: pure noise gives −0.035, genuine 4 min bouts give +0.510.
**Both animals are above the 4 min bout calibration.** For scale, C1 on 31 July, the project's
previous best, gave **r@1min 0.744**.

All five physiology checks pass on both animals: wake has the highest EMG, NREM has the most delta,
NREM has the largest amplitude, REM has the highest theta/delta, REM has low EMG.

### ⭐ The circadian check, which is the strongest part

| animal | light phase | dark phase | **asleep in light** | literature ~70% |
| --- | --- | --- | --- | --- |
| **B1** | WAKE 17.9% | WAKE 73.5% | **82.1%** | consistent |
| **D2** | WAKE 29.7% | WAKE 53.1% | **70.3%** | consistent |
| B1 afternoon (light only) | WAKE 24.4% | no data | 75.6% | consistent |

**D2 lands at 70.3% against a literature value of about 70%.** Both animals show the light/dark
contrast in the correct direction, B1 very strongly.

Nothing in the QC gate, the staging rule or the persistence statistic knows about the clock, so
this remains **external evidence** even with the caveats of §2.

### 🔴 Honest note on the pre-registered confounds

**They did not materialise, and I am recording that rather than quietly dropping it.** §2 predicted
that B1, tethered for the first time that morning, might read as unusually **awake**, following the
2026-06-29 precedent of 95% wake on flawless data.

The opposite happened: B1 slept **more** than the literature figure in the light phase, 82.1%
against about 70%. So the registered risk was real and worth stating in advance, and it simply did
not occur. The planned sensitivity analysis on the second half of the recording is **not needed**
and was not run.

⚠️ B1's 82.1% is above the literature mean. Sleeping more than normal is itself consistent with
recent tethering or mild stress, so **do not read B1's figure as a demonstration of normal
architecture**. D2's 70.3% is the cleaner number of the two.

### 🛑 REM, as registered

Both animals' cross-check confirms REM is not separable with this montage: the percentile rule
forces roughly 7 to 11%, while an independent Otsu cut on theta/delta gives **41.6% and 41.3% of
sleep**, against a literature value below 10%. Both land far from it, so neither is a measurement.
**Only WAKE versus NREM and the REM-from-NREM order are reported**, and both animals clear the
>70% expectation on the latter.

## 6. What this establishes

The **analysis pipeline works end to end**, on data from the current rig, and agrees with external
biology it was never tuned against. Combined with the quality result, the rig now produces
**scoreable sleep data from two animals simultaneously**, which is what the whole project needs.
