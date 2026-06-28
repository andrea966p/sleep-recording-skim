---
tags:
  - procedure
  - radiens
  - allego
  - signal-mapping
  - headstage
  - eeg
  - emg
  - onboarding
created: 2026-06-19
status: complete
---

# Signal Mapping Guide — Telling Allego Which Channel Is Which Electrode

> [!abstract] TL;DR — for non-technical readers
> **What this is.** A plain-language, click-by-click guide to **signal mapping**: teaching the recording software (Allego) which of its numbered channels corresponds to which real electrode on which mouse, and what each one is (EEG or EMG).
>
> **Why it exists.** When you plug a headstage in, Allego just sees anonymous channels called `pri_0, pri_1, …`. It has **no idea** that channel 0 is "Mouse 1's EEG" — *you* have to tell it (or write it down). Get this wrong and your brain-wave trace is silently labelled as a muscle trace. Every person running an animal must do this for their own wiring.
>
> **How to read this page.** Read "The idea" once. Then follow the steps in order. A worked example (2 mice on one headstage) runs through the whole guide so each abstract step has a concrete version next to it. Software reference: [[radiens-software-reference]]. First-rig story: [[first-headstage-connection]].

---

## 0. The idea, in one picture

Signal travels from the animal to the software through a chain of physical parts. Each part renames the signal. **Signal mapping = keeping track of that renaming end to end.**

```
   MOUSE                    CABLES & BOARDS                       SOFTWARE
 ┌────────┐   tether    ┌──────────┐  headstage   ┌──────┐      ┌─────────┐
 │electrode│──wires────►│ adapter  │──pads────────►│ RHD  │─SPI─►│ XDAQ +  │──► Allego
 │(EEG/EMG)│ (colored)  │ board    │ (solder)     │ chip │ cable│ adapter │     channels
 └────────┘  slip-ring  │ (C3410)  │              └──────┘      └─────────┘   pri_0…pri_N
```

| Real-world thing | What it is | Becomes, in Allego… |
|---|---|---|
| **Electrode** (skull screw / wire in muscle) | Picks up the actual EEG or EMG voltage | one **channel** |
| **Tether** | The bundle of thin coloured wires from the animal | (the colours are your map key) |
| **Slip-ring** | Rotating connector so the animal can turn without twisting wires | (pass-through, no renumbering) |
| **Adapter board** (Intan **C3410**) | Small PCB where each electrode wire is **soldered to a numbered pad/hole** | sets which **headstage channel** an electrode lands on |
| **Headstage** (Intan **RHD2216 / XR**) | The amplifier chip; has **native channels** numbered `0 … N-1` | `pri_0 … pri_(N-1)` |
| **SPI cable / HDMI adapter / XDAQ** | Carry the digitised signal to the computer | (pass-through, no renumbering) |
| **Allego** | The recording software | shows channels as **`D/1, D/2 …`** and stores them as `pri_N` |

> [!important] The single most important fact
> **A "channel" is just a number until you label it.** Allego will happily record `pri_5` without knowing it is "Mouse 1 EMG−". The mapping lives in **your wiring sheet** and (optionally) in a **custom sensor file** you load into Allego. If you skip this, the data is not wrong — it's just **unlabelled**, and only you can decode it later.

---

## 1. Three numbering systems you must not confuse

This trips everyone up. There are **three** ways the same channel gets numbered:

| Name | Counts from | Where you see it | Example |
|---|---|---|---|
| **Native channel** (`ntv_chan`) | **0** | Headstage "as labelled", CSV files, Signal Map "Data Channel Index" | `0, 1, 2 … 31` |
| **Allego channel** (`D/n`) | **1** | System tab, Monitor, channel-select chips | `D/1, D/2 … D/32` |
| **Site number** | **1** | Probe geometry, Signal Map "Site Number" | `1, 2 … 32` |

**The golden rule:**

> **`D/n`  =  native channel `n − 1`.**
> So `D/1` = native `0` = `pri_0`. `D/9` = native `8` = `pri_8`.

The **site number** is whatever *you* decide when you build a custom map (see §5). Without a custom map, site number just equals native+1.

---

## 1.1 The master decoder — one row, all three numbers (our 2-mice rig)

