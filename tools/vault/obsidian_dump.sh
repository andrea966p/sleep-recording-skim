#!/usr/bin/env bash
# Dump Obsidian's own link graph (resolvedLinks, unresolvedLinks, file list) to JSON.
# Used as the referee for vault link rewrites: our parser must agree with Obsidian.
# Needs Obsidian running with Settings > General > Advanced > Command line interface ON.
# The flatpak wrapper re-splits arguments on spaces, so the JS is passed base64-encoded.
set -euo pipefail
out="${1:?usage: obsidian_dump.sh OUT.json}"
out="$(readlink -f "$out")"
js="(function(){const fs=require('fs');const mc=app.metadataCache;
const d={resolved:mc.resolvedLinks,unresolved:mc.unresolvedLinks,files:app.vault.getFiles().map(f=>f.path)};
fs.writeFileSync('${out}',JSON.stringify(d));return 'ok '+d.files.length;})()"
b64="$(printf '%s' "$js" | base64 -w0)"
timeout 60 flatpak run md.obsidian.Obsidian eval "code=eval(atob('${b64}'))" 2>&1 | grep -E '^=>|Error' || true
test -s "$out" && echo "wrote $out"
