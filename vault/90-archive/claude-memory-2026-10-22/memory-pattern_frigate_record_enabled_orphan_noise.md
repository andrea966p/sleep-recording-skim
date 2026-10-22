---
name: pattern-frigate-record-enabled-orphan-noise
description: Frigate config record.enabled=true makes ORPHAN findings structurally noisy — must use high duration threshold or skip the category in alerting.
metadata: 
  node_type: memory
  type: project
  originSessionId: 5cbc6d77-6b1d-49ac-9f41-42050a74c3fc
---

Frigate runs with `record.enabled: true` in its config (see [[feedback_record_enabled_false_off_limits]] — toggling off breaks Frigate). That means **Frigate records 24/7 regardless of daemon-tracked sessions**. Any reconciler / consistency check that flags "Frigate segments without a daemon session = ORPHAN" will produce findings every minute the daemon doesn't have a session running. With four cameras and continuous operation, this is structural noise, not a bug.

**Why:** The recording subsystem is uncoupled from the session lifecycle by design (Frigate keeps the always-on safety net even if the daemon is offline). Any "intent vs reality" cross-check needs to model this — sessions are about *intent to keep + metadata*, not about whether video was captured at all.

**How to apply:**

- For nightly reconciler-style checks, set `MIN_ORPHAN_DURATION_S` high (current: 6 h = `21600`) so only outsized continuous runs trigger. PARTIAL / STUCK / DEGRADED stay actionable; ORPHAN becomes a canary for "something genuinely weird, like a day of continuous recording without intervention."
- For Slack/alert wiring, **suppress ORPHAN counts entirely**. Alert only on `partial_count + stuck_count + degraded_count > 0`.
- If a future redesign makes ORPHAN actionable (e.g. by tracking daemon uptime windows in the WAL and scoping ORPHAN to those — see [[2026-05-24#Architecture / wiring|2026-05-24 architecture notes]]), reset the threshold to `MIN_FINDING_DURATION_S` and re-enable ORPHAN in alerting. Don't conflate the two thresholds in a single tunable.

The trade — "lower ORPHAN noise" vs "loses small-anomaly detection" — is acceptable because PARTIAL already catches "session existed but coverage was poor", which is the most useful signal for QC. ORPHAN's residual value is large-scale weirdness; the 6 h floor preserves that without flooding.

Reference: `reconciler.py` module-level constants + [[reconciler]] vault golden-config note.
