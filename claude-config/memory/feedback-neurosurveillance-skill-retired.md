---
name: feedback-neurosurveillance-skill-retired
description: The claude.ai skill neurosurveillance-expert is RETIRED by Andrea (2026-10-01); do not use or cite it. Vault + repo are the source of truth.
metadata:
  type: feedback
---

Andrea retired the `neurosurveillance-expert` skill on 2026-10-01.

**Why:** it was out of date. It assumed a PostgreSQL/TimescaleDB layer that was never deployed, linked a missing
`references/eeg_sync.md`, described an "Allego MCP" that does not exist, and knew nothing about the XDAQ, the
recording console, the SKIM NAS or QC. It also assumes cameras that were removed on 2026-08-04.

**How to apply:** never load it or quote it. If its synced copies (`~/.claude/skills/synced/*/neurosurveillance-expert`)
still appear, the claude.ai deletion has not propagated yet. Use the vault and the repo code instead.
