# Project Memory

## EEG rig (the active problem)
- 🎉⭐⭐⭐ **[8-CORE TETHER, 8 MICE, 83 min SCREEN — 2026-09-09](recording-2026-09-09-8core-tether-screen.md). NEWEST, READ FIRST.** Best screen this rig ever made: 7/8 chips grounded, 7/8 EEG 96.6-100%. 🔴 `RMS_HI_UV=150` CLIPS REAL EMG. 🔴 A1 = ground-screw contact fault, not a re-mate.
- ⏳🔴⭐⭐⭐ **[S-SD RECOVERY SLEEP, TERMINAL ENDPOINT — 2026-09-02](s-sd-recovery-sleep-run-2026-09-02.md).** 20.0 h, CSD finished, animals SAMPLED ⇒ UNREPEATABLE. ✅ Pre-flight screen GATED for the first time; a bench re-seat fixed ALL EIGHT chip grounds. 🎉 D2 = a GROUND fault, not an electrode.
- 🔑⭐⭐⭐ **[FLICKER TELLS A BENT TETHER FROM A SEVERED ONE](flicker-discriminates-bend-from-break.md).** Epoch-to-epoch variability of the OPEN level: **80-150% and max/min 7-55× = bending** (recoverable by handling); **4-14% and max/min 1.1-1.8× = continuous break** (handling will NOT fix). ⭐ Works on ~20 epochs, a file FAR too short for any usable fraction. ⭐ Both roles switching together = one cable; other role **AND the chip floor** jumping in the SAME epoch = the tether BODY moved. ⚠️ 84 s cannot rule out a SLOW intermittent.
- 🏁🔴⭐⭐⭐ **[W-SD BATCH CLOSED, SAMPLED 2026-08-28](w-sd-batch-closeout-2026-08-28.md). NEWEST, READ FIRST.** ✅ Pre-CSD baseline recomputed per-chip = **best full-cohort data this rig has made: 5 with EEG, 4 pass rung 2** (A1 96.1% both roles, 39.5 h in long blocks). 🔴🔴 **7 d CSD collapsed 4 grounds** (A1 4976→1347, A2 4396→1575, D1, B1) — **the 2 BEST animals lost to a GROUND fault, not electrodes** ⇒ **recovery comparison n=1 (D2)**. 🔑 **C1 passes rung 2 AND stays withdrawn — that was a RUNG 4 call.** ⏭️ S-SD samples 09-03.
- 🔴⭐⭐⭐ **["NO EEG" IS 5 FAULTS — A WEAK GROUND HIDES](weak-chip-ground-hides-as-electrode-failure.md). READ BEFORE BLAMING AN ELECTRODE.** 🔑 Discriminator = **EEG 60 Hz ÷ its OWN chip floor**: ≈0.03 normal (weak-ground looks IDENTICAL to working), ≥1.0 open. Then read the floor: **<2000 µV ⇒ nothing on that chip means anything.** 🔴 **`FLOOR_MIN_HUM_UV=800` TOO LOW** — 6 chips <2000 µV, 0 gave EEG; lowest working 2186. Proposed 2000, **NOT APPLIED, awaiting decision**. ⭐ **Working EMG exonerates that implant+tether.**
- 🔴⭐⭐⭐ **[W-SD RECOVERY SLEEP, 7 d CSD — 2026-08-27/28](w-sd-recovery-sleep-run-2026-08-27.md).** 20.121 h, unrepeatable. 🔴🔴 ONLY D2 usable ⇒ the paired comparison is n=1. 🔑 B1 ground DECAYED 825→469 µV over 20 h = a conductor working loose. 🔑 A first-hour screen must GATE an unrepeatable run.
- ⭐⭐⭐ **[20.3 h B1-SWAP BASELINE — 2026-08-26](recording-2026-08-26-b1-swap-20h-baseline.md).** ✅ Swap confirms B1 port good; D2 passes strict rung 2 a 3rd time ⇒ the scoring pack. 🔴 C1 break is EMG-conductor only. ⚠️ Never quote B1 %. ⭐ B1+C1 are the CHEWING CAGES.
- 🔴⭐⭐⭐ **[B SLOT 1 WAS THE TETHER, NOT THE PORT — 2026-08-26](b-slot1-was-the-tether-not-the-port.md). NEWEST.** **RETRACTS my "B1 is a port fault" call.** Chewed tether on HLBCSD13; spare **HLBCSD17** into the SAME slot ⇒ floor 246 → 2338 µV, grounded, real EEG. 🔑 **A recurrence argument is not a swap test — do the swap before naming a root cause.** ⚠️ A2 and C2 have since DEGRADED.
- ✅⭐⭐⭐ **[FLOOR THRESHOLD FIXED — 2026-08-26](floor-threshold-fixed-per-chip.md). NEWEST.** `floor_stats(feat, position)` is now PER-CHIP; estimator `site_p1_median`; **ungrounded chip ⇒ rung 2 `UNJUDGEABLE`, not FAIL** (`FLOOR_MIN_HUM_UV=800`). ✅ Falsification suite passes and the physically-railing channels stay rejected ⇒ it does NOT manufacture passes. 🔴 `falsification_check` on REAL data is vacuous (floor fails the amplitude gate first). 🟡 lf/hf separates better than slope, not implemented.
- ⭐⭐⭐ **[24 h ZT0-TO-ZT0 RUN, S-SD — 2026-08-25](recording-2026-08-25-24h-zt0-S-SD.md). NEWEST, READ FIRST.** 24.276 h clean (726 watchdog checks, 0 stalls). **Only D2 passes strict rung 2**; EEG-only A2/D2/C2/C1. 🔴 B slot 1 reads floating (246 uV) — ⚠️ **my "ground pin / port fault" reading RETRACTED, it was a CHEWED TETHER: [[b-slot1-was-the-tether-not-the-port]]**. ✅ D1's chip IS grounded ⇒ its failure is the TETHER. 🔴 **EEG usability drops 15-34 pts in the DARK phase** (D2 immune). 🛑 1 h snapshots badly overstate a 24 h run.
- ⭐⭐⭐ **[`S-SD` BATCH, 8 MICE, 1 h SCREEN — 2026-08-24](recording-2026-08-24-new-8-mice.md). NEWEST, READ FIRST.** ✅ **First cohort with REAL ids (HLBCSD11-19); manifest `cohorts/S-SD.yaml`, source = `HLB_SOD1_Intake_Monitoring.xlsx` sheet Registry, header on ROW 5, openpyxl only in `~/eeg-analysis-venv`.** 🔴 **Surgical bleeding notes do NOT predict signal quality**; ⭐ B1 mouse has no adverse note and gives nothing — ⚠️ I called this a PORT fault; **RETRACTED, it was a chewed tether**.
- ⭐⭐ **[8 NEW MICE, 1 h SCREEN — 2026-08-24](recording-2026-08-24-new-8-mice.md) — measurements.** 4 give hour-long EEG (A2, C2 unbroken 60 min); **only D2 passes strict EEG+EMG (89.2%, 23.8 min)**; B1 nothing, B2 EMG-only. 🔴🔴 **The PER-CHIP floor can itself be CONTAMINATED** (A1 7/14 floor sites EEG-steep) — at p1 one bad site sets the bar and fakes a failure. ⭐ Always do the per-10-min time course: A1/D1 are intermittent, not dead. 🛑 A midway number overstates a flickering channel.
- ⭐⭐⭐ **[FIRST HYPNOGRAMS; B1+C1 ANIMALS GONE — 2026-08-22](hypnograms-and-per-mouse-export.md). NEWEST.** 3 of 6 hypnograms usable; `r@1min` decides, bar 0.30. 🛑 Never report REM %. 🛑 All provisional until the kappa. Analysis → `/usr/bin/python3`, `setsid` not `nohup`.
- 🔴⭐⭐⭐ **[EMG GATE PASSES + THE POOLED-FLOOR BUG — 2026-08-21](emg-gate-passes-and-floor-bug.md).** 🔴 `criteria.floor_stats()` pooled the floor across all 8 chips — ✅ **FIXED 2026-08-26, see [[floor-threshold-fixed-per-chip]]**. ✅ Kappa unblocked at n=3. 🔑 Always ABSOLUTE delta, never the ratio. A pooled FAIL is suspect, a pooled PASS survives.
- 🔴⭐⭐⭐ **[EVERY RUN IS NEW MICE UNLESS I SAY OTHERWISE](cohort-identity-every-run-is-new-mice.md). READ BEFORE ANY ANALYSIS.** Rig position ≠ animal. No cross-run carry-over of animal facts; hardware facts DO carry.
- ⭐⭐⭐ **[8 `W-SD` MICE — SCREEN + 1 h RE-SEAT RUN, 2026-08-18](recording-2026-08-18-eight-new-mice.md).** Name = batch + position. 2 roles, no ECG. ✅ Never call a channel animal-side before a re-seat + re-record. 🔑 Strict rung 2 = EEG AND EMG in the SAME epoch — say which number you quote.
- 🔴⭐⭐⭐ **[ANALYSIS STACK AUDIT — 2026-08-11](analysis-stack-audit-2026-08-11.md).** ⚠️ Its "EMG gate failed by everyone" used the POOLED floor ⇒ may be an artefact. 🔴 "Filtering cannot manufacture slope" is FALSE. ⭐ Slope fractions carry ±20 pts. 🛑 Repo has zero git commits.
- ⭐⭐⭐ **[A2 CONTROL, 48 h, TWO CIRCADIAN CYCLES — BEST DATA EVER TAKEN HERE](a2-control-48h-reference-profile.md).** 47.09/48.19 h usable, zero railed epochs. ⭐ Prefer ZT0 starts for long runs. ⭐ Replicates day to day. ⚠️ Circadian ORDERING survives a ±25% sweep, the absolute % does not.
- 🔴⭐⭐ **[TEST SUITE: 2 OF 4 VERIFY NOTHING — 2026-08-24](test-suite-two-of-four-verify-nothing.md).** Not pytest — run as scripts with `PYTHONPATH=.`. 🔴 `test_ladder_verdicts` + `test_criteria_regression` SKIP (fixture `uid0806-16-57-38` gone) yet exit 0, and the ladder one PRINTS "all pass ... agrees on both recordings". 🛑 "3 suites green" is not currently true. venv `~/eeg-test-venv` has pytest + numpy 1.26/scipy 1.11.
- ⭐⭐⭐ **[ANIMAL CARD + VERDICT LADDER, 2026-08-09](animal-card-verdict-ladder.md). READ BEFORE ANY ANALYSIS OR FIGURE.** Six rungs, each blocked by the one below. Code at `~/sleep-recording-skim/eeg-emg-analysis/`; `core/qc_thresholds.py` + `core/criteria.py` are the only engines. 🔑 Rung 2 gates on longest unbroken block ≥15 min.
- ✅⭐⭐⭐ **[THE GROUND RE-PIN WORKED — 2026-08-08](ground-fix-worked-2026-08-08.md).** 🔴🔴 THE HUM CRITERION IS DEAD — use the SLOPE criterion. 🔴 Slope is a CATEGORY ERROR for EMG. 🔴 ECG dead 7/7 vs a floor null. 🔑 A low, stable, zero-flip impedance can mean NO GROUND.
- 🔴⭐⭐⭐ **[ROOT CAUSE: CEREBELLUM GROUND ON THE WRONG PIN — 2026-08-07](ecg-cohort-ground-miswired.md).** Dura pin on the wrong colour ⇒ floating. Explains the hum collapse AND the perfect impedance at once. ✅ Fix = connector re-mate, no anaesthesia.
- **[COHORT REPLACED: 7 EEG+EMG+ECG MICE — 2026-08-07](ecg-cohort-2026-08-07.md).** 3-role channel map and its floor. 🔴 `set_recording_config()` BROKEN — use `qc/set_recording_config_fixed.py`. ⚠️ `get_status().recording.path` LIES; always `ls` the destination.
- ⭐⭐⭐ **[COUNCIL REVIEW + PIPELINE FIXES](council-and-pipeline-fixes.md). READ BEFORE TOUCHING THE ANALYSIS.** ⭐ Three council findings did NOT survive measurement. 🔴 Circadian check is threshold-DEPENDENT. 🔴 4 of 5 physiology checks CANNOT FAIL — stop quoting "5/5". 🟡 Open: the KAPPA, a POSITIVE CONTROL.
- ⭐⭐ **[3 SCOREABLE RECORDINGS + CIRCADIAN CHECK — 2026-08-07](staging-circadian-validation-2026-08-07.md).** Synthesis = vault `07-decisions/2026-08-07-rig-specification-and-analysis-method.md` = the page to argue from. ⚠️ SUPERSEDED as circadian evidence by [[a2-control-48h-reference-profile]].
- ⭐⭐⭐ **[TWO ANIMALS WORK; THE TETHER IS THE FIX — 2026-08-07](overnight-two-animals-tether-is-the-fix.md).** 🔴 RETRACTS the 08-06 "arm C harmed D2". ⭐ Long recovery NOT required; cohort recoverable WITHOUT surgery. 🔑 Impedance SCREENS; only a multi-hour recording is an OUTCOME — always state block duration.
- ⭐⭐ **[USABLE FRACTION vs AN IN-FILE CONTROL](recording-usable-fraction-analysis.md)** — ⛔ its script is DELETED; `core/criteria.py` is the only engine. 🔑 XDAT = float32, 262 interleaved ch, µV, labels from `biointerface_map`. ⚠️ Hardware bandpass 1.10-475.17 Hz reaches the file and eats the bottom of delta.
- ⭐⭐⭐ **[THE 0.5 MΩ CRITERION, AND WHY 2 MΩ DIED — 2026-08-06](fleet-duty-cycle-census-and-new-mouse.md).** An EMPTY tether read "connected" 22% of the time at 2 MΩ ⇒ use |Z| < 0.5 MΩ. ✅ Tether/slip-ring/splitter innocent; false positives are the amplifier's floating input. ⚠️ 0.5 MΩ still calls our best-ever channel open.
- ⭐⭐⭐ **[ELECTRODES PROVEN GOOD; CONTACT IS INTERMITTENT — 2026-08-04](movement-dependent-contact-root-cause.md).** 🛑 NO SURGERY. Contact flips fast and reversibly within minutes ⇒ a single sweep cannot rank, screen or classify. ⚠️ Movement NOT proven as the trigger.
- 🔴⭐⭐ **[FULL EEG RIG STATE](eeg-rig-current-state.md) — READ BEFORE ANY EEG WORK.** Channel law, channel signatures, run results, retractions. ⚠️ Its electrode-failure framing is SUPERSEDED by the ground root cause.
- ⭐⭐⭐ **Channel selection SETTLED: `02-procedures/CANONICAL-allego-channel-selection.md`.** ⚠️ That page is the OLD 2-channel map; the ECG cohort adds `/3`,`/35`.
- 🛑 **NEVER suggest "reseating" an electrode/EMG wire** — impossible after implantation; only animal-side option is a tether change = isoflurane. **Do NOT schedule surgeries.** 🛑 **Signals are ALREADY bipolar — never subtract EEG from EMG.**
- 🧹 **Recording room stripped 2026-08-04:** rack = wifi router + ASUS PC + XDAQ + white-noise generator. ⚠️ **ALL CAMERAS REMOVED ⇒ NO VIDEO** until restored.
- ⭐ **Only ONE old recording has real sleep: 2026-07-31, C1 8.73 h, one 8.1 h unbroken block, r@1min +0.744; C2 qualifies ⇒ n=2.** Report `05-experiments/completed/2026-08-03-data-quality-report-for-professor.md`.
- 🟡 **Only half of each electrode pair has ever been measured** (all impedances are `inX+`). ❌ **[Open Ephys does NOT fix this](impedance-negative-electrode-unmeasurable.md)** — don't propose switching software for it. Free fix = DMM each C3410 pad vs GND pad.
- 📤 **KONTEX BATCH 2026-08-04:** Q12 impedance polarity + Q13 Allego spike-sorter filter errors; paste-ready text in `01-infrastructure/vendor-correspondence/2026-07-29-kontex-kc-call-prep-rig-finalization.md` §"TO SEND".
- ⚠️ [82% of epidural electrodes fail in 3 weeks](electrode-failure-literature.md) — real literature, ❌ **NOT our failure mode.** Do not use it to lower expectations.
- ⭐⭐🔑 [THE ANALYSIS PIPELINE](eeg-analysis-pipeline.md) — `02-procedures/eeg-data-analysis/pipeline/` is THE path; thresholds re-derived from 1,137,955 epochs.
- ⭐⭐ [Light schedule 09:00 ON / 21:00 OFF KST, ZT0=09:00](light-schedule-and-circadian-validation.md).
- 🔴 [Scoring bug #2 — persistence measured across time gaps](eeg-analysis-codebase.md) — fixed by within-block autocorrelation. Older scripts: [EEG QC tooling](eeg-qc-tooling.md). [Full 60 Hz saga](eeg-60hz-saga.md). [First headstage bring-up](project_first_headstage_bringup.md).
- **Hardware-video-sync (Phase 0a):** gate = `DO 03` (DB25 pin22) Gated mode + Allego "BNC Breakout Board" toggle ON; shadow-first MQTT. [[project_hardware_sync_neuronexus_reply]].

## Rig expansion (8 → 32 mice)
- ⭐⭐ **START AT `07-decisions/RIG-EXPANSION-HUB.md`.** Vendor emails in `01-infrastructure/vendor-correspondence/`.
- 🔴⭐ [DAQ research corrections](daq-research-corrections-2026-07-28.md) — **8 primary-source corrections; READ BEFORE trusting older DAQ notes.** Core has NO isolation; PortExp MANDATORY for 16/box; **don't buy Allego**; Intan via White Mountain Systems.
- ⭐ [XDAQ channel law + wiring](xdaq-channel-law-and-32-mouse-wiring.md) — **animals = channels ÷ 64**. ⚠️ order **ONE-R1024**, R512 gives only 8. A splitter fills a box, never exceeds it → **32 = 2 boxes**.
- [DAQ ecosystem comparison](daq-ecosystem-comparison.md) (VAULT-ONLY, confidential) · [16→32 device](acquisition-device-16-32-mice.md) · [Open Ephys option](openephys-scale-up-option.md). **Kontex quote 262024 = $10,002.89**, valid to 2026-08-20.
- 📞 **Kontex call prep:** `01-infrastructure/vendor-correspondence/2026-07-29-kontex-kc-call-prep-rig-finalization.md`. ⚠️ **OPEN: why 2 PCs, is SyncLink needed, behaviour under OE GUI.**

## Working across machines
- ✅🔴⭐⭐⭐ **[ONE REPO NOW: `sleep-recording-skim`](workspace-single-repo-sleep-recording-skim.md). NEWEST, READ FIRST.** Vault + all code + Claude config in ONE git repo, subtree, full history. Sync = MANUAL `./skim status|pull|push|check`. 🔑 The 19-day memory deadlock was `settings.json` keeping the tree dirty ⇒ `git rebase` refuses ⇒ push AND pull locked. 🛑 Syncthing RETIRED. ⚠️ e10 cutover NOT done (daemon symlink).
- ⚠️ **[The Syncthing-era setup, SUPERSEDED 2026-09-10](multi-machine-setup-and-vault-safety.md).** Why the vault died in 2026-04 (no versioning + replicated live `.git`), the office-PC relay surprise, the `claude-portable` design. Historical; the workflow it describes is retired.

## Other big findings
- ✅ **RustDesk + HDMI-switch crash FIXED + VALIDATED** (2026-07-15). `GRUB_CMDLINE_LINUX_DEFAULT="quiet splash video=HDMI-A-1:1920x1080@60e"` (`e` = forced-enabled). 1080p not 4K (thermal). Journal `2026-07-13.md`.
- **72h/20h runs (Jul 10-14):** byte-perfect files, 0 scoreable EEG. **VIDEO recorded NOTHING** — Frigate recording OFF at runtime since 2026-07-03. **PC THROTTLED ~78% of the 72h run, peak 101°C — cooling is the wall.**

## Project Overview
NeuroSurveillance: Raspberry Pi 5 + Frigate NVR video monitoring for neuroscience sleep research. **Scale-up planned to ≥4 Pi5 / 8 cameras.**
- **Pi1** `192.168.0.11`: go2rtc 1.9.14, pi_cam_0/1. **Pi2** `192.168.0.12`: pi_cam_2/3. All 1024x768@15fps H.264.
- **NVR** `192.168.0.50` (mini-PC `e10ubuntu`): Frigate (Docker), session daemon, Mosquitto MQTT. 4 cams/4 chambers.
- ONE repo `~/sleep-recording-skim/`: `vault/` (docs) + `neurosurveillance/` (backend+frontend monorepo) + `eeg-emg-analysis/` + `claude-config/`.

## Architecture (detail derivable from code — key facts only)
- **Backend** (Python 3.12 Flask) `neurosurveillance/backend/`: `daemon.py` (Radiens poll, MQTT, Flask API `127.0.0.1:8585`, sessions) + storage_monitor · radiens_poller · session_manager · manual_session_manager · frigate_controller · session_journal (SQLite WAL) · reconciler · recording_watchdog. Export ffprobe sanity: `<0.95×` dur ⇒ partial.
- **Frontend** (React 19 + TS + Tailwind + DaisyUI 5, Vite + Tauri): ChamberSilo per camera, SystemHealth/Storage/SessionHistory footer, SettingsModal. Polls `/api/status` 1.5s, `/api/health` 5s, `/api/storage` 10s.
- **Config:** production `/opt/neurosurveillance/config.yaml`. **Daemon auto video start/stop DISABLED 2026-07-03** (`sessions.auto_start:false`). Re-enable = flip flag + `sudo systemctl restart neurosurveillance-session`. Deferred daemon bugs: session-JSON filename collision, long-export partial, `radiens.log` unrotated.

## Monitoring Stack (Mar-Apr 2026)
- Netdata v2.9.0 on NVR+Pi1+Pi2. Uptime Kuma (Docker, NVR, 7 monitors). NVR alerts: 16 `nvr_*`, 227 defaults silenced. Slack webhook shared. **No Netdata MQTT collector** → bridge does MQTT→Slack ([[pattern_netdata_no_mqtt_collector]]).

## Host Hardware
- `e10ubuntu` @ `192.168.0.50`: Intel Core Ultra 5 125H (14c/18t, iGPU QSV+NPU), 30GiB RAM, 1.9TB NVMe. (CLAUDE.md says Ultra 7 — actual Ultra 5.)
- 🔴⭐ **[allegoserver spins a core after the GUI closes](allegoserver-runaway-thread-thermal.md)** — caused the CPU temp alarms 2026-08-23; +10 W/+11 °C. `kill` it. ⚠️ `ps %CPU` = lifetime avg, misleads.
- 🔴⭐⭐ **[Allego GPU crashes in Mesa + 6.5 GB log storm killed a run — 2026-08-24](allego-mesa-gpu-crash-and-log-storm.md).** Fix = launch `--disable-gpu`. 🔑 Frozen GUI ≠ lost data (judge by bytes on disk + rms), but app death DOES end the recording. ⚠️ Fresh launch comes up 30 kHz / SMARTBOX_PRO — re-check fs+mode. 🛑 `pkill -f /opt/allego/allego` kills your own shell.
- **Thermal = the wall:** PL1 capped 20W. Fixes: aggressive fan curve, dedust+repaste, headless. Council leans proper desktop/SFF for a 72h live-animal instrument.

## Known Issues
- ✅ **[USB HDD would not mount = NTFS DIRTY BIT, not a dying drive](usb-hdd-ntfs-dirty-bit.md)** — `ntfs3` refuses dirty volumes; fix `sudo ntfsfix -d /dev/sda1`. 🛑 bare `ntfsfix` SETS the bit. SMART clean, CRC 0.
- [Exports move out of Frigate dir](frigate-exports-moved-out-of-frigate-dir.md) — CHECK THERE before saying an export failed.
- [Recording toggle fragility](frigate-recording-toggle-fragility.md) — capture gated by RETAINED MQTT; SIGTERM-OFF → silent no-capture after reboot (cost a 72h run). 🔧 LEASE-model fix written, 12/12 tests pass, ACTIVATES ON NEXT RESTART. Recording dirs are UTC not KST.
- Recurring Pi5 PoE crashes (Waveshare PoE HAT PMIC latch-up).
- [Docker upgrades fire unwanted recordings](project_docker_upgrade_recordings.md) — `apt-mark hold` applied 2026-05-20.
- Lab members list: only `["andrea"]`.

## Completed work (pointers)
- ✅⭐⭐⭐ **[ALL 831 GB OF RAW DATA IS ON THE NAS + UNATTENDED RECORDING, 2026-08-19](raw-data-archive-and-recording-automation.md).** 124 files, zero errors, sha256 both ends. 🛑 Never deletes locally; ONE-SHOT not a schedule. 🔴 `radiens` only in `/opt/neurosurveillance/venv/bin/python3`. 🔴 `ssh` in a `while read` loop eats stdin — always `ssh -n`.
- 🔴⭐⭐ **[NAS BACKUP: 6-DAY OUTAGE WAS A WRONG IP, 2026-08-19](nas-backup-stale-address-outage.md)** — use the MagicDNS name `bilab-syn.tail8808c0.ts.net`, never a hardcoded `100.x` literal. 🛑 Two confident wrong diagnoses first; a `tailscale ping` pong proves nothing. ⭐ NAS has 13 TB free.
- **NAS backup** DEPLOYED+VERIFIED (May 26): daily 00:00 → Synology over Tailscale. Transfer = **ssh pipe NOT rsync/scp**. [[nas-backup]].
- **Stabilization sprint wk1 CLOSED** (May 22-26): Mosquitto auth + SHA-pins; SQLite WAL journal; Frigate restart-grace via LWT ([[pattern_frigate_mqtt_message_ordering]]); watchdog→Slack; ffprobe export sanity; nightly reconciler ([[pattern_frigate_record_enabled_orphan_noise]]).
- **Storage mgmt** (Apr 2): StorageMonitor 30s poll, 200GB EEG reserve. [Storage](project_storage_management.md).

## Planned Work
- [Hardware-sync XDAQ→Pi GPIO](project_hardware_sync_neuronexus_reply.md) — vendor CLOSED; remaining = bench validation + ~$40 BOM. 🟢 PLAN FINAL: alignment uses NO clocks — pulse from the camera FRAME-CAPTURE CALLBACK, fit frame N ↔ sample S, PER-CAMERA. In-frame LED REJECTED. 24/7 recording REJECTED.
- [Settings sync gap](project_settings_sync.md) — SettingsModal → localStorage only (deferred).
- [Camera per-partition framing](camera-roi-framing.md) — ROI test Pi1.
- [Multi-user recording schedules](project_multiuser_recording_schedules.md) — Allego **GUI** = one global R_ON/R_OFF. **OVERTURNED 2026-07-24: radiens v4.0 Python API DOCUMENTS per-port control** (`start_recording(*, port=...)`, `split_files_by_port=True`). ⚠️ UNVALIDATED on our Gen-1 Core → bench test owed.

## Vault navigation
- ⭐⭐ **EEG ANALYSIS = FOUR PAGES, no others:** `_eeg-analysis-hub.md` = START HERE · `pipeline/README.md` · `analysis-methods-and-justification.md` (hand to professor) · `06-references/eeg-analysis-glossary.md`; symptoms in `03-troubleshooting/symptoms/eeg-analysis-problems.md`. `03-scripts-and-usage.md` + `_archive_pre_sleep64/` = SUPERSEDED TWICE.
- ⭐ **`07-decisions/` FILING RULE (trimmed 26→9 on 2026-08-03): CHOICES ONLY.** Results→`05-experiments/completed/`, literature→`06-references/`, procedures→`02-procedures/`, symptoms→`03-troubleshooting/symptoms/`. Table in [[reference-vault-07-decisions]].
- `02-procedures/allego-electrode-setup-sleep64.md` — THE electrode SOP. `signal-mapping-guide.md`, `signal-quality-and-grounding.md`, `multimeter-guide.md`.
- `06-references/radiens-software-reference.md` — PRIMARY Radiens/Allego ref. `00-config/production-values.md` — IPs/ports/paths. `_INDEX.md`, `AI-INSTRUCTIONS.md`.

## Environment Notes
- NVR hostname `e10ubuntu` (not `frigate-server`); user `skimlab` (not `sleepigene`). We are ON the NVR — no SSH for local commands.

## Artefact policy
- ⭐⭐ **`02-procedures/eeg-artefact-and-railing-rejection-policy.md` = THE standing rule.** Reject at EPOCH level, never repair or interpolate; report what was rejected and why.

## Working Preferences
- [No dashes in emails](feedback_no_dashes_in_emails.md) — never use `-` or `—` in email bodies.
- [Implementation guides preferred](feedback_leave_guides.md) — for major features, write vault guide not code.
- [Verify operational details](feedback_verify_operational_details.md) — read source files, never assume names/paths.
- [Don't suggest `record.enabled: false`](feedback_record_enabled_false_off_limits.md) — breaks Frigate, off-limits.
- [Sudo command style](feedback_sudo_command_style.md) — bare commands, one step at a time, expected output.
- [Report writing style](feedback_report_writing_style.md) — informal first-person, expand acronyms, ALLCAPS warnings, TL;DR + still-open.

## Operational patterns
- [Docker SHA-pinning](project_docker_sha_pin_pattern.md) — pin `:tag@sha256:digest` of local cached image.
- [Frigate MQTT retained-topic ordering](pattern_frigate_mqtt_message_ordering.md) — defer state callbacks + cancel-on-availability.
- [Frigate `record.enabled=true` ORPHAN noise](pattern_frigate_record_enabled_orphan_noise.md) — 6h floor + Slack suppression.
- [No Netdata MQTT collector](pattern_netdata_no_mqtt_collector.md) — extend the bridge service for future MQTT alerts.
