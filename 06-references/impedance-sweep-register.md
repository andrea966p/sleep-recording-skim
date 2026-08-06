---
tags: [reference, eeg, impedance, electrodes, register]
created: 2026-08-03
status: active
---

# Impedance sweep register

> [!abstract] TL;DR
> Every impedance sweep we have taken, what configuration it was taken in, which
> recording it brackets, and where the file is. Files were renamed on 2026-08-03
> so the name itself carries the date, the time and the context, because the old
> names (`imp_8mice_corrected.csv`, `imp_8mice_channelscorrect.csv`) could not be
> told apart and their meaning lived only in someone's memory.

Files: `~/Downloads/impedance measurments/`, **foldered by date since 2026-08-04**.
Copies are placed in each day folder
under `/home/skimlab/eeg-processed/YYYY-MM-DD/impedance/` by
`pipeline/stage2_split.py`, alongside a parsed `impedance_summary.csv`.

## Naming convention

```
imp_YYYY-MM-DD_HHMM_<configuration>_<context>.csv
     │          │     │               └─ PRE-run1, POST-run2, config-test, ...
     │          │     └─ 8mice-64ch, 4mice-32ch, portB-32ch, ...
     │          └─ time of the sweep
     └─ date of the sweep
```

The date and time come from the **filename**, not the file modification time.
Modification time does not survive copying, syncing or restoring from backup, so
it is not a safe identity. `pipeline/stage2_split.sweep_identity()` parses the
name and falls back to mtime only for unlabelled files.

## The register

| Date | Time | Configuration | Context | Sites read | File |
| --- | --- | --- | --- | --- | --- |
| 2026-07-31 | 16:11 | port B only, 32 ch | B2 alone, after the dual-headstage test | 32 | `imp_2026-07-31_1611_portB-32ch_B2-alone-after-dual.csv` |
| 2026-07-31 | 16:13 | port B only, 32 ch | B1 alone, after the dual-headstage test | 32 | `imp_2026-07-31_1613_portB-32ch_B1-alone-after-dual.csv` |
| 2026-07-31 | 17:20 | — | **ABORTED**, one site only (`B/25`) | 1 | `imp_2026-07-31_1720_ABORTED_1-site-only.csv` |
| **2026-07-31** | **17:34** | **8 mice, 64 ch/port** | ⭐ **PRE-RUN 1** (run started 18:06) | 256 | `imp_2026-07-31_1734_8mice-64ch_PRE-run1.csv` |
| 2026-07-31 | 17:51 | 4 mice, 32 ch/port | config test, splitters removed | 128 | `imp_2026-07-31_1751_4mice-32ch_config-test-nosplitter.csv` |
| **2026-08-02** | **01:44** | **8 mice, 64 ch/port** | ⭐ **PRE-RUN 2** (run started 01:46) | 256 | `imp_2026-08-02_0144_8mice-64ch_PRE-run2.csv` |
| **2026-08-02** | **23:34** | **8 mice, 64 ch/port** | ⭐ **POST-RUN 2** | 256 | `imp_2026-08-02_2334_8mice-64ch_POST-run2.csv` |
| 2026-08-04 | 16:33 | 8 mice, 64 ch/port | after the DMM test and a full restart | 256 | `2026-08-04/imp_2026-08-04_1633_8mice-64ch_post-DMM-restart.csv` |
| 2026-08-04 | 16:40 | D2 alone, port D, 32 ch, no splitter | single animal, lands on `D/1`+`D/2` | 32 | `2026-08-04/imp_2026-08-04_1640_D2-alone-portD-32ch_single-animal.csv` |
| 2026-08-04 | 16:42 | D1 alone, port D, 32 ch, no splitter | single animal | 32 | `2026-08-04/imp_2026-08-04_1642_D1-alone-portD-32ch_single-animal.csv` |
| 2026-08-04 | 16:44 | B1 alone, **port D**, 32 ch, no splitter | port swap control | 32 | `2026-08-04/imp_2026-08-04_1644_B1-alone-portD-32ch_port-swap-control.csv` |
| **2026-08-04** | **16:47** | **B1 alone, port B, 32 ch, no splitter** | ⭐⭐ **MOUSE STILL** | 32 | `2026-08-04/imp_2026-08-04_1647_B1-alone-portB-32ch_MOUSE-STILL.csv` |
| **2026-08-04** | **16:48** | **B1 alone, port B, 32 ch, no splitter** | ⭐⭐ **MOUSE MOVING** | 32 | `2026-08-04/imp_2026-08-04_1648_B1-alone-portB-32ch_MOUSE-MOVING.csv` |
| **2026-08-04** | **16:56** | **8 mice, 64 ch/port** | ⭐⭐ **replication: B1, B2, C1 MOVING, other five STILL. Prediction FAILED, 50% vs 50%** | 256 | `2026-08-04/imp_2026-08-04_1656_8mice-64ch_replication-B1B2C1-moving.csv` |

