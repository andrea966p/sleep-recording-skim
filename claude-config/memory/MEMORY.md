# Project Memory

## EEG rig — Allego / hardware behaviour
- 🔑 **[Allego 60 Hz notch = DISPLAY-ONLY; impedance needs stream OFF](eeg-60hz-saga.md).** Verified 07-31 + 10-01, never re-check.
- 🔴 **[Stream ran 30× real time while Allego said 1000 Hz (09-30)](allego-stream-30x-rate-label-lies.md).** Measure `stream.time_range` vs wall clock (~1.0×) before recording.
- 🔴 **[Blank Monitor = canvas bigger than the renderer (09-16)](allego-blank-monitor-canvas-texture-limit.md).** Launch WITHOUT `--disable-gpu` (Intel GL 16384 vs SwiftShader 8192).
- 🔴 **[Orphaned allegoserver makes a healthy rig look dead](allego-orphaned-server-blocks-the-rig.md).** Parent `systemd --user`, holds ports 50051-4. Check PPID first.
- 🔴 **[Allego Mesa GPU crash + 6.5 GB log storm (08-24)](allego-mesa-gpu-crash-and-log-storm.md).** Frozen GUI ≠ lost data; app death ends the recording. Fresh launch = 30 kHz/SMARTBOX_PRO, re-check.
- 🔴 [allegoserver spins a core after the GUI closes](allegoserver-runaway-thread-thermal.md): +10 W/+11 °C; `ps %CPU` misleads.
- 🔴 **[Allego stop works; file size lags ~30 s](allego-stop-works-and-the-30s-size-lag.md).** Growth checks < 35 s are false negatives. Stop in a `finally`.
- 🔴 **[radiens 4.0.0 has no per-port recording](radiens-4-has-no-per-port-recording.md).** Recording is GLOBAL; 4.0.0 is latest, don't upgrade. `AllegoClient.restart()` broken too.
- 🛑 **NEVER suggest reseating an electrode/EMG wire** (impossible post-implant; tether change = isoflurane). **Do NOT schedule surgeries.** Signals are already bipolar, never subtract EEG from EMG.

## EEG rig — signal interpretation
- 🔴 **["No EEG" is 5 faults; a weak ground hides](weak-chip-ground-hides-as-electrode-failure.md).** EEG 60 Hz ÷ own chip floor: ≈0.03 normal, ≥1.0 open. Floor scale is geometry-dependent (2000 µV falsified 10-01). Gate = 59-61 Hz line PEAK.
- 🔑 **[Flicker tells a bent tether from a severed one](flicker-discriminates-bend-from-break.md).** 80-150 % variability = bending; 4-14 % = break.
- **[Electrodes proven good; contact is intermittent](movement-dependent-contact-root-cause.md).** One sweep cannot classify.
- **[The 0.5 MΩ criterion](fleet-duty-cycle-census-and-new-mouse.md).** An empty tether read "connected" 22 % of the time at 2 MΩ.
- ✅ **[The ground re-pin worked (08-08)](ground-fix-worked-2026-08-08.md).** Hum criterion dead, use SLOPE (never for EMG).
- 🔴 **[Root cause: cerebellum ground on the wrong pin](ecg-cohort-ground-miswired.md).** Explains hum collapse + perfect impedance at once.
- 🔴 **[B slot 1 was the tether, not the port](b-slot1-was-the-tether-not-the-port.md).** A recurrence argument is not a swap test.
- 🔴 **[Every run is new mice unless Andrea says otherwise](cohort-identity-every-run-is-new-mice.md).** Rig position ≠ animal.
- 🟡 Only `inX+` of each electrode pair has ever been measured; [Open Ephys does NOT fix it](impedance-negative-electrode-unmeasurable.md).
- ⚠️ [82 % of epidural electrodes fail in 3 weeks](electrode-failure-literature.md): real literature, NOT our failure mode.
- 🔴 **[Partly loaded rig graded on all 8 slots](partial-rig-qc-and-unjudgeable-presets.md).** Pre-09-13 bundles for < 8 mice hold `UNKNOWN@slot` cards; `unipolar_lfp` has no QC criterion.

