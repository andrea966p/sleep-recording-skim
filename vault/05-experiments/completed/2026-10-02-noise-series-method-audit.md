---
tags: [audit, qc, noise, methods, critique, eeg]
created: 2026-10-02
status: active
---

# Method audit of the XDAQ noise series and tonight's QC (overnight 2026-10-01/02)

> [!abstract] TL;DR
> A critical review, written overnight while the first 4-mouse run recorded, of the methods used in
> [[2026-09-30-xdaq-noise-series]] and of the QC that will grade the run. **Two flaws change conclusions
> if left alone**: the chip-floor ground gate (`FLOOR_MIN_HUM_UV`) no longer measures ground in the current
> rig geometry, and the all-chip event rule degenerates when 2 of 4 chips carry a railing input. Neither
> changes tonight's headline (no electrical injection reaches the clean mice), which rests on measurements
> that avoid both flaws. ⚠️ The code review then found that my own floor numbers were band rms while the gate reads the line PEAK (√2):
> on the gate's scale B1 is 742 µV, 7 % under 800, not 38 %. All numbers below are restated on the gate's scale. Nothing in `core/` or the console was changed; proposals are listed with their tests.

## What was evaluated

Tonight's checks on run `cfdf8ebde0c6` (`allego_0__uid1001-21-00-07`, 4 mice A1 A2 B1 B2, A1/B2 EMG open):
the impedance block, Signal Metrics, pre-flight and biology probe, 3-run repeatability, the live-file scans
(all-chip events, floor flicker, 60 Hz phase, narrow-line scan) and the QC rules that the 09:02
post-processing will apply.

## Strengths

- **One change at a time, with A/B/A** where it mattered (isolator), and **predictions written before data** (boards off).
- **Every QC verdict has an in-file negative control** (wire-free inputs on the same chip, cable and room), per chip, not pooled.
- **Fail-safe labels**: a chip the rig cannot judge is UNJUDGEABLE, not FAIL, so hardware faults are not blamed on mice.
- **Live-file reads were bounded** (nice 19, ionice idle, 300 s chunks, page cache dropped, < 1.2 GB RAM, growth
  checked before and after every pass). The recording shows zero dropped samples.
- Thresholds are documented with the data that set them and an explicit "do not tune to an animal" rule.

## Concerns

### 🔴 Critical: they change a conclusion

**C1. The ground gate measures antenna geometry, not ground, in the current configuration.**
`FLOOR_MIN_HUM_UV = 800` reads 60 Hz pickup on open inputs as a stand-in for "the chip has a ground". The 800 µV line
sat in an empty gap between grounded (1138-5609 µV) and floating (82-466 µV) chips, all measured before 2026-09-30.
Since then the geometry changed (free slip-ring wires taped, boards off and back on, 8-core tethers), and both
failure directions now show up:
- empty headstages with **no animal and no ground** read ~1750-4300 µV on the gate's scale (1200-3000 rms), so the gate would call them grounded;
- **B1, with a working mouse**, reads 632-745 µV on the gate's own scale all night (808 at 20:42), so the gate calls it ungrounded, by ~7 %. Its EEG is 1/f at normal scale
  and its EMG tracks behaviour.

This is a **construct-validity** failure (the proxy no longer tracks the construct) plus an **external-validity**
failure (calibrated on another configuration). Because the bias depends on wiring and cage position, it is also a
**selection bias** on which mice get scored. The pending 2000 µV proposal is falsified here: on the gate's scale B2 1820
and B1 742 carry EEG (A2 2057 is above it). Full write-up and proposals: noise-series page, "QC gate re-think".
*Effect tonight:* B1 will most likely be UNJUDGEABLE at rung 2, leaving A2 as the only scoreable mouse.
*Mechanism found at 01:30:* B1's floor is low because **specific input pairs collapsed** (/6, /14-/16 down 5-50x to 14-146 µV) after its
board was re-seated, not because the chip scaled down. The gate's median of 14 heterogeneous sites (14-6200 µV) lands in a gap and
swings ~2x. A site-specific geometry change on the board decides a verdict the gate attributes to the ground.

