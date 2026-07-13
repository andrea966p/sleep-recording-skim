---
tags:
  - procedure
  - radiens
  - allego
  - neuronexus
  - workspace
  - config
  - eeg
created: 2026-07-13
status: review
---

# Allego Settings — Save & Restore (so we never re-enter the whole rig again)

> [!abstract] TL;DR
> A lab member reopened Allego and every setting was gone. This is a KNOWN Allego behavior, not a one-off mistake. Allego has a built-in **Save Workspace / Restore Workspace** feature (the download and circular-arrow icons, top right of the window) and it DOES restore most of our setup on the next launch: Mode, Sample Rate, Filters (including our 60 Hz notch), Headstage + Probe selection, Gain, Highpass, Digital In triggering. The manual's own retention table (p30) is the source of truth.
>
> **THE ONE GAP:** Restore Workspace does NOT bring back **Selected/Deselected Sites** (our per-port channel selection, `/1-4` + `/33-36`) and does NOT bring back **Site Reordering**. Those two must be re-selected by hand every launch, OR re-applied from a script via the SDK. That gap is exactly the "Allego forgets channel-select on every re-enumeration" note we already had.
>
> **What to do right now (zero code):** Click **Save Workspace** ONCE after you have the rig fully configured. From then on, launch Allego and click **Restore Workspace** — you get everything back except the channel-select tick boxes, which you re-tick from the wiring cheat sheet ([[signal-mapping-guide]] §1.1). Also make a file-level backup of the config files listed below so a bad workspace or a `~/.config/allego` reset (like the Jul 9 one) can't wipe you out.
>
> **Still open / needs bench test:** whether Save Workspace survives a full hardware **re-enumeration** (unplug/replug XDAQ), and whether an SDK script can re-apply channel selection to close the one gap. Marked NEEDS TESTING below.

Related: [[signal-mapping-guide]] (how to build + select the channel map), [[signal-quality-and-grounding]], [[06-references/radiens-software-reference|radiens-software-reference]] (embeds the 177-pg manual; Save Workspace p29, retention table p30, Preset Filters p71).

---

## The problem, plainly

When Allego is closed and reopened, or when the XDAQ / headstage **re-enumerates** (unplug, power blip, backend crash + restart), the running configuration is lost and has to be typed back in by hand:

