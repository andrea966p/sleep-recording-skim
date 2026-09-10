#!/usr/bin/env python3
"""Single source of truth for every constant in the EEG pipeline.

RULE: no magic numbers anywhere else in the pipeline. Every constant here
carries its provenance -- either a measurement on our own data, a hardware
datasheet value, or a literature citation. If a number has no provenance it
does not belong in a paper.

Audited 2026-08-03 against 1,137,955 pooled 4 s epochs (41 animal-recordings).

CONSOLIDATED 2026-08-09. This file previously lived in the Obsidian vault at
02-procedures/eeg-data-analysis/pipeline/ while a second, disagreeing set of
constants lived inline across eeg-emg-analysis/qc/. They disagreed on the epoch
length (4 vs 10 s), on the impedance pass mark (2.0 vs 0.5 MOhm) and on the rail
voltage (four different values). Every one of those is now settled here, with
the reasoning at the constant, and nothing else in the codebase defines them.

Anything importing a threshold from anywhere else is a bug. The animal card
prints this file's content hash in its footer so a figure can never silently
have come from a different set of numbers.
"""

# ---------------------------------------------------------------------------
# ACQUISITION -- fixed by hardware, not choices
# ---------------------------------------------------------------------------
FS_RAW = 1000            # Hz, Allego/XDAQ sample rate for these recordings
LSB_UV = 0.195           # uV per ADC count, Intan RHD2000-series datasheet
ADC_FULL_SCALE = 32767   # 16-bit signed

RAIL_UV = LSB_UV * ADC_FULL_SCALE          # = 6389.565 uV
# MEASURED 2026-08-03: max|sample| on all 8 channels of allego_1__uid0731 is
# 6389.8 uV, identical to 4 significant figures across channels. That is the
# ADC full scale, NOT the amplifier's analogue input range. Confirms the
# constant is a hardware ceiling and not a property of any one animal.
RAIL_GUARD = 0.998       # count a sample as railed at >= 99.8% of full scale
RAIL_UV_EFF = RAIL_UV * RAIL_GUARD          # = 6376.8 uV

# ---------------------------------------------------------------------------
# EPOCHING AND SPECTRA
# ---------------------------------------------------------------------------
EPOCH_S = 4
EPOCH_S_STAGING = 4        # alias, explicit at the call site
EPOCH_S_QC = 10            # connection QC only; see the note below
# ⚠️ TWO EPOCH LENGTHS EXIST ON PURPOSE, and until 2026-08-09 they lived in two
# different files that did not know about each other, which is how you get two
# "usable fraction" numbers for the same animal that cannot be compared.
#
#   EPOCH_S_STAGING = 4 s   sleep staging and everything downstream of it
#   EPOCH_S_QC      = 10 s  the connection test against the wire-free floor
#
# The QC epoch is longer because the 60 Hz and spectral-slope estimates it makes
# need frequency resolution more than they need time resolution, and because
# contact states persist for minutes. The staging epoch is short because mouse
# NREM bouts are frequently under 30 s.
#
# 🛑 A usable fraction computed at 10 s and one computed at 4 s ARE DIFFERENT
# NUMBERS. Never table them together. The card records which one it used.
#
# 4 s is the short end of the accepted rodent range. Mouse sleep is far more
# fragmented than human sleep and NREM bouts are frequently under 30 s, so the
# 20-30 s epochs used in human PSG smear state transitions. Published rodent
# work spans 4 s (IntelliSleepScorer), 10 s (Kostin 2025) and 20 s (FASTER,
# MC-SleepNet). We use 4 s and NEVER report bouts shorter than 2 epochs.

