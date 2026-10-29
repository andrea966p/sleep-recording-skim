"""Re-derive ntvChanIdx -> site label from the live channel metadata table.

MUST be run after any port/headstage change. ntvChanIdx is global, so adding a
port shifts every downstream index and would silently mislabel every file.
"""
from radiens_core import AllegoClient
from radiens_core.models.signals import SignalType

c = AllegoClient()
c.get_status()
meta = c.get_channel_metadata()
amp = SignalType.AMP
keys = meta.sig_map[amp].ntv          # native index of each amp channel, parallel to the lists below
rows = [(int(k), port.name, name) for k, port, name in
        zip(keys, meta.ports[amp], meta.ntv_chan_names[amp]) if name.startswith("port_")]

per_port = {}
for _, p, name in rows:
    per_port.setdefault(p, []).append(name)

print("ports present:", sorted(per_port))
for p in sorted(per_port):
    print(f"  port {p}: {len(per_port[p])} amp channels")

# global ntv index -> label, keyed on the native index (not list position); sorted by it
sites = []
counters = {}
for k, p, _ in sorted(rows):
    counters[p] = counters.get(p, 0) + 1
    sites.append(f"{p}/{counters[p]}")

print("\nSITES total:", len(sites))
for i in (0, 1, 2, 31, 32, 33, 63, 64, 65):
    if i < len(sites):
        print(f"  ntv{i:<3} -> {sites[i]}")
print("\nSITES = " + repr(sites[:4]) + " ... " + repr(sites[-2:]))
