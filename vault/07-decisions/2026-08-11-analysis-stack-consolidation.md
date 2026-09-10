# Analysis stack consolidation: the choices, 2026-08-11

Choices only. The measurements behind every one of them are in
`05-experiments/completed/2026-08-11-analysis-stack-audit-measurements.md`.

Context: an LLM council reviewed the analysis stack on 2026-08-09/10. Its findings
were then checked against the code and the data. Several did not survive that
check; several things it never saw did not survive either. These are the decisions
taken.

---

## D1. Delete the legacy "subtract offline" half of the repo

**Decision.** Deleted `core/config.py`, `core/dsp.py`, `core/channel_map.py`,
`core/xdat_io.py`, `sleep/`, `convert/to_edf.py`, `qc/qc_scan.py`, `examples/`.

**Why.** They implemented a four-rows-per-mouse model and differenced offline, so
their "EEG" was EEG minus EMG and their "EMG" was one empty pad minus another.
They carried a second constants file that also claimed to be the single source of
truth and disagreed on three bands. `convert/to_edf.py` labelled its output
"scorer-ready EDF+".

**Alternative rejected: quarantine in a folder.** It leaves code a future reader
can still run by accident, which is the failure mode being fixed, not a smaller
version of it.

**Cost accepted.** MATLAB export was the only unique capability in that half.
`convert/to_mat_csv.py` was rewritten against stage 2 output — it now copies the
already-bipolar channels and derives nothing. EDF export was already duplicated,
correctly, by `pipeline/stage4_export_edf.py`.

**Also deleted:** `qc/usable_fraction_vs_floor.py`,
`qc/usable_fraction_vs_floor_ecg.py`, `qc/plot_usable_timeline.py` — three
surviving independent copies of the usable-fraction criterion. `core/criteria.py`
claimed to be "the only one" and was not. It is now.

## D2. Keep `SLOPE_BAND_HZ = (1.0, 40.0)`; enforce the precondition instead

**Decision.** The band is unchanged. A band-limit guard was added that refuses the
slope criterion on any channel whose spectrum is not scale free.

**Why not narrow it.** The band is genuinely vulnerable — a wire-free input
band-passed to 0.5-30 Hz scores 100 % usable, because the 30 Hz corner sits inside
the measurement band. But on real data the criterion reads the **raw** memmap and
nothing is filtered. Moving to 2-20 Hz flips **no verdict**, leaves the floor at
0.00 % either way, and costs working animals 12 to 16 points. That is restating
every published number to buy nothing.

**Why a guard rather than a comment.** The vulnerability is one line away at all
times: `chain()` lives in the same module and exists to filter. A documented
precondition that a caller must remember is the same class of thing as the hum
criterion, which was also correct-if-you-remembered.

**The false claim was corrected in place.** Both `core/qc_thresholds.py` and
`core/criteria.py` asserted "filtering cannot manufacture slope, which is exactly
why this criterion survives the trap". It does manufacture slope. The sentence is
replaced with the measurement.

## D3. Retire ECG

**Decision.** ECG is a negative result. Deleted `qc/cardiac_comb_test.py` and
`qc/heartbeat_on_quiet_stretch.py`. `qc/emg_ecg_forensics.py` deleted too — it was
already dead, reading an `.npz` from a script removed under D1 — after porting its
burstiness test.

**Why delete the detectors rather than keep them.** Keeping a detector for an
absent signal invites someone to run it and find noise. This project has already
withdrawn one set of "CARDIAC" verdicts that turned out to be boundary artefacts.

**The methods sentence, to be used verbatim:**

> ECG was attempted on a third bipolar site per animal and produced no heartbeat
> distinguishable from unwired amplifier inputs recorded simultaneously in the same
> file, in 7 of 7 animals; it is reported as a negative result and no cardiac
> measure is derived.

**What is NOT retired.** `CohortSpec(roles=("eeg","emg","ecg"))` stays. The
2026-08-07 onward recordings physically have a third site, and **the floor must
start at `/4` for those files**. Retiring the measurement does not move the floor.

## D4. Envelope variability emits no pass

**Decision.** The EMG burstiness test is a printed diagnostic. Nothing may gate on
it.

**Why.** A1, which has no ground at all, scores 0.769 against a floor-derived bar
of 0.319 — near the top of the cohort — while D2 reads "flat" despite 63.7 %
usable EEG. A floating input is high impedance and picks up variable interference,
so a test rewarding variability rewards having no electrode.

**Why keep printing it.** "A1 scores bursty" is the evidence that kills the
criterion. Deleting the column would delete the reason it is not used.

## D5. A control may not satisfy the EMG gate

**Decision.** `qc/emg_state_dependence.py` takes `--control` and excludes those
positions from the gate verdict.

**Why.** Run without it, the gate reported "PASSED for 1 animal" — counting A2,
the carried-over control, which is not in the publishable set. A control passing
proves the instrument works; it says nothing about the cohort. Letting it count is
how a cohort with no working EMG reports green.

