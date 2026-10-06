---
name: recording-2026-10-01-noise-4mice-overnight
description: "First overnight of the XDAQ noise series WITH mice: 4 mice A1 A2 B1 B2 (8-core tethers), console run cfdf8ebde0c6, 2026-10-01 21:00 -> 10-02 09:00 (whole dark phase). Placeholder mouse IDs POS-<slot>. A1 and B2 EMG open (implant side)."
metadata:
  type: project
---

# Noise-series overnight, 4 mice, 2026-10-01 21:00 -> 2026-10-02 09:00 KST

Console run **`cfdf8ebde0c6`** (⚠️ stop moved to **09:02** at Andrea's request, to catch the lights-ON), owner andrea, batch **`noise-tests`**, setting `eeg_emg`, ports A+B only
(C/D not attached), keep_labels `A/1 A/2 A/33 A/34 B/1 B/2 B/33 B/34`. ZT12 -> ZT0 = the whole dark phase.
Scheduled by Claude while Andrea was at dinner; she asked for it ("record until tomorrow, stop at 9 am").

🔴 **Mouse IDs were NOT given.** Slots carry `POS-A1 POS-A2 POS-B1 POS-B2` (rig-position placeholders, said
in the run note). NAS copy lands at `02_Data_Sleep/andrea/noise-tests/Baseline/20261001_POS-<slot>_B/`.
Ask for the real IDs and re-file. "Normal EEG/EMG mice"; cohort unknown ([[cohort-identity-every-run-is-new-mice]]).

**Known before the start:**
- **A1 EMG (A/2) and B2 EMG (B/34) are OPEN**: 3.5 mV of 60 Hz, 14 % of samples on the rail, impedance the
  same as an unwired input (5 % duty, ~4.8 MΩ). Andrea: tethers checked fine, the fault is surgical/implant
  side and cannot be fixed. ⇒ A1 and B2 are EEG only, so not scoreable under the strict rung 2. **A2 and B1 are the candidates.**
- The railing EMGs disturb their own chip's wire-free floor (1-45 Hz floor 2.5-3x run to run), so **only the A2
  chip (and B1, ~1.3x) can serve as a noise meter**. A2's floor repeats within 2-7 % across 3 untouched runs.
- All 4 EEGs normal (EEG 60 Hz 6-17 uV, 1/f, r(E,M) about 0). B1 chip floor 509-599 uV (low, but EEG plainly works).

**Facts learned on the way (already partly in memory, I missed them):**
- Allego 60 Hz notch is display-only. Andrea runs it as her usual Monitor setting. Already verified 2026-07-31
  ([[eeg-60hz-saga]]); re-verified 2026-10-01 from the saved data. Don't re-check it again.
- Impedance needs the stream OFF (`Z_measure attempted during data acq`), already noted in
  [[allego-mesa-gpu-crash-and-log-storm]]. Re-stream and re-check the rate (~1.0x) afterwards.
- `qc/sweep_block_all_ports.py` and `qc/block_duty_cycle.py` hard-code 4 ports. Use
  `qc/sweep_block_ports.py` / `qc/block_duty_cycle_slots.py` (`--slots`) on a 2-port rig.
- Allego Signal Metrics via the API (`AllegoClient().signal_metrics().get_metrics(...)`) computes only the
  SELECTED channels. Wire-free inputs read 0, so it cannot show the floor.
- 🔴 **A console run does NOT arm the hourly `recording-watchdog-cron.sh`.** Arm it by hand after the start:
  `echo <basename> > neurosurveillance/deploy/logs/current-recording.txt && rm -f .../watchdog-lastsize.txt`
  ([[raw-data-archive-and-recording-automation]]).

Vault: `05-experiments/active/2026-09-30-xdaq-noise-series.md` Entries 5-6, `06-references/impedance-sweep-register.md`.
Related: [[xdaq-gen1-has-chassis-gnd]] · [[animal-card-verdict-ladder]] · [[feedback-never-strip-during-a-live-recording]]

## Mid-run (23:42)
- 🔴 **Allego GUI FROZE ~23:30** after a warning flood that began when I restarted the stream for impedance (20:17):
  `resample_antialias` (Monitor Anti-Alias mode) + `[HAL] unable to send to listener`. Renderer 108 % CPU, 11-14 GB RSS.
  **Zero dropped samples** (timestamps all step 1). Lesson: use the `Spikes` view mode for long runs, and expect stale
  listeners after a stream restart. Probably clears only on an Allego restart.
- Reading a LIVE file is OK if light: nice 19 + ionice -c3, 300 s chunks, fadvise DONTNEED, < 1 GB RAM, growth checked before/after.
- No system-wide event in the first 2.8 h; port-A floor wobbles are movement-linked; within-mouse EEG+EMG spikes A2 7 total, none electrical.
- **Stop moved 09:00 → 09:02** (Andrea, to catch the lights-ON). There is no API for a RECORDING run, so I used
  `RunStore.transition(id, RECORDING, scheduled_stop=...)` (same-state, audit event), after a DB backup.
- 🔴 **B1 chip floor < FLOOR_MIN_HUM_UV 800 by only ~7 %**: 742 uV on the gate's PEAK scale (632-808 over the night; 455-599 was band
  RMS, my mistake, √2 small). ⇒ B1 is likely UNJUDGEABLE at rung 2, so A2 may be the ONLY scoreable mouse. Check the B1 GND path
  (board re-plugged 10-01 16:48).
