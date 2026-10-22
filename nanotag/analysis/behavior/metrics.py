#!/usr/bin/env python3
"""Derived behavioural measures, per Acute_SD_Behavioral_Protocol.pdf.

Pure functions only: no video, no EthoVision, no I/O. They take an arm-visit
sequence (Y-maze) or exploration durations in seconds (NOR) and return the
endpoints the protocol names. Run `behavior/metrics.py` to execute the asserts.

Definitions are frozen here on purpose: the HLBNSL (sleep-normal) and HLBNSD
(sleep-deprived) batches form one 2x2 design, so both must be scored by the
same rules. Changing a threshold means re-deriving BOTH batches.
"""
import statistics as st

ARMS = ("A", "B", "C")
MIN_EXPLORATION_S = 20.0      # protocol: exclude if < 20 s total across both objects
MAX_LOCATION_BIAS = 0.80      # protocol: exclude if > 80% intrinsic bias in T1
CHANCE_ALTERNATION = 50.0     # 3-arm maze, chance level for SA%


# --- Y-maze ----------------------------------------------------------------

def arm_sequence(zone_visits, arms=ARMS, collapse_repeats=False):
    """EthoVision's zone-visit list -> the arm-entry sequence.

    Drops the centre zone and anything else not in `arms`. A re-entry into the
    same arm (arm -> centre -> same arm) is KEPT as an entry by default, which
    is the usual convention: it counts toward Total Arm Entries but can never
    form an alternation. Pass collapse_repeats=True for the stricter variant.
    """
    seq = [z for z in zone_visits if z in arms]
    if not collapse_repeats:
        return seq
    out = []
    for z in seq:
        if not out or out[-1] != z:
            out.append(z)
    return out


def spontaneous_alternation(seq):
    """-> (alternations, total_entries, percent). percent is None when the mouse
    made fewer than 3 entries, where the protocol's formula is undefined."""
    n = len(seq)
    alts = sum(1 for i in range(n - 2) if len({seq[i], seq[i + 1], seq[i + 2]}) == 3)
    if n < 3:
        return alts, n, None
    return alts, n, 100.0 * alts / (n - 2)


# --- NOR -------------------------------------------------------------------

def discrimination_index(t_novel, t_familiar):
    """d2 in [-1, +1]. None when the mouse explored neither object."""
    total = t_novel + t_familiar
    return None if total <= 0 else (t_novel - t_familiar) / total


def location_bias(t_left, t_right):
    """Share of T1 exploration spent on the more-visited object, in [0.5, 1.0].
    None when the mouse explored neither."""
    total = t_left + t_right
    if total <= 0:
        return None
    return max(t_left, t_right) / total


def nor_exclusions(t1_a, t1_b, t2_familiar, t2_novel,
                   min_s=MIN_EXPLORATION_S, max_bias=MAX_LOCATION_BIAS):
    """-> list of reason strings. Empty list means the mouse is included.

    Applies to NOR only; a mouse excluded here still contributes Y-maze and OFT.
    """
    reasons = []
    if t1_a + t1_b < min_s:
        reasons.append(f"T1 exploration {t1_a + t1_b:.1f}s < {min_s:.0f}s")
    if t2_familiar + t2_novel < min_s:
        reasons.append(f"T2 exploration {t2_familiar + t2_novel:.1f}s < {min_s:.0f}s")
    bias = location_bias(t1_a, t1_b)
    if bias is not None and bias > max_bias:
        reasons.append(f"T1 location bias {bias:.0%} > {max_bias:.0%}")
    return reasons


# --- open field ------------------------------------------------------------

def thigmotaxis(track, arena_cm, wall_band_cm=5.0):
    """Fraction of samples within `wall_band_cm` of any wall.

    `track` is [(x_cm, y_cm), ...] with the arena spanning 0..arena_cm on both
    axes (EthoVision's origin is the arena centre, so shift before calling).
    Missing samples are passed as None and dropped, so the denominator is
    tracked samples, not elapsed time.
    """
    pts = [p for p in track if p is not None]
    if not pts:
        return None
    near = sum(1 for x, y in pts
               if min(x, y, arena_cm - x, arena_cm - y) <= wall_band_cm)
    return near / len(pts)


