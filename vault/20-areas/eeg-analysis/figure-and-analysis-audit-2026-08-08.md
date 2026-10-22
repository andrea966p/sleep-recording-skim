---
type: experiment
area: eeg-analysis
status: done
tags: [troubleshooting, figures, statistics, audit, integrity]
created: 2026-08-09
---

# Audit of the 2026-08-08 figures, and what had to be rebuilt

> [!abstract] TL;DR — for non-technical readers
> **What this is.** A record of what was wrong with the first set of figures made for the professor update, and what changed. It exists so that two specific mistakes cannot quietly come back.
>
> **Why it exists.** Three of the findings were integrity problems rather than styling problems: a reference band drawn from arithmetic that matches no published value, confidence intervals that were far too narrow, and numbers typed into the figure scripts by hand instead of computed. A fourth surfaced during the rebuild and changes how one headline should be quoted.
>
> **How to read it.** Section 1 is the finding that matters most. Section 2 is everything else by severity. Section 3 records the inspections that were run and what they returned, including where they did not pass.

Figures audited: `05-experiments/attachments/2026-08-08-fig01..fig10-*.png`, now moved to `attachments/superseded/2026-08-08-figures/`.
Replacements: `2026-08-09-fig01..fig09-*.png` plus PDF and a `.export.json` manifest for each.
Scripts: `eeg-emg-analysis/qc/figures_2026-08-08/`.
Standards applied: the `scientific-visualization`, `statistical-analysis` and `scientific-critical-thinking` skills.

## 1. 🔴 The finding that came out of the rebuild: the tether result is threshold dependent

Rebuilding the tether panel from the raw CSVs rather than from the write up exposed something the vault had not recorded.

The headline **"a soldered tether took the duty cycle from 45 percent to 100 percent"** was computed at the **2 MOhm** pass mark, which was in use on 5 August. On 6 August that pass mark was retired, because a cut cable with no animal on it was found to pass **22 percent of the time** at 2 MOhm, and the criterion moved to **0.5 MOhm**. The census memory said plainly: re-score old blocks before quoting them. **The arm A against arm B blocks were never re-scored.**

Re-scored now, from the same 40 sweeps:

| channel | at 2 MOhm | Fisher p | at 0.5 MOhm | Fisher p |
| --- | --- | --- | --- | --- |
| B1 EEG | 9/20 → **20/20** | 0.0001 | 5/20 → **2/20** | 0.41 |
| B1 EMG | 4/20 → 15/20 | 0.0012 | 0/20 → **7/20** | 0.0083 |
| D2 EEG, concurrent control | 8/20 → 3/20 | 0.16 | 2/20 → 2/20 | 1.00 |
| D2 EMG, concurrent control | 20/20 → 19/20 | 1.00 | 16/20 → 14/20 | 0.72 |

🔴 **At the corrected pass mark the EEG half of the result disappears and points the other way.** The muscle channel improvement survives and is still significant. The control still fails to improve, so the design is intact; it is the threshold that was doing the work.

**What this does NOT overturn.** The claim that the tether chain is the fix does not rest on this block. It rests on the **recording**: D2 went from 0.0 percent to 87.9 percent usable EEG, with hum from 917 to 133 microvolts and spectral slope from −0.38 to −2.05, after a tether swap with the implant untouched. That is the project's own rule at work, **impedance blocks screen, only a multi-hour recording is an outcome**, and it is the reason the conclusion survives.

**What must change in how it is quoted.** Stop quoting 45 percent to 100 percent as the tether evidence. Quote the recording. If the impedance block is shown at all, show it at both pass marks, which is what figure 8 now does.

## 2. Findings from the audit itself

### 🔴 Critical, changed what a reader would conclude

**2.1 A reference band that matches no published value.** The old figure 7 drew a shaded band computed as `62.0 - 7.8 + 8` to `70 + 7.8`. That arithmetic corresponds to nothing. The dispersion this project holds is **NREM 62.0 plus or minus 7.8 percent per 12 hours**, whereas the quantity plotted is NREM plus REM. **Fixed:** no band is drawn. A single dashed line marks the approximate literature value for total sleep and the caption states that no defensible interval is available for the plotted quantity.

**2.2 Confidence intervals that were far too narrow.** The old figure 2 put Jeffreys intervals on 8,517 epochs as though epochs were independent Bernoulli trials. Contact persists for tens of minutes. **Fixed:** 95 percent block bootstrap over contiguous runs, 2,000 resamples. For D2's EEG the interval goes from about 1.4 points wide to **7.3 points wide, 5.4 times wider**, and its effective sample size is about **1,088 epochs, not 8,517**.

**2.3 Numbers typed into figure scripts.** Usable fractions, per channel forensics and scoreable hours were transcribed from vault documents into Python dictionaries, so a transcription error would have been invisible and no figure could be regenerated from data. **Fixed:** `compute_inputs.py` builds `derived/inputs.json` from the raw recording, the impedance CSVs and the pipeline feature files; `figs_common.derived()` **refuses to run** if a derived input is missing rather than falling back to anything hand entered. Two upstream scripts gained machine readable output for this: `usable_fraction_vs_floor.py --npz` (per epoch masks, not just percentages, because a percentage cannot support a block bootstrap) and `per_animal_forensics.py --json`.

✅ **Verification:** every recomputed usable fraction reproduces the vault value exactly. B1 100.0 and 99.6, D2 87.9 and 98.6, C1 EMG 37.8, C2 EMG 15.2, A1 EMG 7.6, floor 0.00, A2 no animal 0.0. The only change anywhere is C2 EEG 0.0 to 0.1 percent. **No previously reported number was wrong.**

