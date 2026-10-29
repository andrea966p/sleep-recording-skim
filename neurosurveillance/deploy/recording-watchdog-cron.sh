#!/usr/bin/env bash
# recording-watchdog-cron.sh — hourly proof that the live recording is still
# writing bytes, and an ntfy alert (nvr-notify.sh) the moment it is not.
#
# Exists because a recording that starts correctly and then silently stops is the
# documented way runs have been lost here (see the 72 h run, 2026-07). A green
# start is not evidence of a green run.
#
# 2026-10-28 PER-PORT RECORDING (radiens-core 0.1.2, Allego 4.1.2). Allego now records per port
# (`split_files_by_port=True`): one file per recording port,
# `<dir>/allego_port<X>_<N>__uid<...>_data.xdat`, and `recording.active_filename` is NOT per
# port. So while the recorder is ON the watchdog checks growth of the NEWEST data file of EVERY
# port whose record_mode_port_x is ON (dir = get_recording_config().base_file_path) and alerts
# naming the stalled ports. Sizes per port are kept in logs/watchdog-lastsize-ports.txt. If no
# port file is found (old combined file, or split off) it falls back to the single-file check
# below. Allego mode now comes from `record_mode.name` ("ON"/"OFF"); an ImportError of
# radiens_core is reported as a broken watchdog and never as "recording stopped", and nothing is
# disarmed on it.
#
# WHAT IS WATCHED (revised 2026-10-02 after a code review)
#   The file Allego is writing RIGHT NOW. The status call returns the recorder mode
#   AND its current file name; if the armed name (logs/current-recording.txt) differs
#   from the live file while Allego is R_ON, the watchdog RE-ARMS to the live file.
#   Before this, a stale arm (an earlier run's name) was never replaced: the next run
#   went unwatched and the old file's frozen size raised a max-priority STALL every hour.
#
# HOW IT GETS ARMED
#   * by hand or by scheduled-recording.sh: write the base name to current-recording.txt;
#   * automatically: Allego R_ON with a file name, or the recording console's RECORDING
#     run (GET /api/runs?state=RECORDING -- the console's database only; /api/state would
#     make the console poll Allego). A console run used to go unwatched unless armed by hand.
#   The source is kept in logs/current-recording-source.txt.
#
# WHEN THE RECORDER STOPS
#   It alerts once and disarms. A console run that the console itself stopped gets an `ok`
#   note; a stop nobody can account for gets `warn`; the console still listing a run as
#   RECORDING while Allego is not R_ON gets ONE `fail` (the name is kept in
#   logs/watchdog-disarmed.txt so the alert does not repeat every hour).
#
# State: logs/current-recording.txt (base name), logs/watchdog-lastsize.txt (bytes at
# last check), logs/current-recording-source.txt, logs/watchdog-disarmed.txt.
set -uo pipefail

# Sandbox: overriding SOME paths and not others would silently mix a test with the live
# console, the live Allego and real alerts. All-or-nothing: WATCHDOG_DIR must be set
# whenever any other WATCHDOG_* variable is.
if env | grep -q '^WATCHDOG_' && [[ -z "${WATCHDOG_DIR:-}" ]]; then
  echo "WATCHDOG_* variables set without WATCHDOG_DIR: refusing to half-sandbox" >&2; exit 2
fi
DIR="${WATCHDOG_DIR:-/home/skimlab/sleep-recording-skim/neurosurveillance/deploy}"
LOGS="${WATCHDOG_LOGS:-$DIR/logs}"
NOTIFY="${WATCHDOG_NOTIFY:-$DIR/nvr-notify.sh}"
DEST="${WATCHDOG_DEST:-/home/skimlab/radix/data}"
PY="${WATCHDOG_PY:-/opt/neurosurveillance/venv/bin/python3}"
REPO="${WATCHDOG_REPO:-/home/skimlab/sleep-recording-skim/eeg-emg-analysis}"
CONSOLE="${WATCHDOG_CONSOLE:-http://127.0.0.1:8600}"
CUR="$LOGS/current-recording.txt"
SRC="$LOGS/current-recording-source.txt"
LAST="$LOGS/watchdog-lastsize.txt"
LASTP="$LOGS/watchdog-lastsize-ports.txt"
DISARMED="$LOGS/watchdog-disarmed.txt"
LOG="$LOGS/watchdog.log"
mkdir -p "$LOGS"
log() { echo "[$(date '+%F %T')] $*" >> "$LOG"; }

