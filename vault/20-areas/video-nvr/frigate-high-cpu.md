---
type: incident
area: video-nvr
status: active
tags: [troubleshooting, symptom, frigate]
created: 2026-02-05
severity: high
---

## Description

- Frigate container using 100% CPU
- Recordings dropping frames
- Web interface sluggish

## Root Cause

**No hardware acceleration enabled** - CPU doing all video decoding

## Quick Diagnosis

```bash
# Check GPU usage
curl -s http://localhost:5000/api/stats | grep -i qsv

# Check CPU usage
docker stats frigate --no-stream
```

## Solution

### 1. Add GPU device to docker-compose.yml:
```yaml
devices:
  - /dev/dri:/dev/dri
group_add:
  - "992"  # render
  - "44"   # video
```

### 2. Add hwaccel to config.yml:
```yaml
ffmpeg:
  hwaccel_args: preset-intel-qsv-h264
```

### 3. Restart:
```bash
docker compose down
docker compose up -d
```

## Verify Fix

```bash
# CPU should drop from 100% to 9-12%
docker stats frigate

# Check QSV is active
curl -s http://localhost:5000/api/stats | python3 -c \
  "import sys,json;d=json.load(sys.stdin);print(d.get('gpu_usages',{}))"
```

## Expected Performance After Fix

| Metric | Before | After |
|--------|--------|-------|
| CPU | 100% | 9-12% |
| GPU | 0% | 3-4% |

## Related

- [[docker-compose|Docker Compose config]]
- [[config-yml|Frigate config.yml]]
