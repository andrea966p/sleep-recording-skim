#!/usr/bin/env python3
"""Bridge NVR operational MQTT alert topics to Slack.

Netdata has no MQTT collector, so this small standalone service forwards the
daemon's MQTT alert topics to the shared Slack incoming-webhook. It is
deliberately decoupled from the session daemon: a daemon crash is itself an
alert condition, and this bridge must keep running to report it.

It subscribes through the mosquitto *container* (`docker exec`) because
mosquitto-clients is not installed on the host. systemd restarts the unit if
the broker container restarts and kills the exec'd subscriber.

Configuration comes from the environment (see deploy/nvr-mqtt-slack.env.example,
installed at /etc/nvr-mqtt-slack.env, mode 0600):

    NVR_MQTT_PASSWORD   broker password for user 'nvr' (auth on since 2026-05-22)
    SLACK_WEBHOOK_URL   Slack incoming-webhook URL (shared with Netdata/Uptime Kuma)

Currently forwarded:
    neurosurveillance/watchdog/+/stall    -> always alert (4.1)

Reserved for 4.6 (enable only after the 3-night reconciler dry-run, ~2026-05-27):
    neurosurveillance/reconciler/findings -> alert only when
        partial_count + stuck_count + degraded_count > 0  (orphan_count suppressed,
        per the reconciler design rationale — Frigate's record.enabled:true makes
        ORPHAN structurally noisy).
"""
import json
import os
import subprocess
import sys
import urllib.request

MQTT_USER = "nvr"
MOSQUITTO_CONTAINER = "mosquitto"

# Topics this bridge subscribes to. Add the reconciler topic here for 4.6.
TOPICS = [
    "neurosurveillance/watchdog/+/stall",
    # "neurosurveillance/reconciler/findings",  # TODO(4.6): enable after dry-run
]


def post_slack(text: str) -> None:
    """POST a Slack message; log to stderr on failure (never crash the loop)."""
    webhook = os.environ["SLACK_WEBHOOK_URL"]
    data = json.dumps({"text": text}).encode()
    req = urllib.request.Request(
        webhook, data=data, headers={"Content-Type": "application/json"}
    )
    try:
        urllib.request.urlopen(req, timeout=10)
    except Exception as e:  # noqa: BLE001 — alerting must not take the bridge down
        print(f"slack post failed: {e}", file=sys.stderr, flush=True)


def format_stall(topic: str, payload: dict) -> str:
    parts = topic.split("/")
    camera = payload.get("camera") or (parts[2] if len(parts) >= 3 else "?")
    lag = payload.get("lag_seconds")
    lag_str = f" lag={lag:.0f}s" if isinstance(lag, (int, float)) else ""
    last_ts = payload.get("last_segment_ts")
    detail = (
        "no segments since recording started"
        if last_ts is None
        else "last segment present"
    )
    session = payload.get("session_id")
    session_str = f" (session {str(session)[:8]})" if session else ""
    return (
        f":rotating_light: *NVR recording STALL* — `{camera}`{lag_str}"
        f"{session_str} — {detail}. Check the Pi / go2rtc for that camera."
    )


def handle(topic: str, payload_raw: str) -> None:
    try:
        payload = json.loads(payload_raw)
    except (ValueError, TypeError):
        payload = {}
    if "/watchdog/" in topic and topic.endswith("/stall"):
        post_slack(format_stall(topic, payload))
    # TODO(4.6): elif topic == "neurosurveillance/reconciler/findings": ...


def main() -> int:
    password = os.environ["NVR_MQTT_PASSWORD"]
    sub_args = ["-u", MQTT_USER, "-P", password, "-v"]
    for t in TOPICS:
        sub_args += ["-t", t]
    cmd = ["docker", "exec", MOSQUITTO_CONTAINER, "mosquitto_sub", *sub_args]

    print(f"nvr-mqtt-slack: subscribing to {TOPICS}", file=sys.stderr, flush=True)
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, text=True)
    if proc.stdout is None:
        return 1
    # mosquitto_sub -v prints "<topic> <payload>" per line.
    for line in proc.stdout:
        line = line.rstrip("\n")
        if not line:
            continue
        topic, _, payload_raw = line.partition(" ")
        try:
            handle(topic, payload_raw)
        except Exception as e:  # noqa: BLE001
            print(f"handler error for {topic!r}: {e}", file=sys.stderr, flush=True)
    return proc.wait()


if __name__ == "__main__":
    sys.exit(main())
