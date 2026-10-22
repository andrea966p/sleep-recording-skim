---
name: Verify operational details before writing guides
description: Never assume service names, paths, or system commands — always read the actual config/service files first
type: feedback
---

Always verify operational details (service names, file paths, systemd unit names, exact commands) by reading the source files before writing them into guides or procedures.

**Why:** Wrote `neurosurveillance` as the systemd service name in a guide when it was actually `neurosurveillance-session`. The correct name was in `01-infrastructure/session-daemon/session-service.md` but was never checked during planning.

**How to apply:** When writing procedures that reference system commands (systemctl, journalctl, etc.), read the relevant service/config files first. Don't guess names based on project conventions — look them up. Key reference: `session-service.md` has the systemd unit name, paths, and restart commands.
