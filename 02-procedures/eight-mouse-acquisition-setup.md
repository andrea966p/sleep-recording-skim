---
tags: [procedure, radiens, allego, signal-mapping, headstage, eeg, emg, eight-mouse, c3442]
created: 2026-07-04
status: active
---

# 8-Mouse Acquisition Setup — Signal Map + Sensor Files + Channel Selection

> [!abstract] What this is
> Everything ready to **plug in 8 mice and start recording**: the definitive signal map (which Allego channel is which mouse/electrode), the pre-built Allego **headstage + probe** files, the grounding rule, and the exact channel selection to click. Beginner, step-by-step. Builds on [[signal-mapping-guide]] (the concepts) and [[signal-quality-and-grounding]] (grounding/quality). Validated topology from [[2026-07-01]] + [[2026-07-03]].

---

## 0. The topology in one picture

**8 mice = 8 headstages = 4 XDAQ ports × 2 headstages/port (via C3442 dual-headstage adapter).**

```
XDAQ (bottom SPI socket each port — top is DEAD)
  Port A ── C3442 ──┬── HS-A (RHD2216) → Mouse 1   natives 0–3   (A/1–A/4)
                    └── HS-B (RHD2216) → Mouse 2   natives 32–35 (A/33–A/36)
  Port B ── C3442 ──┬── HS-A → Mouse 3   B/1–B/4
                    └── HS-B → Mouse 4   B/33–B/36
  Port C ── C3442 ──┬── HS-A → Mouse 5   C/1–C/4
                    └── HS-B → Mouse 6   C/33–C/36
  Port D ── C3442 ──┬── HS-A → Mouse 7   D/1–D/4
                    └── HS-B → Mouse 8   D/33–D/36
```

> [!important] The key number from the stress test ([[2026-07-03]])
> With a C3442, **each port enumerates as 64 channels** — HS-A = natives **0–31**, HS-B = natives **32–63**. Proof: Mouse-2's EEG-P showed up as **`A/34`** (= native 33) last run. So the second headstage on a port does **NOT** start at native 16 — it starts at **native 32**. Every mouse still only uses its own board's **pads 0–3**.

Each mouse uses **4 electrodes on C3410 pads 0,1,2,3**, plus a **ground** on the board `GND` bus. `REF` stays empty (RHD2216 is bipolar). We ignore pads 4/6 for now (per operator: pads 0–3 only).

---

## 1. Per-mouse electrode map (same on every C3410 board)

| C3410 pad | Slip-ring colour | Electrode | Bipolar role |
|---|---|---|---|
| **pad 0** | red | EEG frontal (EEG-F) | **EEG +** |
| **pad 1** | black | EEG parietal (EEG-P) | **EEG −** |
| **pad 2** | yellow | EMG left | **EMG +** |
| **pad 3** | blue | EMG right | **EMG −** |
| `GND` bus | green | parietal-R dura | **animal ground** (not recorded) |
| `REF` | — | — | **empty, leave unconnected** |

- **EEG signal = pad 0 − pad 1** (frontal − parietal).
- **EMG signal = pad 2 − pad 3** (left − right).
- Ground green wire → the board's `GND` bus (its own per mouse — see §4).

---

## 2. ⭐ Master signal map — all 8 mice

`native` = the headstage channel (files store this as `pri_N`). `Allego label` = what you see on the chip (`Port/n` = native + 1). `site` = the tidy number after loading the custom sensor (§3).

