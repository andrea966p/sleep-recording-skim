---
tags: [experiment, noise, light-phase, run-log, markers, foil, presence, multimeter, figures]
created: 2026-10-02
status: active
---

# Light-phase run 8f84e3e62af6 (2026-10-02): what was done to it, when, and what it showed

> [!abstract] TL;DR
> - **The run:** `allego_0__uid1002-09-16-58`, 09:16:58 → 21:02 (scheduled). Same 4 mice as the overnight (A1, A2, B1, B2; A1/B2 EMG open).
>   Raw in `~/radix/data/`; the console strips, exports and uploads after 21:02.
> - **Rig session with Andrea, 15:19-16:35 (start from the data; the message said 15:35), all inside this recording:** nothing on the rig was changed permanently. A multimeter
>   probe, hands, waving, and a wireless receiver were tested near the headstages. **Every intervention is in the canonical markers**
>   (`MARKERS_lightphase_allego_0__uid1002-09-16-58.tsv`, in the file's exact time base; table below), so the sleep scoring and any later analysis can exclude or use them.
> - **Findings:**
>   1. a lead touching A2's foil feeds mains into **A2's floor (x1.22 with the meter ON, x2.09 with it OFF)** and, with the meter
>      OFF, **into its mouse's EMG (x1.15, phase-locked, while the muscle band did not rise: pickup, not movement)**;
>   2. hands near a headstage dip the floors 28-42 % for seconds but **never touch the mice's EEG/EMG**;
>   3. the wireless receiver showed nothing;
>   4. untouched all day, **B1's floor rises 790 → 1152 µV** (first vs last hour; it crosses the 800 µV gate) and **A2's EMG 60 Hz
>      wanders 14-30 µV** (highest 13:00-17:00, back to ~20 µV by 21:00).
> - **The completed 24 h analysis** (official verdicts, sleep-wake, the notch validation, NAS package): [[2026-10-02-noise-series-4mice-24h-analysis]].
>   Numbers on this page were re-run after the code review of 2026-10-02 23:00; first-run values are kept where they changed.
> - **Next:** a solid bond of the foil to the chassis (plan T2a-c). Details and protocol: [[2026-10-02-noise-troubleshooting-plan]];
>   narrative: [[2026-09-30-xdaq-noise-series]] Entry 8.

## Event markers

> [!important] Canonical markers (2026-10-02 23:30) supersede `trials/MARKERS.tsv`
> `eeg-emg-analysis/qc/noise_mice_markers_2026_10_02.py` holds the single list for both runs. It writes `MARKERS_<run>_<base>.tsv`
> with `file_s` (= the per-mouse CSV's `timestamp_sec`), `sample` (= the CSV row) and `timestamp_raw`, all on the file's own
> origin (`status.start_time`, 09:16:58.153 here), plus `clock_basis` (data, console, allego, or Andrea's clock, which ran >= 8 s
> ahead) and the disturbed windows to exclude. Copies are on the NAS (`ANALYSIS_2026-10-01_to_10-02_4mice_24h/markers/`).
> The visit starts at 15:19:33 by the data. The older table below and `trials/MARKERS.tsv` used the file-name clock (0.15 s early)
> and the chat's 15:35. `qc/rig_session_2026_10_02.py` no longer writes a marker file.

Canonical files in the vault: [[2026-10-02-noise-MARKERS-lightphase-uid1002-09-16-58.tsv]] (this run) and
[[2026-10-02-noise-MARKERS-overnight-uid1001-21-00-07.tsv]] (the overnight before it).

Older table (kept for the record; its file was [[2026-10-02-light-phase-run-MARKERS.tsv]]). Source "Andrea" = from Andrea's messages;
"data" = located in the recording.

| start | end | s from file start | what | source |
|---|---|---|---|---|
| 09:16:58 | | 0 | run starts (console) | console |
| ~15:35 | | ~22682 | Andrea at the rig | Andrea |
| 15:50:50 | 15:51:25 | 23632-23667 | multimeter `V~` 200: black on XDAQ chassis GND lug, red on A2's foil, reads 0.0; hands at the headstages | data |
| 16:00:00 | 16:03:00 | 24182-24362 | absent (control) | Andrea |
| 16:03:00 | 16:04:00 | 24362-24422 | standing 50 cm in front, hand brought close to each headstage (no touch) | Andrea |
| 16:04:00 | 16:05:00 | 24422-24482 | absent (control) | Andrea |
| 16:05:00 | 16:06:00 | 24482-24542 | in front, waving hands | Andrea |
| 16:06:00 | 16:07:00 | 24542-24602 | waving the powered custom wireless EEG/EMG receiver (4 antennas, Dell PC) near the headstages | Andrea |
| 16:22:04 | 16:23:13 | 25506-25575 | meter ON, black fixed on chassis lug, red tip hover/touch on A2's foil | Andrea + data |
| 16:22:15 / :34 / :49, 16:23:05 | +6 to 8 s each | 25517, 25536, 25551, 25567 | the four touches (meter ON) | data |
| 16:27:01 | 16:27:11 | 25803-25813 | meter OFF: floating lead touching A2's foil | data |
| 17:22:14 | | 29116 | facility air shower (next to the recording room) switched ON | Andrea |
| ~17:23-17:24 | | ~29176-29236 | air shower ON again, "1 or 2 minutes later" (exact second not logged) | Andrea |
| 17:35:50 (Andrea's clock) | | 29932 | air shower ON (message reached e10 at <= 17:35:42 e10 time, so Andrea's clock runs >= 8 s ahead) | Andrea |
| Allego 29937.4 s | | 29834 or 29937 | another air shower ON, time read off Allego: 17:34:12.5 if Allego shows stream time (file starts at stream 103.04 s), 17:35:55.5 if file time | Andrea |

For the sleep scoring: these are **behavioural** disturbances for the mice (a person in the room), not electrical ones on their
EEG/EMG, except the 16:27:01-11 EMG step on A2 (x1.16 on the 60 Hz line). The end of Andrea's visit is not logged yet (after 16:35).

## Figures

![[2026-10-02-noise-figH-light-phase-run-overview.png]]

**Figure H.** The whole run (re-drawn on the finished file). Left: one 10 s epoch every 3 min. **B1's floor rises from 790 µV (first
hour) to 1152 µV (last hour) and crosses the 800 µV gate** (dashed), while A1, A2, B2 stay within ±3 %. **A2's EMG 60 Hz wanders
14-30 µV, highest 13:00-17:00 and back to ~20 µV by 21:00** (the first version, drawn at 16:35, read this as a "15 → 30 µV drift").
Cause unknown: posture, tether position or contact; the mice were not handled. Right: 15:15-16:40 every 30 s, each test shaded.

![[2026-10-02-noise-figF-presence-test.png]]

**Figure F.** Presence test, 1 s resolution: hands near a headstage dip that chip's floor (deepest single second A1 x0.58, A2 x0.69,
B1 x0.51; first run x0.58/0.72/0.61, the 1 s grid moved by 0.15 s) and the open EMGs rise when waving (A1 x1.28); the mice's own 60 Hz
does not move; the receiver shows nothing electrical (B1's EEG delta/theta change between those minutes is its brain state).

![[2026-10-02-noise-figG-probe-tests.png]]

**Figure G.** Probe tests on A2's foil (medians, touching vs not, re-run after the code review). Left, meter ON: during the four
contacts A2's floor goes 2146 → 2624 µV (x1.22), other floors x0.93-0.99, A2's EMG 60 Hz x1.03. Right, meter OFF: A2's floor doubles
(2262 → 4730 µV, x2.09) and the A2 EMG 60 Hz line rises 29.7 → 34.1 µV (x1.15) while its muscle band does not rise (5.4 → 4.5 µV,
x0.83; the first version's "11.3 → 4.8" came from a ±1-bin band that leaked mains). The added 60 Hz keeps one phase every second
(R = 0.97) at a fixed angle to the floor's added pickup (-104°), so it is mains coupled from the foil, not the mouse moving.

![[2026-10-02-noise-figI-air-shower.png]]

**Figure I.** Facility air shower, 17:12-17:27:30 (re-run after the code review). Orange = 17:22:14 on Andrea's clock; dashed =
the latest true switch-on, 17:22:06 (that clock ran >= 8 s ahead). **No electrical trace:** floors x1.00-1.02 in the minute after vs
before, and the step detector, now the |d/dt| of the 50 ms comb (the first version's raw |dx| only saw ~1-2 mV steps on a floor
carrying 2 mV of mains), finds **no step on two chips at once**. A two-chip step would have had to clear 116 µV (the second-lowest
chip threshold: A2 79, B1 116, B2 362, A1 573 µV). Its 3 single-chip steps are all B1, during a 2.5-4 mV burst of B1's own EMG: that
mouse moving. **The mice:** A2 was asleep and bursts its EMG x11 at **+9.6 s or later** after the true switch-on;
a burst from quiet within 11 s happens by chance ~11 % of the time (16:40-17:21, disturbed windows excluded). Arousal possible, not
shown. B1 was already awake (from 17:18:40). After 17:23 the A1 (17:24:08) and B2 (17:25:01) events sit on one chip each = that mouse
moving its headstage.

![[2026-10-02-noise-figJ-air-shower-2.png]]

**Figure J.** Two more air-shower starts, 17:28-17:38: one Andrea timed at 17:35:50 (Andrea's clock) and one they read off Allego as
29937.4 s, which is 17:34:12.5 if Allego shows stream time or 17:35:55.5 if it shows file time. **No electrical trace at any of
them:** no floor or open EMG changes its 60 Hz line or shows a switching step. The mice cannot settle the arousal question here:
A2 woke at 17:34:30.2 (first 100 ms burst after 2 s quiet), 18 s after the stream-time candidate, and was already awake at 17:35:50;
B1 was awake throughout.

## What was measured (numbers)

| test | A2 floor | other floors | mice's EEG/EMG | open EMGs |
|---|---|---|---|---|
| baseline 15:30-15:35 (`trials/A0_live_1535.json`) | 2087 | A1 2889, B1 1014, B2 1904 | A2 EMG60 19.0, EEG60 3.1 | 4.7-4.8 mV |
| meter probe 15:51 (hands at the headstages) | +20 % one epoch, then +6 % lasting vs A1/B2 | -5 to -10 % | A2 EMG60 21 → 15-16 (mouse?) | |
| hand near each headstage 16:03 | x0.69 (seconds; first run x0.72) | A1 x0.58, B1 x0.51 (x0.61), B2 x0.97 | no change | x1.02-1.05 |
| waving hands 16:05 | x0.89 | A1 x0.69, B1 x0.79 | no change | A1 x1.28 |
| wireless receiver 16:06 | none | none | none | one doubtful 88.75 Hz bin on A/2 |
| meter ON touches 16:22 | **x1.22** (median of the 4 contacts; peaks x1.25-1.4) | x0.93-0.99 | A2 EMG60 x1.03 (not distinguishable) | none |
| meter OFF touch 16:27 | **x2.09** | none | **A2 EMG60 x1.15, muscle band x0.83 (did not rise; first run x0.42 was mains leakage)** | none |
| air shower ON 17:22:14 (+ again ~1-2 min later) | none (x1.00, no two-chip step at >= 116 µV) | none (B1: single-chip movement) | A2 EMG burst x11 at +9.6 s or later from the true switch-on, chance ~11 %: arousal possible, not shown | none |
| air shower ON 17:35:50 + Allego 29937.4 s (17:34:12.5 or 17:35:55.5) | none | none | A2 already awake / woke 18 s after a candidate; B1 awake | none |
| AC volts foil ↔ chassis (Harden 661002, `V~` 200) | 0.0 (meter too coarse, loads the foil) | | | |

## What it means, and what is still open

- The foil's potential reaches A2's own floor pads AND its mouse's EMG; a floating conductor on it adds pickup, a weak path to earth
  removes some. **A solid low-ohm bond should lower both below today's floating foil: test next session (plan T2a: A2 first, A/B/A).**
- Connected EEG/EMG are immune to hands and people (differential, low-impedance legs); floors and open EMGs are not, so during floor
  measurements: hands off, stand still or away.
- ✅ **Answered 21:11: yes.** The official light-phase QC passes B1 at rung 2 (floor 971, 93.7 % usable); overnight it was UNJUDGEABLE
  (702). Nothing was changed on B1. Audit C1 confirmed. Lights-OFF found at 21:01:11.5 (below the all-chip bar). Noise-series Entry 9.
- The visit began **~15:19 by the data** (all-chip events 15:19:33-40), not 15:35. Strong unexplained events later: 17:10:08 (all 4 chips), 18:12:10.
- A2's EMG 60 Hz wanders 14-30 µV over 24 h (dark 17, light 21 µV hourly median; Fig M of [[2026-10-02-noise-series-4mice-24h-analysis]]); it matters for staging (C3).
- **Air shower:** a building load switching next door leaves no electrical mark, but it may wake the mice. For staging, treat
  17:22-17:26 and 17:34-17:37 as disturbed windows. To test arousal properly, time each start on ONE clock tied to the file:
  read Allego's time and the phone clock together once (a photo of both), so the Allego convention and the phone offset are both known.
- ✅ Done 2026-10-03: the canonical markers of both runs are on the NAS with the analysis (`ANALYSIS_2026-10-01_to_10-02_4mice_24h/markers/`).

Scripts: `qc/noise_mice_markers_2026_10_02.py` (markers), `qc/rig_session_2026_10_02.py` (Fig G, H), `qc/air_shower_2026_10_02.py` (Fig I, J), `qc/presence_test_2026_10_02.py` (Fig F), `qc/noise_scan.py`, `qc/gate_floor.py`.
Related: [[2026-09-30-xdaq-noise-series]] · [[2026-10-02-noise-troubleshooting-plan]] · [[2026-10-02-noise-series-method-audit]] · [[2026-10-02]]
