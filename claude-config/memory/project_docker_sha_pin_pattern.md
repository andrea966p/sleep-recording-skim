---
name: project-docker-sha-pin-pattern
description: "Pin a Docker image that has no per-patch tag by SHA256 digest of the locally cached image (image: name:tag@sha256:digest); Mosquitto example in the vault"
metadata: 
  node_type: memory
  type: project
  originSessionId: 0b64ed9b-5689-4074-8603-f37b0836d899
---

When `docker compose up -d` says `not found` after a tag bump (e.g. `eclipse-mosquitto:2.1.2` does not exist, only `2.1.2-alpine`), do not guess other tags: read the running digest with `docker images <name> --digests` and pin `image: <name>:<floating-tag>@sha256:<digest>`. The digest is immutable and uses the local cache. Mosquitto was pinned this way 2026-05-22.

Details: [[docker-compose]] (pinned digest and why) · journal 2026-05-22 · related [[project_docker_upgrade_recordings]]
