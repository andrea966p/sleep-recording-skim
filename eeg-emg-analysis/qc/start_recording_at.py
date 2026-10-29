"""Start an Allego recording at an exact wall-clock time, one file per port.

Waits until the target time, sets the recording configuration, turns streaming on, starts the
recording on each requested port, then VERIFIES by watching the destination directory rather than
by trusting the client.

Ported 2026-10-28 from the old `radiens` 4.0.0 client to `radiens-core` 0.1.2 (Allego 4.1.2). What
changed and why:
  * `set_recording_config()` used to be broken, so this script built the raw gRPC message. The new
    client has `update_recording_config()`; the raw gRPC, the id-token interceptor and every
    `radiens` import are gone (the old package cannot authenticate to Allego 4 and cannot be loaded
    next to `radiens_core`).
  * Recording is PER PORT now (measured 2026-10-28): `start_recording(port="a")`. With
    `split_files_by_port=True`, the permanent setting, the files are
    `<dir>/allego_port<X>_<N>__uid<MMDD-HH-MM-SS>_data.xdat`, one per recording port.
  * `get_status().recording.active_filename` is NOT per port, so it is not used to find files: the
    newest `*_port<X>_*_data.xdat` of each port in the destination is.
  * `update_recording_config()` is REFUSED while any port records. If another port is recording the
    config is only VERIFIED (path and split), and the script refuses when it differs.
  * A second `start_recording(port=X)` on a port that is already ON is silently accepted and makes no
    new file, so a requested port that is already ON makes this script refuse.
  * File size lags ~30 s (0 bytes at +3 s), hence the 40 s verification window.

Usage:
  python start_recording_at.py HH:MM[:SS] [--ports A,B,C,D]   # today, local time; default: every
                                                              # port the rig reports channels on
"""
import argparse
import os
import sys
import time
import glob
from datetime import datetime, timedelta

from radiens_core import AllegoClient

from core import paths as PATHS
DEST = str(PATHS.RAW_ROOT)
BASE_NAME = "allego"

ap = argparse.ArgumentParser()
ap.add_argument("target", help="HH:MM[:SS], local time")
ap.add_argument("--ports", default="", help="comma separated port letters; default every port with channels")
args = ap.parse_args()

parts = [int(p) for p in args.target.split(":")]
while len(parts) < 3:
    parts.append(0)
now = datetime.now()
target = now.replace(hour=parts[0], minute=parts[1], second=parts[2], microsecond=0)
if target < now:
    target += timedelta(days=1)
print(f"now {now:%H:%M:%S}, target {target:%Y-%m-%d %H:%M:%S}, "
      f"waiting {(target-now).total_seconds():.0f} s", flush=True)

c = AllegoClient()
s0 = c.get_status()
rig_ports = [p.port.name for p in s0.ports if p.channel_count > 0]
ports = [p.strip().upper() for p in args.ports.split(",") if p.strip()] or rig_ports
bad = [p for p in ports if p not in rig_ports]
if not ports or bad:
    sys.exit(f"refusing: port(s) {bad or ports} not reported with channels by Allego (rig has {rig_ports})")


def port_mode(status, letter):
    return getattr(status.recording, "record_mode_port_" + letter.lower())


already = [p for p in ports if port_mode(s0, p) is not None and port_mode(s0, p).name == "ON"]
if already:
    sys.exit(f"refusing: port(s) {already} already recording; a second start would be silently ignored")

# configure early so the only thing left at the target instant is the start call
cfg = c.get_recording_config()
if s0.recording.record_mode.name == "ON":
    # Another port records: Allego refuses a config change now, so only VERIFY.
    if os.path.realpath(cfg.base_file_path) != os.path.realpath(DEST) or not cfg.split_files_by_port:
        sys.exit(f"refusing: another port is recording with path={cfg.base_file_path!r} "
                 f"split={cfg.split_files_by_port}, expected {DEST!r} split=True and the config cannot "
                 "be changed while a port records")
    print("recording config verified (another port is recording)", flush=True)
