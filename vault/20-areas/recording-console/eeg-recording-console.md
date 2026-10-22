---
tags: [procedure, eeg, allego, recording, console, automation, multi-user]
created: 2026-09-11
status: active
---

# The EEG recording console — set up a run, leave the room, find your data on the NAS

> [!abstract] TL;DR — for non-technical readers
> **What this is.** A page you open in a browser on the recording computer. You pick your name, say
> which mouse is in which position on the rig, and press start — or set a time for it to start by
> itself. When the recording ends, the computer shrinks the file down to just your channels and
> copies it into your folder on the lab's network storage — under a name you chose, not the
> acquisition software's — checking that the copy is perfect before it says so.
>
> **Why it exists.** Five people share one rig. Before this, starting a recording meant clicking in
> the acquisition software, and nothing anywhere recorded who was recording, which animal was in
> which slot, or what kind of experiment it was. That information lived in people's heads and
> notebooks, and the resulting file was a single 262-channel block that nobody could split up later
> without asking whoever ran it.
>
> **How to read this page.** Section 1 is everything you need to run a recording. Section 2 is the
> three things about this rig that are surprising and worth knowing before you trust what you see.
> Section 5 is what to do when something looks wrong. Background: [[nvr-system-overview]].

> [!tip] The page will not load, or something looks down?
> [[starting-the-rig-after-a-restart]] — one command tells you what is up and what is not.
> Short version: the console, the NAS mount and the network start themselves and survive a desktop crash;
> the Allego GUI is the only thing a human launches.

**Open it at <http://127.0.0.1:8600>** on the recording computer. It is bound to localhost only —
this drives amplifiers with animals attached, so it is deliberately not reachable from the lab
network.

## 1. Running a recording

1. **Pick your name.** There is no default, on purpose — see section 2.3.
2. **Check the rig layout.** It fills in from your name. The four port boxes show what is plugged
   in — a splitter means two animals on that port, none means one — and whether that agrees with
   what Allego actually found. **A disagreement disables Start until you fix it.**
   Full detail, and how to add your own settings: [[rig-layout-and-recording-settings]].

3. **Type a recording batch name** — e.g. `HLBSSL`. This is what the folder on the NAS will be
   called, so it is the field that decides whether anyone can find this run in six months. Letters,
   digits, `-` and `_`, up to 32 characters. Leave it blank and the folder keeps Allego's own name,
   as before. **The console shows the exact folder and file names under the slot grid as you type.**
4. **Fill in the occupied slots** — mouse ID and recording type (`basal`, `recovery`, `sd`). Leave
   empty slots empty; **any number of mice from one up is normal**, in any positions, and section
   2.4 says exactly what that changes. Mouse IDs become part of a folder name, so letters, digits,
   `-` and `_` only.

   > [!warning] Each animal needs its own ID, and case does not make one different
   > `HLBSSL31` and `hlbssl31` are the same mouse. Two slots sharing an ID makes the whole run
   > **unjudgeable** — the cohort record, every QC card and the per-animal export are all keyed on
   > it — so Start and Schedule stay disabled until you fix it, and the clashing slots are outlined.
   > Before 2026-09-14 this was accepted and the run failed QC minutes after it finished.
5. **Check the two lines under the grid.** They say exactly which channels will be kept and what
   the folder and files will be called, *before* anything happens. This is the one decision that
   cannot be undone after the run.
6. **Start now**, or set **Start at** and **Stop at** and press **Schedule**. Times are local, and
   the header shows the current **ZT** so you do not have to do the arithmetic. Default is the next
   09:00 (ZT0) running 24 h, which is the shape most runs here have.

While recording, the page shows elapsed time, the file name, bytes on disk and when it will stop.
Pressing **Stop recording** ends it and immediately queues the post-processing.

### Where your mice land on the NAS

Since 2026-09-29 each mouse gets **its own folder with one CSV**, filed by batch and by the
condition you picked for that mouse:

    02_Data_Sleep/andrea/HLBSSL/
        Baseline/20260912_HLBSSL31_B/20260912_HLBSSL31_B.csv  + .info.json
        Recovery/20260921_HLBSSL31_R/20260921_HLBSSL31_R.csv  + .info.json

| part | meaning |
|---|---|
| `andrea` | who is recording |
| `HLBSSL` | your batch name. **Required.** For a test, type `SCREEN` or `TEST` |
| `Baseline` / `Recovery` | the type chosen **per mouse** in its slot |
| `20260921` | the date the recording **starts**, not the day you filled in the form |
| `HLBSSL31` | the mouse ID typed in the slot |
| `B` / `R` | baseline / recovery |

