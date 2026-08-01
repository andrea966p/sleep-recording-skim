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

> [!danger] ⚠️ CORRECTED 2026-08-01 — pads are NOT channels. Two pads make ONE channel.
> The table above is correct about the WIRING, and it contains the answer we missed for weeks. The RHD2216 is **bipolar**, so its `+` and `−` columns are the two pins of a **single amplifier channel**:
>
> | C3410 pads | amplifier channel | Allego site (mouse A / B) | signal |
> | --- | --- | --- | --- |
> | pad 0 (`EEG +`) + pad 1 (`EEG −`) | **native 0** | **`/1` / `/33`** | **EEG, already bipolar** |
> | pad 2 (`EMG +`) + pad 3 (`EMG −`) | **native 1** | **`/2` / `/34`** | **EMG, already bipolar** |
> | — | natives 2, 3 | `/3`,`/4` / `/35`,`/36` | **EMPTY PADS, no wire** |
>
> **4 pads → 2 channels, NOT 4 channels.** The subtraction happens INSIDE THE CHIP. Do not subtract again in software.
>
> ```
> EEG = native0 = /1     (do NOT compute /1 − /2)
> EMG = native1 = /2
> ```
> See [[2026-08-01-channel-mapping-correction-first-sleep]].

- ~~**EEG signal = pad 0 − pad 1** (frontal − parietal)~~ → **done in hardware; read `native0` = `/1` directly.**
- ~~**EMG signal = pad 2 − pad 3** (left − right)~~ → **done in hardware; read `native1` = `/2` directly.**
- Ground green wire → the board's `GND` bus (its own per mouse — see §4).

---

## 2. ⭐ Master signal map — all 8 mice

`native` = the headstage channel (files store this as `pri_N`). `Allego label` = what you see on the chip (`Port/n` = native + 1). **Use passthrough — no custom sensor (see §3); the label IS native+1.**

> [!danger] The 2nd headstage sits at native +32, NOT +16 or +28 — verified live 2026-07-04
> With a C3442, each port = 64 ch: HS-A real = natives **0–3** (pads 0–3), HS-B real = natives **32–35** (pads 0–3). Natives **16–31 and 48–63 are the empty second-MISO floor slots** (quiet ~40 µV). Live proof (2026-07-04): on passthrough ports the 2nd-mouse channels `pri_(base+32..35)` read railing/signal (real), while `pri_28–31` read quiet floor (empty). **Select `/33,/34,/35,/36` for the 2nd mouse — never `/29–/32`.**

| Mouse | Port / HS | pad→signal | native | **Allego label (select these)** |
|---|---|---|---|---|
| **M1** | A / HS-A | 0,1,2,3 = EEG+,EEG−,EMG+,EMG− | 0–3   | **A/1, A/2, A/3, A/4** |
| **M2** | A / HS-B | 0,1,2,3 = EEG+,EEG−,EMG+,EMG− | 32–35 | **A/33, A/34, A/35, A/36** |
| **M3** | B / HS-A | 0–3 | 0–3   | **B/1–B/4** |
| **M4** | B / HS-B | 0–3 | 32–35 | **B/33–B/36** |
| **M5** | C / HS-A | 0–3 | 0–3   | **C/1–C/4** |
| **M6** | C / HS-B | 0–3 | 32–35 | **C/33–C/36** |
| **M7** | D / HS-A | 0–3 | 0–3   | **D/1–D/4** |
| **M8** | D / HS-B | 0–3 | 32–35 | **D/33–D/36** |

~~**Total recorded = 8 mice × 4 = 32 channels.**~~

> [!danger] ⚠️ CORRECTED 2026-08-01 — it is 2 channels per mouse, not 4
> **Total = 8 mice × 2 = 16 channels. Per port: `/1, /2` + `/33, /34`.**
> The "pad→signal" column in the table above should read **`0,1 → EEG (native 0)` and `2,3 → EMG (native 1)`**. The `/3, /4, /35, /36` entries are EMPTY PADS. On 2026-07-31 they were measured and reported as 24 failed EMG surgeries; they never had a wire on them. See [[2026-08-01-channel-mapping-correction-first-sleep]].

> [!note] Offline decode (analysis)
> Allego records **all** primary channels of every enumerated port, not just the selected ones (selection is display/QC only). In `get_signals` / the `.xdat` file the rows are per-port blocks of 64: **Port A = rows 0–63, B = 64–127, C = 128–191, D = 192–255**. Each mouse's 4 channels are at offset **0–3** (HS-A) or **32–35** (HS-B) inside its port block. The analysis channel-name map needs an 8-mouse version before scoring (TODO — the old `2mice32` decode map is deprecated).

---

## 3. Use PASSTHROUGH — no custom sensor

