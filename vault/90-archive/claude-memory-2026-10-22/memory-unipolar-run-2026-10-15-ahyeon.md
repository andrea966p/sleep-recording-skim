---
name: unipolar-run-2026-10-15-ahyeon
description: "ahyeon's 3 unipolar mice (A B C). 10-14 prep: corrected unipolar map, GPIO strip fix, watchdog auto-arm, full 30 h CSVs; old 08-05 map was a TYPO. 10-15 run LOST to hardware: B dropped 23:54 the night before, C lost its reference; console started without re-checking ports."
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

**Scheduled 10-14 20:27 by Andrea:** run `dca84de0cc7a`, batch `test` (intentional: a TEST recording for ahyeon), mice
A B6JF020112, B B6JF020114, C B6JF020113, all basal. Mouse A carries ~3.5-4 mV 60 Hz on all 6 channels (81 % of the
time at 20:19): a known SURGICAL mistake, ahyeon knows why. Do not troubleshoot it. B and C clean (60 Hz 1-3 µV).

**10-min pipeline test 2026-10-14 21:08-21:18 (run `901e16ee8bf8`, batch `10minutes_test`): PASS end to end.**
Start +3.5 s, stop +4.9 s, growth 1.11 GB/h, strip 18 ch (80.77 % smaller), 3 CSVs 598,528 rows, NAS sha256 local=remote,
DONE 41 s after stop, local CSVs removed, info.json qc NOT ASSESSED. Watchdog not exercised (run did not cross :05).
`sig_proc_spec` is ABSENT from this recording's .xdat.json (present on 10-07): verify filters from the DATA spectrum instead.
🔴 **`AllegoClient.get_signals()` returns the VISUALIZATION-FILTERED stream.** With Andrea's 10-300 Hz EMG viz filter on, a
live grab showed delta 1-2 % and flat spectra (I misread it as "mice awake"); the saved file had full < 10 Hz power.
For any live quality check, first ask whether a Software Stage 2 filter is on, or analyse the recorded file.
Also: the console accepts OVERLAPPING schedules (refused only at start, FAILED_START, active run untouched).
Cancel button for SCHEDULED/DRAFT runs added in app.js (uses existing /abort).

**🔴 10-15 RUN LOST: hardware, not software.** Port B dropped off the SPI scan at **10-14 23:54:01 KST** (allegoserver.log
`portB=0`), 9 h before the start. The console started anyway at 09:00 on its creation-time enumeration and recorded A + C only.
Port C's 6 channels went common-mode (r 0.75-0.99, 500-700 µV, 60 Hz ~110 µV vs 2 µV on 10-14), varying with movement:
a lost head reference/ground contact. Andrea stopped it in the Allego GUI at 09:12:57 (773 s); run `dca84de0cc7a` = `FAILED_STOP`,
raw left in `~/radix/data/allego_0__uid1015-09-00-04_*`. Cause per Andrea: the mice loosen the unipolar headstage; the SPI cable runs
to the XDAQ with no counterbalance arm. The 10-14 code changes were audited and are clean (abort = state only, watchdog read-only).
Gap: no live enumeration check at start ⇒ separate session adds check + ntfy alert, still starting the run.
For "did the hardware drop?", grep allegoserver.log `Scanned ports` for per-port counts over time. Journal `04-journal/2026-10/2026-10-15.md`.
