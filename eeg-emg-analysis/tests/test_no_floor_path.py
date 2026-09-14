#!/usr/bin/env python3
"""A chip with no wire-free control must yield NO VERDICT -- never a bad one.

Per-port layouts allow a chip to declare that it has no characterised wire-free
floor. The unipolar RHD2132 is the real case: it has 32 real inputs, ~26 of them
unused, and a floor COULD be derived from them -- but those inputs are tied to
ground (median 0.17 MOhm, measured 2026-08-05), so a floor built from them would
flatter the control and condemn every real animal.

The danger is not that such a chip crashes. It is that it quietly produces a
NUMBER. Two ways that happens, and this file exists to make both impossible:

  1. NaN percentiles. `_raw_mask` does `feat.slope[:, c] < floor.slope_p1`, and
     every comparison against NaN is False, so a NaN floor gives an all-False
     mask -- an ordinary-looking 0% usable, a FAIL invented for an animal nobody
     can judge.
  2. A derived-anyway floor. If the reason were recorded as "the model does not
     fit", someone fixes the shape and derives one.

🔑 THE CENTRAL CASE IS R3. The animal is given a strong, plausible signal and the
sites a fabricated floor would use are made LOUD AND FLAT, so that a wrongly
derived floor would score the animal near 100% usable. The test demands that no
percentage is produced at all.

    PYTHONPATH=. ~/eeg-test-venv/bin/python3 tests/test_no_floor_path.py
"""
from __future__ import annotations

import sys
import tempfile
import traceback
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import synth
from core import criteria as C
from cards import ladder as L

PASS, FAIL = [], []
FS = 1000
SECONDS = 600


def check(name, fn):
    try:
        fn()
    except Exception:
        FAIL.append((name, traceback.format_exc()))
        print(f"  FAIL  {name}")
    else:
        PASS.append(name)
        print(f"  ok    {name}")


def expect(name, fn, exc=Exception, want=""):
    def run():
        try:
            fn()
        except exc as e:
            if want and want.lower() not in str(e).lower():
                raise AssertionError(f"wrong reason: {e}\nwanted {want!r}")
            return
        raise AssertionError("NOT REFUSED")
    check(name, run)


# --------------------------------------------------------------------------- #
def _unipolar_recording(tmp: Path) -> tuple[str, C.CohortSpec]:
    """Port A as the 2026-08-05 unipolar prep, plus a trap.

    /18../23 carry real, steep, plausible signal -- a good animal.
    /7../16 are LOUD AND FLAT: the sites a wrongly derived floor would pick.
    A floor taken from them would be beaten by everything, so a fabricated
    verdict here would read ~100% usable. That is the point.
    """
    rng = np.random.default_rng(20260914)
    n = FS * SECONDS
    ch: dict[str, np.ndarray] = {}

    # the animal: steep 1/f, the signature of a connected electrode
    for site in (18, 19, 20, 21, 22, 23):
        ch[f"A/{site}"] = synth.connected_eeg(n, rng, rms_uv=60.0)

    # the trap: flat, loud white noise where a derived floor would look
    for site in range(7, 17):
        ch[f"A/{site}"] = synth.scale_to_epoch_rms(synth.white(n, rng), 400.0)

    base = str(tmp / "unipolar")
    synth.write(base, ch)

    spec = C.CohortSpec(ports_spec=(
        C.PortSpec("A", (C.ChipSpec(
            base=1,
            role_sites=(("emg1", 18), ("lfp_ref", 19), ("lfp_tgt", 20),
                        ("eeg_f", 21), ("eeg_p", 22), ("emg2", 23)),
            real_channels=32,
            floor=(),
            floor_reason=("Unipolar RHD2132. Which of its 26 unused real inputs "
                          "are unwired was never recorded, and those inputs are "
                          "tied to ground."),
        ),)),
    ))
    return base, spec


def t_spec_reports_no_floor():
    with tempfile.TemporaryDirectory() as d:
        _, spec = _unipolar_recording(Path(d))
        assert spec.floor_sites() == []
        assert C.floor_sites_of(spec, "A1") == []
        assert spec.positions() == ["A1"]
        assert not spec.chip_of("A1").has_floor


def t_floor_stats_is_unavailable_with_none_not_nan():
    with tempfile.TemporaryDirectory() as d:
        base, spec = _unipolar_recording(Path(d))
        feat = C.compute_features(base, spec)
        f = C.floor_stats(feat, "A1")
        assert f.available is False
        assert "never recorded" in f.unavailable_reason
        for field in ("slope_p1", "hum_p1", "slope_median", "hum_median"):
            v = getattr(f, field)
            assert v is None, f"{field} is {v!r}; must be None, never NaN"
            # the exact trap: NaN would compare False and fabricate a 0% FAIL
            assert not isinstance(v, float) or not np.isnan(v)


def t_one_pass_still():
    """A no-floor chip contributes animal sites and no floor sites, in one read."""
    with tempfile.TemporaryDirectory() as d:
        base, spec = _unipolar_recording(Path(d))
        feat = C.compute_features(base, spec)
        animals = {s for r in spec.animal_sites().values() for s in r.values()}
        assert set(feat.sites) == animals, (set(feat.sites), animals)
        assert len(feat.sites) == 6