def path_length_cm(track):
    """Total distance over a track, skipping gaps where tracking was lost."""
    total, prev = 0.0, None
    for p in track:
        if p is not None and prev is not None:
            total += ((p[0] - prev[0]) ** 2 + (p[1] - prev[1]) ** 2) ** 0.5
        prev = p
    return total


# --- self-check ------------------------------------------------------------

def _selftest():
    # arm_sequence strips the centre zone and, by default, keeps re-entries
    raw = ["A", "centre", "B", "centre", "B", "centre", "C"]
    assert arm_sequence(raw) == ["A", "B", "B", "C"]
    assert arm_sequence(raw, collapse_repeats=True) == ["A", "B", "C"]

    # perfect alternation: ABCAB -> ABC, BCA, CAB = 3 of 3
    alts, n, pct = spontaneous_alternation(list("ABCAB"))
    assert (alts, n) == (3, 5) and abs(pct - 100.0) < 1e-9

    # no alternation at all
    assert spontaneous_alternation(list("ABABAB")) == (0, 6, 0.0)

    # mixed: ABCACB -> ABC yes, BCA yes, CAC no, ACB yes = 3 of 4
    alts, n, pct = spontaneous_alternation(list("ABCACB"))
    assert (alts, n) == (3, 6) and abs(pct - 75.0) < 1e-9

    # a repeated arm breaks the triplets it sits in: AABC -> AAB no, ABC yes
    assert spontaneous_alternation(list("AABC")) == (1, 4, 50.0)

    # undefined below 3 entries, and never a ZeroDivisionError at exactly 2
    assert spontaneous_alternation(list("AB")) == (0, 2, None)
    assert spontaneous_alternation([]) == (0, 0, None)

    # d2 spans the full range and is 0 for no preference
    assert discrimination_index(30.0, 10.0) == 0.5
    assert discrimination_index(10.0, 10.0) == 0.0
    assert discrimination_index(0.0, 10.0) == -1.0
    assert discrimination_index(0.0, 0.0) is None

    assert location_bias(50.0, 50.0) == 0.5
    assert location_bias(90.0, 10.0) == 0.9
    assert location_bias(10.0, 90.0) == 0.9          # symmetric: side does not matter
    assert location_bias(0.0, 0.0) is None

    # exclusions
    assert nor_exclusions(15.0, 15.0, 20.0, 20.0) == []          # 30 s and 40 s, no bias
    assert len(nor_exclusions(5.0, 5.0, 20.0, 20.0)) == 1        # T1 too short
    assert len(nor_exclusions(15.0, 15.0, 5.0, 5.0)) == 1        # T2 too short
    assert len(nor_exclusions(27.0, 3.0, 20.0, 20.0)) == 1       # 90% bias
    assert len(nor_exclusions(5.0, 1.0, 2.0, 2.0)) == 3          # all three fire
    # exactly at the thresholds: included (the protocol says "< 20 s" and "> 80%")
    assert nor_exclusions(10.0, 10.0, 16.0, 4.0) == []

    # thigmotaxis in a 50 cm arena with a 5 cm wall band
    assert thigmotaxis([(25, 25)], 50.0) == 0.0                  # dead centre
    assert thigmotaxis([(2, 25)], 50.0) == 1.0                   # hugging a wall
    assert thigmotaxis([(47, 47)], 50.0) == 1.0                  # corner, far side
    assert thigmotaxis([(25, 25), (2, 2)], 50.0) == 0.5
    assert thigmotaxis([(25, 25), None], 50.0) == 0.0            # gaps dropped
    assert thigmotaxis([None], 50.0) is None

    # path length skips gaps rather than bridging them
    assert path_length_cm([(0, 0), (3, 4)]) == 5.0
    assert path_length_cm([(0, 0), None, (3, 4)]) == 0.0
    assert path_length_cm([(0, 0)]) == 0.0

    print("metrics selftest ok")


if __name__ == "__main__":
    _selftest()