The CSV format is on its own page: [[per-mouse-csv-format]].

> [!tip] Mixed conditions in one run are fine
> Each mouse is filed under its own type, so a run with some baseline and some recovery animals
> just sends each one to its own folder.

> [!warning] The date follows the START, so the two buttons can disagree
> **Start at** is pre-filled with the next 09:00. After 09:00 that is *tomorrow*, while **Start now**
> would be dated *today*. When they differ, the console says so under the per-mouse paths.

A second folder for the same mouse on the same day (a restarted recording) gets `-2`. Its
`info.json` says why and which Allego file each folder holds. Local files keep their Allego names.

### What happens after it stops, without anyone present

    QC bundle  →  strip to your channels  →  upload to your folder  →  verify

Your data appears at `{SKIMNAS_ROOT}/<your name>/<YYYYMMDD>_<batch>_<CODE>/` containing the stripped
recording under the same name, the strip report, `run.json` (who, which mice, which channels) and
`UPLOAD.json` (what was verified and how).

## 2. Three things about this rig that surprise people

### 2.1 The channel selection does not change what is recorded

> [!warning] ALLEGO ALWAYS RECORDS EVERY CHANNEL
> All 262 of them, every time, whatever is selected anywhere. Your selection decides only **what
> survives into the stripped copy** that goes to the NAS. The full original stays on the recording
> computer and is never deleted by this tool.
>
> The upside: a mistake in the slot grid costs you nothing on the raw file. It can be re-stripped.

### 2.2 "0 bytes" for the first half-minute is normal

> [!danger] THE FILE SIZE DOES NOT MOVE FOR ABOUT 30 SECONDS AFTER A HEALTHY START
> Measured on this rig: the file exists immediately, reports **zero** for a full 30 s, then jumps
> straight to ~31 MB. Allego flushes its metadata in ~30-second blocks; the data were never missing.
>
> The console says so on screen during the first 90 seconds. **Do not conclude a recording has
> failed because it shows 0 bytes.** Growth is confirmed in the background after 40 s, and only then
> does the console complain. Full measurement:
> [[2026-09-11-allego-control-bench-test]].

### 2.3 One run owns the whole rig, and there is no default owner

> [!warning] RECORDING IS GLOBAL — ONE BOX, ONE RECORD BUTTON, ONE FILE
> The XDAQ has a single `R_ON` state for all four ports. `radiens 4.0.0` has **no per-port recording
> control** whatever the upstream documentation says — measured, see
> [[multi-user-independent-recording-schedules]]. Two people cannot record
> independently at the same time, and the console refuses to start a second run while one is active.
>
> To share the rig, record the **union** of both windows and separate afterwards by stripping — the
> console's per-slot mouse IDs are what makes that separation possible at all.

And there is **no default name in the owner dropdown**. It is the one field nobody should be able to
get wrong by not looking: a pre-selected name is how one person's run ends up in another person's
folder. Buttons stay disabled, with the reason shown, until a name is chosen.

### 2.4 Fewer mice than slots is ordinary, and nothing has to be told twice

Put mice in whichever positions you are using and leave the rest blank. A slot with no mouse ID is
simply not part of the run:

- **Only your channels are kept.** Three mice in `A1`, `C2`, `D1` gives a six-channel file, not a
  sixteen-channel one with ten empty columns. Measured on a real recording 2026-09-13 — bit-exact,
  and the stripped copy reads back as exactly `A/1 A/2 C/33 C/34 D/1 D/2`.
- **Only your animals are graded.** Quality control runs on the positions you filled in.

> [!warning] THIS WAS WRONG UNTIL 2026-09-13 AND THE OUTPUT LOOKED PLAUSIBLE
> Before that date, quality control graded **all eight positions regardless**, so a four-mouse run
> came back with four extra cards named `UNKNOWN@B2` and similar — and three such cards read
> **PASS at rung 2**. Those cards are built from amplifier inputs with nothing plugged into them.
> If you have a QC bundle produced before 2026-09-13 for a partially loaded rig, **ignore every
> `UNKNOWN@` row in it**; they are not animals somebody forgot to name.

The one thing that is *not* free: the empty slots' channels are still recorded (§2.1) and still
occupy disk at the full rate. A one-mouse run costs the same 90 GB/day as an eight-mouse run.

### 2.5 The unipolar layout produces no quality verdict, by design

This project judges every channel against **wire-free amplifier inputs recorded in the same file** —
sites `/3`–`/16` and `/35`–`/48` on a 64-channel chip.

