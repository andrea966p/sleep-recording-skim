---
tags: [infrastructure, session-daemon, reconciler, golden-config]
status: production
version: 1.0
added: 2026-05-24
related-commit: 3830dba
---

# Reconciler — golden config

> [!abstract] TL;DR — for non-technical readers
> **What this is.** A nightly self-audit. At 00:01 KST every night, the daemon compares what it thinks happened (the WAL journal) against what's actually on disk (Frigate's recordings database) and reports any disagreement.
>
> **Why it exists.** Without it, drift accumulates silently — an export hangs, a session is half-recorded, nobody notices for weeks. The reconciler flags four kinds of problems by name: ORPHAN (video without a session), PARTIAL (session with poor video coverage), STUCK (export that never finished), DEGRADED (session that stalled mid-recording).
>
> **How to read this page.** Read "Finding categories" first — that's the menu of what the reconciler can tell you. Skip to "MIN_ORPHAN_DURATION_S = 6h" if you wonder why ORPHANs seem noisy (Frigate records 24/7 — it's by design).

> [!quote] Paper-ready
> A background reconciler thread runs at 00:01 KST nightly, joining the durable session WAL against Frigate's recordings database to flag four categories of drift — ORPHAN, PARTIAL, STUCK, DEGRADED — and publishing a compact summary over MQTT to `neurosurveillance/reconciler/findings` for downstream alerting.

Nightly cross-check of the [[session-journal|session WAL journal]] against Frigate's `recordings` SQLite. Surfaces drift between **intent** (sessions the daemon started) and **reality** (segments on disk + exports completed).

> [!important] Read-only on both ends
> The reconciler never writes to the WAL nor to Frigate's DB. Both reads use `sqlite3.connect("file:…?mode=ro", uri=True)` — multi-reader WAL means runs can overlap a live daemon write without lock contention.

## File location

- Source: `~/Monitoring_project/neurosurveillance/backend/reconciler.py`
- Deployed (symlink): `/opt/neurosurveillance/session-daemon/reconciler.py`
- Reads:
  - `/opt/neurosurveillance/session_wal.db` (read-only)
  - `/srv/frigate/storage/frigate.db` (read-only — file is `0644 root:root`, world-readable; no permission change required)
- Writes: nothing on disk. MQTT publish to `neurosurveillance/reconciler/findings`.

## Schedule

| Field | Default | Source |
|---|---|---|
| `scheduled_hour` | `0` | `config.yaml` → `reconciler.scheduled_hour` |
| `scheduled_minute` | `1` | `config.yaml` → `reconciler.scheduled_minute` |
| `window_hours` | `24` | `config.yaml` → `reconciler.window_hours` |
| Timezone | `Asia/Seoul` | `config.yaml` → `daemon.timezone` |

The thread sleeps until the next `HH:MM` in local tz, runs `run_once()`, then loops. `_seconds_until_next_run` advances the target by one day whenever it has already passed today, so the first wait after daemon start is up to 24 hours.

## Tunables

Defined as module-level constants near the top of `reconciler.py`. **Read each comment before changing — most have a known noise/coverage tradeoff.**