## ⭐ 2026-08-05, the tether comparison. One row per BLOCK, not per sweep

Sweeps became **automated** on this date (gRPC `GetIntanImpedance`, see [[2026-08-05]]), so
blocks of 20 replaced single sweeps. Duty cycle = fraction of sweeps below 2 MΩ.

| block | window | config | n | `B/1` | `B/2` | `D/1` | `D/2` | folder |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| **arm A** original tether | 16:36:59-16:55:59 | B1 port B + D2 port D, 32 ch/port | 20 | **45%** | **20%** | 40% | 100% | `2026-08-05/armA-original/` |
| **arm B** short soldered | 17:46:17-18:05:17 | same | 20 | **100%** | **75%** | 15% | 95% | `2026-08-05/armB-short-soldered/` |

Fisher exact B against A: `B/1` **p = 0.0001**, `B/2` **p = 0.0006**. Controls did not
improve (`D/1` fell 40% → 15%), excluding session-wide drift.
Full analysis and its limits: [[2026-08-05-tether-comparison]].

One-off sweeps from the same day live in `2026-08-05/00-checks/`: the 8-mouse pre-session
sweep (16:22), the 2-port config check (16:26), the **unipolar LFP reference mouse** (17:23,
see [[2026-08-05-unipolar-lfp-mouse-reference]]) and the post-swap check (17:42).

> [!danger] 🔴 B1 died under isoflurane on 2026-08-05
> Colony is now **n = 7**. Its arm A and arm B blocks stand and are the strongest data in
> this register. **Arm C against arm B, the only comparison that isolated the slip ring,
> is permanently lost.**

> [!warning] A duty cycle and a single sweep are not the same measurement
> Every row above 2026-08-05 is a **single 20 second snapshot** of a contact that flips
> within minutes. Every row from 2026-08-05 onward is a **rate over 20 minutes**. Do not
> put them in the same column and do not compare them directly.

## Folder layout, reorganised 2026-08-04

```
~/Downloads/impedance measurments/
├── RENAME-MANIFEST.csv        every original name → its current path
├── 2026-07-31/                5 sweeps
├── 2026-08-02/                2 sweeps, the two run brackets
├── 2026-08-04/                7 sweeps, the DMM and intermittency session
└── 2026-08-05/                the tether comparison, one subfolder per arm
    ├── armA-original/
    ├── armB-short-soldered/
    └── armC-long-direct-noslipring/   (empty)
```

### 2026-08-06, reorganised the same evening

Numbered **chronologically**. Config string for the whole day is
**`7mice-A2empty-4ports-64ch`** — seven mice, because the **A2 position holds a cut cable with
no animal on it**.

```
└── 2026-08-06/
    ├── README.md                                          channel map, traps, contents
    ├── 01-fleet-census-20sweeps/                11:30-11:41  all 8 positions, duty cycle
    ├── 02-teardown-rungA2-ring+headstage-15sweeps/  12:04-12:11  A2 chain, tether removed
    ├── 03-teardown-rungA1-headstage-only-15sweeps/  12:19-12:27  A2 chain, slip ring also removed
    ├── 04-preswap-D2-baseline-15sweeps/         15:57-16:04  20 min before D2's swap
    ├── 05-armC-D2-longtether-noslipring-40sweeps/  16:27-16:47  arm C, finally run, on D2
    └── 06-single-sweeps/                        one-off readings, NEVER pool these
```

