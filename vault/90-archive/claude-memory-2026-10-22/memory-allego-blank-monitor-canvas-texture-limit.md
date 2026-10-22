---
name: allego-blank-monitor-canvas-texture-limit
description: "Allego Monitor draws nothing (axis sweeps, traces hoverable but invisible) because --disable-gpu forces SwiftShader with an 8192 px texture limit while the Monitor canvas is signals x chan-height = 262 x 50 = 13175 px. Hardware GL (16384) renders it. Solved 2026-09-16."
metadata: 
  node_type: memory
  type: project
  originSessionId: 6ac52e19-d272-4acf-9208-5e857b939775
  modified: 2026-09-16T11:54:57.663Z
---

# The Monitor went blank because the canvas outgrew the software renderer

**2026-09-16.** Allego streamed, recorded and reported every channel healthy, but the
Monitor drew NOTHING: the time axis swept, the channel rows were hoverable and
clickable, and not one pixel of trace was painted. Fixed by launching
`/opt/allego/allego` WITHOUT `--disable-gpu`.

## The mechanism

The Monitor renders into an **OffscreenCanvas transferred to a Web Worker** — which is
why nothing ever appeared in `allegoserver.log`, `allego-ui.log`, or the page console.
Errors happen in the worker, invisible everywhere we normally look.

That canvas is sized **all AVAILABLE signals x Chan height**, NOT the selected ones.
Measured directly: chan height 5 -> canvas 1317 px, 20 -> 5270 px, 50 -> 13175 px,
with 262 signals present.

| launch | renderer | MAX_TEXTURE_SIZE | 13175 px canvas |
|---|---|---|---|
| `--disable-gpu` | ANGLE / SwiftShader | **8192** | FAILS -> blank |
| no flag, kernel 7.0.0-28 | ANGLE / Intel Arc Mesa | **16384** | fits -> **draws** |
| no flag, kernel 7.0.0-31 | fell back to SwiftShader | 8192 | FAILS -> blank |

🔑 **Nothing broke. A threshold got crossed.** The rig used to enumerate ~96 signals
(3 ports x 32) => 96 x 50 = 4800 px, comfortably under 8192, so `--disable-gpu` was
harmless for months. Moving to **4 ports x 64 = 262 signals** pushed the canvas past
the software limit. Last good recording 2026-09-09 was under the old channel count.

## Why it is so hard to diagnose

- Acquisition is completely unaffected — data reaches the cache and records fine.
- Every layer reports healthy: ports scan, `IsHardwareConnected=true`, KPI tracking,
  packets climbing, cache growing.
- A canvas over `MAX_TEXTURE_SIZE` is **silently clamped**, not refused.
- The traces stay hit-testable, so they feel "there but invisible" — which sends you
  hunting for a colour/opacity bug that does not exist.

## What was ruled OUT (each cost real time)

🛑 Licensing (`FeatureStop feature=Feat_Scope module=licensing` appears in KNOWN-GOOD
Aug 28 / Sep 3 logs — it is routine teardown noise, NOT a revocation).
🛑 The Radiens cloud 502s on `hstg__usrdef_8mice_EEG_EMG` — real, but only forces a
fallback to a default sensor map; local files at `~/radix/devices/` load fine.
🛑 RustDesk capture (server-side `xwd` of the window is blank too).
🛑 Electrodes-tab site selection, Units-vs-Fields preset, Viz Bandpass, Chan height,
AMP range — all inert while there is no WebGL context at all.
🛑 Kernel rollback on its own: on 7.0.0-28 WITH `--disable-gpu` it is still blank.

## The live trade-off, UNRESOLVED

`--disable-gpu` exists for a reason: [[allego-mesa-gpu-crash-and-log-storm]], the
2026-08-24 Mesa crash that killed a recording and made a 6.5 GB log storm. Running
without it restores the scope but puts that crash back in front of a 20 h unattended
live-animal run.

⭐ **Untested option that would keep both:** keep `--disable-gpu` and set **Chan height
<= 30** (262 x 30 = 7860 < 8192). The dropdown is fixed values — 25 does not exist,
check for 30 or 20. If that renders, it is the configuration to standardise on.

## What was actually applied, 2026-09-16

✅ **Kernel pinned to 7.0.0-28 permanently.** `GRUB_DEFAULT` set to
`gnulinux-advanced-3fa24403-...>gnulinux-7.0.0-28-generic-advanced-3fa24403-...`,
`update-grub` run, entry id verified present in `grub.cfg`. On 7.0.0-31 Chromium
refuses the Intel GPU and falls back to SwiftShader, which puts the blank Monitor back.
✅ **Kernel held:** `apt-mark hold linux-generic-hwe-24.04 linux-image-generic-hwe-24.04
linux-headers-generic-hwe-24.04` — unattended-upgrades can no longer move it.
✅ **`--disable-gpu` removed from `~/.local/share/applications/allego.desktop`**, with
the full history written into the file so it is not re-added blindly.

🔴 **Therefore the 2026-08-24 Mesa crash risk is BACK for long unattended runs.** Test
the Chan height ≤30 option before the next multi-hour live-animal run.

## Related

[[allego-mesa-gpu-crash-and-log-storm]] · [[allego-orphaned-server-blocks-the-rig]]


## From the memory index, trimmed there 2026-10-06 (kept here verbatim)

- ✅🔴⭐⭐⭐ **[BLANK MONITOR = CANVAS BIGGER THAN THE SOFTWARE RENDERER — 2026-09-16](allego-blank-monitor-canvas-texture-limit.md). NEWEST.** Canvas = ALL signals × Chan height (262×50=13175 px); `--disable-gpu` ⇒ SwiftShader 8192 ⇒ never draws. Launch WITHOUT the flag ⇒ Intel GL 16384 ⇒ works. 96→262 signals crossed a threshold.
