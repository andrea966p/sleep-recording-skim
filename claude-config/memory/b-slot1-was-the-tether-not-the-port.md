---
name: b-slot1-was-the-tether-not-the-port
description: "2026-08-26 swap test: a new mouse with an intact tether in B slot 1 restored the chip ground, falsifying 'B1 is a port fault'; HLBSSD13's tether was chewed through. A recurrence argument is not a swap test."
metadata: 
  node_type: memory
  type: project
  originSessionId: aa023ba0-4d68-4842-9819-c574f4dde34b
  modified: 2026-08-26T03:55:26.885Z
---

**Retraction 2026-08-26.** I had concluded "B slot 1 is a port fault, not a mouse". Andrea pulled HLBSSD13 (chewed tether) and put HLBSSD17 in the same slot: chip floor 60 Hz 246 uV (ungrounded) -> 2338 uV (grounded). The fault followed the ANIMAL/tether; B slot 1, its cable, splitter branch and XDAQ input are good. B1 may simply be the cage position where animals can reach and chew the tether.

Details: [[2026-08-27-B1-swap-baseline-20h-run]]

🛑 A recurrence argument is not a swap test. Do the swap before naming a root cause. Note the swap changed BOTH animal and tether at once, so it exonerates the PORT but does not separate "animal ground wire" from "tether conductor".

Rules:
🛑 Only ~20 epochs at first look — not a verdict. (HLBSSD17 in B1: EEG 84 µV, slope −1.23, lf/hf 10.0 vs floor p99 2.78, EMG 103 µV.)
