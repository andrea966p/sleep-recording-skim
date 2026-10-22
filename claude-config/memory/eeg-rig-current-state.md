---
name: eeg-rig-current-state
description: "STALE rig-state page of 2026-08-03/04: only the hard rules are kept here (never reseat, no surgeries, stop quoting ~6% yield, never report REM %, signals already bipolar). Channel law, signatures and runs are in the vault."
metadata: 
  node_type: memory
  type: project
  originSessionId: 73d8f40f-8fe5-4e49-9c74-3b734c900c35
  modified: 2026-08-04T07:57:03.809Z
---

> **STALE (2026-10-22), DELETION PROPOSED once the rules below are homed elsewhere.** The banner calling "movement-dependent contact the root cause" is contradicted ([[2026-08-04-movement-dependent-contact]]: the movement test failed the same day, vault ER-1) and "~10.4 scoreable mouse-hours, only one recording" is time-superseded (ER-14). The channel law and the three-signature table are in [[CANONICAL-allego-channel-selection]], the runs in [[2026-08-03-two-8-mouse-runs]], the hard rules in [[_eeg-rig-hub]].

## Hard rules, never violate

- 🛑 **NEVER SUGGEST "RESEATING" AN ELECTRODE/EMG WIRE: IMPOSSIBLE AFTER IMPLANTATION.** Only animal-side option = change tether = ISOFLURANE, RUINS THE BATCH. Hierarchy: (1) FREE = rig-side of the slip ring; (2) expensive = tether; (3) impossible = implant, new mice.
- 🛑 **"Make new mice" is SUPERSEDED: DO NOT schedule surgeries.**
- 🛑 **STOP QUOTING "~6% yield".** Both early runs were commissioning tests, 2-6 d early vs our own >= 14 d SOP and ~1 d vs >= 7 d habituation. C1 is MORE impressive for it.
- 🔴 **REM NOT RELIABLY SEPARABLE: never report a REM share.** Report WAKE vs NREM + REM-entry-from-NREM only.
- **Signals are ALREADY bipolar: NEVER subtract EEG from EMG.**
- Chip = RHD2216 bipolar, REF empty by design. Bottom SPI socket ONLY (top dead by design on XDAQ Core, DON'T RMA). 8-headstage ceiling is a HARD Core limit. ONE mouse per headstage.

- 🛑 **2026-07-15 "first sleep biology" (td_sep −0.65) RETRACTED** — clipping artifact, 1/493 clean epochs, flips to +0.63 when railed epochs excluded. `earthing-60hz-hum-fix.md` retracted entirely (wrong device).
- 🛑 **Frontal-sinus hypothesis DROPPED** (built on the wrong channel map).
