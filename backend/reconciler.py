"""Nightly reconciler — cross-check the WAL session journal against Frigate's
recordings DB to surface drift between intent (sessions started) and reality
(segments on disk + exports completed).

Findings categories:

  ORPHAN   — Frigate recording segments not covered by any WAL START.
             Continuous runs of segments are emitted as one finding per
             uncovered run, not per segment. NOTE: Frigate's config keeps
             ``record.enabled: true`` so it records 24/7 regardless of
             daemon-tracked sessions. That means there is always *some*
             ORPHAN time between sessions — it is not by itself a bug. We
             keep the finding category as a canary for unexpectedly long
             continuous runs (filtered by MIN_ORPHAN_DURATION_S, default 6h)
             rather than per-minute background noise. The Slack alerting
             path (Phase 3.4) suppresses ORPHAN counts intentionally.
  PARTIAL  — Session has a START + close event (EXPORT_COMPLETE or ABORT) in
             the WAL, but Frigate's segment coverage over [start, end] is below
             PARTIAL_RATIO. Suggests recording dropped mid-session.
  STUCK    — EXPORT_BEGIN row older than STUCK_EXPORT_HOURS without a matching
             EXPORT_COMPLETE. Backfilled rows are skipped (no EXPORT_BEGIN was
             ever written for backfilled history, so this is defensive).
  DEGRADED — Session completed (START + EXPORT_COMPLETE) but had at least one
             STALL event between them. QC flag — data may be lower-quality
             than the export status suggests.

The reconciler runs on a background thread, sleeping until the next
SCHEDULED_HOUR:SCHEDULED_MINUTE local time. It can also be invoked directly
via run_once() for ad-hoc / API-triggered runs.

CLI usage (smoke test or manual run):

    /opt/neurosurveillance/venv/bin/python reconciler.py \\
        --since 24h --dry-run --json
"""

import argparse
import json
import logging
import sqlite3
import sys
import threading
import time
from datetime import datetime, timedelta
from typing import Callable, Optional

try:
    from zoneinfo import ZoneInfo
except ImportError:  # pragma: no cover — Python < 3.9 not supported anyway
    ZoneInfo = None  # type: ignore

logger = logging.getLogger(__name__)

# Schedule defaults (overridable via constructor).
SCHEDULED_HOUR = 0
SCHEDULED_MINUTE = 1
DEFAULT_TZ = "Asia/Seoul"

# Tunables. Conservative defaults so the first few nights produce a low noise
# floor; sharpen as we learn from the first real findings.
RECENT_WINDOW_HOURS = 24       # how far back nightly scan looks
STUCK_EXPORT_HOURS = 24        # EXPORT_BEGIN this old with no end → STUCK
FRIGATE_RETENTION_DAYS = 7     # PARTIAL is skipped for sessions older than this
PARTIAL_RATIO = 0.5            # MIN actual_segment_seconds / wall_duration
MIN_FINDING_DURATION_S = 30    # Min duration considered a "run" at all
MIN_ORPHAN_DURATION_S = 21600  # Only flag ORPHAN runs ≥ 6h (record.enabled=true
                                # produces continuous background segments that
                                # would otherwise dominate every nightly run).
SEGMENT_RUN_GAP_S = 30         # segments more than this apart = new run


