---
tags: [procedure, allego, radiens, electrode-setup, sleep64, onboarding, sop]
created: 2026-07-13
status: complete
---

# Allego Electrode Setup — the `sleep64` map (READ THIS, ignore the rest)

> [!success] ⭐ Channel selection is settled — see [[CANONICAL-allego-channel-selection]]
> **Select `/1`, `/2`, `/33`, `/34` per port. 16 channels for 8 mice.**
> `/1`=EEG and `/2`=EMG are ALREADY bipolar — never subtract them.
> Proven 2026-08-03 from the datasheet, the recorded metadata, and a
> measurement of all 64 slots on all four ports. **If anything below
> disagrees with that page, that page is right.**


> [!tip] THE WHOLE THING ON ONE CARD
> In Allego, **Electrodes tab**, for EVERY port that has mice:
> - **Headstage:** `usrdef_sleep64`
> - **Probe:** `usrdef_sleep64_probe`
>
> Then select these channels to record, per port:
> - **Mouse A → channels 1, 2, 3, 4**
> - **Mouse B → channels 33, 34, 35, 36**
>
> That's it. If you see channels 1-8 instead of 33-36, you loaded the WRONG map, switch back to `usrdef_sleep64`.

> [!note] RECONCILED 2026-07-31 — `Passthrough 64` is EQUALLY correct, the two procedures never actually disagreed
> This page used to say "do NOT pick any other headstage or probe", which conflicted with [[eight-mouse-acquisition-setup]] telling you to use the built-in `Passthrough 64` + `Default 8x8`. I diffed the files on 2026-07-31: `hstg__usrdef_sleep64.hstg` and `hstg__passthrough_64.hstg` contain **the exact same 64 native to site pairs**, both pure passthrough where site = native + 1. The md5 sums differ ONLY because passthrough writes floats (`0.0`) and sleep64 writes ints (`0`).
>
> **Either choice is correct and the recorded data is identical.** The original warning was aimed at the ARCHIVED repacking maps (`usrdef_2mice32`, `usrdef_dual_mouse_c3442`, etc), which really do renumber channels. It was never about `Passthrough 64`.
>
> **Practical advice:** the built-ins need no "Use local devices" tick and cannot go missing from the dropdown, so they have one less failure mode. Use `Passthrough 64` + `Default 8x8` unless you specifically want the custom map.
>
> **With ONE headstage per port and NO splitter** (port reports 32 ch, not 64), the equivalent is **`Passthrough 32` + `Default 4x8`**, verified pure passthrough and confirmed as what Allego selects by itself in that configuration.
>
> See [[2026-07-31-contact-intermittency-no-wire-control]] §9.

## Why this exists
We made a pile of custom maps during setup (`2mice32`, `single_mouse`, `mouse_4ch`, `dual_mouse_c3442`…). They REPACK the channel numbers in confusing ways (e.g. Mouse B shows up as 5-8 instead of 33-36), and Allego does NOT auto-pick a matching probe, so everyone guessed. That's fixed now. There is ONE map to use: **`sleep64`**. The confusing old ones are archived (see bottom).

## Our wiring (so the numbers make sense)
- One mouse per headstage. Each headstage plugs into an **SPI splitter**, so **2 mice share one XDAQ port**.
- `sleep64` is a plain **passthrough** map: site number = native channel + 1. So on each port:
  - **Mouse A** = first headstage = native 0,1,2,3 = **channels 1,2,3,4**
  - **Mouse B** = second headstage = native 32,33,34,35 = **channels 33,34,35,36**

> [!danger] ⚠️ CORRECTED 2026-08-01 — the per-channel table below is WRONG
> The RHD2216 is BIPOLAR, so each channel already reports the difference of its own `+`/`−` pins. The 4 mouse wires land on **two** channels, not four:
> - **`/1` (mouse A) or `/33` (mouse B) = EEG**, frontal vs parietal, already bipolar
> - **`/2` or `/34` = EMG**, neck pair, already bipolar
> - **`/3`, `/4`, `/35`, `/36` = EMPTY PADS, no wire by design**
>
> Do NOT subtract `/1 − /2` — that computes EEG minus EMG. See [[2026-08-01-channel-mapping-correction-first-sleep]].

