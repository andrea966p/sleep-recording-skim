---
tags: [methods, eeg, emg, procedure, scoring, report, canonical]
created: 2026-08-03
status: active
audience: PI / lab meeting / methods section
---

# How a recording becomes scorable, step by step

> [!abstract] TL;DR
> This is the ordered procedure that takes one raw recording from the acquisition
> computer to a file a person can open and score by hand, with the reason for
> every step and a pointer to the code and the source it comes from.
>
> **The method itself is conventional.** Four second epochs, delta and theta band
> power, electromyogram (EMG) tone, per animal thresholds, then validation
> against known physiology and against the light cycle. Nothing here is invented
> to suit our rig.
>
> **We add one thing on top, and it is also conventional:** we reject epochs where
> the electrode is not electrically connected, using the size of the fifty five to
> sixty five hertz mains signal. Flagging bad channels by their line noise level
> is standard practice in electroencephalogram (EEG) preprocessing pipelines.
>
> **The one genuinely unusual thing about this project is not the method, it is
> that most of the data has to be thrown away.** That is a hardware problem, not
> an analysis problem, and no amount of method design fixes it.

Code: `02-procedures/eeg-data-analysis/pipeline/`. Operating manual:
[[pipeline/README]]. Every numeric constant lives in one file,
`qc_thresholds.py`, with its justification written next to it, so there are no
unexplained numbers anywhere else in the codebase.

---

## 1. What is standard, and what we added

I want this table read first, because it is the question a reviewer will ask.

| Part of the analysis                                                                                       | Standard, or ours?                                     | Note                                                                                                                                                                     |
| ---------------------------------------------------------------------------------------------------------- | ------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| Record wide band, filter offline                                                                           | **Standard**                                           | Intan, Open Ephys and Radiens all default to this. Filtering is irreversible, so it is done as late as possible                                                          |
| Band pass EEG 0.5 to 30 hertz, EMG 10 to 300 hertz                                                         | **Standard**                                           | Oishi 2016 uses 0.5 to 64 and 16 to 64, Kim 2022 uses 0.3 to 100                                                                                                         |
| Four second epochs                                                                                         | **Standard**                                           | Published rodent work spans 4, 5, 10 and 20 seconds                                                                                                                      |
| Delta 0.5 to 4 hertz, theta 6 to 9 hertz, theta over delta ratio                                           | **Standard**                                           | The conventional rodent discriminator                                                                                                                                    |
| EMG tone separates wake, threshold per animal                                                              | **Standard**                                           | Oishi 2016, and every automatic scorer                                                                                                                                   |
| Reject saturated epochs                                                                                    | **Standard**                                           | Universal in EEG preprocessing                                                                                                                                           |
| **Reject epochs where the electrode is disconnected, using mains amplitude**                               | **Standard method, our threshold**                     | Line noise is a recognised bad channel metric (PREP pipeline, EEGLAB `clean_rawdata`). Bad channel thresholds are always data derived, ours came from our own recordings |
| Check the three states behave like wake, non rapid eye movement (NREM) and rapid eye movement (REM) should | **Standard**                                           | Basic sanity checking                                                                                                                                                    |
| Compare sleep amount against published C57BL/6 values for the light phase                                  | **Standard**                                           | The strongest external check we have                                                                                                                                     |
| **Persistence statistic `r@1min`**                                                                         | **OURS. It is a validity check, not a scoring method** | We added it to test whether the states are real or noise. It does not assign any epoch to a stage. Treat it as extra scrutiny, not as part of the staging                |

> [!important] On the persistence statistic
> I want to be explicit, because it would be easy to present this as if it were a
> conventional criterion and it is not. `r@1min` measures whether sleep and wake
> come in runs rather than flickering at random. Real sleep is consolidated, noise
> is not. We added it after twice mistaking noise for sleep, so it exists to stop
> us fooling ourselves, and it is calibrated against synthetic data so the number
> means something concrete. But it is our own addition and it should be described
> that way in any methods section.

---

## 2. Answering the obvious question about the mains filter

**Yes, turn the sixty hertz notch on in Allego.** It is display only. We confirmed
this on 2026-07-31 by parking the notch at fifty hertz, where nothing real lives,
and checking the saved spectrum: one hertz bins across forty seven to fifty three
hertz came out 2.457, 2.504, 2.354, 2.401, 2.365, 2.462, perfectly flat, no null.
The notch never reaches the saved file. Switch it on, the live traces become
readable, and nothing about the data changes.

**Sixty hertz is removed before any analysis anyway.** The EEG band pass is 0.5 to
30 hertz, so mains is excluded by construction from every band power and every
number in any report. We do not analyse hum contaminated signal.

So there are two separate questions, and they have different answers:

