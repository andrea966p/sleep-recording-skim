---
type: reference
area: video-nvr
status: active
tags: [reference, video, configuration]
created: 2026-02-05
---

## Current Settings

| Parameter | Value |
|-----------|-------|
| Resolution | 1024x768 |
| Frame Rate | 15 fps |
| Bitrate | 1.5 Mbps |
| Codec | H.264 (libav) |
| Storage/day | ~16 GB/camera |

---

## Resolution Options

| Setting | Resolution | Parameters | Storage/Day |
|---------|------------|------------|-------------|
| High Detail | 1280x720 | `--width 1280 --height 720` | ~20 GB |
| **Current** | 1024x768 | `--width 1024 --height 768` | ~16 GB |
| Efficient | 800x600 | `--width 800 --height 600` | ~12 GB |
| Minimal | 640x480 | `--width 640 --height 480` | ~8 GB |

## Frame Rate Options

| FPS | Parameter | Use Case | Impact |
|-----|-----------|----------|--------|
| 30 | `--framerate 30` | Smooth motion | High CPU/heat |
| **15** | `--framerate 15` | Behavioral analysis | Balanced |
| 10 | `--framerate 10` | Standard monitoring | Low |
| 5 | `--framerate 5` | Long observation | Minimal |

## Bitrate Options

| Quality | Bitrate | Parameter |
|---------|---------|-----------|
| High | 3 Mbps | `--bitrate 3000000` |
| **Medium** | 1.5 Mbps | `--bitrate 1500000` |
| Low | 800 kbps | `--bitrate 800000` |

---

## Presets

### High Quality Analysis
```
--width 1280 --height 720 --framerate 30 --bitrate 2500000
```
Storage: ~22 GB/camera/day

### Standard (Current)
```
--width 1024 --height 768 --framerate 15 --bitrate 1500000
```
Storage: ~16 GB/camera/day

### Long-Term Studies
```
--width 800 --height 600 --framerate 10 --bitrate 1000000
```
Storage: ~11 GB/camera/day

### Extended Recording
```
--width 640 --height 480 --framerate 5 --bitrate 500000
```
Storage: ~5 GB/camera/day

---

## Storage Calculator

```
Daily Storage = Bitrate(Mbps) × 24 × 3600 × Cameras ÷ 8

Examples:
2 cameras @ 1.5 Mbps = 32.4 GB/day
4 cameras @ 1.0 Mbps = 43.2 GB/day
```

---

## Thermal Guidelines

| Temperature | Action |
|-------------|--------|
| < 60°C | Normal |
| 60-70°C | Monitor |
| > 70°C | Reduce settings |

**If overheating:** Reduce FPS or resolution first, then bitrate.

---

## Important Rules

1. **H.264 ONLY** - Never use H.265 (causes kernel panics)
2. **Monitor temperature** after changes
3. **Test one parameter** at a time
4. **Backup config** before changes
