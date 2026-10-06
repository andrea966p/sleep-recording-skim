---
tags: [reference, nanotag, kissei, actigraphy, sleep, literature]
created: 2026-10-05
status: active
---

# Nanotag (Kissei Comtec VSMN 210): what it measures, and what the literature says

> [!abstract] TL;DR
> - **What it is.** A 2.7 g implantable logger, 15 × 14.2 × 7.1 mm. It has a 3-axis accelerometer and a temperature sensor and is read by NFC. We use it for **home-cage sleep and activity without EEG**, in the HLB SOD1 study ([[2026-09-14-HLBNSL-nanotag-SOD1-sleep]]).
> - **What it stores.** Activity is a **cross count**: how often the combined 3-axis signal (sampled at 25 Hz) rises through a threshold that is fixed on the tag at recording, summed per bin (12 s for us). Temperature is the **tag-case temperature under the skin**, one value every 5 min. It is **not core temperature**.
> - **Its limits drive the protocol.**
>   - Memory holds **8 days** at 12 s activity + 5 min temperature, or 20 days with activity alone.
>   - The battery lasts **~60 days** and cannot be replaced.
>   - NFC reaches **~1 cm**, so the tag must sit under the skin.
>   - The viewer runs on **Windows only** and needs its USB licence dongle.
> - **Sleep is inferred, not measured.** Immobility ≥ 40 s ≈ sleep (Pack 2007, video-based, 92% agreement with EEG). On 12 s bins we use **≥ 4 empty bins (48 s)**; the only published mouse nanotag sleep study used 2 bins (24 s). **Nobody has validated the nanotag against EEG in mice**; the closest is a monkey study against polysomnography.
> - **For us:** the tag site (right flank, after migrating from the neck) is not a Kissei-validated site, and the neck threshold (170) was used. Counts are therefore **relative units, valid within one study**.

> [!quote] Paper-ready
> Locomotor activity and subcutaneous temperature were recorded with implantable accelerometer loggers (nano tag® VSMN 210, Kissei Comtec, Matsumoto, Japan; 2.7 g). Activity was stored as threshold cross counts of the 3-axis acceleration vector (25 Hz sampling, threshold 170) in 12 s bins, and tag temperature every 5 min. Data were read out by near-field communication and exported with nanotagViewer. Sleep was scored as ≥ 48 s of continuous immobility (≥ 4 consecutive zero-count bins), adapted from the ≥ 40 s criterion of Pack et al. (2007).

## The device (manual, 2025-09-25 edition)

The manuals are in the vault: [[Kissei_nanotag_VSMN210_UsersManual_2025-09-25.pdf]] (English) and [[Kissei_nanotagViewer_UsersManual_JP.pdf]] (Japanese viewer manual). Page numbers refer to the English edition.

| Property | Value | Manual |
|---|---|---|
| Model | nano tag® VSMN 210 | p2 |
| Size, mass | 15 × 14.2 × 7.1 mm, about 2.7 g; ABS case, IPX7 | p2 |
| Sensors | 3-axis acceleration (25 Hz) and temperature | p2, p46 |
| Activity | Cross count: crossings of the threshold by the combined vector signal, per bin. At most 150 per 12 s bin; ours peak at 56–79 | p37, p46, p49 |
| Threshold | Written to the tag at setup; cannot be changed afterwards. Kissei values: mouse neck 170, mouse abdomen 150, rat neck 170, rat abdomen 140. For any other site, derive one from a 27-min vector-wave recording with video | p18–20, p49 |
| Temperature | Tag-case temperature. Sensor range 10–45 °C; values outside the range set at recording (ours 30.0–45.8 °C) are stored as the text `Out of range` | p2, p37 |
| Time stamp | A row's value covers the bin that starts at its stamp | p49 |
| Memory | 12 s activity + 5 min temperature: 8 days. 12 s activity alone: 20 days. Full table in the sheet's NANOTAG recordings tab. `Using memory type` = Stop (default; recording ends when full) or Loop (overwrites the oldest) | p3, p24–27 |
| Battery | CR1220, not replaceable. Activity + temperature: 60 days; temperature only: 180 days. It also drains while the tag waits to start | p3 |
| Read-out | NFC, about 1 cm without obstacles, so implant **under the skin, antenna side (blank face) out**. A tag in the abdominal cavity can only be read after removal | p2, p16–17 |
| Recovery | "About 3 days" after neck or abdominal implant in rat or mouse (the literature waits ≥ 1 week; see below) | p17 |
| Several reads | One file per read; join them with the viewer's "Combine recording files" or by CSV (our route, [[nanotag-recording-and-analysis]]) | p27 |
| Software | nanotagViewer R1.2.10 (Windows 10/11 Pro), USB licence dongle, Sony PaSoRi RC-S380 NFC reader (not on a PC with its own NFC/FeliCa port) | p4–11 |

Our setup files (installer, PaSoRi driver, VC2008 runtime, Kissei sample data) are on the SKIM workstation in `~/Desktop/Andrea/nanotag/`.

## How the literature uses it