MIN_BOUT_EPOCHS = 3
# = 12 s at 4 s epochs. A run of a state shorter than this is not counted as
# that state; it is merged into the neighbouring state.
#
# PROVENANCE: THIS LAB'S SCORING CONVENTION, stated by the operator 2026-08-07:
#   "The basic unit epoch is 4 seconds, and we look at 5 blocks at once, so it
#    is set to 20 seconds. Also, after analyzing with 4 s epoch, we do not count
#    it as a stage if it is shorter than three consecutive epochs (12 s)."
#
# ⚠️ NOT from the IIIS Tsukuba reference. Checked directly against Nakata et al.
# SLEEP 2025 (doi:10.1093/sleep/zsae279), the current method from the Funato /
# Yanagisawa group: it specifies 4 s epochs, semiautomatic scoring followed by
# visual inspection, and computes mean episode duration as total time in state
# divided by number of episodes, with NO minimum bout criterion of any kind.
# So this constant is a house rule, defensible and common in rodent work, but it
# must be reported as ours and not attributed to that reference.

NPERSEG = 2048
# DO NOT LOWER. df = fs/nperseg = 0.49 Hz. At nperseg=512 df = 1.95 Hz and the
# 6-9 Hz theta band spans a single FFT bin, so np.trapz over one point returns
# exactly 0.0 and silently destroys every REM measurement with no error raised.

BAND_DELTA = (1.0, 4.0)   # REPORTING band; see BAND_DELTA_STAGING for the staging one
# CHANGED 2026-08-08 from (0.5, 4.0) to match the IIIS Tsukuba reference exactly:
# "NREMS was characterized by high-amplitude, delta (1-4 Hz)-frequency EEG waves"
# and "The delta range ... was calculated as the average of the EEG power of
# 1-4 Hz". SOURCE: Nakata et al., SLEEP 2025, doi:10.1093/sleep/zsae279.
# Kostin 2025 / FASTER use 0.5-4 or 0.75-4, so both are defensible; we align with
# the reference lab whose montage we copied.
# ⭐ It also suits our hardware: the acquisition high-pass sits at 1.10 Hz and
# irreversibly attenuates 0.5-1.1 Hz before the data is saved, so a 0.5 Hz lower
# edge was integrating a band the hardware had already eaten.
BAND_THETA = (6.0, 9.0)   # avoid putting 7 Hz on a boundary (Kostin 2025)

BAND_DELTA_STAGING = (0.5, 4.5)
# ⚠️ OPEN ISSUE, MEASURED 2026-08-10, DELIBERATELY NOT CHANGED YET.
# The lower edge of 0.5 Hz sits BELOW the 1.10 Hz acquisition high-pass, which
# reaches the saved file and irreversibly attenuates everything under it. This is
# the same defect that caused BAND_DELTA (the REPORTING band) to be moved from
# 0.5 to 1.0 on 2026-08-08. The staging band did not get that fix, and the two
# have disagreed ever since.
#
# HOW BIG IS IT. Share of the 0.5-4.5 Hz staging band that comes from the
# attenuated 0.5-1.1 Hz region, first hour of each animal, 2026-08-06:
#     B1 4.7-5.4%   A2 7.7-13.6%   A1 9.3-10.5%   B2 12.1-16.1%
# So between a twentieth and a sixth of the staging delta denominator is power
# that passed through an uncontrolled attenuation. It enters the theta/delta
# ratio that separates NREM from REM.
#
# WHY IT IS STILL 0.5. Moving it re-scores every recording and moves published
# architecture numbers, and the REM cut is a per-animal percentile that will
# partly absorb the change. That is a scientific decision with a paper attached,
# not a cleanup, and it should be made deliberately and recorded -- not slipped
# in during a refactor. The 0.5 edge is also the ONLY number in this file with no
# external source: the Japanese tool low-passes at 4.5 Hz and has no lower edge
# at all, so 0.5 was our own choice and is the weakest constant here.
#
# WHEN IT IS CHANGED, the honest comparison is a re-scored hypnogram at both
# edges with the kappa packs held constant.
# The band used to build the theta/delta ratio that separates NREM from REM.
# The Japanese scoring tool (SleepyScore) LOW-PASSES at 4.5 Hz for this purpose:
# `delta_cutoff_hz = 4.5`, 2nd-order Butterworth low-pass.
# SOURCE: sleepy_pipeline_refined.py / SleepyScoreApp_HM_260312_exported.m, read
# 2026-08-08. Our lower edge is 0.5 rather than 0 because a 0 Hz edge is not
# meaningful for a band-power integral and the 1.10 Hz hardware high-pass has
# already removed everything below it.
#
# ⚠️ STAGING AND REPORTING USE DIFFERENT DELTA BANDS ON PURPOSE.
# The paper (Nakata 2025, doi:10.1093/sleep/zsae279) quotes delta as 1-4 Hz for
# REPORTED SPECTRA; the tool uses 0-4.5 Hz for STAGING. Those are two jobs and
# one constant cannot serve both.
BAND_TOTAL = (0.5, 30.0)
BAND_NORM = (15.0, 30.0)
# Normalisation band. IIIS Tsukuba express each frequency bin as a percentage of
# the MEAN TOTAL EEG POWER OVER 15-30 Hz across all sleep/wake states, and define
# NREMS delta density as delta power during NREMS over the 15-30 Hz sum during
# NREMS. Adopted 2026-08-08 so our delta values are comparable to theirs.
# SOURCE: Nakata et al., SLEEP 2025, doi:10.1093/sleep/zsae279 (Funato/Yanagisawa).
# CAVEAT: their EEG hardware filter is 0.5-100 Hz; ours is 0.5-30 Hz, so the top
# of this band sits on our filter's roll-off. The normaliser is therefore
# internally consistent but not numerically identical to theirs.