| Mouse | Port / HS | Signal | pad | native | **Allego label** | **site** |
|---|---|---|---|---|---|---|
| **M1** | A / HS-A | EEG+ | 0 | 0  | **A/1**  | 1 |
| M1 | A / HS-A | EEG− | 1 | 1  | A/2  | 2 |
| M1 | A / HS-A | EMG+ | 2 | 2  | A/3  | 3 |
| M1 | A / HS-A | EMG− | 3 | 3  | A/4  | 4 |
| **M2** | A / HS-B | EEG+ | 0 | 32 | **A/33** | 5 |
| M2 | A / HS-B | EEG− | 1 | 33 | A/34 | 6 |
| M2 | A / HS-B | EMG+ | 2 | 34 | A/35 | 7 |
| M2 | A / HS-B | EMG− | 3 | 35 | A/36 | 8 |
| **M3** | B / HS-A | EEG+…EMG− | 0–3 | 0–3   | **B/1–B/4**  | 1–4 |
| **M4** | B / HS-B | EEG+…EMG− | 0–3 | 32–35 | **B/33–B/36** | 5–8 |
| **M5** | C / HS-A | EEG+…EMG− | 0–3 | 0–3   | **C/1–C/4**  | 1–4 |
| **M6** | C / HS-B | EEG+…EMG− | 0–3 | 32–35 | **C/33–C/36** | 5–8 |
| **M7** | D / HS-A | EEG+…EMG− | 0–3 | 0–3   | **D/1–D/4**  | 1–4 |
| **M8** | D / HS-B | EEG+…EMG− | 0–3 | 32–35 | **D/33–D/36** | 5–8 |

**Total recorded = 8 mice × 4 = 32 channels.**

> [!note] Offline decode (analysis)
> Allego records **all** primary channels of every enumerated port, not just the selected ones (selection is display/QC only). In `get_signals` / the `.xdat` file the rows are per-port blocks of 64: **Port A = rows 0–63, B = 64–127, C = 128–191, D = 192–255**. Each mouse's 4 channels are at offset **0–3** (HS-A) or **32–35** (HS-B) inside its port block. The analysis channel-name map needs an 8-mouse version before scoring (TODO — the old `2mice32` decode map is deprecated).

---

## 3. Allego sensor files (already built — ready to load)

One custom sensor covers a **whole C3442 port** (2 mice, 64 ch). **Load the same file on all 4 ports.** It puts the 8 used channels on tidy **sites 1–8** and parks the rest.

**Files (already generated into `/home/skimlab/radix/devices/`):**
- Headstage: `hstg__usrdef_dual_mouse_c3442.hstg`
- Probe: `probe__usrdef_dual_mouse_c3442_probe.prb`

Source CSVs + generator in the vault: `06-references/neuronexus/sensor-maps/dual_mouse_c3442.csv`, `..._probe.csv`, `gen_dual_mouse.py`. To rebuild: `./csv2sensor-linux-x86_64 -type headstage dual_mouse_c3442.csv` (and `-type probe ..._probe.csv`).

Site layout inside the file:
- sites **1,2,3,4** = HS-A mouse EEG+, EEG−, EMG+, EMG− (natives 0,1,2,3)
- sites **5,6,7,8** = HS-B mouse EEG+, EEG−, EMG+, EMG− (natives 32,33,34,35)
- sites 9–64 = parked unused channels

---

## 4. Grounding — 8 independent grounds (one per mouse)

> [!important] C3442 keeps grounds separate — do NOT bus mice together
> Two headstages on a C3442 = **two separate C3410 boards = two independent animal grounds** (the good topology from [[2026-07-01]] §7). This is NOT the old shared-ground 2-mice-per-headstage setup. **Each mouse's green → its OWN board's `GND` bus.** Never tie two mice's grounds together.

Per mouse, before streaming:
1. Green (animal ground) → that mouse's C3410 `GND` bus (via its brass busbar star node if used).
2. **DMM continuity** green wire → `GND` pad = ~0 Ω.
3. `REF` empty.
4. After the map loads and you stream, confirm that headstage's **floor channels are quiet** (~4–25 µV): HS-A floor = natives 16–31, HS-B floor = natives 48–63. Quiet floor ⇒ grounded; all-railing ⇒ that mouse floats (ground not made).

---

## 5. Physical connect order (do this at the rig)

