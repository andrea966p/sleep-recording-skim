---
tags: [index, navigation, home]
---

# NeuroSurveillance System Documentation

> [!abstract] Start here
> New to this vault? Read [[SYSTEM-OVERVIEW|the one-page system overview]] first — it explains what NeuroSurveillance is, what changed in the recent stabilization sprint, and where to read more.
> For a deeper Q&A walkthrough with durability guarantees and a glossary: [[01-infrastructure/system-overview|the deeper overview]].
> Onboarding a new lab member: [[02-procedures/new-researcher-onboarding|new-researcher-onboarding]].

> [!info] Quick Access
> | Service | URL |
> |---------|-----|
> | **Frigate** | http://192.168.0.50:5000 |
> | **go2rtc (Pi 1)** | http://192.168.0.11:1984 |
> | **go2rtc (Pi 2)** | http://192.168.0.12:1984 |
> | **Session Daemon** | http://127.0.0.1:8585 (NVR localhost) |
> | **Netdata (NVR)** | http://192.168.0.50:19999 |
> | **Uptime Kuma** | http://192.168.0.50:3001 |
> | **Status Page** | http://192.168.0.50:3001/status/neurosurveillance |
> | **Config** | [[00-config/production-values]] |
> | **Tasks** | [[00-config/task-dashboard]] |

---

## Documentation Map

### [[00-config/production-values|Configuration]]
Production IPs, usernames, paths, and settings.

### Infrastructure

**Raspberry Pi:**
- [[01-infrastructure/raspberry-pi/golden-go2rtc-config|go2rtc Config]]
- [[01-infrastructure/raspberry-pi/golden-systemd-service|systemd Service]]
- [[01-infrastructure/raspberry-pi/golden-boot-config|Boot Hardening]]
- [[01-infrastructure/raspberry-pi/watchdog-monitoring|Watchdog & Monitoring]]

**Frigate NVR:**
- [[01-infrastructure/frigate/docker-compose|Docker Compose]]
- [[01-infrastructure/frigate/config-yml|config.yml]]

**EEG recording pipeline (added 2026-09-13):**
- ⭐⭐⭐ [[01-infrastructure/eeg-recorder/pipeline-architecture|THE RECORDING PIPELINE — what runs, what fires it, and what stops it going wrong]] — the machinery behind the console: every program, what starts it, every failsafe and the specific way the rig can hurt you that each one exists for. 🔑 **§5 lists all six defects this system has had — every one was found by RUNNING it, not by testing it.** Read this before changing any guard.

**Backup (added 2026-08-19):**
- ⭐⭐ [[02-procedures/backup-architecture|CANONICAL — the three destinations and the one job each]] — **START HERE for backups.** bilab NAS = how to rebuild the rig · SKIM NAS = the working copy, **NOT a backup** · S3 = what survives the building burning down. The four pages below each describe ONE destination; this one says which is which (added 2026-09-20)
- ⭐ [[01-infrastructure/raw-recording-archive-to-nas|Raw recording archive to the NAS]] — the verified copy of all 831 GB of `.xdat` data. **Read this before deleting anything from `~/radix/data`.**
- [[02-procedures/installation/nas-backup|NAS backup (nightly project snapshot)]] — vault, code, daemon config
- ⭐⭐ [[02-procedures/installation/skim-nas-smb-and-upload|SKIM Lab NAS — mounting it over SMB, and uploading recordings safely]] — **a DIFFERENT NAS from the nightly backup above**: `SKIM_NAS`, SMB only (SSH is closed), per-member folders under `03_Data_Mouse`. 🔴 **A failed mount turns the destination into the rig's OWN system disk** — `mountpoint` does not catch it, hence the sentinel file. 🔴 **Reading a file back over CIFS verifies your own page cache** (1538 MB/s vs 90 MB/s) unless you `posix_fadvise` it away first (added 2026-09-11)
- ⭐⭐ [[02-procedures/installation/xdat-channel-stripping|Stripping an XDAT recording to the channels that were actually wired]] — 262 channels → 16, a **93.2% reduction**, verified bit-exact. 🔴 **Stripping DELETES the in-file wire-free floor**, so `compute_features` can never judge the recording again — the QC bundle is a PRECONDITION, not a follow-up. 🔴 **A keep list written as indices is not portable**: one recording here *was* 134 channels with 32-channel ports (deleted 2026-09-23; the rule stands, its counter-example does not). Use site labels (added 2026-09-11)
- 🔴 [[03-troubleshooting/incidents/2026-08-19-nas-backup-wrong-address|Incident: backup dead 6 days from one wrong IP]] — **why you must never hardcode a `100.x` address**

**Sleep recording (Intan RHD2216 + Allego) — operator docs:**
- [[02-procedures/sleep-recording-operator-manual|⭐ Sleep-Recording Operator Manual — START HERE, ordered phases from assembly to EEG/EMG analysis]]
- [[06-references/radiens-software-reference|⭐ Radiens Software — PRIMARY Reference (Allego + Videre)]] — **main software reference; embeds the full 177-page NeuroNexus manual + our load-bearing facts (mode, channel select, no in-GUI rename)**
- [[06-references/intan-rhd2216-reference|⭐ Intan RHD2216 Chip Reference — bipolar, ±5 mV rail, filters (datasheet-cited)]]
- ⭐⭐ [[02-procedures/CANONICAL-recording-windows-and-protocol|CANONICAL — recording windows, and which window of each run to analyse]] — **every session starts 09:00 ZT0. Baseline 09:00→09:00 (24 h); SD recovery 13:00→13:00 (24 h); ad libitum recovery 09:00→13:00 (28 h).** Longer is fine and gets trimmed; shorter is lost. Carries the eight canonical analysis windows and the discard list. **If any other page disagrees, this one wins.**
- ⭐⭐ [[02-procedures/CANONICAL-recording-naming-and-inventory|CANONICAL — what a recording is called, and every recording there is]] — **always `allego_N__uidMMDD-HH-MM-SS`; a bare `uid0910-09-00-00` names no file.** Holds the generated inventory of all 27 recordings on e10, which eight are the experiment, and the known discrepancies. **If any other page disagrees, this one wins.**
- ⭐⭐ [[02-procedures/CANONICAL-allego-channel-selection|CANONICAL — which Allego channels to select. SETTLED.]] — **select `/1`,`/2`,`/33`,`/34` per port. 16 channels for 8 mice.** Proven from the datasheet, the recorded metadata, and a measurement of all 64 slots on all 4 ports. **If any other page disagrees, this one wins.**
- [[02-procedures/signal-mapping-guide|⭐ Signal Mapping Guide — which channel is which electrode (EEG/EMG, step-by-step)]]
- [[02-procedures/signal-quality-and-grounding|⭐ Signal Quality & Grounding — fix the ground, then judge the signal]]
- [[02-procedures/grounding-reference-noise-concepts|Grounding vs Reference vs Tissue/Environmental Noise — concepts + slip-ring color defect]]
- [[02-procedures/eeg-emg-data-guide|EEG/EMG Data Guide — read by eye first, then analyze in Python]]
- [[02-procedures/rig-assembly-guide|Rig Assembly Guide — connect the full recording chain]]
- [[02-procedures/multimeter-guide|Multimeter Guide (Harden 661002) — power/continuity/short tests]]
- ⏳⭐ [[02-procedures/dmm-eeg-path-continuity-test|DMM continuity test on the EEG path — THE FREE TIER-1 BENCH TEST]] — **owed since 2026-08-02, run it before concluding anything about the implants.** No animal contact. Pads 2/3 (EMG) are the built-in control; includes the **slip-ring rotation test** that a static probe cannot replace
- [[02-procedures/allego-monitor-guide|Allego Monitor Tab Guide]]
- [[02-procedures/allego-sampling-rate|Allego Sampling Rate — 1 kHz min; 128–256 Hz = offline decimate]]
- [[02-procedures/allego-presets-workspace|Allego Presets & Save Workspace]]
- [[02-procedures/intan-headstage-troubleshooting|Intan Headstage Troubleshooting — symptom → cause → fix]]
- [[02-procedures/first-headstage-connection|First Headstage Connection — bring-up + channel map]] ✅ resolved 2026-06-19