**Sleep from immobility.** These are the papers our scoring rests on. They were supplied by the lab and checked in PubMed on 2026-10-05.

- **Pack et al. 2007**, *Physiol Genomics* 28:232. ≥ 40 s of inactivity = sleep; 92% epoch agreement with EEG/EMG in C57BL/6J mice. The 40 s criterion gave near-minimum bias; the bias leans toward the light phase. Brief arousal movements split long bouts, which is why we bridge ≤ 24 s gaps for bout statistics. Video-based, not a tag. [doi](https://doi.org/10.1152/physiolgenomics.00139.2006)
- **Nagai M et al. 2020**, *Sci Rep* 10:19800. **The only mouse sleep study with the nanotag.** 12 s bins; "sleep-like inactivity" = 2 empty bins (24 s); intraperitoneal implant, so it reads core temperature but must be removed to read; ≥ 1 week recovery; body temperature tracks activity (r = 0.85). [doi](https://doi.org/10.1038/s41598-020-76717-8)
- **Maret et al. 2011** (*Nat Neurosci*) and **Nagai H et al. 2017** (*Sleep*). Motion-based scoring gives ≥ 90% accuracy for total sleep against EEG and cannot separate NREM from REM. [doi](https://doi.org/10.1038/nn.2934) · [doi](https://doi.org/10.1093/sleep/zsw059)
- **Hasegawa et al. 2024**, *Sci Rep* 14:16909. Rats, neck s.c. They analyse active and resting periods separately, normalise each animal to its own baseline and **remove data recorded during interventions**. They **sutured the tag to the muscle membrane** (5-0 nylon) to stop migration, and found subcutaneous temperature too subtle to be useful. Their 5-min intensity cut points are for rats and are not used here. [doi](https://doi.org/10.1038/s41598-024-67024-7)

**Other published nanotag use.** Found in PubMed on 2026-10-05; not in the 2026-10-01 report.

| Study | Species, site | What it adds for us |
|---|---|---|
| Yoshizawa et al. 2019, *Exp Anim* 68:277 (with Kissei authors) | Rat, s.c., group-housed | Activity was still changed **9 days after transport and 3 h after a cage change**. Handling and husbandry events leave a measurable tail, which is the reason for our exclusion windows. [doi](https://doi.org/10.1538/expanim.18-0097) |
| Sakai et al. 2020, *Heliyon* 6:e03524 | Cynomolgus monkey, s.c. forehead | **The closest thing to an EEG validation**: nanotag activity correlated with polysomnography wake time, and responded to modafinil and triazolam. Primate, diurnal, a different site. [doi](https://doi.org/10.1016/j.heliyon.2020.e03524) |
| Kishida et al. 2022, *J Pharmacol Toxicol Methods* 118:107224 (Kissei Pharmaceutical) | Monkey, s.c. | Activity and temperature roughly match an implanted telemetry transmitter; recovery from implantation by day 7. [doi](https://doi.org/10.1016/j.vascn.2022.107224) |
| Mori et al. 2024, *Transl Psychiatry* 14:138 | Mouse (3q29 deletion), intraperitoneal | Long-term activity + body temperature; mutants reacted faster and more strongly at lights-off. [doi](https://doi.org/10.1038/s41398-023-02679-w) |
| Mori et al. 2024, *Transl Psychiatry* 14:216 | Mouse (Pcdh15), implanted | Higher diurnal amplitude of activity and temperature in the mutants. Diurnal amplitude is the same kind of readout as our RA. [doi](https://doi.org/10.1038/s41398-024-02952-6) |
| Takeda et al. 2025, *J Integr Neurosci* 24:42403 | Aged mouse, **s.c. dorsal**, like ours | Post-operative activity for 7 days, **combined with Y-maze and novel-object recognition**, the same tests as our Day 0–2. [doi](https://doi.org/10.31083/JIN42403) |

## What this means for our data

- **Comparisons only within a study.** The site and threshold are not validated, so absolute counts and absolute sleep minutes are not comparable with other labs. Group comparisons are fair: every tag has the same site, side and threshold.
- **The cutoff changes the amount, not the comparison.** 24 s vs 48 s moves total sleep by ~65 min/day but leaves the SOD1–water difference unchanged ([[2026-10-05-HLBNSL-nanotag-merged-analysis]]).
- **Handling has a tail.** The tail is measurable for hours (Yoshizawa 2019), and in our data dark-phase sleep is ~10 points higher on the handling and test days. Remove the sessions, and analyse or report the disturbed days separately.
- **Validation is still missing.** A nanotag in a few EEG/EMG mice on our own rig, scored over the same 24 h, would give the first mouse accuracy figure and settle the cutoff. See "For the next nanotag cohort" in the report.

## SOD1 context

The project's rationale (oral microbial SOD against sleep-loss oxidative stress), design and the EEG → nanotag pivot are in [[_HLB-SOD1-project-hub]].

## History

> [!history]
> - **2026-10-05** — Created. Device facts re-checked against the English manual (spec table p2, battery p3, read-out and recovery p16–17). Core references verified in PubMed (PMIDs 16985007, 33188274, 39043741); six further nanotag studies added from PubMed.
