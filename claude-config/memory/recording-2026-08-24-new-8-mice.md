---
name: recording-2026-08-24-new-8-mice
description: "2026-08-24 one-hour screen of 8 newly plugged mice: 4 give hour-long EEG, only D2 passes the strict EEG+EMG gate, and 3 of 8 chips have a CONTAMINATED wire-free floor that fakes an EEG failure"
metadata: 
  node_type: memory
  type: project
  originSessionId: aa023ba0-4d68-4842-9819-c574f4dde34b
  modified: 2026-08-24T10:09:07.595Z
---

⭐⭐ **`allego_0__uid0824-17-56-51`, 2026-08-24 17:56:51-18:56:54 KST, 60.04 h:mm min, 3.78 GB.
RUNG 0 PASS — 3,602,432 data samples = 3,602,432 timestamp samples, remainders 0 and 0.**
✅⭐⭐ **BATCH = `S-SD` (SOD1 + CSD). IDENTITIES NOW KNOWN — the first cohort in this project with
REAL animal ids, surgery dates and body weights instead of placeholders.** Source: the lab's own
`~/Downloads/HLB_SOD1_Intake_Monitoring.xlsx`, sheet **`Registry`** (⚠️ header is on **row 5**, not
row 1; `openpyxl` lives ONLY in `~/eeg-analysis-venv`). Manifest written and schema-validated:
`eeg-emg-analysis/cohorts/S-SD.yaml`.

| pos | mouse | surgery | BW pre→teth | surgery note |
|---|---|---|---|---|
| A1 | HLBSSD11 | 08-10 | 31.4→32.2 | **bleeding F-L eeg**, struggle to induce anaesthesia, hiccups strong |
| A2 | HLBSSD12 | 08-10 | 28.9→29.5 | — |
| B1 | HLBSSD13 | 08-10 | 29.7→30.4 | — |
| B2 | HLBSSD14 | 08-10 | 29.3→28.8 | — |
| C1 | HLBSSD15 | 08-11 | 28.4→31.5 | **bleeding P-L eeg** |
| C2 | HLBSSD16 | 08-11 | 31.4→30.9 | — |
| D1 | HLBSSD19 | 08-12 | 31.0→31.4 | *"tethered in the habituation rack. Might have tether damaged due to climbing"* |
| D2 | HLBSSD18 | 08-11 | 29.0→28.6 | lots superficial bleeding, lots of bleeding from 4 holes |

All male, DOB 2026-05-04, arrived 07-28, **all tethered 2026-08-18**. HLBSSD17 operated+tethered but
**no XDAQ position**; HLBSSD20 **Excluded**. ⚠️ Registry says `Recording start = 2026-08-25` but the
run was actually 08-24 — **the sheet is a day behind**. CSD start 08-27, sampling 09-03.

8 mice on the rig. 2 roles (EEG `/1` `/33`, EMG `/2` `/34`), NO ECG; `/3` and `/35` are
bare floor on every port. See [[cohort-identity-every-run-is-new-mice]].

## ⭐⭐ SURGERY NOTES vs MEASURED OUTCOME — the notes are NOT predictive, with one exception
- ✅ **D1 = HLBSSD19, "might have tether damaged due to climbing"** → its EEG dips to 8% mid-run and
  recovers to 92%. **A damaged tether IS movement-dependent intermittent contact. ACT ON THIS ONE:
  replace D1's tether.**
- 🟡 A1 = HLBSSD11 "bleeding F-L eeg" → EEG intermittent (35.3%), EMG fine. Consistent, but see below.
- 🔴 **C1 "bleeding P-L eeg" gives 99.7% EEG, and D2 "lots of bleeding from 4 holes" is the BEST
  animal in the cohort and the only strict pass.** ⇒ **Surgical bleeding notes do NOT predict signal
  quality. Do not triage animals on them.**
- ⭐⭐ **B1 = HLBSSD13 has NO adverse note, normal weight gain, and gives NOTHING.** Combined with B
  slot 1 failing across three cohorts and having the rig's weakest floor, I read this as **B1 being a PORT FAULT**.
  🔴 **WRONG — RETRACTED 2026-08-26 by a swap test: [[b-slot1-was-the-tether-not-the-port]].** 🔑 **TESTABLE: move HLBSSD13 to a working
  position (or put the spare HLBSSD17 into B1). If the fault follows the position, it is the rig.**

## 🔴🔴 NEW FINDING — THE PER-CHIP FLOOR CAN ITSELF BE CONTAMINATED
The per-chip fix from [[emg-gate-passes-and-floor-bug]] is necessary but **not sufficient**. On
this file **3 of 8 chips have wire-free "floor" sites whose own median slope is EEG-steep**:
**A1 7 of 14, D1 5 of 14, B1 3 of 14, B2 2 of 14** (values −1.29 to −1.67). They are all
**>200 µV rms**, so they are NOT hidden electrodes — they look like drifting unterminated inputs.
🔑 **At `FLOOR_PERCENTILE = 1` a SINGLE contaminated site sets the whole threshold.** A1 then had
to beat −2.00 while D2 only had to beat −0.95, so **the same EEG slope passes on one chip and fails
on another**. A1 EEG median −1.39 scored 0.0%; D2 at −1.57 scored 99.7%.