> [!danger] CORRECTED 2026-09-14 — the reason is EVIDENCE-ABSENT, not shape-mismatch
> This section used to say the floor model "simply does not describe" `/18`–`/23`. That is the wrong
> reason and a dangerous one. An **RHD2132 has 32 real unipolar inputs**, so those six sites are real
> amplifiers and about 26 real inputs sit unused — a floor *could* be derived from them.
>
> It must not be. [[2026-08-05-unipolar-lfp-mouse-reference]] measured those
> unused inputs at a median **0.17 MΩ** and warns that *"on this headstage the unused inputs are tied
> to ground, so a low magnitude proves nothing at all."* A floor built from ground-tied inputs
> flatters the control and condemns every real animal.
>
> Why it matters which reason is recorded: *"the shape does not fit"* invites the next person to fix
> the shape and derive a floor from `/24`–`/32`. *"Nobody characterised these inputs"* does not.

So the recording setting declares `qc: none` with its reason, the console says so under the slot grid **before you start**, and
the run record carries `qc_not_applicable` — deliberately a different mark from `qc_bundle_skipped`,
which means a person waived a check that *was* possible. A unipolar recording reaches the NAS with
no quality verdict from this project attached. That is a property of the layout, not a failure of
the run.

> Until 2026-09-13 this instead demanded a manual override on **every** unipolar run. That is worse
> than useless: a guard that can never be satisfied is a guard people learn to click past, including
> on the runs where it is load-bearing.

## 3. Scheduling rules

| Situation | What happens | Why |
|---|---|---|
| scheduled start arrives | starts, records how late it was | |
| service was down over the instant, **< 3 min late** | starts, lateness recorded | |
| **> 3 min late** | **`FAILED_START`, does not start** | a sleep recording that begins hours after ZT0 is not the experiment that was designed. A clear failure beats an unexplained recording |
| scheduled stop arrives late | **always stops**, overrun recorded | stopping late costs a longer file; not stopping costs 90 GB/day and the next person's slot |
| service restarts mid-run | in-flight runs rewind to the last actionable state; schedules re-arm from disk | a 24 h run outlives any process |
| NAS unreachable when the upload comes | run rests in `UPLOAD_PENDING` and drains later | **this is designed behaviour, not a fault** |
| a reservation was made by mistake | press **cancel** on its row in the runs table (since 2026-10-14); it becomes `ABORTED` and stays listed | only a scheduled or draft run can be cancelled; a started run is stopped with Stop |
| a headstage dropped off the bus before the start | **starts anyway**, records the ports that are present; the live enumeration and the mismatch go on the run (`results.start_enumeration`, `start_warning`), the runs table shows a red **port missing at start** tag, and ntfy gets a `fail` alert (since 2026-10-15, after run `dca84de0cc7a` silently recorded 2 of 3 mice) | refusing would lose every other animal to save one; takes effect after the next `eeg-recorder` restart |
| two reservations overlap | **both are accepted**; the later one fails at its own start (`FAILED_START`, "already using the rig") and the active run is untouched | 🔴 not refused at creation yet (found 2026-10-14). **Check the DATE field**: the form pre-fills the next day |

> [!info] How it works underneath
> Every program involved, what fires each one, every failsafe and why it exists:
> [[pipeline-architecture]]. Read that before changing any of it.

## 4. What it is made of

| File | Role |
|---|---|
| `eeg-recorder/backend/app.py` | Flask on `127.0.0.1:8600`, serves the API and the page |
| `eeg-recorder/backend/allego.py` | status, the `ConfigRecording` workaround, start/stop, growth check |
| `eeg-recorder/backend/runs.py` | durable run store (SQLite, WAL) and the state machine |
| `eeg-recorder/backend/scheduler.py` | absolute-instant start/stop, re-armed on boot |
| `eeg-recorder/backend/postprocess.py` | QC → strip → upload, one worker at a time |
| `eeg-recorder/backend/nas_upload.py` | CIFS upload with cache-dropped read-back verification |
| `eeg-recorder/backend/presets.py`, `config/users.yaml` | who records, and which channels their layout uses |
| `eeg-recorder/frontend/` | the page. One HTML file, no build step |

Service: `eeg-recorder.service`, enabled at boot. Logs: `journalctl -u eeg-recorder -f`.
State: `~/.local/state/eeg-recorder/runs.db`.

> [!info] Why this is separate from the video session daemon
> `neurosurveillance-session.service` polls Radiens and declares observe-only as an invariant. This
> service **drives** the recorder. Keeping them in separate processes on separate ports means a bug
> in recording control cannot take video recording down, and a video-daemon crash cannot strand a
> 24-hour EEG run. The vault already recorded keeping the EEG scheduling path separate as a decision
> rather than an accident.

