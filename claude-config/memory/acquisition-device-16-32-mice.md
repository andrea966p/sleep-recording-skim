---
name: acquisition-device-16-32-mice
description: "Device decision for 16 then 32 mice: XDAQ Core is hard-capped at 8 headstages by MISO-line count; 16 = One+, 32 = 2x One+; Port Expander. Facts in the vault."
metadata: 
  node_type: memory
  type: project
  originSessionId: 0f0de6a5-55d5-4402-8180-cf30b24d90ae
  modified: 2026-07-21T09:15:43.046Z
---

**Datasheet-verified 2026-07-21:** one RHD SPI cable = CS+SCLK+MOSI + MISO1 + MISO2, so max 2 chips per cable and one chip per MISO line regardless of channel count. XDAQ Core = 8 headstages (hard, wire count, not firmware); One/One+ = 16; 32 mice = 2x One+. Kontex call 2026-07-21: custom 4-socket adapter NOT possible, 2 mice per Intan adapter NOT possible even with Port Expander, KC recommends trying the Port Expander. Later primary-source corrections (Port Expander mandatory for 16/box, Core has no isolation) are in [[daq-research-findings-primary-sources]].

Details: [[2026-07-21-acquisition-device-16-32-mice-and-kontex-thread]]

Ruled out, do not revive: "DDR = 2 chips per MISO pair so 16 on Core"; Prof. Kim's "4 sockets/port at 32 ch + 8 more headstages"; KC's $75 re-routing adapter (cannot create MISO3/4). No box fixes an open frontal electrode.
