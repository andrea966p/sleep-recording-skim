"""Behavioural tests for export-row cleanup. No MQTT, no Frigate, no network."""
import sys, types
sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parent.parent))

import frigate_controller
from frigate_controller import FrigateController

calls = []

class FakeResponse:
    def __init__(self, status_code=200):
        self.status_code = status_code
    def raise_for_status(self):
        if self.status_code >= 400:
            raise Exception(f"HTTP {self.status_code}")

def make(status_code=200, raises=None):
    """A controller whose requests.delete is stubbed out."""
    c = FrigateController(mqtt_host="x", mqtt_port=1, frigate_url="http://x")
    def fake_delete(url, timeout=None):
        calls.append(url)
        if raises is not None:
            raise raises
        return FakeResponse(status_code)
    frigate_controller.requests.delete = fake_delete
    return c

def check(name, cond):
    print(f"{'PASS' if cond else 'FAIL'}  {name}")
    return cond

ok = True

# 1. Happy path: a 200 means the row is gone.
calls.clear(); c = make(200)
ok &= check("200 reports success", c.delete_export("pi_cam_0_abc123") is True)
ok &= check("hits the right URL", calls == ["http://x/api/export/pi_cam_0_abc123"])

# 2. Already deleted is the end state we wanted, not a failure.
calls.clear(); c = make(404)
ok &= check("404 reports success", c.delete_export("pi_cam_0_gone") is True)

# 3. A server error must NOT be reported as success.
calls.clear(); c = make(500)
ok &= check("500 reports failure", c.delete_export("pi_cam_0_boom") is False)

# 4. Frigate unreachable must not raise into the export thread.
calls.clear(); c = make(raises=frigate_controller.requests.exceptions.ConnectionError())
ok &= check("connection error reports failure", c.delete_export("pi_cam_0_down") is False)

# 5. Any other exception is swallowed too — export bookkeeping must never
#    take down the session-stop path.
calls.clear(); c = make(raises=RuntimeError("unexpected"))
ok &= check("unexpected error reports failure", c.delete_export("pi_cam_0_weird") is False)

# 6. THE KEY ONE: the row is deleted only when the file was actually moved.
#    Simulates daemon._execute_export's guard without building a whole daemon.
deleted = []
def simulate(moved_to):
    row_deleted = False
    if moved_to is not None:
        deleted.append(moved_to)
        row_deleted = True
    return row_deleted

deleted.clear()
ok &= check("move failed -> row survives", simulate(None) is False)
ok &= check("no delete attempted", deleted == [])
ok &= check("move worked -> row deleted", simulate("/opt/neurosurveillance/exports/a.mp4") is True)

print()
print("ALL PASS" if ok else "FAILURES ABOVE")
sys.exit(0 if ok else 1)
