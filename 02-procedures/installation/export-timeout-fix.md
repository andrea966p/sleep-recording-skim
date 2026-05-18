---
tags: [procedure, implementation, bugfix, frigate, session-daemon]
created: 2026-05-18
completed: 2026-05-18
status: completed
related-incident: 2026-05-11 export timeout
---

# Export Timeout Fix — Implementation Guide

## Purpose

Replace the session daemon's fixed 5-minute export-completion timeout with a progress-aware wait, so multi-day recordings can finish multiplexing in Frigate before the daemon gives up.

Triggered by the 2026-05-11 incident in which three ~96-hour sessions (Diane / H5S251A mice) finished multiplexing in Frigate within 6–7 minutes of stop, but the daemon had already given up at 5 minutes — marking all three `"failed: export timed out"`, leaving the MP4s orphaned under `/srv/frigate/storage/exports/` (root-owned, never moved).

## Background — what the bug actually does

**File:** `neurosurveillance/backend/frigate_controller.py`

```python
EXPORT_POLL_INTERVAL = 2.0
EXPORT_TIMEOUT = 300.0       # 5 minutes max wait for export   ← the bug
```

`wait_for_export()` loops until `time.time() < deadline`. When it gives up, `_execute_export()` in `daemon.py:378-382` writes `"failed: export timed out"` to the session JSON and **never calls `_move_export_file()`**. Frigate keeps multiplexing happily in the background; the finished MP4 sits orphaned in the exports directory.

The Mar 6 fix added `in_progress` polling so we don't move files mid-write — that part still works. The remaining defect is purely that the deadline is too short for long recordings, and we ignore the signal Frigate already gives us (`in_progress: True` = "still working").

### Empirical multiplex speed

The May 11 recovery files give us a data point:

| Recording | Wall-clock multiplex time | Source duration | Speedup vs realtime |
| ---: | ---: | ---: | ---: |
| pi_cam_0 (`izz943`) | ~6 min | 95.5 h (requested) | ~950× |
| pi_cam_1 (`nnw1z8`) | ~7 min | 95.5 h (requested) | ~820× |

For sizing purposes: a week-long (168 h) recording should finish multiplexing in ~12–15 min on this hardware. A fixed timeout of even 60 min would have prevented this incident, but a progress-aware wait is more robust.

## What gets changed

- `neurosurveillance/backend/frigate_controller.py` — constants and `wait_for_export()` body
- Nothing in `daemon.py`, `manual_session_manager.py`, or the frontend changes
- Config schema unchanged

---

## Step 1 — Update the polling constants

**File:** `neurosurveillance/backend/frigate_controller.py:24-26`

Replace:

```python
# Frigate export status polling
EXPORT_POLL_INTERVAL = 2.0   # seconds between export status checks
EXPORT_TIMEOUT = 300.0       # 5 minutes max wait for export
```

With:

```python
# Frigate export status polling.
# The wait is progress-driven: as long as Frigate reports the export as
# in_progress=True, we keep waiting. STALL_TIMEOUT only kicks in if Frigate
# stops responding or the export disappears from the list. MAX_TIMEOUT is
# a safety ceiling to prevent indefinite hangs.
EXPORT_POLL_INTERVAL = 5.0    # seconds between export status checks
EXPORT_STALL_TIMEOUT = 600.0  # 10 min grace if Frigate unreachable / export vanishes
EXPORT_MAX_TIMEOUT = 86400.0  # 24h hard ceiling (safety net)
```

Rationale: 5s polls instead of 2s reduce churn during multi-day exports (~14k requests at 2s vs ~6k at 5s — both negligible, but 5s is friendlier when GET `/api/exports` itself takes a few hundred ms on a busy NVR). The 24h ceiling is generous enough to never trip in normal operation.

## Step 2 — Rewrite `wait_for_export()`

**File:** `neurosurveillance/backend/frigate_controller.py:296-334`

Replace the entire method with:

