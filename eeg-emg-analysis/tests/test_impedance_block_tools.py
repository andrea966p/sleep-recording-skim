"""qc/sweep_block_ports.py (pure parts) and qc/block_duty_cycle_slots.py, hardened 2026-10-02.

No Allego, no gRPC: the sweep script's mapping/validation are pure functions, and the scorer is
run as a subprocess on a synthetic block written to tmp_path.
"""
import csv, math, os, random, subprocess, sys
from pathlib import Path

import pytest

from qc import sweep_block_ports as SB

QC = Path(__file__).resolve().parents[1] / "qc"


def rows_for(ports="AB", per_port=64, site_of=lambda i: i + 1):
    out = []
    for k, p in enumerate(ports):
        for i in range(per_port):
            out.append({"ntv_chan_name": f"port_{p}_{k * per_port + i}", "ntv_key_idx": k * per_port + i,
                        "port": p, "site_num": site_of(i)})
    out.append({"ntv_chan_name": "din_0", "ntv_key_idx": 999, "port": "A", "site_num": 1})   # not an amp
    return out


def test_site_map_is_independent_of_row_order():
    rows = rows_for(); shuffled = rows[:]; random.Random(1).shuffle(shuffled)
    assert SB.site_map(shuffled) == SB.site_map(rows)
    m = SB.site_map(rows)
    assert m[0] == "A/1" and m[32] == "A/33" and m[64] == "B/1" and len(m) == 128 and 999 not in m


def test_site_map_follows_site_num_not_position():
    # a non-passthrough map: native i carries probe site 64-i
    m = SB.site_map(rows_for(ports="A", site_of=lambda i: 64 - i))
    assert m[0] == "A/64" and m[63] == "A/1"


def test_site_map_refuses_duplicates():
    rows = rows_for(ports="A"); rows[1]["site_num"] = rows[0]["site_num"]
    with pytest.raises(ValueError):
        SB.site_map(rows)


@pytest.mark.parametrize("bad", ["A3", "B12", "a", "E", "1A", "A0"])
def test_parse_slots_refuses_aliases(bad):
    with pytest.raises(ValueError):
        SB.parse_slots(bad, {"A", "B"})


def test_parse_slots_and_animals():
    assert [s[0] for s in SB.parse_slots("a1, B2", {"A", "B"})] == ["A1", "B2"]
    assert [s[0] for s in SB.parse_slots("", {"B", "A"})] == ["A1", "A2", "B1", "B2"]
    an = SB.animals(SB.parse_slots("A2", {"A"}), ["eeg", "emg"])
    assert an == [("A2", [("eeg", "A/33"), ("emg", "A/34")])]


def test_sweep_table_writes_nan_for_missing_ntv():
    m = SB.site_map(rows_for(ports="A"))
    t = SB.sweep_table({0: (0.1, 5.0)}, m)
    assert t[0] == ("A/1", 0.1, 5.0) and math.isnan(t[1][1]) and len(t) == 64
    assert SB.state_char(float("nan")) == "?" and SB.state_char(0.1) == "C" and SB.state_char(5.0) == "o"


def test_prepare_outdir_refuses_to_mix_blocks(tmp_path):
    hdr = SB.log_header(["A/1_Z"])
    assert SB.prepare_outdir(tmp_path / "new", hdr, append=False) == 1
    d = tmp_path / "old"; d.mkdir(); (d / SB.LOG_NAME).write_text(hdr + "1\t10:00:00\t0.1\t1\n2\t10:00:30\t0.2\t1\n")
    with pytest.raises(SystemExit):
        SB.prepare_outdir(d, hdr, append=False)
    assert SB.prepare_outdir(d, hdr, append=True) == 3
    with pytest.raises(SystemExit):
        SB.prepare_outdir(d, SB.log_header(["B/1_Z"]), append=True)


# ---- the scorer ---------------------------------------------------------------------------
def write_block(d, nsweep=6, stray=False, nan_sites=()):
    d.mkdir()
    sites = [f"A/{i}" for i in range(1, 65)]
    with open(d / "_census_log.tsv", "w") as fh:
        fh.write("sweep\tclock\tA/1_Z\tA/1_ph\n")
        for n in range(1, nsweep + 1):
            fh.write(f"{n}\t10:{n:02d}:00\t0.1\t1\n")
    for n in range(1, nsweep + (2 if stray else 1)):
        tag = f"10{n:02d}00" if n <= nsweep else "095959"
        num = n if n <= nsweep else 1
        with open(d / f"imp_2026-10-02_{tag}_cfg_census-{num:03d}.csv", "w", newline="", encoding="utf-8") as fh:
            w = csv.writer(fh); w.writerow(["SITE", "MAGNITUDE (MΩ)", "PHASE (°)"])
            for s in sites:
                z = 0.1 if s == "A/1" else 5.0
                if s in nan_sites and n == 1:
                    z = float("nan")
                w.writerow([s, f"{z:.6f}", "1.0"])


def score(d, *extra):
    return subprocess.run([sys.executable, str(QC / "block_duty_cycle_slots.py"), str(d), "--roles", "eeg,emg",
                           "--slots", "A1", *extra], capture_output=True, text=True)


def test_scorer_takes_n_from_the_log_and_ignores_strays(tmp_path):
    write_block(tmp_path / "b", stray=True)
    r = score(tmp_path / "b")
    assert r.returncode == 0, r.stderr
    assert "n = 6 sweeps (from _census_log.tsv)" in r.stdout and "IGNORED" in r.stdout


def test_scorer_drops_nan_instead_of_counting_open(tmp_path):
    write_block(tmp_path / "b", nan_sites=("A/1", "A/5"))
    r = score(tmp_path / "b")
    assert r.returncode == 0, r.stderr
    assert "non-finite magnitudes dropped on 2 site(s)" in r.stdout
    a1 = next(l for l in r.stdout.splitlines() if l.startswith("A1") and " A/1 " in l)
    assert " 5 " in a1 and "100.0" in a1        # 5 finite sweeps, all connected


def test_scorer_refuses_without_log_or_with_missing_csv(tmp_path):
    write_block(tmp_path / "b"); os.remove(tmp_path / "b" / "_census_log.tsv")
    assert score(tmp_path / "b").returncode != 0
    write_block(tmp_path / "c"); os.remove(next((tmp_path / "c").glob("*census-003.csv")))
    assert score(tmp_path / "c").returncode != 0
