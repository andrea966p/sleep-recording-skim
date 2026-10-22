---
name: pattern-frigate-record-enabled-orphan-noise
description: "Frigate record.enabled=true makes reconciler ORPHAN findings structural noise: keep MIN_ORPHAN_DURATION_S at 6 h and suppress ORPHAN in alerts"
metadata: 
  node_type: memory
  type: project
  originSessionId: 5cbc6d77-6b1d-49ac-9f41-42050a74c3fc
---

Frigate runs `record.enabled: true`, so it records 24/7 regardless of daemon sessions; "Frigate segments without a session = ORPHAN" fires constantly. The reconciler sets `MIN_ORPHAN_DURATION_S = 21600` (6 h) so ORPHAN only flags outsized runs; PARTIAL / STUCK / DEGRADED stay actionable.

Details: [[reconciler]] · [[2026-05-24]] (journal architecture notes)

- Alert only on `partial + stuck + degraded > 0`; suppress ORPHAN counts. If ORPHAN is ever made actionable, reset to `MIN_FINDING_DURATION_S` and do not merge the two thresholds into one tunable.
- 🛑 Never set `record.enabled: false` to quieten this: [[feedback_record_enabled_false_off_limits]].
