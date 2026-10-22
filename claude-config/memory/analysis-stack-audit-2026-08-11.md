---
name: analysis-stack-audit-2026-08-11
description: "Council audit + verification of the analysis stack: legacy backwards pipeline deleted, slope criterion's justification falsified and guarded, EMG gate failed by every experimental animal, floor sampling error quantified"
metadata: 
  node_type: memory
  type: project
  originSessionId: 5a89f8f2-b656-4a31-927c-b16a644cf89f
  modified: 2026-08-11T00:58:02.113Z
---

Audit 2026-08-10/11. Council reviewed the stack; I then checked its claims against
code and data. **Evidence:** `20-areas/eeg-analysis/2026-08-11-analysis-stack-audit-measurements.md`.
**Choices:** `20-areas/eeg-analysis/2026-08-11-analysis-stack-consolidation.md`.

🔴🔴 **THE EMG GATE FAILS FOR EVERY EXPERIMENTAL ANIMAL**, full 16.39 h of
`allego_0__uid0808-16-17-36` **including the dark phase** (previously unscored).
r(EMG rms, EEG delta) over 1-min bins, usable-EEG minutes only:
**A2 (carried-over CONTROL) −0.734** · C2 −0.174 · B2 −0.156 · D1 +0.023 ·
D2 +0.010 · A1/B1/C1 **no usable EEG minutes at all**. Dark phase did NOT rescue
it. ⇒ **THE KAPPA IS NOT "NEXT", IT IS BLOCKED** — staging starts with an EMG
threshold, so packs from this cohort would burn a human's hours on unvalidated
labels and be unreusable after a fix. ⭐ **Only lead: C2 dark −0.332 (n=50 min)** —
a longer dark-phase run on C2 is the cheapest test of recoverability.
Script `qc/emg_state_dependence.py` (takes `--control`; a control may NOT satisfy
the gate — it reported a false "PASSED" counting A2 before that was added).

🔴🔴 **"FILTERING CANNOT MANUFACTURE SLOPE" IS FALSE.** It was written into
`qc_thresholds.py` AND `criteria.py` as the reason slope is safe. Measured: white
noise band-passed 0.5-30 Hz reads slope **−1.08** over 1-40 Hz (raw 0.00, real EEG
−1.81) and scores **100% usable**. The 30 Hz corner sits inside the band. ✅ **Band
NOT narrowed** — on real data 2-20 Hz flips no verdict, floor is 0.00% either way,
and working animals lose 12-16 pts. ✅ **Guard added instead:** a power law is
scale free, slope(25-45) − slope(1-25) ≈ 0; a filter corner is not. Scale-free
cases ±0.11, band-limited −2.1 to −11.3, **bar −1.0**. Real data reads +0.29 to
+1.02 ⇒ silent on genuine recordings.

🔴 **A SECOND, BACKWARDS PIPELINE WAS LIVE IN THE REPO** (council never saw it).
`core/config.py`+`dsp.py`+`channel_map.py` used 4-rows-per-mouse **subtract
offline** ⇒ "EEG" = EEG−EMG, "EMG" = pad−pad, plus a 2nd constants file
disagreeing on delta/EMG bands and rail. Fed `convert/to_edf.py` ("scorer-ready
EDF+") and `examples/run_all.sh`. **No published number affected** (pipeline never
imported it; kappa packs read stage-2). **DELETED**, with `to_mat_csv.py` rewritten
against stage-2. Also deleted the **3 surviving copies** of the usable-fraction
criterion — `criteria.py`'s "only one" claim is now true.

⭐⭐ **FLOOR SAMPLING ERROR IS HUGE ON SLOPE, ZERO ON HUM.** Bootstrap over
**SITES** (epochs within a site are autocorrelated): hum threshold moves fractions
**0.0 pts**; **slope: B1 83.1% → [53.1, 98.0], D2 75.2% → [48.9, 86.2]**. Slope is
the criterion now in use ⇒ **the interim 57.5/71.6/70.3/63.7% carry ~±20 pts from
the floor alone.** ✅ Does not move a verdict — rung 2 gates on longest unbroken
block, not fraction. Cards now carry the intervals.

🔴 **ENVELOPE VARIABILITY (burst_cv) DOES NOT VALIDATE EMG HERE.** A1 (NO GROUND)
scores 0.769 vs bar 0.319, near the top; D2 reads "flat" at 0.316 despite 63.7%
usable EEG. Floating = high-Z = variable interference ⇒ the hum criterion's failure
in a new costume. **Printed as diagnostic, emits no pass.**

✅ **CONSTANTS RE-DERIVED POST-RE-PIN** (8 h, 2026-08-08): `OPEN_UV` survives —
valley **149.4** vs constant 150.0. ⚠️ **`FLAT_UV` IS NOW INERT** — 0.00% of epochs
fall below it, p10 = 63.8 µV; anything 3-60 µV gives identical output. **Stop
citing it as a gate doing work.**

⚠️ **`BAND_DELTA_STAGING` still starts at 0.5 Hz, below the 1.10 Hz hardware
high-pass** — 4.7-16.1% of the staging delta denominator. `BAND_DELTA` got this fix
on 08-08; staging never did. **Measured and documented, deliberately NOT changed**
(moving it re-scores everything). Only constant in the file with **no external
source**.

⭐ **FOURTH TEST SUITE = the software positive control.** `tests/test_criterion_falsification.py`
+ `tests/synth.py` write **real .xdat files** with truth fixed in advance; half the
cases must be **rejected**. Assertions on **direction/ordering, never pinned
values**. 🔑 The 3 old suites reproduce published numbers and **would have stayed
green through the whole hum-criterion era** — "any movement is a bug" applies to
them, NOT to this one. Still owed: a **wet** injection at the electrode.

🔧 Repo now installable (`pyproject.toml`, `pip install -e .`), `core/paths.py`
holds every location as an env var. **31 hardcoded `/home/skimlab` paths → 0**;
`sys.path.insert` 26 → 2 (both point at the viz skill, outside the package).
🔑 **The regression test hardcoded one laptop's home dir — the "contract" could not
run anywhere else.** Now portable, and a skip prints an unmissable block instead of
exiting 0 quietly. 61 → 54 files, 11,227 → 10,387 lines. 4 suites green.

🛑 **THE REPO HAS ZERO GIT COMMITS.** 10,387 lines untracked.

⛔ **Blocked, needs husbandry data:** no cohort manifest exists for the 2026-08-07
onward animals, so rig positions still stand in for animals there — the exact error
`cohorts/` exists to prevent — and A1 cannot be recorded as an opportunistic
no-ground observation rather than a "control".

Related: [[animal-card-verdict-ladder]] · [[ground-fix-worked-2026-08-08]] ·
[[council-and-pipeline-fixes]] · [[recording-usable-fraction-analysis]] ·
[[ecg-cohort-2026-08-07]]


## From the memory index, trimmed there 2026-10-06 (kept here verbatim)

- 🔴⭐⭐⭐ **[ANALYSIS STACK AUDIT — 2026-08-11](analysis-stack-audit-2026-08-11.md).** "Filtering cannot manufacture slope" is FALSE. Slope fractions carry ±20 pts.