> [!warning] Custom `dual_mouse_c3442` sensor DEPRECATED 2026-07-04 — do NOT load it
> A custom sensor was built first, but it **relabels channels by site number** and that collided with the natural per-port layout: picking "sites 33–36" landed on natives **28–31 (empty floor)** instead of the 2nd mouse at natives 32–35. It caused a wrong Port-A selection on the first real 8-mouse setup. For only 4 channels per headstage a custom map buys nothing and adds a trap. **Use the built-in passthrough** so the on-screen label = native + 1 on every port.

Per port, in the **Electrodes** tab:
- Headstage = **`Passthrough 64`**
- Probe = **`Default 8x8`**
- Apply. (Same on all 4 ports.)

The label you see is then simply `Port/(native+1)`, so the §2 table's "Allego label" column is exactly what you tick. The dead `hstg__usrdef_dual_mouse_c3442.*` files can be left in `/home/skimlab/radix/devices/` (ignored) or deleted.

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

## 6. Set passthrough + select channels in Allego

**Electrodes tab — each port A, B, C, D:** Headstage = `Passthrough 64`, Probe = `Default 8x8`, Apply. (No "Use local devices" / custom file.)

> [!note] RECONCILED 2026-07-31 — this and [[allego-electrode-setup-sleep64]] give the SAME result
> [[allego-electrode-setup-sleep64]] tells you to use `usrdef_sleep64` + `usrdef_sleep64_probe` and says not to pick anything else. Both pages are right. The two headstage files contain **the exact same 64 native to site pairs**, both pure passthrough (site = native + 1); the md5 differs only because one writes floats and the other ints. Either choice records identical data. Details in [[2026-07-31-contact-intermittency-no-wire-control]] §9.
>
> **No splitter, one headstage per port** (port reports 32 ch): use **`Passthrough 32` + `Default 4x8`**, and select only `/1, /2, /3, /4` per port. The second mouse's `/33-/36` range does not exist in that configuration, and a headstage plugged straight into the port lands on natives 0-3 whichever animal it was before.

> [!danger] ⚠️ CORRECTED 2026-08-01 — you only need `/1, /2` and `/33, /34`
> The RHD2216 is BIPOLAR. **`/1` is already the EEG** (frontal vs parietal on its `+`/`−` pins) and **`/2` is already the EMG**. **`/3`, `/4`, `/35`, `/36` are EMPTY PADS with no wire on them.** Selecting them records nothing and — as happened on 2026-07-31 — invites reading empty pads as failed EMG surgeries.
>
> **Select `/1, /2, /33, /34` per port = 16 channels for 8 mice.** The `+32` trap below is still correct for finding the second mouse. See [[2026-08-01-channel-mapping-correction-first-sleep]].

**Select channels (System tab → Signals) — per port:**
- On each port row, **DESELECT ALL**, then tick: **`/1, /2, /3, /4`** (HS-A mouse) **+ `/33, /34, /35, /36`** (HS-B mouse).
- Do all 4 ports → **32 channels total** (8 mice).

> [!warning] The +32 trap (read this)
> The 2nd mouse on each port is at label **`/33–/36`** (native 32–35), **not `/29–/32`**. `/17–/32` are HS-A's empty floor. If you tick `/29,/30,/31,/32` you record **empty channels** and the 2nd mouse is missing. Always `/33,/34,/35,/36` for the second mouse. (This is exactly the mistake that happened on Port A the first time — see [[2026-07-04]].)

---

## 7. Verify before recording (per mouse, 2-min check)

1. **Signal Map** (System tab): every selected channel has a real Headstage/Probe (passthrough), no blanks.
2. **Floor quiet** = grounded (§4.4): HS-A floor natives 16–31, HS-B floor 48–63 read ~5–40 µV.
3. **Tap test:** nudge a mouse's EMG lead → its EMG channel (`/3` or `/35`) jumps. Wrong channel jumps ⇒ wiring ≠ map.
4. **Signal Metrics:** background RMS tens of µV = good; ~thousands of µV (railing) = **open electrode contact**. ⚠️ **CORRECTED 2026-07-31: this is NOT necessarily surgical.** On 2026-07-31, 22 of 32 legs matched a no-wire open-circuit control, and contact state was observed FLIPPING SPONTANEOUSLY (522× in 0.5 s, 102× in 11 minutes). "Open" means "not connected right now", and the break can be anywhere from the implant to the headstage pad. **DO NOT conclude bad surgery from a railing channel.** See [[electrode-connection-state-test]] and [[2026-07-31-contact-intermittency-no-wire-control]].
5. **Bipolar pair check:** EEG = `/1`−`/2` (or `/33`−`/34`); EMG = `/3`−`/4` (or `/35`−`/36`). A scoreable mouse needs a clean EEG pair **and** a working EMG pair.

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
