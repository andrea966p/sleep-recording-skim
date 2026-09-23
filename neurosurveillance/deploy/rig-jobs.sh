#!/usr/bin/env bash
# rig-jobs.sh -- one screen showing what the rig is chewing on right now.
#
# Covers the long jobs that otherwise only exist as a process and a log tail:
# a recording, a channel strip, a NAS upload, the S3 archive, and the QC ladder.
# Progress is measured from the BYTES ON DISK against the size the job must
# reach, never from a percentage the job prints, so it stays honest if a job
# dies: a stalled bar is a stalled job.
#
#   rig-jobs.sh            print once
#   rig-jobs.sh -w         refresh every 5 s until Ctrl-C
#   rig-jobs.sh -w 30      refresh every 30 s
set -uo pipefail
exec /opt/neurosurveillance/venv/bin/python3 "$(dirname "$0")/rig_jobs.py" "$@"
