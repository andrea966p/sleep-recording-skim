---
type: experiment
area: hlb-sod1
status: active
created: 2026-11-02
summary: "Tissue assays of the four EEG cohorts (W-SD, S-SD, W-SL, S-SL) re-derived from the raw ODs: hippocampal total SOD unchanged by SOD1; hippocampal MDA higher in the SD cohorts, no SOD1 effect; heart SOD crossover (interaction p < 0.001) that is a cohort pattern and fragile to normalisation; group = cohort, so none of it is causal; data-entry questions for Andrea"
tags: [hlb, sod1, tissue, sod, mda, statistics]
---

# 2026-11-02: EEG cohorts, tissue SOD activity and MDA, reanalysed from the raw ODs

> [!abstract] TL;DR
> **Question.** What do the heart and hippocampus SOD and hippocampus MDA assays of the four EEG cohorts
> show, and does the lab's interpretation (`HLB_biochemical_assay.pdf`) hold up?
> **Answer.**
> - **Hippocampal SOD activity: no SOD1 effect** (SOD1 − water within ±5 %, CIs include 0). The
>   SD-vs-normal-sleep difference (p ≈ 0.01-0.02) is **not interpretable**: the SD cohorts ran on one plate and
>   the normal-sleep cohorts on the other, and no tissue mass was recorded.
> - **Hippocampal MDA: higher in the two SD cohorts** (+15 % water, +28 % SOD1; sleep main effect p = 0.007),
>   **no SOD1 effect** (p = 0.81). The figure's star for vehicle CSD vs NSL does not reproduce (Šidák p = 0.26).
> - **Heart SOD activity: a crossover.** Water: SD cohort 15 % above normal sleep. SOD1: SD cohort 10 % below
>   normal sleep, and SOD1 normal-sleep 11 % above water normal-sleep. Interaction p < 0.001, robust to the
>   curve method, but weaker per mg tissue (p = 0.005) and the simple effects flip across 0.05 with single mice.
> - **Group = cohort.** Each group is one cohort with its own surgery, sampling date, dissection and freezer
>   time, so every contrast is a cohort difference. Nothing here is causal for SOD1 or for sleep.
> - **The sheet's SOD calculation does not follow the kit** (linear fit on OD instead of the linearized rate, no
>   ×23 well factor): absolute values are 11-17x too low. Group conclusions barely change.
> - **The test that would answer the question:** the same assays on the nanotag cohorts (HLBNSL, NS-SD), where
>   SOD1 and water mice share a cohort, on one plate with interleaved samples.

> [!note] 2026-11-02, later: answers from Andrea and the kit manuals
> - **Kit manuals checked** (Cayman 706002, Abcam ab118970, copies in `nanotag/analysis/tissue/raw/`). The
>   Cayman values in the results table follow the manual exactly: blank-corrected standards, LR = CSV(std A) /
>   CSV(std), sample LR = CSV(std A) / (sample − sample background), × 0.23/0.01 × dilution. No blank wells were
>   recorded, so the mean sample-background well stands in for the blank.
> - **Buffer was fixed per mg of tissue for heart and hippocampus.** So the heart volumes of mice 6 (3.70 mL) and
>   24 (4.04 mL) are entry errors, and U/mL is proportional to U/mg for every mouse. The heart result is the U/mL
>   row (interaction p = 0.0006); the U/mg row and "weaker per mg tissue" in the TL;DR came only from those two
>   entries and are withdrawn.
> - **Freezer time does not matter** (−80 °C deep freezer, Andrea): dropped as a confound. Sampling date stays as
>   part of the cohort difference.
> - Hippocampal SOD mice 36 and 37 were left out because the plate was full. The MDA S-SL ID mismatch is
>   unresolved and changes no group result. Coating and isoform of the powder are unknown (ask HLB).
> - **HLBNSL and NS-SD tissue is all stored at −80 °C**, so the recommended within-cohort assays need no new mice.

## Data
- Raw files from Andrea, 2026-11-02, copied to `nanotag/analysis/tissue/raw/`: `SOD1-biochem_raw_data.xlsx`
  (sheets `0922 Hippocampus`, `SOD1-Heart`, `MDA-Hippo`), `HLB_biochemical_assay.pdf` (figures and
  discussion), `HLB_biochem_assay_protocol.docx`, `HLB_ROS_product.pdf` (kits).
- Kits: total SOD, Cayman 706002 (xanthine oxidase, tetrazolium; measures Cu/Zn-, Mn- and Fe-SOD together, so
  **"SOD1 activity" is the wrong name: it is total SOD activity**); MDA, Abcam ab118970 (TBA reaction).
- Mice: the EEG cohorts W-SD (HLBWSD), S-SD (HLBSSD), W-SL (HLBWSL), S-SL (HLBSSL), mouse numbers = the sheet's.
  About 2 weeks on SOD1 or water, then 7-8 days of 4 h/day SD (09:00-13:00) or normal sleep
  ([[hlb-sod1-design]]). SD mice were sampled after about 22-24 h of recovery: W-SD 2026-08-28 about 11:00
  ([[2026-08-28-W-SD-cohort-closeout]]), S-SD 2026-09-03 13:00 ([[2026-09-02-S-SD-recovery-sleep]]);
  W-SL about 09-18, S-SL 09-22.
