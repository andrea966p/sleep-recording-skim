---
name: tether-soldered-duty-cycle-result
description: "2026-08-05 tether comparison: the soldered resin tether took B1's EEG duty cycle 45 to 100 percent; B1 later euthanised (electrode detached); the arm C 'harm' claim was retracted; gRPC impedance sweeps automated. Detail in the vault"
metadata: 
  node_type: memory
  type: project
  originSessionId: 1c8ce7c5-ec36-4595-9a71-7100cbae80c1
  modified: 2026-10-22T00:00:00.000Z
---

2026-08-05 on B1 (within animal, 20 sweeps per arm, duty cycle = fraction below 2 MOhm): original heatshrink 45 % to short SOLDERED + RESIN tether 100 % (p = 0.0001). B1 was euthanised the same day because its skull electrode DETACHED (not an anaesthesia death; colony n = 7), so the arm that would isolate the slip ring is lost. Arm C (D2, long custom tether, slip ring removed) read 66.7 to 0.0 % and was called "harm": RETRACTED, D2 went to 87.9 % usable overnight (the 21-min block caught one long open state): [[overnight-two-animals-tether-is-the-fix]].

Details: [[2026-08-05-tether-comparison]] (arm C retraction in section 14) · [[impedance-sweep-register]] · [[2026-08-07-overnight-recording-two-animals-work]]

- 🛑 Do NOT say "the soldered tether works" from the 08-05 swap alone: it bundled construction + connector re-seat + an isoflurane episode. Never report arm C harm as established.
- Vault gap (journal 2026-08-05 only): impedance sweeps via `AllegoCore.GetIntanImpedance(port)` on `127.0.0.1:50051` (~30 s, REAL measurement, Cognito token from `radiens.utils.interceptors`); `radiens` 4.0.0 has no impedance method (`radiens-core` 0.0.8 does). Silent traps: the `port` arg is ignored, `ntvChanIdx` is GLOBAL (always run `remap_channels.py` after any port change), and phase is NOT a reliable open/connected classifier (use magnitude).
- Data hygiene: `armC-long-direct-noslipring/` holds THREE conditions (a folder glob scores 41, not 40).
- Related: [[movement-dependent-contact-root-cause]] · [[dmm-continuity-test-result]]
- 🛑 Do NOT revert D2 under anaesthesia same-day (08-06 rule; B1 was lost the day before). `radiens-core` 0.0.8 exposes `get_intan_impedance(port)` officially and should be adopted in a SEPARATE venv, never `/opt/neurosurveillance/venv`.