# --- what the recorder is doing, and which file it writes ---------------------
# Prints: MODE LIVE-NAME ON-PORTS CONFIG-DIR  (MODE = ON | OFF | UNREACHABLE | IMPORTERROR;
# "-" = none). Only the radiens_core import is allowed to be reported as IMPORTERROR.
read -r MODE LIVE PORTS CFGDIR < <(cd "$REPO" && PYTHONPATH="$REPO" "$PY" -c "
try:
    from radiens_core import AllegoClient
except ImportError:
    print('IMPORTERROR - - -'); raise SystemExit
try:
    c = AllegoClient(); r = c.get_status().recording
    on = ','.join(p.upper() for p in 'abcdefgh'
                  if getattr(r, 'record_mode_port_' + p, None) is not None
                  and getattr(r, 'record_mode_port_' + p).name == 'ON')
    try:
        d = c.get_recording_config().base_file_path
    except Exception:
        d = ''
    print(r.record_mode.name, r.active_filename or '-', on or '-', d or '-')
except Exception:
    print('UNREACHABLE - - -')" 2>/dev/null | tail -1)
MODE="${MODE:-UNREACHABLE}"; LIVE="${LIVE:--}"; PORTS="${PORTS:--}"; CFGDIR="${CFGDIR:--}"
# The data dir: an explicit WATCHDOG_DEST (sandbox) wins, then Allego's own recording config.
DIRP="$DEST"; [[ -z "${WATCHDOG_DEST:-}" && "$CFGDIR" != "-" ]] && DIRP="$CFGDIR"

if [[ "$MODE" == "IMPORTERROR" ]]; then
  log "radiens_core cannot be imported by $PY: the watchdog cannot see Allego (state left untouched)"
  "$NOTIFY" warn "Recording watchdog is blind" "radiens_core is not importable by \`$PY\`, so the hourly recording check could not run. Nothing was disarmed. Fix the interpreter."
  exit 1
fi

# --- what the console thinks is recording -------------------------------------
RESP="$(curl -s -m 10 -w '\n%{http_code}' "$CONSOLE/api/runs?state=RECORDING&limit=1" 2>/dev/null)"; CURL_RC=$?
HTTP="${RESP##*$'\n'}"; BODY="${RESP%$'\n'*}"
CBN=""; CPATH=""
if (( CURL_RC == 0 )) && [[ "$HTTP" == "200" ]]; then
  read -r CBN CPATH < <(printf '%s' "$BODY" | python3 -c '
import json, sys
try:
    runs = json.load(sys.stdin).get("runs") or []
except Exception:
    runs = []
r = runs[0] if runs else {}
print(r.get("base_name") or "-", r.get("data_path") or "-")' 2>/dev/null)
  [[ "$CBN" == "-" ]] && CBN=""; [[ "$CPATH" == "-" ]] && CPATH=""
else
  log "console not answering (curl rc=$CURL_RC, http=${HTTP:-none}); using the hand arm and Allego only"
fi

ARMED="$( [[ -f "$CUR" ]] && tr -d '[:space:]' < "$CUR" || true )"
WAS_DISARMED="$( [[ -f "$DISARMED" ]] && tr -d '[:space:]' < "$DISARMED" || true )"

# --- recorder NOT running -----------------------------------------------------
# UNREACHABLE (gRPC error, timeout) is not "stopped": say so, change no state, disarm nothing.
if [[ "$MODE" != "ON" && "$MODE" != "OFF" ]]; then
  log "cannot read Allego (mode $MODE): state left untouched"
  "$NOTIFY" warn "Recording watchdog cannot reach Allego" "The hourly check got no answer from Allego (\`${MODE}\`). Nothing was disarmed and no stop was assumed. If Allego is down during a recording, the recording is at risk: check the rig."
  exit 1
fi

if [[ "$MODE" == "OFF" ]]; then
  if [[ -n "$ARMED" ]]; then
    SOURCE="$( [[ -f "$SRC" ]] && cat "$SRC" || echo hand )"
    FILE="$DEST/${ARMED}_data.xdat"
    SIZE=$( [[ -f "$FILE" ]] && stat -c %s "$FILE" || echo -1 )
    # per-port files: the armed name is one port's file; its uid token is shared by every port
    # started together, so sum all data files carrying it for the final size.
    UIDTOK="$(grep -oP '__uid\K[0-9-]+' <<<"$ARMED" | head -1)"
    if (( SIZE < 0 )) && [[ -n "$UIDTOK" ]]; then
      PSUM=$(stat -c %s "$DIRP"/*__uid"${UIDTOK}"_data.xdat 2>/dev/null | awk '{s+=$1} END{print s+0}'); (( PSUM > 0 )) && SIZE=$PSUM
    fi
    GB=$(python3 -c "print(f'{$SIZE/1e9:.1f}')" 2>/dev/null || echo '?')
    if [[ -n "$CBN" && "$CBN" == "$ARMED" ]]; then
      "$NOTIFY" fail "Recording STOPPED but the console still says RECORDING" "File: \`${ARMED}\` (${GB} GB). Allego mode is \`${MODE}\`, the recording console still lists the run as RECORDING. The rig is not recording; the console has not noticed. Needs hands-on attention."
    elif [[ "$SOURCE" == console* ]]; then
      "$NOTIFY" ok "Recording finished" "File: \`${ARMED}\` — final size ${GB} GB. The recording console ended the run; watchdog disarmed."
    else
      "$NOTIFY" warn "Recording has STOPPED" "File: \`${ARMED}\` — final size ${GB} GB
Recorder mode is \`${MODE}\`.
If you stopped it yourself, nothing to do. If you did not, the run ended on its own.
Watchdog is now disarmed and will stop reporting."
    fi
    rm -f "$CUR" "$LAST" "$LASTP" "$SRC"; echo "$ARMED" > "$DISARMED"
    log "disarmed after stop: $ARMED (source $SOURCE, mode $MODE)"
    exit 0
  fi
  if [[ -n "$CBN" && "$CBN" != "$WAS_DISARMED" ]]; then
    "$NOTIFY" fail "Console says RECORDING, Allego does not" "The recording console lists \`${CBN}\` as RECORDING but Allego mode is \`${MODE}\`. Nothing is being written. This alert is sent once."
    echo "$CBN" > "$DISARMED"
    log "console lists $CBN as RECORDING but Allego is $MODE: alerted once"
    exit 1
  fi
  log "disarmed (not recording, mode $MODE)"; exit 0
fi

# --- recorder running: watch the file it is writing ---------------------------
TARGET=""; TSRC=""
if [[ "$LIVE" != "-" ]]; then
  TARGET="$LIVE"; TSRC="allego"; [[ -n "$CBN" && "$CBN" == "$LIVE" ]] && TSRC="console+allego"
elif [[ -n "$CBN" ]]; then
  TARGET="$CBN"; TSRC="console"
fi
if [[ -n "$TARGET" && "$TARGET" != "$ARMED" ]]; then
  echo "$TARGET" > "$CUR"; echo "$TSRC" > "$SRC"; rm -f "$LAST" "$LASTP"
  log "armed: ${ARMED:-nothing} -> $TARGET (source $TSRC)"
  ARMED="$TARGET"
fi
[[ -n "$ARMED" || "$PORTS" != "-" ]] || { log "recorder ON but no file name is known (Allego gave none, console none, no hand arm)"; exit 0; }
FNAME="$ARMED"

# --- per-port files (split_files_by_port): newest data file of every ON port --
PORT_ROWS=(); MISSING_PORTS=()
if [[ "$PORTS" != "-" ]]; then
  IFS=, read -ra PL <<<"$PORTS"
  for X in "${PL[@]}"; do
    PF="$(ls -t "$DIRP"/*_port"${X}"_*_data.xdat 2>/dev/null | head -1)"
    if [[ -n "$PF" ]]; then PORT_ROWS+=("$X"$'\t'"$PF"); else MISSING_PORTS+=("$X"); fi
  done
fi
if (( ${#PORT_ROWS[@]} > 0 )); then
  STALLED=""; NEWLAST=""; FIRSTFILE=""; GBTXT=""
  for ROW in "${PORT_ROWS[@]}"; do
    X="${ROW%%$'\t'*}"; PF="${ROW#*$'\t'}"
    SZ=$(stat -c %s "$PF" 2>/dev/null || echo -1)
    # compare only against the SAME file: a restart of a port makes a new file (N+1)
    PV=$( [[ -f "$LASTP" ]] && awk -F'\t' -v x="$X" -v p="$PF" '$1==x && $2==p {print $3; exit}' "$LASTP" || true )
    PV="${PV:--1}"
    NEWLAST+="$X"$'\t'"$PF"$'\t'"$SZ"$'\n'
    [[ -z "$FIRSTFILE" ]] && FIRSTFILE="$PF"
    PGB=$(python3 -c "print(f'{$SZ/1e9:.1f}')" 2>/dev/null || echo '?')
    GBTXT+="port $X ${PGB} GB; "
    log "mode=$MODE port=$X file=$(basename "$PF") size=$SZ prev=$PV"
    if (( PV >= 0 && SZ <= PV )); then
      STALLED+="port $X: \`$(basename "$PF")\` unchanged at ${PGB} GB"$'\n'
    fi
  done
  printf '%s' "$NEWLAST" > "$LASTP"
  FREE_GB=$(df --output=avail -BG "$(dirname "$FIRSTFILE")" 2>/dev/null | tail -1 | tr -dc '0-9'); FREE_GB="${FREE_GB:-0}"
  if [[ -n "$STALLED" ]]; then
    "$NOTIFY" fail "Recording STALLED — mode says ON but no new bytes" "${STALLED}Unchanged across a full hour while the recorder claims ON for ports ${PORTS}.
This is the silent-failure signature. Needs hands-on attention."
    log "STALL detected: ${STALLED//$'\n'/; }"
    exit 1
  fi
  if (( ${#MISSING_PORTS[@]} > 0 )); then
    "$NOTIFY" warn "Recording file not found" "Allego is recording on ports ${PORTS} but no data file was found for port(s) ${MISSING_PORTS[*]} in \`$DIRP\`, so growth cannot be checked for them."
    log "no data file for port(s) ${MISSING_PORTS[*]} in $DIRP"
    exit 1
  fi
  if (( FREE_GB < 150 )); then
    "$NOTIFY" warn "Disk low during recording" "Only ${FREE_GB} GB free on \`$(dirname "$FIRSTFILE")\` while recording ${GBTXT%; }."
  fi
  log "OK growing (ports ${PORTS})"
  exit 0
fi

# --- legacy: one combined file (split off, or an old run) ---------------------
FILE="$DEST/${FNAME}_data.xdat"
[[ -n "$CPATH" && "$CBN" == "$FNAME" ]] && FILE="$CPATH"           # the console knows its own path
NOW_SIZE=$( [[ -f "$FILE" ]] && stat -c %s "$FILE" || echo -1 )
PREV_SIZE=$( [[ -f "$LAST" ]] && cat "$LAST" || echo -1 )
echo "$NOW_SIZE" > "$LAST"
FREE_GB=$(df --output=avail -BG "$(dirname "$FILE")" 2>/dev/null | tail -1 | tr -dc '0-9'); FREE_GB="${FREE_GB:-0}"
GB=$(python3 -c "print(f'{$NOW_SIZE/1e9:.1f}')" 2>/dev/null || echo '?')
log "mode=$MODE file=$FNAME size=$NOW_SIZE prev=$PREV_SIZE free=${FREE_GB}G"

# --- running, but the armed file does not exist ------------------------------
if (( NOW_SIZE < 0 )); then
  if [[ "$( [[ -f "$SRC" ]] && cat "$SRC" )" == "allego" ]]; then
    # Known only from Allego's file name: a hand-started recording, possibly into another
    # folder (e.g. ~/radix/noise-tests). Not ours to alarm about every hour; log it.
    rm -f "$CUR" "$SRC" "$LAST" "$LASTP"          # do not stay armed: its normal end must not raise a STOPPED alert
    log "Allego is recording $FNAME outside $DEST (not armed by hand or console): not watched"
    exit 0
  fi
  "$NOTIFY" warn "Recording file not found" "Allego is recording and the watchdog is armed for \`${FNAME}\`, but \`${FILE}\` does not exist, so growth cannot be checked."
  log "armed file missing: $FILE"
  exit 1
fi

# --- running but not growing = the silent failure mode -----------------------
if (( PREV_SIZE >= 0 && NOW_SIZE <= PREV_SIZE )); then
  "$NOTIFY" fail "Recording STALLED — mode says ON but no new bytes" "File: \`${FNAME}\`
Size unchanged at ${GB} GB across a full hour while the recorder claims ON.
This is the silent-failure signature. Needs hands-on attention."
  log "STALL detected"
  exit 1
fi

# --- disk pressure ------------------------------------------------------------
if (( FREE_GB < 150 )); then
  "$NOTIFY" warn "Disk low during recording" "Only ${FREE_GB} GB free on \`$(dirname "$FILE")\` while recording \`${FNAME}\` (${GB} GB so far)."
fi

log "OK growing"
exit 0
