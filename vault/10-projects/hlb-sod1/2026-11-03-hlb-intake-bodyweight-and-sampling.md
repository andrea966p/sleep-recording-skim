---
type: experiment
area: hlb-sod1
status: active
created: 2026-11-03
summary: "Liquid intake, SOD1 dose and body weight of every HLB batch from the intake sheet (read only), SOD1 vs water per batch, and an inventory of all tissue sampled so far; data for section 3 of the final report draft"
tags: [hlb, sod1, intake, bodyweight, sampling, tissue]
---

# 2026-11-03: intake, SOD1 dose, body weight and the tissue inventory

> [!abstract] TL;DR
> - **Source:** Google Sheet `HLB_SOD1_Intake_Monitoring_SDSLNANO`, read only on 2026-11-03 (nothing written). CSV copies of
>   every tab used and the code: `nanotag/analysis/intake/` (`intake_summary.py`, `data/`). The CSV transcription is checked
>   against the sheet's own TOTAL rows by the script.
> - **Every SOD1 mouse drank enough.** Mean intake 3.2 to 4.1 mL/mouse/day gives 22 to 28 U/mouse/day, 108 to 138 % of the
>   20.4 U target. The lowest mouse mean is 19.2 U (94 %). Nothing suggests the solution was refused.
> - **SOD1 mice drank less volume than water mice in all four batch pairs** (0.4 to 1.7 mL/day). Part of that is probably the
>   bottle, not the solution: water mice moved to large bottles mid-batch, and the same mice read 0.5 to 2.4 mL/day higher on them
>   (below). The cleanest pair, W-SD vs S-SD (same small bottles), differs by -0.8 mL/day [-1.7, 0.0], p = 0.052.
> - **Body weight:** no detectable difference SOD1 vs water in any batch with sampling weights (CIs about ±3 % points EEG,
>   ±1.8 HLBNSL). EEG mice lost 3 to 6 % from tethering to sampling in both arms; HLBNSL mice stayed flat. Only two weights per
>   mouse exist (no daily weights), so tolerability by weight rests on those two points. NS-SD / NW-SD have no weight since
>   6 days after surgery; sampling weights come 2026-11-04.
> - **Tissue:** 54 mice sampled on 6 days so far (35 EEG, 9 HLBNSL, 10 SPF gavage). Assayed: hippocampal SOD (35 mice), heart SOD
>   (24), hippocampal MDA (23), all EEG mice. HLBNSL (9 mice, with liver) and the SPF mice (10) are stored unassayed;
>   NS-SD / NW-SD (10) are sampled 2026-11-04.

## How intake was measured, and how far per-mouse values can be trusted

- **Per mouse, not per cage.** Each mouse has its own 10 mL bottle (EEG mice are tethered one per cage; nanotag mice were
  single-housed, 2026-09-12 for HLBNSL and 2026-10-19 for NS-SD). The sheet has one In (g) and Out (g) pair per mouse per day.
- **Bottle weighing.** Consumed (mL) = In - Out on the same row, 1 g = 1 mL, 0.1 g resolution. A fresh bottle is made and
  weighed each evening (EEG after SD about 13:00; nanotag 14:00 to 17:00); the old bottle is weighed before it is removed.
  Source: sheet `README`, `Config`.
- **No spillage or evaporation control.** The sheet records no bottle without a mouse, so leaks and drips cannot be subtracted.
  A mouse that knocks or empties its bottle shows as a high value.
- **Verdict.** Per-mouse means are real measurements of how much each mouse removed from its bottle. They are good to about
  ±1 mL on a single day, which matters little against a 3 to 4 mL mean over 8 to 19 days. They are **not** exact drinking
  volumes: three artefacts decide the SOD1 vs water gap (bottle type, emptied bottles, nozzle problems), listed in the data
  problems below.