OTSU_SENSITIVITY_MULTIPLIERS = (0.75, 0.90, 1.00, 1.10, 1.25)
# The WAKE/non-WAKE split is an Otsu cut on log10(EMG rms in uV), REFIT PER
# ANIMAL. That means animals are not on a common scale and any cross-animal
# comparison is only as good as the cut's stability. These multipliers are
# applied to the threshold IN LINEAR uV (0.75x and 1.25x = +/-25%), which is the
# interpretable form; in log10 that is -/+0.097.
# Required by the 2026-08-07 council review, which flagged that describing the
# circadian result as "threshold-independent" is false.

EXCLUDE_TRANSITION_EPOCHS_FROM_SPECTRA = True
# IIIS exclude, FROM THE POWER SPECTRUM ANALYSIS ONLY, epochs with artifacts and
# epochs in which either the preceding or the following epoch was in a different
# vigilance state. Staging and state totals still use every epoch.
# SOURCE: same paper.

FILT_EEG = (0.5, 30.0)    # band-pass, 4th-order Butterworth, zero-phase
FILT_EMG = (10.0, 300.0)  # band-pass; 300 Hz or Nyquist-1, whichever is lower
FILT_MAINS = (55.0, 65.0) # Korea mains is 60 Hz

# ---------------------------------------------------------------------------
# QC GATE -- an epoch must pass ALL of these
# ---------------------------------------------------------------------------

OPEN_UV = 150.0
# MEASURED: the pooled distribution of 55-65 Hz amplitude is cleanly BIMODAL in
# log space. Mode A (connected) = 84 uV; mode B (open) = 3731 uV; the valley
# between them sits at 134 uV. 150 uV places the cut just above the valley.
# The previous value of 300 uV sat on the rising flank of the OPEN mode and was
# therefore permissive. Changing 300 -> 150 does not remove any scoreable
# animal (verified by sensitivity sweep 2026-08-03).
# Physical basis: differential_60Hz ~= common_mode * electrode_Z_imbalance, so
# hum amplitude is a direct readout of contact quality, not merely a nuisance.
#
# ✅ RE-DERIVED 2026-08-10 ON POST-RE-PIN DATA and it survives unchanged. The
# original audit used data from the era when the cerebellum ground sat on the
# wrong pin for all seven new mice, so a threshold fitted to that distribution
# had to be re-checked rather than assumed. Repeating the log-space valley search
# on 8 h of allego_0__uid0808-16-17-36 (2,880 epochs x 8 EEG channels, ground
# corrected) puts the valley at 149.4 uV against the constant's 150.0 -- a
# difference of 0.4%. The cut is a property of the amplifier and the electrode
# physics, not of the wiring fault.

