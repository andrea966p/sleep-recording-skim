"""Re-derive ntvChanIdx -> site label from the live channel metadata table.

MUST be run after any port/headstage change. ntvChanIdx is global, so adding a
port shifts every downstream index and would silently mislabel every file.
"""
from radiens.allego_client import AllegoClient

c = AllegoClient()
c.get_status()
t = c.get_channel_metadata().table
amp = t[t["ntv_chan_name"].astype(str).str.startswith("port_")]

per_port = {}
for _, r in amp.iterrows():
    per_port.setdefault(str(r["port"]), []).append(str(r["ntv_chan_name"]))

print("ports present:", sorted(per_port))
for p in sorted(per_port):
    print(f"  port {p}: {len(per_port[p])} amp channels")

# global ntv index -> label, in table order
sites = []
counters = {}
for _, r in amp.iterrows():
    p = str(r["port"])
    counters[p] = counters.get(p, 0) + 1
    sites.append(f"{p}/{counters[p]}")

print("\nSITES total:", len(sites))
for i in (0, 1, 2, 31, 32, 33, 63, 64, 65):
    if i < len(sites):
        print(f"  ntv{i:<3} -> {sites[i]}")
print("\nSITES = " + repr(sites[:4]) + " ... " + repr(sites[-2:]))
