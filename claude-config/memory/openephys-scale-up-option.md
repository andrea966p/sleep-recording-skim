---
name: openephys-scale-up-option
description: "Open Ephys Acquisition Board as a 3rd 16-mouse DAQ path — open hardware, free software; REPLY 2026-07-23: extension board DEAD, 16 = 4 boards or custom Atlanta build"
metadata: 
  node_type: memory
  type: project
  originSessionId: dfe12453-7955-4bc1-a2fe-bdca0e0878a9
  modified: 2026-07-23T04:39:16.039Z
---

Third candidate for the 16(→32)-mouse rig, alongside XDAQ ONE+ and Intan RHD Recording Controller 1024. See [[acquisition-device-16-32-mice]].

**Open Ephys Acquisition Board (3rd gen):** open-source hardware, runs the SAME Intan RHD chips we own. **8 headstages max today** (4 ports × 2 via dual adapter), 512ch — identical MISO ceiling to our XDAQ Core. Out of the box does NOT reach 16.

**Path to 16 = the `extension-board`** in repo `open-ephys/acquisition-board`. README (verbatim): "+4 SPI headstone connectors for a total capacity of up to 16 RHD chips for a maximum number of 1024 channels"; reaches it "with a few cmos<>lvds bridges" but "**theoretically**", "assuming the bandwidth is not destroyed by the board layout", and "**this is not a finished or tested design yet!**". → UNVALIDATED CONCEPT, not orderable. Physics-legit though: it adds real MISO lines (unlike the impossible XDAQ Core tricks).

**Software/license (resolves the call's "license" question):** the license KC flagged for a 2nd XDAQ = **NeuroNexus paid Allego/Radiens software** (~$2.5-5k perpetual/seat). **Open Ephys GUI + XDAQ-OE plugin + XDAQ-RHX are all FREE/open-source.** So a new box run on OE/RHX needs NO software license. CAVEAT: confirm with KC the "license" is Allego software, not an XDAQ firmware entitlement (evidence says software — Kontex ships the free GUIs). Switching off Allego = rebuild whole pipeline (sleep64 map, XDAT-based eeg-emg-analysis, impedance workflow, video-sync Phase 0a Gated-mode gate).

**Real advantage = OPEN hardware:** design files public → custom expansion genuinely possible (impossible with closed XDAQ). **Real risk:** betting a live-animal 72h instrument on an unfinished board; community vs vendor support.

**🆕 REPLY RECEIVED 2026-07-23 (Margarida, OE Support):**
- **Extension board DEAD** — OE "not familiar", "not something we're currently developing", disowns the repo README. Single-board route to 16 = VAPOR. The whole premise above (16 via extension board) is gone.
- **Base board framed as "max 4 animals"** (dual adapter = 2 headstages in the SAME animal, probe-positioning). ⚠️ Conflicts with our MISO physics (8 chips = 8 single-headstage mice). UNRESOLVED — decides 2-vs-4 boards for 16. Clarify on Discord/GitHub.
- **16 mice → 4 acq boards synced via I/O boards** (8 AI+8 DI+8 AO+8 DO/board, their SyncLink equiv), all on one PC/GUI; OR **paid custom 16-headstage board from OE Atlanta team** (the only non-vapor single-board path).
- **RHD2216 fully supported** ✅ ("optimal for paired differential EEG/EMG").
- **Software $0** ✅ (Open Ephys GUI).
- **NO per-animal ground isolation product** ❌ — "depends on your design", punted to docs/Discord. Kontex Port Expander still the only vendor with a real isolation answer (bad for [[eeg-60hz-saga]]).
- Prices on webstore / formal quote; board + SPI 16ch bipolar headstage IN STOCK. Paid Training + 1yr warranty + repairs + Discord.

**🆕 END-TO-END VALIDATED 2026-07-23:** OE GUI **fully drives our XDAQ Core, license-free** — acquire (no crash) + impedance QC (XML export) + recorded 42s/16ch Binary, real µV, no railing, numpy-readable. XDAQ-OE v0.4.4 plugin needs a **symlink fix** on GUI 1.1.0 (`~/.config/open-ephys/shared`→`shared-api10` + `shared-api10/XDAQ-OE/libxdaq_device.so`→`../libxdaq_device.so`) or it won't load (packaging path bug: RUNPATH `$ORIGIN/../shared/XDAQ-OE` but GUI uses `shared-api10`). Caveats: sample rate recorded 10kHz not 1k (10× storage ~28GB/day/mouse — MUST set+verify in structure.oebin); Record Node at chain END = filtered not raw (move right after source); "Legacy firmware" warning on Gen-1 (DON'T reflash prod Core w/o KC). Impedance: CH1-16 real / CH17-32 empty floor. **Full setup guide = vault [[openephys-gui-setup-xdaq-sleep-eeg]]** (`02-procedures/`). Close Allego before OE (one process owns Opal Kelly USB `151f:0130`). We are ON the acq host e10ubuntu — XDAQ is physically here. Per-animal Record Node control = the Allego-beating feature, still to test w/ 2+ headstages.

**Verdict (post-reply):** OE 16-story got WORSE — no single board, no isolation hw, full pipeline rebuild (XDAT→OE). Wins stay $0 software + confirmed RHD2216. **XDAQ ONE+ still leads** (reliability + pipeline reuse + Port Expander isolation). Ready to council once OE prices pulled. Open follow-ups: 4-vs-8 animals/board, isolation hw?, prices (multi-board vs Atlanta custom). Vault [[openephys-inquiry-email]] + [[2026-07-21-openephys-acquisition-board-scale-up-option]] + [[2026-07-21-acquisition-device-16-32-mice-and-kontex-thread]].
