#!/usr/bin/env bash
# radix-archive-watchdog.sh — keeps the archive moving without a human.
#
# Runs from cron. If the archive is not COMPLETE and no run currently holds the
# lock, it starts one. That covers every way a run can die: ssh drop, NAS
# reboot, this machine rebooting, the process being killed, a transient network
# fault. The archive script itself is idempotent and resumable, so relaunching
# is always safe.
#
# It is deliberately quiet: it only speaks to Slack when it actually restarts
# something, or when it has been stuck failing for a long time.
set -uo pipefail

DIR="/home/skimlab/Monitoring_project/neurosurveillance/deploy"
LOGS="$DIR/logs"; mkdir -p "$LOGS"
STATE="$LOGS/radix-archive.state"
LOCK="$LOGS/radix-archive.lock"
LOG="$LOGS/radix-archive-watchdog.log"
STRIKES="$LOGS/radix-archive.strikes"
NOTIFY="$DIR/nvr-notify.sh"

log() { echo "[$(date '+%F %T')] $*" >> "$LOG"; }

# Complete: nothing to do, ever again (delete the state file to re-arm).
if [[ -f "$STATE" ]] && grep -q '^COMPLETE' "$STATE"; then
  log "complete; standing down"; exit 0
fi

# A run is in progress if the lock is held.
if [[ -f "$LOCK" ]] && ! flock -n 9 9<"$LOCK" 2>/dev/null; then
  log "run in progress; leaving it alone"
  rm -f "$STRIKES"
  exit 0
fi

# Do not start a run inside the recording window.
HH=$(date +%H); MM=$(date +%M)
if (( 10#$HH >= 8 && 10#$HH < 20 )) && ! { (( 10#$HH == 8 )) && (( 10#$MM < 30 )); }; then
  log "inside the protected recording window; not starting"
  exit 0
fi

n=$(( $( [[ -f "$STRIKES" ]] && cat "$STRIKES" || echo 0 ) + 1 ))
echo "$n" > "$STRIKES"
log "no run in progress and archive incomplete -> starting (restart #$n)"

if (( n == 1 )); then
  "$NOTIFY" info "Archive restarting" "The archive run was not active and the copy is not finished, so the watchdog started it again. Transfers resume from what the NAS already holds, so nothing is repeated."
elif (( n % 6 == 0 )); then
  "$NOTIFY" warn "Archive has restarted $n times" "It keeps stopping before completion. Something is failing repeatedly.
Check \`$LOGS/radix-archive.log\`."
fi

nohup "$DIR/radix-archive.sh" >> "$LOGS/radix-archive-nohup.log" 2>&1 &
log "launched pid $!"
exit 0