### 🟠 Important, affected interpretation

**2.4 No multiplicity control.** 16 Fisher tests ran against one shared comparison group with raw p values. **Fixed:** Holm and Benjamini-Hochberg columns. Four channels survive Holm, and the sentence in the reports is unchanged in substance because the four that survive are the four that were being claimed.

**2.5 A clustered comparison group treated as independent.** The 2,240 wire free readings come from 4 ports. **Fixed:** a port level permutation p is printed beside the Fisher p, **and labelled as having no power at four clusters**. It is shown so the reader can see the limitation, not as a second opinion.

**2.6 No effect sizes.** **Fixed:** risk difference against the floor with an interval, so the figure says how much better than a bare wire, not only that it is better. The four surviving channels run from +26.9 to +66.9 points.

**2.7 A rank correlation dominated by ties, and a control animal inside it.** The old figure 10 reported an asymptotic Spearman p on 8 EEG channels of which five were tied, and included the A2 position, which holds no animal. **Fixed:** A2 excluded and marked separately, exact permutation p from 10,000 relabellings. Result: **rho 0.73, p 0.094, n 7, not significant**, which is the quantitative form of the operational rule.

**2.8 Two figures making one claim by two methods.** Old figures 6 and 10 overlapped, one using a Gaussian approximation to the null and one using real permutations. **Fixed:** the approximation is retired, the permutation version kept, and the set renumbered to nine contiguous figures.

### 🟡 Craft

**2.9 Lines implying trajectories that were never measured.** Figure 1 connected five single 20 second sweeps of a contact that flips within minutes. **Fixed:** markers with a faint connector, and the caption states each point is one unrepeated measurement with no interval available.

**2.10 Hypnograms drawn as lines** through state codes 0, 1, 2, so a wake to REM transition was drawn as if it passed through NREM. **Fixed:** state bands, with epochs outside a usable block drawn explicitly in grey instead of joined over.

**2.11 Colour carrying meaning alone.** **Fixed:** hatching on the partial category, markers differing by shape wherever colour separates classes.

**2.12 Two different window selection rules.** Figure 3 used a median amplitude rule, figure 4 a fixed index. **Fixed:** one rule in `figs_common.median_window`, used by both and stated in both captions.

**2.13 A caption asserting a number its panel did not support.** The old figure 3 caption quoted about 69 microvolts for wire free inputs while the panel showed 531. **Fixed:** twelve wire free inputs are computed, the median one is drawn, and the caption gives the measured span across all twelve, 193 to 438 microvolts.

**2.14 No provenance, no alt text, raster only, seeds not recorded.** **Fixed:** every figure exports PNG and PDF through the skill's exporter with a `.export.json` manifest recording source files, transformations, uncertainty definition, missing data policy, palette, style and seed, plus an alt text string.

**2.15 Page sizes were not what they claimed.** Captions were written at negative axes coordinates and `bbox_inches="tight"` silently grew every canvas. **Fixed:** captions live in a reserved axes row, `layout="constrained"`, `bbox_inches=None`.

## 3. Inspections run, and what they returned

**Palette.** `scripts/palette_audit.py --palette okabe_ito_on_white --role graphical`. Four pairs are **flagged for grayscale review**, not passed: blue against vermillion, delta L\* 8.2; vermillion against green, 3.6; vermillion against purple, 6.9; green against purple, 3.3. Every one of those pairs is separated by an additional channel in the figures where it appears, by marker shape in figures 1, 4 and 8 and by panel position in figure 5. **This is recorded as reviewed, not as compliant.**

**Files.** `scripts/image_metadata.py` on all nine PNGs: 300 dpi, RGBA, 3,240 to 4,020 pixels wide, 292 kB to 1.34 MB. Two honest notes. The dpi field reads **299.9994** and therefore fails a strict `--min-dpi 300` check, which is a rounding artefact of the PNG header rather than a resolution problem. The files carry an **alpha channel** even though the background is painted opaque white, so any downstream check with a forbid-alpha policy will flag them.

**PDF.** Not inspected. The inspector needs `pypdf`, which is not installed in `~/eeg-analysis-venv`. Recorded as **not checked** rather than assumed good.

**Statistical method that was built and then discarded.** A moving block bootstrap for the persistence statistic produced 95 percent intervals that **did not bracket their own point estimate**, because the best recording is a single unbroken block and the estimator is sensitive to the chunk length. It was discarded rather than tuned until it looked acceptable, and figure 9 now shows an exact within block permutation null instead, with the caption saying explicitly that no interval is quoted on the magnitude and why.

## 4. What was deliberately not changed

* **The smoothed against raw label gap is displayed, not hidden.** Recomputed persistence and REM ordering sit above the headline values because the stored hypnograms carry the 12 second minimum bout rule. Both are drawn, because the gap is itself the evidence that smoothing inflates these statistics.
* **The port level permutation stays in figure 8** despite having no power at four clusters, because its weakness is the point being communicated.
* **Older recordings keep their vault sourced yield values**, marked with an asterisk in figure 7, rather than being dropped or silently mixed with pipeline computed values.

## 5. Related

* [[2026-08-08-professor-update-short]] — the handout these figures serve
* [[2026-08-08-full-update-for-professor]] — the long working record
* [[2026-08-06-fleet-duty-cycle-census]] — where the 0.5 MOhm pass mark came from
* [[2026-08-05-tether-comparison]] — the arm A against arm B blocks re-scored in section 1