> [!important] If you read one table, read this one
> Every real wire has **four** different numbers (board pad, native channel, Allego `D/n`, site number) plus its meaning. The confusion is that they don't line up — `D/n` skips, sites are repacked. This table puts all four side by side so you never have to convert in your head. **It is the single source of truth for our wiring.**

| Signal | C3410 **pad** | **native** `pri_N` | Allego **`D/n`** | **site #** | record it? |
|---|---|---|---|---|---|
| M1 EEG+ | pad 0 | `pri_0` | **D/1** | **1** | ✅ |
| M1 EEG− | pad 1 | `pri_1` | **D/2** | **2** | ✅ |
| M1 EMG+ | pad 2 | `pri_2` | **D/3** | **3** | ✅ |
| M1 EMG− | pad 3 | `pri_3` | **D/4** | **4** | ✅ |
| **M1 ground** (green) | **pad 5** | `pri_5` | D/6 | 10 | ❌ — should be on the **`GND`** pad, not a signal pad |
| M2 EEG+ | pad 8 | `pri_8` | **D/9** | **5** | ✅ |
| M2 EEG− | pad 9 | `pri_9` | **D/10** | **6** | ✅ |
| M2 EMG+ | pad 10 | `pri_10` | **D/11** | **7** | ✅ |
| M2 EMG− | pad 11 | `pri_11` | **D/12** | **8** | ✅ |
| **M2 ground** (green) | **pad 13** | `pri_13` | D/14 | 14 | ❌ — should be on the **`GND`** pad, not a signal pad |

> [!warning] This table = the OLD 2-mice (`2mice32`) layout. Current standard = single-mouse 8-channel slip-ring.
> Since 2026-06-27 the standard rig is **one mouse, 8-pin slip-ring socket** with a different pad map. Current scheme (slip-ring colour → pad): pad 0 red EEG-F_L, 1 black EEG-P_L, 2 yellow EMG-L, 3 blue EMG-R, **pad 4 brown = dura frontal-R** (recorded), **pad 5 purple = nothing** (spare line, deselect), **pad 6 orange = copper/env-ref**, **`GND` bus = green = dura parietal-R animal ground** (not a signal pad). `REF` empty (bipolar). Note pad 5 here ≠ an M1 ground. Full definitive map lives in [[grounding-reference-noise-concepts]] §2. Use that for the single-mouse rig; this table only for the legacy 2-mice setup.

**Three rules that remove all confusion:**
1. **pad = native.** The C3410 hole `N` solders straight to headstage channel `N` (identity). Pad 0 → `pri_0`.
2. **`D/n` = native + 1.** Allego's on-screen label is 1-indexed. `pri_3` shows as `D/4`.
3. **site = the custom remap.** `csv2sensor` packs the 8 real wires into a clean block **sites 1–8** (M1 = 1–4, M2 = 5–8) so the System tab shows them contiguous. That's the whole point of the custom map.

> [!warning] The "1–8" trap — sites 1–8 ≠ D/1–D/8
> With the custom map loaded, the channel-select chips are labeled by **site number**, so ticking **sites 1–8 is CORRECT** (both mice). But "1–8" in *raw* `D/n` terms (`D/1…D/8`) is **WRONG** — that's native 0–7 = Mouse 1 + four parked junk channels, and **Mouse 2 never streams**. Same digits, different channels.
>
> | You tick "1–8" as… | Native channels | Result |
> |---|---|---|
> | **site numbers** (custom map loaded) | 0,1,2,3,8,9,10,11 | ✅ both mice |
> | **`D/n` channels** (raw) | 0,1,2,3,4,5,6,7 | ❌ M1 + junk, no M2 |
>
> Correct selection expressed either way: **sites 1–8**, or equivalently **`D/1,D/2,D/3,D/4,D/9,D/10,D/11,D/12`**. Both name the same 8 channels.

---

## 2. Before you start (prerequisites)

1. **Headstage is detected.** In Allego's **System** tab, your port (usually **Port D**) shows a channel count (e.g. `32`), not `0`. If it shows `0`, fix detection first — see [[first-headstage-connection]] (most common cause: wrong **Mode** — it must be **"XDAQ One (G1) with XR Headstage"**, not "SmartBox Pro").

