#!/usr/bin/env bash
# scheduled-recording.sh — start an Allego recording at a wall-clock time,
# unattended, and tell Slack whether it actually worked.
#
# Wraps eeg-emg-analysis/qc/start_recording_at.py, which is the only start path
# that (a) sets split_files_by_port=True and starts every port with channels (radiens-core
# 0.1.2 on Allego 4.1.2, since 2026-10-28; the old raw-gRPC workaround for the broken
# set_recording_config() is gone) and (b) verifies by watching bytes land on disk,
# per port, instead of trusting the client's status.
#
# Usage: scheduled-recording.sh HH:MM[:SS]
#
# Design notes:
#  - Run it a few minutes EARLY. The python script does its own waiting and
#    configures the recorder ahead of the instant, so cron firing at 08:50 for a
#    09:00 target is correct and intentional.
#  - Success is defined as bytes growing on disk. Nothing else counts.
#  - One automatic retry, because a transient gRPC hiccup should not cost a day
#    of animal time.
set -uo pipefail

TARGET="${1:?usage: scheduled-recording.sh HH:MM[:SS]}"
REPO="/home/skimlab/sleep-recording-skim/eeg-emg-analysis"
PY="/opt/neurosurveillance/venv/bin/python3"   # the only interpreter with radiens-core
DEST="/home/skimlab/radix/data"
NOTIFY="/home/skimlab/sleep-recording-skim/neurosurveillance/deploy/nvr-notify.sh"
LOG="/home/skimlab/sleep-recording-skim/neurosurveillance/deploy/logs/recording-$(date +%F).log"
mkdir -p "$(dirname "$LOG")"

log() { echo "[$(date '+%F %T')] $*" | tee -a "$LOG"; }

log "=== scheduled-recording.sh target=$TARGET ==="

# ---- preflight -------------------------------------------------------------
fail_pre() { log "PREFLIGHT FAIL: $1"; "$NOTIFY" fail "Recording NOT started" "Preflight failed: $1
Target was $TARGET. Nothing is recording. Manual action needed."; exit 1; }

[[ -x "$PY" ]] || fail_pre "interpreter $PY missing"
pgrep -f 'allegoserver hardware' >/dev/null || fail_pre "allegoserver is not running"

FREE_GB=$(df --output=avail -BG "$DEST" | tail -1 | tr -dc '0-9')
log "free space: ${FREE_GB} GB"
(( FREE_GB > 150 )) || fail_pre "only ${FREE_GB} GB free on $DEST (need >150)"

# 2026-10-28: radiens-core, compare .name. record_mode is ON if ANY port records. Only an
# explicit OFF lets the start go ahead; ON refuses; anything else (import error, gRPC failure)
# also refuses. (This check was already fail-safe before the port; it still is.)
CUR_MODE=$(cd "$REPO" && PYTHONPATH="$REPO" timeout 60 "$PY" -c "
from radiens_core import AllegoClient
print(AllegoClient().get_status().recording.record_mode.name)" 2>/dev/null | tail -1)
log "current recording mode: ${CUR_MODE:-UNKNOWN}"
[[ "$CUR_MODE" == "ON" ]] && fail_pre "a recording is ALREADY running (some port is ON) — refusing to disturb it"
[[ "$CUR_MODE" == "OFF" ]] || fail_pre "could not query allego status (got '${CUR_MODE:-nothing}')"

# ---- start (with one retry) -------------------------------------------------
attempt_start() {
  cd "$REPO" || return 1
  PYTHONPATH="$REPO" timeout 3600 "$PY" qc/start_recording_at.py "$TARGET" 2>&1 | tee -a "$LOG"
  return "${PIPESTATUS[0]}"
}

OUT=""
for attempt in 1 2; do
  log "start attempt $attempt"
  OUT="$(attempt_start)"
  if grep -q "RECORDING CONFIRMED GROWING" <<<"$OUT"; then
    FNAME=$(grep -oP 'file=\K\S+' <<<"$OUT" | tail -1)
    RATE=$(grep -oP '\(\K[0-9.]+(?= GB/h\))' <<<"$OUT" | tail -1)
    log "SUCCESS file=$FNAME rate=${RATE} GB/h"
    "$NOTIFY" ok "Recording STARTED — 8 mice" "File: \`${FNAME}\`
Growth verified on disk: ${RATE} GB/h
Started at target ${TARGET}. Runs until stopped manually.
Hourly watchdog is now checking that it keeps growing."
    echo "$FNAME" > /home/skimlab/sleep-recording-skim/neurosurveillance/deploy/logs/current-recording.txt
    exit 0
  fi
  log "attempt $attempt did not confirm growth"
  # only retry immediately; the target time has already passed by now
  TARGET="$(date -d '+45 seconds' +%H:%M:%S)"
done

log "BOTH ATTEMPTS FAILED"
# the real Allego mode now, not an assumption (start_recording_at.py stops the ports it started)
END_MODE=$(cd "$REPO" && PYTHONPATH="$REPO" timeout 60 "$PY" -c "
from radiens_core import AllegoClient
print(AllegoClient().get_status().recording.record_mode.name)" 2>/dev/null | tail -1)
log "Allego mode after failure: ${END_MODE:-UNKNOWN}"
"$NOTIFY" fail "Recording FAILED to start" "Two attempts made, neither confirmed bytes growing on disk.
Allego recording mode now: \`${END_MODE:-UNKNOWN}\` (ON means a port may still be recording unverified).
Log: \`$LOG\`
Needs hands-on attention."
exit 1
