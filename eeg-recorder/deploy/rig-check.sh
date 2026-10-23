#!/usr/bin/env bash
# rig-check.sh -- is everything that a recording needs actually up?
#
# Run this after any restart, before setting up a run, or whenever something
# looks wrong. It changes NOTHING: no service is started, no file is written, no
# recording is touched. Safe to run while a recording is in progress.
#
#   ~/sleep-recording-skim/eeg-recorder/deploy/rig-check.sh
#
# Exit 0 = ready to record. Exit 1 = at least one thing needs a human.
#
# WHY THIS EXISTS. On 2026-09-13 a RustDesk restart dropped the desktop session
# and it looked, from the far end, exactly like the machine had crashed and
# rebooted. Nothing had: the host had been up four weeks and the console had
# never stopped. Guessing at that from a black screen is hard; asking is easy.
set -uo pipefail

# Overridable so the failure path can be exercised without breaking the rig.
# A check that has only ever been seen to pass is not evidence.
UI="${RIG_CHECK_UI:-http://127.0.0.1:8600}"
FAIL=0
say()  { printf '%-28s %s\n' "$1" "$2"; }
bad()  { printf '%-28s \033[31m%s\033[0m\n' "$1" "$2"; FAIL=1; }
good() { printf '%-28s \033[32m%s\033[0m\n' "$1" "$2"; }
warn() { printf '%-28s \033[33m%s\033[0m\n' "$1" "$2"; }

echo "=== the machine ==="
say  "host up since" "$(uptime -s)  ($(uptime -p))"
say  "now" "$(date '+%F %T %Z')"

echo
echo "=== services (these survive a desktop crash) ==="
for u in tailscaled eeg-recorder mnt-skimnas.automount; do
  a=$(systemctl is-active "$u" 2>&1)
  e=$(systemctl is-enabled "$u" 2>&1)
  if [[ "$a" == "active" ]]; then good "$u" "active ($e at boot)"
  else bad "$u" "$a  -> sudo systemctl start $u"; fi
done

echo
echo "=== the console ==="
code=$(curl -s -o /dev/null -w '%{http_code}' --max-time 10 "$UI/" 2>/dev/null)
if [[ "$code" == "200" ]]; then good "web page" "$UI  (HTTP 200)"
else bad "web page" "HTTP ${code:-no answer}  -> sudo systemctl restart eeg-recorder"; fi

# One call carries the rig, the NAS, the disk and any run in flight.
state=$(curl -s --max-time 20 "$UI/api/state" 2>/dev/null)
if [[ -z "$state" ]]; then
  bad "api/state" "no answer  -> journalctl -u eeg-recorder -n 50"
else
  python3 - "$state" <<'PY'
import json, sys
G, R, Y, Z = "\033[32m", "\033[31m", "\033[33m", "\033[0m"
def line(k, v, col=""): print(f"{k:<28} {col}{v}{Z}")
d = json.loads(sys.argv[1])
a, n, s = d.get("allego") or {}, d.get("nas") or {}, d.get("storage") or {}
bad = False

# --- the rig -------------------------------------------------------------
if not a.get("reachable"):
    line("allego", "NOT REACHABLE -- is the Allego GUI open?", R); bad = True
else:
    probs = a.get("problems") or []
    # A fresh Allego comes up 30 kHz / SMARTBOX_PRO. Recording in that state
    # produces a file this project's analysis cannot read as a sleep recording,
    # and nothing later in the chain notices.
    mode, fs = a.get("system_mode"), a.get("sample_freq")
    ok = (mode == "XDAQ_ONE_REC" and float(fs or 0) == 1000.0)
    line("allego", f"reachable | {mode} | {fs} Hz | rec {a.get('recording')}",
         G if ok and not probs else R)
    if not ok:
        line("", "EXPECTED XDAQ_ONE_REC at 1000 Hz -- fix it in the GUI "
                 "BEFORE recording", R); bad = True
    for p in probs:
        line("", p, R); bad = True

# --- the NAS -------------------------------------------------------------
if n.get("ok"):
    line("nas", f"mounted, sentinel ok, {n.get('free_bytes',0)/1e9:.0f} GB free", G)
else:
    # Not fatal: finished runs wait in UPLOAD_PENDING and drain when it returns.
    line("nas", "NOT USABLE -- uploads will queue, recording still works", Y)

# --- disk ----------------------------------------------------------------
hrs = s.get("hours_remaining") or 0
line("local disk", f"{s.get('free_bytes',0)/1e9:.0f} GB free, "
                   f"{hrs:.0f} h at {s.get('gb_per_hour')} GB/h",
     G if hrs > 30 else R)
if hrs <= 30: bad = True

# --- anything in flight --------------------------------------------------
run = d.get("active_run")
line("active run", f"{run['run_id']} {run['state']}" if run else "none",
     Y if run else G)
pend = d.get("pending_upload") or []
line("waiting to upload", f"{len(pend)} run(s)" if pend else "none",
     Y if pend else G)
sys.exit(1 if bad else 0)
PY
  [[ $? -ne 0 ]] && FAIL=1
fi

echo
echo "=== the Allego GUI (a human launches this, nothing else does) ==="
# The MAIN window process, not its --type=zygote/gpu-process/renderer children.
# `pgrep -f '^/opt/allego/allego$'` was WRONG: it anchors on end-of-string, so the
# moment a --disable-gpu flag (which this script once asked for) is present, the pattern
# stops matching and the check reports Allego as not running. Caught 2026-09-13,
# minutes after the flag was applied -- the checker would have called a correctly
# launched rig broken. Pick the one process whose arguments contain no `--type=`.
apid=""
for p in $(pgrep -f '/opt/allego/allego' 2>/dev/null); do
  [[ -r "/proc/$p/cmdline" ]] || continue
  c=$(tr '\0' ' ' < "/proc/$p/cmdline")
  case "$c" in
    /opt/allego/allego*)  [[ "$c" != *--type=* ]] && { apid=$p; break; } ;;
  esac
done
if [[ -n "$apid" ]]; then
  cmd=$(tr '\0' ' ' < "/proc/$apid/cmdline")
  good "allego process" "running"
  # Allego runs WITHOUT --disable-gpu (decided 2026-10-23). The flag forces the
  # software renderer, whose 8192 px texture limit is smaller than the Monitor
  # canvas (262 signals x 50 px), so the Monitor draws nothing. The flag had been
  # added after the 2026-08-24 Mesa crash; that risk is accepted. Vault:
  # allego-blank-monitor-canvas-texture-limit, allego-mesa-gpu-crash-and-log-storm.
  case "$cmd" in
    *--disable-gpu*) warn "  launched WITH --disable-gpu" "the Monitor will be blank: relaunch /opt/allego/allego plainly" ;;
    *) good "  launched without" "--disable-gpu" ;;
  esac
else
  bad "allego process" "not running -> launch it from the desktop, then re-run this"
fi

echo
if [[ $FAIL -eq 0 ]]; then
  printf '\033[32m%s\033[0m\n' "READY. Open $UI"
else
  printf '\033[31m%s\033[0m\n' "NOT READY -- see the red lines above."
fi
exit $FAIL
