---
base: "[[🚑 Troubleshooting & Triage.base]]"
Solution Notes: Usually storage related - clean old recordings and restart container
Priority: 🟠 High
System: Frigate Server
Status: 🟡 Common
---
## 😨 Initial Observation

Docker container exits with "cannot allocate memory" or similar resource errors.

## 🩺 First-Level Diagnostics

- [ ] Check available disk space: `df -h`
- [ ] Check memory usage: `free -h`
- [ ] Check Docker container status: `docker ps -a`
- [ ] Review Docker logs: `docker logs frigate --tail 100`
- [ ] Check system load: `htop`

## 🧠 Known Causes

- Insufficient disk space in recording directory
- Memory leak in Frigate container
- Corrupted video files filling storage
- System swap disabled

## ✅ Solution

```bash
# Check and clean old recordings
find /path/to/recordings -name "*.mp4" -mtime +7 -delete

# Restart Frigate with fresh container
docker compose down
docker compose up -d

# If memory issues persist, check Frigate retention settings
# Reduce retain days in config.yml
```