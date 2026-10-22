# Move map for review (vault rehaul 2026-10-22)

Every note's new home. Nothing has moved yet. File names are kept unless listed under
Renames. Journal notes stay in `04-journal/` and are not listed.

**250 notes** · status: - 6, active 116, done 94, planned 10, superseded 21

## Renames

- `00-config/task-dashboard.md` → `TASKS.md`
- `00-config/weekly-view.md` → `TASKS-WEEK.md`
- `01-infrastructure/system-overview.md` → `nvr-system-overview.md`
- `02-procedures/eeg-data-analysis/pipeline/README.md` → `eeg-pipeline-manual.md`
- `02-procedures/eeg-data-analysis/scripts/_archive_pre_sleep64/README.md` → `scripts-archive-pre-sleep64-readme.md`
- `02-procedures/eeg-data-analysis/scripts/contact-state-2026-07-31/README.md` → `scripts-contact-state-2026-07-31-readme.md`
- `02-procedures/eeg-data-analysis/scripts/rescore-v2-2026-08-03/README.md` → `scripts-rescore-v2-2026-08-03-readme.md`
- `99-archive/2026-08-09-pipeline-moved-to-repo/README.md` → `pipeline-moved-to-repo-readme.md`

## Leaving the vault

- DELETE `05-experiments/active.md` — 0-byte stub.
- DELETE `05-experiments/templates.md` — 0-byte stub.
- DELETE `05-experiments/templates/TEMPLATE-experiment.md` — Older copy of _templates/Experiment.md; differs only by Templater placeholders and a stripped body.
- DELETE `06-references/datasheets/Radiens Technical Documentation.pdf` — byte-identical duplicate of neuronexus/Radiens-Technical-Documentation.pdf, which is the embedded copy [coord]
- DELETE `06-references/neuronexus/sensor-maps/radiens.log` — Log file from 2026-07-14 gRPC errors
- DELETE `radiens.log` — stray Allego log
- 27 code files (.py .sh .pyc .bak, csv2sensor binary) move to `eeg-emg-analysis/archive/vault-scripts/` and `tools/neuronexus/`
- 164 images and figure files go to `_attachments/` (flat)

## (root)  (2)

| note | type | status | from |
|---|---|---|---|
| TASKS-WEEK | hub | active | 00-config |
| TASKS | hub | active | 00-config |

## 10-projects/hlb-sod1  (19)

| note | type | status | from |
|---|---|---|---|
| 2026-08-18-W-SD-cohort-first-screen | experiment | done | 05-experiments/completed |
| 2026-08-21-39h-run-score | experiment | done | 05-experiments/completed |
| 2026-08-24-S-SD-first-hour-screen | experiment | done | 05-experiments/completed |
| 2026-08-25-S-SD-24h-ZT0-run | experiment | done | 05-experiments/completed |
| 2026-08-27-B1-swap-baseline-20h-run | experiment | done | 05-experiments/completed |
| 2026-08-27-W-SD-recovery-sleep | experiment | done | 05-experiments/completed |
| 2026-08-28-W-SD-cohort-closeout | experiment | done | 05-experiments/completed |
| 2026-09-02-S-SD-recovery-sleep | experiment | done | 05-experiments/completed |
| 2026-09-14-HLBNSL-nanotag-SOD1-sleep | experiment | done | 05-experiments/active |
| 2026-09-18-W-SL-light-phase-sleep | experiment | done | 05-experiments/completed |
| 2026-09-23-S-SL-connection-audit | experiment | done | 05-experiments/completed |
| 2026-09-28-HLBNSL-sheet-handover | procedure | done | 05-experiments/completed |
| 2026-09-30-scoreable-mice-on-the-24h-windows | experiment | done | 05-experiments/completed |
| 2026-10-05-HLBNSL-nanotag-merged-analysis | experiment | done | 05-experiments/completed |
| 2026-10-05-HLBNSL-sheet-handover-run2 | procedure | active | 05-experiments/active |
| 2026-10-06-S-SD-EMG-rescue-between-harmonics | experiment | done | 05-experiments/completed |
| 2026-10-06-SOD1-sleep-EEG-2x2-quick-compute | experiment | done | 05-experiments/completed |
| _HLB-SOD1-project-hub | hub | active | 05-experiments |
| sod1-sheet-change-log-workflow | procedure | active | 02-procedures |

## 10-projects/noise-hunt  (6)

