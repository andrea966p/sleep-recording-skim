#!/usr/bin/env bash
# recording-watchdog-cron.sh — hourly proof that the live recording is still
# writing bytes, and a Slack alert the moment it is not.
#
# Exists because a recording that starts correctly and then silently stops is the
# documented way runs have been lost here (see the 72 h run, 2026-07). A green
# start is not evidence of a green run.
#
# State lives in logs/current-recording.txt (the filename, written by
# scheduled-recording.sh) and logs/watchdog-lastsize.txt (bytes at last check).
# Removing current-recording.txt disarms the watchdog, which is what a clean
# manual stop does.
set -uo pipefail

DIR="/home/skimlab/Monitoring_project/neurosurveillance/deploy"
LOGS="$DIR/logs"
NOTIFY="$DIR/nvr-notify.sh"
DEST="/home/skimlab/radix/data"
PY="/opt/neurosurveillance/venv/bin/python3"
REPO="/home/skimlab/Monitoring_project/eeg-emg-analysis"
CUR="$LOGS/current-recording.txt"
LAST="$LOGS/watchdog-lastsize.txt"
LOG="$LOGS/watchdog.log"
mkdir -p "$LOGS"
log() { echo "[$(date '+%F %T')] $*" >> "$LOG"; }

# Disarmed: nothing to watch.
[[ -f "$CUR" ]] || { log "disarmed (no current-recording.txt)"; exit 0; }
FNAME="$(tr -d '[:space:]' < "$CUR")"
[[ -n "$FNAME" ]] || { log "empty current-recording.txt"; exit 0; }

FILE="$DEST/${FNAME}_data.xdat"
MODE="$(cd "$REPO" && PYTHONPATH="$REPO" "$PY" -c "
from radiens.allego_client import AllegoClient
print(AllegoClient().get_status().recording.mode)" 2>/dev/null | tail -1)"

NOW_SIZE=$( [[ -f "$FILE" ]] && stat -c %s "$FILE" || echo -1 )
PREV_SIZE=$( [[ -f "$LAST" ]] && cat "$LAST" || echo -1 )
echo "$NOW_SIZE" > "$LAST"
FREE_GB=$(df --output=avail -BG "$DEST" | tail -1 | tr -dc '0-9')
GB=$(python3 -c "print(f'{$NOW_SIZE/1e9:.1f}')" 2>/dev/null || echo '?')
log "mode=$MODE size=$NOW_SIZE prev=$PREV_SIZE free=${FREE_GB}G"

# --- recorder reports stopped -------------------------------------------------
if [[ "$MODE" != "R_ON" ]]; then
  "$NOTIFY" warn "Recording has STOPPED" "File: \`${FNAME}\` — final size ${GB} GB
Recorder mode is \`${MODE:-unreachable}\`.
If you stopped it yourself, nothing to do. If you did not, the run ended on its own.
Watchdog is now disarmed and will stop reporting."
  rm -f "$CUR" "$LAST"
  log "disarmed after stop"
  exit 0
fi

# --- running but not growing = the silent failure mode -----------------------
if (( NOW_SIZE >= 0 && PREV_SIZE >= 0 && NOW_SIZE <= PREV_SIZE )); then
  "$NOTIFY" fail "Recording STALLED — mode says R_ON but no new bytes" "File: \`${FNAME}\`
Size unchanged at ${GB} GB across a full hour while the recorder claims R_ON.
This is the silent-failure signature. Needs hands-on attention."
  log "STALL detected"
  exit 1
fi

# --- disk pressure ------------------------------------------------------------
if (( FREE_GB < 150 )); then
  "$NOTIFY" warn "Disk low during recording" "Only ${FREE_GB} GB free on \`${DEST}\` while recording \`${FNAME}\` (${GB} GB so far).
The 775 GB archive copy is still present on this machine; deleting it once verified frees that space."
fi

log "OK growing"
exit 0