> [!warning] Single sweeps must never sit inside a block folder
> Two loose sweeps were sitting in the arm C folder, so a folder glob scored **41** sweeps
> instead of 40. They now live in `06-single-sweeps/`. A cut tether with no mouse reads below
> 2 MOhm about **22%** of the time, so one sweep cannot classify anything and must never be
> pooled into a duty cycle.

> [!important] ⭐ The floor control is free and is in every sweep ever taken
> Each mouse uses only 2 of its chip's 16 amplifier inputs, so **`/3`-`/16` and `/35`-`/48` are
> real amplifier inputs with no wire attached** — 112 per sweep. They are the null distribution:
> **21.4% of them pass 2 MOhm, 3.1% pass 0.5 MOhm**, and one reached **0.051 MOhm**.
> ❌ **Never include `/17`-`/32` or `/49`-`/64`** — inactive slots, internally tied, they read low
> almost always and would destroy the control.
> ⇒ **The connected criterion is now |Z| < 0.5 MOhm**, not 2 MOhm. Re-score old blocks before
> quoting them. See [[2026-08-06-fleet-duty-cycle-census]].

> [!important] 2026-08-05 onward, a block of sweeps is one register row, not twenty
> The tether comparison fires ~20 sweeps per arm because the primary outcome is a **duty
> cycle**, not a reading. Register the **arm**: its clock window, its configuration, how
> many sweeps it fired and the duty cycle per channel. Listing every individual file would
> bury the register in rows that individually mean nothing.
> Design: [[2026-08-05-tether-comparison]].

All 14 sweeps now follow `imp_YYYY-MM-DD_HHMM_<config>_<context>.csv`, so
`sweep_identity()` reads date, time and label from the **name** for every file
with no mtime fallback anywhere. Times in the table above are the real file
times, not estimates.

> [!note] The pipeline glob was made recursive on the same day
> `pipeline/stage2_split.py` used to glob `IMP_DIR/*.csv`, which the date folders
> would have broken. It now globs `IMP_DIR/**/*.csv` with `recursive=True`, which
> also still matches any flat file. Verified after the move: all 14 sweeps are
> discovered and all 14 resolve their identity from the filename.

> [!warning] A sweep name is a claim about what was measured
> The 16:47 and 16:48 files carry `MOUSE-STILL` and `MOUSE-MOVING` in their names.
> Those labels were assigned **by eye at the bench**, not scored from video. Treat
> them as the experimenter's note, not as an instrument reading.

`RENAME-MANIFEST.csv` sits beside the files and records every original name, so
the rename is reversible and older notes referring to the old names can still be
resolved.

> [!warning] The 17:51 sweep is NOT the pre-run-1 sweep
> It was taken 15 minutes before Run 1 but in a **different configuration**: 32
> channels per port, splitters removed, 4 mice. Run 1 itself ran at 64 channels
> per port with 8 mice. The sweep that matches the run configuration is the
> **17:34** one. Using the 17:51 file as "the pre-run sweep" would compare
> impedances measured through a different signal path.

## What the three run-bracketing sweeps show

Reading only `/1`, `/2` (slot 1) and `/33`, `/34` (slot 2), because those are the
only wired amplifiers. See [[CANONICAL-allego-channel-selection]].

| Mouse | | PRE-run1 | PRE-run2 | POST-run2 |
| --- | --- | --- | --- | --- |
| A1 | EEG | 6.757 | 4.446 | 8.284 |
| A1 | EMG | **0.087** | **0.087** | **0.073** |
| A2 | EEG | 7.644 | 5.962 | 6.917 |
| A2 | EMG | 5.849 | 4.851 | **1.746** |
| B1 | EEG | **1.717** | **0.133** | **0.732** |
| B1 | EMG | 5.465 | 7.099 | 6.375 |
| B2 | EEG | 7.110 | 5.771 | 7.336 |
| B2 | EMG | 5.663 | 6.287 | 2.695 |
| **C1** | **EEG** | **0.465** | 5.720 | 7.929 |
| **C1** | **EMG** | **0.190** | **0.051** | **0.270** |
| C2 | EEG | 4.418 | **1.146** | 2.507 |
| C2 | EMG | **0.139** | **0.168** | **0.111** |
| D1 | EEG | 6.300 | 3.980 | 7.504 |
| D1 | EMG | **0.335** | **0.202** | **0.279** |
| D2 | EEG | **0.660** | 2.114 | 9.200 |
| D2 | EMG | **0.286** | **0.023** | **1.273** |

