#!/usr/bin/env bash
# nvr-notify.sh — push a message to the lab's phone via ntfy.
#
# The recipient URL is NOT stored here. It is read at runtime from
# /etc/netdata/health_alarm_notify.conf, which is world-readable and is already
# the source of truth for Netdata and Uptime Kuma. Keeping one copy means there
# is one place to rotate it.
#
# Usage:  nvr-notify.sh <level> <title> <body>
#   level: ok | warn | fail | info   (chooses priority + tag only)
#
# Never fails loudly: a broken notifier must not take down the job that called
# it. Returns 0 always; writes its own trouble to stderr.
#
# > [!history] Historical note (pre-2026-09-20)
# > This posted to a Slack webhook. Moved to ntfy so script alerts land in the
# > same place Netdata and Uptime Kuma already push (since 2026-09-14) instead of
# > a separate Slack DM. The Slack webhook is still live in the netdata config;
# > set NVR_NOTIFY_SLACK=1 to fall back to it.
set -uo pipefail

LEVEL="${1:-info}"; TITLE="${2:-(no title)}"; BODY="${3:-}"
NETDATA_CONF="/etc/netdata/health_alarm_notify.conf"

# ntfy has no emoji field; it renders Tags as emoji and uses Priority for the
# phone's alert behaviour. max = bypasses Do Not Disturb, which is what a failed
# backup deserves and a routine success does not.
case "$LEVEL" in
  ok)   PRIORITY="low";     TAGS="white_check_mark" ;;
  warn) PRIORITY="high";    TAGS="warning"          ;;
  fail) PRIORITY="max";     TAGS="rotating_light"   ;;
  *)    PRIORITY="default"; TAGS="information_source" ;;
esac

# Full URL, never a bare topic. This netdata build passes ${recipient} straight
# to curl as the request URL, so a bare topic name becomes a hostname lookup and
# fails silently with no visible config error. See monitoring-setup.md §8.3b.
NTFY="${NTFY_URL:-}"
if [[ -z "$NTFY" && -r "$NETDATA_CONF" ]]; then
  NTFY="$(grep -oP '^\s*DEFAULT_RECIPIENT_NTFY="\K[^"]+' "$NETDATA_CONF" | head -1)"
fi
if [[ -z "$NTFY" ]]; then
  echo "nvr-notify: no ntfy URL available, message dropped: $TITLE" >&2
  exit 0
fi
if [[ "$NTFY" != http*://* ]]; then
  echo "nvr-notify: recipient is not a full URL ('$NTFY'), message dropped: $TITLE" >&2
  exit 0
fi

TS="$(date '+%Y-%m-%d %H:%M:%S %Z')"
BODY_FULL="$(hostname) · ${TS}
${BODY}"

for attempt in 1 2 3; do
  # --data-binary, not --data: --data strips newlines and the body is multi-line.
  if curl -fsS -m 15 \
          -H "Title: ${TITLE}" \
          -H "Priority: ${PRIORITY}" \
          -H "Tags: ${TAGS}" \
          --data-binary "$BODY_FULL" \
          "$NTFY" >/dev/null 2>&1; then
    exit 0
  fi
  sleep $(( attempt * 3 ))
done
echo "nvr-notify: all 3 ntfy attempts failed for: $TITLE" >&2

# Opt-in Slack fallback, off by default. The webhook is still live in the
# netdata config even though SEND_SLACK="NO" disables netdata's own use of it.
if [[ "${NVR_NOTIFY_SLACK:-0}" == "1" ]]; then
  WEBHOOK="${SLACK_WEBHOOK_URL:-}"
  if [[ -z "$WEBHOOK" && -r "$NETDATA_CONF" ]]; then
    WEBHOOK="$(grep -oP '^\s*SLACK_WEBHOOK_URL="\K[^"]+' "$NETDATA_CONF" | head -1)"
  fi
  if [[ -n "$WEBHOOK" ]]; then
    TEXT="*${TITLE}*
${BODY_FULL}"
    PAYLOAD="$(TEXT="$TEXT" python3 -c 'import json,os; print(json.dumps({"text": os.environ["TEXT"]}))')"
    curl -fsS -m 15 -X POST -H 'Content-type: application/json' \
         --data "$PAYLOAD" "$WEBHOOK" >/dev/null 2>&1 \
      && echo "nvr-notify: delivered via Slack fallback" >&2
  fi
fi
exit 0
