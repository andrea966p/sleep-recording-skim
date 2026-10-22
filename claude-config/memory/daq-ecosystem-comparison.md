---
name: daq-ecosystem-comparison
description: "3-way DAQ comparison (XDAQ vs Open Ephys vs Intan) for 32 mice, revised 2026-07-28 to no-Allego / OE-GUI everywhere / complete-rig BOM. VAULT-ONLY (Kontex quote confidentiality). Older 'Intan strongest' reading is stale."
metadata:
  node_type: memory
  type: project
  originSessionId: d82d08e4-aa65-41f6-9c48-c49e1066f262
  modified: 2026-07-28T01:05:27.763Z
---

Revised 2026-07-28 on Andrea's four ground rules: (1) NO Allego licence, drive all three ecosystems with the free Open Ephys GUI; (2) price the COMPLETE rig; (3) one PC is enough (the "2 PCs" was an Allego licence artefact); (4) our code/daemon excluded from the evaluation. Consequences: per-mouse independent start/stop is gone (OE start/stop is GLOBAL), record continuously and slice offline; commutators dominate the budget (OEPS-7761 EUR 2,595 x 32 = EUR 83,040); OE Record Node syncs multiple boards online off a shared TTL.

Details: [[2026-07-24-daq-32-mouse-final-comparison]]

🛑 VAULT-ONLY: Kontex quote confidentiality, never publish this comparison as an Artifact. ⚠️ The original memory's "Intan direct now looks STRONGEST" is older than the vault's section 6.3 (XDAQ back in the lead after KC's 2026-07-28 confirmation): do not repeat it. Still gated behind surgical yield; council only after the gates.