FLAT_UV = 11.0
# MEASURED: epoch-level EEG rms has a local minimum at ~11 uV separating a
# small low cluster (2.9-9 uV, amplifier noise floor with no biological signal)
# from the main distribution (13 uV upward). An epoch below this is a dropout.
# The previous single threshold of 25 uV cut into real signal: it discarded
# 9.5% of ALL epochs, including genuine low-amplitude wake.
#
# ⚠️ RE-DERIVED 2026-08-10: THIS CONSTANT IS NOW INERT AND REJECTS NOTHING.
# On 8 h of post-re-pin data (allego_0__uid0808-16-17-36) the 10th percentile of
# epoch rms is 63.8 uV and **0.00%** of epochs fall below 11.0 uV. The low
# cluster this threshold was built to catch does not exist in this cohort: with
# the ground correctly pinned there are no amplifier-floor dropout epochs.
# It is kept because it costs nothing and the failure mode it detects is real on
# other cohorts, but NO CURRENT RESULT DEPENDS ON ITS VALUE, and it must not be
# cited as one of the gates doing work. Anything between 3 and 60 uV would give
# byte-identical output on this data.

DEAD_CHANNEL_UV = 20.0
# A short / dead electrode is a property of the CHANNEL, not of an epoch, so it
# is tested on the channel's median rms across the whole recording rather than
# epoch by epoch. A channel whose median rms is below this never carried EEG.
# Splitting the old 25 uV rule into a channel-level test (this) and an
# epoch-level dropout test (FLAT_UV) is what removes the threshold sensitivity:
# the old rule was the only constant whose exact value moved a verdict.

CLIP_FRAC = 0.0
# Any railed sample makes the epoch's band powers undefined, so we reject on a
# single occurrence. MEASURED: this is free -- results are byte-identical for
# CLIP_FRAC in {0, 1e-3, 1e-2} because railed epochs are already excluded by
# the OPEN test. Clipping is therefore NOT load-bearing for any conclusion.

# ---------------------------------------------------------------------------
# BLOCK STRUCTURE AND PERSISTENCE
# ---------------------------------------------------------------------------
LAG_S = 60
LAG = LAG_S // EPOCH_S            # 15 epochs
MIN_BLOCK = 2 * LAG + 1           # 31 epochs = 124 s, one full lag pair
R_THRESH = 0.30
# CALIBRATED on synthetic alternating states through the identical code path:
#   pure noise -0.035 | 30 s bouts +0.112 | 2 min +0.214 | 4 min +0.510
#   10 min +0.703
# so r > 0.30 at a 1 min lag corresponds to consolidated bouts of roughly 3 min
# or longer. Persistence is computed strictly WITHIN unbroken blocks; measuring
# it across gaps is the 2026-08-03 bug that produced both a false negative
# (+0.078) and the largest false positive in the project (+0.854).

MIN_BLOCK_MINUTES = 15.0   # usable time INSIDE long blocks, not merely in total

# ---------------------------------------------------------------------------
# PLAUSIBILITY
# ---------------------------------------------------------------------------
WAKE_LO, WAKE_HI = 15.0, 90.0
# A mouse over a full day sleeps roughly 50% of the time, more in the light
# phase. Wake outside 15-90% means the staging collapsed onto one state.
# NOTE 06-29/D1 fails here at 96.7% wake with a 2.56 h unbroken wake bout --
# on technically flawless data. That is a real animal state (first tethering),
# not an artefact, which is why the verdict is REJECT and not INSUFFICIENT.

REM_FROM_NREM_MIN = 70.0   # REM is entered from NREM, essentially never from wake

