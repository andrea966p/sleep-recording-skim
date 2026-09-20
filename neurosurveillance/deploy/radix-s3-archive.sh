#!/usr/bin/env bash
# radix-s3-archive.sh — nightly off-site copy of ~/radix/data (raw Allego .xdat)
# to Amazon S3, incremental, and without ever endangering a live recording.
#
# WHY THIS EXISTS
#   radix-archive.sh puts the raw recordings on the lab NAS. The NAS is a single
#   box in the same building as the rig. This adds a second, off-site copy so a
#   fire, a theft or a controller failure does not end the project. The animals
#   were sampled; these recordings cannot be retaken.
#
# RELATIONSHIP TO radix-archive.sh
#   Same guards, same file-at-a-time structure, different destination. They are
#   deliberately separate scripts: the NAS copy must keep working even if AWS
#   access is revoked, and vice versa. Run them on different nights (see timer).
#
# WHAT IT GUARANTEES
#   - Never competes with the rig. Defers entirely if a recording is live, and
#     stops before the morning recording window.
#   - Incremental. A file already in S3 at the same byte size is skipped without
#     being read off disk at all.
#   - Integrity is checked by S3 itself: every upload carries a SHA256 that S3
#     verifies server-side and rejects on mismatch. No second read pass locally.
#   - Never deletes anything, locally or in S3. The IAM user it runs as does not
#     hold s3:DeleteObject, so this is enforced by AWS, not just by this script.
#
# CREDENTIALS
#   Uses AWS profile $AWS_PROFILE_NAME from /home/skimlab/.aws/credentials — a
#   dedicated IAM user scoped to this one bucket. It is NOT your SSO login; SSO
#   sessions expire and cannot drive an unattended timer.
#
# Usage: radix-s3-archive.sh [--dry-run]
set -uo pipefail

# One script, several jobs. JOB keeps the log/lock/state files distinct so the
# raw and stripped runs never share a lock or overwrite each other's state.
#   raw      (default) : ~/radix/data     -> radix/data/
#   stripped           : ~/radix/stripped -> radix/stripped/
JOB="${RADIX_S3_JOB:-raw}"
SRC="${RADIX_S3_SRC:-/home/skimlab/radix/data}"
BUCKET="${RADIX_S3_BUCKET:-skim-eeg-radix-archive-760396521414}"
PREFIX="${RADIX_S3_PREFIX:-radix/data}"
REGION="ap-northeast-2"
STORAGE_CLASS="GLACIER_IR"
AWS_PROFILE_NAME="radix-backup"
AWS_BIN="/home/skimlab/.local/bin/aws"

DIR="/home/skimlab/sleep-recording-skim/neurosurveillance/deploy"
LOGS="$DIR/logs"; mkdir -p "$LOGS"
LOG="$LOGS/radix-s3-archive-$JOB.log"
LOCK="$LOGS/radix-s3-archive-$JOB.lock"
STATE="$LOGS/radix-s3-archive-$JOB.state"
NOTIFY="$DIR/nvr-notify.sh"
REPO="/home/skimlab/sleep-recording-skim/eeg-emg-analysis"
PY="/opt/neurosurveillance/venv/bin/python3"

# Stop well before the 09:00 recording so we are never reading the disk hard
# while the amplifiers are writing to it.
HARD_STOP="08:30"
MAX_RETRIES=3

DRY_RUN=0
[[ "${1:-}" == "--dry-run" ]] && DRY_RUN=1

export AWS_PROFILE="$AWS_PROFILE_NAME"
export AWS_SHARED_CREDENTIALS_FILE="/home/skimlab/.aws/credentials"
export AWS_DEFAULT_REGION="$REGION"
# The CLI writes ~50 MB of cache/history by default; keep it off the data disk path.
export AWS_CLI_HISTORY_FILE=/dev/null

log() { echo "[$(date '+%F %T')] $*" | tee -a "$LOG"; }

# ---- single instance --------------------------------------------------------
exec 9>"$LOCK"
if ! flock -n 9; then
  log "another run holds the lock; exiting"
  exit 0
fi

