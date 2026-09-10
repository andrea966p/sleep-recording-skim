#!/usr/bin/env bash
# nvr-notify.sh — post a message to the lab Slack.
#
# The webhook is NOT stored here. It is read at runtime from
# /etc/netdata/health_alarm_notify.conf, which is world-readable and is already
# the source of truth for Netdata and Uptime Kuma. Keeping one copy means there
# is one place to rotate it.
#
# Usage:  nvr-notify.sh <level> <title> <body>
#   level: ok | warn | fail | info   (chooses the emoji only)
#
# Never fails loudly: a broken webhook must not take down the job that called
# it. Returns 0 always; writes its own trouble to stderr.
set -uo pipefail

LEVEL="${1:-info}"; TITLE="${2:-(no title)}"; BODY="${3:-}"
NETDATA_CONF="/etc/netdata/health_alarm_notify.conf"

case "$LEVEL" in
  ok)   ICON=":white_check_mark:" ;;
  warn) ICON=":warning:"          ;;
  fail) ICON=":rotating_light:"   ;;
  *)    ICON=":information_source:" ;;
esac

WEBHOOK="${SLACK_WEBHOOK_URL:-}"
if [[ -z "$WEBHOOK" && -r "$NETDATA_CONF" ]]; then
  WEBHOOK="$(grep -oP '^\s*SLACK_WEBHOOK_URL="\K[^"]+' "$NETDATA_CONF" | head -1)"
fi
if [[ -z "$WEBHOOK" ]]; then
  echo "nvr-notify: no webhook available, message dropped: $TITLE" >&2
  exit 0
fi

TS="$(date '+%Y-%m-%d %H:%M:%S %Z')"
TEXT="${ICON} *${TITLE}*
\`$(hostname)\` · ${TS}
${BODY}"

PAYLOAD="$(TEXT="$TEXT" python3 -c 'import json,os; print(json.dumps({"text": os.environ["TEXT"]}))')"

for attempt in 1 2 3; do
  if curl -fsS -m 15 -X POST -H 'Content-type: application/json' \
          --data "$PAYLOAD" "$WEBHOOK" >/dev/null 2>&1; then
    exit 0
  fi
  sleep $(( attempt * 3 ))
done
echo "nvr-notify: all 3 attempts failed for: $TITLE" >&2
exit 0
