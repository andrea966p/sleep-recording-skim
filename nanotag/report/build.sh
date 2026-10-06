#!/usr/bin/env bash
# Rebuild the Word and PowerPoint versions of the HLBNSL report from its HTML
# pages, so they never drift from the HTML. Run after editing report.html or
# methods.html, or after cohort.py has redrawn the figures.
#   nanotag/report/build.sh [OUT_DIR]      (default: nanotag/analysis/out/HLBNSL)
# Needs node (nvm) and python3; installs docx + pptxgenjs from package-lock.json once.
set -euo pipefail
here=$(cd "$(dirname "$0")" && pwd)
out=${1:-$here/../analysis/out/HLBNSL}
command -v node >/dev/null || source "$HOME/.nvm/nvm.sh"
[ -d "$here/node_modules" ] || (cd "$here" && npm ci --no-fund --no-audit)
tmp=$(mktemp -d); trap 'rm -rf "$tmp"' EXIT
for page in report methods; do
  python3 "$here/html_blocks.py" "$out/$page.html" > "$tmp/$page.json"
  node "$here/build_docx.js" "$tmp/$page.json" "$out" "$out/HLBNSL_nanotag_$page.docx"
done
node "$here/build_pptx.js" "$tmp/report.json" "$out" "$out/HLBNSL_nanotag_figures.pptx"