- **Dose = mL × 6.8 U/mL** (`Config!C7`; the sheet's U columns do the same). The daily preparation log divides the powder's units
  by 6.8, so the concentration is formula-driven; the actual concentration in the bottle was not measured.

## Intake and dose per batch and arm

Mean ± SD over mouse-days, all recorded full days (the sheet's own rule), min = lowest single day, n = mouse-days (mice).
Dose only for SOD1 arms. Pairs are never pooled.

| Pair | Arm | Batch | mL/mouse/day | min | n mouse-days (mice) | SOD1 dose U/mouse/day (% of 20.4) | days < 2 mL | days > 6 mL |
|---|---|---|---|---|---|---|---|---|
| EEG, SD | water | W-SD | 4.26 ± 2.25 | 0.2 | 119 (9) | | 12 | 15 |
| EEG, SD | SOD1 | S-SD | 3.44 ± 1.32 | 0.2 | 144 (9) | 23.4 ± 9.0 (115 %) | 14 | 4 |
| EEG, normal sleep | water | W-SL | 3.67 ± 1.49 | 0.0 | 144 (9) | | 18 | 4 |
| EEG, normal sleep | SOD1 | S-SL | 3.23 ± 1.16 | 0.0 | 152 (8) | 22.0 ± 7.9 (108 %) | 17 | 1 |
| Nanotag HLBNSL | water | NW-SL | 5.09 ± 1.31 | 1.1 | 75 (5) | | 2 | 15 |
| Nanotag HLBNSL | SOD1 | NS-SL | 3.97 ± 0.51 | 2.2 | 60 (4) | 27.0 ± 3.5 (132 %) | 0 | 0 |
| Nanotag NS-SD (running) | water | NW-SD | 5.84 ± 1.88 | 2.7 | 40 (5) | | 0 | 14 |
| Nanotag NS-SD (running) | SOD1 | NS-SD | 4.13 ± 1.76 | 2.1 | 40 (5) | 28.1 ± 12.0 (138 %) | 0 | 2 |

- HLBNSL SOD1 is 4 mice: HLBNSSL43 died 2026-09-28 and the sheet discards its data. NS-SD / NW-SD cover 8 full days
  (2026-10-24 to 10-30 and 11-02; 10-31, 11-01 and 11-03 are not full days, see below); the last bottles are weighed at sampling
  on 2026-11-04, so the numbers will change.
- Per-mouse means of the SOD1 arms, mL (U): S-SD 2.98 to 4.24 (20 to 29); S-SL 2.82 to 3.86 (19 to 26); NS-SL 3.64 to 4.25
  (25 to 29); NS-SD 3.35 to 5.68 (23 to 39, the top one inflated by two emptied bottles).
- Days under 2 mL are mostly the first two days after tethering (EEG: W-SL 15 of 18, S-SL 14 of 17, W-SD 8 of 12, S-SD 6
  of 14), a nozzle learning effect that hit both arms. They are not a SOD1 signal. See HLBSSD17 below for the exception.
- A weekend bottle (made Sat 2026-10-31, weighed Mon 11-02) gives, if it stayed two days, (In - Out)/2 = 3.8 mL/day (3.1 to
  4.6) for NS-SD and 6.3 (4.5 to 9.4) for NW-SD. This is an inference (see problems) and is not in the table.

## SOD1 vs water

SOD1 minus water, difference of per-mouse means (mouse = unit), exact permutation p, 95 % CI from inverting that test
(grid of 0.3 % of the range). "Steady" drops Days 1 to 2 and any day above 6 mL (leak or emptied bottle, the sheet's own amber
flag).

| Pair | n (SOD1 vs water) | Intake, all days, mL/day | Intake, steady | Body weight change, % points |
|---|---|---|---|---|
| EEG, SD (S-SD vs W-SD) | 9 vs 9 (weight 9 vs 8) | -0.82 [-1.67, -0.01], p = 0.052 | -0.44 [-1.25, +0.38], p = 0.27 | -1.2 [-3.8, +1.6], p = 0.38 |
| EEG, normal sleep (S-SL vs W-SL) | 8 vs 9 (weight 8 vs 8) | -0.44 [-0.83, -0.05], p = 0.032 | -0.43 [-0.76, -0.11], p = 0.014 | -1.2 [-3.9, +1.6], p = 0.38 |
| Nanotag HLBNSL (NS-SL vs NW-SL) | 4 vs 5 | -1.12 [-1.91, -0.26], p = 0.024 | -0.66 [-1.56, +0.10], p = 0.10 | +0.0 [-1.8, +1.8], p = 1.0 |
| Nanotag NS-SD (running) | 5 vs 5 | -1.71 [-3.39, +0.08], p = 0.063 | -1.05 [-1.83, -0.24], p = 0.024 | not yet weighed |

- Read: **SOD1 mice removed less volume than water mice in all four pairs**, with CIs that touch or exclude zero in some
  analyses and not in others. Weight: **no detectable difference** in any pair.
- Caveats that change the reading of the intake rows (all measured, below): bottle type differs by arm in three pairs, EEG pairs
  were different cohorts on different weeks, and the SOD1 arm is capped by a 10 mL bottle. Only W-SD vs S-SD used the same
  bottle type in both arms.
- The weight comparisons are small: CIs of ±3 % points (EEG) mean a weight difference of 1 to 2 % points is not excluded.

## Body weight

Start = weight at tethering (EEG) or 6 days after surgery (nanotag, tag in both weights); end = sampling. The sheet has no daily
weights, so there is no trajectory.

| Batch | Arm | n | Start g | Sampling g | Change % (range) |
|---|---|---|---|---|---|
| W-SD | water | 8 | 31.2 | 30.3 | -3.0 (-8.7 to +1.9) |
| S-SD | SOD1 | 9 | 30.4 | 29.2 | -4.1 (-7.0 to -1.7) |
| W-SL | water | 8 | 31.9 | 30.5 | -4.4 (-7.9 to -0.7) |
| S-SL | SOD1 | 8 | 32.2 | 30.4 | -5.6 (-9.2 to 0.0) |
| NW-SL | water | 5 | 32.6 | 32.5 | -0.2 (-1.5 to +0.9) |
| NS-SL | SOD1 | 4 | 33.0 | 33.0 | -0.2 (-1.2 to +0.3) |
| NW-SD | water | 5 | 6 d post-surgery 29.2 | pending 2026-11-04 | |
| NS-SD | SOD1 | 5 | 6 d post-surgery 30.9 | pending 2026-11-04 | |

- No mouse lost more than 10 % between start and sampling (largest: HLBSSL32, -9.2 %, SOD1).
- NS-SD / NW-SD before treatment started (6 d post-surgery vs pre-surgery, tag 2.7 g removed): NW-SD -3.9 % on average, HLBNWSD58
  -10.2 % and HLBNWSD60 -10.0 %; NS-SD -0.8 %, lowest HLBNSSD55 -6.6 %. That was 2026-10-18, six days before SOD1 or water began,
  so it is surgery recovery, not tolerability. No weight is recorded since.
- Excluded from weight rows: W-SD05 (sacrificed 2026-08-21), W-SD10 (never tethered), W-SL28 (no tethering weight), S-SD20 and
  W-SL30 (excluded), S-SL36 and S-SL37 (dead), HLBNSSL43 (died 2026-09-28).

![[2026-11-03-hlb-intake-fig1-intake-weight.png]]

*Fig. 1. Top: mean liquid intake per mouse (all recorded days); dashed line = 3 mL/day, the volume the dose was sized for.
Bottom: body weight change from tethering (EEG) or 6 days after surgery (nanotag) to sampling. Points = mice, bar = mean; grey =
water, teal = SOD1. NS-SD / NW-SD are not weighed yet. Code: `nanotag/analysis/intake/intake_summary.py`.*

## Tissue sampling inventory

Source: sheet tabs `Sampling`, `NANOTAG sampling`, `Registry`, `NANOTAG registry`; assays from
[[2026-11-02-EEG-cohorts-tissue-SOD-MDA-reanalysis]]. The tissue note says HLBNSL and NS-SD tissue is stored at -80 °C (Andrea,
2026-11-02); freezer storage of the EEG tissue is "-80 °C deep freezer" (same note). The SPF storage is not documented anywhere in
the sheet or the vault.

| Batch | Date | n sampled (per arm) | Tissues | Storage | Assays run | Stored unassayed |
|---|---|---|---|---|---|---|
| W-SD (water + chronic SD) | 2026-08-28 | 9 water (of 10; W-SD05 sacrificed 08-21, no tissue; W-SD10 never tethered) | cortex, hippocampus, hypothalamus, heart | -80 °C | hippocampal SOD 9, heart SOD 6, hippocampal MDA 6 | cortex 9, hypothalamus 8 (09 has none), heart 3 |
| S-SD (SOD1 + chronic SD) | 2026-09-03 | 9 SOD1 (S-SD20 excluded) | same | -80 °C | hippocampal SOD 9, heart SOD 6, hippocampal MDA 5 | cortex 9, hypothalamus 8 (12 has none), heart 3 |
| W-SL (water, normal sleep) | 2026-09-18 | 9 water (W-SL30 excluded) | same | -80 °C | hippocampal SOD 9, heart SOD 6, hippocampal MDA 6 | cortex 9, hypothalamus 9, heart 3 |
| S-SL (SOD1, normal sleep) | 2026-09-21 | 8 SOD1 (36, 37 dead) | same | -80 °C | hippocampal SOD 8, heart SOD 6, hippocampal MDA 6 | cortex 8, hypothalamus 8, heart 2 |
| NS-SL / NW-SL (HLBNSL) | 2026-10-02 | 4 SOD1 + 5 water (NS-SL43 died 09-28) | cortex, hippocampus, hypothalamus, liver, heart | -80 °C | none | all of it (9 mice) |
| W-SPF / S-SPF (gavage, out of report scope) | 2026-10-27 | 5 vehicle + 5 SOD1 gavage; SD 6 h, sampled 15:00 | cortex, hippocampus, hypothalamus, liver, heart | not documented | none | all of it (10 mice); BW at sampling not recorded |
| NS-SD / NW-SD (running) | 2026-11-04 (planned) | 5 SOD1 + 5 water | same five tissues, "40 sec sampling" | -80 °C planned | none | |

- The EEG cohorts have **no liver**: the sheet's organ list for them is cortex, hippocampus, hypothalamus, heart. Liver SOD or MDA
  is possible only on HLBNSL, NS-SD / NW-SD and the SPF mice.
- Whether homogenate or whole tissue remains after the hippocampal SOD / MDA and heart SOD plates (heart 6 per group used) is not
  recorded; "stored unassayed" counts untouched organs only.
- The sheet's `Used (date)` and `Experiment` columns of the sampling tabs are empty for every mouse, so the sheet does not record
  which tissue went into which assay. The assay column above comes from the tissue note.

## Data problems found

1. **Bottle type confounds the arms.** Water mice used ~250 to 300 g bottles (In > 100 g) for 44 of 144 W-SL mouse-days, all W-SL
   mice from Day 13 (HLBWSL25 from Day 5), 5 of 75 NW-SL (HLBNWSL48 from Day 11) and 36 of 40 NW-SD mouse-days (four of five mice
   from Day 1). No SOD1 mouse ever used one. On switching, the same mice read higher: W-SL +1.3, +1.9, +1.8, +1.9, +1.9, +0.5,
   +1.5, +1.2 mL/day (8 of 8 up), HLBNWSL48 +2.4, HLBNWSD56 +0.7; the SOD1 arm S-SL over the same days drifted +0.15. So much of the
   water-arm excess in W-SL, NW-SL and NW-SD is probably the bottle (drip, or a different nozzle), not drinking.
2. **Emptied bottles, so intake is censored and may be a leak.** Out ≈ 45.0 to 45.7 g is the empty-bottle weight: W-SD has 12
   such days (HLBWSD04 drained its bottle on 6 of its last 7 days, 7.6 to 10.8 mL; also W-SD01, 02, 03, 05, 08), S-SD 3 (HLBSSD14 Day 14,
   HLBSSD17 Days 3 and 15), NS-SD 2 (HLBNSSD55 Day 2, 7.9 mL, and Day 4, 13.2 mL from a 60 g bottle). The README says above ~6 mL
   usually means a leaking or knocked bottle. The flag is a heuristic (NW-SL has four light bottles it also catches; those are not
   empty).
3. **Mice that could not drink from the bottle.** HLBSSD17 drank 0.4 to 1.0 mL on Days 1 and 2 and 4 to 9 (and 8.8 on Day 3, an
   emptied bottle); the log says a normal water bottle was added on 2026-08-23 and again 08-27 "even with a different nozzle", with the
   water volume not logged. Its 2.93 mL mean (98 % of target) is not a valid dose. HLBWSD01 "struggled to drink from the glass tube"
   (0.3 to 0.7 mL on Days 1 to 3). Both are nozzle problems, not solution refusal.
4. **W-SL Days 13 to 16 look rounded.** Out weights 300.0, 295.0, 290.0, 285.0, 280.0 and exactly 5.00 mL for HLBWSL21 on three days
   in a row; W-SL has 9 days at exactly 5.0 mL against 0 in S-SL. These may be estimates rather than weighings. Ask Andrea.
5. **Weekend 2026-10-31 / 11-01 (NS-SD, NW-SD).** In sits on the Saturday row and Out on the Sunday row, with no new bottle in between.
   For NW-SD the In on 11-02 (264.8 g) equals the "Out" of 11-01 (265.0 g), so that Out was weighed Monday: the bottle stayed
   about two days, and the sheet leaves both days empty. I excluded them. A SOD1 bottle left two days also conflicts with "fresh
   every day" (the draft says SOD1 degrades within about 30 h): the weekend dose is uncertain.
6. **S-SL has intake after its sampling date.** Rows Day 18 and 19 (2026-09-21, 09-22) have both In and Out although the Registry and
   `Sampling` give sampling on 09-21. Either the sampling date or the rows are wrong (the tissue note says S-SL was sampled 09-22).
   The README tracking windows disagree too: it gives S-SL tethering 08-31 → sampling 09-18 and W-SL 09-03 → 09-21, while the tabs
   say S-SL 09-04 → 09-21 and W-SL 09-02 → 09-18. No intake number depends on it.
7. **HLBSSL36 / 37 status.** The sheet says Dead, no tissue, no intake. The tissue note records Andrea's answer that they were "left out
   because the plate was full". Both cannot be true (Dead mice have no hippocampus on the sampling sheet): needs Andrea.
8. **Group sizes in the sheet are overstated.** README and `Summary` say n = 10 for the four EEG batches; mice with data are 9, 9, 9,
   8 (W-SD10 not tethered, S-SD20 and W-SL30 excluded, S-SL36 and 37 dead). `Summary` also lists NS-SL as 4 and HLBNSSL43 separately.
   W-SD05 has 7 intake days (sacrificed 08-21) and stays in the intake means; HLBNSSL43's 10 days are dropped as the sheet does.
9. **`NANOTAG sampling`, Dissection time (min).** For HLBNSSL44 and 49 and all five NW-SL mice the value equals the body weight
   at sampling (33.8, 32.2, 33.0, ...): a copy error, not a dissection time. Only HLBNSSL41 (4) and 42 (3.3) look real.
10. **No weights between the two time points, and no spill control**; whether the EEG tethering weight includes the implant or tether is
    not recorded, so the 3 to 6 % EEG loss is read only as the same in both arms.
11. **Sheet values were not edited** (read only); none of the above was fixed there.

## Still open

- [ ] Ask Andrea: were W-SL Days 13 to 16 weighed or estimated; why do water mice get large bottles (NW-SD, W-SL, NW-SL); were
      SOD1 bottles really changed daily over the 2026-10-31 weekend.
- [ ] Ask Andrea: HLBSSL36 / 37 (dead or left out for the plate); S-SL sampling date; the water given to HLBSSD17.
- [ ] Weigh the NS-SD / NW-SD mice at sampling 2026-11-04 and rerun `intake_summary.py` after the last bottles are entered
      (add the CSVs again from the sheet).
- [ ] For the report: say "SOD1 mice drank less volume, partly a bottle effect" or drop the water-arm pairs from the intake claim;
      the dose statement (108 to 138 % of target) does not depend on the water arm.
- [ ] Decide with the professor which stored tissue to assay first (HLBNSL: heart SOD, heart MDA, hippocampal MDA; liver); see
      [[2026-11-02-EEG-cohorts-tissue-SOD-MDA-reanalysis]].
- [ ] Where is the SPF tissue stored and what is it for (not in the sheet or the vault).

Related: [[2026-11-02-hlb-sod1-final-report-draft]] (section 3), [[sod1-sheet-change-log-workflow]], [[hlb-sod1-design]],
[[2026-10-19-NS-SD-NW-SD-nanotag-study]].
