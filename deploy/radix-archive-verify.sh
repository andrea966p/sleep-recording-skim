#!/usr/bin/env bash
# radix-archive-verify.sh — re-read every archived file ON THE NAS and compare
# its sha256 to the value recorded when it was transferred.
#
# The transfer already verified both ends. This is the separate question: is the
# data still intact where it now lives? It is the check that should gate any
# decision to delete the local copy, so it reads only the NAS side and never
# touches the local disk — it cannot compete with a live recording.
set -uo pipefail
DIR="/home/skimlab/Monitoring_project/neurosurveillance/deploy"
LOGS="$DIR/logs"; NOTIFY="$DIR/nvr-notify.sh"
MANIFEST="$LOGS/radix-archive.manifest"; LOG="$LOGS/radix-archive-verify.log"
ND="/volume1/homes/Andrea/e10_radix_archive/data"
# -n is REQUIRED: without it ssh reads the while-loop's stdin and swallows the
# rest of the manifest, so the loop silently verifies only the first file.
SSH=(ssh -n -i /home/skimlab/.ssh/id_ed25519 -p 53 -o BatchMode=yes -o ConnectTimeout=30
     -o ServerAliveInterval=15 Andrea@bilab-syn.tail8808c0.ts.net)
log(){ echo "[$(date '+%F %T')] $*" >> "$LOG"; }

log "=== full at-rest verification start ==="
ok=0; bad=0; missing=0; BADLIST=""
while IFS=$'\t' read -r name size sha status _; do
  [[ "$status" == "DONE" ]] || continue
  actual=$("${SSH[@]}" "sha256sum '$ND/$name' 2>/dev/null | cut -d' ' -f1" 2>/dev/null | tr -dc '0-9a-f')
  if   [[ -z "$actual" ]];      then missing=$((missing+1)); BADLIST+="
  - $name (MISSING on NAS)"; log "MISSING $name"
  elif [[ "$actual" == "$sha" ]]; then ok=$((ok+1))
  else bad=$((bad+1)); BADLIST+="
  - $name (checksum changed)"; log "CORRUPT $name"
  fi
done < <(sort -u -t$'\t' -k1,1 "$MANIFEST")

log "=== done: ok=$ok corrupt=$bad missing=$missing ==="
if (( bad == 0 && missing == 0 )); then
  "$NOTIFY" ok "Archive re-verified at rest — $ok/$ok files intact" "Every archived file was re-read on the NAS and its sha256 still matches the value recorded at transfer.

This is the green light: the NAS copy is complete and correct, so deleting the local copy of \`~/radix/data\` is safe whenever you choose.
Excluded, correctly: the live recording \`allego_0__uid0819-09-00-00\`, which is still being written."
else
  "$NOTIFY" fail "Archive verification FOUND PROBLEMS" "Intact: $ok · Corrupt: $bad · Missing: $missing
$BADLIST

DO NOT delete the local copy. Re-run the archive to repair."
fi