✅ **SENSITIVITY RULE USED (mine, NOT the project criterion — do not quote it as the headline):**
drop any floor site whose own median slope < −1.0, then recompute.
⭐⭐ **IT PASSES THE DIRECTION TEST: the four chips with clean floors (A2, C1, C2, D2) do not move
one decimal, and the two genuinely open EEGs (B1, B2) stay at 0.0%. Only the contaminated chips
move** — A1 0.0→35.3%, D1 0.3→53.3%. Same logic as the pooled-vs-per-chip direction rule.
🟡 **This needs writing up and pre-registering before it is used in anything for the professor.**

## VERDICTS (per-chip floor, trimmed; 360 epochs of 10 s; bar = 15 min unbroken)
| pos | EEG rms/slope/lf-hf | EEG % | blk min | EMG rms | EMG % | blk | strict BOTH |
|---|---|---|---|---|---|---|---|
| **D2** | 79 / −1.57 / 16.6 | 99.7 | 36.7 | **33** | 89.2 | 23.8 | ✅ **PASS 89.2%, 23.8 min** |
| A2 | 118 / −1.71 / 24.3 | 100 | **60.0** | 531 | 0 | — | EEG only |
| C2 | 94 / −1.71 / 25.4 | 100 | **60.0** | 1001 | 0 | — | EEG only |
| C1 | 105 / −1.84 / 28.3 | 99.7 | 41.3 | 453 | 0 | — | EEG only |
| A1 | 98 / −1.39 / 17.5 | 35.3 | 3.0 | **15** | 92.8 | 21.3 | EEG intermittent |
| D1 | 99 / −1.46 / 17.8 | 53.3 | 9.0 | 928 | 0 | — | EEG intermittent |
| B2 | 4431 / −0.64 / 2.2 | 0.0 | — | **91** | 88.1 | 30.8 | EMG only, EEG OPEN |
| B1 | 3137 / **+0.00** / 2.8 | 0.0 | — | 2932 | 0.3 | — | nothing |

**⭐ ONLY D2 PASSES THE STRICT EEG-AND-EMG-IN-THE-SAME-EPOCH GATE.** Four animals give hour-long
usable EEG (A2, C2 unbroken the whole 60 min). Falsification passes on all 8 chips; band-limit
guard `raw` on all 8.

## ⭐ TIME COURSE SEPARATES "INTERMITTENT" FROM "DEAD" — ALWAYS DO THIS
EEG usable % per 10-min block:
```
A1   60  57  62   0   0  33     <- dropped out completely for ~20 min, partial recovery
D1   92  73  27   8  28  92     <- deep mid-run dip, FULL recovery by the last block
A2  100 100 100 100 100 100     C1  100  98 100 100 100 100
C2  100 100 100 100 100 100     D2  100 100  98 100 100 100
B1    0   0   0   0   0   0     B2    0   0   0   0   0   0   <- flat zero, genuinely open
```
🔑 **A1 and D1 are NOT weak electrodes — they are intermittent contact**, the movement-dependent
pattern of [[movement-dependent-contact-root-cause]]. D1 ends at 92%. 🛑 A 27-min midway reading
called A1 98.3%/14.7 min; the full hour gave 35.3%/3.0. **A half-recording overstates a flickering
channel — never report a midway number as the outcome.**

## HARDWARE
⚠️ **B slot 1 ground is STILL the weakest** — floor 60 Hz median **1491 µV vs 2807-5398 on every
other chip** (it was 192 µV in the crashed run earlier the same day, so it improved but did not
fully come right). Both B1 roles are open. **B slot 1 has now failed across three separate
cohorts** ⇒ treat as a standing port fault, not an animal.
⭐ EEG and EMG are close to mutually exclusive here: the 4 best EEGs (A2 C1 C2 D1) all have open
EMG (453-1001 µV), while B2 gives good EMG and no EEG. Only A1 and D2 have both.

## DELIVERABLES
- `~/eeg-processed/2026-08-24/allego_0__uid0824-17-56-51_channel_table.{csv,mat}` — one row per
  animal channel: position, role, Allego site, `ntv_chan_name`, **1-based MATLAB column**, rms,
  60 Hz, slope, lf/hf, usable %, longest block.
  🔴 **`feat.col(site)` is an index into the FEATURE SUBSET, not the 262-channel data matrix.**
  For a real column use `labels.index(site)` from `C.open_xdat`. I shipped this wrong once
  (A1 EMG as column 9 instead of 2) — verify against `is_selected`, which marks exactly the 16
  animal channels at data columns 0,1,32,33,64,65,96,97,128,129,160,161,192,193,224,225.
- Impedance earlier that day was **uninformative**: wire-free floor sites read "connected" 51-77%
  of the time at 0.5 MΩ (historical floor 2.5-3.4%), so the floor beat most animal channels.
  🔑 Impedance is refused during acquisition (`Z_measure attempted during data acq`).

Related: [[allego-mesa-gpu-crash-and-log-storm]] (same day, killed the first attempt) ·
[[animal-card-verdict-ladder]] · [[emg-gate-passes-and-floor-bug]]


## From the memory index, trimmed there 2026-10-06 (kept here verbatim)

- ⭐⭐⭐ **[S-SD BATCH, 8 MICE — 2026-08-24](recording-2026-08-24-new-8-mice.md).** First cohort with REAL ids (HLBSSD11-19); manifest `cohorts/S-SD.yaml`. 🔴 Surgical bleeding notes do NOT predict signal quality. 🔴🔴 The PER-CHIP floor can itself be CONTAMINATED.