Bold = below the 2 MΩ open-circuit threshold. Values in MΩ at 1 kHz.

**Across Run 2 the EEG got worse on 8 of 8 animals and better on none**, while
EMG went 3 better, 3 unchanged, 2 worse. Full analysis:
[[2026-08-03-two-8-mouse-runs]].

> [!danger] ⭐⭐ Read this before drawing ANY trend from the table above
> **Overturned 2026-08-04.** These numbers do not measure electrode condition.
> They are **snapshots of a contact that flips within minutes**: B1's EEG read
> **0.052, 8.649, 6.236 and 0.177 MΩ in a single afternoon**. A movement
> explanation was proposed and **failed its same-day replication**, so the trigger
> is still unknown. Each sweep takes about **20 seconds**.
> See [[2026-08-04-movement-dependent-contact]].
>
> Consequences for this register:
> - **The "8 of 8 EEG got worse across Run 2" trend is not a degradation trend.**
>   Post-run sweeps were taken with animals awake and active.
> - **A single sweep cannot classify a channel.** Comparing two sweeps of the same
>   channel taken on different days compares two postures, not two conditions.
> - The channel-to-channel *ranking* within one sweep is equally unsafe, because
>   the eight animals were not all moving at the same instant.
>
> The register is still worth keeping, as a record of what was measured and when.
> It is no longer evidence about electrodes.

## The 2026-08-04 8-mouse sweep, and why the numbers churn

| Mouse | | PRE-run1 | PRE-run2 | POST-run2 | 2026-08-04 |
| --- | --- | --- | --- | --- | --- |
| A1 | EEG | 6.757 | 4.446 | 8.284 | 6.078 |
| A1 | EMG | **0.087** | **0.087** | **0.073** | **0.252** |
| A2 | EEG | 7.644 | 5.962 | 6.917 | **1.966** |
| A2 | EMG | 5.849 | 4.851 | **1.746** | 8.195 |
| B1 | EEG | **1.717** | **0.133** | **0.732** | 6.236 |
| B1 | EMG | 5.465 | 7.099 | 6.375 | 6.660 |
| B2 | EEG | 7.110 | 5.771 | 7.336 | **0.879** |
| B2 | EMG | 5.663 | 6.287 | 2.695 | 7.765 |
| C1 | EEG | **0.465** | 5.720 | 7.929 | 4.323 |
| C1 | EMG | **0.190** | **0.051** | **0.270** | **0.323** |
| C2 | EEG | 4.418 | **1.146** | 2.507 | 5.137 |
| C2 | EMG | **0.139** | **0.168** | **0.111** | **0.318** |
| D1 | EEG | 6.300 | 3.980 | 7.504 | **1.172** |
| D1 | EMG | **0.335** | **0.202** | **0.279** | 8.203 |
| D2 | EEG | **0.660** | 2.114 | 9.200 | **0.352** |
| D2 | EMG | **0.286** | **0.023** | **1.273** | **0.233** |

Count below 1 MΩ: **7 → 6 → 5 → 6 of 16**. Flat. But the **membership changes
almost completely** between sweeps.

- Connected in all four sweeps: **A1 EMG, C1 EMG, C2 EMG.** Three channels.
- The other 13 flip. Volatility as max/min across the four sweeps: **D2 EMG 55×,
  B1 EEG 47×, D1 EMG 41×, D2 EEG 26×, C1 EEG 17×.**

Channels do not drift. **They flip.** That is the fingerprint of a mechanical
contact, and 2026-08-04 identified the variable that flips them.

## ⭐ The 2026-08-04 session, in order, and what each sweep was for

Seven sweeps in 23 minutes. Read top to bottom, this is the day's whole argument.

