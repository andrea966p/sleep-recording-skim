---
tags: [procedure, eeg, allego, recording, console, layout, headstage, splitter, settings]
created: 2026-09-14
status: active
---

# Telling the console what the rig is: splitters, headstages and recording settings

> [!abstract] TL;DR — for non-technical readers
> **What this is.** Before a recording, the console asks what is physically plugged in: which ports
> have a splitter, and which signals each mouse carries. From that it works out how many mice you
> can enter, which channels to keep, and how to quality-check the result.
>
> **Why it exists.** The console used to offer three fixed whole-rig choices. The rig is not always
> one of those three — recordings already exist that none of them describe. And nothing checked the
> answer, so a wrong choice was discovered after the animals were done.
>
> **The one thing to remember.** The console now compares what you declared against what Allego
> actually found, and **refuses to record if they disagree**. Big picture:
> [[nvr-system-overview]].

## 1. What varies, and what does not

> [!important] Every mouse in a run has the same configuration
> Andrea, 2026-09-14: *"there will never be mice connected to the rig with different configuration
> at the same time. When someone records, the mice have all the same settings. What changes is just
> the amount of mice connected."*

So a run varies in exactly two ways:

| | varies? | where |
|---|---|---|
| headstage type | **no** — one for the rig | follows the recording setting |
| recording setting (EEG/EMG, +ECG, +LFP) | **no** — one for the rig | a dropdown |
| **SPI splitter fitted** | **yes, per port** | a checkbox per port |
| **how many mice, and where** | **yes** | leave a slot blank and it is not in the run |

## 2. The splitter decides how many slots a port has

This is the piece most worth understanding, because it is also what the console checks.

> "Each port is 64 slots because the **C3442 splitter puts two RHD2216 chips on one port**, and each
> chip occupies **32 slots** in the RHD2000 data stream — of which only the first 16 are real."
> — [[CANONICAL-allego-channel-selection]] §3

    channels a port enumerates = (chips on it) × (slots that chip occupies)

| port has | chips | Allego enumerates | slots | slot names |
|---|---|---|---|---|
| a splitter | 2 | **64** | 2 animals | `A1`, `A2` |
| no splitter | 1 | **32** | 1 animal | `A` |

A port without a splitter is called by its bare letter. The second animal on a split port sits at
**`/33`, not `/29`** — the +32 trap in [[eight-mouse-acquisition-setup]] §6.

### A port you are not using at all

Each port also has an **In use** checkbox. Untick it and that port leaves the run entirely: its
slots disappear, its splitter setting is greyed out, it is exempt from the check in §3, and none of
its channels reach the stripped copy.

> [!important] This is what you need when a headstage is unplugged
> A port with nothing connected enumerates **0**, which the check refuses — correctly, since the
> alternative is recording a port you think is live and finding out afterwards. Until 2026-09-14
> there was no way to say "I am not recording on that port today", so an unplugged headstage was a
> dead end that looked like the console being broken.
>
> Leaving slots **blank** is different and unrelated: that is how you record fewer mice on a port
> that *is* connected. Both are normal.

> [!warning] The headstage does NOT change the channel count. It changes what is real.
> 64-vs-32 is a **splitter** property. What the chip decides is how many of those enumerated slots
> are real amplifiers: an RHD2216 exposes 16, an RHD2132 exposes 32. That is why `/18`–`/23` carry
> signal on the unipolar prep and read as inactive tied slots on a bipolar one.

## 3. 🔴 The check that makes this worth doing

Allego reports what each port actually enumerated. The console predicts the same number from your
declaration and **compares them**:

```
Port A  [x] splitter   64 ch, expects 64   A1 · A2
Port B  [x] splitter   64 ch, expects 64   B1 · B2
Port C  [ ] splitter   64 ch, expects 32   C          <- red
Port D  [x] splitter   64 ch, expects 64   D1 · D2

Cannot record:
• port C: declared no splitter with RHD2216 bipolar, which enumerates 32 channels
  -- but Allego reports 64. Either the splitter state is wrong or the headstage
  is not the one declared.
```

**Start and Schedule are disabled** until it agrees, and the API refuses the same thing independently
of the page, so it is not only a screen courtesy.

Why a refusal rather than a warning: declaring the rig wrongly means the strip keeps the wrong
channels, and nothing downstream notices. A warning at 09:00 before a 24 h run gets clicked through.

A port you are not using is exempt. A port reporting **0** is called out as nothing connected.

## 4. Recording settings

A setting says which site number carries which signal, within one chip.

| setting | headstage | sites | QC |
|---|---|---|---|
| `eeg_emg` | RHD2216 bipolar | `eeg=/1 emg=/2` | yes |
| `eeg_emg_ecg` | RHD2216 bipolar | `eeg=/1 emg=/2 ecg=/3` | yes |
| `eeg_emg_lfp` | Intan unipolar RHD2132 | `/18`–`/23` | **none — §5** |

The unipolar map: `/18` EMG left (`emg_l`), `/19` LFP target (`lfp_tgt`), `/20` LFP reference
(`lfp_ref`), `/21` EMG right (`emg_r`), `/22` EEG parietal (`eeg_p`), `/23` EEG frontal (`eeg_f`).

> [!warning] Corrected 2026-10-14
> The map first written here and in
> [[2026-08-05-unipolar-lfp-mouse-reference]] (`/18` EMG 1, `/19` LFP ref,
> `/20` LFP target, `/21` EEG frontal, `/22` EEG parietal, `/23` EMG 2) was a typo (Andrea,
> 2026-10-14). The map above is the only correct one. No console run used the old one.

