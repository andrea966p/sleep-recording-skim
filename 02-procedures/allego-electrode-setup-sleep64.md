---
tags: [procedure, allego, radiens, electrode-setup, sleep64, onboarding, sop]
created: 2026-07-13
status: complete
---

# Allego Electrode Setup — the `sleep64` map (READ THIS, ignore the rest)

> [!tip] THE WHOLE THING ON ONE CARD
> In Allego, **Electrodes tab**, for EVERY port that has mice:
> - **Headstage:** `usrdef_sleep64`
> - **Probe:** `usrdef_sleep64_probe`
>
> Then select these channels to record, per port:
> - **Mouse A → channels 1, 2, 3, 4**
> - **Mouse B → channels 33, 34, 35, 36**
>
> That's it. Do NOT pick any other headstage or probe. If you see channels 1-8 instead of 33-36, you loaded the WRONG map, switch back to `usrdef_sleep64`.

## Why this exists
We made a pile of custom maps during setup (`2mice32`, `single_mouse`, `mouse_4ch`, `dual_mouse_c3442`…). They REPACK the channel numbers in confusing ways (e.g. Mouse B shows up as 5-8 instead of 33-36), and Allego does NOT auto-pick a matching probe, so everyone guessed. That's fixed now. There is ONE map to use: **`sleep64`**. The confusing old ones are archived (see bottom).

## Our wiring (so the numbers make sense)
- One mouse per headstage. Each headstage plugs into an **SPI splitter**, so **2 mice share one XDAQ port**.
- `sleep64` is a plain **passthrough** map: site number = native channel + 1. So on each port:
  - **Mouse A** = first headstage = native 0,1,2,3 = **channels 1,2,3,4**
  - **Mouse B** = second headstage = native 32,33,34,35 = **channels 33,34,35,36**

### What each channel is (per mouse)
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
Archived (moved to `~/radix/devices/_archive_old_maps/`, reversible, and regenerable from CSVs): `usrdef_2mice32`, `usrdef_mouse1`, `usrdef_single_mouse`, `usrdef_mouse_4ch` (headstage + probe each). `usrdef_dual_mouse_c3442` was still LOADED at cleanup time, so it's left in place, once `sleep64` is confirmed working it can be archived too.

## Related
- [[signal-mapping-guide]] — the deep reference (3 numbering systems, csv2sensor, real-world ↔ channel)
- [[radiens-software-reference]] — Electrodes tab p60, Signal Map p37, channel select p38
- [[allego-settings-save-restore]] — save/restore the rest of the config (mode, rate, filters)
- [[signal-quality-and-grounding]] — is the signal good enough to record
