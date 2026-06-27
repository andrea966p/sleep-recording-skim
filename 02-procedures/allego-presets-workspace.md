---
tags:
  - procedure
  - radiens
  - allego
  - workspace
  - settings
  - onboarding
created: 2026-06-27
status: complete
---

# Allego Save Workspace & User Profile — What Gets Remembered

> [!abstract] TL;DR — for non-technical readers
> **What this is.** A guide to Allego's **Save Workspace** feature — the button that remembers your window/tab layout *and* most of your settings so you don't rebuild the screen every launch. Crucially, it lists exactly **what is** and **what is NOT** remembered.
>
> **Why it exists.** There is one nasty gap: **your channel selection (which sites are recorded) is NOT saved.** An operator who trusts "Restore" and skips re-selecting channels can start a session recording the wrong (or zero) channels. This page makes that gap loud.
>
> **How to read this page.** Read the retention table once, tattoo the "Selected Sites = No" row on your brain, then use the start-of-session checklist. Big picture: [[01-infrastructure/system-overview]].

> [!warning] The gap that bites operators
> **Selected / Deselected Sites = NOT retained** (manual p30). Save Workspace remembers your layout, mode, sample rate, filters, gain — but **not which channels you selected**. You must **re-select your recording channels every session** (for us: System tab → Signals → Port D → `D/1,2,3,4,9,10,11,12`). Verify before hitting `Record`. See [[allego-monitor-guide]] and [[radiens-software-reference]] for the selection steps.

---

## Save Workspace vs. Restore vs. Trashcan

The workspace buttons live in the **upper-right** of the Allego window (manual p29-30):

| Button | Icon (manual) | What it does |
|---|---|---|
| **Save Workspace** | down-arrow / download icon | "Saves the current configuration of your workspace. It allows you to preserve the arrangement of tabs and windows, making it easier to restore the layout at a later time" (manual p29). |
| **Restore** | circular-arrow icon | "Restores the tabs to their saved locations when you launch Allego. This functionality ensures that your preferred layout is automatically applied upon starting the software" (manual p30). |
| **Trashcan** | trashcan icon | "Deletes the currently saved workspace and return the UI to its default state" (manual p29). |

> [!note] Layout itself is freely rearrangeable
> Independent of save/restore, the **Dashboard** is drag-configurable: "Click and hold on the tab header… drag the tab to the desired location… release" — and tabs can be shown split-screen or stacked like browser tabs (manual p31). Save Workspace simply *persists* whatever arrangement you've built.

## What is retained by Restore Workspace

This is the manual's own "Restore Workspace Feature Retention" table (manual **p30**), reproduced verbatim:

| Group | Feature | Retained? |
|---|---|---|
| **System** | Mode | **Yes** |
| System | Sample Rate | **Yes** |
| System | **Selected / Deselected Sites** | **No** ⚠️ |
| System | Gain | **Yes** |
| System | AO Control | **Yes** |
| System | Highpass filter | **Yes** |
| System | AO 1 / AO 2 mapping | **Yes** |
| System | Digital Out Control Mode | **No** |
| System | Digital In Triggering State | **Yes** |
| System | Digital In Triggering Channel | **Yes** |
| **Electrodes** | Headstage Selection | **Yes** |
| Electrodes | Probe Selection | **Yes** |
| Electrodes | Site Reordering | **No** |
| **Signal Processing** | Filters | **Yes** |
| **Spike Sorter** | Threshold | **Yes** |
| **3d-model** | Stereotactic Coords | **No** |
| 3d-model | Animal Model | **No** |
| 3d-model | Hide Atlas Panel | **No** |
| 3d-model | Atlas Slice | **No** |

> [!important] Read the "No" rows for our rig
> - **Selected / Deselected Sites = No** → re-select channels every session (the big one).
> - **Site Reordering = No** → if you use a custom site order, it resets.
> - **Digital Out Control Mode = No** → re-verify the recording-gate `DO` mode (our hardware-sync `DO 03` "Gated" setup) after relaunch. The 3d-model / atlas rows are irrelevant to us (no spike/atlas workflow).
> - Reassuring "Yes" rows: **Mode, Sample Rate, Filters, Headstage/Probe selection** all persist — but **always re-confirm Mode** anyway, since it is known to silently revert (see [[radiens-software-reference]]), and **re-confirm Sample Rate** because switching Mode resets it ([[allego-sampling-rate]]).

## Recording file name & location = Settings, not Workspace

The recording **file name and save location** are set in the **Settings** module (gear icon), which also activates the software and sets visual themes (manual p29). The Status bar at the top holds the `Stream`/`Record` buttons and shows live recording/streaming duration; the Settings module is reachable from there too (manual p29). The user profile icon (top-right) shows subscription status and the installed Allego version (manual p31).

> [!note] For us, `Record` drives the session daemon
> Hitting `Record` (not `Stream`) is what our session daemon treats as a real `R_ON` and pairs with a Frigate video session. Confirm the file name/location in Settings before recording. See [[radiens-software-reference]].

## Preset Filters ≠ Save Workspace (don't confuse them)

A separate feature called **Preset Filters** (manual **p71**) lives in the Signal Processing tab. It is a *filter* shortcut, not a workspace feature: pick a port/channel from the dropdown, then click a one-touch button — **`SINGLE UNIT`, `MULTI UNIT`, `LFP`, or `EEG`** — to apply a tailored filter set, which then shows in the active filter group (manual p71).

| | Save Workspace (p29-30) | Preset Filters (p71) |
|---|---|---|
| Where | Upper-right window buttons | Signal Processing tab |
| Scope | Whole UI layout + settings retention | A bundle of filters for a signal type |
| Persists across launch? | Yes (via Restore) | Only as part of the retained **Filters** row (p30), if saved |

Note: applied **Filters** *are* retained by Restore (table above), so an `EEG` preset you applied will generally come back — but the **channels** you applied it to may need re-selecting, per the gap above.

## Start-of-session checklist

1. Launch Allego; let **Restore** reapply the layout.
2. **Re-confirm Mode** = `XDAQ One (G1) with XR Headstage` (it can silently revert).
3. **Re-confirm Sample Rate** (Mode changes reset it — see [[allego-sampling-rate]]).
4. **Re-select recording channels** (Selected Sites is *not* saved) → for us `D/1,2,3,4,9,10,11,12`.
5. Re-verify **Digital Out Control Mode** (sync gate) if used.
6. Confirm **recording file name + location** in Settings.
7. Check signal in [[allego-monitor-guide]] / [[signal-quality-and-grounding]], then `Record`.

## Related
- [[allego-sampling-rate]] — sample rate is retained, but Mode changes reset it
- [[allego-monitor-guide]] — re-selecting channels + reading the signal
- [[signal-quality-and-grounding]] — grounding + referencing before you record
- [[radiens-software-reference]] — PRIMARY Radiens/Allego reference (Mode revert gotcha, Record vs Stream)
- [[01-infrastructure/system-overview]]
