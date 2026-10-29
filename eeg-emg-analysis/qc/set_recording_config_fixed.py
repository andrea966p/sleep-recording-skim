"""Set the Allego recording config (base name "allego", path = the raw root, split per port).

Thin wrapper over `AllegoClient.update_recording_config()` of radiens-core 0.1.2 (ported 2026-10-28).
The old reason for this file is gone: with radiens 4.0.0, `set_recording_config()` could not serialise
(ConfigRecording's required `recordingType` enum was never set), so this script built the gRPC message
by hand. The new client does it properly, so prefer calling `update_recording_config()` directly;
this stays only so old notes and habits keep working. `qc/start_recording_at.py` sets the same config
itself.

`split_files_by_port=True` is the permanent setting (Andrea, 2026-10-28). Allego REFUSES a config change
while any port records ("No setting file name while recording is on"), so this exits without changing
anything in that case.
"""
import sys

from radiens_core import AllegoClient

from core import paths as PATHS
DEST = str(PATHS.RAW_ROOT)

c = AllegoClient()
if c.get_status().recording.record_mode.name == "ON":
    sys.exit("refusing: a port is recording and Allego will not change the recording config now")
cfg = c.get_recording_config()
c.update_recording_config(cfg.model_copy(update={
    "base_file_name": "allego", "base_file_path": DEST, "datasource_idx": 0, "time_stamp": True,
    "split_files_by_port": True, "force_start_at_tstamp_0": False}))
print("record cfg now:", c.get_recording_config())
