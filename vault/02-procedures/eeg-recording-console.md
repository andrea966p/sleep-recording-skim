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
> copies it into your folder on the lab's network storage, checking that the copy is perfect before
> it says so.
>
> **Why it exists.** Five people share one rig. Before this, starting a recording meant clicking in
> the acquisition software, and nothing anywhere recorded who was recording, which animal was in
> which slot, or what kind of experiment it was. That information lived in people's heads and
> notebooks, and the resulting file was a single 262-channel block that nobody could split up later
> without asking whoever ran it.
>
> **How to read this page.** Section 1 is everything you need to run a recording. Section 2 is the
> three things about this rig that are surprising and worth knowing before you trust what you see.
> Section 5 is what to do when something looks wrong. Background: [[01-infrastructure/system-overview]].

**Open it at <http://127.0.0.1:8600>** on the recording computer. It is bound to localhost only —
this drives amplifiers with animals attached, so it is deliberately not reachable from the lab
network.

## 1. Running a recording

1. **Pick your name.** There is no default, on purpose — see section 2.3.
2. **Pick the rig layout.** It fills in from your name, but change it if today is different:

   | preset | channels | sites per port | animals |
   |---|---|---|---|
   | `8mice_eeg_emg` | 16 | `/1 /2 /33 /34` | 8, two per port |
   | `8mice_eeg_emg_ecg` | 24 | `/1 /2 /3 /33 /34 /35` | 8, two per port |
   | `unipolar_lfp` | 24 + all 6 GPIO | `/18`–`/23` | **4, one per port** |

   The slot grid follows the preset, so `unipolar_lfp` shows **four** slots, not eight.
3. **Fill in the occupied slots** — mouse ID and recording type (`basal`, `recovery`, `sd`). Leave
   empty slots empty. Mouse IDs become part of a folder name, so letters, digits, `-` and `_` only.
4. **Check the line under the grid.** It says exactly which channels will be kept and which folder
   the data will land in, *before* anything happens. This is the one decision that cannot be undone
   after the run.
5. **Start now**, or set **Start at** and **Stop at** and press **Schedule**. Times are local, and
   the header shows the current **ZT** so you do not have to do the arithmetic. Default is the next
   09:00 (ZT0) running 24 h, which is the shape most runs here have.

While recording, the page shows elapsed time, the file name, bytes on disk and when it will stop.
Pressing **Stop recording** ends it and immediately queues the post-processing.

### What happens after it stops, without anyone present

    QC bundle  →  strip to your channels  →  upload to your folder  →  verify

Your data appears at `{SKIMNAS_ROOT}/<your name>/<date>_<recording>/` containing the stripped
recording, the strip report, `run.json` (who, which mice, which channels) and `UPLOAD.json` (what
was verified and how).

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
> [[05-experiments/completed/2026-09-11-allego-control-bench-test]].

### 2.3 One run owns the whole rig, and there is no default owner

> [!warning] RECORDING IS GLOBAL — ONE BOX, ONE RECORD BUTTON, ONE FILE
> The XDAQ has a single `R_ON` state for all four ports. `radiens 4.0.0` has **no per-port recording
> control** whatever the upstream documentation says — measured, see
> [[02-procedures/multi-user-independent-recording-schedules]]. Two people cannot record
> independently at the same time, and the console refuses to start a second run while one is active.
>
> To share the rig, record the **union** of both windows and separate afterwards by stripping — the
> console's per-slot mouse IDs are what makes that separation possible at all.

And there is **no default name in the owner dropdown**. It is the one field nobody should be able to
get wrong by not looking: a pre-selected name is how one person's run ends up in another person's
folder. Buttons stay disabled, with the reason shown, until a name is chosen.

## 3. Scheduling rules

| Situation | What happens | Why |
|---|---|---|
| scheduled start arrives | starts, records how late it was | |
| service was down over the instant, **< 3 min late** | starts, lateness recorded | |
| **> 3 min late** | **`FAILED_START`, does not start** | a sleep recording that begins hours after ZT0 is not the experiment that was designed. A clear failure beats an unexplained recording |
| scheduled stop arrives late | **always stops**, overrun recorded | stopping late costs a longer file; not stopping costs 90 GB/day and the next person's slot |
| service restarts mid-run | in-flight runs rewind to the last actionable state; schedules re-arm from disk | a 24 h run outlives any process |
| NAS unreachable when the upload comes | run rests in `UPLOAD_PENDING` and drains later | **this is designed behaviour, not a fault** |

> [!info] How it works underneath
> Every program involved, what fires each one, every failsafe and why it exists:
> [[01-infrastructure/eeg-recorder/pipeline-architecture]]. Read that before changing any of it.

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
| NAS pill red | share not mounted, or the sentinel is missing | see [[02-procedures/installation/skim-nas-smb-and-upload]] §5. Runs wait safely meanwhile |
| a run sits in `FAILED_QC` | no QC bundle, so stripping would destroy the only record of the wire-free floor | **This is the expected state for any recording that has not been QC'd yet, including every test run.** Press **retry**: it asks whether to strip anyway. Say yes for a test; for real data, compute the bundle first and then retry. The choice is recorded on the run either way, and applies to that run alone |
| a run sits in `UPLOAD_PENDING` | the NAS is unreachable | nothing to do. It drains when the NAS returns |

> [!warning] THIS TOOL DOES NOT REPLACE THE PRE-FLIGHT SCREEN
> For any recording whose timepoint dies with the animals, [[02-procedures/pre-flight-connection-screen]]
> still gates the run. The console tells you a recording is *writing bytes*; it says nothing about
> whether the electrodes are connected.

## 6. Status

✅ **The full chain has run end-to-end on a real recording** (2026-09-11, `allego_0__uid0911-22-32-22`,
91 s, eight slots): started on time, growth confirmed at 2.86 GB/h, stopped `R_ON → R_OFF`, held at
QC for the missing bundle, stripped 93.18% smaller after the bundle was explicitly waived, and
uploaded with **4 files verified, 0 size-only**. The whole sequence is in that run's event log.

That first real run also exposed three defects in the retry path, all now fixed and covered by
regression tests — see §5 and
[[03-troubleshooting/symptoms/recording-console-retry-was-a-dead-end]].

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

- [[05-experiments/completed/2026-09-11-allego-control-bench-test]] — the measurements behind §2.2
- [[02-procedures/installation/xdat-channel-stripping]] — what the strip does and what it costs
- [[02-procedures/installation/skim-nas-smb-and-upload]] — the NAS, and how uploads are verified
- [[02-procedures/scheduled-recording-and-watchdogs]] — the older crontab-based path, still valid
- [[02-procedures/CANONICAL-allego-channel-selection]] — which sites are the wired ones
