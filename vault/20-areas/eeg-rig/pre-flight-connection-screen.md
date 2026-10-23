---
type: procedure
area: eeg-rig
status: active
tags: [procedure, eeg, qc, recording]
created: 2026-08-29
---

# The pre-flight connection screen: check before the run, not after it

> [!warning] Updated 2026-10-22: The ≥ 2000 µV chip-floor bar was falsified on 2026-10-02, and since the 2026-10-07 grounding fix chip floors read 36-235 µV, so this bar fails every chip; no replacement gate exists yet. Whether to launch Allego with `--disable-gpu` is disputed (logged in `_meta/contradictions/eeg-rig.md`). [[weak-chip-ground-vs-open-electrode]]

> [!abstract] TL;DR
> **Before any recording whose timepoint cannot be repeated, take a short recording, score the
> connection on it, fix what is fixable, and only then start the real run.** Twenty minutes of
> checking is cheap. Twenty hours of one-animal data is not.
>
> This exists because of 2026-08-27. A 20 h rebound recording was started on eight animals at
> 13:00 on the Thursday, the moment the penultimate day's sleep-deprivation bout ended, and ran to
> 09:00 on the Friday with sampling straight afterwards. A first-hour screen was
> run **during** the recording and reported that one of the eight positions was working. The fault
> on two of the failing positions was a connector, it was fixed in minutes, and it was fixed
> **after the recording had already ended**. See [[2026-08-27-W-SD-recovery-sleep]].

## When this is mandatory

Any recording where **the timepoint dies if the data is bad**:

- a recovery-sleep or any other post-treatment endpoint, where the animals are sampled afterwards;
- the last recording before a scheduled sacrifice;
- a run at a fixed circadian phase that will not recur before the animals are needed;
- any run longer than about 6 h, simply because the cost of losing it is high.

For an ordinary exploratory run it is optional, though it still costs almost nothing.

## The procedure

1. **Record 10 minutes.** Same sampling rate, same channel selection, same mode as the real run.
   Confirm the file is 1000 Hz and 262 channels — a fresh Allego launch can come up at 30 kHz in
   `SMARTBOX_PRO` mode. Launch Allego plainly, without `--disable-gpu` (the flag blanks the Monitor; decided 2026-10-23, [[allego-blank-monitor-canvas-texture-limit]]).

2. **Score it, position by position.** Run the connection check against the **wire-free floor in
   that same file**. Three numbers per position, and nothing else is needed at this stage:

   | | what it must show |
   |---|---|
   | chip floor 60 Hz | **≥ 2000 µV**. Below that, no statistic on that chip means anything |
   | EEG lf/hf vs its own chip floor's 99th percentile | **animal above floor** = real EEG present |
   | EEG railing | **≈ 0%**. High railing means an open input riding the rail |

3. **Triage what you find** using
   [[weak-chip-ground-vs-open-electrode|"no EEG" is at least four different faults]]:

   | finding | fixable at the bench right now? |
   |---|---|
   | chip floor low or collapsing | ✅ **yes** — re-mate the headstage and the tether connector |
   | EEG open and railing, floor normal | ❌ no — animal side, needs a tether change under isoflurane |
   | EMG works, EEG flat | ✅ **yes** — the implant and cable are carrying signal, so it is the EEG path or the reference |
   | both channels open and railing | ❌ no — usually a chewed or severed tether |

4. **Fix what is fixable, then re-screen for 10 minutes.** Confirm the floor came back before
   trusting anything.

5. **Write the go / no-go line down** in the day's journal entry, with the positions that passed and
   the positions you knowingly started without. That single line is what tells you later whether a
   missing animal was a surprise or a decision.

6. **Start the real run**, and arm the byte-rate watchdog on the new file.

## What "good enough to start" means

There is no universal answer, but the decision should be explicit:

- **Green** — enough positions pass that the experiment answers its question. Start.
- **Amber** — the run is worth taking but under-powered. Start, and record in the journal that the
  result will be n = *whatever*, so nobody discovers that at analysis time.
- 🔴 **Red** — one or two positions passing on an endpoint that cannot be repeated. **Fix first.**
  On 2026-08-27 this was red, it was recorded as amber by default, and the outcome was n = 1.

## Why the screen must gate rather than annotate

A screen run during a recording produces exactly the same numbers as a screen run before it. The
difference is entirely in what can still be done about them. On 2026-08-27:

| | |
|---|---|
| what the first hour said | 1 of 8 positions giving EEG; four chip grounds at a third of normal |
| what was actually wrong on two of them | a connector |
| how long the fix took | minutes |
| when it was applied | after the 20 h run had ended |
| what the run produced | one usable animal, and the paired comparison it existed for became n = 1 |

🔑 **Nothing about the analysis was too slow. The screen ran and reported the same day. It just was
not positioned where it could change anything.**

## Watchdog, separately

The byte-rate watchdog answers a different question — *is the file still growing* — and does not
detect a disconnected electrode. Both are needed. See
[[scheduled-recording-and-watchdogs]].

```bash
# check bytes on disk every 120 s, log the rate as a % of 262 * 4 * fs bytes/s,
# and record whether allegoserver is alive
```

## Related

[[2026-08-27-W-SD-recovery-sleep]] · [[weak-chip-ground-vs-open-electrode]] ·
[[per-animal-failure-signatures]] · [[animal-card-and-verdict-ladder]] ·
[[scheduled-recording-and-watchdogs]] · [[sleep-recording-operator-manual]]
