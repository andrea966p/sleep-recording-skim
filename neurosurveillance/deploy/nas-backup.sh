#!/usr/bin/env bash
# nas-backup.sh — daily snapshot of the NeuroSurveillance project (this NVR) to the NAS.
#
# Backs up: the Obsidian vault, the neurosurveillance code repo, the deployed
# daemon state (config.yaml, sessions/, session_wal.db) and the Frigate config.
# Excludes the bulk/regenerable data: recorded videos (MP4 + Frigate cache),
# build artifacts (node_modules, Rust target, venv) and the giant radiens.log.
#
# Produces one dated tarball per run and keeps the newest RETAIN on the NAS,
# deleting older ones (rolling 3-day retention by default).
#
# Runs as user `skimlab` via systemd timer (nas-backup.timer) at 00:00 daily.
# Auth is key-based (skimlab's ~/.ssh/id_ed25519 → NAS user `Andrea`).
#
# Vault doc: 02-procedures/installation/nas-backup.md
set -euo pipefail

# ---- NAS target -------------------------------------------------------------
# Use the MagicDNS name, NOT a literal 100.x address. The NAS was readdressed
# (100.120.86.10 -> 100.120.86.9) and the hardcoded literal silently broke every
# run from 2026-08-14 to 2026-08-19. Third stale-address outage in this setup.
NAS_HOST="bilab-syn.tail8808c0.ts.net"   # shared into this tailnet from bilab
NAS_PORT="53"
NAS_USER="Andrea"
NAS_DIR="e10_setup_backups"   # relative to NAS user's home
RETAIN=3                      # number of daily snapshots to keep on the NAS

NOTIFY="/home/skimlab/sleep-recording-skim/neurosurveillance/deploy/nvr-notify.sh"

SSH_KEY="/home/skimlab/.ssh/id_ed25519"
SSH_OPTS=(-i "$SSH_KEY" -p "$NAS_PORT" -o BatchMode=yes -o StrictHostKeyChecking=accept-new -o ConnectTimeout=20)

# ---- what to back up --------------------------------------------------------
PROJECT_HOME="home/skimlab/sleep-recording-skim"   # paths are relative to / (tar -C /)
INCLUDES=(
  "${PROJECT_HOME}"                        # the WHOLE workspace: vault, all code, claude-config, machine
  "home/skimlab/radix/devices"             # Allego device/port configuration
  "home/skimlab/radix/workspace"           # Allego workspace settings
  "opt/neurosurveillance/config.yaml"
  "opt/neurosurveillance/sessions"
  "opt/neurosurveillance/exports"          # MP4s are excluded below; keeps the sidecar JSONs
  "srv/frigate/docker-compose.yml"
  "srv/frigate/config"
  "srv/frigate/mosquitto"
)
EXCLUDES=(
  --exclude='*/node_modules'
  --exclude='*/src-tauri/target'
  --exclude='*/venv'
  --exclude='radiens.log'
  --exclude='*.mp4'                         # drop video bulk, keep export sidecar JSONs
  # NEVER back up the raw EEG recordings or the video. They are hundreds of GB,
  # they are archived separately by deploy/radix-archive.sh, and including them
  # would blow past the NAS retention of 3 daily snapshots. ~/radix/data is
  # deliberately absent from INCLUDES; these two lines make that impossible to
  # undo by accident.
  --exclude='*/radix/data'                  # raw Allego recordings (xdat), archived separately
  --exclude='*.xdat'
  --exclude='storage'                       # Frigate recording cache
  --exclude='*.db-wal' --exclude='*.db-shm' # transient SQLite WAL sidecars (see snapshot below)
  --exclude='__pycache__' --exclude='*.pyc'
  --exclude='*/mosquitto/passwd'            # 0600 1883:1883, unreadable as skimlab; secret lives in production-values.md
)

# ---- staging ----------------------------------------------------------------
STAMP="$(date +%F)"                          # YYYY-MM-DD (lexical sort == chronological)
ARCHIVE="e10_backup_${STAMP}.tar.gz"
STAGE="$(mktemp -d /tmp/e10-backup.XXXXXX)"
TARBALL="${STAGE}/${ARCHIVE}"
trap 'rm -rf "$STAGE"' EXIT

log() { echo "[nas-backup $(date '+%F %T')] $*"; }

# ---- skip unchanged nights --------------------------------------------------
# Fingerprint = path, size and mtime of everything the tarball would hold. Two
# paths are left out of the fingerprint (not the tarball) because they change
# every day on their own: deploy/logs (the archive watchdog writes every 20 min)
# and .git/FETCH_HEAD (`skim status` fetches at every session start). Logs still
# ride along whenever anything real changed. Written only after a verified upload,
# so a failed night is retried the next night.
FPFILE="/home/skimlab/.cache/nas-backup.fingerprint"
FINGERPRINT="$(cd / && { find "${INCLUDES[@]}" opt/neurosurveillance/session_wal.db opt/neurosurveillance/session_wal.db-wal \
    \( -name node_modules -o -path '*/src-tauri/target' -o -name venv -o -name __pycache__ \
       -o -path '*/radix/data' -o -name storage -o -path '*/deploy/logs' \) -prune \
    -o -type f ! -name '*.mp4' ! -name '*.xdat' ! -name '*.pyc' ! -name radiens.log \
       ! -name '*.db-shm' ! -path '*/.git/FETCH_HEAD' \
       ! -path '*/mosquitto/passwd' -printf '%p %s %T@\n' 2>/dev/null || true; } | sort | sha256sum | cut -d' ' -f1)"