![[sigmap-fig0-mode-dropdown.png]]
*Figure 0 — The **Mode** dropdown (top of System tab). For our XDAQ Core Gen-1 + XR headstage the correct entry is **"XDAQ One (G1) with XR Headstage"** (highlighted). Sample Rate beside it should read **30000**.*

> [!warning] "One" vs "Core" naming trap
> Our hardware chassis is badged **XDAQ Core**, but the **mode that actually detects the headstage is "XDAQ One (G1) with XR Headstage"** — *not* "XDAQ Core (G1)…", even though that also exists in the list. Pick the mode that **detects** (channel count > 0 / `priSigs > 0`), not the one whose name matches the chassis label. `XSR` = a different headstage type; we use **`XR`**.
2. **You are streaming** (click **STREAM**, not **RECORD** — `RECORD` starts a real session + video).
3. **You have your wiring sheet** — the piece of paper (or PDF) that says which electrode wire went to which pad. You cannot map without it. If you don't have one, make one *before* you ever put the animal on (you can't recover it afterwards).

---

## 3. Step A — Write the real-world map (your source of truth)

For **each** electrode, fill one row. Do this from your wiring sheet / soldering notes, **not** from memory.

| Mouse | Signal | Tether colour | Slip-ring colour | Board pad (C3410 hole) | Headstage native ch |
|---|---|---|---|---|---|
| 1 | EEG + | Red | Red | 0 | 0 |
| 1 | EEG − | Black | Black | 1 | 1 |
| 1 | EMG + | Yellow | Yellow | 2 | 2 |
| 1 | EMG − | Blue | Orange | 3 | 3 |
| 2 | EEG + | Red | Red | 8 | 8 |
| 2 | EEG − | Black | Black | 9 | 9 |
| 2 | EMG + | Yellow | Yellow | 10 | 10 |
| 2 | EMG − | Blue | Orange | 11 | 11 |

> [!example] Worked example — what this means in real life
> Two mice share **one** 32-channel headstage. Mouse 1's four electrodes are soldered to board pads **0–3**; Mouse 2's to pads **8–11**. Pads 4–7 and 12–31 are empty (not wired). Each mouse gives **two signals**: **EEG** (brain) and **EMG** (muscle), and each signal is a **bipolar pair** — a `+` wire and a `−` wire, because the real signal is the *difference* between them.

**Notes that matter:**
- **EEG = brain waves** (sleep staging). **EMG = neck-muscle activity** (movement / REM atonia). You usually record both per animal.
- **Bipolar pair:** EEG = (EEG+ − EEG−). The two wires are useless alone; keep the pair together.
- **Ground / reference wire** (often green): this is *not* a recorded signal — it's the common zero. It connects to the headstage ground; you do **not** select it as a data channel.

---

## 4. Step B — Translate your table into Allego channels

Apply the golden rule (`D/n = native + 1`) to the last column of your Step-A table:

| Mouse | Signal | Native ch | **Allego `D/n`** |
|---|---|---|---|
| 1 | EEG + | 0 | **D/1** |
| 1 | EEG − | 1 | **D/2** |
| 1 | EMG + | 2 | **D/3** |
| 1 | EMG − | 3 | **D/4** |
| 2 | EEG + | 8 | **D/9** |
| 2 | EEG − | 9 | **D/10** |
| 2 | EMG + | 10 | **D/11** |
| 2 | EMG − | 11 | **D/12** |

→ The **8 channels you will record** are `D/1, D/2, D/3, D/4, D/9, D/10, D/11, D/12`.

---

## 5. Step C — Choose: quick map or custom map

Allego **cannot type a name like "EEG" onto a channel** (the Signal Map table is read-only, and the data files are stored by native channel `pri_N`). You have two honest options:

| | **Quick (passthrough)** | **Custom sensor (recommended for shared rigs)** |
|---|---|---|
| What you do | Keep the default map; just **select** your channels and rely on your Step-A table for meaning | Build a small file (with `csv2sensor`) that gives your channels tidy **site numbers** and a **layout grouped by mouse/signal** |
| Channel names in Allego | `pri_0 …` (anonymous) | still `pri_N`, **but** the Signal Map + wireframe picture now reflect *your* layout |
| Best for | A quick test, one operator | Multiple people, real experiments, fewer mistakes |
| Effort | None | ~5 minutes, reusable |

