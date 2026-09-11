#!/usr/bin/env python3
"""postprocess.py -- what happens after a recording stops: QC, strip, upload.

ONE WORKER, ONE RUN AT A TIME. Stripping reads the whole recording and hashes it
twice; two of those at once would compete for the same NVMe the amplifiers write
to. The queue is the point, not a limitation.

THE ORDER IS NOT NEGOTIABLE, AND THE REASON IS SCIENTIFIC, NOT TECHNICAL

    QC BUNDLE  ->  STRIP  ->  UPLOAD

    `core/criteria.py` derives every verdict in this project against WIRE-FREE
    AMPLIFIER INPUTS RECORDED IN THE SAME FILE -- sites /3../16 and /35../48 in a
    two-role cohort. The strip keeps only the wired channels, so it DELETES THAT
    FLOOR, and `compute_features` afterwards exits with "N expected sites are not
    in this file's biointerface_map". Demonstrated on 2026-09-11, not assumed.

    So the cached features are the ONLY surviving record of the floor, and they
    must be computed BEFORE the strip and travel WITH it. A stripped recording
    that reaches the NAS without its bundle can never be QC'd again by this
    project's own criterion. That is why a missing bundle is a refusal by default
    rather than a warning.

EVERY STAGE IS RESUMABLE AND NOTHING IS EVER DELETED LOCALLY. A service restart
mid-upload continues; it does not start over. The original 262-channel recording
stays where Allego wrote it, and removing it is a human decision taken after
reading the manifest.
"""
from __future__ import annotations

import json
import os
import queue
import subprocess
import sys
import threading
import traceback
from pathlib import Path
from typing import Callable

import runs as R
import nas_upload

ANALYSIS = Path(os.environ.get(
    "EEG_ANALYSIS_DIR",
    Path(__file__).resolve().parents[2] / "eeg-emg-analysis"))
# The only interpreter that has BOTH numpy and radiens. The stripper itself is
# numpy+stdlib, but keeping one interpreter for every stage avoids a second
# environment drifting out of step.
PYTHON = os.environ.get("EEG_RECORDER_PYTHON",
                        "/opt/neurosurveillance/venv/bin/python3")


class PostprocessError(RuntimeError):
    pass


def qc_cache_path(base_name: str) -> Path:
    from importlib import import_module
    sys.path.insert(0, str(ANALYSIS))
    paths = import_module("core.paths")
    return Path(paths.CACHE_ROOT) / f"{base_name}.npz"


def has_qc_bundle(base_name: str) -> bool:
    return qc_cache_path(base_name).exists()


def _duration_s(run) -> float | None:
    """Recorded duration in seconds, or None if the run never really started."""
    from datetime import datetime
    try:
        a = datetime.fromisoformat(run.actual_start.replace("Z", "+00:00"))
        b = datetime.fromisoformat(run.actual_stop.replace("Z", "+00:00"))
        return (b - a).total_seconds()
    except Exception:
        return None


def strip(run: R.Run, *, out_dir: str | Path | None = None,
          progress: Callable[[str], None] | None = None) -> dict:
    """Run the stripper as a subprocess and return its report.

    A subprocess rather than an import: the stripper is a long CPU+IO job, and
    keeping it out of the service's address space means a crash in it cannot take
    the API down mid-recording.
    """
    say = progress or (lambda m: None)
    if not run.base_path:
        raise PostprocessError(f"run {run.run_id} has no recorded base_path")
    cmd = [PYTHON, "-m", "convert.strip_channels", run.base_path,
           "--keep-labels", ",".join(run.keep_labels),
           "--verify", "full", "--require-idle"]
    if run.with_gpio:
        cmd.append("--with-gpio")
    if out_dir:
        cmd += ["--out", str(out_dir)]
    say(f"  {' '.join(cmd[:4])} ... ({len(run.keep_labels)} labels)")
    env = dict(os.environ, PYTHONPATH=str(ANALYSIS))
    p = subprocess.run(cmd, cwd=ANALYSIS, env=env, capture_output=True, text=True)
    if p.returncode != 0:
        raise PostprocessError(
            f"strip_channels exited {p.returncode}:\n{(p.stderr or p.stdout)[-2000:]}")
    from importlib import import_module
    sys.path.insert(0, str(ANALYSIS))
    paths = import_module("core.paths")
    root = Path(out_dir) if out_dir else Path(paths.STRIPPED_ROOT)
    report = root / f"{run.base_name}.strip-report.json"
    if not report.exists():
        raise PostprocessError(f"strip reported success but {report} is missing")
    return json.loads(report.read_text())