**EEG data analysis (everything AFTER the recording exists):**
- ⭐⭐ [[02-procedures/eeg-data-analysis/per-mouse-export|Per-mouse export — raw + MATLAB + hypnogram per position]] — how to split a recording into one folder per mouse. **Not EDF.** Includes the `setsid` warning and how to read `_VERDICT.txt`.
- ⭐⭐ [[06-references/is-our-qc-approach-sound|Is our QC approach sound? — literature check, 2026-08-21]] — **read if you ever wonder whether this project is analysing its data in a defensible way.** Short answer: the method is sound, but **the bottleneck is hardware, not analysis**, and the field's currency is a kappa against a human scorer, which we still do not have.
- ⏳🔴 ⭐⭐⭐ [[05-experiments/active/2026-09-02-S-SD-recovery-sleep|S-SD RECOVERY SLEEP — the terminal endpoint, Wed 2026-09-02 13:00 → Thu 09-03 09:00]] — **NEWEST, READ FIRST.** 20.0 h, **CSD is FINISHED across this window** (unlike the W-SD 08-27 run, which sat after the PENULTIMATE bout), animals **SAMPLED Thu 13:00**, four hours after it stops ⇒ **UNREPEATABLE**. ✅ **The pre-flight screen ran BEFORE the run for the first time and a bench re-seat fixed ALL EIGHT chip grounds** (B2 117→2486, D2 1052→4541 µV) — 🎉 **D2 came back on BOTH roles and it was a GROUND fault, not an electrode.** 🔑 **The remaining faults split two ways on FLICKER, and only half are torsion:** A1/C1/C2 flip open↔closed on a seconds timescale with the chip floor unmoved (EEG rms variability 150/101/80%, max/min 49×/7.3×/55×) = a bending conductor; **B1/B2/D1 hold a FIXED open level (4.0/4.3/13.6%, max/min 1.2/1.1/1.8) = a continuous break, and straightening will NOT recover them.** 🔴 Go/no-go **AMBER, recorded in advance: n = 2 guaranteed (A2 EEG, D2 both), up to n = 5.** A 10 min re-screen GATES the start. 🛑 Both screens are 84-116 s ⇒ **no usable percentage may be quoted from them.**
- 🏁🔴 ⭐⭐⭐ [[05-experiments/completed/2026-08-28-W-SD-cohort-closeout|W-SD BATCH CLOSE-OUT — sampled 2026-08-28]] — **NEWEST, READ FIRST FOR THIS COHORT.** Everything W-SD produced, first screen to sampling. ✅ The pre-CSD baseline recomputed per-chip is **five positions with real EEG and FOUR passing strict rung 2** (A1 96.1% both roles with **39.5 h of EEG in long blocks**, D2 92.8%, A2 82.2%, C1 66.4%) — the best full-cohort data this rig has made. 🔴🔴 **The rebound recording — recovery sleep after the PENULTIMATE SD day, 13:00 Thu 08-27 → 09:00 Fri 08-28 — produced ONE usable animal, so the paired comparison is n = 1.** 🔑 **Cause identified and it is NOT the implants: four chip grounds collapsed over the seven days of deprivation** (A1 4976→1347, A2 4396→1575, D1 4441→1814, B1 1275→593 µV) and **A1 and A2, the two best animals, were lost this way** — an 80 s check 21 min after the run had them fully back. 🔑 **C1 passes rung 2 and is still withdrawn — that was a RUNG 4 call, not a connection failure.**
- 🔴 ⭐⭐⭐ [[03-troubleshooting/symptoms/weak-chip-ground-vs-open-electrode|"No EEG" is at least FOUR different faults]] — **READ BEFORE BLAMING ANY ELECTRODE.** A **weak** chip ground is a distinct fault from an open electrode **and it hides**: the channel stays proportionally normal against its own chip (**≈0.03 of the chip floor, same as a working channel**) while the whole reference collapses. Two numbers separate all four faults. 🔴 **The `FLOOR_MIN_HUM_UV = 800` gate is too low** — 6 chips below 2000 µV, **none produced EEG**; lowest working floor ever **2186 µV**. Proposed 2000, **NOT YET APPLIED**, awaiting a decision. ⭐ **Working EMG on a position exonerates that implant and tether** — both roles share the cable.
- ⭐⭐ [[02-procedures/pre-flight-connection-screen|The pre-flight connection screen — gate the run, don't annotate it]] — for any recording whose **timepoint dies with the animals**. 10 min, score the connection, fix what is fixable, re-screen, then start. 🔑 On 2026-08-27 the first-hour screen already said 1 of 8 positions worked; **the connector fix landed after the 20 h run had ended.** Write the go/no-go line in the journal so a missing animal is a decision, not a surprise.
- 🔴🔴 ⭐⭐⭐ [[05-experiments/completed/2026-08-21-39h-run-score|Scoring the 39.7 h run — 2026-08-21]] — ⚠️ **SUPERSEDED IN PART — recomputed per-chip on 2026-08-29, see the close-out above: FOUR positions pass rung 2, not three.** The EMG gate finally **PASSES** on **3** positions (A1, A2, D2), which unblocks the kappa at n=3. ⚠️ **C1 and C2 were withdrawn under falsification — C1 had the best number on the rig and it was an artefact.** And **the wire-free floor is POOLED across amplifier chips when the project's own definition says per-chip** — on that run the choice decides every rung-2 verdict. `floor_stats()` is not fixed.
- ⭐⭐⭐ [[02-procedures/eeg-data-analysis/animal-card-and-verdict-ladder|THE ANIMAL CARD AND THE VERDICT LADDER]] — **newest, and the new first step.** One page per animal-recording saying how far up six rungs that animal got and why it stopped. 🔑 **A rung is not evaluated if the rung below it failed**, and no panel is drawn for it. ⚠️ **The code moved out of this vault** to `~/sleep-recording-skim/eeg-emg-analysis/`; every constant is now in `core/qc_thresholds.py` and nowhere else. Proved by reproducing every published usable fraction exactly.
- ⭐⭐ [[02-procedures/eeg-data-analysis/_eeg-analysis-hub|START HERE — EEG data analysis]] — the four commands, what each stage decides, the four rules you must not break. **The only page that says what to run.**
- ⭐ [[02-procedures/eeg-data-analysis/pipeline/README|Pipeline operating manual]] — every stage in detail, every threshold with its provenance
- ⭐ [[02-procedures/eeg-data-analysis/analysis-methods-and-justification|Methods and justification]] — what is standard practice and what we added, with citations. **The one to hand to the professor.**
- 📖 [[06-references/eeg-analysis-glossary|Analysis glossary — every term and parameter in plain words]] — `nperseg`, `r@1min`, `Wn`, `DIRTY`, `ZT`, Otsu, block, rms, EDF. Search it when a word blocks you.
- 🔧 [[03-troubleshooting/symptoms/eeg-analysis-problems|Analysis troubleshooting — symptom lookup]] — including the failures that are **silent** (theta zeroed by `nperseg`, persistence measured across contact gaps)

**Hardware Sync (XDAQ GPIO):**
- [[01-infrastructure/hardware-sync/xdaq-core-gen1-ubuntu-driver|⭐ XDAQ Core (Gen-1) — Ubuntu Driver Setup + Verified State (2026-05-29)]] — **current source of truth; supersedes Core2 assumptions below**
- [[01-infrastructure/hardware-sync/overview|Overview & Architecture]] ⚠️ Core2-era
- [[01-infrastructure/hardware-sync/wiring-guide|Wiring Guide & BOM]]
- [[01-infrastructure/hardware-sync/gpio-sync-service|GPIO Sync Service (Golden Config)]]
- [[01-infrastructure/hardware-sync/radiens-api-reference|Radiens API — Digital I/O Reference]]
- [[01-infrastructure/hardware-sync/xdaq-core2-manual-reference|XDAQ Core2 Manual Reference (authoritative pinout + specs)]]
- [[01-infrastructure/hardware-sync/kontex-developer-portal-notes|Kontex Developer Portal Notes (libxdaq / pylibxdaq / Linux Thunderbolt)]]
- [[01-infrastructure/hardware-sync/literature-review|Literature Review]]

**Vendor Correspondence:**
- [[01-infrastructure/vendor-correspondence/kontex-call-confirmation-email-2026-07-29|Kontex — 2026-07-29 call confirmation + advance questions (SENT 2026-07-28)]]
- [[01-infrastructure/vendor-correspondence/neuronexus-inquiry-email|NeuroNexus / Kontex Inquiry & Replies]]
- [[01-infrastructure/vendor-correspondence/openephys-inquiry-email|Open Ephys Inquiry & Reply (Margarida)]]

**Session Daemon:**
- [[01-infrastructure/system-overview|System Overview — Q&A and glossary]]
- [[01-infrastructure/session-daemon/architecture|Architecture & Design]]
- [[01-infrastructure/session-daemon/session-journal|Session Journal — WAL (added 2026-05-23)]]
- [[01-infrastructure/session-daemon/reconciler|Reconciler — nightly WAL ↔ Frigate cross-check (added 2026-05-24)]]
- [[01-infrastructure/session-daemon/frontend-reference|Frontend Reference]]
- [[01-infrastructure/session-daemon/session-service|Systemd Service]]

**Monitoring & Alerting:**
- [[01-infrastructure/netdata/nvr-alerts-config|Netdata NVR Alerts (Golden Config)]]
- [[02-procedures/installation/monitoring-setup|Monitoring Setup Procedure]]
- [[02-procedures/installation/watchdog-slack-bridge|Watchdog → Slack Bridge (added 2026-05-25)]]
- [[03-troubleshooting/emergency-runbook|Emergency Runbook — first 10 min]]

### Procedures
- 🔴⭐ [[02-procedures/electrode-connection-state-test|Electrode connection state test — OPEN vs SHORTED vs WORKING]] — **the no-wire control method (2026-07-31).** Read before judging any electrode by impedance again.
- [[02-procedures/installation/new-pi-setup|New Pi Setup]]
- [[02-procedures/session-recording-workflow|Session Recording Workflow]]
- [[02-procedures/hardware-sync-setup|Hardware Sync Setup Procedure]]
- [[02-procedures/installation/storage-management-implementation|Storage Management System]] ✅
- [[02-procedures/new-researcher-onboarding|New Researcher Onboarding]] — day-0 access + first-recording walkthrough
- [[02-procedures/bus-factor-runbook|Bus-Factor Runbook]] — "Andrea is unreachable" emergency operator guide (added 2026-05-28)
- ⭐ [[02-procedures/scheduled-recording-and-watchdogs|Scheduled recording + watchdogs]] — start Allego at an exact time unattended and get Slack proof it is really writing bytes (added 2026-08-19)
- ⭐⭐⭐ [[02-procedures/rig-layout-and-recording-settings|TELLING THE CONSOLE WHAT THE RIG IS — splitters, headstages, recording settings]] — a splitter per port decides how many animals that port holds (2 chips = 64 ch = `A1`+`A2`; none = 32 ch = bare `A`), and one recording setting is shared by every mouse in a run. 🔑 **The console compares what you declared against what Allego actually enumerated and REFUSES to record if they disagree** — a wrong declaration used to be discovered after the animals were done. 🔴 The unipolar layout has **no QC criterion, and the reason is EVIDENCE-ABSENT not shape-mismatch**: its unused inputs are tied to ground, so a floor from them would flatter the control. Settings are addable in the console; the curated config is never machine-written 🔑 A port with no headstage gets an **In use** checkbox; the same mouse ID in two slots is refused before you can start, case-folded. ⚠️ Allego reporting 0 for an unplugged port is unit-tested only (added 2026-09-14)
- ⭐⭐⭐ [[02-procedures/starting-the-rig-after-a-restart|STARTING EVERYTHING AFTER A RESTART, A CRASH, OR A BLACK SCREEN]] — **start here when something looks down.** One command, `eeg-recorder/deploy/rig-check.sh`, answers whether the rig is ready and names the fix for anything that is not. 🔑 **Almost nothing needs starting**: the console, the NAS mount and Tailscale are system services and survive a desktop crash, a logout and a dropped RustDesk session — **a recording in progress keeps recording through all of them**. The only manual step is the Allego GUI. 🔴 **Check `uptime -s` before concluding the machine rebooted** — on 2026-09-13 a RustDesk restart looked exactly like a crash while the host had been up four weeks (added 2026-09-13)
- ⭐⭐⭐ [[02-procedures/eeg-recording-console|THE EEG RECORDING CONSOLE — set up a run, leave the room, find your data on the NAS]] — the local page at `http://127.0.0.1:8600` where each of the five lab members sets up their own run: who, which mouse in which slot, start/stop or schedule. On stop it strips the recording to the channels that were wired and uploads it, verified, to that person's NAS folder. 🔑 **Recording is GLOBAL — one box, one Record button, one file**, so one run owns the whole rig and per-user separation happens afterwards by stripping. 🔴 **"0 bytes" for the first ~30 s is NORMAL**, the file size lags. ✅ Proven end to end on a real 24 h 8-mouse run and on a scheduled bench run. 🔑 Type a **recording batch name** and the NAS folder is `YYYYMMDD_<batch>_<BSR|RSR|SDR>/` instead of Allego's own name (added 2026-09-11, updated 2026-09-13)

### Troubleshooting
- 🔴⭐ [[03-troubleshooting/symptoms/recording-console-retry-was-a-dead-end|The recording console's retry button did nothing — three defects found by the FIRST REAL RUN]] — all three passed every automated test and were found within minutes of a human using the tool. 🔴 **The worst was invisible: waiving the QC bundle flipped a flag on the SHARED worker, disabling the guard for every subsequent run by every user**, with no trace. Now per-run and recorded. 🔑 **Two copies of the same rule in different files will drift** — the API's retry map disagreed with the state machine's own table, so two of three retry paths returned HTTP 500 (added 2026-09-11)

**By Symptom:**
- [[03-troubleshooting/symptoms/no-frames-received|No frames received]]
- [[03-troubleshooting/symptoms/system-freeze-ssh-hang|System freeze / SSH hang]]
- [[03-troubleshooting/symptoms/frigate-high-cpu|Frigate 100% CPU]]
- [[03-troubleshooting/symptoms/docker-memory-crash|Docker memory crash]]
- [[03-troubleshooting/symptoms/allego-iir-filter-design-errors|Allego IIR filter design errors on Monitor band change]] — cosmetic, DEFERRED, does not affect recording
- ⭐ [[03-troubleshooting/symptoms/eeg-analysis-problems|EEG analysis problems — symptom lookup]] — wrong Python, missing mice, wrong day folder, blank EDF, **plus the two SILENT failures**: `nperseg` zeroing theta, and persistence measured across contact gaps

**Incident Log:**
- **Incidents** — `03-troubleshooting/incidents/`, one page per dated failure. A folder, so it is a path, not a link
- [[03-troubleshooting/incidents/2026-02-23-session-daemon-radiens-auth-cors|2026-02-23 Session Daemon Auth + CORS]]

### 📓 Daily Journal
- ⭐ [[04-journal/_JOURNAL-INDEX|Journal Index — chronological master navigator]] — **every day in date order.** The journal records what happened and links down into the detail notes. Start here to navigate by time rather than by topic.

### Experiments
**EEG runs and results — read these for the current scientific picture:**
- 🔴⭐⭐ [[05-experiments/completed/2026-09-11-allego-control-bench-test|2026-09-11 — BENCH TEST: STOPPING ALLEGO WORKS, AND THE FILE SIZE LAGS 30 SECONDS]] — twenty minutes on the live rig with no animals, to settle whether software may be trusted to start and stop the amplifiers. ✅ **`set_recording('off')` works on the first call** — the "never used here" flag was an absence of use, not a problem. 🔴🔴 **The real finding: `os.path.getsize()` reports 0 for a FULL 30 s after a perfectly healthy start**, then jumps to 31 MB (30,208 samples = 30.2 s). **Any growth check shorter than ~35 s reports a working recording as dead** — an 11 s check did exactly that, and because it asserted before its stop call it **left the rig recording**. ⭐ `qc/start_recording_at.py`'s 40 s window is safe; do NOT optimise it down. 🔑 Anything asserting on growth must stop the recorder in a `finally`. ⚠️ `ConfigRecording` is persistent — a test that redirects the path must restore it.
- ⭐⭐ [[02-procedures/blind-scoring-and-kappa|blind scoring and Cohen's kappa — READY TO RUN]] — the last unmeasured thing about the pipeline. Packs of 300 items are built for D2 and B1. ⭐ **§2 pre-registers what each kappa value will mean, written before a single epoch was scored**, including the REM rule that decides whether we ever report a REM share. 🛑 Never tune the threshold to maximise `r@1min` — that makes our own validity statistic circular.
- 📋 [[02-procedures/positive-control-known-signal-injection|positive control: known signal injection]] — **PLANNED, not scheduled.** Every control we have is negative; they prove we do not hallucinate signal, not that we find it. ⭐ Would also settle the standing **1.10 Hz hardware high-pass** question by measuring the real attenuation at 0.5 and 0.75 Hz. Half a day of bench time, ~£20 of parts, no animals.
- ⭐⭐ [[06-references/sleepyscore-japan-scoring-tool-algorithm|SleepyScore, the Japanese scoring tool: what its source ACTUALLY does]] — read off `SleepyScoreApp_HM_260312_exported.m` + `sleepy_pipeline_refined.py`. ⭐ **Their REM threshold is a 2-CLUSTER K-MEANS SPLIT, not a percentile** — the fix for our p80 rule. Their staging delta is a **0-4.5 Hz low-pass**, their EMG a **30 Hz high-pass**, features are **time-domain rectified integrals** not band powers. Confirms **no minimum-bout rule** exists in their method. `.3eg` format spec included.
- ⭐ [[03-troubleshooting/symptoms/per-animal-failure-signatures|per-animal failure signatures]] — four different faults hide behind a single `OPEN` verdict. ⭐ **The correlation between an animal's OWN two channels is the discriminator**: working animals 0.07-0.08, a shared-path wiring fault 0.74. Worked example on all 8 positions; **C2's chewed tether confirmed from the data**. 🔴 **A FIFTH fault was added 2026-08-29 — a WEAK (not absent) chip ground:** [[03-troubleshooting/symptoms/weak-chip-ground-vs-open-electrode]].
- ⭐⭐⭐ [[05-experiments/completed/2026-08-11-a2-control-48h-reference-profile|2026-08-11 — A2 OVER 48 HOURS: THE REFERENCE PROFILE FOR A WORKING ANIMAL]] — **START HERE, newest. The best data this project has ever taken.** **47.09 of 48.19 h usable, ZERO railed epochs in 17,349**, median slope −1.52 vs a floor p1 of −1.11, 60 Hz 36 µV vs a floor median of 2754 µV. ⭐⭐ **Started AND ended at ZT0 ⇒ two complete circadian cycles**, 24.2 h light and 24.0 h dark. ⭐ **The EMG is genuinely state-dependent** (r = −0.645, negative in BOTH phases separately) and its raw amplitude alone separates the phases, **31 µV light vs 73 µV dark**, with no scoring at all. ⭐⭐ **The circadian ordering survives the WHOLE ±25% sweep** (light beats dark by 25.5-42.7 points at every threshold) even though **the absolute % is STILL threshold-dependent and must not be quoted as fact**. ⭐⭐⭐ **AND IT REPLICATES ON ITSELF: asleep-in-light differs by 1.4 points and median light EMG by 0.1 µV across two consecutive days.** 🛑 The 0.90× row lands on the literature ~70% — **that threshold was NOT chosen**, it would be circular. ⚠️ **This is the CONTROL, not the fleet**, and there is still no kappa.
- ⭐⭐⭐ [[05-experiments/active/2026-08-08-ground-fix-post-repin-night|2026-08-08 — THE GROUND WAS RE-PINNED AND THE SIGNAL CAME BACK]] — **the fix that made the cohort possible.** Six of seven new mice re-pinned; **A1 could not be, so it is now a free NO-GROUND control sharing the surgery batch and tether with the six that were fixed.** ⭐⭐ In a 120 s live look **nine of 21 new-mouse channels went steeper than −0.9 (D/33 −0.32 → −1.79, B/1 −0.30 → −1.35) and the only three that did not move are A1's three.** ⭐ A 30-sweep block **pre-registered before it ran** confirmed both predictions: impedance got **much worse on the six repaired mice** and **barely moved on A1** — the "100% duty, zero flips" signature is gone from the repaired animals. 🔴 **No ECG channel passes the heartbeat test yet** (CV 0.35-0.58, needs <0.1). Recording `allego_0__uid0808-16-17-36` running.
- 🔴⭐⭐⭐ [[05-experiments/active/2026-08-07-ecg-cohort-baseline|2026-08-07 — THE ECG COHORT, AND THE GROUND WAS ON THE WRONG PIN]] — the diagnosis the page above tests. All seven new mice recorded with **no ground connection**: the cerebellum dura pin was mated to the **orange** (floating) wire while the **brown** wire in the headstage GND pad touched nothing. ⭐⭐ Explains the **fleet-wide hum collapse** (no ground ⇒ mains is common mode ⇒ a bipolar channel rejects it) **and** the **perfect impedance** (return runs through the paired electrode) at once. 🔑 **Zero flips was the tell — electrode failures are intermittent, wiring errors are not.** 🗂️ Pre-fix baseline `allego_0__uid0807-19-14-58`, 2.768 h, KEEP.
- 🔴⭐⭐⭐ [[07-decisions/2026-08-07-council-review-of-the-analysis-pipeline|2026-08-07/08 — COUNCIL REVIEW OF THE PIPELINE + THE FIXES]] — **READ BEFORE QUOTING ANY ANALYSIS NUMBER.** 🔴 The QC gate **selects on contact, contact is movement, movement is STATE** ⇒ selection bias. 🔴 **4 of 5 physiology checks CANNOT FAIL.** 🔴 **The Otsu ±25% sweep moves D2's circadian number from 23% to 89% ⇒ the circadian check is NOT threshold-independent.** ✅ Applied: minimum bout 12 s (+ raw-vs-smoothed split), the 4 IIIS alignment items, the Otsu sweep. ⛔ Council **rejected** "modernise the staging" at n=2 with no ground truth.
- ⭐⭐⭐ [[07-decisions/2026-08-07-rig-specification-and-analysis-method|2026-08-07 — THE RIG SPECIFICATION AND THE ANALYSIS METHOD]] — **THE PAGE TO ARGUE FROM.** Established claims with evidence-strength ratings, how the rig should be built, how the data must be analysed, what may not be claimed. ⚠️ **Carries a SCOPE BANNER: the cohort was replaced the same evening**, so the channel map (§2.2) and floor-control list (§3.1) are cohort-specific and already updated for the ECG cohort. The principles in Parts 1 and 3 are unaffected.
- ⭐⭐⭐ [[05-experiments/active/2026-08-07-staging-preregistration|2026-08-07 — THREE SCOREABLE RECORDINGS, AND THE CIRCADIAN CHECK PASSED]] — **B1 23.66 h in ONE block, r@1min 0.603; D2 23.28 h, r@1min 0.499; both 5/5 physiology, REM-from-NREM 73.9% and 79.5%.** ⭐ **Asleep in the light phase: D2 70.3%, B1 82.1%, against a literature ~70%** — external validation, since nothing in the pipeline knows the clock. 🔴 The pre-registered acclimatisation confound **did not materialise** (B1 slept MORE, not less), recorded rather than dropped.
- ⭐⭐⭐ [[05-experiments/completed/2026-08-07-overnight-recording-two-animals-work|2026-08-07 — TWO ANIMALS WORK NOW, AND THE TETHER IS THE FIX]] — **START HERE, newest.** 23.66 h, a full light/dark cycle: **B1 99.6% usable with an unbroken 3.6 h block, D2 86.5%**. 🔴 **RETRACTS the 2026-08-06 "arm C harmed D2"** — the swap took D2's EEG from **0.0% to 87.9%** usable, hum 917 → 133 µV, slope −0.38 → **−2.05**. The 40-sweep block had caught one long open state. ⭐ **D2 was tethered at day 8, so LONG RECOVERY IS NOT REQUIRED — the tether chain is sufficient**, and the cohort is recoverable **without new surgery**. 🔑 **Impedance blocks SCREEN; only a multi-hour recording is an OUTCOME** — always state a block's duration.
- 🔴⭐⭐ [[03-troubleshooting/symptoms/figure-and-analysis-audit-2026-08-08|2026-08-09 — FIGURE AND ANALYSIS AUDIT, what was wrong and what was rebuilt]] — **READ BEFORE CITING ANY FIGURE.** 🔴 A **fabricated reference band** (`62.0-7.8+8`, matching no published value) · **confidence intervals 5.4× too narrow** (epochs treated as independent when contact persists for tens of minutes) · **three figures held typed-in values** · 🔴⭐ **the tether headline 45%→100% is threshold-dependent and the EEG half reverses at the corrected 0.5 MΩ pass mark.** ✅ Also records what was checked and did NOT pass: 4 palette pairs flagged for grayscale, dpi reads 299.9994, PDFs not inspected, and a block bootstrap that was built and DISCARDED because its intervals did not bracket their own point estimate.
- 📄⭐⭐⭐ [[05-experiments/completed/2026-08-08-professor-update-short|2026-08-08 — EEG RIG UPDATE, THE TWO PAGE HANDOUT]] — **THIS IS THE ONE TO SEND.** Crucial points only, **9 figures, rebuilt 2026-08-09**: impedance trajectories of all 8 positions · fleet outcome · **real signal traces raw vs cleaned vs auto scaled, with the processing written on the figure** · spectra + the hum/slope discriminator · hypnograms across a full light/dark cycle · persistence + REM order nulls · **the Otsu ±25% sweep that breaks the circadian claim** · scoreable hours before/after the tether change · **fig 9 = the STATISTICS behind the hardware claims** (every channel vs 2,240 wire-free readings, Fisher exact + Jeffreys CIs; only 4 of 16 beat an unconnected input) · **fig 10 = the statistics behind the sleep claims** (permutation nulls, and **Spearman impedance vs yield rho 0.63 p 0.094, NOT significant at n=8**). Figures `05-experiments/attachments/2026-08-09-fig01..09-*.png` (PNG + PDF + provenance manifest + alt text), rebuilt by `eeg-emg-analysis/qc/figures_2026-08-08/`. 🔴 **Carries a CORRECTION: the tether duty-cycle headline 45%→100% was computed at the retired 2 MΩ pass mark; at the corrected 0.5 MΩ mark the EEG half REVERSES (5/20 → 2/20). The tether conclusion rests on the RECORDING, not on that block.**
- 📄 [[05-experiments/completed/2026-08-08-full-update-for-professor|2026-08-08 — THE TEST MICE, START TO FINISH: THE LONG WORKING RECORD]] — **the appendix behind the handout, not for sending.** Part 0 is paste-ready with no dashes. Part 1 is the whole narrative in the order we learned it (mains hum → the retracted clipping artefact → the no-wire control → **the channel map was wrong all along** → the persistence bug → movement-dependent contact → the 22% false-positive pass mark → **filtering manufactures 69 µV of fake EEG** → the retracted "arm C harmed D2" → the 23.66 h recording that worked). Part 2 is the analysis, the council review, and the **±25% Otsu sweep that damaged the circadian claim**. **Part 1b follows B1 and D2 INDIVIDUALLY, sweep by sweep, from their first connection on 30 July** — including the fact that **B1 is two different animals** (the original was sacrificed 5 Aug, detached skull electrode) and D2's full 0.660 → 9.200 → recovered → 87.9% arc. **Parts 1c and 1d cover the OTHER SIX POSITIONS and what their degradations imply** — the full 5-sweep impedance history of all 8 animals, **C1's collapse from the project's only real sleep recording (8.73 h, r 0.744) to 0.0% usable**, C2's chewed tether read off the data, **A1's textbook 0.087 MΩ muscle channel that still gives 5% usable data because 296 of its 331 µV is mains**, and D1/B2's shared-path correlations of 0.74 and 0.50. 🔑 **No animal shows a monotonic decline ⇒ not failing implants.** Part 3 is **claims defended / withdrawn / refused**. Part 4 is the two open items. ⚠️ Scope: the OLD EEG+EMG cohort only, and it is the complete dataset — those animals were replaced 7 Aug.
- 📄 [[05-experiments/completed/2026-08-06-rig-status-for-professor|2026-08-06/07 — RIG STATUS FOR THE PROFESSOR]] — **the handout.** Part 0 is a paste-ready short version; the rest is capacity vs yield, the method and why it changed, figures, statistics, interpretation, and what is still open.
- ⭐⭐⭐ [[05-experiments/completed/2026-08-06-fleet-duty-cycle-census|2026-08-06 — WE FINALLY GOT A NEGATIVE CONTROL, AND OUR PASS MARK WAS TOO GENEROUS]] — **START HERE, newest.** The A2 position holds a **cut cable with no mouse**; it passed the 2 MΩ test **22%** of the time, and so do 2,240 readings from **wire-free amplifier inputs** (`/3`-`/16`, `/35`-`/48`). Pass mark moved to **0.5 MΩ** (floor 3.1%). Re-scored, **only 4 of 14 channels beat an empty cable ⇒ the rig records 1 animal of 8.** ⭐ A mouse given **16 days of recovery** before tethering scored **40/40 with zero flips**, but it also got a new soldered tether, so **two variables changed at once**. ✅ Duty cycle **reproduces across days** (D2 27.5% → 30%).
- ⭐⭐⭐ [[05-experiments/active/2026-08-06-recording-data-quality-preregistration|2026-08-06 — THE RECORDING AGREES: ONE MOUSE OF EIGHT HAS EEG]] — pre-registered before the data existed. **B1 99.7% usable, everyone else 0.0% EEG.** 🔴 **Filtering a bare wire yields a median 69 µV of convincing fake EEG**, so trace appearance is never evidence; classify by **spectral slope** instead (B1 −2.15 vs a floor range of −1.10 to −0.04). §10 and §11 are a **plain-language walkthrough of the whole method and both figures**.
- ⭐⭐ [[02-procedures/eeg-artefact-and-railing-rejection-policy|artefact and railing rejection policy]] — reject at **epoch** level, never animal level, **but only after checking the surviving clean epochs still have real spectral shape**. 🔴 On this rig **railing is the open-electrode signature, not movement** — the no-mouse position rails 100% of the time. Always state **samples vs epochs**.
- ⭐⭐⭐ [[05-experiments/active/2026-08-05-tether-comparison|2026-08-05 — A SOLDERED TETHER TOOK THE DUTY CYCLE FROM 45% TO 100%]] — **START HERE, newest.** B1's EEG went 9/20 → **20/20** connected (p = 0.0001) and its EMG 20% → 75%, with zero flips and a worst reading of 1.341 MΩ against 9.089. Concurrent controls in a second animal did **not** improve, so it is not drift. ⚠️ The swap bundled tether construction, connector re-seating and anaesthesia, so **the cause is not isolated**. 🔴 **B1 was SACRIFICED the same evening because its skull electrode detached (NOT an anaesthesia death, corrected 2026-08-09); colony n = 7 and the slip-ring comparison is permanently lost.** Sweeps are now **automated** and the unit of measurement is a **duty cycle**, never a single reading.
- ⭐ [[05-experiments/completed/2026-08-05-unipolar-lfp-mouse-reference|2026-08-05 — the unipolar LFP mouse, a working reference prep]] — different surgery, no tether, no slip ring: **six live sites at once**, scorable EEG/EMG/LFP, first unambiguous EMG on the project. ⚠️ Changes five variables at once, so it assigns no cause. Also: impedance thresholds do **not** transfer between preps.
- ⭐⭐⭐ [[05-experiments/completed/2026-08-04-movement-dependent-contact|2026-08-04 — THE ELECTRODES ARE GOOD. THE CONTACT IS INTERMITTENT. The trigger is unknown]] — **START HERE.** B1's EEG hit **0.052 MΩ**, the best ever recorded here and inside the published 10-50 kΩ band, and **D2 recovered completely from fully open**, so the electrodes and implants are **good** and **NO SURGERY** is warranted. But B1's EEG read 6.236, 0.052, 8.649 and 0.177 MΩ across 23 minutes, so **a single sweep cannot rank or screen a channel**. ⚠️ A movement explanation was proposed and **disproved the same day**. (Superseded as the entry point by the 2026-08-05 tether result above; still the reference for why the electrodes are exonerated.)
- ⭐⭐ [[02-procedures/dmm-eeg-path-continuity-test|the DMM continuity test]] — ✅ **CLOSED 2026-08-04**, passed **fleet-wide**: pads, joints, shorts and 360° rotation all clean. Boards and solder exonerated. Do not run it again.
- [[06-references/impedance-sweep-register|impedance sweep register]] — all 14 sweeps, foldered by date, with the full 2026-08-04 session timeline
- ⭐⭐🔴 [[05-experiments/completed/2026-08-03-two-8-mouse-runs|2026-08-03 — THE TWO 8-MOUSE RUNS — Run 1 is everything we have, Run 2 is a total loss]] — C1 8.73 h + C2 2.34 h scoreable, validated against circadian norms; Run 2 = 0/8. ⚠️ Its "EEG degradation is directional (8/8 worse)" conclusion is **OVERTURNED** by the 2026-08-04 result above — that was a sampling artefact, not degradation.
- ⭐⭐🔴 [[05-experiments/completed/2026-08-01-channel-mapping-correction-first-sleep|2026-08-01 ⭐ CHANNEL MAP WAS WRONG — EMG always worked, FIRST REAL SLEEP ARCHITECTURE]] — `/1`=EEG `/2`=EMG already bipolar, `/3`,`/4` empty pads. Read before trusting any earlier EEG/EMG analysis.
- ⭐ [[05-experiments/completed/2026-08-03-data-quality-report-for-professor|2026-08-03 — data quality report for the professor]] — the full rescore of every recording
- 🔴⭐ [[05-experiments/completed/2026-07-31-contact-intermittency-no-wire-control|2026-07-31 — Legs are OPEN, not high-impedance, and state FLIPS on its own]] — **overturns "make new mice". DO NOT schedule surgeries on the old conclusion.**
- 🔴⭐ [[05-experiments/completed/2026-08-01-28h-contact-duty-cycle-and-c1-negative|2026-08-01 — 27.9 h run: duty cycle, grounds perfect, two failure modes]] — ⚠️ **its title and its "C1 has NO sleep" conclusion are RETRACTED** (C1 is the project's best result); read for the no-wire method and the grounds data only
- [[05-experiments/completed/2026-07-13-72h-4mouse-recording-audit|2026-07-13 — 72 h 4-mouse recording audit]]
- [[05-experiments/completed/2026-07-02-eeg-recording-checkpoint|2026-07-02 — EEG recording checkpoint]]
- ⏳⭐ [[05-experiments/active/2026-08-02-run2-preregistration|RUN 2 — pre-registered predictions]] — predictions written before the data

**Video / encoding:**
- [[05-experiments/completed/h265-encoding-failure|H.265 Failure (DO NOT USE)]]
- [[05-experiments/completed/2026-02-11-mpegts-container-test|MPEG-TS Container Test (adopted v5.2)]]
- [[05-experiments/active/|Active Experiments]]

### References
- 📖 [[06-references/eeg-analysis-glossary|⭐ EEG analysis glossary]] — every term and parameter in plain words (`nperseg`, `r@1min`, `Wn`, `DIRTY`, `ZT`, Otsu, block, rms, EDF)
- ⭐⭐🔴 [[06-references/electrode-failure-and-impedance-literature|Electrode failure + impedance literature — 82% of epidural electrodes fail in 3 weeks]] — six primary papers vs our data. **Weakens the "EMG works so it must be our solder" argument**; our best channel is poor by published standards; drops the frontal-sinus hypothesis.
- 🔴⭐ [[06-references/daq-research-findings-primary-sources|DAQ research findings — primary sources]] — 8 corrections; read before trusting older DAQ notes
- [[06-references/daq-ecosystem-comparison-xdaq-vs-openephys|DAQ ecosystem comparison — XDAQ vs Open Ephys vs Intan]] — priced BOMs (confidential, vault only)
- [[06-references/monitoring-diagnostics|Monitoring Diagnostics]] — Netdata/Uptime Kuma query commands for troubleshooting
- [[06-references/command-cheatsheet|Command Cheatsheet]]
- [[06-references/video-parameters|Video Parameters]]

### Rig Expansion (8 → 32 mice)
- ⭐ [[07-decisions/RIG-EXPANSION-HUB|RIG EXPANSION HUB — 8 → 32 Mice]] — **START HERE.** Single entry point: the decision, all vendor correspondence, wiring, open items, superseded claims
- [[07-decisions/2026-07-24-daq-32-mouse-final-comparison|DAQ 3-way comparison, 32 mice (XDAQ vs Open Ephys vs Intan)]] — the decision doc + professor summary
- [[06-references/xdaq-32-mouse-wiring-and-channel-law|XDAQ 32-mouse wiring + the channel law]] — animals = channels ÷ 64; full power-to-mouse wiring
- [[01-infrastructure/vendor-correspondence/2026-07-29-kontex-kc-call-prep-rig-finalization|Kontex call prep, 2026-07-29 — rig finalization]] — 45 questions + live build checklist

### Decisions & Reviews
`07-decisions/` holds **decisions only** — architecture choices, council reviews,
sprint plans. Trimmed 2026-08-03 from 26 files to 9; results moved to
`05-experiments/completed/`, literature and comparisons to `06-references/`,
procedures to `02-procedures/`, vendor call prep to
`01-infrastructure/vendor-correspondence/`.

- ⭐ [[07-decisions/RIG-EXPANSION-HUB|RIG EXPANSION HUB — 8 → 32 mice]] — the entry point for the expansion decision
- [[07-decisions/2026-07-27-video-eeg-sync-recording-architecture|2026-07-27 — video/EEG sync + recording architecture]] — the alignment plan; no clocks, pulse train mandatory
- [[07-decisions/2026-07-24-daq-32-mouse-final-comparison|2026-07-24 — DAQ 3-way comparison, 32 mice]]
- [[07-decisions/2026-07-21-acquisition-device-16-32-mice-and-kontex-thread|2026-07-21 — acquisition device for 16-32 mice]]
- [[07-decisions/2026-07-21-openephys-acquisition-board-scale-up-option|2026-07-21 — Open Ephys scale-up option]]
- [[07-decisions/2026-07-16-camera-node-scale-up|2026-07-16 — camera node scale-up]]
- [[07-decisions/2026-07-15-earth-and-sleep-council|2026-07-15 — earth and sleep council]] ⚠️ its "first sleep biology" result is **RETRACTED** (clipping artefact)
- [[07-decisions/2026-05-01-llm-council-review|2026-05-01 LLM Council Review]] — full advisor responses, peer reviews, chairman synthesis, staged plan
- [[07-decisions/2026-05-stabilization-sprint-week-1-plan|2026-05 Stabilization Sprint Week 1 — Plan + live status]] — single source of truth for sprint-item status

### Archive
- `99-archive/` — the 2026-05 rehaul snapshots and superseded pages. The old
  Notion import folder it used to list was removed and no longer exists.

---

## System Status

| Component | IP | Status |
|-----------|------|--------|
| **Pi 1** | 192.168.0.11 | Online |
| **Pi 2** | 192.168.0.12 | Online |
| **go2rtc (Pi 1)** | :1984 | Online |
| **go2rtc (Pi 2)** | :1984 | Online |
| **Frigate** | 192.168.0.50:5000 | Online |
| **Session Daemon** | 127.0.0.1:8585 | Healthy (daemon + MQTT + Radiens connected) |
| **Netdata (NVR)** | 192.168.0.50:19999 | Active (16 NVR alerts, Slack notifications) |
| **Netdata (Pi 1)** | 192.168.0.11:19999 | Active |
| **Netdata (Pi 2)** | 192.168.0.12:19999 | Active |
| **Uptime Kuma** | 192.168.0.50:3001 | Active (7 monitors, Slack alerting) |
| **nvr-mqtt-slack** | systemd (NVR) | Active (watchdog stalls → Slack; added 2026-05-25) |
| **NAS (`Bilab_Syn`)** | `bilab-syn.tail8808c0.ts.net` | Reachable (shared in from the `bilab` tailnet; 13 TB free). **Use the name, never an IP.** |
| **Nightly project backup** | `nas-backup.timer` 00:00 | Active — fixed 2026-08-19 after 6 days dead; now also covers `eeg-emg-analysis` |
| **Raw data archive** | cron watchdog, 20 min | 124 files / 831 GB copied + checksum-verified 2026-08-19 |
| **Recording watchdog** | cron, hourly | Armed while a recording runs; self-disarms on stop |

---

## Quick Commands

```bash
# Pi health check
ssh skimlab@192.168.0.11 'vcgencmd measure_temp && systemctl status go2rtc'

# Frigate logs
ssh skimlab@192.168.0.50 'docker logs frigate --tail 20'

# Stream test
ffprobe rtsp://192.168.0.11:8554/pi_cam_0
```

---

## Emergency

1. Check the symptom pages in `03-troubleshooting/symptoms/` — start with [[03-troubleshooting/symptoms/eeg-analysis-problems|analysis problems]] or [[03-troubleshooting/symptoms/no-frames-received|no frames received]]
2. Run: `sudo systemctl restart go2rtc.service`
3. See [[06-references/command-cheatsheet|Command Cheatsheet]]

---

## 🔗 Links that do not resolve, and are not meant to

> [!warning] `[[eeg-60hz-saga]]` and about 22 other slugs are NOT missing pages
> They are **memory notes**, living in `claude-config/memory/*.md` — Claude's
> persistent memory, which is in this repository but **outside the vault**, so
> Obsidian cannot resolve them. `eeg-60hz-saga` alone is linked 48 times from 20
> pages and is a real 25 KB document; it is simply not a vault page.
>
> 🛑 **Do not "fix" them by creating stub pages.** That would put the same fact in
> two places with no way to tell which is current — the exact failure this vault
> spent 2026-09-23 undoing. A link checker will keep reporting roughly 86 of
> these; that count is expected, not a backlog.
>
> To read one: `claude-config/memory/<slug>.md` at the repository root.
> Whether the two namespaces should be merged is an open question, not a bug.

---

*Last updated: 2026-06-27 (📚 **sleep-recording operator documentation set shipped** — new [[02-procedures/sleep-recording-operator-manual|operator manual]] (start-here hub) + 8 new docs: Intan RHD2216 chip reference (datasheet-cited), rig-assembly, multimeter, Allego Monitor/sampling-rate/presets, headstage troubleshooting, EEG/EMG data guide. Verified finding: **128–256 Hz acquisition impossible; Allego min = 1 kHz → decimate offline**. Earlier 2026-06-19 (🎉 **first headstage detected — electrophysiology first light.** Intan RHD2216 enumerates on the XDAQ Core Gen-1, streaming shows signal. Root cause of the prior block was a wrong Allego system mode (`SMARTBOX_PRO`); correct = **"XDAQ One (G1) with XR Headstage"** / `XDAQ_ONE_REC` — see [[02-procedures/first-headstage-connection]]. No hardware fault, no RMA). Prev 2026-05-29 (XDAQ unit identified as Gen-1 Core / Opal Kelly USB — NOT Core2; Ubuntu driver solved via plugdev udev rule, Allego detects device; new authoritative doc `xdaq-core-gen1-ubuntu-driver`, Core2 docs banner-flagged, KC email trimmed). Prev 2026-05-28 (Phase 4.6 reconciler→Slack enabled in bridge; vault restructure — `07-decisions/` section added; council + sprint plan extracted out of `04-journal/2026-05-01.md` and `2026-05-20.md` into their own decision docs; daily journals get `created:` frontmatter for stable sort; bus-factor runbook shipped — Phase 6 council Stage 3.4 closed)*
