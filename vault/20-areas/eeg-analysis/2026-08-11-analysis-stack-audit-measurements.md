# Analysis stack audit: what I measured, 2026-08-10/11

**TL;DR.** An LLM council reviewed the analysis stack, and then I checked the
council's claims against the code and the data rather than taking them. Two of
its headline findings did not survive that check. Four things it never saw did.
The important ones: **a second, backwards implementation of the whole pipeline was
sitting in the repo**; **the slope criterion's central justification is false**;
**no experimental animal passes the EMG gate, on the full recording including the
dark phase** (⚠️ **PARTLY WRONG — corrected 2026-08-21, see §4: with a per-chip floor B2 reaches
-0.366 and does pass**); and **slope-criterion usable fractions carry 37 to 45 point
intervals from the wire-free floor's own sampling error alone.**

All four test suites are green. Every number below was measured on this rig's own
data or on synthetic data with known ground truth. Nothing here is quoted from
memory.

Decisions taken as a result live in
`07-decisions/2026-08-11-analysis-stack-consolidation.md`. This page is the
evidence.

---

## 1. The council's headline finding was aimed at a dead file

Five advisors and five peer reviewers, independently, called the same thing fatal:
that `sleep/hypnogram.py` split NREM from REM at the **median** theta over delta
ratio, which forces REM to be half of all sleep when a mouse has 5 to 10 percent.

That code existed and said exactly that. **It was not the scorer.** Nothing
imported it. The production path is `pipeline/stage3_features.py`, which:

- cuts REM at the **80th percentile**, with the comment `<- fixes REM share by
  construction` written at the line;
- computes a **second, independent Otsu cut** so a data-driven REM share exists;
- **refuses to report any REM percentage at all** (`cards/ladder.py`), because the
  two disagree by roughly a factor of five;
- computes persistence and REM ordering on **raw labels**, before the minimum
  bout rule, precisely so smoothing cannot inflate them;
- merges short bouts into the **longer** neighbour, not the preceding one;
- already labels four of its five physiology checks `FORCED`.

So the criticism was wrong about the pipeline. **It was right about the risk.** An
orphaned scorer that contradicts the real one fooled ten independent readers in
ten minutes. It would fool a referee. That is a clutter problem with scientific
consequences, and it is why the deletions below happened.

## 2. A second, backwards implementation of the pipeline was live in the tree

Nobody had flagged this. `core/config.py` + `core/dsp.py` + `core/channel_map.py`
implemented a **four rows per mouse, subtract offline** channel model:

| | current pipeline | the legacy half |
|---|---|---|
| channel model | `/1` EEG, `/2` EMG, already bipolar; `/3`,`/4` empty pads | 4 rows per mouse, differenced offline |
| what "EEG" was | the saved bipolar signal | `rows[0] - rows[1]` = **EEG minus EMG** |
| what "EMG" was | the saved bipolar signal | `rows[2] - rows[3]` = **pad minus pad** |
| constants | `core/qc_thresholds.py` | `core/config.py`, also claiming to be the single source of truth |

The two constants files **disagreed**: delta 0.5-4.0 against 1.0-4.0, EMG band
10-100 Hz against 10-300 Hz, rail 6390.0 against 6389.565 µV.

It fed `convert/to_edf.py`, which was labelled "scorer-ready EDF+", and
`examples/run_all.sh` ran the whole wrong path end to end.

**No published number is affected.** The current pipeline never imported it, and
`qc/make_scoring_set.py` reads stage 2 output, so the kappa packs were never at
risk. But the file a human scorer would have been handed was built by the wrong
half.

## 3. "Filtering cannot manufacture slope" is false

This sentence was written into both `core/qc_thresholds.py` and
`core/criteria.py` as the reason the slope criterion is safe.

Measured on 3,000 s of synthetic noise, slope over the 1-40 Hz measurement band:

| signal | slope | usable fraction |
|---|---|---|
| raw white noise, i.e. a wire-free input | 0.00 | ~1 % (by construction) |
| **the same white noise, band-passed 0.5-30 Hz** | **-1.08** | **100.0 %** |
| real 1/f^1.8 EEG | -1.81 | 100.0 % |