| # | time | what | result | what it established |
| --- | --- | --- | --- | --- |
| 1 | **16:33** | 8 mice, after the DMM test and a full restart | 6 of 16 connected | **D2 recovered** (EEG 9.200 → 0.352). **D1 EMG apparently dead** (0.279 → 8.203). **B1 EEG apparently dead** (0.732 → 6.236). Membership churned, count did not |
| 2 | **16:40** | **D2 alone**, port D | `D/1` 0.459 @ 2.5°, `D/2` 0.270 @ 178.5° | D2's recovery is real, not a splitter artefact. Confirms the clean streaming signal |
| 3 | **16:42** | **D1 alone**, port D | `D/1` 7.444, `D/2` **0.688** | **D1's EMG never broke.** 8.203 at 16:33, 0.688 nine minutes later. First hard proof the flipping is fast and reversible |
| 4 | **16:44** | **B1 alone in port D** | `D/1` 0.873, `D/2` 0.325 | B1 works in a **different port** ⇒ port, splitter and XDAQ path exonerated. This discharges step 2 of the §6 ladder in [[dmm-eeg-path-continuity-test]] |
| 5 | **16:47** | **B1 alone, port B, MOUSE STILL** | `B/1` **0.052 @ 179.7°** | ⭐ **Best impedance ever recorded on this rig**, EEG or EMG, and inside the published 10 to 50 kΩ band. **The electrode and the implant are good.** |
| 6 | **16:48** | **B1 alone, port B, MOUSE MOVING** | `B/1` **8.649 @ 54.6°** | 166× against sweep 5, one minute apart. Generated the movement hypothesis |
| 7 | **16:56** | 8 mice, **B1 B2 C1 moving, five still** | moved 3/6, still 5/10 connected | ⚠️ **Replication FAILED.** 50% against 50%. **B1 moving read 0.177 CONNECTED**, contradicting sweep 6 in the same animal |

### B1's EEG on one afternoon

| 16:33 | 16:47 | 16:48 | 16:56 |
| --- | --- | --- | --- |
| 6.236 (8 mice) | **0.052** (alone, still) | 8.649 (alone, moving) | **0.177** (8 mice, moving) |

**Four values spanning 166×, in 23 minutes, on one electrode.** This single row is
the strongest evidence in the register: no fixed property of an electrode can
produce it, and no single sweep can characterise it.

### What the day settled, and what it did not

| ✅ Established | ❌ Not established |
| --- | --- |
| The **electrodes and implants are good** (0.052 MΩ) | **What triggers the flip** |
| The contact is **intermittent, fast and reversible**, both directions, within minutes | That **movement** is the trigger. Tested, and it failed |
| A single sweep **cannot rank, screen or classify** a channel | Whether the slip ring is involved. Untested under load |
| **Port, splitter and XDAQ** are not the variable (sweep 4) | Whether implantation depth contributes |
| **Boards, pads and solder** are clean, fleet wide ([[dmm-eeg-path-continuity-test]]) | |

> [!important] A sweep takes about 20 seconds
> Measured at the bench on 2026-08-04. This matters for interpreting sweep 7: the
> animal's state held for the whole measurement, so the failed replication cannot
> be explained away as a sweep averaging over mixed postures. It was a clean test
> with a clean null.
>
> It also means an unpaired comparison across 8 animals at a ~50% base rate has
> very little power. Sweep 7 is **weak evidence against** the movement hypothesis.
> What actually damages the hypothesis is **B1 contradicting itself** between
> sweeps 6 and 7.

> [!note] D1's EMG never broke
> It reads 8.203 MΩ in the 2026-08-04 8-mouse sweep, which looked like a working
> control channel dying during the DMM work. Measured alone an hour later it
> reads **0.688 MΩ**. Nothing broke. The animal moved.

## Three things to remember when reading any of these numbers

1. **Only one electrode of each pair is measured.** The RHD2216 is bipolar, and
   the chip's `Zcheck pol sel` register selects which input is tested, but
   Radiens exposes no way to reach it. By chip default we get the positive input,
   so "the EEG impedance" is the **frontal** electrode and the parietal one has
   never been measured. See [[electrode-connection-state-test]]. **Open Ephys
   does not fix this either** — see the section below.
2. **`Z < 2 MΩ` means "not open", not "good".** Published epidural electrodes sit
   at 10–50 kΩ; our best channel in the whole fleet is 73 kΩ.
   See [[electrode-failure-and-impedance-literature]].
3. **Impedance predicts class, not yield.** It tells you which channel may work,
   never for how long. B1 read 0.133 MΩ before Run 2, the best in the fleet, then
   ran fully open for 21.7 hours. **As of 2026-08-04 we know why**: the sweep
   caught a good posture and the run caught the animal moving.