class Reconciler:
    """Background-thread reconciler. Read-only against both SQLite files."""

    def __init__(
        self,
        journal_db_path: str,
        frigate_db_path: str,
        tz=None,
        mqtt_publish: Optional[Callable[[str, str], None]] = None,
        scheduled_hour: int = SCHEDULED_HOUR,
        scheduled_minute: int = SCHEDULED_MINUTE,
        window_hours: int = RECENT_WINDOW_HOURS,
    ):
        self.journal_db = journal_db_path
        self.frigate_db = frigate_db_path
        self.tz = tz if tz is not None else (
            ZoneInfo(DEFAULT_TZ) if ZoneInfo is not None else None
        )
        self._publish = mqtt_publish
        self.scheduled_hour = scheduled_hour
        self.scheduled_minute = scheduled_minute
        self.window_hours = window_hours

        self._stop = threading.Event()
        self._thread: Optional[threading.Thread] = None
        self._lock = threading.Lock()
        self._last_findings: Optional[dict] = None
        self._last_run_at: Optional[float] = None

    # ----- lifecycle -----

    def start(self):
        if self._thread is not None and self._thread.is_alive():
            return
        self._stop.clear()
        self._thread = threading.Thread(
            target=self._loop, daemon=True, name="reconciler",
        )
        self._thread.start()
        tz_label = self.tz.key if self.tz is not None else "naive"
        logger.info(
            "Reconciler started (scheduled %02d:%02d %s, window=%dh)",
            self.scheduled_hour, self.scheduled_minute, tz_label,
            self.window_hours,
        )

    def stop(self):
        self._stop.set()
        if self._thread:
            self._thread.join(timeout=5.0)

    # ----- public read-side -----

    def get_last_findings(self) -> Optional[dict]:
        """Return the most recent run's findings, or None if not yet run."""
        with self._lock:
            return None if self._last_findings is None else dict(self._last_findings)

    # ----- main loop -----

    def _seconds_until_next_run(self, now: datetime) -> float:
        target = now.replace(
            hour=self.scheduled_hour,
            minute=self.scheduled_minute,
            second=0,
            microsecond=0,
        )
        if target <= now:
            target = target + timedelta(days=1)
        return (target - now).total_seconds()

    def _loop(self):
        while not self._stop.is_set():
            now = datetime.now(self.tz) if self.tz else datetime.now()
            sleep_for = self._seconds_until_next_run(now)
            logger.info(
                "Reconciler next run in %.1f minutes (at %02d:%02d %s)",
                sleep_for / 60, self.scheduled_hour, self.scheduled_minute,
                self.tz.key if self.tz else "local",
            )
            if self._stop.wait(sleep_for):
                return
            try:
                self.run_once()
            except Exception as e:
                logger.exception("Reconciler tick failed: %s", e)

    # ----- single-shot run -----

    def run_once(self, window_hours: Optional[int] = None) -> dict:
        """Execute one reconciliation pass and return the findings dict.

        Safe to call from any thread — does not mutate shared state beyond
        ``_last_findings`` (locked).
        """
        window = window_hours if window_hours is not None else self.window_hours
        now = time.time()
        window_start = now - (window * 3600)

        # STUCK lookback needs to reach past the STUCK threshold even when the
        # nightly window itself is short. Without this, a STUCK from 25h ago
        # gets missed on a 24h-window run.
        stuck_lookback = now - (STUCK_EXPORT_HOURS + 24) * 3600
        events = self._read_wal_events(since=min(window_start, stuck_lookback))
        wal_by_session = self._group_by_session(events)

        retention_cutoff = now - (FRIGATE_RETENTION_DAYS * 86400)

        findings: dict = {
            "ts": now,
            "window_hours": window,
            "window_start": window_start,
            "orphans": [],
            "partials": [],
            "stucks": [],
            "degradeds": [],
        }

        # PARTIAL — sessions closed within the window with poor segment coverage
        for sid, evts in wal_by_session.items():
            start_evt = self._first_of(evts, "START")
            if start_evt is None:
                continue
            if start_evt["ts"] < max(window_start, retention_cutoff):
                continue
            end_evt = (
                self._first_of(evts, "EXPORT_COMPLETE")
                or self._first_of(evts, "ABORT")
            )
            if end_evt is None:
                continue  # still in flight; not a PARTIAL yet
            wall_duration = end_evt["ts"] - start_evt["ts"]
            if wall_duration < 5:
                continue
            camera = start_evt.get("camera")
            if not camera:
                continue

            segment_seconds = self._sum_frigate_segments(
                camera, start_evt["ts"], end_evt["ts"],
            )
            ratio = segment_seconds / wall_duration if wall_duration > 0 else 0.0
            if ratio < PARTIAL_RATIO:
                findings["partials"].append({
                    "session_id": sid,
                    "camera": camera,
                    "mouse_id": start_evt.get("mouse_id"),
                    "started_at": start_evt["ts"],
                    "ended_at": end_evt["ts"],
                    "wall_duration_seconds": round(wall_duration, 1),
                    "segment_seconds": round(segment_seconds, 1),
                    "coverage_ratio": round(ratio, 3),
                })

        # STUCK — EXPORT_BEGIN > STUCK_EXPORT_HOURS without EXPORT_COMPLETE
        cutoff_stuck = now - (STUCK_EXPORT_HOURS * 3600)
        for sid, evts in wal_by_session.items():
            begin = self._first_of(evts, "EXPORT_BEGIN")
            if begin is None:
                continue
            if begin.get("payload", {}).get("backfilled"):
                continue
            if begin["ts"] >= cutoff_stuck:
                continue
            done = self._first_of(evts, "EXPORT_COMPLETE")
            if done is not None and done["ts"] >= begin["ts"]:
                continue
            findings["stucks"].append({
                "session_id": sid,
                "camera": begin.get("camera"),
                "started_export_at": begin["ts"],
                "age_hours": round((now - begin["ts"]) / 3600, 1),
            })

        # DEGRADED — completed sessions that had at least one STALL
        for sid, evts in wal_by_session.items():
            start_evt = self._first_of(evts, "START")
            done = self._first_of(evts, "EXPORT_COMPLETE")
            stalls = [e for e in evts if e["event_type"] == "STALL"]
            if start_evt and done and stalls:
                if start_evt["ts"] < window_start:
                    continue
                findings["degradeds"].append({
                    "session_id": sid,
                    "camera": start_evt.get("camera"),
                    "mouse_id": start_evt.get("mouse_id"),
                    "started_at": start_evt["ts"],
                    "stall_count": len(stalls),
                })

        # ORPHAN — continuous Frigate segment runs not covered by any START
        findings["orphans"] = self._find_orphans(wal_by_session, window_start, now)

        summary = {
            "orphan_count": len(findings["orphans"]),
            "partial_count": len(findings["partials"]),
            "stuck_count": len(findings["stucks"]),
            "degraded_count": len(findings["degradeds"]),
        }
        findings["summary"] = summary

        with self._lock:
            self._last_findings = findings
            self._last_run_at = now

        logger.info(
            "Reconciler complete: orphans=%d partials=%d stucks=%d degradeds=%d "
            "(window=%dh)",
            summary["orphan_count"], summary["partial_count"],
            summary["stuck_count"], summary["degraded_count"], window,
        )

        # Publish a compact summary. Detail stays in the API response /
        # last_findings — MQTT payload kept small so Netdata/Slack stay clean.
        if self._publish is not None:
            try:
                payload = json.dumps({
                    "ts": now,
                    "window_hours": window,
                    **summary,
                })
                self._publish("neurosurveillance/reconciler/findings", payload)
            except Exception as e:
                logger.error("Failed to publish reconciler findings: %s", e)

        return findings

    # ----- helpers -----

    def _read_wal_events(self, since: float) -> list[dict]:
        conn = sqlite3.connect(
            f"file:{self.journal_db}?mode=ro", uri=True, timeout=5.0,
        )
        try:
            rows = conn.execute(
                "SELECT ts, event_type, session_id, camera, mouse_id, payload_json "
                "FROM events WHERE ts >= ? ORDER BY ts ASC",
                (since,),
            ).fetchall()
        finally:
            conn.close()

        out: list[dict] = []
        for ts, et, sid, cam, mouse, payload_json in rows:
            try:
                payload = json.loads(payload_json) if payload_json else {}
            except json.JSONDecodeError:
                payload = {}
            out.append({
                "ts": ts,
                "event_type": et,
                "session_id": sid,
                "camera": cam,
                "mouse_id": mouse,
                "payload": payload,
            })
        return out

    @staticmethod
    def _group_by_session(events: list[dict]) -> dict[str, list[dict]]:
        groups: dict[str, list[dict]] = {}
        for e in events:
            sid = e["session_id"]
            if sid is None:
                continue
            groups.setdefault(sid, []).append(e)
        return groups

    @staticmethod
    def _first_of(events: list[dict], event_type: str) -> Optional[dict]:
        for e in events:
            if e["event_type"] == event_type:
                return e
        return None

    def _sum_frigate_segments(
        self, camera: str, start: float, end: float,
    ) -> float:
        conn = sqlite3.connect(
            f"file:{self.frigate_db}?mode=ro", uri=True, timeout=5.0,
        )
        try:
            rows = conn.execute(
                "SELECT start_time, end_time FROM recordings "
                "WHERE camera = ? AND end_time >= ? AND start_time <= ?",
                (camera, start, end),
            ).fetchall()
        finally:
            conn.close()

        total = 0.0
        for s, e in rows:
            overlap_start = max(s, start)
            overlap_end = min(e, end)
            if overlap_end > overlap_start:
                total += overlap_end - overlap_start
        return total

    def _find_orphans(
        self,
        wal_by_session: dict[str, list[dict]],
        window_start: float,
        now: float,
    ) -> list[dict]:
        # Build per-camera covered intervals from WAL sessions.
        covered: dict[str, list[tuple[float, float]]] = {}
        for evts in wal_by_session.values():
            start_evt = self._first_of(evts, "START")
            if start_evt is None or start_evt.get("camera") is None:
                continue
            end_evt = (
                self._first_of(evts, "EXPORT_COMPLETE")
                or self._first_of(evts, "ABORT")
            )
            cam = start_evt["camera"]
            end_ts = end_evt["ts"] if end_evt else now
            covered.setdefault(cam, []).append((start_evt["ts"], end_ts))

        # Pull all Frigate segments in the window.
        conn = sqlite3.connect(
            f"file:{self.frigate_db}?mode=ro", uri=True, timeout=5.0,
        )
        try:
            rows = conn.execute(
                "SELECT camera, start_time, end_time FROM recordings "
                "WHERE end_time >= ? AND start_time <= ? "
                "ORDER BY camera, start_time",
                (window_start, now),
            ).fetchall()
        finally:
            conn.close()

        # Group consecutive segments into runs per camera.
        by_cam: dict[str, list[tuple[float, float]]] = {}
        for cam, s, e in rows:
            by_cam.setdefault(cam, []).append((s, e))

        orphans: list[dict] = []
        for cam, segs in by_cam.items():
            cam_covered = covered.get(cam, [])
            run_start = run_end = None
            for s, e in segs:
                if run_start is None:
                    run_start, run_end = s, e
                elif s - run_end <= SEGMENT_RUN_GAP_S:
                    run_end = e
                else:
                    self._emit_orphans(
                        orphans, cam, run_start, run_end, cam_covered,
                    )
                    run_start, run_end = s, e
            if run_start is not None:
                self._emit_orphans(
                    orphans, cam, run_start, run_end, cam_covered,
                )

        return orphans

    @staticmethod
    def _emit_orphans(
        out: list[dict],
        cam: str,
        run_start: float,
        run_end: float,
        covered: list[tuple[float, float]],
    ):
        if (run_end - run_start) < MIN_FINDING_DURATION_S:
            return
        # Subtract any intervals that are covered by a WAL session.
        uncovered: list[tuple[float, float]] = [(run_start, run_end)]
        for cs, ce in covered:
            new_uncovered: list[tuple[float, float]] = []
            for us, ue in uncovered:
                if ce <= us or cs >= ue:
                    new_uncovered.append((us, ue))
                    continue
                if cs > us:
                    new_uncovered.append((us, cs))
                if ce < ue:
                    new_uncovered.append((ce, ue))
            uncovered = new_uncovered
        # The MIN_ORPHAN_DURATION_S threshold is intentionally much higher
        # than MIN_FINDING_DURATION_S: with record.enabled=true Frigate is
        # always recording, so per-minute gaps between sessions would flood
        # the report. We only flag runs at the daily-anomaly scale.
        for us, ue in uncovered:
            if (ue - us) >= MIN_ORPHAN_DURATION_S:
                out.append({
                    "camera": cam,
                    "start_ts": us,
                    "end_ts": ue,
                    "duration_seconds": round(ue - us, 1),
                })