- n: hippocampal SOD 9 / 9 / 9 / 8 (W-SD / S-SD / W-SL / S-SL); heart SOD 6 per group; MDA 6 / 5 / 6 / 6.
- Code: `nanotag/analysis/tissue/sod_mda_reanalysis.py` and `prism_sidak.py` (mine), `cayman_extract.py` +
  `cayman_analyse.py` (an independent reanalysis by a second agent; output `results_2026-11-02.txt`).

## Checks on the calculation
- **Sheet reproduced** to 4 decimals: SOD = linear fit of standard OD (not blank-subtracted) on U/mL, sample OD
  minus its own background well, × 50 dilution. MDA = (OD − intercept)/slope of a linear fit, R² 0.987.
- **Not the kit's method.** Cayman uses the linearized rate LR = A0/A against U/mL, then × (0.23/0.01) × dilution.
  Linear on OD fits poorly (R² 0.89 heart, 0.95 hippocampus; LR 0.97-0.997), and the ×23 factor is missing, so
  absolute U/mL are 11-17x too low. Group inference is unchanged across five curve variants, except the heart
  SOD1-vs-water normal-sleep contrast (Šidák 0.046 sheet, 0.060 LR, 0.058 4PL).
- **Duplicates:** CV median 1-5 %, max 10 %. A small systematic first-well > second-well offset in some groups
  (heart S-SD 6/6, p = 0.001), each group in its own block of wells, so plate position is confounded with group.
- **Plates:** hippocampal SOD on two plates, plate 1 = W-SD + S-SD, plate 2 = W-SL + S-SL. Heart SOD and MDA
  on one plate each.

## Results
Mean (n); Cayman LR for SOD. Type III two-way ANOVA (unbalanced n), Šidák as Prism "compare within rows" (k = 2),
Hedges g; permutation tests agree.

| Assay | W-SD | S-SD | W-SL | S-SL | p SOD1 / sleep / interaction | SOD1 − water, SD | SOD1 − water, normal sleep |
|---|---|---|---|---|---|---|---|
| Hippocampal SOD (U/mL homogenate) | 29.6 (9) | 30.7 (9) | 28.0 (9) | 25.8 (8) | 0.66 / 0.019 (= plate) / 0.21 | +1.1 [−2.6, 4.8], p 0.80 | −2.3 [−6.1, 1.6], p 0.42 |
| Heart SOD (U/mL homogenate) | 30.0 (6) | 21.7 (6) | 21.6 (6) | 27.2 (6) | 0.45 / 0.40 / **0.0006** | −8.2 [−13.3, −3.2], p 0.005 | +5.6 [0.6, 10.6], p 0.060 |
| Heart SOD (U/mg wet tissue) | 0.563 | 0.435 | 0.421 | 0.540 | 0.90 / 0.64 / **0.0045** | −0.13, p 0.057 | +0.12, p 0.082 |
| Hippocampal MDA (nmol/well, ∝ nmol/mg) | 1.69 (6) | 1.80 (5) | 1.47 (6) | 1.41 (6) | 0.81 / **0.007** / 0.39 | +0.11 [−0.19, 0.42], p 0.69 | −0.06 [−0.36, 0.23], p 0.88 |

Sleep within each drink (MDA, Šidák k = 2): water SD − SL +0.22, p 0.26; SOD1 SD − SL +0.39, p 0.030.
Heart, water SD − SL +15 %, p 0.006.

- **Outliers without an independent reason to exclude** (report with and without): hippocampal SOD W-SL 27
  (studentised residual 3.4; without it the SOD1 − water normal-sleep gap shrinks to −0.9); MDA S-SD 15
  (3.1; without it the SD contrast is −0.03, the sleep main effect stays p = 0.015).
- **No within-mouse links:** hippocampal SOD vs MDA ρ 0.18, hippocampal vs heart SOD ρ −0.16 (n 23-24).

## What the lab's interpretation gets right and wrong
- ✅ Hippocampus shows no SOD1 effect on SOD activity or MDA.
- ✅ Native SOD reaches the brain poorly; the literature supports this for SOD given into the blood (PEG and
  nanoparticle formulations exist because native SOD does not cross). But for an oral product the first barrier
  is the gut: unprotected oral SOD is digested: plain melon SOD left blood and liver enzymes unchanged, while the gliadin-combined form raised
  them (Vouldoukis et al. 2004), and the positive Bacillus study used a formulated Mn-SOD (Yoon et al. 2023). So "no hippocampal effect" is expected before the BBB is
  reached. Write the BBB as one of two reasons, not the explanation.
- ❌ "Total superoxide dismutase 1 (SOD1) activity": the kit measures total SOD.
- ❌ "Hippocampal SOD unaffected by sleep condition": the ANOVA gives a sleep effect (p ≈ 0.01-0.02). It is not
  interpretable because it equals the plate, which is the honest statement.