# ---------------------------------------------------------------------------
# IMPEDANCE SCREEN (pre-flight, measured at 1 kHz by the RHD chip)
# ---------------------------------------------------------------------------
IMP_GOOD_MOHM = 0.10
# LITERATURE: epidural screw electrodes in rodents are normally 5-50 kOhm at
# 1 kHz; <=10 kOhm is the usual confirmation of proper epidural contact, and
# silver-treated screws are specified at <=30 kOhm.
IMP_CONNECTED_MOHM = 0.5
# ⚠️ CHANGED 2026-08-09 from 2.0 to 0.5 during the consolidation of this file.
# 2.0 was measured against a no-wire control at 5.233 MOhm and looked safe. It
# is not. On 2026-08-06 a CUT TETHER ATTACHED TO NOTHING, in the A2 position,
# read "connected" in 9 of 40 channel-sweeps = 22 percent at 2.0 MOhm, against
# 3.1 percent at 0.5 MOhm. The false-positive rate at 2.0 MOhm is high enough
# that a block of sweeps on an empty cable looks like a working animal.
# SOURCE: 07-decisions/2026-08-07-rig-specification-and-analysis-method.md §3.2,
# and 05-experiments/completed/2026-08-06-fleet-duty-cycle-census.md.
#
# This constant is used ONLY in stage2_split.py's impedance SUMMARY, which is a
# reported column and not a gate, so this change moves no animal into or out of
# the analysis. It does change the "connected" count printed in
# impedance_summary.csv, and it should: the old count was inflated.
#
# 🔑 0.5 MOhm IS NOT AN ABSOLUTE CONTACT STATEMENT. It beats a floor. On the
# ECG cohort it calls the best channel this rig ever had (B1 EEG, median 0.813
# MOhm) open. Always use it against the wire-free floor measured IN THE SAME
# SWEEP BLOCK, never as a bare number.
#
# 🔑 AND A LOW STABLE IMPEDANCE CAN MEAN NO GROUND AT ALL. Seven animals read
# 100 percent duty with ZERO FLIPS on 2026-08-07 while recording no biology
# whatsoever, because their ground pin was on the wrong wire and the return path
# ran through the paired electrode. Zero flips is a WIRING SIGNATURE, not a good
# electrode: every genuine contact failure on this rig has been intermittent.
#
# Prior value, kept for reading old outputs:
IMP_CONNECTED_MOHM_RETIRED_2026_08_06 = 2.0
#
# READ THIS BEFORE QUOTING IMPEDANCE. Our best channel in the fleet is 0.073
# MOhm = 73 kOhm, which is ALREADY above the literature ceiling for a good
# epidural screw. So IMP_CONNECTED_MOHM is not a quality bar, it is only an
# open-circuit detector, and it is ~40x looser than the literature norm. A
# channel at 0.5-2 MOhm is a POOR electrode that merely is not fully open.
# Impedance predicts CLASS (which channel is connected) and NOT YIELD (how many
# usable hours you get): B1 read 0.133 MOhm at rest yet ran at 2802 uV hum for
# an entire recording. Resting impedance is not contact under load.
# Read only the /1 and /2 sites; /3 and /4 are empty pads with no wire.

# ---------------------------------------------------------------------------
# ANIMAL ROOM LIGHT CYCLE (recorded 2026-08-03)
# ---------------------------------------------------------------------------
LIGHTS_ON_HOUR = 9     # 09:00 KST
LIGHTS_OFF_HOUR = 21   # 21:00 KST
# 12:12 LD. ZT0 = 09:00 KST. Light phase ZT0-ZT12, dark phase ZT12-ZT24.
TZ_OFFSET_HOURS = 9    # KST = UTC+9; xdat metadata start_time is UTC

# ---------------------------------------------------------------------------
# CHANNEL MAP -- RHD2216 is a BIPOLAR chip
# ---------------------------------------------------------------------------
# port_base + 0 = /1  = EEG   <- already a difference, do NOT subtract
# port_base + 1 = /2  = EMG   <- already a difference, do NOT subtract
# port_base + 2,3     = /3,/4 = EMPTY PADS, no wire attached
# second animal on a 64-channel splitter port: port_base + 32, +33
# Layout is ALWAYS derived from the file's own sensors_by_port, never assumed.