else:
    os.makedirs(DEST, exist_ok=True)
    c.update_recording_config(cfg.model_copy(update={
        "base_file_name": BASE_NAME, "base_file_path": DEST, "datasource_idx": 0, "time_stamp": True,
        "split_files_by_port": True, "force_start_at_tstamp_0": False}))
    print("recording config set", flush=True)

# streaming on 20 s early so the amplifiers are settled at the target instant
while (target - datetime.now()).total_seconds() > 20:
    time.sleep(1)
if c.get_status().streaming.stream_mode.name != "ON":
    c.start_streaming()
print(f"{datetime.now():%H:%M:%S} streaming on", flush=True)

while datetime.now() < target:
    time.sleep(0.05)
# s0 may be hours old (the script waits for the target): re-read just before starting.
s1 = c.get_status()
already = [p for p in ports if port_mode(s1, p) is not None and port_mode(s1, p).name == "ON"]
if already:
    sys.exit(f"refusing: port(s) {already} started recording while this script waited")
t0 = datetime.now()
t0_epoch = time.time()
started = []
try:
    for p in ports:
        c.start_recording(port=p)
        started.append(p)
except Exception as exc:
    # Do not leave a half-started set running: stop only the ports THIS script started.
    for p in started:
        try:
            c.stop_recording(port=p)
        except Exception as stop_exc:
            print(f"WARNING: could not stop port {p}: {stop_exc}", flush=True)
    sys.exit(f"start_recording failed after ports {started}: {exc}")
print(f"{t0:%H:%M:%S.%f} start_recording returned for ports {','.join(started)}", flush=True)

time.sleep(5)
s = c.get_status()
print(f"mode={s.recording.record_mode.name}  ports=" +
      ",".join(f"{p}:{port_mode(s, p).name if port_mode(s, p) is not None else '?'}" for p in ports), flush=True)


def newest(letter):
    """Newest data file of one port created at or after the start call, or None."""
    files = [f for f in glob.glob(os.path.join(DEST, f"{BASE_NAME}_port{letter}_*_data.xdat"))
             if os.path.getmtime(f) >= t0_epoch - 2]
    return max(files, key=os.path.getmtime) if files else None


paths = {p: newest(p) for p in ports}
for p, f in paths.items():
    print(f"  port {p}: {os.path.basename(f) if f else 'NO FILE YET'}", flush=True)


def size(f):
    return os.path.getsize(f) if f and os.path.exists(f) else -1


# a file that does not exist yet (size lags ~30 s) has baseline 0, not -1, so a healthy port is not failed
a = {p: max(0, size(f)) for p, f in paths.items()}
time.sleep(40)
paths = {p: (f or newest(p)) for p, f in paths.items()}
b = {p: size(f) for p, f in paths.items()}
total = 0
ok = True
for p in ports:
    grew = b[p] > a[p]
    ok = ok and grew
    total += max(0, b[p] - a[p])
    print(f"VERIFY port {p}: {paths[p]}")
    print(f"  {a[p]} -> {b[p]} bytes in 40 s  ({(b[p]-a[p])/40*3600/1e9:.2f} GB/h)  "
          f"{'growing' if grew else 'NOT GROWING'}")
print(f"VERIFY total ({total/40*3600/1e9:.2f} GB/h)")
first = next((f for f in paths.values() if f), None)
if first:
    # the arm name for the watchdog: the first port's file, without _data.xdat (console base_name rule)
    print(f"mode={s.recording.record_mode.name}  file={os.path.basename(first)[:-len('_data.xdat')]}", flush=True)
if not ok:
    # Do not leave unverified ports recording: stop the ports THIS run started.
    for p in started:
        try:
            c.stop_recording(port=p)
        except Exception as stop_exc:
            print(f"WARNING: could not stop port {p}: {stop_exc}", flush=True)
    print("stopped the ports this run started", flush=True)
print("RECORDING CONFIRMED GROWING" if ok else "🔴 NOT GROWING, INVESTIGATE")
sys.exit(0 if ok else 1)