| note | type | status | from |
|---|---|---|---|
| 2026-09-30-xdaq-noise-series | experiment | done | 05-experiments/active |
| 2026-10-02-light-phase-run-rig-session | experiment | done | 05-experiments/active |
| 2026-10-02-noise-series-4mice-24h-analysis | experiment | done | 05-experiments/completed |
| 2026-10-02-noise-series-method-audit | experiment | done | 05-experiments/completed |
| 2026-10-02-noise-troubleshooting-plan | experiment | active | 05-experiments/active |
| 2026-10-06-noise-hunt-verdict | experiment | done | 05-experiments/completed |

## 10-projects/rig-bringup  (21)

| note | type | status | from |
|---|---|---|---|
| 2026-06-28-eeg-recording-troubleshooting-report | experiment | done | 03-troubleshooting/incidents |
| 2026-07-02-eeg-recording-checkpoint | decision | done | 05-experiments/completed |
| 2026-07-13-72h-4mouse-recording-audit | experiment | done | 05-experiments/completed |
| 2026-07-15-earth-and-sleep-council | decision | done | 07-decisions |
| 2026-07-31-contact-intermittency-no-wire-control | experiment | superseded → [[2026-08-01-channel-mapping-correction-first-sleep]] | 05-experiments/completed |
| 2026-08-01-28h-contact-duty-cycle-and-c1-negative | experiment | superseded → [[2026-08-01-channel-mapping-correction-first-sleep]] | 05-experiments/completed |
| 2026-08-01-channel-mapping-correction-first-sleep | experiment | done | 05-experiments/completed |
| 2026-08-02-run2-preregistration | experiment | done | 05-experiments/active |
| 2026-08-03-two-8-mouse-runs | experiment | done | 05-experiments/completed |
| 2026-08-04-movement-dependent-contact | experiment | done | 05-experiments/completed |
| 2026-08-05-tether-comparison | experiment | done | 05-experiments/active |
| 2026-08-06-fleet-duty-cycle-census | experiment | done | 05-experiments/completed |
| 2026-08-06-recording-data-quality-preregistration | experiment | done | 05-experiments/active |
| 2026-08-06-unloaded-chain-interference | experiment | done | 05-experiments/active |
| 2026-08-07-ecg-cohort-baseline | experiment | done | 05-experiments/active |
| 2026-08-07-overnight-recording-two-animals-work | experiment | done | 05-experiments/completed |
| 2026-08-07-staging-preregistration | experiment | done | 05-experiments/active |
| 2026-08-08-ground-fix-post-repin-night | experiment | done | 05-experiments/active |
| 2026-08-11-a2-control-48h-reference-profile | experiment | done | 05-experiments/completed |
| experiment-pad7-floating-input-B1 | experiment | planned | 02-procedures |
| first-headstage-connection | experiment | done | 02-procedures |

## 10-projects/rig-expansion  (10)

| note | type | status | from |
|---|---|---|---|
| 2026-07-21-acquisition-device-16-32-mice-and-kontex-thread | decision | done | 07-decisions |
| 2026-07-21-openephys-acquisition-board-scale-up-option | reference | done | 07-decisions |
| 2026-07-24-daq-32-mouse-final-comparison | decision | active | 07-decisions |
| 2026-10-16-pinnacle-wireless-16-mice-evaluation | decision | active | 06-references |
| RIG-EXPANSION-HUB | hub | active | 07-decisions |
| daq-ecosystem-comparison-xdaq-vs-openephys | decision | superseded → [[2026-07-24-daq-32-mouse-final-comparison]] | 06-references |
| daq-research-findings-primary-sources | reference | active | 06-references |
| intan-rhd-spi-wiring-and-headstage-limits | reference | active | 06-references |
| kontex-xdaq-hardware-reference | reference | active | 01-infrastructure/hardware-sync |
| xdaq-32-mouse-wiring-and-channel-law | reference | active | 06-references |

## 10-projects/unipolar-lfp  (1)

| note | type | status | from |
|---|---|---|---|
| 2026-08-05-unipolar-lfp-mouse-reference | experiment | done | 05-experiments/completed |

## 20-areas/allego  (15)

