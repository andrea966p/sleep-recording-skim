#!/usr/bin/env bash
# radix-archive.sh — copy ~/radix/data (the raw Allego .xdat recordings) to the
# NAS, verifiably, resumably, and without ever endangering a live recording.
#
# WHY THIS EXISTS
#   The nightly nas-backup.sh deliberately excludes bulk data, so ~775 GB of raw
#   electrophysiology has never been backed up anywhere. This is the only copy.
#
# WHAT IT GUARANTEES
#   - Every file is verified by sha256 on BOTH ends before being called done.
#     A file is only renamed into place after its checksum matches.
#   - Interruptions are free: transfers resume byte-wise from what the NAS
#     already holds, so a killed run loses seconds, not hours.
#   - It will not compete with the rig. If a recording is running it backs off,
#     and it stops entirely before the morning recording window.
#   - It never deletes anything on this machine. Ever. Deleting the local copy
#     is a human decision, taken after reading the completion report.
#
# STATE
#   logs/radix-archive.manifest  TSV: name <TAB> size <TAB> sha256 <TAB> status
#   A file is re-verified if its local size changes.
#
# Usage: radix-archive.sh [--verify-only]
set -uo pipefail

SRC="/home/skimlab/radix/data"
NAS="Andrea@bilab-syn.tail8808c0.ts.net"
NAS_PORT="53"
NAS_DIR="/volume1/homes/Andrea/e10_radix_archive/data"
KEY="/home/skimlab/.ssh/id_ed25519"
DIR="/home/skimlab/Monitoring_project/neurosurveillance/deploy"
LOGS="$DIR/logs"; mkdir -p "$LOGS"
MANIFEST="$LOGS/radix-archive.manifest"
LOG="$LOGS/radix-archive.log"
LOCK="$LOGS/radix-archive.lock"
NOTIFY="$DIR/nvr-notify.sh"
REPO="/home/skimlab/Monitoring_project/eeg-emg-analysis"
PY="/opt/neurosurveillance/venv/bin/python3"

# Stop well before the 09:00 recording so we are never reading the disk hard
# while the amplifiers are writing to it.
HARD_STOP="08:30"
MAX_RETRIES=3

SSH=(ssh -i "$KEY" -p "$NAS_PORT" -o BatchMode=yes -o StrictHostKeyChecking=accept-new
     -o ConnectTimeout=30 -o ServerAliveInterval=15 -o ServerAliveCountMax=4 "$NAS")

log() { echo "[$(date '+%F %T')] $*" | tee -a "$LOG"; }

# ---- single instance --------------------------------------------------------
exec 9>"$LOCK"
if ! flock -n 9; then
  log "another run holds the lock; exiting"
  exit 0
fi

