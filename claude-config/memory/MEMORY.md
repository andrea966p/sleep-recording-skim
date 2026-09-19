# Project Memory

## EEG rig — Allego / hardware behaviour
- ✅🔴⭐⭐⭐ **[BLANK MONITOR = CANVAS BIGGER THAN THE SOFTWARE RENDERER — 2026-09-16](allego-blank-monitor-canvas-texture-limit.md). NEWEST.** Canvas = ALL signals × Chan height (262×50=13175 px); `--disable-gpu` ⇒ SwiftShader 8192 ⇒ never draws. Launch WITHOUT the flag ⇒ Intel GL 16384 ⇒ works. 96→262 signals crossed a threshold.
- 🔴⭐⭐ **[ORPHANED allegoserver MAKES A HEALTHY RIG LOOK DEAD](allego-orphaned-server-blocks-the-rig.md).** Reparented to `systemd --user`, holds ports 50051-4, maybe no USB ⇒ stream toggles, zero samples. Check PPID first.
- 🔴⭐⭐ **[Allego GPU crashes in Mesa + 6.5 GB log storm — 2026-08-24](allego-mesa-gpu-crash-and-log-storm.md).** `--disable-gpu` was the fix. Frozen GUI ≠ lost data; app death DOES end recording. Fresh launch = 30 kHz/SMARTBOX_PRO, re-check fs+mode.
- 🔴⭐ **[allegoserver spins a core after the GUI closes](allegoserver-runaway-thread-thermal.md)** — +10 W/+11 °C. `ps %CPU` = lifetime avg, misleads.
- 🔴⭐⭐ **[ALLEGO STOP WORKS; FILE SIZE LAGS ~30 s](allego-stop-works-and-the-30s-size-lag.md).** `getsize()` reads 0 for a full 30 s ⇒ any growth check under ~35 s is a FALSE NEGATIVE. Stop in a `finally`.
- 🔴⭐⭐ **[radiens 4.0.0 HAS NO PER-PORT RECORDING](radiens-4-has-no-per-port-recording.md).** Recording is GLOBAL. 4.0.0 IS latest stable — don't upgrade to fix it. ⚠️ `AllegoClient.restart()` is also broken (`mode.enum`); call the `Restart` gRPC with `mode.value`.
- 🛑 **NEVER suggest reseating an electrode/EMG wire** (impossible post-implant; tether change = isoflurane). **Do NOT schedule surgeries.** Signals are ALREADY bipolar — never subtract EEG from EMG.

## EEG rig — signal interpretation
- 🔴⭐⭐⭐ **["NO EEG" IS 5 FAULTS — A WEAK GROUND HIDES](weak-chip-ground-hides-as-electrode-failure.md).** Discriminator = EEG 60 Hz ÷ its OWN chip floor: ≈0.03 normal, ≥1.0 open. Floor <2000 µV ⇒ nothing on that chip means anything. `FLOOR_MIN_HUM_UV=800` TOO LOW; 2000 proposed, NOT APPLIED.
- 🔑⭐⭐⭐ **[FLICKER TELLS A BENT TETHER FROM A SEVERED ONE](flicker-discriminates-bend-from-break.md).** 80-150% variability + max/min 7-55× = bending (recoverable); 4-14% + 1.1-1.8× = continuous break.
- ⭐⭐⭐ **[ELECTRODES PROVEN GOOD; CONTACT IS INTERMITTENT](movement-dependent-contact-root-cause.md).** Contact flips within minutes ⇒ a single sweep cannot rank or classify.
- ⭐⭐⭐ **[THE 0.5 MΩ CRITERION](fleet-duty-cycle-census-and-new-mouse.md).** Empty tether read "connected" 22% at 2 MΩ ⇒ use |Z| < 0.5 MΩ.
- ✅⭐⭐⭐ **[THE GROUND RE-PIN WORKED — 2026-08-08](ground-fix-worked-2026-08-08.md).** HUM CRITERION IS DEAD, use SLOPE. Slope is a CATEGORY ERROR for EMG.
- 🔴⭐⭐⭐ **[ROOT CAUSE: CEREBELLUM GROUND ON WRONG PIN](ecg-cohort-ground-miswired.md).** Explains hum collapse AND perfect impedance at once.
- 🔴⭐⭐⭐ **[B SLOT 1 WAS THE TETHER, NOT THE PORT](b-slot1-was-the-tether-not-the-port.md).** A recurrence argument is not a swap test.
- 🔴⭐⭐⭐ **[EVERY RUN IS NEW MICE UNLESS I SAY OTHERWISE](cohort-identity-every-run-is-new-mice.md).** Rig position ≠ animal. Hardware facts carry; animal facts do not.
- 🟡 Only half of each electrode pair has ever been measured (all `inX+`). ❌ **[Open Ephys does NOT fix this](impedance-negative-electrode-unmeasurable.md).**
- ⚠️ [82% of epidural electrodes fail in 3 weeks](electrode-failure-literature.md) — real literature, ❌ NOT our failure mode.
- 🔴⭐⭐⭐ **[A PARTLY LOADED RIG WAS GRADED ON ALL 8 SLOTS](partial-rig-qc-and-unjudgeable-presets.md).** Pre-2026-09-13 bundles for <8 mice contain `UNKNOWN@slot` cards from FLOATING inputs, 3 read PASS at rung 2. `unipolar_lfp` has NO QC criterion by design.

