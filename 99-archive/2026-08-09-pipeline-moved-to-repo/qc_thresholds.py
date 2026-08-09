#!/usr/bin/env python3
"""Single source of truth for every constant in the EEG pipeline.

RULE: no magic numbers anywhere else in the pipeline. Every constant here
carries its provenance -- either a measurement on our own data, a hardware
datasheet value, or a literature citation. If a number has no provenance it
does not belong in a paper.

Audited 2026-08-03 against 1,137,955 pooled 4 s epochs (41 animal-recordings).
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

FLAT_UV = 11.0
# MEASURED: epoch-level EEG rms has a local minimum at ~11 uV separating a
# small low cluster (2.9-9 uV, amplifier noise floor with no biological signal)
# from the main distribution (13 uV upward). An epoch below this is a dropout.
# The previous single threshold of 25 uV cut into real signal: it discarded
# 9.5% of ALL epochs, including genuine low-amplitude wake.

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
IMP_CONNECTED_MOHM = 2.0
# OUR EMPIRICAL open/closed separator: legs read 5.2-8.7 MOhm when open, versus
# a no-wire control at 5.233 MOhm.
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