# ---- guards -----------------------------------------------------------------
# 10# forces base 10. Without it `date +%H` returns "08"/"09", bash reads them as
# octal, and the test ERRORS OUT instead of firing — which is exactly what happened
# on 2026-08-19, leaving the 08:30 guard inoperative.
past_hard_stop() {
  local hh mm now
  hh=$((10#$(date +%H))); mm=$((10#$(date +%M)))
  now=$(( hh*60 + mm ))
  (( now >= 8*60+30 && hh < 20 ))
}

recording_active() {
  local m
  m=$(cd "$REPO" && PYTHONPATH="$REPO" timeout 30 "$PY" -c "
from radiens.allego_client import AllegoClient
print(AllegoClient().get_status().recording.mode)" 2>/dev/null | tail -1)
  [[ "$m" == "R_ON" ]]
}

human() { python3 -c "print(f'{$1/1e9:.1f} GB')" 2>/dev/null || echo "$1 B"; }

# ---- manifest helpers -------------------------------------------------------
touch "$MANIFEST"
manifest_status() {  # name size -> DONE if recorded at that exact size
  awk -F'\t' -v n="$1" -v s="$2" '$1==n && $2==s && $4=="DONE"{print "DONE"; exit}' "$MANIFEST"
}
manifest_put() { printf '%s\t%s\t%s\t%s\t%s\n' "$1" "$2" "$3" "$4" "$(date '+%F %T')" >> "$MANIFEST"; }

# ---- prepare remote ---------------------------------------------------------
if ! "${SSH[@]}" "mkdir -p '$NAS_DIR'" 2>>"$LOG"; then
  log "FATAL: cannot reach NAS or create $NAS_DIR"
  "$NOTIFY" fail "Archive cannot start" "Could not reach the NAS or create \`$NAS_DIR\`.
Nothing was transferred. See \`$LOG\`."
  exit 1
fi

mapfile -t FILES < <(cd "$SRC" && ls -1 2>/dev/null | sort)
TOTAL_FILES=${#FILES[@]}
TOTAL_BYTES=$(du -sb "$SRC" | cut -f1)
log "=== radix-archive start: $TOTAL_FILES files, $(human "$TOTAL_BYTES") ==="

if recording_active; then
  log "a recording is live — deferring entirely (no files touched)"
  echo "DEFERRED $(date '+%F %T')" > "$LOGS/radix-archive.state"
  exit 0
fi

START_TS=$(date +%s)
done_files=0; done_bytes=0; failed_files=0; skipped=0
FAILED_LIST=""

for name in "${FILES[@]}"; do
  src="$SRC/$name"
  [[ -f "$src" ]] || continue

  if past_hard_stop; then
    log "HARD STOP ($HARD_STOP) reached — pausing before the recording window"
    "$NOTIFY" warn "Archive paused for the recording window" "Stopped at $HARD_STOP so the 09:00 recording has the disk to itself.
Progress: $done_files/$TOTAL_FILES files, $(human $done_bytes) transferred.
It resumes automatically tonight; nothing is lost."
    exit 0
  fi

  # A recording that starts mid-run means we stop, not churn. Sleeping per file
  # would idle for ~21 h across the file list and then report INCOMPLETE to Slack
  # once per pass for the whole length of the recording.
  if recording_active; then
    log "recording started — deferring the rest of the run, will resume when it ends"
    echo "DEFERRED $(date '+%F %T')" > "$LOGS/radix-archive.state"
    exit 0
  fi

  size=$(stat -c %s "$src")

  if [[ -n "$(manifest_status "$name" "$size")" ]]; then
    skipped=$((skipped+1)); done_bytes=$((done_bytes+size)); done_files=$((done_files+1))
    continue
  fi

  ok=0
  for try in $(seq 1 $MAX_RETRIES); do
    remote_have=$("${SSH[@]}" "stat -c %s '$NAS_DIR/$name.part' 2>/dev/null || echo 0" 2>/dev/null | tr -dc '0-9')
    remote_have=${remote_have:-0}
    if (( remote_have > size )); then
      log "$name: remote .part larger than source — discarding and restarting"
      "${SSH[@]}" "rm -f '$NAS_DIR/$name.part'"; remote_have=0
    fi

    if (( remote_have == size )); then
      log "$name: bytes already present, verifying"
    else
      log "$name: sending from offset $remote_have of $size ($(human $((size-remote_have))) to go), try $try"
      # nice/ionice so the rig always wins any disk contention
      if ! ionice -c3 nice -n 19 dd if="$src" bs=4M skip="$remote_have" iflag=skip_bytes status=none \
           | "${SSH[@]}" "cat >> '$NAS_DIR/$name.part'" 2>>"$LOG"; then
        log "$name: transfer error on try $try"
        sleep $((try*15)); continue
      fi
    fi

    local_sha=$(ionice -c3 nice -n 19 sha256sum "$src" | cut -d' ' -f1)
    remote_sha=$("${SSH[@]}" "sha256sum '$NAS_DIR/$name.part' 2>/dev/null | cut -d' ' -f1" 2>/dev/null | tr -dc '0-9a-f')

    if [[ -n "$local_sha" && "$local_sha" == "$remote_sha" ]]; then
      "${SSH[@]}" "mv -f '$NAS_DIR/$name.part' '$NAS_DIR/$name'"
      manifest_put "$name" "$size" "$local_sha" "DONE"
      done_files=$((done_files+1)); done_bytes=$((done_bytes+size))
      log "$name: VERIFIED ($(human $size)) [$done_files/$TOTAL_FILES]"
      ok=1; break
    fi

    log "$name: CHECKSUM MISMATCH (local=${local_sha:0:12} remote=${remote_sha:0:12}) — discarding remote, try $try"
    "${SSH[@]}" "rm -f '$NAS_DIR/$name.part'"
    sleep $((try*15))
  done

  if (( ok == 0 )); then
    failed_files=$((failed_files+1)); FAILED_LIST+="
  - $name ($(human $size))"
    manifest_put "$name" "$size" "-" "FAILED"
    log "$name: GAVE UP after $MAX_RETRIES tries"
  fi
done

ELAPSED=$(( $(date +%s) - START_TS ))
SUMMARY="Files verified on NAS: $done_files of $TOTAL_FILES  (already done: $skipped)
Data: $(human $done_bytes) of $(human $TOTAL_BYTES)
Elapsed: $((ELAPSED/60)) min
Destination: \`$NAS_DIR\`
Every file matched sha256 on both ends before being counted."

if (( failed_files == 0 && done_files == TOTAL_FILES )); then
  log "=== COMPLETE: all $TOTAL_FILES files verified ==="
  "$NOTIFY" ok "Raw recordings ARCHIVED — all $TOTAL_FILES files verified" "$SUMMARY

Nothing was deleted from e10. The local copy is untouched and still the working set."
  echo "COMPLETE $(date '+%F %T')" > "$LOGS/radix-archive.state"
else
  log "=== INCOMPLETE: $failed_files failed ==="
  "$NOTIFY" warn "Archive incomplete — $failed_files file(s) failed" "$SUMMARY

Failed:$FAILED_LIST
The watchdog will retry automatically. Nothing was deleted."
  echo "INCOMPLETE $(date '+%F %T')" > "$LOGS/radix-archive.state"
fi
exit 0