> [!quote] Paper-ready
> Recordings are initiated and terminated through a local control service that records, for each
> run, the responsible investigator, the animal identifier and experimental condition assigned to
> each amplifier position, and the set of electrode sites in use. Because the acquisition system
> provides a single global record state for all four ports, concurrent independent recordings are
> not possible; runs are therefore serialised, and per-animal separation is performed after
> acquisition using the recorded position assignments.

## 5. When something looks wrong

| Symptom | Meaning | What to do |
|---|---|---|
| Allego pill red, "unreachable" | the acquisition software is not running or not answering | start Allego (with `--disable-gpu`), then reload |
| Allego pill amber, "sample rate is 30000" | a freshly launched Allego comes up at 30 kHz in `SMARTBOX_PRO` | fix the mode and rate in Allego; the console refuses to start until they are right |
| live panel shows 0 bytes | **normal for the first ~30 s** | wait. If it persists past the growth check the console says so explicitly |
| "R_ON but NOT GROWING" | the recorder claims to be recording and no bytes are landing | needs a person. This is the silent-failure signature that cost a 72 h run before |
| NAS pill red | share not mounted, or the sentinel is missing | see [[skim-nas-smb-and-upload]] §5. Runs wait safely meanwhile |
| a run sits in `FAILED_QC` | no QC bundle, so stripping would destroy the only record of the wire-free floor | **This is the expected state for any recording that has not been QC'd yet, including every test run.** Press **retry**: it asks whether to strip anyway. Say yes for a test; for real data, compute the bundle first and then retry. The choice is recorded on the run either way, and applies to that run alone |
| a run sits in `UPLOAD_PENDING` | the NAS is unreachable | nothing to do. It drains when the NAS returns |
| a run sits in `FAILED_STRIP`, "din_1 ... transitions" | Gate B saw a varying digital input it would drop. With nothing wired to the GPIO header that is noise on a floating input (run `ee0263bffeaa`, 10-08) | since 2026-10-14 `rig.gpio_header_connected: false` in `config/users.yaml` makes the console pass `--gpio-never-connected` itself, and the strip report records it as `gate_b_override`. Set it to `true` the day the XDAQ → Pi sync is wired |

> [!warning] THIS TOOL DOES NOT REPLACE THE PRE-FLIGHT SCREEN
> For any recording whose timepoint dies with the animals, [[pre-flight-connection-screen]]
> still gates the run. The console tells you a recording is *writing bytes*; it says nothing about
> whether the electrodes are connected.

## 6. Status

✅ **Unipolar, 3 mice, one per port (2026-10-14):** a scheduled 10-minute rehearsal (run `901e16ee8bf8`, layout
`4mice_unipolar_lfp`) went start → stop → strip (18 channels) → 3 CSVs → NAS verified → `DONE` in 41 s after the stop.
See [[2026-10-14]].

✅ **The full chain has run end-to-end on a real recording** (2026-09-11, `allego_0__uid0911-22-32-22`,
91 s, eight slots): started on time, growth confirmed at 2.86 GB/h, stopped `R_ON → R_OFF`, held at
QC for the missing bundle, stripped 93.18% smaller after the bundle was explicitly waived, and
uploaded with **4 files verified, 0 size-only**. The whole sequence is in that run's event log.

That first real run also exposed three defects in the retry path, all now fixed and covered by
regression tests — see §5 and
[[recording-console-retry-was-a-dead-end]].

✅ **Scheduling is verified on the real rig** (2026-09-13, a 9-minute bench run): the start
fired **3 s after the instant**, the stop fired **0.5 s late**, and the full chain ran afterwards
— including a QC bundle the system **computed for itself**, with no manifest and no human step.

That bench run also found a real defect: a *scheduled* stop halted the rig and then stranded the
run at `STOPPED`, because the handoff to post-processing existed only on the manual stop button.
Fixed, and covered by a test that fails when the handoff is removed.

Still open:

- Whether the Radiens reader accepts a stripped file is **unproven** — there is no Videre hub on this
  host to ask. Our own reader accepts it.
- **No unattended overnight run has completed yet.** The 24 h run on 2026-09-12 was started and
  stopped by hand; scheduling has only been exercised over 9 minutes.

## 7. Related

- [[2026-09-11-allego-control-bench-test]] — the measurements behind §2.2
- [[xdat-channel-stripping]] — what the strip does and what it costs
- [[skim-nas-smb-and-upload]] — the NAS, and how uploads are verified
- [[scheduled-recording-and-watchdogs]] — the older crontab-based path, still valid
- [[CANONICAL-allego-channel-selection]] — which sites are the wired ones