class Worker:
    """The post-stop chain, on one background thread."""

    def __init__(self, store: R.RunStore, *,
                 require_qc_bundle: bool = True,
                 on_event: Callable[[str], None] | None = None):
        self.store = store
        self.require_qc_bundle = require_qc_bundle
        self.log = on_event or (lambda m: print(f"[postprocess] {m}", flush=True))
        self._q: queue.Queue = queue.Queue()
        self._stop = threading.Event()
        self._thread: threading.Thread | None = None
        self.current: str | None = None

    def start(self) -> None:
        self._thread = threading.Thread(target=self._loop, name="postprocess",
                                        daemon=True)
        self._thread.start()
        # Anything left waiting from a previous life goes back in the queue. A
        # NAS outage across a restart must not strand a finished run.
        for state in (R.STOPPED, R.QC, R.STRIPPED, R.UPLOAD_PENDING):
            for run in self.store.list(states=(state,), limit=50):
                self.submit(run.run_id)
        self.log("worker armed")

    def stop(self, timeout: float = 5.0) -> None:
        self._stop.set()
        self._q.put(None)
        if self._thread:
            self._thread.join(timeout)

    def submit(self, run_id: str) -> None:
        self._q.put(run_id)

    def _loop(self) -> None:
        while not self._stop.is_set():
            run_id = self._q.get()
            if run_id is None:
                return
            self.current = run_id
            try:
                self.process(run_id)
            except Exception:
                self.log(f"{run_id}: chain raised:\n{traceback.format_exc()}")
            finally:
                self.current = None

    # ---- the chain ------------------------------------------------------ #
    def process(self, run_id: str) -> R.Run:
        run = self.store.get(run_id)

        if run.state == R.STOPPED:
            run = self._qc(run)
        if run.state == R.QC:
            run = self._strip(run)
        if run.state == R.STRIPPED:
            run = self.store.transition(run.run_id, R.UPLOAD_PENDING,
                                        detail="ready to upload")
        if run.state == R.UPLOAD_PENDING:
            run = self._upload(run)
        return run

    def _qc(self, run: R.Run) -> R.Run:
        """Check the feature cache exists. This does NOT compute it.

        Computing the ladder cache takes tens of minutes on a 24 h recording and
        needs a cohort spec that only a person can supply, so it is not something
        to do silently behind someone's back. The chain refuses and says exactly
        which command to run.

        THE OVERRIDE IS PER-RUN AND RECORDED ON THE RUN. An earlier version
        flipped `self.require_qc_bundle` on the shared worker, which silently
        disabled the guard for EVERY subsequent run until the service restarted,
        and left no trace that it had happened. A guard that one click can switch
        off for the whole lab, invisibly, is not a guard. The override now lives
        in the run's own results, so it applies to exactly one recording and the
        run record says plainly that the data travelled without its floor.
        """
        present = has_qc_bundle(run.base_name or "")
        if present:
            self.log(f"{run.run_id}: QC bundle present")
            return self.store.transition(run.run_id, R.QC, detail="QC bundle present",
                                         results={"qc_bundle": str(qc_cache_path(run.base_name))})

        override = bool((run.results or {}).get("skip_qc_bundle"))
        if override or not self.require_qc_bundle:
            self.log(f"{run.run_id}: WARNING, proceeding WITHOUT a QC bundle. This "
                     "recording's wire-free floor will not survive the strip.")
            return self.store.transition(
                run.run_id, R.QC,
                detail="no QC bundle -- EXPLICITLY OVERRIDDEN for this run",
                results={"qc_bundle": None, "qc_bundle_skipped": True})

        # A recording too short to clear rung 2's unbroken-block bar cannot
        # produce a meaningful ladder anyway, so say so rather than sending
        # someone off to run a command that will not help them.
        short = ""
        dur_s = _duration_s(run)
        if dur_s is not None and dur_s < 15 * 60:
            short = (f" NOTE: this recording is only {dur_s / 60:.1f} min long, which "
                     "is below the 15 min unbroken-block bar the verdict ladder gates "
                     "on, so a QC bundle for it would not be meaningful. If this was a "
                     "test, either abandon the run or strip it with the override.")
        msg = (
            f"no QC bundle for {run.base_name}. Stripping removes the in-file "
            "wire-free floor, after which core/criteria.py can never judge this "
            "recording again, so the cached features are the only surviving "
            f"record of it.{short} Compute it with:\n"
            f"  cd {ANALYSIS} && PYTHONPATH=. {PYTHON} cards/ladder.py "
            f"{run.base_name} --cohort <id> --cache {qc_cache_path(run.base_name)}")
        self.log(f"{run.run_id}: HELD -- {msg}")
        return self.store.fail(run.run_id, "QC", msg)

    def _strip(self, run: R.Run) -> R.Run:
        self.log(f"{run.run_id}: stripping {run.base_name} "
                 f"-> {len(run.keep_labels)} channels")
        self.store.transition(run.run_id, R.STRIPPING, detail="strip_channels")
        try:
            rep = strip(run, progress=self.log)
        except Exception as exc:
            self.log(f"{run.run_id}: STRIP FAILED -- {exc}")
            return self.store.fail(run.run_id, "STRIP", str(exc))
        plan = rep.get("plan", {})
        self.log(f"{run.run_id}: stripped, {plan.get('saving_pct')}% smaller")
        return self.store.transition(
            run.run_id, R.STRIPPED, detail="verified bit-exact",
            results={"strip": {"dst_base": rep.get("dst_base"),
                               "saving_pct": plan.get("saving_pct"),
                               "bytes_out": plan.get("bytes_out"),
                               "dataset_checksum": rep.get("dataset_checksum")}})

    def _upload(self, run: R.Run) -> R.Run:
        st = nas_upload.nas_status()
        if not st["ok"]:
            # NOT a failure. The run rests here and the next sweep retries.
            self.log(f"{run.run_id}: NAS unavailable ({st.get('hint')}); "
                     "staying in UPLOAD_PENDING")
            return run
        dst = (run.results.get("strip") or {}).get("dst_base")
        if not dst:
            return self.store.fail(run.run_id, "UPLOAD",
                                   "no stripped output recorded for this run")
        self.store.transition(run.run_id, R.UPLOADING, detail="uploading")
        qc = run.results.get("qc_bundle")
        try:
            summary = nas_upload.upload_recording(
                dst, run.owner, run_json=run.to_dict(),
                qc_bundle=[qc] if qc else (), progress=self.log)
        except nas_upload.UploadRefused as exc:
            self.log(f"{run.run_id}: upload refused ({exc}); back to UPLOAD_PENDING")
            return self.store.transition(run.run_id, R.UPLOAD_PENDING,
                                         detail=f"refused: {exc}")
        except Exception as exc:
            self.log(f"{run.run_id}: UPLOAD FAILED -- {exc}")
            return self.store.fail(run.run_id, "UPLOAD", str(exc))
        if summary["status"] != "VERIFIED":
            return self.store.fail(
                run.run_id, "UPLOAD",
                f"{summary['files_size_only']} file(s) were SIZE_ONLY, not verified")
        self.log(f"{run.run_id}: DONE -> {summary['dest']}")
        return self.store.transition(run.run_id, R.DONE, detail="uploaded and verified",
                                     results={"upload": summary})