if [[ -f "$FPFILE" && "$(cut -d' ' -f1 "$FPFILE")" == "$FINGERPRINT" ]]; then
  SINCE="$(cut -d' ' -f2 "$FPFILE")"
  log "nothing changed since the ${SINCE} snapshot; skipping"
  "$NOTIFY" ok "Nightly backup: nothing changed" "Repo, vault, e10 settings, daemon state and Frigate config are identical to the ${SINCE} snapshot.
No tarball built, nothing uploaded. The NAS still holds that snapshot."
  exit 0
fi

# ---- consistent SQLite snapshot --------------------------------------------
# Copying a live WAL-mode DB by file can miss committed rows. Use the online
# backup API to get a coherent copy, then include that instead of the live file.
WAL_SRC="/opt/neurosurveillance/session_wal.db"
if [[ -f "$WAL_SRC" ]]; then
  mkdir -p "${STAGE}/opt/neurosurveillance"
  python3 - "$WAL_SRC" "${STAGE}/opt/neurosurveillance/session_wal.db" <<'PY'
import sqlite3, sys
src = sqlite3.connect(sys.argv[1]); dst = sqlite3.connect(sys.argv[2])
with dst:
    src.backup(dst)
dst.close(); src.close()
PY
  log "SQLite snapshot taken"
fi

# ---- build tarball ----------------------------------------------------------
log "building ${ARCHIVE}"
set +e
tar czf "$TARBALL" "${EXCLUDES[@]}" \
  -C / "${INCLUDES[@]}" \
  -C "$STAGE" opt/neurosurveillance/session_wal.db
rc=$?
set -e
# tar exit 1 = "some files changed/vanished while reading" (benign on a live tree);
# exit >=2 = fatal (e.g. permission denied) — refuse to ship a broken snapshot.
if [[ $rc -gt 1 ]]; then
  log "tar FAILED (exit $rc)"
  "$NOTIFY" fail "Nightly backup FAILED to build" "tar exited $rc while building \`${ARCHIVE}\`.
Nothing was uploaded; the NAS still holds yesterday's snapshot.
See the journal: \`journalctl -u nas-backup.service -n 50\`."
  exit 1
fi
[[ $rc -eq 1 ]] && log "tar warning (exit 1: files changed during read) — continuing"

# verify integrity before we trust it as a backup
gzip -t "$TARBALL"
SIZE="$(du -h "$TARBALL" | cut -f1)"
log "tarball OK (${SIZE})"

# ---- upload -----------------------------------------------------------------
log "ensuring remote dir + uploading"
if ! ssh "${SSH_OPTS[@]}" "${NAS_USER}@${NAS_HOST}" "mkdir -p ${NAS_DIR}"; then
  log "FATAL: cannot reach ${NAS_HOST} or create ${NAS_DIR}"
  "$NOTIFY" fail "Nightly backup cannot reach the bilab NAS" "Could not reach \`${NAS_HOST}\` or create \`${NAS_DIR}\`.
The tarball built fine (${SIZE}) but nothing was uploaded.
Check Tailscale: the NAS is shared in from the bilab tailnet."
  exit 1
fi
# Stream the tarball over the SAME ssh invocation that is proven to work on this
# NAS. Synology's rsync forced-command and OpenSSH-9 scp's SFTP backend both
# misbehave here; piping into a remote `cat` depends only on plain ssh + a shell.
# Write to a temp name, then atomic rename, so a failed transfer never leaves a
# half-written file that rotation would treat as a valid backup.
ssh "${SSH_OPTS[@]}" "${NAS_USER}@${NAS_HOST}" \
    "cat > ${NAS_DIR}/.${ARCHIVE}.part && mv -f ${NAS_DIR}/.${ARCHIVE}.part ${NAS_DIR}/${ARCHIVE}" \
    < "$TARBALL"

# verify the remote copy is byte-for-byte complete
local_bytes=$(wc -c < "$TARBALL")
remote_bytes=$(ssh "${SSH_OPTS[@]}" "${NAS_USER}@${NAS_HOST}" "wc -c < ${NAS_DIR}/${ARCHIVE}" | tr -d '[:space:]')
if [[ "$local_bytes" != "$remote_bytes" ]]; then
  log "upload size mismatch (local=${local_bytes} remote=${remote_bytes})"
  "$NOTIFY" fail "Nightly backup upload is CORRUPT" "\`${ARCHIVE}\` uploaded short or long.
local=${local_bytes} bytes, remote=${remote_bytes} bytes.
Treat the newest snapshot on the NAS as untrustworthy."
  exit 1
fi
log "uploaded ${ARCHIVE} (${remote_bytes} bytes verified)"
mkdir -p "$(dirname "$FPFILE")" && echo "$FINGERPRINT $STAMP" > "$FPFILE"

# ---- rotate (keep newest RETAIN) -------------------------------------------
log "rotating: keeping newest ${RETAIN}"
ssh "${SSH_OPTS[@]}" "${NAS_USER}@${NAS_HOST}" \
  "cd ${NAS_DIR} && ls -1t e10_backup_*.tar.gz 2>/dev/null | tail -n +$((RETAIN+1)) | xargs -r rm -f && echo 'remaining:' && ls -1t e10_backup_*.tar.gz"

REMAINING="$(ssh "${SSH_OPTS[@]}" "${NAS_USER}@${NAS_HOST}" \
  "cd ${NAS_DIR} && ls -1t e10_backup_*.tar.gz 2>/dev/null" | tr '\n' ' ')"
"$NOTIFY" ok "Nightly backup on the bilab NAS" "Uploaded \`${ARCHIVE}\` (${SIZE}, ${remote_bytes} bytes verified).
Repo, vault, e10 settings, daemon state and Frigate config. No bulk data by design.
Kept (newest ${RETAIN}): ${REMAINING}"
log "done"
