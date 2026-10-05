"""Impedance duty-cycle block, PORT-AGNOSTIC variant of qc/sweep_block_all_ports.py (2026-10-01).

Sites come from the live channel table, so a 2-port rig gives 128 sites, not a KeyError.
Every sweep is written to its own CSV, plus one _census_log.tsv for the block; score the block
with qc/block_duty_cycle_slots.py, which takes n from that log.

🔑 Impedance is refused while streaming ("Z_measure attempted during data acq"): stop the stream
first, restart it afterwards, and check the stream rate (~1.0x real time) before recording.

Channel roles depend on the cohort:
  --roles eeg,emg        2 ch per mouse: /1 /2 and /33 /34
  --roles eeg,emg,ecg    3 ch per mouse: /1 /2 /3 and /33 /34 /35
A 128-site sweep takes ~30 s.

Hardened 2026-10-02 after a code review:
  * Each site is labelled from the channel table's OWN columns (ntv_key_idx -> port/site_num),
    not from its row position plus a counter. radiens never re-sorts that table, so a non-native
    row order or a non-passthrough sensor map would otherwise mislabel every row silently
    (cf. vault eight-mouse-acquisition-setup.md, "sites 33-36" landing on natives 28-31).
  * --slots is validated (A-H then 1 or 2) and every watched site must exist BEFORE the first RPC.
  * A reply missing a native index writes NaN for that site instead of crashing after the CSV.
  * An outdir that already holds a block is refused unless --append is given; --append requires
    the same log header and continues the sweep numbering, so sweep numbers never repeat.
  * BLOCK DONE reports the sweeps actually written, not the number requested.

Usage:
  /opt/neurosurveillance/venv/bin/python3 qc/sweep_block_ports.py OUTDIR N CADENCE CONFIG \\
      [--roles eeg,emg] [--slots A1,A2,B1,B2] [--append]
"""
import argparse, csv, glob, math, os, re, sys, time
from datetime import datetime

LOG_NAME = "_census_log.tsv"


def site_map(rows):
    """{ntv_key_idx: 'A/1', ...} from channel-table rows (dicts with ntv_chan_name, ntv_key_idx,
    port, site_num). Amplifier rows only. Refuses duplicate labels or duplicate native indices."""
    out = {}
    for r in rows:
        if not str(r["ntv_chan_name"]).startswith("port_"):
            continue
        ntv, label = int(r["ntv_key_idx"]), f"{r['port']}/{int(r['site_num'])}"
        if ntv in out:
            raise ValueError(f"native index {ntv} appears twice in the channel table")
        out[ntv] = label
    if len(set(out.values())) != len(out):
        raise ValueError("two native indices map to the same site label")
    return out


def parse_slots(spec, ports):
    """'A1,B2' -> [('A1','A',1), ('B2','B',2)]; default every attached port x slots 1, 2."""
    if not spec:
        return [(f"{p}{k}", p, k) for p in sorted(ports) for k in (1, 2)]
    out = []
    for lab in spec.split(","):
        m = re.fullmatch(r"([A-H])([12])", lab.strip().upper())
        if not m:
            raise ValueError(f"bad slot {lab!r}: expected a port letter A-H and slot 1 or 2, e.g. A1,B2")
        out.append((m.group(0), m.group(1), int(m.group(2))))
    return out


def animals(slots, roles):
    """[(label, [(role, site), ...]), ...]: slot 1 uses /1.., slot 2 /33.."""
    return [(lab, [(role, f"{p}/{(1 if k == 1 else 33) + i}") for i, role in enumerate(roles)])
            for lab, p, k in slots]


def sweep_table(vals, ntv2site):
    """(site, mag MOhm, phase deg) for every site in native order; NaN where the reply lacks it."""
    nan = (float("nan"), float("nan"))
    return [(ntv2site[n],) + vals.get(n, nan) for n in sorted(ntv2site)]


def log_header(watch):
    return "sweep\tclock\t" + "\t".join(f"{s}_Z\t{s}_ph" for s in watch) + "\n"


def prepare_outdir(outdir, header, append):
    """Return the first sweep number to use. Refuses to mix two blocks in one folder."""
    os.makedirs(outdir, exist_ok=True)
    logp = os.path.join(outdir, LOG_NAME)
    existing = os.path.exists(logp) or glob.glob(os.path.join(outdir, "imp_*.csv"))
    if not existing:
        return 1
    if not append:
        raise SystemExit(f"{outdir} already holds a block; use a new folder, or --append to extend it")
    with open(logp, encoding="utf-8") as fh:
        lines = fh.readlines()
    if not lines or lines[0] != header:
        raise SystemExit("--append: the existing log has a different header (other slots/roles)")
    last = max((int(l.split("\t", 1)[0]) for l in lines[1:] if l.strip()), default=0)
    return last + 1


