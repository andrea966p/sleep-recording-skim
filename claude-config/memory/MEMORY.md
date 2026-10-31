# Project Memory

The vault (`vault/`) is the single source of truth for facts, results and procedures. Start every session at `vault/HOME.md`;
file and edit by the rules in `vault/CLAUDE.md`; run `./skim lint` (zero errors) before you stop. Memory holds only behaviour
rules and short pointers into the vault: when a hook and the vault disagree, the vault wins. Recency is shown by dates only.

## Allego (vault: 20-areas/allego)
- [Allego 30x stream, rate label lies](allego-stream-30x-rate-label-lies.md) — 09-30: said 1000 Hz, streamed 30 kHz. Before recording, compare `stream.time_range` with wall clock (~1.0x)
- [Blank Monitor = canvas over texture limit](allego-blank-monitor-canvas-texture-limit.md) — Launch WITHOUT `--disable-gpu` (confirmed 10-23; rig-check warns if present); kernel pinned 7.0.0-28. Later: move to Open Ephys GUI
- [Orphaned allegoserver blocks the rig](allego-orphaned-server-blocks-the-rig.md) — Parent `systemd --user`, holds ports 50051-4: check PPID first; kill by PID; verify exactly one instance
- [Allego Mesa GPU crash + log storm](allego-mesa-gpu-crash-and-log-storm.md) — 08-24: frozen GUI ≠ lost data, app death ends the recording. Fresh launch = 30 kHz + wrong mode: re-check. Risk back since 09-16
- [allegoserver runaway thread](allegoserver-runaway-thread-thermal.md) — Spins a core after the GUI closes (+10 W, +11 °C); `ps %CPU` is a lifetime average, use `top -b -n2`; plain `kill` fixes it
- [Allego stop works; size lags ~30 s](allego-stop-works-and-the-30s-size-lag.md) — 09-11: growth checks < 35 s are false negatives. Any script asserting growth stops the recording in a `finally`
- [Per-port recording works on Allego 4](radiens-4-has-no-per-port-recording.md) — 10-28: radiens-core 0.1.2, one file per port, one run per port. 🛑 Never import old `radiens`; a stop names its port; restart only in the current mode; after launch re-set 1000 Hz + split, `scan_ports()` after a rate change
- [First headstage bring-up](project_first_headstage_bringup.md) — 06-19: wrong Allego mode (SMARTBOX_PRO), never hardware. Use `Stream`, not `Record`, for checks (Record starts a video session)
## EEG rig: hardware and signal interpretation (vault: 20-areas/eeg-rig)
- [60 Hz saga and the hard rules](eeg-60hz-saga.md) — 🛑 NEVER suggest reseating an electrode/EMG wire (impossible post-implant; tether change = isoflurane). 🛑 Do NOT schedule surgeries
- [60 Hz mains discovery](eeg-60hz-mains-discovery.md) — 07-05: Korea mains is 60 Hz. Signals are already bipolar on the chip: never subtract EEG from EMG. Allego notch is display-only
- [Every run is new mice](cohort-identity-every-run-is-new-mice.md) — 🛑 Every run is new mice unless Andrea says otherwise. Rig position ≠ animal. Hardware facts carry across runs, animal facts do not
- [Weak chip ground hides](weak-chip-ground-hides-as-electrode-failure.md) — "No EEG" is 5 faults. EEG 60 Hz ÷ own chip floor: ≈0.03 normal, ≥1.0 open. 🛑 2000 µV gate falsified 10-01; gate = 59-61 Hz PEAK
- [Flicker: bent vs severed tether](flicker-discriminates-bend-from-break.md) — 80-150 % epoch variability = bending; 4-14 % = break. Mechanical test (rotate one tether while recording) is definitive
- [Contact is intermittent](movement-dependent-contact-root-cause.md) — 08-04: electrodes proven good; contact flips within minutes; movement hypothesis disproved same day. One sweep cannot classify
- [Fleet duty-cycle census](fleet-duty-cycle-census-and-new-mouse.md) — 08-06: empty tether read "connected" 22 % at 2 MΩ ⇒ use 0.5 MΩ. A single low impedance is never evidence of contact
- [B slot 1 was the tether](b-slot1-was-the-tether-not-the-port.md) — 08-26 swap: fault followed the animal/tether, not the port. A recurrence argument is not a swap test
- [Soldered tether duty cycle](tether-soldered-duty-cycle-result.md) — 08-05: B1 45 → 100 %, but construction, re-seat and isoflurane changed at once; arm C "harm" retracted
- [DMM continuity test](dmm-continuity-test-result.md) — 08-04: whole fleet passed; procedure CLOSED, do not rerun. Cold-joint and static slip-ring hypotheses are dead
- [Negative electrode unmeasurable](impedance-negative-electrode-unmeasurable.md) — Only `inX+` of each pair has ever been measured; Open Ephys does NOT fix it; DMM per pad. Do not propose switching software
- [Electrode failure literature](electrode-failure-literature.md) — 82 % of epidural electrodes fail in 3 weeks: real, NOT our failure mode. 🛑 Stop quoting "~6 % yield"
- [2 mice per board test](2mice_per_board_test.md) — 07-01: ONE mouse per headstage; TOP SPI socket dead, use BOTTOM. Never `GetIntanImpedance` while streaming
- [Gen-1 XDAQ has chassis GND](xdaq-gen1-has-chassis-gnd.md) — 09-30: wired to building earth (07-16 claim wrong). Noise tests go to `~/radix/noise-tests/`, never `~/radix/data`
## EEG analysis (vault: 20-areas/eeg-analysis)
- [Animal card + verdict ladder](animal-card-verdict-ladder.md) — Analysis entry point. `core/qc_thresholds.py` + `core/criteria.py` are the only engines. "Suites green = contract" is stale (10-22)
- [Contaminated floor](contaminated-floor-rejects-good-eeg.md) — Fixed 09-26: floor slope < −1.90 ⇒ UNJUDGEABLE; after 10-07 −1.90 no longer separates. 🛑 Never test floor vs animal. UNJUDGEABLE ≠ PASS
- [Floor threshold per chip](floor-threshold-fixed-per-chip.md) — 08-26: each chip vs its own floor; ungrounded chip (< 800 µV) ⇒ UNJUDGEABLE, not FAIL. Estimator chosen on robustness, not on who passes
- [EMG gate + pooled-floor bug](emg-gate-passes-and-floor-bug.md) — 08-21: state dependence on ABSOLUTE delta, never the ratio; per-chip null. Andrea does not want a methods paper
- [Mains in the EMG corrupts staging](emg-mains-corrupts-sleep-staging.md) — 10-02: 60/120 Hz notch validated (44 → 69/100 scoreable). 🛑 NOT adopted (re-scores published numbers); Andrea decides
- [Analysis stack audit](analysis-stack-audit-2026-08-11.md) — 08-11: filtering CAN manufacture slope (guard added); slope fractions carry ±20 pts; backwards pipeline deleted
- [Test suites: two verify nothing](test-suite-two-of-four-verify-nothing.md) — Regression suites exit 2 "NOTHING WAS VERIFIED" on e10 (fixtures only in S3, since 09-26). pytest venv `~/eeg-test-venv`
- [Council review + pipeline fixes](council-and-pipeline-fixes.md) — 08-08: 4 of 5 physiology checks cannot fail; never call circadian threshold-independent; never tune to `r@1min`
- [First hypnograms](hypnograms-and-per-mouse-export.md) — 08-21: `r@1min` decides (bar 0.30). 🛑 Never report REM %. All provisional until a kappa. `setsid`, not `nohup`
- [Light schedule](light-schedule-and-circadian-validation.md) — Lights 09:00 ON / 21:00 OFF KST, ZT0 = 09:00. xdat.json `start_time` is UTC, the uid token is KST. REM not separable
- [Usable fraction vs in-file floor](recording-usable-fraction-analysis.md) — XDAT float32, 262 interleaved ch, µV; band-pass 1.10-475 Hz. Never put `/17`-`/32`, `/49`-`/64` in the floor
- [Analysis pipeline](eeg-analysis-pipeline.md) — Stage 1-4 since 08-03. Never say "we deliberately differ from the literature"; `r@1min` is ours, label it. Day folder from UTC → KST
- [QC tooling lessons](eeg-qc-tooling.md) — Reject clipped epochs before any metric; report `keep%`. Allego forgets mode/rate/selection on every re-enumeration
- [Partial rig QC + unjudgeable presets](partial-rig-qc-and-unjudgeable-presets.md) — Pre-09-13 bundles for < 8 mice hold fake `UNKNOWN@slot` cards; `unipolar_lfp` has no QC criterion
## Rig bring-up runs, Jul to Aug 2026 (vault: 10-projects/rig-bringup)
- [72 h 4-mouse run](eeg-72h-4mouse-2026-07-10.md) — 07-10/13: byte-perfect, 0/4 scoreable, no video, PC throttled (101 °C). Its "floating system" root cause was retracted 07-16
- [ECG cohort](ecg-cohort-2026-08-07.md) — 08-07: 🔴 `set_recording_config()` broken; `get_status().recording.path` lies: always `ls` the destination
- [Ground on the wrong pin](ecg-cohort-ground-miswired.md) — 08-07: explains hum collapse + perfect impedance at once; fixed by a connector re-mate, no anaesthesia
- [Ground re-pin worked](ground-fix-worked-2026-08-08.md) — 08-08: hum criterion dead, use SLOPE (never for EMG). Screen on the stream, not the impedance sweep
- [Two animals work; the tether is the fix](overnight-two-animals-tether-is-the-fix.md) — 08-07: impedance SCREENS; only a multi-hour recording is an OUTCOME
- [A2 control 48 h](a2-control-48h-reference-profile.md) — 08-09/11: 47.09/48.19 h usable; a historical single animal, NOT a reference. The method transfers (prefer ZT0 starts), the animal does not
## HLB SOD1 EEG batches (vault: 10-projects/hlb-sod1)
- [Did SOD1 change sleep? 2x2](sod1-sleep-eeg-2x2-2026-10-06.md) — 10-06: EEG baselines are ON treatment; no detectable effect without SD; after SD n = 1 per arm (EMG rescue), a case
- [S-SL paired n = 3](s-sl-has-sleep-data-n3.md) — 09-26: HLBSSL31/33/35. 🛑 No sleep conclusion (window composition). uid0920 = uid0921 split; 09-30 note counts it 1 (3)
- [HLBW_SL 28 h](recording-2026-09-17-HLBW_SL-28h.md) — 09-17/18: unattended console workflow clean; 3 scoreable (B1 B2 D2), only B2 pairs ⇒ n = 1
- [8-core tether screen](recording-2026-09-09-8core-tether-screen.md) — 09-09: 7/8 chips grounded; A1 = ground-screw fault. 🔴 `RMS_HI_UV=150` clips real EMG
- [S-SD recovery sleep](s-sd-recovery-sleep-run-2026-09-02.md) — 09-02: animals sampled ⇒ unrepeatable; n = 0 scoreable at every S-SD timepoint (10-06 rescue later gave n = 1)
- [W-SD batch closeout](w-sd-batch-closeout-2026-08-28.md) — 08-28: 4 pass rung 2 pre-CSD; 7 d CSD collapsed 4 grounds; paired n = 1 (D2/HLBWSD08). n = 1 is a case
- [W-SD recovery sleep](w-sd-recovery-sleep-run-2026-08-27.md) — 08-27: window after the penultimate SD day; B1 ground decayed 825 → 469 µV over 20 h
- [B1-swap 20 h baseline](recording-2026-08-26-b1-swap-20h-baseline.md) — 08-26: B1 + C1 are chewing cages. 🛑 Never quote B1's percentage
- [24 h ZT0 S-SD run](recording-2026-08-25-24h-zt0-S-SD.md) — 08-25: EEG usability −15 to −34 pts in the dark; 1 h snapshots overstate; quote the vault's recomputed figures
- [S-SD first screen](recording-2026-08-24-new-8-mice.md) — 08-24: real ids HLBSSD11-19, `cohorts/S-SD.yaml`; surgical bleeding notes do not predict signal
- [W-SD first screen](recording-2026-08-18-eight-new-mice.md) — 08-18: strict rung 2 = EEG AND EMG in the same epoch; B1 verdicts after 08-19 17:16 belong to the old animal
## Noise hunt, Sep to Oct 2026 (vault: 10-projects/noise-hunt)
- [Grounding fix: mains collapsed](grounding-fix-2026-10-07-mains-collapsed.md) — 10-07/09: floors ÷12-60, A2 EMG 60 Hz → 1 µV. 800 µV gate calls EVERY chip UNJUDGEABLE: re-measure grounds, new gate (Andrea 10-23)
- [Noise hunt verdict](noise-hunt-verdict-2026-10-06.md) — 10-06: EMG mains is the only real noise. 🛑 No more long noise-chasing tests or spending (Andrea, 10-23: noise considered fixed). Never claim "all EEG clean"
- [Noise series, 4 mice, 24 h](recording-2026-10-01-noise-4mice-overnight.md) — 10-01/02: placeholder ids `POS-<slot>`; A1/B2 EMG open; Andrea's clock ≥ 8 s ahead. Console runs arm the watchdog since 10-14
## Unipolar LFP (vault: 10-projects/unipolar-lfp)
- [ahyeon's unipolar run](unipolar-run-2026-10-15-ahyeon.md) — Map /18 emg_l /19 lfp_tgt /20 lfp_ref /21 emg_r /22 eeg_p /23 eeg_f. 10-15 run lost (B off SPI scan, C reference). `get_signals()` is viz-filtered
## Rig expansion, 8 → 16/32 mice (vault: 10-projects/rig-expansion, start at `_rig-expansion-hub`)
- [Pinnacle wireless, 16 mice](pinnacle-wireless-16-mice-evaluation.md) — 10-19/23: 8474-HR-SE4-C confirmed, own headmount ≤ 6 mm, 12 + 4 units on one Windows PC (Sirenia has no Linux); ask Pinnacle about TTL
- [DAQ research corrections](daq-research-corrections-2026-07-28.md) — 07-28: Core has no isolation, Port Expander mandatory, don't buy Allego, Intan only via White Mountain
- [XDAQ channel law](xdaq-channel-law-and-32-mouse-wiring.md) — Animals = XR channels ÷ 64; order ONE-R1024 (R512 records 8); 32 mice = 2 boxes. Reason from animals, never channels
- [DAQ ecosystem comparison](daq-ecosystem-comparison.md) — 🛑 VAULT-ONLY (Kontex quote confidentiality): never publish as an Artifact. The "Intan strongest" reading is stale
- [Acquisition device 16/32 mice](acquisition-device-16-32-mice.md) — 07-21: Core hard-capped at 8 headstages (MISO lines); 16 = One+, 32 = 2x One+. Ruled-out adapter ideas stay dead
- [Open Ephys scale-up](openephys-scale-up-option.md) — Extension board dead (07-23); OE GUI drives our XDAQ licence-free. Close Allego before OE; never reflash the Core without KC
## Nanotag and the SOD1 sheet (vault: 20-areas/nanotag, 10-projects/hlb-sod1)
- [Nanotag SOD1 studies](nanotag-sod1-hlbnsl.md) — HLBNSL 10-05: no SOD1 effect. NS-SD: SD 11-03 + 11-04, Y-maze + sampling Wed 11-04, NOR dropped (10-30). 🛑 No SD/tests at weekends. Mouse = header tag ID
- [SOD1 sheet: change log + direct edits](sod1-sheet-pending-changes-tab.md) — Since 10-26 Claude Code edits via the Google Sheets connector, every change logged (last CHG-016). 🛑 Andrea OKs exact cells first; no paste files, no Drive-export fallback
- [HLBNSL behaviour videos](hlbnsl-behavior-videos-pointer.md) — Rules frozen in `nanotag/analysis/behavior/BEHAVIOR_SOP.md`. Videos on `kaist-bilab-win`; all cut to the trial (10-25). OFT/NOR tracked by YOLO pose: `max_det` > 1, floor per clip
## Computing: machines and workspace (vault: 20-areas/computing)
- Host `e10ubuntu` @ 192.168.0.50, user `skimlab`, Core Ultra 5 125H (not Ultra 7, not `frigate-server`). We are ON it: no SSH for local commands. Facts: `production-values`
- [One repo `sleep-recording-skim`](workspace-single-repo-sleep-recording-skim.md) — Manual `./skim status|pull|push|check|lint`, 5 machines (incl. Windows `kaist-bilab-win`, Git Bash). Diff a KEPT `settings.json`; set git identity. 🛑 No Tailscale SSH on e10
- [Syncthing retired, vault safety](multi-machine-setup-and-vault-safety.md) — Gone everywhere (09-19). `apt purge` doesn't stop the daemon; read the `apt autoremove` list on that machine every time
- [ThinkPad: NAS + e10 via personal tailnet b888](thinkpad-personal-tailnet-nas-e10.md) — 10-23: a share lands in the tailnet where it was accepted. Tailscale SSH on e10 was ON and blocked shared users: disabled
- [USB HDD NTFS dirty bit](usb-hdd-ntfs-dirty-bit.md) — Won't mount = dirty bit, not a dying drive: `sudo ntfsfix -d /dev/sda1`. 🛑 Bare `ntfsfix` SETS the bit
## Data storage and AWS (vault: 20-areas/data-storage)
- [Backup: 3 destinations](backup-architecture-three-destinations.md) — 09-20: bilab NAS = rebuild the rig, SKIM NAS = working copy NOT a backup, S3 = survive the fire. ntfy needs the full URL
- [83 % of raw had no raw backup](raw-data-had-no-offsite-copy-since-aug19.md) — 09-20: "NAS-verified" = the STRIPPED file (16/262 ch). Resolve NAS dirs via `UPLOAD.json` `allego_base`
- [Raw recordings off-site to S3](radix-s3-offsite-archive.md) — Bucket `skim-eeg-radix-archive-760396521414`, GLACIER_IR, cron 01:30, delete denied. No budget alert, none needed (Andrea, 10-23)
- [AWS access + agent toolkit](aws-access-and-agent-toolkit.md) — Account 760396521414, profile `andrea`, `ap-northeast-2`. 🔴 SSO never for unattended jobs. `chmod 700 ~/.aws` dirs on new machines
- [SKIM NAS per-mouse CSV layout](skim-nas-per-mouse-csv-layout.md) — Since 09-29: one CSV per mouse in `02_Data_Sleep/<user>/<batch>/<B|R>/`, 24 h windows; analysis reads the CSV, never the xdat
- [Nightly NAS backup](nas-backup.md) — Excludes `*.mp4`: exported video has no backup. GUI deletes sit in `~/.local/share/Trash` and free nothing until emptied
## Video NVR (vault: 20-areas/video-nvr)
- Cameras disconnected since 2026-08-04 (no video recorded); the area is ACTIVE and work will resume: never call it retired. Pi1 .11, Pi2 .12, NVR .50; `sessions.auto_start: false` since 07-03
- Alerts: Netdata, Uptime Kuma and deploy scripts → ntfy topic `nvr-b39a24e80833bb95` (09-14/09-20); recording-stall and reconciler alerts still Slack via `nvr-mqtt-slack`
- [Exports moved out of the Frigate dir](frigate-exports-moved-out-of-frigate-dir.md) — Check `/opt/neurosurveillance/exports/` before concluding an export failed; Frigate's DB row is a ghost
- [Recording toggle fragility](frigate-recording-toggle-fragility.md) — Retained MQTT toggle gates capture; OFF drops the last 10-20 s. Lease/drain fix loaded since the 10-07 restart (untested live). Dirs are UTC
- [Docker upgrades fire recordings](project_docker_upgrade_recordings.md) — aptdaemon docker upgrades restart Frigate on every camera; `apt-mark hold` (re-checked 10-22). Check `docker ps` uptime first
- [Startup-guard regression](project_daemon_startup_guard_regression.md) — 05-20: manual `docker start frigate` made 4 spurious sessions; fixed 05-24 (availability grace + 1.5 s defer)
## Video NVR: operational patterns
- [Docker SHA-pinning](project_docker_sha_pin_pattern.md) — No per-patch tag: pin `image: name:tag@sha256:<local digest>`; never guess tags
- [Frigate MQTT retained-topic ordering](pattern_frigate_mqtt_message_ordering.md) — State arrives BEFORE `frigate/available`: defer state callbacks 1.5 s; check real order with `mosquitto_sub`
- [Frigate orphan noise](pattern_frigate_record_enabled_orphan_noise.md) — `record.enabled: true` makes ORPHAN structural noise: keep 6 h minimum, alert only on partial/stuck/degraded
- [No Netdata MQTT collector](pattern_netdata_no_mqtt_collector.md) — MQTT alerts go through the `nvr-mqtt-slack` bridge; extend it, don't reach for a Netdata collector
## Completed infrastructure work
- [Raw archive + unattended recording](raw-data-archive-and-recording-automation.md) — 08-19/21: 🛑 never delete locally. `radiens` only in `/opt/neurosurveillance/venv/bin/python3`. `while read` loops: `ssh -n`
- [SKIM NAS + channel stripper](skim-nas-smb-and-channel-stripper.md) — 09-11: 🛑 never write to `~/radix/data`. A failed mount fills the NVMe; CIFS read-back needs `posix_fadvise(DONTNEED)`
- [NAS backup wrong-IP outage](nas-backup-stale-address-outage.md) — 08-14/19: use `bilab-syn.tail8808c0.ts.net`; a `tailscale ping` pong proves nothing, test the TCP port
- [Sprint phase 3](project_phase_3_complete.md) — 05-24: nightly reconciler (canonical for session QC: `/api/reconciler/last`), Frigate restart grace; ad-hoc `docker restart frigate` is safe
- [Sprint phase 4](project_phase_4_complete.md) — 05-25: watchdog stall alerts via the Slack bridge, ffprobe < 0.95x duration ⇒ partial export, runbooks
- [Storage management](project_storage_management.md) — 04-02: 30 s poll, 200 GB EEG reserve blocks new recordings, warn 75 % / critical 90 %, 1.7 Mbps per camera
## Planned or deferred work
- [Hardware sync XDAQ → Pi GPIO](project_hardware_sync_neuronexus_reply.md) — Gate = `DO 03` (DB25 pin 22), Wire 2 pulse from the frame-capture callback; bench validation owed. 🛑 No 24/7 recording
- [Settings sync gap](project_settings_sync.md) — Deferred: frontend settings live in localStorage only and never reach `config.yaml`
## Vault navigation
- Front door `vault/HOME.md`; rules for filing, frontmatter, INGEST / CLOSE-OUT / LINT in `vault/CLAUDE.md`. Notes link by bare name; never link a memory file from the vault
- Project hubs: `_hlb-sod1-hub`, `_rig-expansion-hub`, `_rig-bringup-hub`, `_noise-hunt-hub`, `_unipolar-lfp-hub`. Each hub's dated Current state is the only "current"
- Area hubs: `_eeg-rig-hub`, `_allego-hub`, `_recording-console-hub`, `_eeg-analysis-hub`, `_sleep-scoring-hub`, `_nanotag-hub`, `_data-storage-hub`, `_computing-hub`, `_video-nvr-hub`
- `vault/_meta/`: `path-map-2026-10-22.tsv` (old path → new), `contradictions/<key>.md` (needs-Andrea items), `log.md`; lint = `./skim lint`
- Old memory, verbatim: `vault/90-archive/claude-memory-2026-10-22/`. Key pages: `production-values`, `CANONICAL-allego-channel-selection` (A/1, A/2, A/33, A/34 per port)
- Artefacts: `eeg-artefact-and-railing-rejection-policy` (reject at EPOCH level, never repair). Is this signal usable: `animal-card-and-verdict-ladder`
## Working preferences (behaviour rules)
- [Background waits must terminate](feedback-background-waits-must-terminate.md) — 🛑 Deadline on every loop, no self-matching `pgrep -f`, explicit target file, TaskStop when done
- [neurosurveillance-expert skill retired](feedback-neurosurveillance-skill-retired.md) — 🛑 Retired 10-01: never use or cite it; vault + repo are the source
- [Never strip during a live recording](feedback-never-strip-during-a-live-recording.md) — 🛑 No stripping or heavy disk jobs while recording; console runs strip themselves on stop. `RIG BUSY` = stop; exception 10-29: console QC/strip of a per-port run may run while another port records
- [SOD1: EEG and nanotag separate](feedback-sod1-eeg-nanotag-separate.md) — 🛑 SOD1 effect: EEG and nanotag findings stay SEPARATE; never "nanotag agrees"; one section per method
- [No dashes in emails](feedback_no_dashes_in_emails.md) — 🛑 Never use dashes (`-` or `—`) in emails; recast with commas, parentheses, colons
- [No `record.enabled: false`](feedback_record_enabled_false_off_limits.md) — 🛑 Never propose Frigate `record.enabled: false` for restart-triggered recordings
- [Implementation guides](feedback_leave_guides.md) — For major features write a step-by-step vault guide in the area folder instead of coding; small fixes directly
- [Verify operational details](feedback_verify_operational_details.md) — Read the real unit/config files before naming services or paths (it is `neurosurveillance-session`)
- [Sudo command style](feedback_sudo_command_style.md) — Bare terminal commands, one per step, expected output stated; never the chat `!` prefix
- [Report writing style](feedback_report_writing_style.md) — Andrea's voice: informal first person, acronyms expanded, commas not dashes, TL;DR first, "still open" last
- [Colour-coded comparison tables](feedback-colour-coded-comparison-tables.md) — Status column first: 🟢 settled 🟡 uncertain 🟠 to ask 🔴 not applicable 🔵 our decision, legend callout above
## Sleep scoring (vault: 20-areas/sleep-scoring)
- [Andrea is learning sleep scoring](andrea-learning-sleep-scoring.md) — Scoring questions also go to the professor; log cases with screenshots in the journal; write Andrea's own rules
- [Work on local copies](work-on-local-copies.md) — Stage in `~/sleep-data`, check sha256 against `info.json`; never work on the NAS
- [SleepStager csv-reader branch](sleepstager-csv-reader-branch.md) — PR #1 + #2 open (10-22). 🛑 Never push to somnocode `main`. 60 Hz notch = our own fork change, no prof approval (10-23); check features notch
- [Sleep-scoring vault pages](sleep-scoring-vault-pages.md) — Start at `_sleep-scoring-hub` (handbook, user guide, backlog, working method, kappa)

## Deleted 2026-10-23 (stale)
Six memory files contradicted by later vault notes were deleted; verbatim copies are in
`vault/90-archive/claude-memory-2026-10-22/` (memory-eeg-analysis-codebase,
memory-eeg-qc-2026-07-14-two-runs, memory-eeg-rig-current-state,
memory-project_multiuser_recording_schedules, memory-staging-circadian-validation-2026-08-07,
memory-reference_vault_07_decisions). Do not recreate them; the vault holds the current facts.