1. **Power/enumeration:** each port's C3442 on the **bottom** SPI socket (top is dead). 4 ports = 4 C3442.
2. Two RHD2216 headstages per C3442 (left/right), one mouse each.
3. **Allego Mode = `XDAQ One (G1) with XR Headstage`**, sample rate **1000**. (Allego forgets these on every re-enumeration — re-set every time.)
4. Confirm each port shows **64 ch** (not 0, not 32). 0 = not detected (check bottom socket / mode); 32 = only one headstage seen on that port.
5. Ground each mouse (§4), DMM-verify.

---

## 6. Load sensor + select channels in Allego

**Load (Electrodes tab) — repeat for each port A, B, C, D:**
1. Electrodes tab → **Port = A**.
2. Tick **"Use local devices"** (un-tick/re-tick if the file isn't listed).
3. Headstage dropdown → **`Usrdef dual_mouse_c3442`**.
4. Probe dropdown → **`Usrdef-dual_mouse_c3442-Probe`**.
5. **Apply.** Wireframe redraws as two clusters (left = HS-A mouse, right = HS-B mouse).
6. Repeat for Port B, C, D (same two files).

**Select channels (System tab → Signals) — per port:**
- On each port row, **DESELECT ALL**, then tick **sites 1–8**. That's both mice on that port.
- Do all 4 ports → **32 channels selected total** (8 mice).

> [!warning] The sites-vs-labels trap (read this)
> With the custom sensor loaded, chips are labeled by **site number**. Ticking **sites 1–8 is CORRECT** (= natives 0,1,2,3,32,33,34,35). Do NOT tick "1,2,3,4,33,34,35,36" as raw labels here — after the map loads those digits mean sites, and sites 9+ are the parked junk. **Just pick the contiguous block sites 1–8 per port.**

---

## 7. Verify before recording (per mouse, 2-min check)

1. **Signal Map** (System tab): used channels show real Headstage/Probe, **no `−23` / no-site**. Native 0–3 → sites 1–4; native 32–35 → sites 5–8.
2. **Floor quiet** = grounded (§4.4).
3. **Tap test:** nudge a mouse's EMG lead → its EMG site (3 or 7) jumps. Wrong site jumps ⇒ wiring ≠ map, fix the sheet.
4. **Signal Metrics:** background RMS tens of µV = good; thousands of µV = floating/open. Railing wired channel = **open electrode contact** (surgical/contact issue, not the rig).
5. **Bipolar pair check:** EEG = site1−site2 (or 5−6), EMG = site3−site4 (or 7−8). A scoreable mouse needs a clean EEG pair **and** a working EMG pair.

Record only mice that pass. A single clean leg is not scoreable.

---

## 8. Known gotchas (from prior runs)

- **Bottom SPI socket only** — top socket dead on both HDMI adapters ([[2026-07-01]] §2).
- Allego **forgets mode + 1000 S/s + channel selection on every re-enumeration** — re-set each time.
- **Never** run SDK `GetIntanImpedance` while streaming (crashes allegoserver). Impedance only via GUI, paused.
- Backend crashes under rapid sensor-reload/channel-select churn → apply once, let it settle; if it spams garbage "notifications", restart Allego and re-set mode/electrodes/channels.
- Recording stores **all** port primaries (256 ch across 4 ports) — the file is big; decode the 32 real channels offline via §2.

---

## Related
- [[signal-mapping-guide]] — the mapping concepts (native / `D/n` / site, csv2sensor, tap test)
- [[signal-quality-and-grounding]] — grounding + is-the-signal-good-enough
- [[2026-07-01]] — dual-headstage validated, one-mouse-per-headstage, bottom-socket rule
- [[2026-07-03]] — overnight stress test (C3442, 64 ch/port, `A/34` proof)
- [[2026-07-02-eeg-recording-checkpoint]] — the scale-to-8 plan
