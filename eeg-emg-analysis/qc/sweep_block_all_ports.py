"""Impedance duty-cycle block, 8 slots, 4 ports with splitters, 256 ch.

Map verified by remap_channels.py: ntv 0-63 -> A/1..A/64, 64-127 -> B, 128-191 -> C,
192-255 -> D. Slot 1 of a port = /1 /2 /3; slot 2 = /33 /34 /35.

Channel roles depend on the cohort:
  --roles eeg,emg        2 ch per mouse: /1 /2 and /33 /34   (cohort up to 2026-08-06)
  --roles eeg,emg,ecg    3 ch per mouse: /1 /2 /3 and /33 /34 /35  (ECG cohort, 2026-08-07 on)

Every sweep is written to its own CSV, plus one _census_log.tsv for the block.
Sweeps run back to back; a 256 ch sweep takes ~31 s.

Usage:
  python sweep_block_all_ports.py OUTDIR N CADENCE CONFIG [--roles eeg,emg,ecg]
"""
import argparse, csv, os, time
from datetime import datetime
import grpc, radiens.utils.interceptors as itc
from radiens.allego_client import AllegoClient
from radiens.grpc_radiens import allegoserver_pb2_grpc as ag, common_pb2 as cm, datasource_pb2 as ds

ap = argparse.ArgumentParser()
ap.add_argument("outdir")
ap.add_argument("n", type=int)
ap.add_argument("cadence", type=float)
ap.add_argument("config", help="config string embedded in every filename")
ap.add_argument("--roles", default="eeg,emg,ecg")
args = ap.parse_args()

ROLES = [r.strip().lower() for r in args.roles.split(",")]
NROLE = len(ROLES)

SITES = [f"{p}/{i}" for p in "ABCD" for i in range(1, 65)]
# (mouse label, [(role, site), ...]) for both slots of every port
ANIMALS = [
    (f"{p}{slot}", [(ROLES[k], f"{p}/{base + k}") for k in range(NROLE)])
    for p in "ABCD"
    for slot, base in ((1, 1), (2, 33))
]
WATCH = [s for _, chans in ANIMALS for _, s in chans]

client = AllegoClient(); client.get_status()
channel = grpc.intercept_channel(
    grpc.insecure_channel("127.0.0.1:50051"),
    itc.MetadataClientInterceptor(id_token=itc.SessionMetaData._instance._id_token))
stub = ag.AllegoCoreStub(channel)

os.makedirs(args.outdir, exist_ok=True)
log = open(os.path.join(args.outdir, "_census_log.tsv"), "a", buffering=1)
if log.tell() == 0:
    log.write("sweep\tclock\t" + "\t".join(f"{s}_Z\t{s}_ph" for s in WATCH) + "\n")

for n in range(1, args.n + 1):
    t0 = time.time(); stamp = datetime.now()
    try:
        reply = stub.GetIntanImpedance(ds.ImpedanceRequest(port=cm.B), timeout=600)
    except grpc.RpcError as exc:
        print(f"[{n:02d}] RPC FAILED {exc.code()} {exc.details()}", flush=True)
        time.sleep(max(0.0, args.cadence - (time.time() - t0))); continue

    vals = {x.ntvChanIdx: (x.zMag / 1e6, x.zPhase) for x in reply.impedances}
    if len(vals) != 256:
        print(f"[{n:02d}] WARNING n={len(vals)}, expected 256", flush=True)

    name = f"imp_{stamp:%Y-%m-%d}_{stamp:%H%M%S}_{args.config}_census-{n:03d}.csv"
    with open(os.path.join(args.outdir, name), "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh); w.writerow(["SITE", "MAGNITUDE (MΩ)", "PHASE (°)"])
        for i, site in enumerate(SITES):
            mag, ph = vals.get(i, (float("nan"), float("nan")))
            w.writerow([site, f"{mag:.6f}", f"{ph:.4f}"])

    row = [str(n), stamp.strftime("%H:%M:%S")]; brief = []
    for label, chans in ANIMALS:
        # C = connected at the 0.5 MOhm criterion, o = open; one char per role, in role order
        state = "".join("C" if vals[SITES.index(s)][0] < 0.5 else "o" for _, s in chans)
        brief.append(f"{label}:{state}")
    for s in WATCH:
        mag, ph = vals[SITES.index(s)]; row += [f"{mag:.4f}", f"{ph:.2f}"]
    log.write("\t".join(row) + "\n")
    print(f"[{n:02d}] {stamp:%H:%M:%S} {(time.time()-t0):5.1f}s  " + " ".join(brief), flush=True)

    if n < args.n:
        time.sleep(max(0.0, args.cadence - (time.time() - t0)))
print(f"BLOCK DONE: {args.n} sweeps, roles={'/'.join(ROLES)}", flush=True)