If you pick **Quick**, skip to **§7 (Select channels)**. If you pick **Custom**, do §6 first.

---

## 6. Step D — Build a custom sensor with `csv2sensor`

`csv2sensor` is a small NeuroNexus command-line tool that turns two CSV tables into the files Allego loads:
- a **headstage file** (`.hstg`) = "native channel → site number"
- a **probe file** (`.prb`) = "where each site sits" (the picture)

Tool + our example CSVs live in the vault: `06-references/neuronexus/sensor-maps/`.

### 6.1 Make the headstage CSV

> [!warning] The #1 mistake — you must list ALL native channels
> The tool decides the headstage size from the **number of rows**, and the native numbers must run **0, 1, 2 … up to size−1**. If you only list your 8 used channels (and they include high numbers like 8–11), Allego marks everything `Site Number −23` / **"no-site"** and nothing maps.
> **Always list every native channel of the headstage** (all 32 for a 32-channel headstage). Put your used ones on the low site numbers; park the unused ones on the high site numbers.

`2mice32.csv` (first column = native channel, second = site number):

```csv
ntv_chan, site_num
0, 1      # M1 EEG+
1, 2      # M1 EEG-
2, 3      # M1 EMG+
3, 4      # M1 EMG-
8, 5      # M2 EEG+
9, 6      # M2 EEG-
10, 7     # M2 EMG+
11, 8     # M2 EMG-
4, 9      # unused, parked
5, 10     # unused, parked
...       # every remaining native channel up to 31, parked on sites 11..32
```

(Our generator script fills the "parked" rows automatically. You only care about the first 8.)

### 6.2 Make the probe CSV (the picture)

One row per **site**. `center_x` / `center_y` are positions in microns — use them to **group** sites so the picture is readable: put Mouse 1's four sites in one cluster and Mouse 2's in another.

```csv
site_num, center_x, center_y, radius, shape
1, 0,   0,  6, circle    # M1 EEG+   ┐ Mouse 1
2, 0,   25, 6, circle    # M1 EEG-   │ cluster
3, 60,  0,  6, circle    # M1 EMG+   │ (left)
4, 60,  25, 6, circle    # M1 EMG-   ┘
5, 200, 0,  6, circle    # M2 EEG+   ┐ Mouse 2
6, 200, 25, 6, circle    # M2 EEG-   │ cluster
7, 260, 0,  6, circle    # M2 EMG+   │ (right)
8, 260, 25, 6, circle    # M2 EMG-   ┘
...                       # sites 9..32 parked off to one side
```

### 6.3 Generate the files

```bash
cd 06-references/neuronexus/sensor-maps      # (in the vault folder)
./csv2sensor-linux-x86_64 -type headstage 2mice32.csv
./csv2sensor-linux-x86_64 -type probe    2mice32_probe.csv
```

Output (named `usrdef_<your-csv-name>`) lands in **`/home/skimlab/radix/devices/`** — the folder Allego reads:
- `hstg__usrdef_2mice32.hstg`
- `probe__usrdef_2mice32_probe.prb`

---

## 7. Step E — Load and select in Allego

### 7.1 Load the sensor (Electrodes tab)
1. Open the **Electrodes** tab (left menu → *Electrodes*).
2. Set **Port** = **D** (or whichever port your headstage is on).
3. Tick **"Use local devices"** — this makes your custom files appear. *If your new file isn't in the list, un-tick and re-tick to force a re-scan; restart Allego only as a last resort.*
4. **Headstage** dropdown → choose your headstage file (e.g. `Usrdef 2mice32`).
5. **Probe** dropdown → choose your probe file (e.g. `Usrdef-2mice32-Probe`).
6. Click **Apply**. The wireframe picture should redraw as your layout (two clusters, one per mouse).

![[sigmap-fig2-headstage-dropdown.png]]
*Figure 1 — Electrodes tab, Headstage dropdown open with **"Use local devices"** ticked (blue check). Your custom files (e.g. `Usrdef mouse1`) appear alongside the built-in `Passthrough …` entries. Pick yours here, then pick the matching Probe.*