### What each channel is (per mouse) — ⚠️ SUPERSEDED, see box above
| Channel (Mouse A / Mouse B) | Signal |
| --- | --- |
| 1 / 33 | EEG (frontal) |
| 2 / 34 | EEG (parietal) |
| 3 / 35 | EMG |
| 4 / 36 | EMG |

> [!note] EEG is the bipolar pair (ch1 & ch2), EMG is the bipolar pair (ch3 & ch4). Confirm exact per-pin meaning against the wiring sheet in [[signal-mapping-guide]] if in doubt, that guide is the source of truth for real-world ↔ channel.

## Step-by-step in Allego
1. Open the **Electrodes tab** (Radiens manual p60).
2. For each active port (A, B, C, D…):
   - Headstage dropdown → **`usrdef_sleep64`**
   - Probe dropdown → **`usrdef_sleep64_probe`**
3. Go to **Signal Map** and add the **Data Channel Index** + **Site Number** columns (COLUMNS button). CONFIRM:
   - Data Channel Index `0` → Site Number `1`  (Mouse A, ch 1)
   - Data Channel Index `32` → Site Number `33` (Mouse B, ch 33)
   - No row shows `Site Number -23` / "no-site". If it does, the map didn't load, reselect `usrdef_sleep64`.
4. In channel selection, tick **1,2,3,4,33,34,35,36** for each port (the 8 real electrodes for the 2 mice). The rest are empty/parked.

> [!warning] Allego forgets channel selection on every hardware re-enumeration
> Mode, sample rate, and filters can be brought back with **Restore Workspace**, but the CHANNEL SELECTION (the 1-4 / 33-36 ticks) is NOT retained, that's a documented Allego gap. After any unplug/replug or re-enumeration you must re-tick them. Full save/restore story: [[allego-settings-save-restore]].

## What NOT to do
- Do NOT use `usrdef_dual_mouse_c3442` or any archived `usrdef_*` map, they repack the numbers and confuse everyone.
- Do NOT pick a geometric NeuroNexus probe (`a8x32…`, `sinaps…`, `default_8x8`…). Those describe real silicon-probe geometry we don't have. `sleep64`'s probe is just a cosmetic layout, the numbers come from the headstage.
- The probe picture looks like a plain grid with 8 dots clustered and the rest tucked below, that's NORMAL and correct.

## If `sleep64` ever disappears (rebuild it)
The map is generated from two CSVs in the vault with NeuroNexus's `csv2sensor` tool, so it's fully reproducible:
- Source CSVs: `06-references/neuronexus/sensor-maps/sleep64.csv` (headstage) + `sleep64_probe.csv` (probe)
- Tool: `06-references/neuronexus/sensor-maps/csv2sensor-linux-x86_64`
- Rebuild:
```bash
cd ~/Monitoring_project/Monitoring_project_obsidian_vault/06-references/neuronexus/sensor-maps
./csv2sensor-linux-x86_64 -type headstage -out-dir ~/radix/devices sleep64.csv
./csv2sensor-linux-x86_64 -type probe    -out-dir ~/radix/devices sleep64_probe.csv
```
Output lands in `~/radix/devices/` as `hstg__usrdef_sleep64.hstg` + `probe__usrdef_sleep64_probe.prb`.

## Cleanup done 2026-07-13
ALL old custom maps archived to `~/radix/devices/_archive_old_maps/` (reversible, and regenerable from the CSVs in the vault): `usrdef_2mice32`, `usrdef_mouse1`, `usrdef_single_mouse`, `usrdef_mouse_4ch`, and `usrdef_dual_mouse_c3442` (headstage + probe each). `~/radix/devices/` now holds exactly ONE custom map, **`sleep64`**, plus the stock NeuroNexus built-ins. Confirmed `usrdef_sleep64` loaded and streaming on the ports before archiving c3442.

## Related
- [[signal-mapping-guide]] — the deep reference (3 numbering systems, csv2sensor, real-world ↔ channel)
- [[radiens-software-reference]] — Electrodes tab p60, Signal Map p37, channel select p38
- [[allego-settings-save-restore]] — save/restore the rest of the config (mode, rate, filters)
- [[signal-quality-and-grounding]] — is the signal good enough to record
