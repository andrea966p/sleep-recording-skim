---
name: project_first_headstage_bringup
description: "First headstage bring-up RESOLVED 2026-06-19: root cause was the wrong Allego mode (SMARTBOX_PRO reports priSigs=0), never hardware. Full record in the vault; keeps the mode lesson and the Stream-not-Record rule"
metadata: 
  node_type: memory
  type: project
  originSessionId: 68182adf-7c89-4b69-97a8-4783530bdd8b
---

Resolved 2026-06-19: the headstage was detected (Port D, `priSigs=32`) as soon as Allego was switched from `SMARTBOX_PRO` (reports `priSigs=0` for this hardware) to "XDAQ One (G1) with XR Headstage" (`XDAQ_ONE_REC`). The 2-day teardown (DMM 3.56 V, cables, adapters, ports, C3442) chased a false trail; hardware was always fine. Escalation emails were drafted but NOT sent.

Details: [[first-headstage-connection]] · [[signal-mapping-guide]] · [[radiens-software-reference]] (Allego has no per-channel rename; XDAT is sorted by `pri_N`)

- 🔑 Controller-connects is not correct-mode; Allego modes cannot be enumerated from the log (it lists only modes ever selected).
- 🔴 `csv2sensor` custom maps must list ALL 32 native channels (headstage size = row count, natives 0..N-1) or every site reads `no-site`/-23.
- Use `Stream`, not `Record`, for checks (Record triggers the session daemon / video session). Retracted since: the 2-mice-on-one-headstage map (see the vault banner).
- Related: [[project_hardware_sync_neuronexus_reply]] · [[xdaq-core-gen1-ubuntu-driver]]