4. ⭐ **A sweep is a 20 second snapshot of a flipping contact, not of hardware.**
   Two sweeps of the same channel on different days compare two moments, not two
   conditions. Record what the animal was doing anyway, so the correlate can be
   found later.
5. **`Z < 2 MΩ` no longer means the electrode is mediocre.** B1 EEG reads
   **0.052 MΩ** when the animal is still, which is in the published 10 to 50 kΩ
   band. Our electrodes are good. Our contact is intermittent.

> [!note] The mouse label on single-port sweeps is the PORT, not the animal
> In the 16:11 and 16:13 sweeps a single animal was moved onto port B, so both
> files report their readings under the label `B1` (derived from port + site).
> The animal identity is in the filename, not the label. Trust the filename.

## ❌ Can the Open Ephys GUI measure each electrode separately? No, not as shipped

**Asked and answered 2026-08-03, by inspecting the installed plugin binary.**

The hope was that the Open Ephys GUI, being open source, might expose the
`Zcheck pol sel` register that Radiens hides, and so finally measure the
**negative** electrode of each bipolar pair. It does not.

### What was checked

`~/.config/open-ephys/plugins-api10/XDAQ-OE.so`, the XDAQ-OE v0.4.4 plugin that
is actually installed and working on this machine ([[openephys-gui-setup-xdaq-sleep-eeg]]).

The plugin embeds Intan's `Rhd2000Registers` class, and the polarity setter **is
compiled in**:

```
_ZN16Rhd2000Registers17setZcheckPolarityENS_14ZcheckPolarityE   @ 0x7a420
```

But it is **never called**. Counting call sites in the disassembly:

| register setter | call sites in the shipped plugin |
| --- | --- |
| `setZcheckScale` | 3 |
| `setZcheckChannel` | 1 |
| `enableZcheck` | 1 |
| `setZcheckDacPower` | 0 |
| **`setZcheckPolarity`** | **0** |

The other three setters *are* called out of line from the impedance path, so the
absence of a call to the polarity setter is meaningful and not an inlining
artefact. The function is dead code, carried along because
`Rhd2000Registers.cpp` is compiled whole.

Result: the plugin leaves `Zcheck pol sel` at its power-on default and measures
**the same pin Radiens measures**. Confirmed by the shape of its own export,
`~/Downloads/OE imp with mouse split ground` — exactly **one** magnitude and
phase per amplifier, with no polarity dimension anywhere:

```xml
<CHANNEL name="CH1" number="0" magnitude="585478.75" phase="-61.93849945068359"/>
<CHANNEL name="CH2" number="1" magnitude="2.090344875e6" phase="1.613905072212219"/>
```

> [!important] Switching acquisition software does not buy you this measurement
> Allego and the Open Ephys XDAQ plugin are equally blind to the negative
> electrode. This is a **software** gap in both, not a chip limitation: the
> RHD2216 can test either pin, and that register bit exists precisely for
> bipolar chips.

### What actually would work, cheapest first

1. **Multimeter on each C3410 pad against the GND pad. Free, today, and it sees
   both sides.** It is a DC continuity check rather than a 1 kHz impedance, so
   the number is not comparable to a sweep, but the question we need answered is
   "is this electrode connected at all", and that it answers. This remains the
   recommended next step. See [[multimeter-guide]].
2. **Patch the plugin.** Open Ephys and the XDAQ plugin are open source. The
   change is small: run the existing measurement pass twice, calling
   `setZcheckPolarity(ZcheckNegativeInput)` before the second, and emit a second
   value per amplifier. The cost is not the code, it is building and installing
   an unofficial plugin on a live production rig, and then owning it at every
   upgrade.
3. **Ask Kontex for it.** This is a small, concrete, well-specified feature
   request against a plugin they maintain, and there is an open thread already.
   Cheapest path to a *supported* fix. Vendor thread:
   `01-infrastructure/vendor-correspondence/`.

> [!quote] Paper-ready
> Impedance was measured at the positive input of each bipolar amplifier;
> neither acquisition package exposes the chip register that selects the
> negative input, so the second electrode of each pair was verified by direct
> continuity measurement rather than by impedance sweep.