- 🔴 **SCALE TRAP: the gate reads the 59-61 Hz line PEAK (10 s Hann), never compare a 55-65 Hz band-pass std with 800/2000.** Use
  `qc/gate_floor.py`. On quiet EEG/EMG the band std is mostly broadband signal (A2 EEG line 3-5 uV peak vs "6-9" band rms).
- ⭐ **B1's low floor = a few input PAIRS collapsed after the B1 board was re-seated (16:48 boards-off test) + mice on**:
  /6 2853→103, /14 717→14, /15-/16 ~800→146 uV (gate scale), other sites unchanged. A weak ground scales the WHOLE chip; this is
  site-specific ⇒ suspect board seating / bridge / foil or wire touching pads ~10-11, 18-31. B2 (same handling) unaffected.
  The gate's median of 14 sites spanning 14-6200 uV lands in a gap (468|936) ⇒ swings 2x. Tool: `qc/site_floor_compare.py`.
- Morning plan: after the console reaches DONE, run `qc/shadow_ladder.py` (FLOOR_MIN_HUM_UV changed in memory only, cache COPY,
  cards to a *shadow* dir) for B1 under /opt/neurosurveillance/venv/bin/python3 with PYTHONPATH=eeg-emg-analysis. Re-run
  `qc/splitter_coincidence.py` (fixed N') then too. Ask Andrea to inspect the B1 adapter board / foil (pads ~10-11, 18-31).
- 🔴 **PRODUCTION watchdog hazard (found in review, 2026-10-02):** a stale `current-recording.txt` is never replaced. If a NEW recording
  starts between a stop and the next :05 check, the old file's frozen size raises a max-priority STALL every hour and the new run is
  unwatched. Fixed (re-arms to Allego's live file) in worktree `/home/skimlab/srs-overnight-worktree` branch
  `overnight/2026-10-02-console-fixes`, NOT deployed; also a compare-and-set + 72 h cap for the new `/api/runs/<id>/stop_at`.

## Outcome (2026-10-02 09:00-09:25)
- Stopped 09:02:04, 12.032 h, ZERO dropped samples; lights-ON event 08:59:51 inside. DONE 09:14:47, NAS verified.
- **Official rung 2: ALL FOUR UNJUDGEABLE**: B1 hum gate 702 < 800; A1/A2/B2 contaminated-floor guard (slope p1 -3.24/-2.54/-3.44 < -1.90).
- Diagnostic stages 1-3 (outputs in ~/radix/noise-tests/2026-10-02/diag-*): A2/B1 stage-1 CLEAN; stage 3 B1 SCOREABLE r 0.304, A2 REJECT 0.19
  → 0.323 with EMG mains notched ([[emg-mains-corrupts-sleep-staging]]).
- **Light-phase run `8f84e3e62af6` (`allego_0__uid1002-09-16-58`) 09:16:58 → 21:02**, Allego GUI restarted first (allegoserver reused:
  same PID, parent systemd --user, works at 0.998x). Watchdog hand-armed; RAM watcher ~/radix/noise-tests/2026-10-02/.
- **Mouse IDs (Andrea 10-02)**: A1 B6/J BomTac ♀ DOB 2026-04-12 (no ID); A2 = HLBWSL30 (W-SL); B1 = HLBSSD20 (S-SD); B2 = same as A1.
  Registry: Google Drive sheet HLB_SOD1_Intake_Monitoring_SDSLNANO. Not used for experiments → placeholders on the NAS kept.

**Compute venue (2026-10-02 11:00):** single-night full scans → the workstation (raw on NAS `RAW_20261001_2100_overnight_4mice_cfdf8ebde0c6/`), not AWS. The raw S3 archive job defers while ANY recording is live, so a new file reaches S3 only on the first 01:30 with nothing recording. AWS = later, for archive-wide C1/C3 reprocessing (needs IaC + budget alert first). Vault logged: journal 10-02 (file table, waiting-on list), noise-series "Next steps and open decisions (as of 2026-10-02 11:10)", audit note.

**Figures + plan (2026-10-02 11:45):** 10 figures now IN the vault (`05-experiments/attachments/2026-09-30..10-02-noise-fig*`), embedded with captions; new ones from `qc/noise_figures_2026_10_02.py` (reproduces B1 707, B2 1820). Before that every figure was only a `~/radix` path (Obsidian shows nothing): put figures in `attachments/` and embed. Plan for the next trials = [[2026-10-02-noise-troubleshooting-plan]] (T1 isolator with mice, T2 foil→chassis GND, T3 tether shield, T4-T7 box/shield/Faraday, T8-T11 counterbalance/slip ring, A/B/A, thresholds from untouched spread: A2 floor x1.03, EMG60 x1.07). `qc/record_block.py` records a trial block (refuses during console runs, verified live). ✅ The tether's copper shield was NEVER inserted into any pad (Andrea 10-02): connected to nothing. The 06-28 page's pad-6 plan was never built, do not repeat it. B1 collapse: refit and mice connection CONFOUNDED (A2 /37 also collapsed, board untouched).

**Light-phase run 8f84e3e62af6 rig session (2026-10-02 15:35-16:35):** all in vault `2026-10-02-light-phase-run-rig-session` (MARKERS.tsv with s-from-file-start, Figs F-H). Lead on A2's foil: floor x1.3 (meter ON, 10 MΩ to chassis) / x2.1 (meter OFF), A2 EMG 60 Hz x1.16 phase-locked with muscle band DOWN ⇒ pickup not movement. Hands/people dip floors and open EMGs only, never the connected EEG/EMG. B1 floor creeps 732→~1000 untouched; A2 EMG60 drifts 15→30 µV untouched. Next: T2a solid bond (crocodile lead). Check at 21:09 whether official QC flips B1 to grounded. Add MARKERS.tsv to the NAS folder after DONE.

## Light-phase run 8f84e3e62af6 outcome (2026-10-02 21:02-21:45)
- DONE 21:11:30, 11.751 h, zero dropped samples. Lights-OFF in file 21:01:11.5 (sub-threshold; timer ~70 s late at OFF, ~9 s early at ON).
- **Official QC flipped B1 UNJUDGEABLE → rung 2 PASS (floor 702 → 971) with nothing touched** = audit C1 confirmed by the pipeline itself.
- Notch test over ALL ~/eeg-processed: 100 animal-recordings, unnotched reproduces 99/99; SCOREABLE 44 → 69 (27 up, 2 down on physiology). Shuffle control NOT re-run at scale. Still not adopted.
- Full scans: overnight lights-ON only + 3 small 3-chip events (01:59:56, 07:27:42, 08:41:14); light phase: Andrea's visit (~15:19 by data), 17:10:08 + 18:12:10 unexplained. Splitter re-run: at chance.
- ⚠️ Andrea's phone/watch clock ran ≥ 8 s ahead of e10 (17:35); never trust a reported second without a sync photo of Allego time + phone.
- Pending: MARKERS.tsv to the NAS run folders (needs OK).

## Full 24 h analysis on e10 (2026-10-02 22:40-23:59): vault `05-experiments/completed/2026-10-02-noise-series-4mice-24h-analysis`
- Official stages 2-3 + ladder in `~/radix/noise-tests/2026-10-02/official-noise-tests/` (test mice kept OUT of ~/eeg-processed). **B1 light phase SCOREABLE (r 0.407)**; all else NO VERDICT. NAS info.json `qc` refreshed with the console's qc_info (backups in the NAS analysis folder).
- NAS analysis folder `02_Data_Sleep/andrea/noise-tests/ANALYSIS_2026-10-01_to_10-02_4mice_24h/` (README, INDEX.csv, markers in each file's time base, cards, staging, scans, figures, scripts). Per-mouse CSVs were already there (console).
- 🔴 **Scan counts made before 23:00 on 10-02 are WRONG** (allchip v3: port-local + noisy chip passed, IIR ringing): use `fullscans-v2/`. System-wide now = BOTH PORTS. Overnight 4 events (01:59:56, 07:27:42, 08:41:14 + lights-ON), light 13 (10 in the visit; 17:10:08, 18:12:11, 20:56:36).
- 🔴 `pipeline/stage1_qc.py` used to drop `_feat.npz` INTO ~/radix/data when given a full path (fixed + test). If one ever appears there again, move it out before 01:30 (S3 cannot delete).
- Canonical markers module `qc/noise_mice_markers_2026_10_02.py` (origin = status.start_time; visit 15:19:33 by data). trials/MARKERS.tsv superseded.


## From the memory index, trimmed there 2026-10-06 (kept here verbatim)

- 🌙⭐⭐ **[NOISE-SERIES OVERNIGHT, 4 MICE — 2026-10-01 21:00→10-02 09:00](recording-2026-10-01-noise-4mice-overnight.md). NEWEST.** Console run `cfdf8ebde0c6`, batch `noise-tests`, ⚠️ placeholder IDs `POS-<slot>` (ask Andrea). A1/B2 EMG OPEN (implant) ⇒ A2, B1 only candidates; B1 floor 742 (peak) < 800 by ~7 % ⇒ likely UNJUDGEABLE. Stop moved to 09:02. 🔴 Console runs do NOT arm the hourly watchdog. ⭐ Next trials: vault `2026-10-02-noise-troubleshooting-plan` + `qc/record_block.py`; figures go in `05-experiments/attachments/` and get embedded. ✅ **Light-phase run DONE 10-02 21:11: official QC flipped B1 to PASS (floor 702→971, untouched) = C1 confirmed.** Andrea's clock ≥8 s ahead of e10. ⭐ **Full 24 h analysis + NAS folder `noise-tests/ANALYSIS_2026-10-01_to_10-02_4mice_24h/` (vault completed `2026-10-02-noise-series-4mice-24h-analysis`). 🔴 Pre-23:00 all-chip counts WRONG; system-wide = both ports. 🔴 stage1 full-path cache bug fixed.**
