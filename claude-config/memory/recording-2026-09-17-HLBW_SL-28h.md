---
name: recording-2026-09-17-HLBW_SL-28h
description: "28 h HLBW_SL run scheduled 2026-09-17 09:00 to 2026-09-18 13:00 KST, ZT0 to ZT4, 8 mice. A1 EEG confirmed dead before the start; Mesa GPU crash risk knowingly accepted because --disable-gpu stays out."
metadata:
  node_type: memory
  type: project
---

# HLBW_SL, 28 h, 2026-09-17 09:00 -> 2026-09-18 13:00 KST  ✅ DONE

Run `6255ffcf2575`, owner andrea, batch `HLBW_SL`, scheduled through the recorder
console at `127.0.0.1:8600`. ZT0 start to ZT4 stop, 28.0 h, ~106 GB at 3.77 GB/h.
Layout `8mice_eeg_emg`, 8 slots, 16 keep_labels A/1 A/2 A/33 A/34 per port.

## Known before the run started

🔴 **A1 EEG IS DEAD, its EMG is fine.** Two independent tests on 2026-09-16, each
on 5 min of live stream: EEG rms 6.2-6.3 uV against `DEAD_CHANNEL_UV` 20, and
spectral slope -0.02 where a wire-free input is -1.29 to -0.07 and a working
animal -1.5 to -2.1. The EMG partner carries 294-312 uV with 60 Hz at 15.9-40.6 uV,
inside `CONNECTED_HUM_BAND_UV` -- so the headstage, cable and ground on that slot
are all good and **only the EEG conductor is open**. Not a shared-path fault:
`r(E,M)` was 0.00-0.01 on all eight animals, against a 0.50 bar.

⚠️ **Expect 7 animals with EEG, not 8.** A1 should fail rung 2 on EEG alone.

🔴 **The 2026-08-24 Mesa GPU crash risk was ACCEPTED, deliberately.** The operator
chose to keep hardware GL (no `--disable-gpu`) rather than test the Chan-height
<= 30 workaround, so a 28 h unattended live-animal run is exposed to the crash
that killed a recording on 2026-08-24. App death ends the recording; a frozen GUI
does not lose data. **If this run dies mid-way, that is the first thing to check.**

## Other state at the start

- Kernel 7.0.0-28, pinned and held. Allego `XDAQ_ONE_REC`, 1000 Hz.
- 60 Hz notch confirmed NOT on the Data stage, so the file keeps its hum evidence.
- Local disk 758 GB free (150 GB reserve), NAS mounted with 4.98 TB free.
- ⚠️ The recorder backend runs at **PPID 1 with no systemd unit**. Nothing restarts
  it. `START_GRACE_S = 180`, so if it dies the run FAILS rather than starting late.
- Streaming was left OFF overnight on purpose; the scheduler turns it on ahead of
  the instant so the amplifiers settle.

## Related

[[allego-blank-monitor-canvas-texture-limit]] · [[allego-mesa-gpu-crash-and-log-storm]] ·
[[cohort-identity-every-run-is-new-mice]] · [[animal-card-verdict-ladder]]

## ✅ HOW IT ENDED, 2026-09-18

**The workflow ran clean end to end, unattended.** Stop 13:00:05 (5 s late),
28.00 h, 100,793,088 samples, remainder 0. Strip 262 -> 16 ch, 93.18% saving,
`verify: full` compared EVERY sample with `exact: True`. Upload 5 files VERIFIED
by sha256 at both ends, ~105 MB/s, **QC bundle uploaded with it** so the
wire-free floor survives as a cached feature set even though the stripped copy
has none. Stop -> verified on the NAS in **13 minutes**. No Mesa crash.
Landed at `andrea/20260917_HLBW_SL_RSR/`.

**Rung 2, full file: 7 of 8 CLEAN, A1 DEAD (4.9 uV).** B1, B2 and D2 held
UNBROKEN 28 h blocks.

**Sleep, full 28 h — 3 scoreable, all on grounded chips:**
B1 r@1min 0.671 WAKE 38.0% · B2 0.697 / 41.7% · D2 0.503 / 33.5%.
Rejected: A2 (floor 582), C1 (floor 7), D1 (floor 2) — all ungrounded — and
C2 on `nrem_has_most_delta` despite a good floor of 4084; C2 also drops to
4-11% sleep after ZT9. ⚠️ Wake 33-42% over a full cycle is normal; the 22-23%
quoted from the light phase alone is not comparable.

Analysis + figures: `05-experiments/completed/2026-09-18-W-SL-light-phase-sleep.md`.
🔑 Only **B2** is judgeable and accepted on BOTH 09-10 and 09-17, so the
baseline comparison is n=1.
