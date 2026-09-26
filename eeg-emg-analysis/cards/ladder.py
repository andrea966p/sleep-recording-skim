#!/usr/bin/env python3
"""THE VERDICT LADDER. Six rungs, same order forever, one animal-recording.

    ~/eeg-analysis-venv/bin/python cards/ladder.py <recording_base> \
        --cohort HLB-fem-profsurgery-troubleshooting

WHY A LADDER
------------
Every figure this project has produced is an argument. None of them answers the
one question that actually gets asked about a new mouse: "is this animal, on
this day, any good, and how far up the chain of questions did it get?"

The ladder answers exactly that, and it enforces the ordering that the old
figures left implicit:

    RUNG 0  FILE           is the file physically sound?
    RUNG 1  IDENTITY       which native channels are this animal's?
    RUNG 2  CONNECTION     is the electrode connected, judged against wire-free
                           inputs in the SAME file?
    RUNG 3  SCOREABILITY   can the sleep question even be asked?
    RUNG 4  ARCHITECTURE   what did the animal do?          (always PROVISIONAL)
    RUNG 5  EXPORT         can a human check us?

🔑 A RUNG IS NOT EVALUATED IF THE RUNG BELOW IT FAILED. It is marked BLOCKED and
carries the reason. This is the whole point. A hypnogram from an animal that
failed the connection test is not a weak result, it is not a result, and putting
the two side by side at equal visual weight is how this project previously
published a sleep architecture for a channel that turned out to be an
unconnected amplifier input.

VERDICT VOCABULARY, and one distinction that has been misread before:
    PASS         the rung's question was asked and answered yes
    FAIL         asked, answered no
    INSUFFICIENT THE QUESTION COULD NOT BE ASKED. Not the same as FAIL. An
                 animal with 8 minutes of usable data is not an animal that does
                 not sleep.
    BLOCKED      a lower rung failed, so this one was never evaluated
    PROVISIONAL  answered, but the answer is gated behind work not yet done
                 (rung 4 stays here until a blind-scoring kappa exists)

This module does NO PLOTTING. It emits JSON. That keeps the verdicts testable
without a display and means the renderer can never quietly change a number.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import subprocess
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

import numpy as np

ROOT = Path(__file__).resolve().parent.parent

from core import criteria as C            # noqa: E402
from core import qc_thresholds as T       # noqa: E402
from core import paths as PATHS      # noqa: E402
from cohorts.load import load_cohort      # noqa: E402
from cohorts.schema import Animal, Cohort  # noqa: E402

PROCESSED_ROOT = PATHS.PROCESSED_ROOT

PASS_VERDICTS = {"PASS", "PROVISIONAL"}


# --------------------------------------------------------------------------- #
@dataclass
class Rung:
    """One rung. `headline` is the single number that decided it."""
    number: int
    name: str
    question: str
    verdict: str = "BLOCKED"
    headline: str = ""            # the deciding number, formatted
    threshold: str = ""           # what it was compared against
    reason: str = ""
    detail: dict[str, Any] = field(default_factory=dict)

    @property
    def passed(self) -> bool:
        return self.verdict in PASS_VERDICTS


@dataclass
class AnimalCard:
    schema_version: int = 2
    generated: str = ""
    # identity
    cohort_id: str = ""
    project_id: str = ""
    batch_id: str = ""
    animal_id: str = ""
    sex: str = ""
    position: str = ""
    tether_arm: str = ""
    role: str = "animal"
    # this recording
    recording: str = ""
    recording_base: str = ""
    recording_date: str = ""
    duration_h: float | None = None
    zt_start: float | None = None
    zt_end: float | None = None
    # state at this recording
    age_weeks: int | None = None
    age_is_derived: bool = False
    days_post_surgery: int | None = None
    days_post_tether: int | None = None
    body_weight_g: float | None = None
    body_weight_occasion: str = ""
    # method
    criterion: str = ""
    epoch_s_qc: int = T.EPOCH_S_QC
    epoch_s_staging: int = T.EPOCH_S_STAGING
    thresholds_hash: str = ""
    floor: dict[str, Any] = field(default_factory=dict)
    # the ladder
    rungs: list[Rung] = field(default_factory=list)
    # narrative
    notes: str = ""
    surgery_notes: str = ""
    sampling_notes: str = ""
    timeline: list[dict[str, Any]] = field(default_factory=list)
    weighings: list[dict[str, Any]] = field(default_factory=list)
    provenance: dict[str, Any] = field(default_factory=dict)

    @property
    def top_rung(self) -> int:
        """Highest rung number that passed. -1 if even rung 0 failed."""
        best = -1
        for r in self.rungs:
            if r.passed:
                best = r.number
            else:
                break
        return best

    def to_json(self) -> dict:
        d = asdict(self)
        d["top_rung"] = self.top_rung
        return d


# --------------------------------------------------------------------------- #
# helpers
# --------------------------------------------------------------------------- #

def _git_rev() -> str:
    try:
        return subprocess.check_output(
            ["git", "-C", str(ROOT), "rev-parse", "--short", "HEAD"],
            stderr=subprocess.DEVNULL, text=True).strip()
    except Exception:                                    # noqa: BLE001
        return "not a git repo"


def find_processed(recording: str, position: str) -> dict[str, Path]:
    """Locate stage 2/3/4 products for one animal-recording.

    Files are named port<P>-slot<N>_<date>_<time>_<dur>, so the position label
    "B1" maps to portB-slot1.
    """
    port, slot = position[0], position[1]
    stem = f"port{port}-slot{slot}_"
    found: dict[str, Path] = {}
    for day_dir in sorted(PROCESSED_ROOT.glob("20*/")):
        for npz in day_dir.glob(f"{stem}*.npz"):
            try:
                meta = json.loads(str(np.load(npz, allow_pickle=True)["meta"]))
            except Exception:                            # noqa: BLE001
                continue
            if meta.get("recording") != recording:
                continue
            base = npz.with_suffix("")
            found["npz"] = npz
            found["meta"] = meta
            for key, suffix in (("features", "_features.json"),
                                ("hypnogram", "_hypnogram.csv"),
                                ("summary", "_summary.txt"),
                                ("edf", ".edf"),
                                ("scorer_readme", "_SCORER-README.txt"),
                                ("tsv", ".tsv"),
                                ("tsv_gz", ".tsv.gz"),
                                ("epochs_tsv", "_epochs.tsv")):
                p = Path(str(base) + suffix)
                if p.exists():
                    found[key] = p
            found["day_dir"] = day_dir
            return found
    return found


# --------------------------------------------------------------------------- #
# the rungs
# --------------------------------------------------------------------------- #

def rung0_file(base: str) -> Rung:
    r = Rung(0, "FILE", "Is the recording file physically sound?")
    info = C.file_integrity(base)
    r.detail = info
    if info["verdict"] == "INTACT":
        r.verdict = "PASS"
        r.headline = f"{info['n_data_samples']:,} samples, {info['duration_h']:.2f} h"
        r.threshold = "data samples == timestamp samples, remainder 0"
    elif info["verdict"] == "TRUNCATED":
        r.verdict = "FAIL"
        r.headline = "sample counts disagree"
        r.threshold = "data samples == timestamp samples, remainder 0"
    else:
        r.verdict = "FAIL"
        r.headline = "file missing"
    r.reason = info["reason"]
    return r


def rung1_identity(feat: C.EpochFeatures, position: str, spec: C.CohortSpec,
                   floor: C.FloorStats) -> Rung:
    r = Rung(1, "IDENTITY", "Which native channels belong to this animal?")
    sites = spec.animal_sites()[position]
    x, labels, _, _ = C.open_xdat(feat.base)
    del x

    # The three signatures, from CANONICAL-allego-channel-selection.md §5:
    #   connected  rms 30-90 uV, mains 6-20 uV
    #   floating   rms 200-4700 uV, mains 150-4500 uV
    #   inactive   rms ~30 uV, mains ~3 uV, flat, HF ~93%
    detail = {}
    for role, site in sites.items():
        c = feat.col(site)
        med_rms = float(np.median(feat.rms[:, c]))
        med_hum = float(np.median(feat.hum[:, c]))
        med_slope = float(np.median(feat.slope[:, c]))
        if med_hum < 5.0 and med_rms < 60.0 and med_slope > -0.5:
            sig = "inactive-slot"
        elif med_hum > 150.0:
            sig = "floating"
        else:
            sig = "connected-or-quiet"
        detail[role] = {"site": site, "native_col": labels.index(site),
                        "median_rms_uv": round(med_rms, 1),
                        "median_hum_uv": round(med_hum, 1),
                        "median_slope": round(med_slope, 2),
                        "signature": sig}
    r.detail = {"sites": detail,
                "layout_source": "biointerface_map in the recording's own .xdat.json",
                "bipolar": True,
                "n_floor_sites": floor.n_sites}
    r.verdict = "PASS"
    r.headline = "  ".join(f"{k.upper()} {v['site']}" for k, v in detail.items())
    r.threshold = "layout derived from the file, never assumed"
    r.reason = (f"{len(detail)} channels resolved from sensors_by_port; "
                f"{floor.n_sites} wire-free inputs available as an in-file floor")
    return r


def rung2_connection(feat: C.EpochFeatures, position: str, spec: C.CohortSpec,
                     floor: C.FloorStats, criterion: str) -> Rung:
    r = Rung(2, "CONNECTION",
             "Is the electrode connected, judged against wire-free inputs in the same file?")

    # 🔑 JUDGE THIS ANIMAL AGAINST ITS OWN CHIP. The floor handed in may be the
    # historical pooled one; re-derive it per chip unless the caller already did.
    if floor.scope != "chip" or floor.position != position:
        floor = C.floor_stats(feat, position)

    # 🛑 THIS CHIP DECLARES NO WIRE-FREE CONTROL AT ALL. Must be tested BEFORE
    # `grounded`, because an unavailable floor reports grounded=False: without
    # this branch a unipolar prep that was perfectly grounded would be told its
    # headstage has no ground reference, and the .0f format on a None median
    # would crash on the way. Two different facts:
    #   available=False  a SPEC fact, known before a byte is read
    #   grounded=False   a MEASURED fact, from a floor that does exist
    if not floor.available:
        r.verdict = "UNJUDGEABLE"
        r.reason = floor.unavailable_reason
        r.headline = ("no wire-free floor is declared for this chip -- "
                      "no connection verdict can be drawn")
        r.detail = {"floor": floor.as_dict()}      # key must exist: render_card indexes it
        return r

    # 🛑 AN UNGROUNDED CHIP HAS NO VALID NEGATIVE CONTROL. Its wire-free inputs
    # go quiet and steep, which makes the threshold unbeatable and reports a
    # hardware fault as a dead animal. Say UNJUDGEABLE and say why.
    if not floor.grounded:
        r.verdict = "UNJUDGEABLE"
        r.reason = floor.validity_reason
        r.headline = (f"chip floor is {floor.hum_median:.0f} uV of 60 Hz "
                      f"(grounded chips show >{T.FLOOR_MIN_HUM_UV:.0f}) -- "
                      "no verdict can be drawn")
        r.detail = {"floor": floor.as_dict()}
        return r

    # 🛑 A GROUNDED CHIP CAN STILL HAVE AN INVALID CONTROL. When its wire-free
    # inputs carry signal, the slope threshold lands past what real EEG reaches
    # and a healthy electrode reads 0.0%. Same treatment as ungrounded, for the
    # same reason. Only the SLOPE criterion reads this floor's slope; a card
    # judged on hum is unaffected. Diagnosed 2026-08-27, unfixed until 2026-09-26,
    # by which time it had produced a retracted S-SL conclusion.
    if criterion == "slope" and not floor.slope_flat:
        r.verdict = "UNJUDGEABLE"
        r.reason = floor.slope_validity_reason
        r.headline = (f"chip floor is not flat: typical wire-free slope "
                      f"{floor.site_median_slope:.2f} (clean floors are flatter "
                      f"than {T.FLOOR_MAX_SITE_MEDIAN_SLOPE:.2f}) -- "
                      "no verdict can be drawn")
        r.detail = {"floor": floor.as_dict()}
        return r

    sites = spec.animal_sites()[position]
    masks: dict[str, np.ndarray] = {}
    refusals: dict[str, str] = {}
    per_role: dict[str, Any] = {}

    for role, site in sites.items():
        # EEG gets the requested criterion. Non-EEG roles are broadband, so the
        # slope test is a category error for them and hum is used instead.
        role_criterion = criterion if role == "eeg" else "hum"
        try:
            m = C.usable(feat, site, floor, role_criterion, role=role)
        except C.CriterionRefused as exc:
            refusals[role] = str(exc)
            m = C.usable(feat, site, floor, role_criterion, role=role,
                         allow_refused=True)
        masks[role] = m
        s = C.summarise(feat, m)
        s["criterion"] = role_criterion
        s["site"] = site
        per_role[role] = s

    both = np.ones(feat.n_epochs, dtype=bool)
    for m in masks.values():
        both &= m
    combined = C.summarise(feat, both)
    combined["criterion"] = criterion

    # 🔑 THE FLOOR THRESHOLD IS ITSELF AN ESTIMATE, and on the SLOPE criterion its
    # sampling error is not a rounding detail. MEASURED 2026-08-10 on
    # allego_1__uid0806-16-57-38, resampling over the 112 wire-free SITES:
    #     hum criterion    every position moves 0.0 points
    #     slope criterion  B1 83.1% -> [53.1, 98.0], D2 75.2% -> [48.9, 86.2]
    # The hum threshold sits in the empty valley of a distribution separated by a
    # factor of ~100, so it is insensitive. The slope threshold sits inside a
    # continuous distribution and is not. Any slope-criterion fraction quoted
    # without this interval is quoted to a precision it does not have.
    # This does NOT move the rung 2 verdict, which gates on the longest unbroken
    # block rather than the fraction -- one of the reasons it does.
    thr_ci = C.floor_threshold_ci(feat, criterion, position=position)
    intervals = {}
    for role, site in sites.items():
        if role in refusals:
            continue
        role_criterion = per_role[role]["criterion"]
        ci_for_role = (thr_ci if role_criterion == criterion
                       else C.floor_threshold_ci(feat, role_criterion,
                                                 position=position))
        intervals[role] = C.usable_fraction_interval(feat, site, floor,
                                                     role_criterion, ci_for_role)

    r.detail = {"per_role": per_role, "combined": combined,
                "refusals": refusals,
                "floor": floor.as_dict(),
                "floor_threshold_ci": thr_ci,
                "usable_fraction_intervals": intervals,
                # Carried in every card so the term travels with the number it
                # describes. See core.criteria.USABLE_FRACTION_DEFINITION.
                "usable_fraction_definition": C.USABLE_FRACTION_DEFINITION,
                "falsification": C.falsification_check(feat, floor, criterion)}

    frac = combined["usable_fraction"]
    longest_min = combined["longest_block_minutes"]
    r.headline = (f"{100 * frac:.1f}% usable, longest unbroken block "
                  f"{longest_min:.1f} min")
    thr = (f"slope < {floor.slope_p1:.2f}" if criterion == "slope"
           else f"60 Hz < {floor.hum_p1:.1f} uV")
    r.threshold = (f"{thr} (p{T.FLOOR_PERCENTILE} of {floor.n_sites} wire-free "
                   f"inputs in this file), rms {T.RMS_LO_UV:.0f}-{T.RMS_HI_UV:.0f} uV, "
                   "zero railed samples")

    # 🔑 THE GATE IS THE LONGEST UNBROKEN BLOCK, NOT THE TOTAL FRACTION.
    # A fraction gate fails this project's own best recording: C1 on 2026-07-31
    # is usable in only 31.3% of epochs and yet contains a single 485.7 minute
    # unbroken block, which is the 8.1 hours that produced the only real sleep
    # data this project held. Fragmentation is what kills scoreability, not the
    # total. This also matches the rig's standing rule that only a multi-hour
    # recording is an outcome, and stage 3's own gate of 15 minutes inside long
    # blocks.
    if refusals:
        r.verdict = "FAIL"
        r.reason = ("criterion refused: " + " | ".join(refusals.values()))
    elif combined["insufficient"]:
        r.verdict = "INSUFFICIENT"
        r.reason = (f"only {feat.n_epochs} QC epochs of {feat.epoch_s}s; "
                    f"below {T.MIN_USABLE_EPOCHS}, a fraction here is a ratio of "
                    "small integers")
    elif longest_min >= T.MIN_BLOCK_MINUTES:
        r.verdict = "PASS"
        r.reason = (f"{combined['n_epochs_usable']:,} of "
                    f"{combined['n_epochs_total']:,} epochs usable on every role, "
                    f"with an unbroken block of {longest_min:.1f} min")
    elif frac > 0.0:
        r.verdict = "FAIL"
        r.reason = (f"INTERMITTENT: {100 * frac:.1f}% of epochs usable but the "
                    f"longest unbroken run is only {longest_min:.1f} min, under "
                    f"the {T.MIN_BLOCK_MINUTES:.0f} min a recording needs to be "
                    "an outcome rather than a screen")
    else:
        r.verdict = "FAIL"
        worst = min(per_role.items(), key=lambda kv: kv[1]["usable_fraction"])
        r.reason = (f"no epoch passes on every role; weakest is {worst[0].upper()} "
                    f"at {100 * worst[1]['usable_fraction']:.1f}%")
    return r


def rung3_scoreability(processed: dict, blocked_by: Rung | None) -> Rung:
    r = Rung(3, "SCOREABILITY", "Can the sleep question even be asked?")
    if blocked_by is not None:
        r.verdict = "BLOCKED"
        r.reason = f"rung {blocked_by.number} {blocked_by.name} did not pass"
        return r
    feats = processed.get("features")
    if feats is None:
        r.verdict = "INSUFFICIENT"
        r.reason = ("no stage 3 output for this animal-recording; run "
                    "pipeline/stage3_features.py on its day folder")
        return r

    d = json.loads(Path(feats).read_text())
    pers = d.get("persistence", {}).get("1min", {})
    r.detail = {
        "qc_verdict": d.get("qc_verdict"),
        "verdict": d.get("verdict"),
        "hours_in_blocks": d.get("hours_in_blocks"),
        "n_blocks": d.get("n_blocks"),
        "longest_block_min": d.get("longest_block_min"),
        "r_1min": pers.get("r"),
        "r_1min_shuffled": pers.get("shuffled"),
        "wake_pct": d.get("wake_pct"),
        "physiology_informative_pass": d.get("physiology_informative_pass"),
        "reasons": d.get("reasons", []),
    }
    r.threshold = (f">= {T.MIN_BLOCK_MINUTES:.0f} min inside blocks of "
                   f">= {T.MIN_BLOCK * T.EPOCH_S} s, within-block r@1min > "
                   f"{T.R_THRESH:.2f}, wake {T.WAKE_LO:.0f}-{T.WAKE_HI:.0f}%")
    r.headline = (f"{d.get('hours_in_blocks', 0):.2f} h in {d.get('n_blocks', 0)} "
                  f"block(s), r@1min {pers.get('r', float('nan')):.3f}")
    if d.get("verdict") == "SCOREABLE":
        r.verdict = "PASS"
        r.reason = (f"longest block {d.get('longest_block_min', 0):.1f} min; "
                    f"persistence {pers.get('r', 0):.3f} against a shuffled "
                    f"{pers.get('shuffled', 0):.3f}")
    elif "INSUFFICIENT" in str(d.get("verdict", "")).upper():
        r.verdict = "INSUFFICIENT"
        r.reason = "; ".join(d.get("reasons", [])) or "not enough time inside blocks"
    else:
        r.verdict = "FAIL"
        r.reason = "; ".join(d.get("reasons", [])) or str(d.get("verdict"))
    return r


def rung4_architecture(processed: dict, blocked_by: Rung | None) -> Rung:
    r = Rung(4, "ARCHITECTURE", "What did the animal do?")
    if blocked_by is not None:
        r.verdict = "BLOCKED"
        r.reason = f"rung {blocked_by.number} {blocked_by.name} did not pass"
        return r
    d = json.loads(Path(processed["features"]).read_text())

    sens = d.get("otsu_sensitivity", {}).get("rows", [])
    light = [row.get("asleep_in_light_pct") for row in sens
             if row.get("asleep_in_light_pct") is not None]
    swing = (max(light) - min(light)) if len(light) > 1 else None
    nominal = next((row.get("asleep_in_light_pct") for row in sens
                    if row.get("multiplier") == 1.0), None)
    null = d.get("rem_from_nrem_null", {}) or {}

    r.detail = {
        "wake_pct": d.get("wake_pct"),
        "nrem_pct": d.get("nrem_pct"),
        "rem_pct_CONSTRUCTED": d.get("rem_pct_CONSTRUCTED"),
        "asleep_in_light_pct": nominal,
        "asleep_in_light_swing_pts": round(swing, 1) if swing is not None else None,
        "otsu_sensitivity": sens,
        "rem_from_nrem_pct": d.get("rem_from_nrem_pct"),
        "rem_from_nrem_null": null,
        "bouts": d.get("bouts"),
        "min_bout_s": d.get("min_bout"),
        "by_light_phase": d.get("by_light_phase"),
        "physiology_informative_checks": d.get("physiology_informative_checks"),
    }
    r.verdict = "PROVISIONAL"
    r.headline = (f"wake {d.get('wake_pct', 0):.1f}%, NREM {d.get('nrem_pct', 0):.1f}%"
                  + (f", asleep in light {nominal:.1f}%" if nominal is not None else ""))
    r.threshold = "no pass mark: this rung reports, it does not judge"
    # Kept to one line: the card clamps rung text at two lines, and the full
    # caveats live in `detail` and on the panel beside the ladder.
    swing_txt = (f"the light-phase figure swings {swing:.1f} points across a "
                 f"+/-25% threshold sweep; " if swing is not None else "")
    r.reason = (f"{swing_txt}no human has scored any epoch, so accuracy is "
                "unmeasured; no REM percentage is reportable")
    caveats = [
        "PROVISIONAL until a blind-scoring Cohen kappa exists. No human has "
        "scored any epoch from this project, so these labels have no known "
        "accuracy.",
        ("The light-phase sleep figure moves {:.1f} points across a +/-25% "
         "sweep of the wake threshold, so it is NOT threshold-independent and "
         "agreement with the literature is not independent confirmation."
         ).format(swing) if swing is not None else "",
        "NO REM PERCENTAGE IS REPORTED: the percentile rule and an independent "
        "Otsu cut disagree by roughly a factor of five on this montage.",
        "Four of the five physiology checks restate the staging rule and cannot "
        "fail. Only 'NREM carries the largest amplitude' is informative.",
    ]
    r.detail["caveats"] = [c for c in caveats if c]
    return r


def rung5_export(processed: dict, blocked_by: Rung | None) -> Rung:
    r = Rung(5, "EXPORT", "Can a human check us?")
    if blocked_by is not None:
        r.verdict = "BLOCKED"
        r.reason = f"rung {blocked_by.number} {blocked_by.name} did not pass"
        return r

    have = {k: (str(processed[k]) if k in processed else None)
            for k in ("edf", "scorer_readme", "tsv", "tsv_gz", "epochs_tsv",
                      "hypnogram", "summary")}
    day_dir = processed.get("day_dir")
    packs = sorted(str(p.name) for p in day_dir.glob("*_SCORING*")) if day_dir else []
    scored = []
    for p in (day_dir.glob("*_SCORING*/scoresheet.csv") if day_dir else []):
        scored.append(str(p.parent.name))

    r.detail = {"artifacts": have, "scoring_packs": packs, "packs_scored": scored,
                "kappa_available": bool(scored)}
    text_ok = bool(have["tsv"] or have["tsv_gz"] or have["epochs_tsv"])
    r.threshold = "EDF for a scorer, plain text for the professor, both present"
    present = [k for k in ("edf", "hypnogram", "summary", "scorer_readme") if have[k]]
    r.headline = (f"{len(present)}/4 pipeline artifacts"
                  + (", plain text written" if text_ok else ", NO plain text"))
    if have["edf"] and text_ok:
        r.verdict = "PASS"
        r.reason = "EDF and plain-text export both present"
    else:
        r.verdict = "INSUFFICIENT"
        missing = []
        if not have["edf"]:
            missing.append("EDF (run pipeline/stage4_export_edf.py)")
        if not text_ok:
            missing.append("plain text (run cards/export_text.py)")
        r.reason = "missing: " + "; ".join(missing)
    if packs and not scored:
        r.reason += (f"; {len(packs)} blind-scoring pack(s) built and NOT YET "
                     "SCORED, which is what gates rung 4")
    return r


# --------------------------------------------------------------------------- #
# assembly
# --------------------------------------------------------------------------- #

def build_card(base: str, cohort: Cohort, position: str,
               feat: C.EpochFeatures, floor: C.FloorStats,
               criterion: str) -> AnimalCard:
    recording = Path(base).name
    rec_ref = next((r for r in cohort.recordings if r.base == recording), None)
    rec_date = rec_ref.date if rec_ref else None

    processed_early = find_processed(recording, position)
    # Resolve identity at the recording's START MOMENT, not merely its date.
    # Two recordings on 2026-08-06 sit either side of a 16:27 tether swap.
    #
    # A BARE DATE RESOLVES AT MIDNIGHT, WHICH NAMES THE WRONG MOUSE. as_moment()
    # combines a date with time.min, so a 12:50 recording was resolved as if at
    # 00:00. On 2026-08-26 that put HLBSSD13 in B1 -- its 10:00 move OFF-RIG had
    # not "happened" yet at midnight, and HLBSSD17's 12:00 arrival was still in
    # the future. The card named the animal that had already been pulled.
    rec_moment = rec_date
    start_local = processed_early.get("meta", {}).get("start_local")
    if start_local:
        try:
            rec_moment = dt.datetime.fromisoformat(start_local).replace(tzinfo=None)
        except ValueError:
            pass
    else:
        # Stage 2 has not run for this animal-recording. Allego writes the local
        # start time into the file name, and pipeline_common already parses it;
        # that is a better answer than midnight.
        try:
            from pipeline.pipeline_common import parse_start_local
            parsed, _src = parse_start_local(recording, "")
            if parsed is not None:
                rec_moment = parsed.replace(tzinfo=None)
        except Exception:
            pass

    # THE MANIFEST'S OWN WORD COMES FIRST. A per-animal recordings row states
    # (base, position) outright, needs no timestamp, and survives a missing
    # stage 2 entirely. Fall back to the placement timeline only when no row
    # declares this position for this recording.
    animal: Animal | None = next(
        (a for a in cohort.animals
         for r in a.recordings
         if r.base == recording and r.position == position), None)
    if animal is None:
        animal = (cohort.animal_at(position, rec_moment) if rec_moment else None)

    card = AnimalCard()
    card.generated = dt.datetime.now().astimezone().isoformat(timespec="seconds")
    card.cohort_id = cohort.cohort_id
    card.position = position
    card.recording = recording
    card.recording_base = base
    card.recording_date = rec_date.isoformat() if rec_date else ""
    card.criterion = criterion
    card.thresholds_hash = C.thresholds_hash()
    card.floor = floor.as_dict()

    if animal is not None:
        placement = animal.placement_at(rec_moment)
        weight = animal.weight_at_or_before(rec_date)
        age, derived = animal.age_weeks_at(rec_date)
        card.animal_id = animal.animal_id
        card.project_id = animal.project_id
        card.batch_id = animal.batch_id
        card.sex = animal.sex
        card.tether_arm = placement.tether_arm if placement else ""
        card.age_weeks = age
        card.age_is_derived = derived
        card.days_post_surgery = animal.days_post_surgery(rec_date)
        card.days_post_tether = animal.days_post_tether(rec_date)
        card.body_weight_g = weight.grams if weight else None
        card.body_weight_occasion = weight.occasion if weight else ""
        card.notes = animal.notes
        card.surgery_notes = animal.surgery_notes
        card.sampling_notes = animal.sampling_notes
        card.weighings = [{"date": w.date.isoformat() if w.date else None,
                           "grams": w.grams, "occasion": w.occasion,
                           "source": w.source} for w in animal.weighings]
        from cohorts.schema import iter_timeline
        card.timeline = [{"date": d.isoformat(), "kind": k, "label": lab}
                         for d, k, lab in iter_timeline(animal)]
        my_rec = next((r for r in animal.recordings if r.base == recording), None)
        if my_rec is not None:
            card.role = my_rec.role
    else:
        card.animal_id = f"UNKNOWN@{position}"
        card.notes = (f"No animal is recorded in the {position} position on "
                      f"{card.recording_date or 'this date'} in cohort "
                      f"{cohort.cohort_id}. The card is still produced, because "
                      "the measurements are real, but the identity is not known.")

    processed = processed_early
    if "meta" in processed:
        meta = processed["meta"]
        card.duration_h = meta.get("hours")

    # --- the ladder, in order, each blocked by the first failure below it ---
    r0 = rung0_file(base)
    r1 = rung1_identity(feat, position, feat.spec, floor) if r0.passed else Rung(
        1, "IDENTITY", "Which native channels belong to this animal?",
        reason="rung 0 FILE did not pass")
    r2 = (rung2_connection(feat, position, feat.spec, floor, criterion)
          if r1.passed else Rung(
              2, "CONNECTION",
              "Is the electrode connected, judged against wire-free inputs in the same file?",
              reason="rung 1 IDENTITY did not pass"))
    r3 = rung3_scoreability(processed, None if r2.passed else r2)
    r4 = rung4_architecture(processed, None if r3.passed else r3)
    r5 = rung5_export(processed, None if r3.passed else r3)

    card.rungs = [r0, r1, r2, r3, r4, r5]

    # ZT is a property of the clock, not of whether the electrode worked. An
    # earlier version computed it only when rung 2 passed, so every failing
    # animal's card read "ZT span unknown" for no reason.
    zt = processed.get("meta", {}).get("start_local")
    if zt:
        try:
            start = dt.datetime.fromisoformat(zt)
            card.zt_start = round(((start.hour + start.minute / 60)
                                   - T.LIGHTS_ON_HOUR) % 24, 2)
            if card.duration_h:
                card.zt_end = round((card.zt_start + card.duration_h) % 24, 2)
        except ValueError:
            pass

    card.provenance = {
        "thresholds_file": str(Path(T.__file__).resolve()),
        "thresholds_hash": card.thresholds_hash,
        "git_rev": _git_rev(),
        "cohort_manifest": getattr(cohort, "manifest_path", ""),
        "processed_files": {k: str(v) for k, v in processed.items()
                            if isinstance(v, Path)},
        "epoch_s_qc": feat.epoch_s,
        "n_qc_epochs": feat.n_epochs,
        "criterion": criterion,
        "criterion_note": (
            "SLOPE and HUM usable fractions are NOT comparable, and neither is "
            "comparable to a fraction computed at the 4 s staging epoch."),
    }
    return card


# --------------------------------------------------------------------------- #
def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("base", help="recording base path or bare recording name")
    ap.add_argument("--cohort", required=True, help="cohort id or manifest path")
    ap.add_argument("--husbandry", help="CSV or XLSX husbandry sheet to join")
    ap.add_argument("--positions", help="comma list, default every position")
    ap.add_argument("--criterion", choices=("slope", "hum"),
                    help="override the cohort's criterion")
    ap.add_argument("--out", default=None, help="output directory for card JSON")
    ap.add_argument("--max-hours", type=float, help="analyse only the first N hours")
    ap.add_argument("--cache", default=None, help="npz feature cache to read/write")
    args = ap.parse_args(argv)

    base = args.base
    if not Path(base + ".xdat.json").exists():
        guess = PATHS.RAW_ROOT / Path(base).name
        if Path(str(guess) + ".xdat.json").exists():
            base = str(guess)
        else:
            raise SystemExit(f"no recording at {base}.xdat.json")

    cohort = load_cohort(args.cohort, args.husbandry, verbose=True)
    criterion = args.criterion or cohort.criterion
    # The manifest decides the layout. A manifest with no `ports:` key -- every
    # one written before 2026-09-14 -- yields exactly CohortSpec(roles=...), the
    # object this line used to build.
    spec = cohort.to_spec()
    if args.positions:
        positions = [p.strip() for p in args.positions.split(",") if p.strip()]
        # Was unvalidated: an unknown position reached spec.animal_sites()[...]
        # and surfaced as a bare KeyError with no hint of what was wrong.
        # postprocess.py feeds run.occupied straight in here.
        unknown = [p for p in positions if p not in spec.positions()]
        if unknown:
            raise SystemExit(
                f"--positions names {', '.join(unknown)}, which this cohort's "
                f"layout does not have. It has: {', '.join(spec.positions())}\n"
                + spec.describe())
    else:
        positions = spec.positions()
    if not spec.is_uniform:
        print("layout: NOT uniform -- each animal is judged against its own chip")
        print(spec.describe())

    cache = Path(args.cache) if args.cache else None
    if cache and cache.exists():
        print(f"features: cached {cache}")
        z = np.load(cache, allow_pickle=True)
        feat = C.EpochFeatures(base=base, fs=int(z["fs"]), epoch_s=int(z["epoch_s"]),
                               n_epochs=int(z["n_epochs"]), n_samples=int(z["n_samples"]),
                               sites=list(z["sites"]), spec=spec, hum=z["hum"],
                               rms=z["rms"], rail=z["rail"], slope=z["slope"],
                               delta=z["delta"], lfhf=z["lfhf"])
    else:
        print(f"features: computing from {base}")
        feat = C.compute_features(base, spec, max_hours=args.max_hours)
        if cache:
            cache.parent.mkdir(parents=True, exist_ok=True)
            np.savez_compressed(cache, fs=feat.fs, epoch_s=feat.epoch_s,
                                n_epochs=feat.n_epochs, n_samples=feat.n_samples,
                                sites=np.array(feat.sites), hum=feat.hum, rms=feat.rms,
                                rail=feat.rail, slope=feat.slope, delta=feat.delta,
                                lfhf=feat.lfhf)
    # Card-level floor is per-chip now; computed inside the loop so each
    # animal is judged against its OWN chip's wire-free inputs.
    floor = C.floor_stats(feat)          # pooled, kept only for the header

    outdir = Path(args.out) if args.out else (
        ROOT / "cards" / "out" / cohort.cohort_id)
    outdir.mkdir(parents=True, exist_ok=True)

    print(f"\n{'pos':<5} {'animal':<16} {'arm':<4} {'top':<4} "
          f"{'0 FILE':<8} {'1 IDENT':<9} {'2 CONN':<13} {'3 SCORE':<13} "
          f"{'4 ARCH':<12} {'5 EXPORT':<12}")
    print("-" * 118)
    for pos in positions:
        card = build_card(base, cohort, pos, feat, C.floor_stats(feat, pos), criterion)
        path = outdir / f"{card.recording}__{pos}_card.json"
        path.write_text(json.dumps(card.to_json(), indent=2, default=str))
        v = {r.number: r.verdict for r in card.rungs}
        print(f"{pos:<5} {card.animal_id:<16} {card.tether_arm or '-':<4} "
              f"{card.top_rung:<4} "
              f"{v[0]:<8} {v[1]:<9} {v[2]:<13} {v[3]:<13} {v[4]:<12} {v[5]:<12}")
    print(f"\ncards written to {outdir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