OUTPUT_FS = 250   # Hz, decimation target for per-mouse files
# 250 Hz keeps the full 0.5-30 Hz EEG analysis band and 10-100 Hz of EMG with
# large margin, and shrinks a per-mouse file 4x versus the 1 kHz raw rate.

# ---------------------------------------------------------------------------
# CONNECTION CRITERIA -- judging a channel against WIRE-FREE INPUTS IN THE SAME
# FILE. Added here 2026-08-09; these numbers previously existed only as literals
# inside three separate copies of the same loop.
# ---------------------------------------------------------------------------
#
# WHY AN IN-FILE FLOOR AT ALL. A mouse uses only a few of its chip's 16
# amplifier inputs. The rest are real amplifier inputs with no wire attached,
# recorded simultaneously, through the same amplifier, the same cable and the
# same room. They are the perfect negative control and they are free. Judging a
# channel against them, rather than against a fixed number, is what makes the
# verdict robust to the room, the day and the gain setting.
#
# 🛑 A FILTERED NO-WIRE CHANNEL LOOKS LIKE BEAUTIFUL EEG. A wire-free input put
# through a 60/120/180 Hz notch and a 0.5-30 Hz band-pass emerges as a median of
# about 69 uV of smooth, plausible, EEG-shaped signal. NEVER judge by eye.

RMS_LO_UV, RMS_HI_UV = 10.0, 150.0
# Plausible amplitude window for a connected rodent EEG/EMG channel, applied per
# QC epoch. Below is a dropout, above is hum or railing.

FLOOR_PERCENTILE = 1
# Both criteria compare a channel against the 1st percentile of the wire-free
# distribution measured in the SAME FILE. Not a fixed number, and not the
# median: we want "better than nearly every unwired input", not "better than
# average".

FLOOR_SCOPE = "chip"
# "chip"  -- the wire-free inputs of the SAME port+slot as the animal (correct)
# "pooled" -- all wire-free inputs in the file (the historical behaviour, WRONG)
#
# WHY THIS EXISTS. usable_fraction's own definition says the comparison is made
# against wire-free inputs "recorded simultaneously through the same chip, cable
# and room". Pooling all 8 chips contradicts that sentence, and it is not a
# harmless approximation: chips differ. MEASURED on allego_0__uid0825-09-00-00,
# the pooled slope threshold is -1.94 while the per-chip thresholds run from
# -0.95 (A2) to -2.38 (B1). Under the pooled number EVERY animal in that file
# fails, including ones with 96% usable EEG against their own chip. A single
# floating headstage is enough to drag the pooled floor steep and condemn the
# whole rig, which is exactly what happened on 2026-08-18.
#
# DIRECTION RULE, measured repeatedly: a FAIL under the pooled floor is suspect,
# a PASS under it is conservative and survives the change to per-chip.

FLOOR_ESTIMATOR = "site_p1_median"
# How the percentile is estimated from a chip's wire-free sites.
#   "pooled_p1"       -- percentile over every (epoch, site) value together
#   "site_p1_median"  -- percentile per SITE, then the median across sites
#
# WHY NOT "pooled_p1". A chip has only ~14 wire-free sites. Pooling their epochs
# lets the lower tail of ONE unrepresentative site set the threshold for the
# whole chip. MEASURED on allego_0__uid0825-09-00-00 chip A1: every floor site
# has a flat median slope (+0.38 to -0.74), yet sites A/11-A/15 are partially
# coupled (rms 651-2696 uV, lf/hf 3.6-5.2) and their epoch tails drag the pooled
# p1 down to -1.59, the strictest bar on the rig. Taking the percentile per site
# first and then the median makes one bad site a minority vote instead of the
# decider. Across-chip spread of the threshold falls from 1.16 to 0.96.
#
# 🛑 THIS CHOICE WAS NOT MADE BY LOOKING AT WHICH ANIMALS IT PASSES. It is a
# robustness argument about estimating a percentile from a small, heterogeneous
# sample. It moves A1's threshold by 0.07 and does NOT change A1's verdict.

