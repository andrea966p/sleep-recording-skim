---
name: council-and-pipeline-fixes
description: "2026-08-07/08 LLM council review of the analysis pipeline, IIIS Tsukuba check, Fix 1 (min bout) with the raw-vs-smoothed split, Otsu sweep. Rules: 4 of 5 physiology checks cannot fail; never call circadian threshold-independent; never tune to r@1min."
metadata:
  type: project
---

Council 2026-08-07 (5 advisors + anonymised review) and fixes 2026-08-08 (min-bout 3 epochs, IIIS alignment, Otsu sweep, kappa harness). Biggest findings: selection bias (QC rejects on contact, contact is movement, movement is state); only negative controls exist; accuracy is unmeasured (no kappa yet); "modernise the staging" REJECTED as busywork at n=2. A +-25 % shift in D2's Otsu cut moves asleep-in-light from 23 % to 89 %.

Details: [[2026-08-07-council-review-of-the-analysis-pipeline]]; decision rules and the kappa SOP in [[blind-scoring-and-kappa]]

🛑 STOP reporting "physiology 5/5" as validation (4 of 5 checks cannot fail). 🛑 NEVER call the circadian result threshold-independent: always quote the Otsu-sweep swing beside the number. 🛑 NEVER choose a threshold that maximises `r@1min` (circular); choose it by agreement with a human scorer. Persistence and REM-order are computed on `lab_raw` BEFORE min-bout smoothing (smoothing inflates r by construction). The 12 s / 3-epoch min-bout rule is a HOUSE CONVENTION: never attribute it to IIIS. 🛑 Do not swap the REM rule before kappa; never report a REM share.
