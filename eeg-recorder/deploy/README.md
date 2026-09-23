# eeg-recorder

A local console for the Allego rig: set up a run, start or schedule it, stop it,
and have the recording stripped to the channels that were actually wired and
uploaded, verified, to the SKIM Lab NAS.

## Run it

    sudo cp deploy/eeg-recorder.service /etc/systemd/system/
    sudo systemctl daemon-reload
    sudo systemctl enable --now eeg-recorder

Then open <http://127.0.0.1:8600>. Logs: `journalctl -u eeg-recorder -f`.

For development, without installing anything:

    cd backend && /opt/neurosurveillance/venv/bin/python3 app.py

## What it does after a recording stops

    QC bundle  ->  strip  ->  upload  ->  verify

`core/criteria.py` judges every channel against **wire-free amplifier inputs
recorded in the same file**. The strip keeps only the wired channels, so it
deletes that floor and `compute_features` can never run on the result again.
The cached features are therefore the only surviving record of it, and the chain
**refuses to strip a recording that has no QC bundle** rather than quietly
destroying the evidence. Compute one with:

    cd ../eeg-emg-analysis && PYTHONPATH=. /opt/neurosurveillance/venv/bin/python3 \
        cards/ladder.py <base> --cohort <id> --cache /home/skimlab/eeg-qc-cache/<base>.npz

Nothing is ever deleted locally. The original 262-channel file stays where Allego
wrote it; removing it is a human decision.

## Things that are true and non-obvious

- **Recording is global.** One XDAQ, one `R_ON` for all four ports, one file.
  radiens 4.0.0 has no `start_recording(port=...)` whatever the upstream docs
  say. Per-user separation happens afterwards, by stripping. So one run owns the
  whole rig, and the console refuses to start a second one.
- **The `.xdat` file size does not move for ~30 s after a healthy start.**
  Measured on the rig. A growth check shorter than that reports a working
  recording as dead, so the console shows "0 bytes is normal at first" and
  confirms growth in the background after 40 s.
- **The channel selection does not change what is recorded.** Allego always
  records everything. The selection decides what survives into the stripped copy.
- **A missed scheduled start fails loudly** rather than beginning hours late.
  Starting a sleep recording at the wrong point in the light cycle is not the
  experiment anyone designed.
- **`UPLOAD_PENDING` is a resting state.** If the NAS is unreachable, finished
  runs queue there and drain when it returns.

## Layout

    backend/app.py           Flask, 127.0.0.1:8600, serves the API and the page
    backend/allego.py        status, config workaround, start/stop, growth check
    backend/runs.py          durable run store (SQLite, WAL) and state machine
    backend/scheduler.py     absolute-instant start/stop, re-armed on boot
    backend/postprocess.py   QC -> strip -> upload chain, one worker
    backend/nas_upload.py    CIFS upload with cache-dropped read-back verification
    backend/presets.py       users and channel layouts
    backend/storage.py       free space in hours, not just gigabytes
    config/users.yaml        who records, and which channels their layout uses
    frontend/               one page, no build step

    state: ~/.local/state/eeg-recorder/runs.db
