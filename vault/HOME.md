---
tags: [home]
---

# SKIM sleep lab

Mouse sleep EEG/EMG, the HLB SOD1 study, nanotag activity loggers, the video NVR, and the
machines behind them. Every project and area has a **hub**. Its *Current state* section is
where to look for what is true now. Rules for agents and for filing: [[CLAUDE]].

## Projects (have an end)

| Hub | Scope |
|---|---|
| [[_hlb-sod1-hub\|HLB SOD1]] | oral SOD1 vs water: the four EEG batches (W-SL, W-SD, S-SL, S-SD) and the nanotag studies (HLBNSL, NS-SD / NW-SD) |
| [[_rig-expansion-hub\|Rig expansion]] | from 8 to 16 / 32 mice: XDAQ, Open Ephys, Pinnacle wireless, headmount |
| [[_rig-bringup-hub\|Rig bring-up]] | Jun to Aug 2026: getting the first valid EEG/EMG recordings |
| [[_noise-hunt-hub\|Noise hunt]] | Sep to Oct 2026: the 60 Hz investigation and the grounding fix |
| [[_unipolar-lfp-hub\|Unipolar LFP]] | ahyeon's unipolar LFP mice |

## Areas (kept running)

| Hub | Scope |
|---|---|
| [[_eeg-rig-hub\|EEG rig]] | electrodes, headstages, tethers, XDAQ, grounding, impedance, pre-flight screen |
| [[_allego-hub\|Allego]] | Allego / Radiens: channels, Monitor, presets, sensor maps, known gotchas |
| [[_recording-console-hub\|Recording console]] | `http://127.0.0.1:8600` on e10: runs, scheduling, stripping, upload, naming |
| [[_eeg-analysis-hub\|EEG analysis]] | QC verdict ladder, pipeline, per-mouse CSV, analysis windows, methods |
| [[_sleep-scoring-hub\|Sleep scoring]] | manual scoring, SleepStager, kappa |
| [[_nanotag-hub\|Nanotag]] | Kissei nanotag device, read-out and analysis method |
| [[_data-storage-hub\|Data storage]] | bilab NAS, SKIM NAS, S3: where every recording lives |
| [[_computing-hub\|Computing]] | e10ubuntu, the laptops, Tailscale, monitoring and alerts, production values |
| [[_video-nvr-hub\|Video NVR]] | Pi cameras, Frigate, session daemon, video-EEG sync |

Resources (browse `30-resources/`): literature, vendors, meetings and professor reports,
datasheets. Pre-2026-10-22 navigation: `90-archive/`.

## Common questions

| Question | Answer lives in |
|---|---|
| Did SOD1 change sleep? (EEG and nanotag, reported separately) | [[_hlb-sod1-hub#Current state\|HLB SOD1 hub, Current state]] |
| Which mice are scoreable at both timepoints? | [[2026-09-30-scoreable-mice-on-the-24h-windows]] |
| Which hours of a recording are analysed? | [[CANONICAL-recording-windows-and-protocol#⭐ The analysis windows in use, set 2026-09-29\|analysis windows]] |
| How do I record a run? | [[eeg-recording-console]] |
| The rig rebooted or Allego looks dead | [[starting-the-rig-after-a-restart]], then [[_allego-hub#Rules that must not be broken\|Allego rules]] |
| Which Allego channels do I select? | [[CANONICAL-allego-channel-selection]] |
| Is this animal's signal usable? | [[animal-card-and-verdict-ladder]] |
| Where is the data, and what is backed up? | [[_data-storage-hub]], [[per-mouse-csv-format]] |
| Hosts, IPs, ports, paths | [[production-values]] |

## Status of every hub

![[hubs.base]]

## Adding something

- **New note:** create it anywhere (Ctrl+N). It lands in `00-inbox/`, asks what it is and
  where it belongs, fills in the frontmatter and moves itself. Cancel and it waits in the inbox.
- **Today's journal:** Ctrl+D. Write what happened; link the notes that hold the detail.
- **Not sure where it goes:** the table in [[CLAUDE#Where does a new thing go?]].
- **Health check:** `./skim lint` in a terminal, or [[vault-health.base|vault health]].

## Open decisions

[[decisions-needed-2026-10-22|Decisions needed]]: questions only Andrea or the professor can
settle (the 800 µV gate, `--disable-gpu`, Pinnacle vs XDAQ, the Slack webhook, …).

## Daily

- [[journal.base|Journal index]] — every day, newest first, one line each
- [[TASKS]] · [[TASKS-WEEK]]
- [[production-values]] — hosts, IPs, ports, paths