| Question | Answer |
| --- | --- |
| Is sixty hertz removed before analysis? | **Yes, always**, by the 0.5 to 30 hertz band pass. Standard. |
| Is sixty hertz destroyed when the file is written? | **No**, and that is also standard. |

The only reason this is worth a paragraph at all is that the mains amplitude, in
the raw file, happens to tell us whether the electrode is connected. Keeping the
raw file costs nothing and preserves that. It is a free by product of doing the
standard thing, not a reason to do something unusual.

---

## 3. The procedure

```
raw .xdat  ──1──►  layout  ──2──►  filter, epoch  ──3──►  quality gate
                                                              │
    EDF+ for the scorer  ◄──6──  per mouse files  ◄──5──  ◄──4── worth scoring?
```

```bash
python3 stage1_qc.py         allego_1__uid0731-18-06-37 --json qc.json
python3 stage2_split.py      allego_1__uid0731-18-06-37
python3 stage3_features.py   /home/skimlab/eeg-processed/2026-07-31
python3 stage4_export_edf.py /home/skimlab/eeg-processed/2026-07-31
```

Use the system `python3`, not the `/opt/neurosurveillance` virtual environment,
which has a numpy and scipy version conflict and fails on import.

### Step 0. Write down what the file cannot tell you

**What.** Implant date, tethering date, which animal is on which port and slot,
and the light schedule.

**Why.** None of this is stored in the recording, and without it the data cannot
be interpreted. Both eight mouse runs turned out to be eight to twelve days after
implantation with about one day of tethering, against our own protocol of at
least fourteen days and at least seven days of cage acclimatisation, which
changes how every sleep number should be read.

**Source.** Oishi 2016 (habituate two to three days),
[[tsukuba-sleep-recording-method]] (recover at least five days, acclimatise at
least seven days, at least fourteen days from implant to recording).

⚠️ **THIS IS CURRENTLY LOGGED NOWHERE. IT NEEDS TO START.**

### Step 1. Work out which channel is which, from the file itself

**What.** Read `sapiens_base.sensors_by_port`, take `connection_ntv_idx` as the
port base, then the animal in splitter slot one is at base plus zero (EEG) and
base plus one (EMG), and slot two is at base plus thirty two and base plus thirty
three. In Allego that is `/1`, `/2`, `/33`, `/34`.

**Why.** The RHD2216 is a bipolar chip, so each amplifier has two electrode pins
and outputs their difference in hardware. The four wires on adapter pads zero to
three are therefore **two channels, not four**. Channel counts also vary between
recordings (thirty two per port, sixty four per port, and mixed), so assuming a
layout silently mis maps the older files.

**Code.** `pipeline_common.derive_layout()`.

**Source.** Intan RHD2000 datasheet page 1, "16 amplifiers having independently
accessible differential inputs (in0+, in0–, in1+, in1–, …)", and page 20, "Only
channels 0-15 are active in the RHD2216", which is why a port shows thirty two
slots per chip. Verified against the recorded metadata and by measuring all sixty
four slots on all four ports: [[CANONICAL-allego-channel-selection]].

> [!danger] TWO MISTAKES THIS STEP PREVENTS
> **NEVER SUBTRACT `/1` FROM `/2`.** That computes EEG minus EMG, which is
> meaningless. The chip already did the subtraction.
> **NEVER TREAT `/3` OR `/4` AS EMG.** They are amplifiers with no wires on their
> inputs. Doing both of these cost this project several weeks and produced twenty
> four phantom "failed EMG surgeries".

### Step 2. Filter and cut into epochs

**What.** Zero phase fourth order Butterworth filters: EEG 0.5 to 30 hertz, EMG 10
to 300 hertz, and a separate 55 to 65 hertz band kept only as a noise measure.
Four second epochs. Welch power spectral density with `nperseg = 2048`.

**Why.** Sleep EEG content sits below thirty hertz and muscle tone is broadband.
Zero phase filtering does not shift events in time. Four seconds is at the fine
end of the accepted rodent range and suits mouse sleep, which is much more
fragmented than human sleep.

**Code.** `stage1_qc.extract_features()`.

**Source.** Oishi 2016 (EEG 0.5 to 64 hertz, EMG 16 to 64 hertz, ten second
epochs), Kim 2022 (0.3 to 100 hertz, ten second epochs), needle electrode
preprint 2026 (five second epochs). Delta 0.5 to 4 hertz and theta 6 to 9 hertz
follow the rodent convention, and Kostin 2025 warns specifically against putting
seven hertz on a band boundary.

> [!danger] `nperseg = 2048`, DO NOT LOWER IT
> Frequency resolution is sampling rate divided by `nperseg`, so 0.49 hertz here.
> At `nperseg = 512` it becomes 1.95 hertz, the six to nine hertz theta band
> collapses into a SINGLE frequency bin, and integrating over one point returns
> EXACTLY ZERO. That silently destroys every REM measurement with no error raised.

