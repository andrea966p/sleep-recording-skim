---
type: experiment
area: rig-bringup
status: done
tags: [decision, audit, eeg, recording, thermal, frigate, grounding]
created: 2026-07-13
subjects: [mouse-A, mouse-B, mouse-C, mouse-D]
recording: allego_0__uid0710-08-53-31
---

# 72h 4-Mouse Recording — Full Audit (Jul 10-13 2026)

> [!abstract] TL;DR
> We ran our first 72-hour, 4-mouse recording (Fri Jul 10 08:53 → Mon Jul 13 09:06 KST). The FILE is a triumph, 72.22 hours, byte-perfect, zero dropped samples, so the rig's endurance at full 256-channel scale is now PROVEN. Everything else has a problem:
> - **EEG signal UNUSABLE** — all 4 mice swamped by massive 60 Hz mains hum. 0 of 4 scoreable. Cause is a FLOATING system (nothing earthed), not the surgeries. Fix: [[earthing-60hz-hum-fix]].
> - **VIDEO recorded NOTHING** — Frigate recording was left OFF since Jul 3, so there's no synchronized video for the whole run.
> - **PC survived but ran at its thermal ceiling** — peak 101 C, thermally throttled ~78% of the run. Cooling is the wall.
> - **Allego did NOT crash on Thursday** — it was a clean quit tied to RustDesk, and the "lost settings" is the known re-enumeration reset. Fixes: [[allego-settings-save-restore]] and the RustDesk display issue in [[2026-07-13]].
>
> Method: I ran 5 parallel investigation agents (EEG quality, PC performance, Allego logs, Frigate, settings), each read-only against the live machine.

---

## 1. EEG data integrity — PASS (this is the good news)

- File `allego_0__uid0710-08-53-31` in `~/radix/data`. 256 primary channels = 4 mice (ports A/B/C/D) x 64. Sample rate 1000 S/s. 259,986,944 samples = 72.22 hours.
- `data.xdat` = 272,466,317,312 bytes = exactly num_smpl x 262 x 4 (262 = 256 primary + 2 aux + 2 digital-in + 2 digital-out). Matches the header.
- Timestamps strictly monotonic, EVERY step +1, ZERO gaps, ZERO missing samples across all 260M samples.
- **Verdict:** the full 72.22 h is one continuous, byte-perfect recording. Write-endurance and crash-resilience at 256ch / 72h are PROVEN.

## 2. EEG signal quality — FAIL (0 of 4 mice usable)

Every mouse is buried under ~60 Hz mains hum, raw RMS 2000 to 4500 µV (2 to 4.5 mV), pk-pk hitting the ±6.4 mV amplifier rail. Real mouse EEG is tens-to-low-hundreds of µV, so the hum is 10 to 40x bigger than signal.

Per-mouse (avg of start / mid / end windows), amplitudes in µV:

| Mouse | EEG raw RMS | EEG resid (post-notch) | EMG raw RMS | EMG resid | Bipolar resid | Usable? |
|---|---|---|---|---|---|---|
| A | 2455 | 207 | 2177 | 201 | 275 | NO |
| B | 3897 | 139 | 868 | 39 | 203 | EMG marginal, EEG dirty |
| C | 2308 | 343 | 4012 | 216 | 476 | NO |
| D | 2541 | 189 | 3441 | 86 | 289 | NO |