![[sigmap-fig3-electrodes-loaded.png]]
*Figure 2 — After **Apply** with the 2-mice sensor loaded: Headstage = `Usrdef 2mice`, Probe = `Usrdef-2mice-Probe`. The wireframe (bottom) now shows two clusters — the left filled cluster is Mouse 1's selected sites, the right outlined cluster is Mouse 2. This visual grouping is the payoff of a custom map.*

*(Quick-map users: skip loading; leave Headstage = `Passthrough 32`, Probe = `Default-4x8`.)*

### 7.2 Select the channels you actually record (System tab)
1. Open the **System** tab → **Signals** section.
2. On your port's row (**Port D**), use **`Select More`** to tick **only your used channels**: `D/1, D/2, D/3, D/4, D/9, D/10, D/11, D/12`.
3. Use **`DESELECT ALL`** first if it's easier, then add back the 8.
4. Do **not** select the ground/reference channels or unused pads.

You should end with **8 selected channels** (4 per mouse).

> [!warning] Sites vs. channel numbers — easy mistake after loading a custom map
> Once a **custom sensor** (e.g. `2mice32`) is loaded, the channel chips are labeled by **site number**, not the headstage's native number. So Mouse 2 is on **sites 5,6,7,8** — **not** 9–12 (sites 9+ are the unused/parked channels). Select the contiguous block **sites 1–8** to get both mice. Picking `1,2,3,4,9,10,11,12` (the plain-passthrough habit) records Mouse 1 + junk and **Mouse 2 never streams**. Full cross-reference of pad ↔ native ↔ `D/n` ↔ site is in **§1.1 (master decoder)**; also note **sites 1–8 ≠ `D/1–D/8`** (§1.1 trap box). See [[signal-quality-and-grounding]] §1.

![[sigmap-fig1-channel-select.png]]
*Figure 3 — System tab → Signals → Port D. Each chip (`D/1, D/2 …`) is one channel; the `×` removes it. The drop-down checklist (**Select More**) is where you tick exactly the channels you use. Remember `D/1` = native `0` = your first electrode. Here Port D has 32 available channels; you keep only the 8 wired ones.*

---

## 8. Step F — Verify (do not skip)

### 8.1 Check the map on screen
Click **Signal Map** (top of the System tab). Add the **Site Number** and **Data Channel Index** columns if hidden (the **COLUMNS** button). Confirm:
- Data Channel Index `0,1,2,3` → Site Number `1,2,3,4`
- Data Channel Index `8,9,10,11` → Site Number `5,6,7,8`
- **No row shows `−23` / "no-site"** for your used channels, and Headstage/Probe columns are filled in.

![[sigmap-fig4b-signalmap-2mice32-ok.png]]
*Figure 4 — The **final 2-mice map, verified**. "Data Channel Index" = native channel (from 0); "Site Number" = your logical site; "Channel Name" = `pri_N` (how the data file stores it). Read the mapping: native **0,1,2,3 → sites 1,2,3,4** (Mouse 1 EEG±/EMG±) and native **8,9,10,11 → sites 5,6,7,8** (Mouse 2 EEG±/EMG±). The "parked" unused channels (4,5,6,7 → sites 9,10,11,12 …) sit on the high site numbers. Every row has a real Headstage (`hstg__usrdef_2mice32`) + Probe — no `−23`. **This is what "mapped correctly" looks like.***

![[sigmap-fig4-signal-map-table.png]]
*Figure 4b — Earlier single-mouse test (`mouse1`) for comparison: only native 0–3 are defined here.*

If you see `−23`, your headstage CSV didn't list all native channels — go back to §6.1.

![[sigmap-fig5-signalmap-nosite.png]]
*Figure 5 — The **failure** to recognise: rows 4–31 show **Site Number `−23`** with blank Headstage/Probe = "no-site" (unmapped). In this shot only natives 0–3 were defined, so everything else is unmapped. If you see `−23` on channels you expect to use, your headstage file is missing native channels (§6.1, "map ALL native channels").*

### 8.2 Confirm the wiring physically (the "tap test")
The software map only matches reality if the **soldering** matches your sheet. Prove it:
1. Watch the **Monitor** tab for a known channel (e.g. Mouse 1 EMG, `D/3`).
2. **Gently move/tap that electrode** (or lightly touch the EMG lead).
3. The trace on **that** channel should jump. If a *different* channel jumps, your physical wiring differs from your table — trust the tap test and fix the table.

