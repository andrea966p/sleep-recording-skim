#!/usr/bin/env python3
"""add_qc_to_nas_info.py -- write the ladder verdict into every info.json on the NAS.

ONE-OFF, 2026-09-30. The 64 mouse folders rebuilt on 2026-09-29 carry the CSV and
its provenance but not the QC verdict, and the CSV cannot be judged on its own: its
wire-free control inputs stayed in the raw file. This adds `qc` (see
backend/qc_info.py) from the WINDOWED cards in eeg-emg-analysis/cards/out-windows/,
which judged exactly the hours each CSV holds, and extends `pairing` with whether
the partner timepoint is scoreable too.

Only info.json is touched, never a CSV. Each original is copied to a local backup
first, the new file is written to a temporary name and renamed, then read back and
compared.

    /usr/bin/python3 eeg-recorder/deploy/add_qc_to_nas_info.py         # dry run
    /usr/bin/python3 eeg-recorder/deploy/add_qc_to_nas_info.py --go
"""
from __future__ import annotations

import argparse
import glob
import json
import os
import shutil
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "eeg-recorder" / "backend"))
import qc_info  # noqa: E402

NAS = Path("/mnt/skimnas/02_Data_Sleep/andrea")
CARDS = REPO / "eeg-emg-analysis" / "cards" / "out-windows"
COHORT = {"HLBWSD": "W-SD", "HLBSSD": "S-SD", "HLBWSL": "W-SL", "HLBSSL": "S-SL"}
BACKUP = Path.home() / "radix" / "per-mouse" / "info-json-backup-2026-09-30"


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--go", action="store_true")
    a = ap.parse_args(argv)
    if not (NAS.parent / ".skim-nas-share").is_file():
        print("REFUSED: the NAS sentinel is not readable; the share is not mounted", file=sys.stderr)
        return 1

    infos = {}
    for f in sorted(NAS.glob("*/*/*/*.info.json")):
        i = json.loads(f.read_text())
        cp = CARDS / COHORT[i["batch"]] / f"{i['allego_base']}__{i['position']}_card.json"
        card = qc_info.load_card(cp)
        if card is None:
            print(f"REFUSED: no windowed card for {f.name} at {cp}", file=sys.stderr)
            return 1
        if (card.get("window") or {}).get("start_kst", "")[:16].replace("T", " ") != \
                i["window"]["requested"]["start_kst"][:16]:
            print(f"REFUSED: {cp.name} was judged on a different window than {f.name}",
                  file=sys.stderr)
            return 1
        feats = ((card.get("provenance") or {}).get("processed_files") or {}).get("features")
        st3 = json.loads(Path(feats).read_text()) if feats and Path(feats).is_file() else None
        rungs = {r["number"]: r["verdict"] for r in card["rungs"]}
        qc = qc_info.qc_block(card, card_path=str(cp.relative_to(REPO)),
                              judged_on=f"the CSV's window, {i['window']['requested']['start_kst']} "
                                        f"-> {i['window']['requested']['end_kst']}",
                              stage3=st3 if rungs.get(3) != "PASS" else None)
        infos[i["folder"]] = (f, i, qc)

    def s3ok(q):   # scoreable by the ladder, or by stage 3 where the ladder had no verdict
        return q["verdict"] == "SCOREABLE" or (
            q["verdict"] == "NO VERDICT" and (q.get("stage3") or {}).get("verdict") == "SCOREABLE")

    print(f"{'mouse folder':28s} {'qc verdict':14s} {'partner':14s} both")
    for folder, (f, i, qc) in infos.items():
        pr = dict(i.get("pairing") or {})
        partner = (pr.get("partner") or "").rsplit("/", 1)[-1]
        pq = infos.get(partner, (None, None, None))[2]
        if pq is not None:
            pr["partner_qc_verdict"] = pq["verdict"]
            pr["scoreable_at_both"] = qc["verdict"] == "SCOREABLE" and pq["verdict"] == "SCOREABLE"
            pr["scoreable_at_both_incl_stage3"] = s3ok(qc) and s3ok(pq)
        i2 = dict(i, qc=qc, pairing=pr)
        infos[folder] = (f, i2, qc)
        both = ("YES" if pr.get("scoreable_at_both") else
                "stage3" if pr.get("scoreable_at_both_incl_stage3") else "-")
        print(f"{folder:28s} {qc['verdict']:14s} {pr.get('partner_qc_verdict', 'unpaired'):14s} {both}")

    if not a.go:
        print("\nDRY RUN. Nothing written. Re-run with --go.")
        return 0
    for folder, (f, i2, _) in infos.items():
        b = BACKUP / f.relative_to(NAS)
        b.parent.mkdir(parents=True, exist_ok=True)
        if not b.exists():
            shutil.copy2(f, b)
        tmp = f.with_name(f".{f.name}.tmp")
        tmp.write_text(json.dumps(i2, indent=2))
        os.replace(tmp, f)
        fd = os.open(f, os.O_RDONLY)
        try:
            os.posix_fadvise(fd, 0, 0, os.POSIX_FADV_DONTNEED)   # read the NAS, not the cache
        finally:
            os.close(fd)
        if json.loads(f.read_text()) != json.loads(json.dumps(i2)):
            print(f"FAILED: {f} did not read back as written", file=sys.stderr)
            return 1
    print(f"\n{len(infos)} info.json updated and read back. Originals in {BACKUP}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
