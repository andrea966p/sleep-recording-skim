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

Files: `~/Downloads/impedance measurments/`. Copies are placed in each day folder
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
   ran fully open for 21.7 hours.

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