def state_char(mag):
    """C = connected at the 0.5 MOhm criterion, o = open, ? = missing from the reply."""
    return "?" if math.isnan(mag) else ("C" if mag < 0.5 else "o")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("outdir")
    ap.add_argument("n", type=int)
    ap.add_argument("cadence", type=float)
    ap.add_argument("config", help="config string embedded in every filename")
    ap.add_argument("--roles", default="eeg,emg,ecg")
    ap.add_argument("--slots", default="", help="occupied slots, e.g. A1,A2,B1,B2")
    ap.add_argument("--append", action="store_true", help="extend an existing block in OUTDIR")
    args = ap.parse_args()
    roles = [r.strip().lower() for r in args.roles.split(",")]

    import grpc, radiens.utils.interceptors as itc
    from radiens.allego_client import AllegoClient
    from radiens.grpc_radiens import allegoserver_pb2_grpc as ag, common_pb2 as cm, datasource_pb2 as ds

    client = AllegoClient(); client.get_status()
    table = client.get_channel_metadata().table
    ntv2site = site_map(r for _, r in table.iterrows())
    site2ntv = {s: n for n, s in ntv2site.items()}
    ports = {s.split("/")[0] for s in site2ntv}
    try:
        slots = parse_slots(args.slots, ports)
    except ValueError as exc:
        sys.exit(str(exc))
    anim = animals(slots, roles)
    watch = [s for _, chans in anim for _, s in chans]
    missing = [s for s in watch if s not in site2ntv]
    if missing:
        sys.exit(f"watched site(s) not in the channel table: {', '.join(missing)} "
                 f"(attached ports: {', '.join(sorted(ports))})")
    header = log_header(watch)
    first = prepare_outdir(args.outdir, header, args.append)
    print("ports", sorted(ports), "sites", len(ntv2site), "watching", watch, flush=True)

    channel = grpc.intercept_channel(
        grpc.insecure_channel("127.0.0.1:50051"),
        itc.MetadataClientInterceptor(id_token=itc.SessionMetaData._instance._id_token))
    stub = ag.AllegoCoreStub(channel)
    log = open(os.path.join(args.outdir, LOG_NAME), "a", buffering=1)
    if log.tell() == 0:
        log.write(header)

    written = 0
    for n in range(first, first + args.n):
        t0 = time.time(); stamp = datetime.now()
        try:
            reply = stub.GetIntanImpedance(ds.ImpedanceRequest(port=cm.B), timeout=600)
        except grpc.RpcError as exc:
            print(f"[{n:02d}] RPC FAILED {exc.code()} {exc.details()}", flush=True)
            time.sleep(max(0.0, args.cadence - (time.time() - t0))); continue
        vals = {x.ntvChanIdx: (x.zMag / 1e6, x.zPhase) for x in reply.impedances}
        if set(vals) != set(ntv2site):
            print(f"[{n:02d}] WARNING reply has {len(vals)} native indices, table has {len(ntv2site)} "
                  f"({len(set(ntv2site) - set(vals))} missing -> NaN)", flush=True)
        rows = sweep_table(vals, ntv2site)
        by_site = {s: (m, p) for s, m, p in rows}
        row = [str(n), stamp.strftime("%H:%M:%S")]
        for s in watch:
            m, p = by_site[s]; row += [f"{m:.4f}", f"{p:.2f}"]
        brief = [f"{lab}:" + "".join(state_char(by_site[s][0]) for _, s in chans) for lab, chans in anim]
        name = f"imp_{stamp:%Y-%m-%d}_{stamp:%H%M%S}_{args.config}_census-{n:03d}.csv"
        with open(os.path.join(args.outdir, name), "w", newline="", encoding="utf-8") as fh:
            w = csv.writer(fh); w.writerow(["SITE", "MAGNITUDE (MΩ)", "PHASE (°)"])
            for s, m, p in rows:
                w.writerow([s, f"{m:.6f}", f"{p:.4f}"])
        log.write("\t".join(row) + "\n")
        written += 1
        print(f"[{n:02d}] {stamp:%H:%M:%S} {(time.time()-t0):5.1f}s  " + " ".join(brief), flush=True)
        if n < first + args.n - 1:
            time.sleep(max(0.0, args.cadence - (time.time() - t0)))
    print(f"BLOCK DONE: {written} of {args.n} sweeps written, roles={'/'.join(roles)}", flush=True)


if __name__ == "__main__":
    main()