| note | type | status | from |
|---|---|---|---|
| 2026-04-02-allegoserver-thermal-spikes | incident | done | 03-troubleshooting/incidents |
| 2026-09-11-allego-control-bench-test | experiment | done | 05-experiments/completed |
| CANONICAL-allego-channel-selection | reference | active | 02-procedures |
| allego-electrode-setup-sleep64 | procedure | active | 02-procedures |
| allego-iir-filter-design-errors | incident | active | 03-troubleshooting/symptoms |
| allego-monitor-guide | procedure | active | 02-procedures |
| allego-presets-workspace | reference | active | 02-procedures |
| allego-sampling-rate | reference | active | 02-procedures |
| allego-settings-save-restore | procedure | active | 02-procedures |
| eight-mouse-acquisition-setup | procedure | active | 02-procedures |
| live-signal-quality-terms | reference | active | 06-references |
| openephys-gui-setup-xdaq-sleep-eeg | procedure | active | 02-procedures |
| radiens-api-reference | reference | active | 01-infrastructure/hardware-sync |
| radiens-software-reference | reference | active | 06-references |
| signal-mapping-guide | reference | active | 02-procedures |

## 20-areas/computing  (9)

| note | type | status | from |
|---|---|---|---|
| 2026-02-09-tailscale-restart-lockout | incident | done | 03-troubleshooting/incidents |
| 2026-04-29-syncthing-deletion-and-recovery | incident | done | 03-troubleshooting/incidents |
| 2026-08-19-laptop-workflow-alignment-task | procedure | superseded | 01-infrastructure |
| 2026-08-19-office-pc-nas-firewall-task | procedure | superseded → [[2026-08-19-nas-backup-wrong-address]] | 01-infrastructure |
| monitoring-diagnostics | reference | active | 06-references |
| monitoring-setup | procedure | active | 02-procedures/installation |
| multi-machine-work-setup | reference | superseded | 01-infrastructure |
| nvr-alerts-config | reference | active | 01-infrastructure/netdata |
| production-values | reference | active | 00-config |

## 20-areas/data-storage  (6)

| note | type | status | from |
|---|---|---|---|
| 2026-08-19-nas-backup-wrong-address | incident | done | 03-troubleshooting/incidents |
| backup-architecture | reference | active | 02-procedures |
| nas-backup | procedure | active | 02-procedures/installation |
| radix-s3-archive | procedure | active | 02-procedures/installation |
| raw-recording-archive-to-nas | procedure | active | 01-infrastructure |
| skim-nas-smb-and-upload | procedure | active | 02-procedures/installation |

## 20-areas/eeg-analysis  (28)

| note | type | status | from |
|---|---|---|---|
| 01-environment-setup | procedure | active | 02-procedures/eeg-data-analysis |
| 02-file-formats-reference | reference | active | 02-procedures/eeg-data-analysis |
| 03-scripts-and-usage | reference | superseded → [[eeg-pipeline-manual]] | 02-procedures/eeg-data-analysis |
| 04-processing-guidelines | reference | active | 02-procedures/eeg-data-analysis |
| 2026-08-07-council-review-of-the-analysis-pipeline | decision | done | 07-decisions |
| 2026-08-07-rig-specification-and-analysis-method | decision | active | 07-decisions |
| 2026-08-09-HLB-cohort-report-generated | reference | done | 05-experiments/completed |
| 2026-08-11-analysis-stack-audit-measurements | experiment | done | 05-experiments/completed |
| 2026-08-11-analysis-stack-consolidation | decision | done | 07-decisions |
| CANONICAL-recording-windows-and-protocol | reference | active | 02-procedures |
| _eeg-analysis-hub | hub | active | 02-procedures/eeg-data-analysis |
| analysis-methods-and-justification | reference | active | 02-procedures/eeg-data-analysis |
| animal-card-and-verdict-ladder | reference | active | 02-procedures/eeg-data-analysis |
| contaminated-floor-rejects-good-eeg | incident | done | 03-troubleshooting/symptoms |
| eeg-analysis-glossary | reference | active | 06-references |
| eeg-analysis-problems | incident | active | 03-troubleshooting/symptoms |
| eeg-artefact-and-railing-rejection-policy | procedure | active | 02-procedures |
| eeg-emg-data-guide | reference | active | 02-procedures |
| eeg-pipeline-manual | procedure | active | 02-procedures/eeg-data-analysis/pipeline |
| emg-without-muscle-band-activity-passes-rung-2 | incident | active | 03-troubleshooting/symptoms |
| figure-and-analysis-audit-2026-08-08 | experiment | done | 03-troubleshooting/symptoms |
| is-our-qc-approach-sound | reference | active | 06-references |
| per-mouse-csv-format | reference | active | 02-procedures |
| per-mouse-export | procedure | active | 02-procedures/eeg-data-analysis |
| positive-control-known-signal-injection | experiment | planned | 02-procedures |
| scripts-archive-pre-sleep64-readme | reference | superseded → [[eeg-pipeline-manual]] | 02-procedures/eeg-data-analysis/scripts/_archive_pre_sleep64 |
| scripts-contact-state-2026-07-31-readme | reference | superseded → [[eeg-pipeline-manual]] | 02-procedures/eeg-data-analysis/scripts/contact-state-2026-07-31 |
| scripts-rescore-v2-2026-08-03-readme | reference | superseded → [[eeg-pipeline-manual]] | 02-procedures/eeg-data-analysis/scripts/rescore-v2-2026-08-03 |