def t_rung2_is_unjudgeable_not_fail():
    """THE CENTRAL CASE. A fabricated floor would score this animal ~100%.

    Demands: the verdict is UNJUDGEABLE, it is not a pass, and NO usable
    percentage appears anywhere in the rung's output.
    """
    with tempfile.TemporaryDirectory() as d:
        base, spec = _unipolar_recording(Path(d))
        feat = C.compute_features(base, spec)
        floor = C.floor_stats(feat, "A1")
        r = L.rung2_connection(feat, "A1", spec, floor, "slope")

        assert r.verdict == "UNJUDGEABLE", r.verdict
        assert r.verdict not in L.PASS_VERDICTS
        assert r.verdict != "FAIL"
        assert "never recorded" in (r.reason or "")
        assert "no wire-free floor" in (r.headline or "").lower()
        assert "floor" in (r.detail or {}), "render_card indexes detail['floor']"

        # no fraction may have been computed, under any key, at any depth
        def walk(o):
            if isinstance(o, dict):
                for k, v in o.items():
                    assert "usable" not in str(k).lower() or v in (None, 0, ""), \
                        f"a usable fraction reached the output: {k}={v!r}"
                    walk(v)
            elif isinstance(o, (list, tuple)):
                for v in o:
                    walk(v)
        walk(r.detail)
        blob = f"{r.headline} {r.reason}"
        assert "%" not in blob, f"a percentage was reported: {blob}"


def t_a_real_floor_still_judges():
    """SENSITIVITY. Without this the whole change could pass by refusing all.

    Same builder, a normal 2-role chip: the animal must come out usable by a wide
    margin. A change that made everything UNJUDGEABLE would look identical to a
    change that worked, and only this test tells them apart.
    """
    with tempfile.TemporaryDirectory() as d:
        rng = np.random.default_rng(7)
        base = synth.build(Path(d) / "ok",
                           synth.connected_eeg(FS * SECONDS, rng, rms_uv=60.0),
                           seconds=SECONDS)
        spec = C.CohortSpec(roles=("eeg", "emg"), ports="A", slot_bases=(1,))
        feat = C.compute_features(base, spec)
        floor = C.floor_stats(feat, "A1")
        assert floor.available is True
        assert floor.n_sites == 14
        m = C.usable(feat, "A/1", floor, "slope", role="eeg")
        frac = float(np.mean(m))
        assert frac > 0.8, f"a good channel scored {frac:.1%} against a real floor"


def refusals():
    with tempfile.TemporaryDirectory() as d:
        base, spec = _unipolar_recording(Path(d))
        feat = C.compute_features(base, spec)
        floor = C.floor_stats(feat, "A1")

        expect("refuse: usable() against a floor that does not exist",
               lambda: C.usable(feat, "A/21", floor, "slope", role="eeg"),
               C.CriterionRefused, "no wire-free floor")

        expect("refuse: _raw_mask, the single chokepoint",
               lambda: C._raw_mask(feat, "A/21", floor, "slope"),
               C.CriterionRefused, "never characterised")

        # these two used to crash inside numpy on an empty array, which read as a
        # library bug rather than as the real situation
        check("floor_threshold_ci says unavailable instead of crashing",
              lambda: (C.floor_threshold_ci(feat, "slope", n_boot=10,
                                            position="A1")["available"] is False)
              or (_ for _ in ()).throw(AssertionError("claimed available")))
        check("falsification_check says not applicable instead of crashing",
              lambda: (C.falsification_check(feat, floor,
                                             "slope")["applicable"] is False)
              or (_ for _ in ()).throw(AssertionError("claimed applicable")))

    # a pooled floor across a mixed rig is not a number about anything
    mixed = C.CohortSpec(ports_spec=(
        C.PortSpec("A", (C.ChipSpec(1, (("eeg", 1), ("emg", 2))),)),
        C.PortSpec("C", (C.ChipSpec(1, (("eeg", 1), ("emg", 2), ("ecg", 3))),)),
    ))
    assert not mixed.is_uniform

    class _Feat:
        spec = mixed
    expect("refuse: pooled floor across a non-uniform rig",
           lambda: C.floor_stats(_Feat(), None), C.LayoutError, "not uniform")


def main() -> int:
    print("THE NO-FLOOR PATH")
    for fn in (t_spec_reports_no_floor,
               t_floor_stats_is_unavailable_with_none_not_nan,
               t_one_pass_still, t_rung2_is_unjudgeable_not_fail,
               t_a_real_floor_still_judges):
        check(fn.__name__, fn)
    print("\nMUST REFUSE")
    refusals()
    print(f"\n{len(PASS)} passed, {len(FAIL)} failed")
    for n, tb in FAIL:
        print(f"\n--- {n} ---\n{tb}")
    return 1 if FAIL else 0


if __name__ == "__main__":
    raise SystemExit(main())
