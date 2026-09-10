---
name: cohort-identity-every-run-is-new-mice
description: "Every recording is a NEW cohort of mice unless the user says otherwise; rig positions are not animal identities and nothing carries across runs"
metadata:
  type: feedback
---

🔴⭐⭐⭐ **DEFAULT ASSUMPTION: EVERY RUN HAS NEW MICE.** Stated by the user on 2026-08-18. A recording is a fresh cohort of freshly operated animals unless the user explicitly says an animal is the same one. The 8 positions of `allego_0__uid0818-18-56-33` are **8 newly operated mice, independent of every earlier cohort**.

🛑 **A RIG POSITION IS NOT AN ANIMAL.** `A1`, `B2`, `D2` name a port and slot on the amplifier, nothing more. Two recordings both labelled "D2" are two different mice by default.

🛑 **NO CROSS-RUN CARRY-OVER OF ANIMAL FACTS.** Never open a new run's analysis with "A2 is the good control" or "D2 was fixed by the arm C tether". Those statements belong to the cohort they were measured on and expire with it. [[a2-control-48h-reference-profile]] is a historical single animal, **not a standing reference mouse**; [[overnight-two-animals-tether-is-the-fix]] and [[ground-fix-worked-2026-08-08]] describe animals that are gone.

✅ **WHAT DOES CARRY ACROSS RUNS: THE HARDWARE, NOT THE ANIMALS.** Wire-free amplifier inputs, per-chip 60 Hz floor, headstage grounding, tether arms, channel law, thresholds and criteria are rig properties and are comparable between files. That is why the per-chip floor comparison across `uid0814` / `uid0816` / `uid0818` is legitimate even though the mice differ: it measures headstage grounding, not biology.

**Why:** every cohort so far has been replaced wholesale after a few days, and treating a position label as an animal has already published two mice as one (the B1a/B1b case in `cohorts/HLB-fem-profsurgery-troubleshooting.yaml`). Carrying a prior animal in as a reference smuggles an expectation into a fresh cohort and makes a bad run look explainable.

**How to apply:** at the start of any analysis, treat the file's animals as unknown and unrelated to anything earlier. Judge every channel against the wire-free floor **in that same file**. Ask the user for animal ids, surgery dates and tether arms rather than inferring them from a previous manifest. Only merge two runs into one animal's history when the user says they are the same animal. See [[animal-card-verdict-ladder]] and [[recording-2026-08-18-eight-new-mice]].