## EEG rig — analysis stack
- ⭐⭐⭐ **[ANIMAL CARD + VERDICT LADDER](animal-card-verdict-ladder.md). READ BEFORE ANY ANALYSIS OR FIGURE.** Six rungs. `core/qc_thresholds.py` + `core/criteria.py` are the only engines. Rung 2 gates on longest unbroken block ≥15 min.
- ✅⭐⭐⭐ **[FLOOR THRESHOLD FIXED, PER-CHIP — 2026-08-26](floor-threshold-fixed-per-chip.md).** Ungrounded chip ⇒ rung 2 UNJUDGEABLE, not FAIL. Falsification suite passes.
- 🔴⭐⭐⭐ **[EMG GATE + THE POOLED-FLOOR BUG](emg-gate-passes-and-floor-bug.md).** Pooled floor FIXED 2026-08-26. Always ABSOLUTE delta, never the ratio.
- 🔴⭐⭐⭐ **[ANALYSIS STACK AUDIT — 2026-08-11](analysis-stack-audit-2026-08-11.md).** "Filtering cannot manufacture slope" is FALSE. Slope fractions carry ±20 pts.
- 🔴⭐⭐ **[TEST SUITE: 2 OF 4 VERIFY NOTHING](test-suite-two-of-four-verify-nothing.md).** Two suites SKIP yet exit 0 and PRINT success. "3 suites green" is not true. venv `~/eeg-test-venv`.
- ⭐⭐⭐ **[COUNCIL REVIEW + PIPELINE FIXES](council-and-pipeline-fixes.md).** 3 council findings did NOT survive measurement. 4 of 5 physiology checks CANNOT FAIL.
- ⭐⭐⭐ **[FIRST HYPNOGRAMS](hypnograms-and-per-mouse-export.md).** `r@1min` decides, bar 0.30. 🛑 Never report REM %. Analysis → `/usr/bin/python3`, `setsid` not `nohup`.
- ⭐⭐ **[USABLE FRACTION vs AN IN-FILE CONTROL](recording-usable-fraction-analysis.md).** XDAT = float32, 262 interleaved ch, µV. Hardware bandpass 1.10-475.17 Hz eats the bottom of delta.
- ⭐⭐🔑 [THE ANALYSIS PIPELINE](eeg-analysis-pipeline.md) · [Scoring bug #2](eeg-analysis-codebase.md) · [QC tooling](eeg-qc-tooling.md) · [60 Hz saga](eeg-60hz-saga.md) · [First bring-up](project_first_headstage_bringup.md)
- ⭐⭐ [Light schedule 09:00 ON / 21:00 OFF KST, ZT0=09:00](light-schedule-and-circadian-validation.md)
- ⭐⭐ **Artefact policy:** `02-procedures/eeg-artefact-and-railing-rejection-policy.md`. Reject at EPOCH level, never repair or interpolate.

## EEG rig — runs
- ✅🔴⭐⭐⭐ **[HLBW_SL 28 h DONE — 2026-09-17→18](recording-2026-09-17-HLBW_SL-28h.md). NEWEST.** **Unattended workflow ran CLEAN: stop 5 s late, strip bit-exact on every sample, NAS-verified in 13 min, QC bundle with it.** 7/8 rung 2 CLEAN, A1 EEG dead. **3 scoreable (B1 B2 D2), all grounded**; A2/C1/D1 UNJUDGEABLE (floors 582/7/2). Sleep + figures → `05-experiments/completed/2026-09-18-W-SL-light-phase-sleep.md`. 🔑 Only B2 pairs with the 09-10 baseline ⇒ n=1.
- 🎉⭐⭐⭐ **[8-CORE TETHER, 8 MICE — 2026-09-09](recording-2026-09-09-8core-tether-screen.md).** Best screen this rig ever made: 7/8 grounded, 7/8 EEG 96.6-100%. 🔴 `RMS_HI_UV=150` CLIPS REAL EMG.
- ⏳🔴⭐⭐⭐ **[S-SD RECOVERY SLEEP — 2026-09-02](s-sd-recovery-sleep-run-2026-09-02.md).** 20.0 h, animals SAMPLED ⇒ UNREPEATABLE. Pre-flight screen GATED for the first time.
- 🏁🔴⭐⭐⭐ **[W-SD BATCH CLOSED — 2026-08-28](w-sd-batch-closeout-2026-08-28.md).** Best full-cohort data: 5 with EEG, 4 pass rung 2. 🔴 7 d CSD collapsed 4 grounds ⇒ recovery comparison n=1.
- 🔴⭐⭐⭐ **[W-SD RECOVERY SLEEP — 2026-08-27/28](w-sd-recovery-sleep-run-2026-08-27.md).** B1 ground DECAYED 825→469 µV over 20 h = conductor working loose.
- ⭐⭐⭐ **[20.3 h B1-SWAP BASELINE — 2026-08-26](recording-2026-08-26-b1-swap-20h-baseline.md).** B1+C1 are the CHEWING CAGES. Never quote B1 %.
- ⭐⭐⭐ **[24 h ZT0-TO-ZT0, S-SD — 2026-08-25](recording-2026-08-25-24h-zt0-S-SD.md).** 🔴 EEG usability drops 15-34 pts in the DARK phase. 🛑 1 h snapshots badly overstate a 24 h run.
- ⭐⭐⭐ **[S-SD BATCH, 8 MICE — 2026-08-24](recording-2026-08-24-new-8-mice.md).** First cohort with REAL ids (HLBCSD11-19); manifest `cohorts/S-SD.yaml`. 🔴 Surgical bleeding notes do NOT predict signal quality. 🔴🔴 The PER-CHIP floor can itself be CONTAMINATED.
- ⭐⭐⭐ **[8 W-SD MICE — 2026-08-18](recording-2026-08-18-eight-new-mice.md).** Never call a channel animal-side before a re-seat + re-record. Strict rung 2 = EEG AND EMG in the SAME epoch.
- ⭐⭐⭐ **[A2 CONTROL, 48 h — BEST DATA EVER TAKEN HERE](a2-control-48h-reference-profile.md).** 47.09/48.19 h usable, zero railed epochs. Prefer ZT0 starts.
- ⭐⭐⭐ **[TWO ANIMALS WORK; THE TETHER IS THE FIX](overnight-two-animals-tether-is-the-fix.md).** Impedance SCREENS; only a multi-hour recording is an OUTCOME.
- **[ECG COHORT — 2026-08-07](ecg-cohort-2026-08-07.md).** 🔴 `set_recording_config()` BROKEN. ⚠️ `get_status().recording.path` LIES; always `ls`.
- ⭐⭐ **[3 SCOREABLE RECORDINGS + CIRCADIAN CHECK](staging-circadian-validation-2026-08-07.md).** ⚠️ SUPERSEDED as circadian evidence by [[a2-control-48h-reference-profile]].
- 🔴⭐⭐ **[FULL EEG RIG STATE](eeg-rig-current-state.md).** Channel law, signatures, retractions. ⚠️ Electrode-failure framing SUPERSEDED by the ground root cause.
- ⭐ Only ONE old recording has real sleep: 2026-07-31, C1 8.73 h, r@1min +0.744; C2 qualifies ⇒ n=2.
- ⭐⭐⭐ Channel selection SETTLED: `02-procedures/CANONICAL-allego-channel-selection.md`. ⚠️ That page is the OLD 2-channel map. **8-mouse montage = A/1, A/2, A/33, A/34 per port** (EEG+EMG × 2 mice/port).
- 🧹 Recording room stripped 2026-08-04: rack = wifi router + ASUS PC + XDAQ + white-noise gen. ⚠️ ALL CAMERAS REMOVED ⇒ NO VIDEO.
- 📤 KONTEX BATCH 2026-08-04: Q12 impedance polarity + Q13 spike-sorter filter errors; text in `01-infrastructure/vendor-correspondence/2026-07-29-kontex-kc-call-prep-rig-finalization.md`.
- **Hardware-video-sync (Phase 0a):** gate = `DO 03` (DB25 pin22) Gated mode + Allego BNC Breakout toggle ON. [[project_hardware_sync_neuronexus_reply]]

## Rig expansion (8 → 32 mice)
- ⭐⭐ **START AT `07-decisions/RIG-EXPANSION-HUB.md`.**
- 🔴⭐ [DAQ research corrections](daq-research-corrections-2026-07-28.md) — 8 primary-source corrections. Core has NO isolation; PortExp MANDATORY; don't buy Allego; Intan via White Mountain.
- ⭐ [XDAQ channel law](xdaq-channel-law-and-32-mouse-wiring.md) — animals = channels ÷ 64. Order ONE-R1024. 32 mice = 2 boxes.
- [DAQ comparison](daq-ecosystem-comparison.md) (confidential) · [16→32 device](acquisition-device-16-32-mice.md) · [Open Ephys](openephys-scale-up-option.md). Kontex quote 262024 = $10,002.89.

## Working across machines
- ✅🔴⭐⭐⭐ **[ONE REPO: `sleep-recording-skim`](workspace-single-repo-sleep-recording-skim.md).** Vault + code + Claude config. Sync = MANUAL `./skim status|pull|push|check`. **4 machines**; e10 cutover DONE 09-11. 🔴 `bootstrap.sh` KEEPS an existing `settings.json` ⇒ can leave a machine with NO hooks. DIFF IT.
- ✅🔴⭐⭐ **[THE THINKPAD IS ON THE WORKFLOW, set up remotely from e10 — 2026-09-19](workspace-single-repo-sleep-recording-skim.md).** 🔴 Its only gap was a **MISSING GIT IDENTITY — `check.sh` AND `skim status` both pass without one**. 🔑 e10→laptop = **Tailscale SSH + a TAG** (`dst` can only be `autogroup:self` or a tag). 🔴🔴 **Enabling Tailscale SSH HIJACKS port 22 and bypasses the real sshd** — it broke `ssh e10`; `--ssh=false` fixed it.
- ❌🔴 **[Syncthing UNINSTALLED from e10 + the OFFICE PC, 2026-09-16](multi-machine-setup-and-vault-safety.md).** ✅ Gone from the ThinkPad too ⇒ **retired everywhere**. Identities parked, not deleted. 🔴 `apt purge` does NOT stop the daemon; **`apt autoremove` blast radius VARIES** (52 pkgs / NVIDIA stack on the office PC). Why the vault died in 2026-04.

## Cloud / AWS
- ✅🔴⭐⭐ **[AWS ACCESS + AGENT TOOLKIT — 2026-09-19](aws-access-and-agent-toolkit.md). NEWEST.** Account 760396521414, profile `andrea`, `ap-northeast-2`, 12 h creds. 🔴 Ubuntu apt `awscli` HAS NO `aws login` — use the official installer. 🔴 `aws-mcp` needs `AWS_MCP_PROXY_PROFILES`.

## Host hardware / infrastructure
- `e10ubuntu` @ `192.168.0.50`: Intel Core Ultra 5 125H (14c/18t, iGPU), 30GiB RAM, 1.9TB NVMe. (CLAUDE.md says Ultra 7 — actual Ultra 5.)
- ⚠️ **Kernel 7.0.0-31 blocklists the Intel GPU in Chromium; 7.0.0-28 does not.** Rollback via `grub-reboot` is ONE BOOT ONLY. See [[allego-blank-monitor-canvas-texture-limit]].
- **Thermal = the wall:** PL1 capped 20W. Council leans proper desktop/SFF for a 72h live-animal instrument.
- ✅ **RustDesk + HDMI-switch crash FIXED** (2026-07-15). `GRUB_CMDLINE_LINUX_DEFAULT="quiet splash video=HDMI-A-1:1920x1080@60e"`. 1080p not 4K (thermal).
- **72h/20h runs (Jul 10-14):** byte-perfect files, 0 scoreable EEG. VIDEO recorded NOTHING. PC THROTTLED ~78%, peak 101°C.
- ✅ **[USB HDD would not mount = NTFS DIRTY BIT](usb-hdd-ntfs-dirty-bit.md)** — `sudo ntfsfix -d /dev/sda1`. 🛑 bare `ntfsfix` SETS the bit.

## NeuroSurveillance (video/NVR)
- Raspberry Pi 5 + Frigate NVR for sleep research. **Pi1** `192.168.0.11`: pi_cam_0/1. **Pi2** `192.168.0.12`: pi_cam_2/3. All 1024x768@15fps H.264. NVR `192.168.0.50`.
- **Backend** (Python 3.12 Flask) `neurosurveillance/backend/`: `daemon.py` + storage_monitor · radiens_poller · session_manager · frigate_controller · session_journal (SQLite WAL) · reconciler · recording_watchdog. Export ffprobe: `<0.95×` dur ⇒ partial.
- **Frontend** React 19 + TS + Tailwind + DaisyUI 5, Vite + Tauri. Polls `/api/status` 1.5s, `/api/health` 5s, `/api/storage` 10s.
- **Config** `/opt/neurosurveillance/config.yaml`. **Daemon auto video start/stop DISABLED 2026-07-03** (`sessions.auto_start:false`).
- Netdata v2.9.0 on NVR+Pi1+Pi2; Uptime Kuma (Docker, 7 monitors); Slack webhook. [[pattern_netdata_no_mqtt_collector]]
- [Exports move out of Frigate dir](frigate-exports-moved-out-of-frigate-dir.md) · [Recording toggle fragility](frigate-recording-toggle-fragility.md) (LEASE fix written, activates on next restart; dirs are UTC not KST) · [Docker upgrades fire recordings](project_docker_upgrade_recordings.md) (`apt-mark hold` 2026-05-20)
- Recurring Pi5 PoE crashes (Waveshare PoE HAT PMIC latch-up). Lab members list: only `["andrea"]`.

## Completed work
- ✅⭐⭐⭐ **[ALL 831 GB RAW DATA ON THE NAS + UNATTENDED RECORDING](raw-data-archive-and-recording-automation.md).** 124 files, sha256 both ends. 🔴 `radiens` only in `/opt/neurosurveillance/venv/bin/python3`. 🔴 `ssh` in a `while read` loop eats stdin — always `ssh -n`.
- ✅🔴⭐⭐⭐ **[SKIM LAB NAS + CHANNEL STRIPPER — 2026-09-11](skim-nas-smb-and-channel-stripper.md).** SMB-only, 94 MB/s. 🔴 A failed mount fills the rig's OWN NVMe. 🔴 CIFS read-back verification VACUOUS without `posix_fadvise(DONTNEED)`. 🔴 `np.memmap` = 9.26 GB RSS. 🛑 Never write to `~/radix/data`.
- 🔴⭐⭐ **[NAS BACKUP: 6-DAY OUTAGE WAS A WRONG IP](nas-backup-stale-address-outage.md)** — use MagicDNS `bilab-syn.tail8808c0.ts.net`. A `tailscale ping` pong proves nothing. NAS has 13 TB free. [[nas-backup]]
- **Stabilization sprint wk1 CLOSED** (May 22-26): Mosquitto auth + SHA-pins; SQLite WAL; Frigate restart-grace via LWT ([[pattern_frigate_mqtt_message_ordering]]); watchdog→Slack; nightly reconciler ([[pattern_frigate_record_enabled_orphan_noise]]).
- **Storage mgmt** (Apr 2): StorageMonitor 30s poll, 200GB EEG reserve. [[project_storage_management]]

## Planned work
- [Hardware-sync XDAQ→Pi GPIO](project_hardware_sync_neuronexus_reply.md) — vendor CLOSED; bench validation + ~$40 BOM. Pulse from the camera FRAME-CAPTURE CALLBACK, per-camera. In-frame LED REJECTED.
- [Settings sync gap](project_settings_sync.md) (deferred) · [Camera ROI framing](camera-roi-framing.md) · [Multi-user schedules](project_multiuser_recording_schedules.md) (⚠️ per-port claim RETRACTED, see radiens-4 note)

## Vault navigation
- ⭐⭐ **EEG ANALYSIS = FOUR PAGES:** `_eeg-analysis-hub.md` (START) · `pipeline/README.md` · `analysis-methods-and-justification.md` · `06-references/eeg-analysis-glossary.md`; symptoms in `03-troubleshooting/symptoms/eeg-analysis-problems.md`.
- ⭐ **`07-decisions/` = CHOICES ONLY.** Results→`05-experiments/completed/`, literature→`06-references/`, procedures→`02-procedures/`, symptoms→`03-troubleshooting/symptoms/`. [[reference-vault-07-decisions]]
- `02-procedures/allego-electrode-setup-sleep64.md` = THE electrode SOP · `signal-mapping-guide.md` · `signal-quality-and-grounding.md` · ⭐ `06-references/live-signal-quality-terms.md` (LIVE numbers: Signal Metrics controls, which metrics are spike-only junk for us, filter stages, `qc/preflight_screen.py`) · `06-references/radiens-software-reference.md` (PRIMARY Allego ref; manual PDF `06-references/datasheets/Radiens Technical Documentation.pdf`, Monitor p27/75-78, Electrodes p60-66) · `00-config/production-values.md`
- Environment: NVR hostname `e10ubuntu` (not `frigate-server`); user `skimlab`. We are ON the NVR — no SSH for local commands.

## Working preferences
- 🛑 **[NEVER strip or run heavy disk jobs while the rig is recording](feedback-never-strip-during-a-live-recording.md).** A console-started run strips itself on stop; `RIG BUSY` in a dry run = stop.
- [No dashes in emails](feedback_no_dashes_in_emails.md) · [Implementation guides preferred](feedback_leave_guides.md) · [Verify operational details](feedback_verify_operational_details.md) · [Don't suggest `record.enabled: false`](feedback_record_enabled_false_off_limits.md) · [Sudo command style](feedback_sudo_command_style.md) · [Report writing style](feedback_report_writing_style.md)

## Operational patterns
- [Docker SHA-pinning](project_docker_sha_pin_pattern.md) · [Frigate MQTT retained-topic ordering](pattern_frigate_mqtt_message_ordering.md) · [Frigate orphan noise](pattern_frigate_record_enabled_orphan_noise.md) · [No Netdata MQTT collector](pattern_netdata_no_mqtt_collector.md)