The 30 Hz corner of the EEG band-pass sits **inside** the 1-40 Hz measurement
band, and its roll-off is read as spectral slope. A filtered wire-free input
scores fully usable.

**Why the band was not narrowed.** Measured on 6 h of the re-pinned
`allego_0__uid0808-16-17-36`, comparing 1-40 Hz against 2-20 Hz:

| position | 1-40 Hz | 2-20 Hz | change |
|---|---|---|---|
| A1 | 0.0 % | 0.0 % | 0.0 |
| A2 | 87.3 % | 92.0 % | +4.7 |
| B1 | 10.2 % | 7.8 % | -2.4 |
| B2 | 52.3 % | 36.1 % | **-16.2** |
| C1 | 0.0 % | 0.0 % | 0.0 |
| C2 | 69.6 % | 57.0 % | **-12.6** |
| D1 | 65.2 % | 61.3 % | -4.0 |
| D2 | 59.1 % | 44.4 % | **-14.7** |

The wire-free floor scores 0.00 % under **both** bands, and **no verdict changes**.
Narrowing would restate every published number to buy nothing on data that is not
filtered.

**What was done instead.** The precondition is now enforced. A power law is scale
free, so its log-log slope is the same in any sub-band; a filter corner is not.
Slope over 25-45 Hz minus slope over 1-25 Hz:

| signal | difference | class |
|---|---|---|
| raw white, wire-free | -0.05 | scale free |
| real 1/f^1.8 EEG | +0.04 | scale free |
| 1/f^1.5 | +0.07 | scale free |
| acquisition high-pass only | -0.11 | scale free |
| band-passed 0.5-45 Hz | **-2.12** | band limited |
| band-passed 0.5-30 Hz | **-11.25** | band limited |

Bar set at **-1.0**, an order of magnitude of margin on both sides. On the real
2026-08-06 recording all eight positions measure **+0.29 to +1.02**, so the guard
is silent on genuine data and fires only on the trap.

## 4. The EMG gate: no experimental animal passes

> [!warning] PARTLY CORRECTED 2026-08-21 — THE HEADING IS WRONG, AND THE REASON IS A BUG
> These numbers were computed with the **pooled** wire-free floor. `criteria.floor_stats()` pools
> all unwired inputs across all eight amplifier chips, but this project's own definition of usable
> fraction — written in the same source file — says the comparison is against inputs recorded
> **"through the same chip"**. On this very recording the pooled value (-1.335) is **harsher than
> seven of the eight chips' own floors**, so the gate was restricted to far fewer minutes than it
> should have been.
>
> **Re-run on the same file with a per-chip floor, one animal changes verdict:**
>
> | animal | r pooled (below) | r per-chip | |
> |---|---|---|---|
> | **B2** | -0.156 (n=159 min) | **-0.366 (n=203 min)** | **crosses the bar → STATE-DEPENDENT** |
> | A2 (control) | -0.734 (n=597) | -0.713 (n=983) | unchanged |
> | C2 | -0.174 (n=137) | -0.180 (n=142) | unchanged |
> | D1 | +0.023 (n=428) | +0.028 (n=326) | unchanged |
> | D2 | +0.010 (n=353) | -0.135 (n=660) | improves, still fails |
>
> So **"no experimental animal passes" is false — B2 passes.** The wider claim, that most of the
> cohort failed, still stands: three of the four evaluable experimental animals fail either way.
>
> ⭐ **This cuts both ways and is worth stating plainly: the floor fix does NOT manufacture passes.**
> Applied to this recording it moves exactly one animal. That is the evidence that the four passes on
> the 2026-08-19 run are a real improvement in the DATA, not an artefact of changing the floor.
>
> Full detail: [[2026-08-21-39h-run-score]].


`qc/emg_state_dependence.py`, run on the **full 16.39 h** of
`allego_0__uid0808-16-17-36`, including the dark phase that had never been
analysed. r = Pearson correlation over 1-minute bins between EMG rms and EEG delta
ratio, restricted to minutes where that animal's own EEG passes the slope
criterion. **A working pair gives a negative r.**

