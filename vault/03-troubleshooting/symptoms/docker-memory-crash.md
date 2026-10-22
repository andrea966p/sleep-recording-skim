---
tags: [troubleshooting, symptom, frigate, docker]
created: 2026-02-05
severity: high
---

## Description

Docker container exits with "cannot allocate memory" or resource errors.

## Quick Diagnosis

```bash
# Check disk space
df -h

# Check memory
free -h

# Check container status
docker ps -a

# Review logs
docker logs frigate --tail 100
```

## Common Causes

| Cause | Likelihood | Check |
|-------|------------|-------|
| Disk full (recordings) | High | `df -h` |
| Memory leak | Medium | `docker stats frigate` |
| Corrupted videos | Low | Check storage directory |

## Solutions

### If disk full:
```bash
# Clean old recordings
find /srv/frigate/storage/recordings -name "*.mp4" -mtime +7 -delete

# Restart
docker compose down
docker compose up -d
```

### If memory leak:
```bash
# Reduce retention in config.yml
record:
  retain:
    days: 7  # Reduce from higher value

# Restart container
docker compose restart frigate
```

### Increase shm_size:
In `docker-compose.yml`:
```yaml
shm_size: "256mb"  # Increase if needed
```

## Prevention

- Set reasonable retention days (7 recommended)
- Monitor disk usage regularly
- Enable `expire_interval: 60` in config

## Related

- [[config-yml|Frigate config]]