## 20-areas/eeg-rig  (19)

| note | type | status | from |
|---|---|---|---|
| 60hz-mains-hum-discovery | reference | active | 02-procedures |
| dmm-eeg-path-continuity-test | experiment | done | 02-procedures |
| earthing-60hz-hum-fix | reference | superseded → [[headstage-shielding-faraday-foil]] | 02-procedures |
| electrode-connection-state-test | procedure | active | 02-procedures |
| floating-cm-vs-contact-reconciliation | reference | active | 02-procedures |
| grounding-reference-noise-concepts | reference | active | 02-procedures |
| headstage-shielding-faraday-foil | reference | active | 02-procedures |
| impedance-sweep-register | reference | active | 06-references |
| intan-headstage-troubleshooting | incident | active | 02-procedures |
| intan-rhd2216-reference | reference | active | 06-references |
| multimeter-guide | procedure | active | 02-procedures |
| per-animal-failure-signatures | incident | active | 03-troubleshooting/symptoms |
| pre-flight-connection-screen | procedure | active | 02-procedures |
| rig-assembly-guide | procedure | active | 02-procedures |
| signal-quality-and-grounding | procedure | active | 02-procedures |
| sleep-recording-operator-manual | hub | active | 02-procedures |
| tsukuba-sleep-recording-method | reference | active | 06-references |
| weak-chip-ground-vs-open-electrode | incident | active | 03-troubleshooting/symptoms |
| xdaq-core-gen1-ubuntu-driver | reference | active | 01-infrastructure/hardware-sync |

## 20-areas/nanotag  (2)

| note | type | status | from |
|---|---|---|---|
| nanotag-kissei-device-and-literature | reference | active | 06-references |
| nanotag-recording-and-analysis | procedure | active | 02-procedures |

## 20-areas/recording-console  (9)

| note | type | status | from |
|---|---|---|---|
| CANONICAL-recording-naming-and-inventory | reference | active | 02-procedures |
| eeg-recording-console | procedure | active | 02-procedures |
| multi-user-independent-recording-schedules | experiment | planned | 02-procedures |
| pipeline-architecture | reference | active | 01-infrastructure/eeg-recorder |
| recording-console-retry-was-a-dead-end | incident | done | 03-troubleshooting/symptoms |
| rig-layout-and-recording-settings | procedure | active | 02-procedures |
| scheduled-recording-and-watchdogs | procedure | active | 02-procedures |
| starting-the-rig-after-a-restart | procedure | active | 02-procedures |
| xdat-channel-stripping | procedure | active | 02-procedures/installation |

## 20-areas/sleep-scoring  (6)

| note | type | status | from |
|---|---|---|---|
| 2026-10-06-sleepstager-csv-ingestion | decision | done | 07-decisions |
| blind-scoring-and-kappa | procedure | planned | 02-procedures |
| sleep-scoring-handbook | reference | active | 06-references |
| sleepstager-changes-and-backlog | reference | active | 01-infrastructure/sleepstager |
| sleepstager-user-guide | procedure | active | 02-procedures |
| sleepyscore-japan-scoring-tool-algorithm | reference | active | 06-references |

## 20-areas/video-nvr  (37)