## EEG rig — analysis stack
- 🔴 **[Mains in the EMG corrupts sleep staging (10-02)](emg-mains-corrupts-sleep-staging.md).** 60/120 Hz notch validated: 44 → 69/100 scoreable, shuffle 0/100, dark>light 47/49. 🛑 NOT adopted (re-scores published numbers).
- ✅ **[Contaminated floor reported healthy EEG as 0 % (fixed 09-26)](contaminated-floor-rejects-good-eeg.md).** Floor slope < −1.90 ⇒ UNJUDGEABLE. 🛑 Never test the floor against the animal. UNJUDGEABLE ≠ PASS.
- ⭐ **[Animal card + verdict ladder](animal-card-verdict-ladder.md). READ BEFORE ANY ANALYSIS OR FIGURE.** `core/qc_thresholds.py` + `core/criteria.py` are the only engines.
- ✅ [Floor threshold per chip (08-26)](floor-threshold-fixed-per-chip.md): ungrounded chip ⇒ UNJUDGEABLE, not FAIL.
- 🔴 [EMG gate + pooled-floor bug](emg-gate-passes-and-floor-bug.md): always ABSOLUTE delta, never the ratio.
- 🔴 [Analysis stack audit (08-11)](analysis-stack-audit-2026-08-11.md): filtering CAN manufacture slope; slope fractions carry ±20 pts.
- 🔴 [Test suite: 2 of 4 verify nothing](test-suite-two-of-four-verify-nothing.md): they SKIP yet exit 0. venv `~/eeg-test-venv`.
- [Council review + pipeline fixes](council-and-pipeline-fixes.md): 4 of 5 physiology checks CANNOT FAIL.
- **[First hypnograms](hypnograms-and-per-mouse-export.md).** `r@1min` decides, bar 0.30. 🛑 Never report REM %. `/usr/bin/python3`, `setsid` not `nohup`.
- [Usable fraction vs an in-file control](recording-usable-fraction-analysis.md): XDAT float32, 262 interleaved ch, µV; hardware band-pass 1.10-475 Hz.
- [Analysis pipeline](eeg-analysis-pipeline.md) · [Scoring bug #2](eeg-analysis-codebase.md) · [QC tooling](eeg-qc-tooling.md) · [First bring-up](project_first_headstage_bringup.md) · [Light schedule 09:00 ON / 21:00 OFF, ZT0 = 09:00](light-schedule-and-circadian-validation.md)
- **Artefact policy:** `02-procedures/eeg-artefact-and-railing-rejection-policy.md`. Reject at EPOCH level, never repair.

## EEG rig — runs
- ✅🔴⭐ **[GROUNDING FIX COLLAPSED THE MAINS (10-07)](grounding-fix-2026-10-07-mains-collapsed.md). NEWEST.** Socket + XDAQ bonded to earthed rack: floors x12-60, A2 EMG 60 Hz 26-33 → 1 µV. 🔴 800 µV gate now calls EVERY chip UNJUDGEABLE: fix before next real run. Run `ee0263bffeaa` until 10-08 21:02.
- 🧪⭐⭐⭐ **[Did SOD1 change sleep? 4 EEG batches as a 2x2 (10-06)](sod1-sleep-eeg-2x2-2026-10-06.md). NEWEST.** EEG baselines are ON treatment. No effect without SD. EMG rescue between 60 Hz harmonics (raw 1000 Hz, κ 0.95) ⇒ HLBSSD15 paired: rebound +6.6 vs water +16.1, n=1/arm; max rescue adds nothing.
- ✅⭐ **[Noise hunt verdict: mostly a ghost (10-06)](noise-hunt-verdict-2026-10-06.md). NEWEST.** EMG mains is the only real noise; the notch removes it. 🛑 No more environmental-noise trials or spending. Isolated socket + foil busbar coming; lab moving to E7. Never claim "all EEG clean".
- 🌙 **[Noise series, 4 mice, 24 h (10-01/02)](recording-2026-10-01-noise-4mice-overnight.md).** Placeholder IDs `POS-<slot>`; A1/B2 EMG open. 🔴 Console runs do NOT arm the watchdog. B1 flipped UNJUDGEABLE → PASS untouched (audit C1). Andrea's clock ≥ 8 s ahead.
- ✅ **[S-SL paired n = 3 (09-26)](s-sl-has-sleep-data-n3.md).** HLBSSL31/33/35. 🛑 No sleep conclusion (window composition). uid0920 = uid0921 split.
- ✅ **[HLBW_SL 28 h (09-17/18)](recording-2026-09-17-HLBW_SL-28h.md).** Unattended workflow clean. 3 scoreable (B1 B2 D2); only B2 pairs ⇒ n = 1.
- 🎉 **[8-core tether, 8 mice (09-09)](recording-2026-09-09-8core-tether-screen.md).** Best screen ever. 🔴 `RMS_HI_UV=150` clips real EMG.
- 🔴 **[S-SD recovery sleep (09-02)](s-sd-recovery-sleep-run-2026-09-02.md).** Animals sampled ⇒ unrepeatable. n = 0 scoreable; D2 EMG has no muscle-band modulation.
- 🏁 **[W-SD batch closed (08-28)](w-sd-batch-closeout-2026-08-28.md).** 4 pass rung 2; 7 d CSD collapsed 4 grounds. D2/HLBWSD08 n = 1 at rung 3.
- 🔴 [W-SD recovery sleep (08-27)](w-sd-recovery-sleep-run-2026-08-27.md): B1 ground decayed 825 → 469 µV over 20 h.
- [20.3 h B1-swap baseline (08-26)](recording-2026-08-26-b1-swap-20h-baseline.md): B1 + C1 = chewing cages, never quote B1 %.
- [24 h ZT0-ZT0, S-SD (08-25)](recording-2026-08-25-24h-zt0-S-SD.md): 🔴 EEG usability −15 to −34 pts in the dark; 1 h snapshots overstate.
- [S-SD batch, 8 mice (08-24)](recording-2026-08-24-new-8-mice.md): real ids HLBSSD11-19, `cohorts/S-SD.yaml`; bleeding notes don't predict signal.
- [8 W-SD mice (08-18)](recording-2026-08-18-eight-new-mice.md): strict rung 2 = EEG AND EMG in the same epoch.
- ⭐ **[A2 control 48 h, best data ever](a2-control-48h-reference-profile.md).** 47.09/48.19 h usable. Prefer ZT0 starts.
- [Two animals work; the tether is the fix](overnight-two-animals-tether-is-the-fix.md): impedance SCREENS; only a multi-hour recording is an OUTCOME.
- [ECG cohort (08-07)](ecg-cohort-2026-08-07.md): 🔴 `set_recording_config()` broken; `get_status().recording.path` lies, always `ls`.
- [3 scoreable + circadian check](staging-circadian-validation-2026-08-07.md) (superseded by the A2 48 h) · [Full EEG rig state](eeg-rig-current-state.md) (electrode-failure framing superseded)
- Only one old recording has real sleep: 2026-07-31 C1 8.73 h (r@1min 0.744); C2 qualifies ⇒ n = 2.
- Channel selection: `02-procedures/CANONICAL-allego-channel-selection.md` (OLD 2-ch map). **8-mouse montage = A/1, A/2, A/33, A/34 per port.**
- Room stripped 2026-08-04: rack = wifi router + ASUS PC + XDAQ + white-noise gen. ⚠️ ALL CAMERAS REMOVED ⇒ NO VIDEO.
- 📤 Kontex batch 08-04 (Q12 impedance polarity, Q13 spike-sorter filters): `01-infrastructure/vendor-correspondence/2026-07-29-kontex-kc-call-prep-rig-finalization.md`.
- Hardware-video-sync gate = `DO 03` (DB25 pin 22) Gated mode + Allego BNC Breakout toggle ON. [[project_hardware_sync_neuronexus_reply]]
- ✅ **[Gen-1 XDAQ HAS a chassis GND, wired to building earth (09-30)](xdaq-gen1-has-chassis-gnd.md).** The 07-16 claim was wrong. Noise tests → `~/radix/noise-tests/`.

## Rig expansion (8 → 32 mice)
- **Start at `07-decisions/RIG-EXPANSION-HUB.md`.** [DAQ corrections](daq-research-corrections-2026-07-28.md) (Core has no isolation, PortExp mandatory, don't buy Allego, Intan via White Mountain) · [XDAQ channel law](xdaq-channel-law-and-32-mouse-wiring.md) (animals = ch ÷ 64, order ONE-R1024, 32 mice = 2 boxes) · [DAQ comparison](daq-ecosystem-comparison.md) (confidential) · [16→32 device](acquisition-device-16-32-mice.md) · [Open Ephys](openephys-scale-up-option.md). Kontex quote 262024 = $10,002.89.

## Nanotag studies (SOD1, no EEG)
- 🧪 **[Nanotag SOD1 study HLBNSL (10-05)](nanotag-sod1-hlbnsl.md).** Run 1 + 2 merged; no SOD1 sleep effect. 🔴 Mouse = header tag ID; `.nta` mtime = save time. ⚠️ No off-site copy.

## Working across machines
- ✅ **[One repo `sleep-recording-skim`](workspace-single-repo-sleep-recording-skim.md).** Manual `./skim status|pull|push|check`, 4 machines. 🔴 `bootstrap.sh` keeps an existing `settings.json` (maybe no hooks): diff it. 🔴 Set the git identity on new machines (checks pass without it). e10→ThinkPad = Tailscale SSH + tag; 🔴 Tailscale SSH on e10 hijacks port 22.
- ❌ [Syncthing retired everywhere (09-16/19)](multi-machine-setup-and-vault-safety.md): `apt purge` doesn't stop the daemon; `apt autoremove` blast radius varies.
- ✅ **[SKIM NAS: one CSV per mouse in 02_Data_Sleep, 24 h windows (09-30)](skim-nas-per-mouse-csv-layout.md).** 64 folders verified; `info.json` carries the `qc` verdict.

## Cloud / AWS
- ✅ **[Backup: 3 destinations, one job each (09-20)](backup-architecture-three-destinations.md).** bilab NAS = rebuild the rig · SKIM NAS = working copy, NOT a backup · S3 = survive the fire. Alerts via ntfy.
- 🔴 **[83 % of the raw archive had no raw backup (09-20)](raw-data-had-no-offsite-copy-since-aug19.md).** "NAS-verified" = the STRIPPED file (16/262 ch). Resolve NAS dirs via `UPLOAD.json` `allego_base`.
- ✅ **[Raw recordings go off-site to S3](radix-s3-offsite-archive.md).** `skim-eeg-radix-archive-760396521414`, GLACIER_IR, cron 01:30. No budget/alerts (user request). IAM user with Deny on delete. No passwordless sudo on e10.
- ✅ **[AWS access + agent toolkit (09-19)](aws-access-and-agent-toolkit.md).** Account 760396521414, profile `andrea`, `ap-northeast-2`. 🔴 SSO never for unattended jobs. 🔴 `chmod 700 ~/.aws{,/login,/login/cache,/cli,/cli/cache}` on new machines.

## Host hardware / infrastructure
- `e10ubuntu` @ `192.168.0.50`: Core Ultra 5 125H (CLAUDE.md says Ultra 7, wrong), 30 GiB RAM, 1.9 TB NVMe. Thermal is the wall (PL1 20 W); council leans desktop/SFF for 72 h runs.
- ⚠️ Kernel 7.0.0-31 blocklists the Intel GPU in Chromium; 7.0.0-28 does not. `grub-reboot` rollback = one boot only. [[allego-blank-monitor-canvas-texture-limit]]
- ✅ RustDesk + HDMI-switch crash fixed (07-15): `GRUB_CMDLINE_LINUX_DEFAULT="quiet splash video=HDMI-A-1:1920x1080@60e"`; 1080p, not 4K.
- 72 h/20 h runs (Jul 10-14): byte-perfect, 0 scoreable EEG, video recorded nothing, PC throttled ~78 %, peak 101 °C.
- ✅ [USB HDD would not mount = NTFS dirty bit](usb-hdd-ntfs-dirty-bit.md): `sudo ntfsfix -d /dev/sda1`; bare `ntfsfix` SETS it.

## NeuroSurveillance (video/NVR)
- Pi5 + Frigate NVR. Pi1 `192.168.0.11` (pi_cam_0/1), Pi2 `192.168.0.12` (pi_cam_2/3), 1024x768@15fps H.264, NVR `192.168.0.50`.
- Backend Flask `neurosurveillance/backend/` (daemon, storage_monitor, radiens_poller, session_manager, frigate_controller, session_journal SQLite WAL, reconciler, recording_watchdog); export ffprobe < 0.95× dur ⇒ partial. Frontend React 19 + Vite + Tauri.
- Config `/opt/neurosurveillance/config.yaml`; daemon auto video start/stop DISABLED 2026-07-03 (`sessions.auto_start:false`).
- Netdata v2.9.0 (NVR, Pi1, Pi2), Uptime Kuma (7 monitors), **ntfy** topic `nvr-b39a24e80833bb95` (Slack retired 09-20). [[pattern_netdata_no_mqtt_collector]]
- [Exports out of the Frigate dir](frigate-exports-moved-out-of-frigate-dir.md) · [Recording toggle fragility](frigate-recording-toggle-fragility.md) (lease fix pending restart; dirs UTC not KST) · [Docker upgrades fire recordings](project_docker_upgrade_recordings.md) (`apt-mark hold`)
- Pi5 PoE crashes (Waveshare PoE HAT PMIC latch-up). Lab members list: only `["andrea"]`.

## Completed work
- ✅ **[All 831 GB raw on the NAS + unattended recording](raw-data-archive-and-recording-automation.md).** 🔴 `radiens` only in `/opt/neurosurveillance/venv/bin/python3`. 🔴 `ssh` in a `while read` loop eats stdin: `ssh -n`.
- ✅ **[SKIM lab NAS + channel stripper (09-11)](skim-nas-smb-and-channel-stripper.md).** 🔴 A failed mount fills the NVMe; CIFS read-back needs `posix_fadvise(DONTNEED)`. 🛑 Never write to `~/radix/data`.
- 🔴 [NAS backup 6-day outage = wrong IP](nas-backup-stale-address-outage.md): use `bilab-syn.tail8808c0.ts.net`; a `tailscale ping` pong proves nothing. [[nas-backup]]
- Stabilization sprint wk1 closed (May 22-26): Mosquitto auth, SHA pins, SQLite WAL, Frigate restart grace ([[pattern_frigate_mqtt_message_ordering]]), nightly reconciler ([[pattern_frigate_record_enabled_orphan_noise]]).
- Storage mgmt (Apr 2): 30 s poll, 200 GB EEG reserve. [[project_storage_management]]

## Planned work
- [Hardware sync XDAQ→Pi GPIO](project_hardware_sync_neuronexus_reply.md): bench validation + ~$40 BOM; pulse from the camera frame-capture callback; in-frame LED rejected.
- [Settings sync gap](project_settings_sync.md) (deferred) · [Camera ROI framing](camera-roi-framing.md) · [Multi-user schedules](project_multiuser_recording_schedules.md) (per-port claim retracted)

## Vault navigation
- **EEG analysis = 4 pages:** `_eeg-analysis-hub.md` (start) · `pipeline/README.md` · `analysis-methods-and-justification.md` · `06-references/eeg-analysis-glossary.md`; symptoms `03-troubleshooting/symptoms/eeg-analysis-problems.md`.
- **`07-decisions/` = choices only**; results → `05-experiments/completed/`. [[reference-vault-07-decisions]]
- `02-procedures/allego-electrode-setup-sleep64.md` (electrode SOP) · `signal-mapping-guide.md` · `06-references/live-signal-quality-terms.md` (live numbers) · `06-references/radiens-software-reference.md` (primary Allego ref; manual PDF Monitor p27/75-78, Electrodes p60-66) · `00-config/production-values.md`
- Hostname `e10ubuntu` (not `frigate-server`), user `skimlab`. We are ON the NVR: no SSH for local commands.

## Working preferences
- 🛑 **[Background waits must terminate](feedback-background-waits-must-terminate.md):** deadline on every loop, no self-matching `pgrep -f`, TaskStop when done.
- 🛑 **[neurosurveillance-expert skill retired](feedback-neurosurveillance-skill-retired.md):** never use it; vault + repo are the source.
- 🛑 **[Never strip or run heavy disk jobs while recording](feedback-never-strip-during-a-live-recording.md).** `RIG BUSY` in a dry run = stop.
- 🛑 **[SOD1 effect: EEG and nanotag findings stay SEPARATE](feedback-sod1-eeg-nanotag-separate.md):** never "nanotag agrees"; one section per method.
- [No dashes in emails](feedback_no_dashes_in_emails.md) · [Implementation guides](feedback_leave_guides.md) · [Verify operational details](feedback_verify_operational_details.md) · [No `record.enabled: false`](feedback_record_enabled_false_off_limits.md) · [Sudo command style](feedback_sudo_command_style.md) · [Report writing style](feedback_report_writing_style.md)

## Operational patterns
- [Docker SHA-pinning](project_docker_sha_pin_pattern.md) · [Frigate MQTT retained-topic ordering](pattern_frigate_mqtt_message_ordering.md) · [Frigate orphan noise](pattern_frigate_record_enabled_orphan_noise.md) · [No Netdata MQTT collector](pattern_netdata_no_mqtt_collector.md)

## Sleep scoring / SleepStager (from the SleepStager-folder sessions, merged 2026-10-09)
- [Andrea is learning sleep scoring](andrea-learning-sleep-scoring.md) — scoring questions go to the professor; log cases with screenshots
- [Work on local copies](work-on-local-copies.md) — stage in ~/sleep-data, never on the NAS
- [SleepStager csv-reader branch](sleepstager-csv-reader-branch.md) — PR #1 (CSV) + #2 (resume fix) open, tone row local only, feature 60 Hz notch pending
- [Sleep-scoring vault pages](sleep-scoring-vault-pages.md) — handbook, user guide, backlog, decision, journal cases