- **Usable EEG: 0 of 4. Usable EMG: 0-1 of 4** (only mouse B's EMG residual, 39 µV, looks plausible). **3-state scoreable (needs BOTH clean EEG and EMG): 0 of 4.**
- Channel layout confirmed from JSON: port base indices A=0, B=64, C=128, D=192. Per current wiring one port carries 2 mice via SPI splitter, ch 1-4 = mouse A, ch 33-36 = mouse B. See [[signal-mapping-guide]].
- Stable over the 72h, uniformly bad, no drift. Not an electrode drying out, it's constant background hum.
- PSD figure saved (giant 60 Hz spike + 120/180 Hz harmonics, tiny 50 Hz, all 4 mice).

### The 60 Hz finding
- 60 Hz peak power ~10^6 to 5x10^7 µV²/Hz. 50 Hz peak ~1 to 18,000 µV²/Hz (negligible). Ratio 1000x to millions. Strong 120 and 180 Hz harmonics.
- Confirms AGAIN that Korea mains is 60 Hz. The Jul 5 decision to move the notch to 60 Hz is CORRECT.
- BUT the notch is an OFFLINE software filter and this master file is raw wideband by design, so the hum is fully present. And critically, even after notch AND the bipolar subtraction (n0 - n1), 200 to 475 µV of hum SURVIVES. That means the hum is partly DIFFERENTIAL (unequal electrode / ground impedances), not pure common-mode, so software cannot rescue it.
- Uniform across all 4 independent ports = a SYSTEM-level grounding problem, not four bad surgeries.

### Root cause + fix
The whole recording system is FLOATING, nothing is tied to earth (the mini-PC runs off a 2-prong brick, and the animal ground → board GND → headstage → SPI splitter → XDAQ → USB → mini-PC chain touches no earth). A floating island sits in the 60 Hz field and swings, and unequal electrode-leg impedance converts that common-mode swing into surviving differential hum. **This is NOT a ground loop (earlier note was backwards), it's the OPPOSITE, too few earth connections (zero).** Fix = add ONE earth reference: wire board GND to the metal case of an earthed desktop PC, bond the aluminium rack to the same single point. Full procedure and a 2-minute live confirmation test in [[earthing-60hz-hum-fix]].

## 3. PC performance — survived, but at the thermal ceiling

Machine: mini-PC `e10ubuntu`, Intel Core Ultra 5 125H, 30 GiB RAM, 1.9 TB NVMe. This run = 4 mice EEG (Allego) + 4 cameras (Frigate) at once.

- **Continuity: all green.** Booted Jun 27 19:07, up 15 days, single boot ID across the whole window, NO reboot. Recording one continuous R_ON, Jul 10 08:53:31 → Jul 13 09:06:41. Frigate container RestartCount=0, OOMKilled=false. No systemd failures, no kernel MCE / disk errors.
- **Temperature (the concern):** package temp avg ~76 C, PEAK 101 C. Cores at >=90 C for 46.8% of the run (~34h), >=95 C for 21.5% (~15h), >=100 C for 3.6% (~2.5h).
- **Thermal throttling CONFIRMED:** Netdata's MSR THERM_STATUS counter showed throttle events in 77.7% of the window (~56h), peak 90.7 events/s on a core. RAPL package power pinned at ~20.0 W (the PL1 cap) the whole time. CPU frequency averaged only 1946 MHz (floor 560, peak 3306). NOTE: the kernel journal logged ZERO thermal lines, thermald manages it silently via RAPL, so journalctl alone would miss it. The MSR counter is the real evidence.
- **CPU / RAM / disk all fine:** CPU busy avg 20.3% (never compute-bound), iowait avg 7.6%. Load1 avg 4.17, max 10.75 on 18 threads. RAM used avg 9.4 GiB of 30, available never below 21 GiB, no OOM. Swap 4.3 GiB parked but static. NVMe 33% used (579 G / 1.9 TB, 1.2 TB free), composite 40.9 C, no errors.
- GPU/QSV: Frigate confirmed using `preset-intel-qsv-h264` hwaccel for the 4 streams, CPU stayed low = QSV offloading works, no sign of GPU overload.
- **Verdict:** hardware DID hold up for 72h at 4-mouse + 4-camera scale, no crash / restart / data loss. But this was NOT comfortable headroom, the CPU was power-capped at 20 W and throttling ~78% of the run, hitting 101 C with the fan barely spinning (~2000 RPM). Compute was never the limit (20% busy), COOLING is. Scaling to 8 mice or a hot ambient day is risky without the fixes: aggressive fan curve, dedust + repaste, run headless, or ultimately a proper continuous-duty chassis.

> [!warning] Monitoring gap this run
> The stress-test logger (`system_logger.sh`) and the Allego watchdog were NOT running during this recording, both frozen since Jul 3-5. So we had no per-60s telemetry of our own, this performance history came from Netdata. RE-ARM both before the next recording.

## 4. Video / Frigate — recorded NOTHING (clean total miss)

- Zero recording segments on disk for ANY of the 4 cameras for the entire 72h. Frigate recordings API returns `[]` for every camera. No exports.
- Root cause chain:
  1. Storage confirmed at real path `/srv/frigate/storage` → container `/media/frigate` (NOT the empty `/media/frigate-recordings`). Recordings dir genuinely empty.
  2. Config `/srv/frigate/config/config.yml` correctly has all 4 cameras with `record.enabled: true`, BUT the RUNTIME state (`/api/config`) shows `record.enabled = False` for all 4, an MQTT toggle overrides the config default and persists across restarts.
  3. Frigate app log: last recording event was `Turning off recordings for pi_cam_{0..3}` at Jul 3 09:20:34 (end of the prior stress test). NO "turning on" event after that, so recording was already OFF 7 days before this window opened.
  4. Daemon journal explicit: at Jul 10 08:53:31 `Auto video start DISABLED (sessions.auto_start=false), ignoring Radiens R_ON`, and Jul 13 09:06:41 `Auto video stop DISABLED, ignoring Radiens R_OFF`.
- Exports: none in the window (expected, auto-export disabled + no manual session). Newest exports are from the prior stress test.
- Health: NO stall/watchdog alerts, NO Pi5 PoE crashes, all 4 cameras currently live in `/api/stats`, daemon stayed connected to Radiens the full 72h. Cameras and Pis were healthy the whole time, this was purely the recording-enable STATE.
- Minor flags: cameras currently stream at **5.1 fps, not the configured 15 fps** (investigate separately). Disk `/` 579 G used, 1.2 TB free, healthy.
- **Verdict:** the video side did not capture this recording. Recoverable in future by re-enabling `sessions.auto_start: true` (flip flag + restart `neurosurveillance-session`) OR having an operator manually start Frigate recording. The EEG exists and is intact, there is simply no synchronized video for it.

## 5. Allego "closed by itself" Thursday — NO, clean quit tied to RustDesk

- The instance left open ran ~8 days (started Jul 1 16:04), then was cleanly SHUT DOWN Jul 9 19:53:11 KST via a normal "Close request" (`radix.log`: `Close - Close request received` → `Stopping pybridge server and exiting`; `allego-ui.log`: clean on-close). NO segfault, NO OOM, NO SIGKILL. The session daemon saw port 50051 go away at the same instant.
- 7 seconds earlier (19:53:04) a RustDesk remote-desktop session connected and the monitor did an EDID re-probe. Most likely a quit / window-close action happened around that connect. WORTH ASKING the lab member whether that RustDesk session was them and whether they closed the window.
- After 19:53 it was relaunched cleanly many times (20:09, 20:10, 20:57, 21:06, final backbone ~21:08), workspace state written 22:07, matching the "day before the recording" story. A few GPU `divide error` traps in libgallium during the churn, each survived.
- **Why settings were gone:** expected, not corruption. `allego-workspaces.json` shows the active workspace as "Untitled Workspace", `saved: false`, so no workspace was ever saved and the fresh launch came up at defaults. Even a saved workspace would NOT restore channel selection. Plus hardware re-enumeration resets Mode / rate / channels, the known "Allego forgets on re-enumeration" behavior. Config files were all intact.

Related, and confirmed again TODAY (Jul 13): the same RustDesk + shared-monitor/dummy-HDMI setup crashed the desktop session and killed a live Allego stream. Full write-up + the forced-EDID future fix in [[2026-07-13]].

## 6. Allego settings save / restore

Deliverable guide: [[allego-settings-save-restore]]. Key facts:
- Allego HAS a built-in **Save Workspace / Restore Workspace** (top-right icons, manual p29-30).
- Restore brings back Mode, Sample Rate, Filters (INCLUDING the 60 Hz notch), Headstage, Probe, Gain, Highpass, Digital-In triggering, but per the manual's own retention table (p30) NOT the selected/deselected sites (our 1-4 + 33-36 channel ticks) and NOT Digital-Out control mode. That documented gap IS the channel-forget behavior.
- On-disk workspace `~/radix/workspace/.system/ws-default_allego.json` was STALE (dated Feb 3, showing 30000 S/s), it was never tracking the live 1000 S/s config. `~/.config/allego` was reset Jul 9. Probe/channel maps `~/radix/devices/*.hstg` are plain-text YAML, safe to back up.
- Recommended: Save Workspace once, Restore each launch (covers ~90% incl. the notch), re-tick channel selection by hand (the one gap), plus a file backup of `~/radix/devices/`. 6 items flagged for bench verification (top one: does Save Workspace survive a full hardware unplug/replug, not just an app reopen).

---

## Action items / still open

| # | Item | Priority | Doc |
|---|---|---|---|
| 1 | **Earth the rig** (single earth point, live-test first). The #1 blocker, no scoreable EEG until fixed. | CRITICAL | [[earthing-60hz-hum-fix]] |
| 2 | Re-enable video capture for next run (`auto_start: true` or operator manual start) | HIGH | this doc §4 |
| 3 | Cooling before any 8-mouse / longer run (fan curve, dedust + repaste, headless) | HIGH | this doc §3 |
| 4 | Re-arm `system_logger.sh` + Allego watchdog before next recording | MEDIUM | this doc §3 |
| 5 | RustDesk display crash, forced EDID on `HDMI-A-1` (Tier 2) | MEDIUM | [[2026-07-13]] |
| 6 | Save Allego workspace + back up `~/radix/devices/` | MEDIUM | [[allego-settings-save-restore]] |
| 7 | Ask lab member about the RustDesk session Jul 9 19:53 | LOW | this doc §5 |
| 8 | Investigate cameras streaming 5.1 fps vs configured 15 fps | LOW | this doc §4 |

## Related
- [[earthing-60hz-hum-fix]] — the grounding fix (the big one)
- [[allego-settings-save-restore]] — never lose the acquisition config again
- [[2026-07-13]] — today's journal, RustDesk / HDMI display-crash future fix
- [[60hz-mains-hum-discovery]] — the original 60 Hz mains discovery
- [[signal-quality-and-grounding]] — signal evaluation (note: its "two mice per headstage" framing is superseded)
- [[signal-mapping-guide]] — channel map
- `05-experiments/completed/2026-07-02-eeg-recording-checkpoint.md` — prior checkpoint
