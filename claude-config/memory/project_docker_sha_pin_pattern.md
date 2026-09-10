---
name: project-docker-sha-pin-pattern
description: "When pinning a Docker image that doesn't publish per-patch tags on Docker Hub, pin by SHA256 digest of the locally-cached image"
metadata: 
  node_type: memory
  type: project
  originSessionId: 0b64ed9b-5689-4074-8603-f37b0836d899
---

When a Docker image's running version doesn't have a corresponding tag on the registry, pin by SHA256 digest. The compose syntax is:

```yaml
image: <name>:<floating-tag>@sha256:<digest>
```

**Why:** Some upstreams (Mosquitto on 2026-05-22 is an example — `eclipse-mosquitto:2.1.2` doesn't exist as a plain tag, only `2.1.2-alpine`) only publish the rolling major tag plus the latest-and-greatest specific. The SHA digest is immutable, makes Docker use the locally-cached image directly (no Docker Hub roundtrip), and survives Docker Hub policy changes upstream.

**How to apply:** When `docker compose up -d` reports `not found` after a tag bump, check `docker images <name> --digests` for the running SHA, then pin to `<name>:<floating-tag>@sha256:<digest>`. Don't try guessing other specific tags upstream might or might not have — go straight to the digest.

**Real example (2026-05-22 NeuroSurveillance Phase 1.2):**
- Wanted to pin `eclipse-mosquitto:2` to a specific minor
- Tried `eclipse-mosquitto:2.1.2` (the running version per `mosquitto -h`) — failed: `not found`
- Docker Hub showed `2.1.2-alpine` exists but not plain `2.1.2`
- Solution: pin to `eclipse-mosquitto:2@sha256:9cfdd46ad59f3e3e5f592f6baf57ab23e1ad00605509d0f5c1e9b179c5314d87` (the SHA of the running image)
- Container starts from local cache; immutable; survives upstream tag changes

Related: [[project-docker-upgrade-recordings]] — the broader pattern of preventing unexpected Docker behavior changes.