# ---- guards -----------------------------------------------------------------
# 10# forces base 10. Without it `date +%H` returns "08"/"09", bash reads them as
# octal, and the test ERRORS OUT instead of firing — exactly what happened to the
# NAS archiver on 2026-08-19, leaving its 08:30 guard inoperative.
past_hard_stop() {
  [[ "${ARCHIVE_IGNORE_WINDOW:-0}" == "1" ]] && return 1
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

# Byte size of an object already in S3, or empty if absent. This is the whole
# "skip what is already there" mechanism: one HEAD per file, no disk read.
remote_size() {
  "$AWS_BIN" s3api head-object --bucket "$BUCKET" --key "$PREFIX/$1" \
    --query 'ContentLength' --output text 2>/dev/null | tr -dc '0-9'
}

# ---- preflight --------------------------------------------------------------
if [[ ! -d "$SRC" ]]; then
  log "FATAL: source directory $SRC does not exist"
  "$NOTIFY" fail "S3 archive ($JOB) has no source" "\`$SRC\` does not exist on e10.
Nothing was transferred. If the directory was renamed, update RADIX_S3_SRC."
  exit 1
fi

if [[ ! -x "$AWS_BIN" ]]; then
  log "FATAL: $AWS_BIN not found"
  exit 1
fi

if ! "$AWS_BIN" s3api head-bucket --bucket "$BUCKET" >/dev/null 2>>"$LOG"; then
  log "FATAL: cannot reach bucket $BUCKET (credentials or network)"
  "$NOTIFY" fail "S3 archive ($JOB) cannot start" "Could not reach \`s3://$BUCKET\`.
Nothing was transferred. Check the \`$AWS_PROFILE_NAME\` credentials on e10.
See \`$LOG\`."
  exit 1
fi

mapfile -t FILES < <(cd "$SRC" && ls -1 2>/dev/null | sort)
TOTAL_FILES=${#FILES[@]}
TOTAL_BYTES=$(du -sb "$SRC" | cut -f1)
log "=== radix-s3-archive [$JOB] start: $TOTAL_FILES files, $(human "$TOTAL_BYTES") -> s3://$BUCKET/$PREFIX ==="
(( DRY_RUN )) && log "DRY RUN — nothing will be uploaded"

if recording_active; then
  log "a recording is live — deferring entirely (no files touched)"
  echo "DEFERRED $(date '+%F %T')" > "$STATE"
  (( DRY_RUN )) && log "RIG BUSY"
  exit 0
fi

START_TS=$(date +%s)
done_files=0; done_bytes=0; failed_files=0; skipped=0; uploaded=0
FAILED_LIST=""

for name in "${FILES[@]}"; do
  src="$SRC/$name"
  [[ -f "$src" ]] || continue

  if past_hard_stop; then
    log "HARD STOP ($HARD_STOP) reached — pausing before the recording window"
    "$NOTIFY" warn "S3 archive ($JOB) paused for the recording window" "Stopped at $HARD_STOP so the 09:00 recording has the disk to itself.
Progress: $done_files/$TOTAL_FILES files, $(human $done_bytes) accounted for ($uploaded newly uploaded).
It resumes automatically tonight; nothing is lost."
    echo "PAUSED $(date '+%F %T')" > "$STATE"
    exit 0
  fi

  # Cheap checks FIRST. recording_active() spawns a python client (~3.3 s), so
  # asking it about files that are already archived wasted ~7 min per resumed
  # run on the NAS archiver's 124-file backlog. A file we will skip needs no
  # rig query and no disk read.
  size=$(stat -c %s "$src")
  rsize=$(remote_size "$name")

  if [[ -n "$rsize" && "$rsize" == "$size" ]]; then
    skipped=$((skipped+1)); done_bytes=$((done_bytes+size)); done_files=$((done_files+1))
    continue
  fi

  if recording_active; then
    log "recording started — deferring the rest of the run, will resume when it ends"
    echo "DEFERRED $(date '+%F %T')" > "$STATE"
    exit 0
  fi

  if (( DRY_RUN )); then
    log "WOULD UPLOAD $name ($(human $size))"
    uploaded=$((uploaded+1)); done_files=$((done_files+1)); done_bytes=$((done_bytes+size))
    continue
  fi

  ok=0
  for try in $(seq 1 $MAX_RETRIES); do
    log "$name: uploading $(human $size), try $try"
    # nice/ionice so the rig always wins any disk contention.
    # --checksum-algorithm SHA256 makes S3 verify integrity server-side and
    # reject a corrupted upload, so we get the NAS script's end-to-end guarantee
    # without a second full read of the file.
    if ionice -c3 nice -n 19 "$AWS_BIN" s3 cp "$src" "s3://$BUCKET/$PREFIX/$name" \
         --storage-class "$STORAGE_CLASS" \
         --checksum-algorithm SHA256 \
         --only-show-errors 2>>"$LOG"; then
      rsize=$(remote_size "$name")
      if [[ "$rsize" == "$size" ]]; then
        done_files=$((done_files+1)); done_bytes=$((done_bytes+size)); uploaded=$((uploaded+1))
        log "$name: VERIFIED in S3 ($(human $size)) [$done_files/$TOTAL_FILES]"
        ok=1; break
      fi
      log "$name: size mismatch after upload (local=$size remote=${rsize:-absent}), try $try"
    else
      log "$name: upload error on try $try"
    fi
    sleep $((try*15))
  done

  if (( ok == 0 )); then
    failed_files=$((failed_files+1)); FAILED_LIST+="
  - $name ($(human $size))"
    log "$name: GAVE UP after $MAX_RETRIES tries"
  fi
done

ELAPSED=$(( $(date +%s) - START_TS ))
SUMMARY="Files in S3: $done_files of $TOTAL_FILES  (already present: $skipped, newly uploaded: $uploaded)
Data: $(human $done_bytes) of $(human $TOTAL_BYTES)
Elapsed: $((ELAPSED/60)) min
Destination: \`s3://$BUCKET/$PREFIX\` ($STORAGE_CLASS, $REGION)
Every upload was SHA256-verified by S3 before being counted."

if (( DRY_RUN )); then
  log "=== DRY RUN COMPLETE ==="
  log "$SUMMARY"
  exit 0
fi

if (( failed_files == 0 && done_files == TOTAL_FILES )); then
  log "=== COMPLETE: all $TOTAL_FILES files present in S3 ==="
  "$NOTIFY" ok "S3 archive ($JOB) COMPLETE — all $TOTAL_FILES files" "$SUMMARY

Nothing was deleted from e10 or from the NAS. This is a third copy."
  echo "COMPLETE $(date '+%F %T')" > "$STATE"
else
  log "=== INCOMPLETE: $failed_files failed ==="
  "$NOTIFY" warn "S3 archive ($JOB) incomplete — $failed_files file(s) failed" "$SUMMARY

Failed:$FAILED_LIST
The next nightly run retries automatically. Nothing was deleted."
  echo "INCOMPLETE $(date '+%F %T')" > "$STATE"
fi
exit 0
