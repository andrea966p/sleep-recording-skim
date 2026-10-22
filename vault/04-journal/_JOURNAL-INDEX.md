# 📓 Journal Index — chronological master navigator

> [!abstract] How the journal works
> Every daily journal in date order, **newest first**.
>
> **The daily journal is the master navigator.** It records what happened that day and links out to the notes where the detail lives: decisions in `07-decisions/`, procedures in `02-procedures/`, references in `06-references/`, incidents in `03-troubleshooting/`.
>
> Read a day here, then follow its links down. **Detail belongs in the linked notes, not in the journal.**

**73 entries.** Dates with no entry had no vault activity, mostly weekends.


## September 2026

| Date | Day | What happened |
|---|---|---|
| [[2026-10-21]] | Wed | 🧪 **NS-SD sampling moved Sun 11-08 → Thu 11-05** (no weekend SD/tests): SD Mon 11-02 → Thu 11-05, SOD 12 d; sheet requests CHG-005 → 009 sent. [[_HLB-SOD1-project-hub]] |
| [[2026-10-20]] | Tue | 🖥️ **Pinnacle acquisition PC = custom build:** ASUS PRIME B550-PLUS (DDR4, no WiFi, 1 x16 + 1 x16@x4 + 3 x1 = GPU + 4 x1 USB cards, 4 dongles per card = 16). 12 units by end of 2026, 4 more in January. Unstable ⇒ second identical PC, 8 + 8. [[2026-10-16-pinnacle-wireless-16-mice-evaluation]] |
| [[2026-10-19]] | Mon | 🛒 **Pinnacle wireless settled with the professor:** custom 4-ch **8474-HR-SE4-C** (2 EEG + 2 independent), EEG HP 0.5/0.1 Hz, our own headmount PCB ≤ 6 mm AP, 16 mice on one PC. Verified pin map = Pinnacle **4-ch standard** (8 pins, no spare; "2nd GND" retracted). To-scale headmount concept drawing. [[2026-10-16-pinnacle-wireless-16-mice-evaluation]] · 🧪 **Nanotag NS-SD re-planned** (single-housed 10-19, tags from 10-22, SOD 10-24, SD 11-05 → 11-08, sampling 11-08) + sheet change-log tab, round 1 approved [[sod1-sheet-change-log-workflow]] |
| [[2026-10-16]] | Fri | 🧪 **NS-SD / NW-SD nanotag schedule brought in from the workstation** (decided there 10-12): SOD1 10-22 → sampling **11-02** (11 d), 4-day SD 10-30 → 11-02, one live tag read 10-27. 🔴 12 s activity-only memory = **9 days, not 20** (English-manual misprint); hub, procedure and device reference corrected. [[_HLB-SOD1-project-hub]] |
| [[2026-10-09]] | Fri | ⚡⭐⭐⭐ **The grounding fix holds over 24 h** (run `ee0263bffeaa`, 29.5 h): floors < 240 µV and A2 EMG 60 Hz < 2.3 µV in every hour; **A2 scores WITHOUT the notch** (r@1min 0.615, before REJECT), B1 0.587; wake dark 2-3x light; building events 1 vs 6; light-switch spikes unchanged. Lab member's visit 10-08 16:41-17:37 marked. Strip finished with `--gpio-never-connected` (din_1 glitches, nothing wired). [[2026-09-30-xdaq-noise-series]] |
| [[2026-10-08]] | Thu | 🧪 **SleepStager CSV vs .mat re-run for Andrea:** HLBSSL33 R, 0.000000 µV, 0 µs, cuts and features identical, **21,600 / 21,600 stages identical**; only the coverage differs (.mat 36.7 h). CSV reading settled; the 11 GB comparison copy deleted. 🧑‍🔬 **Scoring session 2: HLBSSL33 R 840 → 8441**, 235 epochs re-staged (NR→W 122 quiet wake, NR→R 94 late REM onsets); Andrea's own conventions C11 (quiet wake inside W) and C12 (one-sided arousals in NR stay NR) added to the handbook and the rules card. 🧰 PR prep: `n` notch now off → 50 → 60 Hz (display only); tone row stays local; smoke tests pass on a Japan .3eg; **[PR #1](https://github.com/somnocode/SleepStager/pull/1) opened** for the professor. 🐛 Resume brought back cleared rule marks (in `main`, not from CSV): fixed, [PR #2](https://github.com/somnocode/SleepStager/pull/2). |
| [[2026-10-07]] | Wed | ⚡⭐⭐ **The grounding fix collapsed the mains:** isolated-earth socket + XDAQ bonded to the earthed rack. Chip floors 12-60x lower, A2 EMG 60 Hz 26-33 → 1 µV, B1 → 0.5 µV; A1/B2 open EMGs no longer rail. Andrea: a very big success. 🔴 The 800 µV ground gate now calls every chip UNJUDGEABLE. 29.5 h confirmation run `ee0263bffeaa` started 15:28. [[2026-09-30-xdaq-noise-series]] · 🧪⭐⭐ **SleepStager opens the rig's per-mouse CSV** (identical to the xdat route on HLBSSL33 R: 21,600/21,600 stages) and the **first manual scoring session** (HLBSSL33 R, epochs 1–840, 9 cases with screenshots for the professor). 🔴 SleepStager notches 50 Hz, our mains is 60 Hz (18 % of NREM EMG power). New: [[sleep-scoring-handbook]] · [[sleepstager-user-guide]] · [[sleepstager-changes-and-backlog]] |
| [[2026-10-06]] | Tue | ⚡ **Building electrician inspects the recording room:** the rig socket becomes an isolated-earth socket, the headstage foils go onto one earth busbar. ⭐ **Verdict on the noise hunt: mostly a ghost** once per-mouse faults are set aside; the EMG mains is the only real noise and a validated notch removes it (not adopted, Andrea's decision). [[2026-10-06-noise-hunt-verdict]] · 🧪 🧪 **Did SOD1 change sleep? The four EEG batches as a 2x2.** No detectable effect without deprivation (61.1 vs 60.6 % of 24 h, p = 0.96; notched p = 0.24). After deprivation, not answerable: S-SD has no scoreable recovery. EMG notch sensitivity run on e10 (42/42 reproduced) shows the official W-SL baseline is mains-inflated. [[2026-10-06-SOD1-sleep-EEG-2x2-quick-compute]] · ⭐ **S-SD EMG rescue:** EMG measured between the 60 Hz harmonics from the raw 1000 Hz file (κ 0.95 against the notched staging) makes **HLBSSD15 scoreable at both timepoints**. Rebound +6.6 vs water +16.1, n = 1 per arm. [[2026-10-06-S-SD-EMG-rescue-between-harmonics]] · 🧰 **SleepStager read and a council held on how it should read the rig's CSV** (verdict: converter; superseded 10-07 by a native reader) [[2026-10-06-sleepstager-csv-ingestion]] |
| [[2026-10-05]] | Mon | 🧹 Vault checked and tidied (links, markers, index grouping, current-state TL;DR), then the whole noise-series work (09-30 → 10-03) committed and pushed. 🧪 Nanotag SOD1 study (HLBNSL) brought into the repo, vault and NAS; Run 1 + Run 2 merged and re-analysed. |
| [[2026-10-02]] | Fri | 🌙 **First 4-mouse overnight of the noise series** (21:00→09:02). No non-mains injection on the clean mice; B1's low floor is steady. **QC ground gate mis-calibrated for the new geometry; all-chip rule degenerates** [[2026-10-02-noise-series-method-audit]]. Pre-flight OPEN-reason bug fixed; console fixes prepared in a worktree. Morning: 12.03 h, 0 dropped, lights-ON caught; **official QC all UNJUDGEABLE**; ⭐ **mains in the EMG corrupts staging** (C3); light-phase run started; raw on NAS for the workstation (AWS deferred). Midday: **10 figures embedded**; ⭐ [[2026-10-02-noise-troubleshooting-plan]] (T1-T11); `qc/record_block.py`. Afternoon rig session (probe on the foil → A2 floor x2.1, EMG x1.16; hands don't reach the mice' EEG/EMG): [[2026-10-02-light-phase-run-rig-session]]. · 🌃 **Night: full 24 h analysis on e10** — B1 light phase officially SCOREABLE, the EMG notch validated across the archive (shuffle 0/100, dark>light 47/49), two code reviews fixed the system-wide rule (both ports) and several numbers, NAS analysis folder [[2026-10-02-noise-series-4mice-24h-analysis]] |
| [[2026-10-01]] | Wed–Thu | ⭐⭐ **XDAQ noise series, no mice.** Gen-1 Core HAS a chassis GND (vault corrected). Light switch spikes every chip at once, but only ~2.3 real all-chip events/day in 52 h of mice. **USB isolator: no help, broadband 2x up (A/B/A) ⇒ direct cable.** Board + slip ring = antenna on open inputs, not solder. Splitter at chance. [[2026-09-30-xdaq-noise-series]] |
| [[2026-09-29]] | Tue–Wed | ⭐⭐⭐ **The SKIM NAS is organised BY MOUSE, as CSV, in `02_Data_Sleep/<user>/<batch>/<Baseline|Recovery>/`.** Console pipeline is now QC → STRIP → EXPORT → UPLOAD; batch required; B/R codes. **All 8 canonical recordings rebuilt, cut to 24 h windows (SD recovery 13:00→09:00, 20 h): 64 folders, 291 GB, audit clean.** S-SD B1 unpaired (13 baseline / 17 recovery). Scoreable at both timepoints on the windows: **HLBWSD08, HLBWSL24, HLBSSL33** (+ HLBSSL31, HLBSSL35 on stage 3); **S-SD none.** |
| [[2026-09-19]] | Sat | ⭐⭐ **The ThinkPad joined the push/pull workflow, set up remotely from e10.** Its only real gap was a **missing git identity** — `check.sh` and `skim status` both pass without one, and `./skim push` would have failed. 51 commits pulled. ✅ Syncthing already gone there ⇒ **retired on every machine**. 🔑 **A Tailscale SSH rule's `dst` can only be `autogroup:self` or a TAG, never another user's login** (`400 users in dst are only allowed from the same user`) ⇒ crossing owners REQUIRES tagging the destination, which moves its ownership to the tag. 🔴 **Enabling Tailscale SSH makes tailscaled INTERCEPT port 22 for tailnet peers and bypass the real sshd** — that is what broke `ssh e10` from the laptop; `--ssh=false` restored it. ⚠️ The CLI cannot edit tailnet policy; only the console or an API token. |
| [[2026-09-16]] | Wed | ✅ **Syncthing uninstalled from `e10ubuntu` AND the office PC** (`Andrea-KAIST-PC-ubuntu`), packages and all — ⚠️ (the ThinkPad claim here was superseded on 09-19: it is gone there too). Both device identities parked, not deleted. ⚠️ The office PC's live config was `~/.local/state/syncthing`, and `apt purge` does NOT stop a running daemon: `which` went quiet while `pgrep` still returned two PIDs. 🔴 **`sudo apt autoremove` took 52 packages / 984 MB there** including the NVIDIA 570 stack, then left the WORKING 580 driver marked auto-removable — pinned with `apt-mark manual`. ⭐ **A fourth machine**, the SKIM office workstation (`/home/skim`): `bootstrap.sh` KEEPS an existing `settings.json`, so it reported success while the machine had **no SessionStart hooks and no `skim status`**. 🔴 Uncommitted work still stranded in the office PC's `neurosurveillance`. |
| [[2026-09-14]] | Mon | per-port rig layouts; a false line of mine corrected (a unipolar headstage HAS run here); the enumeration check that refuses a wrong declaration; the settings panel |
| [[2026-09-13]] | Sun | ⭐⭐ **The 24 h S-SL recording reached the NAS** (93.18% smaller, 5 files verified, **5 of 8 animals pass rung 2**) after three fixes: a **new mouse id was blocking the pipeline** (QC needs only the role list, which the console already knew), **Gate B refused a 90 GB strip over a 1 ms blip** on an unconnected input, and **dates came from UTC on a KST rig**. ✅ **Scheduler bench-tested on the real rig** — start 3 s late, stop 0.5 s late — which found that a SCHEDULED stop stranded the run because the handoff to post-processing existed only on the manual button. 🔑 **All six defects so far were found by running it, not by testing it.** |
| [[2026-09-11]] | Fri | ⭐⭐ **The SKIM Lab NAS is mounted (SMB, DIRECT 1 ms path, 94 MB/s) and the recording console is live** — set up a run, start or schedule, and on stop it strips to the wired channels and uploads verified to your own folder. 🔴 **Allego's `.xdat` file size reports 0 for a FULL 30 s after a healthy start** — an 11 s growth check called a working recording dead and left the rig recording. ✅ `set_recording('off')` works. 🔴 **Read-back over CIFS verifies your own page cache** (1538 vs 90 MB/s) without `posix_fadvise`. 🔴 RETRACTED: radiens 4.0.0 has **no per-port recording** |
| [[2026-09-01]] | Tue | ⭐⭐ Pre-flight screen run where it could still change something; ✅ **a bench re-seat fixed ALL EIGHT chip grounds**, D2 back on both roles; 🔑 the tethers are failing two different ways and only one is torsion; go/no-go AMBER; ⚠️ a **223 GB file on disk that is not ours** |

## August 2026

| Date | Day | What happened |
|---|---|---|
| [[2026-08-18]] | Tue | ⭐⭐ **Eight new W-SD mice. After an electrode re seat, ONE HOUR: five clear the 15 min bar on EEG (A1 + C1 unbroken for the whole hour), but on the STRICT combined EEG+EMG rung 2 only A2 passes**; ✅ **C2 was NOT animal side, the re seat revived it**; 🔴 **B1 ground still wrong and STABLE at 453 µV ⇒ pin position, not a loose plug**; ⚠️ **the POOLED floor in `criteria.py` condemns good mice, per chip floor fixes it**; **Radiens reference page rewritten + the wrong "subtract EEG− offline" line killed** |
| [[2026-08-16]] | Sun | Work moved to the ThinkPad; **vault deletion root-caused (no Syncthing versioning + `.git` synced)**, both fixed and tested; duplicate laptop vault untangled; **shared Claude config now self-syncs via a `SessionEnd` hook**; **NAS backup + office PC DEFERRED on purpose** |
| [[2026-08-02]] | Sun | All 8 mice rescored: **D2 withdrawn, replication is n=2**; **B1 = 11.8 h of good EEG blocked by a dead EMG**; 5/8 mice have zero EEG |
| [[2026-08-01]] | Sat | ⭐⭐ **CHANNEL MAP WAS WRONG — EMG always worked; FIRST REAL SLEEP ARCHITECTURE (C1: W 66.8 / NREM 29.3 / REM 3.9 %)**; 21 scoreable mouse-hours, not zero |
| [[2026-08-01]] | Sat | 🔴⭐ (earlier, wrong-map) 27.9 h run analysed: grounds perfect 28 h; **78 % of leg-time OPEN**; two failure modes (one-way vs chattering); **C1 clean but NO sleep structure**; yield 3.9 % |

## July 2026

| Date | Day | What happened |
|---|---|---|
| [[2026-07-31]] | Fri | 🔴⭐ Earth did nothing; splitter excluded; **legs are OPEN not bad implants**, state flips on its own; **first clean unclipped EEG (C1)**; DO NOT make new mice |
| [[2026-07-29]] | Wed | Kontex finalization call; call sheet rebuilt; vault reorganised |
| [[2026-07-28]] | Tue | Overnight run checked, LED question settled, daemon stop-path fixed |
| [[2026-07-27]] | Mon | Video-EEG sync architecture finalized; the recording toggle root-caused |
| [[2026-07-24]] | Fri | DAQ comparison goes 3-way; Intan added; per-port record control overturned |
| [[2026-07-23]] | Thu | Open Ephys reply on 16→32-mouse scale-up |
| [[2026-07-21]] | Tue | Kontex call (KC Kong) + scale-up decisions |
| [[2026-07-18]] | Sat | I was reading EMG wrong, and the good news is EMG is not our problem |
| [[2026-07-16]] | Thu | I have to take back yesterday's discovery, and the real problem is the electrodes |
| [[2026-07-15]] | Wed | RustDesk display fix validated; the council; impedance test confirms H2 |
| [[2026-07-14]] | Tue | Post-processing QC of the 72h run and yesterday's 8-headstage run |
| [[2026-07-13]] | Mon | RustDesk/HDMI-switch crash root-caused; 72h 4-mouse recording audit |
| [[2026-07-05]] | Sun | 🔴 THE BIG ONE: Korea mains is 60 Hz, not 50 Hz. Weeks of "bad electrodes" were mostly 60 Hz hum + a wrong notch. |
| [[2026-07-04]] | Sat | First real 8-mouse setup; C3442 2nd-headstage channel offset nailed (+32, not +16/+28); custom sensor dropped for passthrough |
| [[2026-07-03]] | Fri | Overnight 2-mice + 4-cam STRESS TEST = SUCCESS (thermal resolved; 14h data intact); daemon auto-video disabled |
| [[2026-07-02]] | Thu | LLM Council review of the EEG rig + checkpoint; `2mice32` map bug fixed; MEMORY.md trimmed |
| [[2026-07-01]] | Wed | MAJOR CLOSURE: ONE headstage per mouse (not 2 mice/headstage); dual-headstage acquisition validated; "broken headstage" root cause found (HDMI top SPI socket is dead) |

## June 2026

| Date | Day | What happened |
|---|---|---|
| [[2026-06-30]] | Tue | EEG analysis toolkit shipped; first 2-mice plug (contact troubles) |
| [[2026-06-29]] | Mon | Grounding fixed, EEG validated live, first 4.5 h recording |
| [[2026-06-28]] | Sun | Slip-ring rebuild: DEFINITIVE plug map locked |
| [[2026-06-27]] | Sat | Grounding root cause FOUND + fixed; color-swap defect; doc set shipped |
| [[2026-06-26]] | Fri | 8-channel standard; Setup A won't enumerate; Setup B still floating |
| [[2026-06-23]] | Tue | Hardware-sync BOM received + grounding busbar decided |
| [[2026-06-22]] | Mon | Pre-grounding check: both mice floating, decoder + topology locked |
| [[2026-06-21]] | Sun | Grounding evidence pack + hardware video-sync Phase 0a |
| [[2026-06-19]] | Fri | First headstage bring-up RESOLVED (wrong Allego mode) |
| [[2026-06-01]] | Mon | Hardware-sync: KC Kong round-3b correction sent |

## May 2026

| Date | Day | What happened |
|---|---|---|
| [[2026-05-28]] | Thu | 1. Confirm gate |
| [[2026-05-26]] | Tue |  |
| [[2026-05-25]] | Mon |  |
| [[2026-05-24]] | Sun | 0 |
| [[2026-05-23]] | Sat |  |
| [[2026-05-22]] | Fri | backend/frigate_controller.py — __init__ signature |
| [[2026-05-21]] | Thu |  |
| [[2026-05-20]] | Wed |  |
| [[2026-05-18]] | Mon |  |
| [[2026-05-01]] | Fri |  |

## April 2026

| Date | Day | What happened |
|---|---|---|
| [[2026-04-30]] | Thu |  |
| [[2026-04-29]] | Wed |  |
| [[2026-04-13]] | Mon |  |
| [[2026-04-08]] | Wed |  |
| [[2026-04-03]] | Fri |  |
| [[2026-04-01]] | Wed |  |

## March 2026

| Date | Day | What happened |
|---|---|---|
| [[2026-03-14]] | Sat |  |
| [[2026-03-09]] | Mon |  |
| [[2026-03-08]] | Sun |  |
| [[2026-03-07]] | Sat |  |
| [[2026-03-06]] | Fri | Before (broken): |

## February 2026

| Date | Day | What happened |
|---|---|---|
| [[2026-02-24]] | Tue |  |
| [[2026-02-23]] | Mon |  |
| [[2026-02-20]] | Fri |  |
| [[2026-02-19]] | Thu |  |
| [[2026-02-13]] | Fri |  |
| [[2026-02-12]] | Thu |  |
| [[2026-02-11]] | Wed | Create higher-priority drop-in config |
| [[2026-02-10]] | Tue |  |
| [[2026-02-09]] | Mon |  |
| [[2026-02-06]] | Fri |  |
| [[2026-02-05]] | Thu |  |
| [[2026-02-04]] | Wed | Wednesday |

## Related
- [[_INDEX]] — vault home
- [[RIG-EXPANSION-HUB]] — the 8 → 32 mouse programme