| Constant | Default | Tradeoff |
|---|---|---|
| `RECENT_WINDOW_HOURS` | `24` | Wider = catches stale issues but slower; the loop's nightly window. |
| `STUCK_EXPORT_HOURS` | `24` | Lower = faster STUCK detection but more false-positives for genuinely slow exports. |
| `FRIGATE_RETENTION_DAYS` | `7` | Must match Frigate's retention. PARTIAL is suppressed for sessions older than this. |
| `PARTIAL_RATIO` | `0.5` | Min `segment_seconds / wall_duration`. Below = PARTIAL. |
| `MIN_FINDING_DURATION_S` | `30` | Runs shorter than this are not considered "runs" at all. |
| `MIN_ORPHAN_DURATION_S` | `21600` (6h) | Only flag ORPHAN runs at the daily-anomaly scale. See [[#Why MIN_ORPHAN_DURATION_S is 6h|note below]]. |
| `SEGMENT_RUN_GAP_S` | `30` | Segments more than this apart start a new run. |

## Finding categories

| Category | Definition | Action |
|---|---|---|
| `ORPHAN` | Continuous Frigate segment runs not covered by any WAL `START` interval. | **Information only**. Frigate's `record.enabled: true` records 24/7 regardless of sessions, so per-minute gaps would flood the report. The 6h floor surfaces only outsized anomalies. Slack alerts intentionally suppress this category. |
| `PARTIAL` | Session with `START + EXPORT_COMPLETE/ABORT` where Frigate segment coverage of `[start, end]` is below `PARTIAL_RATIO`. | Actionable. Recording dropped mid-session. Inspect Frigate logs for the camera in the time window. |
| `STUCK` | `EXPORT_BEGIN` older than `STUCK_EXPORT_HOURS` with no matching `EXPORT_COMPLETE`. Rows with `payload.backfilled == true` are skipped. | Actionable. Likely a Frigate export-API hang. Cross-reference with [[2026-04-08-frigate-export-stuck-and-missing-on-edges\|prior export incidents]]. |
| `DEGRADED` | Session has `START + EXPORT_COMPLETE + ≥ 1 STALL event` between them. | QC flag, not data loss. The export completed but recording stalled at least once. May indicate Pi or camera health issues. |

### Why `MIN_ORPHAN_DURATION_S` is 6h

The first dry-run (no orphan threshold) reported **25 ORPHANs** across 7 days. Tracing one: WAL session `8f2b89a1` (Diane, May 20 16:37:15 KST → May 22 18:35:06 KST per [[2026-05-20|2026-05-20]]) covered her actual recording window correctly. The reported ORPHANs were *other* continuous Frigate segment runs outside Diane's session — Frigate keeps recording whenever it's running, regardless of whether a daemon-tracked session exists.

A 6h floor drops normal background continuity from the report while keeping it as a canary for unbounded multi-day continuous runs (which would suggest a deeper problem). If the daemon ever owns Frigate's `record.enabled` toggle ([[#Future direction|see below]]), reset this threshold to `MIN_FINDING_DURATION_S` since every recording would then map to a session.

## Output surface

### Python (in-process)

```python
findings = reconciler.run_once(window_hours=24)
# {
#   "ts": <float>,
#   "window_hours": 24,
#   "window_start": <float>,
#   "orphans": [{"camera", "start_ts", "end_ts", "duration_seconds"}, ...],
#   "partials": [{"session_id", "camera", "mouse_id", "started_at", "ended_at",
#                 "wall_duration_seconds", "segment_seconds", "coverage_ratio"}, ...],
#   "stucks":   [{"session_id", "camera", "started_export_at", "age_hours"}, ...],
#   "degradeds":[{"session_id", "camera", "mouse_id", "started_at", "stall_count"}, ...],
#   "summary":  {"orphan_count", "partial_count", "stuck_count", "degraded_count"},
# }
```

`reconciler.get_last_findings()` returns a shallow copy of the most recent run's findings or `None`.

### HTTP

```http
GET  /api/reconciler/last                      -> findings dict, 404 if never run
POST /api/reconciler/run?window_hours=N       -> synchronous run + findings
```

Both return `503` if the reconciler hasn't been wired by `init_api()`.

### MQTT

```
topic:   neurosurveillance/reconciler/findings
payload: {"ts": <float>, "window_hours": <int>,
          "orphan_count": <int>, "partial_count": <int>,
          "stuck_count": <int>, "degraded_count": <int>}
qos:     1 (publish via FrigateController.publish — same default QoS)
```

The payload is intentionally compact: scalars only, no arrays. The detail stays on `/api/reconciler/last` so Netdata's MQTT collector and Slack's webhook stay parseable. Subscribers wanting the per-finding detail call the API.

### CLI

```bash
/opt/neurosurveillance/venv/bin/python reconciler.py \
    --since 24h --dry-run --json
```

CLI mode skips MQTT publish (no `mqtt_publish` callable is wired) and exits after one pass. Flags:

| Flag | Default | Meaning |
|---|---|---|
| `--wal` | `/opt/neurosurveillance/session_wal.db` | Path to the WAL DB |
| `--frigate-db` | `/srv/frigate/storage/frigate.db` | Path to Frigate's recordings DB |
| `--since` | `24h` | Window — accepts `Xh` or `Xd` |
| `--dry-run` | off | Cosmetic — already the standalone behavior. Reserved for future "print but skip MQTT" parity. |
| `--json` | off | Emit findings as JSON to stdout |
| `--tz` | `Asia/Seoul` | TZ name |

## Wiring summary

| Where | What |
|---|---|
| `daemon.py` `__init__` | Instantiates `Reconciler` with config + `frigate.publish` callback + `ZoneInfo(tz_name)`. |
| `daemon.py` `start()` | `self.reconciler.start()` after `watchdog.start()`. |
| `daemon.py` `stop()` | `self.reconciler.stop()` after `watchdog.stop()`. |
| `api.py` `init_api()` | Accepts `reconciler` kwarg into the `_reconciler` module global. |
| `api.py` endpoints | `/api/reconciler/last` (GET), `/api/reconciler/run` (POST) — both return JSON. |

## Failure semantics

- **WAL read failure** (DB locked, permissions, missing) — the run logs `Reconciler tick failed: …` and the thread sleeps to the next scheduled time. Last findings stay stale until the next successful run. Acceptable since the daemon log carries the failure.
- **Frigate DB read failure** — same path. The reconciler retries next cycle.
- **MQTT publish failure** — logged, swallowed. The findings dict is still returned to in-process callers and the cached `_last_findings` is still set.
- **Daemon shutdown during a run** — `_stop.wait(sleep_for)` returns `True` immediately; the thread exits. An in-flight `run_once()` completes (sub-second) so no findings are lost.
- **Schema mismatch** (e.g. Frigate adds a column we don't expect) — the reconciler reads only `start_time`, `end_time`, `camera`, `path` from `recordings`, and `ts, event_type, session_id, camera, mouse_id, payload_json` from `events`. New columns are silently ignored.

## Operational notes

### Inspecting findings live

```bash
# Last run's results
curl -s http://127.0.0.1:8585/api/reconciler/last | python3 -m json.tool

# Ad-hoc 24h run
curl -s -X POST 'http://127.0.0.1:8585/api/reconciler/run?window_hours=24' \
    | python3 -m json.tool

# Or via CLI (does not write to MQTT)
/opt/neurosurveillance/venv/bin/python /opt/neurosurveillance/session-daemon/reconciler.py \
    --since 7d --json | jq '.summary'
```

### Subscribing to the MQTT topic

```bash
docker exec mosquitto mosquitto_sub \
    -u nvr -P "$(grep '^password' /opt/neurosurveillance/config.yaml | awk '{print $2}')" \
    -t 'neurosurveillance/reconciler/findings' -v
```

(The Mosquitto auth password is in [[production-values#Mosquitto MQTT Authentication (since 2026-05-22)|production-values]].)

### When the schedule changes

- Daemon restart picks up new `reconciler.scheduled_hour` / `scheduled_minute` / `window_hours` from `config.yaml`.
- The thread logs `Reconciler next run in N minutes (at HH:MM Asia/Seoul)` on every wake-up; verify the value after a config change.

### Per-run timing

Sub-second on the current 60 k-segment Frigate DB. Should stay sub-second as the DB grows since both queries are time-bound (`start_time BETWEEN ? AND ?`). If runs ever exceed 30 s, add an index hint or split per-camera queries.

## Future direction

- **Couple Frigate `record.enabled` to session lifecycle.** Currently Frigate records 24/7, which makes ORPHAN structurally noisy. If the daemon owned this toggle, `MIN_ORPHAN_DURATION_S` could collapse to `MIN_FINDING_DURATION_S` (30 s) and ORPHAN would become actionable. Council previously flagged the toggle as off-limits ([[2026-05-23#Future considerations & optimizations|see 2026-05-23 future considerations]] — investigated before, breaks Frigate). Not on the table.
- **Daemon uptime tracking.** Adding `BOOT` and `SHUTDOWN` event types to the WAL would let the reconciler scope ORPHAN detection to daemon-up windows, sidestepping the Frigate-side coupling problem. Cheaper than the previous bullet. Decide after observing 1 week of reconciler output.
- **Persist findings to the WAL.** Today findings live only in memory + MQTT. Adding a `findings` table or `RECONCILE` event type would give findings the same crash-safety the lifecycle events have. Worth considering once we see organic non-zero findings.
- **Frontend integration.** A small badge in the header reading `/api/reconciler/last` every 30 s, color-coded by `partial_count + stuck_count + degraded_count`. Mirrors the existing storage badge pattern.

## See also

- [[session-journal|Session Journal — golden config]] (the input data)
- [[architecture|Session Daemon — architecture]] (where the reconciler fits)
- [[2026-05-24|2026-05-24]] — implementation journal
- [[2026-05-20|2026-05-20]] — sprint plan + Stage 2.2 origin