### Step 3. Decide which epochs are usable

An epoch must pass all of these, and the reason for any rejection is recorded.

| Test | Rule | Why, and where the number comes from |
| --- | --- | --- |
| **Open** | 55 to 65 hertz below **150 microvolts** on EEG and EMG | The electrode is not in contact. Measured across 1,137,955 epochs, the distribution is bimodal in log space: connected mode 84 microvolts, open mode 3731 microvolts, valley at 134 microvolts. The previous value of 300 sat on the flank of the open mode and was too permissive |
| **Flat** | EEG root mean square at least **11 microvolts** | A momentary dropout. Measured as the local minimum separating the amplifier noise floor from real signal |
| **Dead** | Channel median root mean square at least **20 microvolts** across the whole recording | A short circuit is a property of the CHANNEL, not of an epoch, so it is tested once per channel rather than epoch by epoch |
| **Clipped** | **Zero** saturated samples, rail at **6389.6 microvolts** | A saturated amplifier makes band powers undefined. Measured: the maximum absolute sample is 6389.8 microvolts, identical on all eight channels, which is 0.195 microvolts per bit times 32767, the sixteen bit converter full scale |
| **Finite** | Delta, theta and EMG amplitude all above zero | Degenerate epochs |

**Code.** `stage1_qc.gate()`.

**Why these tests.** Published rodent pipelines assume the electrode works and
reject **artefacts**, for example Kostin 2025 uses mean plus or minus four
standard deviations on the amplitude envelope. Our dominant failure is not an
artefact, it is **no electrical contact at all**, which those gates do not test
for. Rejecting channels on line noise is itself standard, the PREP pipeline and
EEGLAB `clean_rawdata` both do it, so what is specific to us is only the
threshold value, and bad channel thresholds are always derived from the data at
hand.

> [!important] THE THRESHOLDS WERE TESTED FOR SENSITIVITY
> Every threshold was swept across its plausible range. Animal C1 is invariant,
> giving `r = 0.74` over 8.7 hours in EVERY variant tested, and C2 survives every
> variant. Clipping turns out not to matter at all. A conclusion that moved when a
> threshold moved would not be reportable, and these do not move.

### Step 4. Group into unbroken blocks, then decide whether it is worth scoring

**What.** Join consecutive passing epochs into blocks, keep blocks of at least 124
seconds, then require at least fifteen minutes inside blocks, a within block
persistence above 0.30, a passing physiology check, and a wake fraction between
fifteen and ninety percent.

**Why blocks matter.** Contact is intermittent, so the epochs that pass are
**fragments scattered through time**. Any statistic computed over the
concatenated array compares epochs that may be hours apart. That is exactly the
error we found on 2026-08-03, and it failed in both directions: it produced the
largest false positive in the project, a value of plus 0.854 on a stretch that is
thirty nine minutes of pure wake, and it also hid a real result, plus 0.078 on
data that could not possibly have passed.

**Code.** `pipeline_common.blocks_of()` and `within_block_persistence()`.

**Calibration** on synthetic data through the same code path: pure noise minus
0.035, thirty second bouts plus 0.112, two minute plus 0.214, four minute plus
0.510, ten minute plus 0.703. So a value above 0.30 corresponds to consolidated
bouts of roughly three minutes or longer.

Remember from section 1 that this persistence test is **our addition and a
validity check**, not a staging rule. It decides whether we believe the staging,
it does not assign any epoch to a stage.

### Step 5. Split into one file per mouse, organised by day

**What.** Anti aliased decimation to 250 hertz, one file per animal, named
`port{PORT}-slot{SLOT}_{DATE}_{HHMMSS}_{DURATION}.npz`, inside a folder for that
day that also carries the impedance sweeps and the quality control summary.

**Why 250 hertz.** It keeps the whole 0.5 to 30 hertz EEG band and 10 to 100 hertz
of EMG with a large margin, and it makes the file four times smaller than the one
kilohertz raw rate. For comparison Kim 2022 records at 500 hertz and Oishi 2016
digitises at 128 hertz.

**Why the raw file is never modified.** The `.xdat` is the master copy, so
everything can be re derived if a decision later turns out to be wrong. That has
already happened twice on this project.

**Code.** `stage2_split.py`.

⚠️ **THE DAY FOLDER DATE COMES FROM THE METADATA UTC `start_time`, CONVERTED TO
KOREAN TIME.** The `uidMMDD-HH-MM-SS` token in the filename is ALREADY LOCAL, so
mixing the two files a recording under the wrong day and shifts every zeitgeber
time by nine hours.

### Step 6. Export to EDF+ so a person can score it

**What.** `stage4_export_edf.py` writes a two signal (EEG and EMG) EDF+C file per
animal, plus a plain language `_SCORER-README.txt` that lists the time windows
worth scoring.