| note | type | status | from |
|---|---|---|---|
| 2026-02-05-optimization-resource-reduction | experiment | done | 05-experiments/completed |
| 2026-02-09-go2rtc-setup-troubleshooting | incident | done | 03-troubleshooting/incidents |
| 2026-02-10-post-boot-stream-crash | incident | active | 03-troubleshooting/incidents |
| 2026-02-11-mpegts-container-test | experiment | done | 05-experiments/completed |
| 2026-02-11-persistent-journal-fix | incident | done | 03-troubleshooting/incidents |
| 2026-02-11-vscode-remote-cpu-exhaustion | incident | done | 03-troubleshooting/incidents |
| 2026-02-19-pmic-fault-poe-death | incident | done | 03-troubleshooting/incidents |
| 2026-02-23-session-daemon-radiens-auth-cors | incident | done | 03-troubleshooting/incidents |
| 2026-02-24-pi-unreachable-no-route | incident | done | 03-troubleshooting/incidents |
| 2026-03-24-webkit-internal-error-tauri | incident | done | 03-troubleshooting/incidents |
| 2026-04-08-frigate-export-stuck-and-missing-on-edges | incident | active | 03-troubleshooting/incidents |
| 2026-05-01-llm-council-review | decision | done | 07-decisions |
| 2026-05-20-docker-upgrade-and-startup-guard-regression | incident | done | 03-troubleshooting/incidents |
| 2026-05-stabilization-sprint-week-1-plan | decision | done | 07-decisions |
| 2026-07-16-camera-node-scale-up | decision | planned | 07-decisions |
| 2026-07-27-video-eeg-sync-recording-architecture | decision | active | 07-decisions |
| boot-config-ssh-lockout | incident | done | 03-troubleshooting/incidents |
| bus-factor-runbook | procedure | active | 02-procedures |
| camera-roi-framing | procedure | active | 02-procedures |
| command-cheatsheet | reference | active | 06-references |
| docker-memory-crash | incident | active | 03-troubleshooting/symptoms |
| emergency-runbook | procedure | active | 03-troubleshooting |
| export-timeout-fix | procedure | done | 02-procedures/installation |
| frigate-high-cpu | incident | active | 03-troubleshooting/symptoms |
| frigate-setup | procedure | active | 02-procedures/installation |
| h265-encoding-failure | experiment | done | 05-experiments/completed |
| new-pi-setup | procedure | active | 02-procedures/installation |
| new-researcher-onboarding | procedure | active | 02-procedures |
| no-frames-received | incident | active | 03-troubleshooting/symptoms |
| nvr-system-overview | reference | active | 01-infrastructure |
| recording-health-watchdog | procedure | done | 02-procedures/installation |
| session-recording-workflow | procedure | active | 02-procedures |
| storage-management-implementation | procedure | done | 02-procedures/installation |
| storage-troubleshooting | reference | active | 06-references |
| system-freeze-ssh-hang | incident | active | 03-troubleshooting/symptoms |
| video-parameters | reference | active | 06-references |
| watchdog-slack-bridge | procedure | active | 02-procedures/installation |

## 20-areas/video-nvr/frigate  (2)

| note | type | status | from |
|---|---|---|---|
| config-yml | reference | active | 01-infrastructure/frigate |
| docker-compose | reference | active | 01-infrastructure/frigate |

## 20-areas/video-nvr/hardware-sync  (9)

| note | type | status | from |
|---|---|---|---|
| gpio-sync-service | reference | planned | 01-infrastructure/hardware-sync |
| hardware-sync-bench-test-do03 | procedure | planned | 02-procedures |
| hardware-sync-setup | procedure | planned | 02-procedures |
| kontex-developer-portal-notes | reference | superseded → [[xdaq-core-gen1-ubuntu-driver]] | 01-infrastructure/hardware-sync |
| literature-review | reference | done | 01-infrastructure/hardware-sync |
| overview | reference | planned | 01-infrastructure/hardware-sync |
| references-and-justification | reference | active | 01-infrastructure/hardware-sync |
| wiring-guide | procedure | planned | 01-infrastructure/hardware-sync |
| xdaq-core2-manual-reference | reference | active | 01-infrastructure/hardware-sync |

## 20-areas/video-nvr/raspberry-pi  (4)

| note | type | status | from |
|---|---|---|---|
| golden-boot-config | reference | active | 01-infrastructure/raspberry-pi |
| golden-go2rtc-config | reference | active | 01-infrastructure/raspberry-pi |
| golden-systemd-service | reference | active | 01-infrastructure/raspberry-pi |
| watchdog-monitoring | reference | active | 01-infrastructure/raspberry-pi |

