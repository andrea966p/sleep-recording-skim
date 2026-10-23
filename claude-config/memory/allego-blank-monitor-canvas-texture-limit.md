---
name: allego-blank-monitor-canvas-texture-limit
description: "Allego Monitor draws nothing when launched with --disable-gpu (SwiftShader 8192 px texture limit vs canvas 262 signals x Chan height = 13175 px). Launch WITHOUT the flag; kernel pinned 7.0.0-28. Solved 2026-09-16."
metadata: 
  node_type: memory
  type: project
  originSessionId: 6ac52e19-d272-4acf-9208-5e857b939775
  modified: 2026-09-16T11:54:57.663Z
---

**2026-09-16:** blank Monitor (axis sweeps, traces hoverable, nothing painted) = canvas (ALL available signals x Chan height, 262 x 50 = 13175 px) bigger than SwiftShader's 8192 px limit under `--disable-gpu`. Fix: launch `/opt/allego/allego` WITHOUT `--disable-gpu` (Intel Arc GL, 16384 px). Kernel pinned to 7.0.0-28 (GRUB_DEFAULT) and held with `apt-mark hold`, because on 7.0.0-31 Chromium refuses the Intel GPU and falls back to SwiftShader. `--disable-gpu` removed from `~/.local/share/applications/allego.desktop`.

Details: [[allego-blank-monitor-canvas-texture-limit]]

🔴 The 2026-08-24 Mesa crash risk ([[allego-mesa-gpu-crash-and-log-storm]]) is therefore BACK for long unattended runs. Untested option that keeps both: `--disable-gpu` plus Chan height <= 30 (262 x 30 = 7860 < 8192). Ruled out, do not chase: licensing `FeatureStop` log lines (routine teardown noise), Radiens cloud 502 (only a sensor-map fallback), RustDesk capture, Electrodes-tab / Viz / AMP-range settings, kernel rollback alone.
- 2026-10-23, Andrea: keep Allego without `--disable-gpu`; no Chan-height test. `rig-check.sh` now warns if the flag is present. Later: move to the Open Ephys GUI.