> [!note] Signal quality this round
> If the **ground/reference is not yet connected**, expect every channel to look noisy or railed (big 50 Hz hum). That is normal and does **not** mean the mapping is wrong. Mapping is about *identity* (which channel is which); cleanliness comes from grounding.

---

## 9. Doing a second animal / re-using the pattern

Because both mice share **one** headstage, there is **one** sensor file covering both — you do **not** load a second file per mouse. The second mouse is just the **same four-site pattern** (EEG pair + EMG pair) mapped to its own native channels (8–11) and drawn in a second cluster. To add more animals/channels, extend the same two CSVs and regenerate.

---

## 10. Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| Every channel shows **Site Number −23 / no-site** | Headstage CSV didn't list **all** native channels (or used non-contiguous low numbers) | List all 32 natives; used → low sites, unused → high sites (§6.1) |
| Your new sensor **isn't in the dropdown** | Allego cached the device list | Un-tick / re-tick **"Use local devices"**; or restart Allego |
| Port shows **0 channels** | Headstage not detected | Check **Mode** = "XDAQ One (G1) with XR Headstage"; see [[first-headstage-connection]] |
| Wrong channel jumps in the **tap test** | Physical solder ≠ your table | Re-check soldering; correct the Step-A table to match reality |
| Channels look like pure noise/hum | Ground/reference not connected | Connect ground; mapping is still fine |
| You want literal "EEG"/"EMG" text labels | Allego can't do that | Keep the meaning in your wiring sheet / analysis script; sensor files only give site numbers + geometry |
| Allego suddenly spams **dozens of "notifications"** full of code/gibberish (random dates like 1970, 5897) | The Radiens **backend (allegoserver) crashed** and dumped its stack trace into the notification area — seen after heavy/rapid sensor reloads + channel select/deselect | It's software, not your hardware/wiring (sensor files on disk are safe). **Restart Allego**, then re-set Mode + Electrodes + channel selection and STREAM. The session daemon re-pairs automatically. Avoid rapid-fire reloading sensors; apply once and let it settle. |

---

## 11. Glossary (real world ↔ software)

| Term | Plain meaning |
|---|---|
| **Headstage** | The amplifier chip you plug the animal into (Intan RHD). Has *native channels*. |
| **Adapter / electrode board (C3410)** | Small PCB where electrode wires are soldered to numbered pads → decides which headstage channel an electrode uses. |
| **Tether** | The thin coloured wires running from the animal. |
| **Slip-ring** | Rotating joint so the animal can turn freely; doesn't change channel numbers. |
| **Pin / pad / hole** | The solder point on the board for one wire. |
| **EEG** | Brain electrical activity (sleep staging). |
| **EMG** | Muscle electrical activity (movement / REM). |
| **Bipolar pair (+ / −)** | Two wires whose *difference* is the real signal. |
| **Ground / reference** | The common zero wire; connected, but not recorded as data. |
| **Native channel (`ntv_chan`, `pri_N`)** | The headstage's own channel number, counting from 0. How data files are stored. |
| **`D/n`** | How Allego labels the same channel on screen, counting from 1 (`D/n` = native `n−1`). |
| **Site number** | A logical "this is electrode position X" label you assign in a custom map. |
| **Headstage file (`.hstg`)** | Tells Allego: native channel → site number. |
| **Probe file (`.prb`)** | Tells Allego: where each site sits (the picture). |
| **`csv2sensor`** | NeuroNexus tool that builds `.hstg` + `.prb` from CSV tables. |
| **Signal Map** | Allego's read-only table showing the full native → site → port routing. |

---

## Related
- [[signal-quality-and-grounding]] — next step after mapping: grounding + judging if the signal is good enough to record
- [[radiens-software-reference]] — main Allego/Radiens software reference (embeds the full manual; `csv2sensor` section)
- [[first-headstage-connection]] — first-rig bring-up + our exact channel map (§8.1)
- [[radiens-api-reference]] — the Python SDK (read-only `get_channel_metadata` etc.)
- Source files: `06-references/neuronexus/sensor-maps/` (`csv2sensor` tool + our CSVs)