- ❌ MDA: "CSD significantly increased hippocampal MDA" holds only as a main effect over two SD cohorts against
  two normal-sleep cohorts. Within water it is not significant. It is also cohort-confounded: the SD cohorts
  were sampled 3-4 weeks earlier (longer freezer time) and W-SD hippocampi weigh twice the others (16 vs 8-10 mg,
  p = 0.019), which suggests a different dissection.
- ⚠️ Heart: "compensatory up-regulation in vehicle CSD, absent with SOD1" is one reading. The pattern is a
  crossover of four cohort means, which a cohort effect explains equally well. Even taken at face value, a lower
  SD-cohort SOD with SOD1 fits "less oxidative burden" and "blunted adaptive response" equally (antioxidants blunt
  exercise-induced antioxidant-enzyme expression: Ristow et al. 2009; Gomez-Cabrera et al. 2008), and without a
  heart damage marker the two cannot be told apart. The SOD1 normal-sleep cohort above water matches oral melon
  SOD raising cardiac SOD by 30-40 % in hypertensive rats (Carillon et al. 2014), but that was a different
  product, species and route.
- ⚠️ The SD mice were sampled after 22-24 h of recovery, so "CSD" here means what is left a day after the last
  bout, not the deprived state. Rodent studies with gentle handling often find no lipid peroxidation at all
  (Gopalakrishnan et al. 2004; systematic review Villafuerte et al. 2015), so an MDA rise after recovery would be
  unusual and needs replication within one cohort.

## Questions for Andrea (data entry)
1. Heart buffer: mouse 6 (W-SD) is 3.70 mL for 285 mg (13 µL/mg) and mouse 24 (W-SL) 4.04 mL for 247 mg
   (16 µL/mg); every other mouse is 20 µL/mg. Typos for 5.70 and 4.94? The per-mg results depend on it.
2. Hippocampal SOD: was the homogenisation ratio fixed (mL per mg)? No tissue mass is in the sheet.
3. MDA S-SL: the tissue table lists 31, 33, 34, 35, 38, 39, the OD table 31, 32, 33, 34, 35, 38. Which is right?
   S-SD mouse 11 was weighed but has no OD.
4. Hippocampal SOD: why are 36 and 37 missing (5 was sacrificed early)?
5. Assay dates for heart SOD and MDA (freezer time per cohort), and who ran them.
6. Is the HLB product coated or plain, and is it Cu/Zn-SOD (SOD1) or a Mn-SOD? The Bacillus product in the
   literature (Yoon et al. 2023) is a Mn-SOD.
7. Is tissue from HLBNSL (sampled 10-02) and NS-SD (11-04) stored for the same assays?

## Still open
- [x] Answers to the questions above (2026-11-02, callout under the TL;DR); per-mg heart = U/mL row.
- [ ] Ask HLB: coating and isoform of the powder.
- [ ] Recompute and re-plot the figures with the Cayman method and "total SOD" labels.
- [ ] Liver SOD; heart MDA (the marker that separates the two heart readings).
- [ ] Heart SOD and MDA on HLBNSL + NS-SD, one plate, interleaved, blind codes, protein (BCA) normalisation.

## References (retrieved from PubMed: abstract unless stated)
- Carillon J, et al. Endogenous antioxidant defense induction by melon superoxide dismutase reduces cardiac
  hypertrophy in spontaneously hypertensive rats. Int J Food Sci Nutr 2014;65:602-9. doi:10.3109/09637486.2014.893286
- Gomez-Cabrera MC, et al. Oral administration of vitamin C decreases muscle mitochondrial biogenesis and hampers
  training-induced adaptations in endurance performance. Am J Clin Nutr 2008;87:142-9. doi:10.1093/ajcn/87.1.142
- Gopalakrishnan A, Ji LL, Cirelli C. Sleep deprivation and cellular responses to oxidative stress. Sleep
  2004;27:27-35. doi:10.1093/sleep/27.1.27
- Ristow M, et al. Antioxidants prevent health-promoting effects of physical exercise in humans. PNAS
  2009;106:8665-70. doi:10.1073/pnas.0903485106
- Villafuerte G, et al. Sleep deprivation and oxidative stress in animal models: a systematic review. Oxid Med Cell
  Longev 2015:234952 (full text). doi:10.1155/2015/234952
- Vouldoukis I, et al. Supplementation with gliadin-combined plant superoxide dismutase extract promotes
  antioxidant defences and protects against oxidative stress. Phytother Res 2004;18:957-62. doi:10.1002/ptr.1542
- Yoon HJ, et al. Bacillus-derived manganese superoxide dismutase relieves ocular-surface inflammation and damage by
  reducing oxidative stress and apoptosis in dry eye. Invest Ophthalmol Vis Sci 2023;64:30. doi:10.1167/iovs.64.12.30
- Methods: Lazic SE, et al. What exactly is 'N' in cell culture and animal experiments? PLoS Biol
  2018;16:e2005282. doi:10.1371/journal.pbio.2005282
