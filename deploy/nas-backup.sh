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
NAS_HOST="100.120.86.10"      # Tailscale address
NAS_PORT="53"
NAS_USER="Andrea"
NAS_DIR="e10_setup_backups"   # relative to NAS user's home
RETAIN=3                      # number of daily snapshots to keep on the NAS

SSH_KEY="/home/skimlab/.ssh/id_ed25519"
SSH_OPTS=(-i "$SSH_KEY" -p "$NAS_PORT" -o BatchMode=yes -o StrictHostKeyChecking=accept-new -o ConnectTimeout=20)

# ---- what to back up --------------------------------------------------------
PROJECT_HOME="home/skimlab/Monitoring_project"   # paths are relative to / (tar -C /)
INCLUDES=(
  "${PROJECT_HOME}/Monitoring_project_obsidian_vault"
  "${PROJECT_HOME}/neurosurveillance"
  "${PROJECT_HOME}/neurosurveillance-system"
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
  log "tar FAILED (exit $rc)"; exit 1
fi
[[ $rc -eq 1 ]] && log "tar warning (exit 1: files changed during read) — continuing"

# verify integrity before we trust it as a backup
gzip -t "$TARBALL"
SIZE="$(du -h "$TARBALL" | cut -f1)"
log "tarball OK (${SIZE})"

# ---- upload -----------------------------------------------------------------
log "ensuring remote dir + uploading"
ssh "${SSH_OPTS[@]}" "${NAS_USER}@${NAS_HOST}" "mkdir -p ${NAS_DIR}"
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
  log "upload size mismatch (local=${local_bytes} remote=${remote_bytes})"; exit 1
fi
log "uploaded ${ARCHIVE} (${remote_bytes} bytes verified)"

# ---- rotate (keep newest RETAIN) -------------------------------------------
log "rotating: keeping newest ${RETAIN}"
ssh "${SSH_OPTS[@]}" "${NAS_USER}@${NAS_HOST}" \
  "cd ${NAS_DIR} && ls -1t e10_backup_*.tar.gz 2>/dev/null | tail -n +$((RETAIN+1)) | xargs -r rm -f && echo 'remaining:' && ls -1t e10_backup_*.tar.gz"

log "done"