**Why EDF+.** It is the portable format every scoring tool imports, and it is the
agreed hand off to the scorer at the International Institute for Integrative
Sleep Medicine (IIIS).

**Implementation.** Written with no third party dependency. The archived
`xdat_to_edf.py` needed the `pyedflib` package and, worse, computed bipolar
derivations, which is the retracted pre 2026-08-01 model. The physical range is
pinned to the true converter rail of plus or minus 6389.56 microvolts, so the EDF
step equals the hardware bit size of 0.195 microvolts and no extra rounding error
is introduced. Verified by reading the file back: maximum error 0.195 microvolts,
which is exactly one bit, so pure quantisation and no scaling bug.

Three deliberate choices:

1. **The automatic staging is NOT written into the EDF.** A scorer who sees our
   labels cannot un see them, and this project's recurring failure has been
   believing its own automatic output. Score blind first, then compare against
   `*_hypnogram.csv`.
2. **Rejected epochs are left in place, not cut out.** Deleting them would splice
   discontinuous time into a continuous file and destroy the scorer's sense of
   how long a bout is, which is the same class of error as the persistence bug.
3. **The scorer is told which windows to score**, with start and end times, so
   the excluded stretches are not mistaken for flat physiology.

---

## 4. What the scorer receives, per animal

```
portC-slot1_2026-07-31_180637_27h54m.edf                 <- open this
portC-slot1_2026-07-31_180637_27h54m_SCORER-README.txt   <- read this first
portC-slot1_2026-07-31_180637_27h54m_hypnogram.csv       <- compare AFTER scoring
portC-slot1_2026-07-31_180637_27h54m_summary.txt
../impedance/   ../qc/qc_summary.csv   ../README.txt
```

A real example, animal C1:

```
SCORE ONLY INSIDE THESE WINDOWS
    from (h:mm:ss)      to (h:mm:ss)    minutes
           0:00:00           8:05:44      485.7
           8:06:08           8:43:56       37.8
```

---

## 5. One thing we will not report

**We do not report a REM percentage**, and I want that stated rather than quietly
omitted. The rule that defines REM (the top twenty percent of the theta over delta
ratio among non wake epochs) fixes its share by construction. An independent
threshold found by Otsu's method gives twenty four to forty eight percent of
sleep, and the published value for mice is below ten percent. Both rules land far
above it, so REM is not reliably separable with this montage. What we do report is
wake versus NREM, and the ORDER property that REM is entered from NREM rather than
from wake, which is a real and checkable feature.

---

## 6. Sources

- Oishi, Takata, Taguchi, Kohtoh, Urade, Lazarus (2016). Polygraphic recording
  procedure for measuring sleep in mice. *Journal of Visualized Experiments* 107.
- Kim et al. (2022). Nine day continuous recording of EEG and 2 hour high density
  EEG under chronic sleep restriction in mice. *Scientific Data* 9.
- Hsieh et al. (2024). An open source mouse chronic EEG array system with high
  density MXene based skull surface electrodes. *eNeuro* 11(2).
- Choi, Koch, Poppendieck, Lee, Shin (2010). High resolution electroencephalography
  in freely moving mice. *Journal of Neurophysiology* 104.
- Kappenman and Luck (2010). The effects of electrode impedance on data quality and
  statistical power in human EEG. *Psychophysiology* 47(5).
- Kostin et al. (2025). Open source algorithm for automated vigilance state
  classification using single channel EEG in rodents. *Sensors* 25(3).
- Minimally invasive EEG recording in mice using thin needle electrodes, preprint
  (2026).
- Intan Technologies. RHD2000 series digital electrophysiology interface chip
  datasheet. Local copy: `06-references/datasheets/`.
- NeuroNexus. Radiens technical documentation, and the `radiens-core` Python
  client version 0.0.8.

Papers are in `~/Desktop/andrea/papers/`. The full evaluation of them against our
own data is in
[[2026-08-03-literature-check-impedance-and-electrode-failure]].

---

## 7. Still open

- **The bench test with a multimeter on the adapter pads has not been done.** It
  is free, it needs no animal contact, and it is the only way we currently have to
  measure the negative electrode of each pair at all.
- **Implant and tethering dates are not being logged.** Without them the
  degradation across runs cannot be interpreted.
- **No recording has yet been made under our own protocol** of at least fourteen
  days after implantation and at least seven days of tethering, so we do not know
  what this rig does under correct conditions.
- **The impedance sweep measures only one electrode of each pair.** The chip can
  measure both, using the `Zcheck pol sel` register, but the Radiens software
  exposes no way to reach it. This is worth raising with NeuroNexus.
- Room temperature and humidity are not logged, and Kappenman 2010 shows warm and
  humid conditions make high impedance recordings substantially worse.
