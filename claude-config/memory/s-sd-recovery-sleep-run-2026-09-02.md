---
name: s-sd-recovery-sleep-run-2026-09-02
description: "S-SD terminal recovery-sleep endpoint 2026-09-02/03 (unrepeatable, animals sampled): n = 0 scoreable at every S-SD timepoint; D2 EMG has no muscle-band modulation. Detail in the vault"
metadata: 
  node_type: memory
  type: project
  originSessionId: 96a1ed89-9db0-4f3f-bf96-57a4fbc53432
  modified: 2026-10-22T00:00:00.000Z
---

Wed 2026-09-02 13:00 to Thu 09-03 09:00, 20.0 h, file `allego_2__uid0902-13-00-28` (75.7 GB); CSD finished across the window and the animals were SAMPLED Thursday 13:00, so the run is UNREPEATABLE. A bench re-seat on 09-01 fixed all eight chip grounds. Outcome 2026-09-26: n = 0 scoreable at every S-SD timepoint; D2 / HLBSSD18 passes rung 2 but its EMG has no muscle-band modulation (not proven dead). The 10-06 EMG rescue later gave S-SD paired n = 1 (HLBSSD15).

Details: [[2026-09-02-S-SD-recovery-sleep]] · [[2026-10-06-S-SD-EMG-rescue-between-harmonics]] · [[weak-chip-ground-hides-as-electrode-failure]] · [[w-sd-recovery-sleep-run-2026-08-27]]

- 🔑 Always write window + weekday + protocol state with a recovery run (this one is after the protocol; W-SD 08-27 sat after the penultimate bout).
- 🛑 No usable percentage may be quoted from 8-QC-epoch files (the two 09-01 re-screens). `FLOOR_MIN_HUM_UV = 800` let a physically ungrounded D2 through at 1052 uV (4th recording where 800 is too low); 2000 proposed, not applied.
- `allego_0__uid0829-08-34-39` (59.2 h, 223 GB) is NOT ours (no such run): use no number from it.
- Judge D1 on rms and slope, never its lf/hf ratio (its own floor is contaminated). The pre-flight screen GATES an unrepeatable run: go/no-go was AMBER (n = 2 guaranteed, up to 5), a 10-min re-screen gates the start, every chip floor must read >= 2000 uV.
