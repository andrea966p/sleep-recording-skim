---
name: electrode-failure-literature
description: "Six papers on mouse EEG electrode impedance and failure (Hsieh 2024: 82 % of epidural preps lose an electrode in 3 weeks): real literature, NOT our failure mode. Rules: don't cite Kappenman for our hum result, stop quoting ~6 % yield."
metadata: 
  node_type: memory
  type: reference
  originSessionId: 21a6d0c8-6c66-4695-9945-f1f3d834eb58
  modified: 2026-08-03T02:56:39.040Z
---

Hsieh et al., eNeuro 2024: 82 % of epidural 0.1 mm preparations lost at least one electrode within 3 weeks (MXene 18 %). It is real literature but it does NOT explain our failures: the electrodes were later proven good (B1 0.052 MOhm, D2 fully recovered; [[2026-08-04-movement-dependent-contact]]). Literature impedance at 1 kHz is 10-50 kohm for screws; ours is poor by that standard. Only the positive input of each bipolar pair has ever been measured ([[impedance-sweep-register]]).

Details: [[electrode-failure-and-impedance-literature]]

⚠️ DO NOT CITE Kappenman & Luck 2010 for our hum-vs-contact result (they compared 5 vs 50 kohm in a shielded room; we compare connected vs OPEN circuit): our bimodal 9-90 / 1000-4700 uV separation is our own empirical finding. 🛑 STOP QUOTING "~6% yield": it describes an under-habituated cohort recorded early during commissioning, not the rig. 🛑 The frontal-sinus hypothesis is DROPPED (it was built on the wrong channel map). The cheapest decisive experiment, re-running animals at >= 14 d post-op / >= 7 d tethered, was the protocol gap.
