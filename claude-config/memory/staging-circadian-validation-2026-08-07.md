---
name: staging-circadian-validation-2026-08-07
description: "2026-08-07 — stage 3 gave THREE scoreable recordings and the circadian check passed (D2 70.3% asleep in light vs literature ~70%), validating the whole analysis chain"
metadata:
  type: project
---

> 🔴 **STALE, 2026-10-22: the headline of this file is OVERTURNED.** "Circadian check PASSED, validates the whole analysis chain" is wrong as stated: an Otsu +-25 % sweep moves D2's asleep-in-light from 23.0 % to 88.9 %, so the check is NOT threshold-independent, and 4 of the 5 "physiology PASS" checks are forced by the staging rule and cannot fail (council review 2026-08-08). Only the REM-from-NREM order property survived (72.4 % vs null 56.6 %). Read [[2026-08-07-staging-preregistration]] (corrected banner) and [[2026-08-07-council-review-of-the-analysis-pipeline]] instead, and always quote the threshold swing beside any asleep-in-light number. Per-animal forensics live in [[per-animal-failure-signatures]]. Deletion proposed.

**Pre-registration + results:** vault `10-projects/rig-bringup/2026-08-07-staging-preregistration.md`.
⭐⭐⭐ **THE SYNTHESIS PAGE TO ARGUE FROM: `20-areas/eeg-analysis/2026-08-07-rig-specification-and-analysis-method.md`**
— established claims with evidence-strength ratings, the rig spec, the analysis method, what may not
be claimed. Professor update = **PART 0b** of `30-resources/meetings/2026-08-06-rig-status-for-professor.md`.

⭐⭐⭐ **THREE SCOREABLE ANIMAL-RECORDINGS** (project had two before, both 31 July). Ran
`stage3_features.py /home/skimlab/eeg-processed/2026-08-06`.

| | B1 overnight | D2 overnight | B1 afternoon |
| --- | --- | --- | --- |
| blocks | **23.66 h in 1** | 23.28 h in 9, longest 576.4 min | 3.18 h in 1 |
| WAKE / NREM | 46.1 / 46.8 | 41.7 / 46.8 | 24.4 / 65.0 |
| r@1min | **0.603** | 0.499 | 0.481 |
| REM from NREM | 73.9% | 79.5% | 79.6% |
| physiology | **5/5 PASS** | **5/5 PASS** | PASS |

Calibration: noise −0.035, real 4-min bouts +0.510 ⇒ **both above the bout calibration**. C1
(31 July, previous best) was 0.744.

⭐⭐ **CIRCADIAN CHECK PASSED — the strongest result.** Asleep in the light phase: **D2 70.3%**,
**B1 82.1%**, literature C57BL/6 ≈ **70%**. Dark phase far more awake (B1 WAKE 73.5%, D2 53.1%).
**Nothing in the QC gate, staging rule or persistence statistic knows the clock ⇒ external
validation of the whole chain.** ZT verified correct (B1 ZT 7.96→7.62, is_light 0.493).

🔴 **THE PRE-REGISTERED CONFOUNDS DID NOT MATERIALISE — recorded, not dropped.** I predicted B1
(tethered that morning) might read unusually AWAKE, per the 2026-06-29 precedent of 95% wake on
flawless data. **The opposite happened: B1 slept MORE than the literature mean.** The registered
sensitivity analysis (second half only) was therefore **not needed and not run**.
⚠️ **B1's 82.1% is ABOVE the mean ⇒ do NOT quote it as normal architecture** (consistent with recent
tethering). **D2's 70.3% is the cleaner number.**

🛑 **REM still unseparable, as always**: percentile rule 7-11%, independent Otsu cut **41.6% and
41.3% of sleep**, literature <10%. **Report WAKE vs NREM + REM order only.**

🔴⭐ **SCOPE: this is the OLD EEG+EMG cohort. It was REPLACED the same evening by 7 EEG+EMG+ECG mice**
([[ecg-cohort-2026-08-07]], [[ecg-cohort-ground-miswired]]). The synthesis page carries a scope
banner and its **channel map + floor-control list were corrected for the ECG cohort**
(`/1` EEG `/2` EMG `/3` ECG; floor is now **`/4`-`/16`, `/36`-`/48`**). Added there too:
**0.5 MΩ is NOT an absolute contact measure** (it calls the best-ever channel open), **zero flips =
wiring-error signature**, the **phase column** interpretation, and **low hum is no longer a contact
proxy**. Parts 1 and 3's principles are unaffected.

📌 Deferred (needs the OLD cohort back, which will not happen — they were replaced): new tether chain for the other five
animals · Part B interference test · restore cameras (blocks C1's ambiguous EMG and video-EEG sync).
✅ **STAGE 4 DONE — the standard-mouse pipeline is COMPLETE end to end**: 16 `.edf` + per-file
`_SCORER-README.txt` in `/home/skimlab/eeg-processed/2026-08-06/`, deliberately **without automatic
labels so scoring is blind**. `by-mouse/<name>/` now carries all 13 artefacts per animal.
⭐ **PER-ANIMAL FORENSICS on the six failures: `20-areas/eeg-rig/per-animal-failure-signatures.md`**,
script `qc/per_animal_forensics.py`. **C2 = chewed tether CONFIRMED** (both channels intermediate hum,
*quieter than the floor*, ~0% railing). **C1's EMG is genuinely connected (hum 75.9 µV)** = best
salvage. **D1 r=0.74 and B2 r=0.50 between their OWN two channels = ONE shared-path fault each**
(working animals sit at 0.07-0.08). ⇒ **five of six failures point at the tether chain, not implants.**
🛑 **Spectral slope judges EEG, NOT EMG** (real EMG is broadband ⇒ flat is expected).
⚠️ **The wire-free floor is NOT the quietest thing on the rig** (hum 2276 µV) — a damaged tether can
read quieter than the floor and still carry nothing.

See also [[overnight-two-animals-tether-is-the-fix]], [[light-schedule-and-circadian-validation]],
[[eeg-analysis-pipeline]].


## From the memory index, trimmed there 2026-10-06 (kept here verbatim)

- ⭐⭐ **[3 SCOREABLE RECORDINGS + CIRCADIAN CHECK](staging-circadian-validation-2026-08-07.md).** ⚠️ SUPERSEDED as circadian evidence by [[a2-control-48h-reference-profile]].