```python
def wait_for_export(self, export_id: str) -> Optional[dict]:
    """Poll Frigate until the export completes, stalls, or hits the ceiling.

    Wait semantics:
      - As long as Frigate reports the export with in_progress=True, keep
        waiting. There is no per-recording timeout.
      - If Frigate becomes unreachable OR the export disappears from the
        list, allow EXPORT_STALL_TIMEOUT of grace before giving up.
      - EXPORT_MAX_TIMEOUT is a hard ceiling (default 24h) that should
        never be hit during normal operation.

    Args:
        export_id: The export ID returned by export_recording().

    Returns:
        Export metadata dict if completed, None on stall/ceiling/error.
    """
    url = f"{self.frigate_url}/api/exports"
    started = time.time()
    last_progress = started   # last time we confirmed in_progress=True
    logger.info("Waiting for export %s to complete...", export_id)

    while time.time() - started < EXPORT_MAX_TIMEOUT:
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            exports = response.json()

            found = False
            for export in exports:
                eid = export.get("id") or export.get("name")
                if eid != export_id:
                    continue
                found = True
                if export.get("in_progress", False):
                    last_progress = time.time()
                    break
                elapsed = time.time() - started
                logger.info(
                    "Export %s completed after %.0fs", export_id, elapsed,
                )
                return export

            if not found:
                # Export not (yet) in list — could be initializing, or
                # finished+cleaned. Allow stall grace before giving up.
                stalled_for = time.time() - last_progress
                if stalled_for > EXPORT_STALL_TIMEOUT:
                    logger.error(
                        "Export %s vanished from Frigate's list for %.0fs",
                        export_id, stalled_for,
                    )
                    return None

            time.sleep(EXPORT_POLL_INTERVAL)

        except Exception as e:
            stalled_for = time.time() - last_progress
            logger.warning(
                "Error checking export status (%.0fs since progress): %s",
                stalled_for, e,
            )
            if stalled_for > EXPORT_STALL_TIMEOUT:
                logger.error(
                    "Lost contact with Frigate for %.0fs while waiting for %s",
                    stalled_for, export_id,
                )
                return None
            time.sleep(EXPORT_POLL_INTERVAL)

    logger.error(
        "Export %s exceeded max wait of %.0fs",
        export_id, EXPORT_MAX_TIMEOUT,
    )
    return None
```

### Behavioural diff vs. the old code

| Scenario | Old behaviour | New behaviour |
| --- | --- | --- |
| 96 h recording, 7 min multiplex | ❌ Timeout at 5 min, file orphaned | ✅ Returns when Frigate flips `in_progress` → false |
| Export legitimately stuck for hours | ✅ Times out at 5 min | ✅ Hits 24h ceiling (rare; would also be caught by stall grace if Frigate ever stops reporting `in_progress`) |
| Frigate crashes mid-export | ❌ Falsely succeeds until 5 min, then times out | ✅ Stall grace fires at 10 min once API stops responding |
| Frigate restarts and forgets export | ❌ Timeout at 5 min | ✅ Stall grace fires at 10 min after export disappears |

## Step 3 — Restart the daemon

```bash
sudo systemctl restart session-daemon
sudo systemctl status session-daemon --no-pager | head -15
tail -f /opt/neurosurveillance/logs/session-daemon.log    # watch for clean startup
```

No config changes, no schema migration — the only state in flight is `_active` and `_history` in `ManualSessionManager`, both reloaded from disk on restart.

## Step 4 — Verify with a long-duration test

Quick smoke test (won't catch the long-duration bug but proves nothing regressed):

1. From the Tauri UI, start a manual recording on one camera
2. Stop it after ~30 seconds
3. Confirm session JSON ends with `"export_status": "completed"` and file lands in `/opt/neurosurveillance/exports/<user>/<mouse>/<date>/`
4. `grep "Export .* completed" /opt/neurosurveillance/logs/session-daemon.log` — should show elapsed time

Long-duration verification (run when convenient):

1. Start a recording, leave running for ≥ 24 h
2. Stop and watch the daemon log
3. Expected log lines: `Waiting for export ...` → `Export ... completed after Ns` where N ≫ 300
4. Confirm the MP4 lands in the organised export tree, not in `/srv/frigate/storage/exports/`

## Rollback

Revert both edits to `frigate_controller.py` (one constants block + one method body). No state to migrate, no config to roll back. `sudo systemctl restart session-daemon` after revert.

## Related

- [[04-journal/2026-03/2026-03-06|Mar 6 race-condition fix]] — added `in_progress` polling; this guide reuses that signal as the primary wait condition
- 2026-05-11 incident (this guide) — three Diane / H5S251A sessions, 95.5 h each, marked failed; two files recovered (~8.3 h each — recording itself was truncated; the export wait bug is independent of that), pi_cam_2 export never produced by Frigate and source segments now aged out by `retain.days: 7`
- [[02-procedures/session-recording-workflow#manual-export|session-recording-workflow]] — the "manual export" fallback section is what users had to fall back to with the bug present; keep it for the rare cases where this fix doesn't help (e.g. Frigate truly stuck)
