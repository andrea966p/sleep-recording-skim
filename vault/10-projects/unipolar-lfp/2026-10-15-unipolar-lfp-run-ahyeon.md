---
type: experiment
area: unipolar-lfp
status: done
created: 2026-10-22
summary: "ahyeon's 30 h unipolar LFP run of 2026-10-15 was lost to hardware after 13 min: port B left the SPI scan the night before, port C lost its reference; the 10-14 preparation is recorded here"
tags: [experiment, unipolar, lfp, ahyeon, run-lost, console]
promoted-from: "Claude memory unipolar-run-2026-10-15-ahyeon; journals 2026-10-14 and 2026-10-15"
---

# ahyeon's three unipolar mice: preparation 2026-10-14 and the lost run of 2026-10-15

> [!abstract] TL;DR
> Three unipolar mice (one RHD2132 per port A, B, C) were to record for 30 h from 2026-10-15 09:00. The run `dca84de0cc7a` recorded only A and C for 773 s and ended `FAILED_STOP`.
> The cause was hardware: port B dropped off the SPI scan at 2026-10-14 23:54:01, and port C lost its head reference or ground contact. Nothing in the console or Allego logs shows software acting on the ports.
> Written 2026-10-22 from [[2026-10-14]], [[2026-10-15]] and the Claude memory file of the same run; the figures below are the journals' own.