- acquisition **Mode** = `XDAQ One (G1) with XR Headstage` (`XDAQ_ONE_REC`)
- **Sample Rate** = 1000 S/s (Allego's floor; we decimate offline)
- **Channel selection** = the `passthrough_64` map loaded, then per-port tick `/1-4` and `/33-36` (8-mouse map, 2nd headstage native +32)
- **Filters** = notch now **60 Hz** (Korea mains is 60 Hz, see the 60 Hz mains discovery), highpass, etc.
- **Montage / references**
- **Probe / sensor map** (the `.hstg` + `.prb` custom map)

Re-entering all that for 4 to 8 mice is slow AND error-prone, and a wrong channel-select silently records junk (Mouse 2 never streams — see [[signal-mapping-guide]] §7 trap box). So we want to save the full setup and load it back in one step.

---

## Where Allego actually stores its settings (verified on disk 2026-07-13)

I read these on the live NVR (`e10ubuntu`, user `skimlab`). Formats and what each file holds:

| Path | Format | What it holds | Notes |
|------|--------|---------------|-------|
| `~/radix/workspace/.system/ws-default_allego.json` | JSON (with base64-**protobuf** blobs inside) | The signal-side workspace: `config_core` (`samp_freq`, cable lengths), `config_recording` (base name + path), `signal_groups`, `dsp_group`, spike-sorter params | This is the meaty one. BUT on this machine it's dated **Feb 3** and shows `samp_freq: 30000`, i.e. it is the stale factory default and was NOT being rewritten with the user's live 1000 S/s setup. So a plain "copy this file" backup of the *current* file may capture stale values unless we Save Workspace first (see NEEDS TESTING). Many fields are base64 protobuf = NOT human-editable by hand. |
| `~/.config/allego/allego-workspaces.json` | JSON | The Electron/React **UI layout** — which panels (System, Monitor, Impedance, Electrodes, DSP, Settings) are open and how they're arranged. `"saved": false`, `"Untitled Workspace"` currently. | This is the layout half of "workspace", not the signal config. |
| `~/.config/allego/allego-windows.json` | JSON | Tiny window-index map | Cosmetic. |
| `~/.config/allego/` (whole dir) | Chromium/Electron profile | Cache, Cookies, Local Storage, Preferences, GPU cache | This is the app profile dir. **It was reset Jul 9** — that reset is a plausible trigger for the "all settings gone" event. |
| `~/radix/devices/*.hstg` | **YAML** (`ntv_chan_idx` → `site_num`) | Headstage / channel maps. Ours: `hstg__passthrough_64.hstg`, `hstg__usrdef_dual_mouse_c3442.hstg`, `hstg__usrdef_mouse_4ch.hstg`, etc. | These are safe, plain-text, human-readable, and stable on disk. Built by NeuroNexus's `csv2sensor` (see [[signal-mapping-guide]] §5). Losing these would be bad; they're easy to back up. |
| `~/radix/devices/*.prb` | text/JSON-ish | Probe geometry maps paired with the `.hstg` files | Same deal — plain files on disk. |
| `~/radix/custom_sensors/` | (empty right now) | Custom sensor defs | Empty on this box. |
| `~/.config/radiens/session.json` | JSON | **Cognito login token only** (Staci Kim / KAIST). NOT signal config. | ⚠️ **DO NOT back this up to the NAS or anywhere shared — it contains live auth tokens (idToken / refreshToken).** It only controls who's logged in, not the rig config. |
| `~/.local/state/radiens/logs/` | gz logs | allegoserver logs | Not config. Big + noisy, exclude from backups. |

**Bottom line on files:** the durable, human-readable, safe-to-copy stuff is the **`~/radix/devices/` maps**. The workspace JSONs exist but are partly opaque protobuf AND (at least the signal one) were not being kept current on this machine. So file-copy is a good *safety net* for the maps, but it is NOT by itself a reliable "restore the whole live setup" mechanism. The reliable mechanism is Allego's own Save/Restore Workspace, described next.

---

## Does Allego have a built-in Save / Load? YES — Save Workspace / Restore Workspace

Straight from the vendor manual (embedded in [[06-references/radiens-software-reference|radiens-software-reference]], **p29–30**):

In the **upper-right of the Allego window** there are three buttons:

- **Save Workspace** (download / down-arrow icon) — "saves the current configuration of your workspace ... preserve the arrangement of tabs and windows ... restore the layout at a later time."
- **Trashcan** — deletes the currently saved workspace and returns the UI to default. (This, or the `~/.config/allego` reset, is how everything got wiped.)
- **Restore Workspace** (circular-arrow icon) — "restores the tabs to their saved locations when you launch Allego ... your preferred layout is automatically applied upon starting the software."

Despite the "tabs and windows" wording, the manual's own **Restore Workspace Feature Retention table (p30)** shows it restores a lot MORE than layout. Here is that table, verbatim, because it's the whole answer:

### What Restore Workspace brings back (manual p30)

| Group | Setting | Retained by Restore? |
|-------|---------|:---:|
| **System** | Mode | ✅ Yes |
| System | **Sample Rate** | ✅ Yes |
| System | **Selected / Deselected Sites** | ❌ **NO** |
| System | Gain | ✅ Yes |
| System | AO Control | ✅ Yes |
| System | Highpass filter | ✅ Yes |
| System | AO 1 / AO 2 mapping | ✅ Yes |
| System | Digital Out Control Mode | ❌ No |
| System | Digital In Triggering State | ✅ Yes |
| System | Digital In Triggering Channel | ✅ Yes |
| **Electrodes** | Headstage Selection | ✅ Yes |
| Electrodes | Probe Selection | ✅ Yes |
| Electrodes | **Site Reordering** | ❌ **NO** |
| **Signal Processing** | **Filters** (incl. our 60 Hz notch) | ✅ Yes |
| **Spike Sorter** | Threshold | ✅ Yes |
| **3D Model** | Stereotactic Coords / Animal Model / Atlas | ❌ No (we don't use these) |

> [!important] The single gap that bites us
> Restore Workspace brings back Mode, Sample Rate, Headstage, Probe, and Filters — that's most of our pain. **The one thing it does NOT restore is "Selected / Deselected Sites"** = our per-port channel tick boxes (`/1-4` + `/33-36`). "Site Reordering" also isn't retained, but we don't reorder. So after a Restore we still must **re-tick the channel selection by hand**. That matches our existing note that "Allego forgets channel-select on every re-enumeration" — turns out it's not just re-enumeration, it's every launch, and it's documented behavior.

Filters ARE retained, which is great because it means our **60 Hz notch** (manual p71–72: Notch filter, default bandwidth 2, so 60 Hz notches 59–61 Hz) comes back automatically once saved. That removes the biggest correctness risk (recording with the wrong notch, the thing that burned weeks — see the 60 Hz mains discovery).

---

## Recommended approach

**Primary: use Allego's built-in Save Workspace / Restore Workspace, plus a file-level backup of the `~/radix/devices/` maps as a safety net, plus re-tick channel selection by hand after each Restore (or via an SDK script once we verify one — see NEEDS TESTING).**

Rationale (weighing the three options):

- **(a) Copy/backup the workspace files and restore them.** Good as a *safety net* for the plain-text `.hstg` / `.prb` maps and to recover from a `~/.config/allego` wipe. But NOT sufficient as the main mechanism: the signal-side JSON has opaque protobuf blobs, and on this machine it was stale (Feb 3, 30 kHz) rather than tracking the live config. Restoring a stale file could quietly set the wrong sample rate. So: back these up, but don't rely on file-restore alone.
- **(b) Built-in Save/Restore Workspace.** This is Allego's supported, documented path and it restores Mode, Sample Rate, Filters, Headstage, Probe, Gain, DI triggering. This is the backbone of the recommendation. Its one weakness is the channel-select gap.
- **(c) Startup script via the Radiens Python SDK.** Attractive for closing the channel-select gap (re-apply `/1-4` + `/33-36` in one command after each launch/re-enumeration), because that's the ONE thing Save/Restore can't do. BUT: I could NOT confirm the SDK exposes site-selection setters on this system — the `radiens` package is not importable from the system Python or the `eeg-analysis-venv` here (the daemon imports it lazily and only ever calls read-only `get_status()`; see `neurosurveillance/backend/radiens_poller.py`). So (c) is the RIGHT long-term answer for the gap but is UNVERIFIED. Do NOT build it until the SDK surface is confirmed. ⚠️ And remember the hard rule: **never call `GetIntanImpedance` (or any impedance call) while streaming — it crashes allegoserver.** A config-apply script must run while paused / not streaming.

So the layered plan: **Save/Restore Workspace = 90% of the setup automatically. Hand re-tick channel selection = the last 10%. File backup of `~/radix/devices/` = insurance. SDK auto-select = future upgrade to kill the last 10%, once verified.**

---

## Procedure — SAVE the setup (do this ONCE, after the rig is fully configured)

Do this while the rig is fully set up the way you want it (correct mode, 1000 S/s, maps loaded, channels selected, 60 Hz notch on). Bare steps, one at a time:

1. In Allego, confirm the current setup is correct: Mode `XDAQ One (G1) with XR Headstage`, Sample Rate `1000`, headstage/probe map loaded, channels `/1-4` + `/33-36` per port ticked, notch = 60 Hz. (Verify against [[signal-mapping-guide]] §1.1 and [[signal-quality-and-grounding]].)

2. Click the **Save Workspace** button — the **download / down-arrow icon** in the **upper-right** of the Allego window.

   Expected: the workspace is now saved; Restore on next launch will pull back everything in the p30 table.

3. Make a file-level backup of the plain-text maps and the workspace JSONs (safety net). From a terminal:

   ```bash
   mkdir -p ~/allego-config-backup/$(date +%F)
   ```

   ```bash
   cp -a ~/radix/devices ~/allego-config-backup/$(date +%F)/devices
   ```

   ```bash
   cp -a ~/radix/workspace ~/allego-config-backup/$(date +%F)/workspace
   ```

   ```bash
   cp -a ~/.config/allego/allego-workspaces.json ~/.config/allego/allego-windows.json ~/allego-config-backup/$(date +%F)/
   ```

   Expected: a dated folder under `~/allego-config-backup/` holding `devices/`, `workspace/`, and the two small UI JSONs. **DO NOT copy `~/.config/radiens/session.json` — it holds live login tokens.**

4. (Optional but recommended) Write down the exact channel-select pattern on paper / in [[signal-mapping-guide]], because that's the one thing Restore won't bring back. For our 8-mouse map that's: `passthrough_64` loaded, then per port select `/1-4` and `/33-36`.

> [!note] NEEDS TESTING — does Save Workspace refresh `ws-default_allego.json`?
> On this machine the signal-side `ws-default_allego.json` was stale (Feb 3, 30 kHz) BEFORE any Save. After clicking Save Workspace, check its timestamp + `samp_freq`:
> ```bash
> ls -l ~/radix/workspace/.system/ws-default_allego.json
> ```
> ```bash
> grep -o '"samp_freq":[0-9]*' ~/radix/workspace/.system/ws-default_allego.json
> ```
> If the timestamp updates to "now" and `samp_freq` becomes 1000, then Save Workspace genuinely writes the live config to disk and our file-backup captures the real setup. If not, the workspace lives somewhere else (possibly inside the allegoserver process / a Radiens cloud profile) and file-backup only protects the maps. EITHER WAY the built-in Restore button is still the mechanism; this test just tells us how much the file-backup is worth.

---

## Procedure — RESTORE the setup (every launch / after re-enumeration)

1. Launch Allego. Let it detect the system. If the headstage re-enumerated, re-confirm the port shows connected in the bottom status bar.

2. Click the **Restore Workspace** button — the **circular-arrow icon**, upper-right.

   Expected (per manual p30): Mode, Sample Rate, Gain, Highpass, **Filters (60 Hz notch)**, Headstage selection, Probe selection, and Digital-In triggering all come back.

3. **Re-tick the channel selection by hand** — this is the ONE thing Restore does NOT bring back. Go to System → Signals, and for each port select `/1-4` and `/33-36` (8-mouse map). Cross-check against [[signal-mapping-guide]] §7 so you don't fall into the "sites vs D/n" trap (wrong tick = Mouse 2 never streams and you record junk silently).

4. Verify before recording:
   - Mode reads `XDAQ One (G1) …` (`priSigs > 0`, not 0).
   - Sample Rate reads `1000`.
   - Notch filter reads **60 Hz** (NOT 50 Hz — the 50 Hz mistake is the one that cost weeks).
   - The expected channels are ticked and streaming looks alive.

5. Only then Stream / Record.

> [!warning] If everything is gone anyway (workspace wiped / `~/.config/allego` reset)
> If Restore does nothing (empty/deleted workspace, or someone hit the Trashcan, or the app profile was reset like on Jul 9), restore the plain-text maps from your backup so at least the headstage/probe maps are present, then rebuild the workspace by hand ONE more time and Save Workspace again:
> ```bash
> cp -a ~/allego-config-backup/<DATE>/devices/. ~/radix/devices/
> ```
> The `.hstg` / `.prb` maps are the tedious-to-recreate part (they come from `csv2sensor`), so this saves the worst of the pain. Then redo mode/rate/filters/channels in the GUI and click Save Workspace.

---

## Open questions — need bench verification against the live Allego GUI

Mark these clearly as UNVERIFIED; I researched from files + the manual only, I did NOT touch the live Allego config (read-only pass):

1. **Does Save Workspace survive a full hardware re-enumeration** (physically unplug/replug the XDAQ, or power-cycle the headstage), not just an app close/reopen? The manual only promises retention "upon starting the software." Our existing hard-won note says re-enumeration resets mode/rate/channel-select. TEST: save, unplug/replug XDAQ, relaunch, hit Restore, see what comes back. This is the single most important test.
2. **Does Save Workspace actually rewrite `ws-default_allego.json`** (the NEEDS TESTING box above)? Determines how much the file-backup is worth.
3. **Is the workspace stored per-OS-user only, or is there a Radiens cloud "User Profile"** tied to the login (the p31 profile panel)? If it's cloud-tied, a fresh login might pull it back — or a `~/.config/allego` reset might not actually lose it. UNKNOWN.
4. **Does the Radiens Python SDK expose a channel-selection setter** (to close the one gap with a startup script)? The `radiens` package isn't importable in the environments on this box, so I couldn't introspect `AllegoClient`. If it does, a tiny "apply-our-config" script run after each launch (while NOT streaming) would fully close the gap. ⚠️ Must avoid any impedance call while streaming (crashes allegoserver).
5. **Does loading a custom sensor / re-applying the headstage map re-tick the last-used sites**, or always clear them? If loading the map re-applies a saved selection, that would sidestep the gap. UNKNOWN — test in the Electrodes tab.
6. **Preset Filters as a second safety net for the notch:** manual p71 shows Preset Filter buttons (SINGLE UNIT / MULTI UNIT / LFP / EEG) per port. Worth checking whether a saved/preset EEG filter set reliably re-applies the 60 Hz notch even without Restore. UNTESTED.
