---
name: animal-card-verdict-ladder
description: "The animal card + six-rung verdict ladder is the analysis entry point; core/qc_thresholds.py and core/criteria.py are the only engines. The 'three suites all green = contract' claim is stale (2026-10-22)."
metadata: 
  node_type: memory
  type: project
  originSessionId: 9e891ed8-8737-468b-92b3-91e670ec3574
  modified: 2026-08-09T02:15:54.458Z
---

**Built 2026-08-09.** One A4 card + JSON per animal-recording. Rungs: 0 FILE, 1 IDENTITY, 2 CONNECTION, 3 SCOREABILITY, 4 ARCHITECTURE (always PROVISIONAL until a kappa), 5 EXPORT; a rung whose predecessor failed reads BLOCKED and draws no panel; INSUFFICIENT ("could not ask") is distinct from FAIL. `core/qc_thresholds.py` is the ONLY constants file and `core/criteria.py` the ONLY usable-fraction engine. Rung 2 gates on the LONGEST UNBROKEN BLOCK (>= 15 min), not the total fraction. The animal (cohort manifest `cohorts/*.yaml`), not the rig position, is the key. Hard errors: the HUM criterion is refused when it contradicts SLOPE (EEG roles only); SLOPE is refused on non-EEG roles.

Details: [[animal-card-and-verdict-ladder]]

⚠️ STALE in the original: "three test suites, all green, and they are the contract". On 2026-10-22 the regression and ladder suites verified NOTHING on e10 (their fixtures exist only in S3; vault contradiction EA-2). Any movement in a published number is still a bug to explain, not an improvement, but it cannot be checked by those suites here.