## D6. The kappa is blocked until an experimental animal passes the EMG gate

**Decision.** Do not build scoring packs from the 2026-08-08 cohort.

**Why.** Staging begins with an EMG threshold. On the full 16.39 h including the
dark phase, no experimental animal reaches state dependence; the best is C2 at
-0.174 overall. Packs built from these animals would spend a human's hours on
epochs whose staging input is unvalidated, and could not be reused after a fix.

**This reverses the working assumption** that the kappa was simply the next thing
to schedule. It is not next; it is downstream of an unmet precondition.

**The lead to pursue instead:** C2's dark phase reaches -0.332 on 50 minutes, the
only re-pinned animal showing state coupling anywhere. A longer dark-phase
recording on C2 is the cheapest test of whether the cohort is recoverable.

## D7. `BAND_DELTA_STAGING` stays at 0.5 Hz, under protest, and recorded

**Decision.** Not changed. Measured, documented at the constant, flagged as open.

**Why not changed.** Moving it re-scores every recording and moves published
architecture numbers, and the REM cut is a per-animal percentile that will partly
absorb the change. That is a scientific decision with a paper attached, not a
cleanup, and slipping it in during a refactor is how a number changes without
anyone deciding it should.

**Why it is nonetheless wrong.** Its lower edge sits below the 1.10 Hz acquisition
high-pass, which is the exact defect that moved `BAND_DELTA` from 0.5 to 1.0 on
2026-08-08; the staging band never got that fix. Between 4.7 % and 16.1 % of the
staging delta denominator is power that passed through an uncontrolled
attenuation. It is also **the only constant in the file with no external source** —
the Japanese tool has no lower edge at all, so 0.5 was ours.

**When it is changed**, the honest comparison is a re-scored hypnogram at both
edges with the kappa packs held constant.

## D8. Make the repo installable and the contract portable

**Decision.** Added `pyproject.toml` and `core/paths.py`. Removed 24 of 26
`sys.path.insert` calls and all 31 hardcoded `/home/skimlab` paths. Deleted the
`pipeline/qc_thresholds.py` shim.

**Why this is not cosmetic.** `tests/test_criteria_regression.py` — the file the
README calls "the contract" — hardcoded one laptop's home directory. **A contract
only one machine can check is not a contract**, and this project's entire argument
is that it does not ask to be taken on trust. Every location is now an environment
variable defaulting to its historical value, so nothing changed here and
everything is overridable elsewhere.

**A skip must not read like a pass.** The regression suite previously printed one
line and exited 0 when the data was absent. It now prints an unmissable block
naming the variable to set.

**The two remaining `sys.path.insert` calls** point at the scientific-visualization
skill, deliberately outside the package.

## D9. Add a test suite that is allowed to fail

**Decision.** `tests/test_criterion_falsification.py` plus `tests/synth.py`. It
writes real `.xdat` files with ground truth fixed before the engine runs, and half
its cases are things the engine must reject.

**Why.** The three existing suites reproduce numbers already published, so
"any movement is a bug" is correct for them — and they **would have stayed green
through the entire hum-criterion era**. A test that can only pass is not evidence.

**Assertions are on direction and ordering, never on remembered values.** A
falsification test that pins a number is a regression test wearing a different hat.

**This is the software arm of the positive control** owed since 2026-08-07. It does
not discharge the obligation: it tests the analysis chain, not the hardware path.
A wet injection at the electrode is still owed.

## D10. `falsification_check`'s bar is stated relative to `FLOOR_PERCENTILE`

**Decision.** `passes` changed from `mean < 0.01` to `mean <= 3 × FLOOR_PERCENTILE/100`.

**Why.** The floor is scored against its own 1st percentile, so about 1 % of floor
epochs fall below it **by construction**. The old bar was a coin flip on noise and
reported failure for a floor behaving exactly as it must.

---

## Not decided here, and why

- **A cohort manifest for the 2026-08-07 onward animals.** Blocked on husbandry
  data: ear tags, surgery dates, ages, and which physical mouse sits at each
  position. Until it exists, rig positions stand in for animals in that cohort,
  which is the error `cohorts/` was built to prevent, and A1 cannot be recorded
  properly as an opportunistic no-ground observation rather than a "control".
- **Whether to reframe the paper as rig validation rather than sleep architecture.**
  The council argued for it strongly and the argument is good, but it is the
  professor's call, not a refactor.

## One operational risk

**The repo has zero git commits.** 10,387 lines are untracked and one `rm` from
gone. The pre-audit tree is backed up only in a session scratchpad, which is
temporary. This should be fixed before anything else.

Related: [[2026-08-11-analysis-stack-audit-measurements]] ·
`07-decisions/2026-08-07-council-review-of-the-analysis-pipeline.md` ·
`07-decisions/2026-08-07-rig-specification-and-analysis-method.md`