![[2026-10-02-noise-figD-gate-floor-vs-config.png]]

**Figure (C1).** Chip floors of every noise-series recording against the 800 uV gate: empty headstages read "grounded", B1 with a working mouse sits on the line (692-834 uV). Details in [[2026-09-30-xdaq-noise-series]] Entry 7.

> [!warning] C1 confirmed by the official QC, 2026-10-02 21:09
> **Same mouse, same hardware, nothing touched between the runs.** B1's gate floor was **702 µV overnight** and its rung 2
> verdict was **UNJUDGEABLE**. In the light-phase run its floor was **971 µV** and the verdict was **PASS** (93.7 % usable,
> longest block 47.3 min). Over the same 24 h, A1, A2 and B2 moved ±3 % (2590→2591, 2061→2117, 1767→1748; per-chip median
> of the QC bundles' `hum`). The floor crept up through the day (Fig H on [[2026-10-02-light-phase-run-rig-session]]).
> The gate's verdict on B1 tracked a slow drift of the pickup, not a change in its ground.

**C2. The "all-chip event" rule degenerates when chips are contaminated.**
`qc/allchip_scan_file.py` and the `noise_scan.py` "system-wide" block call an event when ≥ 75 % of chips' floors hit
in the same 100 ms, which is 3 of 4 tonight. A1 and B2 floors fire ~420 and ~580 events/h on their own (2344/3079 hit windows/h), because each chip
has a railing EMG input. So "3 of 4" collapses to "A2 **or** B1 plus two chips that are always firing".
- The two detections at 21:34 and 22:23 both have this shape (A1 + A2 + B2, B1 flat).
- Chance alone predicts about 0.4 such triples from A2's 77 hits.
- The right test for this rig is **A2 and B1 in the same 100 ms**, which gives 0 (and 0 against a chance level of 0.00).
  That is what the conclusion was based on.

*Fix (qc/ only, not core):* exclude chips whose floor hit rate exceeds ~10x the rig median, or chips whose position
has a railing input, from the vote, and print the chance expectation next to every count.

> [!warning] C2, second round (2026-10-02 23:00, second code review): the first fix was not enough
> The per-chunk exclusion with a 1 %-of-windows floor still let the railing chips vote in 48 of 145 overnight chunks, and up to
> 71 of 142 in the light phase. "3 of 4" was then met by A1 + A2 (one port) plus B2. Two more defects:
> - the 8-notch IIR chain rang 100-200 ms ahead of sharp transients, so rows came 1-2 windows early at a fraction of their size;
> - the chance level treated the two chips of one headstage as independent.
>
> **Rewritten** (`qc/allchip_scan_file.py`, and `qc/allchip_events.py` on the same functions):
> - the 50 ms comb replaces the IIR chain;
> - contamination is decided once per file (rate > 10x the cleanest chip; every port keeps its cleanest chip);
> - **an event must hit both ports**;
> - each event is reported at its peak;
> - chance comes from a per-chunk circular-shift null of the ports.
>
> Positive control NOISE02: all 4 light-switch flips at 4/4 chips. Result: **overnight 4 system-wide events, not 1** (three of
> them in 01:05-08:50; chance 0.01). **Light phase 13, not 32**: 3 outside the visit (chance 0.03) and 10 inside it (chance 2.58,
> both ports busy).
>
> A third review round re-tested the rewrite on synthetic files. It passed the case it was built for and found three more problems,
> all fixed:
> - a never-hitting chip broke the contamination reference;
> - events could land on the comb's echo;
> - a 300 s chance window let two ports busy for one minute look 2-2.5x "coupled". Chance is now local to 30 s (shifts of 2-30 s, 30 s strata).
>
> The A2-B1 coincidence was the right test all along: overnight 4 vs 0.06; light phase 10 vs 8.7, i.e. at chance while both
> floors were busy. Full numbers: [[2026-10-02-noise-series-4mice-24h-analysis]].

**C3 (found 09:20 on 2026-10-02). Stage 3's EMG measure includes mains, and that corrupts WAKE staging.** `emg_rms` = rms of the 10-300 Hz
band-pass (10-124 Hz at the stored 250 Hz) with no mains removal. With the EMG's 60/120 Hz notched (stage 3 otherwise unchanged): 10-01 A2 goes
REJECT 0.19 → SCOREABLE 0.323, and **all 13 W-SL light-phase animals of 09-10 and 09-17 become scoreable**, with r@1min 0.59-0.69 and wake
22.5-35.8 % (official: 8 of 13, r 0.10-0.70, wake 1.9-62 %). An epoch-shuffle negative control collapses r@1min to ~0. Pending: dark/full-day sets,
the whole stage-2 archive, the falsification suite. **This would re-score published sleep numbers**; it is a decision, not a patch.

![[2026-10-02-noise-figE-emg-mains-staging-effect.png]]

**Figure (C3).** Stage 3 unchanged except the EMG notched at 60/120 Hz, 15 animal-recordings: r@1min (left, bar 0.30) and WAKE % (right). Diagnostic only.

> [!info] C3 over the whole stage-2 archive, 2026-10-02 21:22-21:31
> `qc/emg_mains_staging_test.py` on every `~/eeg-processed` day folder: 100 animal-recordings. The unnotched run reproduces **99/99
> official verdicts** (method check). With the EMG notched, **SCOREABLE 44 → 69 (27 up, 2 down)**. Scoreable both ways: r@1min median
> +0.027. The 2 that drop fail a physiology check: 07-31 C2 (`nrem_largest_amplitude`), 08-19 C1 (`nrem_has_most_delta`,
> `nrem_largest_amplitude`). The light-phase run repeats the overnight: A2 0.290 REJECT → 0.440 SCOREABLE. **Not yet done:** the
> epoch-shuffle negative control at this scale, the falsification suite, and a look at the high notched WAKE % in some dark sets
> (72-88 %). Fig K on [[2026-09-30-xdaq-noise-series]] Entry 9.

> [!success] C3 validation at archive scale (2026-10-02 23:10, `qc/emg_notch_validation_2026_10_02.py`, Fig P)
> The test asks whether the notch is a validity gain or only a way to pass, using three checks the notch could fail:
> 1. **Shuffle control:** notch, then shuffle the EMG's 4 s epochs: **0 of 100 pass**, median r@1min −0.002 (max 0.029).
> 2. **Dose-response:** mains is a median **68 %** of the variance of the stager's EMG measure (10th-90th percentile 12-98 %).
>    - The change follows that share: Spearman 0.53 for |Δr|, 0.66 for |ΔWAKE|.
>    - Below a share of 0.2 (15 recordings) nothing flips: |Δr| median 0.014, |ΔWAKE| ≤ 1.6 points.
>    - At 0.8 or more (34 recordings), 22 go REJECT → SCOREABLE.
> 3. **Physiology:** dark WAKE % > light WAKE % in 41 of 49 recordings that cover both phases as published, **47 of 49 notched**.
>    - The median contrast goes from +25 to **+37 points**.
>    - It is unchanged in the 29 recordings scoreable both ways (+36 → +37).
>
> **The notch repairs the recordings that mains broke and leaves the good ones alone.** Recordings and animals repeat across
> folders, so the n count recordings and the p values are optimistic. Still a decision: the falsification suite and the re-scoring of
> published numbers come first.

### 🟠 Important: they affect interpretation

**I1. The repeatability baseline is short, but the night confirms it.** n = 3 untouched runs within one hour, all
in the light phase. The overnight floor confirms the A2 meter: CV 0.4 %, max/min 1.04 over 3.5 h. **B1 is not a
meter**: CV 6.8 %, a 17 % drift in the first 2 h, and it moves against the other chips (r -0.21 to -0.34).

**I2. The pre-flight is blind to grounding by construction.** `get_signals()` returns only selected channels, so it
reports NO FLOOR. Allego records every channel, so a 60 s test recording into `~/radix/noise-tests/`, plus
`qc/noise_scan.py`, gives the per-chip floors before a run (done by hand on 2026-10-01). **Done overnight**: `qc/xdat_to_preflight_npz.py BASE OUT.npz [t0] [dur]` writes any short recorded file in the
pre-flight's capture format with every amplifier channel, so `qc.preflight_screen --npz` grades grounding before a run
without touching the selection. Checked on `mice4_baseline2`: A2 CLEAN; B1 UNJUDGEABLE (floor 591 < 800, as predicted);
A1/B2 OPEN. C1 still applies to what that floor means.
**Bug found and fixed on the way** (`qc/preflight_screen.py`, standalone, not used by the post-processing): the OPEN
reason printed the EEG's 60 Hz whatever channel tripped, so an open EMG beside a good EEG read "60 Hz 16 uV vs 150 uV
limit: not connected". It now names the open channel ("EMG 60 Hz 3452 uV ..."). Verdicts are unchanged. Test
`tests/test_preflight_reason.py` passes 5/5, and 3 of its 5 fail on the old code (red-green). The stale "2000 uV
proposed" warning now points to this audit.

**I3. Impedance is a screen, and only half of each pair.** Only the positive input is measured. The EEG duty
cycles sit at 10-60 %, around the 0.5 MΩ line, while all four EEGs are physiologic. The sweep did agree with the
stream on the two open EMGs (≈ unwired input).

**I4. Restarting the stream for impedance seems to leave Allego unhealthy for a long run.** From the 20:17 restart on,
`allegoserver.log` filled with `[HAL] unable to send to listener '0','1','2'` (about 5 per minute) and with Anti-Alias
`resample_antialias` warnings. The GUI renderer grew to 108 % CPU and 11-14 GB, and the GUI froze about 23:30. No data
was lost (every timestamp step is 1), but app death would end the run.
*Procedure fix:* after an impedance block, close and reopen Allego before a long run (then reset 1 kHz + XDAQ ONE REC
and check the stream rate), and use the `Spikes` view mode for long runs. Timing pins the trigger: `allegoserver.log` shows `stream thread finished ok and killed` at 20:17:41 (the API `set_streaming('off')` for the impedance block) and the first `[HAL:cad5] ... unable to send to listener '0','1','2'` one second later. After that it repeats on the HAL's 5 s cadence. So stopping and restarting the stream from the API orphans three HAL status subscribers. Whether those were the GUI's subscriptions, and so linked to the freeze, is not established.

### 🟡 Minor

- **M1.** The overnight event scripts use a 150-sample comb (nulls every 6.67 Hz, theta included), while the vault
  calls the method a "3-cycle comb, 50 ms". Self-normalised detection is unaffected in kind, but counts are not
  comparable across scripts. To be made consistent (see the code review).
- **M2.** The first narrow-line scan assumed mains at exactly 60.000 Hz and misread folded high harmonics as non-mains.
  Fixed: the tolerance grows with harmonic order.
- **M3.** Mouse IDs are placeholders (`POS-<slot>`); the NAS copy must be re-filed when they are known.

## Code review of tonight's qc scripts (two read-only reviewer agents, then verified and fixed)

**Impedance tools** (`sweep_block_ports.py`, `block_duty_cycle_slots.py`; full report in the session). Fixed and tested
(`tests/test_impedance_block_tools.py`, 15 pass):
- 🔴 the scorer took n from a folder glob. Shown: a stray single sweep made it 21 sweeps and moved B1 EEG's p from 0.041 to 0.054.
  Now n comes from `_census_log.tsv` and only CSVs that match a log row are scored.
- 🟠 the floor was pooled across chips, against the project's per-chip rule. Per chip, B1 EEG is p 0.18 (no star).
- 🟠 NaN magnitudes counted as "open"; now dropped per site.
- 🟠 dormant: sites were labelled by table row position. On a shuffled table the old logic mislabels **125 of 128** sites, and
  on a non-passthrough map it calls native 0 "A/1" when it is A/64. Now labelled from `ntv_key_idx` → `port/site_num`. Untested
  against the live table (needs Allego): check with one sweep after the run.
- 🟡 slot labels are validated ("A3" and "B12" used to alias other slots), a folder that already holds a block is refused without `--append`,
  "BLOCK DONE" counts the sweeps actually written, and a missing native index gives NaN rather than a crash after the CSV.
- Quick-look `mice_first_look.py`: whole-file Welch let a 10 % artefact burst flatten a slope from -2.0 to -0.03. Now 4 s epochs, with
  railed and outlier epochs dropped and the kept fraction printed. The 19:50 numbers barely move (slopes -1.73 to -2.06).
- **Not fixed tonight, needs a decision or code that is off-limits during the run:** `pipeline/stage2_split.py` `sweep_identity()` regex
  expects `_HHMM_`, but the census files are named `_HHMMSS_`. **201 of 202** census files fall back to mtime and "unlabelled",
  which also pools the single test sweep with the block. Proposed: time group `(\d{4})(?:\d{2})?`.
  `allego_signal_metrics.py` does not de-duplicate packets (documented in its docstring; needs a live test).

**Noise and event scripts** (second reviewer; verified, fixed, re-run on tonight's file):
- 🔴 **Scale.** The scripts reported the floor as a 55-65 Hz band-pass std (rms), while the gate applies 800 µV to the 59-61 Hz line
  **peak** (10 s Hann). That made them √2 low, and on quiet channels mostly broadband signal. Every comparison against 800 or 2000 was
  restated. **B1 is 742 µV on the gate's scale (632-808 over the night, 740/839/808 in the three evening runs), still below 800, but by
  ~7 %.** The pre-flight's `chip_floor` had the same bug and now uses the gate estimator (test, red-green). New `qc/gate_floor.py`.
  `floor_flicker`, `night_trend` and `noise_scan` now report the gate scale; `noise_scan` keeps the legacy rms in its JSON as `mains`.
- 🔴 **`night_spikes` double-counted.** The 150 ms comb echoes every transient into another window, and 150 ms-lagged EEG/EMG pairs counted as
  "same 100 ms". Rewritten: the documented 50 ms comb, hits merged into events, coincidence = event overlap. Re-run (4.04 h): floor events
  A2 10.1/h, B1 1.0/h, never together (chance ≈ 0); EEG+EMG events A2 3 in 4 h, none on a floor. **Conclusions unchanged, counts about halved.**
- 🟠 **`floor_phase` used linear statistics on wrapped angles.** With circular statistics every chip has R 0.11-0.24, so no chip has a defined floor
  phase. The earlier "B1 not at 180 deg" is **retracted**: the test is uninformative.
- 🟠 **C2 fixed in `allchip_scan_file.py`**: chips that fire on their own (> 10x the lower-quartile chip rate, > 1 % of windows) are left out of the vote,
  per 300 s chunk, and the chance level is printed. A first version compared against the median chip and excluded nothing, because with half
  the chips railing the median is contaminated. Tonight: A1/B2 left out in 40-45 of ~50 chunks, **0 system-wide events, chance 0.01**
  (before: 2 events against a chance level of 1.15, i.e. chance). The positive control (NOISE02 light switch) still finds 4/4.
  ⚠️ Superseded by the second and third rounds below: this per-chunk version still let railing chips vote.
- 🟠 `noise_scan.py`: notches at every 60k (the 1-100 Hz band edge passed 120 Hz at ~17 %, which skewed robust SD per chip); chip-MEDIAN floor hit
  rule (was any one of 14 inputs); folded mains masked out of bb/hf; system-wide vote with the same exclusion and chance level. On NOISE02 it
  now also flags 4 small common events (8.9-23.7 s, 140-685 µV, chance 0.07) besides the 4 switch events.
- 🟡 fs assertions added where the code assumes 1 kHz (30 kHz fresh-launch files would silently get 3 ms windows); `allchip_events` uses
  ceil like the others; the event plot now uses the 50 ms comb and labels its echo; `splitter_coincidence` computes chance over the windows
  it keeps (it used to zero all-chip windows but keep them in N). **The splitter numbers were re-run 2026-10-02 21:31 (noise-series Entry 9): same conclusion, partners at chance (0.4-1.9x vs 0.3-2.6x for unrelated pairs)**. Originally: the splitter numbers had not been re-run: that needs 2 h of the 262-channel
  uid0921 file, which is too heavy during a live recording. Do it after 09:02.

## Second code-review round (2026-10-02 22:50-23:40: two reviewer agents on today's analysis and scan code, then fixed and re-run)

**Reviewer 1, the figure and analysis scripts:**
- The air-shower step detector was blind below about 1-2 mV on a floor carrying mains. Now it uses the comb: a step on two
  chips must clear the second-lowest chip threshold, 116-149 µV here (the clean floors alone see 66-150 µV). Steps are counted
  once (the comb's echo used to double them).
- Two scripts read to the end of the file: about 21 GB of RAM on the finished file. Both are now bounded.
- `rig_session` would have overwritten hand-curated markers. It no longer writes any; one canonical marker module replaces it.
- The "non-mains" bands dropped ±1 bin, inside the Hann main lobe, so mains leaked. They now drop ±2. The meter-OFF muscle band
  ×0.42 was this leakage; the corrected value is ×0.83.
- Captions carried typed numbers (fig K's "99/99", fig B's "0.25 s later", fig H's "15 → 30 µV"). They are now computed or corrected.
- The time origin came from the file name (off by 0.15-0.17 s). It now comes from `status.start_time`.

**Reviewer 2, the scan tools:**
- C2 second round, above.
- The chance levels used whole-file rates, which are too low when rates co-vary. They are now local to 30 s in `night_spikes`
  and the splitter test (30 s strata) and in `allchip_scan_file` (ports shifted 2-30 s). The splitter conclusion is unchanged.
- `emg_mains_staging_test` reused stale symlinks. It now refuses them and prints its own method check against the official verdicts.

**Found while running the analysis:** `pipeline/stage1_qc.py` wrote its feature cache into `~/radix/data` whenever it was given a
full path (`os.path.join` restarts at an absolute component). Two such files, from today's diagnostic runs, were moved out before
the 01:30 S3 job could archive them for good. A regression test is in `tests/test_stage1_cache_path.py`.

Every changed published number is listed in section 8 of [[2026-10-02-noise-series-4mice-24h-analysis]].

## Recommendations (none applied to `core/`, `cards/` or the console's live code)

1. Leave tonight's QC as it is; grade B1 again later under a pre-registered rule. A shadow verdict for B1, gate bypassed
   and labelled diagnostic-only, goes next to the official one.
2. Withdraw the 2000 µV proposal. Treat 800 µV as configuration-specific until it is re-derived.
3. Fix C2 in `qc/allchip_scan_file.py` and `qc/noise_scan.py`: exclude contaminated chips and report the chance expectation.
4. Restart Allego after impedance blocks; use the `Spikes` view mode for long runs.
5. Console (prepared overnight in a separate worktree, **not deployed**, see below): an API to move a live run's
   stop, and the hourly watchdog arming itself from the console.

> [!note] Where to compute the re-derivations (2026-10-02)
> Testing C1 (floor guards) and C3 (EMG notch) properly means re-running stages 1-3 and the QC over the whole archive, not one night.
> That is the job for AWS: ~1 TB of raw is already in `s3://skim-eeg-radix-archive-760396521414/radix/data` (GLACIER_IR, instant
> retrieval) and the work is embarrassingly parallel per file. Needs an IaC stack (instance role read-only on the bucket), a budget alert
> first (none exist since 2026-09-20) and a non-SSO credential path for unattended runs. Single-night scans stay on the workstation.

## Prepared but not deployed: console fixes in a worktree

Worktree `/home/skimlab/srs-overnight-worktree`, branch `overnight/2026-10-02-console-fixes` (uncommitted, off `5a52ad7`).
Review with `git -C /home/skimlab/srs-overnight-worktree diff`.
- `Scheduler.reschedule_stop()` + `POST /api/runs/<id>/stop_at`: moves the stop of a RECORDING run, leaves an audit event,
  refuses a non-recording run, a stop less than 30 s ahead, an unreadable instant, and a current stop already due.
  Tests: 39/39 pass under `/usr/bin/python3`, which has no `radiens`, so the rig cannot be reached. A mutant that drops the new
  stop fails the new test (red-green done). The route itself is not exercised: importing `app.py` opens the real run database.
- `recording-watchdog-cron.sh`: arms itself from `GET /api/runs?state=RECORDING` when nobody armed it by hand, and every path
  can be overridden from the environment for testing. Exercised against a scratch dir with a fake console, a fake Allego status
  and a fake notifier: arms, OK, stall alert, no console run → disarmed, console down → disarmed. Production defaults unchanged.

### Console changes: reviewed by a third agent, then revised (still not deployed)

The review found the watchdog change **not deployable as first written**. 🔴 A stale `current-recording.txt` was never replaced: after an
auto-armed run stopped and a new run started before the next :05 check, the old file's frozen size raised a **max-priority STALL every
hour** and the new run went unwatched (verified in a sandbox). This also affects the CURRENT production watchdog with a hand arm, if a new
recording starts between a stop and the next check. **It is not a risk tonight**: nothing starts between 09:02 and 09:05. Also found: an hourly
alert loop when the console says RECORDING but Allego does not; a wrong-path → silent "OK"; an alert after every normal console stop;
console errors logged as an idle rig; half-overridden sandbox variables reaching the live console. In `reschedule_stop`: a snapshot → write
race that could turn a run stopped in between back into RECORDING (STOPPING → RECORDING is legal for the boot rewind; the same pattern
existed in `_confirm_later`), no upper bound (a typo like `2027-...` would record until the disk fills), and inconsistent HTTP codes.

**Revised in the worktree** (tests: backend 41/41, red-green on the compare-and-set; watchdog: 12 sandbox scenarios):
- `RunStore.transition(..., expect_state=, expect=)` compare-and-set inside the transaction, used by `reschedule_stop` and `_confirm_later`.
- `reschedule_stop`: at most 72 h after the start, refused beyond the disk's remaining hours (storage status), tolerant of an unreadable stored
  stop, stores local time. Route: 404 for an unknown run, JSON 500 on errors, listed in the endpoint table.
- Watchdog: asks Allego for mode AND live file each hour and **re-arms when they differ**; arms from Allego or the console; `ok` note when the
  console ended the run, `warn` for an unexplained stop, ONE `fail` when the console and Allego disagree (remembered in
  `watchdog-disarmed.txt`); uses the console's own `data_path`; warns on a missing armed file, but only logs (and drops the arm) for a
  hand-started recording in another folder; logs console failures distinctly; refuses half-sandboxed runs.
- **Deploy advice:** only after the current run reaches DONE, and restart the console only when no run is active. The watchdog can be
  swapped in any time no recording is live; it is run by cron, so there is no service restart.

## Overall

The noise-series conclusions so far rest on measurements that survive these critiques: no building-wide injection
reaches the clean mice, hum is steady and small, and nearly all coordinated spikes are within-mouse. The **QC** is
where the weakness lies. Its ground gate is a proxy calibrated on hardware that no longer exists, and it will exclude a
mouse that is plainly physiological. That should be fixed by re-deriving the gate or adding an independent route,
decided in advance, not by moving the number until B1 passes.

Related: [[2026-09-30-xdaq-noise-series]] · [[weak-chip-ground-vs-open-electrode]] · [[impedance-sweep-register]] ·
[[animal-card-and-verdict-ladder]]