## 20-areas/video-nvr/session-daemon  (5)

| note | type | status | from |
|---|---|---|---|
| architecture | reference | active | 01-infrastructure/session-daemon |
| frontend-reference | reference | active | 01-infrastructure/session-daemon |
| reconciler | reference | active | 01-infrastructure/session-daemon |
| session-journal | reference | active | 01-infrastructure/session-daemon |
| session-service | reference | active | 01-infrastructure/session-daemon |

## 30-resources/datasheets/sensor-maps  (1)

| note | type | status | from |
|---|---|---|---|
| csv2sensor-README | reference | active | 06-references/neuronexus/sensor-maps |

## 30-resources/literature  (1)

| note | type | status | from |
|---|---|---|---|
| electrode-failure-and-impedance-literature | reference | active | 06-references |

## 30-resources/meetings  (10)

| note | type | status | from |
|---|---|---|---|
| 2026-08-03-data-quality-report-for-professor | meeting | done | 05-experiments/completed |
| 2026-08-06-rig-status-for-professor | meeting | done | 05-experiments/completed |
| 2026-08-08-full-update-for-professor | meeting | done | 05-experiments/completed |
| 2026-08-08-professor-update-short | meeting | done | 05-experiments/completed |
| lab-meeting-2026-04-10-final-script | meeting | done | 06-references |
| lab-meeting-2026-04-10-presentation-brief | meeting | done | 06-references |
| lab-meeting-2026-04-10-presentation-plan | meeting | done | 06-references |
| lab-meeting-2026-04-10-presentation-revisions | meeting | done | 06-references |
| lab-meeting-2026-04-10-speaker-notes | meeting | done | 06-references |
| progress-meeting-2026-03-12 | meeting | done | 06-references |

## 30-resources/vendors  (6)

| note | type | status | from |
|---|---|---|---|
| 2026-07-21-kontex-kc-call-prep | reference | done | 01-infrastructure/vendor-correspondence |
| 2026-07-29-kontex-kc-call-prep-rig-finalization | reference | done | 01-infrastructure/vendor-correspondence |
| hdmi-spi-adapter-top-socket-vendor-inquiry | reference | done | 01-infrastructure/vendor-correspondence |
| kontex-call-confirmation-email-2026-07-29 | reference | done | 01-infrastructure/vendor-correspondence |
| neuronexus-inquiry-email | reference | done | 01-infrastructure/vendor-correspondence |
| openephys-inquiry-email | reference | done | 01-infrastructure/vendor-correspondence |

## 90-archive  (8)

| note | type | status | from |
|---|---|---|---|
| 2026-07-02-vault-reorganization-plan | decision | superseded | 99-archive |
| 2026-07-18-eeg-emg-analysis-checkpoint | decision | done | 99-archive |
| AI-INSTRUCTIONS | reference | superseded | (root) |
| SYSTEM-OVERVIEW | reference | superseded | (root) |
| _INDEX | reference | superseded | (root) |
| mpegts-test-handoff | experiment | done | 99-archive |
| ui-handoff-project-idx | procedure | done | 99-archive |
| vault-setup-log-2026-02 | reference | done | 99-archive |

## 90-archive/2026-05-rehaul  (4)

| note | type | status | from |
|---|---|---|---|
| frigate-docker-compose-2026-05-22 | reference | superseded → [[docker-compose]] | 99-archive/2026-05-rehaul |
| frigate-setup-mosquitto-2026-05-22 | reference | superseded → [[frigate-setup]] | 99-archive/2026-05-rehaul |
| frontend-reference-api-pre-journal-2026-05-23 | reference | superseded → [[frontend-reference]] | 99-archive/2026-05-rehaul |
| session-recording-workflow-unauth-mosquitto-2026-05-22 | reference | superseded → [[session-recording-workflow]] | 99-archive/2026-05-rehaul |

## 90-archive/2026-08-09-pipeline-moved-to-repo  (1)

| note | type | status | from |
|---|---|---|---|
| pipeline-moved-to-repo-readme | reference | superseded | 99-archive/2026-08-09-pipeline-moved-to-repo |

## _templates  (6)

| note | type | status | from |
|---|---|---|---|
| Daily Journal | - | - | _templates |
| Experiment | - | - | _templates |
| Incident Report | - | - | _templates |
| Meeting Notes | - | - | _templates |
| Procedure | - | - | _templates |
| Symptom | - | - | _templates |

