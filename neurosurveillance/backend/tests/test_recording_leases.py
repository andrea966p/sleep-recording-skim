"""Behavioural tests for the recording lease model. No MQTT, no Frigate."""
import sys, threading, time
sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parent.parent))

from frigate_controller import FrigateController, LEASE_SESSION, LEASE_MANUAL

published = []

def make():
    c = FrigateController(mqtt_host="x", mqtt_port=1, frigate_url="http://x")
    c.set_recording = lambda cam, enabled: (published.append((cam, enabled)), True)[1]
    c.drain_seconds = 0.2  # keep tests fast
    return c

def check(name, cond):
    print(f"{'PASS' if cond else 'FAIL'}  {name}")
    return cond

ok = True

# 1. Single holder: acquire turns ON, release turns OFF.
published.clear(); c = make()
c.acquire_lease("cam", LEASE_SESSION)
c.release_lease("cam", LEASE_SESSION)
ok &= check("single holder ON then OFF", published == [("cam", True), ("cam", False)])

# 2. Two holders: second acquire does NOT republish; first release does NOT stop.
published.clear(); c = make()
c.acquire_lease("cam", LEASE_MANUAL)
c.acquire_lease("cam", LEASE_SESSION)
ok &= check("second acquire is silent", published == [("cam", True)])
c.release_lease("cam", LEASE_SESSION)
ok &= check("release with other holder does NOT stop", published == [("cam", True)])
c.release_lease("cam", LEASE_MANUAL)
ok &= check("last release stops", published == [("cam", True), ("cam", False)])

# 3. THE KEY ONE: an EEG session must never stop a human's manual recording.
published.clear(); c = make()
c.adopt_lease("cam", LEASE_MANUAL)          # human already recording
c.acquire_lease("cam", LEASE_SESSION)       # EEG session starts
c.release_lease("cam", LEASE_SESSION)       # EEG session ends
ok &= check("EEG end does NOT stop manual recording", published == [])
ok &= check("manual lease survives", c.has_lease("cam", LEASE_MANUAL))

# 4. Acquire DURING the drain must cancel the pending OFF.
published.clear(); c = make(); c.drain_seconds = 1.0
t = threading.Thread(target=c.release_lease, args=("cam", LEASE_SESSION))
c.acquire_lease("cam", LEASE_SESSION)
published.clear()
t.start(); time.sleep(0.3)
c.acquire_lease("cam", LEASE_MANUAL)   # sneaks in mid-drain
t.join()
ok &= check("acquire during drain cancels OFF", published == [])

# 5. Drain actually blocks for drain_seconds.
published.clear(); c = make(); c.drain_seconds = 0.5
c.acquire_lease("cam", LEASE_SESSION); published.clear()
t0 = time.time(); c.release_lease("cam", LEASE_SESSION); dt = time.time() - t0
ok &= check(f"drain blocks ~0.5s (got {dt:.2f}s)", 0.45 <= dt <= 0.9)
ok &= check("OFF published after drain", published == [("cam", False)])

# 6. shutdown_event during drain => LEAVE RECORDING ON (fail-ON).
published.clear(); c = make(); c.drain_seconds = 2.0
ev = threading.Event()
c.acquire_lease("cam", LEASE_SESSION); published.clear()
threading.Timer(0.2, ev.set).start()
c.release_lease("cam", LEASE_SESSION, shutdown_event=ev)
ok &= check("shutdown mid-drain leaves recording ON", published == [])

# 7. Releasing a lease you never held is a no-op.
published.clear(); c = make()
c.release_lease("cam", LEASE_SESSION)
ok &= check("release of unheld lease is a no-op", published == [])

# 8. drain=False skips the wait (manual UI path, tail already lost upstream).
published.clear(); c = make(); c.drain_seconds = 5.0
c.adopt_lease("cam", LEASE_MANUAL); published.clear()
t0 = time.time(); c.release_lease("cam", LEASE_MANUAL, drain=False); dt = time.time() - t0
ok &= check(f"drain=False returns immediately ({dt:.2f}s)", dt < 0.2 and published == [("cam", False)])

print("\nALL PASS" if ok else "\nFAILURES PRESENT")
sys.exit(0 if ok else 1)
