---
type: incident
area: allego
status: active
status-note: "fixed 2026-09-16 by launching without --disable-gpu; the Mesa-crash trade-off is still open"
created: 2026-09-16
tags: [allego, monitor, gpu, incident]
---

# The Allego Monitor went blank because the canvas outgrew the software renderer

> [!abstract] TL;DR
> **What broke.** On 2026-09-16 Allego streamed, recorded and reported every channel healthy, but the Monitor drew nothing: the time axis swept, the channel rows were hoverable, and no trace was painted.
> **Fix.** Launch `/opt/allego/allego` without `--disable-gpu`, on kernel 7.0.0-28. The trade-off with [[allego-mesa-gpu-crash-and-log-storm]] is not closed.

> [!info] Promoted from a Claude memory file on 2026-10-22
> Written from the memory note `allego-blank-monitor-canvas-texture-limit` (saved 2026-09-16). The launcher file and the kernel pin were re-checked read-only on 2026-10-22 and match what is written here.

## Symptoms

Acquisition was completely unaffected: data reached the cache and was recorded. Every layer reported healthy (ports scan, `IsHardwareConnected=true`, KPI tracking, packets climbing, cache growing). The traces stayed hit-testable, so they felt "there but invisible", which sends you hunting for a colour or opacity bug that does not exist.

## Root cause

The Monitor renders into an `OffscreenCanvas` transferred to a Web Worker. Errors happen in the worker, so nothing appeared in `allegoserver.log`, `allego-ui.log` or the page console. The canvas is sized **all available signals x Chan height**, not the selected ones. Measured directly with 262 signals present: chan height 5 gave 1317 px, 20 gave 5270 px, 50 gave 13175 px.

| launch | renderer | MAX_TEXTURE_SIZE | 13175 px canvas |
|---|---|---|---|
| `--disable-gpu` | ANGLE / SwiftShader | **8192** | fails, blank |
| no flag, kernel 7.0.0-28 | ANGLE / Intel Arc Mesa | **16384** | fits, draws |
| no flag, kernel 7.0.0-31 | fell back to SwiftShader | 8192 | fails, blank |

A canvas over `MAX_TEXTURE_SIZE` is silently clamped, not refused.

🔑 **Nothing broke. A threshold got crossed.** The rig used to enumerate about 96 signals (3 ports x 32), so 96 x 50 = 4800 px, under 8192, and `--disable-gpu` was harmless for months. Moving to 4 ports x 64 = 262 signals pushed the canvas past the software limit. The last good recording under the old channel count was 2026-09-09.

## What was ruled out (each cost real time)

🛑 Licensing: `FeatureStop feature=Feat_Scope module=licensing` appears in known-good logs of 2026-08-28 and 2026-09-03. It is routine teardown noise, not a revocation.
🛑 The Radiens cloud 502s on `hstg__usrdef_8mice_EEG_EMG`: real, but they only force a fallback to a default sensor map; local files in `~/radix/devices/` load fine.
🛑 RustDesk capture: a server-side `xwd` of the window is blank too.
🛑 Electrodes-tab site selection, Units-vs-Fields preset, Viz Bandpass, Chan height and AMP range are all inert while there is no WebGL context at all.
🛑 A kernel rollback on its own: on 7.0.0-28 with `--disable-gpu` the Monitor is still blank.

## Fix, as applied 2026-09-16

- ✅ Kernel pinned to 7.0.0-28: `GRUB_DEFAULT` names that entry and `update-grub` was run. On 7.0.0-31 Chromium refuses the Intel GPU and falls back to SwiftShader, which brings the blank Monitor back.
- ✅ Kernel held with `apt-mark hold` on `linux-generic-hwe-24.04`, `linux-image-generic-hwe-24.04` and `linux-headers-generic-hwe-24.04`, so unattended upgrades cannot move it.
- ✅ `--disable-gpu` removed from `~/.local/share/applications/allego.desktop`. The file carries the full history so the flag is not re-added blindly.

Re-checked read-only on 2026-10-22: the kernel is 7.0.0-28-generic, `GRUB_DEFAULT` names it, the three hwe packages are held, the `Exec` line of the launcher has no flag, and the running Allego has a GPU process.

## Prevention and the open trade-off

🔴 Without the flag the 2026-08-24 Mesa crash risk is back for long unattended runs ([[allego-mesa-gpu-crash-and-log-storm]]).

⭐ An untested option that would keep both: keep `--disable-gpu` and set Chan height to 30 or less (262 x 30 = 7860, under 8192). The dropdown has fixed values, so check that 30 or 20 exists. If that renders, it is the configuration to standardise on. Test it before the next multi-hour live-animal run.

Related: [[allego-orphaned-server-blocks-the-rig]] · [[starting-the-rig-after-a-restart]] · [[live-signal-quality-terms]]
