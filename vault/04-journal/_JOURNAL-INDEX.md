# 📓 Journal Index — chronological master navigator

> [!abstract] How the journal works
> Every daily journal in date order, **newest first**.
>
> **The daily journal is the master navigator.** It records what happened that day and links out to the notes where the detail lives: decisions in `07-decisions/`, procedures in `02-procedures/`, references in `06-references/`, incidents in `03-troubleshooting/`.
>
> Read a day here, then follow its links down. **Detail belongs in the linked notes, not in the journal.**

**67 entries.** Dates with no entry had no vault activity, mostly weekends.


## September 2026

| Date | Day | What happened |
|---|---|---|
| [[2026-09-16]] | Wed | ✅ **Syncthing uninstalled from `e10ubuntu` AND the office PC** (`Andrea-KAIST-PC-ubuntu`), packages and all — **only the ThinkPad still has it**. Both device identities parked, not deleted. ⚠️ The office PC's live config was `~/.local/state/syncthing`, and `apt purge` does NOT stop a running daemon: `which` went quiet while `pgrep` still returned two PIDs. 🔴 **`sudo apt autoremove` took 52 packages / 984 MB there** including the NVIDIA 570 stack, then left the WORKING 580 driver marked auto-removable — pinned with `apt-mark manual`. ⭐ **A fourth machine**, the SKIM office workstation (`/home/skim`): `bootstrap.sh` KEEPS an existing `settings.json`, so it reported success while the machine had **no SessionStart hooks and no `skim status`**. 🔴 Uncommitted work still stranded in the office PC's `neurosurveillance`. |
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