> [!note] Those six are SINGLE-ENDED and the pairing is deliberately not encoded
> The signal is a difference between two of them (EEG = `/22` and `/23`). Our bipolar chips do that
> subtraction in hardware, which is why the standing rule is never to subtract our normal channels.
> The console keeps the raw sites and **computes nothing**; the pairing lives in the procedure, not
> in the config.

## 5. 🔴 Why the unipolar layout gets no quality verdict

Not because the shape does not fit. **Because nobody characterised the control.**

An RHD2132 has **32 real inputs**, so `/18`–`/23` are real amplifiers and about 26 real inputs sit
unused. A floor *could* be derived from them. It must not be: the 2026-08-05 page measured those
unused inputs at a median **0.17 MΩ** and warns that *"on this headstage the unused inputs are tied
to ground, so a low magnitude proves nothing at all."* A floor built from ground-tied inputs flatters
the control and condemns every real animal.

> [!danger] The distinction is the whole point
> *"The shape does not fit"* invites the next person to fix the shape and derive a floor from
> `/24`–`/32`. *"Nobody characterised these inputs"* does not. The config records the second, in a
> field of its own, and the console refuses to save a layout like it without a reason.

A unipolar recording therefore reaches the NAS with **no quality verdict from this project**. Animals
on such a chip come out `UNJUDGEABLE` — not `FAIL`, and never a fabricated pass.

## 5b. Channels for one run only

The **Recording setting** dropdown ends with **＋ Custom channels for this run…**. It opens the same
picker the settings panel has, but scoped to this run and not written to the config: one row per
signal, a name and a site number.

It starts as a **copy of the setting you were already using**, so you are editing your rig rather
than building one from nothing. The preview shows the sites for both animals on a split port, and
whether a QC floor will exist, as you type. A **Save as a named setting…** button turns the
selection into a reusable entry.

The selection goes through **exactly the same validator** as a setting stored in YAML, so nothing
typed here can be looser than something written into the config file by hand.

> [!info] A run remembers its own channels
> The role map is stored **on the run**, not just the name of a setting to look up later. So a
> recording stays readable after its setting is renamed or deleted — and a custom selection has no
> config entry to look up at all.

## 6. Adding your own recording setting

**Rig settings** at the bottom of the console → *Add a recording setting*. Give it a key, a label, a
headstage, then one row per signal: what to call it and which site carries it.

The form shows the consequence before you save:

```
3 channels per mouse. First animal on port A: A/1 eeg · A/2 emg · A/3 eeg2.
Second animal on a split port: A/33 · A/34 · A/35.
QC applies: the wire-free floor is /4–/16 on each chip.
```

and for sites the floor rule cannot describe it says **no QC bundle will ever be produced for this
layout** and makes you write why. It also catches sites past the chip's real channels.

**Saved layouts** are one-click starting points: the current setting plus which ports are split. Save
the declaration you are looking at under a name, and it appears in the Rig layout dropdown.

> [!info] What the panel will not let you do
> - **change anything while a run is in flight** — the run was created against the current config
> - **delete something a run still needs** — it waits until that run has stripped and uploaded
> - **edit headstages** — chip physics, YAML only; a wrong `slots_per_chip` silently breaks §3
> - **shadow a curated definition** — pick another name instead

## 7. Where the configuration lives

| file | written by | contains |
|---|---|---|
| `eeg-recorder/config/users.yaml` | **people, by hand** | the curated definitions and their provenance |
| `eeg-recorder/config/custom.yaml` | **the console** | whatever the settings panel added |
| `eeg-recorder/config/backups/` | the console | every replaced version of the above |

> [!important] The console never writes the curated file
> `users.yaml` carries the comments this project runs on — which recording each layout was measured
> from, why the unipolar floor is absent. No YAML writer in the standard library preserves comments,
> so a machine rewriting that file would silently delete all of it. Everything the form adds goes to
> `custom.yaml` instead. `git diff` then shows at a glance what a person wrote and what a form
> generated.

Every change is validated in full **before** the file is replaced, so a bad entry cannot leave a
service that will not start; the swap is atomic; the previous version is kept; and each change is
appended to an audit log shown at the bottom of the panel.

## 8. When something is wrong

| Symptom | Meaning | Fix |
|---|---|---|
| a port is red, "Allego reports 64" | you declared no splitter on a split port | tick the splitter, or check the hardware |
| a port is red, "nothing is connected" | Allego enumerates 0 | check the SPI cable and the bottom socket — or untick **In use** if you are not recording on it today |
| Start is greyed and mentions a mouse ID | the same ID is in two slots | give each animal its own. Capitalisation does not make them different: `HLBSSL31` and `hlbssl31` are one mouse |
| "has never been recorded on this rig" | a splitter with two unipolar headstages | someone must see it enumerate, then set `splitter_verified: true` |
| the layout dropdown says **Custom** | your ports no longer match any saved layout | normal; save it as one if you will use it again |
| "cannot change while a run is in flight" | a run has not finished stripping or uploading | wait for it, or abort it |

## 9. Related

- [[eeg-recording-console]] — running a recording once the layout is declared
- [[pipeline-architecture]] — every program and every failsafe
- [[CANONICAL-allego-channel-selection]] — the measured channel map
- [[eight-mouse-acquisition-setup]] — the +32 trap, and the physical topology
- [[2026-08-05-unipolar-lfp-mouse-reference]] — the unipolar measurement
- [[xdat-channel-stripping]] — what the strip keeps, and its gates
