#!/usr/bin/env bash
# Run the full pipeline on one or more recordings.
#
#   ./run_pipeline.sh allego_1__uid0731-18-06-37 [more...]
#
# Use the SYSTEM python3. The /opt/neurosurveillance venv has a numpy/scipy ABI
# mismatch and dies with "numpy.core.multiarray failed to import".
#
# Stage 2 buffers every kept animal at the full sample rate (~2.4 GB for three
# mice over 28 h), so do not run two recordings concurrently on this machine --
# 30 GB of RAM with the page cache full pushes it into swap.
set -euo pipefail

cd "$(dirname "$0")"
ROOT="${EEG_PROCESSED_ROOT:-/home/skimlab/eeg-processed/}"

for base in "$@"; do
    echo "=============================================================="
    echo "  $base"
    echo "=============================================================="
    python3 stage1_qc.py "$base" --json "/tmp/qc_${base}.json"
    python3 stage2_split.py "$base" --root "$ROOT"
done

# stage 3 over every day folder that stage 2 touched
for day in $(ls -1d "$ROOT"*/ 2>/dev/null); do
    if compgen -G "${day}port*.npz" > /dev/null; then
        python3 stage3_features.py "$day"
        python3 stage4_export_edf.py "$day"
    fi
done
