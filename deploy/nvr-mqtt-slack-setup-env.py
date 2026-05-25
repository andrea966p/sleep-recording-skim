#!/usr/bin/env python3
"""Generate /etc/nvr-mqtt-slack.env for nvr-mqtt-slack.service.

Pulls the broker password from the daemon config and the Slack webhook from the
Netdata notify config, so neither secret has to be typed by hand or printed.

Run as root (reads the Netdata config + writes under /etc):

    sudo python3 /opt/neurosurveillance/session-daemon/deploy/nvr-mqtt-slack-setup-env.py

Writes the file mode 0600. Prints only a success line, never the secrets.
"""
import os
import re
import sys

import yaml

CONFIG = "/opt/neurosurveillance/config.yaml"
NETDATA_NOTIFY = "/etc/netdata/health_alarm_notify.conf"
OUT = "/etc/nvr-mqtt-slack.env"


def main() -> int:
    with open(CONFIG) as f:
        cfg = yaml.safe_load(f)
    pw = (cfg.get("mqtt") or {}).get("password")

    hook = ""
    with open(NETDATA_NOTIFY) as f:
        for line in f:
            m = re.match(r'\s*SLACK_WEBHOOK_URL="?([^"\n]+)"?', line)
            if m:
                hook = m.group(1).strip()
                break

    if not pw or not hook:
        print(
            f"ERROR: missing values (password set={bool(pw)}, webhook set={bool(hook)})",
            file=sys.stderr,
        )
        return 1

    os.umask(0o077)
    with open(OUT, "w") as f:
        f.write(f"NVR_MQTT_PASSWORD={pw}\n")
        f.write(f"SLACK_WEBHOOK_URL={hook}\n")
    os.chmod(OUT, 0o600)
    print(f"wrote {OUT} (mode 0600)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