FLOOR_MIN_HUM_UV = 800.0
# A chip whose wire-free inputs are QUIETER than this has no ground reference,
# so its floor is not a valid negative control and no verdict can be drawn from
# it. Such a chip is UNJUDGEABLE, which is not the same as the animal failing.
#
# WHY 800. A grounded chip's wire-free inputs sit in mains hum. MEASURED across
# every recording since 2026-08-07, a grounded chip's floor 60 Hz is 1138-5609
# uV and a floating one is 82-466 uV -- two populations separated by more than a
# factor of two with nothing in between. 800 sits in that empty gap. The value
# is deliberately NOT tuned to any animal's verdict; moving it anywhere inside
# 500-1100 changes nothing about which chips are called floating.

SLOPE_BAND_HZ = (1.0, 40.0)
# Band for the log-log spectral slope. Starts at 1.0 because the acquisition
# high-pass sits at 1.10 Hz, ends at 40 to stay clear of the 60 Hz mains and its
# harmonics, so the slope criterion needs NO notch filter to be valid.
# Real EEG is steep (working animals -1.5 to -2.1); a wire-free input is flat
# (floor -1.29 to -0.07).
#
# 🔴 CORRECTED 2026-08-10. THIS CONSTANT USED TO CARRY THE CLAIM "FILTERING
# CANNOT MANUFACTURE SLOPE, WHICH IS EXACTLY WHY THIS CRITERION SURVIVES THE
# TRAP". THAT CLAIM IS FALSE, and tests/test_criterion_falsification.py now
# demonstrates it. MEASURED on 3,000 s of synthetic noise:
#
#     slope over 1-40 Hz     raw white   0.00     <- a wire-free input
#     ... after a 4th-order 0.5-30 Hz band-pass  -1.08     <- MANUFACTURED
#     ... real 1/f^1.8 EEG                       -1.81
#
# The 30 Hz corner of the EEG band-pass sits INSIDE this 1-40 Hz window, and its
# roll-off is read as spectral slope. A band-passed wire-free input therefore
# scores 100.0% usable. Filtering manufactures slope whenever a filter corner
# lies in the measurement band.
#
# ✅ WHY THE BAND IS NEVERTHELESS UNCHANGED. compute_features reads the RAW
# memmap and filters nothing, and the only filtering that reaches the saved file
# is the acquisition chain, whose 1.10 Hz high-pass contributes +0.08 here --
# negligible and of the wrong sign to flatter a channel. MEASURED on 6 h of the
# re-pinned 2026-08-08 recording: the wire-free floor scores 0.00% under this
# band, moving to (2, 20) also gives 0.00%, and NO VERDICT CHANGES either way
# while every working animal's usable fraction falls 12-16 points. Narrowing the
# band would therefore restate every published number to buy nothing on data
# that is not filtered.
#
# 🔑 THE PRECONDITION IS NOW ENFORCED INSTEAD. The criterion is valid only on
# UNFILTERED input, so criteria.py refuses to apply it to a band-limited channel
# rather than trusting the caller to remember. See BANDLIMIT_* below.
# A band of (2.0, 20.0) is immune by construction (it clears both the 1.10 Hz
# high-pass and the 30 Hz corner) and is the right choice if this criterion is
# ever applied to filtered data on purpose.

# --------------------------------------------------------------------------- #
# BAND-LIMIT GUARD -- is the slope criterion even being shown raw data?
# --------------------------------------------------------------------------- #
BANDLIMIT_LO_BAND = (1.0, 25.0)
BANDLIMIT_HI_BAND = (25.0, 45.0)
BANDLIMIT_MAX_DROP = -1.0
# A power law is SCALE FREE: its log-log slope is the same in any sub-band. A
# filter corner is not. So measuring the slope in two adjoining sub-bands and
# taking the difference separates "steep because it is 1/f" from "steep because
# a filter rolls off here", which is precisely what the criterion needs and what
# the single-band measurement cannot see.
#
# MEASURED, same synthetic set (slope 25-45 minus slope 1-25):
#     raw white, wire-free        -0.05      scale free
#     real 1/f^1.8 EEG            +0.04      scale free
#     1/f^1.5                     +0.07      scale free
#     acquisition high-pass only  -0.11      scale free in this window
#     ---------------------------------------------------------------
#     band-passed 0.5-45 Hz       -2.12      BAND LIMITED
#     band-passed 0.5-30 Hz      -11.25      BAND LIMITED
#
# Every scale-free case sits inside +/-0.11 and every band-limited case beyond
# -2.1, so a bar at -1.0 has an order of magnitude of margin on both sides. It
# is set at a round number rather than fitted, because a threshold fitted to two
# clusters this well separated would only be false precision.

