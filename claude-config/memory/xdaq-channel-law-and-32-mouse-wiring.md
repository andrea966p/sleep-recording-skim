---
name: xdaq-channel-law-and-32-mouse-wiring
description: "THE XDAQ CHANNEL LAW (animals = XR channels / 64), 32-mouse wiring, splitter cannot exceed 16 per box, ONE+ R512 ordering trap. Every fact is in the vault note; the old 'Gen-1 has no chassis terminal' sentence was wrong and is dropped"
metadata: 
  node_type: memory
  type: project
  modified: 2026-10-22T00:00:00.000Z
  originSessionId: a71f4126-a668-426f-b904-b7936fd73591
---

Max animals = XR recording channels / 64 (the box reserves a 64-channel slot per headstage whatever the chip): CORE2 512 ch = 8 mice, ONE+ R512 = 8, ONE+ R1024 = 16. Our 16-ch RHD2216 burns a full slot, so "1024 channels" means 16 MICE. The SPI splitter fills a box, never exceeds it (16-slot ceiling); 32 mice = 2 x ONE+ R1024 with Port Expanders (KC Kong confirmed Intan headstages work with the Port Expander, 2026-07-28). Order ONE-R1024-SR64: the R512 tier records only 8.

Details: [[xdaq-32-mouse-wiring-and-channel-law]] · [[_rig-expansion-hub]] · [[daq-ecosystem-comparison]] · [[acquisition-device-16-32-mice]]

- Never reason from channels; reason from animals.
- The decisive compatibility and model tables on docs.kontex.io are PNG images: a text-only scrape MISSES them.
- Correction: our Gen-1 Core DOES have a chassis GND wired to building earth (2026-09-30): see [[xdaq-gen1-has-chassis-gnd]].