| animal | all | light | dark | verdict |
|---|---|---|---|---|
| **A2** (carried-over control) | **-0.734** | -0.644 | -0.730 | STATE-DEPENDENT |
| C2 | -0.174 | -0.126 | **-0.332** (n=50 min) | weak overall |
| B2 | -0.156 | -0.160 | n=3 min | weak |
| D1 | +0.023 | -0.014 | +0.022 | none |
| D2 | +0.010 | +0.028 | -0.090 | none |
| A1, B1, C1 | — | — | — | no usable EEG minutes at all |

**The dark phase did not rescue it.** A2 is now *stronger* than the -0.651 on
record, which is the useful part: it confirms the measurement works. Sites,
binning, sign convention and restriction are all correct. It works on the one
animal that is not the experiment.

⚠️ The gate initially reported "PASSED for 1 animal", counting A2. A control
passing proves the instrument, not the cohort. The script now takes `--control`
and refuses to let a control satisfy the gate.

⭐ **One lead: C2's dark phase reaches -0.332 on 50 minutes.** It is the only
re-pinned animal showing real state coupling anywhere, and it is thin.

## 5. Envelope variability does not validate an EMG channel here

The burstiness test (coefficient of variation of the 1 s amplitude envelope,
30-300 Hz) is attractive because it needs no EEG, and three of seven animals have
no usable EEG. Measured on the same recording, floor burst_cv 0.213, bar 0.319:

| animal | burst_cv | reading |
|---|---|---|
| C1 | 1.394 | "bursty" — yet **zero usable EEG across three days** |
| B2 | 1.360 | "bursty" |
| A2 | 0.878 | "bursty" — correct, this is the working control |
| **A1** | **0.769** | "bursty" — **A1 HAS NO GROUND AT ALL** |
| C2 | 0.798 | "bursty" |
| D1 | 0.482 | "bursty" |
| B1 | 0.319 | flat |
| D2 | 0.316 | flat — yet D2 gave 63.7 % usable EEG |

The ranking is uncorrelated with every other line of evidence, and the
known-floating channel scores near the top.

🔴 **This is the hum criterion's failure in a new costume.** A floating input is
high impedance and picks up variable interference, so its envelope is variable, so
a test that rewards variability rewards having no electrode. The column is still
printed, because "A1 scores bursty" is exactly the evidence that kills a
criterion, but it now emits no pass and nothing may gate on it.

## 6. The wire-free floor's own sampling error, and what it does

Every usable fraction is a comparison against the 1st percentile of the wire-free
floor, and that percentile is itself an estimate. Bootstrapped **over sites, not
epochs** — epochs within one unwired input are strongly autocorrelated, so
resampling them would treat ~950,000 correlated numbers as independent draws and
give a dishonestly narrow interval. 112 floor sites, 1,000 resamples,
`allego_1__uid0806-16-57-38`:

| criterion | threshold | 95 % CI | effect on fractions |
|---|---|---|---|
| hum | 415.0 µV | [341.4, 507.7] | **0.0 points, every position** |
| slope | -1.351 | [-1.536, -1.155] | **B1 83.1 % → [53.1, 98.0]; D2 75.2 % → [48.9, 86.2]** |

The hum threshold sits in the empty valley of a distribution separated by a factor
of about 100, so it is insensitive. **The slope threshold sits inside a continuous
distribution and is not.**

🔴 **This matters now, because slope is the criterion in use** — hum died on this
cohort. The interim numbers (B2 57.5 %, C2 71.6 %, D1 70.3 %, D2 63.7 %) carry
roughly ±20 points from the floor estimate alone, before any other source of
uncertainty.

✅ **It does not move a verdict.** Rung 2 gates on the longest unbroken block, not
on the fraction. That design choice, made for a different reason, pays off here.

## 7. Re-deriving the two gate constants on post-re-pin data

The constants were audited 2026-08-03, during the era when the cerebellum ground
was on the wrong pin. A threshold fitted to a distribution produced by a wiring
fault has to be re-checked. Repeated on 8 h of post-re-pin
`allego_0__uid0808-16-17-36`, 2,880 epochs by 8 EEG channels:

| constant | value | post-re-pin measurement | conclusion |
|---|---|---|---|
| `OPEN_UV` | 150.0 µV | log-space valley at **149.4 µV** | ✅ survives, 0.4 % apart |
| `FLAT_UV` | 11.0 µV | **0.00 %** of epochs fall below it; p10 is 63.8 µV | ⚠️ **inert** |

