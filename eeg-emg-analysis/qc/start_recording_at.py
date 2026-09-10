"""Start an Allego recording at an exact wall-clock time.

Waits until the target time, sets the recording configuration with the workaround for the broken
library call, turns streaming on, starts the recording, then VERIFIES by watching the destination
directory rather than by trusting the client.

⚠️ set_recording_config() in the radiens client is broken: ConfigRecording has a required
recordingType enum that the library never sets, so the message fails to serialise. This builds
the message directly.

⚠️ get_status().recording.path reports the CLIENT PROCESS'S CURRENT WORKING DIRECTORY, not the
output directory. The only reliable check is that _data.xdat grows in the destination.

Usage:
  python start_recording_at.py HH:MM[:SS]        # today, local time
"""
import os, sys, time, glob
from datetime import datetime, timedelta

import grpc
import radiens.utils.interceptors as itc
from radiens.allego_client import AllegoClient
from radiens.grpc_radiens import allegoserver_pb2 as ap, allegoserver_pb2_grpc as ag

from core import paths as PATHS
DEST = str(PATHS.RAW_ROOT)

parts = [int(p) for p in sys.argv[1].split(":")]
while len(parts) < 3:
    parts.append(0)
now = datetime.now()
target = now.replace(hour=parts[0], minute=parts[1], second=parts[2], microsecond=0)
if target < now:
    target += timedelta(days=1)
print(f"now {now:%H:%M:%S}, target {target:%Y-%m-%d %H:%M:%S}, "
      f"waiting {(target-now).total_seconds():.0f} s", flush=True)

# configure early so the only thing left at the target instant is the start call
c = AllegoClient(); c.get_status()
chan = grpc.intercept_channel(
    grpc.insecure_channel("127.0.0.1:50051"),
    itc.MetadataClientInterceptor(id_token=itc.SessionMetaData._instance._id_token))
stub = ag.AllegoCoreStub(chan)
stub.SetConfigRecording(ap.ConfigRecording(
    baseFileName="allego", baseFilePath=DEST, dataSourceIdx=0, timeStamp=True,
    splitFilesByPort=False, forceStartAtTStamp0=False, recordingType=ap.continuous), timeout=60)
print("recording config set", flush=True)

# streaming on 20 s early so the amplifiers are settled at the target instant
while (target - datetime.now()).total_seconds() > 20:
    time.sleep(1)
c.set_streaming("on")
print(f"{datetime.now():%H:%M:%S} streaming on", flush=True)

while datetime.now() < target:
    time.sleep(0.05)
c.set_recording("on")
t0 = datetime.now()
print(f"{t0:%H:%M:%S.%f} set_recording('on') returned", flush=True)

time.sleep(5)
s = c.get_status()
name = s.recording.file_name
print(f"mode={s.recording.mode}  file={name}", flush=True)

path = os.path.join(DEST, name + "_data.xdat")
a = os.path.getsize(path) if os.path.exists(path) else -1
time.sleep(40)
b = os.path.getsize(path) if os.path.exists(path) else -1
print(f"VERIFY on disk: {path}")
print(f"  {a} -> {b} bytes in 40 s  ({(b-a)/40*3600/1e9:.2f} GB/h)")
print("RECORDING CONFIRMED GROWING" if b > a > -1 else "🔴 NOT GROWING, INVESTIGATE")