## The run as planned
- **Owner and mice:** owner `ahyeon` (not Andrea's mice); three unipolar RHD2132 headstages, one per port A, B, C, port D empty. Scheduled by Andrea in the console UI at 2026-10-14 20:27: start 2026-10-15 09:00, stop 2026-10-16 15:00 (30 h).
- **Run and batch:** run `dca84de0cc7a`, batch `test` (intentional: a test recording for ahyeon). Mice A B6JF020112, B B6JF020114, C B6JF020113, all basal.
- **Layout and setting:** layout `4mice_unipolar_lfp` (ahyeon's default since 10-14), setting `eeg_emg_lfp`, `qc: none`, so QC reads "not applicable" and `info.json` carries `NOT ASSESSED`.
- **Output:** one full 30 h CSV per mouse (Andrea's choice; the console never cuts 24 h windows), single-ended columns `EMG_L, LFP_TGT, LFP_REF, EMG_R, EEG_P, EEG_F`. NAS path `02_Data_Sleep/ahyeon/<batch>/Baseline/20261015_<mouse>_B/`. ahyeon uses her own tools, so SleepStager compatibility was not needed.

## Preparation on 2026-10-14
Details are in [[2026-10-14]]; the points a later run needs:
- 🔴 **The unipolar map on file since 2026-08-05 was a typo.** The only correct map is `/18` EMG left, `/19` LFP target, `/20` LFP reference, `/21` EMG right, `/22` EEG parietal, `/23` EEG frontal. Fixed in place in `eeg_emg_lfp` in `eeg-recorder/config/users.yaml`; no stored run had used the old one. See [[2026-08-05-unipolar-lfp-mouse-reference]] and [[rig-layout-and-recording-settings]].
- **Splitter:** a C3442 with ONE chip on it still enumerates 32 channels per port (A, B, C = 32 each, measured live), so it is declared as no splitter.
- **Live check, read-only, 18:34:** Allego healthy (XDAQ_ONE_REC, 1000 Hz, stream 1.00x); the 18 selected channels carry signal, rms 22-336 µV, 60 Hz 1-4 µV (A/21 10.6 µV). The grounding fix of 2026-10-07 held.
- **`get_signals()` returns only the SELECTED channels**, so unused inputs cannot be probed live without changing the selection.
- **GPIO strip fix:** `rig.gpio_header_connected: false` makes the console pass `--gpio-never-connected`, which prevents a repeat of the 10-08 `FAILED_STRIP` on floating `din_1`. Set it to `true` when the XDAQ-to-Pi sync is wired.
- **Watchdog:** `recording-watchdog-cron.sh` now arms itself on console runs (sandbox-tested on e10 over 10 scenarios). The `stop_at` endpoint of the same worktree was not brought in.
- **Pull and restart:** e10 needs `./skim pull` and `sudo systemctl restart eeg-recorder` before the run is created, because a run snapshots its roles at creation.
- **Mouse A:** about 3.4 mV of 60 Hz on all channels (3.5-4 mV and 81 % of the time at 20:19), a known surgical mistake that ahyeon knows about. Not to be troubleshooted. B and C are clean (60 Hz 1-3 µV; within-pair raw r 0.39-0.77; between mice r = 0.00).
- **10 minute rehearsal, 21:08-21:18, run `901e16ee8bf8`, batch `10minutes_test`: PASS end to end.** Start +3.5 s, stop +4.9 s, growth 1.11 GB/h, strip 18 channels kept (80.77 % smaller), 3 CSVs of 598,528 rows, NAS sha256 equal, DONE 41 s after the stop. The watchdog was not exercised (the run did not cross :05). A first attempt dated 10-15 by mistake was accepted although it overlaps the 30 h run; it was cancelled, and a cancel button for scheduled runs was added.
- 🔴 **`AllegoClient.get_signals()` returns the visualization-filtered stream.** With a 10-300 Hz EMG display filter on, a live grab showed almost no power below 10 Hz while the saved file had all of it. For a live quality check, ask first whether a Software Stage 2 filter is on, or analyse the recorded file. This recording's `.xdat.json` has no `sig_proc_spec`, so the data spectrum is the proof.

## What happened on 2026-10-15
| KST | Event |
|---|---|
| 10-14 21:18 | The rehearsal ends; A, B and C each enumerate 32 channels. |
| **10-14 23:54:01** | **Port B drops to 0 channels** in Allego's autoscan (`allegoserver.log`, `portB=0`). No console action, cron job or user session was active. |
| 10-15 09:00:01 | The pre-stream scan reads `portA=32 portB=0 portC=32`. The console started anyway on the enumeration stored at creation. |
| 09:00:07 | Recording `allego_0__uid1015-09-00-04` starts with 70 signals (A + C + GPIO), growth 0.76 GB/h. |
| 09:12:57 | Andrea stops it in the Allego GUI after seeing B gone and C "mirrored" (773 s). |
| 09:14:10-19 | Allego is closed and relaunched; the console's stop came after, so the run is `FAILED_STOP`. No strip, CSV or upload. |

- **Port C, channels 18-23:** rms 500-700 µV (32-73 µV on 10-14), median pairwise r 0.75-0.99 (about 0 on 10-14), 60 Hz about 110 µV (2.3 µV on 10-14), and the rms of ch 22 moves with movement (335 to 950 to 237 µV). One large common signal carrying mains on every electrode is the pattern of a **lost reference or ground contact at the head connector**, not of the electrodes. Inputs 0-7 and 24-31 stay near 3 µV.
- **Cause (Andrea):** the mice loosen the unipolar headstages; the SPI cable runs straight to the XDAQ with no counterbalance arm or commutator.
- **Code audit of the 10-14 changes:** the cancel button changes run state only and is refused for a started run; the watchdog reads `get_status()` only; the map, strip and uploader changes run after the recording; the console's only Allego writes are `set_streaming` and `set_recording` at the scheduled times. Nothing in software can drop a headstage from the SPI scan.
- **Gap found and closed in code:** the scheduler did not compare the live enumeration with the declared layout at start. Commit `3793258` makes a missing port warn (run results, red tag, ntfy) but never block the start; see [[eeg-recording-console]].
- **To find out whether hardware dropped:** grep `allegoserver.log` for `Scanned ports` and read the per-port counts over time.
- **State at about 09:35:** Allego up with A = 32, B missing, C = 32, `R_OFF`; the raw 13 min file is in `~/radix/data/allego_0__uid1015-09-00-04_*`, untouched, and holds no B.

## Open
- [ ] ahyeon: reconnect B and C at the head, then decide whether to reschedule. Before any new run confirm that A, B and C each enumerate 32 on the console's state panel.
- [ ] For tethered unipolar runs: a counterbalance arm or commutator to take the cable pull off the head connector.
- [ ] Decide what to do with run `dca84de0cc7a`: abandon it (`/abort` accepts `FAILED_*`) or post-process the 13 min of A + C.
- [ ] Optional unipolar floor check from sites /9-/17 + /24 (about 10 sites read as true open inputs on an empty unipolar headstage, uid1001-16-48-09 port C), which the lost run cannot supply.
- [ ] NAS `02_Data_Sleep/ahyeon/10minutes_test/`: delete only when Andrea decides.