`OPEN_UV` is a property of the amplifier and the electrode physics, not of the
wiring fault. `FLAT_UV` now rejects nothing: with the ground correctly pinned
there are no amplifier-floor dropout epochs, and anything from 3 to 60 µV gives
byte-identical output. **It must not be cited as one of the gates doing work.**

## 8. The staging delta band still starts below the hardware high-pass

`BAND_DELTA` (reporting) was moved from 0.5 to 1.0 Hz on 2026-08-08 because the
1.10 Hz acquisition high-pass reaches the saved file. `BAND_DELTA_STAGING` never
got that fix and still starts at 0.5 Hz. Share of the 0.5-4.5 Hz staging band
coming from the attenuated 0.5-1.1 Hz region, first hour of each animal,
2026-08-06:

| animal | share |
|---|---|
| B1 | 4.7 – 5.4 % |
| A2 | 7.7 – 13.6 % |
| A1 | 9.3 – 10.5 % |
| B2 | 12.1 – 16.1 % |

Between a twentieth and a sixth of the staging delta denominator is power that
passed through an uncontrolled attenuation, and it enters the theta over delta
ratio that separates NREM from REM. **Not changed** — see the decisions page.

## 9. The test suite could not fail, and now can

The three existing suites reproduce numbers already published. They prove the code
did not drift. They cannot prove it is right, and **they would have stayed green
through the entire hum-criterion era**, while a floating unreferenced amplifier
input was reported as 100 percent usable EEG.

`tests/test_criterion_falsification.py` is the other half, and it is the software
arm of the positive control this project has owed itself since 2026-08-07. It
writes **real `.xdat` files** with known ground truth, so the whole measurement
chain runs through the ordinary `open_xdat` path — no test double. Thirteen
assertions; half are things the engine must **reject**:

- a steep 1/f channel at a plausible amplitude **is** usable;
- the band-passed wire-free trap **does** beat the bare slope bar, and the guard
  catches it, and `usable()` raises;
- the guard stays silent on scale-free signals;
- the no-ground signature makes the hum criterion raise;
- the slope criterion raises on an EMG role;
- a railed channel is rejected outright;
- the floor scores at about `FLOOR_PERCENTILE`.

Assertions are on **direction and ordering**, not on remembered values. The first
version asserted absolute pass rates and was wrong three times out of seven, for
reasons that were construction errors in the generator rather than faults in the
engine — both are written down in `tests/synth.py` so they are not rediscovered.

⚠️ **One of those was itself a finding.** `falsification_check` reported
`passes = mean < 0.01` while `FLOOR_PERCENTILE = 1` places exactly 1 % of floor
epochs under the threshold **by construction**. The bar was a coin flip on noise.
It is now stated relative to `FLOOR_PERCENTILE`.

---

## What this changes for the paper

1. **The kappa is not merely unrun, it is currently unbuildable from this cohort.**
   Staging begins with an EMG threshold, and no experimental animal has a
   validated EMG. Scoring packs from these animals would spend a human's hours on
   epochs whose staging input is unvalidated, and could not be reused after a fix.
2. **Slope-criterion usable fractions must be quoted with their intervals.** The
   cards now carry them.
3. **`FLAT_UV` and the port-level cluster p-value should both stop being listed as
   checks that are doing work.** Neither can currently fail.
4. **The ECG result is a negative result and should be written as one.** See the
   decisions page.

## Still open, deliberately

- **The kappa**, blocked on the EMG gate above.
- **A wet positive control** — signal injection at the electrode, not in software.
  The synthetic suite covers the analysis chain; it cannot test the hardware path.
- **`BAND_DELTA_STAGING`**, measured above, unchanged by choice.
- **No cohort manifest exists for the 2026-08-07 onward animals**, so rig positions
  are still standing in for animals in that cohort. Blocked on husbandry data.

Related: [[2026-08-11-analysis-stack-consolidation]] ·
`07-decisions/2026-08-07-council-review-of-the-analysis-pipeline.md` ·
`02-procedures/eeg-data-analysis/animal-card-and-verdict-ladder.md`