# ---------------------------------------------------------------------------
# CLI — `python reconciler.py --since 24h --dry-run --json`
# ---------------------------------------------------------------------------

def _parse_since(spec: str) -> int:
    s = spec.strip().lower()
    if s.endswith("h"):
        return int(s[:-1])
    if s.endswith("d"):
        return int(s[:-1]) * 24
    raise ValueError(f"Invalid --since value: {spec!r} (use e.g. 24h, 7d)")


def main():
    parser = argparse.ArgumentParser(
        description="NeuroSurveillance reconciler — single run, no scheduling.",
    )
    parser.add_argument("--wal", default="/opt/neurosurveillance/session_wal.db")
    parser.add_argument("--frigate-db", default="/srv/frigate/storage/frigate.db")
    parser.add_argument("--since", default="24h",
                        help="Window to scan (24h, 7d, 1h ...)")
    parser.add_argument("--dry-run", action="store_true",
                        help="Do not publish MQTT — print findings only")
    parser.add_argument("--json", action="store_true",
                        help="Emit findings as JSON to stdout")
    parser.add_argument("--tz", default=DEFAULT_TZ)
    args = parser.parse_args()

    try:
        hours = _parse_since(args.since)
    except ValueError as e:
        print(str(e), file=sys.stderr)
        sys.exit(2)

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%H:%M:%S",
    )

    r = Reconciler(
        journal_db_path=args.wal,
        frigate_db_path=args.frigate_db,
        tz=ZoneInfo(args.tz) if ZoneInfo is not None else None,
        mqtt_publish=None,
    )
    findings = r.run_once(window_hours=hours)

    if args.json:
        json.dump(findings, sys.stdout, indent=2, default=str)
        sys.stdout.write("\n")
        return

    s = findings["summary"]
    print(f"Window: last {hours}h ({findings['window_start']:.0f}..{findings['ts']:.0f})")
    print(f"  ORPHAN segment runs : {s['orphan_count']}")
    print(f"  PARTIAL sessions    : {s['partial_count']}")
    print(f"  STUCK exports       : {s['stuck_count']}")
    print(f"  DEGRADED sessions   : {s['degraded_count']}")
    for category in ("orphans", "partials", "stucks", "degradeds"):
        items = findings[category]
        if items:
            print(f"\n=== {category.upper()} ({len(items)}) ===")
            for item in items:
                print(f"  {json.dumps(item, default=str)}")


if __name__ == "__main__":
    main()