CRITERION_DEFAULT = "slope"
# "slope" | "hum". See core/criteria.py.
#
# 🔴🔴 THE HUM CRITERION IS CONDITIONALLY VALID AND MUST BE CHECKED PER COHORT.
# It asks "is the 60 Hz amplitude below the wire-free floor", and it works only
# while the floor's hum distribution is BIMODAL, i.e. while connected and open
# channels really do sit in two separated modes. On the original EEG+EMG cohort
# that held: mode A 84 uV, mode B 3731 uV, valley at 134 uV, roughly 100x apart.
#
# On the ECG cohort it BROKE, and the animal that broke it is instructive. A1
# was recording with NO GROUND AT ALL, and scored 100 percent "usable" on the
# hum criterion, because a floating BIPOLAR pair rejects mains as common mode
# and is therefore QUIET. The criterion rewards quiet, and no-ground is quiet.
# Its median 60 Hz was 44-78 uV against a wire-free floor median of 3962 uV.
#
# Therefore core/criteria.py REFUSES to run the hum criterion unless the floor's
# own bimodality is verified in that same file. That refusal is a hard error, on
# purpose: the alternative is a confident, wrong, publishable number.

# HOW THE REFUSAL IS ACTUALLY TESTED. The obvious guard, "check the wire-free
# floor is bimodal", DOES NOT WORK, and it is worth writing down why so nobody
# reimplements it. The floor's 60 Hz median was high in BOTH cohorts, about
# 2276 uV on the working one and 3962 uV on the broken one. The floor is not
# what changed. What changed was the animal side: with no ground, a floating
# bipolar pair is QUIET, so it slips under a threshold built from a loud floor.
#
# The test that did catch A1 is the DISAGREEMENT BETWEEN THE TWO CRITERIA.
# A1 scored 100.0 percent usable on hum and 0.0 percent on slope, on the same
# epochs of the same channel. Quiet and flat at once is not an electrode, it is
# an unreferenced amplifier input. So criteria.py computes BOTH criteria always,
# and refuses to report a hum number for any channel where they contradict.
HUM_CONTRADICTION_HUM_MIN = 0.50   # hum criterion calls at least half the epochs usable
HUM_CONTRADICTION_SLOPE_MAX = 0.05  # ... while the slope criterion calls almost none
# Both conditions together = the floating-no-ground signature. On this rig it has
# now reproduced three days running on the same animal.

MIN_USABLE_EPOCHS = 30
# Below this many QC epochs (= 5 min at 10 s) a usable fraction is a ratio of
# small integers and is reported as INSUFFICIENT rather than as a percentage.

# ---------------------------------------------------------------------------
# FAILURE-MODE DISCRIMINATORS (which fault hides behind "OPEN")
# ---------------------------------------------------------------------------
SHARED_PATH_CORR = 0.50
# Correlation between an animal's OWN two filtered channels. Working animals sit
# at 0.07-0.08; a fault in a path shared by both channels drives it up. D1
# measured 0.74 and B2 0.50, which is what identified them as one upstream fault
# rather than two coincidental electrode failures.

CONNECTED_HUM_BAND_UV = (9.0, 90.0)
# An EMG channel whose 60 Hz amplitude falls in this band is genuinely connected
# even when its EEG partner is floating. Used to tell "one good channel of two"
# apart from "both dead".
