---
name: unipolar-run-2026-10-15-ahyeon
description: "2026-10-14 prep for ahyeon's 3 unipolar mice (A1 B1 C1, 10-15 09:00 → 10-16 15:00, 30 h): corrected unipolar map, GPIO strip fix, watchdog auto-arm, full 30 h CSVs. The old 08-05 unipolar map was a TYPO."
metadata:
  node_type: memory
  type: project
  originSessionId: d4e35d3a-d8bb-4d52-b115-b0c9c407aedc
  modified: 2026-10-14T09:53:39.707Z
---

**Run:** owner `ahyeon` (not Andrea's mice), 3 unipolar RHD2132, one per port A B C, D empty. Andrea schedules it
in the console UI: start 2026-10-15 09:00, stop 2026-10-16 15:00 (30 h). Layout `4mice_unipolar_lfp` (ahyeon's
default now), setting `eeg_emg_lfp`, `qc: none` ⇒ `qc_not_applicable`, info.json qc `NOT ASSESSED`.

🔴 **The unipolar map on file since 08-05 was Andrea's TYPO.** The only correct map:
`/18 emg_l, /19 lfp_tgt, /20 lfp_ref, /21 emg_r, /22 eeg_p, /23 eeg_f`. The 08-05 page's role names and
pairings ("EEG = A/21−A/22") are wrong labels; read as site numbers only. Fixed in place 10-14 (no stored run used it).

- A C3442 splitter carrying ONE chip still enumerates 32 per port (measured live 10-14) ⇒ declare "no splitter".
- Allego `get_signals()` returns only SELECTED channels; unused inputs cannot be probed live without changing the selection.
- `rig.gpio_header_connected: false` in `users.yaml` ⇒ console passes `--gpio-never-connected` (fixes the 10-08
  FAILED_STRIP on floating din_1). Flip to `true` when the XDAQ→Pi sync is wired [[project_hardware_sync_neuronexus_reply]].
- Watchdog `recording-watchdog-cron.sh` now auto-arms on console runs (10-02 fix, sandbox-tested 10/10, deployed with this push).
- CSVs: ONE full 30 h CSV per mouse (Andrea's choice; console never windows), 6 single-ended columns
  `EMG_L,LFP_TGT,LFP_REF,EMG_R,EEG_P,EEG_F`; SleepStager can't read them and does not need to (ahyeon uses own tools).
- e10 needs `./skim pull` + `sudo systemctl restart eeg-recorder` BEFORE the run is created: a run snapshots its
  roles at creation, so a run made on the old config gets the typo names on its CSV columns.

Vault: journal `04-journal/2026-10/2026-10-14.md`. Related: [[partial-rig-qc-and-unjudgeable-presets]] · [[grounding-fix-2026-10-07-mains-collapsed]]
